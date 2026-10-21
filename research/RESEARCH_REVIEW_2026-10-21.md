# Paper-bot review — 2026-10-21

## Scope and revisions

- Production service: `telegram-paper-worker` in Railway production.
- Deployed source: `107457d89399dcfc610ac635a4d3acf3ce4b9430`.
- Main source: `96ad38db59e7ebf4c1bdad588b011918f4c9c76d`.
- Review candidate: PR #15 at `3c3d7a2318ff6836902b1870ec3f3b2d218d3ed1`.
- The historical `research/test-campaign-2026-10-11` work is already represented in merged production history; it is not a new unmerged candidate.

## Production health (sanitized)

- Railway reported one online replica, zero crashed replicas, zero failed/crashed deployments in the preceding 24 hours, and no active warnings or critical notifications.
- The live deployment remains `16bfa522-3998-4507-a203-2d6c84a084d1`, status `SUCCESS`.
- The existing non-destructive staged source change from deployed `107457d8` to main `96ad38db` remains uncommitted. This review did not apply it or deploy anything.
- A bounded search for `ERROR`, `Traceback`, and `VALIDATION_FAILED` during the reviewed interval returned no matching runtime records. This is not proof that every cycle completed.

## New recorded-session evidence

Interval reviewed: 2026-10-20 13:00 UTC through 2026-10-21 02:55 UTC.

- `NEWS_LAB_HEALTH`: 68 records from 13:36:07 UTC through 19:57:24 UTC.
- Four initial account states were `AWAITING_POST_DECISION_QUOTE` (one per lab account).
- The remaining 268 account states were `CORPORATE_ACTION_REVIEW_REQUIRED`.
- All 68 log envelopes said `coverage_valid=true`; this field is news-window coverage, not full session validity or profitability evidence.
- Five successive lab-observation gaps exceeded 600 seconds: 629.823, 640.556, 630.884, 629.903, and 640.760 seconds.
- `NEWS_HEALTH`: 158 records from 13:04:17 UTC through 02:53:30 UTC; maximum platform gap 322.001 seconds; 41 unique delayed-news records; zero rejected; all records declared research-only execution disabled.

The news collector continued inside the longer lab gaps. This narrows the incident away from a complete worker outage, but the deployed revision does not emit enough cycle-stage detail to distinguish quote/history/reconciliation failures. No cause is inferred.

## Offline fixture campaigns

The campaign runner executed deployment and research suites in separate Python interpreters.

| Revision | Deployment fixtures | Research fixtures | Result |
|---|---:|---:|---|
| deployed `107457d8` | 109 | 144 | PASS |
| PR #15 `3c3d7a2` | 116 | 144 | PASS |

Artifacts:

- `DEPLOYED_FIXTURE_CAMPAIGN_2026-10-21.json` SHA-256 `00d8d9cc884f267083cddade3f0471ec3169fb48c025f40ca7abae3788a7c5bc`
- `PR15_FIXTURE_CAMPAIGN_2026-10-21.json` SHA-256 `82316cea76e8d88861db5ce5482d073d2b32566621162228997396732aabfd41`

These are deterministic fixture tests. They do not validate live data completeness, corporate-action evidence, execution quality, or profitability.

## Decision and next action

- Do not merge a corporate-action approval or enable execution from this evidence.
- Keep the AAPL research accounts fail-closed.
- The missing private-ledger diagnosis remains the blocking input. Run owner-only `/audit` in Telegram and retain the complete reply privately; the reply should identify the exact review/identity/coverage failure without publishing balances or ledger contents.
- PR #11's bounded cycle-stage diagnostics are still the appropriate review candidate for distinguishing future lab gaps, but this review does not merge or deploy them.

No live orders, paid services, production writes, or strategy changes were made.
