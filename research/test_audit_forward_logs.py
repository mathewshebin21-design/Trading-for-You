import copy
import unittest
from audit_forward_logs import audit, ACCOUNTS


def records():
    # 9 October 2026, 14:00 UTC. Synthetic fixture, not market evidence.
    return [{'observed_ms': 1791554400000 + offset, 'paper_only': True,
             'coverage_valid': True, 'statuses': {k: 'NO_ACTION' for k in ACCOUNTS}}
            for offset in (0, 300000, 600000)]


class AuditTests(unittest.TestCase):
    def test_valid_news_does_not_hide_corporate_review_or_quote_rejection(self):
        for status in ('CORPORATE_ACTION_REVIEW_REQUIRED', 'NO_FILL_QUOTE_UNAVAILABLE',
                       'NEWS_COVERAGE_ENTRY_BLOCKED'):
            rows = records()
            rows[1]['statuses']['baseline:1'] = status
            original = copy.deepcopy(rows)
            result = audit(rows)
            self.assertTrue(result['review_required'])
            self.assertEqual(result['blocked_status_counts']['baseline:1'], {status: 1})
            self.assertFalse(result['strategy_validated'])
            self.assertEqual(rows, original)

    def test_clean_logs_do_not_certify_performance(self):
        result = audit(records())
        self.assertFalse(result['review_required'])
        for key in ('session_completeness_verified', 'ledger_reconciled', 'strategy_validated'):
            self.assertFalse(result[key])

    def test_valid_news_does_not_hide_observation_gap(self):
        rows = records(); rows[-1]['observed_ms'] += 600001
        result = audit(rows)
        self.assertTrue(result['review_required'])
        self.assertEqual(len(result['candidate_observation_gaps']), 1)

    def test_news_failure_and_missing_accounts(self):
        rows = records(); rows[1]['coverage_valid'] = False
        self.assertTrue(audit(rows)['review_required'])
        rows[1]['statuses'].pop('baseline:1')
        with self.assertRaises(ValueError): audit(rows)

    def test_duplicate_unordered_and_nonpaper_rejected(self):
        for modifier in ('duplicate', 'unordered', 'nonpaper'):
            rows = records()
            if modifier == 'duplicate': rows[1]['observed_ms'] = rows[0]['observed_ms']
            elif modifier == 'unordered': rows.reverse()
            else: rows[1]['paper_only'] = False
            with self.assertRaises(ValueError): audit(rows)
        with self.assertRaises(ValueError): audit([])

    def test_overnight_is_not_intraday_gap_and_input_is_unchanged(self):
        rows = records(); rows[-1]['observed_ms'] += 86400000
        original = copy.deepcopy(rows)
        self.assertEqual(audit(rows)['candidate_observation_gaps'], [])
        self.assertEqual(rows, original)
