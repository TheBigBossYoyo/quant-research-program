"""Funding-rate economics only: deliberately not a carry-strategy backtest."""
import json
import hashlib
from datetime import datetime,timezone
from decimal import Decimal,ROUND_CEILING
import numpy as np
import pandas as pd
from core import ROOT,code_hash,config

def funding_diagnostic(rows):
    d=pd.DataFrame(rows)
    d.index=pd.to_datetime(d.fundingTime,unit='ms',utc=True)
    assert d.index.is_unique and d.index.is_monotonic_increasing
    assert d.index.min()>=pd.Timestamp('2022-01-01',tz='UTC')
    assert d.index.max()<pd.Timestamp('2025-01-01',tz='UTC')
    d['rate']=pd.to_numeric(d.fundingRate)
    d['mark']=pd.to_numeric(d.markPrice,errors='coerce')
    assert np.isfinite(d.rate).all()
    scheduled=d.index.floor('8h')
    expected=pd.date_range('2022-01-01','2025-01-01',freq='8h',inclusive='left',tz='UTC')
    assert scheduled.is_unique and len(expected.difference(scheduled))==0
    jitter=((d.index-scheduled).total_seconds())
    assert jitter.max()<60,'Unexpected funding schedule; do not silently force 8h'
    monthly=d.rate.resample('MS').sum()
    # Fixed normalized notional illustration; not fixed-quantity realized PnL.
    cases={'fee_only':.003,'base':.0038,'stress':.0076}
    m=pd.DataFrame({'sum_funding_rates':monthly})
    for case,cost in cases.items():
        m[case+'_normalized_combined_capital_yield']=(monthly-cost)/2
    annual={str(y):dict(sum_funding_rates=float(x.rate.sum()),
        normalized_funding_only_on_2x_notional_capital=float(x.rate.sum()/2),
        monthly_reset_base_normalized_yield=float((x.rate.sum()-12*.0038)/2)) for y,x in d.groupby(d.index.year)}
    return d,m,dict(events=len(d),missing_scheduled_events=0,max_timestamp_jitter_seconds=float(jitter.max()),
        missing_funding_mark_prices=int(d.mark.isna().sum()),
        positive_event_fraction=float((d.rate>0).mean()),negative_event_fraction=float((d.rate<0).mean()),
        rate_autocorrelation=float(d.rate.autocorr()),annual=annual,
        monthly_base_hurdle_positive=int((monthly>.0038).sum()),
        monthly_stress_hurdle_positive=int((monthly>.0076).sum()),months=len(monthly),
        min_monthly_rate_sum=float(monthly.min()),max_monthly_rate_sum=float(monthly.max()),
        note='Sum of realized rates is a normalized constant-notional diagnostic, not actual income for a fixed-quantity hedge; basis PnL and margin omitted.')

def main():
    cfg=config();eid='E004_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    ep=sorted((ROOT/'data/metadata').glob('futures_exchangeInfo*'))[-1]
    pp=sorted((ROOT/'data/metadata').glob('futures_premiumIndex*'))[-1]
    exchange=json.loads(ep.read_text(encoding='utf8'));prices=json.loads(pp.read_text(encoding='utf8'))
    results=[]
    for sym in cfg['symbols']:
        p=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
        d,m,diagnostic=funding_diagnostic(json.loads(p.read_text()))
        m.to_csv(out/f'{sym}_monthly.csv')
        rule=next(x for x in exchange['symbols'] if x['symbol']==sym)
        price=next(x for x in prices if x['symbol']==sym)
        filters={x['filterType']:x for x in rule['filters']}
        mark=Decimal(price['markPrice'])
        step=Decimal(filters['LOT_SIZE']['stepSize'])
        minqty=Decimal(filters['LOT_SIZE']['minQty'])
        mn=Decimal(filters['MIN_NOTIONAL']['notional'])
        q=max(minqty,(mn/mark/step).to_integral_value(rounding=ROUND_CEILING)*step)
        # Published futures step is coarser than spot step for these two symbols;
        # minimum must still be refreshed and checked against all market filters.
        capital_floor=2*q*mark*(1+Decimal('.0019'))
        results.append(dict(symbol=sym,input_file=p.name,input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            diagnostic=diagnostic,current_filters=filters,current_mark_price=str(mark),
            minimum_hedge_quantity=str(q),illustrative_combined_capital_floor_usdt=str(capital_floor),
            capital_floor_warning='Current mark-based notional approximation, excludes conversion and margin safety buffers; not minimum efficient capital.',
            verdict='INCOMPLETE: funding mechanism measurable; full carry net PnL and margin survival unverified'))
        print(sym,json.dumps(diagnostic),flush=True)
    result=dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=None,
        hypotheses=2,cumulative_signal_asset_hypotheses=80,results=results,
        exchange_snapshot=ep.name,exchange_sha256=hashlib.sha256(ep.read_bytes()).hexdigest(),
        price_snapshot=pp.name,price_sha256=hashlib.sha256(pp.read_bytes()).hexdigest(),
        funding_fee_assumptions='spot 10bps + futures 5bps each side; two legs entry/exit 30bps normalized leg notional. Base add 2bps friction per each of 4 executions =38bps; stress76bps. Divide by2 for spot+equal futures cash allocation. Not portfolio return.',
        validation_accessed=False,final_test_accessed=False)
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
