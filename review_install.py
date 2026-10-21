"""Validate a dated review against private paper accounts in place.

Default is read-only. --install publishes a missing review atomically; it never
changes balances, flags, experiment fingerprints, or historical validity.
Run as the worker user. No network, credentials, or order endpoints.
"""
import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path
import tempfile
import time
from zoneinfo import ZoneInfo

from us_accounting import reconcile, ReviewRequired
from us_paper import account


def read(path):
    if path.stat().st_size > 20_000_000:
        raise ValueError('FILE_TOO_LARGE')
    return json.loads(path.read_text())


def run(state_root, source, observed, through=None, install=False):
    manifest = read(Path(source))
    symbol = manifest['symbol']
    if symbol not in ('AAPL', 'SPY', 'GLD'):
        raise ValueError('SYMBOL_UNSUPPORTED')
    today = datetime.fromtimestamp(observed/1000, ZoneInfo('America/New_York')).date().isoformat()
    day = through or today
    date.fromisoformat(day)
    if day > today:
        raise ValueError('FUTURE_REVIEW_REJECTED')
    root = Path(state_root)/'us_automatic'
    states = []
    original = root/(symbol+'_state.json')
    if original.exists():
        s = read(original)
        if s.get('version') != 'US.1':
            raise ValueError('ACCOUNT_VERSION_INVALID')
        states.append(s)
    for path in (root/'lab'/(symbol+'_lab.json'), root/'news_lab'/(symbol+'_news_lab.json')):
        if path.exists():
            record = read(path)
            if not isinstance(record.get('accounts'), dict) or not record['accounts']:
                raise ValueError('LAB_ACCOUNTS_MISSING')
            if path.parent.name == 'news_lab':
                from news_paper_lab import FINGERPRINT, RULES
                expected={f'{name}:{cost}' for name in RULES['strategies'] for cost in RULES['costs']}
                version='NEWSLAB.1'
            else:
                from prospective_lab import FINGERPRINT, RULES, STRATEGIES
                expected={f'{name}:{cost}' for name in STRATEGIES for cost in (1,2)}
                version='LAB.1'
                if (record.get('symbol') != symbol or record.get('currency') != 'USD'
                    or json.dumps(record.get('rules'),sort_keys=True) != json.dumps(RULES,sort_keys=True)):
                    raise ValueError('LAB_RULES_OR_IDENTITY_INVALID')
            if (record.get('version') != version or record.get('fingerprint') != FINGERPRINT
                or set(record['accounts']) != expected):
                raise ValueError('LAB_VERSION_OR_ACCOUNTS_INVALID')
            states.extend(record['accounts'].values())
    if not states:
        raise ValueError('NO_SAVED_ACCOUNTS')
    for s in states + [account(symbol)]:
        if s.get('symbol') != symbol or s.get('currency') != 'USD':
            raise ValueError('ACCOUNT_IDENTITY_INVALID')
        reconcile(s, manifest, day, observed)
    result = {'status':'VALIDATED_NO_ACCOUNT_WRITES', 'symbol':symbol,
              'accounts_checked':len(states), 'through':day,
              'current_day_covered':day == today, 'installed':False}
    if not install:
        return result
    target = root/'action_reviews'/(symbol+'.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError('EXISTING_REVIEW_PRESERVED')
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(manifest, handle, indent=2, allow_nan=False)
            handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
        os.link(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    result.update(status='REVIEW_INSTALLED_NO_ACCOUNT_WRITES', installed=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', required=True)
    parser.add_argument('--review', required=True)
    parser.add_argument('--through', help='Reviewed historical date; never extends coverage')
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    try:
        result = run(args.state_root, args.review, int(time.time()*1000), args.through, args.install)
    except Exception as error:
        # Never echo malformed JSON, provider data, paths or private journal values.
        reason = str(error) if isinstance(error, ReviewRequired) else 'INPUT_OR_INSTALL_INVALID'
        print(json.dumps({'status':'REFUSED_NO_ACCOUNT_WRITES', 'reason':reason}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
