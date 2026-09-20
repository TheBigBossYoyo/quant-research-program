"""E020: long-only monthly ETF trend/momentum screen for a Trading 212 GBP Invest account. Development only."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from etf_data import load_etfs,load_cash_rate,ETFS

PRIOR_HYPOTHESES=219;NEW_HYPOTHESES=4;COST_CASES=[('base',.0010),('stress',.0020),('severe',.0040)];ENTRY_MONTHS=12

def month_ends(index):
    return pd.Series(index,index=index).groupby([index.year,index.month]).last().to_numpy()

def cash_monthly(rate,months):
    """Lagged monthly UK short rate accrued for the month following each signal date (previous month's published rate)."""
    r=rate.copy();r.index=r.index.to_period('M')
    out=[]
    for m in months:
        prev=(pd.Timestamp(m)-pd.offsets.MonthBegin(1)).to_period('M')-0
        v=r.get(pd.Timestamp(m).to_period('M')-1,np.nan)
        out.append(v/12. if np.isfinite(v) else 0.)
    return pd.Series(out,index=months)

def available(adj,me):
    """An ETF is in the universe ENTRY_MONTHS after its first observed bar."""
    first=adj.apply(lambda s:s.first_valid_index())
    return pd.DataFrame({t:[bool(first[t] is not None and d>=first[t]+pd.DateOffset(months=ENTRY_MONTHS) and np.isfinite(adj.loc[d,t])) for d in me] for t in adj.columns},index=me)

def signals(adj,me,cash_m):
    a=adj.reindex(me);avail=available(adj,me);cash12=(1+cash_m).rolling(12).apply(np.prod,raw=True)-1
    ret12=a/a.shift(12)-1;ret12_1=a.shift(1)/a.shift(12)-1
    sma10=adj.rolling(10*21).mean().reindex(me);trend_sma=(a>sma10)
    trend=(ret12.gt(cash12,axis=0))&avail;trend_sma=trend_sma&avail
    def top3(score,mask):
        w=pd.DataFrame(0.,index=me,columns=a.columns)
        for d in me:
            s=score.loc[d].where(mask.loc[d]).dropna().sort_values(ascending=False).head(3)
            if len(s):w.loc[d,s.index]=1./3.
        return w
    def equal(mask):
        n=mask.sum(axis=1);return mask.astype(float).div(n.where(n>0),axis=0).fillna(0.)
    return {'T1_trend12':equal(trend),'T2_sma10':equal(trend_sma),'M_mom12_1':top3(ret12_1,avail),'C_combined':top3(ret12_1,trend),
            'ew_all':equal(avail),'mix_60_40':mix_60_40(a.columns,me,avail)}

def mix_60_40(columns,me,avail):
    w=pd.DataFrame(0.,index=me,columns=columns)
    if 'VWRL.L' in columns and 'IGLT.L' in columns:
        ok=avail[['VWRL.L','IGLT.L']].all(axis=1);w.loc[ok,'VWRL.L']=.6;w.loc[ok,'IGLT.L']=.4
    return w

def ledger(close,adj,volume,weights,cost,cash_m,initial=10000.,delay=1):
    """Monthly targets execute at the close of the first executable day (volume>0) at least `delay` days after the signal.

    Holdings earn total return via the adjusted-close ratio; cash earns the lagged monthly rate.
    Weights are NAV fractions at execution; costs on traded notional. No leverage, no shorts.
    """
    idx=close.index;nav=initial;hold=pd.Series(0.,index=close.columns);units=pd.Series(0.,index=close.columns);entry_adj=None
    rows=[];exec_days={}
    for d in weights.index:
        pos=idx.searchsorted(d)+delay
        while pos<len(idx) and not (np.isfinite(close.iloc[pos][weights.loc[d]>0]).all() and (volume.iloc[pos][weights.loc[d]>0]>0).all()):pos+=1
        if pos<len(idx):exec_days[idx[pos]]=weights.loc[d]
    tr=adj/adj.shift(1);cash_daily=pd.Series(0.,index=idx)
    for m,v in cash_m.items():
        nxt=idx[idx>m];days=nxt[nxt<=m+pd.offsets.MonthEnd(1)]
        if len(days):cash_daily.loc[days]=(1+v)**(1/len(days))-1
    frac=pd.Series(0.,index=close.columns);cash=1.
    for i,day in enumerate(idx):
        if i>0:
            g=tr.iloc[i].fillna(1.);growth=float((frac*g).sum()+cash*(1+cash_daily.iloc[i]))
            nav*=growth;frac=frac*g/growth;cash=cash*(1+cash_daily.iloc[i])/growth
        if day in exec_days:
            target=exec_days[day].reindex(close.columns).fillna(0.);turn=float((target-frac).abs().sum())
            nav*=(1-turn*cost);frac=target;cash=1.-float(frac.sum());assert cash>-1e-9
        else:turn=0.
        rows.append(dict(time=day,nav=nav,turnover=turn,invested=float(frac.sum())))
    return pd.DataFrame(rows).set_index('time')

def performance(path,cash_m,initial=10000.):
    nav=path.nav;r=nav.pct_change();r.iloc[0]=nav.iloc[0]/initial-1;years=len(nav)/252.
    m=nav.resample('ME').last().pct_change().dropna();dd=nav/nav.cummax().clip(lower=initial)-1
    cash_ann=float((1+cash_m.reindex(m.index,method='ffill').fillna(0.)).prod()**(1/max(years,1e-9))-1)
    excess_by_year={str(y):float((1+x).prod()-(1+cash_m.reindex(x.index,method='ffill').fillna(0.)).prod()) for y,x in m.groupby(m.index.year)}
    return dict(cagr=float((nav.iloc[-1]/initial)**(1/years)-1),cash_reference_cagr=cash_ann,monthly_sharpe=float(m.mean()/m.std()*np.sqrt(12)) if m.std()>0 else 0.,
        max_drawdown=float(dd.min()),annual_turnover=float(path.turnover.sum()/years),mean_invested=float(path.invested.mean()),
        excess_over_cash_by_year=excess_by_year,positive_excess_year_share=float(np.mean([v>0 for v in excess_by_year.values()])))

def main():
    eid='E020_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();panels,meta=load_etfs();rate=load_cash_rate();adj,close,vol=panels['adj'],panels['close'],panels['volume']
    me=pd.DatetimeIndex(month_ends(adj.index));cash_m=cash_monthly(rate,me);sig=signals(adj,me,cash_m)
    rows=[]
    for name,w in sig.items():
        for case,c in COST_CASES:
            p=ledger(close,adj,vol,w,c,cash_m);m=performance(p,cash_m);rows.append(dict(hypothesis=name,case=case,cost=c,**m))
            if case=='stress':print(name,'stress cagr',round(m['cagr'],4),'cash',round(m['cash_reference_cagr'],4),'sharpe',round(m['monthly_sharpe'],3),'dd',round(m['max_drawdown'],3),'turnover',round(m['annual_turnover'],2),flush=True)
            if case=='stress':p.to_csv(out/f'{name}_stress_path.csv')
    ew=next(r for r in rows if r['hypothesis']=='ew_all' and r['case']=='stress');survivors=[]
    for r in rows:
        if r['case']!='stress' or r['hypothesis'] in ('ew_all','mix_60_40'):continue
        if r['cagr']>r['cash_reference_cagr'] and r['monthly_sharpe']>max(0.,ew['monthly_sharpe']) and r['positive_excess_year_share']>=.6 and r['max_drawdown']>=ew['max_drawdown']:
            survivors.append(r['hypothesis'])
    assert starting==code_hash(),'Source changed during experiment'
    payload=dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=None,cumulative_hypotheses=PRIOR_HYPOTHESES+NEW_HYPOTHESES,rows=rows,survivors=survivors,
        data=meta,development_end_exclusive='2020-01-01',validation_accessed=False,final_test_accessed=False,
        verdict='DEVELOPMENT SCREEN ONLY; yfinance data without checksums, spread assumptions uncalibrated, ETF-closure survivorship disclosed.')
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False,default=float))
    pd.DataFrame([{k:v for k,v in r.items() if k!='excess_over_cash_by_year'} for r in rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
