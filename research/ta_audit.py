"""E034: audit of the slow-trend regime cells reached in E032 — alpha vs buy-and-hold, textbook DSR, crashes,
concentration, Monte Carlo, vol-managed benchmark. Parameters frozen as selected in E032; development only."""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars
from ta_engine import run_ledger,metrics,buy_hold,sma,atr
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe
from ta_screen import COSTS,BPY
from perpetual_screen import prepare as perp_prepare

CELLS=[('perp','BTCUSDT','4h','A1',dict(slow=250)),('perp','BTCUSDT','4h','A3',dict(ma=200)),('perp','ETHUSDT','4h','A1',dict(slow=150)),('perp','ETHUSDT','1D','A4',dict(slow=200,cap_atr=4)),('spot','BTCUSDT','4h','A3',dict(ma=200)),('spot','ETHUSDT','4h','A1',dict(slow=200))]
CRASHES={'2018_bear':('2018-01-01','2018-12-31'),'covid_2020':('2020-02-15','2020-04-15'),'may_2021':('2021-05-01','2021-07-31'),'bear_2022':('2022-01-01','2022-12-31')}

def target_for(arch,b,p):
    c=b.close
    if arch=='A1':return np.sign(c-sma(c,p['slow']))
    if arch=='A3':m=sma(c,p['ma']);return np.sign(m-m.shift(5))
    if arch=='A4':m=sma(c,p['slow']);d=(c-m)/atr(b,14);return np.sign(c-m).where(d.abs()<p['cap_atr'],0.)

def alpha_vs_bh(r,rb,samples=5000,block=7,seed=0):
    x=rb.reindex(r.index).fillna(0).to_numpy();y=r.to_numpy();n=len(y);rng=np.random.default_rng(seed)
    def fit(yy,xx):b=np.cov(yy,xx)[0,1]/np.var(xx) if np.var(xx)>0 else 0.;return (yy.mean()-b*xx.mean())*365,b
    a,beta=fit(y,x);starts=rng.integers(0,n,size=(samples,int(np.ceil(n/block))));idx=((starts[:,:,None]+np.arange(block))%n).reshape(samples,-1)[:,:n]
    draws=np.array([fit(y[i],x[i])[0] for i in idx]);return dict(alpha_annual=float(a),beta=float(beta),alpha_ci95=np.quantile(draws,[.025,.975]).tolist(),alpha_p_one_sided=float(np.mean(draws<=0)))

def monte_carlo(trades,r,seed=0,samples=5000):
    rng=np.random.default_rng(seed);tr=trades.ret.to_numpy();n=len(tr)
    if n<10:return None
    res=np.array([np.prod(1+rng.choice(tr,n,replace=True))-1 for _ in range(samples)]);x=r.to_numpy();m=len(x);block=7
    starts=rng.integers(0,m,size=(samples,int(np.ceil(m/block))));idx=((starts[:,:,None]+np.arange(block))%m).reshape(samples,-1)[:,:m];bx=x[idx]
    eq=np.cumprod(1+bx,axis=1);dd=(eq/np.maximum.accumulate(eq,axis=1)-1).min(axis=1);sh=bx.mean(axis=1)/bx.std(axis=1)*np.sqrt(365)
    return dict(trade_resample_total_return_q05_q50_q95=np.quantile(res,[.05,.5,.95]).tolist(),block_sharpe_q05_q50_q95=np.quantile(sh,[.05,.5,.95]).tolist(),
        max_dd_q05_q50_q95=np.quantile(dd,[.05,.5,.95]).tolist(),p_dd_worse_than={str(k):float(np.mean(dd<-k)) for k in [.2,.3,.5]})

def main():
    source=ROOT/sys.argv[1];screen=json.loads((source/'results.json').read_text());fam=screen['architecture_trials']
    eid='E034_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[]
    C=pd.read_csv(source/'stage_c.csv');sr_daily=(C.sharpe/np.sqrt(365)).to_numpy();var_trials=float(np.var(sr_daily))
    cache={}
    for kind,sym,tf,arch,p in CELLS:
        if (kind,sym) not in cache:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            cache[(kind,sym)]=(hourly,funding)
        hourly,funding=cache[(kind,sym)];b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
        cost=COSTS[kind]['stress'];a14=atr(b,14);target=target_for(arch,b,p)
        path,tr=run_ledger(b,target,cost,funding=fnd,long_only=(kind=='spot'));m=metrics(path,tr,BPY[tf]);r=daily_returns(path)
        bh_path,bh_tr=buy_hold(b,cost);rb=daily_returns(bh_path);bhm=metrics(bh_path,bh_tr,BPY[tf])
        # vol-managed buy-and-hold: size = min(1, 20%/trailing 30-bar realised vol), long-only, same costs
        lr=np.log(b.close/b.close.shift(1));v=lr.rolling(30).std()*np.sqrt(BPY[tf]);size=(0.2/v).clip(upper=1.)
        vm_path,vm_tr=run_ledger(b,pd.Series(1.,index=b.index),cost,size=size,long_only=True);vmm=metrics(vm_path,vm_tr,BPY[tf])
        boot=block_bootstrap_sharpe(r.to_numpy(),seed=1);dsr_cons=deflated_sharpe(boot['sharpe'],len(r),fam,r.to_numpy());dsr_text=deflated_sharpe(boot['sharpe'],len(r),fam,r.to_numpy(),var_trials=var_trials)
        al=alpha_vs_bh(r,rb);e=path.equity
        crashes={}
        for name,(s0,s1) in CRASHES.items():
            seg=e.loc[s0:s1];pos=path.position.loc[s0:s1]
            if len(seg)<10:continue
            crashes[name]=dict(strategy_return=float(seg.iloc[-1]/seg.iloc[0]-1),buy_hold_return=float(bh_path.equity.loc[s0:s1].iloc[-1]/bh_path.equity.loc[s0:s1].iloc[0]-1),worst_30d=float((seg/seg.rolling(30*BPY[tf]//365 if tf=='1D' else 30*6 if tf=='4h' else 30*24,min_periods=2).max()-1).min()),mean_exposure=float(pos.abs().mean()))
        yearly=pd.Series(m['calendar']);pnl_by_year=e.groupby(e.index.year).apply(lambda s:s.iloc[-1]-s.iloc[0]);top_year=str(pnl_by_year.idxmax())
        conc=dict(top5_trade_share=m['top5_trade_share'],top_year=top_year,top_year_share=float(pnl_by_year.max()/pnl_by_year[pnl_by_year>0].sum()) if (pnl_by_year>0).any() else None,
            cagr_ex_top_year=float(np.prod([1+v for y,v in m['calendar'].items() if y!=top_year])**(1/max(len(m['calendar'])-1,1))-1))
        turnover=float(tr.ret.abs().count()*2*cost) if len(tr) else 0.;gross=float(m['cagr']+2*cost*m['trades_per_year'])
        results.append(dict(cell=dict(kind=kind,symbol=sym,tf=tf,arch=arch,params=p),stressed=m,buy_hold=bhm,vol_managed_bh=vmm,bootstrap=boot,dsr_conservative=dsr_cons,dsr_textbook=dsr_text,trial_sharpe_variance=var_trials,
            alpha_vs_buy_hold=al,crashes=crashes,concentration=conc,monte_carlo=monte_carlo(tr,r,seed=2),cost_ratio=float(2*cost*m['trades_per_year']/max(gross,1e-9)),
            classification=('PORTFOLIO_COMPONENT_CANDIDATE' if (al['alpha_ci95'][0]>0 and dsr_text['dsr']>=.95 and m['sharpe']>vmm['sharpe']) else 'WEAK_SIGNAL')))
        print(kind,sym,tf,arch,p,'sharpe',round(m['sharpe'],2),'alpha',round(al['alpha_annual'],3),'ci',[round(x,3) for x in al['alpha_ci95']],'beta',round(al['beta'],2),'dsr cons/text',round(dsr_cons['dsr'],3),round(dsr_text['dsr'],3),'volmgd BH sharpe',round(vmm['sharpe'],2),'->',results[-1]['classification'],flush=True)
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,source=str(source.relative_to(ROOT)),family_trials=fam,results=results,validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,[r['classification'] for r in results])

if __name__=='__main__':main()
