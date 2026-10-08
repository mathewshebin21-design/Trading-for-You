import asyncio
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, AsyncMock
from us_paper import ET, account, fill, get_data, poll_us, quote, sessions, signal, market_session, preserve_decision, fresh_quote, QuoteUnavailable

class USTests(unittest.TestCase):
    def setUp(self):
        self.calendar=[{'date':'2026-10-08','open':'09:30','close':'16:00'}]
        self.time=int(datetime(2026,10,8,10,tzinfo=ET).timestamp()*1000)
        self.raw={'t':datetime.fromtimestamp(self.time/1000,ET).isoformat(),'bp':100,'ap':100.1,'bs':100,'as':100}
        self.q=quote(self.raw,self.time,self.time)
        self.s=account('SPY');self.s['signal']={'observed_ms':self.time,'target_long':True}
    def test_allowlist(self):
        with self.assertRaises(ValueError):get_data('/v2/orders',{})
    def test_same_signal_preserves_decision_but_revision_does_not(self):
        first={'bar_close_ms':1,'fast':110.,'slow':100.,'target_long':True,'observed_ms':self.time-10000}
        current={**first,'observed_ms':self.time}
        decision=preserve_decision(first,current)
        self.assertEqual(decision['observed_ms'],first['observed_ms'])
        raw={**self.raw,'t':datetime.fromtimestamp((self.time-1000)/1000,ET).isoformat()}
        self.assertEqual(quote(raw,self.time,decision['observed_ms'])['event_ms'],self.time-1000)
        for change in ({'bar_close_ms':2},{'fast':111.},{'target_long':False}):
            revised=preserve_decision(first,{**first,**change,'observed_ms':self.time})
            self.assertEqual(revised['observed_ms'],self.time)
            with self.assertRaises(QuoteUnavailable):quote(raw,self.time,revised['observed_ms'])
    def test_quote_retry_accepts_only_new_fresh_event(self):
        old={**self.raw,'t':datetime.fromtimestamp((self.time-1000)/1000,ET).isoformat()}
        with patch('us_paper.get_data',side_effect=[{'quote':old},{'quote':self.raw}]),patch('us_paper.now_ms',return_value=self.time),patch('us_paper.asyncio.sleep',new_callable=AsyncMock):
            q,observed=asyncio.run(fresh_quote('SPY',self.time))
        self.assertEqual(q['event_ms'],self.time)
    def test_stale_quotes_still_rejected_after_bounded_retries(self):
        old={**self.raw,'t':datetime.fromtimestamp((self.time-6000)/1000,ET).isoformat()}
        with patch('us_paper.get_data',return_value={'quote':old}) as fetch,patch('us_paper.now_ms',return_value=self.time),patch('us_paper.asyncio.sleep',new_callable=AsyncMock):
            with self.assertRaisesRegex(QuoteUnavailable,'QUOTE_STALE'):asyncio.run(fresh_quote('SPY',self.time-10000))
        self.assertEqual(fetch.call_count,3)
    def test_poll_diagnostics_do_not_expose_provider_secret(self):
        def data(path,params):
            if path=='/v2/calendar':return self.calendar
            raise RuntimeError('secret_private_token')
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'US_PAPER_ENABLED':'1'}),patch('us_paper.get_data',side_effect=data),patch('us_paper.now_ms',return_value=self.time):
            result=asyncio.run(poll_us(folder))
        self.assertEqual(result[1]['reason'],'HISTORY_FETCH')
        self.assertNotIn('secret_private_token',json.dumps(result))
    def test_repeated_poll_uses_persisted_decision_without_duplicate_fill(self):
        sig={'bar_close_ms':1,'fast':110.,'slow':100.,'target_long':True,'observed_ms':self.time-10000}
        raw={**self.raw,'t':datetime.fromtimestamp((self.time-1000)/1000,ET).isoformat()}
        def data(path,params):
            if path=='/v2/calendar':return self.calendar
            if path.endswith('/bars'):return {'bars':[]}
            return {'quote':raw}
        with tempfile.TemporaryDirectory() as folder:
            for symbol in ('SPY','AAPL','GLD'):
                state=account(symbol);state['signal']=dict(sig)
                (Path(folder)/(symbol+'_state.json')).write_text(json.dumps(state))
            with patch.dict(os.environ,{'US_PAPER_ENABLED':'1'}),patch('us_paper.get_data',side_effect=data),patch('us_paper.now_ms',return_value=self.time),patch('us_paper.signal',side_effect=lambda *args:{**sig,'observed_ms':self.time}):
                first=asyncio.run(poll_us(folder));second=asyncio.run(poll_us(folder))
            self.assertEqual(first[1]['status'],'SIMULATED_BUY')
            self.assertEqual(second[1]['status'],'NO_ACTION')
            restored=json.loads((Path(folder)/'SPY_state.json').read_text())
            self.assertEqual(restored['signal']['observed_ms'],sig['observed_ms'])
            self.assertEqual(len(restored['ledger']),1)
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
    def test_market_open_boundaries(self):
        opening=sessions(self.calendar)[0][1];closing=sessions(self.calendar)[0][2]
        self.assertEqual(market_session(self.calendar,opening)['status'],'MARKET_OPEN')
        self.assertEqual(market_session(self.calendar,opening-1)['status'],'MARKET_CLOSED')
        self.assertEqual(market_session(self.calendar,closing)['status'],'MARKET_CLOSED')
        self.assertEqual(market_session([],opening)['status'],'MARKET_CLOSED')
    def test_session_survives_bad_symbol_history(self):
        def data(path,params):
            if path=='/v2/calendar':return self.calendar
            raise ValueError('No bars')
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{'US_PAPER_ENABLED':'1'}),patch('us_paper.get_data',side_effect=data),patch('us_paper.now_ms',return_value=self.time):
            out=asyncio.run(poll_us(folder))
        self.assertEqual(out[0]['status'],'MARKET_OPEN')
        self.assertEqual(out[1]['status'],'NO_FILL_DATA_ERROR')
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
