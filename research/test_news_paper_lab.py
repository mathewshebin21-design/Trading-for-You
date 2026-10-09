import unittest
from news_paper_lab import advance
from us_paper import sessions


class NewsPaperTests(unittest.TestCase):
    def setUp(self):
        self.calendar=[{'date':'2026-10-09','open':'09:30','close':'16:00'}]
        self.now=sessions(self.calendar)[0][1]+60000
        self.signal={'bar_close_ms':self.now-86400000,'observed_ms':self.now-1000,'fast':101,'slow':100,'target_long':True}
        self.news={'valid':True,'latest_receipt_ms':None,'coverage_end_ms':self.now-900000}
        self.q={'bid':100.,'ask':100.01,'bid_qty':100,'ask_qty':100,'event_ms':self.now}

    def step(self,state=None,offset=0,news=None,signal=None,entry=True,q=None):
        return advance(state,signal or self.signal,{**(q or self.q),'event_ms':self.now+offset},self.calendar,self.now+offset,news or self.news,entry)

    def ready(self):return self.step(self.step(),10)

    def test_new_accounts_wait_for_post_decision_quote_and_deduplicate(self):
        s=self.step()
        self.assertTrue(all(not a['ledger'] for a in s['accounts'].values()))
        s=self.step(s,10)
        self.assertTrue(all(len(a['ledger'])==1 for a in s['accounts'].values()))
        self.assertEqual(s,self.step(s,10))

    def test_news_delay_blocks_only_delayed_account_and_expiry_waits_new_quote(self):
        news={**self.news,'latest_receipt_ms':self.now}
        s=self.step(self.step(news=news),10,news=news)
        self.assertEqual(s['accounts']['baseline:1']['units'],24)
        self.assertEqual(s['accounts']['news_delay:1']['units'],0)
        for offset in (500000,1000000,1500000):
            s=self.step(s,offset,news=news)
        s=self.step(s,1800001,news=news)
        self.assertEqual(s['accounts']['news_delay:1']['units'],0)
        s=self.step(s,1800011,news=news)
        self.assertGreater(s['accounts']['news_delay:1']['units'],0)

    def test_missing_coverage_blocks_both_entries_and_retains_invalid_day(self):
        news={**self.news,'valid':False}
        s=self.step(self.step(news=news),10,news=news)
        self.assertTrue(all(not a['units'] for a in s['accounts'].values()))
        s=self.step(s,20)
        self.assertFalse(s['daily_marks']['2026-10-09']['valid'])

    def test_exits_continue_with_missing_news_and_global_pause(self):
        s=self.ready();signal={**self.signal,'target_long':False,'fast':99}
        s=self.step(s,20,signal=signal,news={**self.news,'valid':False},entry=False)
        s=self.step(s,30,signal=signal,news={**self.news,'valid':False},entry=False)
        self.assertTrue(all(a['units']==0 and a['status']=='SIMULATED_SELL' for a in s['accounts'].values()))

    def test_double_costs_reduce_equity_and_account_corruption_rejected(self):
        s=self.ready()
        self.assertLess(s['accounts']['baseline:2']['equity'],s['accounts']['baseline:1']['equity'])
        s['accounts']['baseline:1']['cash']+=1
        with self.assertRaises(ValueError):self.step(s,20)

    def test_invalid_quotes_and_fingerprint_rejected(self):
        with self.assertRaises(ValueError):self.step(q={**self.q,'ask':float('nan')})
        s=self.step();s['fingerprint']='wrong'
        with self.assertRaises(ValueError):self.step(s,10)

    def test_risk_pause_exits_partial_size_and_remains_paused(self):
        s=self.ready()
        for i in range(24):
            s=self.step(s,20+i*10,q={**self.q,'bid':1.,'ask':1.001,'bid_qty':1},entry=False)
        self.assertTrue(all(a['paused'] and a['units']==0 for a in s['accounts'].values()))
        s=self.step(s,300)
        self.assertTrue(all(a['units']==0 for a in s['accounts'].values()))

    def test_observation_gap_marks_comparison_day_invalid(self):
        s=self.step(self.ready(),700000)
        self.assertFalse(s['daily_marks']['2026-10-09']['valid'])


if __name__=='__main__':unittest.main()
