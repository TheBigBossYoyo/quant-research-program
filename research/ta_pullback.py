"""E033: Families M/F/N — pullback-with-trend, RSI persistence, multi-timeframe triggers. Development only."""
import json,itertools
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars,bars_15m,SYMBOLS
from ta_engine import run_ledger,metrics,buy_hold,sma,ema,atr,rsi,bollinger,supertrend,donchian
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv,walk_forward
from ta_screen import COSTS,BPY,vol_size
from perpetual_screen import prepare as perp_prepare

FASTS=[10,20,30];DEPTH=[.5,1.];RSI_LVL=[30,40];TRAIL=[2.,3.,4.]

def daily_regime(hourly,index):
    d=bars(hourly,'1D');rd=np.sign(d.close-sma(d.close,200));return rd.shift(1).reindex(index,method='ffill')

def state_machine(regime,pullback,trigger):
    """Armed after a pullback inside the regime; enter on trigger; exit when regime flips (stops handled by the ledger)."""
    reg=regime.to_numpy();pb=pullback.to_numpy();tg=trigger.to_numpy();out=np.zeros(len(reg));armed=0.;pos=0.
    for i in range(len(reg)):
        r=reg[i] if np.isfinite(reg[i]) else 0.
        if pos!=0 and r!=pos:pos=0.;armed=0.
        if r==0:armed=0.;out[i]=pos;continue
        if pos==0:
            if pb[i]:armed=r
            if armed==r and tg[i]:pos=r;armed=0.
        out[i]=pos
    return pd.Series(out,index=regime.index)

def architectures(b,tf,hourly):
    a14=atr(b,14);c=b.close;reg=daily_regime(hourly,b.index)
    for f,dpt in itertools.product(FASTS,DEPTH):
        e=ema(c,f);dist=(c-e)/a14
        pb=(reg*dist<=-dpt);tg=(reg*(c-e)>0)
        yield 'M1_ema_pullback',dict(fast=f,depth=dpt),state_machine(reg,pb,tg),3.,True,a14
    r14=rsi(c,14)
    for lvl in RSI_LVL:
        pb=((reg>0)&(r14<lvl))|((reg<0)&(r14>100-lvl));tg=((reg>0)&(r14>r14.shift(1)))|((reg<0)&(r14<r14.shift(1)))
        yield 'M2_rsi_pullback',dict(level=lvl),state_machine(reg,pb,tg),3.,True,a14
    for n in [20]:
        _,_,z,_=bollinger(c,n,2);pb=(reg*z<=-1);tg=(reg*z>-.5)&(reg*z.shift(1)<=-.5)
        yield 'M3_bollinger_pullback',dict(n=n),state_machine(reg,pb,tg),3.,True,a14
    for k in TRAIL:
        f=20;e=ema(c,f);pb=(reg*(c-e)/a14<=-.5);tg=(reg*(c-e)>0)
        yield 'M1_ema_pullback_trail',dict(fast=f,depth=.5,trail=k),state_machine(reg,pb,tg),k,True,a14
    slope=np.sign(r14-r14.shift(5));yield 'F3_rsi_slope_in_regime',dict(n=14),slope.where(slope==reg,0.),None,False,a14
    m=sma(c,100);ms=np.sign(m-m.shift(5));yield 'A3_MA_slope_in_regime_control',dict(ma=100),ms.where(ms==reg,0.),None,False,a14

def mtf_15m(sym,hourly):
    """N2: 4h Supertrend regime + 1h pullback (M1) + 15m breakout trigger; spot 2022-24 long-only."""
    b15=bars_15m(sym);b4=bars(hourly,'4h');b1=bars(hourly,'1h')
    st,_=supertrend(b4.dropna(subset=['close']),10,3.);reg=st.shift(1).reindex(b15.index,method='ffill')
    e1=ema(b1.close,20);a1=atr(b1,14);pb1=(((b1.close-e1)/a1)<=-.5).shift(1).reindex(b15.index,method='ffill').fillna(False)
    hi15=b15.high.rolling(20).max().shift(1);tg=(b15.close>hi15)
    return b15,state_machine(reg,pb1.astype(bool),tg),atr(b15,14)

def main():
    eid='E033_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();rows=[];daily={}
    for kind in ['spot','perp']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            cells=[(tf,bars(hourly,tf)) for tf in ['1h','4h']]
            for tf,b in cells:
                fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                bh_path,bh_tr=buy_hold(b,COSTS[kind]['stress']);bh=metrics(bh_path,bh_tr,BPY[tf])
                for arch,params,target,stop_k,trail,a14 in architectures(b,tf,hourly):
                    for case,cost in COSTS[kind].items():
                        path,tr=run_ledger(b,target,cost,stop_atr=stop_k,atr_series=a14,trail=trail,funding=fnd,long_only=(kind=='spot'));m=metrics(path,tr,BPY[tf])
                        key=(kind,sym,tf,arch,json.dumps(params,sort_keys=True))
                        if case=='stress':daily[key]=daily_returns(path)
                        rows.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,params=json.dumps(params,sort_keys=True),case=case,cost=cost,bh_sharpe=bh['sharpe'],bh_max_dd=bh['max_dd'],**{k:v for k,v in m.items() if k!='calendar'},positive_years=float(np.mean([v>0 for v in m['calendar'].values()])) if m['calendar'] else 0.))
                print(kind,sym,tf,'done',len(rows),flush=True)
            if kind=='spot':
                b15,target,a15=mtf_15m(sym,hourly);bh_path,bh_tr=buy_hold(b15,COSTS['spot']['stress']);bh=metrics(bh_path,bh_tr,4*24*365)
                for case,cost in COSTS['spot'].items():
                    path,tr=run_ledger(b15,target,cost,stop_atr=3.,atr_series=a15,trail=True,long_only=True);m=metrics(path,tr,4*24*365);key=('spot',sym,'15m','N2_mtf_breakout','{}')
                    if case=='stress':daily[key]=daily_returns(path)
                    rows.append(dict(kind='spot',symbol=sym,tf='15m',arch='N2_mtf_breakout',params='{}',case=case,cost=cost,bh_sharpe=bh['sharpe'],bh_max_dd=bh['max_dd'],**{k:v for k,v in m.items() if k!='calendar'},positive_years=float(np.mean([v>0 for v in m['calendar'].values()])) if m['calendar'] else 0.))
                print('spot',sym,'15m N2 done',flush=True)
    R=pd.DataFrame(rows);R.to_csv(out/'stage_ab.csv',index=False);S=R[R.case=='stress'].copy()
    S['gate']=(S.sharpe>.5)&(S.profit_factor.fillna(0)>1.2)&(S.trades>=40)&(S.max_dd>S.bh_max_dd)&(S.positive_years>=.6)&(S.cagr>0)&np.where(S.kind=='spot',S.sharpe>S.bh_sharpe,True)
    fam=int(S.groupby(['kind','symbol','tf','arch']).ngroups);stage_c=[]
    for (kind,sym,tf,arch),g in S.groupby(['kind','symbol','tf','arch']):
        best=g.sort_values('sharpe',ascending=False).iloc[0];r=daily[(kind,sym,tf,arch,best.params)];boot=block_bootstrap_sharpe(r.to_numpy(),seed=1)
        M=np.column_stack([daily[(kind,sym,tf,arch,p)].reindex(r.index).fillna(0).to_numpy() for p in g.params]) if len(g)>1 else None
        pbo=pbo_cscv(M,S=8)['pbo'] if M is not None and len(r)>160 else None;plateau=bool(g.sharpe.median()>=.5*best.sharpe and (g.sharpe>0).all()) if len(g)>1 else True
        wf=walk_forward({p:daily[(kind,sym,tf,arch,p)] for p in g.params},r.index,sorted(set(r.index.year)));wf_eff=float(np.mean([w['oos_sharpe'] for w in wf]))/max(float(np.mean([w['is_sharpe'] for w in wf])),1e-9) if wf else None
        dsr=deflated_sharpe(boot['sharpe'],len(r),fam,r.to_numpy())
        stage_c.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,best_params=best.params,gate_b=bool(best.gate),sharpe=float(best.sharpe),cagr=float(best.cagr),max_dd=float(best.max_dd),trades=int(best.trades),boot_p=boot['p_value_one_sided'],sharpe_ci95=boot['ci95'],pbo=pbo,plateau=plateau,walk_forward=wf,wf_efficiency=wf_eff,dsr=dsr['dsr'],family_trials=fam))
    C=pd.DataFrame(stage_c);C['bh_pass']=benjamini_hochberg(C.boot_p.to_numpy(),q=.10) if len(C) else [];C['stage_c_pass']=C.gate_b&C.bh_pass&(C.dsr>=.95)&(C.pbo.fillna(1)<.5)&C.plateau&(C.wf_efficiency.fillna(0)>.5)
    assert starting==code_hash();C.drop(columns=['walk_forward']).to_csv(out/'stage_c.csv',index=False)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=3,cumulative_economic=375,architecture_trials=fam,parameter_configs=int(len(S)),stage_c=stage_c,
        survivors=C[C.stage_c_pass][['kind','symbol','tf','arch','best_params','sharpe','cagr','max_dd','dsr','pbo','wf_efficiency']].to_dict('records'),gate_b_passers=int(S.gate.sum()),validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,'configs',len(S),'gateB',int(S.gate.sum()),'stageC survivors',int(C.stage_c_pass.sum()))

if __name__=='__main__':main()
