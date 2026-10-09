import unittest
from research_inputs import connect, ingest, report

NOW = 1791504000000


def record():
    return {'kind': 'news', 'source_url': 'https://example.org/fixture',
            'publisher': 'Synthetic fixture', 'published_at': '2026-10-09T00:00:00Z',
            'symbols': ['SPY'], 'summary': 'Synthetic test only; no market claim.',
            'tool': 'manual-fixture', 'tool_revision': 'fixture-v1'}


class ResearchInputTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(':memory:')

    def tearDown(self):
        self.db.close()

    def test_receipt_blocks_lookahead_even_for_old_publication(self):
        ingest(self.db, record(), lambda: NOW+100)
        self.assertEqual(report(self.db, NOW), [])
        self.assertEqual(len(report(self.db, NOW+100)), 1)

    def test_duplicate_preserves_first_receipt_and_revision_is_separate(self):
        digest = ingest(self.db, record(), lambda: NOW)
        self.assertEqual(digest, ingest(self.db, record(), lambda: NOW+1000))
        ingest(self.db, {**record(), 'summary': 'Revised synthetic fixture.'}, lambda: NOW+2000)
        rows = report(self.db, NOW+2000)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['first_received_ms'], NOW)

    def test_freshness_changes_without_rewriting_evidence(self):
        ingest(self.db, record(), lambda: NOW)
        self.assertEqual(report(self.db, NOW)[0]['freshness'], 'RECENT')
        row = report(self.db, NOW+86400001)[0]
        self.assertEqual(row['freshness'], 'STALE')
        self.assertFalse(row['execution_eligible'])
        self.assertEqual(row['verification'], 'ATTRIBUTED_NOT_VERIFIED')

    def test_invalid_records_leave_inbox_empty(self):
        for change in ({'published_at':'2026-10-10T00:00:00Z'},
                       {'published_at':'2026-10-09T00:00:00'},
                       {'source_url':'https://example.org/?token=private'},
                       {'publisher':''}, {'symbols':['UNKNOWN']},
                       {'summary':'x'*1001}, {'execution_eligible':True}):
            with self.assertRaises(ValueError):
                ingest(self.db, {**record(), **change}, lambda: NOW)
        self.assertEqual(report(self.db, NOW), [])

    def test_normalized_timezone_and_symbols_deduplicate(self):
        first = ingest(self.db, record(), lambda: NOW)
        second = ingest(self.db, {**record(), 'published_at':'2026-10-09T05:30:00+05:30', 'symbols':['SPY','SPY']}, lambda: NOW+100)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
