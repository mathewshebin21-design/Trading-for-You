# Paper validation plan

Recorded 8 October 2026. Research and simulated execution only. Passing this plan supports further paper research; it does not authorize live trading or establish future profitability.

## Evidence so far

- Telegram command delivery and crypto simulated positions have been observed in user-supplied reports. US history/calendar reads have also been observed.
- Software tests use synthetic/mocked inputs. They test behavior, not trading edge.
- Actual US market-open notification, eligible US fills, sustained uptime and recovery still need observation.
- News analysis and verified-trader copying are not implemented. No eligible trader feed has been selected.
- Previously examined historical periods, including January–September 2026, are development evidence, not untouched out-of-sample evidence.

## Stage 1: operational qualification

Observe seven consecutive calendar days within the existing free hosting allowance; do not upgrade or enable payment. This is a minimum operational screen, not a performance test. If hosting stops, record the gap and extend the observation window after restoration.

Keep timestamped collection attempts, failures, quote age, decision time, simulated fills, modeled costs, account balances and notification delivery evidence. Record missing observations rather than inventing prices or fills. A worker marked running is not proof of a healthy collector.

Acceptance requires no unexplained ledger difference, unauthorized command execution, duplicate confirmed manual fill, stale-data fill or risk-pause bypass. Observe at least one actual regular US session opening notification and one controlled restart with preserved state. Measure collection/notification gaps and latency; report outages separately. Any accounting or safety failure blocks qualification until fixed and retested.

Current US blockers: overnight corporate-action reconciliation is incomplete; quote acquisition must reliably obtain an eligible event after the recorded decision. Until resolved, do not interpret US overnight equity or sparse fills as strategy performance. Do not clear review flags by editing account state.

## Stage 2: freeze a performance experiment

After operational qualification, record an explicit future start time, code revision, instrument universe, starting virtual equity, rules, execution assumptions and benchmark conventions. Current observations are pilot data. Maintain independent USD and USDT accounts and separate manual accounts; never sum currencies or count manual trades as automatic-strategy results.

Baseline retains SMA20/SMA100, long-only exposure, 25% entry allocation and existing permanent 10% per-account drawdown entry pause. Crypto assumptions: observed spread, 3 bp adverse slippage and 10 bp modeled fee per side. US assumptions: observed spread, 5 bp adverse slippage and 10 bp modeled cost per side. These assumptions are not verified execution costs.

Use cash and a matched 25%-allocated buy-and-hold reference for each instrument, with the same starting time, eligible quote convention, costs and valuation timestamps. Compare end equity, net return, maximum drawdown, exposure, completed round trips, turnover, modeled costs, stale/missing data and risk halts. Mark open holdings separately; a fill count is not a completed-trade count.

Set a first review after 90 calendar days, subject to free hosting availability. Extend if fewer than 30 completed round trips per tested strategy/instrument; 30 is a screening minimum, not statistical proof. A slow daily strategy may require substantially longer. No result is classified as successful merely because a time or trade-count threshold is reached.

## Stage 3: evaluate additions separately

News: archive permitted source metadata, publication time and first-observed time; freeze symbol mapping, handling of revisions/duplicates and an objective decision rule before evaluation. Information cannot influence a decision before first observation. Compare baseline and news variant over the same future interval, with separate ledgers. News summaries alone are not a trading signal.

Trader copying: require an attributable, permissioned feed with timestamped entries and exits and a sufficiently complete record including losses. Document identity, verification scope, omitted trades, fees, leverage, drawdown and publication delay. If a feed cannot be verified, reject it for copying. Screenshots and promotional return claims are insufficient. Copy only into a separate virtual account, after actual receipt, with the same risk limits and realistic latency/costs.

Neither addition changes the running baseline before it is separately specified, implemented and tested. Preserve every tested variant and failed result; changing rules starts a new experiment on future data.

## Decision rules

- **Blocked:** incomplete accounting, unresolved data leakage, unavailable/unverifiable source or operational qualification failure. Repair before performance evaluation.
- **Insufficient evidence:** short record, too few completed round trips, material gaps, uncertain accounting or uncertainty consistent with no advantage. Extend or discard; do not label validated.
- **Discard/revise:** documented risk limit breached, or a completed qualifying evaluation fails the predeclared objective. Preserve results and use a fresh future window for revisions.
- **Continue paper research:** positive net return and net excess return versus the matched reference, drawdown below the existing risk limit, and favorable results under doubled modeled fees/slippage without worse drawdown than the reference. All conditions must hold for an instrument to pass this screen; report failures rather than selecting only winners. Prospective doubled-cost shadow ledgers must exist before claiming this condition passed.

Before Stage 2 starts, fix the statistical method for uncertainty in benchmark-relative returns and dependence between observations; report estimates and intervals rather than a fabricated confidence score. Even a favorable screen is provisional and needs evidence across different conditions. No live-order endpoint, live credential or paid service is part of this plan.
