# SPY development campaign — 11 October 2026

Paper research only. No strategy is validated or selected. No production strategy, credential, infrastructure setting or live-order path was changed.

## Decision

Do not promote any candidate on these results. Each active strategy exceeded the matched 25%-invested buy-and-hold return in only 3 of 20 independent measurement windows, under both assumed cost scenarios. Lower drawdowns are a useful observation, but do not establish superior risk-adjusted performance or a profitable edge.

## Method

The protocol was written before running this campaign. It specifies three fixed active strategies, buy-and-hold and zero-interest cash; 19 independent calendar-year starts from 2007 through 2025 plus January–September 2026. Each account starts with $10,000 virtual capital and targets 25% allocation. Each active account has a daily-close 10% drawdown pause; the passive benchmark has no pause. The comparison therefore evaluates complete policies, not isolated entry signals. All ten strategy/cost combinations are retained per window: 200 comparisons total.

Base assumed costs per side are 10 basis points commission, 1 basis point adverse half-spread and 5 basis points slippage. Stress doubles all three. These are modeling assumptions, not measured execution costs. Signals execute on the next available daily open. Synthetic fractional adjusted units are used; these are not the bot's whole-share execution model. End-of-window liquidation includes costs and is reported separately from naturally closed trades. Independent windows must not be compounded or treated as one continuous account.

## Results

Median return is across independent windows, including the partial 2026 window; it is not a CAGR or a forecast. Worst drawdown is the worst within-window daily equity drawdown. Counts of natural round trips describe separate accounts, not independent statistical samples.

| Policy | Base median window return | Double-cost median return | Wins vs matched buy-and-hold, base / stress | Worst base drawdown | Natural round trips, base |
|---|---:|---:|---:|---:|---:|
| SMA 20/100 | 1.02% | 0.81% | 3/20 / 3/20 | -7.14% | 25 |
| Breakout 55/20 | 1.13% | 0.68% | 3/20 / 3/20 | -4.06% | 61 |
| Mean reversion 20 | 1.06% | 0.69% | 3/20 / 3/20 | -11.32% | 93 |
| Buy-and-hold, 25% initial allocation | 3.41% | 3.32% | Reference | -11.94% | 0 |
| Cash, no interest | 0.00% | 0.00% | 3/20 / 3/20 | 0.00% | 0 |

The mean-reversion account triggered its pause in one base-cost window. Its drawdown exceeded 10%, illustrating that a daily-close trigger cannot guarantee a 10% maximum loss. Costs lowered active strategy median returns. These descriptive comparisons contain no multiple-testing-adjusted significance claim.

## Data and evidence limits

5,218 daily SPY bars from 3 January 2006 through 30 September 2026 matched the expected community XNYS calendar exactly. Two floating-point OHLC discrepancies of at most 1e-12 were normalized and recorded. Calendar completeness is not price correctness.

The input is a mutable, unofficial Yahoo Finance snapshot. OHLC is multiplied by adjusted-close/close and distributions are set to zero to avoid double counting. Price values, adjustment factors and corporate actions have not been independently cross-verified. Input, calendar and protocol hashes are saved with the summary; the original snapshot and transformed inputs are preserved privately for replay. The raw price history is not committed to the public repository.

All history is retrospective development evidence. Earlier project tests already inspected 2018–September 2026, and older crises are widely known. No interval is represented as an untouched holdout. Cash earns no interest; overnight gaps, time-varying spreads, order-book liquidity, taxes and execution failures are not fully modeled. This campaign does not measure the deployed bot's performance or certify its current market data.

## Verification and next gate

94 deployment tests and 126 research tests pass. New checks cover missing sessions, invalid OHLC/warmup, future-input isolation, retained alternatives/cost stress, terminal-trade counts, and rejection of dividends on an adjusted proxy. Test passes establish software checks, not trading profitability.

Replay `python research/spy_campaign.py --history INPUTS/spy_adjusted.csv --calendar INPUTS/calendar.json --output RESULTS.json --reviewed-adjusted-proxy` using the preserved inputs.

Next: independently verify the historical input; audit persisted forward-paper ledgers and data coverage; compare frozen paper policies and benchmarks at identical timestamps, including costs and missing-data exclusions. Do not repeatedly tune the active bot against the same evidence. A short initial review can identify operational failures; adequate prospective trade and regime evidence is still required before any claim of an edge.
