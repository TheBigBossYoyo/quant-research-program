"""E012: preregistered aggressive-flow diagnostics on perpetuals. Development only.

Stage 1 is a statistical IC gate; Stage 2 reuses the E010 signed ledger unchanged.
OHLCV taker aggregates support no queue-position or sub-minute claims.
"""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.stats import rankdata,spearmanr
from core import ROOT,code_hash,load_data,aggregate
from perpetual_screen import prepare,signed_ledger,performance

FEATURES=['imb1','imb6','xv1'];TIMEFRAMES=[1,4,24];SYMBOLS=['BTCUSDT','ETHUSDT']
CELLS=18;DIRECTIONAL_HYPOTHESES=36;PRIOR_HYPOTHESES=119
BLOCK_DAYS=7;THRESHOLD_DAYS=30;IC_SAMPLES=2000;SEED=20260908
COST_CASES=[('fee_only',.0005),('base',.0007),('stress',.0014)]

def imbalance(taker_buy,volume,window):
    """Signed aggressive imbalance in [-1,1]; NaN when the window has no volume or a gap."""
    net=2*taker_buy-volume
    if window>1:
        net=net.rolling(window).sum();volume=volume.rolling(window).sum()
    return (net/volume).where(volume>0)

def resample_bars(f,tf):
    """Complete tf-hour buckets only; the bucket open is the executable first-hour open."""
    if tf==1:return f[['open','close','volume','taker_base']].copy()
    g=f.resample(f'{tf}h',label='left',closed='left',origin='epoch')
    a=g.agg(dict(open='first',close='last',volume='sum',taker_base='sum'))
    a.loc[g.open.count()!=tf,:]=np.nan
    return a

def forward_return(exec_open,h):
    """Return from the open two bars after the signal bar to h bars later."""
    return exec_open.shift(-2-h)/exec_open.shift(-2)-1

def cell_features(perp_hourly,spot_hourly,tf):
    p=resample_bars(perp_hourly,tf);s=resample_bars(spot_hourly,tf).reindex(p.index)
    out=pd.DataFrame(index=p.index)
    out['imb1']=imbalance(p.taker_base,p.volume,1)
    out['imb6']=imbalance(p.taker_base,p.volume,6)
    out['xv1']=imbalance(s.taker_base,s.volume,1)-out['imb1']
    out['exec_open']=p.open;out['bar_return']=p.close/p.open-1
    return out

def following_target(feature,direction):
    return (direction*np.sign(feature)).fillna(0.)

def threshold_target(feature,direction,window,min_obs=None):
    """Trade only beyond trailing 20th/80th percentiles of bars <= t; flat otherwise."""
    min_obs=int(np.ceil(2*window/3)) if min_obs is None else min_obs
    hi=feature.rolling(window,min_periods=min_obs).quantile(.8)
    lo=feature.rolling(window,min_periods=min_obs).quantile(.2)
    t=pd.Series(0.,index=feature.index)
    t[feature>hi]=1.;t[feature<lo]=-1.
    return direction*t

def block_bootstrap_ic(x,y,block,samples,seed,cells=CELLS,chunk=200):
    x=np.asarray(x,float);y=np.asarray(y,float);ok=np.isfinite(x)&np.isfinite(y);x=x[ok];y=y[ok];n=len(x)
    ic=float(spearmanr(x,y).statistic);rng=np.random.default_rng(seed);draws=[]
    for start in range(0,samples,chunk):
        m=min(chunk,samples-start)
        starts=rng.integers(0,n,size=(m,int(np.ceil(n/block))))
        idx=((starts[:,:,None]+np.arange(block))%n).reshape(m,-1)[:,:n]
        rx=rankdata(x[idx],axis=1);ry=rankdata(y[idx],axis=1)
        rx-=rx.mean(axis=1,keepdims=True);ry-=ry.mean(axis=1,keepdims=True)
        draws.append((rx*ry).sum(axis=1)/np.sqrt((rx**2).sum(axis=1)*(ry**2).sum(axis=1)))
    d=np.concatenate(draws);a=.05/cells
    return dict(ic=ic,observations=int(n),block=int(block),samples=int(samples),seed=int(seed),
        ci95=np.quantile(d,[.025,.975]).tolist(),ci_lower_adjusted=float(np.quantile(d,a/2)),
        ci_upper_adjusted=float(np.quantile(d,1-a/2)),bonferroni_cells=cells)

def spearman(a,b):
    m=a.notna()&b.notna()
    return float(spearmanr(a[m],b[m]).statistic) if m.sum()>2 else float('nan')

def stage1(cf,cell_index,tf,features=FEATURES,cells=CELLS,seed=SEED,horizons=(1,4,24)):
    fwd=forward_return(cf.exec_open,1);rows={}
    block=max(1,int(BLOCK_DAYS*24/tf))
    for k,name in enumerate(features):
        s=cf[name];valid=s.notna()&fwd.notna()
        boot=block_bootstrap_ic(s[valid],fwd[valid],block,IC_SAMPLES,seed+cell_index*len(features)+k,cells=cells)
        passes=boot['ci_lower_adjusted']>0 or boot['ci_upper_adjusted']<0
        decay={str(h):spearman(s,forward_return(cf.exec_open,h)) for h in horizons}
        years={str(y):spearman(s[valid][valid[valid].index.year==y],fwd[valid][valid[valid].index.year==y]) for y in sorted(set(valid[valid].index.year))}
        q=s[valid].quantile([.2,.8]);top=fwd[valid&(s>=q[.8])];bot=fwd[valid&(s<=q[.2])]
        rows[name]=dict(feature=name,**boot,passes_stage1=bool(passes),direction=int(np.sign(boot['ic'])) if passes else 0,
            decay_ic_by_horizon_bars=decay,ic_by_year=years,feature_autocorrelation=float(s.autocorr()),
            contemporaneous_bar_return_correlation=spearman(s,cf.bar_return),
            top_quintile_forward_mean_bps=float(top.mean()*1e4),bottom_quintile_forward_mean_bps=float(bot.mean()*1e4),
            base_round_trip_cost_bps=14.)
    return rows

def to_hourly_target(t,px_index):
    return t.shift(2).fillna(0).reindex(px_index).ffill().fillna(0)

def main():
    eid='E012_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();stage1_rows=[];stage2_rows=[];sources=[];cell_index=0;rule_b_trials=0
    for sym in SYMBOLS:
        f,px,funding,meta=prepare(sym);spot,si=load_data(sym);spot_hourly=aggregate(spot,60)
        sources.append(dict(symbol=sym,spot_rows=si['rows'],spot_missing=si['missing_count'],**meta))
        mn=50 if sym=='BTCUSDT' else 20
        for tf in TIMEFRAMES:
            cf=cell_features(f,spot_hourly,tf)
            s1=stage1(cf,cell_index,tf);cell_index+=1
            for name,r in s1.items():stage1_rows.append(dict(symbol=sym,timeframe_hours=tf,**r))
            print(sym,tf,{k:(round(v['ic'],4),v['passes_stage1']) for k,v in s1.items()},flush=True)
            survivors=[r for r in s1.values() if r['passes_stage1']]
            if not survivors:continue
            long_target=to_hourly_target(pd.Series(1.,index=cf.index),px.index)
            for case,fee in COST_CASES:
                m=performance(signed_ledger(px,long_target,funding,fee=fee,min_notional=mn))
                stage2_rows.append(dict(symbol=sym,timeframe_hours=tf,feature='long_baseline',rule='long_baseline',direction=1,case=case,**m))
            window=int(THRESHOLD_DAYS*24/tf)
            for r in survivors:
                d=r['direction'];s=cf[r['feature']]
                for rule,t in [('a_following',following_target(s,d)),('b_threshold',threshold_target(s,d,window))]:
                    if rule=='b_threshold':rule_b_trials+=1
                    target=to_hourly_target(t,px.index)
                    for case,fee in COST_CASES:
                        m=performance(signed_ledger(px,target,funding,fee=fee,min_notional=mn))
                        stage2_rows.append(dict(symbol=sym,timeframe_hours=tf,feature=r['feature'],rule=rule,direction=d,case=case,**m))
                    print(sym,tf,r['feature'],rule,'stress cagr',round(stage2_rows[-1]['cagr'],4),flush=True)
    stage2_survivors=[]
    for r in stage2_rows:
        if r['case']!='stress' or r['rule']=='long_baseline':continue
        b=next(x for x in stage2_rows if x['symbol']==r['symbol'] and x['timeframe_hours']==r['timeframe_hours'] and x['rule']=='long_baseline' and x['case']=='stress')
        if r['cagr']>0 and r['daily_sharpe']>max(0.,b['daily_sharpe']) and sum(v>0 for v in r['calendar_returns'].values())>=2 and not r['halted']:
            stage2_survivors.append({k:r[k] for k in ['symbol','timeframe_hours','feature','rule','direction']})
    assert starting==code_hash(),'Source changed during experiment'
    cumulative=PRIOR_HYPOTHESES+DIRECTIONAL_HYPOTHESES+rule_b_trials
    result=dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED,ic_cells=CELLS,directional_hypotheses=DIRECTIONAL_HYPOTHESES,
        rule_b_trials_run=rule_b_trials,cumulative_hypotheses=cumulative,stage1=stage1_rows,
        stage1_survivors=[dict(symbol=r['symbol'],timeframe_hours=r['timeframe_hours'],feature=r['feature'],direction=r['direction']) for r in stage1_rows if r['passes_stage1']],
        stage2=stage2_rows,stage2_survivors=stage2_survivors,sources=sources,validation_accessed=False,final_test_accessed=False,
        verdict='CHEAP DEVELOPMENT DIAGNOSTIC ONLY; taker aggregates, no depth/queue model; margin and executable quotes unverified.')
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame([{k:v for k,v in r.items() if k not in ('decay_ic_by_horizon_bars','ic_by_year','ci95')} for r in stage1_rows]).to_csv(out/'ic.csv',index=False)
    if stage2_rows:pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in stage2_rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'STAGE1',len(result['stage1_survivors']),'STAGE2',stage2_survivors,'CUMULATIVE',cumulative)

if __name__=='__main__':main()
