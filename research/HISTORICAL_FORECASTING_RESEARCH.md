# Historical forecasting research — 14 October 2026

Paper-only. No complete market knowledge or profitable prediction is established.

Implemented history_campaign.py: SPY/AAPL/GLD-compatible offline fixed-policy comparison across 10 full calendar years (2016–2025) and overlapping five years (2021–2025). Five policies, ordinary/doubled modeled costs, 100 plus 50 annual comparisons per symbol. Uses existing simple rules and matched 25% invested buy-and-hold; does not train/select models or alter production. Historical news, quotes, delisted universe and intraday data are not supplied. Calendar and prices require independent review. Known historical windows are development evidence, not untouched evaluation.

SPY completed using prior adjusted daily snapshot (5218 bars with warmup), transformation OHLC scaled by adjusted-close/close, zero additional dividends and synthetic units. Independent price verification false. Input hash 6c93e12d27b2725ed1e1de27c6997664d1b25cf298c24e7d42cf0709790c29d5; calendar hash c399eb611c99c4208fac6584da95cdd375f4df773f6a4d04f87292073526ce10. Full raw/provider data is not published. Summary retains unfavorable outcomes. SMA beats benchmark 1/10 ten-year annual windows and 0/5 recent windows; breakout and mean reversion 2/10 and 1/5 respectively at both costs. Mean annual excess is negative for all active policies. Overlapping spans cannot be pooled. Independent annual resets cannot be compounded into portfolio performance.

AAPL public historical download returned non-JSON; AAPL/GLD campaigns and model training are not completed. Existing Railway Alpaca secrets were not copied. No paid data access added.

Verification: 106 deployment and 146 research fixture executions pass in separate interpreters. New history tests check future-data isolation, calendar mismatch, insufficient warmup and unsupported symbols. These executions overlap; not proof of trading edge.

## Tool choices and evidence gates

- Keep existing simulator as reference accounting/cost engine.
- scikit-learn TimeSeriesSplit supports ordered folds/gaps; a chosen horizon also needs label-overlap purge and transformations fitted on training only. Start with logistic regression predicting probability of a positive five-session return, not an unconstrained LLM price guess. Compare calibration/log loss against base-rate forecast; evaluate tradable net returns at next eligible quotes separately. No such model is trained yet.
- Microsoft Qlib is an MIT-licensed quantitative ML research framework. Evaluate in isolated research after audited dataset ingestion; pin tagged versions and record hashes/trials. Repository models/demo datasets do not establish an edge. Do not import production orders or auto-optimization into frozen experiments.
- Alpaca historical data supplies IEX/SIP feeds. IEX is single-venue/free and not consolidated coverage. Actual ten-year availability/entitlement must be checked, never silently truncate data.
- FRED/ALFRED macro data can add rates/inflation/volatility context. Use releases/vintages known at the decision time; revised values cannot be used retrospectively as though initially available.
- SEC/issuer sources for filings and corporate actions; publication and receipt timestamps matter. A missing AAPL action-review manifest is a separate operational blocker and is not repaired by historical training.
- Existing delayed-news feed remains a delayed-news hypothesis. Financial sentiment models may be compared later but sentiment accuracy is not return predictability. Verified social profiles cannot replace complete audited trader records.

## Predeclared forecasting experiment

Before gathering additional data: register one horizon (five sessions), fixed feature set (lagged returns, trailing realized volatility, SMA20/100 distance, lagged volume), base-rate/logistic alternatives, chronological folds with >=five-session purge/gap, calendar/missing-session rejection, publication/receipt checks, cost assumptions and every trial. Use verified pre-2026 history for development and freeze a newly chosen future interval for prospective evaluation; previously inspected history is not held out. Keep no-change/abstention decisions. Reject a model that fails calibration, net benchmark comparison, doubled costs, accounting validity, drawdown/exposure review or dependence-aware uncertainty. No strategy may be promoted merely for best historical return. Prefer simple models before tree/LLM complexity.

Commands: python research/history_campaign.py --symbol SPY --history PRIVATE_ADJUSTED.csv --calendar PRIVATE_CALENDAR.json --output PRIVATE_RESULTS.json; python scripts/run_test_campaign.py.

Primary sources checked 14 October 2026:
https://docs.alpaca.markets/us/docs/historical-stock-data-1
https://github.com/microsoft/qlib
https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
https://fred.stlouisfed.org/docs/api/fred/
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551

No heavy dependency installs, production changes, order submissions, credentials or profitability claim. Next: independently validate prices/actions, obtain complete AAPL/GLD data, and implement predeclared baseline forecasting on audited inputs.
