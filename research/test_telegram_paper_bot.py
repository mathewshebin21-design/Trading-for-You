import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock,patch
from telegram_paper_bot import Controller,TelegramAPI
from prospective_paper import new_session,save_state

class TelegramTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.folder=Path(self.tmp.name)
        self.now=2_000_000;self.c=Controller(self.folder,123,clock=lambda:self.now)
    def tearDown(self):self.c.db.close();self.tmp.cleanup()
    def update(self,text,ident=1,owner=123,chat=123,kind='private',date=2000):
        return {'update_id':ident,'message':{'date':date,'from':{'id':owner},'chat':{'id':chat,'type':kind},'text':text}}
    def messages(self):return [r[0] for r in self.c.db.execute('SELECT body FROM outbox').fetchall()]
    def code(self):return self.c.db.execute('SELECT code FROM intents WHERE used=0').fetchone()[0]
    async def test_unauthorized_silent(self):
        for i,u in enumerate([self.update('/pause',owner=9),self.update('/pause',chat=-99,kind='group'),self.update('/paper_trade BUY BTCUSDT',owner=9)]):
            u['update_id']=i+1;await self.c.handle(u)
        self.assertEqual(self.messages(),[]);self.assertEqual(self.c.get('paused'),'0')
    async def test_duplicate_and_restart(self):
        await self.c.handle(self.update('/paper_trade BUY BTCUSDT'))
        self.c.db.close();self.c=Controller(self.folder,123,clock=lambda:self.now)
        await self.c.handle(self.update('/paper_trade BUY BTCUSDT'))
        self.assertEqual(len(self.messages()),1);self.assertEqual(self.c.get('offset'),'2')
    async def test_expired_and_cancelled(self):
        await self.c.handle(self.update('/paper_trade BUY BTCUSDT'));code=self.code()
        self.now+=61000
        self.c.manual=AsyncMock()
        await self.c.handle(self.update('/confirm '+code,ident=2,date=2061))
        self.c.manual.assert_not_awaited()
        await self.c.handle(self.update('/paper_trade BUY BTCUSDT',ident=3,date=2061))
        code=self.code();await self.c.handle(self.update('/cancel',ident=4,date=2061))
        await self.c.handle(self.update('/confirm '+code,ident=5,date=2061));self.c.manual.assert_not_awaited()
    async def test_confirmation_once_even_new_update(self):
        await self.c.handle(self.update('/paper_trade BUY ETHUSDT'));code=self.code()
        self.c.manual=AsyncMock(return_value='PAPER SIMULATED_BUY')
        await self.c.handle(self.update('/confirm '+code,ident=2))
        await self.c.handle(self.update('/confirm '+code,ident=3))
        self.c.manual.assert_awaited_once()
    async def test_failure_consumes_confirmation(self):
        await self.c.handle(self.update('/paper_trade BUY ETHUSDT'));code=self.code()
        self.c.manual=AsyncMock(side_effect=RuntimeError('SECRET'))
        await self.c.handle(self.update('/confirm '+code,ident=2))
        await self.c.handle(self.update('/confirm '+code,ident=3))
        self.c.manual.assert_awaited_once();self.assertNotIn('SECRET',' '.join(self.messages()))
    async def test_stale_commands(self):
        await self.c.handle(self.update('/pause',date=1000))
        self.assertEqual(self.c.get('paused'),'0')
    async def test_invalid_trade_syntax(self):
        for i,text in enumerate(['/paper_trade BUY SPY','/paper_trade BUY BTCUSDT 10','/paper_trade SHORT BTCUSDT']):await self.c.handle(self.update(text,ident=i+1))
        self.assertEqual(self.c.db.execute('SELECT count(*) FROM intents').fetchone()[0],0)
    async def test_pause_collector_and_permanent_risk(self):
        state=new_session('BTCUSDT');state['paused']=True
        save_state(self.folder/'automatic/BTCUSDT_state.json',state)
        await self.c.handle(self.update('/pause'))
        with patch('telegram_paper_bot.poll_session',new_callable=AsyncMock,return_value=[]) as poll:
            await self.c.collect();poll.assert_awaited_once_with(self.folder/'automatic',allow_entry=False)
        await self.c.handle(self.update('/resume',ident=2))
        self.assertTrue(self.c.states('automatic')[0]['paused'])
    async def test_manual_isolation_and_persistence(self):
        automatic=new_session('BTCUSDT');save_state(self.folder/'automatic/BTCUSDT_state.json',automatic)
        info={'symbols':[{'symbol':'BTCUSDT','status':'TRADING','quoteAsset':'USDT','filters':[
            {'filterType':'LOT_SIZE','stepSize':'0.001','minQty':'0.001','maxQty':'100'},
            {'filterType':'MIN_NOTIONAL','minNotional':'5'}]}]}
        q={'event_ms':self.now+10,'received_ms':self.now+11,'bid':99.99,'ask':100,'bid_qty':100,'ask_qty':100}
        with patch('telegram_paper_bot.public_get',return_value=(info,self.now)),patch('telegram_paper_bot.fresh_quote',new_callable=AsyncMock,return_value=q):
            result=await self.c.manual('BUY','BTCUSDT',9,'abcd')
        self.assertIn('SIMULATED_BUY',result)
        self.assertEqual(self.c.states('automatic')[0],automatic)
        manual=self.c.states('manual')[0];self.assertEqual(len(manual['ledger']),1)
        self.assertEqual(manual['ledger'][0]['intent_id'],'abcd');self.assertGreaterEqual(manual['cash'],7500)
    async def test_paused_manual_rejected(self):
        self.c.set('paused',1)
        with self.assertRaises(ValueError):await self.c.manual('BUY','BTCUSDT',9,'abcd')
        self.assertEqual(self.c.states('manual'),[])
    async def test_retry_outbox(self):
        self.c.queue('PAPER');api=type('API',(),{'call':lambda *a:(_ for _ in ()).throw(RuntimeError('network'))})()
        with self.assertRaises(RuntimeError):await self.c.flush(api)
        self.assertEqual(self.c.db.execute('SELECT sent FROM outbox').fetchone()[0],0)
        api=type('API',(),{'call':lambda *a:{'message_id':1}})();await self.c.flush(api)
        self.assertEqual(self.c.db.execute('SELECT sent FROM outbox').fetchone()[0],1)
    async def test_stale_report_marked(self):
        s=new_session('BTCUSDT');s['quote_observations']=[{'bid':100,'received_ms':self.now-120000}]
        save_state(self.folder/'automatic/BTCUSDT_state.json',s)
        self.assertIn('STALE',self.c.report('/report'))

class TransportTests(unittest.TestCase):
    def test_secret_redacted(self):
        api=TelegramAPI('123:TEST_SECRET')
        with patch('urllib.request.build_opener',side_effect=RuntimeError('https://api.telegram.org/bot123:TEST_SECRET')):
            with self.assertRaises(RuntimeError) as raised:api.call('getMe',{})
        self.assertNotIn('TEST_SECRET',str(raised.exception))
    def test_order_method_disallowed(self):
        with self.assertRaises(ValueError):TelegramAPI('123:FAKE').call('placeOrder',{})
