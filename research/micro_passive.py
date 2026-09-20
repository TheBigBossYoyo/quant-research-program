"""E027: passive capture of the depth-imbalance drift with a conservative trade-through fill rule.

A limit order at the last trade price on the predicted side is filled only if a later trade prints
through it by at least `ticks` ticks within the waiting window (queue position unknown, so any fill
requires the price to move against the order first). Unfilled orders are cancelled free.
"""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty
from micro_data import SYMBOLS,sample_days,load_seconds
from micro_ledger import thresholds_previous_day,performance
from micro_screen import COSTS,LATENCY,SEED

TICK={'BTCUSDT':.1,'ETHUSDT':.01};MAKER=.0002;WAIT=300;HOLD=1800;FEATURE='depth_imb'

def passive_fills(sec,t,side,wait=WAIT,ticks=1,latency=LATENCY,tick=.1):
    """Return (filled, fill_second, limit_price) for orders placed at t+latency at the last trade price."""
    last=pd.Series(sec.last_price).ffill().to_numpy();lo=sec.low_price.to_numpy();hi=sec.high_price.to_numpy()
    n=len(last);filled=np.zeros(len(t),bool);fsec=np.full(len(t),-1);limit=np.full(len(t),np.nan)
    for k,(s,sd) in enumerate(zip(t,side)):
        p0=s+latency
        if p0>=n or sd==0:continue
        L=last[p0-1] if p0>0 else np.nan
        if not np.isfinite(L):continue
        limit[k]=L;end=min(n,p0+wait)
        if sd>0:
            hit=np.flatnonzero(lo[p0:end]<=L-ticks*tick)
        else:
            hit=np.flatnonzero(hi[p0:end]>=L+ticks*tick)
        if len(hit):filled[k]=True;fsec[k]=p0+hit[0]
    return filled,fsec,limit

def exit_price(sec,fill_sec,hold):
    first=pd.Series(sec.first_price).bfill().to_numpy();x=fill_sec+hold
    return np.where(x<len(first),first[np.clip(x,0,len(first)-1)],np.nan)

def run(sym,F,direction,cost,wait=WAIT,ticks=1,latency=LATENCY,hold=HOLD,maker=MAKER,noise=0.,seed=0):
    rng=np.random.default_rng(seed);lo_q,hi_q=thresholds_previous_day(F,FEATURE);x=F[FEATURE].to_numpy(float)
    if noise:x=x+rng.normal(0,noise*np.nanstd(x),len(x))
    sig=np.where(x>=hi_q.to_numpy(),1,np.where(x<=lo_q.to_numpy(),-1,0))*direction
    rows=[];attempts=0
    for day in sample_days():
        ds=day.strftime('%Y-%m-%d');idx=np.flatnonzero(F.day.to_numpy()==ds)
        if not len(idx):continue
        sec=load_seconds(sym,day);t=(np.arange(len(idx))+1)*60;side=sig[idx]
        active=side!=0;attempts+=int(active.sum())
        filled,fsec,limit=passive_fills(sec,t,side,wait,ticks,latency,TICK[sym]);busy=-1
        for k in np.flatnonzero(filled):
            if t[k]<busy:continue
            xp=exit_price(sec,np.array([fsec[k]]),hold)[0]
            if not np.isfinite(xp):continue
            r=side[k]*(xp/limit[k]-1)-maker-cost;rows.append(dict(day=ds,side=int(side[k]),fill_delay=int(fsec[k]-t[k]),ret=r));busy=fsec[k]+hold
    trades=pd.DataFrame(rows);days=sorted(set(F.day));daily=(trades.groupby('day').ret.sum() if len(trades) else pd.Series(dtype=float)).reindex(days).fillna(0.)
    p=performance(trades,daily);p['attempts']=attempts;p['fill_rate']=float(len(trades)/attempts) if attempts else 0.
    return trades,daily,p

def main():
    source=ROOT/sys.argv[1];eid='E027_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();trials=293;results=[]
    for j,sym in enumerate(SYMBOLS):
        F=pd.read_parquet(source/f'{sym}_features.parquet');d=1  # E024: positive IC (cushion side continues)
        cases={}
        for case,cost in COSTS.items():
            tr,dl,p=run(sym,F,d,cost);u={str(b):uncertainty(dl.to_numpy(),np.zeros(len(dl)),SEED+80+j,trials=trials,samples=10000,block=b) for b in [1,5,20]}
            cases[case]=dict(metrics=p,uncertainty=u,gate=bool(p['net_return']>0 and p['positive_month_share']>=.6 and u['5']['mean_daily_ci95'][0]>0),passes_adjusted=all(a['simultaneous_lower_mean_daily']>0 for a in u.values()))
            tr.to_csv(out/f'{sym}_{case}_trades.csv',index=False);print(sym,case,{k:(round(v,4) if isinstance(v,float) else v) for k,v in p.items()},flush=True)
        st=COSTS['stress'];hostile=dict(wait_60s=run(sym,F,d,st,wait=60)[2],two_ticks=run(sym,F,d,st,ticks=2)[2],fee_plus_2bps=run(sym,F,d,st+.0002)[2],latency_30s=run(sym,F,d,st,latency=30)[2],noise_10pct=run(sym,F,d,st,noise=.1,seed=3)[2])
        obs=cases['stress']['metrics']['net_return'];pl=[]
        rng=np.random.default_rng(SEED+950+j);G=F.copy()
        for k in range(200):
            G[FEATURE]=F.groupby('day')[FEATURE].transform(lambda s:rng.permutation(s.to_numpy()));pl.append(run(sym,G,d,st)[2]['net_return'])
            if k%50==0:print(sym,'placebo',k,round(pl[-1],4),flush=True)
        pl=np.array(pl);hostile['placebo']=dict(runs=200,fraction_at_or_above_observed=float(np.mean(pl>=obs)),quantiles=np.quantile(pl,[.5,.95,.99]).tolist())
        fill_dependent=cases['stress']['metrics']['fill_rate']>.5
        verdict='RESEARCH-PROMISING (development only)' if cases['stress']['gate'] and cases['stress']['passes_adjusted'] and hostile['placebo']['fraction_at_or_above_observed']<.05 and hostile['fee_plus_2bps']['net_return']>0 and not fill_dependent else 'REJECTED FOR PROMOTION'
        results.append(dict(symbol=sym,direction=d,cases=cases,hostile=hostile,fill_dependent=bool(fill_dependent),verdict=verdict));print(sym,verdict,flush=True)
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED+80,source=str(source.relative_to(ROOT)),new_hypotheses=2,cumulative_hypotheses=trials,
        fill_model='trade-through by >=1 tick within 300 s; maker 2 bps entry; taker exit',results=results,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out)

if __name__=='__main__':main()
