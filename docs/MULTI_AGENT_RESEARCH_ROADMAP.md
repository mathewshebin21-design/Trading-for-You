# Multi-agent paper trading: audited roadmap (2026-11-11)

Status: proposal and source-document audit only. No profitable strategy has been validated.

## Confirmed existing safeguards and blockers
- README: Telegram worker on Railway, crypto simulation, optional IEX-based SPY/AAPL/GLD simulation, no live-order endpoints.
- US_MARKET_SETUP.md: overnight equity positions block fills pending manual corporate-action review; automatic splits and dividends are not reconciled.
- VALIDATION_PLAN.md: seven-day operational screen, frozen prospective evaluation, matched benchmarks, cost stress tests, and separate USD/USDT accounts.
- Dockerfile includes news-related scripts; inclusion does not demonstrate validated news trading.
- Historical comparison gaps must be reproduced before any backtest conclusions.

## Execution sequence
1. Audit modules, tests, persistent-state schema, deployed health and nonsecret Railway settings. Do not modify production.
2. Build deterministic fixtures for stale/future quotes, missing market sessions, incomplete pagination, splits/dividends, delayed news and restarts.
3. Implement a pure data-quality gate that rejects future information, incomplete sessions, stale quotes and unreconciled corporate actions. Default off until tested.
4. Require ledger replay and idempotency checks before changing any strategy.
5. Freeze baseline strategy, universe, data sources, benchmark, costs and future evaluation window.
6. Add research agents behind a paper-only interface; never allow LLM outputs to bypass deterministic risk checks.
7. Validate against cash and matched-exposure buy-and-hold, including doubled-cost sensitivity, drawdown and uncertainty.
8. Only after operational qualification, use Telegram for audited paper alerts. No live trading authorization.

## Proposed eight agents
1. Data ingestion and provenance; 2. Market regime; 3. Strategy hypotheses; 4. Bull case; 5. Bear case; 6. Backtest and leakage checks; 7. Deterministic risk gate; 8. Review and Telegram reporting.

## Acceptance gates
- Every market observation records source, exchange time, first-observed time and data-quality status.
- No fabricated prices, silently filled gaps, or decisions using information first observed later.
- No new fills when a corporate-action hold, drawdown pause, stale-data gate or global pause applies.
- Keep USD and USDT accounts separate; account equity must reconcile to cash and positions.
- Reproducible tests and full suite pass, with commit and command logged.
- No claims of profitability from synthetic tests, in-sample backtests or unverified social posts.

## First implementation PR after audit
Add isolated data-quality validation plus regression tests, then review integration boundaries before changing the worker. Do not deploy or migrate automatically.