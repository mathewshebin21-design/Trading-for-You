# Paper bot test review — 16 October 2026

## Recovered scope and revisions

Workspace maintenance removed the prior local checkout/raw data. Re-cloned the GitHub repository and created separate worktrees at production and candidate commits. No applicable AGENTS.md found in the recovered repository or checked workspace ancestors. Inspected Railway skill and operate reference; platform access remained read-only.

Railway production deployment 16bfa522-3998-4507-a203-2d6c84a084d1 still reports SUCCESS at 107457d89399dcfc610ac635a4d3acf3ce4b9430. The source update to merged-main 96ad38db59e7ebf4c1bdad588b011918f4c9c76d remains STAGED in patch f0e0cf8e-8fbf-49d0-8dc4-2ab0df144113. No deployment was initiated. SUCCESS and fresh logs establish processing observations, not uninterrupted health or valid account performance.

Original research/test-campaign-2026-10-11 was merged via PR #1. PR #3 remains open at 31ec716d312fd9d96b32791394370a05cfa9d5e5. PR #9 is open at d345ac8f0d0d047f8e19629deaa4ad350fc34b80, stacked on literature PR #8. The volatility lab and its tests are candidate research, not deployed worker code.

## Separate-interpreter fixture results

Ran scripts/run_test_campaign.py in each exact worktree:
- Production 107457d: 109 deployment / 144 research PASS.
- Candidate d345ac8 before this change: 110 deployment / 151 research PASS.
- Candidate plus this fix: 110 deployment / 152 research PASS.

Saved dated manifests retain source SHA256 hashes and execution times. Counts overlap across suites and revisions; they are not independent market findings. No historical data campaign was rerun: the previous raw adjusted SPY snapshot was removed by maintenance. Existing GitHub summary results remain prior evidence, not newly reproduced price evidence.

## New production coverage observation

Bounded NEWS_LAB_HEALTH query for 15 October 13:30–20:00 UTC returned 58 records: one AWAITING_POST_DECISION_QUOTE and 57 CORPORATE_ACTION_REVIEW_REQUIRED observations for each of four accounts. All reported paper_only true and coverage_valid true. Retained only sanitized time/status/coverage observations; no balances, secrets or private ledgers.

The offline auditor identifies a 5,206.271-second (86.77-minute) candidate lab observation gap from 16:54:48.751 to 18:21:35.022 UTC, using observed_ms. This is materially longer than the prior day's two ten-minute gaps. Bounded news-processing logs across 16:50–18:30 UTC returned 18 RESEARCH_ONLY observations, all COMPLETE_DELAYED_WINDOW and execution_enabled false, with maximum adjacent attempt interval 328.844 seconds. News processing therefore continued through the lab gap. This does not verify quote quality, full session coverage or account marks.

The lab is invoked only after the original account reaches quote/fill handling. Rejected quotes or other original-account failures can suppress lab observations, but the exact reason during these private cycles is not determined from the available health messages. No stale/spread thresholds changed. The separate persisted quote-quality counts/latest_poll records are needed to quantify rejection patterns and distinguish causes.

Fresh NEWS_HEALTH processing continues through 2026-10-16T02:49:46Z. The ordinary-action bootstrap patch remains undeployed; its dated manifest ends October 14 and is already insufficient for October 15/16 coverage. This review does not manufacture a new reviewed date, overwrite manifests, clear risk flags or reset historical invalid days.

## Reproduced candidate bug and regression fix

In research/volatility_lab.py, individually finite positive closes can produce a non-finite return ratio. Reproduction: weight([1e308, 1e-308] * 11) raises AttributeError from statistics.stdev before reaching the documented invalid-volatility abstention.

The helper now checks computed returns for finiteness before estimating volatility. A new synthetic regression exercises both helper abstention and liquidation of an existing research position on a non-weekly session. This preserves the invalid-data exit override, nonnegative balances, capped sizing rules and weekly schedule. No production module, market-data filter, frozen experiment, receipt-time rule or cost assumption changed.

This extreme-data fixture is not a diagnosis of the production lab gap, and no such prices are alleged to have occurred. It repairs a verified boundary failure in candidate code only. Ordinary/doubled-cost comparison code remains unchanged; normal finite-return calculations are unchanged.

## Blockers and next action

Private mounted ledgers/action manifests are unavailable through this connector. Current private P/L, replay validity and session completeness remain unknown. Obtain owner-only /audit, authorized private snapshots, persisted quote-quality evidence and independently reviewed current action coverage; reconcile on copies before any authorized installation. Prior invalid days stay invalid.

For research, review this stacked PR and recover independently verifiable raw price/action data before reproducing H1/H2 or forecasting comparisons. No candidate is promoted from tests, logs or sparse fills. No live orders, paid services, secret copying, production writes, merge or deployment occurred.
