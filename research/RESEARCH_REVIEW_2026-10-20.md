# Paper test review — 20 October 2026

## New session evidence

Production is still SUCCESS deployment `16bfa522-3998-4507-a203-2d6c84a084d1`, source `107457d89399dcfc610ac635a4d3acf3ce4b9430`. Railway reports one running replica, zero crashed replicas and no deployment failures, warnings or critical notifications in its queried 24-hour window. This is a platform snapshot, not session or account certification. Main remains `96ad38db59e7ebf4c1bdad588b011918f4c9c76d`. Staged source patch `f0e0cf8e-8fbf-49d0-8dc4-2ab0df144113` remains untouched.

The October19 regular-session log query (13:20–20:10 UTC, NEWS_LAB filter, limit500) returned 70 records, 13:30:28.079–19:56:44.290 UTC. Each of the four accounts reported AWAITING_POST_DECISION_QUOTE once, then CORPORATE_ACTION_REVIEW_REQUIRED 69 times. All 70 records' coverage_valid fields were true; code inspection shows that field describes delayed-news coverage, not the final comparison-day validity. The existing lab marks review-blocked days invalid. No persisted daily mark was read.

Four successive observed_ms intervals exceeded ten minutes: 632.729, 633.943, 636.754, 635.874 seconds. Platform log arrival intervals differ (maximum641.847 seconds); neither timing series proves a complete session. A parallel NEWS_HEALTH query returned77 records, 13:25:06.199–20:07:25.076 UTC, maximum platform-arrival gap321.879 seconds. All77 reported COMPLETE_DELAYED_WINDOW and execution_enabled=false; total unique_new_records across them was15. News polling continued inside each lab-log gap. This narrows the gap investigation away from a complete worker outage; it does not identify quote, history, reconciliation or lab failure as the cause.

A separate Traceback OR ERROR OR VALIDATION_FAILED query over the same13:20–20:10 UTC interval returned zero matches. This does not establish absence of skipped quotes or lab failures: those outcomes need not contain these strings. The collector reaches the news lab only after history validation and a qualified quote; no persisted quote-quality file or original-account ledger was available. PR11's finer cycle diagnostics remain undeployed. No stale/spread rejection rate is inferred from these lab logs. Latest bounded NEWS_HEALTH retrieval reached2026-10-20T02:52:53.194Z.

## Exact fixture verification

| Scope | Source revision | Deployment fixtures | Research fixtures |
| --- | --- | --- | --- |
| Actual deployed source | `107457d89399dcfc610ac635a4d3acf3ce4b9430` | 109 PASS | 144 PASS |
| Undeployed PR15 checker | `5a8535a03db4b7edd87022f8a997cf35020b296f` | 116 PASS | 144 PASS |

Both campaigns ran scripts/run_test_campaign.py with separate Python interpreters for deployment/research suites. Dated reports preserve exact source hashes; the only local difference during these runs was generated JSON evidence, not Python source. PR15 is still draft/open/unmerged. The original October11 branch is an ancestor of main and already merged; its dated review was re-read. No applicable AGENTS.md exists in this checkout or inspected ancestors. No new reproducible source defect was found, so no speculative fix or threshold tuning was added.

## Blocking evidence and next action

Monday confirms the AAPL lab's review block persisted into a new session. It does not establish whether the mounted manifest is missing, stale, unreadable or mismatched. The current mounted review, original account and four lab journals remain unavailable through configured Railway platform tools. No owner /audit reply or authorized copied private state arrived. Browser sign-in was not retried during this unattended review.

The existing owner-only /audit response and PR15's read-only checker against authorized private copies remain the next diagnostic steps. Obtain fixed reasons and required date coverage before preparing any state repair; do not overwrite a review, clear flags, reset balances, erase gaps or retroactively validate comparison days. The separate October8–16 issuer-source review remains retrospective and is not extended or installed. The October15 gap is still unresolved.

No production state, frozen rules, corporate-action gates, receipt-time news handling, risk controls or ordinary/doubled-cost comparisons were changed. No deploy, paid service, live order, secret copying or publication of private ledgers occurred. No new historical-price campaign ran. Fixture passes and health records do not establish profitability; current private performance is unknown.
