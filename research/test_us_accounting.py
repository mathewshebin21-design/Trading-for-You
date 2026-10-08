from copy import deepcopy
from datetime import datetime
import unittest
from zoneinfo import ZoneInfo
from us_accounting import reconcile, receivable_value, audit_balances, ReviewRequired

def ms(day):
    return int(datetime.fromisoformat(day+'T10:00:00').replace(tzinfo=ZoneInfo('America/New_York')).timestamp()*1000)

def state():
    return {'symbol':'AAPL','currency':'USD','cash':9699.,'units':3,'peak':10000.,
            'last_session':'2026-10-08','quote':{'bid':100},'review_required':True,
            'ledger':[{'side':'BUY','quantity':3,'model_fill_price':100,'commission':1,'event_ms':ms('2026-10-08')}]}

def manifest(actions=None, day='2026-10-09'):
    return {'symbol':'AAPL','currency':'USD','reviewed':True,'reviewer':'fixture-review',
            'source_urls':['https://example.org/fixture-only'],
            'coverage_start':'2026-10-08','coverage_end':day,'reviewed_ms':ms(day),
            'actions':actions or []}

class AccountingTests(unittest.TestCase):
    def test_reviewed_no_action_and_balance_audit(self):
        s=reconcile(state(),manifest(),'2026-10-09',ms('2026-10-09'))
        self.assertFalse(s['review_required']);audit_balances(s)
        self.assertEqual(s['cash'],9699)
    def test_split_idempotent_on_restart_and_invalidates_old_quote(self):
        action={'id':'s','type':'split','ex_date':'2026-10-09','ratio':2}
        s=reconcile(state(),manifest([action]),'2026-10-09',ms('2026-10-09'))
        self.assertEqual(s['units'],6);self.assertIsNone(s['quote'])
        self.assertEqual(s,reconcile(s,manifest([action]),'2026-10-09',ms('2026-10-09')))
    def test_dividend_entitlement_survives_sale_until_payment(self):
        a={'id':'d','type':'cash_dividend','ex_date':'2026-10-09','pay_date':'2026-10-12','cash_per_share':2}
        s=reconcile(state(),manifest([a]),'2026-10-09',ms('2026-10-09'))
        self.assertEqual(s['cash'],9699);self.assertEqual(receivable_value(s),6)
        s['ledger'].append({'side':'SELL','quantity':3,'model_fill_price':100,'commission':1,'event_ms':ms('2026-10-09')+1})
        s['cash']+=299;s['units']=0;s['last_session']='2026-10-09'
        s=reconcile(s,manifest([a],'2026-10-12'),'2026-10-12',ms('2026-10-12'))
        self.assertEqual(s['cash'],10004);self.assertEqual(receivable_value(s),0)
        self.assertEqual(s,reconcile(s,manifest([a],'2026-10-12'),'2026-10-12',ms('2026-10-12')))
    def test_revision_and_removed_records_block(self):
        a={'id':'s','type':'split','ex_date':'2026-10-09','ratio':2}
        s=reconcile(state(),manifest([a]),'2026-10-09',ms('2026-10-09'))
        for m in (manifest([{**a,'ratio':3}]),manifest()):
            with self.assertRaises(ReviewRequired):reconcile(s,m,'2026-10-09',ms('2026-10-09'))
    def test_fractional_split_rolls_back(self):
        original=state();snapshot=deepcopy(original)
        a={'id':'s','type':'split','ex_date':'2026-10-09','ratio':.5}
        with self.assertRaisesRegex(ReviewRequired,'FRACTIONAL'):
            reconcile(original,manifest([a]),'2026-10-09',ms('2026-10-09'))
        self.assertEqual(original,snapshot)
    def test_late_and_unsupported_actions_block(self):
        for a in ({'id':'l','type':'split','ex_date':'2026-10-08','ratio':2},
                  {'id':'u','type':'merger','ex_date':'2026-10-09'}):
            with self.assertRaises(ReviewRequired):reconcile(state(),manifest([a]),'2026-10-09',ms('2026-10-09'))
    def test_future_coverage_missing_attestation_and_corruption_block(self):
        for patch in ({'reviewed':False},{'coverage_end':'2026-10-12'},{'source_urls':[]}):
            with self.assertRaises(ReviewRequired):reconcile(state(),{**manifest(),**patch},'2026-10-09',ms('2026-10-09'))
        s=state();s['cash']+=1
        with self.assertRaisesRegex(ReviewRequired,'BALANCE_MISMATCH'):
            reconcile(s,manifest(),'2026-10-09',ms('2026-10-09'))
