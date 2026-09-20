"""Phase 3 technical-architecture engine: causal indicators, signed-position ledger with stops, metrics.

Signals are computed from completed bars; a target decided at the close of bar t is executed at the open of
bar t+1 (or the next tradable open). Stops are checked on bars after entry using high/low; a stop fills at
the stop price, or at the bar open when the bar opens through it. Costs per side on executed notional.
No leverage above 1x notional. Funding (perpetuals) is applied per bar from a per-bar cash series if given.
"""
import numpy as np,pandas as pd

# ---------- indicators (all trailing / completed-bar) ----------
def sma(x,n):return x.rolling(n).mean()
def ema(x,n):return x.ewm(span=n,adjust=False,min_periods=n).mean()
def wma(x,n):
    w=np.arange(1,n+1,dtype=float);return x.rolling(n).apply(lambda v:np.dot(v,w)/w.sum(),raw=True)
def true_range(b):return pd.concat([b.high-b.low,(b.high-b.close.shift(1)).abs(),(b.low-b.close.shift(1)).abs()],axis=1).max(axis=1)
def atr(b,n):return true_range(b).ewm(alpha=1/n,adjust=False,min_periods=n).mean()  # Wilder smoothing
def rsi(x,n):
    d=x.diff();up=d.clip(lower=0).ewm(alpha=1/n,adjust=False,min_periods=n).mean();dn=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False,min_periods=n).mean()
    rs=up/dn.replace(0,np.nan);return 100-100/(1+rs)
def donchian(b,n):return b.high.rolling(n).max(),b.low.rolling(n).min()
def adx(b,n):
    up=b.high.diff();dn=-b.low.diff();pdm=((up>dn)&(up>0))*up;ndm=((dn>up)&(dn>0))*dn;tr=true_range(b)
    atr_=tr.ewm(alpha=1/n,adjust=False,min_periods=n).mean();pdi=100*pdm.ewm(alpha=1/n,adjust=False,min_periods=n).mean()/atr_;ndi=100*ndm.ewm(alpha=1/n,adjust=False,min_periods=n).mean()/atr_
    dx=100*(pdi-ndi).abs()/(pdi+ndi).replace(0,np.nan);return dx.ewm(alpha=1/n,adjust=False,min_periods=n).mean(),pdi,ndi
def supertrend(b,n,mult):
    """Returns direction (+1 up / -1 down) and the active band, computed causally bar by bar."""
    a=atr(b,n);hl2=(b.high+b.low)/2;up=hl2+mult*a;dn=hl2-mult*a;c=b.close.to_numpy();upv=up.to_numpy();dnv=dn.to_numpy()
    n_=len(b);direction=np.full(n_,np.nan);band=np.full(n_,np.nan);fu=np.nan;fd=np.nan;d=0
    for i in range(n_):
        if not np.isfinite(upv[i]) or not np.isfinite(c[i]):continue
        fu=upv[i] if not np.isfinite(fu) or upv[i]<fu or c[i-1]>fu else fu
        fd=dnv[i] if not np.isfinite(fd) or dnv[i]>fd or c[i-1]<fd else fd
        if d==0:d=1 if c[i]>fu else -1
        elif d==1 and c[i]<fd:d=-1
        elif d==-1 and c[i]>fu:d=1
        direction[i]=d;band[i]=fd if d==1 else fu
    return pd.Series(direction,index=b.index),pd.Series(band,index=b.index)
def bollinger(x,n,k):m=sma(x,n);s=x.rolling(n).std(ddof=0);return m,s,(x-m)/s.replace(0,np.nan),(2*k*s)/m
def macd(x,f=12,s=26,g=9):m=ema(x,f)-ema(x,s);sig=ema(m,g);return m,sig,m-sig
def rolling_vwap(b,n):pv=(b.close*b.volume).rolling(n).sum();v=b.volume.rolling(n).sum();return pv/v.replace(0,np.nan)

# ---------- ledger ----------
def run_ledger(b,target,cost,stop_atr=None,atr_series=None,trail=False,funding=None,size=None,long_only=False,initial=10000.):
    """b: bars with open/high/low/close/tradable. target: desired sign (-1/0/1) decided at close of bar t.
    size: optional per-bar fraction of equity notional (<=1). Returns (equity path, trades DataFrame)."""
    o=b.open.to_numpy();h=b.high.to_numpy();l=b.low.to_numpy();c=b.close.to_numpy();tr=b.tradable.to_numpy()
    tg=target.fillna(0).to_numpy().astype(float);sz=np.ones(len(b)) if size is None else size.fillna(0).clip(0,1).to_numpy()
    av=atr_series.to_numpy() if atr_series is not None else None;fnd=funding.reindex(b.index).fillna(0).to_numpy() if funding is not None else np.zeros(len(b))
    eq=initial;pos=0.;units=0.;entry=np.nan;stop=np.nan;best=np.nan;rows=[];trades=[];i_entry=-1;mfe=0.;mae=0.
    pending=0.;pend_size=1.;blocked=0.  # after a stop-out, the stopped direction stays blocked until the target leaves it
    for i in range(len(b)):
        if not np.isfinite(o[i]):rows.append(dict(time=b.index[i],equity=eq,position=pos));continue
        # 1) execute pending target at this open (decided at previous close)
        if tr[i] and pending!=pos:
            if pos!=0:
                pnl=units*(o[i]-entry);eq+=pnl-abs(units)*o[i]*cost;trades.append(dict(entry_time=b.index[i_entry],exit_time=b.index[i],side=int(np.sign(units)),ret=pnl/(abs(units)*entry),mfe=mfe,mae=mae,bars=i-i_entry,reason='signal'))
                pos=0.;units=0.
            if pending!=0:
                notional=eq*pend_size/(1+cost);units=pending*notional/o[i];eq-=abs(units)*o[i]*cost;entry=o[i];pos=pending;i_entry=i;mfe=mae=0.
                stop=(entry-pending*stop_atr*av[i-1]) if (stop_atr and av is not None and i>0 and np.isfinite(av[i-1])) else np.nan;best=entry
        # 2) stop check within the bar
        if pos!=0 and np.isfinite(stop):
            hit=(l[i]<=stop) if pos>0 else (h[i]>=stop)
            if hit and tr[i]:
                fill=stop if (o[i]>stop if pos>0 else o[i]<stop) else o[i]
                pnl=units*(fill-entry);eq+=pnl-abs(units)*fill*cost;trades.append(dict(entry_time=b.index[i_entry],exit_time=b.index[i],side=int(np.sign(units)),ret=pnl/(abs(units)*entry),mfe=mfe,mae=mae,bars=i-i_entry,reason='stop'))
                blocked=pos;pos=0.;units=0.;stop=np.nan;pending=0.
        # 3) mark to close, update excursions and trailing stop
        if pos!=0:
            eq_mark=eq+units*(c[i]-entry)
            mfe=max(mfe,pos*(h[i]/entry-1));mae=min(mae,pos*(l[i]/entry-1))
            if trail and stop_atr and av is not None and np.isfinite(av[i]):
                best=max(best,h[i]) if pos>0 else min(best,l[i]);new=best-pos*stop_atr*av[i];stop=max(stop,new) if pos>0 else min(stop,new) if np.isfinite(stop) else new
        else:eq_mark=eq
        eq_mark-=units*fnd[i] if pos!=0 else 0.;eq-=units*fnd[i] if pos!=0 else 0.
        rows.append(dict(time=b.index[i],equity=eq_mark,position=pos*sz[i] if pos!=0 else 0.))
        # 4) decide next target from this bar's close
        want=tg[i];pend_size=sz[i]
        if long_only and want<0:want=0.
        if want!=blocked:blocked=0.
        pending=0. if (want==blocked and blocked!=0) else want
        if pos!=0 and want==pos:pending=pos  # hold
    if pos!=0:
        last=c[-1];pnl=units*(last-entry);eq+=pnl-abs(units)*last*cost;trades.append(dict(entry_time=b.index[i_entry],exit_time=b.index[-1],side=int(np.sign(units)),ret=pnl/(abs(units)*entry),mfe=mfe,mae=mae,bars=len(b)-1-i_entry,reason='terminal'))
        rows[-1]['equity']=eq
    path=pd.DataFrame(rows).set_index('time');return path,pd.DataFrame(trades)

def metrics(path,trades,bars_per_year,initial=10000.):
    e=path.equity;r=e.pct_change().fillna(0.);daily=e.resample('1D').last().dropna();dr=daily.pct_change().dropna();years=len(e)/bars_per_year
    dd=e/e.cummax()-1;win=trades[trades.ret>0].ret if len(trades) else pd.Series(dtype=float);loss=trades[trades.ret<0].ret if len(trades) else pd.Series(dtype=float)
    gross=float(trades.ret.abs().sum()) if len(trades) else 0.
    out=dict(cagr=float((e.iloc[-1]/initial)**(1/max(years,1e-9))-1),sharpe=float(dr.mean()/dr.std()*np.sqrt(365)) if dr.std()>0 else 0.,
        sortino=float(dr.mean()*365/(np.sqrt(np.mean(np.minimum(dr,0)**2))*np.sqrt(365))) if (dr<0).any() else None,max_dd=float(dd.min()),
        trades=int(len(trades)),win_rate=float((trades.ret>0).mean()) if len(trades) else None,profit_factor=float(win.sum()/-loss.sum()) if len(loss) and loss.sum()<0 else None,
        payoff=float(win.mean()/-loss.mean()) if len(win) and len(loss) else None,expectancy=float(trades.ret.mean()) if len(trades) else None,
        skew=float(trades.ret.skew()) if len(trades)>2 else None,avg_bars=float(trades.bars.mean()) if len(trades) else None,exposure=float((path.position!=0).mean()),
        trades_per_year=float(len(trades)/max(years,1e-9)),calendar=({str(y):float(v.iloc[-1]/v.iloc[0]-1) for y,v in e.groupby(e.index.year)}))
    out['top5_trade_share']=float(trades.ret.nlargest(5).sum()/trades.ret[trades.ret>0].sum()) if len(trades) and (trades.ret>0).any() else None
    return out

def buy_hold(b,cost,initial=10000.):
    t=pd.Series(1.,index=b.index);return run_ledger(b,t,cost,long_only=True,initial=initial)
