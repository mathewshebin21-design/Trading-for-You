"""Safety/accounting regression checks for virtual execution only."""
import unittest
import tempfile
import json
from pathlib import Path
from prospective_paper import *

class ProspectiveTests(unittest.TestCase):
    def setUp(self):
        self.t=200*DAY_MS+12345
        self.s=new_session('BTCUSDT')
        observe_signal(self.s,list(range(1,101)),200*DAY_MS-1,self.t)
        self.f={'step':0.001,'min_qty':0.001,'max_qty':1000,'min_notional':5}
        self.r={'e':'24hrTicker','s':'BTCUSDT','E':self.t+1000,'b':'99','a':'100','B':'100','A':'100'}
    def q(self): return validate_quote(self.r,'BTCUSDT',self.t+1100,self.t)
    def test_timing(self):
        for event,receipt in [(self.t-1,self.t),(self.t+1000,self.t+7000),(self.t+4000,self.t+1000)]:
            with self.assertRaises(ValueError):validate_quote({**self.r,'E':event},'BTCUSDT',receipt,self.t)
    def test_wrong_crossed_and_nan(self):
        for delta in [{'s':'ETHUSDT'},{'a':'98'},{'b':'nan'},{'a':'101'}]:
            with self.assertRaises(ValueError):validate_quote({**self.r,**delta},'BTCUSDT',self.t+1100,self.t)
    def test_quote_spread(self):
        self.r.update(b='99.99')
        self.assertEqual(self.q()['ask'],100)
    def test_dedup(self):
        self.r.update(b='99.99');q=self.q()
        self.assertEqual(execute_paper(self.s,q,self.f),'SIMULATED_BUY')
        cash=self.s['cash'];units=self.s['units']
        self.assertEqual(execute_paper(self.s,q,self.f),'NO_ACTION')
        self.assertEqual((self.s['cash'],self.s['units']),(cash,units))
        self.assertFalse(observe_signal(self.s,[100]*100,200*DAY_MS-1,self.t+9999))
        self.assertEqual(self.s['decision_ms'],self.t)
    def test_entry_pause_allows_exit(self):
        self.r.update(b='99.99');q=self.q()
        self.assertEqual(execute_paper(self.s,q,self.f,allow_entry=False),'ENTRY_PAUSED')
        self.assertEqual(len(self.s['ledger']),0)
        execute_paper(self.s,q,self.f)
        self.s['target_long']=False
        self.assertEqual(execute_paper(self.s,q,self.f,allow_entry=False),'SIMULATED_SELL')
        self.assertEqual(self.s['units'],0)
    def test_fee_size_budget(self):
        self.r.update(b='99.99',A='2.3456')
        execute_paper(self.s,self.q(),self.f)
        self.assertAlmostEqual(self.s['units'],2.345)
        self.assertAlmostEqual(self.s['cash'],10000-2.345*100*1.0003*1.001)
        self.assertLessEqual(10000-self.s['cash'],2500)
    def test_risk_pause_and_partial_exit(self):
        self.r.update(b='99.99');execute_paper(self.s,self.q(),self.f)
        old=self.s['units'];old_cost=self.s['entry_outlay']
        low={**self.q(),'bid':40,'ask':40.01,'bid_qty':1}
        self.assertEqual(execute_paper(self.s,low,self.f),'SIMULATED_SELL')
        self.assertTrue(self.s['paused']);self.assertAlmostEqual(self.s['units'],old-1)
        self.assertAlmostEqual(self.s['entry_outlay'],old_cost*(old-1)/old)
        execute_paper(self.s,{**low,'bid_qty':100},self.f)
        self.assertEqual(self.s['units'],0)
        self.assertEqual(execute_paper(self.s,self.q(),self.f),'NO_ACTION')
    def test_notional_and_currency(self):
        self.r.update(b='99.99',A='0.001')
        self.assertEqual(execute_paper(self.s,self.q(),self.f),'REJECTED_SIZE_OR_NOTIONAL')
        self.assertEqual(len(self.s['ledger']),0)
        self.s['currency']='USD'
        with self.assertRaises(ValueError):execute_paper(self.s,self.q(),self.f)
    def candles(self):
        return [[d*DAY_MS,'100','101','99','100','1',(d+1)*DAY_MS-1] for d in range(100,200)]
    def test_complete_bars(self):
        rows=self.candles();closes,end=completed_closes(rows,self.t)
        self.assertEqual(len(closes),100);self.assertEqual(end,200*DAY_MS-1)
        with self.assertRaises(ValueError):completed_closes(rows[:-1],self.t)
        with self.assertRaises(ValueError):completed_closes(rows,self.t+DAY_MS)
        rows[20][0]+=DAY_MS
        with self.assertRaises(ValueError):completed_closes(rows,self.t)
    def test_atomic_restore(self):
        self.r.update(b='99.99');execute_paper(self.s,self.q(),self.f)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'state.json';save_state(path,self.s)
            restored=json.loads(path.read_text())
            self.assertEqual(execute_paper(restored,self.q(),self.f),'NO_ACTION')
            self.assertEqual(len(restored['ledger']),1)
            self.assertFalse(path.with_suffix('.tmp').exists())

if __name__=='__main__': unittest.main()
