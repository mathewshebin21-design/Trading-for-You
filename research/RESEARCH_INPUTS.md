# Attributed research inbox

Implemented 9 October 2026. Offline input validation and private storage only;
news fetching, fact verification, sentiment and copying traders are not enabled.
No deployment change, API credential or paid service is required.

The Vibe news tool supplies public-search headlines; that does not establish
issuer verification or historical point-in-time availability. Fincept's bundled
GNews script strips timezone information from publication strings. We therefore
do not import either output directly or guess missing timezones. This module is
original project code, not copied AGPL code.

Each JSON record must have exactly these fields:
`kind` (news/analysis/trader_claim), `source_url` (canonical HTTPS public URL
without credentials, query or fragment), `publisher`, `published_at` (ISO timestamp
with explicit timezone), `symbols` (supported bot symbols), `summary` (locally
authored, maximum 1,000 characters), `tool`, and `tool_revision`.
Link presence is attribution, not proof that the source or claim was verified.
Do not paste full articles, API secrets or private trader/account information.

`python research_inputs.py --db /private/path/research.sqlite --import-json /private/path/record.json`
validates one record and displays the inbox. Omit `--import-json` to display it.
Keep the database and imported files private; do not upload them to GitHub.

Receipt time is assigned by our clock, not supplied by the source. Duplicate
content retains its original receipt time. Changed content creates a separate
record with a new receipt time. Historical queries exclude records not yet
received. This models our knowledge availability; it does not prove the provider
has complete archival coverage. Staleness is evaluated when reporting, with a
24-hour default publication-age threshold that is an operational label only.

Every output says `ATTRIBUTED_NOT_VERIFIED` and `execution_eligible: false`.
The trading worker does not import this module. Before news can affect even a
paper strategy, require approved feed access, fact checks, frozen symbol/entity
mapping and a prospective hypothesis with matched benchmarks and realistic costs.
Trader performance claims additionally need complete independently attributable
records, fees, drawdowns, leverage and timestamped availability; identity badges
or promotional screenshots do not meet that requirement.
