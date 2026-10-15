"""Synthetic correctness fixtures, not historical market evidence."""
import copy
from datetime import date, timedelta
import unittest
from continuous_campaign import evaluate


def fixture():
    start = date(2015, 1, 1)
    return [{'date': (start + timedelta(days=i)).isoformat(), 'open': 100.,
             'high': 101., 'low': 99., 'close': 100., 'volume': 1000,
             'distribution': 0} for i in range((date(2026, 10, 1) - start).days)]


class ContinuousCampaignTests(unittest.TestCase):
    def test_missing_or_truncated_history_refused(self):
        rows = fixture(); calendar = [r['date'] for r in rows]
        with self.assertRaisesRegex(ValueError, 'endpoint'):
            evaluate(rows[:-1], calendar[:-1])
        with self.assertRaises(ValueError):
            evaluate(rows[:500] + rows[501:], calendar)

    def test_future_bars_cannot_change_measured_results_or_inputs(self):
        rows = fixture(); before = copy.deepcopy(rows)
        first = evaluate(rows, [r['date'] for r in rows])
        later = rows + [dict(rows[-1], date='2026-10-01', open=900., high=901., low=899., close=900.)]
        second = evaluate(later, [r['date'] for r in later])
        self.assertEqual(first, second)
        self.assertEqual(rows, before)
        self.assertEqual(len(first['results']), 30)
        self.assertFalse(first['model_trained'])
        self.assertFalse(first['strategy_validated'])
