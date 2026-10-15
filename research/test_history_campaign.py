import copy
import unittest
from datetime import date, timedelta
from history_campaign import evaluate


def fixture():
    start = date(2015, 1, 1)
    return [{'date':(start + timedelta(days=i)).isoformat(), 'open':100.,
             'high':101., 'low':99., 'close':100., 'volume':1000,
             'distribution':0} for i in range((date(2026,1,1)-start).days)]


class HistoryCampaignTests(unittest.TestCase):
    def test_future_prices_do_not_change_measured_history(self):
        rows = fixture(); dates = [r['date'] for r in rows]
        first = evaluate('AAPL', rows, dates)
        changed = copy.deepcopy(rows)
        changed.append({'date':'2026-01-01', 'open':9000., 'high':9001.,
                        'low':8999., 'close':9000., 'volume':1000, 'distribution':0})
        second = evaluate('AAPL', changed, dates + ['2026-01-01'])
        self.assertEqual(first, second)
        self.assertFalse(first['model_trained'])
        self.assertFalse(first['strategy_validated'])
        self.assertEqual(len(first['campaigns']['10']['results']),100)
        self.assertEqual(len(first['campaigns']['5']['results']),50)

    def test_missing_calendar_and_insufficient_history_fail(self):
        rows = fixture(); dates = [r['date'] for r in rows]
        with self.assertRaises(ValueError): evaluate('SPY', rows[:-1], dates)
        with self.assertRaises(ValueError): evaluate('SPY', rows[365:], dates[365:])
        with self.assertRaises(ValueError): evaluate('UNKNOWN', rows, dates)
