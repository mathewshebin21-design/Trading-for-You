import os
import unittest
from unittest.mock import patch
from news_collector import collect, convert
from research_inputs import connect, ingest, report

NOW=1791504000000


def article():
    return {'id':1,'created_at':'2026-10-08T23:00:00Z',
            'updated_at':'2026-10-08T23:01:00Z','symbols':['AAPL','OTHER'],
            'url':'https://example.org/fixture','source':'Synthetic',
            'headline':'Synthetic headline','summary':'Synthetic summary'}


class NewsTests(unittest.TestCase):
    def test_disabled_never_attempts_network(self):
        with patch.dict(os.environ,{},clear=True), patch('urllib.request.build_opener') as opener:
            self.assertEqual(collect(None)['status'],'DISABLED')
            opener.assert_not_called()

    def test_missing_credentials_never_attempts_network(self):
        with patch.dict(os.environ,{'RESEARCH_NEWS_ENABLED':'1'},clear=True), patch('urllib.request.build_opener') as opener:
            self.assertEqual(collect(None)['status'],'CREDENTIALS_MISSING')
            opener.assert_not_called()

    def test_mapping_and_no_copied_content(self):
        row=convert(article(),NOW)
        self.assertEqual(row['symbols'],['AAPL'])
        self.assertNotIn('Synthetic headline',row['summary'])

    def test_revision_creates_separate_receipt(self):
        db=connect(':memory:')
        try:
            ingest(db,convert(article(),NOW),lambda:NOW)
            ingest(db,convert({**article(),'headline':'Edited fixture'},NOW+1),lambda:NOW+1)
            self.assertEqual(len(report(db,NOW)),1)
            self.assertEqual(len(report(db,NOW+1)),2)
        finally:db.close()

    def test_future_naive_and_reversed_updates_rejected(self):
        for change in ({'updated_at':'2026-10-10T00:00:00Z'},
                       {'updated_at':'2026-10-08T22:00:00Z'},
                       {'created_at':'2026-10-08T23:00:00'}):
            with self.assertRaises(ValueError):convert({**article(),**change},NOW)

    def test_unmapped_symbol_rejected(self):
        with self.assertRaises(ValueError):convert({**article(),'symbols':['OTHER']},NOW)


if __name__=='__main__':unittest.main()
