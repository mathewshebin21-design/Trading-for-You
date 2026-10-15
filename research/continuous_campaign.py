"""Offline SPY development comparisons; no provider calls, training or orders."""
import argparse
import hashlib
import json
from pathlib import Path
from paper_engine import load_history
from spy_campaign import run_campaign

WINDOWS = (('2016-01-01', '2025-12-31'),
           ('2021-01-01', '2025-12-31'),
           ('2026-01-01', '2026-09-30'))


def evaluate(rows, calendar):
    # These fixed endpoints are weekdays. Do not silently evaluate a truncated
    # requested span. Calendar provenance still needs independent verification.
    if not rows or rows[-1]['date'] < WINDOWS[-1][1]:
        raise ValueError('History ends before requested measurement endpoint')
    result = run_campaign(rows, calendar, WINDOWS)
    result['mode'] = 'CONTINUOUS_KNOWN_HISTORY_DEVELOPMENT_ONLY'
    result['model_trained'] = False
    result['independent_price_verification'] = False
    result['independent_calendar_verification_this_run'] = False
    for item in result['results']:
        dates = [r['date'] for r in rows if item['start'] <= r['date'] <= item['end']]
        item['actual_first_session'] = dates[0]
        item['actual_last_session'] = dates[-1]
    result['limitations'] += [
        'Windows overlap; comparisons are not independent and are not pooled.',
        'Initial 25% buy-and-hold allocation drifts; it is not equal dynamic exposure.',
        'Zero cash interest and omitted taxes affect comparisons.',
        'Whole-share IEX fills and live corporate-action accounting are not reproduced.',
        'No news or copied-trader strategy is tested; no model is trained.',
        'Inherited volatility, Sharpe and invested-bar metrics include 100 warmup bars; do not treat them as measurement-only statistics.',
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('history', 'calendar', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    history, calendar, output = map(Path, (args.history, args.calendar, args.output))
    if output.resolve() in (history.resolve(), calendar.resolve()):
        raise ValueError('Output cannot overwrite input')
    result = evaluate(load_history(history), json.loads(calendar.read_text()))
    result['input_sha256'] = hashlib.sha256(history.read_bytes()).hexdigest()
    result['calendar_sha256'] = hashlib.sha256(calendar.read_bytes()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
