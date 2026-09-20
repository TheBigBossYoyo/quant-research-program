"""E026: horizon extension (2h, 4h) of the depth-imbalance and liquidity-normalised-flow cells. Development sampled days only."""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from micro_data import SYMBOLS,sample_days,load_seconds
from micro_screen import forward_returns,stage_a,SEED,COSTS

FEATURES=['depth_imb','flow_rel'];HORIZONS=[7200,14400]

def main():
    source=ROOT/sys.argv[1];eid='E026_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();results=[];k=0;ncells=len(FEATURES)*len(HORIZONS)*len(SYMBOLS)
    for sym in SYMBOLS:
        F=pd.read_parquet(source/f'{sym}_features.parquet');parts=[]
        for day in sample_days():
            sec=load_seconds(sym,day)
            if sec is None:continue
            sub=F[F.day==day.strftime('%Y-%m-%d')].copy();t=(np.arange(len(sub))+1)*60
            for h in HORIZONS:sub[f'fwd_{h}']=forward_returns(sec,t,h)
            parts.append(sub)
        G=pd.concat(parts,ignore_index=True);G.to_parquet(out/f'{sym}_features.parquet',index=False)
        days=G.day.to_numpy();months=G.month.to_numpy();hours=G.hour.to_numpy()
        for name in FEATURES:
            for h in HORIZONS:
                r=stage_a(G[name].to_numpy(float),G[f'fwd_{h}'].to_numpy(float),days,months,hours,SEED+50+k,ncells);k+=1
                results.append(dict(symbol=sym,feature=name,horizon_s=h,**r))
                print(sym,name,h,'IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'stat',r['passes_statistical'],'edge bps',round(r['extreme_decile_edge_bps'],2),'econ',r['passes_economic'],'n',r['n'],flush=True)
    survivors=[dict(symbol=r['symbol'],feature=r['feature'],horizon_s=r['horizon_s'],direction=r['direction']) for r in results if r['passes_economic']]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED+50,source=str(source.relative_to(ROOT)),new_hypotheses=2*ncells,cumulative_hypotheses=275+2*ncells,
        costs_per_side=COSTS,stage_a=results,stage_a_survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
