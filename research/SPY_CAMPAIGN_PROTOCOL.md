# SPY accelerated paper research protocol — 11 October 2026

Frozen before running this campaign. Scope: SPY only. No strategy selection or
production rule change. All history is retrospective development evidence;
2018–September 2026 has already been inspected. Earlier history includes widely
known crises and cannot be called pristine out-of-sample evidence either.

Input: daily OHLC total-return adjusted synthetic proxies, zero distributions
to avoid double counting, starting January 2006. Retain raw provider response,
receipt timestamp, SHA256 and transformation details privately. Check exact date
coverage against exchange-calendars 4.11.2 XNYS sessions through September 2026.
This community-maintained calendar is a completeness check, not official NYSE
certification or an independent second price source. Reject discrepancies.

Independent calendar-year starts 2007–2025 and Jan–Sep 2026, each with at least
100 prior sessions. Each account starts with virtual USD 10,000. Strategies:
SMA20/100, close breakout55/20, mean-reversion20 (enter below 98% of 20-close
mean, exit at/above mean), 25% buy-and-hold and zero-interest cash. All original
rules stay fixed, with 25% entry allocation, no leverage or shorting, permanent
10% observed daily-close drawdown entry pause for active strategies, and no
parameter search. Targets use only completed earlier closes; fills use next open.

Adjusted prices are synthetic proxies: use 0.000001 synthetic-unit quantum,
not supposed historical whole shares. This differs from deployed whole-share
IEX accounts and cannot establish executable fills. Base assumptions per side:
10 bps fee, 1 bp assumed adverse half-spread, 5 bps adverse slippage. Stress:
double all three. Same entry/liquidation convention for matched benchmarks.
Terminal liquidation counts separately from natural completed trades. Report
every alternative/window, costs, exposure, returns, drawdown and excess against
the matched buy-and-hold. Do not compound independent yearly experiments.

Before any favorable conclusion: independently cross-check prices/actions,
review corporate-action coverage, qualify production recovery and gaps, and
collect prospective matched paper observations. Historical results can reject
weak candidates quickly; they cannot prove future profitability. Changing rules
requires a new experiment. No automatic deployment, order API or paid service.
