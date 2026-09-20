"""E031: implied-volatility (BVOL) information — minute-framework IV shocks on sampled days and daily-framework
variance-risk-premium / IV-level cells on all days. Development 2023-06-20..2024-12-31 only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from core import ROOT,code_hash
from micro_data import SYMBOLS,sample_days,load_seconds
from vol_data import load_bvol,START as VOL_START,END as VOL_END
from micro_screen import forward_returns,stage_a,block_bootstrap_ic,STEP,SEED,COSTS
from universe import load_klines

MINUTE_H=[1800,7200];DAILY_H=[1,7];DAILY_ROUND_TRIP_BPS=2*.0007*1e4  # stress perpetual round trip 14 bps

def bvol_series(sym,days):
    parts=[]
    for d in days:
        b=load_bvol(sym,d)
        if b is None:continue
        idx=pd.Timestamp(d)+pd.to_timedelta(b.minute,unit='m');parts.append(pd.Series(b.bvol_close.to_numpy(),index=idx))
    return pd.concat(parts).sort_index()

def iv_shock_features(bv_all,day,n=86400):
    """At decision seconds t: 15-minute BVOL change (minute closes at or before t) scaled by the trailing 24-hour std of 15-minute changes."""
    t=np.arange(STEP,n,STEP);start=pd.Timestamp(day)-pd.Timedelta(days=1);w=bv_all.loc[start:pd.Timestamp(day)+pd.Timedelta(days=1)]
    w=w[~w.index.duplicated()];full=pd.date_range(start,pd.Timestamp(day)+pd.Timedelta(days=1),freq='min',inclusive='left');w=w.reindex(full)
    ch=w-w.shift(15);sd=ch.rolling(1440,min_periods=720).std()
    z=(ch/sd);sec_index=(pd.Timestamp(day)+pd.to_timedelta(t,unit='s'));minute_floor=sec_index.floor('min')-pd.Timedelta(minutes=1)  # last completed minute before t
    return pd.Series(z.reindex(minute_floor).to_numpy(),index=t)

def daily_features(sym,bv_all,close):
    """Daily rows at 00:00 UTC of day d: BVOL at 00:00 (first minute close), realised vol over the previous 30 daily closes (excluding d), IV percentile over the trailing 90 days."""
    bv0=bv_all[bv_all.index.strftime('%H:%M')=='00:00'];bv0.index=bv0.index.normalize()
    lr=np.log(close/close.shift(1));rv=lr.rolling(30).std().shift(1)*np.sqrt(365)*100  # percentage points, excludes current day
    df=pd.DataFrame(dict(iv=bv0)).join(rv.rename('rv'),how='left');df['vrp']=df.iv-df.rv
    df['iv_pct']=df.iv.rolling(90,min_periods=60).apply(lambda x:(x[:-1]<x[-1]).mean() if len(x)>1 else np.nan,raw=True)
    return df

def daily_stage(feature,fwd,seed,cells):
    x=feature.to_numpy(float);y=fwd.to_numpy(float);ok=np.isfinite(x)&np.isfinite(y);x,y=x[ok],y[ok];days=np.arange(len(x))//7  # 7-day blocks
    boot=block_bootstrap_ic(x,y,days,2000,seed,cells);passes=boot['ci_lower_adjusted']>0 or boot['ci_upper_adjusted']<0
    q=pd.qcut(pd.Series(x),5,labels=False,duplicates='drop');m=pd.Series(y).groupby(q.to_numpy()).mean()*1e4;edge=(float(m.iloc[-1])-float(m.iloc[0]))/2*np.sign(boot['ic'])
    return dict(**boot,passes_statistical=bool(passes),direction=int(np.sign(boot['ic'])) if passes else 0,quintile_means_bps=m.round(2).tolist(),extreme_quintile_edge_bps=float(edge),passes_economic=bool(passes and edge>=DAILY_ROUND_TRIP_BPS))

def main():
    eid='E031_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[];k=0;ncells=12
    panels,_=load_klines();all_days=pd.date_range(VOL_START,VOL_END,freq='D')
    for col in ('close','open'):panels[col]=panels[col].tz_localize(None)  # daily panel is UTC-aware; volatility dates are naive UTC
    for sym in SYMBOLS:
        bv=bvol_series(sym,all_days);print(sym,'bvol minutes',len(bv),flush=True)
        frames=[]
        for day in sample_days():
            if day<VOL_START+pd.Timedelta(days=1):continue
            sec=load_seconds(sym,day)
            if sec is None:continue
            f=pd.DataFrame(dict(iv_shock=iv_shock_features(bv,day)));t=f.index.to_numpy()
            for h in MINUTE_H:f[f'fwd_{h}']=forward_returns(sec,t,h);f[f'fwd_{h}_lat30']=forward_returns(sec,t+25,h)
            f['day']=day.strftime('%Y-%m-%d');f['month']=day.strftime('%Y-%m');f['hour']=t//3600;frames.append(f.reset_index(drop=True))
        F=pd.concat(frames,ignore_index=True);F.to_parquet(out/f'{sym}_minute_features.parquet',index=False)
        for h in MINUTE_H:
            r=stage_a(F.iv_shock.to_numpy(float),F[f'fwd_{h}'].to_numpy(float),F.day.to_numpy(),F.month.to_numpy(),F.hour.to_numpy(),SEED+200+k,ncells);k+=1
            results.append(dict(symbol=sym,feature='iv_shock',horizon='%ds'%h,**r));print(sym,'iv_shock',h,'IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'edge bps',round(r['extreme_decile_edge_bps'],2),'econ',r['passes_economic'],flush=True)
        close=panels['close'][sym].loc[VOL_START-pd.Timedelta(days=40):VOL_END];open_=panels['open'][sym]
        D=daily_features(sym,bv,close);D=D.loc[VOL_START:VOL_END]
        for h in DAILY_H:D[f'fwd_{h}d']=(open_.shift(-1-h)/open_.shift(-1)-1).reindex(D.index)  # next-day open to open h days later
        D.to_csv(out/f'{sym}_daily_features.csv')
        for name in ['vrp','iv_pct']:
            for h in DAILY_H:
                r=daily_stage(D[name],D[f'fwd_{h}d'],SEED+220+k,ncells);k+=1
                results.append(dict(symbol=sym,feature=name,horizon='%dd'%h,**r));print(sym,name,h,'d IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'edge bps',round(r['extreme_quintile_edge_bps'],2),'econ',r['passes_economic'],'n',r['n'],flush=True)
    survivors=[dict(symbol=r['symbol'],feature=r['feature'],horizon=r['horizon'],direction=r['direction']) for r in results if r['passes_economic']]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED+200,new_hypotheses=24,cumulative_hypotheses=367,costs_per_side=COSTS,daily_round_trip_bps=DAILY_ROUND_TRIP_BPS,
        stage_a=results,stage_a_survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
