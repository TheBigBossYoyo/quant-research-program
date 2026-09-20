"""E015: falsification audit of E014 Stage-2 survivors. No retuning, no validation/final access."""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty
from economic_audit import reference,accrual_reference
from universe import load_klines,load_funding,daily_funding,eligibility,features,rebalance_days,quintile_weights,MIN_HISTORY_BARS
from cross_sectional_screen import xs_ledger,performance,COST_CASES,STEP,DELAY

def daily_returns(path,initial=10000.):
    r=path.nav.pct_change();r.iloc[0]=path.nav.iloc[0]/initial-1
    return r

def capital_feasibility(weights_by_day,open_panel,capital=500.):
    """Current filters applied to historical target weights; forward-feasibility assumption only."""
    p=sorted((ROOT/'data/metadata').glob('futures_exchangeInfo*'))[-1]
    info=json.loads(p.read_text(encoding='utf8'));rules={}
    for s in info['symbols']:
        f={x['filterType']:x for x in s['filters']}
        rules[s['symbol']]=dict(step=float(f['LOT_SIZE']['stepSize']),min_notional=float(f['MIN_NOTIONAL']['notional']))
    infeasible=0;total=0;unlisted=0
    for d,w in weights_by_day.items():
        for sym,val in w.items():
            total+=1
            if sym not in rules:unlisted+=1;continue
            px=open_panel.loc[d,sym]
            if not np.isfinite(px):continue
            notional=abs(val)*capital;q=np.floor(notional/px/rules[sym]['step'])*rules[sym]['step']
            if q<=0 or q*px<rules[sym]['min_notional']:infeasible+=1
    return dict(capital_usdt=capital,positions=total,infeasible_at_current_filters=infeasible,symbols_not_in_current_exchange_info=unlisted,
        note='Current filters are not historical rules; a high infeasible share means the candidate needs more capital, not a distorted rule.',snapshot=p.name)

def main():
    source=ROOT/sys.argv[1];screen=json.loads((source/'results.json').read_text())
    eid='E015_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    panels,ki=load_klines();funding,fi=load_funding();days=panels['close'].index;syms=list(panels['close'].columns)
    fund_daily=daily_funding(funding,days,syms);elig=eligibility(panels);feat=features(panels,fund_daily)
    rb=rebalance_days(days,days[MIN_HISTORY_BARS],STEP);rates,rate_meta=reference('DGS3MO');trials=screen['cumulative_hypotheses'];results=[]
    for j,c in enumerate(screen['stage2_survivors']):
        w={d:x for d in rb for x in [quintile_weights(feat[c['feature']].loc[d],elig.loc[d],c['direction'])] if len(x)}
        cases={}
        for case,cost in COST_CASES:
            path=xs_ledger(panels['open'],fund_daily,w,cost);r=daily_returns(path);cash=accrual_reference(rates,r.index)
            audits={str(b):uncertainty(r-cash,np.zeros(len(r)),20260908+200+j,trials=trials,samples=10000,block=b) for b in [7,30,60]}
            years={str(y):float((1+x).prod()-1) for y,x in r.groupby(r.index.year)}
            cases[case]=dict(metrics=performance(path),excess_uncertainty=audits,leave_one_year_out_positive=all(sum(v for k,v in years.items() if k!=y)>0 for y in years),
                passes_all_adjusted_bounds=all(a['simultaneous_lower_mean_daily']>0 for a in audits.values()))
            r.to_csv(out/f'{j}_{case}_daily_returns.csv')
        delayed=performance(xs_ledger(panels['open'],fund_daily,w,.0014,delay=DELAY+1))
        verdict='RESEARCH-PROMISING ONLY' if cases['stress']['passes_all_adjusted_bounds'] and delayed['cagr']>0 and cases['stress']['leave_one_year_out_positive'] else 'REJECTED FOR PROMOTION'
        results.append(dict(candidate=c,cases=cases,extra_day_delay_stress=delayed,capital=capital_feasibility(w,panels['open']),verdict=verdict))
        print(c,verdict,flush=True)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=20260908,source=str(source.relative_to(ROOT)),
        multiplicity_trials=trials,rate_reference=rate_meta,results=results,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
