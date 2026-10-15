# Paper bot review — 15 October 2026

## Scope and exact revisions

Read-only Railway inspection; no production state writes, configuration changes or deployment. No applicable AGENTS.md found in recovered repository or checked ancestors. Railway use-railway and operate instructions inspected.

Production deployment 16bfa522-3998-4507-a203-2d6c84a084d1 is SUCCESS at 107457d89399dcfc610ac635a4d3acf3ce4b9430. Startup reported ACTION_REVIEW_BOOTSTRAP VALIDATION_FAILED_NO_REPAIR. The exact accounting failure remains unknown because this release logs a generic reason. Main is the merged PR #5 revision 96ad38db59e7ebf4c1bdad588b011918f4c9c76d; Railway still has that source update STAGED, not deployed (patch f0e0cf8e-8fbf-49d0-8dc4-2ab0df144113). Fresh NEWS_HEALTH processing observed through 2026-10-15T03:19:55Z; not full uptime qualification.

Original research/test-campaign-2026-10-11 is merged through PR #1. Historical research PR #3 remains OPEN and currently nonmergeable, at 31ec716d312fd9d96b32791394370a05cfa9d5e5; its two additional history tests and historical comparisons are not deployed.

## Fixture verification

Deployed-equivalent sources: 109 deployment and 144 research tests PASS in separate interpreters. Recovered Python files matched the deployed saved source-hash manifest except railway_start.py (manifest predates bootstrap); that file plus bootstrap implementation/tests were fetched at the exact deployed commit into an isolated test directory.

Merged-main equivalent: 110 deployment / 144 research PASS. This PR adds one regression for consecutive 640.759/635.967-second lab observation gaps with valid news markers and blocked accounts: main-equivalent research becomes 145 PASS. Combined local research including unmerged PR #3 becomes 147 PASS, with 110 deployment PASS via scripts/run_test_campaign.py. Counts overlap and are not independent evidence of edge. The mixed local latest manifest is deliberately not presented as a production manifest.

## New October 14 production evidence

Bounded query 13:30–20:00 UTC returned 70 NEWS_LAB_HEALTH records: one AWAITING_POST_DECISION_QUOTE then 69 CORPORATE_ACTION_REVIEW_REQUIRED in each of four accounts. All reported coverage_valid true and paper_only true. Sanitized observations are retained in FORWARD_LOG_OBSERVATIONS_2026-10-14.json; no balances, provider credentials or private ledger.

Two adjacent candidate observation gaps:
- 17:32:55.858 → 17:43:36.617 UTC: 640.759 seconds.
- 17:43:36.617 → 17:54:12.584 UTC: 635.967 seconds.

These use observed_ms, not platform ingestion timestamps. News processing logs continued at 17:38:21 and 17:49:02 UTC, so missing lab records are not proof of a stopped worker. us_paper.poll invokes the AAPL news lab only after fresh_quote validation and fill/state handling; a quote rejection can skip a lab observation. That is a plausible mechanism, not the confirmed cause in these private cycles. No calibrated quote rejection rate or spread/stale distribution can be inferred from these health records; persisted quality records and latest_poll/ledger are needed. No threshold was loosened. Boundary coverage/session completeness remains unverified, and October 9's earlier gap remains unresolved.

The offline regression verifies that both gaps stay visible despite valid news coverage and unchanged inputs. No production or frozen strategy code changes.

## Recovery and next evidence

PR #5's diagnostic/earlier-date correction is not deployed, and even that bundled ordinary-action review ends October 14. At this check it is still October 14 in New York; the file cannot cover the October 15 US session. Deploying the dated patch later alone will not restore current-session coverage. Do not extend review dates mechanically or reset prior invalid days. Obtain fresh issuer-action evidence and validate an appropriately dated manifest against copies of original and four news-lab accounts before any authorized installation. Existing review files are preserved by the installer; an existing invalid/expired file is not automatically replaced.

Mounted private state is not accessible through this connector. The owner-only /audit plus an authorized private snapshot are needed for exact failure diagnosis and reviewed accounting. No current private P/L or profitability certification is available. Existing replay PASS checks arithmetic only. Receipt-time news rules, paper-only execution, risk/corporate-action gates, ordinary/doubled costs and frozen fingerprints are preserved. This review PR is not merged or deployed.
