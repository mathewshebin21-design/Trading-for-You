# Delayed-news prospective paper experiment — 9 October 2026

Implemented, tests passed; deployment status must be verified separately.
No broker order endpoint, live order credential or paid service is used.

## Coverage

The collector now requests a fixed interval ending 15 minutes before its receipt
clock, not a supposed real-time tier. Each cycle follows up to 10 pages (50 rows
per page), with a 20-second request budget and 5-second per-request timeout.
Canonical source metadata, provider ID/update, revision fingerprints and our own
receipt times are retained. Report separate record occurrences and unique newly
inserted records. Duplicate rows do not start fresh receipt times.

First requested interval is the preceding 24 hours of delayed data; subsequent
intervals start one minute before the last complete end. Failed, malformed,
rejected, repeated-token or capped pagination is INCOMPLETE and cannot advance
that checkpoint. Partial data remains visible but cannot qualify entries. If
24-hour volume exceeds the cap, the collector may remain incomplete; it does not
claim coverage or silently skip records. Completed interval metadata persists in
the bounded private SQLite database. COMPLETE_DELAYED_WINDOW means the provider
finished pagination without rejected rows, not independent truth or completeness
of the provider's own news universe. Late backdated revisions can still escape
the one-minute overlap and are a limitation.

This changes the original proposal into an explicitly delayed-news experiment;
rules are frozen before its first future observation. It is not a news-scalping
system. Provider access and market-data redistribution rights are not expanded.

## Four independent virtual accounts

New AAPL baseline and news-delay accounts each run base and doubled execution
costs, starting at virtual USD 10,000. They receive the SAME original collector's
validated IEX quote and completed SMA20/100 input, without new price requests.
Accounts are hypothetical alternatives, not one combined USD 40,000 portfolio.
The existing bot accounts and other shadow experiments are not rewritten.

Entry target: SMA20 > SMA100, at most 25% of current equity, whole shares,
displayed-size caps, no leverage/pyramiding. Baseline has no news delay. Delayed
account blocks BUY until 30 minutes after the most recent new or revised AAPL
record RECEIVED after experiment start. Publication time cannot move a decision
backward. A change in entry eligibility waits for a subsequent source quote.
All source events are deduplicated across restarts.

Both account variants block new entries unless the latest news cycle completed
its delayed interval, was received within 10 minutes, and has an end 15–25 minutes
behind the decision. An observed quote gap over 10 minutes also blocks entries
and invalidates that day's comparison. Market closure itself is not an outage;
the gap test applies within the same session, not across overnight closure.
Global entry pause applies to all accounts. Exits and risk handling continue
when news is incomplete. A 10% observed drawdown permanently pauses that account
and attempts to exit; gaps and limited bid size can exceed the trigger.

Base fee 10 bps and slippage 5 bps, plus observed spread; doubled case doubles
the observed half-spread, fee and slippage. The common fill helper accepts an
explicit cost multiplier; its existing default remains base costs. Overnight
holdings require the same private reviewed corporate-action manifest as the
original US accounts. Balance replay, receivables and reviewed payments apply.
Failure in this news experiment cannot block original-account processing.

## Results

Owner-only `/news_lab` reports each separate account's indicative net P/L,
excess dollars versus its matched trend baseline, observed drawdown, modeled
execution costs, natural roundtrips, fills, shares and mark age. Reports remain
INSUFFICIENT_EVIDENCE; no automatic winner or profitability label exists.
Timestamped daily marks are LAST OBSERVED, not official closing prices. Any
news, quote or accounting gap keeps that day's mark invalid even after recovery.
Experiment fingerprint includes rules and relevant implementation bytes; code
changes require a new experiment rather than rewriting old rules/results.

The existing on-volume snapshot includes the `*_lab.json` file, but not the
private research SQLite database. Missing news history prevents further
qualification. Off-volume disaster recovery is not implemented.

Full current code tests: 94 deployment and 115 research fixture tests. Pagination,
duplicate/revised receipt times, missing coverage, delayed-entry expiry, strict
post-decision quotes, doubled costs, immutable invalid days, risk pause/partial
exits and failure isolation are tested. These do not prove provider reliability,
profitability, real production fills or independent factual verification.

Until sufficient prospective evidence exists, evaluate all results alongside
coverage, fees, exposure and accounting flags. Existing 90-day/30-natural-trade
screening minima do not establish statistical confidence or justify real trades.
