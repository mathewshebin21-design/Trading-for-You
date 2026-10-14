"""Read-only audit of saved AAPL news paper accounts; no orders or provider calls."""
import json
import math
from datetime import date
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from news_paper_lab import FINGERPRINT
from us_accounting import audit_balances, reconcile, ReviewRequired

KEYS = {'baseline:1', 'baseline:2', 'news_delay:1', 'news_delay:2'}


def review_diagnostic(folder, state, observed):
    """Inspect the existing review and dry-run reconciliation on copies only."""
    path = Path(folder).parent / 'action_reviews' / 'AAPL.json'
    lines = ['Corporate-action review file: us_automatic/action_reviews/AAPL.json']
    if not path.exists():
        return lines + ['Review file: MISSING; independently reviewed coverage is required.']
    try:
        if path.stat().st_size > 1_000_000:
            raise ValueError('Oversized review')
        manifest = json.loads(path.read_text())
        day = datetime.fromtimestamp(observed / 1000, ZoneInfo('America/New_York')).date().isoformat()
        lines.append('Review file: PRESENT; checking coverage through ' + day)
        for key in sorted(KEYS):
            try:
                reconcile(state['accounts'][key], manifest, day, observed)
                status = 'DRY_RUN_PASS'
            except ReviewRequired as error:
                # Only fixed, source-defined accounting reasons; never payload text.
                status = str(error) if str(error) in {
                    'ACTION_COVERAGE_INCOMPLETE', 'ACTION_REVIEW_MISSING',
                    'ACTION_REVIEW_TIME_INVALID', 'ACTION_FUTURE_COVERAGE_REJECTED',
                    'ACTION_IDENTITY_MISMATCH', 'ACTION_SOURCE_INVALID',
                    'ACTION_LATE_REQUIRES_REPLAY', 'ACTION_REVISION_REQUIRES_REPLAY',
                    'ACTION_RECORD_REMOVED', 'ACTION_UNSUPPORTED',
                    'ACTION_SAME_DAY_ORDER_REVIEW', 'ACTION_FRACTIONAL_CASH_IN_LIEU_REVIEW'
                } else 'ACTION_REVIEW_INVALID'
            lines.append(key + ': ' + status)
        return lines + ['Dry run only: no balances, review flags or invalid days changed.']
    except (OSError, KeyError, TypeError, ValueError, OverflowError, AttributeError):
        return lines + ['Review diagnostic: INVALID_OR_UNREADABLE; no repair performed.']


def audit(state, observed):
    if type(observed) is not int or observed < 0:
        raise ValueError('NEWS_AUDIT_OBSERVATION_INVALID')
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
                if not isinstance(action, dict):
                    raise ValueError('Invalid recorded action structure')
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
        state = json.loads(path.read_text())
        result = audit(state, observed)
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
    return lines + review_diagnostic(folder, state, observed)
