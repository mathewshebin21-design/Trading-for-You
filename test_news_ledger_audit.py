import copy
import json
from pathlib import Path
import tempfile
import unittest
from news_ledger_audit import audit, report
from news_paper_lab import advance
from us_paper import sessions


def fixture():
    calendar = [{'date': '2026-10-09', 'open': '09:30', 'close': '16:00'}]
    now = sessions(calendar)[0][1] + 60000
    signal = {'bar_close_ms': now-86400000, 'observed_ms': now-1000,
              'fast': 101, 'slow': 100, 'target_long': True}
    news = {'valid': True, 'latest_receipt_ms': None, 'coverage_end_ms': now-900000}
    q = {'bid': 100., 'ask': 100.01, 'bid_qty': 100, 'ask_qty': 100, 'event_ms': now}
    state = advance(None, signal, q, calendar, now, news)
    state = advance(state, signal, {**q, 'event_ms': now+10}, calendar, now+10, news)
    return state, now+10


class LedgerAuditTests(unittest.TestCase):
    def test_replay_pass_does_not_certify_returns_or_mutate(self):
        state, now = fixture(); original = copy.deepcopy(state)
        result = audit(state, now)
        self.assertTrue(result['ledger_reconciled'])
        self.assertFalse(result['session_completeness_verified'])
        self.assertFalse(result['strategy_validated'])
        self.assertEqual(state, original)

    def test_cash_drift_and_nonfinite_balance_fail(self):
        for cash in (10000., float('nan')):
            state, now = fixture(); state['accounts']['baseline:1']['cash'] = cash
            result = audit(state, now)
            self.assertFalse(result['ledger_reconciled'])
            self.assertEqual(result['accounts']['baseline:1']['replay'], 'FAILED')

    def test_future_predecision_and_nonpaper_fills_fail(self):
        for change in ({'event_ms': 9999999999999}, {'decision_ms': 9999999999999}, {'mode': 'LIVE'}):
            state, now = fixture(); state['accounts']['baseline:1']['ledger'][0].update(change)
            self.assertFalse(audit(state, now)['ledger_reconciled'])

    def test_gaps_and_invalid_day_are_retained(self):
        state, now = fixture(); state['coverage_gaps'] = 1
        state['daily_marks']['2026-10-09']['valid'] = False
        result = audit(state, now)
        self.assertEqual(result['coverage_gaps'], 1)
        self.assertEqual(result['invalid_comparison_days'], ['2026-10-09'])

    def test_rules_and_account_set_mismatch_rejected(self):
        for key in ('fingerprint', 'accounts'):
            state, now = fixture()
            if key == 'fingerprint': state[key] = 'changed'
            else: state[key].pop('baseline:1')
            with self.assertRaises(ValueError): audit(state, now)

    def test_malformed_state_and_day_rejected(self):
        with self.assertRaises(ValueError): audit([], 0)
        state, now = fixture(); state['daily_marks']['PRIVATE_SECRET'] = {'valid': False}
        with self.assertRaises(ValueError): audit(state, now)

    def test_report_reads_without_writing_and_redacts_malformed_content(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIn('No saved', '\n'.join(report(folder, 0)))
            state, now = fixture(); path = Path(folder)/'AAPL_news_lab.json'
            path.write_text(json.dumps(state)); before = path.read_bytes()
            self.assertIn('replay: PASS', '\n'.join(report(folder, now)))
            self.assertEqual(path.read_bytes(), before)
            path.write_text('PRIVATE_SECRET')
            result = '\n'.join(report(folder, now))
            self.assertIn('AUDIT_FAILED', result)
            self.assertNotIn('PRIVATE_SECRET', result)
