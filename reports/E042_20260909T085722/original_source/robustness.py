"""Post-screen falsification; no retuning, validation or final-test access."""
import json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from core import ROOT,config,code_hash,load_data,aggregate,signal,simulate,metrics
from audit import daily,uncertainty

def drawdown_risk(r,seed,paths=4000,block=14):
    rng=np.random.default_rng(seed); x=np.asarray(r); n=365
    starts=rng.integers(0,len(x),size=(paths,int(np.ceil(n/block))))
    idx=((starts[:,:,None]+np.arange(block))%len(x)).reshape(paths,-1)[:,:n]
    e=np.cumprod(1+x[idx],axis=1)
    peaks=np.maximum.accumulate(np.c_[np.ones(paths),e],axis=1)[:,1:]
    worst=(e/peaks-1).min(axis=1)
    terminal=e[:,-1]-1
    return dict(paths=paths,horizon_days=365,block_days=block,seed=seed,
        probability_max_drawdown_exceeds={str(k):float(np.mean(worst < -k)) for k in [.1,.2,.3,.5]},
        probability_terminal_loss_exceeds={str(k):float(np.mean(terminal < -k)) for k in [.1,.2,.3,.5]},
        max_drawdown_quantiles=np.quantile(worst,[.05,.5,.95]).tolist(),
        warning='Conditional resampling of 2022-2024, not calibrated future probabilities; no leveraged liquidation model.')

def main():
    cfg=config(); eid='E003_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    rows=[];audits=[];liquidity=[]
    for j,sym in enumerate(cfg['symbols']):
        raw,integ=load_data(sym);d=aggregate(raw,1440)
        q=raw.quote_volume.dropna()
        liquidity.append(dict(symbol=sym,quote_volume_5m_quantiles=q.quantile([.01,.05,.5]).to_dict(),
            conservative_0_1pct_of_p1_quote_volume_usdt=float(q.quantile(.01)*.001),
            fraction_500_usdt_of_p1_volume=float(500/q.quantile(.01)),
            note='Historical bar volume only; not depth or guaranteed capacity. Zero-volume intervals are not tradable.'))
        for n in [36,42,48,54,60]:
            for delay in [2,3,4]:
                b=simulate(d,signal(d,'momentum',n),24,delay=delay)
                rows.append(dict(symbol=sym,lookback=n,delay=delay,cost_bps=24,**metrics(b,1440)))
        s=signal(d,'momentum',48); b=simulate(d,s,12)
        benchmark=simulate(d,signal(d,'buyhold',0),12)
        regimes={}
        trailing=d.close/d.close.shift(90)-1
        vol=d.close.pct_change(fill_method=None).rolling(20).std()*np.sqrt(365.25)
        # Fixed absolute classifications, available at signal time; descriptive only.
        labels=pd.Series('sideways',index=d.index)
        labels.loc[trailing>.10]='rising';labels.loc[trailing<-.10]='falling'
        labels.loc[trailing.isna()]='unknown'
        labels=labels.shift(2).fillna('unknown')
        vr=(vol>.60).shift(2)
        for label in ['rising','falling','sideways','unknown']:
            rr=b.net[labels==label]
            regimes[label]=dict(days=len(rr),arithmetic_mean_daily=float(rr.mean()),
                compounded_selected_days=float((1+rr).prod()-1),note='Selected disjoint days, not separately tradable equity.')
        for label,mask in [('high_vol',vr==True),('low_vol',vr==False)]:
            rr=b.net[mask];regimes[label]=dict(days=len(rr),arithmetic_mean_daily=float(rr.mean()))
        audits.append(dict(symbol=sym,candidate='daily momentum48',
            uncertainty_by_block={str(k):uncertainty(daily(b),daily(benchmark),cfg['seed']+j, trials=78,block=k) for k in [7,30,60]},
            unlevered_drawdown_risk=drawdown_risk(daily(b),cfg['seed']+j),regimes=regimes))
        print(sym,'robustness complete',flush=True)
    result=dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=cfg['seed'],
        dataset='Same checksum-verified development archives as E001; 2022-2024 only',
        additional_signal_asset_trials=8,total_signal_asset_trials=78,
        rows=rows,audits=audits,liquidity=liquidity,
        verdict='FALSIFICATION ONLY; cannot promote or replace original parameters',
        validation_accessed=False,final_test_accessed=False)
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in rows]).to_csv(out/'parameter_surface.csv',index=False)
    print('OUTPUT',out)

if __name__=='__main__':main()
