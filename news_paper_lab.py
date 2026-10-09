"""Frozen delayed-news entry filter versus matched trend accounts. PAPER ONLY."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from us_accounting import audit_balances, reconcile, receivable_value, ReviewRequired
from prospective_paper import save_state

RULES={'version':'NEWSLAB.1','symbol':'AAPL','initial_cash':10000,
       'delay_ms':1800000,'feed_delay_ms':900000,'max_poll_age_ms':600000,
       'strategies':['baseline','news_delay'],'costs':[1,2],
       'entry_allocation':.25,'risk_pause_drawdown':.1,'quote_max_age_ms':5000}
CODE_HASH=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('us_paper.py').read_bytes()+Path(__file__).with_name('news_collector.py').read_bytes()+Path(__file__).with_name('us_accounting.py').read_bytes()).hexdigest()
FINGERPRINT=hashlib.sha256((json.dumps(RULES,sort_keys=True)+CODE_HASH).encode()).hexdigest()


def evidence(folder, observed, started):
    folder=Path(folder);health=json.loads((folder/'news_health.json').read_text())
    valid=(health.get('status')=='RESEARCH_ONLY' and health.get('coverage')=='COMPLETE_DELAYED_WINDOW'
           and 0<=observed-health['received_ms']<=600000
           and 900000<=observed-health['coverage_end_ms']<=1500000)
    latest=None
    db=sqlite3.connect(f'file:{folder / "research.sqlite"}?mode=ro',uri=True)
    try:
        for payload,received in db.execute('SELECT payload,first_received_ms FROM evidence WHERE first_received_ms >= ? AND first_received_ms <= ?',(started,observed)):
            if 'AAPL' in json.loads(payload)['symbols']:latest=max(latest or 0,received)
    finally:db.close()
    return {'valid':valid,'latest_receipt_ms':latest,'coverage_end_ms':health.get('coverage_end_ms'),
            'received_ms':health.get('received_ms')}


def advance(state, signal, q, calendar, observed, news, allow_entry=True, manifest=None):
    from us_paper import account, fill, preserve_decision, sessions
    s=deepcopy(state) if state else {'version':'NEWSLAB.1','fingerprint':FINGERPRINT,
        'started_ms':observed,'last_event_ms':0,'accounts':{
            f'{name}:{cost}':account('AAPL') for name in RULES['strategies'] for cost in RULES['costs']},
        'coverage_gaps':0,'daily_marks':{}}
    if s['fingerprint']!=FINGERPRINT or s['version']!='NEWSLAB.1':raise ValueError('NEWS_LAB_RULES_CHANGED')
    if set(s['accounts'])!={f'{n}:{c}' for n in RULES['strategies'] for c in RULES['costs']}:raise ValueError('NEWS_LAB_ACCOUNTS_INVALID')
    if not 0<=observed-q['event_ms']<=5000:raise ValueError('NEWS_LAB_STALE_QUOTE')
    if not all(math.isfinite(q[k]) and q[k]>0 for k in ('bid','ask','bid_qty','ask_qty')) or q['ask']<q['bid'] or (q['ask']-q['bid'])/q['bid']>.005:
        raise ValueError('NEWS_LAB_INVALID_QUOTE')
    if q['event_ms']<=s['last_event_ms']:return s
    active=[r for r in sessions(calendar) if r[1]<=observed<r[2]]
    if len(active)!=1 or not active[0][1]<=q['event_ms']<active[0][2]:raise ValueError('NEWS_LAB_OUTSIDE_SESSION')
    day=active[0][0]
    quote_gap=s.get('last_day')==day and s['last_event_ms']>0 and q['event_ms']-s['last_event_ms']>600000
    s['last_event_ms']=q['event_ms'];s['last_day']=day;s['last_news']=news
    valid=bool(news['valid']) and not quote_gap
    if not valid:s['coverage_gaps']+=1
    # Gaps are retained. Comparison periods with a gap must not be certified.
    for key,a in s['accounts'].items():
        if a['symbol']!='AAPL' or a['currency']!='USD':raise ValueError('NEWS_LAB_IDENTITY_INVALID')
        audit_balances(a)
        if manifest:
            try:a=reconcile(a,manifest,day,observed);s['accounts'][key]=a
            except ReviewRequired:a['review_required']=True
        incoming={**signal,'observed_ms':observed}
        a['signal']=preserve_decision(a.get('signal'),incoming)
        delay=key.startswith('news_delay:') and news['latest_receipt_ms'] is not None and observed-news['latest_receipt_ms']<RULES['delay_ms']
        gate=[bool(allow_entry),valid,delay]
        if a.get('entry_gate')!=gate and not a['units'] and a['signal']['target_long']:
            a['signal']['observed_ms']=observed
        a['entry_gate']=gate
        a['equity']=a['cash']+a['units']*q['bid']+receivable_value(a)
        a['observed_ms']=observed
        a['quote']=q
        if q['event_ms']<=a['signal']['observed_ms']:
            a['status']='AWAITING_POST_DECISION_QUOTE';continue
        before=len(a['ledger'])
        a['status']=fill(a,q,calendar,observed,allow_entry=allow_entry and valid and not delay,cost_multiplier=int(key[-1]))
        if a['status']=='ENTRY_PAUSED' and not valid:a['status']='NEWS_COVERAGE_ENTRY_BLOCKED'
        elif a['status']=='ENTRY_PAUSED' and delay:a['status']='NEWS_DELAY_ENTRY_BLOCKED'
        if len(a['ledger'])>before:
            t=a['ledger'][-1];t['decision_ms']=a['signal']['observed_ms']
            t['news_coverage_end_ms']=news.get('coverage_end_ms');t['news_delay_active']=delay
            t['modeled_execution_cost']=abs(t['model_fill_price']-(q['ask']+q['bid'])/2)*t['quantity']+t['commission']
        a['equity']=a['cash']+a['units']*q['bid']+receivable_value(a)
        a['max_drawdown']=min(a.get('max_drawdown',0),a['equity']/a['peak']-1)
        a['observed_ms']=observed
    prior_valid=s['daily_marks'].get(day,{}).get('valid',True)
    s['daily_marks'][day]={'observed_ms':observed,'source_event_ms':q['event_ms'],
        'valid':prior_valid and valid and not any(a['review_required'] for a in s['accounts'].values()),
        'equity':{k:a.get('equity') for k,a in s['accounts'].items()}}
    return s


def observe(folder, news_folder, signal, q, calendar, observed, allow_entry, review_path):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);path=folder/'AAPL_news_lab.json'
    state=json.loads(path.read_text()) if path.exists() else None
    news=evidence(news_folder,observed,state['started_ms'] if state else observed)
    manifest=json.loads(Path(review_path).read_text()) if Path(review_path).exists() else None
    s=advance(state,signal,q,calendar,observed,news,allow_entry,manifest)
    save_state(path,s)
    print('NEWS_LAB_HEALTH '+json.dumps({'observed_ms':observed,'coverage_valid':news['valid'],
        'statuses':{k:a['status'] for k,a in s['accounts'].items()},'paper_only':True}),flush=True)


def report(folder, observed):
    path=Path(folder)/'AAPL_news_lab.json'
    lines=['AAPL DELAYED-NEWS PAPER LAB — unvalidated; virtual USD only.']
    if not path.exists():return lines+['Not started; needs an open session, fresh quote and news coverage records.']
    s=json.loads(path.read_text());lines.append(f"Age {(observed-s['started_ms'])/86400000:.1f} days; coverage gaps {s['coverage_gaps']}; frozen {s['fingerprint'][:12]}")
    for key,a in s['accounts'].items():
        base=s['accounts']['baseline:'+key[-1]]
        equity=a.get('equity');ref=base.get('equity')
        units=0;closed=0
        for t in a['ledger']:
            units+=t['quantity'] if t['side']=='BUY' else -t['quantity']
            if t['side']=='SELL' and units==0:closed+=1
        pnl=f"${equity-10000:.2f}" if equity is not None else 'unmarked'
        excess=f"${equity-ref:.2f}" if equity is not None and ref is not None else 'unmarked'
        lines.append(f"{key}: net P/L {pnl}; excess vs trend {excess}; DD {100*a.get('max_drawdown',0):.2f}%; natural roundtrips {closed}; fills {len(a['ledger'])}; {a.get('status','NOT_STARTED')}")
        lines.append(f"Modeled costs ${sum(t.get('modeled_execution_cost',0) for t in a['ledger']):.2f}; shares {a['units']}; latest mark age {max(0,(observed-a.get('observed_ms',s['started_ms']))/1000):.0f}s (indicative)")
    return lines+['INSUFFICIENT_EVIDENCE; delayed feed, sampled quotes; no profitability claim.']
