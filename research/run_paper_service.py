"""Dedicated paper-only single-process worker. No credentials or order endpoints."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime,timezone
from prospective_paper import poll_session,save_state

async def run(args):
    folder=Path(args.state_dir);folder.mkdir(parents=True,exist_ok=True)
    lock=folder/'worker.lock'
    # Kernel advisory lock is automatically released on crash/restart.
    import fcntl
    with lock.open('a') as handle:
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise SystemExit('Another paper worker owns this state directory')
        count=0
        while args.cycles==0 or count<args.cycles:
            results=await poll_session(folder)
            count+=1
            record={'mode':'PAPER_ONLY','pid':os.getpid(),'updated_utc':datetime.now(timezone.utc).isoformat(),
                    'cycle':count,'results':results,'any_source_error':any('error' in r for r in results)}
            save_state(folder/'heartbeat.json',record)
            print(json.dumps(record),flush=True)
            if args.cycles==0 or count<args.cycles:await asyncio.sleep(args.interval_seconds)

if __name__=='__main__':
    p=argparse.ArgumentParser(description='Paper-only public-data worker; no broker account access.')
    p.add_argument('--state-dir',default='./paper_state')
    p.add_argument('--interval-seconds',type=int,default=60)
    p.add_argument('--cycles',type=int,default=1,help='0 continues until stopped; default performs one poll')
    args=p.parse_args()
    if args.interval_seconds<30 or args.cycles<0:p.error('Interval must be >=30 seconds; cycles >=0')
    try:asyncio.run(run(args))
    except KeyboardInterrupt:print('Paper worker stopped; persisted checkpoints remain.')
