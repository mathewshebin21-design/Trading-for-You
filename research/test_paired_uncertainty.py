import copy
import math
import unittest
from datetime import date, timedelta
from paired_uncertainty import paired_interval


def fixture():
    dates = [(date(2026, 1, 1) + timedelta(days=i)).isoformat() for i in range(41)]
    rows = [{'date': day, 'valid': True, 'strategy_equity': 10000 * 1.001 ** i,
             'benchmark_equity': 10000 * 1.001 ** i} for i, day in enumerate(dates)]
    return rows, dates


class PairedUncertaintyTests(unittest.TestCase):
    def test_identical_accounts_have_zero_excess(self):
        rows, dates = fixture()
        result = paired_interval(rows, dates)
        self.assertEqual(result['descriptive_95pct_percentile_interval'], [0, 0])
        self.assertFalse(result['strategy_validated'])
        self.assertIsNone(result['selected_strategy'])

    def test_missing_invalid_and_reordered_days_rejected(self):
        rows, dates = fixture()
        invalid = copy.deepcopy(rows)
        invalid[20]['valid'] = False
        for bad in (rows[:20] + rows[21:], invalid, list(reversed(rows)), rows + rows[-1:]):
            with self.assertRaises(ValueError):
                paired_interval(bad, dates)

    def test_numeric_corruption_rejected(self):
        rows, dates = fixture()
        for value in (math.nan, math.inf, 0, -1, True, '10000'):
            bad = copy.deepcopy(rows)
            bad[10]['strategy_equity'] = value
            with self.assertRaises(ValueError):
                paired_interval(bad, dates)

    def test_short_sample_and_bad_configuration_rejected(self):
        rows, dates = fixture()
        with self.assertRaises(ValueError):
            paired_interval(rows[:10], dates[:10])
        for kwargs in ({'block_length': 0}, {'block_length': True}, {'samples': 99}, {'samples': 10001}, {'seed': True}):
            with self.assertRaises(ValueError):
                paired_interval(rows, dates, **kwargs)

    def test_repeatable_and_does_not_mutate_input(self):
        rows, dates = fixture()
        for i, row in enumerate(rows):
            row['strategy_equity'] *= 1 + .01 * math.sin(i)
        before = copy.deepcopy(rows)
        self.assertEqual(paired_interval(rows, dates, seed=42), paired_interval(rows, dates, seed=42))
        self.assertEqual(rows, before)

    def test_known_constant_daily_excess(self):
        rows, dates = fixture()
        for i, row in enumerate(rows):
            row['strategy_equity'] = 10000 * 1.002 ** i
        result = paired_interval(rows, dates)
        self.assertAlmostEqual(result['mean_daily_excess_return'], .001)

