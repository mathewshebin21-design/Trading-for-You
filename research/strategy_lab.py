"""Offline paper research only. No network, credentials, or order execution.

Fixed comparisons are development evidence, never an automatic strategy selector.
Input must be independently reviewed, consistently adjusted daily OHLC history.
"""
import argparse
import hashlib
import json
from dataclasses import asdict, replace
from datetime import date
from pathlib import Path
import statistics

from paper_engine import PaperAccount, Rules, load_history, metrics

STRATEGIES = ('sma_20_100', 'breakout_55_20', 'mean_reversion_20',
              'buy_hold_25', 'cash')


class ComparisonAccount(PaperAccount):
    def __init__(self, rules, strategy):
        if strategy not in STRATEGIES:
            raise ValueError('Unknown frozen strategy')
        self.strategy = strategy
        super().__init__(rules)

    def signal(self):
        if self.strategy == 'cash':
            return False
        if self.strategy == 'buy_hold_25':
            return True
        if len(self.closes) < 100:
            return False
        if self.strategy == 'sma_20_100':
            return super().signal()
        if self.strategy == 'breakout_55_20':
            # Close-only breakout: reference window excludes the newest close.
            return (self.closes[-1] >= min(self.closes[-21:-1]) if self.units
                    else self.closes[-1] > max(self.closes[-56:-1]))
        mean = statistics.mean(self.closes[-20:])
        return self.closes[-1] < mean if self.units else self.closes[-1] < mean * .98


def compare(rows, start, end, crypto=False):
    date.fromisoformat(start); date.fromisoformat(end)
    if start > end:
        raise ValueError('Reversed measurement window')
    warmup = [r for r in rows if r['date'] < start]
    measured = [r for r in rows if start <= r['date'] <= end]
    if len(warmup) < 100 or not measured:
        raise ValueError('Require 100 prior bars and a nonempty measurement window')
    # Match current simulator fees/slippage; OHLC spread remains an assumption.
    base = Rules(commission_bps=10, spread_bps=2 if crypto else 1,
                 slippage_bps=3 if crypto else 5,
                 quantum=.000001 if crypto else 1, crypto=crypto)
    results = []
    for multiplier in (1, 2):
        rules = replace(base, commission_bps=base.commission_bps * multiplier,
                        spread_bps=base.spread_bps * multiplier,
                        slippage_bps=base.slippage_bps * multiplier)
        group = []
        for strategy in STRATEGIES:
            account = ComparisonAccount(rules, strategy)
            for row in warmup + measured:
                enabled = row['date'] >= start
                account.step(row, trade_enabled=enabled,
                             benchmark=strategy == 'buy_hold_25',
                             pause_enabled=strategy not in ('buy_hold_25', 'cash'))
            # Identical liquidation convention includes exit costs in benchmarks.
            last = measured[-1]
            had_units = account.units > 0
            account.trade('SELL', last['close'], last['date'], 'terminal_measurement_close')
            account.curve[-1].update(equity=account.cash, cash=account.cash, units=0)
            result = {'strategy': strategy, 'cost_multiplier': multiplier,
                      'rules': asdict(rules), **metrics(account),
                      'terminal_liquidations': int(had_units),
                      'natural_closed_trades': len(account.closed_trades) - int(had_units)}
            group.append(result)
        benchmark = next(r for r in group if r['strategy'] == 'buy_hold_25')
        for result in group:
            result['excess_return_vs_buy_hold_pct_points'] = (
                result['net_return_pct'] - benchmark['net_return_pct'])
            result['evaluation'] = 'DEVELOPMENT_ONLY_NOT_UNSEEN'
        results.extend(group)
    return {'mode': 'PAPER_RESEARCH_ONLY', 'start': start, 'end': end,
            'measured_bars': len(measured), 'strategies': results,
            'selected_strategy': None, 'strategy_validated': False,
            'limitations': ['Previously inspected history is not unseen evidence.',
                            'Daily OHLC fills do not establish executable quotes.',
                            'Single symbols are separate accounts, not a portfolio.',
                            'Cash earns zero interest; taxes excluded.',
                            'US runtime overnight corporate-action review remains required.',
                            'No news or trader feed has been qualified.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--crypto', action='store_true')
    parser.add_argument('--reviewed-adjusted-data', action='store_true', required=True,
                        help='Explicitly attest input adjustment/calendar review')
    args = parser.parse_args()
    source = Path(args.history)
    result = compare(load_history(source, crypto=args.crypto), args.start, args.end, args.crypto)
    result['input_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    destination = Path(args.output)
    if destination.resolve() == source.resolve():
        raise ValueError('Output cannot overwrite input')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    main()
