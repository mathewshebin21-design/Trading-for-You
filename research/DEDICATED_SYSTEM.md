# Dedicated paper-trading system

## Scope and status
This project simulates trades only. It has no live-order endpoint, broker credentials, or switch to live execution. Historical and prospective accounts are independent. Profitability is unproven. The supplied Colab notebook is an interactive prototype, not a continuous service.

## Service design
- Read-only market adapters: source identity, event and receipt times, raw archives and stale-data rejection.
- Deterministic strategy worker: frozen rules and first-observed signals; no GPT discretionary order decisions.
- Risk gate: allocation, minimum sizes, cash checks, drawdown pause and permanent pause state.
- Paper execution: bid/ask-based fills with explicit fee/slippage assumptions; displayed liquidity bounds.
- Durable ledger: cash, holdings, decision IDs, source evidence and checkpoint versions. One worker per account; no concurrent writers.
- Research assistant: documented repository review, news/claim collection, evidence grading and candidate hypotheses. Unverified trader records cannot trigger copy simulations.
- Operations: health display, error log, resumable state and export. Fail closed if data or account state is invalid.

## Continuous deployment requirements
Use a dedicated small CPU cloud instance or managed container with persistent storage, a single scheduled worker, process supervision and heartbeat monitoring. Do not assume a Colab runtime stays connected or that this chat runs a background service. No continuous host is provisioned or paid for in this deliverable.

Production readiness requires transactional storage and durable observation/fill commits, exact decimal quantity handling, dependency locking, controlled restart tests, source outage tests, monitoring, and provider terms review. Current JSON checkpoints support interactive research but are not a multi-process production ledger. A paper-service adapter, if later authorized and configured, must use its paper-only endpoint and independent sandbox credentials. Do not request or store secrets in chat.

## External skills and repositories
Apply GPT skills to research, documentation and review. They do not supply verified prices or verified trader track records. Prefer official provider documentation and maintained narrowly scoped libraries. Dependencies used: pinned yfinance for unofficial Yahoo history and websockets for transport. Official Binance public market-data documentation defines the read-only REST/WebSocket interfaces. No pretrained trading model, arbitrary downloaded skill, or profitability claim is adopted.

## Pending research
Gold/stocks current-feed verification; point-in-time universe and corporate actions; actual cost calibration; statistical uncertainty; news incremental-value experiment; independently verified trader-copy records. No strategy is ready for validation or live use.

## Supplied dedicated worker
`run_paper_service.py` runs a single paper poll by default. On a provisioned Linux CPU host, install `requirements-paper.txt` in an isolated environment, then run `python run_paper_service.py --state-dir /path/to/persistent/paper_state --cycles 0 --interval-seconds 60`. This produces virtual ledger checkpoints, raw source records, errors and a heartbeat JSON. An advisory lock prevents two workers from writing the same directory. Stop with Ctrl+C; restart using the same directory. This command has not been deployed as a continuous service. Logs/source archives grow with polling and require retention/backup planning. Do not reset the state directory to conceal losses.
