# US paper research extension

SPY, AAPL and GLD have separate $10,000 virtual USD accounts. This is experimental research, not a validated strategy or a broker execution system.

## Private configuration

Leave `US_PAPER_ENABLED` unset until ready. To enable, set it to `1` and privately set `ALPACA_DATA_KEY` and `ALPACA_DATA_SECRET` from an Alpaca **paper-only account**. Never commit credentials. No paid data plan is required by this code. It explicitly requests `feed=iex`; no paid-feed fallback exists. Credentials are used only for GET market data and GET the paper calendar. No order endpoint exists.

The Telegram token and numeric owner ID, persistent volume and verified no-paid hosting allowance are still required separately. The source has been tested locally, not deployed or tested with real Alpaca or Telegram credentials.

## Rules

100 completed trading-session daily bars, adjusted for splits and dividends, supply SMA20 and SMA100. The target is long only when SMA20 exceeds SMA100. Calendar-provided session times handle holidays, early closes and America/New_York daylight saving. Missing or duplicate bars, incomplete pagination, stale quotes (>5 seconds), quotes before decisions, crossed prices and spreads above 0.5% reject fills. Regular hours only; no shorts, leverage or options.

Local whole-share simulated fills use ask for buying / bid for selling, 5 basis points adverse slippage and 10 basis points cost per side. These are research assumptions, not actual broker fees. Each independent account targets 25% equity exposure. Quote size is conservatively capped to one share per reported quote lot. A 10% peak drawdown permanently pauses entries; same-session exits remain possible. Global Telegram `/pause` also blocks entries. Reports identify USD, IEX, timestamp/quote age, trend, shares and simulated fill count. Existing manual commands remain crypto-only.

## Corporate actions and limitations

An overnight held position **blocks all further fills and requires review**. Automatic split quantity changes and dividend cash credits are not implemented. There is no automatic reconciliation/unlock command. Preserve the affected account for review; do not edit its ledger to clear this flag. Overnight positions therefore cannot support a complete swing-trading evaluation yet. No profitability claim is justified. Quotes/equity after a corporate action require reconciliation before interpreting results.

IEX is one venue, not consolidated NBBO. Sparse IEX daily observations can fail the strict completeness check. There is no queue/auction model, guaranteed liquidity, independent data verification, dividend-accounting validation, news model or verified trader-copying. Network errors produce generic errors without exposing credentials. Each poll downloads history/calendar; caching, rate-limit handling and operational soak testing remain future work.

## Verification

Run `python -m unittest discover -s research -p 'test_*.py'` from repository root, or discover in `trading-research` in the original workspace. Tests use synthetic/mocked inputs. No real Telegram delivery, external data connectivity, Docker deployment or sustained operation has been verified.

References: https://docs.alpaca.markets/us/reference/stockbarsingle-1 ; https://docs.alpaca.markets/us/v1.4.2/reference/stocklatestquotes-1 ; https://docs.alpaca.markets/us/reference/legacycalendar

## Telegram market-open alerts

With US_PAPER_ENABLED=1 and working calendar credentials, the collector queues one owner-only US regular-session open notice per trading date. Times are displayed in Asia/Kolkata; the provider calendar handles holidays, daylight saving and early closes. Alerts arrive on the first successful collection during the session, normally within five minutes plus data-request and Telegram latency. A late startup may send a notice later in the session, explicitly labeled with its observation time. Calendar errors and closed sessions send no open notice. Per-date markers and the durable outbox are written in one SQLite transaction, so a restart cannot enqueue the same date twice. Network delivery retries can duplicate a message if Telegram accepted it but its response was lost. Entry pauses do not suppress market-open alerts. No new credentials are needed.

54 synthetic/mocked tests passed after this addition. Actual first market-open delivery remains to be verified.
