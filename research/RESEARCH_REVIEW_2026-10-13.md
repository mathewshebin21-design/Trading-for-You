# Paper bot review — 13 October 2026

## Revisions and tests

Railway production deployment c11219aa-a185-4762-9467-686fee88c945 remains SUCCESS at commit 8c0c6de5f48ba99915e6422046d3d85454387cdc. PR #1 is merged; /audit is now included in this release. One configured replica, persistent /data 500 MB, no staged changes. Fresh bounded logs show NEWS_HEALTH polling through 2026-10-13T03:11:05.983268732Z. This is processing evidence, not full uptime qualification.

Recovered deployment-equivalent Python sources were compared with the deployed commit's saved SHA256 manifest. Before the research-only change, 104 root deployment tests and 141 research tests pass; after change, 104 and 142 pass via scripts/run_test_campaign.py in separate interpreters. Only research/audit_forward_logs.py and its test differ from the deployed Python hash manifest. Updated TEST_CAMPAIGN_LATEST.json records source hashes and UTC check time. Counts overlap, and fixture success does not establish trading edge. No applicable AGENTS instructions were found in recovered repository or workspace ancestors; existing review documents and Railway skill were inspected.

## New production observation: blocked corporate-action review

Bounded NEWS_LAB_HEALTH query for 12 October 13:30–20:00 UTC returned 74 observations. Observed times run 13:31:48.850–19:58:32.623 UTC; maximum adjacent observed interval 320.932 seconds. All four AAPL comparison accounts show one AWAITING_POST_DECISION_QUOTE followed by 73 CORPORATE_ACTION_REVIEW_REQUIRED observations each. All records mark news coverage valid and paper-only. No candidate gap above ten minutes appears within this sample; this does not verify session boundaries or complete quote coverage. Friday's prior 635.372-second candidate gap remains unresolved.

The held-position safeguard in us_paper.fill sets review_required when accounted_through/last_session differs from the current session. us_accounting.reconcile requires explicit reviewed inclusive coverage, sources and review time, even for an empty action list, and rejects future coverage. The observed statuses are consistent with absent or unacceptable current-session accounting coverage; no persisted manifest was retrieved, so the exact manifest failure and presence of actual issuer actions are unknown. This is an evidence blocker, not a demonstrated market-data error. Do not bypass review, assert no actions, reset flags, widen stale/spread limits or repair balances from health logs. No simulated fill statuses appear in this bounded sample; that is not an independently reconciled trade count.

## Research fix

The offline log auditor previously set review_required only for gaps or invalid news coverage. It could report false despite corporate-action blocked accounts. It now retains per-account blocked-status counts and flags corporate-action review, NO_FILL_* rejections and NEWS_COVERAGE_* blocks for investigation. A new regression tests these three cases while verifying unchanged inputs and no strategy certification. Only the offline research helper changes; running experiments, fingerprints, receipt-time news rules, costs and accounting remain unchanged.

Replay: python research/audit_forward_logs.py --input research/FORWARD_LOG_OBSERVATIONS_2026-10-12.json --output AUDIT.json

## Next evidence

Obtain the owner-only /audit and /news_lab results and an authorized private saved-ledger snapshot, current calendar and independently reviewed issuer-action coverage. Reconcile all four accounts and validate daily marks before ordinary/doubled-cost comparison or restore testing on copies. The platform connector supplies logs/configuration, not mounted private state, so current P/L, ledger reconciliation and performance remain unknown. Retained observation JSON contains only times, statuses and coverage booleans, not credentials or private balances. No production state, deployment, live order or paid service was changed.
