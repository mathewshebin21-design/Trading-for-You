"""Offline paper-lab observation audit. Logs cannot certify ledgers or returns."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ACCOUNTS = {'baseline:1', 'baseline:2', 'news_delay:1', 'news_delay:2'}
NONBLOCKING_STATUSES = {'NO_ACTION', 'SIMULATED_BUY', 'SIMULATED_SELL', 'MARKET_CLOSED'}
WAITING_STATUSES = {'AWAITING_POST_DECISION_QUOTE'}


def audit(rows):
    if not rows:
        raise ValueError('No observations to audit')
    previous = None
    gaps, invalid = [], []
    waiting_counts = {key: {} for key in sorted(ACCOUNTS)}
    unknown_counts = {key: {} for key in sorted(ACCOUNTS)}
    blocked_counts = {key: {} for key in sorted(ACCOUNTS)}
    status_counts = {key: {} for key in sorted(ACCOUNTS)}
    for row in rows:
        observed = row['observed_ms']
        if type(observed) is not int or observed < 0:
            raise ValueError('Invalid observation time')
        if previous is not None and observed <= previous['observed_ms']:
            raise ValueError('Duplicate or unordered observations')
        if row.get('paper_only') is not True:
            raise ValueError('Paper-only marker missing')
        if type(row.get('coverage_valid')) is not bool or set(row['statuses']) != ACCOUNTS:
            raise ValueError('Incomplete health record')
        day = datetime.fromtimestamp(observed / 1000, ZoneInfo('America/New_York')).date().isoformat()
        if previous is not None:
            prev_day = datetime.fromtimestamp(previous['observed_ms'] / 1000, ZoneInfo('America/New_York')).date().isoformat()
            elapsed = observed - previous['observed_ms']
            if day == prev_day and elapsed > 600000:
                gaps.append({'day': day, 'from_ms': previous['observed_ms'],
                             'to_ms': observed, 'seconds': elapsed / 1000})
        if not row['coverage_valid']:
            invalid.append(observed)
        for key, status in row['statuses'].items():
            if not isinstance(status, str) or not status:
                raise ValueError('Invalid account status')
            status_counts[key][status] = status_counts[key].get(status, 0) + 1
            if status in WAITING_STATUSES:
                waiting_counts[key][status] = waiting_counts[key].get(status, 0) + 1
            elif (status in {'CORPORATE_ACTION_REVIEW_REQUIRED', 'ENTRY_PAUSED', 'REJECTED_SIZE'}
                    or status.startswith(('NO_FILL_', 'NEWS_COVERAGE_', 'NEWS_DELAY_'))):
                blocked_counts[key][status] = blocked_counts[key].get(status, 0) + 1
            elif status not in NONBLOCKING_STATUSES:
                unknown_counts[key][status] = unknown_counts[key].get(status, 0) + 1
        previous = row
    return {'mode': 'PAPER_LOG_AUDIT_ONLY', 'observations': len(rows),
            'first_observed_ms': rows[0]['observed_ms'], 'last_observed_ms': rows[-1]['observed_ms'],
            'invalid_news_coverage_observations': invalid, 'candidate_observation_gaps': gaps,
            'status_counts': status_counts, 'session_completeness_verified': False,
            'ledger_reconciled': False, 'strategy_validated': False,
            'blocked_status_counts': blocked_counts,
            'waiting_status_counts': waiting_counts,
            'unknown_status_counts': unknown_counts,
            'review_required': bool(gaps or invalid or any(blocked_counts.values())
                                    or any(unknown_counts.values())),
            'limitations': ['Bounded logs may omit observations; gaps require persisted-ledger review.',
                            'News coverage is not full quote or session coverage.',
                            'No session calendar, balances, quotes or corporate-action records are certified.',
                            'No P/L, trade count or winner can be inferred from health statuses.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='JSON array of sanitized NEWS_LAB_HEALTH records')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source, destination = Path(args.input), Path(args.output)
    if source.resolve() == destination.resolve():
        raise ValueError('Output cannot overwrite input')
    result = audit(json.loads(source.read_text()))
    result['input_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
