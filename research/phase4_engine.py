"""E040 signal-preserving accounting correction; no parameter selection.

Funding inputs are cash per unit settled at the labelled bar OPEN, BEFORE orders.
Non-boundary events must be resolved upstream, never silently grouped into a bar.
"""
import hashlib, json, re
from pathlib import Path
import numpy as np
import pandas as pd
from ta_engine import atr
from ta_ensemble import ensemble_weight
from ta_volcomp import breakout_state

class ProtectedValidationError(ValueError): pass
class FinalHoldoutProtectedError(ValueError): pass

def guard_dates(start, end):
    a,b=pd.Timestamp(start),pd.Timestamp(end)
    if a.tzinfo is None:a=a.tz_localize('UTC')
    if b.tzinfo is None:b=b.tz_localize('UTC')
    if a>=pd.Timestamp('2026-01-01',tz='UTC') or b>pd.Timestamp('2026-01-01',tz='UTC'):
        raise FinalHoldoutProtectedError('2026+ final holdout protected')
    if a>=pd.Timestamp('2025-01-01',tz='UTC') or b>pd.Timestamp('2025-01-01',tz='UTC'):
        raise ProtectedValidationError('2025 locked; no authorization implemented')
    if b<=a:raise ValueError('Invalid interval')

def guard_path(path):
    text=str(path)
    if re.search(r'(?:^|[-_/])202[6-9](?:[-_/]|$)',text):raise FinalHoldoutProtectedError(text)
    if re.search(r'(?:^|[-_/])2025(?:[-_/]|$)',text):raise ProtectedValidationError(text)

def verified_bytes(path):
    p=Path(path);guard_path(p)
    raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
    if h!=p.with_name(p.name+'.CHECKSUM').read_text().split()[0]:raise ValueError('Checksum '+str(p))
    return raw,h

def aggregate(hourly):
    guard_dates(hourly.index.min(),hourly.index.max()+pd.Timedelta(hours=1))
    g=hourly.resample('4h',label='left',closed='left',origin='epoch')
    b=g.agg(dict(open='first',high='max',low='min',close='last',volume='sum',quote_volume='sum',taker_base='sum',trades='sum'))
    complete=g.open.count().eq(4)&g.close.count().eq(4)
    b.loc[~complete,:]=np.nan
    b['complete']=complete
    b['execution_open']=hourly.open.reindex(b.index)
    b['valuation_close']=g.close.last()
    b['observed_low']=g.low.min();b['observed_high']=g.high.max()
    # Candle open is a price proxy, not proof of an executable quote or depth.
    b['tradable']=b.execution_open.notna()
    return b

def signals(b):
    a=atr(b,14)
    comp=(a.rolling(250,min_periods=120).rank(pct=True)<.2).shift(1).fillna(False)
    return {'trend':ensemble_weight(b.close),'breakout':breakout_state(b,20,comp),'atr':a}

def ledger(b,target,cost,component,funding=None,atr_series=None,delay=0,initial=10000.):
    """Original targets, size-on-target-change and breakout stop/block rules.

    Mark-to-market bookkeeping, net trade episodes, absorbing insolvency.
    Missing signal bars retain prior intent; known executable opens stay available.
    Stops on partial bars use observed extremes, whose unresolved ordering is logged.
    """
    step=b.index[1]-b.index[0] if len(b)>1 else pd.Timedelta(hours=4)
    guard_dates(b.index.min(),b.index.max()+step)
    if component not in ('trend','breakout'):raise ValueError(component)
    tg=target.shift(delay).fillna(0).clip(-1,1).to_numpy()
    av=atr_series.to_numpy() if atr_series is not None else np.full(len(b),np.nan)
    f=np.zeros(len(b)) if funding is None else funding.reindex(b.index).fillna(0).to_numpy()
    eq=initial;q=0.;mark=np.nan;held=0.;pending=0.;blocked=0.;stop=np.nan;best=np.nan
    rows=[];trades=[];ep=None;ruin=False
    values=b.to_dict('records')
    def close_episode(ts,reason):
        nonlocal ep
        if ep is not None:
            ep.update(exit_time=ts,reason=reason,ret=ep['pnl']/ep['entry_equity'])
            trades.append(ep);ep=None
    for i,(ts,row) in enumerate(zip(b.index,values)):
        before=eq;fees=0.;paid=0.;turn=0.;lp=0.;sp=0.
        o=float(row.get('execution_open',row['open']))
        c=float(row.get('valuation_close',row['close']))
        hi=float(row.get('observed_high',row['high']));lo=float(row.get('observed_low',row['low']))
        complete=bool(row.get('complete',True))
        if ruin:
            rows.append(dict(time=ts,equity=0.,position=0.,units=0.,turnover=0.,cost=0.,funding=0.,long_pnl=0.,short_pnl=0.,ruin=True));continue
        def post(delta,side):
            nonlocal eq,lp,sp
            eq+=delta
            if side>0:lp+=delta
            elif side<0:sp+=delta
            if ep is not None:ep['pnl']+=delta
        if np.isfinite(o):
            if np.isfinite(mark):post(q*(o-mark),np.sign(q))
            mark=o
        paid=q*f[i];post(-paid,np.sign(q))
        if eq<=0:
            ruin=True;eq=0.;close_episode(ts,'insolvency');q=0.
        if not ruin and np.isfinite(o) and row.get('tradable',True):
            want=pending
            if component=='breakout' and want==blocked and blocked!=0:want=0.
            if row.get('orderable',True) and want!=held:
                target_equity=eq
                oldside=np.sign(q);newside=np.sign(want)
                if oldside and oldside!=newside:
                    x=abs(q)*o;fee=x*cost;turn+=x;fees+=fee;post(-fee,oldside)
                    close_episode(ts,'signal');q=0.;held=0.
                if newside:
                    if ep is None:ep=dict(entry_time=ts,side=int(newside),entry_equity=eq,pnl=0.)
                    nq=want*target_equity/o if component=='trend' else want*eq/(1+cost)/o
                    x=abs(nq-q)*o;fee=x*cost;turn+=x;fees+=fee;post(-fee,newside);q=nq
                    if component=='breakout':
                        best=o;stop=o-want*3*av[i-1] if i and np.isfinite(av[i-1]) else np.nan
                held=want
            if component=='breakout' and q and np.isfinite(stop):
                hit=(lo<=stop) if q>0 else (hi>=stop)
                if hit:
                    side=np.sign(q);fill=min(o,stop) if q>0 else max(o,stop)
                    post(q*(fill-mark),side);x=abs(q)*fill;fee=x*cost;turn+=x;fees+=fee;post(-fee,side)
                    close_episode(ts,'stop');blocked=side;q=0.;held=0.;stop=np.nan;pending=0.;mark=fill
        if np.isfinite(c):
            if np.isfinite(mark):post(q*(c-mark),np.sign(q))
            mark=c
        if component=='breakout' and q and complete and np.isfinite(av[i]):
            best=max(best,row.get('trailing_high',hi)) if q>0 else min(best,row.get('trailing_low',lo))
            new=best-np.sign(q)*3*av[i]
            stop=max(stop,new) if q>0 else min(stop,new)
        if eq<=0:
            ruin=True;eq=0.;close_episode(ts,'insolvency');q=0.;held=0.
        if complete:
            want=tg[i]
            if component=='breakout':
                if want!=blocked:blocked=0.
                pending=0. if want==blocked and blocked else want
                if held and want==held:pending=held
            else:pending=want
        # Preserve original terminal convention: breakout closes; trend stays marked.
        if i==len(b)-1 and q and component=='breakout' and not ruin:
            x=abs(q)*mark;fee=x*cost;turn+=x;fees+=fee;post(-fee,np.sign(q));close_episode(ts,'terminal');q=0.;held=0.
        rows.append(dict(time=ts,equity=eq,position=q*mark/eq if eq>0 else 0.,units=q,turnover=turn,cost=fees,funding=paid,long_pnl=lp,short_pnl=sp,ruin=ruin))
    if ep is not None:close_episode(b.index[-1],'terminal_mark_open')
    return pd.DataFrame(rows).set_index('time'),pd.DataFrame(trades)

def combine(ra,rb,method='equal'):
    ra,rb=ra.align(rb,join='inner')
    if method=='equal':w=pd.Series(.5,index=ra.index)
    elif method=='inverse_vol':
        va=ra.rolling(60).std().shift(1);vb=rb.rolling(60).std().shift(1)
        w=(1/va)/((1/va)+(1/vb))
    else:raise ValueError(method)
    return (w*ra+(1-w)*rb).fillna(0.),w
