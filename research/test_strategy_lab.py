import unittest
from datetime import date, timedelta
from strategy_lab import ComparisonAccount, compare
from paper_engine import Rules


def fixture():
    return [{'date': (date(2020, 1, 1) + timedelta(days=i)).isoformat(),
             'open': 100+i, 'high': 101+i, 'low': 99+i,
             'close': 100+i, 'volume': 1000, 'distribution': 0}
            for i in range(130)]


class LabTests(unittest.TestCase):
    def test_matched_benchmarks_and_cost_stress(self):
        rows = fixture()
        result = compare(rows, rows[100]['date'], rows[-1]['date'])
        self.assertEqual(len(result['strategies']), 10)
        self.assertIsNone(result['selected_strategy'])
        for r in result['strategies']:
            self.assertFalse(r['strategy_validated'])
            if r['strategy'] == 'cash':
                self.assertEqual(r['net_return_pct'], 0)
                self.assertEqual(r['closed_trades'], 0)
            if r['strategy'] == 'buy_hold_25':
                self.assertEqual(r['excess_return_vs_buy_hold_pct_points'], 0)
                self.assertEqual(r['natural_closed_trades'], 0)
        base, stress = [r for r in result['strategies'] if r['strategy'] == 'buy_hold_25']
        self.assertGreater(base['net_return_pct'], stress['net_return_pct'])

    def test_signal_uses_previous_completed_bar(self):
        a = ComparisonAccount(Rules(), 'breakout_55_20')
        for r in fixture()[:100]:
            a.step(r, trade_enabled=False)
        row = fixture()[100]
        a.step(row)
        self.assertEqual(a.ledger[0]['reference'], row['open'])
        self.assertEqual(a.ledger[0]['date'], row['date'])

    def test_breakout_excludes_current_close(self):
        a = ComparisonAccount(Rules(), 'breakout_55_20')
        a.closes = [100.] * 99 + [101.]
        self.assertTrue(a.signal())
        a.units = 1
        a.closes[-1] = 99
        self.assertFalse(a.signal())

    def test_reversion_hysteresis(self):
        a = ComparisonAccount(Rules(), 'mean_reversion_20')
        a.closes = [100.] * 99 + [99.]
        self.assertFalse(a.signal())
        a.units = 1
        self.assertTrue(a.signal())
        a.units = 0
        a.closes[-1] = 90
        self.assertTrue(a.signal())

    def test_insufficient_warmup_rejected(self):
        with self.assertRaises(ValueError):
            compare(fixture(), '2020-01-02', '2020-02-01')

    def test_unknown_strategy_rejected(self):
        with self.assertRaises(ValueError):
            ComparisonAccount(Rules(), 'best_bot')

    def test_future_bars_do_not_change_result(self):
        rows = fixture()
        first = compare(rows, rows[100]['date'], rows[110]['date'])
        rows[-1]['close'] = 99999
        self.assertEqual(first, compare(rows, rows[100]['date'], rows[110]['date']))
