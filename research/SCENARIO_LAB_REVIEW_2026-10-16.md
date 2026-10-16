# Scenario research candidate — 16 October 2026

Paper research only. No trained AI, order integration, validated edge or perfect strategy claim.

## Source study

Read-only inspection of pst-group/pysystemtrade commit
`164328bd76d2937d3dd61491377704c488283bc2`:

- [forecast_combine.py](https://github.com/pst-group/pysystemtrade/blob/164328bd76d2937d3dd61491377704c488283bc2/systems/forecast_combine.py): weighted forecasts, diversification adjustment and mapping/capping.
- [positionsizing.py](https://github.com/pst-group/pysystemtrade/blob/164328bd76d2937d3dd61491377704c488283bc2/systems/positionsizing.py): forecast and volatility scaling, position buffers.
- [portfolio.py](https://github.com/pst-group/pysystemtrade/blob/164328bd76d2937d3dd61491377704c488283bc2/systems/portfolio.py): instrument weights, diversification and risk scaling.

These are useful architectural lessons, not evidence that a regime classifier is profitable. Upstream is a futures framework with GPL-3 licensing. No upstream code was copied, installed or executed; this implementation uses our existing simulator and independently written rules. No modifications or contributions to upstream.

## Implemented candidate

`scenario_lab.py` adds an offline daily-close classifier and one fixed long-only router. Latest completed close determines a target for the next modeled open. Existing 25% entry allocation and permanent 10% drawdown pause remain. Allocation can drift while held; this is not a continuously enforced portfolio exposure cap. Regime changes reuse the existing position: no separate strategy subaccounts or forced sell/rebuy on a label change. Warmup is 100 bars.

| Scenario | Exact initial rule, evaluated in order | Research policy |
| --- | --- | --- |
| Invalid/unknown | Invalid positive finite closes, nonfinite derived return, or fewer than 100 closes | Cash |
| Stress | Last-20-return sample annualized volatility >=40%, or latest close return <=-5% | Cash |
| Downtrend | SMA20/SMA100 - 1 < -2% | Cash; no shorting |
| Up breakout | Average separation >2%, latest close above previous 55 closes | Existing 55/20 close breakout |
| Uptrend | Average separation >2%, no breakout | Existing 20/100 trend |
| Range | Absolute separation <=0.5%, volatility <=20% | Existing 20-day mean reversion |
| Ambiguous | Everything else | Cash |

Thresholds are newly registered assumptions, not values fitted to maximize returns. A falling price can continue falling; average and volatility signals lag; range detection can fail at a breakout. The router may incur more turnover and perform worse than fixed policies. This is an auditable baseline for testing later AI proposals, not AI market understanding.

## Broader strategy coverage

| Family | Current state / required evidence |
| --- | --- |
| Trend, breakout, mean reversion, cash | Implemented offline fixed policies and candidate router |
| Volatility sizing | Separate unmerged H1 research branch; not combined here |
| Diversified allocation | Requires synchronized reviewed multiasset prices, distributions and portfolio accounting |
| Relative value / pairs | Requires point-in-time pair selection, hedge estimation, borrow and spread costs; not implemented |
| Carry / futures | Requires term structures, contract rolls and margin model; not implemented |
| Event / news | Existing separate frozen delayed-news paper experiment; receipt-time rules and corporate-action review still apply |
| Copy trading | Requires qualified leader identity, complete timestamped fills, risk and execution-delay evidence; no source qualified |
| Options / market making | Requires historical option chains or order books, executable liquidity and additional risk models; not implemented |

No daily-price classifier can diagnose news, executable liquidity or all market conditions from closes alone.

## Validation completed

Candidate based on our `96ad38db59e7ebf4c1bdad588b011918f4c9c76d`, separate branch `research/scenario-lab-2026-10-16`. `scripts/run_test_campaign.py` ran both suites in separate interpreters: deployment **110 PASS**, research **151 PASS**, including **7 new synthetic tests**. Exact Python source hashes are in `TEST_CAMPAIGN_LATEST.json`.

New checks cover scenario cases, invalid/extreme prices, warmup, prior-close/next-open timing, a crash not causing a retrospective same-open exit, persistent risk pause, frozen windows, benchmark presence, ordinary/doubled costs and measured scenario counts. Counts are specific to this branch, not additive to other pending branches.

No fresh real historical campaign was run: previously used raw SPY input is not present in this checkout. No private ledger or production session was audited in this task. Passing fixtures establish behavior only. Production and frozen running experiments were not changed.

## Reproducible next evaluation

After restoring independently reviewed adjusted daily OHLC with distribution treatment and complete session-calendar checks:

```bash
python research/scenario_lab.py --history /path/reviewed.csv --start YYYY-MM-DD --end YYYY-MM-DD --reviewed-adjusted-data --output /path/results.json
```

The flag is an attestation, not an automated audit of calendar completeness. All rows must be chronological; simulator validation rejects duplicate/out-of-order bars. Compare router against all five fixed policies under ordinary and doubled modeled costs. Report return, drawdown, turnover, natural roundtrips, exposure and scenario transitions. Preserve contiguous account/risk state within each evaluation window. Evaluate locked chronological holdouts and unseen forward paper periods, then multiasset regimes; log every trial and avoid retroactively choosing scenario thresholds from the best result. Compare risk-matched alternatives as well as initial-allocation buy-and-hold, whose exposure can drift.

Promotion requires independently reviewed data and accounting, reconciliation, enough independent trade cycles and robust cost-sensitive holdout evidence. No fixed number of tests guarantees profitable predictions. If the router fails to improve defensible risk/return tradeoffs, retain the simpler fixed policy or cash. A later learned classifier must demonstrate incremental out-of-sample benefit over this frozen baseline before any paper integration.
