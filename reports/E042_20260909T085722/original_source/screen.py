"""Registered development screen. Never loads validation/final data."""
from datetime import datetime, timezone
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from core import ROOT, config, code_hash, load_data, aggregate, signal, simulate, metrics

def main():
    cfg = config()
    eid = 'E001_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out = ROOT/'reports'/eid
    out.mkdir(parents=True, exist_ok=False)
    rows, integrity, diagnostics = [], [], []
    for sym in cfg['symbols']:
        raw, check = load_data(sym)
        integrity.append(check)
        for tf in cfg['timeframes_minutes']:
            d = aggregate(raw, tf)
            candidates = [(f,n) for f in ('momentum','reversal') for n in cfg['lookbacks_bars']]
            candidates += [('flow',1), ('sma',20), ('buyhold',0)]
            for family,n in candidates:
                s = signal(d,family,n)
                target = d.execution_open.shift(-3)/d.execution_open.shift(-2)-1
                valid = s.notna() & target.notna()
                ic = float(spearmanr(s[valid],target[valid]).statistic) if family != 'buyhold' else None
                diagnostics.append(dict(symbol=sym, minutes=tf, family=family, lookback=n,
                    spearman_ic=ic, observations=int(valid.sum()),
                    directional_accuracy=float(((s[valid]>0)==(target[valid]>0)).mean()),
                    conditional_long_mean_bps=float(target[valid & (s>0)].mean()*1e4),
                    signal_autocorrelation=float(s.autocorr()) if family != 'buyhold' else None))
                for case,cost in cfg['one_way_cost_bps'].items():
                    m = metrics(simulate(d,s,cost),tf)
                    rows.append(dict(symbol=sym, minutes=tf, family=family, lookback=n, case=case, cost_bps=cost, **m))
            print(sym,tf,'screened',flush=True)
    survivors = []
    for r in rows:
        if r['case'] != 'stress' or r['family'] in ('buyhold','sma'):
            continue
        bench = next(x for x in rows if x['symbol']==r['symbol'] and x['minutes']==r['minutes'] and x['family']=='buyhold' and x['case']=='stress')
        if (r['cumulative_return'] > 0 and r['sharpe'] > max(0.,bench['sharpe'])
            and sum(v>0 for v in r['calendar_returns'].values()) >= 2):
            survivors.append({k:r[k] for k in ('symbol','minutes','family','lookback')})
    result = dict(experiment_id=eid, code_hash=code_hash(), git_commit=None, config=cfg,
                  split='development 2022-2024 only', seed=cfg['seed'],
                  signal_asset_trials=70, baseline_asset_trials=20, rows=rows,
                  survivors=survivors, diagnostics=diagnostics, integrity=integrity,
                  status='PROVISIONAL SCREEN ONLY; NO PROMOTION')
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out, 'SURVIVORS',json.dumps(survivors),flush=True)

if __name__ == '__main__':
    main()
