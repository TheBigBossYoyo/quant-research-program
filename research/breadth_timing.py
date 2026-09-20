"""E019: market-wide positioning/breadth as a weekly BTC timing signal. Development 2020-2024 only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from universe import load_klines,load_funding,daily_funding,eligibility,features,rebalance_days,MIN_HISTORY_BARS
from cross_sectional_screen import xs_ledger,performance,COST_CASES,STEP,DELAY
from flow_screen import block_bootstrap_ic

FEATURES=['agg_fund7','breadth30'];PRIOR_HYPOTHESES=215;NEW_HYPOTHESES=4;SEED=20260908+400;ASSET='BTCUSDT'

def aggregate_features(panels,feat,elig):
    """Cross-sectional aggregates over names eligible at t; NaN when fewer than 10 names."""
    n=elig.sum(axis=1)
    agg_fund=feat['fund7'].where(elig).mean(axis=1).where(n>=10)
    close=panels['close'];above=(close>close.shift(30)).where(elig&close.shift(30).notna())
    breadth=above.mean(axis=1).where(n>=10)
    return pd.DataFrame(dict(agg_fund7=agg_fund,breadth30=breadth))

def btc_forward(open_panel,start=DELAY,end=DELAY+STEP):
    o=open_panel[ASSET];return o.shift(-end)/o.shift(-start)-1

def main():
    eid='E019_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();panels,ki=load_klines();funding,fi=load_funding();days=panels['close'].index;syms=list(panels['close'].columns)
    fund_daily=daily_funding(funding,days,syms);elig=eligibility(panels);feat=features(panels,fund_daily);agg=aggregate_features(panels,feat,elig)
    rb=rebalance_days(days,days[MIN_HISTORY_BARS],STEP);fwd=btc_forward(panels['open']);stage1={}
    crit_cells=len(FEATURES)
    for k,name in enumerate(FEATURES):
        s=agg[name].reindex(rb);f=fwd.reindex(rb);m=s.notna()&f.notna()
        boot=block_bootstrap_ic(s[m],f[m],block=4,samples=2000,seed=SEED+k,cells=crit_cells)
        passes=boot['ci_lower_adjusted']>0 or boot['ci_upper_adjusted']<0
        years={str(y):float(pd.Series(s[m]).groupby(s[m].index.year).apply(lambda x:x.corr(f[m].loc[x.index],method='spearman')).get(y,np.nan)) for y in sorted(set(s[m].index.year))}
        stage1[name]=dict(feature=name,**boot,passes_stage1=bool(passes),direction=int(np.sign(boot['ic'])) if passes else 0,ic_by_year=years,
            feature_autocorrelation=float(s.autocorr()),weeks=int(m.sum()))
        print(name,'IC',round(boot['ic'],4),'adj CI',[round(boot['ci_lower_adjusted'],3),round(boot['ci_upper_adjusted'],3)],'pass',passes,flush=True)
    stage2=[];extra=0
    base_w={d:pd.Series({ASSET:1.}) for d in rb if np.isfinite(panels['open'].loc[d,ASSET])}
    for case,c in COST_CASES:stage2.append(dict(hypothesis='btc_long',feature='btc_long',rule='long',direction=1,case=case,**performance(xs_ledger(panels['open'],fund_daily,base_w,c))))
    for name,r in stage1.items():
        if not r['passes_stage1']:continue
        d=r['direction'];s=agg[name];med=s.expanding(min_periods=52).median()  # causal reference level: expanding median of the aggregate
        sig=(d*np.sign(s-med)).reindex(rb).fillna(0.)
        rules={'signed':{day:pd.Series({ASSET:float(v)}) for day,v in sig.items() if v!=0 and np.isfinite(panels['open'].loc[day,ASSET])},
               'long_flat':{day:pd.Series({ASSET:1.}) for day,v in sig.items() if v>0 and np.isfinite(panels['open'].loc[day,ASSET])}}
        extra+=1
        for rule,w in rules.items():
            for case,c in COST_CASES:
                m=performance(xs_ledger(panels['open'],fund_daily,w,c));stage2.append(dict(hypothesis=f'{name}_{rule}',feature=name,rule=rule,direction=d,case=case,**m))
                print(name,rule,case,'cagr',round(m['cagr'],4),'sharpe',round(m['daily_sharpe'],3),flush=True)
    survivors=[]
    btc=next(x for x in stage2 if x['hypothesis']=='btc_long' and x['case']=='stress')
    for r in stage2:
        if r['case']!='stress' or r['hypothesis']=='btc_long':continue
        if r['cagr']>0 and r['daily_sharpe']>max(0.,btc['daily_sharpe']) and sum(v>0 for v in r['calendar_returns'].values())>=2 and r['max_daily_drawdown']>-.30:
            survivors.append(dict(hypothesis=r['hypothesis'],feature=r['feature'],rule=r['rule'],direction=r['direction']))
    assert starting==code_hash(),'Source changed during experiment'
    payload=dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED,cumulative_hypotheses=PRIOR_HYPOTHESES+NEW_HYPOTHESES+extra,new_hypotheses=NEW_HYPOTHESES,long_flat_trials=extra,
        stage1=list(stage1.values()),stage2=stage2,stage2_survivors=survivors,validation_accessed=False,final_test_accessed=False,
        note='Signal sign relative to the causal expanding median of the aggregate (52-week minimum); no threshold optimization.')
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False,default=float))
    agg.to_csv(out/'aggregates.csv')
    print('OUTPUT',out,'STAGE1',[k for k,v in stage1.items() if v['passes_stage1']],'STAGE2',survivors)

if __name__=='__main__':main()
