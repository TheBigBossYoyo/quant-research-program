"""Bounded signed-perpetual development screen; not a liquidation engine."""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,code_hash
from carry_backtest import load_prices,rounded_quantity
from carry_screen import funding_diagnostic

def signed_ledger(prices,desired,unit_funding,fee=.0007,step=.001,min_notional=20):
    """50% entry gross; size changes only when side changes. No borrowing.

    Mark-to-market futures equity includes signed funding. Risk can latch a halt
    and close on the following observation. Maintenance rules remain unverified.
    """
    equity=500.;q=0.;last=float(prices.future.iloc[0]);intent=0;halt=False
    trade_prices=prices.future.to_numpy();marks=prices.mark.to_numpy()
    funding_values=unit_funding.to_numpy();targets=desired.to_numpy()
    tradable=prices.tradable.to_numpy() if 'tradable' in prices else np.ones(len(prices),dtype=bool)
    if not tradable[-1]:raise ValueError('Terminal observation is not executable')
    rows=[]
    for i,ts in enumerate(prices.index):
        p=float(trade_prices[i]);m=float(marks[i])
        equity+=q*(p-last)-q*float(funding_values[i])
        if equity<=0:raise ValueError('Necessary insolvency; no continuing ghost account')
        want=0 if halt or i==len(prices)-1 else int(targets[i])
        turnover=0.
        if want!=intent and tradable[i]:
            amount=rounded_quantity(.5*equity/(1+2*fee),p,step)
            newq=want*amount
            if newq and abs(newq)*p<min_notional:newq=0.
            turnover=abs(newq-q)*p
            equity-=turnover*fee;q=newq;intent=want if q else 0
        mark_equity=equity+q*(m-p)
        gross=abs(q)*m/mark_equity if mark_equity>0 else float('inf')
        if q and (gross>.95 or mark_equity<.25*abs(q)*m):halt=True
        rows.append(dict(time=ts,nav=equity,quantity=q,turnover_notional=turnover,gross=gross,halt=halt))
        last=p
    return pd.DataFrame(rows).set_index('time')

def prepare(sym):
    f,fi=load_prices(sym,'klines');m,mi=load_prices(sym,'markPriceKlines')
    p=pd.DataFrame(dict(future=f.open,mark=m.open,tradable=f.volume>0))
    fp=sorted((ROOT/'data/raw/funding').glob(f'{sym}*combined*'))[-1]
    funding,_,_=funding_diagnostic(json.loads(fp.read_text()))
    proxy=m.open.reindex(funding.index.floor('8h')).to_numpy()
    marks=funding['mark'].fillna(pd.Series(proxy,index=funding.index))
    # First observation at or after each realized funding event, using the units
    # held since the previous observation. Events at initial time are excluded.
    times=p.index.searchsorted(funding.index,side='left')
    cash=np.zeros(len(p))
    for i,v in zip(times,(marks*funding.rate).to_numpy()):
        if 0<i<len(cash):cash[i]+=v
    return f,p,pd.Series(cash,index=p.index),dict(futures=fi,marks=mi,funding_file=fp.name)

def performance(path):
    nav=path.nav;dn=nav.resample('1D').last();r=dn.pct_change();r.iloc[0]=dn.iloc[0]/500-1
    dd=nav/nav.cummax().clip(lower=500)-1
    return dict(ending_equity=float(nav.iloc[-1]),cumulative_return=float(nav.iloc[-1]/500-1),
        cagr=float((nav.iloc[-1]/500)**(365.25/len(dn))-1),
        daily_sharpe=float(r.mean()/r.std()*np.sqrt(365.25)) if r.std()>0 else 0.,
        max_observed_drawdown=float(dd.min()),max_observed_gross=float(path.gross.max()),
        fills=int((path.turnover_notional>0).sum()),turnover_usdt=float(path.turnover_notional.sum()),
        halted=bool(path.halt.any()),calendar_returns={str(y):float((1+x).prod()-1) for y,x in r.groupby(r.index.year)})

def main():
    eid='E010_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting_code_hash=code_hash()
    rows=[];sources=[]
    for sym in ['BTCUSDT','ETHUSDT']:
        f,px,funding,meta=prepare(sym);sources.append(dict(symbol=sym,**meta))
        for tf in [1,4,24]:
            close=f.close.resample(f'{tf}h').last()
            specifications=[(family,n) for family in ['momentum','reversal'] for n in [3,12,48]]+[('long_baseline',0)]
            for family,n in specifications:
                s=pd.Series(1.,index=close.index) if family=='long_baseline' else close/close.shift(n)-1
                if family=='reversal':s=-s
                target=np.sign(s).shift(2).fillna(0).reindex(px.index).ffill().fillna(0)
                for case,fee in [('fee_only',.0005),('base',.0007),('stress',.0014)]:
                    path=signed_ledger(px,target,funding,fee=fee,min_notional=50 if sym=='BTCUSDT' else 20)
                    rows.append(dict(symbol=sym,timeframe_hours=tf,family=family,lookback=n,case=case,fee=fee,**performance(path)))
            print(sym,tf,'screened',flush=True)
    survivors=[]
    for r in rows:
        if r['case']!='stress' or r['family']=='long_baseline':continue
        baseline=next(x for x in rows if x['symbol']==r['symbol'] and x['timeframe_hours']==r['timeframe_hours'] and x['family']=='long_baseline' and x['case']=='stress')
        if r['cagr']>0 and r['daily_sharpe']>max(0.,baseline['daily_sharpe']) and sum(v>0 for v in r['calendar_returns'].values())>=2 and not r['halted']:
            survivors.append({k:r[k] for k in ['symbol','timeframe_hours','family','lookback']})
    assert starting_code_hash==code_hash(),'Source changed during experiment; do not misattribute results'
    result=dict(experiment_id=eid,code_hash=starting_code_hash,git_commit=None,seed=None,additional_hypotheses=36,cumulative_hypotheses=119,
        rows=rows,sources=sources,survivors=survivors,validation_accessed=False,final_test_accessed=False,
        verdict='CHEAP DEVELOPMENT SCREEN ONLY; margin, price/funding timestamp micro-ordering and executable quotes unverified. Gross risk actions lag one observation.')
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':main()
