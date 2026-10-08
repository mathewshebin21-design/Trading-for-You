"""Frozen prospective US shadow experiment. Separate virtual accounts only."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

from prospective_paper import save_state
from us_accounting import receivable_value, reconcile, ReviewRequired, audit_balances

STRATEGIES = ('sma_20_100','breakout_55_20','mean_reversion_20','buy_hold_25','cash')
RULES = {'version':'LAB.1','capital':10000,'allocation':.25,'drawdown_pause':.1,
         'fee':.001,'slippage':.0005,'spread_limit':.005,'max_age_ms':5000,
         'strategies':STRATEGIES,'cost_multipliers':(1,2),'feed':'iex',
         'evaluation':'90 days and 30 natural roundtrips are screening minima, not proof'}
CODE_HASH = hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('us_accounting.py').read_bytes()).hexdigest()
FINGERPRINT = hashlib.sha256((json.dumps(RULES,sort_keys=True)+CODE_HASH).encode()).hexdigest()


def target(strategy, closes, holding):
    if strategy == 'cash': return False
    if strategy == 'buy_hold_25': return True
    if len(closes) != 100 or not all(math.isfinite(c) and c > 0 for c in closes):
        raise ValueError('LAB_HISTORY_INVALID')
    if strategy == 'sma_20_100':
        return statistics.mean(closes[-20:]) > statistics.mean(closes)
    if strategy == 'breakout_55_20':
        return closes[-1] >= min(closes[-21:-1]) if holding else closes[-1] > max(closes[-56:-1])
    if strategy == 'mean_reversion_20':
        mean = statistics.mean(closes[-20:])
        return closes[-1] < mean if holding else closes[-1] < .98*mean
    raise ValueError('LAB_STRATEGY_INVALID')


def new_lab(symbol, observed):
    return {'version':'LAB.1','symbol':symbol,'currency':'USD','started_ms':observed,
            'rules':RULES,'fingerprint':FINGERPRINT,'code_hash':CODE_HASH,'last_event_ms':0,
            'accounts':{f'{name}:{cost}':{'strategy':name,'cost_multiplier':cost,
                'symbol':symbol,'currency':'USD','cash':10000.,'units':0,'peak':10000.,
                'max_drawdown':0.,'paused':False,'ledger':[],'closed_trades':[],
                'entry_outlay':0.,'realized_partial':0.,'cycle_outlay':0.,
                'decision_ms':observed,'signal_key':None,'target':False,
                'last_session':None,'quote':None,'review_required':False}
                for name in STRATEGIES for cost in (1,2)}}


def advance(record, signal, q, observed, day, allow_entry=True):
    s = deepcopy(record)
    if s['fingerprint'] != FINGERPRINT or s['version'] != 'LAB.1':
        raise ValueError('LAB_RULES_CHANGED_NEW_EXPERIMENT_REQUIRED')
    if json.dumps(s['rules'],sort_keys=True)!=json.dumps(RULES,sort_keys=True):
        raise ValueError('LAB_RULES_RECORD_MISMATCH')
    expected={f'{name}:{cost}' for name in STRATEGIES for cost in (1,2)}
    if set(s['accounts'])!=expected:raise ValueError('LAB_ACCOUNTS_MISMATCH')
    for key,a in s['accounts'].items():
        if key!=f"{a['strategy']}:{a['cost_multiplier']}" or a['symbol']!=s['symbol'] or a['currency']!='USD':
            raise ValueError('LAB_ACCOUNT_IDENTITY_MISMATCH')
        audit_balances(a)
    if not s['started_ms'] <= observed or not 0 <= observed-q['event_ms'] <= 5000:
        raise ValueError('LAB_QUOTE_TIME_INVALID')
    if q['event_ms'] <= s['last_event_ms']:
        return s  # Restart/repeated source event cannot refill.
    if not all(math.isfinite(q[k]) and q[k] > 0 for k in ('bid','ask','bid_qty','ask_qty')) or q['ask'] < q['bid'] or (q['ask']-q['bid'])/q['bid'] > .005:
        raise ValueError('LAB_QUOTE_INVALID')
    s['last_event_ms'] = q['event_ms']
    s['last_observation']={'observed_ms':observed,'quote':q,'bar_close_ms':signal['bar_close_ms'],
                           'closes':signal['closes']}
    for a in s['accounts'].values():
        desired = target(a['strategy'],signal['closes'],a['units'] > 0)
        key = [signal['bar_close_ms'],desired,
               hashlib.sha256(json.dumps(signal['closes']).encode()).hexdigest()]
        if key != a['signal_key']:
            a['signal_key'] = key; a['decision_ms'] = observed; a['target'] = desired
        if a['units'] and a.get('accounted_through',a['last_session']) != day:
            a['review_required'] = True
        if a['review_required']:
            a['status'] = 'CORPORATE_ACTION_REVIEW_REQUIRED'; continue
        equity = a['cash']+a['units']*q['bid']+receivable_value(a)
        a['peak'] = max(a['peak'],equity)
        dd = equity/a['peak']-1; a['max_drawdown'] = min(a['max_drawdown'],dd)
        if a['strategy'] not in ('cash','buy_hold_25') and dd <= -.1:
            a['paused'] = True
        a['equity'] = equity; a['quote'] = q; a['status'] = 'NO_ACTION'
        if q['event_ms'] <= a['decision_ms']:
            a['status'] = 'AWAITING_POST_DECISION_QUOTE'; continue
        wanted = a['target'] and not a['paused']
        side = 'BUY' if wanted and not a['units'] else 'SELL' if not wanted and a['units'] else None
        if side is None: continue
        if side == 'BUY' and not allow_entry:
            a['status'] = 'ENTRY_PAUSED'; continue
        mult = a['cost_multiplier']; mid = (q['ask']+q['bid'])/2
        # Double modeled observed half-spread too, not only fee/slippage.
        price = mid+(q['ask']-mid)*mult if side == 'BUY' else mid-(mid-q['bid'])*mult
        price *= 1+.0005*mult if side == 'BUY' else 1-.0005*mult
        fee_rate = .001*mult
        qty = min(math.floor(min(a['cash'],equity*.25)/(price*(1+fee_rate))),math.floor(q['ask_qty'])) if side == 'BUY' else min(a['units'],math.floor(q['bid_qty']))
        if qty < 1:
            a['status'] = 'REJECTED_SIZE'; continue
        fee = qty*price*fee_rate
        if side == 'BUY':
            outlay = qty*price+fee; a['cash'] -= outlay; a['units'] += qty
            a['entry_outlay'] = outlay; a['cycle_outlay'] = outlay; a['realized_partial'] = 0.
        else:
            allocated = a['entry_outlay']*qty/a['units']
            proceeds = qty*price-fee; a['cash'] += proceeds
            a['realized_partial'] += proceeds-allocated; a['entry_outlay'] -= allocated; a['units'] -= qty
            if not a['units']:
                a['closed_trades'].append({'net_trade_pnl_excluding_distributions':a['realized_partial'],
                                         'event_ms':q['event_ms']})
        a['last_session'] = day
        a['ledger'].append({'mode':'PAPER_ONLY','side':side,'quantity':qty,
            'model_fill_price':price,'commission':fee,'event_ms':q['event_ms'],
            'modeled_execution_cost':qty*abs(price-mid)+fee,'decision_ms':a['decision_ms']})
        a['equity'] = a['cash']+a['units']*q['bid']+receivable_value(a)
        a['max_drawdown'] = min(a['max_drawdown'],a['equity']/a['peak']-1)
        a['status'] = 'SIMULATED_'+side
    # Daily last-observed marks are explicitly NOT official closing prices.
    day_marks=s.setdefault('daily_last_observed',{})
    day_marks[day]={'observed_ms':observed,'source_event_ms':q['event_ms'],
                    'equity':{key:a.get('equity') for key,a in s['accounts'].items()},
                    'blocked':any(a['review_required'] for a in s['accounts'].values())}
    return s


def observe(folder, symbol, signal, q, observed, day, allow_entry=True, review_path=None):
    path = Path(folder)/(symbol+'_lab.json')
    state = json.loads(path.read_text()) if path.exists() else new_lab(symbol,observed)
    if state['symbol'] != symbol: raise ValueError('LAB_IDENTITY_MISMATCH')
    if review_path and Path(review_path).exists():
        manifest=json.loads(Path(review_path).read_text())
        for key,a in list(state['accounts'].items()):
            try:
                state['accounts'][key]=reconcile(a,manifest,day,observed)
            except ReviewRequired:
                a['review_required']=True
    state = advance(state,signal,q,observed,day,allow_entry)
    save_state(path,state)


def report(folder, observed):
    lines = ['PROSPECTIVE US SHADOW LAB — paper only; unvalidated.']
    for path in sorted(Path(folder).glob('*_lab.json')):
        s = json.loads(path.read_text())
        elapsed = (observed-s['started_ms'])/86400000
        started=datetime.fromtimestamp(s['started_ms']/1000,timezone.utc).isoformat()
        lines.append(f"{s['symbol']}: started {started}; {elapsed:.1f} days; frozen {s['fingerprint'][:12]}")
        for key,a in s['accounts'].items():
            benchmark=s['accounts'][f"buy_hold_25:{a['cost_multiplier']}"]
            if a['review_required'] or benchmark['review_required']:
                lines.append(key+': BLOCKED_ACCOUNTING; mark/excess comparison unavailable');continue
            if 'equity' not in a or 'equity' not in benchmark:
                lines.append(key+': awaiting comparable marks'); continue
            pnl=a['equity']-10000; excess=a['equity']-benchmark['equity']
            evidence = ('BLOCKED_ACCOUNTING' if a['review_required'] else
                        'INSUFFICIENT_EVIDENCE' if elapsed<90 or len(a['closed_trades'])<30 else
                        'REVIEW_REQUIRED_NOT_VALIDATED')
            costs=sum(t['modeled_execution_cost'] for t in a['ledger'])
            lines.append(f"{key}: indicative P/L ${pnl:.2f}; excess ${excess:.2f}; DD {a['max_drawdown']*100:.2f}%; modeled costs ${costs:.2f}; roundtrips {len(a['closed_trades'])}; {evidence}")
    return lines
