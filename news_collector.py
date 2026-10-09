"""Opt-in Alpaca news metadata collector; research only, no orders or AI calls."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
import time
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
from research_inputs import connect, ingest, normalize
from prospective_paper import save_state

ENDPOINT = 'https://data.alpaca.markets/v1beta1/news'
SYMBOLS = {'SPY', 'AAPL', 'GLD'}


def convert(article, received):
    symbols = sorted(set(article['symbols']) & SYMBOLS)
    published = article['created_at']
    updated = article['updated_at']
    times = [datetime.fromisoformat(t.replace('Z', '+00:00')) for t in (published, updated)]
    if any(t.tzinfo is None for t in times) or not 0 <= times[0].timestamp()*1000 <= times[1].timestamp()*1000 <= received:
        raise ValueError('NEWS_TIME_INVALID')
    # Fingerprint provider content to preserve revisions without copying articles.
    digest = hashlib.sha256(json.dumps({k:article.get(k) for k in ('headline','summary','symbols','url','source')}, sort_keys=True).encode()).hexdigest()
    record = {'kind':'news', 'source_url':article['url'], 'publisher':article['source'],
              'published_at':published, 'symbols':symbols,
              'summary':'Provider indexed a news item. Content and relevance are not independently verified.',
              'tool':'alpaca-news-metadata',
              'tool_revision':f"NEWS.1:{article['id']}:{updated}:{digest}"}
    normalize(record, received)
    return record


def collect(db):
    if os.getenv('RESEARCH_NEWS_ENABLED') != '1':
        return {'status':'DISABLED', 'execution_enabled':False}
    key, secret = os.getenv('ALPACA_DATA_KEY'), os.getenv('ALPACA_DATA_SECRET')
    if not key or not secret:
        return {'status':'CREDENTIALS_MISSING', 'execution_enabled':False}
    # Omit end: provider chooses its entitlement-compatible latest time. Never
    # force a real-time tier or change subscription settings.
    start = (datetime.now(timezone.utc)-timedelta(hours=24)).isoformat()
    params = {'symbols':','.join(sorted(SYMBOLS)), 'limit':50, 'sort':'desc',
              'start':start, 'include_content':'false'}
    request = urllib.request.Request(ENDPOINT+'?'+urllib.parse.urlencode(params),
        headers={'APCA-API-KEY-ID':key,'APCA-API-SECRET-KEY':secret}, method='GET')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('NEWS_REDIRECT_REJECTED')
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=15) as response:
            raw = response.read(1000001)
        if len(raw)>1000000:raise ValueError('NEWS_RESPONSE_TOO_LARGE')
        data = json.loads(raw)
        if not isinstance(data['news'],list) or len(data['news'])>50:
            raise ValueError('NEWS_ENVELOPE_INVALID')
    except urllib.error.HTTPError as error:
        return {'status':'HTTP_'+str(error.code), 'execution_enabled':False}
    except (OSError, ValueError, KeyError, TypeError):
        return {'status':'NEWS_FETCH_UNAVAILABLE', 'execution_enabled':False}
    received = int(time.time()*1000)
    accepted, rejected = 0, 0
    for article in data['news']:
        try:
            ingest(db, convert(article, received), lambda:received)
            accepted += 1
        except (ValueError, KeyError, TypeError, AttributeError):
            rejected += 1
    return {'status':'RESEARCH_ONLY', 'accepted_records':accepted,
            'rejected_records':rejected, 'coverage':'INCOMPLETE' if data.get('next_page_token') or rejected else 'ONE_RESPONSE_NOT_CERTIFIED',
            'received_ms':received, 'feed_latency':'ENTITLEMENT_AND_PROVIDER_DEPENDENT',
            'execution_enabled':False}


def poll_news(folder):
    """Own SQLite connection in worker thread; failures cannot change accounts."""
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    health={'status':'NEWS_COLLECTION_FAILED','execution_enabled':False}
    try:
        db=connect(folder/'research.sqlite')
        try:
            # Bound private storage to roughly 10 MiB; retain evidence or stop,
            # never silently delete older observations to claim full coverage.
            size=db.execute('PRAGMA page_size').fetchone()[0]
            db.execute(f'PRAGMA max_page_count={max(1,10000000//size)}')
            health=collect(db)
        finally:db.close()
    except Exception:
        pass  # Never emit provider exception text or secrets.
    health['attempted_ms']=int(time.time()*1000)
    save_state(folder/'news_health.json',health)
    print('NEWS_HEALTH '+json.dumps(health),flush=True)
    return health


def report_news(folder, observed):
    folder=Path(folder)
    lines=['NEWS RESEARCH ONLY — attributed, not verified; cannot trigger trades.']
    path=folder/'news_health.json'
    if not path.exists():return lines+['Collector has not run in this deployment.']
    health=json.loads(path.read_text())
    age=max(0,(observed-health['attempted_ms'])/1000)
    lines.append(f"Collector: {health['status']}; attempt age {age:.0f}s; feed latency unverified.")
    lines.append('Coverage: '+health.get('coverage','UNAVAILABLE'))
    if (folder/'research.sqlite').exists():
        db=connect(folder/'research.sqlite')
        try:
            rows=db.execute('SELECT payload, published_ms, first_received_ms FROM evidence WHERE first_received_ms <= ? ORDER BY first_received_ms DESC LIMIT 5',(observed,)).fetchall()
        finally:db.close()
        for payload,published,received in rows:
            item=json.loads(payload)
            lines.append(','.join(item['symbols'])+' — '+item['publisher'][:80]+
                         f'; publication age {max(0,(observed-published)/60):.0f}m; receipt age {max(0,(observed-received)/60):.0f}m')
            lines.append(item['source_url'][:500])
    return lines


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', required=True, help='Private research database')
    args = parser.parse_args()
    with connect(args.db) as db:
        print(json.dumps(collect(db), indent=2))
