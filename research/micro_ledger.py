"""E024 Stage B/C/D: taker ledger, multiplicity bound and hostile execution audit for Stage-A survivors."""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty
from micro_screen import COSTS,LATENCY,SEED

def thresholds_previous_day(F,feature):
    """Decile thresholds from the previous sampled day only (causal)."""
    q=F.groupby('day')[feature].quantile([.1,.9]).unstack();q=q.shift(1)
    return F.day.map(q[.1]),F.day.map(q[.9])

def taker_ledger(F,feature,h,direction,cost,latency_extra=0,miss_rate=0.,seed=0,noise=0.,notional=500.):
    """One position at a time; enter in the extreme decile in the predicted direction; hold h seconds.

    Entry/exit prices come from forward_returns computed at the preregistered latency; extra latency
    is modeled by using the return series computed with a later entry (fwd shifted by latency_extra seconds
    is approximated with the next decision row when latency_extra >= STEP). Missed fills skip entries.
    """
    rng=np.random.default_rng(seed);lo,hi=thresholds_previous_day(F,feature);x=F[feature].to_numpy(float)
    if noise:x=x+rng.normal(0,noise*np.nanstd(x),len(x))
    col=f'fwd_{h}' if latency_extra==0 else f'fwd_{h}_lat{latency_extra}'
    fwd=F[col].to_numpy(float);days=F.day.to_numpy();sig=np.where(x>=hi.to_numpy(),1,np.where(x<=lo.to_numpy(),-1,0))*direction
    rows=[];busy_until=-1;pnl_day={}
    for i in range(len(F)):
        d=days[i];t=int(F.index[i]) if False else i
        if sig[i]==0 or not np.isfinite(fwd[i]):continue
        if i<busy_until:continue
        if miss_rate and rng.random()<miss_rate:continue
        r=sig[i]*fwd[i]-2*cost;pnl_day[d]=pnl_day.get(d,0.)+r*notional;rows.append(dict(day=d,i=i,side=int(sig[i]),ret=r))
        busy_until=i+int(np.ceil(h/60))
    trades=pd.DataFrame(rows);daily=pd.Series(pnl_day).reindex(sorted(set(days))).fillna(0.)/notional
    return trades,daily

def performance(trades,daily):
    if len(trades)==0:return dict(trades=0,net_return=0.,daily_sharpe=0.,positive_month_share=0.,mean_trade_bps=0.)
    m=daily.groupby(pd.to_datetime(daily.index).strftime('%Y-%m')).sum()
    return dict(trades=int(len(trades)),net_return=float(daily.sum()),daily_sharpe=float(daily.mean()/daily.std()*np.sqrt(365)) if daily.std()>0 else 0.,
        positive_month_share=float((m>0).mean()),mean_trade_bps=float(trades.ret.mean()*1e4),hit_rate=float((trades.ret>0).mean()),
        worst_day=float(daily.min()),top5pct_days_share=float(daily.sort_values(ascending=False).head(max(1,int(.05*len(daily)))).sum()/daily[daily>0].sum()) if (daily>0).any() else None)

def placebo(F,feature,h,direction,cost,runs,seed):
    out=[];rng=np.random.default_rng(seed);G=F.copy()
    for k in range(runs):
        G[feature]=F.groupby('day')[feature].transform(lambda s:rng.permutation(s.to_numpy()))
        tr,dl=taker_ledger(G,feature,h,direction,cost);out.append(performance(tr,dl)['net_return'])
    return np.array(out)

def main():
    source=ROOT/sys.argv[1];screen=json.loads((source/'results.json').read_text());trials=screen['cumulative_hypotheses']
    eid='E025_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[]
    for j,c in enumerate(screen['stage_a_survivors']):
        F=pd.read_parquet(source/f"{c['symbol']}_features.parquet");feature,h,d=c['feature'],c['horizon_s'],c['direction']
        cases={}
        for case,cost in COSTS.items():
            tr,dl=taker_ledger(F,feature,h,d,cost);p=performance(tr,dl)
            u={str(b):uncertainty(dl.to_numpy(),np.zeros(len(dl)),SEED+j,trials=trials,samples=10000,block=b) for b in [1,5,20]}
            cases[case]=dict(metrics=p,uncertainty=u,gate=bool(p['net_return']>0 and p['daily_sharpe']>0 and p['positive_month_share']>=.6 and u['5']['mean_daily_ci95'][0]>0),
                passes_adjusted=all(a['simultaneous_lower_mean_daily']>0 for a in u.values()))
            tr.to_csv(out/f'{j}_{case}_trades.csv',index=False)
        hostile=dict(latency_30s=performance(*taker_ledger(F,feature,h,d,COSTS['stress'],latency_extra=30)),fee_plus_2bps=performance(*taker_ledger(F,feature,h,d,COSTS['stress']+.0002)),miss_20pct=performance(*taker_ledger(F,feature,h,d,COSTS['stress'],miss_rate=.2,seed=1)),
            noise_10pct=performance(*taker_ledger(F,feature,h,d,COSTS['stress'],noise=.1,seed=2)),
            horizon_half=performance(*taker_ledger(F,feature,h//2,d,COSTS['stress'])) if f'fwd_{h//2}' in F else None,
            horizon_double=performance(*taker_ledger(F,feature,h*2,d,COSTS['stress'])) if f'fwd_{h*2}' in F else None)
        pl=placebo(F,feature,h,d,COSTS['stress'],200,SEED+900+j);obs=cases['stress']['metrics']['net_return']
        hostile['placebo']=dict(runs=200,fraction_at_or_above_observed=float(np.mean(pl>=obs)),quantiles=np.quantile(pl,[.5,.95,.99]).tolist())
        verdict='RESEARCH-PROMISING (development only)' if cases['stress']['gate'] and cases['stress']['passes_adjusted'] and hostile['placebo']['fraction_at_or_above_observed']<.05 and hostile['fee_plus_2bps']['net_return']>0 else 'REJECTED FOR PROMOTION'
        results.append(dict(candidate=c,cases=cases,hostile=hostile,verdict=verdict));print(c,verdict,cases['stress']['metrics'],flush=True)
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED,source=str(source.relative_to(ROOT)),multiplicity_trials=trials,results=results,
        validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float));print('OUTPUT',out)

if __name__=='__main__':main()
