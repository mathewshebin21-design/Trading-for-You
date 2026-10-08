from copy import deepcopy
import unittest
import json
from pathlib import Path
import tempfile
from prospective_lab import new_lab, advance, target, report, observe

class LabTests(unittest.TestCase):
    def setUp(self):
        self.time=1791554400000
        self.signal={'bar_close_ms':self.time-100000,'closes':list(range(100,200))}
        self.q={'event_ms':self.time-1,'bid':100.,'ask':100.1,'bid_qty':100,'ask_qty':100}
    def step(self,state,offset=10,day='2026-10-09',q=None,entry=True):
        quote={**(q or self.q),'event_ms':self.time+offset-1}
        return advance(state,self.signal,quote,self.time+offset,day,entry)
    def ready(self):
        s=advance(new_lab('SPY',self.time),self.signal,self.q,self.time,'2026-10-09')
        return self.step(s)
    def test_first_decision_then_post_decision_quote_and_restart_dedup(self):
        s=advance(new_lab('SPY',self.time),self.signal,self.q,self.time,'2026-10-09')
        self.assertEqual(s['accounts']['sma_20_100:1']['units'],0)
        s=self.step(s);self.assertGreater(s['accounts']['sma_20_100:1']['units'],0)
        self.assertEqual(s,self.step(s))
    def test_cost_stress_cash_and_separate_accounts(self):
        s=self.ready();base=s['accounts']['buy_hold_25:1'];stress=s['accounts']['buy_hold_25:2']
        self.assertGreater(stress['ledger'][0]['modeled_execution_cost'],base['ledger'][0]['modeled_execution_cost'])
        self.assertEqual(s['accounts']['cash:1']['cash'],10000)
        s['accounts']['cash:1']['cash']=42
        self.assertEqual(s['accounts']['cash:2']['cash'],10000)
    def test_invalid_stale_and_future_quotes_fail_without_mutation(self):
        s=self.ready();old=deepcopy(s)
        for q in ({**self.q,'event_ms':self.time-10000},
                  {**self.q,'event_ms':self.time+10000},
                  {**self.q,'event_ms':self.time+19,'ask':110}):
            with self.assertRaises(ValueError):advance(s,self.signal,q,self.time+20,'2026-10-09')
        self.assertEqual(s,old)
    def test_overnight_holdings_block_without_review(self):
        s=self.step(self.ready(),30,'2026-10-12')
        a=s['accounts']['sma_20_100:1']
        self.assertTrue(a['review_required']);self.assertEqual(len(a['ledger']),1)
    def test_pause_blocks_entries(self):
        s=advance(new_lab('SPY',self.time),self.signal,self.q,self.time,'2026-10-09')
        s=self.step(s,entry=False)
        self.assertEqual(s['accounts']['sma_20_100:1']['units'],0)
    def test_rule_change_rejected(self):
        s=new_lab('SPY',self.time);s['fingerprint']='modified'
        with self.assertRaises(ValueError):self.step(s)
    def test_corrupted_balance_and_account_identity_fail_closed(self):
        for field,value in (('cash',9999.),('symbol','GLD')):
            s=new_lab('SPY',self.time);s['accounts']['cash:1'][field]=value
            with self.assertRaises(ValueError):self.step(s)
    def test_saved_restart_and_report_remain_unvalidated(self):
        with tempfile.TemporaryDirectory() as temp:
            observe(temp,'SPY',self.signal,self.q,self.time,'2026-10-09')
            q={**self.q,'event_ms':self.time+9}
            observe(temp,'SPY',self.signal,q,self.time+10,'2026-10-09')
            before=json.loads((Path(temp)/'SPY_lab.json').read_text())
            observe(temp,'SPY',self.signal,q,self.time+10,'2026-10-09')
            self.assertEqual(before,json.loads((Path(temp)/'SPY_lab.json').read_text()))
            text='\n'.join(report(temp,self.time+10))
            self.assertIn('INSUFFICIENT_EVIDENCE',text)
            self.assertIn('modeled costs',text)
    def test_drawdown_exits_even_when_global_entries_paused(self):
        s=self.step(self.ready(),30,q={**self.q,'bid':1.,'ask':1.001},entry=False)
        a=s['accounts']['sma_20_100:1']
        self.assertTrue(a['paused']);self.assertEqual(a['units'],0)
        self.assertEqual(len(a['closed_trades']),1)
    def test_partial_exit_counts_roundtrip_only_when_flat(self):
        s=self.ready();count=s['accounts']['sma_20_100:1']['units']
        for i in range(count):
            s=self.step(s,30+i*10,q={**self.q,'bid':1.,'ask':1.001,'bid_qty':1},entry=False)
            a=s['accounts']['sma_20_100:1']
            self.assertEqual(len(a['closed_trades']),int(i==count-1))
        self.assertEqual(a['units'],0)
