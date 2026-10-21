# Paper review — 18 October 2026

## New reproducible finding

Undeployed PR15 at `be9d4a9afd9ffac7d12c8cad04ba0bae1332744c` checked the original account's US.1 version, but not its currency before calling reconcile. The existing reconciliation routine validates the supplied manifest currency, not the original state's currency. A synthetic original account changed from USD to EUR returned COPIED_RECONCILIATION_PASS and all_copied_reconciliations_passed=true. This is a checker identity-validation defect, not evidence of corrupted production accounts.

The candidate now requires the original identity tuple `(US.1, AAPL, USD)` before copied-state reconciliation. A mismatch returns the fixed IDENTITY_OR_RULES_MISMATCH code, cannot contribute to the all-passed result and does not change private input bytes. One new regression exercises currency, symbol and version mismatches. Existing missing-file, balance-drift, dated-coverage and no-mutation checks also pass. No running accounting module, risk control, experiment fingerprint, news receipt-time rule or cost comparison was changed.

## Exact fixture scope

| Scope | Revision | Deployment fixtures | Research fixtures |
| --- | --- | --- | --- |
| Actual deployed code | `107457d89399dcfc610ac635a4d3acf3ce4b9430` | 109 PASS | 144 PASS |
| Updated PR15 candidate | Parent `be9d4a9afd9ffac7d12c8cad04ba0bae1332744c` plus exact source hashes in TEST_CAMPAIGN_LATEST.json | 116 PASS | 144 PASS |

Both campaigns used scripts/run_test_campaign.py in separate Python interpreters for deployment/research fixtures. Deployed evidence is saved as DEPLOYED_FIXTURE_CAMPAIGN_2026-10-18.json. PR15 had 115/144 before this additional regression; prior dated reports describe their own scopes. Counts overlap and do not measure profitability. No applicable AGENTS.md was found in this checkout or ancestors. The original October11 branch was already merged via PR1; it is not a pending experiment to retest separately.

## Fresh production observations

Railway still reports deployment `16bfa522-3998-4507-a203-2d6c84a084d1` SUCCESS at `107457d...`, one running replica, zero crashed replicas and zero reported failures/warnings/criticals over the queried 24-hour status window. Main remains `96ad38db59e7ebf4c1bdad588b011918f4c9c76d`. PR15 remains unmerged. The pending source patch `f0e0cf8e-8fbf-49d0-8dc4-2ab0df144113` was not accepted or changed.

Latest bounded NEWS_HEALTH retrieval shows six records from `2026-10-18T02:48:27.602Z` through `03:14:38.012Z`, all RESEARCH_ONLY, COMPLETE_DELAYED_WINDOW and execution_enabled=false. This is delayed-news polling, not quote qualification, fills, complete sessions or private performance. A separate bounded log search from October17 03:15Z to October18 03:15Z for Traceback OR ERROR OR VALIDATION_FAILED returned zero matching records. This text-filter result does not establish absence of all errors or resolve older startup review failures.

The weekend adds no new regular US session to the prior October16 sample. No new quote/spread rejection inference is possible from these news-only records. No private ledger, mounted review manifest, original journal or recovery archive became available. Corporate-action repair remains blocked on private-state evidence, not on fixture test counts. No new issuer review date was fabricated or extended.

## Next action and limits

Obtain the existing owner-only Telegram `/audit` diagnostic, then run the read-only checker against authorized copied private state. The October8–16 retrospective review is not future coverage and is not installed. Do not overwrite a mounted review, clear flags, reset gaps or invalidate preserved experiment history based on this public review or synthetic tests. Review exact failure reasons and required dated coverage first.

No production changes, automatic deployment, live orders, paid services, secret retrieval or private-ledger publication occurred. No historical-price campaign ran today. Current private results and profitability remain unverified.
