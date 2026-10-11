# Research and test review — 11 October 2026

Decision: continue controlled paper research; no trading edge established.
The existing free allowance constraint remains in force.

## Verified current state

Railway production reports one running replica, SUCCESS deployment
306c25c8-ad36-4e3f-affc-7299bc14cf24, source commit
4029cda758a0357fa58152485ca964402d667ab0, no recent failures in its default
eight-hour status window and a persistent /data volume. Both Alpaca data
variable names are present; values were not read or copied. There is no pending
deployment. This status is a snapshot, not sustained uptime qualification.

Runtime logs show research-only delayed-news polling through 09:20 UTC today,
including one newly accepted record at 09:09 UTC. Latest 21 matching Friday
NEWS_LAB_HEALTH log entries, 18:01–19:52 UTC on 9 October, report valid delayed
coverage and NO_ACTION for all four alternatives. These logs establish processing,
not account P/L, completed trades or complete session coverage. One observed
gap between these entries exceeds ten minutes and needs ledger/coverage review;
do not infer uninterrupted operation from the current Online label.

Current private account ledgers, corporate-action manifests and recovery archives
were not read. Current P/L, reviewed overnight coverage and performance remain
unverified. Use owner-only /lab, /news_lab, /status and /trades for observations.

Local verification: 94 deployment fixture tests and 121 research fixture tests
pass in separate interpreters. Six new tests validate the offline uncertainty
helper, including missing/invalid days, corrupted values and reproducibility.
These suites overlap in coverage; 215 executions are not 215 independent findings.
Run `python scripts/run_test_campaign.py`. Its report records UTC check time,
per-suite count/outcome and SHA256 source hashes without credentials or private
ledgers. A zero-test suite cannot pass the campaign.

## Best approach for this project: evidence before complexity

| Priority | Method | What it resolves / limits |
|---|---|---|
| 1 | Reconcile every fill, distribution and balance; review issuer corporate actions; measure collector gaps; test restore on a copied state directory | Accounting/data errors can resemble a profitable strategy. Never edit a flag to bypass missing review. |
| 2 | Keep frozen SMA, breakout, mean-reversion, cash and matched 25% buy-and-hold alternatives at ordinary and doubled costs | Already-inspected history is development evidence. Preserve unsuccessful alternatives and exposure differences. |
| 3 | Use chronological development/validation windows and untouched future observations; register every parameter trial | Selecting the largest backtest return creates selection bias. The existing SMA review showed SPY and AAPL beat the reference in only 1/9 inspected windows each. |
| 4 | Quantify paired net daily excess returns with dependence-preserving blocks; report predeclared block-length sensitivity | The new helper provides descriptive intervals, not a pass/fail trading gate. Multiple-testing correction and longer histories remain necessary. |
| 5 | Keep delayed-news entry filter isolated; use actual receipt time, revisions and explicit coverage | A 15-minute-delayed feed plus polling cannot establish a news-speed advantage. Compare its four accounts without rewriting baseline balances. |
| 6 | Evaluate a permitted trader feed only after identity, complete entries/exits, losses, equity/cash flows, leverage, fees and receipt latency are documented | A verified identity or attractive screenshot is not verified performance. No feed is qualified or copied today. |

For the daily-close rules and cost constraints, improving accounting and measured
data reliability is more useful now than adding another AI agent. An IEX quote
stream is a later controlled pilot: official documentation favors streaming over
polling for timely prices, but subscription limits, reconnect/backfill behavior,
memory bounds and single-venue limitations need testing first. Retain source-event
age and post-decision eligibility checks; never raise stale/spread thresholds just
to manufacture more fills. This is a recommendation, not a claim of implementation.

## Statistical tool added

`research/paired_uncertainty.py` takes reconciled net strategy/benchmark equities
at matched timestamps, a separately reviewed expected-date list and explicit
validity flags. Missing, extra, duplicate, unordered, nonfinite or invalid marks
are rejected rather than converted into zero returns. No cash flows may occur.
Circular moving-block resampling estimates a descriptive percentile interval
for mean daily relative return. This differs from terminal dollar excess.

Freeze the evaluation protocol before inspecting results. Suggested sensitivity
grid for a future sufficiently long daily series: blocks 5, 10 and 20 sessions;
do not select the most favorable result. This grid is a proposed protocol and
does not amend running experiment fingerprints. There is no claimed confidence
of profit, automatic strategy selection or correction for trying many strategies.
No actual performance interval was computed because reviewed private marks are
not available here. Existing 90-day/30-natural-roundtrip thresholds are screening
minima; they cannot make an unreliable interval statistically conclusive.

## Source findings checked on 11 October 2026

1. Alpaca Paper Trading: simulated results omit market impact, latency slippage,
queue position, regulatory fees and dividends; fills do not check NBBO size.
This supports retaining our modeled costs, displayed-size caps and reconciliation,
while recognizing that our IEX-only simulator is not an executable NBBO model.
https://docs.alpaca.markets/us/docs/paper-trading
2. Alpaca real-time data: streams are preferable to polling for timely prices;
access is restricted to entitled feeds. IEX is one venue, SIP is consolidated.
https://docs.alpaca.markets/us/docs/real-time-stock-pricing-data
https://docs.alpaca.markets/us/docs/market-data-faq
3. Bailey et al., Probability of Backtest Overfitting: strategy selection from
many backtests requires evaluation beyond an attractive in-sample performance.
https://escholarship.org/uc/item/4w1110bb
4. Bailey and Lopez de Prado, Deflated Sharpe Ratio (2014): selection bias,
non-normality and repeated trials distort naive Sharpe-based conclusions.
Our new helper does not implement the Deflated Sharpe Ratio.
https://doi.org/10.3905/jpm.2014.40.5.094
5. SEC Form 13F FAQ: quarterly holdings are normally filed within 45 days,
subject to weekend/holiday deadline adjustments. These snapshots are not a
timely complete trader execution feed. Keep them as holdings research only.
https://www.sec.gov/rules-regulations/staff-guidance/frequently-asked-questions-about-form-13f

## Next evidence gates

Complete reviewed corporate-action coverage, ledger exports and a controlled
restore drill before evaluating overnight results. Document the observed Friday
gap. Gather genuinely prospective matched results, then evaluate net excess,
drawdown, exposure, cost stress and uncertainty without hiding blocked periods.
News sentiment and trader copying stay separate hypotheses, not presumed edges.
No paid service, broker order endpoint or commercial profitability claim is added.
