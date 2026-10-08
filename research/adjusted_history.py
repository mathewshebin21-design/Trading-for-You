"""Adjusted proxy data: repair only float rounding, retaining raw source archive."""
import csv
from pathlib import Path
from paper_engine import load_history


def load_adjusted_history(path,crypto=False):
    path=Path(path)
    with path.open(newline='') as f:records=list(csv.DictReader(f));fields=records[0].keys()
    corrections=[]
    for r in records:
        o,h,l,c=[float(r[k]) for k in ('Open','High','Low','Close')]
        tol=1e-12*max(abs(o),abs(h),abs(l),abs(c),1)
        if max(o,c)>h and max(o,c)-h<=tol:
            corrections.append({'date':r['Date'],'field':'High','original':h,'normalized':max(o,c)})
            r['High']=str(max(o,c))
        if min(o,c)<l and l-min(o,c)<=tol:
            corrections.append({'date':r['Date'],'field':'Low','original':l,'normalized':min(o,c)})
            r['Low']=str(min(o,c))
    normalized=path.with_name(path.stem+'_normalized.csv')
    with normalized.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(records)
    return load_history(normalized,crypto=crypto),corrections
