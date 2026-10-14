"""Install one dated AAPL paper review if absent; never modify account state."""
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from us_accounting import reconcile
from us_paper import account


def install(state_folder, source, observed):
    root = Path(state_folder) / 'us_automatic'
    target = root / 'action_reviews' / 'AAPL.json'
    if target.exists():
        return 'EXISTING_REVIEW_PRESERVED'
    manifest = json.loads(Path(source).read_text())
    day = datetime.fromtimestamp(observed / 1000, ZoneInfo('America/New_York')).date().isoformat()
    if not manifest['coverage_start'] <= day <= manifest['coverage_end']:
        return 'DATED_REVIEW_EXPIRED_OR_NOT_YET_VALID'
    # Validate the review and all available account journals on copies first.
    candidates = [account('AAPL')]
    original = root / 'AAPL_state.json'
    if original.exists():
        candidates.append(json.loads(original.read_text()))
    news = root / 'news_lab' / 'AAPL_news_lab.json'
    if news.exists():
        candidates.extend(json.loads(news.read_text())['accounts'].values())
    for state in candidates:
        reconcile(state, manifest, day, observed)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Atomic exclusive publication; a crash cannot expose partially written JSON.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(manifest, handle, indent=2, allow_nan=False)
            handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
        os.link(temporary, target)
    except FileExistsError:
        return 'EXISTING_REVIEW_PRESERVED'
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return 'DATED_AAPL_REVIEW_INSTALLED_NO_ACCOUNT_WRITES'
