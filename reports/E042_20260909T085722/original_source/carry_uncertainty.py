"""Statistical gate for continuous carry before any validation access."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash,load_data
from carry_backtest import load_prices,rounded_quantity
from carry_screen import funding_diagnostic
from audit import uncertainty

def main():
    eid='E007_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    results=[]
    for j,sym in enumerate(['BTCUSDT','ETHUSDT']):
        spot,_=load_data(sym);fut,_=load_prices(sym,'klines');mark,_=load_prices(sym,'markPriceKlines')
        prices=pd.DataFrame(dict(spot=spot.open.reindex(fut.index),future=fut.open))
        # Mark-only missing spot opens explicitly carried, never used as fills.
        missing=int(prices.spot.isna().sum());prices.spot=prices.spot.ffill()
        q=rounded_quantity(500*prices.spot.iloc[0]/(prices.spot.iloc[0]+prices.future.iloc[0]),prices.spot.iloc[0],.001)
        fp=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
        f,_,_=funding_diagnostic(json.loads(fp.read_text()))
        scheduled=f.index.floor('8h');f=f.loc[(scheduled>prices.index[0])&(scheduled<prices.index[-1])]
        proxy=mark.open.reindex(f.index.floor('8h')).to_numpy()
        marks=f['mark'].fillna(pd.Series(proxy,index=f.index))
        payment=q*marks*f.rate
        cumulative=pd.Series(payment.to_numpy(),index=f.index).cumsum()
        paid=cumulative.reindex(cumulative.index.union(prices.index)).sort_index().ffill().reindex(prices.index).fillna(0.)
        all_cases={}
        for name,sc,fc in [('base',.0012,.0007),('stress',.0024,.0014)]:
            entry_fee=q*(prices.spot.iloc[0]*sc+prices.future.iloc[0]*fc)
            nav=500-entry_fee+q*((prices.spot-prices.spot.iloc[0])-(prices.future-prices.future.iloc[0]))+paid
            nav.iloc[-1]-=q*(prices.spot.iloc[-1]*sc+prices.future.iloc[-1]*fc)
            daily_nav=nav.resample('1D').last()
            r=daily_nav.pct_change(fill_method=None);r.iloc[0]=daily_nav.iloc[0]/500-1
            dd=nav/nav.cummax().clip(lower=500)-1
            gross=q*(prices.spot+prices.future)/nav
            u={str(b):uncertainty(r,np.zeros(len(r)),20260908+j,trials=82,samples=10000,block=b) for b in [7,30,60]}
            all_cases[name]=dict(ending_equity=float(nav.iloc[-1]),daily_return_uncertainty=u,
                observed_hourly_max_drawdown=float(dd.min()),max_observed_gross=float(gross.max()),
                calendar_returns={str(y):float((1+v).prod()-1) for y,v in r.groupby(r.index.year)},
                passes_adjusted_mean_all_blocks=all(v['simultaneous_lower_mean_daily']>0 for v in u.values()))
            r.to_csv(out/f'{sym}_{name}_daily_returns.csv')
        results.append(dict(symbol=sym,cases=all_cases,missing_spot_hour_marks_carried=missing,
            note='Combined NAV uses futures trade-price marks; maintenance uses separate mark-price diagnostic. Hourly marks cannot bound intrahour paired-basis extremes. Cash benchmark0USDT excludes opportunity-cost/FX risk. No promotion.'))
        print(sym,{k:v['passes_adjusted_mean_all_blocks'] for k,v in all_cases.items()},flush=True)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=20260908,
        results=results,cumulative_hypotheses=82,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
