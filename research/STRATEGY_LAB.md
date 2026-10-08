# Strategy comparison lab — paper research only

Implemented on 8 October 2026. No network access or order execution. This is an
offline research tool, not a deployed replacement for the Telegram collector.

Five fixed accounts share measurement dates, starting capital and price history:

| Account | Objective rules |
|---|---|
| Existing trend | Completed-close SMA20 above SMA100 |
| Breakout | Enter above preceding 55 closes; exit below preceding 20 closes |
| Mean reversion | Enter below 98% of the 20-close mean; exit at/above that mean |
| Matched buy-and-hold | Invest 25% at first measured open; hold until measurement end |
| Cash | No trades; zero interest |

Signals use completed bars and execute at the following bar's open. Each strategy
uses at most 25% initial-entry allocation, no leverage or pyramiding, and the
existing permanent 10% drawdown pause. Gaps can exceed that threshold. Benchmarks
do not pause. Base and doubled fee/spread/slippage models run separately. US
whole-share sizing is respected. Terminal liquidation is labeled and excluded
from the reported natural roundtrip count. Every result remains unvalidated;
there is no automatic winner selection.

Run against independently reviewed, consistently adjusted data:

```sh
python strategy_lab.py --history reviewed_normalized.csv \
  --start 2025-01-01 --end 2025-12-31 \
  --reviewed-adjusted-data --output private_comparison.json
```

Add `--crypto` only for uninterrupted daily crypto histories. Required CSV columns:
Date, Open, High, Low, Close, Volume, Dividends, Stock Splits. Adjusted total-return
inputs must have zero distributions/splits to avoid double counting. The review
flag is an operator attestation, not an automated certification. Equity calendar
completeness and adjustment provenance must be checked separately. Input SHA256
is recorded; output cannot overwrite input. No raw history is published here.

## Verification and interpretation

66 unit tests pass across the project, including seven comparison-specific tests:
next-bar execution, breakout reference windows, mean-reversion entry/exit rules,
matched benchmarks, doubled costs, insufficient warmup and future-bar isolation.
50 comparisons ran on cached 2025 history (five assets, five accounts, two cost
levels). Those prices were previously inspected; these are development results,
not unseen validation. Daily adjusted-price simulations are not actual quote fills.
The results varied substantially by asset; no strategy was promoted.

## Remaining deployment blockers

The current bot still runs its original SMA strategy. This offline module does
not create prospective Telegram shadow accounts. A proper future comparison must
freeze the code, start date, rules, feed and cost assumptions before collecting
new observations, preserve separate ledgers, and reconcile their quotes/fills.

US overnight holdings remain blocked by corporate-action review. Do not clear
that flag merely because an action feed returns no records. Splits, dividend
entitlements/payments, revisions, delayed announcements and unsupported actions
need reconciliation and restart/idempotence tests before multi-session US returns
can be trusted. Alpaca explicitly warns that corporate-action creation can be
delayed: https://docs.alpaca.markets/us/reference/corporateactions-1

News and verified-trader copying remain disabled: no complete, attributable,
timely feed has been qualified. Do not substitute social-media claims for one.
No paid hosting changes, live credentials or live orders are part of this work.
