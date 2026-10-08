"""Local paper accounting for explicitly reviewed corporate-action manifests.

No feed response can automatically certify absence of actions. Unsupported,
late or revised actions fail closed. Never connects to a broker/order endpoint.
"""
from copy import deepcopy
from datetime import date
import hashlib
import json
import math
from datetime import datetime
from zoneinfo import ZoneInfo


class ReviewRequired(ValueError):
    pass


def audit_balances(state):
    """Replay recorded fills/actions; detect balance drift before reconciliation."""
    events = [(t['event_ms'],1,t) for t in state.get('ledger',[])]
    events += [(t['effective_ms'],0,t) for t in state.get('action_ledger',[])]
    cash,units = 10000.,0.
    for _,_,t in sorted(events,key=lambda e:(e[0],e[1])):
        kind=t.get('type')
        if kind=='split': units *= t['ratio']
        elif kind=='dividend_payment': cash += t['amount']
        elif kind=='dividend_entitlement': pass
        elif t.get('side') in ('BUY','SELL'):
            qty=t['quantity'];price=t['model_fill_price'];fee=t['commission']
            if not all(math.isfinite(v) and v>=0 for v in (qty,price,fee)) or qty<=0 or price<=0:
                raise ReviewRequired('LEDGER_FILL_INVALID')
            cash += -(qty*price+fee) if t['side']=='BUY' else qty*price-fee
            units += qty if t['side']=='BUY' else -qty
        else: raise ReviewRequired('LEDGER_EVENT_INVALID')
        if cash < -1e-7 or units < -1e-7:
            raise ReviewRequired('LEDGER_NEGATIVE_BALANCE')
    if not math.isclose(cash,state['cash'],abs_tol=1e-6,rel_tol=1e-12) or not math.isclose(units,state['units'],abs_tol=1e-8,rel_tol=1e-12):
        raise ReviewRequired('LEDGER_BALANCE_MISMATCH')


def reconcile(state, manifest, day, observed):
    """Return a new state, or raise without altering caller state.

    Manifest coverage is inclusive. Review must cover the previous accounting
    date through today and include ALL previously applied action records.
    Explicit manifest attestation is required even for an empty actions list.
    """
    s = deepcopy(state)
    try:
        audit_balances(s)
        date.fromisoformat(day)
        previous = s.get('accounted_through') or s.get('last_session') or day
        if manifest['symbol'] != s['symbol'] or manifest['currency'] != 'USD':
            raise ReviewRequired('ACTION_IDENTITY_MISMATCH')
        if manifest['reviewed'] is not True or not manifest['source_urls'] or not manifest['reviewer']:
            raise ReviewRequired('ACTION_REVIEW_MISSING')
        for endpoint in ('coverage_start', 'coverage_end'):
            date.fromisoformat(manifest[endpoint])
        if not manifest['coverage_start'] <= previous <= day <= manifest['coverage_end']:
            raise ReviewRequired('ACTION_COVERAGE_INCOMPLETE')
        if not 0 <= manifest['reviewed_ms'] <= observed:
            raise ReviewRequired('ACTION_REVIEW_TIME_INVALID')
        reviewed_day=datetime.fromtimestamp(manifest['reviewed_ms']/1000,ZoneInfo('America/New_York')).date().isoformat()
        if manifest['coverage_end'] > reviewed_day:
            raise ReviewRequired('ACTION_FUTURE_COVERAGE_REJECTED')
        if any(not isinstance(url,str) or not url.startswith('https://') for url in manifest['source_urls']):
            raise ReviewRequired('ACTION_SOURCE_INVALID')
        if not all(math.isfinite(s[k]) and s[k] >= 0 for k in ('cash','units','peak')):
            raise ReviewRequired('ACCOUNT_BALANCE_INVALID')
        actions = manifest['actions']
        seen = {}; applied = s.setdefault('applied_actions', {})
        receivables = s.setdefault('dividend_receivables', {})
        journal = s.setdefault('action_ledger', [])
        for action in actions:
            ident = action['id']; ex = action['ex_date']
            if not isinstance(ident, str) or not ident or ident in seen:
                raise ReviewRequired('ACTION_DUPLICATE_ID')
            date.fromisoformat(ex)
            digest = hashlib.sha256(json.dumps(action,sort_keys=True,allow_nan=False).encode()).hexdigest()
            seen[ident] = digest
            if ident in applied and applied[ident] != digest:
                raise ReviewRequired('ACTION_REVISION_REQUIRES_REPLAY')
            if action['type'] not in ('split','cash_dividend'):
                raise ReviewRequired('ACTION_UNSUPPORTED')
            if action['type'] == 'split':
                ratio = float(action['ratio'])
                if not math.isfinite(ratio) or ratio <= 0:
                    raise ReviewRequired('ACTION_INVALID_RATIO')
            else:
                amount = float(action['cash_per_share'])
                date.fromisoformat(action['pay_date'])
                if not math.isfinite(amount) or amount < 0 or action['pay_date'] < ex:
                    raise ReviewRequired('ACTION_INVALID_DIVIDEND')
            if ident not in applied and ex <= previous and s.get('ledger'):
                raise ReviewRequired('ACTION_LATE_REQUIRES_REPLAY')
        if any(ident not in seen for ident in applied):
            raise ReviewRequired('ACTION_RECORD_REMOVED')
        due = [a for a in actions if a['id'] not in applied and previous < a['ex_date'] <= day]
        dates = [a['ex_date'] for a in due]
        if len(dates) != len(set(dates)):
            raise ReviewRequired('ACTION_SAME_DAY_ORDER_REVIEW')
        for a in sorted(due,key=lambda a:a['ex_date']):
            ident = a['id']
            effective=int(datetime.fromisoformat(a['ex_date']).replace(tzinfo=ZoneInfo('America/New_York')).timestamp()*1000)
            if a['type'] == 'split':
                units = s['units'] * float(a['ratio'])
                if not math.isclose(units,round(units),abs_tol=1e-9):
                    raise ReviewRequired('ACTION_FRACTIONAL_CASH_IN_LIEU_REVIEW')
                s['units'] = int(round(units))
                journal.append({'id':ident,'type':'split','ratio':float(a['ratio']),
                                'ex_date':a['ex_date'],'observed_ms':observed,'effective_ms':effective})
                s['quote'] = None  # Old-price marks must not survive a split.
            else:
                receivables[ident] = {'amount':s['units']*float(a['cash_per_share']),
                                     'pay_date':a['pay_date'],'paid':False}
                journal.append({'id':ident,'type':'dividend_entitlement',
                                'amount':receivables[ident]['amount'],
                                'ex_date':a['ex_date'],'observed_ms':observed,'effective_ms':effective})
            applied[ident] = seen[ident]
        for ident, r in receivables.items():
            if not r['paid'] and r['pay_date'] <= day:
                s['cash'] += r['amount']; r['paid'] = True
                journal.append({'id':ident,'type':'dividend_payment','amount':r['amount'],
                                'observed_ms':observed,'effective_ms':int(datetime.fromisoformat(r['pay_date']).replace(tzinfo=ZoneInfo('America/New_York')).timestamp()*1000)})
        s['accounted_through'] = day
        s['review_required'] = False
        s['action_review_ms'] = manifest['reviewed_ms']
        audit_balances(s)
        return s
    except ReviewRequired:
        raise
    except (KeyError,TypeError,ValueError,OverflowError):
        raise ReviewRequired('ACTION_MANIFEST_INVALID') from None


def receivable_value(state):
    return sum(r['amount'] for r in state.get('dividend_receivables',{}).values() if not r['paid'])
