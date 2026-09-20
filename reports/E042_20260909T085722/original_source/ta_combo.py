"""E040: two-component ensemble test — slow-trend plateau ensemble (E035) + compression breakout (E038) on perp BTC/ETH 4h. Development only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars
from ta_engine import run_ledger,metrics,buy_hold,atr
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe
from ta_screen import COSTS,BPY
from ta_ensemble import ensemble_weight,fractional_ledger
from ta_volcomp import breakout_state
from ta_audit import alpha_vs_bh
from perpetual_screen import prepare as perp_prepare

def main():
    eid='E040_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[];cost=COSTS['perp']['stress']
    for sym in ['BTCUSDT','ETHUSDT']:
        hourly=load_hourly(sym,'perp');_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.);b=bars(hourly,'4h');fnd=funding.resample('4h',label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.)
        pa=fractional_ledger(b,ensemble_weight(b.close),cost,funding=fnd);ra=daily_returns(pa)
        a14=atr(b,14);pct=a14.rolling(250,min_periods=120).rank(pct=True);comp=(pct<.2).shift(1).fillna(False);pb,trb=run_ledger(b,breakout_state(b,20,comp),cost,stop_atr=3.,atr_series=a14,trail=True,funding=fnd);rb=daily_returns(pb)
        bh_path,bh_tr=buy_hold(b,cost);rbh=daily_returns(bh_path);idx=ra.index.intersection(rb.index);ra,rb,rbh=ra.reindex(idx).fillna(0),rb.reindex(idx).fillna(0),rbh.reindex(idx).fillna(0)
        corr=float(ra.corr(rb));ea=(1+ra).cumprod();eb=(1+rb).cumprod();dd_a=ea/ea.cummax()-1;dd_b=eb/eb.cummax()-1;overlap=float(((dd_a<-.1)&(dd_b<-.1)).mean())
        combos={'equal':.5*ra+.5*rb}
        va=ra.rolling(60).std().shift(1);vb=rb.rolling(60).std().shift(1);wa=(1/va)/((1/va)+(1/vb));combos['inverse_vol']=(wa*ra+(1-wa)*rb).fillna(0)
        def perf(r):
            e=(1+r).cumprod();years=len(r)/365;return dict(cagr=float(e.iloc[-1]**(1/years)-1),sharpe=float(r.mean()/r.std()*np.sqrt(365)) if r.std()>0 else 0.,max_dd=float((e/e.cummax()-1).min()),positive_years=float(np.mean([(1+x).prod()>1 for _,x in r.groupby(r.index.year)])))
        comp_perf={'trend':perf(ra),'breakout':perf(rb),'buy_hold':perf(rbh)};res={}
        for name,r in combos.items():
            p=perf(r);boot=block_bootstrap_sharpe(r.to_numpy(),seed=7);al=alpha_vs_bh(r,rbh);dsr=deflated_sharpe(boot['sharpe'],len(r),2,r.to_numpy())
            best=max(comp_perf['trend']['sharpe'],comp_perf['breakout']['sharpe']);gate=dict(sharpe_gain=p['sharpe']-best>=.15,alpha=al['alpha_ci95'][0]>0,drawdown=p['max_dd']>max(comp_perf['trend']['max_dd'],comp_perf['breakout']['max_dd']),correlation=corr<.5)
            res[name]=dict(perf=p,bootstrap=boot,alpha=al,dsr=dsr['dsr'],gates=gate,all=all(gate.values()))
        results.append(dict(symbol=sym,correlation=corr,drawdown_overlap=overlap,components=comp_perf,combinations=res))
        print(sym,'corr',round(corr,2),'overlap',round(overlap,2),'trend',{k:round(v,2) for k,v in comp_perf['trend'].items()},'breakout',{k:round(v,2) for k,v in comp_perf['breakout'].items()},{n:(round(x['perf']['sharpe'],2),round(x['perf']['max_dd'],2),round(x['alpha']['alpha_annual'],2),[round(y,2) for y in x['alpha']['alpha_ci95']],x['gates']) for n,x in res.items()},flush=True)
    verdict='PORTFOLIO_COMPONENT_CANDIDATE' if all(any(x['all'] for x in r['combinations'].values()) for r in results) else 'WEAK_SIGNAL'
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,results=results,verdict=verdict,validation_accessed=False,final_test_accessed=False),indent=2,default=float));print('OUTPUT',out,verdict)

if __name__=='__main__':main()
