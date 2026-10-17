import json
from pathlib import Path
import tempfile
import unittest

from aapl_review_check import check
from test_news_ledger_audit import fixture

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT/'research/action_reviews/AAPL_2026-10-16.json'
NOW = 1792212993000


class ReviewCheckTests(unittest.TestCase):
    def prepare(self, folder):
        state, _ = fixture()
        state['coverage_gaps'] = 3
        original = state['accounts']['baseline:1']
        original['accounted_through'] = '2026-10-08'
        root = Path(folder)/'us_automatic'
        lab = root/'news_lab'; lab.mkdir(parents=True)
        (root/'AAPL_state.json').write_text(json.dumps(original))
        (lab/'AAPL_news_lab.json').write_text(json.dumps(state))
        return root

    def test_review_passes_copies_without_mutating_any_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.prepare(folder)
            before = {p: p.read_bytes() for p in root.rglob('*.json')}
            result = check(folder, REVIEW, '2026-10-16', NOW)
            self.assertTrue(result['all_copied_reconciliations_passed'])
            self.assertEqual({p:p.read_bytes() for p in root.rglob('*.json')}, before)
            self.assertFalse((root/'action_reviews/AAPL.json').exists())
            self.assertFalse(result['strategy_validated'])

    def test_missing_accounts_do_not_count_as_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            result = check(folder, REVIEW, '2026-10-16', NOW)
            self.assertFalse(result['all_required_accounts_present'])
            self.assertFalse(result['all_copied_reconciliations_passed'])

    def test_corrupt_private_input_is_redacted_and_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.prepare(folder)
            (root/'AAPL_state.json').write_text('PRIVATE_SENTINEL')
            result = check(folder, REVIEW, '2026-10-16', NOW)
            self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))
            self.assertFalse(result['all_copied_reconciliations_passed'])

    def test_balance_drift_and_missing_earlier_coverage_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.prepare(folder)
            manifest = json.loads(REVIEW.read_text())
            manifest['coverage_start'] = '2026-10-09'
            review = Path(folder)/'review.json';review.write_text(json.dumps(manifest))
            result = check(folder, review, '2026-10-16', NOW)
            self.assertEqual(result['accounts']['original'], 'ACTION_COVERAGE_INCOMPLETE')
            original = json.loads((root/'AAPL_state.json').read_text())
            original['cash'] += 1
            (root/'AAPL_state.json').write_text(json.dumps(original))
            result = check(folder, REVIEW, '2026-10-16', NOW)
            self.assertEqual(result['accounts']['original'], 'LEDGER_BALANCE_MISMATCH')
            self.assertFalse(result['all_copied_reconciliations_passed'])

    def test_dated_review_cannot_cover_later_or_future_days(self):
        with tempfile.TemporaryDirectory() as folder:
            self.prepare(folder)
            result = check(folder, REVIEW, '2026-10-17', NOW)
            self.assertFalse(result['all_copied_reconciliations_passed'])
            self.assertEqual(result['accounts']['original'], 'ACTION_COVERAGE_INCOMPLETE')
            with self.assertRaises(ValueError):
                check(folder, REVIEW, '2026-10-18', NOW)


if __name__ == '__main__':
    unittest.main()
