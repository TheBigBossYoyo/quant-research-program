"""Uncertainty audit of registered development survivors, then fixed validation.

No final-test loading. Predeclared multiplicity correction across all 70 screens.
"""
import sys
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from core import ROOT, config, code_hash, load_data, aggregate, signal, simulate, metrics

def daily(b):
    return (1+b.net).resample('1D').prod()-1

def uncertainty(r, benchmark, seed, trials=70, samples=4000, block=14):
    """Circular daily block bootstrap of mean and OLS intercept versus buyhold.

    Exploratory stationary-within-sample approximation; not proof of stationarity.
    Alpha estimated within each resample. Bonferroni one-sided bound across trials.
    """
    y=np.asarray(r); x=np.asarray(benchmark)
    assert len(y)==len(x) and np.isfinite(y).all() and np.isfinite(x).all()
    rng=np.random.default_rng(seed); n=len(y)
    starts=rng.integers(0,n,size=(samples,int(np.ceil(n/block))))
    idx=((starts[:,:,None]+np.arange(block))%n).reshape(samples,-1)[:,:n]
    by=y[idx]; bx=x[idx]
    mean=by.mean(axis=1); xm=bx.mean(axis=1)
    cov=np.mean((by-mean[:,None])*(bx-xm[:,None]),axis=1)
    var=np.mean((bx-xm[:,None])**2,axis=1)
    beta=np.divide(cov,var,out=np.zeros_like(cov),where=var>0)
    alpha=(mean-beta*xm)*365.25
    sd=by.std(axis=1,ddof=1)
    sharpe=np.divide(mean,sd,out=np.zeros_like(mean),where=sd>0)*np.sqrt(365.25)
    q=.05/trials
    return dict(block_days=block, samples=samples, seed=seed, multiplicity_trials=trials,
        mean_daily_ci95=np.quantile(mean,[.025,.975]).tolist(),
        sharpe_ci95=np.quantile(sharpe,[.025,.975]).tolist(),
        arithmetic_alpha_annual_ci95=np.quantile(alpha,[.025,.975]).tolist(),
        simultaneous_lower_mean_daily=float(np.quantile(mean,q)),
        simultaneous_lower_alpha_annual=float(np.quantile(alpha,q)),
        warning='Extreme adjusted quantile has few bootstrap tail draws; approximate and cannot establish nonstationarity robustness.')

def main():
    cfg=config(); source=sys.argv[1]
    original=json.loads((ROOT/source/'results.json').read_text())
    eid='E002_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid; out.mkdir(parents=True,exist_ok=False)
    results=[]
    for j,p in enumerate(original['survivors']):
        raw,check=load_data(p['symbol'])
        d=aggregate(raw,p['minutes']); s=signal(d,p['family'],p['lookback'])
        b=simulate(d,s,12); bench=simulate(d,signal(d,'buyhold',0),12)
        u=uncertainty(daily(b),daily(bench),cfg['seed']+j)
        # Additional delay is adversarial, not a retuning opportunity.
        delay_stress=metrics(simulate(d,s,24,delay=3),p['minutes'])
        passed=u['simultaneous_lower_mean_daily']>0 and u['simultaneous_lower_alpha_annual']>0 and delay_stress['cumulative_return']>0
        result=dict(candidate=p,development_uncertainty=u,extra_delay_stress=delay_stress,
                    development_audit_pass=passed, validation=None,
                    verdict='REJECTED FOR PROMOTION' if not passed else 'AWAITING VALIDATION')
        # Preserve scarce validation until statistical screen is credible.
        if passed:
            full,vi=load_data(p['symbol'],validation=True)
            full=aggregate(full,p['minutes']); sf=signal(full,p['family'],p['lookback'])
            val=full.loc[cfg['train_end_exclusive']:]
            # Precomputed historical signals remain causal; start validation in cash.
            sv=sf.loc[val.index]
            vb=simulate(val,sv,12); vbench=simulate(val,signal(val,'buyhold',0),12)
            vu=uncertainty(daily(vb),daily(vbench),cfg['seed']+100+j)
            result['validation']=dict(base=metrics(vb,p['minutes']),
                stress=metrics(simulate(val,sv,24),p['minutes']),uncertainty=vu,
                integrity=vi)
            result['verdict']='RESEARCH-PROMISING' if (result['validation']['stress']['cumulative_return']>0 and vu['simultaneous_lower_alpha_annual']>0) else 'REJECTED FOR PROMOTION'
        results.append(result)
        print(p,result['verdict'],flush=True)
    payload=dict(experiment_id=eid,source=source,source_code_hash=original['code_hash'],
                 code_hash=code_hash(),git_commit=None,seed=cfg['seed'],results=results,
                 final_test_accessed=False,validation_accessed=any(r['validation'] is not None for r in results))
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__': main()
