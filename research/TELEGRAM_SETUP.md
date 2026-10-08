# Telegram paper-trading control panel

Research/simulation only. No real money, broker credentials or live order endpoint. Strategy profitability remains unproven. Code and offline tests are complete; Telegram delivery, credentials and continuous hosting are NOT activated or verified.

## Connect your bot
1. In Telegram, use the official verified @BotFather to create a dedicated bot with `/newbot`. Keep its token private.
2. On your chosen Linux cloud host, put `TELEGRAM_BOT_TOKEN` into its secret settings or a root-readable environment file. Do not paste it into ChatGPT, commit it or include it in screenshots.
3. Install the supplied Python files and `requirements-paper.txt` into an isolated Python 3.12 environment. Set the token in that environment, then run `python identify_telegram_owner.py`. It prints a random pairing command: send it to your bot in a private chat within five minutes. The helper prints your numeric user ID locally. Store that as `TELEGRAM_OWNER_ID`. Stop the helper before starting the service.
4. Configure a persistent `PAPER_STATE_DIR` and `PAPER_POLL_SECONDS=60`. Start `python telegram_paper_bot.py`. Send `/start` in your private bot chat to enable notifications. Unknown users and groups receive no replies or command access.
5. Verify `/status`, `/trends` and `/report`; then preview `/paper_trade BUY BTCUSDT`. If you want the simulated trade, send the `/confirm CODE` returned by the bot within 60 seconds. No confirmation means no manual fill.

Telegram Bot API reference: https://core.telegram.org/bots/api
Bot creation reference: https://core.telegram.org/bots/tutorial#obtain-your-bot-token

## Commands
| Command | Behavior |
|---|---|
| `/start`, `/help` | Instructions; `/start` enables notifications |
| `/status`, `/positions`, `/report` | Virtual balances, holdings, modeled P/L, quote age, costs and collector timestamp |
| `/trends` | Automatic daily SMA20/SMA100 signal and observation time; no fresh price fetch implied |
| `/trades` | Last five simulated fills per account |
| `/pause` | Block new entries; allow existing risk checks and strategy exits; does not liquidate holdings |
| `/resume` | Permit entries; never clear a permanent account drawdown pause |
| `/paper_trade BUY BTCUSDT` | Preview a manual paper entry, up to 25% of account equity |
| `/paper_trade SELL BTCUSDT` | Preview a manual paper exit, bounded by displayed liquidity |
| `/confirm CODE` | Consume the preview once and attempt simulation on fresh validated data |
| `/cancel` | Cancel all pending manual previews |

ETHUSDT is also supported. No other symbols or live mode exist. Each symbol has separate automatic and manual 10,000 USDT accounts, so four virtual accounts may exist. Manual activity cannot change the frozen automatic research ledger. New automatic accounts may enter as soon as the service starts if the signal/risk rules allow, even before `/start`; `/start` enables Telegram notifications, not trading. Gold, stocks, news signals and trader copying are not implemented here.

## Notifications and failure behavior
The worker sends simulated fills, new data-source errors, drawdown-pause alerts and a daily snapshot at the first successful collection of each Asia/Kolkata calendar day. This is not a fixed-time scheduled daily report. Reports show last-observed quotes, their age and STALE status; displayed unrealized P/L is indicative and excludes future liquidation costs. Fees/slippage are modeled assumptions.

Commands older than two minutes are ignored. Duplicate update IDs and already-consumed confirmation codes cannot re-execute. Accepted updates/codes are durably consumed before possible fills: after a crash, an interrupted command is not retried. Check `/trades` and local audit records before requesting a new preview. A fill/state save and Telegram update are not one transactional database operation; the design deliberately favors a missed command over a duplicate fill. Notifications use a durable outbox; a crash after sending but before acknowledgment can duplicate a notification, never a trade because of that notification.

Only one worker may own a state directory. Do not run the older paper service against this directory. JSON account saves are atomic but full multi-process/transactional production hardening remains future work. Preserve backups; account resets are not valid forward testing. Partial exits or untradeable dust may remain; `/pause` is not guaranteed immediate liquidation. Quote-based risk checks run only when data is valid and the worker is running. A 10% drawdown trigger does not guarantee a 10% maximum loss.

## Linux restart service
The supplied `deploy/paper-telegram.service` is a template, not an installed service. Install code under `/opt/paperbot`, create an unprivileged `paperbot` user/group, create `/var/lib/paperbot` owned by it, and create the virtual environment under `/opt/paperbot/.venv`. Place populated configuration at `/etc/paperbot/telegram.env`, owned by root with mode 0600. Install the template under `/etc/systemd/system/paper-telegram.service`, then use `systemctl daemon-reload` and `systemctl enable --now paper-telegram`. Verify service status, heartbeat and Telegram replies. Host provisioning/payment remain user-controlled and have not been performed.

The service restarts on failure but repeated startup failures eventually stop. A host outage cannot be reported by a bot running on that host: independent external heartbeat monitoring is still required. Back up state/SQLite consistently; archive retention and source-request rate planning are needed before long unattended runs. The bot uses Telegram long polling and requires outbound HTTPS/WebSocket access, not a public inbound webhook. It refuses an existing webhook rather than removing it.

## Tests
Run `python -m unittest discover -s . -p 'test*.py'`. Tests cover private-user authorization, group rejection, stale commands, duplicate/restarted updates, expired/cancelled/consumed confirmations, manual isolation, pauses, persistent fills, outbox retry and token redaction. Telegram delivery and real credentials cannot be tested until connected. No external messages were sent during development.
