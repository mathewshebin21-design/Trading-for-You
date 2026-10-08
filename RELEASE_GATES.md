# Paper bot delivery and evidence gates

Implemented 9 October 2026 (IST). This is not a profitability certification or a
commercial launch. No real orders, live order credentials or paid services.

Validation: 91 research unit tests and 70 deployment unit tests pass. Tests cover
corporate-action idempotence, dividend eligibility after sale, balance corruption,
partial/exact fill handling, post-decision quotes, restart deduplication, cost
stress, permanent risk pause, snapshot restore and retention. These are fixture
tests, not proof of production performance.

## Accounting

US balances are replayed from recorded fills before each collector cycle.
Reviewed ordinary whole-share splits and ordinary cash dividends are supported.
Dividend entitlement is recorded on ex-date, included as a receivable in equity,
and paid once on payable date even if the shares have subsequently been sold.
Split handling invalidates old-price quotes; total cost basis remains unchanged.
Unsupported actions, fractional cash-in-lieu, revised/deleted/late records, and
multiple same-day actions require a reviewed replay rather than automatic repair.
Changes are applied on copies and saved atomically with the existing state writer.

Accounting requires a privately stored, independently reviewed manifest for each
symbol at `/data/paper_state/us_automatic/action_reviews/SYMBOL.json`.
No manifests are prefilled or inferred from an empty API response. The existing
overnight safeguard remains active until reviewed coverage is supplied. Alpaca
warns that its action feed can be delayed:
https://docs.alpaca.markets/us/reference/corporateactions-1

Required manifest schema (values below are schema descriptions, NOT real data):

```text
symbol: SPY | AAPL | GLD
currency: USD
reviewed: true
reviewer: identity of the reviewer
reviewed_ms: actual review receipt time, epoch milliseconds
source_urls: nonempty HTTPS references to authoritative evidence
coverage_start / coverage_end: inclusive New York dates
actions: complete list of reviewed records, including already applied records
  split: id, type="split", ex_date, ratio=new_shares/old_shares
  cash dividend: id, type="cash_dividend", ex_date, pay_date, cash_per_share
```

Coverage cannot extend beyond the New York date of review. Do not alter a manifest
to clear an error without completing its underlying review. Special distributions,
due-bill arrangements, reorganizations and ambiguous dates are outside automatic
accounting support. No claim of fully automatic corporate-action coverage is made.

## Prospective US experiment

On deployment, the lab starts from the first newly received valid observation,
not from the old bot's fill history. Ten independent accounts per symbol compare
SMA20/100, close breakout55/20, mean reversion20, 25% buy-and-hold and zero-interest
cash, each at base and doubled costs. They consume the original collector's SAME
validated quotes without additional market-data requests. First decisions wait for
a subsequent qualifying source event. Quotes are deduplicated across restarts.
Global pause blocks shadow entries; permanent strategy risk pauses still permit
exits. Whole shares, displayed-size caps, fees and slippage apply. Doubled costs
also double the observed half-spread. Accounts are hypothetical alternatives and
must not be summed into one portfolio or treated as sharing available liquidity.

`/lab` provides separate USD results and matched benchmark excess dollars. Reports
are split into Telegram messages to avoid silent truncation. Partial exits count
as a completed roundtrip only once flat. Roundtrip trade P/L explicitly excludes
distributions; account equity/net P/L includes reconciled dividends. Daily marks
are LAST OBSERVED marks, not official closing prices. The code/rules fingerprint,
start timestamp, latest input and fill decision times are stored privately.
Changing the lab code requires a new experiment, not silently rewriting old rules.

## Recovery and operations

One private snapshot per UTC date includes an SQLite-consistent bot database and
account/lab/review files. Keep only three archives. Limits: 20 MB state input plus
20 MB database, before compression. Failed snapshots are recorded in
`backup_health.json` without provider/credential text. Snapshots are on the SAME
volume: they do not protect against Railway account/volume deletion or credit
expiry. Do not publish snapshots: the database contains private Telegram metadata.

Recovery procedure: pause/stop the worker, copy the volume for inspection, restore
one known-good snapshot into a separate directory, verify SQLite integrity and
replay all account ledgers, then intentionally restore while retaining newer audit
records. Never run two collectors against the same account files. Automated
rollback and off-volume backup are not enabled. Fixture restore tests establish
format consistency, not a production disaster-recovery drill.

## Release decisions

| Stage | Status / remaining evidence |
|---|---|
| 1 Accounting | Code and fixture tests implemented; real issuer review/coverage pending |
| 2 Prospective comparisons | Runtime integration implemented; start only after deployment; overnight reviews required |
| 3 Evaluate edge | Pending future observations; 90 days and 30 natural roundtrips are screening minima, never proof |
| 4 Reliable operations | Quote counters, atomic state, deduplication and local snapshots implemented; production recovery drill and multi-session soak pending |
| 5 Telegram commercial product | Deferred: customer isolation, subscriptions, support and market-data permissions not qualified |

No account becomes validated automatically. After sufficient observations, require
an independent review of data completeness, matched marks, net excess returns,
drawdown, cost stress and uncertainty. Select no winner from previously inspected
history. Missing observations or blocked accounting invalidate affected comparisons.
News and trader feeds stay disabled until complete attributable timestamped data
and authorized access exist. Multi-customer sales are not enabled. Paper results
cannot establish live execution profitability.
