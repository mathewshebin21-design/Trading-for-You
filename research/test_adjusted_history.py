import unittest,tempfile
from pathlib import Path
from adjusted_history import load_adjusted_history
class AdjustedHistoryTests(unittest.TestCase):
    def test_rounding_audited_raw_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.csv';raw='Date,Open,High,Low,Close,Volume\n2026-01-01,100,100,99,100.00000000000001,1\n';p.write_text(raw)
            rows,fixes=load_adjusted_history(p)
            self.assertEqual(p.read_text(),raw);self.assertEqual(len(fixes),1)
            self.assertGreaterEqual(rows[0]['high'],rows[0]['close'])
    def test_material_violation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.csv';p.write_text('Date,Open,High,Low,Close,Volume\n2026-01-01,100,100,99,100.01,1\n')
            with self.assertRaises(ValueError):load_adjusted_history(p)
