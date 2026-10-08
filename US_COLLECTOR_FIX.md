# US collector timing fix — 8 October 2026

Paper only. Repeated polls previously reset the decision timestamp even when the completed bar and SMA values were unchanged, causing otherwise fresh quotes preceding that poll to be rejected. The collector now preserves the first observed timestamp for an unchanged decision, including across restart. A new completed bar or revised indicator values starts a new decision. Existing account files and ledgers remain compatible; no balances are reset.

For a new decision, quote timing failures receive at most three requests separated by one second. Five-second freshness, two-second future-clock tolerance, post-decision timestamps, spreads and regular-session checks remain enforced. No paid feed or order endpoint is added. Sparse IEX quotes can still legitimately prevent fills.

Quote timing rejections now report NO_FILL_QUOTE_UNAVAILABLE with QUOTE_STALE, QUOTE_FUTURE or QUOTE_BEFORE_DECISION. Other failures report the stage: ACCOUNT_STATE, HISTORY_FETCH, HISTORY_VALIDATION, STATE_WRITE, QUOTE_FETCH_OR_VALIDATION or FILL_VALIDATION. Provider exception text and credentials are never included.

59 local synthetic/mocked tests passed, including persisted decisions through repeated polls, no duplicate fill, revised decisions rejecting earlier events, bounded stale-quote retries and provider-secret redaction. Runtime validation after deployment is still required; historical generic errors cannot be conclusively attributed from screenshots alone. US overnight corporate-action reconciliation remains incomplete.
