"""E037: Family E/P — regime-conditioned z-score mean reversion at 1h/4h on BTC/ETH spot and perpetual. Development only."""
import json,itertools
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars,SYMBOLS
from ta_engine import run_ledger,metrics,buy_hold,sma,atr,adx,bollinger
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv,walk_forward
from ta_screen import COSTS,BPY
from perpetual_screen import prepare as perp_prepare

Z_IN=[1.5,2.,2.5];Z_WIN=[20,50];TIME_STOP={'1h':48,'4h':24}

def regimes(b,tf,hourly):
    d=bars(hourly,'1D');a14=atr(d,14);dist=((d.close-sma(d.close,200))/a14).abs();ax,_,_=adx(d,14)
    rng=((dist<1.5)&(ax<25)).shift(1).reindex(b.index,method='ffill').fillna(False)   # range regime from completed daily bars
    lv=(d.close.pct_change().rolling(20).std()<d.close.pct_change().rolling(20).std().rolling(250,min_periods=100).median()).shift(1).reindex(b.index,method='ffill').fillna(False)
    return rng,lv

def mr_target(z,zin,regime,time_stop):
    """Enter opposite to a z extreme inside the regime; exit at the centre (z crosses 0) or after time_stop bars."""
    zv=z.to_numpy();rg=regime.to_numpy();out=np.zeros(len(zv));pos=0.;age=0
    for i in range(len(zv)):
        if pos!=0:
            age+=1
            if (pos>0 and zv[i]>=0) or (pos<0 and zv[i]<=0) or age>=time_stop or not rg[i]:pos=0.;age=0
        if pos==0 and rg[i] and np.isfinite(zv[i]):
            if zv[i]<=-zin:pos=1.;age=0
            elif zv[i]>=zin:pos=-1.;age=0
        out[i]=pos
    return pd.Series(out,index=z.index)

def architectures(b,tf,hourly):
    a14=atr(b,14);rng,lv=regimes(b,tf,hourly);always=pd.Series(True,index=b.index)
    for n,zin in itertools.product(Z_WIN,Z_IN):
        _,_,z,_=bollinger(b.close,n,2)
        yield 'E1_z_unconditional',dict(n=n,z=zin),mr_target(z,zin,always,TIME_STOP[tf]),a14
        yield 'E2_z_range_regime',dict(n=n,z=zin),mr_target(z,zin,rng,TIME_STOP[tf]),a14
        yield 'E3_z_lowvol_regime',dict(n=n,z=zin),mr_target(z,zin,lv,TIME_STOP[tf]),a14

def main():
    eid='E037_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();rows=[];daily={}
    for kind in ['perp','spot']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            for tf in ['1h','4h']:
                b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                bh_path,bh_tr=buy_hold(b,COSTS[kind]['stress']);bh=metrics(bh_path,bh_tr,BPY[tf])
                for arch,params,target,a14 in architectures(b,tf,hourly):
                    for case,cost in COSTS[kind].items():
                        path,tr=run_ledger(b,target,cost,stop_atr=3.,atr_series=a14,funding=fnd,long_only=(kind=='spot'));m=metrics(path,tr,BPY[tf]);key=(kind,sym,tf,arch,json.dumps(params,sort_keys=True))
                        if case=='stress':daily[key]=daily_returns(path)
                        rows.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,params=json.dumps(params,sort_keys=True),case=case,cost=cost,bh_sharpe=bh['sharpe'],bh_max_dd=bh['max_dd'],**{k:v for k,v in m.items() if k!='calendar'},positive_years=float(np.mean([v>0 for v in m['calendar'].values()])) if m['calendar'] else 0.))
                print(kind,sym,tf,'done',len(rows),flush=True)
    R=pd.DataFrame(rows);R.to_csv(out/'stage_ab.csv',index=False);S=R[R.case=='stress'].copy()
    S['gate']=(S.sharpe>.5)&(S.profit_factor.fillna(0)>1.2)&(S.trades>=40)&(S.max_dd>S.bh_max_dd)&(S.positive_years>=.6)&(S.cagr>0)
    fam=int(S.groupby(['kind','symbol','tf','arch']).ngroups);stage_c=[]
    for (kind,sym,tf,arch),g in S.groupby(['kind','symbol','tf','arch']):
        best=g.sort_values('sharpe',ascending=False).iloc[0];r=daily[(kind,sym,tf,arch,best.params)];boot=block_bootstrap_sharpe(r.to_numpy(),seed=1)
        M=np.column_stack([daily[(kind,sym,tf,arch,p)].reindex(r.index).fillna(0).to_numpy() for p in g.params]);pbo=pbo_cscv(M,S=8)['pbo'] if len(r)>160 else None
        plateau=bool(g.sharpe.median()>=.5*best.sharpe and (g.sharpe>0).all());wf=walk_forward({p:daily[(kind,sym,tf,arch,p)] for p in g.params},r.index,sorted(set(r.index.year)))
        wf_eff=float(np.mean([w['oos_sharpe'] for w in wf]))/max(float(np.mean([w['is_sharpe'] for w in wf])),1e-9) if wf else None;dsr=deflated_sharpe(boot['sharpe'],len(r),fam,r.to_numpy())
        stage_c.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,best_params=best.params,gate_b=bool(best.gate),sharpe=float(best.sharpe),cagr=float(best.cagr),max_dd=float(best.max_dd),trades=int(best.trades),boot_p=boot['p_value_one_sided'],pbo=pbo,plateau=plateau,wf_efficiency=wf_eff,dsr=dsr['dsr'],family_trials=fam))
    C=pd.DataFrame(stage_c);C['bh_pass']=benjamini_hochberg(C.boot_p.to_numpy(),q=.10);C['stage_c_pass']=C.gate_b&C.bh_pass&(C.dsr>=.95)&(C.pbo.fillna(1)<.5)&C.plateau&(C.wf_efficiency.fillna(0)>.5)
    assert starting==code_hash();C.to_csv(out/'stage_c.csv',index=False)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=2,cumulative_economic=378,architecture_trials=fam,parameter_configs=int(len(S)),gate_b_passers=int(S.gate.sum()),
        survivors=C[C.stage_c_pass][['kind','symbol','tf','arch','best_params','sharpe','cagr','max_dd','dsr','pbo','wf_efficiency']].to_dict('records'),validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,'configs',len(S),'gateB',int(S.gate.sum()),'stageC survivors',int(C.stage_c_pass.sum()))

if __name__=='__main__':main()
