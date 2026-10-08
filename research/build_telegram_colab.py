from pathlib import Path
import json
p=Path(__file__).parent;cells=[]
def cell(kind,source):
 d={'cell_type':kind,'metadata':{},'id':'telegram-test-'+str(len(cells)),'source':source.splitlines(True)}
 if kind=='code':d.update(outputs=[],execution_count=None)
 cells.append(d)
cell('markdown','# TrendWatchPaperBot — supervised Colab test\nPaper trading only. No paid cloud services. This test is temporary, stops with the runtime, and starts new separate automatic/manual virtual accounts. It does not resume Experiment 002 accounts. No Telegram token is embedded in the notebook.\n\nRun setup and offline tests first. Enter the token only in the hidden input cell directly in Colab, then send the pairing command to your bot. Start the final service cell only while supervising. Export account state before disconnecting.')
cell('code','%pip -q install websockets==15.0.1')
names=['prospective_paper.py','telegram_paper_bot.py','test_prospective_paper.py','test_telegram_paper_bot.py']
cell('code',"from pathlib import Path\nimport sys,json,os,asyncio,unittest,importlib\nROOT=Path('/content/telegram_paper_test');ROOT.mkdir(exist_ok=True)\nSOURCES="+repr({n:(p/n).read_text() for n in names})+"\nfor name,source in SOURCES.items():(ROOT/name).write_text(source)\nif str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))\nimport prospective_paper,telegram_paper_bot\nimportlib.reload(prospective_paper);importlib.reload(telegram_paper_bot)\nresult=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover(str(ROOT),pattern='test*.py'))\nassert result.wasSuccessful()\nprint('Offline safety tests passed:',result.testsRun)\nprint('No Telegram connection or cloud deployment performed by these tests.')")
cell('markdown','## Private token entry\nPaste the bot token into the hidden field below directly in Colab. Do not put it in a code cell, screenshot or notebook text. No token is printed or exported by this code. The bot API necessarily receives it for authentication. Run this cell yourself after the tests.')
cell('code',"""import getpass
from telegram_paper_bot import TelegramAPI
_private_token=getpass.getpass('Telegram bot token (hidden input): ')
_api=TelegramAPI(_private_token)
os.environ['TELEGRAM_BOT_TOKEN']=_private_token
del _private_token
_me=await asyncio.to_thread(_api.call,'getMe',{})
assert _me['username']=='TrendWatchPaperBot','Unexpected bot identity; stop and check configuration'
_webhook=await asyncio.to_thread(_api.call,'getWebhookInfo',{})
assert not _webhook.get('url'),'Dedicated long-poll bot required; existing webhook was not changed'
print('Bot API verified:',_me['username'])
""")
cell('markdown','## Pair your private Telegram account\nRun the next cell. Send its exact `/setup ...` command in the private chat with @TrendWatchPaperBot within five minutes. The cell binds the numeric user ID; it does not place a simulated trade or send Telegram messages.')
cell('code',"""import secrets,time
_pair_code=secrets.token_hex(12)
print('Send this in your private bot chat: /setup '+_pair_code,flush=True)
_deadline=time.monotonic()+300;_offset=0;_paired=False
while time.monotonic()<_deadline and not _paired:
    _updates=await asyncio.to_thread(_api.call,'getUpdates',{'offset':_offset,'timeout':10,'allowed_updates':['message']})
    for _u in _updates:
        _offset=_u['update_id']+1;_m=_u.get('message',{});_f=_m.get('from',{});_chat=_m.get('chat',{})
        if (_m.get('text')=='/setup '+_pair_code and _chat.get('type')=='private' and _f.get('id')==_chat.get('id') and not _f.get('is_bot') and abs(time.time()-_m.get('date',0))<120):
            os.environ['TELEGRAM_OWNER_ID']=str(_f['id']);_paired=True;break
assert _paired,'Pairing timed out. Re-run this cell for a new code.'
print('Private owner paired. No token printed. No simulated trade yet.')
""")
cell('markdown','## Start the supervised service\nRun this cell, then send `/start`, `/status`, `/trends`, `/report`. Automatic simulation can start immediately when the strategy signal permits. Manual trades require `/paper_trade BUY BTCUSDT` and the returned `/confirm CODE`. Stop this cell with its stop button when finished. Permanent risk pauses remain in force. No paid hosting or real orders. Each test account starts with 10,000 virtual USDT; manual and automatic results stay separate.')
cell('code',"""os.environ['PAPER_STATE_DIR']=str(ROOT/'session')
os.environ['PAPER_POLL_SECONDS']='60'
print('Supervised PAPER worker starting. Send /start in your private bot chat. Stop this cell to end.',flush=True)
await telegram_paper_bot.serve()
""")
cell('markdown','## Export after stopping\nStop the worker before exporting. This ZIP contains virtual accounts, source evidence, the Telegram command/audit database and tests. It contains private user IDs and account history: keep it private. Token environment variables are excluded. Restore the same session folder explicitly before restarting if you need continuity; avoid accidental account resets.')
cell('code',"""import zipfile
from google.colab import files
_export=Path('/content/Telegram_Paper_Test_State.zip')
with zipfile.ZipFile(_export,'w',zipfile.ZIP_DEFLATED) as z:
    for path in ROOT.rglob('*'):
        if path.is_file() and '__pycache__' not in str(path):z.write(path,path.relative_to(ROOT))
print('Private state export ready; bot token is not included.')
files.download(str(_export))
""")
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'Telegram_Paper_Bot_Colab_Test.ipynb'},'kernelspec':{'name':'python3','display_name':'Python 3'}},'cells':cells}
Path('Telegram_Paper_Bot_Colab_Test.ipynb').write_text(json.dumps(nb,indent=1))
