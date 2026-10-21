# Missing review recovery and truthful reporting

Owner `/audit` confirms the AAPL review is MISSING. Four lab balance replays pass; 13 gaps and eight invalid days remain. This confirms missing installation, but not the exact earlier startup validation error or validity of the original US account.

The previous startup hard-codes an October 14 review. Its expired coverage prevents installation now. A missing review need not require exporting private accounts: validation can execute inside the existing worker container.

## Changes

- `review_install.py` validates all saved original, shadow, and news accounts on copies, including identity and balance checks. Default is read-only. Explicit `--install` atomically publishes a missing review; existing reviews are preserved. No account files, experiment rules, or historical validity are written.
- Startup uses this validator and a configurable `PAPER_ACTION_REVIEW_SOURCE`, defaulting to the bundled October 20 review.
- Blocks and unknown outcomes no longer increment valid-quote counters. Existing counters are retained and labelled as potentially including legacy review blocks.
- Current P/L is suppressed when accounting is unreviewed or the saved quote is stale. This does not refresh quotes or alter frozen fill/risk handling.

## Reviewed data and expiry

Apple issuer dividend history and split FAQ were retrieved October 21 at about 03:14 UTC, still October 20 in New York:

- https://investor.apple.com/dividend-history/default.aspx
- https://investor.apple.com/faq/default.aspx

No ordinary cash dividend or split is listed for October 8–20. The latest listed cash dividend was declared July 30, payable August 13; the latest split was in 2020. The manifest covers those two event types only and expires after October 20. It must not be extended by changing a date without a new source review. Unsupported events remain outside automated accounting. SPY requires its own independently sourced review and is not cleared by AAPL evidence.

## In-container procedure after deployment

Run as the worker UID 10001 with access to `/data/paper_state`; keep journals on the existing volume. Do not copy credentials or ledgers into GitHub.

Read-only validation of the supplied historical review:

```sh
python /app/review_install.py --state-root /data/paper_state --review /app/AAPL_review_2026-10-20.json --through 2026-10-20
```

To install a missing review, add `--install`. Historical installation returns `current_day_covered=false` after New York midnight; this does not authorize the next session. For current-day recovery, use a freshly reviewed file covering the required original-account date through the current New York date and omit `--through`.

Startup can consume that file using `PAPER_ACTION_REVIEW_SOURCE`. An owner-operated in-container command can install it without exporting private data. No callable remote exec is available in this session, so production installation and private reconciliation have not been performed.

After a successful current-day installation, the next normal poll reconciles copies under existing rules and persists ordinary state updates. Verify `/audit` shows PRESENT and DRY_RUN_PASS, then observe a fresh valid quote and cleared review flag. This does not force an entry. Preserve the eight invalid historical days and start evaluating valid observations prospectively.

## Verification

116 application and 144 research fixtures passed in separate interpreters using `scripts/run_test_campaign.py`. Tests cover read-only validation, unchanged account bytes, atomic missing-file installation, existing-file preservation, currency/balance failures, original earlier-date coverage, explicit historical validation, future refusal, blocked counters, and stale/unreviewed P/L suppression.

No frozen strategy/accounting module changes, production deployment, live orders, or paid services. No profitability conclusion.
