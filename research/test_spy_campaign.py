import copy
import unittest
from datetime import date, timedelta
from spy_campaign import run_campaign


def fixture():
    return [{'date': (date(2006, 1, 1) + timedelta(days=i)).isoformat(),
             'open': 100 + i, 'high': 101 + i, 'low': 99 + i,
             'close': 100 + i, 'volume': 1000, 'distribution': 0} for i in range(150)]


class CampaignTests(unittest.TestCase):
    def test_all_alternatives_and_stress_are_retained(self):
        rows = fixture()
        result = run_campaign(rows, [r['date'] for r in rows], [(rows[100]['date'], rows[140]['date'])])
        self.assertEqual(len(result['results']), 10)
        self.assertFalse(result['strategy_validated'])
        self.assertIsNone(result['selected_strategy'])
        refs = [r for r in result['results'] if r['strategy'] == 'buy_hold_25']
        self.assertGreater(refs[0]['net_return_pct'], refs[1]['net_return_pct'])
        self.assertEqual(refs[0]['natural_roundtrips'], 0)
        for row in result['results']:
            if row['strategy'] == 'cash':
                self.assertEqual(row['net_return_pct'], 0)
            self.assertFalse(row['strategy_validated'])

    def test_missing_session_rejected(self):
        rows = fixture()
        with self.assertRaises(ValueError):
            run_campaign(rows[:-1], [r['date'] for r in rows])

    def test_adjusted_proxy_cannot_double_count_dividends(self):
        rows = fixture()
        rows[100]['distribution'] = 1.0
        with self.assertRaisesRegex(ValueError, 'cannot also pay distributions'):
            run_campaign(rows, [r['date'] for r in rows], [(rows[100]['date'], rows[140]['date'])])

    def test_future_prices_cannot_change_earlier_window(self):
        rows = fixture()
        dates = [r['date'] for r in rows]
        window = [(rows[100]['date'], rows[140]['date'])]
        first = run_campaign(rows, dates, window)
        changed = copy.deepcopy(rows)
        changed[-1].update(open=10000, high=10001, low=9999, close=10000)
        self.assertEqual(first, run_campaign(changed, dates, window))

    def test_bad_warmup_and_ohlc_rejected(self):
        rows = fixture()
        dates = [r['date'] for r in rows]
        with self.assertRaises(ValueError):
            run_campaign(rows, dates, [(rows[99]['date'], rows[-1]['date'])])
        rows[100]['high'] = 1
        with self.assertRaises(ValueError):
            run_campaign(rows, dates, [(rows[100]['date'], rows[-1]['date'])])
