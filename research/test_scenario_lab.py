"""Synthetic fixture evidence only; no assertion of trading edge."""
import math
import unittest
from datetime import date, timedelta
from paper_engine import Rules
from scenario_lab import ScenarioAccount, classify, compare_scenarios


def rows(prices):
    return [dict(date=(date(2020, 1, 1)+timedelta(days=i)).isoformat(),
                 open=p, high=p, low=p, close=p, volume=1000)
            for i, p in enumerate(prices)]


class ScenarioTests(unittest.TestCase):
    def test_warmup_invalid_and_extreme(self):
        self.assertEqual(classify([100]*99).strategy, 'cash')
        for value in (0, -1, math.nan, math.inf):
            self.assertEqual(classify([100]*99+[value]).name, 'invalid')
        self.assertEqual(classify([1e-308]*99+[1e308]).name, 'invalid')

    def test_scenario_boundaries_and_routing(self):
        self.assertEqual(classify([100]*100).name, 'range')
        self.assertEqual(classify([200-i for i in range(100)]).name, 'downtrend')
        self.assertEqual(classify([100+i for i in range(100)]).name, 'up_breakout')
        self.assertEqual(classify([100+i for i in range(99)]+[190]).name, 'uptrend')
        self.assertEqual(classify([100]*80+[101]*20).name, 'ambiguous')
        self.assertEqual(classify([100]*99+[94]).name, 'stress')

    def test_execution_uses_previous_completed_close(self):
        account = ScenarioAccount(Rules())
        bars = rows([100+i for i in range(101)])
        for bar in bars[:100]:
            account.step(bar, trade_enabled=False)
        self.assertEqual(account.ledger, [])
        account.step(bars[100])
        self.assertEqual(account.ledger[0]['reference'], bars[100]['open'])
        self.assertEqual(account.ledger[0]['date'], bars[100]['date'])

    def test_future_perturbation_cannot_change_prefix(self):
        common = rows([100+i*.1 for i in range(120)])
        a, b = ScenarioAccount(Rules()), ScenarioAccount(Rules())
        for bar in common:
            a.step(bar); b.step(bar)
        prefix = list(a.ledger)
        later = rows([112]*120+[1])[120]
        b.step(later)
        self.assertEqual(a.ledger, prefix)
        self.assertEqual(b.ledger[:len(prefix)], prefix)
        # The crash is observed at close; it cannot cause a same-open exit.
        self.assertEqual(len(b.ledger), len(prefix))
        self.assertFalse(b.target)

    def test_pause_cannot_be_cleared_by_scenario(self):
        account = ScenarioAccount(Rules())
        for bar in rows([100+i for i in range(101)]):
            account.step(bar)
        account.paused = True
        account.step(rows([100+i for i in range(102)])[101])
        self.assertEqual(account.units, 0)
        self.assertTrue(account.paused)
        self.assertEqual(account.ledger[-1]['reason'], 'drawdown_pause')

    def test_comparison_costs_benchmarks_and_counts(self):
        data = rows([100+i*.1 for i in range(130)])
        result = compare_scenarios(data, data[100]['date'], data[-1]['date'])
        self.assertEqual(len(result['results']), 12)
        routed = [r for r in result['results'] if r['strategy'] == 'scenario_router_v1']
        self.assertEqual(sum(routed[0]['scenario_days'].values()), 30)
        self.assertLessEqual(routed[1]['net_return_pct'], routed[0]['net_return_pct'])
        self.assertFalse(result['strategy_validated'])
        self.assertTrue(all('excess_vs_buy_hold_pct_points' in r for r in result['results']))

    def test_frozen_windows_and_insufficient_data(self):
        with self.assertRaises(ValueError):
            ScenarioAccount(Rules(fast=10))
        with self.assertRaises(ValueError):
            compare_scenarios(rows([100]*100), '2020-01-10', '2020-02-01')


if __name__ == '__main__':
    unittest.main()
