"""Frozen E008 economic comparison. No account or holdout access."""
from datetime import datetime,timezone
import json,hashlib
import numpy as np,pandas as pd
from core import ROOT,code_hash
from audit import uncertainty

def reference(series):
    p=sorted((ROOT/'data/raw/economic_references').glob(f'{series}_*.csv'))[-1]
    d=pd.read_csv(p)
    idx=pd.to_datetime(d.iloc[:,0],utc=True)
    values=pd.to_numeric(d[series],errors='coerce')
    s=pd.Series(values.to_numpy(),index=idx,name=series)
    assert idx.is_unique and idx.is_monotonic_increasing
    assert idx.max()<pd.Timestamp('2025-01-01',tz='UTC')
    return s,dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=len(s),missing_values=int(s.isna().sum()))

def performance(nav,initial):
    r=nav.pct_change(fill_method=None);r.iloc[0]=nav.iloc[0]/initial-1
    dd=nav/nav.cummax().clip(lower=initial)-1
    return dict(cumulative_return=float(nav.iloc[-1]/initial-1),cagr=float((nav.iloc[-1]/initial)**(365.25/len(nav))-1),
        annual_volatility=float(r.std(ddof=1)*np.sqrt(365.25)),max_daily_drawdown=float(dd.min()),
        calendar_returns={str(y):float((1+v).prod()-1) for y,v in r.groupby(r.index.year)}),r

def translate_gbp(usd_nav,usd_per_gbp):
    if (usd_per_gbp<=0).any():raise ValueError('Invalid USD-per-GBP rate')
    return usd_nav/usd_per_gbp

def accrual_reference(yield_percent,index):
    # Prior calendar-day available observation; weekends carry previous rate.
    full=pd.date_range(yield_percent.index.min(),index.max(),freq='D',tz='UTC')
    lagged=yield_percent.reindex(full).ffill().shift(1).reindex(index)
    assert lagged.notna().all()
    return lagged/100/365.25

def main():
    eid='E009_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    fx,fx_meta=reference('DEXUSUK');rates,rate_meta=reference('DGS3MO')
    source=ROOT/'reports/E008_20260908T165321'
    cases={}
    for name in ['base','stress']:
        p=source/f'{name}_ledger.csv';d=pd.read_csv(p,parse_dates=['time']).set_index('time')
        nav=d.nav.resample('1D').last()
        index=nav.index
        full_idx=pd.date_range(fx.index.min(),index.max(),freq='D',tz='UTC')
        filled_fx=fx.reindex(full_idx).ffill()
        end_fx=filled_fx.reindex(index)
        start_fx=float(filled_fx.loc[index[0]-pd.Timedelta(days=1)])
        cash_r=accrual_reference(rates,index)
        ref_nav=500*(1+cash_r).cumprod()
        usd_stats,r=performance(nav,500)
        cash_stats,_=performance(ref_nav,500)
        gbp_nav=translate_gbp(nav,end_fx)
        gbp_stats,gbp_r=performance(gbp_nav,500/start_fx)
        usd_cash_gbp=translate_gbp(pd.Series(500.,index=index),end_fx)
        fx_stats,_=performance(usd_cash_gbp,500/start_fx)
        relative_nav=nav/ref_nav*500
        relative_stats,_=performance(relative_nav,500)
        excess=r-cash_r
        u=uncertainty(excess,np.zeros(len(excess)),20260908,trials=83,samples=10000,block=30)
        cases[name]=dict(usd_assuming_usdt_parity=usd_stats,usd_short_rate_accrual_reference=cash_stats,
            relative_wealth_vs_reference=relative_stats,gbp_translation_assuming_usdt_parity=gbp_stats,
            uninvested_usd_cash_in_gbp=fx_stats,excess_daily_mean_uncertainty=u,
            initial_usd_per_gbp=start_fx,final_usd_per_gbp=float(end_fx.iloc[-1]),
            input_ledger=str(p.relative_to(ROOT)),input_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        pd.DataFrame(dict(strategy_usdt_nav=nav,gbp_translated_nav=gbp_nav,usd_reference_nav=ref_nav,lagged_reference_daily_accrual=cash_r,usd_per_gbp=end_fx,excess_daily_return=excess)).to_csv(out/f'{name}_comparison.csv')
        print(name,json.dumps(dict(strategy_cagr=usd_stats['cagr'],reference_cagr=cash_stats['cagr'],gbp_vol=gbp_stats['annual_volatility'],gbp_dd=gbp_stats['max_daily_drawdown'],excess_alpha_CI=u['arithmetic_alpha_annual_ci95'])),flush=True)
    payload=dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=20260908,cumulative_hypotheses=83,
        sources=[fx_meta,rate_meta],cases=cases,validation_accessed=False,final_test_accessed=False,
        limitations=['DGS3MO accrual is a yield-based opportunity-cost reference, not a realizable rolling-bond total-return index or a verified broker cash offer.',
        'DEXUSUK is USD per GBP; latest-vintage reference observations, asynchronous daily marks and carried nonbusiness-day valuations are not executable conversions.',
        'USDT assumed equal USD; depeg, conversion costs, tax and access to Treasury alternatives omitted. This is an economic sensitivity audit, not a trade recommendation.'])
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
