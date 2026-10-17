# Paper bot review — 17 October 2026

Decision: retain paper-only controls. Production and frozen experiments unchanged.

## Exact revisions and fixture evidence

| Scope | Revision | Deployment suite | Research suite |
| --- | --- | --- | --- |
| Actual deployed source | `107457d89399dcfc610ac635a4d3acf3ce4b9430` | 109 PASS | 144 PASS |
| PR10, undeployed volatility candidate | `114d84d41c03d0a71bc14d2ff2ceeb2c594f3a98` | 110 PASS | 152 PASS |
| PR13, undeployed scenario candidate | `ae2c53bb252430567952d8af26358f3094390347` | 110 PASS | 151 PASS |
| This audit-only candidate | Base `96ad38db59e7ebf4c1bdad588b011918f4c9c76d` plus source hashes in TEST_CAMPAIGN_LATEST.json | 110 PASS | 147 PASS |

Each campaign used scripts/run_test_campaign.py, which launches the two fixture suites in separate Python interpreters. Dated campaign reports include exact source hashes. Counts overlap and are not independent performance findings. Other pending research branches were not merged into this candidate. The original October 11 research branch was merged via PR1; its review was read for continuity, not treated as current operational evidence.

## Production snapshot

Railway deployment `16bfa522-3998-4507-a203-2d6c84a084d1` remains SUCCESS at the October 14 source revision above. One running replica, zero crashed replicas, zero reported deployment failures/warnings/criticals in the 24-hour status query. These platform indicators do not verify collector completeness or accounts.

Pending patch `f0e0cf8e-8fbf-49d0-8dc4-2ab0df144113` still stages only source commit `107457d...` to main `96ad38d...`. It was not accepted or deployed. PR10, PR11 (head `e1656646c5f720475d2af51170173cbd070bce2a`) and PR13 are still open and undeployed.

Recent delayed-news health records continue through `2026-10-17T02:53:18.309Z`, marked RESEARCH_ONLY, execution_enabled false, COMPLETE_DELAYED_WINDOW. This is news polling, not successful quote cycles or evidence of fills.

## October 16 real log observations

Bounded service log query: `2026-10-16T13:25:00Z` to `2026-10-16T20:10:00Z`, filter NEWS_LAB_HEALTH, limit 500. Returned 73 matching records (below the limit), first platform timestamp `13:34:40.201Z`, last `19:56:20.651Z`. The saved artifact contains only whitelisted observed_ms, coverage_valid, account status names and paper_only, not private ledgers, balances, quotes, credentials or provider text.

- All 73 records report paper_only true and delayed-news coverage_valid true.
- Per account: 1 AWAITING_POST_DECISION_QUOTE, then 72 CORPORATE_ACTION_REVIEW_REQUIRED.
- Maximum adjacent **observation-time** gap: 320.761 seconds; no adjacent gap exceeds 600 seconds. Compared with the October 15 5206.271-second gap, continuity is better in this bounded sample. The prior gap's cause is unresolved, not repaired by this finding.
- Separate NO_FILL-filter query returned no records in the same window. That cannot establish valid quotes or zero rejections: deployed source lacks the cycle diagnostics proposed in PR11.

`OCT16_LOG_AUDIT_2026-10-17.json` is reproducible from `OCT16_SANITIZED_LAB_HEALTH.json` with audit_forward_logs.py. It correctly requires review. Session completeness, independent corporate-action coverage, balances and trade accounting remain unverified. Missing session boundaries and limited log scope are not filled with assumed observations.

## New regression finding and fix

Before this change, isolated synthetic statuses NEWS_DELAY_ENTRY_BLOCKED, ENTRY_PAUSED, REJECTED_SIZE and UNRECOGNIZED_NEW_STATUS each returned review_required false despite valid news coverage not resolving these states. Reproduced locally before patching.

The offline audit now counts delayed-news, pause and size-rejection blocks; unfamiliar statuses require review instead of silently looking clean. Initial AWAITING_POST_DECISION_QUOTE is separately counted as waiting, not a fill or automatic failure. Added three regression tests, including unknown-status fail-closed reporting. This does not change runtime rules, execution, risk pauses, account state, experiment fingerprints or receipt-time news handling. Ordinary/doubled-cost research comparisons are preserved.

## Blockers and next action

The corporate-action review block persists; no current mounted review manifest, private ledgers or recovery archives were accessed. Its exact private-state cause remains unverified. Never clear flags, extend review dates without independent evidence, rewrite frozen balances, or reset invalid days to manufacture valid comparisons.

Next: review the audit-only patch and PR11 diagnostics; independently review required dated issuer corporate-action evidence against a copied persisted state before any proposed operational repair. Recover reviewed historical input for candidate strategy evaluation. No fresh historical price campaign was run today; fixture tests and health logs do not establish alpha. Current private P/L and profitability remain unknown. No paid services or live orders were used or enabled.
