import copy
import json
from pathlib import Path
import tempfile
import unittest
import test_action_review_bootstrap
from review_install import run


class ReviewInstallTests(unittest.TestCase):
    def prepare(self, folder):
        return test_action_review_bootstrap.BootstrapTests().prepare(folder)

    def test_private_validation_and_install_preserve_entire_lab(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder); before=saved.read_bytes()
            self.assertEqual(run(folder,src,now)['accounts_checked'],4)
            target=Path(folder)/'us_automatic/action_reviews/AAPL.json'
            self.assertFalse(target.exists())
            self.assertTrue(run(folder,src,now,install=True)['installed'])
            self.assertEqual(saved.read_bytes(),before)
            with self.assertRaisesRegex(ValueError,'EXISTING_REVIEW_PRESERVED'):
                run(folder,src,now,install=True)

    def test_wrong_currency_or_bad_balance_never_installs(self):
        for field,value in [('currency','EUR'),('cash',1)]:
            with tempfile.TemporaryDirectory() as folder:
                src,saved,m,now=self.prepare(folder)
                s=json.loads(saved.read_text());s['accounts']['baseline:1'][field]=value
                saved.write_text(json.dumps(s)); before=saved.read_bytes()
                with self.assertRaises(ValueError):run(folder,src,now,install=True)
                self.assertFalse((Path(folder)/'us_automatic/action_reviews/AAPL.json').exists())
                self.assertEqual(saved.read_bytes(),before)

    def test_expired_review_can_only_validate_explicit_historical_day(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder)
            with self.assertRaises(ValueError):run(folder,src,now+86400000,install=True)
            result=run(folder,src,now+86400000,through='2026-10-09',install=True)
            self.assertFalse(result['current_day_covered'])
            with self.assertRaisesRegex(ValueError,'FUTURE_REVIEW_REJECTED'):
                run(folder,src,now,through='2026-10-10')

    def test_original_earlier_date_is_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder)
            original=copy.deepcopy(json.loads(saved.read_text())['accounts']['baseline:1'])
            original.update(version='US.1',accounted_through='2026-10-08')
            (Path(folder)/'us_automatic/AAPL_state.json').write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError,'ACTION_COVERAGE_INCOMPLETE'):
                run(folder,src,now,install=True)
            m['coverage_start']='2026-10-08';src.write_text(json.dumps(m))
            self.assertEqual(run(folder,src,now,install=True)['accounts_checked'],5)
