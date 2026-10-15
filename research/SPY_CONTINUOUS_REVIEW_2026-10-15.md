# Continuous SPY data test — 15 October 2026

Offline research only. No deployment, account edits, model training, paid provider calls or orders.

## Data and method

Uses the existing 5,218-bar Yahoo personal-research snapshot rather than downloading or inventing new prices. Raw snapshot SHA256 matches saved input_metadata.json. Adjusted CSV hash: 6c93e12d27b2725ed1e1de27c6997664d1b25cf298c24e7d42cf0709790c29d5. Cached calendar hash: c399eb611c99c4208fac6584da95cdd375f4df773f6a4d04f87292073526ce10. Parsing enforces chronological finite valid OHLC and zero additional distributions for this adjusted proxy; calendar list matches dates. The original calendar metadata records version 4.11.2 and no missing/extra dates. That package is not installed in this interpreter, and calendar provenance was not independently reverified here. A hash match establishes integrity against the saved snapshot, not price correctness.

New continuous_campaign.py evaluates three uninterrupted windows: 2016–2025, 2021–2025, and January–September 2026. Five existing fixed policies × two cost assumptions × three spans = 30 descriptive comparisons. Unlike prior annually reset accounts, capital and policy state carry across each whole span; spans still overlap and cannot be pooled as independent evidence. This is an exploratory extension after inspecting historical results, not a pre-registered or untouched evaluation.

Uses the existing spy_campaign/ComparisonAccount engine and 100 preceding warmup bars, next-open signal execution, initial 25% allocation, existing drawdown pause, and identical terminal liquidation convention. Ordinary costs are 10 bps commission plus 1 bps adverse spread and 5 bps slippage; each component is doubled for stress tests. Initial-25%-invested buy-and-hold exposure drifts as prices change; it is not equal dynamic risk exposure. Cash earns zero interest, taxes are excluded. Synthetic adjusted fractional units do not reproduce the deployed whole-share IEX implementation or its corporate-action gate.

## Results — cumulative modeled account returns, not annualized

| Policy | 2016–2025 ordinary | 2016–2025 doubled | 2021–2025 ordinary | 2021–2025 doubled |
|---|---:|---:|---:|---:|
| SMA20/100 | 24.60% | 23.35% | 15.15% | 14.56% |
| Breakout55/20 | 14.78% | 12.02% | 7.32% | 5.94% |
| Mean reversion20 | 6.97% | 3.42% | 2.35% | 0.40% |
| Initial25% buy-and-hold | 75.01% | 74.69% | 23.51% | 23.35% |
| Cash | 0.00% | 0.00% | 0.00% | 0.00% |

The ten-year span contains 2,514 measured sessions (4 January 2016–31 December 2025). SMA ordinary-cost maximum drawdown is -7.57% versus buy-and-hold -12.74%; lower return accompanies lower drawdown, not demonstrated superiority. SMA has 11 natural roundtrips plus a terminal liquidation, so this is still a small trade sample. All three active strategies underperform the benchmark in every tested span at both costs. January–September 2026 SMA returns 1.06% ordinary / 0.90% doubled versus benchmark 2.93% / 2.84%. Breakout becomes -0.16% under doubled costs for that span. No strategy is promoted.

Inherited volatility, descriptive Sharpe and invested-bar statistics include the 100 warmup bars; they are not measurement-only statistics and are not used for this conclusion. Full summary JSON retains this limitation. No dependence-adjusted confidence or profitability probability is claimed.

## Correctness tests and exact scope

Two new synthetic tests reject truncated endpoints/missing bars and verify future-price isolation, unchanged inputs and no certification. They are distinct from the historical data experiment. On PR #6 parent 9c362d5234b6234b9bf4bb522845ca978d87cfee, the proposed suite is 110 deployment / 147 research PASS in separate interpreters. The combined local working copy also includes two historical-campaign tests from unmerged PR #3, making 149 research PASS via scripts/run_test_campaign.py. These are overlapping test executions, not additional market evidence. Deployed code remains unchanged at 107457d89399dcfc610ac635a4d3acf3ce4b9430 (109/144 previously verified).

Command: python research/continuous_campaign.py --history PRIVATE_ADJUSTED.csv --calendar PRIVATE_CALENDAR.json --output RESULTS.json

Raw provider prices and private trading ledgers are not published. This PR contains the runner, tests, descriptive result JSON and this review. Historical testing does not repair the AAPL review manifest. Current private performance remains unknown.

## Next evidence

Independently cross-check historical prices/actions and calendar, obtain complete AAPL/GLD histories through authorized data access, and evaluate the already proposed five-session forecasting baseline with chronology/label-overlap controls. Preserve unfavorable outcomes and retain cash/buy-and-hold benchmarks. Keep forward paper experiment accounting remediation separate. No profitable prediction has been established.
