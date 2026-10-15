# Professional trading literature → paper research plan
Reviewed 15 October 2026. Paper research only; no production rule changes or execution.

## What was actually reviewed

This is a focused first-pass review of seven professional books using publisher descriptions, tables of contents and publicly accessible material, plus three primary research papers. Full copyrighted books were not obtained or read end-to-end. Publisher claims and interview narratives are not audited proof of a transferable strategy. No scraped full-text corpus or model training is claimed. Links below distinguish source themes from our proposed applications.

## Sources and useful lessons

| Source | Verified scope from available material | Application to this project | Evidence limit |
|---|---|---|---|
| Robert Carver, Systematic Trading | Rules, sizing, diversification, costs and avoiding unnecessary turnover | Evaluate sizing and portfolio risk separately from the forecast | Publisher synopsis supports themes, not a replicated return claim |
| Ernest P. Chan, Algorithmic Trading: Winning Strategies and Their Rationale | Mean reversion and momentum, their rationale and implementation | Require an economic hypothesis, data requirements and invalidation rule for each candidate | Book examples are not evidence our SPY rule is profitable |
| David R. Aronson, Evidence-Based Technical Analysis | Objective rules, scientific inference and data-mining bias | Maintain a complete trial register, including failed and abandoned variants | A scientific framework does not make an untested rule effective |
| Marcos López de Prado, Advances in Financial Machine Learning | Financial cross-validation, backtesting dangers, sizing and risk | Chronological evaluation, overlapping-label controls and simple forecast baselines | Contents reviewed; no claim every technique or chapter was reproduced |
| Antti Ilmanen, Expected Returns | Asset-class returns, risk premia and economic drivers | Separate passive market exposure from incremental timing/news value | Expected premia are uncertain and horizon-dependent |
| Perry J. Kaufman, Trading Systems and Methods | Broad systematic methods reference | Use as a taxonomy; avoid adding many indicators without a hypothesis | Bibliographic/contents review, not a replication of every system |
| Jack D. Schwager, Unknown Market Wizards | Interviews with selected successful individual traders | Translate any lesson into explicit rules; ask for independently reconciled records before considering copying | Selection/survivorship and discretion limit replicability; interviews are not a copy-trade feed |

Sources:
1. Carver publisher: https://www.harriman-house.com/authors/robert-carver/systematic-trading/9780857194459
2. Chan publisher announcement: https://johnwiley2020news.q4web.com/press-releases/press-release-details/2013/Algorithmic-Trading-Winning-Strategies-and-Their-Rationale/default.aspx
3. Aronson publisher: https://onlinelibrary.wiley.com/doi/book/10.1002/9781118268315
4. López de Prado publisher/contents: https://www.wiley-vch.de/en/areas-interest/finance-economics-law/finance-investments-13fi/finance-investments-special-topics-13fiz/advances-in-financial-machine-learning-978-1-119-48208-6
5. Ilmanen publisher: https://onlinelibrary.wiley.com/doi/book/10.1002/9781118467190
6. Kaufman publisher: https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202561
7. Schwager publisher: https://www.harriman-house.com/authors/jack-d-schwager/unknown-market-wizards/9780857198716

## Primary evidence and transfer limits

Hurst, Ooi and Pedersen, A Century of Evidence on Trend-Following Investing (2017), studies long/short trend across multiple futures/forward markets and long history. It motivates broader replication; it does not validate our long-only SPY SMA20/100 rule. Multi-asset, shorting, leverage, sizing and costs differ. We will not import those features into production on the strength of that paper.
https://www.aqr.com/insights/research/journal-article/a-century-of-evidence-on-trend-following-investing

Bailey, Borwein, López de Prado and Zhu, The Probability of Backtest Overfitting (2015), explains why repeated selection makes ordinary holdout assurances inadequate and develops an overfitting framework. Our application is to retain trial history and avoid relabelling familiar history as unseen. No PBO number has been calculated; the research history is not a complete trial-return matrix.
https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf

Frazzini, Israel and Moskowitz, Trading Costs (2018), analyzes institutional execution and how costs depend on market/trade characteristics. It supports measuring implementation costs, not copying institutional cost estimates into a retail single-venue simulator. Keep current ordinary/doubled assumptions until qualified private observations justify revisions; a rejected or stale quote never becomes an executable fill by assumption.
https://www.aqr.com/Insights/Research/Working-Paper/Trading-Costs

## What our own results require us to change

PR #7's known-history continuous SPY comparisons found all active policies below the initial-25%-invested buy-and-hold reference at both cost assumptions. SMA had lower drawdown but lower return. This rejects a claim of demonstrated timing alpha; it does not prove all trend methods fail. The benchmark's allocation drifts, so unequal exposure complicates risk-adjusted interpretation. Forecasts, position sizing and portfolio construction must be evaluated separately.

The AAPL forward experiment has corporate-action and coverage blockers. No historical-book method repairs its ledger, validates prior invalid days, or establishes a delayed-news advantage. Operational repair remains a separate gate. No live orders or paid data access is introduced.

## Hypotheses registered for future implementation

The exact parameters below are OUR engineering proposals, not claimed quotations or faithfully replicated book systems. They were selected after inspecting known historical results; later tests on those prices remain exploratory development evidence. No result for these proposals exists yet.

### H1 — capped volatility sizing, first implementation priority

Question: Can capped lagged-volatility sizing improve drawdown/cost-adjusted behavior relative to fixed sizing without inventing forecast alpha?

Keep completed-close SMA20/100 direction unchanged. Estimate annualized standard deviation of the latest 20 completed close-to-close returns (sample standard deviation × sqrt(252)); require all 21 closes, finite positive prices, verified sessions and corporate-action consistency. Candidate desired long weight = min(0.25, 0.02 / annualized_volatility); otherwise zero. The 2% target and 25% ceiling are conservative research choices, not optimal estimates. Zero/invalid volatility causes abstention, never infinite sizing or leverage.

Rebalance only on the first eligible session of each calendar week using the preceding close's inputs; a bearish signal permits an earlier exit. Execute at next eligible quote/open; existing risk exits override the schedule. This is a NEW offline candidate, not a modification to the frozen account. Retain the existing drawdown pause; do not reset it to make results look better.

Compare unchanged fixed-sizing SMA, this candidate, a long-only benchmark with the identical weekly sizing rule but no trend filter, the original initial-25% buy-and-hold, and cash. All share costs and terminal conventions; distinguish scheduled trades, natural exits and terminal liquidation. A separate within-sample diagnostic may describe realized risk, but do not resize the historical benchmark using volatility calculated over its future evaluation period.

Report net return, drawdown, exposure distribution, turnover, natural roundtrips, costs and rejection coverage at ordinary/doubled costs. Declare a risk-control result separately from a return-prediction result. Reject any superiority claim based only on less exposure, cherry-picked window or best Sharpe.

### H2 — turnover control, only after H1

Question: Does an absolute five-percentage-point weight buffer reduce costs without materially degrading the unchanged candidate's risk behavior?

One fixed buffer, applied only to discretionary weekly rebalancing; never block full bearish exits, drawdown actions or validity checks. Compare H1 with/without buffer under identical data and costs. No buffer grid. Record both variants as additional trials. Data must support actual position/notional rounding and minimum trade handling.

### H3 — simple five-session forecast baseline, already proposed

Use the prior registered lagged-return/volatility/SMA-distance/volume feature list and base-rate versus logistic probability forecast. Fit transformations on training data only; remove labels whose five-session outcomes overlap a later evaluation boundary. Use chronological folds with an explicit horizon gap; evaluate calibration/log loss before any next-session trading conversion. Previously inspected dates are development data even if placed in a later fold. Need validated prices/actions and a newly frozen prospective interval. Probability accuracy is not net trade profitability.

### H4 — diversification, blocked on validated data

SPY/AAPL/GLD are not three independent market exposures; AAPL and SPY share equity risk. Once synchronized verified histories exist, measure correlations and compare equal capped weights against a fixed-risk allocation with portfolio exposure and concentration caps. Do not size three separate USD10,000 accounts and call the sum a funded USD10,000 portfolio. No portfolio backtest or multi-asset trend replication is claimed yet.

## Trial register and decision gates

The companion LITERATURE_HYPOTHESES_2026-10-15.json records IDs, status and hypotheses; it does not import into or control the worker. Prior annual/continuous histories, news experiments and all later variations count as research history. Test counts are not independent profitable trades. A complete retrospective trial count is unknown; do not invent a selection-adjusted confidence level.

Before accepting any candidate:
- Verify data provenance, complete exchange sessions, price/action adjustments, chronology and absence of double-counted distributions.
- Prove accounting and next-decision timing on fixtures, then run data comparisons; distinguish these evidence classes.
- Fix warmup-contaminated volatility/Sharpe reporting before using those statistics for decisions.
- Retain every comparator, negative result, ordinary/doubled costs and dependence-aware uncertainty; report sensitivity without selecting the best interval.
- Freeze candidate code, dataset hashes, evaluation dates and criteria before prospective observation. Define a practical minimum return/risk improvement and acceptable drawdown before that interval; these thresholds are not yet set or approved.
- Require valid forward sessions, private balance/action reconciliation, meaningful natural exits and recovery checks. No universal trade count or time period guarantees qualification.
- Discard or continue research when evidence is weak; do not force a profitable winner or alter frozen running experiments.

## Copying traders and news

A verified profile or a published book cannot supply a complete executable track record. Qualification would require authorized timestamped orders/fills, cash flows, fees, open/closed losses, leverage, drawdowns and a reliable feed, followed by paper shadowing with receipt latency. None was established by this review. News sentiment must likewise use information actually received before the decision, retaining delayed-feed assumptions.

## Completion status

Completed: accessible-source review, project-specific evidence mapping and four unexecuted research hypotheses. Not completed: full-book reading, comprehensive trading-data scraping, model training, strategy implementation, private-ledger repair or profitable prediction. No tests were rerun for this documentation-only change. Earlier PR #7 counts remain separately documented. No production state, credentials, deployment or paid services changed.
