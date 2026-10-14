# Read-only action review diagnostic

Extends owner-only /audit to inspect the existing us_automatic/action_reviews/AAPL.json file. Reports missing, unreadable, oversized or invalid review data. Runs the existing accounting reconcile function on account copies through the current New York date, returning fixed reason codes or DRY_RUN_PASS. Reads no credentials and writes no balances, flags, manifests or invalid-day history. A dry-run pass is not independent source verification or permission to erase invalid days.

106 deployment and 144 candidate research fixture tests pass in separate interpreters. Tests cover missing/corrupt/oversized files, redaction, insufficient coverage, successful dry runs and unchanged state/file bytes. Counts overlap. Requires deployment before the Telegram command includes this diagnostic. Current production file contents are still unknown; no manifest is fabricated and no trading control is bypassed.
