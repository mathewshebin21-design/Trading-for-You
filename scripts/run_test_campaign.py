"""Run deployment and research fixture suites in separate interpreters.

Offline research/paper verification only. No provider calls or order placement.
The evidence report contains counts and source hashes, not captured test output.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]


def main():
    results = []
    for name, directory in (('deployment', ROOT), ('research', ROOT / 'research')):
        completed = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', '.', '-p', 'test_*.py'],
            cwd=directory, text=True, capture_output=True, timeout=120,
        )
        count = re.search(r'Ran (\d+) tests?', completed.stderr)
        passed = completed.returncode == 0 and count is not None and int(count[1]) > 0
        results.append({'suite': name, 'tests': int(count[1]) if count else None,
                        'passed': passed, 'returncode': completed.returncode})
        print(json.dumps(results[-1]))
    sources = {}
    for path in sorted(ROOT.rglob('*.py')):
        if '.git' not in path.parts:
            sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {'checked_at': datetime.now(timezone.utc).isoformat(),
              'mode': 'OFFLINE_FIXTURE_TESTS', 'suites': results,
              'source_sha256': sources, 'strategy_validated': False,
              'limitations': 'Passing tests verify fixture behavior, not production uptime or trading edge.'}
    destination = ROOT / 'research' / 'TEST_CAMPAIGN_LATEST.json'
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return 0 if all(result['passed'] for result in results) else 1


if __name__ == '__main__':
    sys.exit(main())
