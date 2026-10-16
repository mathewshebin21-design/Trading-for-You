"""Original offline paper hypothesis. No network, credentials or order submission.
Thresholds are frozen engineering assumptions, not validated optimal parameters.
"""
import argparse
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import statistics

from paper_engine import Rules, load_history, metrics
from strategy_lab import ComparisonAccount, STRATEGIES


@dataclass(frozen=True)
class Scenario:
    name: str
    strategy: str
    reason: str


def classify(closes):
    """Use at most 100 completed daily closes; caller executes next bar only."""
    values = list(closes)[-100:]
    if any(not math.isfinite(x) or x <= 0 for x in values):
        return Scenario('invalid', 'cash', 'invalid_close')
    if len(values) < 100:
        return Scenario('unknown', 'cash', 'warmup')
    returns = [values[i] / values[i-1] - 1 for i in range(80, 100)]
    if not all(math.isfinite(x) for x in returns):
        return Scenario('invalid', 'cash', 'nonfinite_return')
    vol = statistics.stdev(returns) * math.sqrt(252)
    if not math.isfinite(vol):
        return Scenario('invalid', 'cash', 'nonfinite_volatility')
    fast = statistics.mean(values[-20:])
    slow = statistics.mean(values)
    if not all(math.isfinite(x) for x in (fast, slow)):
        return Scenario('invalid', 'cash', 'nonfinite_average')
    displacement = fast / slow - 1
    if vol >= .40 or returns[-1] <= -.05:
        return Scenario('stress', 'cash', 'high_volatility_or_down_gap_proxy')
    if displacement < -.02:
        return Scenario('downtrend', 'cash', 'long_only_abstention')
    if displacement > .02:
        if values[-1] > max(values[-56:-1]):
            return Scenario('up_breakout', 'breakout_55_20', 'prior_55_close_high')
        return Scenario('uptrend', 'sma_20_100', 'positive_average_separation')
    if abs(displacement) <= .005 and vol <= .20:
        return Scenario('range', 'mean_reversion_20', 'low_vol_flat_averages')
    return Scenario('ambiguous', 'cash', 'no_qualified_scenario')


class ScenarioAccount(ComparisonAccount):
    def __init__(self, rules):
        if (rules.fast, rules.slow) != (20, 100):
            raise ValueError('Scenario hypothesis requires frozen 20/100 windows')
        self.scenario = Scenario('unknown', 'cash', 'warmup')
        super().__init__(rules, 'cash')

    def signal(self):
        self.scenario = classify(self.closes)
        self.strategy = self.scenario.strategy
        return super().signal()


def compare_scenarios(rows, start, end):
    from datetime import date
    date.fromisoformat(start); date.fromisoformat(end)
    if start > end:
        raise ValueError('Reversed window')
    warm = [r for r in rows if r['date'] < start]
    measured = [r for r in rows if start <= r['date'] <= end]
    if len(warm) < 100 or not measured:
        raise ValueError('Require 100 warmup bars and measurement data')
    base = Rules(commission_bps=10, spread_bps=1, slippage_bps=5, quantum=.000001)
    results = []
    for multiplier in (1, 2):
        rules = replace(base, commission_bps=10*multiplier,
                        spread_bps=multiplier, slippage_bps=5*multiplier)
        for name in ('scenario_router_v1',) + STRATEGIES:
            account = ScenarioAccount(rules) if name == 'scenario_router_v1' else ComparisonAccount(rules, name)
            counts = {}
            transitions = 0
            previous = None
            for row in warm + measured:
                enabled = row['date'] >= start
                # This decision is from the PRIOR close, before current bar.
                if enabled and name == 'scenario_router_v1':
                    key = account.scenario.name
                    counts[key] = counts.get(key, 0) + 1
                    transitions += int(previous is not None and previous != key)
                    previous = key
                account.step(row, trade_enabled=enabled, benchmark=name == 'buy_hold_25',
                             pause_enabled=name not in ('buy_hold_25', 'cash'))
            had_units = account.units > 0
            account.trade('SELL', measured[-1]['close'], measured[-1]['date'], 'terminal_measurement_close')
            account.curve[-1].update(equity=account.cash, cash=account.cash, units=0)
            results.append({'strategy': name, 'cost_multiplier': multiplier,
                            'rules': asdict(rules), **metrics(account),
                            'natural_closed_trades': len(account.closed_trades)-int(had_units),
                            'scenario_days': counts, 'scenario_transitions': transitions})
    for result in results:
        benchmark = next(r for r in results if r['strategy'] == 'buy_hold_25' and r['cost_multiplier'] == result['cost_multiplier'])
        result['excess_vs_buy_hold_pct_points'] = result['net_return_pct'] - benchmark['net_return_pct']
    return {'mode': 'OFFLINE_PAPER_RESEARCH', 'strategy_validated': False,
            'start': start, 'end': end, 'results': results,
            'limitations': ['Scenario labels are hypotheses, not ground truth.',
                            'Daily adjusted OHLC cannot establish executable quotes.',
                            'Require independent calendar and corporate-action review.',
                            'No news, liquidity, shorting, trained AI or copying is implemented.',
                            'Regime switching can add costs and underperform fixed policies.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('history', 'start', 'end', 'output'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--reviewed-adjusted-data', action='store_true', required=True)
    args = parser.parse_args()
    source, destination = Path(args.history), Path(args.output)
    if source.resolve() == destination.resolve():
        raise ValueError('Output cannot overwrite history')
    result = compare_scenarios(load_history(source), args.start, args.end)
    result['input_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
