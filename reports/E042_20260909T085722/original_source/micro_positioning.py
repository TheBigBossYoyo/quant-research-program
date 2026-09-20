"""E029: positioning ratios from the 5-minute metrics feed at 15/60-minute horizons. Development sampled days only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from micro_data import SYMBOLS,METRICS_END,sample_days,load_seconds,load_metrics
from micro_screen import forward_returns,stage_a,STEP,SEED,COSTS

FEATURES=['top_pos_shift','retail_crowd','taker_ratio'];HORIZONS=[900,3600]

def positioning_features(metrics,day,n=86400):
    """Features at decision seconds t from metrics rows with create_time <= t (5-minute rows)."""
    t=np.arange(STEP,n,STEP);mts=((metrics.index-pd.Timestamp(day)).total_seconds()).to_numpy()
    top=metrics.sum_toptrader_long_short_ratio.to_numpy(float);glob=metrics.count_long_short_ratio.to_numpy(float);tk=metrics.sum_taker_long_short_vol_ratio.to_numpy(float)
    pos=np.searchsorted(mts,t,side='right')-1;ok=pos>=0;p=np.clip(pos,0,None)
    def lag(arr,k):
        q=p-k;return np.where(ok&(q>=0),arr[np.clip(q,0,None)],np.nan)
    out=pd.DataFrame(index=t)
    out['top_pos_shift']=np.where(ok,top[p],np.nan)/lag(top,3)-1
    g24=pd.Series(glob).rolling(288,min_periods=96).mean().to_numpy();out['retail_crowd']=np.where(ok,glob[p],np.nan)-np.where(ok,g24[p],np.nan)
    tk15=pd.Series(tk).rolling(3,min_periods=3).mean().to_numpy();out['taker_ratio']=np.where(ok,tk15[p],np.nan)
    return out

def build(sym):
    frames=[]
    for day in sample_days():
        if day>METRICS_END:continue
        sec=load_seconds(sym,day);m=load_metrics(sym,day)
        if sec is None or m is None:continue
        f=positioning_features(m,day);t=f.index.to_numpy()
        for h in HORIZONS:f[f'fwd_{h}']=forward_returns(sec,t,h);f[f'fwd_{h}_lat30']=forward_returns(sec,t+25,h)
        f['day']=day.strftime('%Y-%m-%d');f['month']=day.strftime('%Y-%m');f['hour']=t//3600;frames.append(f.reset_index(drop=True))
    return pd.concat(frames,ignore_index=True)

def main():
    eid='E029_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();results=[];k=0;ncells=len(FEATURES)*len(HORIZONS)*len(SYMBOLS)
    for sym in SYMBOLS:
        F=build(sym);F.to_parquet(out/f'{sym}_features.parquet',index=False);print(sym,'rows',len(F),'days',F.day.nunique(),flush=True)
        days=F.day.to_numpy();months=F.month.to_numpy();hours=F.hour.to_numpy()
        for name in FEATURES:
            for h in HORIZONS:
                r=stage_a(F[name].to_numpy(float),F[f'fwd_{h}'].to_numpy(float),days,months,hours,SEED+160+k,ncells);k+=1
                results.append(dict(symbol=sym,feature=name,horizon_s=h,**r))
                print(sym,name,h,'IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'stat',r['passes_statistical'],'edge bps',round(r['extreme_decile_edge_bps'],2),'econ',r['passes_economic'],flush=True)
    survivors=[dict(symbol=r['symbol'],feature=r['feature'],horizon_s=r['horizon_s'],direction=r['direction']) for r in results if r['passes_economic']]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED+160,new_hypotheses=2*ncells,cumulative_hypotheses=317+2*ncells,costs_per_side=COSTS,
        stage_a=results,stage_a_survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
