"""Private, research-only evidence inbox. No fetching, models or order endpoints.

Source attribution is not factual verification. Receipt time is assigned locally,
never taken from an imported claim. Future hypotheses cannot consume records
before this receipt time. No record can authorize a paper or real order.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import time
from urllib.parse import urlsplit

SYMBOLS = {'BTCUSDT', 'ETHUSDT', 'SPY', 'AAPL', 'GLD'}
FIELDS = {'kind', 'source_url', 'publisher', 'published_at', 'symbols',
          'summary', 'tool', 'tool_revision'}


def normalize(record, received_ms):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError('RESEARCH_SCHEMA_INVALID')
    if record['kind'] not in ('news', 'analysis', 'trader_claim'):
        raise ValueError('RESEARCH_KIND_INVALID')
    for key in ('source_url', 'publisher', 'published_at', 'summary', 'tool', 'tool_revision'):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError('RESEARCH_ATTRIBUTION_MISSING')
    parsed = urlsplit(record['source_url'])
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('RESEARCH_CANONICAL_PUBLIC_URL_REQUIRED')
    if len(record['summary']) > 1000:
        raise ValueError('RESEARCH_SUMMARY_TOO_LONG')
    symbols = record['symbols']
    if not isinstance(symbols, list) or not symbols or any(not isinstance(s, str) or s not in SYMBOLS for s in symbols):
        raise ValueError('RESEARCH_SYMBOL_MAPPING_REQUIRED')
    published = datetime.fromisoformat(record['published_at'].replace('Z', '+00:00'))
    if published.tzinfo is None:
        raise ValueError('RESEARCH_TIMEZONE_REQUIRED')
    published_ms = int(published.timestamp() * 1000)
    if not 0 <= published_ms <= received_ms:
        raise ValueError('RESEARCH_PUBLICATION_TIME_INVALID')
    result = {**record, 'symbols': sorted(set(symbols)),
              'published_at': published.astimezone(timezone.utc).isoformat()}
    canonical = json.dumps(result, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return canonical, published_ms, hashlib.sha256(canonical.encode()).hexdigest()


def connect(path):
    db = sqlite3.connect(path)
    db.execute('''CREATE TABLE IF NOT EXISTS evidence (
        digest TEXT PRIMARY KEY, payload TEXT NOT NULL,
        published_ms INTEGER NOT NULL, first_received_ms INTEGER NOT NULL)''')
    return db


def ingest(db, record, clock=None):
    received = int(time.time() * 1000) if clock is None else clock()
    payload, published, digest = normalize(record, received)
    with db:
        db.execute('INSERT OR IGNORE INTO evidence VALUES (?, ?, ?, ?)',
                   (digest, payload, published, received))
    return digest


def report(db, as_of_ms, max_age_ms=86400000):
    if max_age_ms <= 0:
        raise ValueError('RESEARCH_AGE_LIMIT_INVALID')
    rows = db.execute('SELECT digest, payload, published_ms, first_received_ms FROM evidence WHERE first_received_ms <= ? ORDER BY first_received_ms, digest', (as_of_ms,))
    return [{**json.loads(payload), 'digest': digest, 'first_received_ms': received,
             'published_ms': published,
             'freshness': 'STALE' if as_of_ms-published > max_age_ms else 'RECENT',
             'verification': 'ATTRIBUTED_NOT_VERIFIED', 'execution_eligible': False}
            for digest, payload, published, received in rows]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, help='Private SQLite file; never commit it')
    parser.add_argument('--import-json', help='One attributed record; locally authored summary')
    args = parser.parse_args()
    with connect(args.db) as db:
        if args.import_json:
            ingest(db, json.loads(Path(args.import_json).read_text()))
        print(json.dumps(report(db, int(time.time()*1000)), indent=2))
