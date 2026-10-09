"""Summarize existing development backtests; no inference of future profits."""
import argparse
import hashlib
import json
from pathlib import Path


def summarize(path):
    raw=Path(path).read_bytes()
    rows=json.loads(raw)['results']
    output=[]
    for cost in (1,2):
        for symbol in ('SPY','AAPL','GLD','BTC-USD','ETH-USD'):
            group=[r for r in rows if r['symbol']==symbol and r['cost_multiplier']==cost]
            if not group:raise ValueError('Missing comparison group')
            if len({r['window'] for r in group})!=len(group):raise ValueError('Duplicate window')
            output.append({'symbol':symbol,'cost_multiplier':cost,'windows':len(group),
                'benchmark_wins':sum(r['strategy']['net_return_pct']>r['benchmark']['net_return_pct'] for r in group),
                'worst_window_return_pct':min(r['strategy']['net_return_pct'] for r in group),
                'worst_window_drawdown_pct':min(r['strategy']['maximum_drawdown_pct'] for r in group),
                'closed_trades_including_terminal_liquidations':sum(r['strategy']['closed_trades'] for r in group)})
    return {'source_sha256':hashlib.sha256(raw).hexdigest(),'comparison_rows':len(rows),
            'classification':'RETROSPECTIVE_DEVELOPMENT_NOT_VALIDATED',
            'continuous_portfolio':False,'summary':output}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('results_json')
    print(json.dumps(summarize(p.parse_args().results_json),indent=2,allow_nan=False))
