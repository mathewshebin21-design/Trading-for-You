# Experiment 001 — fixed trend baseline

Frozen 1 October 2026, before executing this strategy on the collected dataset. Research/paper simulation only. No tuning or guaranteed returns.

## Scope and qualification

GLD (provisional gold ETF proxy), SPY (US equity index ETF), AAPL (one stock), BTC-USD and ETH-USD. Five independent virtual accounts; no claim of a consolidated portfolio. This contemporary convenience universe has selection/survivorship bias. Historical Yahoo crypto composites are not executable exchange quotes. All results are exploratory and unsuitable as proof of live profitability.

Data are the immutable historical CSV snapshots collected in Colab on 1 October 2026, covering 1 October 2024 through 30 September 2026. Earlier work inspected data quality and dates, not strategy performance. The history is short and has no point-in-time universe certification. No new data-provider account is needed for this experiment.

## Hypothesis and rules

Hypothesis: a fixed trend rule can improve return versus exposure/drawdown trade-offs after costs compared with a cash-heavy buy-and-hold baseline. Failure is possible and must be reported.

For completed daily bars, hold long if SMA(20) > SMA(100), otherwise hold cash. Need 100 completed historical bars. Compute from raw close, not adjusted close. Fill the decision at the next available bar's open with adverse spread/slippage. No same-bar fills, no prediction, no leverage, no shorts. Days-to-weeks is the research preference; this trend rule may hold longer. Position size is fixed at entry, not rebalanced daily. Rounding: whole ETF/stock shares, 0.000001 units for crypto. No pyramiding.

## Costs (assumptions, not verified venue schedules)

| Market | Commission per side | Half spread per side | Slippage per side |
|---|---:|---:|---:|
| GLD/SPY/AAPL | 1 bp | 1 bp | 2 bp |
| BTC/ETH | 10 bp | 2 bp | 3 bp |

Commission applies to executed notional; spread/slippage adjust execution price adversely. Repeat once with every component doubled. These are stress scenarios, not evidence of realistic execution. No depth, queues, market impact, taxes, funding or borrow model; only unlevered long cash/spot proxies. Stops cannot guarantee bounded losses across gaps.

## Accounting and limits

Each account starts with $10,000 virtual cash. New entries use at most 25% of equity measured at that day's open, including reserves for fees. Idle cash earns zero. Mark positions to daily close. Credit explicit dividends/capital gains to overnight holdings on ex-date (payment timing simplified); do not also use adjusted close. Reject split-containing data until corporate-action conventions are independently checked; do not double-apply historical Yahoo split adjustments. Reject invalid OHLCV, non-finite values, duplicates, reverse dates and missing crypto daily bars. Equity holiday-calendar completeness is not certified.

Drawdown pause: if close equity falls 10% below the running peak, freeze new entries and liquidate at the next available open. Remain paused for the rest of that run. A gap can exceed the threshold. This is a per-account circuit breaker; no aggregate portfolio controls are claimed. End the measurement window by liquidating at the final close with costs; explicitly mark this artificial measurement liquidation in the ledger.

## Evaluation windows

- Development/warm-up: 2024-10-01 to 2025-03-31.
- Validation: 2025-04-01 to 2025-12-31.
- Retrospective holdout: 2026-01-01 to 2026-09-30, first performance inspection under these frozen rules.
- Fixed-rule forward windows: Q2/Q3/Q4 2025 and Q1/Q2/Q3 2026. Each starts with fresh cash and uses only earlier bars for indicator warm-up. No fitting or parameter optimization; these are successive independent-start time windows, not claims of full statistically validated walk-forward optimization.

Reset account/peak at each measured window; preserve earlier indicator history. Compare with 25%-allocated buy-and-hold plus cash, under the same costs/accounting, as well as cash. The static 25% benchmark is matched for initial allocation, not exactly for realized volatility or time in market; report exposure to disclose that distinction. No benchmark drawdown pause so it remains a static holding reference.

Report net return, volatility, descriptive zero-cash-rate Sharpe (252 observations/year equities, 365 crypto), drawdown, closed-trade count, net expectancy, profit factor, holding duration, invested time and dollar costs. Do not treat trades or instruments as independent evidence. No significance claim, annualized growth claim or win-probability forecast from this short dataset.

## Decisions and implementation gate

The gate for this bounded engineering experiment is met by the explicit rules, archived data, costs, windows and per-account risk limits above. The professional validation gate remains open: calibrated costs, longer data, point-in-time universe, statistical uncertainty and prospective paper records are missing.

Flag insufficient trade evidence if fewer than 30 closed trades. Passing 30 trades is not proof either. Continue research only if the holdout beats the stated benchmark after base and doubled costs without requiring a revised rule; this is a screening convention, not statistical validation. Negative findings are retained. No strategy is marked validated by this experiment. Changes after inspecting results become separately registered experiments.

## Prospective paper simulator

Use the same deterministic account state transitions for sequential completed bars. Persist state including price window, pending next-open target, cash, units, running peak, pause state, prior date, and ledger. A prospective runner must establish actual first-observed timestamps and known next-executable quotes before generating a paper fill; historical composite next-open replay is not a verified prospective implementation. No automatic real-time orders, no brokerage connection, no live-mode flag.
