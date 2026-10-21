# Cost validation — 2026-10-21

Tested code: PR #16 revision `5a6c8f27dc2aa3d3c564abede0c74e22064c85c8`; no execution-rule changes.

## Fresh synthetic execution check

Two isolated virtual USD accounts started at $10,000. Both bought and sold 24 shares using unchanged bid $100 and ask $100.10. Each had exactly two simulated fills and zero ending units.

| Cost scenario | Commission USD | Spread + slippage USD | Net P/L USD |
|---|---:|---:|---:|
| Ordinary | 4.802401 | 4.801200 | -9.603601 |
| Doubled | 9.604810 | 9.602400 | -19.207210 |

The implemented ordinary model charges 0.10% commission per side, crosses the observed spread and adds 0.05% adverse slippage per side. Doubled costs double the commission rate, midpoint-to-side spread displacement and slippage rate. These are research assumptions, not verified broker charges. This controlled unchanged-price roundtrip demonstrates that costs reduce equity; it is not a market return or strategy-performance result.

Verification: one targeted deployed-engine fill/restart test and 24 research engine/campaign/benchmark tests passed in separate interpreters. The preceding full candidate campaign passed 118 application and 144 research fixtures.

## Existing historical evidence, not rerun here

`research/SPY_CAMPAIGN_SUMMARY_2026-10-11.json` records the SMA20/100 strategy exceeding its 25%-initial-allocation buy-and-hold comparator in 3 of 20 independent historical windows under both ordinary and doubled costs. Input prices were an unofficial adjusted Yahoo snapshot and were not independently cross-verified. These independent windows must not be compounded into one track record. No profitable edge is established.

## Forward-test status

Owner-provided AAPL audit: review MISSING, 13 coverage gaps, all eight comparison days invalid. Actual private ledger recovery and current-session corporate-action coverage remain required. No new production trades were triggered, no deployment was performed, and no strategy or frozen experiment files changed during this cost check.
