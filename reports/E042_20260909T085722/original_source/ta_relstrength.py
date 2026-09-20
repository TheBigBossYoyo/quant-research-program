"""E036: Family O — liquid relative strength with absolute overlay on the perpetual universe, weekly. Development 2020-2024."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty
from universe import load_klines,load_funding,daily_funding,eligibility,rebalance_days,MIN_HISTORY_BARS,LIQUIDITY_WINDOW
from cross_sectional_screen import xs_ledger,performance,COST_CASES,STEP
from ta_stats import block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv
from cross_sectional_hostile import placebo_weights

TOP_N=30;WIDTHS=[.2,.25,.33]

def liquid_mask(panels,elig):
    med=panels['quote_volume'].rolling(LIQUIDITY_WINDOW,min_periods=LIQUIDITY_WINDOW).median().where(elig)
    rank=med.rank(axis=1,ascending=False);return elig&(rank<=TOP_N)

def features(panels):
    c=panels['close'];r=np.log(c/c.shift(1));mom=c.shift(7)/c.shift(84)-1;vol=r.rolling(84).std()*np.sqrt(365)
    return dict(mom=mom,radj=mom/vol.replace(0,np.nan),overlay=(c>c.rolling(200).mean()))

def weights(score,mask,d,width,long_only=False,overlay=None):
    s=score.loc[d].where(mask.loc[d]).dropna()
    if len(s)<10:return pd.Series(dtype=float)
    n=max(1,int(np.floor(width*len(s))));ranked=s.sort_values()
    if long_only:
        top=ranked.index[-n:];ok=[t for t in top if overlay is None or bool(overlay.loc[d,t])]
        return pd.Series(1./n,index=ok) if ok else pd.Series(dtype=float)
    w=pd.Series(0.,index=s.index);w[ranked.index[-n:]]=.5/n;w[ranked.index[:n]]=-.5/n;return w[w!=0]

def main():
    eid='E036_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash()
    panels,ki=load_klines();funding,fi=load_funding();days=panels['close'].index;syms=list(panels['close'].columns);fund=daily_funding(funding,days,syms)
    elig=eligibility(panels);liq=liquid_mask(panels,elig);F=features(panels);rb=rebalance_days(days,days[max(MIN_HISTORY_BARS,200)],STEP);opens=panels['open']
    archs={'O1_ls_mom':('mom',False,False),'O2_ls_radj':('radj',False,False),'O3_lo_mom_overlay':('mom',True,True),'O4_lo_radj_overlay':('radj',True,True)}
    rows=[];daily={}
    ew={d:(lambda m:pd.Series(1./m.sum(),index=m[m].index) if m.sum()>=10 else pd.Series(dtype=float))(liq.loc[d]) for d in rb};ew={d:w for d,w in ew.items() if len(w)}
    btc={d:pd.Series({'BTCUSDT':1.}) for d in rb if np.isfinite(opens.loc[d,'BTCUSDT'])}
    bench={}
    for name,w in [('ew_liquid',ew),('btc_long',btc)]:
        for case,c in COST_CASES:
            p=performance(xs_ledger(opens,fund,w,c));rows.append(dict(arch=name,width=None,case=case,**p))
            if case=='stress':bench[name]=p
    for arch,(feat,lo,ov) in archs.items():
        for width in WIDTHS:
            w={d:x for d in rb for x in [weights(F[feat],liq,d,width,lo,F['overlay'] if ov else None)] if len(x)}
            for case,c in COST_CASES:
                path=xs_ledger(opens,fund,w,c);p=performance(path);rows.append(dict(arch=arch,width=width,case=case,**p))
                if case=='stress':daily[(arch,width)]=path.nav.pct_change().fillna(0.)
            print(arch,width,'stress cagr',round(p['cagr'],3),'sharpe',round(p['daily_sharpe'],2),'dd',round(p['max_daily_drawdown'],3),'names',round(p['mean_names'],1),flush=True)
    R=pd.DataFrame(rows);R.to_csv(out/'stage_ab.csv',index=False);S=R[(R.case=='stress')&R.width.notna()].copy()
    S['gate']=np.where(S.arch.str.startswith('O3')|S.arch.str.startswith('O4'),(S.cagr>0)&(S.daily_sharpe>bench['ew_liquid']['daily_sharpe'])&(S.max_daily_drawdown>bench['ew_liquid']['max_daily_drawdown'])&(S.calendar_returns.apply(lambda d:np.mean([v>0 for v in d.values()]))>=.6),
        (S.cagr>0)&(S.daily_sharpe>0)&(S.max_daily_drawdown>-.30)&(S.calendar_returns.apply(lambda d:np.mean([v>0 for v in d.values()]))>=.6))
    stage_c=[]
    for arch in archs:
        g=S[S.arch==arch];best=g.sort_values('daily_sharpe',ascending=False).iloc[0];r=daily[(arch,best.width)];boot=block_bootstrap_sharpe(r.to_numpy(),seed=5)
        M=np.column_stack([daily[(arch,wd)].to_numpy() for wd in WIDTHS]);pbo=pbo_cscv(M,S=8)['pbo'];dsr=deflated_sharpe(boot['sharpe'],len(r),len(archs),r.to_numpy())
        r21=r[r.index>=pd.Timestamp('2021-01-01',tz='UTC')];s21=block_bootstrap_sharpe(r21.to_numpy(),seed=6)
        feat,lo,ov=archs[arch];w={d:x for d in rb for x in [weights(F[feat],liq,d,best.width,lo,F['overlay'] if ov else None)] if len(x)}
        pl=[];rng=np.random.default_rng(20260909)
        for k in range(100):
            G=F[feat].copy()
            for d in rb:
                s=G.loc[d].where(liq.loc[d]);vals=s.dropna();G.loc[d,vals.index]=rng.permutation(vals.to_numpy())
            wp={d:x for d in rb for x in [weights(G,liq,d,best.width,lo,F['overlay'] if ov else None)] if len(x)};pl.append(performance(xs_ledger(opens,fund,wp,.0014))['cagr'])
        stage_c.append(dict(arch=arch,best_width=float(best.width),gate_b=bool(best.gate),sharpe=float(best.daily_sharpe),cagr=float(best.cagr),max_dd=float(best.max_daily_drawdown),boot_p=boot['p_value_one_sided'],sharpe_ci95=boot['ci95'],pbo=pbo,dsr=dsr['dsr'],start_2021_sharpe_ci=s21['ci95'],placebo_frac_at_or_above=float(np.mean(np.array(pl)>=best.cagr)),placebo_q95=float(np.quantile(pl,.95))))
        print(arch,'stageC',{k:(round(v,3) if isinstance(v,float) else v) for k,v in stage_c[-1].items() if k not in ('sharpe_ci95','start_2021_sharpe_ci')},flush=True)
    C=pd.DataFrame(stage_c);C['bh_pass']=benjamini_hochberg(C.boot_p.to_numpy(),q=.10);C['stage_c_pass']=C.gate_b&C.bh_pass&(C.dsr>=.95)&(C.pbo<.5)&(C.start_2021_sharpe_ci.apply(lambda x:x[0])>0)&(C.placebo_frac_at_or_above<.05)
    assert starting==code_hash();C.to_csv(out/'stage_c.csv',index=False)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=1,cumulative_economic=376,architectures=4,benchmarks=bench,stage_c=stage_c,survivors=C[C.stage_c_pass].arch.tolist(),validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,'survivors',C[C.stage_c_pass].arch.tolist())

if __name__=='__main__':main()
