import asyncio
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from us_paper import ET, account, fill, get_data, poll_us, quote, sessions, signal

class USTests(unittest.TestCase):
    def setUp(self):
        self.calendar=[{'date':'2026-10-08','open':'09:30','close':'16:00'}]
        self.time=int(datetime(2026,10,8,10,tzinfo=ET).timestamp()*1000)
        self.raw={'t':datetime.fromtimestamp(self.time/1000,ET).isoformat(),'bp':100,'ap':100.1,'bs':100,'as':100}
        self.q=quote(self.raw,self.time,self.time)
        self.s=account('SPY');self.s['signal']={'observed_ms':self.time,'target_long':True}
    def test_allowlist(self):
        with self.assertRaises(ValueError):get_data('/v2/orders',{})
    def test_bad_quotes(self):
        for change in ({'bp':float('nan')},{'ap':99},{'ap':102},{'bs':0},{'t':'2026-10-08T08:00:00-04:00'}):
            with self.assertRaises(ValueError):quote({**self.raw,**change},self.time,self.time)
    def test_buy_cost_and_no_duplicate_restart(self):
        self.assertEqual(fill(self.s,self.q,self.calendar,self.time),'SIMULATED_BUY')
        self.assertGreater(self.s['ledger'][0]['model_fill_price'],100.1)
        self.assertGreater(self.s['ledger'][0]['commission'],0)
        restored=json.loads(json.dumps(self.s))
        self.assertEqual(fill(restored,self.q,self.calendar,self.time),'NO_ACTION')
        self.assertGreaterEqual(restored['cash'],0)
        self.assertLess(restored['units']*100.1,2500)
    def test_pause_and_exit(self):
        self.assertEqual(fill(self.s,self.q,self.calendar,self.time,False),'ENTRY_PAUSED')
        fill(self.s,self.q,self.calendar,self.time)
        self.s['signal']['target_long']=False
        self.assertEqual(fill(self.s,self.q,self.calendar,self.time,False),'SIMULATED_SELL')
    def test_overnight_review_persists(self):
        fill(self.s,self.q,self.calendar,self.time)
        self.s['last_session']='2026-10-07'
        self.assertEqual(fill(self.s,self.q,self.calendar,self.time),'CORPORATE_ACTION_REVIEW_REQUIRED')
        self.assertTrue(self.s['review_required'])
    def test_calendar_closed_holiday_and_early_close(self):
        self.assertEqual(fill(self.s,self.q,[],self.time),'MARKET_CLOSED')
        early=[{'date':'2026-10-08','open':'09:30','close':'13:00'}]
        later=self.time+4*3600000
        q={**self.q,'event_ms':later,'received_ms':later}
        self.assertEqual(fill(self.s,q,early,later),'MARKET_CLOSED')
    def test_stale_fill(self):
        with self.assertRaises(ValueError):fill(self.s,self.q,self.calendar,self.time+6000)
    def test_dst(self):
        rows=sessions([{'date':'2026-03-06','open':'09:30','close':'16:00'}, {'date':'2026-03-09','open':'09:30','close':'16:00'}])
        self.assertEqual((rows[1][1]-rows[0][1])/3600000,71)
    def test_history_missing_and_incomplete(self):
        days=[];bars=[];d=datetime(2026,1,1,tzinfo=ET)
        while len(days)<101:
            if d.weekday()<5:
                days.append({'date':d.date().isoformat(),'open':'09:30','close':'16:00'})
                c=100+len(days);bars.append({'t':d.isoformat(),'o':c,'h':c,'l':c,'c':c})
            d+=timedelta(days=1)
        now=sessions(days)[-1][1]+1000
        out=signal(bars,days,now)
        self.assertTrue(out['target_long']);self.assertEqual(out['bar_close_ms'],sessions(days)[-2][2])
        with self.assertRaises(ValueError):signal(bars[1:],days,now)
        with self.assertRaises(ValueError):signal(bars+[bars[0]],days,now)
    def test_missing_credentials_redacted(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'US_PAPER_ENABLED':'1','ALPACA_DATA_KEY':'','ALPACA_DATA_SECRET':''}):
            result=asyncio.run(poll_us(folder))
            self.assertEqual(result[0]['status'],'NO_FILL_DATA_ERROR')
            self.assertFalse(list(Path(folder).glob('*_state.json')))
    def test_disabled_no_network(self):
        with patch.dict(os.environ,{'US_PAPER_ENABLED':'0'}),patch('us_paper.get_data',side_effect=AssertionError):
            self.assertEqual(asyncio.run(poll_us('/unused')),[])

if __name__=='__main__':unittest.main()
