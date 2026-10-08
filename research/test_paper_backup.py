import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
import zipfile
from paper_backup import snapshot

class BackupTests(unittest.TestCase):
    def test_consistent_database_and_state_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'SPY_state.json';p.write_text('{"cash":10000}')
            with sqlite3.connect(root/'telegram.sqlite') as db:
                db.execute('CREATE TABLE fixture(value INTEGER)');db.execute('INSERT INTO fixture VALUES(7)');db.commit()
                self.assertTrue(snapshot(root,db,'2026-10-09'))
                self.assertFalse(snapshot(root,db,'2026-10-09'))
            restore=root/'restore';restore.mkdir()
            with zipfile.ZipFile(root/'backups'/'2026-10-09.zip') as z:z.extractall(restore)
            self.assertEqual(json.loads((restore/'SPY_state.json').read_text())['cash'],10000)
            with sqlite3.connect(restore/'telegram.sqlite') as db:
                self.assertEqual(db.execute('SELECT value FROM fixture').fetchone()[0],7)
    def test_retention_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with sqlite3.connect(':memory:') as db:
                for day in range(1,6):snapshot(root,db,f'2026-10-{day:02d}')
                self.assertEqual(len(list((root/'backups').glob('*.zip'))),3)
                (root/'bad_state.json').symlink_to(root/'missing')
                with self.assertRaisesRegex(ValueError,'SYMLINK'):snapshot(root,db,'2026-10-06')
