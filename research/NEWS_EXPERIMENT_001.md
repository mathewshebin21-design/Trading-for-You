# Prospective news experiment proposal — 9 October 2026

Status: collector code tested on fixtures; no authenticated production news
observation obtained in this workspace. No news-driven trades enabled.

Official references checked today:
https://docs.alpaca.markets/us/reference/news-3
https://docs.alpaca.markets/us/docs/about-market-data-api
https://docs.alpaca.markets/us/docs/real-time-stock-pricing-data

Basic equities are IEX only, not the consolidated market. News endpoint default
end time depends on entitlement: current time or 15 minutes earlier. A successful
response alone does not prove real-time access or complete coverage. Streams are
preferred by the provider for timely quotes; our 300-second polling interval
cannot capture all intervening market events. Do not describe this as a latency
advantage or use the bot for news scalping.

## Collection

`news_collector.py` requests only GET /v1beta1/news, three US symbols, maximum
50 records, bounded response, no full article content, no redirects. Its default
state is disabled. With existing authorized data credentials and feed access
confirmed, `RESEARCH_NEWS_ENABLED=1 python news_collector.py --db /private/path/research.sqlite`
performs one collection. It neither subscribes to a plan nor places orders.
The same collector is now integrated into the existing Railway worker after
account/risk processing, once per normal poll cycle. It remains disabled unless
RESEARCH_NEWS_ENABLED=1. It reuses existing ALPACA_DATA_KEY/ALPACA_DATA_SECRET;
no credential copies or extra service are needed. Deployment verification is
required before describing it as running.
Owner-only /news reports probe health and up to five attributable links; /status
includes concise health. Health logs contain only fixed status codes and counts.
The private research SQLite database is bounded to approximately 10 MB. Storage
failure stops news collection without deleting evidence or affecting accounts.
This database is not included in the existing same-volume paper snapshots.
News ingestion failure cannot prevent original paper risk processing. The
collector is not a complete archive and cannot activate the proposed strategy.
No credentials were copied from Railway or screenshots.

Store canonical source links, explicit provider dates, locally assigned receipt
time, provider article ID/update and content fingerprint. Reject malformed,
future, reversed or timezone-free dates and unmapped symbols. A next-page token
or rejected record marks coverage incomplete. No pagination means this collector
is a bounded probe, not a complete news archive. Accepted counts include duplicates.
No raw article/news database is published to GitHub.

## Frozen candidate, not an established edge

Hypothesis: delaying NEW AAPL trend entries until 30 minutes after the latest
newly received, symbol-mapped news item may reduce adverse entry outcomes after
costs compared with the same trend strategy without this delay. This is a
candidate volatility filter, not a bullish/bearish headline classifier.

Compare separate virtual accounts using identical SMA20/100 inputs, 25% sizing,
post-decision validated IEX quotes, ordinary fees/slippage, doubled-cost stress,
calendar, corporate-action reviews and risk controls. News delay affects BUY only;
exits/risk checks continue. Use actual first receipt, not publication time, to
start the delay. Every changed record starts a new delay. Discard comparison
periods with unobserved feed coverage or outages; do not silently interpret
missing news as no news. No live experiment should start until full collection
and coverage health are implemented and prospective rules fingerprinted.

Primary measure: matched net excess dollars over the unchanged trend account.
Also compare drawdown, exposure, modeled execution costs, completed trades and
missed opportunities. Report intervals with time dependence preserved, no
selection of a winner from previously inspected history. Existing 90-day and
30-natural-roundtrip screening minima are not proof of profitability. They may
take longer to accumulate because the daily trend rule trades infrequently.

No sentiment inference, copied traders or article-triggered BUY rules are
qualified. Identity verification does not establish profitable trader performance.
