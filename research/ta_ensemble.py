"""E035: unselected plateau ensemble of the slow-trend neighbourhood (one rule, eight cells). Development only.

Fractional-weight ledger: weight w_t in [-1,1] decided at the close of bar t is executed at the open of bar t+1
(units rebalanced when w changes); cost on |delta units| x open; marked at close; signed funding per bar.
"""
import json,hashlib
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars,SYMBOLS
from ta_engine import sma,metrics,buy_hold
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe
from ta_screen import COSTS,BPY
from ta_audit import alpha_vs_bh,monte_carlo
from perpetual_screen import prepare as perp_prepare

SLOW=[150,200,250];SLOPE=[100,150,200,250];N_ARCH=11

def ensemble_weight(close):
    s=[np.sign(close-sma(close,n)) for n in SLOW]+[np.sign(sma(close,n)-sma(close,n).shift(5)) for n in SLOPE]
    return pd.concat(s,axis=1).mean(axis=1)

def fractional_ledger(b,w,cost,funding=None,long_only=False,initial=10000.):
    o=b.open.to_numpy();c=b.close.to_numpy();tr=b.tradable.to_numpy();wt=w.fillna(0.).clip(-1,1).to_numpy();fnd=funding.reindex(b.index).fillna(0).to_numpy() if funding is not None else np.zeros(len(b))
    if long_only:wt=np.clip(wt,0,1)
    eq=initial;units=0.;target_w=0.;held_w=0.;rows=[];turn=0.
    for i in range(len(b)):
        if not np.isfinite(o[i]):rows.append(dict(time=b.index[i],equity=eq,position=target_w,turnover=0.));continue
        eq_open=eq+units*(o[i]-c[i-1]) if i>0 and np.isfinite(c[i-1]) else eq
        t=0.
        if tr[i] and target_w!=held_w:  # trade only when the target weight changes; no drift rebalancing
            new_units=target_w*eq_open/o[i] if target_w!=0 else 0.;delta=new_units-units;t=abs(delta)*o[i]
            eq_open-=t*cost;units=new_units;held_w=target_w
        eq=eq_open+units*(c[i]-o[i])-units*fnd[i]
        rows.append(dict(time=b.index[i],equity=eq,position=units*c[i]/eq if eq>0 else 0.,turnover=t))
        target_w=wt[i]
    return pd.DataFrame(rows).set_index('time')

def vol_managed_bh(b,cost,tf,target=.20):
    lr=np.log(b.close/b.close.shift(1));v=lr.rolling(30).std()*np.sqrt(BPY[tf]);w=(target/v).clip(upper=1.)
    return fractional_ledger(b,w,cost,long_only=True)

def main():
    eid='E035_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[]
    var_trials=float(np.var((pd.read_csv(ROOT/'reports/E032_20260909T073600/stage_c.csv').sharpe/np.sqrt(365)).to_numpy()))
    for kind in ['perp','spot']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            for tf in ['4h','1D']:
                b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                w=ensemble_weight(b.close);cases={}
                for case,cost in COSTS[kind].items():
                    path=fractional_ledger(b,w,cost,funding=fnd,long_only=(kind=='spot'));tr=pd.DataFrame(columns=['ret','bars']);m=metrics(path,tr,BPY[tf]);m['annual_turnover']=float(path.turnover.sum()/path.equity.mean()/(len(path)/BPY[tf]))
                    cases[case]=m
                    if case=='stress':
                        r=daily_returns(path);bh_path,bh_tr=buy_hold(b,cost);rb=daily_returns(bh_path);bhm=metrics(bh_path,bh_tr,BPY[tf]);vm=metrics(vol_managed_bh(b,cost,tf),tr,BPY[tf])
                        boot=block_bootstrap_sharpe(r.to_numpy(),seed=3);al=alpha_vs_bh(r,rb);dsr=deflated_sharpe(boot['sharpe'],len(r),N_ARCH,r.to_numpy(),var_trials=var_trials)
                        e=path.equity;yr=e.groupby(e.index.year).apply(lambda s:s.iloc[-1]-s.iloc[0]);top_share=float(yr.max()/yr[yr>0].sum()) if (yr>0).any() else None
                        # yearly alpha sign: intercept per calendar year
                        ya={str(y):float(alpha_vs_bh(r[r.index.year==y],rb,samples=200)['alpha_annual']) for y in sorted(set(r.index.year)) if (r.index.year==y).sum()>60}
                        mc=monte_carlo(pd.DataFrame(dict(ret=r.to_numpy()[r.to_numpy()!=0])),r,seed=4)
                        gates=dict(sharpe=m['sharpe']>.5 and m['sharpe']>bhm['sharpe'],alpha=al['alpha_ci95'][0]>0,alpha_years=float(np.mean([v>0 for v in ya.values()]))>=.6 if ya else False,dsr=dsr['dsr']>=.95,vol_managed=m['sharpe']>vm['sharpe'],concentration=(top_share or 1)<.6)
                        path.to_csv(out/f'{kind}_{sym}_{tf}_stress_path.csv')
                results.append(dict(kind=kind,symbol=sym,tf=tf,cases=cases,buy_hold=bhm,vol_managed_bh=vm,bootstrap=boot,alpha=al,alpha_by_year=ya,dsr_textbook_N11=dsr,top_year_share=top_share,monte_carlo=mc,gates=gates,all_gates=all(gates.values())))
                print(kind,sym,tf,'stress sharpe',round(cases['stress']['sharpe'],2),'cagr',round(cases['stress']['cagr'],2),'dd',round(cases['stress']['max_dd'],2),'BH',round(bhm['sharpe'],2),'volmgd',round(vm['sharpe'],2),'alpha',round(al['alpha_annual'],2),[round(x,2) for x in al['alpha_ci95']],'dsr',round(dsr['dsr'],3),'gates',gates,flush=True)
    passes=sum(r['all_gates'] for r in results);perp_pass=sum(r['all_gates'] for r in results if r['kind']=='perp')
    sharpe_ok=sum(r['gates']['sharpe'] for r in results)>=6;alpha_ok=sum(r['gates']['alpha'] for r in results)>=6
    verdict='VALIDATION-CANDIDATE' if (sharpe_ok and alpha_ok and all(r['gates']['dsr'] for r in results if r['kind']=='perp') and all(r['gates']['vol_managed'] and r['gates']['concentration'] and r['gates']['alpha_years'] for r in results)) else ('PORTFOLIO_COMPONENT_CANDIDATE' if alpha_ok else 'WEAK_SIGNAL')
    assert starting==code_hash()
    rule=dict(rule='mean of sign(close-SMA_n) for n in 150/200/250 and sign(SMA_n - SMA_n[-5]) for n in 100/150/200/250; fractional exposure; next-open execution; no stops; unlevered; spot long-only',cells=[(r['kind'],r['symbol'],r['tf']) for r in results])
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,rule=rule,rule_hash=hashlib.sha256(json.dumps(rule,sort_keys=True).encode()).hexdigest(),architecture_count_for_dsr=N_ARCH,trial_sharpe_variance=var_trials,results=results,verdict=verdict,validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,'VERDICT',verdict,'cells passing all gates',passes)

if __name__=='__main__':main()
