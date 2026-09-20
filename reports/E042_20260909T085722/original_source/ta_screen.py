"""E032: Families A/B/C (trend, Supertrend, Donchian) on BTC/ETH spot and perpetual at 1h/4h/1D. Development only.

Stage A: trade-distribution diagnostics per configuration. Stage B: preregistered gates at stressed costs.
Stage C: plateau, PBO (CSCV), expanding-window walk-forward, DSR at the family trial count, bootstrap Sharpe.
"""
import json,sys,itertools
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars,SYMBOLS
from ta_engine import run_ledger,metrics,buy_hold,sma,ema,atr,supertrend,donchian,adx
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv,walk_forward
from perpetual_screen import prepare as perp_prepare

COSTS={'spot':{'opt':.0010,'real':.0012,'stress':.0024},'perp':{'opt':.000505,'real':.000705,'stress':.000905}}
BPY={'1h':24*365,'4h':6*365,'1D':365};TFS=['1h','4h','1D']
FAST=[10,20,30];MED=[50,75,100];SLOW=[150,200,250];ST_N=[10,14,20];ST_M=[2.,2.5,3.];DON=[20,50,100];TRAIL=[2.,3.,4.]

def architectures(b,tf,hourly=None):
    """Yield (arch, params, target, stop_atr, trail, atr_series). Targets are decided at bar close."""
    c=b.close;a14=atr(b,14)
    # HTF regime from completed daily bars (for 1h/4h); daily uses its own 200-SMA
    if tf=='1D':reg=np.sign(c-sma(c,200))
    else:
        d=bars(hourly,'1D');rd=np.sign(d.close-sma(d.close,200));reg=rd.shift(1).reindex(b.index,method='ffill')  # last completed daily bar strictly before this bar's day
    for s in SLOW:yield 'A1_price_slowMA',dict(slow=s),np.sign(c-sma(c,s)),None,False,a14
    for f,s in itertools.product(FAST,MED):yield 'A2_dual_MA',dict(fast=f,slow=s),np.sign(ema(c,f)-ema(c,s)),None,False,a14
    for s in MED+SLOW:m=sma(c,s);yield 'A3_MA_slope',dict(ma=s),np.sign(m-m.shift(5)),None,False,a14
    for s in SLOW:m=sma(c,s);dist=(c-m)/a14;t=np.sign(c-m).where(dist.abs()<4,0.);yield 'A4_MA_distance_capped',dict(slow=s,cap_atr=4),t,None,False,a14
    for n,m in itertools.product(ST_N,ST_M):d,_=supertrend(b,n,m);yield 'B1_supertrend_flip',dict(n=n,mult=m),d,None,False,a14
    for n,m in itertools.product(ST_N,ST_M):d,_=supertrend(b,n,m);yield 'B3_supertrend_HTF',dict(n=n,mult=m),d.where(d==reg,0.),None,False,a14
    for n in DON:
        hi,lo=donchian(b,n);hi_p=hi.shift(1);lo_p=lo.shift(1)
        raw=pd.Series(np.where(c>hi_p,1.,np.where(c<lo_p,-1.,np.nan)),index=b.index)
        # C1: channel breakout with exit on opposite half-channel (n//2) breach
        hi2,lo2=donchian(b,max(5,n//2));state=raw.copy();st=np.nan;vals=[]
        for i in range(len(b)):
            v=raw.iloc[i]
            if np.isfinite(v):st=v
            elif st==1 and c.iloc[i]<lo2.shift(1).iloc[i]:st=0.
            elif st==-1 and c.iloc[i]>hi2.shift(1).iloc[i]:st=0.
            vals.append(st if np.isfinite(st) else 0.)
        state=pd.Series(vals,index=b.index)
        yield 'C1_donchian_channel',dict(n=n),state,None,False,a14
        for k in TRAIL:yield 'C6_donchian_ATR_trail',dict(n=n,trail=k),raw.ffill().fillna(0.),k,True,a14
        yield 'C4_donchian_HTF',dict(n=n),state.where(state==reg,0.),None,False,a14
    for n in DON:
        hi,lo=donchian(b,n);raw=pd.Series(np.where(c>hi.shift(1),1.,np.where(c<lo.shift(1),-1.,np.nan)),index=b.index).ffill().fillna(0.)
        yield 'C2_donchian_voltarget',dict(n=n,vol_target=.20),raw,3.,True,a14

def vol_size(b,tf,target=.20):
    r=np.log(b.close/b.close.shift(1));v=r.rolling(30).std()*np.sqrt(BPY[tf]);return (target/v).clip(upper=1.).shift(0)

def main():
    eid='E032_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();rows=[];configs_daily={}
    for kind in ['spot','perp']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':
                _,px,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)  # 2022-24 signed funding per unit; earlier years zero (documented limitation)
            for tf in TFS:
                b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                bh_path,bh_tr=buy_hold(b,COSTS[kind]['stress']);bh=metrics(bh_path,bh_tr,BPY[tf])
                for arch,params,target,stop_k,trail,a14 in architectures(b,tf,hourly):
                    size=vol_size(b,tf) if arch=='C2_donchian_voltarget' else None
                    for case,cost in COSTS[kind].items():
                        path,tr=run_ledger(b,target,cost,stop_atr=stop_k,atr_series=a14,trail=trail,funding=fnd,size=size,long_only=(kind=='spot'))
                        m=metrics(path,tr,BPY[tf]);key=(kind,sym,tf,arch,json.dumps(params,sort_keys=True))
                        if case=='stress':configs_daily[key]=daily_returns(path)
                        rows.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,params=json.dumps(params,sort_keys=True),case=case,cost=cost,bh_cagr=bh['cagr'],bh_sharpe=bh['sharpe'],bh_max_dd=bh['max_dd'],**{k:v for k,v in m.items() if k!='calendar'},positive_years=float(np.mean([v>0 for v in m['calendar'].values()])) if m['calendar'] else 0.))
                print(kind,sym,tf,'done',len(rows),flush=True)
    R=pd.DataFrame(rows);R.to_csv(out/'stage_ab.csv',index=False)
    # Stage B gates at stressed costs
    S=R[R.case=='stress'].copy()
    S['gate']=(S.sharpe>.5)&(S.profit_factor.fillna(0)>1.2)&(S.trades>=40)&(S.max_dd>S.bh_max_dd)&(S.positive_years>=.6)&(S.cagr>0)&np.where(S.kind=='spot',S.sharpe>S.bh_sharpe,True)
    # Stage C for gate passers: bootstrap p-values -> BH within family (arch level, best config per arch/asset/tf); PBO across the arch's parameter grid; walk-forward; DSR with family trial count
    fam_trials=int(S.groupby(['kind','symbol','tf','arch']).ngroups);stage_c=[]
    for (kind,sym,tf,arch),g in S.groupby(['kind','symbol','tf','arch']):
        best=g.sort_values('sharpe',ascending=False).iloc[0];key=(kind,sym,tf,arch,best.params);r=configs_daily[key]
        boot=block_bootstrap_sharpe(r.to_numpy(),seed=1);M=np.column_stack([configs_daily[(kind,sym,tf,arch,p)].reindex(r.index).fillna(0).to_numpy() for p in g.params]) if len(g)>1 else None
        pbo=pbo_cscv(M,S=8)['pbo'] if M is not None and len(r)>160 else None
        plateau=bool(g.sharpe.median()>=.5*best.sharpe and (g.sharpe>0).all()) if len(g)>1 else True
        wf=walk_forward({p:configs_daily[(kind,sym,tf,arch,p)] for p in g.params},r.index,sorted(set(r.index.year)))
        wf_eff=float(np.mean([w['oos_sharpe'] for w in wf]))/max(float(np.mean([w['is_sharpe'] for w in wf])),1e-9) if wf else None
        dsr=deflated_sharpe(boot['sharpe'],len(r),fam_trials,r.to_numpy())
        stage_c.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,best_params=best.params,gate_b=bool(best.gate),sharpe=float(best.sharpe),cagr=float(best.cagr),max_dd=float(best.max_dd),trades=int(best.trades),
            boot_p=boot['p_value_one_sided'],sharpe_ci95=boot['ci95'],pbo=pbo,plateau=plateau,walk_forward=wf,wf_efficiency=wf_eff,dsr=dsr['dsr'],family_trials=fam_trials))
    C=pd.DataFrame(stage_c);C['bh_pass']=benjamini_hochberg(C.boot_p.to_numpy(),q=.10) if len(C) else []
    C['stage_c_pass']=C.gate_b&C.bh_pass&(C.dsr>=.95)&(C.pbo.fillna(1)<.5)&C.plateau&(C.wf_efficiency.fillna(0)>.5)
    assert starting==code_hash()
    C.drop(columns=['walk_forward']).to_csv(out/'stage_c.csv',index=False)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=5,cumulative_economic=372,architecture_trials=fam_trials,parameter_configs=int(len(S)),
        stage_c=stage_c,survivors=C[C.stage_c_pass][['kind','symbol','tf','arch','best_params','sharpe','cagr','max_dd','dsr','pbo','wf_efficiency']].to_dict('records'),gate_b_passers=int(S.gate.sum()),
        validation_accessed=False,final_test_accessed=False,limitations=['perpetual funding applied only for 2022-2024 (funding history for 2020-21 not on disk)','stops use bar high/low with gap fill at open; intrabar path unknown']),indent=2,default=float))
    print('OUTPUT',out,'configs',len(S),'gateB',int(S.gate.sum()),'stageC survivors',int(C.stage_c_pass.sum()))

if __name__=='__main__':main()
