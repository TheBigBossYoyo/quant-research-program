"""E013: preregistered funding/basis positioning-state diagnostics on perpetuals.

Development 2022-2024 only. Reuses the E012 Stage-1 gate and the E010 signed ledger.
Funding rates become available at their scheduled settlement time; positioning
features are evaluated on funding-aligned 8-hour bars and daily bars only.
"""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash,load_data,aggregate
from perpetual_screen import prepare,signed_ledger,performance
from carry_screen import funding_diagnostic
from flow_screen import resample_bars,following_target,threshold_target,stage1,to_hourly_target,COST_CASES,THRESHOLD_DAYS

FEATURES=['fund8','fund24','basis','basis_z'];TIMEFRAMES=[8,24];SYMBOLS=['BTCUSDT','ETHUSDT']
CELLS=16;DIRECTIONAL_HYPOTHESES=32;PRIOR_HYPOTHESES=159;SEED=20260908+100

def funding_features(rates,bar_index,tf):
    """Latest realized rate and trailing three-rate sum known at each bar's close."""
    assert rates.index.is_monotonic_increasing and rates.index.is_unique
    end=pd.DatetimeIndex(bar_index)+pd.Timedelta(hours=tf)
    f8=rates.reindex(end,method='ffill');f24=rates.rolling(3).sum().reindex(end,method='ffill')
    return pd.Series(f8.to_numpy(),index=bar_index),pd.Series(f24.to_numpy(),index=bar_index)

def positioning_features(perp_hourly,spot_hourly,rates,tf):
    p=resample_bars(perp_hourly,tf);s=resample_bars(spot_hourly,tf).reindex(p.index)
    out=pd.DataFrame(index=p.index)
    out['fund8'],out['fund24']=funding_features(rates,p.index,tf)
    out['basis']=p.close/s.close-1
    w=int(THRESHOLD_DAYS*24/tf);m=int(np.ceil(2*w/3))
    out['basis_z']=(out.basis-out.basis.rolling(w,min_periods=m).mean())/out.basis.rolling(w,min_periods=m).std()
    out['exec_open']=p.open;out['bar_return']=p.close/p.open-1
    return out

def scheduled_rates(sym):
    fp=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
    funding,_,_=funding_diagnostic(json.loads(fp.read_text()))
    # Availability at the scheduled boundary; recorded settlement jitter is <= 31 ms.
    return pd.Series(funding.rate.to_numpy(),index=funding.index.floor('8h')),fp.name

def main():
    eid='E013_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();stage1_rows=[];stage2_rows=[];sources=[];cell_index=0;rule_b_trials=0
    for sym in SYMBOLS:
        f,px,funding,meta=prepare(sym);spot,si=load_data(sym);spot_hourly=aggregate(spot,60);rates,fname=scheduled_rates(sym)
        sources.append(dict(symbol=sym,spot_rows=si['rows'],spot_missing=si['missing_count'],funding_rate_file=fname,**meta))
        mn=50 if sym=='BTCUSDT' else 20
        for tf in TIMEFRAMES:
            cf=positioning_features(f,spot_hourly,rates,tf)
            s1=stage1(cf,cell_index,tf,features=FEATURES,cells=CELLS,seed=SEED,horizons=(1,4,12));cell_index+=1
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
                    print(sym,tf,r['feature'],rule,'stress cagr',round(stage2_rows[-1]['cagr'],4),'sharpe',round(stage2_rows[-1]['daily_sharpe'],3),flush=True)
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
        verdict='CHEAP DEVELOPMENT DIAGNOSTIC ONLY; funding availability at scheduled boundary; margin and executable quotes unverified.')
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame([{k:v for k,v in r.items() if k not in ('decay_ic_by_horizon_bars','ic_by_year','ci95')} for r in stage1_rows]).to_csv(out/'ic.csv',index=False)
    if stage2_rows:pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in stage2_rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'STAGE1',len(result['stage1_survivors']),'STAGE2',stage2_survivors,'CUMULATIVE',cumulative)

if __name__=='__main__':main()
