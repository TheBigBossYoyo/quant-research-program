"""E039: incremental-information ablations for MACD, ADX, VWAP distance and candle structure at 4h/1D. Development only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.stats import spearmanr
from core import ROOT,code_hash
from ta_data import load_hourly,bars,SYMBOLS
from ta_engine import run_ledger,metrics,sma,atr,adx,macd,rolling_vwap
from ta_stats import daily_returns,block_bootstrap_sharpe
from ta_screen import COSTS,BPY
from perpetual_screen import prepare as perp_prepare
from micro_screen import block_bootstrap_ic

FEATS=['macd_hist','adx_level','adx_change','vwap_dist','body','upper_wick','lower_wick','clv'];N_FEATS=8

def feature_frame(b):
    a=atr(b,14);_,_,h=macd(b.close);ax,_,_=adx(b,14);vw=rolling_vwap(b,20);rng=(b.high-b.low).replace(0,np.nan)
    return pd.DataFrame(dict(macd_hist=h/a,adx_level=ax,adx_change=ax-ax.shift(5),vwap_dist=(b.close-vw)/a,body=(b.close-b.open)/rng,upper_wick=(b.high-b[['open','close']].max(axis=1))/rng,lower_wick=(b[['open','close']].min(axis=1)-b.low)/rng,clv=(b.close-b.low)/rng),index=b.index)

def filters(F,reg):
    return {'macd_hist':np.sign(F.macd_hist)==reg,'adx_level':F.adx_level>25,'adx_change':F.adx_change>0,'vwap_dist':np.sign(F.vwap_dist)==reg,'body':np.sign(F.body)==reg,'upper_wick':F.upper_wick<.3,'lower_wick':F.lower_wick<.3,'clv':(F.clv>.5)==(reg>0)}

def main():
    eid='E039_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False);starting=code_hash();stage_a=[];stage_b=[]
    for kind in ['perp','spot']:
        for sym in SYMBOLS:
            hourly=load_hourly(sym,kind);funding=None
            if kind=='perp':_,_,fcash,_=perp_prepare(sym);funding=fcash.reindex(hourly.index).fillna(0.)
            for tf in ['4h','1D']:
                b=bars(hourly,tf);fnd=funding.resample(tf,label='left',closed='left',origin='epoch').sum().reindex(b.index).fillna(0.) if funding is not None else None
                F=feature_frame(b);reg=np.sign(b.close-sma(b.close,250));o=b.open;fwd1=o.shift(-2)/o.shift(-1)-1;fwd5=o.shift(-6)/o.shift(-1)-1
                days=b.index.strftime('%Y-%m-%d').to_numpy()
                for k,f in enumerate(FEATS):
                    x=F[f];ok=x.notna()&fwd1.notna()&reg.notna()
                    boot=block_bootstrap_ic(x[ok].to_numpy(),fwd1[ok].to_numpy(),days[ok.to_numpy()],1000,20260909+k,N_FEATS)
                    # partial IC: residualise forward return on the regime sign
                    r=fwd1[ok];g=reg[ok];beta=np.cov(r,g)[0,1]/np.var(g) if np.var(g)>0 else 0.;resid=r-beta*g
                    ok5=x.notna()&fwd5.notna()
                    stage_a.append(dict(kind=kind,symbol=sym,tf=tf,feature=f,ic1=boot['ic'],ic1_adj_ci=[boot['ci_lower_adjusted'],boot['ci_upper_adjusted']],partial_ic1=float(spearmanr(x[ok],resid).statistic),ic5=float(spearmanr(x[ok5],fwd5[ok5]).statistic),n=int(ok.sum()),
                        passes=bool(boot['ci_lower_adjusted']>0 or boot['ci_upper_adjusted']<0)))
                cost=COSTS[kind]['stress'];base_path,base_tr=run_ledger(b,reg,cost,funding=fnd,long_only=(kind=='spot'));bm=metrics(base_path,base_tr,BPY[tf]);bb=block_bootstrap_sharpe(daily_returns(base_path).to_numpy(),seed=1)
                half=(bb['ci95'][1]-bb['ci95'][0])/2
                for f,mask in filters(F,reg).items():
                    t=reg.where(mask.fillna(False),0.);path,tr=run_ledger(b,t,cost,funding=fnd,long_only=(kind=='spot'));m=metrics(path,tr,BPY[tf])
                    stage_b.append(dict(kind=kind,symbol=sym,tf=tf,feature=f,base_sharpe=bm['sharpe'],filtered_sharpe=m['sharpe'],improvement=m['sharpe']-bm['sharpe'],half_width=half,retained=bool(m['sharpe']-bm['sharpe']>half),base_cagr=bm['cagr'],filtered_cagr=m['cagr'],trades=m['trades']))
                print(kind,sym,tf,'base sharpe',round(bm['sharpe'],2),{f:round(x['improvement'],2) for f,x in zip(FEATS,stage_b[-N_FEATS:])},flush=True)
    A=pd.DataFrame(stage_a);B=pd.DataFrame(stage_b);A.to_csv(out/'stage_a.csv',index=False);B.to_csv(out/'stage_b.csv',index=False)
    verdicts={}
    for f in FEATS:
        a=A[A.feature==f];bset=B[B.feature==f];retained_4h=int(bset[bset.tf=='4h'].retained.sum());retained_1d=int(bset[bset.tf=='1D'].retained.sum())
        verdicts[f]=dict(stage_a_passes=int(a.passes.sum()),cells=int(len(a)),median_partial_ic=float(a.partial_ic1.median()),filter_retained_4h=retained_4h,filter_retained_1d=retained_1d,verdict='INCREMENTAL' if (retained_4h>=3 or retained_1d>=3) else ('WEAK_SIGNAL' if a.passes.sum()>=4 else 'REJECTED'))
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,economic_hypotheses=4,cumulative_economic=384,stage_a=stage_a,stage_b=stage_b,verdicts=verdicts,validation_accessed=False,final_test_accessed=False),indent=2,default=float))
    print('OUTPUT',out,verdicts)

if __name__=='__main__':main()
