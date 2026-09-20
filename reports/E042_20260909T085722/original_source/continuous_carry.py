"""Falsify a lower-turnover carry baseline; no collateral-transfer assumption."""
import json
from datetime import datetime,timezone
import pandas as pd
import numpy as np
from core import ROOT,load_data,code_hash
from carry_backtest import load_prices,run_case
from carry_screen import funding_diagnostic

def main():
    eid='E006_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    exchange=json.loads(sorted((ROOT/'data/metadata').glob('futures_exchangeInfo*'))[-1].read_text(encoding='utf8'))
    result=[]
    for sym in ['BTCUSDT','ETHUSDT']:
        spot,_=load_data(sym);fut,_=load_prices(sym,'klines');mark,_=load_prices(sym,'markPriceKlines')
        prices=pd.DataFrame(dict(spot=spot.open.reindex(fut.index),spot_volume=spot.volume.reindex(fut.index),future=fut.open,future_volume=fut.volume,mark=mark.open,mark_high=mark.high))
        fp=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
        funding,_,_=funding_diagnostic(json.loads(fp.read_text()))
        funding['scheduled']=funding.index.floor('8h')
        proxy=mark.open.reindex(pd.DatetimeIndex(funding.scheduled)).to_numpy()
        funding['mark_used']=funding['mark'].fillna(pd.Series(proxy,index=funding.index))
        rule=next(x for x in exchange['symbols'] if x['symbol']==sym)
        filters={x['filterType']:x for x in rule['filters']}
        step=float(filters['LOT_SIZE']['stepSize']);mn=float(filters['MIN_NOTIONAL']['notional'])
        cases={}
        for name,sc,fc in [('base',.0012,.0007),('stress',.0024,.0014)]:
            r=run_case(prices,funding,step,mn,sc,fc,continuous=True)
            # At a current mark, an additional 20% price jump reduces wallet by
            # 20% of current marked short notional. Maintenance adds more risk.
            r['survives_additional_20pct_mark_jump_before_maintenance']=r['lowest_adverse_margin_ratio']>.2
            cases[name]=r
        result.append(dict(symbol=sym,cases=cases,verdict='BASELINE DIAGNOSTIC; no margin-verification or OOS claim'))
        print(sym,{k:(round(v['indicative_cagr'],4),round(v['lowest_adverse_margin_ratio'],4)) for k,v in cases.items()},flush=True)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=None,results=result,
        cumulative_hypotheses=82,validation_accessed=False,final_test_accessed=False,
        limitations='Fixed initial quantity; no transfers, hedge rebalancing or cap on gross drift. 20% jump is declared stress, not estimated probability. Mark proxies and unverified maintenance tiers remain.'),indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
