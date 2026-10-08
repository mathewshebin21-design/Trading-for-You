"""Bounded local recovery snapshots. Same-volume backup, not disaster recovery."""
from pathlib import Path
import os
import sqlite3
import tempfile
import zipfile


def snapshot(folder, db, day):
    from datetime import date
    date.fromisoformat(day)
    root=Path(folder);dest=root/'backups';dest.mkdir(exist_ok=True)
    final=dest/(day+'.zip')
    if final.exists():return False
    files=sorted(set(root.glob('**/*_state.json'))|set(root.glob('**/*_lab.json'))|
                 set(root.glob('**/quote_quality.json'))|set(root.glob('**/action_reviews/*.json')))
    if any(p.is_symlink() for p in files):raise ValueError('BACKUP_SYMLINK_REJECTED')
    if sum(p.stat().st_size for p in files)>20_000_000:
        raise ValueError('BACKUP_SIZE_LIMIT')
    with tempfile.TemporaryDirectory(dir=dest) as temp:
        db_path=Path(temp)/'telegram.sqlite'
        with sqlite3.connect(db_path) as target:db.backup(target)
        if db_path.stat().st_size>20_000_000:raise ValueError('BACKUP_DATABASE_SIZE_LIMIT')
        archive=Path(temp)/'snapshot.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(db_path,'telegram.sqlite')
            for p in files:z.write(p,p.relative_to(root).as_posix())
        os.chmod(archive,0o600);archive.replace(final)
    for old in sorted(dest.glob('*.zip'))[:-3]:old.unlink()
    return True
