# US cycle diagnostics — 16 October 2026

Paper-only observability fix based on merged main 96ad38db59e7ebf4c1bdad588b011918f4c9c76d. No frozen strategy, risk rule, quote threshold, news receipt-time rule, cost assumption or account balance is changed.

## Reproduced reporting issue

track_quality previously treated every non-data/non-quote-error outcome as VALID_QUOTE_CYCLE. CORPORATE_ACTION_REVIEW_REQUIRED could occur during reconcile before fresh_quote was called, so that category could overstate validated cycles. It now gets its own counter, and unknown outcomes become UNCLASSIFIED_CYCLE. Historical counters are preserved; reports explicitly warn that old counts may include review-blocked cycles. No past gaps or invalid days are repaired by reclassification.

## Prepared diagnostics

Each completed enabled US poll logs one US_CYCLE_HEALTH JSON summary. It includes current observation time, paper-only marker, symbol, fixed status/reason codes, whether fresh_quote returned successfully this cycle, and whether an action-review file was found (null if processing did not reach the check). File presence is not independent action verification. Quote validation is not a fill or full-session certificate.

The summary uses explicit whitelists. It excludes provider errors, URLs, quote prices, balances, positions, fills, tokens and manifest contents. Calendar/credential failures emit a generic US failure record. Logging I/O failure is suppressed without account retry. Disabled module still returns without network or logging. Normal fill results retain their existing behavior; new fields are metadata only.

The counters measure completed polls, not every HTTP retry. A review-blocked cycle can have a validated quote if the block occurred inside fill; it is still separated from unblocked quote cycles. A missing cycle summary can also reflect failure before poll completion; absence is never automatically classified as a rejected quote.

## Verification

113 deployment and 147 research fixtures PASS via scripts/run_test_campaign.py in separate interpreters. Three new tests per mirrored suite cover blocked/unknown count classification, field/secret whitelisting and logging I/O failure, and history-stage poll failure with quote_validated false. Existing repeated-poll fixture now checks quote_validated true and missing review-file metadata on successful validation, while preserving no duplicate fill.

These are fixture tests, not evidence of returns. Candidate offline volatility research from PR #10 is not part of this branch's test counts.

## Production investigation and next action

The prior bounded October 15 log search found no NO_FILL runtime messages during the 16:54–18:23 UTC lab gap. That means the old log stream does not expose per-cycle rejection causes; it does not mean there were no rejections. News polling continued and lab records were missing, but quote rejection versus earlier processing failures remains unconfirmed.

This change is prepared in a PR only. Once reviewed and explicitly deployed, new summaries can distinguish history/data, quote stale/spread, review-file presence and corporate-action errors. Mounted private state remains unavailable through the connector. Owner-only /audit and independently reviewed current issuer-action coverage are still required to repair the AAPL block. The old dated October 14 manifest is not extended or overwritten by this patch.

No merge, deployment, production writes, live orders, paid services or private-ledger publishing.
