"""Read-only audit of saved AAPL news paper accounts; no orders or provider calls."""
import json
import math
from datetime import date
from pathlib import Path
from news_paper_lab import FINGERPRINT
from us_accounting import audit_balances

KEYS = {'baseline:1', 'baseline:2', 'news_delay:1', 'news_delay:2'}


def audit(state, observed):
    if not isinstance(state, dict):
        raise ValueError('NEWS_AUDIT_STATE_INVALID')
    if (state.get('version') != 'NEWSLAB.1' or state.get('fingerprint') != FINGERPRINT
            or set(state.get('accounts', {})) != KEYS):
        raise ValueError('NEWS_AUDIT_IDENTITY_OR_RULES_MISMATCH')
    start = state['started_ms']
    if type(start) is not int or not 0 <= start <= observed:
        raise ValueError('NEWS_AUDIT_START_INVALID')
    gaps = state['coverage_gaps']
    if type(gaps) is not int or gaps < 0:
        raise ValueError('NEWS_AUDIT_GAP_COUNT_INVALID')
    accounts = {}
    for key in sorted(KEYS):
        a = state['accounts'][key]
        if not isinstance(a, dict):
            raise ValueError('NEWS_AUDIT_ACCOUNT_INVALID')
        result = {'replay': 'FAILED', 'fills': None, 'saved_mark_age_seconds': None}
        try:
            if a['symbol'] != 'AAPL' or a['currency'] != 'USD' or a['version'] != 'US.1':
                raise ValueError('Invalid account identity')
            if not all(type(a[k]) in (int, float) and math.isfinite(a[k]) and a[k] >= 0
                       for k in ('cash', 'units')):
                raise ValueError('Invalid balances')
            previous = start - 1
            for t in a['ledger']:
                event, decision = t['event_ms'], t['decision_ms']
                if (t.get('mode') != 'PAPER_ONLY' or type(event) is not int
                        or type(decision) is not int or not start <= decision < event <= observed
                        or event <= previous):
                    raise ValueError('Invalid fill timing or mode')
                previous = event
            for action in a.get('action_ledger', []):
                if type(action.get('effective_ms')) is not int or not 0 <= action['effective_ms'] <= observed:
                    raise ValueError('Invalid recorded action time')
                field = 'ratio' if action.get('type') == 'split' else 'amount'
                value = action[field]
                if (type(value) not in (int, float) or not math.isfinite(value)
                        or value < 0 or (field == 'ratio' and value == 0)):
                    raise ValueError('Invalid recorded action')
            audit_balances(a)
            result.update(replay='PASS', fills=len(a['ledger']))
        except (KeyError, TypeError, ValueError, OverflowError):
            pass  # Fixed status only; never echo private file/provider text.
        q = a.get('quote')
        event = q.get('event_ms') if isinstance(q, dict) else None
        if type(event) is int and start <= event <= observed:
            result['saved_mark_age_seconds'] = (observed - event) / 1000
        result['corporate_action_review_required'] = a.get('review_required') is not False
        accounts[key] = result
    invalid_days = []
    marks = state.get('daily_marks', {})
    if not isinstance(marks, dict):
        raise ValueError('NEWS_AUDIT_MARKS_INVALID')
    for day, mark in sorted(marks.items()):
        date.fromisoformat(day)
        if not isinstance(mark, dict) or mark.get('valid') is not True:
            invalid_days.append(day)
    return {'mode': 'PAPER_ONLY', 'accounts': accounts, 'coverage_gaps': gaps,
            'invalid_comparison_days': invalid_days, 'recorded_days': len(marks),
            'ledger_reconciled': all(a['replay'] == 'PASS' for a in accounts.values()),
            'session_completeness_verified': False, 'strategy_validated': False}


def report(folder, observed):
    lines = ['AAPL NEWS PAPER AUDIT — read-only; strategy unvalidated.']
    path = Path(folder) / 'AAPL_news_lab.json'
    if not path.exists():
        return lines + ['No saved news-lab accounts to audit.']
    try:
        # Bounded reader, single atomic-state snapshot. No state repair or write.
        if path.stat().st_size > 20_000_000:
            raise ValueError('Oversized state')
        result = audit(json.loads(path.read_text()), observed)
    except (OSError, KeyError, TypeError, ValueError, OverflowError):
        return lines + ['AUDIT_FAILED: saved state unreadable or identity/rules invalid. No repair performed.']
    lines.append('Recorded-action balance replay: ' + ('PASS' if result['ledger_reconciled'] else 'FAILED'))
    for key, a in result['accounts'].items():
        age = a['saved_mark_age_seconds']
        age_text = f'{age:.0f}s' if age is not None else 'unavailable'
        lines.append(f"{key}: replay {a['replay']}; recorded fills {a['fills']}; saved mark age {age_text}; action review {a['corporate_action_review_required']}")
    lines.append(f"Recorded coverage gaps: {result['coverage_gaps']}; recorded days: {result['recorded_days']}; invalid comparison days: {len(result['invalid_comparison_days'])}")
    if result['invalid_comparison_days']:
        lines.append('Invalid days: ' + ', '.join(result['invalid_comparison_days'][:20]))
    lines += ['Replay checks recorded arithmetic, not independent corporate-action evidence.',
              'Saved marks may be old outside market hours; this command fetches no quotes.',
              'Session completeness NOT verified. No P/L or profitability certification.']
    return lines
