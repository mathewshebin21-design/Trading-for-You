# AAPL retrospective review and copied-state check

Source base: `96ad38db59e7ebf4c1bdad588b011918f4c9c76d`.
Candidate branch: `research/aapl-review-dryrun-2026-10-17`.

## Independently checked public evidence

On 17 October 2026, inspected Apple's own dividend history and stock-split FAQ:

- https://investor.apple.com/dividend-history/default.aspx
- https://investor.apple.com/faq/default.aspx

Dividend history's latest listed ordinary cash dividend is declared July 30, record August 10, payable August 13, 2026 ($0.27). The FAQ lists the latest split in 2020. Neither lists an ordinary dividend or split in October 8–16. This supports the narrowly scoped retrospective empty-actions manifest `research/action_reviews/AAPL_2026-10-16.json`. This is not an all-corporate-events feed or certification of a private account.

The old bundled manifest ends October 14. It cannot qualify October 15–16, regardless of whether an older startup failure also involved October 8 coverage. Do not treat this as proof of the exact mounted-file problem: the private file has not been read.

The new file is a separate dated research artifact, not a replacement for the bundled manifest or startup configuration. It covers no later than October 16. It must not be relabeled with future dates to bypass review. It does not clear historical invalid days, coverage gaps or review flags.

## Read-only checker

`aapl_review_check.py` reads the original AAPL state and the four frozen news-lab accounts. It validates news-lab identity/timing and recorded arithmetic, then calls existing corporate-action reconciliation on in-memory copies using the supplied review. It prints fixed diagnostic reason codes only, with no balances, journal contents or provider error text. Missing accounts cannot produce an all-passed result. It writes no state, manifest, recovery archive or output file and makes no network or order request.

Using an authorized console with this candidate's files available, preferably against a private copied state snapshot:

```bash
python aapl_review_check.py --state-root /path/to/private/copied-paper-state --review research/action_reviews/AAPL_2026-10-16.json --through 2026-10-16
```

The explicit historical target permits retrospective inspection after the coverage interval. If the account has already been accounted through a later date, this earlier review correctly fails coverage; do not roll back the account. A reconciliation pass checks supplied records, not the completeness of all real-world actions. The script does not verify sessions, prices, performance or permit installation. Output stays private unless only a sanitized summary is shared.

## Tests and remaining access blocker

Five new synthetic tests cover all-account copied-state success without any byte changes, missing accounts, private error redaction, corrupted balances, required earlier coverage and rejection of later/future dates. **115 deployment fixtures and 144 research fixtures pass**, run in separate interpreters by scripts/run_test_campaign.py. Source hashes are in TEST_CAMPAIGN_LATEST.json. No private production account was tested; a fixture pass must not be presented as private reconciliation.

The connected Railway capabilities expose platform state and logs but no SSH/exec or mounted-volume file read. The CLI is absent locally. No secret was retrieved to create an alternative connection. Therefore the current `/data/paper_state/us_automatic/action_reviews/AAPL.json`, original account and lab journals remain unavailable for direct inspection. No production state was modified and no deployment was triggered.

The immediately available diagnostic is the existing owner-only Telegram `/audit` command. Its result can establish whether the mounted review is missing, unreadable or failing dated coverage on news-lab copies. It does not export or certify the original AAPL journal; the checker above provides the fuller diagnostic once authorized private copied-state access exists. Next repair depends on those actual reasons. Do not overwrite an existing manifest or reset balances, gaps, invalid-day history or risk controls on the basis of public-source review alone.
