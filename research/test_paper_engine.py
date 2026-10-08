"""Accounting and timing checks for the paper-only engine."""
import unittest
from dataclasses import replace
from paper_engine import Rules, PaperAccount, replay, metrics


def bar(day, open_=100, close=100, distribution=0):
    return {'date':day,'open':open_,'high':max(open_,close)+1,'low':min(open_,close)-1,
            'close':close,'volume':1000,'distribution':distribution}


class PaperEngineChecks(unittest.TestCase):
    def setUp(self):
        self.rules=Rules(fast=1,slow=2,commission_bps=0,spread_bps=0,slippage_bps=0)

    def test_signal_fills_next_open(self):
        a=PaperAccount(self.rules)
        a.step(bar('2026-01-01',100,100))
        a.step(bar('2026-01-02',100,110))
        self.assertEqual(a.ledger,[])
        a.step(bar('2026-01-03',120,130))
        self.assertEqual(a.ledger[0]['date'],'2026-01-03')
        self.assertEqual(a.ledger[0]['reference'],120)

    def test_distribution_on_overnight_holding(self):
        a=PaperAccount(self.rules)
        a.step(bar('2026-01-01'),benchmark=True)
        a.step(bar('2026-01-02',100,100,2),benchmark=True)
        self.assertEqual(a.cash,7550)
        a.trade('SELL',100,'2026-01-02','test')
        self.assertEqual(a.closed_trades[0]['net_pnl'],50)

    def test_entry_on_ex_date_does_not_get_distribution(self):
        a=PaperAccount(self.rules)
        a.step(bar('2026-01-01',distribution=2),benchmark=True)
        self.assertEqual(a.cash,7500)

    def test_costs_and_cash_reconcile(self):
        r=replace(self.rules,commission_bps=10,spread_bps=10,slippage_bps=10)
        a=PaperAccount(r)
        a.step(bar('2026-01-01'),benchmark=True)
        self.assertLessEqual(10000-a.cash,2500)
        a.trade('SELL',100,'2026-01-02','test')
        self.assertLess(a.cash,10000)
        self.assertAlmostEqual(a.cash-10000,a.closed_trades[0]['net_pnl'])

    def test_drawdown_next_open_with_gap(self):
        a=PaperAccount(self.rules)
        a.step(bar('2026-01-01'),benchmark=True)
        a.step(bar('2026-01-02',100,50),benchmark=True)
        self.assertTrue(a.paused)
        self.assertGreater(a.units,0)
        a.step(bar('2026-01-03',40,50),benchmark=True)
        self.assertEqual(a.units,0)
        self.assertEqual(a.ledger[-1]['reason'],'drawdown_pause')
        self.assertEqual(a.ledger[-1]['reference'],40)
        a.step(bar('2026-01-04',100,200),benchmark=True)
        self.assertEqual(a.units,0)

    def test_checkpoint_resume_matches_uninterrupted(self):
        a=PaperAccount(self.rules)
        a.step(bar('2026-01-01',100,110))
        a.step(bar('2026-01-02',110,120))
        b=PaperAccount.restore(a.checkpoint())
        a.step(bar('2026-01-03',120,125))
        b.step(bar('2026-01-03',120,125))
        self.assertEqual(a.checkpoint(),b.checkpoint())

    def test_duplicate_date_rejected(self):
        a=PaperAccount(self.rules); a.step(bar('2026-01-01'))
        with self.assertRaises(ValueError): a.step(bar('2026-01-01'))

    def test_crypto_missing_bar_rejected(self):
        a=PaperAccount(replace(self.rules,crypto=True))
        a.step(bar('2026-01-01'))
        with self.assertRaises(ValueError): a.step(bar('2026-01-03'))

    def test_warmup_not_measurement(self):
        a=replay([bar('2026-01-01',100,100),bar('2026-01-02',110,110),bar('2026-01-03',120,120)],
                 self.rules,'2026-01-03','2026-01-03')
        self.assertEqual(len(a.curve),1)
        self.assertEqual(a.ledger[0]['date'],'2026-01-03')
        self.assertEqual(a.ledger[-1]['reason'],'terminal_measurement_close')

    def test_future_bar_does_not_change_earlier_trade(self):
        original=[bar('2026-01-01',100,100),bar('2026-01-02',100,110),bar('2026-01-03',120,130)]
        changed=original+[bar('2026-01-04',10000,10000)]
        a=replay(original,self.rules,'2026-01-01','2026-01-03')
        b=replay(changed,self.rules,'2026-01-01','2026-01-03')
        self.assertEqual(a.ledger,b.ledger)

    def test_flat_cash_metrics_are_finite(self):
        a=replay([bar('2026-01-01'),bar('2026-01-02')],self.rules,'2026-01-01','2026-01-02')
        m=metrics(a)
        self.assertEqual(m['net_return_pct'],0)
        self.assertIsNone(m['descriptive_sharpe_zero_cash_rate'])
        self.assertFalse(m['strategy_validated'])

    def test_invalid_bar_does_not_mutate_account(self):
        a=PaperAccount(self.rules)
        before=a.checkpoint()
        with self.assertRaises(ValueError): a.step(bar('2026-01-01',close=float('nan')))
        self.assertEqual(a.checkpoint(),before)


if __name__=='__main__': unittest.main()
