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
    os.execv(sys.executable,[sys.executable,'-u','/app/telegram_paper_bot.py'])
