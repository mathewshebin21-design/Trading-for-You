# Forward paper audit — 11 October 2026

## Observed deployment health

Railway production worker remains Online with one running replica, deployment `306c25c8-ad36-4e3f-affc-7299bc14cf24` in SUCCESS, zero recent failures in the default eight-hour status window, no pending changes and an attached persistent volume. This is a point-in-time health check, not continuous uptime certification.

The latest retrieved Sunday news collector record was logged at 14:31:48 UTC on 11 October: RESEARCH_ONLY, COMPLETE_DELAYED_WINDOW, execution disabled. The feed explicitly delays news by 15 minutes plus polling. This is operational evidence; it is not a news-trading edge.

## Friday observation audit

The bounded Railway query requested 9 October 2026, 13:30–20:00 UTC with filter NEWS_LAB_HEALTH and limit 500. It returned 72 observations from observed time 13:31:05.689 through 19:52:16.591 UTC. Each health record reports paper-only mode and valid news coverage. Sanitized records are retained in FORWARD_LOG_OBSERVATIONS_2026-10-09.json; no balances or credentials are included.

The offline auditor detects one same-day gap of 635.372 seconds, between observed times 19:20:31.632 and 19:31:07.004 UTC (log receipt timestamps 19:20:38.490 and 19:31:08.377). Valid news coverage does not establish continuous quote observation. This gap requires checking the persisted daily valid flag and ledger. Bounded logs could omit records, so the auditor calls this a candidate observation gap, not proof of a collector outage.

The audit explicitly leaves session completeness, ledger reconciliation and strategy validation false. Health statuses cannot establish net returns, corporate-action correctness or complete fill history. The persisted AAPL_news_lab.json and accounting records have not been retrieved through the available Railway connector. No current P/L is asserted.

## Change and verification

Added research/audit_forward_logs.py as an offline audit tool; it does not import or modify the running strategy. It detects same-day gaps over ten minutes, retains failed news coverage and rejects incomplete, duplicate, unordered or non-paper records. Overnight gaps are not treated as intraday gaps; no exchange calendar is inferred. Output includes the input hash and explicit evidence limits.

94 deployment tests and 131 research tests pass, including five new audit tests. Production rules and experiment fingerprints are unchanged. Research changes are reviewable in PR #1 and are not deployed.

Replay: `python research/audit_forward_logs.py --input research/FORWARD_LOG_OBSERVATIONS_2026-10-09.json --output AUDIT.json`.

Next required evidence: owner `/news_lab` output for a current descriptive view; persisted paper ledger, daily_marks, reviewed corporate-action manifests and actual calendar for full reconciliation. Do not certify Friday from the health logs alone or tune the frozen strategy based on this operational gap.
