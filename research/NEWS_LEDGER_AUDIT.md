# Read-only AAPL news paper audit

Added 11 October 2026. `/audit` is implemented in the review branch; it is not available in the current production release until deployed.

The authenticated private owner can request a single saved news-lab snapshot audit. It checks the frozen experiment fingerprint and account identities; replays balances from recorded fills and action journals; checks fill timing and paper-only markers; and reports saved mark ages, recorded coverage gaps and invalid comparison dates. Failed accounts remain failed; the command does not repair or rewrite their files.

Replay PASS establishes arithmetic agreement with the recorded journal. It does not independently verify corporate actions, missing fills, complete session observations or profitable strategies. Saved mark ages can be large outside market hours. No quote or provider request is made, and no P/L is derived by this command. Failures return fixed messages without private payload or provider text.

The command reads `us_automatic/news_lab/AAPL_news_lab.json` under the configured paper-state directory. It audits only the four AAPL news-comparison accounts, not the other crypto or US strategy accounts. It retains existing owner/private-chat checks and command deduplication. The new module is explicitly included in the Docker image; root and research copies stay aligned. It does not change the frozen strategy modules or fingerprint inputs.

After deployment, use `/audit` alongside `/news_lab`. A current snapshot still cannot replace an independent ledger export and calendar-based session audit. The first portfolio case study should show both successful arithmetic checks and unresolved evidence gaps, with credentials and Telegram metadata excluded.
