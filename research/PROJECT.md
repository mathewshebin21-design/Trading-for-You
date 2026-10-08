# Trading Research — Project Specification v0.1

Created: 1 October 2026. Purpose: systematic research and paper trading only.

## Current status

Experiment 001 now defines a bounded exploratory implementation gate. Its fixed rule, archived snapshot, assumed costs, evaluation windows and per-account risk settings are in EXPERIMENT_001.md. A deterministic backtester and resumable historical paper-account simulator were built and executed in Colab; 12 accounting/timing checks passed and 80 result records were produced. Holdout trade counts were only 2–3 per instrument, and no strategy is validated. Continuous prospective simulation, verified trader copying, realistic venue costs and a professional validation dataset remain pending.

### Original workbench milestone

The research workspace, initial specification and self-contained Colab read-only workbench exist. The workbench includes bar validation, optional public observations, a source archive and an evidence register. Its default offline notebook run and eight targeted checks passed in the build environment. No strategy has been validated, no trader's profitability has been independently verified, and no real-time feed is connected in the user's account. This is research infrastructure, not a running trading bot. Coding the trading engine remains stage 9 under the user's original project contract.

## Confirmed requirements

- Markets: gold, crypto and US stocks.
- Intended holding period: days to weeks.
- Observe current market data and news; produce traceable candidate paper trades.
- Investigate copying traders only where timestamped, sufficiently complete records are accessible.
- Research YouTube, public internet sources, papers, GitHub and Hugging Face; verify claims rather than repeating them.
- All execution is simulated. No live orders, live brokerage integration or real-money execution.
- Prefer simple, reproducible rules, robustness and capital preservation.

## Working scope and unresolved decisions

Start with liquid US cash equities, a gold ETF proxy, and BTC/ETH spot research. These are engineering defaults, not asset recommendations. GLD is a provisional gold research proxy; an ETF is not interchangeable with XAU/USD or gold futures. Gold instrument selection remains open. The first stock universe must be fixed before testing and its selection bias documented; do not backtest today's winners as if they were an unbiased historical universe.

Use USD as the simulation reporting currency and UTC for event storage; display dates in Asia/Kolkata. Label stablecoin quotes explicitly and record their conversion assumptions. Research daily completed bars first while collecting current quotes for monitoring. US equity calendars and crypto's continuous calendar must remain separate.

Budget, historical dataset access, deployment location, feed entitlements and alert destination remain unresolved. Do not purchase feeds, subscribe to services, create external accounts or send alerts to people as part of this specification.

## 1. Foundations

Define edge as a reproducible improvement over a stated baseline after trading costs at comparable exposure and risk. Historical profitability alone does not establish an edge. Copy delay, incomplete positions, hindsight, survivorship, repeated parameter searches, missing costs and changing market conditions are explicit failure hypotheses.

Initial evidence findings:

- SEC Form 13F describes quarterly holdings, with filings generally due within 45 days after quarter-end; it excludes short positions. It is unsuitable as a real-time entry/exit feed. [S1]
- Financial sentiment classification and price prediction are different tasks. FinBERT's model card describes positive/negative/neutral text classification; it does not establish a profitable trading strategy. [S2]
- Alpaca documents limitations in its paper simulator, including omitted market impact and latency slippage; fills may ignore displayed quantity. Simulation results require their own realism checks. [S3]
- Backtest overfitting research describes the risk of selecting an in-sample winner that underperforms out of sample. Log every tested variant. [S4]

## 2. Strategy types

Investigate three separate hypotheses, with no assumed profitability:

| Hypothesis | Question | Required evidence | Main failure mode |
|---|---|---|---|
| H1: simple trend | Do objective trend rules improve risk-adjusted results over baselines after costs? | Point-in-time bars, corporate actions, costs, independent test windows | Whipsaw and persistent regime dependence |
| H2: copy delay | Does a preselected trader's observed activity retain value at our actual receipt time? | Complete positions, entries/exits, disclosure timing, fees, leverage, deposits and withdrawals | Selective reporting and price movement before copying |
| H3: news filter | Does a verified news feature improve H1 versus H1 alone? | First-available article versions and timestamps, entity mapping, fixed feature extraction | Leakage, stale news, misleading sentiment and domain drift |

Mean reversion and breakout remain later candidates. Limit the initial hypothesis count; adding complexity does not establish evidence.

## 3. Objective rules

H1 illustrative preregistration draft: on a completed daily bar, hold a long position when SMA(20) exceeds SMA(100); exit when SMA(20) is at or below SMA(100). Signals cannot fill on the bar that produced them. Require 100 completed bars, a valid next executable quote/session, sufficient virtual cash and approved risk limits. No leverage, shorts or pyramiding in this initial draft. Calendar-based holding duration is an observed outcome, not a guaranteed days-to-weeks interval. A time exit would be a separately logged variant.

Before running tests, specify the price-adjustment convention, next-open or quote fill semantics, quantity rounding, dividends, missing bars, splits, entry cost, exit cost and gap treatment. Stops, if later added, cannot guarantee a maximum loss across gaps.

H2 must specify source selection before an evaluation window, permitted instruments, position scaling, expiry, observable entry/exit events and copy latency. Replay at receipt time, never at a retrospectively reported original price. A position disclosure is not proof of an executed trade. Sources without complete enough records are watchlist research only.

H3 begins in observation mode. News sentiment never directly places a paper order. A predefined filter can be tested against H1 only after a timestamped archive and rule are available; evaluate the incremental change with the same costs and exposure controls.

## 4. Data and costs

Record event time, publication time, first-observed time, ingest time, source, venue, delay category, raw-record checksum and corrections. Never label delayed data real time. Historical news can be used only when its original availability and version are supported; otherwise start a prospective archive.

US stock data: assess read-only market data, licensing, IEX versus consolidated coverage, historical coverage, delistings, splits, dividends, exchange calendars and extended sessions. Alpaca documentation is a candidate reference, not a selected or connected provider. [S3]

Crypto: assess venue-specific read-only spot data. Binance documents a market-data-only WebSocket domain. Availability, regional access, connection recovery and historical completeness still need testing. BTC/USDT is not BTC/USD; never silently merge quotes or assume stablecoin parity. No exchange account or order connection is required for a local simulator. [S5]

Gold: assess GLD data as a provisional exchange-traded proxy and check issuer documentation. Spot gold and futures require a different model, including venue conventions or contract rolls where relevant. [S6]

Cost table per instrument must include spread, commissions, applicable fees, slippage, liquidity limits and latency. Obtain current provider/venue schedules before setting values. Test both base costs and stressed costs; no zero-cost performance claim. Model dividends and splits without double counting them through adjusted prices.

## 5. Backtesting methodology

Freeze a chronological development/validation/final-test split before tuning. Dates depend on dataset coverage. Use rolling or expanding walk-forward evaluation inside development/validation, with gaps appropriate to overlapping holding periods. Keep final-test data untouched until rules are frozen; any post-test revision requires a new evaluation period.

Compare with buy-and-hold, cash and a simple risk/exposure-matched baseline per market. Report both individual market sleeves and the combined portfolio. Treat correlated assets and simultaneous positions as shared exposure. Log every strategy, parameter search, rejected source and failed result. Examine parameter neighborhoods, cost stress, timing delays and regime breakdowns. Use dependence-aware uncertainty estimates; overlapping trades are not independent observations.

Required semantic checks at coding stage: no future data, no same-bar fill, correct split/dividend accounting, receipt-time copying, bar/session boundaries, missing data, stale quotes, duplicate events and reproducible reruns.

## 6. Risk management

Risk parameters remain provisional research settings until preregistered; they are not financial advice or evidence of safety. Define virtual capital, per-position notional limits, aggregate exposure, crypto sleeve cap, correlated exposure limits and a drawdown pause threshold before simulation. Enforce cash availability, quantity precision and cost reserves. Reject new entries when data is stale, clocks are inconsistent, costs are unknown or the ledger fails reconciliation.

Measure gap risk, tail losses, drawdown duration and dependence across holdings. Estimate ruin probability only with a stated failure boundary and documented modelling assumptions; no precise-looking unsupported probability.

## 7. Paper-trading framework

Planned architecture: read-only ingestion → timestamped event store → objective strategy rules → risk checks → local fill simulator → ledger and evaluation dashboard. News analysis and trader records feed separately into the rule layer. No executable live-order adapter or live-mode switch.

Maintain three paper sleeves: strategy-only, copy-only and strategy-plus-news. Compare them over identical applicable periods. Use a local simulator as the initial design so realistic costs and delays are controllable. An external paper service is optional future research infrastructure, not required.

Every candidate card includes: instrument/venue, source type, data timestamp and delay, strategy version, trigger, proposed entry semantics, exit rule, virtual size, estimated costs, evidence tier, invalidation/expiry, risk rejection reason and later simulated outcome. Include WATCH / PAPER CANDIDATE / REJECTED states. Never invent a probability of winning from sentiment scores.

## 8. Evaluation criteria

Before testing, fix numerical tolerances appropriate to the data and intended risk profile. Report net return, CAGR where meaningful, volatility, Sharpe with an explicit convention, Sortino, maximum drawdown, drawdown duration, turnover, exposure, net expectancy, profit factor, tail losses, cost sensitivity and latency sensitivity. Include uncertainty and complete losing trades.

Keep for further paper research only when data/rules are reproducible, independent evaluation supports improvement against the stated baseline, and results survive plausible cost/timing changes without breaching preregistered limits. Improve when operational defects or uncertainty are clearly identified; improvements count as new variants. Discard when a claim cannot be tested, results depend on leakage, copying is not timely enough, or performance fails the predefined criteria. Insufficient evidence is a valid outcome, not a reason to declare success.

## 9. Coding gate and deliverables

Before engine coding: freeze universe and gold instrument, resolve data access, complete cost assumptions, register rules and evaluation dates, set risk parameters, and select a dependency after testing its licence and accounting behavior.

Planned implementation order once the gate is met:
1. Read-only ingestion, validation and immutable event storage.
2. Deterministic historical replay and cost-aware paper ledger.
3. One simple preregistered strategy and appropriate semantic tests.
4. Traceable candidate dashboard and research reports.
5. Trader-copy replay where records meet eligibility.
6. Prospective news archive and controlled sentiment experiment.

Prefer Python, small modules and SQLite/Parquet for a first research implementation. Model inference is optional and deferred. The read-only workbench uses Python's standard library by default. Optional historical downloading installs yfinance in the cloud runtime only. No repositories have been cloned or service credentials requested.

## Reusable tools: initial screen, not completed audit

| Source | Potential role | Finding and decision |
|---|---|---|
| kernc/backtesting.py | Simple rule backtests | Repository identifies AGPL-3.0; shortlist for offline experiments. Portfolio accounting, licence implications, current tests/releases and semantic checks still need review. [S7] |
| polakowo/vectorbt | Portfolio analysis and fast experiments | Repository describes Apache 2.0 with Commons Clause, not unrestricted Apache 2.0. Shortlist subject to fit and licence review; avoid unbounded parameter searches. [S8] |
| ProsusAI/finbert | English financial-news sentiment baseline | Positive/negative/neutral classification only. Test on our gold/crypto/stock news; model scores are not return forecasts. Check model-artifact licence and pinned revision before loading. [S2] |
| AI4Finance-Foundation/FinRL | Reinforcement-learning research reference | Repository identifies MIT licensing and an RL framework. Defer for the first version to preserve simplicity; published examples do not validate our strategy. [S9] |

For every adopted dependency: pin a commit/version; read current licence; inspect data assumptions, network calls and optional trading integrations; run targeted tests; retain attribution. For Hugging Face: prefer inspectable weights, verify provenance and artefact terms, and do not enable arbitrary remote code by default.

## Claim-verification protocol

Evidence labels:
- E0: unsupported marketing, screenshot or selective example.
- E1: complete stated rules with source, but results not reproduced.
- E2: independently reproduced historical result with costs and data provenance.
- E3: prospective timestamped paper record under frozen rules.
- E4: independently supported full account record, including open positions and cash flows; does not establish future profitability or copyability.

These labels are internal research conventions, not regulatory ratings. E2/E3 measure different evidence; neither proves live performance. For traders, separately assess identity, record completeness, unrealized losses, drawdowns, leverage, cash-flow adjustments, latency, exits, source stability and incentive conflicts. Do not rank by followers, screenshots or raw win rate.

For YouTube: discover original videos, retrieve accessible transcripts with timestamp references, extract exact claims and rules, identify affiliate incentives, locate underlying records, and reconstruct only when rules are objective. Preserve inaccessible or ambiguous cases as unresolved. Do not claim to have watched a full video from a title or search snippet.

Initial video lead: Better System Trader episode 026 with Robert Carver. The host's page and written summary were accessible and discuss objective rules and overfitting. The embedded YouTube fetch failed in this session; full video/transcript has not been analyzed. It is a methodology lead, not a verified profitable trader or copy feed. [S10]

## Source register

All sources below were retrieved on 1 October 2026. They support factual scope/limitations; none establishes a validated trading edge. Search summaries alone do not count as full source audits.

- S1 — SEC, Frequently Asked Questions About Form 13F: https://www.sec.gov/rules-regulations/staff-guidance/division-investment-management-frequently-asked-questions/frequently-asked-questions-about-form-13f
- S2 — ProsusAI, FinBERT model card: https://huggingface.co/ProsusAI/finbert
- S3 — Alpaca, Paper Trading: https://docs.alpaca.markets/us/docs/paper-trading
- S4 — Bailey et al., The Probability of Backtest Overfitting: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf (targeted methodological sections reviewed; no strategy replication performed).
- S5 — Binance, Market Data Only: https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- S6 — SPDR Gold Shares issuer site: https://www.spdrgoldshares.com/usa/ (instrument discovery only; detailed fund document review pending).
- S7 — Backtesting.py repository: https://github.com/kernc/backtesting.py
- S8 — Vectorbt repository: https://github.com/polakowo/vectorbt
- S9 — FinRL repository: https://github.com/AI4Finance-Foundation/FinRL
- S10 — Better System Trader, episode 026: https://bettersystemtrader.com/026-robert-carver/

## Next research work

1. Resolve gold ETF versus spot/futures and current read-only data access across all markets.
2. Review point-in-time historical datasets, entitlement limits, actual prices and costs; do not substitute delayed quotes for real-time feeds.
3. Expand the original-video evidence register and locate complete trader records. Report no eligible trader if evidence is insufficient.
4. Finalize preregistration and risk limits, then implement the first deterministic research engine.

No guarantee of returns. All future code and outputs must remain explicitly labelled research/paper trading.
