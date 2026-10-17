"""Read-only paper-account review check. No state writes, network or orders."""
import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from news_ledger_audit import audit, KEYS
from us_accounting import reconcile, ReviewRequired

REASONS = {
    'ACTION_COVERAGE_INCOMPLETE', 'ACTION_REVIEW_MISSING',
    'ACTION_REVIEW_TIME_INVALID', 'ACTION_FUTURE_COVERAGE_REJECTED',
    'ACTION_IDENTITY_MISMATCH', 'ACTION_SOURCE_INVALID',
    'ACTION_LATE_REQUIRES_REPLAY', 'ACTION_REVISION_REQUIRES_REPLAY',
    'ACTION_RECORD_REMOVED', 'ACTION_UNSUPPORTED', 'ACTION_DUPLICATE_ID',
    'ACTION_SAME_DAY_ORDER_REVIEW', 'ACTION_FRACTIONAL_CASH_IN_LIEU_REVIEW',
    'ACTION_INVALID_RATIO', 'ACTION_INVALID_DIVIDEND', 'ACTION_MANIFEST_INVALID',
    'ACCOUNT_BALANCE_INVALID', 'LEDGER_FILL_INVALID', 'LEDGER_EVENT_INVALID',
    'LEDGER_NEGATIVE_BALANCE', 'LEDGER_BALANCE_MISMATCH',
}


def read_json(path):
    with Path(path).open('rb') as handle:
        content = handle.read(20_000_001)
    if len(content) > 20_000_000:
        raise ValueError('oversized input')
    return json.loads(content)


def check(root, review, day, observed):
    """Reconcile snapshots on in-memory copies; never publish input content."""
    date.fromisoformat(day)
    if type(observed) is not int or observed < 0:
        raise ValueError('Invalid check time')
    today = datetime.fromtimestamp(observed/1000, ZoneInfo('America/New_York')).date().isoformat()
    if day > today:
        raise ValueError('Cannot audit a future date')
    results = {}
    result = {'mode': 'READ_ONLY_PAPER_REVIEW_CHECK', 'day': day,
              'accounts': results, 'all_required_accounts_present': False,
              'all_copied_reconciliations_passed': False,
              'production_modified': False, 'strategy_validated': False,
              'limitations': 'Recorded arithmetic and supplied manifest only; no independent ledger or session certification. No repair performed.'}
    try:
        manifest = read_json(review)
    except (OSError, ValueError, TypeError, UnicodeError):
        result['review_status'] = 'UNREADABLE_OR_INVALID'
        return result
    result['review_status'] = 'LOADED_NOT_INDEPENDENTLY_VERIFIED_BY_SCRIPT'
    folder = Path(root)/'us_automatic'
    candidates = {}
    try:
        original = read_json(folder/'AAPL_state.json')
        if original.get('version') != 'US.1':
            raise ValueError('Invalid version')
        candidates['original'] = original
    except FileNotFoundError:
        results['original'] = 'MISSING'
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError):
        results['original'] = 'UNREADABLE_OR_INVALID'
    try:
        lab = read_json(folder/'news_lab'/'AAPL_news_lab.json')
        checked = audit(lab, observed)
        for key in sorted(KEYS):
            if checked['accounts'][key]['replay'] != 'PASS':
                results[key] = 'RECORDED_LEDGER_AUDIT_FAILED'
            else:
                candidates[key] = lab['accounts'][key]
    except FileNotFoundError:
        results['news_lab'] = 'MISSING'
    except (OSError, ValueError, TypeError, KeyError, OverflowError, AttributeError, UnicodeError):
        results['news_lab'] = 'UNREADABLE_OR_INVALID'
    for name, state in candidates.items():
        try:
            reconcile(state, manifest, day, observed)
            results[name] = 'COPIED_RECONCILIATION_PASS'
        except ReviewRequired as error:
            results[name] = str(error) if str(error) in REASONS else 'REVIEW_FAILED'
        except (TypeError, KeyError, ValueError, OverflowError, AttributeError):
            results[name] = 'REVIEW_FAILED'
    required = {'original'} | KEYS
    result['all_required_accounts_present'] = required <= results.keys() and 'news_lab' not in results and results.get('original') not in {'MISSING', 'UNREADABLE_OR_INVALID'}
    result['all_copied_reconciliations_passed'] = (
        result['all_required_accounts_present'] and
        all(results[key] == 'COPIED_RECONCILIATION_PASS' for key in required))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', required=True)
    parser.add_argument('--review', required=True)
    parser.add_argument('--through', required=True, help='Explicit historical New York date')
    args = parser.parse_args()
    result = check(args.state_root, args.review, args.through,
                   int(datetime.now(timezone.utc).timestamp()*1000))
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0 if result['all_copied_reconciliations_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
