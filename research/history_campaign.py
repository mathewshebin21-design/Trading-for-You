"""Offline 5/10-year trend research; no model training, provider calls or orders."""
import argparse
import hashlib
import json
from pathlib import Path
from paper_engine import load_history
from spy_campaign import run_campaign

SYMBOLS = {'SPY', 'AAPL', 'GLD'}


def evaluate(symbol, rows, expected_dates):
    if symbol not in SYMBOLS:
        raise ValueError('Unsupported research symbol')
    if [r['date'] for r in rows] != list(expected_dates):
        raise ValueError('Independent session calendar mismatch')
    results = {}
    for years, first in ((10, 2016), (5, 2021)):
        windows = tuple((f'{y}-01-01', f'{y}-12-31') for y in range(first, 2026))
        campaign = run_campaign(rows, expected_dates, windows)
        campaign['symbol'] = symbol
        campaign['history_years'] = years
        campaign['calendar_verified_independently'] = False
        campaign['price_verified_independently'] = False
        results[str(years)] = campaign
    return {'symbol': symbol, 'mode': 'KNOWN_HISTORY_DEVELOPMENT_ONLY',
            'measurement_end': '2025-12-31', 'campaigns': results,
            'strategy_validated': False, 'selected_strategy': None,
            'model_trained': False,
            'limits': ['Five-year windows overlap the ten-year campaign; do not pool evidence.',
                      'Known history is not untouched out-of-sample evidence.',
                      'No historical news, quotes, delisted universe or intraday coverage supplied.',
                      'Adjusted synthetic units differ from whole-share IEX execution.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--symbol', choices=sorted(SYMBOLS), required=True)
    p.add_argument('--history', required=True)
    p.add_argument('--calendar', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    history, calendar, output = map(Path, (a.history, a.calendar, a.output))
    if output.resolve() in {history.resolve(), calendar.resolve()}:
        raise ValueError('Output cannot overwrite input')
    result = evaluate(a.symbol, load_history(history), json.loads(calendar.read_text()))
    result['input_sha256'] = hashlib.sha256(history.read_bytes()).hexdigest()
    result['calendar_sha256'] = hashlib.sha256(calendar.read_bytes()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
