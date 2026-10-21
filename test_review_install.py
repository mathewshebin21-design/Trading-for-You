import copy
import json
from pathlib import Path
import tempfile
import unittest
import test_action_review_bootstrap
from review_install import run
from unittest.mock import patch


class ReviewInstallTests(unittest.TestCase):
    def test_frozen_experiments_remain_compatible_with_deployed_revision(self):
        from news_paper_lab import FINGERPRINT as news
        from prospective_lab import FINGERPRINT as shadow
        self.assertEqual(news,'9b2ed4ceae2a38623fb9d5181e00681064a8eaefe2034a8e54001b98aa403017')
        self.assertEqual(shadow,'2baf088047c229bf33eb4ce03f549cb936740d6fa5334f8eba43920cdbb14993')

    def test_incomplete_or_different_experiment_refused(self):
        for change in ('account_missing','fingerprint','version'):
            with tempfile.TemporaryDirectory() as folder:
                src,saved,m,now=self.prepare(folder)
                s=json.loads(saved.read_text())
                if change=='account_missing':del s['accounts']['baseline:1']
                else:s[change]='INVALID'
                saved.write_text(json.dumps(s))
                with self.assertRaisesRegex(ValueError,'LAB_VERSION_OR_ACCOUNTS_INVALID'):
                    run(folder,src,now,install=True)
                self.assertFalse((Path(folder)/'us_automatic/action_reviews/AAPL.json').exists())

    def test_failed_atomic_publication_cleans_temporary_file(self):
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder);before=saved.read_bytes()
            with patch('review_install.os.link',side_effect=OSError('private error')):
                with self.assertRaises(OSError):run(folder,src,now,install=True)
            self.assertEqual(list((Path(folder)/'us_automatic/action_reviews').iterdir()),[])
            self.assertEqual(saved.read_bytes(),before)

    def test_valid_review_clears_block_on_normal_lab_observation_without_erasing_invalid_day(self):
        from news_paper_lab import advance
        from us_paper import sessions
        with tempfile.TemporaryDirectory() as folder:
            src,saved,m,now=self.prepare(folder)
            s=json.loads(saved.read_text())
            s['daily_marks']['2026-10-09']['valid']=False
            s['coverage_gaps']=13
            for a in s['accounts'].values():a['review_required']=True
            saved.write_text(json.dumps(s));before=saved.read_bytes()
            run(folder,src,now,install=True)
            self.assertEqual(saved.read_bytes(),before)
            manifest=json.loads((Path(folder)/'us_automatic/action_reviews/AAPL.json').read_text())
            observed=now+1000
            a=s['accounts']['baseline:1']
            q={**a['quote'],'event_ms':observed}
            calendar=[{'date':'2026-10-09','open':'09:30','close':'16:00'}]
            news={'valid':True,'latest_receipt_ms':None,'coverage_end_ms':observed-900000}
            after=advance(s,a['signal'],q,calendar,observed,news,manifest=manifest)
            self.assertTrue(all(not x['review_required'] for x in after['accounts'].values()))
            self.assertFalse(after['daily_marks']['2026-10-09']['valid'])
            self.assertEqual(after['coverage_gaps'],13)
            self.assertEqual([len(x['ledger']) for x in after['accounts'].values()],[1]*4)

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
