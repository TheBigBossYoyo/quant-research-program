"""E041: regularized alpha stacking (ridge / ridge-logistic, yearly expanding refit) vs the E040 equal-weight baseline. perp BTC/ETH 4h."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars
from ta_engine import run_ledger,metrics,buy_hold,sma,atr,rsi
from ta_stats import daily_returns,block_bootstrap_sharpe
from ta_screen import COSTS,BPY
from ta_ensemble import ensemble_weight,fractional_ledger
from ta_volcomp import breakout_state
from ta_audit import alpha_vs_bh
from perpetual_screen import prepare as perp_prepare

ALPHA=10.;DEAD=.1;FIRST_OOS=2022

def features(b):
    c=b.close;a=atr(b,14);F=pd.DataFrame(index=b.index)
    for n in [150,200,250]:F[f'sign_sma{n}']=np.sign(c-sma(c,n))
    for n in [100,150,200,250]:F[f'slope{n}']=np.sign(sma(c,n)-sma(c,n).shift(5))
    F['ens']=ensemble_weight(c);pct=a.rolling(250,min_periods=120).rank(pct=True);F['comp_break']=breakout_state(b,20,(pct<.2).shift(1).fillna(False))
    for n in [20,50,100]:F[f'ret{n}']=c/c.shift(n)-1
    F['dist50']=(c-sma(c,50))/a;F['dist200']=(c-sma(c,200))/a;F['rsi']=rsi(c,14)/100-.5;rng=(b.high-b.low).replace(0,np.nan);F['body']=(c-b.open)/rng;F['clv']=(c-b.low)/rng-.5
    F['relvol']=b.volume/b.volume.rolling(20).median()-1;F['atr_pct']=pct-.5;return F

def ridge_fit(X,y,alpha):
    Xb=np.c_[np.ones(len(X)),X];I=np.eye(Xb.shape[1]);I[0,0]=0;return np.linalg.solve(Xb.T@Xb+alpha*I,Xb.T@y)

def logistic_fit(X,y,alpha,iters=200):
    Xb=np.c_[np.ones(len(X)),X];w=np.zeros(Xb.shape[1]);t=(y>0).astype(float)
    for _ in range(iters):
        p=1/(1+np.exp(-Xb@w));g=Xb.T@(p-t)+alpha*np.r_[0,w[1:]];H=(Xb*(p*(1-p))[:,None]).T@Xb+alpha*np.diag(np.r_[0,np.ones(len(w)-1)]);w-=np.linalg.solve(H,g)
    return w

def stacked_positions(F,y,model):
    years=sorted(set(F.index.year));pos=pd.Series(0.,index=F.index);ok=F.notna().all(axis=1)&y.notna()
    for yr in years:
        if yr<FIRST_OOS:continue
        tr=ok&(F.index.year<yr);te=ok&(F.index.year==yr)
        if tr.sum()<500 or te.sum()==0:continue
        mu=F[tr].mean();sd=F[tr].std().replace(0,1.);Xtr=((F[tr]-mu)/sd).to_numpy();Xte=((F[te]-mu)/sd).to_numpy()
        w=ridge_fit(Xtr,y[tr].to_numpy(),ALPHA) if model=='ridge' else logistic_fit(Xtr,y[tr].to_numpy(),ALPHA)
        pred=np.c_[np.ones(len(Xte)),Xte]@w
        if model=='logistic':pred=pred/ (np.std(np.c_[np.ones(len(Xtr)),Xtr]@w)+1e-12)
        else:pred=pred/(np.std(np.c_[np.ones(len(Xtr)),Xtr]@w)+1e-12)
        pos[te]=np.where(pred>DEAD,1.,np.where(pred<-DEAD,-1.,0.))
    return pos

def perf(r):
    r=r[r.index.year>=FIRST_OOS];e=(1+r).cumprod();years=len(r)/365;return dict(cagr=float(e.iloc[-1]**(1/years)-1),sharpe=float(r.mean()/r.std()*np.sqrt(365)) if r.std()>0 else 0.,max_dd=float((e/e.cummax()-1).min()))

def main():
    eid='E041_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();results=[];cost=COSTS['perp']['stress']
    for sym in ['BTCUSDT','ETHUSDT']:
        hourly=load_hourly(sym,'perp');_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.);b=bars(hourly,'4h');fnd=funding.resample('4h',label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.)
        F=features(b);y=(b.open.shift(-2)/b.open.shift(-1)-1)
        # baseline: E040 equal weight of trend ensemble and compression breakout
        pa=fractional_ledger(b,ensemble_weight(b.close),cost,funding=fnd);a14=atr(b,14);pct=a14.rolling(250,min_periods=120).rank(pct=True)
        pb,_=run_ledger(b,breakout_state(b,20,(pct<.2).shift(1).fillna(False)),cost,stop_atr=3.,atr_series=a14,trail=True,funding=fnd)
        ra=daily_returns(pa);rb=daily_returns(pb);idx=ra.index.intersection(rb.index);base=(.5*ra.reindex(idx).fillna(0)+.5*rb.reindex(idx).fillna(0));bh_path,_=buy_hold(b,cost);rbh=daily_returns(bh_path).reindex(idx).fillna(0)
        res=dict(symbol=sym,baseline=perf(base),buy_hold=perf(rbh));models={}
        for model in ['ridge','logistic']:
            pos=stacked_positions(F,y,model);path,tr=run_ledger(b,pos,cost,funding=fnd);r=daily_returns(path).reindex(idx).fillna(0);p=perf(r);al=alpha_vs_bh(r[r.index.year>=FIRST_OOS],rbh)
            abl={}
            for f in F.columns:
                pos_f=stacked_positions(F.drop(columns=[f]),y,model);pf,_=run_ledger(b,pos_f,cost,funding=fnd);abl[f]=round(perf(daily_returns(pf).reindex(idx).fillna(0))['sharpe'],3)
            models[model]=dict(perf=p,alpha=al,trades=int(len(tr)),drop_one_sharpe=abl,gate=bool(p['sharpe']-res['baseline']['sharpe']>=.15 and al['alpha_ci95'][0]>0))
            print(sym,model,'OOS sharpe',round(p['sharpe'],2),'baseline',round(res['baseline']['sharpe'],2),'BH',round(res['buy_hold']['sharpe'],2),'alpha',round(al['alpha_annual'],2),[round(x,2) for x in al['alpha_ci95']],'trades',len(tr),'gate',models[model]['gate'],flush=True)
        res['models']=models;results.append(res)
    verdict='RESEARCH-PROMISING' if all(any(m['gate'] for m in r['models'].values()) for r in results) else 'REJECTED'
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,results=results,verdict=verdict,first_oos_year=FIRST_OOS,validation_accessed=False,final_test_accessed=False),indent=2,default=float));print('OUTPUT',out,verdict)

if __name__=='__main__':main()
