"""Interactive, read-only Binance data and virtual USDT accounts. No live orders."""
import asyncio
import json
import math
from pathlib import Path
import statistics
import time
import urllib.request
from datetime import datetime,timezone

SESSION_VERSION='002.1'
SYMBOLS=('BTCUSDT','ETHUSDT')
DAY_MS=86_400_000


def now_ms(): return int(time.time()*1000)


def public_get(path,query=''):
    if path not in {'klines','exchangeInfo'}:
        raise ValueError('Only read-only candle and symbol-info requests allowed')
    request=urllib.request.Request('https://data-api.binance.vision/api/v3/'+path+'?'+query,
                                  headers={'User-Agent':'PaperResearch/002'},method='GET')
    # Disable redirect following: never leave the public market-data-only origin.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs): raise ValueError('Unexpected redirect')
    with urllib.request.build_opener(NoRedirect()).open(request,timeout=15) as response:
        raw=response.read(1_000_001)
    if len(raw)>1_000_000: raise ValueError('Oversized response')
    return json.loads(raw), now_ms()


def completed_closes(klines,observed_ms):
    rows=[k for k in klines if int(k[6]) < observed_ms]
    if len(rows)<100: raise ValueError('Need 100 completed daily bars')
    rows=rows[-100:]
    for i,k in enumerate(rows):
        start,end=int(k[0]),int(k[6])
        prices=[float(k[j]) for j in (1,2,3,4)]
        if not all(math.isfinite(v) and v>0 for v in prices): raise ValueError('Invalid candle prices')
        o,h,l,c=prices
        if not l<=min(o,c)<=max(o,c)<=h: raise ValueError('Inconsistent candle OHLC')
        if start % DAY_MS or end!=start+DAY_MS-1: raise ValueError('Not a UTC daily candle')
        if i and start!=int(rows[i-1][0])+DAY_MS: raise ValueError('Missing or reordered daily candle')
    if int(rows[-1][0])!=observed_ms//DAY_MS*DAY_MS-DAY_MS:
        raise ValueError('Latest completed candle is stale')
    return [float(k[4]) for k in rows], int(rows[-1][6])


def validate_quote(record,symbol,received_ms,decision_ms):
    if record.get('e')!='24hrTicker' or record.get('s')!=symbol: raise ValueError('Wrong quote event')
    event_ms=int(record['E'])
    if event_ms < decision_ms: raise ValueError('Quote precedes observed decision')
    if received_ms-event_ms>5000 or event_ms-received_ms>2000: raise ValueError('Stale quote or clock mismatch')
    bid,ask,bid_qty,ask_qty=[float(record[k]) for k in ('b','a','B','A')]
    if not all(math.isfinite(v) and v>0 for v in (bid,ask,bid_qty,ask_qty)) or ask<bid:
        raise ValueError('Invalid or crossed quote')
    if (ask-bid)/bid>0.005: raise ValueError('Excessive spread')
    return {'event_ms':event_ms,'received_ms':received_ms,'bid':bid,'ask':ask,'bid_qty':bid_qty,'ask_qty':ask_qty}


async def fresh_quote(symbol,decision_ms):
    if symbol not in SYMBOLS: raise ValueError('Symbol outside session')
    import websockets
    async with websockets.connect('wss://data-stream.binance.vision/ws/'+symbol.lower()+'@ticker',
                                  open_timeout=10,close_timeout=2,max_size=1_000_000) as stream:
        record=json.loads(await asyncio.wait_for(stream.recv(),timeout=10))
    return validate_quote(record,symbol,now_ms(),decision_ms)


def symbol_filters(info,symbol):
    records=[r for r in info['symbols'] if r['symbol']==symbol]
    if len(records)!=1 or records[0]['status']!='TRADING' or records[0]['quoteAsset']!='USDT':
        raise ValueError('Unsupported instrument or currency')
    filters={f['filterType']:f for f in records[0]['filters']}
    lot=filters['LOT_SIZE']
    notional=filters.get('NOTIONAL',filters.get('MIN_NOTIONAL'))
    if notional is None: raise ValueError('Unknown minimum notional')
    values={'step':float(lot['stepSize']),'min_qty':float(lot['minQty']),
            'max_qty':float(lot['maxQty']),'min_notional':float(notional['minNotional'])}
    if not all(math.isfinite(v) and v>0 for v in values.values()): raise ValueError('Invalid instrument filters')
    return values


def new_session(symbol):
    if symbol not in SYMBOLS: raise ValueError('Unsupported session symbol')
    return {'version':SESSION_VERSION,'symbol':symbol,'venue':'Binance spot','currency':'USDT',
            'started_ms':now_ms(),'cash':10000.0,'units':0.0,'peak':10000.0,'paused':False,
            'last_bar_close_ms':0,'decision_ms':0,'target_long':False,'ledger':[],
            'quote_observations':[],'closed_trades':[],'entry_outlay':None}


def observe_signal(state,closes,close_ms,observed_ms):
    if len(closes)!=100 or not all(math.isfinite(v) and v>0 for v in closes): raise ValueError('Invalid signal history')
    if close_ms>observed_ms or close_ms<state['last_bar_close_ms']: raise ValueError('Future or older signal bar')
    if close_ms==state['last_bar_close_ms']: return False
    fast,slow=statistics.mean(closes[-20:]),statistics.mean(closes)
    state.update(last_bar_close_ms=close_ms,decision_ms=observed_ms,target_long=fast>slow)
    state.setdefault('signal_observations',[]).append({'bar_close_ms':close_ms,
        'observed_ms':observed_ms,'closes':closes,'fast':fast,'slow':slow,'target_long':fast>slow})
    return True


def execute_paper(state,quote,filters,allow_entry=True):
    """Consume a validated post-decision quote; mutate only the virtual ledger."""
    if state['version']!=SESSION_VERSION or state['currency']!='USDT': raise ValueError('State version/currency mismatch')
    if quote['event_ms']<state['decision_ms']: raise ValueError('Quote precedes decision')
    equity=state['cash']+state['units']*quote['bid']
    state['peak']=max(state['peak'],equity)
    if equity/state['peak']-1<=-0.10: state['paused']=True
    desired=state['target_long'] and not state['paused']
    side='BUY' if desired and state['units']==0 else 'SELL' if not desired and state['units']>0 else None
    state['quote_observations'].append({**quote,'mark_equity_before_fill':equity})
    if side=='BUY' and not allow_entry: return 'ENTRY_PAUSED'
    if side is None: return 'NO_ACTION'
    reference=quote['ask'] if side=='BUY' else quote['bid']
    price=reference*(1.0003 if side=='BUY' else 0.9997)
    if side=='BUY':
        limit=min(state['cash'],equity*0.25)/(price*1.001)
        qty=min(limit,quote['ask_qty'],filters['max_qty'])
    else: qty=min(state['units'],quote['bid_qty'],filters['max_qty'])
    qty=math.floor(qty/filters['step']+1e-10)*filters['step']
    if qty<filters['min_qty'] or qty*reference<filters['min_notional']:
        return 'REJECTED_SIZE_OR_NOTIONAL'
    fee=qty*price*0.001
    if side=='BUY':
        outlay=qty*price+fee
        if outlay>state['cash']+1e-8: raise ValueError('Insufficient virtual cash')
        state['cash']-=outlay;state['units']=qty;state['entry_outlay']=outlay
    else:
        old_units=state['units']
        allocated_cost=state['entry_outlay']*qty/old_units
        proceeds=qty*price-fee
        state['cash']+=proceeds;state['units']=max(0.0,old_units-qty)
        state['entry_outlay']=state['entry_outlay']-allocated_cost if state['units'] else None
        state['closed_trades'].append({'net_pnl':proceeds-allocated_cost,'quantity':qty,'partial':state['units']>0})
    state['ledger'].append({'mode':'PAPER_ONLY','side':side,'symbol':state['symbol'],'currency':'USDT',
                           'decision_ms':state['decision_ms'],'event_ms':quote['event_ms'],
                           'received_ms':quote['received_ms'],'quantity':qty,'reference':reference,
                           'model_fill_price':price,'commission':fee,'remaining_units':state['units'],
                           'reason':'drawdown_pause' if state['paused'] else 'observed_daily_trend'})
    return 'SIMULATED_'+side


def save_state(path,state):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2,allow_nan=False));tmp.replace(p)


async def poll_session(folder,allow_entry=True):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for symbol in SYMBOLS:
        p=folder/(symbol+'_state.json')
        try:
            state=json.loads(p.read_text()) if p.exists() else new_session(symbol)
            if state['symbol']!=symbol or state['version']!=SESSION_VERSION or state['currency']!='USDT':
                raise ValueError('Saved state identity mismatch')
            raw,seen=await asyncio.to_thread(public_get,'klines','symbol='+symbol+'&interval=1d&limit=101')
            closes,bar_close=completed_closes(raw,seen)
            info,_=await asyncio.to_thread(public_get,'exchangeInfo','symbol='+symbol)
            filters=symbol_filters(info,symbol)
            save_state(folder/('sources_'+symbol+'_'+str(seen)+'.json'),
                       {'received_ms':seen,'klines':raw,'exchangeInfo':info})
            changed=observe_signal(state,closes,bar_close,seen)
            # Save the real observation time before attempting a fill.
            save_state(p,state)
            q=await fresh_quote(symbol,state['decision_ms'])
            outcome=execute_paper(state,q,filters,allow_entry=allow_entry)
            save_state(p,state)
            outcomes.append({'symbol':symbol,'currency':'USDT','status':outcome,'new_signal_bar':changed,
                'quote_event_utc':datetime.fromtimestamp(q['event_ms']/1000,timezone.utc).isoformat(),
                'quote_age_ms':q['received_ms']-q['event_ms'],'cash':round(state['cash'],2),
                'units':state['units'],'simulated_fill_count':len(state['ledger']),'paused':state['paused']})
        except Exception as exc:
            error={'symbol':symbol,'status':'NO_FILL_SOURCE_OR_VALIDATION_ERROR','error':str(exc),'observed_ms':now_ms()}
            outcomes.append(error)
            with (folder/'errors.jsonl').open('a') as f:f.write(json.dumps(error)+'\n')
    save_state(folder/'latest_poll.json',outcomes)
    return outcomes
