# Evidence review — 9 October 2026

Decision: strategy profitability is not established. Existing news collection
works operationally, but news coverage and a prospective news strategy are not
qualified. No strategy promoted, no real trades or paid changes.

## Historical result verified from saved data

Source: private saved Experiment 002 `long_results.json`, executed 1 October.
SHA256: c7e2dcf3668f0cbdb9ff6669b2e8e85b4d063e517743372b57bd64035a87f8bc
Reproduction: `python summarize_results.py /private/path/long_results.json`.
88 comparisons: 44 independent asset/window starts, each at base/doubled costs.
Windows 2018–2025 and 2026 January–September; ETH 2018 skipped for warm-up.
These are previously inspected development data, not fresh out-of-sample evidence.

| Asset | Base-cost windows beating matched 25% buy-and-hold | Worst window return | Worst window drawdown | Doubled-cost worst return |
|---|---:|---:|---:|---:|
| SPY | 1/9 | -4.84% | -7.10% | -4.89% |
| AAPL | 1/9 | -8.01% | -9.62% | -8.06% |
| GLD | 3/9 | -1.72% | -5.88% | -1.80% |
| BTC-USD | 5/9 | -10.63% | -14.68% | -10.67% |
| ETH-USD | 4/8 | -9.94% | -14.08% | -10.06% |

Benchmark-win counts are unchanged under doubled modeled costs. They are not win
rates per trade, probabilities or independent trials. Separate windows must not
be compounded or pooled into a realized portfolio. Adjusted daily prices are
synthetic proxies, not executable quotes. Trade counts in this older experiment
include terminal liquidation and are not natural-roundtrip screening counts.
Sparse trades, convenience-universe selection and prior inspection limit inference.

Interpretation: these results provide no consistent US benchmark advantage for
the original trend strategy. They justify retaining it as a comparison baseline,
not selling it as a profitable system. Crypto results are mixed, and some losses
exceed the nominal 10% risk trigger; a trigger is not a guaranteed drawdown cap.

## Current production evidence

Railway deployment 8cd1ec13-496f-42e5-8124-7100cbb84041 is SUCCESS, code
d7e68e394ac742ce54339dcdf342d097cb29774b. Runtime news logs observed from
08:24:23 through 08:50:45 UTC today show six successful research-only probes:
50 accepted record occurrences, zero validation rejections per probe, all marked
INCOMPLETE. Counts may repeat records and must not be summed as unique articles.
This confirms authenticated endpoint access and metadata ingestion, not factual
verification, real-time entitlement, complete coverage or profitable news trades.

Current private account and shadow-lab ledgers were not read during this review.
Consequently no current P/L, position, natural-roundtrip count or performance
claim is made. Previous Telegram snapshots cannot substitute for today's ledger.
`/lab` is the deployed owner-only source of current shadow observations;
`/status`, `/trades` and `/news` report account and collector observations.

## What must establish the next result

1. Finish bounded pagination and preserve per-poll covered ranges, rejection and
   outage records. Estimate publication/update-to-receipt lag without claiming
   publication latency alone proves real-time entitlement. Compare only observed
   coverage; discard affected missing-data periods.
2. Freeze and implement the proposed AAPL 30-minute news entry-delay account and
   a matched unchanged trend account, separate from existing balances. Fresh
   post-decision quotes, ordinary/doubled costs, exits during entry pauses and
   corporate-action review are mandatory. The current collector alone does not
   place news-based paper trades.
3. Record timestamped daily matched net excess P/L, costs, exposure, max drawdown,
   natural roundtrips and source/rules fingerprints. Missing marks are not zero
   returns. Never sum independent alternative accounts as one portfolio.
4. Accumulate genuinely prospective observations. Ninety days and 30 natural
   roundtrips are screening minima, not sufficient proof; this slow rule may need
   substantially longer. Assess uncertainty preserving time dependence and keep
   failed experiments. No automatic promotion from a positive short-term P/L.

Results become convincing through reproducible, net-of-cost, matched prospective
evidence. Software tests and collector success are separate operational evidence.
