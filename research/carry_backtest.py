"""Paired spot/perpetual diagnostic with explicit, unverified margin gate."""
import json,hashlib,zipfile
from decimal import Decimal,ROUND_FLOOR
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from core import ROOT,COLS,config,code_hash,load_data
from carry_screen import funding_diagnostic

def rounded_quantity(budget,price,step):
    return float((Decimal(str(budget))/Decimal(str(price))/Decimal(str(step))).to_integral_value(rounding=ROUND_FLOOR)*Decimal(str(step)))

def paired_pnl(q,s0,s1,f0,f1,funding,spot_cost,futures_cost):
    fees=q*((s0+s1)*spot_cost+(f0+f1)*futures_cost)
    basis=q*((s1-s0)-(f1-f0))
    return basis+funding-fees,basis,fees

def parse_price_csv(f):
    d=pd.read_csv(f,header=None)
    assert d.shape[1]==12,'Unexpected futures price schema'
    if str(d.iloc[0,0])=='open_time':d=d.iloc[1:].copy()
    d.columns=['open_time']+COLS[1:]
    return d.apply(pd.to_numeric,errors='raise')

def load_prices(sym,kind):
    frames=[];sources=[]
    for year in range(2022,2025):
        for month in range(1,13):
            p=ROOT/'data/raw/futures'/kind/f'{sym}-1h-{year}-{month:02}.zip'
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            assert digest==p.with_name(p.name+'.CHECKSUM').read_text().split()[0]
            with zipfile.ZipFile(p) as z:
                with z.open(z.namelist()[0]) as f:
                    # Trade klines carry a header; older mark archives may not.
                    d=parse_price_csv(f)
            d.index=pd.to_datetime(d.open_time,unit='ms',utc=True)
            assert np.isfinite(d[['open','high','low','close']]).all().all()
            assert (d[['open','high','low','close']]>0).all().all()
            assert (d.high>=d[['open','low','close']].max(axis=1)).all()
            assert (d.low<=d[['open','high','close']].min(axis=1)).all()
            frames.append(d);sources.append(dict(file=str(p.relative_to(ROOT)),sha256=digest))
    full=pd.concat(frames)
    expected=pd.date_range('2022-01-01','2025-01-01',freq='h',inclusive='left',tz='UTC')
    assert full.index.is_unique and full.index.is_monotonic_increasing
    archive_missing=expected.difference(full.index)
    if kind=='markPriceKlines':
        for day in archive_missing.normalize().unique():
            paths=sorted((ROOT/'data/raw/futures/mark_supplements').glob(f'{sym}_{day.strftime("%Y-%m-%d")}*.json'))
            if not paths:continue
            p=paths[-1];body=p.read_bytes();rows=json.loads(body)
            r=pd.DataFrame(rows,columns=['open_time']+COLS[1:]).apply(pd.to_numeric)
            r.index=pd.to_datetime(r.open_time,unit='ms',utc=True)
            r=r.loc[r.index.isin(archive_missing)]
            assert (r.high>=r[['open','close','low']].max(axis=1)).all()
            assert (r.low<=r[['open','close','high']].min(axis=1)).all()
            full=pd.concat([full,r]).sort_index()
            sources.append(dict(file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(body).hexdigest(),role='REST gap supplement'))
    assert full.index.is_unique
    assert len(expected.difference(full.index))==0
    assert full.index.min()==expected.min() and full.index.max()==expected.max()
    return full,dict(rows=len(full),original_archive_missing_hours=len(archive_missing),missing_hours=0,sources=sources)

def run_case(prices,funding,step,min_notional,spot_cost,fut_cost,omit_proxy=False,continuous=False):
    equity=500.;months=[];risk_breach=False
    groups=[('2022-2024 continuous',prices)] if continuous else prices.groupby(prices.index.strftime('%Y-%m'))
    for month,px in groups:
        # Require observed first/last prices, not forward-filled trade prices.
        tradable=px[['spot','future','mark']].notna().all(axis=1)&(px.spot_volume>0)&(px.future_volume>0)
        p=px.loc[tradable];entry=p.index[0];exit=p.index[-1]
        s0=float(p.spot.iloc[0]);s1=float(p.spot.iloc[-1]);f0=float(p.future.iloc[0]);f1=float(p.future.iloc[-1])
        # Budget both legs so a positive basis cannot push initial gross over 1x.
        q=rounded_quantity(equity*s0/(s0+f0),s0,step)
        if q*f0<min_notional or q*s0<5 or q<=0:
            months.append(dict(month=month,equity_start=equity,equity_end=equity,net_return=0.,traded=False,reason='Minimum notional'))
            continue
        ev=funding.loc[(funding.scheduled>entry)&(funding.scheduled<exit)].copy()
        assert ev.mark_used.notna().all()
        payment=q*ev.mark_used*ev.rate
        if omit_proxy:payment=payment.where(ev['mark'].notna(),0.)
        total_funding=float(payment.sum())
        net,basis,fees=paired_pnl(q,s0,s1,f0,f1,total_funding,spot_cost,fut_cost)
        collateral=equity-q*s0-q*s0*spot_cost-q*f0*fut_cost
        # Funding credited after its actual timestamp. Intrahour high risk test
        # excludes the current hour payment to avoid relying on its ordering.
        grid=px.loc[entry:exit].index
        hourly_pay=pd.Series(payment.to_numpy(),index=ev.index).resample('h').sum().reindex(grid,fill_value=0.)
        prior=hourly_pay.cumsum().shift(1).fillna(0.)
        mark=px.loc[grid,'mark'];high=px.loc[grid,'mark_high']
        account=collateral+q*(f0-mark)+prior
        adverse=collateral+q*(f0-high)+prior+hourly_pay.clip(upper=0.)
        ratio=adverse/(q*high)
        zero=bool((adverse<=0).any());risk_breach|=zero
        start_equity=equity;equity+=net
        months.append(dict(month=month,entry=str(entry),exit=str(exit),q=q,equity_start=start_equity,equity_end=equity,
            net_return=net/start_equity,traded=True,funding_income=total_funding,basis_pnl=basis,fees=fees,
            minimum_futures_wallet=float(account.min()),minimum_adverse_wallet=float(adverse.min()),
            min_adverse_margin_ratio=float(ratio.min()),zero_equity_breach=zero,
            funding_events=len(ev),proxy_funding_events=int(ev['mark'].isna().sum())))
        if zero:break  # Do not continue a ghost account through necessary insolvency.
    rets=pd.Series([x['net_return'] for x in months])
    curve=(1+rets).cumprod();peak=curve.cummax().clip(lower=1.)
    elapsed_years=(prices.index[-1]-prices.index[0]).total_seconds()/(365.25*86400)
    return dict(initial_capital_usdt=500.,ending_equity_usdt=equity,
        cumulative_return=equity/500.-1,months=len(months),
        indicative_cagr=float((equity/500.)**(1/elapsed_years)-1),
        monthly_sharpe=float(rets.mean()/rets.std(ddof=1)*np.sqrt(12)) if rets.std()>0 else None,
        month_end_max_drawdown=None if continuous else float((curve/peak-1).min()),
        positive_months=int((rets>0).sum()),necessary_solvency_breach=risk_breach,
        lowest_adverse_margin_ratio=min(x['min_adverse_margin_ratio'] for x in months if x['traded']),
        total_fees_usdt=sum(x.get('fees',0.) for x in months),
        total_funding_income_usdt=sum(x.get('funding_income',0.) for x in months),
        total_basis_pnl_usdt=sum(x.get('basis_pnl',0.) for x in months),monthly=months,
        note='Indicative paired-account path with mark proxies; month-end DD understates intramonth risk. Maintenance/liquidation unverified; no eligibility verdict from these returns.')

def main():
    cfg=config();eid='E005_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    exchange=json.loads(sorted((ROOT/'data/metadata').glob('futures_exchangeInfo*'))[-1].read_text(encoding='utf8'))
    results=[]
    for sym in cfg['symbols']:
        spot,si=load_data(sym);future,fi=load_prices(sym,'klines');mark,mi=load_prices(sym,'markPriceKlines')
        prices=pd.DataFrame(dict(spot=spot.open.reindex(future.index),spot_volume=spot.volume.reindex(future.index),
            future=future.open,future_volume=future.volume,mark=mark.open,mark_high=mark.high))
        fp=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
        funding,_,fd=funding_diagnostic(json.loads(fp.read_text()))
        funding['scheduled']=funding.index.floor('8h')
        proxy=mark.open.reindex(pd.DatetimeIndex(funding.scheduled)).to_numpy()
        funding['mark_used']=funding['mark'].fillna(pd.Series(proxy,index=funding.index))
        known=funding['mark'].notna()
        err=np.abs(proxy[known]/funding.loc[known,'mark'].to_numpy()-1)*1e4
        rule=next(x for x in exchange['symbols'] if x['symbol']==sym)
        filters={x['filterType']:x for x in rule['filters']}
        step=float(filters['LOT_SIZE']['stepSize']);mn=float(filters['MIN_NOTIONAL']['notional'])
        cases={case:run_case(prices,funding,step,mn,sc,fc,omit) for case,sc,fc,omit in
            [('base',.0012,.0007,False),('stress',.0024,.0014,False),('omit_missing_mark_funding',.0012,.0007,True)]}
        results.append(dict(symbol=sym,integrity=dict(spot=si,future=fi,mark=mi,funding=fd),
            funding_proxy_overlap_absolute_error_bps=dict(n=len(err),median=float(np.median(err)),p99=float(np.quantile(err,.99)),max=float(err.max())),
            cases=cases,verdict='NOT ELIGIBLE: margin schedule, actual fees and historical executable quotes unresolved'))
        print(sym,{k:round(v['indicative_cagr'],4) for k,v in cases.items()},flush=True)
    payload=dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=None,results=results,
        validation_accessed=False,final_test_accessed=False,notes='Two existing carry hypotheses, three stress cases. Current quantity steps/min notionals applied historically as feasibility assumption, not historical rules. 500 USDT is illustrative and not EUR500.')
    (out/'results.json').write_text(json.dumps(payload,indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
