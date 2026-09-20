"""E024: Stage A/B on liquidity-, positioning- and sweep-conditioned signals. Development sampled days only."""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from core import ROOT,code_hash
from micro_data import SYMBOLS,METRICS_END,sample_days,load_depth,load_metrics,load_seconds

LATENCY=5;STEP=60;DEPTH_MAX_AGE=120;SEED=20260908+700
CELLS=[('flow_rel','both',(300,1800)),('depth_imb','depth',(300,1800)),('oi_price','metrics',(900,3600)),('sweep','both',(300,1800))]
COSTS={'base':.0005+.000005+.0001,'stress':.0005+.000005+.0002,'severe':.0005+.000005+.0004}  # per side: fee + half-spread + slippage
BASE_ROUND_TRIP_BPS=2*COSTS['base']*1e4

def rolling_sum(x,w):
    c=np.cumsum(np.insert(x,0,0.));return c[w:]-c[:-w]

def day_features(sec,depth,metrics,day):
    """Features at decision seconds t (every STEP s) from data with timestamps <= t only."""
    n=86400;t=np.arange(STEP,n,STEP);last=sec.last_price.to_numpy();price=pd.Series(last).ffill().to_numpy()
    buy=sec.buy_qty.to_numpy();sell=sec.sell_qty.to_numpy();mx=sec.max_notional.to_numpy();mxs=sec.max_notional_signed.to_numpy()
    out=pd.DataFrame(index=t);out['price']=price[t-1]  # last trade strictly before or at second t-1 (bar t-1 is complete at t)
    net60=rolling_sum(buy-sell,60);out['net_flow_60']=net60[t-60]  # sum over seconds [t-60,t-1]
    if depth is not None:
        dts=((depth.index-pd.Timestamp(day)).total_seconds()).to_numpy();bid1=depth[-1].to_numpy();ask1=depth[1].to_numpy()
        pos=np.searchsorted(dts,t,side='right')-1;ok=(pos>=0)&((t-np.where(pos>=0,dts[np.clip(pos,0,None)],-1e9))<=DEPTH_MAX_AGE)
        b=np.where(ok,bid1[np.clip(pos,0,None)],np.nan);a=np.where(ok,ask1[np.clip(pos,0,None)],np.nan)
        out['flow_rel']=out.net_flow_60/(b+a);out['depth_imb']=(b-a)/(b+a)
    else:out['flow_rel']=np.nan;out['depth_imb']=np.nan
    # sweep: largest signed aggregate in [t-60,t-1] relative to trailing 60-minute median of per-second maxima (seconds [t-3600,t-1])
    idx60=np.array([np.argmax(mx[max(0,s-60):s])+max(0,s-60) for s in t]);big=mxs[idx60]
    med=np.array([np.median(mx[max(0,s-3600):s][mx[max(0,s-3600):s]>0]) if (mx[max(0,s-3600):s]>0).any() else np.nan for s in t])
    out['sweep']=big/med
    if metrics is not None and pd.Timestamp(day)<=METRICS_END:
        mts=((metrics.index-pd.Timestamp(day)).total_seconds()).to_numpy();oi=metrics.sum_open_interest.to_numpy()
        pos=np.searchsorted(mts,t,side='right')-1;prev=pos-3  # 15 minutes earlier (3 x 5-minute rows)
        ok=(prev>=0)&(mts[np.clip(pos,0,None)]<=t)
        prev_oi=oi[np.clip(prev,0,None)];ok=ok&(prev_oi>0)
        with np.errstate(divide='ignore',invalid='ignore'):d_oi=np.where(ok,(oi[np.clip(pos,0,None)]-prev_oi)/np.where(prev_oi>0,prev_oi,np.nan),np.nan)
        p_now=price[t-1];p_prev=price[np.clip(t-1-900,0,None)];out['oi_price']=d_oi*np.sign(p_now-p_prev)
    else:out['oi_price']=np.nan
    return out

def forward_returns(sec,t,h):
    """Entry: first trade at or after t+LATENCY; exit: first trade at or after t+LATENCY+h (within the day)."""
    first=sec.first_price.to_numpy();nxt=pd.Series(first).bfill().to_numpy()
    e=t+LATENCY;x=e+h;valid=x<86400
    entry=np.where(valid,nxt[np.clip(e,0,86399)],np.nan);exit_=np.where(valid,nxt[np.clip(x,0,86399)],np.nan)
    return exit_/entry-1

def block_bootstrap_ic(x,y,days,samples,seed,cells):
    ok=np.isfinite(x)&np.isfinite(y);x,y,days=x[ok],y[ok],days[ok];ic=float(spearmanr(x,y).statistic)
    rx=pd.Series(x).rank().to_numpy();ry=pd.Series(y).rank().to_numpy();ud=np.unique(days);rng=np.random.default_rng(seed);draws=[]
    groups={d:np.flatnonzero(days==d) for d in ud}
    for _ in range(samples):
        pick=rng.choice(ud,size=len(ud),replace=True);idx=np.concatenate([groups[d] for d in pick])
        a=rx[idx]-rx[idx].mean();b=ry[idx]-ry[idx].mean();draws.append(float((a*b).sum()/np.sqrt((a*a).sum()*(b*b).sum())))
    draws=np.array(draws);q=.05/cells/2
    return dict(ic=ic,n=int(ok.sum()),days=int(len(ud)),ci95=np.quantile(draws,[.025,.975]).tolist(),ci_lower_adjusted=float(np.quantile(draws,q)),ci_upper_adjusted=float(np.quantile(draws,1-q)))

def stage_a(feature,fwd,days,months,hours,seed,cells):
    boot=block_bootstrap_ic(feature,fwd,days,2000,seed,cells);passes=boot['ci_lower_adjusted']>0 or boot['ci_upper_adjusted']<0
    ok=np.isfinite(feature)&np.isfinite(fwd);f=feature[ok];r=fwd[ok];d=np.sign(boot['ic']) if passes else 0
    dec=pd.qcut(pd.Series(f),10,labels=False,duplicates='drop');by_dec=pd.Series(r).groupby(dec.to_numpy()).mean()*1e4
    lo=float(by_dec.iloc[0]);hi=float(by_dec.iloc[-1]);edge=(hi-lo)/2*np.sign(boot['ic'])  # average one-sided extreme-decile edge in predicted direction
    def sp(a,b):
        v=float(spearmanr(a,b).statistic) if len(a)>2 else float('nan');return None if not np.isfinite(v) else v
    by_month={str(m):sp(f[months[ok]==m],r[months[ok]==m]) for m in np.unique(months[ok])}
    by_hour={str(h):sp(f[hours[ok]//6==h],r[hours[ok]//6==h]) for h in range(4)}
    return dict(**boot,passes_statistical=bool(passes),direction=int(d),decile_means_bps=by_dec.round(3).tolist(),extreme_decile_edge_bps=float(edge),
        passes_economic=bool(passes and edge>=BASE_ROUND_TRIP_BPS),base_round_trip_bps=BASE_ROUND_TRIP_BPS,ic_by_month=by_month,ic_by_utc_quarter=by_hour)

def build(sym):
    frames=[]
    for day in sample_days():
        sec=load_seconds(sym,day)
        if sec is None:continue
        f=day_features(sec,load_depth(sym,day),load_metrics(sym,day),day);t=f.index.to_numpy()
        for h in sorted({h for _,_,hs in CELLS for h in hs}):f[f'fwd_{h}']=forward_returns(sec,t,h);f[f'fwd_{h}_lat30']=forward_returns(sec,t+25,h)  # 30-s latency stress
        f['day']=day.strftime('%Y-%m-%d');f['month']=day.strftime('%Y-%m');f['hour']=t//3600;frames.append(f.reset_index(drop=True))
    return pd.concat(frames,ignore_index=True)

def main():
    eid='E024_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();results=[];k=0;ncells=len(CELLS)*2*len(SYMBOLS)
    for sym in SYMBOLS:
        F=build(sym);F.to_parquet(out/f'{sym}_features.parquet',index=False);print(sym,'decision rows',len(F),'days',F.day.nunique(),flush=True)
        days=F.day.to_numpy();months=F.month.to_numpy();hours=F.hour.to_numpy()
        for name,_,hs in CELLS:
            for h in hs:
                r=stage_a(F[name].to_numpy(float),F[f'fwd_{h}'].to_numpy(float),days,months,hours,SEED+k,ncells);k+=1
                results.append(dict(symbol=sym,feature=name,horizon_s=h,**r))
                print(sym,name,h,'IC',round(r['ic'],4),'adjCI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'stat',r['passes_statistical'],'edge bps',round(r['extreme_decile_edge_bps'],2),'econ',r['passes_economic'],flush=True)
    survivors=[dict(symbol=r['symbol'],feature=r['feature'],horizon_s=r['horizon_s'],direction=r['direction']) for r in results if r['passes_economic']]
    below_cost=[dict(symbol=r['symbol'],feature=r['feature'],horizon_s=r['horizon_s'],ic=r['ic'],edge_bps=r['extreme_decile_edge_bps']) for r in results if r['passes_statistical'] and not r['passes_economic']]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED,new_hypotheses=32,cumulative_hypotheses=243+32,cells=ncells,
        latency_s=LATENCY,costs_per_side=COSTS,stage_a=results,stage_a_survivors=survivors,statistically_real_but_below_taker_cost=below_cost,
        validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    pd.DataFrame([{k:v for k,v in r.items() if k not in ('ic_by_month','ic_by_utc_quarter','decile_means_bps','ci95')} for r in results]).to_csv(out/'stage_a.csv',index=False)
    print('OUTPUT',out,'SURVIVORS',survivors,'BELOW_COST',len(below_cost))

if __name__=='__main__':main()
