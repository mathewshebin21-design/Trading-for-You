"""Fail closed if Railway persistent volume or credentials are unconfigured."""
import os
from pathlib import Path
import sys

if __name__=='__main__':
    mount=os.environ.get('RAILWAY_VOLUME_MOUNT_PATH','')
    if mount!='/data' or not Path(mount).is_dir():
        raise SystemExit('Configure a Railway persistent volume at /data before starting. No virtual accounts initialized.')
    if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_OWNER_ID','').isdigit():
        raise SystemExit('Configure bot token and numeric owner ID in Railway private variables. No credentials printed.')
    os.umask(0o077)
    state=Path(mount)/'paper_state';state.mkdir(exist_ok=True)
    # Official Python image starts as root; drop privileges after volume preparation.
    if os.geteuid()==0:
        os.chown(state,10001,10001);os.setgid(10001);os.setuid(10001)
    os.environ['PAPER_STATE_DIR']=str(state)
    os.environ.setdefault('PAPER_POLL_SECONDS','300')
    # One dated source-reviewed recovery; no account or historical validity edits.
    from review_install import run
    import time
    try:
        source=os.environ.get('PAPER_ACTION_REVIEW_SOURCE','/app/AAPL_review_2026-10-21.json')
        result=run(state,source,int(time.time()*1000),install=True)
        print('ACTION_REVIEW_BOOTSTRAP',result,flush=True)
    except Exception as error:
        from us_accounting import ReviewRequired
        allowed={'ACTION_COVERAGE_INCOMPLETE','ACTION_REVIEW_MISSING',
                 'ACTION_REVIEW_TIME_INVALID','ACTION_FUTURE_COVERAGE_REJECTED',
                 'ACTION_RECORD_REMOVED','ACTION_LATE_REQUIRES_REPLAY',
                 'LEDGER_BALANCE_MISMATCH','LEDGER_NEGATIVE_BALANCE'}
        reason=str(error) if isinstance(error,ReviewRequired) and str(error) in allowed else 'VALIDATION_FAILED'
        print('ACTION_REVIEW_BOOTSTRAP '+reason+'_NO_REPAIR',flush=True)
    os.execv(sys.executable,[sys.executable,'-u','/app/telegram_paper_bot.py'])
