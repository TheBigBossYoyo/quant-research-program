"""Falsification audit of corrected directional-perpetual survivors."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from perpetual_screen import prepare,signed_ledger,performance
from economic_audit import reference,accrual_reference
from audit import uncertainty

def daily(path):
    n=path.nav.resample('1D').last();r=n.pct_change();r.iloc[0]=n.iloc[0]/500-1
    return r

def main():
    eid='E011_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'reports/E010_20260908T171214/results.json';screen=json.loads(source.read_text())
    rates,rate_meta=reference('DGS3MO');results=[]
    for j,c in enumerate(screen['survivors']):
        f,px,funding,meta=prepare(c['symbol']);tf=c['timeframe_hours']
        close=f.close.resample(f'{tf}h').last()
        raw=close/close.shift(c['lookback'])-1
        if c['family']=='reversal':raw=-raw
        target=np.sign(raw).shift(2).fillna(0).reindex(px.index).ffill().fillna(0)
        delayed=np.sign(raw).shift(3).fillna(0).reindex(px.index).ffill().fillna(0)
        long=pd.Series(1.,index=close.index).shift(2).fillna(0).reindex(px.index).ffill().fillna(0)
        mn=50 if c['symbol']=='BTCUSDT' else 20
        cases={}
        for case,fee in [('base',.0007),('stress',.0014)]:
            path=signed_ledger(px,target,funding,fee=fee,min_notional=mn)
            bench=signed_ledger(px,long,funding,fee=fee,min_notional=mn)
            r=daily(path);br=daily(bench);cash=accrual_reference(rates,r.index)
            audits={str(block):uncertainty(r-cash,br-cash,20260908+j,trials=119,samples=10000,block=block) for block in [7,30,60]}
            cases[case]=dict(metrics=performance(path),uncertainty_excess_vs_reference_and_long_baseline=audits,
                passes_all_adjusted_bounds=all(a['simultaneous_lower_mean_daily']>0 and a['simultaneous_lower_alpha_annual']>0 for a in audits.values()))
            r.to_csv(out/f'{j}_{case}_daily_returns.csv')
        stress_delay=performance(signed_ledger(px,delayed,funding,fee=.0014,min_notional=mn))
        decision='RESEARCH-PROMISING ONLY' if cases['stress']['passes_all_adjusted_bounds'] and stress_delay['cagr']>0 and not stress_delay['halted'] else 'REJECTED FOR PROMOTION'
        results.append(dict(candidate=c,cases=cases,additional_delay_stress=stress_delay,verdict=decision))
        print(c,decision,flush=True)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=20260908,source=str(source.relative_to(ROOT)),rate_reference=rate_meta,
        results=results,cumulative_hypotheses=119,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
