"""E028: synchronized spot/perpetual trade microstructure — Stage A on sampled days (development only)."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from micro_data import SYMBOLS,sample_days,load_seconds
from spot_micro_data import load_spot_seconds
from micro_screen import forward_returns,stage_a,rolling_sum,STEP,SEED,COSTS

FEATURES=['basis_dev','spot_flow','flow_div'];HORIZONS=[300,1800]

def spot_perp_features(perp,spot):
    """Features at decision seconds t from seconds <= t-1 of both venues."""
    n=86400;t=np.arange(STEP,n,STEP)
    pp=pd.Series(perp.last_price).ffill().to_numpy();sp=pd.Series(spot.last_price).ffill().to_numpy()
    basis=(pp-sp)/sp;bmean=pd.Series(basis).rolling(3600,min_periods=600).mean().to_numpy()
    out=pd.DataFrame(index=t);out['basis_dev']=(basis-bmean)[t-1]
    sflow=rolling_sum((spot.buy_qty-spot.sell_qty).to_numpy(),60);pflow=rolling_sum((perp.buy_qty-perp.sell_qty).to_numpy(),60)
    sabs=pd.Series(np.abs(spot.buy_qty-spot.sell_qty).to_numpy()).rolling(3600,min_periods=600).mean().to_numpy()*60
    pabs=pd.Series(np.abs(perp.buy_qty-perp.sell_qty).to_numpy()).rolling(3600,min_periods=600).mean().to_numpy()*60
    with np.errstate(divide='ignore',invalid='ignore'):
        sn=sflow[t-60]/sabs[t-1];pn=pflow[t-60]/pabs[t-1]
    out['spot_flow']=sn;out['flow_div']=sn-pn
    return out

def build(sym):
    frames=[]
    for day in sample_days():
        perp=load_seconds(sym,day);spot=load_spot_seconds(sym,day)
        if perp is None or spot is None:continue
        f=spot_perp_features(perp,spot);t=f.index.to_numpy()
        for h in HORIZONS:f[f'fwd_{h}']=forward_returns(perp,t,h);f[f'fwd_{h}_lat30']=forward_returns(perp,t+25,h)
        f['day']=day.strftime('%Y-%m-%d');f['month']=day.strftime('%Y-%m');f['hour']=t//3600;frames.append(f.reset_index(drop=True))
    return pd.concat(frames,ignore_index=True)

def main():
    eid='E028_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();results=[];k=0;ncells=len(FEATURES)*len(HORIZONS)*len(SYMBOLS)
    for sym in SYMBOLS:
        F=build(sym);F.to_parquet(out/f'{sym}_features.parquet',index=False);print(sym,'rows',len(F),'days',F.day.nunique(),flush=True)
        days=F.day.to_numpy();months=F.month.to_numpy();hours=F.hour.to_numpy()
        for name in FEATURES:
            for h in HORIZONS:
                r=stage_a(F[name].to_numpy(float),F[f'fwd_{h}'].to_numpy(float),days,months,hours,SEED+120+k,ncells);k+=1
                results.append(dict(symbol=sym,feature=name,horizon_s=h,**r))
                print(sym,name,h,'IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'stat',r['passes_statistical'],'edge bps',round(r['extreme_decile_edge_bps'],2),'econ',r['passes_economic'],flush=True)
    survivors=[dict(symbol=r['symbol'],feature=r['feature'],horizon_s=r['horizon_s'],direction=r['direction']) for r in results if r['passes_economic']]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED+120,new_hypotheses=2*ncells,cumulative_hypotheses=293+2*ncells,costs_per_side=COSTS,
        stage_a=results,stage_a_survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
