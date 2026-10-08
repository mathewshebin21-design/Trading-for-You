# Trading for You

Experimental Telegram paper-trading research worker. No live orders or validated profitability.

Root contains the Railway worker and Dockerfile. `research/` contains the research engines and tests. Historical datasets and prior output archives are not published in this source repository.

BTC/ETH public data simulation is implemented. The optional SPY/AAPL/GLD USD research module adds IEX market data, calendar-aware regular hours, SMA20/100 signals, local whole-share simulated fills and Telegram reports. See US_MARKET_SETUP.md for private setup and limitations. Overnight US positions require corporate-action review and block further fills; dividend/split reconciliation remains unfinished.

49 local synthetic/mocked tests passed on 2026-10-08. Run `python -m unittest discover -s research -p "test_*.py"`. Real-data credentials, Telegram delivery, Docker deployment and sustained cloud operation have not been verified. The bot is not currently deployed.

Keep US_PAPER_ENABLED unset until configured with private paper-only data credentials. Keep Telegram token and owner ID in private environment variables. Never commit secrets. Railway activation requires persistent /data storage and verified free allowance; no paid services are authorized.

News analysis and verified trader-copying are not implemented. All strategies remain unvalidated.
