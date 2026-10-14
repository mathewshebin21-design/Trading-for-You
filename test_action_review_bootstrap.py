import copy
import json
from pathlib import Path
import tempfile
import unittest
from action_review_bootstrap import install
from test_news_ledger_audit import fixture


class BootstrapTests(unittest.TestCase):
    def test_earlier_original_account_requires_earlier_review_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder)
            s=json.loads(saved.read_text())
            original=copy.deepcopy(s['accounts']['baseline:1'])
            original['accounted_through']='2026-10-08'
            path=Path(folder)/'us_automatic/AAPL_state.json'
            path.write_text(json.dumps(original));before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'ACTION_COVERAGE_INCOMPLETE'):
                install(folder,src,now)
            m['coverage_start']='2026-10-08';src.write_text(json.dumps(m))
            self.assertIn('INSTALLED',install(folder,src,now))
            self.assertEqual(path.read_bytes(),before)

    def prepare(self, folder):
        state, now = fixture()
        manifest={'symbol':'AAPL','currency':'USD','reviewed':True,'reviewer':'fixture',
                  'reviewed_ms':now,'source_urls':['https://example.test/fixture'],
                  'coverage_start':'2026-10-09','coverage_end':'2026-10-09','actions':[]}
        src=Path(folder)/'review.json';src.write_text(json.dumps(manifest))
        lab=Path(folder)/'us_automatic/news_lab';lab.mkdir(parents=True)
        saved=lab/'AAPL_news_lab.json';saved.write_text(json.dumps(state))
        return src,saved,manifest,now

    def test_installs_without_changing_accounts_or_invalid_days(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,_,now=self.prepare(folder);before=saved.read_bytes()
            self.assertIn('INSTALLED',install(folder,src,now))
            self.assertEqual(saved.read_bytes(),before)
            target=Path(folder)/'us_automatic/action_reviews/AAPL.json'
            before=target.read_bytes();src.write_text('PRIVATE_SECRET')
            self.assertEqual(install(folder,src,now),'EXISTING_REVIEW_PRESERVED')
            self.assertEqual(target.read_bytes(),before)

    def test_expired_review_cannot_extend_coverage(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,_,now=self.prepare(folder);before=saved.read_bytes()
            self.assertIn('EXPIRED',install(folder,src,now+86400000))
            self.assertFalse((Path(folder)/'us_automatic/action_reviews/AAPL.json').exists())
            self.assertEqual(saved.read_bytes(),before)

    def test_bad_review_or_balance_refused_before_write(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder)
            m['reviewed']=False;src.write_text(json.dumps(m))
            with self.assertRaises(ValueError):install(folder,src,now)
            m['reviewed']=True;src.write_text(json.dumps(m))
            s=json.loads(saved.read_text());s['accounts']['baseline:1']['cash']+=1
            saved.write_text(json.dumps(s));before=saved.read_bytes()
            with self.assertRaises(ValueError):install(folder,src,now)
            self.assertEqual(saved.read_bytes(),before)
            self.assertFalse((Path(folder)/'us_automatic/action_reviews/AAPL.json').exists())
