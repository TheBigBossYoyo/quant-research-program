"""E030: optimistic touch-fill upper bound for passive capture (front-of-queue assumption; not executable)."""
import json,sys
from datetime import datetime,timezone
import pandas as pd
from core import ROOT,code_hash
from micro_data import SYMBOLS
from micro_passive import run
from micro_screen import COSTS

def main():
    source=ROOT/sys.argv[1];eid='E030_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[]
    for sym in SYMBOLS:
        F=pd.read_parquet(source/f'{sym}_features.parquet');cases={}
        for case,cost in COSTS.items():
            tr,dl,p=run(sym,F,1,cost,ticks=0);cases[case]=p;tr.to_csv(out/f'{sym}_{case}_trades.csv',index=False)
            print(sym,case,{k:(round(v,4) if isinstance(v,float) else v) for k,v in p.items()},flush=True)
        closed=cases['stress']['net_return']<=0
        results.append(dict(symbol=sym,cases=cases,verdict='PASSIVE ROUTE CLOSED (optimistic bound non-positive)' if closed else 'UNRESOLVED WITHOUT QUEUE DATA; REJECTED FOR PROMOTION'))
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,source=str(source.relative_to(ROOT)),new_hypotheses=2,cumulative_hypotheses=343,fill_model='touch (zero ticks through) within 300 s; front-of-queue upper bound',results=results,validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,[r['verdict'] for r in results])

if __name__=='__main__':main()
