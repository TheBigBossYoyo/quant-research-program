"""E038: Family D/K — compression-to-expansion breakout with volume confirmation, 4h/1D. Development only."""
import json,itertools
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from ta_data import load_hourly,bars,SYMBOLS
from ta_engine import run_ledger,metrics,buy_hold,atr,donchian
from ta_stats import daily_returns,block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv,walk_forward
from ta_screen import COSTS,BPY
from perpetual_screen import prepare as perp_prepare

PCT=[.10,.20,.30];CHAN=[20,50]

def breakout_state(b,n,compressed=None,volume_ok=None):
    """Enter on a close outside the prior n-bar channel (optionally only when compression / volume conditions held on the signal bar); hold until the trailing stop (ledger) or an opposite breakout."""
    hi,lo=donchian(b,n);up=(b.close>hi.shift(1));dn=(b.close<lo.shift(1))
    if compressed is not None:up&=compressed;dn&=compressed
    if volume_ok is not None:up&=volume_ok;dn&=volume_ok
    raw=pd.Series(np.where(up,1.,np.where(dn,-1.,np.nan)),index=b.index);return raw.ffill().fillna(0.)

def architectures(b,tf):
    a14=atr(b,14);pct=a14.rolling(250,min_periods=120).rank(pct=True);vol_ok=b.volume>2*b.volume.rolling(20).median()
    for n in CHAN:
        yield 'C1_control',dict(n=n),breakout_state(b,n),a14
        for p in PCT:
            comp=(pct<p).shift(1).fillna(False)  # compression measured on the bar before the breakout bar
            yield 'D1_compression_breakout',dict(n=n,pct=p),breakout_state(b,n,comp),a14
            yield 'D2_compression_volume',dict(n=n,pct=p),breakout_state(b,n,comp,vol_ok),a14

def main():
    eid='E038_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();rows=[];daily={}
    for kind in ['perp','spot']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            for tf in ['4h','1D']:
                b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                bh_path,bh_tr=buy_hold(b,COSTS[kind]['stress']);bh=metrics(bh_path,bh_tr,BPY[tf])
                for arch,params,target,a14 in architectures(b,tf):
                    for case,cost in COSTS[kind].items():
                        path,tr=run_ledger(b,target,cost,stop_atr=3.,atr_series=a14,trail=True,funding=fnd,long_only=(kind=='spot'));m=metrics(path,tr,BPY[tf]);key=(kind,sym,tf,arch,json.dumps(params,sort_keys=True))
                        if case=='stress':daily[key]=daily_returns(path)
                        rows.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,params=json.dumps(params,sort_keys=True),case=case,cost=cost,bh_sharpe=bh['sharpe'],bh_max_dd=bh['max_dd'],**{k:v for k,v in m.items() if k!='calendar'},positive_years=float(np.mean([v>0 for v in m['calendar'].values()])) if m['calendar'] else 0.))
                print(kind,sym,tf,'done',len(rows),flush=True)
    R=pd.DataFrame(rows);R.to_csv(out/'stage_ab.csv',index=False);S=R[R.case=='stress'].copy()
    S['gate']=(S.sharpe>.5)&(S.profit_factor.fillna(0)>1.2)&(S.trades>=40)&(S.max_dd>S.bh_max_dd)&(S.positive_years>=.6)&(S.cagr>0)&np.where(S.kind=='spot',S.sharpe>S.bh_sharpe,True)
    fam=int(S.groupby(['kind','symbol','tf','arch']).ngroups);stage_c=[]
    for (kind,sym,tf,arch),g in S.groupby(['kind','symbol','tf','arch']):
        best=g.sort_values('sharpe',ascending=False).iloc[0];r=daily[(kind,sym,tf,arch,best.params)];boot=block_bootstrap_sharpe(r.to_numpy(),seed=1)
        M=np.column_stack([daily[(kind,sym,tf,arch,p)].reindex(r.index).fillna(0).to_numpy() for p in g.params]) if len(g)>1 else None;pbo=pbo_cscv(M,S=8)['pbo'] if M is not None and len(r)>160 else None
        plateau=bool(g.sharpe.median()>=.5*best.sharpe and (g.sharpe>0).all()) if len(g)>1 else True;wf=walk_forward({p:daily[(kind,sym,tf,arch,p)] for p in g.params},r.index,sorted(set(r.index.year)))
        wf_eff=float(np.mean([w['oos_sharpe'] for w in wf]))/max(float(np.mean([w['is_sharpe'] for w in wf])),1e-9) if wf else None;dsr=deflated_sharpe(boot['sharpe'],len(r),fam,r.to_numpy())
        ctrl=S[(S.kind==kind)&(S.symbol==sym)&(S.tf==tf)&(S.arch=='C1_control')&(S.params==json.dumps(dict(n=json.loads(best.params)['n']),sort_keys=True))].sharpe
        stage_c.append(dict(kind=kind,symbol=sym,tf=tf,arch=arch,best_params=best.params,gate_b=bool(best.gate),sharpe=float(best.sharpe),cagr=float(best.cagr),max_dd=float(best.max_dd),trades=int(best.trades),boot_p=boot['p_value_one_sided'],sharpe_ci95=boot['ci95'],pbo=pbo,plateau=plateau,wf_efficiency=wf_eff,dsr=dsr['dsr'],family_trials=fam,control_sharpe=float(ctrl.iloc[0]) if len(ctrl) else None))
    C=pd.DataFrame(stage_c);C['bh_pass']=benjamini_hochberg(C.boot_p.to_numpy(),q=.10);C['stage_c_pass']=C.gate_b&C.bh_pass&(C.dsr>=.95)&(C.pbo.fillna(1)<.5)&C.plateau&(C.wf_efficiency.fillna(0)>.5)
    assert starting==code_hash();C.to_csv(out/'stage_c.csv',index=False)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=2,cumulative_economic=380,architecture_trials=fam,parameter_configs=int(len(S)),gate_b_passers=int(S.gate.sum()),
        survivors=C[C.stage_c_pass][['kind','symbol','tf','arch','best_params','sharpe','cagr','max_dd','dsr','pbo','wf_efficiency']].to_dict('records'),validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,'configs',len(S),'gateB',int(S.gate.sum()),'stageC survivors',int(C.stage_c_pass.sum()))

if __name__=='__main__':main()
