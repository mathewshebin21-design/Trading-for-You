# Copy-trading repository screening — 16 October 2026

Paper-only project. Scope: public repository documentation and official docs, not a complete source/security audit, installation or performance replication. No wallet or brokerage credentials used. No repository qualified as independently verified profitable.

## Shortlist

| Repository | Useful documented capability | Fit and qualification |
|---|---|---|
| https://github.com/freqtrade/freqtrade | Crypto backtests, dry-run, Telegram; official producer/consumer mode can share analyzed data and upstream entry/exit signals | First framework to evaluate for our crypto paper signal adapter. This is signal sharing between configured instances, not automatic access to successful traders or identical account fills. Not our Alpaca US-equity implementation. |
| https://github.com/yuno-research/solana_copy_trading | Rust wallet monitoring/position management; Python swap-data backtesting and wallet scoring | Most directly relevant to researching historical wallet-copy selection. Ranking weights optimized against P/L create selection-bias concerns; require time-separated wallet selection, receipt delay and full costs. License/maintenance qualification incomplete; not approved for code reuse or installation. |
| https://github.com/0xJonaseb11/solana-trading-bot | Documents wallet mirroring, dry-run, Telegram, SQLite audit, position caps and circuit breaker; MIT license and CI/test instructions | Candidate for architecture inspection, not deployment. Test claims were not independently run; P/L tracking is a feature, not a validated performance record. Solana-specific, not SPY/AAPL copying. |
| https://github.com/kevin-bruton/trade-copier | MT4/MT5 account copier; documents symbol mapping and 121 unit/integration tests | A copying-mechanics reference for authorized demo accounts. Tests not run; needs MetaTrader terminals and authorized source feed. No license identified on the reviewed landing page; not approved for reuse. Poor direct fit for current Railway/Alpaca architecture. |

Official Freqtrade signal-sharing docs: https://www.freqtrade.io/en/stable/producer-consumer/
This shares analyzed dataframes and optionally signal columns. Actual fills, account sizing and availability can differ. Documentation warns about forward filling signals. Do not mistake replication of a signal for replication of its historical entry price.

Repository activity/maintenance was only screened from visible structure, CI/test documentation and project pages. Exact latest commit dates, pinned dependencies, CI outcomes, maintainership continuity and vulnerability status were not verified. Stars and README language were not used as proof of profitability.

## Excluded pending deeper audit

https://github.com/ryanmccollum/solana-copy-trading-bot documents PRIVATE_KEY loading and startup through redeem-onchain-sdk/proxy.js. That dependency/execution boundary requires inspection before any installation; this observation does not establish malware. No private keys or package installation were used. Leave it out of our current integration shortlist.

## Performance evidence status

Reviewed material did not establish independently reconciled full follower ledgers, complete cash flows/open losses, costs and durable prospective results. Consequently no ranking by verified net profitability is possible. A backtest, P/L endpoint, advertised speed or large star count cannot establish that copied trades will benefit us. These projects do not supply an independently qualified US-stock trader feed for our existing bot.

## Recommended application to Trading-for-You

Evaluate Freqtrade's producer/consumer design as a crypto signal-ingestion reference, while retaining our own paper accounting/risk gates. Inspect yuno's historical analysis separately if we deliberately add Solana wallet research; do not migrate the bot or add wallet signing just to use it. Neither path repairs the current AAPL review/coverage blockers.

Before qualifying a trader/feed:
1. Obtain authorized complete timestamped history, cash flows, holdings and fees. For wallets, classify transfers, airdrops and unsold positions; a high realized win rate alone is insufficient.
2. Select leaders using only information available before each selection date. Retain failed/deleted wallets and every tested selection variant.
3. Simulate follower decisions at actual receipt time and next eligible price, with missing data, spread, size/liquidity, failed transactions and venue costs. Include ordinary/doubled costs and delay sensitivity.
4. Compare follower net results with passive and non-copy baselines under explicit capital/risk caps, then freeze the candidate for prospective paper evaluation.
5. Review license, dependency chain, credential handling, repeat-event suppression and restart reconciliation before importing any code. Source execution tests do not certify returns.

No installation, source changes to the worker, deployment, live orders, paid services or profitability endorsement. Next concrete task is a read-only, pinned source audit of the chosen framework and a paper-only signal adapter, after confirming a usable authorized leader feed.
