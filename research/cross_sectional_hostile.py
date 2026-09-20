"""E017: hostile audit of the frozen E016 flow7 candidate. No retuning; development 2020-2024 only.

Items 1-7 are falsification diagnostics; item 8 (14/28-day rebalance variants) adds two counted
hypotheses judged by the Stage-2 gates and the cumulative adjusted bound.
"""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty
from economic_audit import reference,accrual_reference
from universe import load_klines,load_funding,daily_funding,eligibility,features,rebalance_days,quintile_weights,MIN_HISTORY_BARS,LIQUIDITY_WINDOW
from cross_sectional_screen import xs_ledger,performance,COST_CASES,STEP

PLACEBO_RUNS=200;SEED=20260908+300;VARIANT_STEPS=[14,28]

def build_weights(score,elig,rb,direction=1):
    return {d:w for d in rb for w in [quintile_weights(score.loc[d],elig.loc[d],direction)] if len(w)}

def placebo_weights(score,elig,rb,seed):
    """Permute the feature across eligible names within each rebalance day; nothing else changes."""
    rng=np.random.default_rng(seed);out={}
    for d in rb:
        s=score.loc[d].where(elig.loc[d]).dropna()
        if len(s)<10:continue
        shuffled=pd.Series(rng.permutation(s.to_numpy()),index=s.index)
        w=quintile_weights(shuffled,elig.loc[d],1)
        if len(w):out[d]=w
    return out

def daily_returns(path,initial=10000.):
    r=path.nav.pct_change();r.iloc[0]=path.nav.iloc[0]/initial-1
    return r

def breakeven_cost(open_panel,fund_daily,w,lo=0.,hi=.01,iters=12):
    for _ in range(iters):
        mid=(lo+hi)/2
        if performance(xs_ledger(open_panel,fund_daily,w,mid))['cagr']>0:lo=mid
        else:hi=mid
    return (lo+hi)/2

def main():
    source=ROOT/sys.argv[1];screen=json.loads((source/'results.json').read_text())
    c=screen['stage2_survivors'][int(sys.argv[2]) if len(sys.argv)>2 else 0]  # survivor index; feature/direction taken from the screen
    eid='E017_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();panels,ki=load_klines();funding,fi=load_funding();days=panels['close'].index;syms=list(panels['close'].columns)
    fund_daily=daily_funding(funding,days,syms);elig=eligibility(panels);feat=features(panels,fund_daily);score=c['direction']*feat[c['feature']]
    rb=rebalance_days(days,days[MIN_HISTORY_BARS],STEP);opens=panels['open'];stress=.0014
    w=build_weights(score,elig,rb);path,attr=xs_ledger(opens,fund_daily,w,stress,attribution=True);observed=performance(path)
    rates,rate_meta=reference('DGS3MO');result=dict(observed_stress=observed)
    # 1) start-2021 path
    rb21=rb[rb>=pd.Timestamp('2021-01-01',tz='UTC')];w21={d:w[d] for d in rb21 if d in w}
    p21=xs_ledger(opens.loc['2021':],fund_daily.loc['2021':],w21,stress);r21=daily_returns(p21);cash=accrual_reference(rates,r21.index)
    result['start_2021']=dict(metrics=performance(p21),excess_uncertainty=uncertainty(r21-cash,np.zeros(len(r21)),SEED,trials=1,samples=10000,block=30))
    # 2) concentration
    weekly=path.nav.resample('7D').last().pct_change().dropna();pos=weekly[weekly>0]
    top_weeks=pos.sort_values(ascending=False).head(max(1,int(np.ceil(.05*len(weekly)))))
    sym_pnl=attr['pnl_by_symbol'].sort_values(ascending=False);total_price=float(sym_pnl.sum())
    result['concentration']=dict(weeks=int(len(weekly)),top5pct_weeks_share_of_positive_weekly_returns=float(top_weeks.sum()/pos.sum()),
        top10_symbols=sym_pnl.head(10).round(2).to_dict(),top10_share_of_total_price_pnl=float(sym_pnl.head(10).sum()/total_price) if total_price else None,
        price_pnl_without_top10=float(total_price-sym_pnl.head(10).sum()),total_price_pnl=total_price,funding_pnl=attr['funding_pnl'],cost_paid=attr['cost_paid'],
        net_pnl_without_top10_symbols=float(total_price-sym_pnl.head(10).sum()+attr['funding_pnl']-attr['cost_paid']))
    # 3) breakeven cost
    result['breakeven_cost_per_executed_notional']=breakeven_cost(opens,fund_daily,w)
    # 4) liquidity split (upper half of eligible names by trailing median quote volume, point-in-time)
    med=panels['quote_volume'].rolling(LIQUIDITY_WINDOW,min_periods=LIQUIDITY_WINDOW).median()
    upper=elig&(med.where(elig).rank(axis=1,pct=True)>=.5)
    result['upper_liquidity_half']=performance(xs_ledger(opens,fund_daily,build_weights(score,upper,rb),stress))
    # 5) leg decomposition
    longs={d:x[x>0] for d,x in w.items()};shorts={d:x[x<0] for d,x in w.items()}
    result['long_leg_only']=performance(xs_ledger(opens,fund_daily,longs,stress));result['short_leg_only']=performance(xs_ledger(opens,fund_daily,shorts,stress))
    # 6) placebo
    cagrs=[];sharpes=[]
    for k in range(PLACEBO_RUNS):
        m=performance(xs_ledger(opens,fund_daily,placebo_weights(score,elig,rb,SEED+k),stress));cagrs.append(m['cagr']);sharpes.append(m['daily_sharpe'])
        if k%25==0:print('placebo',k,round(m['cagr'],3),flush=True)
    cagrs=np.array(cagrs);sharpes=np.array(sharpes)
    result['placebo']=dict(runs=PLACEBO_RUNS,seed=SEED,cagr_quantiles=np.quantile(cagrs,[.05,.5,.95,.99]).tolist(),sharpe_quantiles=np.quantile(sharpes,[.05,.5,.95,.99]).tolist(),
        fraction_cagr_at_or_above_observed=float(np.mean(cagrs>=observed['cagr'])),fraction_sharpe_at_or_above_observed=float(np.mean(sharpes>=observed['daily_sharpe'])))
    # 7) funding share
    result['funding_share_of_net_pnl']=float(attr['funding_pnl']/(path.nav.iloc[-1]-10000.))
    # 8) counted variants
    variants=[];trials=screen['cumulative_hypotheses']+len(VARIANT_STEPS)
    for step in VARIANT_STEPS:
        rbs=rebalance_days(days,days[MIN_HISTORY_BARS],step);wv=build_weights(score,elig,rbs);cases={}
        for case,cost in COST_CASES:cases[case]=performance(xs_ledger(opens,fund_daily,wv,cost))
        r=daily_returns(xs_ledger(opens,fund_daily,wv,stress));cash=accrual_reference(rates,r.index)
        u={str(b):uncertainty(r-cash,np.zeros(len(r)),SEED+1000+step+b,trials=trials,samples=10000,block=b) for b in [7,30,60]}
        s=cases['stress'];gate=s['cagr']>0 and s['daily_sharpe']>0 and sum(v>0 for v in s['calendar_returns'].values())>=2 and s['max_daily_drawdown']>-.30
        variants.append(dict(rebalance_days=step,cases=cases,stage2_gate=bool(gate),excess_uncertainty=u,passes_adjusted_bound=all(a['simultaneous_lower_mean_daily']>0 for a in u.values())))
        print('variant',step,'stress cagr',round(s['cagr'],4),'sharpe',round(s['daily_sharpe'],3),'turnover',round(s['annual_turnover'],1),'adjusted pass',variants[-1]['passes_adjusted_bound'],flush=True)
    result['variants']=variants
    keep=(result['placebo']['fraction_cagr_at_or_above_observed']<.05 and result['placebo']['fraction_sharpe_at_or_above_observed']<.05
        and result['start_2021']['excess_uncertainty']['mean_daily_ci95'][0]>0 and result['concentration']['net_pnl_without_top10_symbols']>0)
    result['frozen_candidate_keeps_research_promising_label']=bool(keep)
    assert starting==code_hash(),'Source changed during experiment'
    payload=dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=SEED,source=str(source.relative_to(ROOT)),cumulative_hypotheses=trials,rate_reference=rate_meta,
        validation_accessed=False,final_test_accessed=False,**result)
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'KEEP',keep,'placebo frac cagr',result['placebo']['fraction_cagr_at_or_above_observed'],'breakeven bps',round(result['breakeven_cost_per_executed_notional']*1e4,1))

if __name__=='__main__':main()
