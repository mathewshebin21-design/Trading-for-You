# Railway paper bot deployment candidate

Prepared code only. No Railway account allowance has been inspected; nothing deployed. Do not enable a paid subscription, buy credits, add billable add-ons, or use this bundle until the account shows an active Free/Trial allowance and the chosen service/volume can operate within it. A connector connection does not establish billing entitlement. No guaranteed monthly free operation.

Deploy the contents of this directory as one Docker-based background worker. No web domain, inbound port, public dashboard or webhook is required. Do not run replicas; use one worker and a persistent volume mounted at `/data`. The startup script refuses to initialize accounts without Railway volume metadata. The runtime drops root privileges after preparing its own state directory.

Required private variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_ID`. Never paste actual values into source code. Set `PAPER_POLL_SECONDS=300` initially to reduce collection frequency and source-archive growth. This checks risk approximately every five minutes when data succeeds; it is not a continuous quote-level risk limit. Confirm public Binance HTTP/WebSocket access actually succeeds from the selected Railway region.

The token holder must pair their private Telegram ID using identify_telegram_owner.py before activation, or supply an already-verified numeric private user ID. The helper needs only TELEGRAM_BOT_TOKEN; running it does not simulate trades. Once paired, start the service and send `/start`, `/status`, `/trends`, `/report`. Test one confirmed manual paper trade and check its account ledger, then restart and verify it is preserved with no duplicate entry. Monitor service memory/CPU/egress/storage usage and remaining allowance before leaving it running.

This service uses separate automatic and manual virtual accounts. Starting it may simulate an automatic entry if frozen rules allow. Existing Colab accounts are NOT automatically migrated: either intentionally start a new labeled forward session or restore the correct state files explicitly without changing capital/history. No account-reset masking of losses.

Runtime archives and ledgers grow; a small free volume is not indefinite storage. Maintain backups, check usage and stop collection before exhausting volume/free credits. Logs contain sanitized service errors; Telegram token is never logged intentionally. Provider/platform log and secret settings must still be checked during actual deployment. No external paper broker, live orders or paid services are included.

Documentation consulted: https://docs.railway.com/builds/dockerfiles and https://docs.railway.com/volumes . Docker image build, live Railway networking, Telegram delivery, current balance and cloud restarts remain unverified until platform access is available. Local command/accounting tests passed.
