"""Experimental US research simulator. GET data/calendar only; no broker orders.
IEX is one venue. Overnight positions require corporate-action reconciliation.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import statistics
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo
from prospective_paper import now_ms, save_state

SYMBOLS = ('SPY', 'AAPL', 'GLD')
ET = ZoneInfo('America/New_York')


class QuoteUnavailable(ValueError):
    """A fixed public reason code; never provider text or credentials."""
    pass


def preserve_decision(previous, current):
    # A repeated observation is not a new decision. Revisions to either the
    # completed bar or indicator values do create a new decision timestamp.
    fields = ('bar_close_ms', 'fast', 'slow', 'target_long')
    if previous and all(previous.get(k) == current[k] for k in fields):
        current['observed_ms'] = previous['observed_ms']
    return current


def stamp(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('Timestamp must have timezone')
    return int(dt.timestamp()*1000)


def get_data(path, params):
    allowed = {'/v2/calendar'} | {f'/v2/stocks/{s}/{kind}' for s in SYMBOLS for kind in ('bars', 'quotes/latest')}
    if path not in allowed:
        raise ValueError('Read-only endpoint outside allowlist')
    key, secret = os.getenv('ALPACA_DATA_KEY'), os.getenv('ALPACA_DATA_SECRET')
    if not key or not secret:
        raise ValueError('Configure private paper-account data credentials')
    origin = 'https://paper-api.alpaca.markets' if path == '/v2/calendar' else 'https://data.alpaca.markets'
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('Redirect rejected')
    request = urllib.request.Request(origin+path+'?'+urllib.parse.urlencode(params),
        headers={'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}, method='GET')
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=15) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Oversized response')
    return json.loads(raw)


def sessions(calendar):
    result = []
    for row in calendar:
        day = row['date']
        opening = datetime.fromisoformat(day+'T'+row['open']).replace(tzinfo=ET)
        closing = datetime.fromisoformat(day+'T'+row['close']).replace(tzinfo=ET)
        if opening >= closing:
            raise ValueError('Invalid session')
        result.append((day, int(opening.timestamp()*1000), int(closing.timestamp()*1000)))
    if result != sorted(set(result)):
        raise ValueError('Duplicate or unordered calendar')
    return result


def market_session(calendar, observed):
    """Describe an active regular session from the provider calendar."""
    active = [r for r in sessions(calendar) if r[1] <= observed < r[2]]
    if len(active) > 1:
        raise ValueError('Overlapping calendar sessions')
    if not active:
        return {'symbol':'US_MARKET', 'status':'MARKET_CLOSED'}
    day, opening, closing = active[0]
    return {'symbol':'US_MARKET', 'status':'MARKET_OPEN', 'session_date':day,
            'open_ms':opening, 'close_ms':closing, 'observed_ms':observed}


def signal(bars, calendar, observed):
    completed = [r for r in sessions(calendar) if r[2] < observed][-100:]
    if len(completed) != 100:
        raise ValueError('Need 100 completed sessions')
    indexed = {}
    for bar in bars:
        day = datetime.fromtimestamp(stamp(bar['t'])/1000, ET).date().isoformat()
        if day in indexed:
            raise ValueError('Duplicate daily bar')
        o,h,l,c = [float(bar[k]) for k in ('o','h','l','c')]
        if not all(math.isfinite(v) and v > 0 for v in (o,h,l,c)) or not l <= min(o,c) <= max(o,c) <= h:
            raise ValueError('Invalid OHLC')
        indexed[day] = c
    if any(r[0] not in indexed for r in completed):
        raise ValueError('Missing or stale session bars')
    closes = [indexed[r[0]] for r in completed]
    fast, slow = statistics.mean(closes[-20:]), statistics.mean(closes)
    return {'bar_close_ms': completed[-1][2], 'observed_ms': observed,
            'fast': fast, 'slow': slow, 'target_long': fast > slow}


def quote(record, observed, decision):
    event = stamp(record['t'])
    bid, ask = float(record['bp']), float(record['ap'])
    bsize, asize = float(record['bs']), float(record['as'])
    if not all(math.isfinite(v) and v > 0 for v in (bid, ask, bsize, asize)) or ask < bid:
        raise ValueError('Invalid or crossed quote')
    if observed-event > 5000:
        raise QuoteUnavailable('QUOTE_STALE')
    if event-observed > 2000:
        raise QuoteUnavailable('QUOTE_FUTURE')
    if event < decision:
        raise QuoteUnavailable('QUOTE_BEFORE_DECISION')
    if (ask-bid)/bid > .005:
        raise ValueError('Excessive spread')
    # IEX quote sizes are round lots; simulator deliberately caps fill to ONE
    # share per reported lot to understate, rather than overstate, liquidity.
    return {'event_ms': event, 'received_ms': observed, 'bid': bid, 'ask': ask,
            'bid_qty': math.floor(bsize), 'ask_qty': math.floor(asize), 'feed': 'iex'}


async def fresh_quote(symbol, decision):
    # Only retry timing failures. Never relax freshness or substitute a feed.
    for attempt in range(3):
        raw = await asyncio.to_thread(get_data, f'/v2/stocks/{symbol}/quotes/latest', {'feed':'iex'})
        observed = now_ms()
        try:
            return quote(raw['quote'], observed, decision), observed
        except QuoteUnavailable as error:
            if str(error) == 'QUOTE_FUTURE' or attempt == 2:
                raise
            await asyncio.sleep(1)


def account(symbol):
    if symbol not in SYMBOLS:
        raise ValueError('Unsupported symbol')
    return {'version': 'US.1', 'symbol': symbol, 'currency': 'USD', 'cash': 10000.,
            'units': 0, 'peak': 10000., 'paused': False, 'ledger': [],
            'signal': None, 'last_session': None, 'quote': None, 'review_required': False}


def fill(state, q, calendar, observed, allow_entry=True):
    if state['version'] != 'US.1' or state['currency'] != 'USD' or state['symbol'] not in SYMBOLS:
        raise ValueError('Invalid account identity')
    if observed-q['event_ms'] > 5000 or q['event_ms']-observed > 2000:
        raise ValueError('Stale fill quote')
    active = [r for r in sessions(calendar) if r[1] <= observed < r[2]]
    if len(active) != 1:
        return 'MARKET_CLOSED'
    day, opening, closing = active[0]
    if not opening <= q['event_ms'] < closing or q['event_ms'] < state['signal']['observed_ms']:
        raise ValueError('Quote outside session or before decision')
    if state['units'] and state['last_session'] != day:
        state['review_required'] = True
    if state['review_required']:
        return 'CORPORATE_ACTION_REVIEW_REQUIRED'
    equity = state['cash'] + state['units']*q['bid']
    state['peak'] = max(state['peak'], equity)
    if equity/state['peak'] <= .9:
        state['paused'] = True
    desired = state['signal']['target_long'] and not state['paused']
    side = 'BUY' if desired and not state['units'] else 'SELL' if not desired and state['units'] else None
    state['quote'] = q
    if side == 'BUY' and not allow_entry:
        return 'ENTRY_PAUSED'
    if side is None:
        return 'NO_ACTION'
    price = q['ask']*1.0005 if side == 'BUY' else q['bid']*.9995
    qty = min(math.floor(equity*.25/(price*1.001)), q['ask_qty']) if side == 'BUY' else min(state['units'], q['bid_qty'])
    if qty < 1:
        return 'REJECTED_SIZE'
    fee = qty*price*.001
    cash_change = -(qty*price+fee) if side == 'BUY' else qty*price-fee
    if state['cash']+cash_change < 0:
        raise ValueError('Insufficient virtual cash')
    state['cash'] += cash_change
    state['units'] += qty if side == 'BUY' else -qty
    state['last_session'] = day
    state['ledger'].append({'mode':'PAPER_ONLY','side':side,'quantity':qty,
        'model_fill_price':price,'commission':fee,'event_ms':q['event_ms'],'feed':'iex'})
    return 'SIMULATED_'+side


async def poll_us(folder, allow_entry=True):
    if os.getenv('US_PAPER_ENABLED') != '1':
        return []
    folder = Path(folder)
    results = []
    try:
        observed = now_ms()
        today = datetime.fromtimestamp(observed/1000, ET).date()
        start = (today-timedelta(days=550)).isoformat()
        calendar = await asyncio.to_thread(get_data, '/v2/calendar', {'start':start,'end':today.isoformat()})
        # Validate calendar before processing accounts, including closed days.
        results.append(market_session(calendar, now_ms()))
    except Exception:
        return [{'symbol':'US','status':'NO_FILL_DATA_ERROR','error':'US calendar/credentials unavailable'}]
    for symbol in SYMBOLS:
        path = folder/(symbol+'_state.json')
        stage = 'ACCOUNT_STATE'
        try:
            state = json.loads(path.read_text()) if path.exists() else account(symbol)
            if state['symbol'] != symbol or state['version'] != 'US.1' or state['currency'] != 'USD':
                raise ValueError('Account mismatch')
            stage = 'HISTORY_FETCH'
            data = await asyncio.to_thread(get_data, f'/v2/stocks/{symbol}/bars',
                {'timeframe':'1Day','start':start,'end':today.isoformat(), 'limit':1000,
                 'adjustment':'all','feed':'iex','sort':'asc'})
            stage = 'HISTORY_VALIDATION'
            if data.get('next_page_token'):
                raise ValueError('Incomplete paginated history')
            state['signal'] = preserve_decision(state['signal'], signal(data['bars'], calendar, now_ms()))
            stage = 'STATE_WRITE'
            save_state(path, state)
            if not any(a <= now_ms() < b for _,a,b in sessions(calendar)):
                outcome = 'MARKET_CLOSED'
            else:
                stage = 'QUOTE_FETCH_OR_VALIDATION'
                q, observed = await fresh_quote(symbol, state['signal']['observed_ms'])
                stage = 'FILL_VALIDATION'
                outcome = fill(state, q, calendar, observed, allow_entry)
                stage = 'STATE_WRITE'
                save_state(path, state)
            results.append({'symbol':symbol,'currency':'USD','status':outcome,'trend':'UP' if state['signal']['target_long'] else 'NOT UP',
                'simulated_fill_count':len(state['ledger']),'paused':state['paused']})
        except QuoteUnavailable as error:
            results.append({'symbol':symbol,'status':'NO_FILL_QUOTE_UNAVAILABLE',
                            'reason':str(error),'feed':'iex'})
        except Exception:
            # Never include provider exceptions, request headers or credentials.
            results.append({'symbol':symbol,'status':'NO_FILL_DATA_ERROR',
                            'reason':stage,'error':'US '+stage.lower().replace('_',' ')+' failed'})
    save_state(folder/'latest_poll.json', results)
    return results


def report_us(folder):
    if os.getenv('US_PAPER_ENABLED') != '1':
        return ['US paper module: disabled; SPY/AAPL/GLD available after setup.']
    lines = ['US PAPER ONLY — USD; IEX single venue; strategy unvalidated.']
    for symbol in SYMBOLS:
        p = Path(folder)/(symbol+'_state.json')
        if not p.exists():
            lines.append(symbol+': awaiting valid observations.'); continue
        s = json.loads(p.read_text()); sig = s['signal']
        lines.append(f"{symbol}: {'UP' if sig and sig['target_long'] else 'NOT UP'}; cash ${s['cash']:.2f}; shares {s['units']}; fills {len(s['ledger'])}; corporate-action review {s['review_required']}; signal observed {sig['observed_ms'] if sig else 'none'}")
        if s['quote']:
            lines.append(f"Quote age {(now_ms()-s['quote']['received_ms'])/1000:.0f}s; indicative, not executable.")
    latest = Path(folder)/'latest_poll.json'
    if latest.exists():
        lines.extend(r['symbol']+': '+r['status']+(' ('+r['reason']+')' if r.get('reason') else '') for r in json.loads(latest.read_text()))
    return lines
