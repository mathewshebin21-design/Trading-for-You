"""Frozen offline SPY development campaign. Paper only; never selects a winner."""
import argparse
from dataclasses import asdict, replace
from datetime import date
import hashlib
import json
from pathlib import Path
from paper_engine import Rules, load_history, metrics
from strategy_lab import ComparisonAccount, STRATEGIES

WINDOWS = tuple((f'{year}-01-01', f'{year}-12-31') for year in range(2007, 2026)) + (('2026-01-01', '2026-09-30'),)


def run_campaign(rows, expected_dates, windows=WINDOWS):
    dates = [row['date'] for row in rows]
    if not dates or dates != sorted(set(dates)) or dates != list(expected_dates):
        raise ValueError('Calendar mismatch, duplicate, missing or unordered sessions')
    for day in dates:
        date.fromisoformat(day)
    if any(row.get('distribution', 0) != 0 for row in rows):
        raise ValueError('Adjusted proxy cannot also pay distributions')
    baseline = Rules(commission_bps=10, spread_bps=1, slippage_bps=5, quantum=.000001)
    results = []
    for start, end in windows:
        date.fromisoformat(start); date.fromisoformat(end)
        if start > end:
            raise ValueError('Reversed window')
        prior = [row for row in rows if row['date'] < start][-100:]
        measured = [row for row in rows if start <= row['date'] <= end]
        if len(prior) < 100 or not measured:
            raise ValueError('Insufficient warmup or measurement data')
        for multiplier in (1, 2):
            group = []
            rules = replace(baseline, commission_bps=10 * multiplier,
                            spread_bps=multiplier, slippage_bps=5 * multiplier)
            for strategy in STRATEGIES:
                account = ComparisonAccount(rules, strategy)
                for row in prior:
                    account.step(row, trade_enabled=False)
                for row in measured:
                    account.step(row, benchmark=strategy == 'buy_hold_25',
                                 pause_enabled=strategy not in ('buy_hold_25', 'cash'))
                last = measured[-1]
                had_units = account.units > 0
                account.trade('SELL', last['close'], last['date'], 'terminal_measurement_close')
                account.curve[-1].update(equity=account.cash, cash=account.cash, units=0)
                group.append({'start': start, 'end': end, 'measured_sessions': len(measured),
                              'strategy': strategy, 'cost_multiplier': multiplier,
                              'rules': asdict(rules), **metrics(account),
                              'terminal_liquidations': int(had_units),
                              'natural_roundtrips': len(account.closed_trades) - int(had_units)})
            reference = next(row for row in group if row['strategy'] == 'buy_hold_25')
            for result in group:
                result['excess_return_pct_points'] = result['net_return_pct'] - reference['net_return_pct']
            results.extend(group)
    return {'symbol': 'SPY', 'mode': 'RETROSPECTIVE_DEVELOPMENT_ONLY',
            'strategy_validated': False, 'selected_strategy': None,
            'results': results,
            'limitations': ['Adjusted synthetic units are not executable whole shares.',
                            'Input prices/actions require independent cross-verification.',
                            'Yearly starts are independent; do not compound or pool them.',
                            'Known history and repeated comparisons cannot prove an edge.',
                            'Daily-close drawdown trigger is not a guaranteed loss cap.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', required=True)
    parser.add_argument('--calendar', required=True, help='JSON array of independently checked expected ISO sessions')
    parser.add_argument('--output', required=True)
    parser.add_argument('--reviewed-adjusted-proxy', action='store_true', required=True)
    args = parser.parse_args()
    history, calendar, output = map(Path, (args.history, args.calendar, args.output))
    if output.resolve() in (history.resolve(), calendar.resolve()):
        raise ValueError('Output cannot overwrite input')
    result = run_campaign(load_history(history), json.loads(calendar.read_text()))
    result['input_sha256'] = hashlib.sha256(history.read_bytes()).hexdigest()
    result['calendar_sha256'] = hashlib.sha256(calendar.read_bytes()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
