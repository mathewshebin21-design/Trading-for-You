"""Run pinned external diagnostics on private artifacts; never trading execution.

Requires the separate Vibe-Trading evaluation checkout and environment. No model,
agent, MCP server or broker is started. Results cannot qualify a strategy.
"""
import argparse
import json
from pathlib import Path
import subprocess

PIN = 'e532650b527ba3fb146ef00d533f6fc5040d5d2d'


def run(checkout, run_dir):
    checkout = Path(checkout).resolve()
    run_dir = Path(run_dir).resolve()
    head = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
    if head != PIN:
        raise ValueError('External revision changed; review required')
    # Refuse locally modified upstream code as well as a mismatched revision.
    subprocess.run(['git', '-C', str(checkout), 'diff', '--exit-code', 'HEAD', '--', 'agent'], check=True, capture_output=True)
    config = json.loads((run_dir / 'config.json').read_text())
    if config.get('initial_cash', 0) <= 0:
        raise ValueError('Explicit positive initial_cash required')
    for filename in ('equity.csv', 'trades.csv'):
        if not (run_dir / 'artifacts' / filename).is_file():
            raise ValueError('Missing private artifact: ' + filename)
    python = checkout / '.venv' / 'bin' / 'python'
    subprocess.run([str(python), '-m', 'backtest.validation', str(run_dir)],
                   cwd=checkout / 'agent', check=True, timeout=120,
                   env={'PATH': '/usr/bin:/bin', 'PYTHONNOUSERSITE': '1'})
    notice = {'classification': 'EXPLORATORY_NOT_VALIDATED', 'upstream_commit': PIN,
              'limitations': ['IID bootstrap does not preserve serial dependence',
                  'equity-window analysis is not strategy retraining or held-out testing',
                  'trade-order permutations do not establish profitable edge',
                  'upstream CSV loader excludes zero-P/L trades'],
              'execution_enabled': False}
    (run_dir / 'artifacts' / 'external_review.json').write_text(json.dumps(notice, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout')
    parser.add_argument('run_dir')
    args = parser.parse_args()
    run(args.checkout, args.run_dir)
