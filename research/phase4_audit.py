"""E042: original reproduction and approved signal-preserving accounting audit."""
import sys,json,hashlib
import numpy as np,pandas as pd
from core import ROOT
from ta_data import load_hourly,bars
from perpetual_screen import prepare
from ta_ensemble import ensemble_weight,fractional_ledger
from ta_volcomp import breakout_state
from ta_engine import atr,run_ledger
from ta_stats import daily_returns
from ta_screen import COSTS
from phase4_engine import aggregate,signals,ledger,combine

def perf(r):
    e=(1+r).cumprod();return dict(cagr=float(e.iloc[-1]**(365/len(r))-1),sharpe=float(r.mean()/r.std()*np.sqrt(365)),max_dd=float((e/e.cummax().clip(lower=1)-1).min()))

def main():
    out=ROOT/'reports'/(ROOT/'reports/PHASE4_ACTIVE_AUDIT.txt').read_text().strip();rows=[]
    for sym in ['BTCUSDT','ETHUSDT']:
        h=load_hourly(sym,'perp');_,_,f,_=prepare(sym)
        f=f.reindex(h.index).fillna(0).resample('4h',origin='epoch').sum()
        old=bars(h,'4h');b=aggregate(h);sg=signals(b);cost=COSTS['perp']['stress']
        a=atr(old,14);c=(a.rolling(250,min_periods=120).rank(pct=True)<.2).shift(1).fillna(False)
        legacy={'trend':fractional_ledger(old,ensemble_weight(old.close),cost,funding=f),'breakout':run_ledger(old,breakout_state(old,20,c),cost,stop_atr=3.,atr_series=a,trail=True,funding=f)[0]}
        new={};rr={};or_={}
        for component in ['trend','breakout']:
            pd.testing.assert_series_equal(sg[component],ensemble_weight(old.close) if component=='trend' else breakout_state(old,20,c))
            p,tr=ledger(b,sg[component],cost,component,f,sg['atr']);new[component]=p
            p.to_csv(out/f'{sym}_{component}_corrected_path.csv');tr.to_csv(out/f'{sym}_{component}_net_trades.csv',index=False)
            rr[component]=daily_returns(p);or_[component]=daily_returns(legacy[component])
            rows.append(dict(symbol=sym,component=component,old=perf(or_[component]),corrected=perf(rr[component]),max_abs_equity_difference=float((p.equity-legacy[component].equity).abs().max()),max_gross=float(p.position.abs().max()),ruin=bool(p.ruin.any())))
        for method in ['equal','inverse_vol']:
            r,w=combine(rr['trend'],rr['breakout'],method);ro,_=combine(or_['trend'],or_['breakout'],method)
            rows.append(dict(symbol=sym,component=method,old=perf(ro),corrected=perf(r)))
            pd.DataFrame(dict(original=ro,corrected=r,trend_weight=w)).to_csv(out/f'{sym}_{method}_daily.csv')
        print(sym,[r for r in rows if r['symbol']==sym],flush=True)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'research').glob('*.py'))}
    result=dict(experiment_id=out.name,classification='ACCOUNTING_AUDIT_ONLY',additional_economic_hypotheses=0,cumulative_economic_hypotheses=384,seed=None,cost=.000905,source_hashes=manifest,rows=rows,signal_equality=True,original_reproduction_exact=True,replication_evaluated=False,validation_accessed=False,final_test_accessed=False,funding_note='Legacy inputs retained to isolate accounting. Pre-2022 funding absent; intrabar/jitter placement remains unresolved until event-source audit.')
    (out/'results.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
