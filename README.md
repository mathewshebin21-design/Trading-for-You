# Trading for You

Experimental Telegram paper-trading research worker. All orders are simulated. No validated profitability or live-order endpoints.

Root contains the Railway worker and Dockerfile. `research/` contains engines and tests. Historical datasets and output archives are not published here. Never commit credentials or private account state.

## Current status — 8 October 2026

The worker has been deployed on Railway. User-supplied Telegram reports confirm command delivery, crypto simulated positions and successful US history/calendar reads. These observations do not establish sustained reliability or profitability. Actual first US opening-alert delivery and eligible US simulated fills still require observation.

BTC/ETH public-data simulation is implemented. The optional SPY/AAPL/GLD USD module uses IEX data, regular-session calendars, SMA20/100 signals and local whole-share simulated fills. Overnight US positions require corporate-action review and block further fills; split/dividend reconciliation remains unfinished. See [US setup](US_MARKET_SETUP.md).

54 local synthetic/mocked tests passed on 8 October 2026. Run `python -m unittest discover -s research -p 'test_*.py'`. Software tests are not evidence of a trading edge.

See [the paper validation plan](VALIDATION_PLAN.md) for operational qualification, frozen prospective comparisons, cost stress tests and decision criteria. News analysis and verified trader copying remain unimplemented. All strategies remain unvalidated.

## Private configuration

Telegram token, owner ID and Alpaca paper-only data keys belong in private environment variables. US_PAPER_ENABLED=1 enables the optional US module after setup. Credentials are used for read-only data/calendar requests, never broker orders. Keep persistent state under /data.

Use only the existing free hosting allowance. No paid plan or data upgrade is authorized. Credit availability and operational gaps must be checked separately; deployment does not imply permanent free hosting.
