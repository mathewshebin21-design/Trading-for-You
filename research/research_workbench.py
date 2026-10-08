"""Read-only research infrastructure. Paper trading only; no order execution."""
from datetime import datetime, timezone
from pathlib import Path
import csv
import hashlib
import json
import math
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

VERSION = '0.1.0'
ALLOWED_HOSTS = {'data-api.binance.vision', 'www.federalreserve.gov'}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def validate_bars(rows):
    """Validate daily OHLCV research rows; never repair invalid data silently."""
    if not rows:
        raise ValueError('Empty dataset')
    previous = None
    clean = []
    for row in rows:
        date = datetime.strptime(str(row['date']), '%Y-%m-%d').date()
        if previous is not None and date <= previous:
            raise ValueError('Dates must be increasing and unique')
        previous = date
        vals = {k: float(row[k]) for k in ('open', 'high', 'low', 'close', 'volume')}
        if not all(math.isfinite(v) for v in vals.values()):
            raise ValueError('Non-finite numeric value')
        if any(vals[k] <= 0 for k in ('open', 'high', 'low', 'close')) or vals['volume'] < 0:
            raise ValueError('Invalid price or volume')
        if not (vals['low'] <= min(vals['open'], vals['close']) <=
                max(vals['open'], vals['close']) <= vals['high']):
            raise ValueError('Inconsistent OHLC range')
        clean.append({'date': date.isoformat(), **vals})
    return clean


def dataset_report(rows, symbol, source, synthetic=False):
    rows = validate_bars(rows)
    dates = [datetime.strptime(r['date'], '%Y-%m-%d').date() for r in rows]
    return {
        'symbol': symbol, 'source': source, 'synthetic': synthetic,
        'status': 'DEMO ONLY' if synthetic else 'DATA CHECK ONLY — NOT VALIDATED FOR TRADING',
        'rows': len(rows), 'first_date': rows[0]['date'], 'last_date': rows[-1]['date'],
        'calendar_gaps_over_3_days': sum((b-a).days > 3 for a,b in zip(dates, dates[1:])),
        'zero_volume_bars': sum(r['volume'] == 0 for r in rows),
        'observed_at': utc_now(),
        'limitations': 'Dates are bar labels, not receipt timestamps. Calendar gaps require market-specific review. '
                       'Corporate actions, final-bar completeness and point-in-time universe not verified.',
    }


def read_bar_csv(path):
    with Path(path).open(newline='') as f:
        return validate_bars(list(csv.DictReader(f)))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    tmp.replace(path)


class ReadOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError('Redirect outside approved read-only source')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_readonly(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError('URL outside read-only source allowlist')
    request = urllib.request.Request(url, headers={'User-Agent': 'TradingResearchWorkbench/0.1'}, method='GET')
    with urllib.request.build_opener(ReadOnlyRedirect()).open(request, timeout=15) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Response exceeds research size limit')
    return raw, utc_now()


def parse_quote(raw, symbol, observed_at):
    record = json.loads(raw)
    if record.get('symbol') != symbol:
        raise ValueError('Unexpected quote symbol')
    bid, ask = float(record['bidPrice']), float(record['askPrice'])
    if not all(math.isfinite(v) and v > 0 for v in (bid, ask)) or ask < bid:
        raise ValueError('Invalid or crossed quote')
    return {
        'symbol': symbol, 'venue': 'Binance spot', 'quote_currency': 'USDT',
        'bid': bid, 'ask': ask, 'observed_at': observed_at,
        'source_event_time': None, 'source_update_id': record.get('lastUpdateId'),
        'latency_status': 'UNKNOWN: source event timestamp unavailable',
        'status': 'OBSERVATION ONLY — NOT A TRADE SIGNAL',
    }


def crypto_snapshot(symbol):
    if symbol not in {'BTCUSDT', 'ETHUSDT'}:
        raise ValueError('Symbol outside research scope')
    raw, seen = fetch_readonly('https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=' + symbol)
    return parse_quote(raw, symbol, seen), raw


def parse_news(raw, observed_at):
    root = ET.fromstring(raw)
    return [{
        'title': item.findtext('title', ''), 'url': item.findtext('link', ''),
        'publisher_time_raw': item.findtext('pubDate', ''),
        'observed_at': observed_at, 'publisher': 'Federal Reserve',
        'status': 'SOURCE REPORT — MARKET EFFECT UNTESTED',
    } for item in root.findall('.//item')]


def fed_news():
    raw, seen = fetch_readonly('https://www.federalreserve.gov/feeds/press_all.xml')
    return parse_news(raw, seen), raw


def archive_raw(folder, source_name, raw):
    digest = hashlib.sha256(raw).hexdigest()
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / (source_name + '_' + digest + '.raw')
    if not filename.exists():
        filename.write_bytes(raw)
    return {'sha256': digest, 'path': str(filename), 'bytes': len(raw)}


def new_claim(source_url, claim_text, evidence='E0'):
    if evidence not in {'E0', 'E1', 'E2', 'E3', 'E4'}:
        raise ValueError('Invalid evidence tier')
    return {'source_url': source_url, 'claim': claim_text, 'evidence_tier': evidence,
            'recorded_at': utc_now(), 'verification': 'PENDING',
            'original_video_timestamp': None, 'data_provenance': None,
            'complete_record_available': False, 'copy_eligible': False,
            'notes': 'Source claim only. No independently verified profitability.'}


def self_checks():
    """Targeted validation checks using fixtures, never simulated performance."""
    import unittest
    class Checks(unittest.TestCase):
        def setUp(self):
            self.row = {'date':'2026-01-01','open':10,'high':11,'low':9,'close':10,'volume':100}
        def test_valid_bar(self):
            self.assertEqual(len(validate_bars([self.row])), 1)
        def test_duplicate_date(self):
            with self.assertRaises(ValueError): validate_bars([self.row, self.row])
        def test_invalid_prices(self):
            for patch in ({'close':12}, {'volume':-1}, {'open':float('nan')}, {'low':0}):
                with self.assertRaises(ValueError): validate_bars([{**self.row, **patch}])
        def test_block_order_endpoint(self):
            with self.assertRaises(ValueError): fetch_readonly('https://api.binance.com/api/v3/order')
        def test_quote_timestamps_honest(self):
            q = parse_quote(b'{"symbol":"BTCUSDT","bidPrice":"10","askPrice":"11"}', 'BTCUSDT','2026-01-01T00:00:00+00:00')
            self.assertIsNone(q['source_event_time'])
        def test_crossed_quote(self):
            with self.assertRaises(ValueError):
                parse_quote(b'{"symbol":"BTCUSDT","bidPrice":"12","askPrice":"11"}', 'BTCUSDT','now')
        def test_news_distinguishes_observation(self):
            r = parse_news(b'<rss><channel><item><title>Fixture</title><pubDate>Earlier</pubDate></item></channel></rss>', 'Later')
            self.assertEqual(r[0]['publisher_time_raw'], 'Earlier')
            self.assertEqual(r[0]['observed_at'], 'Later')
        def test_claim_ineligible_default(self):
            self.assertFalse(new_claim('https://example.org','Unverified fixture')['copy_eligible'])
    result = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(Checks))
    if not result.wasSuccessful():
        raise RuntimeError('Research validation checks failed')
    return {'tests': result.testsRun, 'passed': result.wasSuccessful()}
