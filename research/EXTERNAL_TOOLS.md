# External research tools — 9 October 2026

These tools supplement research, not the Telegram worker or trading decisions.
No paid model calls, live broker connections or additional Railway services are
enabled. Installing a tool does not verify its marketing or strategy performance.

## Vibe-Trading

Official source: https://github.com/HKUDS/Vibe-Trading
Version 0.1.16, revision e532650b527ba3fb146ef00d533f6fc5040d5d2d,
MIT license. Installed into a separate evaluation virtual environment; pip's
dependency consistency check passed. The offline validation module was smoke
tested for reproducibility, interval ordering, window count and invalid inputs.
All 67 upstream validation-module tests passed (NumPy deprecation warnings remain).
A private synthetic end-to-end launcher test also passed; no market returns or
production performance are established by these fixture checks.
The full upstream application, market providers and agent workflows are not
qualified by these checks. No language model was configured or invoked.

Use `python vibe_offline.py /path/to/vibe-trading-evaluation /path/to/private/run`
for exploratory diagnostics on existing upstream-format artifacts. The run must
contain explicit `config.json` with positive `initial_cash`, and
`artifacts/equity.csv` and `artifacts/trades.csv`. Review the upstream CSV schema;
our bot's JSON ledgers are not accepted directly. Never invent timestamps or
silently omit fills to make data fit. The launcher checks the source revision and
tracked agent modifications, strips inherited credentials, and launches only the
offline validation module. Dependency checks are not a security audit.

Important limits found in source: Monte Carlo permutes the same trade P/Ls; it
does not test a strategy against a market-based null. Bootstrap independently
samples returns and ignores serial dependence. The named walk-forward function
splits an already computed equity curve and performs no train/test reruns. The
CSV trade loader excludes zero-P/L rows. All outputs remain exploratory; do not
use its p-values, confidence intervals or probability fields as release gates.
Proper frozen out-of-sample comparisons and cost stress remain in our own lab.

## Fincept Terminal

Official source: https://github.com/Fincept-Corporation/FinceptTerminal
Linux v4.5.0 package downloaded, release SHA256 verified and unpacked separately.
It cannot launch in this workspace: required Qt6 shared libraries and a graphical
desktop are absent. This is not a usable desktop installation. Its advertised
web login currently redirects to the open-source information page.

Use as a separate research workstation when a supported desktop is available.
Do not add the desktop or its dependencies to the small Railway bot worker.
No Fincept market/news API integration exists yet, and no exported research has
been accepted into the bot. AGPL-3.0 licensing requires review before combining
or distributing its code in a commercial product; keep it separate meanwhile.
Third-party feed access, data reuse permissions and AI credits need independent
verification. Screenshots claiming savings or feed counts are not evidence of
timely, reliable data or profitable strategies.

## Acceptance before further integration

Require attributable source URLs, event and receipt timestamps, symbol mapping,
feed permissions, missing-data handling and reproducible transformations for
each imported dataset. External news or agent opinions can be logged as research
hypotheses only; they cannot override risk controls or qualify paper fills.
No third-party checkout, dependency environment, credentials, private artifacts
or raw market-history archive is uploaded to this repository.
