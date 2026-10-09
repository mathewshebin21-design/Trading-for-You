"""Private Telegram control for virtual accounts ONLY. No exchange order APIs."""
import asyncio
import json
import os
import re
from pathlib import Path
import secrets
import sqlite3
import time
import urllib.request
from datetime import datetime,timezone
from prospective_paper import (SYMBOLS,new_session,public_get,symbol_filters,
    fresh_quote,execute_paper,save_state,poll_session,now_ms)

from us_paper import poll_us, report_us
from prospective_lab import report as report_lab
from news_collector import poll_news, report_news
from news_paper_lab import report as report_news_lab
from paper_backup import snapshot

HELP=('PAPER ONLY — strategy unvalidated.\n/status /positions /trends /trades /report /lab /news /news_lab\n'
      '/pause stops new automatic entries; exits/risk checks continue.\n'
      '/resume enables entries; never resets a risk pause.\n'
      '/paper_trade BUY BTCUSDT (or ETHUSDT)\n'
      '/paper_trade SELL BTCUSDT\n'
      '/confirm CODE within 60 seconds; /cancel discards requests.\n'
      'Manual accounts are separate from frozen-rule automatic accounts.\n'
      'BUY uses up to 25% of equity; SELL uses available displayed bid size.\n'
      'USDT virtual balances only; no real orders or money.')

def utc(ms): return datetime.fromtimestamp(ms/1000,timezone.utc).isoformat()

class TelegramAPI:
    def __init__(self,token):
        if not token or not re.fullmatch(r'[0-9]+:[A-Za-z0-9_-]+',token):raise ValueError('Invalid bot token configuration')
        self.token=token
    def call(self,method,payload):
        if method not in {'getUpdates','sendMessage','getMe','getWebhookInfo'}:raise ValueError('Unsupported bot method')
        data=json.dumps(payload).encode()
        req=urllib.request.Request('https://api.telegram.org/bot'+self.token+'/'+method,data=data,
             headers={'Content-Type':'application/json'},method='POST')
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*a,**k):raise RuntimeError('Telegram redirect rejected')
        try:
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as r: raw=r.read(1_000_001)
            if len(raw)>1_000_000:raise RuntimeError('Oversized bot response')
            result=json.loads(raw)
            if not result.get('ok'):raise RuntimeError('Bot API rejected request')
            return result['result']
        except Exception:
            # Never expose URL-bearing exceptions: bot tokens are embedded in API URLs.
            raise RuntimeError('Telegram API request failed; check credentials, connectivity or rate limit') from None

class Controller:
    def __init__(self,folder,owner,clock=now_ms):
        if type(owner) is not int or owner<=0:raise ValueError('Positive private Telegram user ID required')
        self.folder=Path(folder);self.folder.mkdir(parents=True,exist_ok=True)
        self.owner=owner;self.clock=clock
        self.db=sqlite3.connect(self.folder/'telegram.sqlite')
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY,v TEXT);
        CREATE TABLE IF NOT EXISTS inbox(id INTEGER PRIMARY KEY,status TEXT);
        CREATE TABLE IF NOT EXISTS intents(code TEXT PRIMARY KEY,side TEXT,symbol TEXT,expires INTEGER,used INTEGER);
        CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT,body TEXT,sent INTEGER DEFAULT 0);''')
        self.db.commit()
    def get(self,key,default='0'):
        row=self.db.execute('SELECT v FROM settings WHERE k=?',(key,)).fetchone();return row[0] if row else default
    def set(self,key,value):
        self.db.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',(key,str(value)));self.db.commit()
    def queue(self,body):
        self.db.execute('INSERT INTO outbox(body) VALUES(?)',(body[:4000],));self.db.commit()
    def states(self,mode):
        folder=self.folder/mode
        found=[]
        for symbol in SYMBOLS:
            p=folder/(symbol+'_state.json')
            if p.exists():found.append(json.loads(p.read_text()))
        return found
    def report(self,command):
        if command=='/news_lab':
            return '\n'.join(report_news_lab(self.folder/'us_automatic'/'news_lab',self.clock()))
        if command=='/news':
            return '\n'.join(report_news(self.folder/'research_news',self.clock()))
        if command=='/lab':
            return '\n'.join(report_lab(self.folder/'us_automatic'/'lab',self.clock()))
        lines=['PAPER ONLY — USDT; unvalidated strategy.',
               'Automatic entries: '+('paused' if self.get('paused')=='1' else 'enabled')]
        for mode in ('automatic','manual'):
            states=self.states(mode)
            if not states:lines.append(mode+': no observed account yet.');continue
            for s in states:
                q=s['quote_observations'][-1] if s['quote_observations'] else None
                age=(self.clock()-q['received_ms'])/1000 if q else None
                bid=q['bid'] if q else None
                equity=s['cash']+s['units']*bid if bid else None
                if command=='/trends':
                    obs=s.get('signal_observations',[])
                    if mode=='manual':continue
                    if obs:
                        a=obs[-1];lines.append(f"{s['symbol']}: {'UP' if a['target_long'] else 'NOT UP'}; SMA20 {a['fast']:.4f}, SMA100 {a['slow']:.4f}; observed {utc(a['observed_ms'])}")
                elif command=='/trades':
                    for t in s['ledger'][-5:]:lines.append(f"{mode} {s['symbol']} {t['side']} {t['quantity']:.8f} @ model {t['model_fill_price']:.4f}; fee {t['commission']:.4f}; {utc(t['event_ms'])}")
                    if not s['ledger']:lines.append(f"{mode} {s['symbol']}: no fills.")
                else:
                    lines.append(f"{mode} {s['symbol']}: cash {s['cash']:.2f}, units {s['units']:.8f}, risk paused {s['paused']}, fills {len(s['ledger'])}")
                    if equity is not None:
                        lines.append(f"Indicative bid equity {equity:.2f}; P/L {equity-10000:.2f}; drawdown {100*(equity/s['peak']-1):.2f}%; quote age {age:.0f}s"+(' STALE' if age>60 else ''))
                    lines.append('Cumulative modeled commissions: '+f"{sum(t['commission'] for t in s['ledger']):.4f}")
        lines.extend(report_us(self.folder/'us_automatic'))
        if command=='/status':
            lines.extend(report_news(self.folder/'research_news',self.clock())[:3])
        beat=self.folder/'heartbeat.json'
        if beat.exists():lines.append('Collector: '+json.loads(beat.read_text())['updated_utc'])
        backup=self.folder/'backup_health.json'
        if backup.exists():lines.append('Recovery snapshot: '+json.loads(backup.read_text())['status']+' (same volume)')
        return '\n'.join(lines)[:4000]
    async def handle(self,update):
        uid=update.get('update_id');m=update.get('message',{})
        if type(uid) is not int:return
        # Offset is durably consumed BEFORE any possible virtual fill. Crash => no replay.
        try:self.db.execute('INSERT INTO inbox VALUES(?,?)',(uid,'consumed'));self.db.commit()
        except sqlite3.IntegrityError:return
        self.set('offset',max(int(self.get('offset')),uid+1))
        if m.get('from',{}).get('id')!=self.owner or m.get('from',{}).get('is_bot') or m.get('chat',{}).get('id')!=self.owner or m.get('chat',{}).get('type')!='private':return
        if not isinstance(m.get('date'),int) or abs(self.clock()/1000-m['date'])>120:
            self.queue('Ignored old/future command. Send a fresh command.');return
        text=m.get('text','')
        if not isinstance(text,str) or len(text)>200:return
        args=text.strip().split();cmd=args[0] if args else ''
        try:
            if cmd in ('/start','/help'):
                self.set('notifications','1');self.queue(HELP)
            elif cmd in ('/lab','/news','/news_lab'):
                chunk=''
                for line in self.report(cmd).splitlines():
                    if len(chunk)+len(line)+1>3900:
                        self.queue(chunk);chunk=''
                    chunk+=line+'\n'
                if chunk:self.queue(chunk.rstrip())
            elif cmd in ('/status','/positions','/trends','/trades','/report'):self.queue(self.report(cmd))
            elif cmd=='/pause':self.set('paused','1');self.queue('New automatic entries paused. Existing exits/risk checks continue; holdings were not liquidated.')
            elif cmd=='/resume':self.set('paused','0');self.queue('Automatic entries enabled. Permanent account drawdown pauses remain in force.')
            elif cmd=='/cancel':
                self.db.execute('UPDATE intents SET used=1');self.db.commit();self.queue('Pending paper requests cancelled.')
            elif cmd=='/paper_trade':
                if len(args)!=3 or args[1] not in ('BUY','SELL') or args[2] not in SYMBOLS:raise ValueError('Use /paper_trade BUY|SELL BTCUSDT|ETHUSDT')
                code=secrets.token_hex(4)
                self.db.execute('UPDATE intents SET used=1')
                self.db.execute('INSERT INTO intents VALUES(?,?,?,?,0)',(code,args[1],args[2],self.clock()+60000));self.db.commit()
                self.queue(f'PAPER ONLY — manual {args[1]} {args[2]}. Separate virtual account. BUY up to 25% equity; SELL available holdings/size. Fresh quotes and risk checks required. Confirm within 60s: /confirm {code}')
            elif cmd=='/confirm':
                if len(args)!=2:raise ValueError('Use /confirm CODE')
                intent=self.db.execute('SELECT side,symbol,expires,used FROM intents WHERE code=?',(args[1],)).fetchone()
                if not intent or intent[3] or self.clock()>intent[2]:raise ValueError('Request expired, cancelled, used or unknown')
                # Consume once before network requests; a failure requires a new preview.
                self.db.execute('UPDATE intents SET used=1 WHERE code=?',(args[1],));self.db.commit()
                outcome=await self.manual(intent[0],intent[1],uid,args[1]);self.queue(outcome)
            else:self.queue('Unknown command. Use /help. Paper only.')
        except ValueError as exc:self.queue(str(exc))
        except Exception:self.queue('Command failed closed; no automatic retry. Check local audit/error logs, then request a fresh preview if needed.')
        self.db.execute('UPDATE inbox SET status=? WHERE id=?',('handled',uid));self.db.commit()
    async def manual(self,side,symbol,update_id,intent_id):
        p=self.folder/'manual'/(symbol+'_state.json')
        s=json.loads(p.read_text()) if p.exists() else new_session(symbol)
        if s['symbol']!=symbol:raise ValueError('Virtual account identity mismatch')
        if side=='BUY' and self.get('paused')=='1':raise ValueError('Entries paused. Use /resume first.')
        if side=='BUY' and s['units']>0:raise ValueError('Already holding; no pyramiding.')
        if side=='SELL' and s['units']==0:raise ValueError('No manual holdings to sell.')
        info,seen=await asyncio.to_thread(public_get,'exchangeInfo','symbol='+symbol)
        filters=symbol_filters(info,symbol)
        s['decision_ms']=self.clock();s['target_long']=side=='BUY'
        q=await fresh_quote(symbol,s['decision_ms'])
        result=execute_paper(s,q,filters)
        if result.startswith('SIMULATED_'):
            s['ledger'][-1].update(reason='telegram_manual_request',update_id=update_id,intent_id=intent_id)
        save_state(p,s)
        save_state(self.folder/'manual'/('intent_'+intent_id+'.json'),{'update_id':update_id,'exchangeInfo':info,'received_ms':seen,'quote':q,'result':result})
        return f"PAPER ONLY {symbol}: {result}; cash {s['cash']:.2f} USDT, units {s['units']:.8f}. Partial fills/dust possible. Manual account only."
    def notify_market_open(self, results):
        for r in results:
            if r.get('symbol')!='US_MARKET' or r.get('status')!='MARKET_OPEN':continue
            day=r['session_date'];key='us_market_open_notice_'+day
            # Queue and daily marker commit atomically. Restart must not enqueue
            # the same session twice. Telegram retry may still duplicate delivery
            # if sendMessage succeeds but its response is lost.
            with self.db:
                if self.db.execute('SELECT 1 FROM settings WHERE k=?',(key,)).fetchone():continue
                zone=__import__('zoneinfo').ZoneInfo('Asia/Kolkata')
                def local(ms):return datetime.fromtimestamp(ms/1000,timezone.utc).astimezone(zone).strftime('%d %b %Y %I:%M %p IST')
                body=('US regular market session is OPEN — PAPER ONLY.\n'
                      +'Opens: '+local(r['open_ms'])+'\nCloses: '+local(r['close_ms'])
                      +'\nObserved: '+local(r['observed_ms'])
                      +'\nUse /status and /trends for current paper observations. '
                      +'This alert does not confirm a fill or predict returns.')
                self.db.execute('INSERT INTO outbox(body) VALUES(?)',(body,))
                self.db.execute('INSERT INTO settings VALUES(?,?)',(key,str(r['observed_ms'])))

    async def collect(self):
        backup_day=datetime.fromtimestamp(self.clock()/1000,timezone.utc).date().isoformat()
        try:
            created=snapshot(self.folder,self.db,backup_day)
            if created:
                save_state(self.folder/'backup_health.json',{'status':'LOCAL_SNAPSHOT_OK','observed_ms':self.clock(),
                    'scope':'same volume; not disaster recovery'})
        except Exception:
            save_state(self.folder/'backup_health.json',{'status':'BACKUP_FAILED','observed_ms':self.clock()})
        results=await poll_session(self.folder/'automatic',allow_entry=self.get('paused')!='1')
        results.extend(await poll_us(self.folder/'us_automatic',allow_entry=self.get('paused')!='1'))
        self.notify_market_open(results)
        # Original account/risk handling runs first. News never supplies orders.
        try:
            await asyncio.to_thread(poll_news,self.folder/'research_news')
        except Exception:
            pass  # News storage errors must not interrupt paper account reporting.
        beat={'mode':'PAPER_ONLY','updated_utc':utc(self.clock()),'results':results}
        save_state(self.folder/'heartbeat.json',beat)
        if self.get('notifications')=='1':
            for r in results:
                key='last_notice_'+r['symbol']
                fingerprint=json.dumps({k:r.get(k) for k in ('status','error','simulated_fill_count','paused')},sort_keys=True)
                if r['status'].startswith('SIMULATED_') or 'error' in r or r.get('paused'):
                    if self.get(key,'')!=fingerprint:self.queue('PAPER collector: '+json.dumps(r))
                self.set(key,fingerprint)
            day=datetime.fromtimestamp(self.clock()/1000,timezone.utc).astimezone(__import__('zoneinfo').ZoneInfo('Asia/Kolkata')).date().isoformat()
            if self.get('daily_report','')!=day:
                self.queue('Daily paper snapshot (Asia/Kolkata):\n'+self.report('/report'));self.set('daily_report',day)
        return results
    async def flush(self,api):
        for ident,body in self.db.execute('SELECT id,body FROM outbox WHERE sent=0 ORDER BY id LIMIT 10').fetchall():
            await asyncio.to_thread(api.call,'sendMessage',{'chat_id':self.owner,'text':body})
            self.db.execute('UPDATE outbox SET sent=1 WHERE id=?',(ident,));self.db.commit()

async def serve():
    owner=int(os.environ['TELEGRAM_OWNER_ID']);folder=Path(os.environ.get('PAPER_STATE_DIR','./telegram_state'))
    interval=int(os.environ.get('PAPER_POLL_SECONDS','60'))
    if interval<30:raise ValueError('Poll interval must be >=30s')
    folder.mkdir(parents=True,exist_ok=True)
    import fcntl
    with (folder/'worker.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('Another worker owns this state directory') from None
        controller=Controller(folder,owner);api=TelegramAPI(os.environ['TELEGRAM_BOT_TOKEN'])
        await asyncio.to_thread(api.call,'getMe',{})
        webhook=await asyncio.to_thread(api.call,'getWebhookInfo',{})
        if webhook.get('url'):raise RuntimeError('Bot has an active webhook; use a dedicated polling bot')
        due=0
        while True:
            try:
                if time.monotonic()>=due:
                    await controller.collect();due=time.monotonic()+interval
                updates=await asyncio.to_thread(api.call,'getUpdates',{'offset':int(controller.get('offset')),'timeout':10,'allowed_updates':['message']})
                for update in updates:await controller.handle(update)
                await controller.flush(api)
            except Exception:
                # Sanitized local operational event, never credentials or incoming message text.
                with (folder/'service_errors.jsonl').open('a') as f:f.write(json.dumps({'utc':utc(now_ms()),'event':'service_cycle_failed'})+'\n')
                await asyncio.sleep(5)

if __name__=='__main__':
    os.umask(0o077)
    try:asyncio.run(serve())
    except KeyboardInterrupt:print('Paper Telegram worker stopped.')
    except Exception:raise SystemExit('Startup failed: check required configuration, webhook and worker lock. No credentials printed.') from None
