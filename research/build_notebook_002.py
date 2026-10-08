from pathlib import Path
import json
p=Path(__file__).parent
cells=[]
def add(kind,text):
 d={'cell_type':kind,'metadata':{},'source':text.splitlines(True),'id':'exp002-'+str(len(cells)).zfill(3)}
 if kind=='code':d.update(execution_count=None,outputs=[])
 cells.append(d)
add('markdown','# Trading Research — Experiment 002\nPaper only. Longer-history tests and interactive timestamped crypto simulations. No credentials or live orders.\n\nRun all to run tests, freeze new historical data, evaluate fixed rules, and take two prospective observations. Re-running preserves virtual account state in this runtime. Export the ZIP before disconnect.\n\nAdjusted historical prices are synthetic total-return proxies; prospective accounts use Binance USDT quotes. Never merge the records. All strategies remain unvalidated.')
add('markdown',(p/'EXPERIMENT_002.md').read_text())
add('code','%pip -q install yfinance==0.2.66 websockets==15.0.1')
sources={name:(p/name).read_text() for name in ['paper_engine.py','test_paper_engine.py','prospective_paper.py','test_prospective_paper.py','adjusted_history.py','test_adjusted_history.py']}
add('code',"from pathlib import Path\nimport json,sys,hashlib,unittest,datetime,zipfile\nROOT=Path('/content/paper_research_002');ROOT.mkdir(exist_ok=True)\nSOURCES="+repr(sources)+"\nfor name,source in SOURCES.items(): (ROOT/name).write_text(source)\nif str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))\nimport importlib\nimport paper_engine,prospective_paper\nimportlib.reload(paper_engine);importlib.reload(prospective_paper)\nsuite=unittest.defaultTestLoader.discover(str(ROOT),pattern='test*.py')\ncheck=unittest.TextTestRunner(verbosity=1).run(suite)\nassert check.wasSuccessful()\nprint('Verified safety/accounting checks:',check.testsRun)")
add('code',"""import yfinance as yf
from paper_engine import Rules,load_history,replay,metrics
from adjusted_history import load_adjusted_history
DATA=ROOT/'historical';DATA.mkdir(exist_ok=True)
freeze=ROOT/'history_manifest.json'
SYMBOLS=['GLD','SPY','AAPL','BTC-USD','ETH-USD']
if not freeze.exists():
    manifest={'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source':'Yahoo Finance via yfinance','yfinance_version':yf.__version__,
        'requested_start':'2016-10-01','end_exclusive':'2026-10-01',
        'convention':'adjusted synthetic OHLC; distributions zero; fractional units','assets':{},'errors':{}}
    for symbol in SYMBOLS:
        try:
            frame=yf.Ticker(symbol).history(start='2016-10-01',end='2026-10-01',auto_adjust=True,actions=False)
            if frame.empty: raise ValueError('No history returned')
            frame=frame[['Open','High','Low','Close','Volume']].copy()
            frame.index=[d.date().isoformat() for d in frame.index];frame.index.name='Date'
            path=DATA/(symbol+'.csv');frame.to_csv(path)
            rows,corrections=load_adjusted_history(path,crypto='-USD' in symbol)
            manifest['assets'][symbol]={'rows':len(rows),'first':rows[0]['date'],'last':rows[-1]['date'],
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rounding_corrections':corrections}
        except Exception as exc: manifest['errors'][symbol]=str(exc)
    freeze.write_text(json.dumps(manifest,indent=2))
manifest=json.loads(freeze.read_text())
# Re-audit frozen raw files; only rounding normalization changes, no data refetch.
for symbol in SYMBOLS:
    path=DATA/(symbol+'.csv')
    if not path.exists(): continue
    try:
        rows,corrections=load_adjusted_history(path,crypto='-USD' in symbol)
        manifest['assets'][symbol]={'rows':len(rows),'first':rows[0]['date'],'last':rows[-1]['date'],
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rounding_corrections':corrections}
        manifest['errors'].pop(symbol,None)
    except Exception as exc: manifest['errors'][symbol]=str(exc)
freeze.write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
""")
add('code',"""windows=[(str(y),f'{y}-01-01',f'{y}-12-31') for y in range(2018,2026)]
windows.append(('2026 Jan-Sep','2026-01-01','2026-09-30'))
results=[];skips=[]
for symbol,meta in manifest['assets'].items():
    path=DATA/(symbol+'.csv')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['sha256']
    rows,corrections=load_adjusted_history(path,crypto='-USD' in symbol)
    for label,start,end in windows:
        if sum(r['date']<start for r in rows)<100 or not any(start<=r['date']<=end for r in rows):
            skips.append({'symbol':symbol,'window':label,'reason':'Insufficient coverage or warm-up'});continue
        for multiplier in (1,2):
            crypto='-USD' in symbol
            rule=Rules(quantum=0.000001,crypto=crypto,commission_bps=(10 if crypto else 1)*multiplier,
                spread_bps=(2 if crypto else 1)*multiplier,slippage_bps=(3 if crypto else 2)*multiplier)
            strategy=replay(rows,rule,start,end);benchmark=replay(rows,rule,start,end,benchmark=True)
            results.append({'symbol':symbol,'window':label,'cost_multiplier':multiplier,
                'strategy':metrics(strategy),'benchmark':metrics(benchmark)})
(ROOT/'long_results.json').write_text(json.dumps({'results':results,'skips':skips},indent=2,allow_nan=False))
import pandas as pd
summary=[]
for symbol in manifest['assets']:
    rs=[r for r in results if r['symbol']==symbol and r['cost_multiplier']==1]
    summary.append({'asset':symbol,'windows':len(rs),'positive_windows':sum(r['strategy']['net_return_pct']>0 for r in rs),
        'beat_reference_windows':sum(r['strategy']['net_return_pct']>r['benchmark']['net_return_pct'] for r in rs),
        'closed_trades':sum(r['strategy']['closed_trades'] for r in rs),
        'worst_window_return_pct':round(min(r['strategy']['net_return_pct'] for r in rs),2),
        'worst_drawdown_pct':round(min(r['strategy']['maximum_drawdown_pct'] for r in rs),2),
        'validated':False})
print('Longer-history comparisons:',len(results),'skipped windows:',len(skips))
print(pd.DataFrame(summary).to_string(index=False))
print('Independent-start periods; no compounding between years. Exploratory, biased convenience universe.')
print('SKIPS:',json.dumps(skips))
""")
add('markdown','## Prospective paper session\nTwo new virtual USDT accounts. This cell polls once, then polls again to verify repeated decisions do not duplicate entries. Public data only. Failure means no simulated fill. This is an interactive session, not an always-on deployment.')
add('code',"""from prospective_paper import poll_session
SESSION_DIR=ROOT/'prospective'
first_poll=await poll_session(SESSION_DIR)
print('FIRST PROSPECTIVE OBSERVATION')
print(json.dumps(first_poll,indent=2))
second_poll=await poll_session(SESSION_DIR)
print('SECOND OBSERVATION — SAME ACCOUNT CHECKPOINTS')
print(json.dumps(second_poll,indent=2))
(ROOT/'prospective_poll_pair.json').write_text(json.dumps({'first':first_poll,'second':second_poll},indent=2))
""")
add('markdown','## Manual refresh and export\nRe-run the prospective cell while connected to collect current quotes. Download the ZIP using the final cell before runtime disconnection. It contains virtual checkpoints, audit sources, tests and fixed historical results. To resume later, upload that ZIP to Colab, extract only its prospective/*.json and errors.jsonl into SESSION_DIR, then poll; do not reset virtual capital. Continuous deployment and external paper-service integration remain separate work.')
add('code',"""ARCHIVE_PATH=Path('/content/Trading_Research_Experiment_002_Run.zip')
with zipfile.ZipFile(ARCHIVE_PATH,'w',zipfile.ZIP_DEFLATED) as archive:
    for path in ROOT.rglob('*'):
        if path.is_file() and '__pycache__' not in str(path):archive.write(path,path.relative_to(ROOT))
print('Export:',ARCHIVE_PATH.name,'bytes:',ARCHIVE_PATH.stat().st_size)
print('SHA256:',hashlib.sha256(ARCHIVE_PATH.read_bytes()).hexdigest())
""")
add('code',"from google.colab import files\nfiles.download(str(ARCHIVE_PATH))")
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'Trading_Research_Experiment_002.ipynb'},'kernelspec':{'display_name':'Python 3','name':'python3'}},'cells':cells}
(p/'Trading_Research_Experiment_002.ipynb').write_text(json.dumps(notebook,indent=1))
