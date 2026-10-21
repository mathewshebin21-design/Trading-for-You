import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from us_paper import account, report_us, track_quality


class ReviewReportingTests(unittest.TestCase):
    def test_blocks_and_unknown_outcomes_not_counted_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            track_quality(folder,[{'symbol':'AAPL','status':'CORPORATE_ACTION_REVIEW_REQUIRED'},
                                  {'symbol':'SPY','status':'NEW_UNKNOWN_STATUS'}],1791554400000)
            counts=next(iter(json.loads((Path(folder)/'quote_quality.json').read_text()).values()))
            self.assertEqual(counts['AAPL'],{'CORPORATE_ACTION_REVIEW_REQUIRED':1})
            self.assertEqual(counts['SPY'],{'UNCLASSIFIED_CYCLE':1})

    def test_unreviewed_or_old_mark_never_displayed_as_current_pnl(self):
        for review,age in [(True,1),(False,6000)]:
            with tempfile.TemporaryDirectory() as folder:
                s=account('AAPL');s['review_required']=review
                s['quote']={'bid':100,'ask':100.01,'event_ms':10000-age}
                (Path(folder)/'AAPL_state.json').write_text(json.dumps(s))
                with patch.dict('os.environ',{'US_PAPER_ENABLED':'1'}),patch('us_paper.now_ms',return_value=10000):
                    result='\n'.join(report_us(folder))
                self.assertIn('Current equity/P&L unavailable',result)
                self.assertNotIn('net P/L $',result)
