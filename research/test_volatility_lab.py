"""Synthetic accounting/timing fixtures; no market-performance evidence."""
import copy
import math
import unittest
from paper_engine import Rules
from volatility_lab import SizedAccount, weight


def bar(day, close=100., opening=100.):
    return {'date': day, 'open': opening, 'close': close, 'high': max(opening, close)+1,
            'low': min(opening, close)-1, 'volume': 1000, 'distribution': 0}


def ready():
    a = SizedAccount(Rules(commission_bps=10, spread_bps=1, slippage_bps=5, quantum=.000001))
    a.closes = [100 * (1.001 if i % 2 else 1) for i in range(100)]
    a.target = True
    a.last_date = '2026-03-06'
    return a


class VolatilityTests(unittest.TestCase):
    def test_weight_formula_and_invalid_inputs(self):
        closes = [100 * (1.01 ** (i % 2)) for i in range(21)]
        import statistics
        expected = min(.25, .02 / (statistics.stdev([b/a-1 for a,b in zip(closes, closes[1:])])*math.sqrt(252)))
        self.assertAlmostEqual(weight(closes), expected)
        for values in ([100.]*21, [100.]*20, [100.]*20+[float('nan')], [100.]*20+[0]):
            self.assertIsNone(weight(values))

    def test_partial_rebalances_replay_cash_and_complete_cycle_pnl(self):
        a = ready()
        for target, price in ((.25,100),(.1,110),(.2,90),(0.,105)):
            a.rebalance(target, price, '2026-03-09', 'fixture')
            self.assertGreaterEqual(a.cash, 0)
            self.assertLessEqual(a.units*price/(a.cash+a.units*price), target+1e-10)
        replay = a.rules.capital
        for fill in a.ledger:
            amount = fill['quantity'] * fill['fill_price']
            replay += -amount-fill['commission'] if fill['side']=='BUY' else amount-fill['commission']
        self.assertAlmostEqual(replay, a.cash)
        self.assertEqual(len(a.closed_trades), 1)
        self.assertAlmostEqual(a.closed_trades[0]['net_pnl'], a.cash-a.rules.capital)
        self.assertEqual(a.units, 0)

    def test_only_first_week_session_rebalances_but_bearish_exits_immediately(self):
        a=ready();a.step(bar('2026-03-09'));self.assertEqual(len(a.ledger),1)
        a.target=True  # Hold direction fixed to isolate weekly scheduling.
        a.step(bar('2026-03-10'));self.assertEqual(len(a.ledger),1)
        a.target=False;a.step(bar('2026-03-11'))
        self.assertEqual(a.units,0);self.assertEqual(len(a.ledger),2)

    def test_same_day_close_cannot_change_open_trade(self):
        a=ready();b=copy.deepcopy(a)
        a.step(bar('2026-03-09',close=101));b.step(bar('2026-03-09',close=80))
        self.assertEqual(a.ledger,b.ledger)

    def test_drawdown_pause_persists_and_exits_before_weekly_rebalance(self):
        a=ready();a.rebalance(.25,100,'2026-03-06','fixture')
        a.step(bar('2026-03-09',close=50))
        self.assertTrue(a.paused)
        a.step(bar('2026-03-10',close=50,opening=50));self.assertEqual(a.units,0)
        a.target=True;a.step(bar('2026-03-16'))
        self.assertTrue(a.paused);self.assertEqual(a.units,0)

    def test_invalid_bars_refused_without_mutating_account(self):
        for change in ({'distribution':1},{'open':float('nan')},{'date':'2026-03-06'}):
            a=ready();before=copy.deepcopy(a.__dict__);bad=bar('2026-03-09');bad.update(change)
            with self.assertRaises(ValueError):a.step(bad)
            self.assertEqual(a.__dict__,before)

    def test_warmup_has_no_fills_or_measurement_returns(self):
        a=ready();a.step(bar('2026-03-09'),trade_enabled=False)
        self.assertEqual(a.ledger,[]);self.assertEqual(a.curve,[])
