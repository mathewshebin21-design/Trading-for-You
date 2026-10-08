# Experiment 002 — longer history and prospective paper observations

Defined 1 October 2026 before inspecting the new performance results. All execution is simulated. No broker, exchange account, credentials, live orders or live-mode flag.

## Longer-history extension

Retain SMA20/SMA100, 10,000 virtual capital per independent instrument, 25% entry allocation, no leverage/shorts, the 10% permanent per-account drawdown pause and base/doubled cost assumptions from Experiment 001. Retain the convenience universe GLD/SPY/AAPL/BTC-USD/ETH-USD; historical selection bias remains.

Request daily history from 2016-10-01 to 2026-10-01 (end exclusive), using yfinance 0.2.66. Archive returned data, collection time, provider, dependency version and checksum. Data coverage may be shorter, especially for crypto. Do not fabricate missing bars. Exact equity holiday-calendar completeness and delisted universes remain unverified.

For this separate experiment, use adjusted OHLC synthetic total-return price proxies (`auto_adjust=True`), with distributions set to zero so dividends are not counted twice. Fractional synthetic units of 0.000001 apply to all proxies. These prices are not executable historical quotes and are not a full corporate-action accounting implementation. This convention differs from Experiment 001; do not combine the two results as if identical. Reject non-finite data, inconsistent OHLC, duplicate dates and missing crypto days. Each measurement needs 100 earlier bars; insufficient periods are skipped visibly.

Freeze independent-start calendar-year windows 2018–2025 and a Jan–Sep 2026 retrospective holdout. Warm up using only earlier bars. Report every window for every instrument at base and doubled costs (up to 90 comparisons), with the 25%-allocated static buy-and-hold reference and cash. No optimization, no winner selection, no claim of fresh untouched holdout: 2026 price behavior has already been inspected in Experiment 001.

Report trade counts and regime variability. Require a prospective frozen-rule record, calibrated venue costs, longer robust evidence and appropriate uncertainty estimates before any validation claim. Thirty historical trades is only a screening convention. Leave `strategy_validated=False` for every result regardless of returns.

## Prospective crypto session

Only Binance spot BTCUSDT and ETHUSDT. Use two new independent virtual accounts with 10,000 USDT each; no USD conversion or reuse of Yahoo composite account state. Read-only REST klines provide completed UTC daily candles; WebSocket `@ticker` provides exchange event timestamps and indicative best bid/ask and displayed sizes.

On each interactive poll: validate 100 consecutive completed daily bars, reject incomplete/future candles, check the most recent completed candle is yesterday UTC, and record source/first-observed times. Seed the indicator from history but never seed historical trades or P&L. The first decision is observed now, not backdated to candle close. A new day's target is timestamped when actually observed. Preserve existing cash/units/decisions across repeated polls using atomic JSON checkpoints.

Simulated entry/exit uses a new quote event at or after the decision's observed time. Reject quotes older than 5 seconds, more than 2 seconds in the future, wrong symbols, invalid/crossed prices, or spreads above 0.5%. Bound fills by displayed best-side size and observed LOT_SIZE/MIN_NOTIONAL/NOTIONAL filters. Use ask for buys, bid for sells, plus assumed adverse 3 bp slippage and 10 bp commission; do not add the historical assumed half spread again. Displayed depth and ticker values do not guarantee real fills. Position allocation is enforced at entry, not a daily rebalance. No pyramiding or duplicate same-decision buy.

Mark holdings at fresh bid quotes. A 10% drawdown breach permanently pauses the account and simulates liquidation using the next eligible fresh quote. Record event time, receipt time, decision time, quantity, model price and fees. This quote-time intraday risk check differs from the daily-close historical replay and is tracked as a prospective execution convention. Unknown/stale data fails closed with no fill. No news/trader-copy input.

This is an interactive Colab polling session, not guaranteed 24/7 collection. Source/network failures are displayed and archived; no safeguard bypass. Runtime checkpoints require export before disconnect, or explicit restore from a saved export. No Google Drive filesystem mount or expanded permissions are required. Notebook code/visible outputs are saved to Drive normally. A private export will preserve state.

## Reused sources

- https://github.com/ranaroussi/yfinance — pinned historical-data client; unofficial research/personal-use source.
- https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md — unauthenticated public market-data-only endpoints.
- https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md — source timestamped ticker events.
- PyPI websockets 15.0.1 — standard WebSocket client; does not supply or certify market data.

No adopted repository or model is evidence of a profitable strategy. Gold and US stocks remain historical research only until a suitable read-only current feed is configured and verified.

Data-validation amendment after first run: one SPY close exceeded its adjusted high by approximately 3e-14 due to floating-point conversion. Preserve raw CSV and checksum; write separately normalized input only when OHLC discrepancies are <=1e-12 times the price scale. Log every corrected value and reject larger discrepancies. This changes no strategy parameter.
