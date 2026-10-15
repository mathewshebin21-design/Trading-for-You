# H1 implementation and data review — 15 October 2026

Paper research only. Implements the first proposal from PR #8; H2 buffer, H3 forecasting and H4 portfolio work remain separate, unimplemented hypotheses. Production and frozen accounts are unchanged.

## Implementation

research/volatility_lab.py introduces an isolated quantity-rebalancing simulator; it does not modify PaperAccount or ComparisonAccount. It uses completed earlier closes for SMA20/100 and the last 20 close-to-close returns for sample volatility × sqrt(252). Long target is min(25%, 2% / annualized volatility). Invalid/zero volatility abstains and liquidates an existing research position at the next modeled open. Weekly rebalancing uses the first available calendar-week session, including holiday weeks. Bearish and permanent drawdown pauses override the schedule. Risk checks use the completed close; consequent liquidation is at the next open, so drawdown can exceed the trigger.

Targets are sized using current open equity with modeled commission/adverse-price deductions, synthetic-unit rounding and no borrowing. Partial increases/decreases preserve cash and units; a completed flat-to-flat cycle includes all partial-trade costs in its P/L. Rebalancing fills are not counted as independent completed roundtrips. At scheduled execution the target ceiling is 25%; drift between executions can exceed it. The sizing budget is not a guaranteed realized-volatility or loss limit.

Comparators: unchanged fixed-sizing SMA, volatility SMA, identical volatility sizing without trend, initial-25% buy-and-hold and zero-interest cash. Both sized alternatives retain the drawdown pause; the original buy-and-hold/cash conventions retain their original exemptions. Historical adjusted prices cannot reproduce live quote validity/corporate-action checks.

CLI:
python research/volatility_lab.py --history PRIVATE_ADJUSTED.csv --calendar PRIVATE_CALENDAR.json --output RESULTS.json

## Test evidence

Seven new fixtures pass: volatility formula/abstention, partial-fill cash replay and complete-cycle P/L, weekly schedule/bearish override, current-close isolation from current-open trades, permanent drawdown pause, nonmutating invalid-data rejection, and no warmup fills/measurement returns.

Exact proposed branch based on PR #8 head 54aeb138a453d96ac6db0ec7b1ad38bc3dddd51d: 110 unchanged deployment tests and 151 research tests PASS. Research was isolated from other open branches by copying the deployed source manifest's research sources and restoring main's audit test before adding H1 files. Combined local campaign: 110 deployment / 156 research PASS; the five extra research tests belong to unmerged PRs #3, #6 and #7. Counts overlap and do not establish trading edge.

One fixture initially failed because its synthetic SMA turned bearish on Tuesday; setting direction explicitly for the scheduling assertion corrected that fixture. Bearish behavior remains separately asserted. No strategy or price parameter was changed to improve results.

## Thirty known-history SPY comparisons

Uses the prior 5,218-bar adjusted snapshot, input hash 6c93e12d27b2725ed1e1de27c6997664d1b25cf298c24e7d42cf0709790c29d5 and cached calendar hash c399eb611c99c4208fac6584da95cdd375f4df773f6a4d04f87292073526ce10. Independent prices/actions remain unverified. Windows 2016–2025, 2021–2025 and January–September 2026 overlap and were previously inspected. Five policies × three spans × ordinary/doubled modeled costs. No tuning, model training or untouched evaluation.

| 2016–2025 policy | Ordinary net return | Maximum drawdown | Doubled-cost net return | Ordinary fills |
|---|---:|---:|---:|---:|
| Fixed SMA | 24.60% | -7.57% | 23.35% | 24 |
| Volatility SMA | 13.65% | -3.37% | 11.81% | 426 |
| Volatility without trend | 20.72% | -3.26% | 19.05% | 523 |
| Initial25% buy-and-hold | 75.01% | -12.74% | 74.69% | 2 |
| Cash | 0.00% | 0.00% | 0.00% | 0 |

Volatility SMA lagged its similarly sized no-trend comparator in every span at both costs. Ten-year mean close exposure was about 14.4% versus 16.4% without trend and 22.0% for fixed SMA; equal sizing formulas do not imply equal realized exposure. Lower drawdown alone does not establish improved forecasting or return superiority. The unbuffered weekly policy generated substantial turnover; H2 remains a separate registered test, not a tuned rescue. No candidate is promoted.

## Correction to earlier reporting

PR #7's review/runner limitation incorrectly stated that inherited volatility, Sharpe and invested-bar metrics include 100 warmup bars. Code inspection and the new warmup fixture show PaperAccount.step(trade_enabled=False) appends no curve points. Those metrics therefore use measured bars, not those warmup bars. H1 also records only enabled bars. This corrects the narrative; previously reported net returns/drawdowns are unaffected. The older PR text should be corrected when integrating it.

## Limits and next action

No fresh external data, IEX execution qualification, AAPL recovery, private performance audit or profitable forecast is claimed. Existing ordinary/doubled costs remain 10/20 bps commission, 1/2 bps adverse spread and 5/10 bps slippage per side; cash interest/taxes are omitted. Full result JSON retains costs, exposure, turnover, fill counts and natural-cycle counts. Raw prices/ledgers are not published.

H1 is implemented and tested for offline research only. Preserve this unfavorable outcome, independently verify prices/actions, and evaluate H2 only as a new separately recorded experiment. Do not deploy this as a proven improvement.
