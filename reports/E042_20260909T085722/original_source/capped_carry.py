"""Conservative development-only carry sizing; no broker or transfer endpoints."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,load_data,code_hash
from carry_backtest import load_prices,rounded_quantity
from carry_screen import funding_diagnostic
from audit import uncertainty

def ledger(px,funding,spot_fee=.0012,future_fee=.0007,step=.001,min_notional=20):
    """Start80% gross; trim to80% after observed95% gross, one-hour delay.

    Flatten if wallet equity <25% of mark notional (20% jump plus assumed5%
    reserve). No actual maintenance-tier assertion. Never add after entry.
    Spot-sale proceeds remain spot cash; no assumed collateral transfer.
    """
    q=0.;wallet=500.;spot_cash=0.;entry_future=0.;pending=None;halt=False
    records=[];event_pos=0;f=funding.sort_index();trim_count=0
    for i,(ts,row) in enumerate(px.iterrows()):
        s=float(row.spot);p=float(row.future);mark=float(row.mark)
        while event_pos<len(f) and f.index[event_pos]<=ts:
            ev=f.iloc[event_pos]
            if i>0:wallet+=q*float(ev.mark_used)*float(ev.rate)
            event_pos+=1
        observed=bool(row.tradable)
        if i==0 and observed:
            q=rounded_quantity(500*.8*s/(s+p),s,step)
            if q*p<min_notional or q*s<5:raise ValueError('Initial hedge below minimum')
            entry_future=p;wallet=500-q*s-q*s*spot_fee-q*p*future_fee
        if pending is not None and observed:
            dq=q-pending
            if dq>0:
                # Treat residual below minimum as a requested full close; this
                # still requires reduce-only/dust verification before deployment.
                spot_cash+=dq*s*(1-spot_fee)
                wallet+=dq*(entry_future-p)-dq*p*future_fee
                q=pending;trim_count+=1
            pending=None
        if i==len(px)-1 and q>0:
            if not observed:raise ValueError('No observed terminal fill')
            spot_cash+=q*s*(1-spot_fee);wallet+=q*(entry_future-p)-q*p*future_fee;q=0.
        nav=spot_cash+q*s+wallet+q*(entry_future-p)
        margin_equity=wallet+q*(entry_future-mark)
        margin_ratio=margin_equity/(q*mark) if q>0 else None
        gross=q*(s+p)/nav
        records.append(dict(time=ts,nav=nav,q=q,gross=gross,margin_ratio=margin_ratio,spot_cash=spot_cash,wallet=wallet))
        # A mandatory halt cannot be downgraded to an ordinary trim while an
        # outage defers the fill. Only a separate human-controlled restart could
        # clear it; no restart exists in this research ledger.
        if q>0 and (halt or margin_ratio<.25):
            pending=0.;halt=True
        elif q>0 and gross>.95:
            newq=rounded_quantity(.8*nav*s/(s+p),s,step)
            if newq*p<min_notional or newq*s<5:newq=0.
            pending=min(q,newq)
    result=pd.DataFrame(records).set_index('time')
    return result,dict(trim_count=trim_count,collateral_halt=halt)

def main():
    eid='E008_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    sym='ETHUSDT';spot,_=load_data(sym);fut,_=load_prices(sym,'klines');mark,_=load_prices(sym,'markPriceKlines')
    px=pd.DataFrame(dict(spot=spot.open.reindex(fut.index),future=fut.open,mark=mark.open))
    px['tradable']=px.spot.notna()&(spot.volume.reindex(fut.index)>0)&(fut.volume>0)
    px.spot=px.spot.ffill()  # valuation only; tradable separately prevents fills
    fp=sorted((ROOT/'data/raw/funding').glob('ETHUSDT*combined*'))[-1]
    f,_,_=funding_diagnostic(json.loads(fp.read_text()))
    f=f.loc[(f.index.floor('8h')>px.index[0])&(f.index.floor('8h')<px.index[-1])]
    proxy=mark.open.reindex(f.index.floor('8h')).to_numpy()
    f['mark_used']=f['mark'].fillna(pd.Series(proxy,index=f.index))
    cases={}
    for name,sc,fc in [('base',.0012,.0007),('stress',.0024,.0014)]:
        path,details=ledger(px,f,sc,fc)
        dn=path.nav.resample('1D').last();r=dn.pct_change();r.iloc[0]=dn.iloc[0]/500-1
        dd=path.nav/path.nav.cummax().clip(lower=500)-1
        cases[name]=dict(**details,ending_equity_usdt=float(path.nav.iloc[-1]),
            indicative_cagr=float((path.nav.iloc[-1]/500)**(365.25/len(r))-1),
            max_observed_gross=float(path.gross.max()),max_observed_hourly_drawdown=float(dd.min()),
            minimum_margin_ratio=float(path.margin_ratio.min()),
            calendar_returns={str(y):float((1+v).prod()-1) for y,v in r.groupby(r.index.year)},
            uncertainty=uncertainty(r,np.zeros(len(r)),20260908,trials=83,samples=10000,block=30))
        path.to_csv(out/f'{name}_ledger.csv');print(name,cases[name]['indicative_cagr'],cases[name]['max_observed_gross'],flush=True)
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=code_hash(),git_commit=None,seed=20260908,cumulative_hypotheses=83,
        cases=cases,validation_accessed=False,final_test_accessed=False,
        verdict='RESEARCH-PROMISING ONLY; unverified account tiers/fees, mark proxies and latency remain. One-hour decision lag is not guaranteed hard cap protection.'),indent=2,allow_nan=False))
    print('OUTPUT',out)

if __name__=='__main__':main()
