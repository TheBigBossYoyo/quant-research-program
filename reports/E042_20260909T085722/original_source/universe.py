"""Survivorship-aware USDT-M perpetual daily panel from checksum-verified archives.

Development 2020-2024 (extended from 2022-2024 in E016); loader refuses 2025+ files. Membership comes from archive
existence (delisted contracts retained), never from a current symbol list.
"""
import hashlib,io,json,zipfile
import numpy as np,pandas as pd
from core import ROOT

KLINE_COLS=['open_time','open','high','low','close','volume','close_time','quote_volume','count','taker_buy_volume','taker_buy_quote_volume','ignore']
FUNDING_COLS=['calc_time','funding_interval_hours','last_funding_rate']
DEV_START=pd.Timestamp('2020-01-01',tz='UTC')  # E016: development extended backward; 2025+ still refused
DEV_END=pd.Timestamp('2025-01-01',tz='UTC')
MIN_HISTORY_BARS=60;LIQUIDITY_WINDOW=30;MIN_MEDIAN_QUOTE_VOLUME=20e6

def _verified(p):
    body=p.read_bytes();digest=hashlib.sha256(body).hexdigest()
    assert digest==p.with_name(p.name+'.CHECKSUM').read_text().split()[0],f'Checksum failure {p.name}'
    assert '-2025-' not in p.name and '-2026-' not in p.name,'Validation/holdout file present in development loader'
    return body,digest

def _csv(body,cols):
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        names=z.namelist();assert len(names)==1
        d=pd.read_csv(z.open(names[0]),header=None)
    assert d.shape[1]==len(cols),f'Unexpected schema width {d.shape[1]}'
    if not str(d.iloc[0,0]).lstrip('-').isdigit():d=d.iloc[1:].copy()
    d.columns=cols
    return d.apply(pd.to_numeric,errors='raise')

def load_klines(root=None):
    root=(root or ROOT/'data/raw/universe/klines_1d');frames=[];sources=[]
    for p in sorted(root.glob('*.zip')):
        body,digest=_verified(p);d=_csv(body,KLINE_COLS);d['symbol']=p.name.split('-1d-')[0]
        frames.append(d);sources.append(dict(file=p.name,sha256=digest))
    d=pd.concat(frames,ignore_index=True)
    d['time']=pd.to_datetime(d.open_time,unit='ms',utc=True)
    assert (d.time.dt.hour==0).all() and (d.time.dt.minute==0).all(),'Non-midnight daily bar'
    assert (d.time>=DEV_START).all() and (d.time<DEV_END).all()
    assert not d.duplicated(['symbol','time']).any(),'Duplicate symbol-day'
    assert (d[['open','high','low','close']]>0).all().all() and np.isfinite(d[['open','close','volume','quote_volume','taker_buy_volume']]).all().all()
    # Archive defect: a few daily rows report taker volume above total volume. Quarantine the
    # flow field only (prices/volume retained) and report it; never silently accept or drop.
    bad=d.taker_buy_volume>d.volume*(1+1e-9)
    quarantined=[dict(symbol=s,time=str(pd.to_datetime(o,unit='ms',utc=True)),volume=float(v),taker_buy_volume=float(x)) for s,o,v,x in d.loc[bad,['symbol','open_time','volume','taker_buy_volume']].itertuples(index=False)]
    d.loc[bad,'taker_buy_volume']=np.nan
    assert (d.taker_buy_volume.fillna(0)<=d.volume*(1+1e-9)).all()
    days=pd.date_range(DEV_START,DEV_END,freq='D',inclusive='left')
    panels={k:d.pivot(index='time',columns='symbol',values=k).reindex(days) for k in ['open','high','low','close','volume','quote_volume','taker_buy_volume']}
    return panels,dict(files=len(sources),symbols=int(d.symbol.nunique()),rows=len(d),taker_volume_quarantined=quarantined,sources=sources)

def load_funding(root=None):
    root=(root or ROOT/'data/raw/universe/fundingRate');frames=[];sources=[]
    for p in sorted(root.glob('*.zip')):
        body,digest=_verified(p);d=_csv(body,FUNDING_COLS);d['symbol']=p.name.split('-fundingRate-')[0]
        frames.append(d);sources.append(dict(file=p.name,sha256=digest))
    d=pd.concat(frames,ignore_index=True)
    d['time']=pd.to_datetime(d.calc_time,unit='ms',utc=True);d['rate']=d.last_funding_rate.astype(float)
    d['interval_hours']=d.funding_interval_hours.astype(int)
    assert (d.time>=DEV_START).all() and (d.time<DEV_END).all() and np.isfinite(d.rate).all()
    d=d.sort_values(['symbol','time']).drop_duplicates(['symbol','time'])
    return d[['symbol','time','rate','interval_hours']].reset_index(drop=True),dict(files=len(sources),symbols=int(d.symbol.nunique()),events=len(d),intervals=d.interval_hours.value_counts().to_dict(),sources=sources)

def daily_funding(funding,days,symbols):
    """Sum of rates whose settlement falls inside calendar day d (00:00 <= s < 24:00 UTC)."""
    f=funding.copy();f['day']=f.time.dt.floor('D')
    g=f.groupby(['day','symbol']).rate.sum().unstack().reindex(index=days,columns=symbols)
    return g.fillna(0.)

def eligibility(panels):
    close=panels['close'];qv=panels['quote_volume']
    history=close.notna().cumsum()>=MIN_HISTORY_BARS
    liquid=qv.rolling(LIQUIDITY_WINDOW,min_periods=LIQUIDITY_WINDOW).median()>=MIN_MEDIAN_QUOTE_VOLUME
    return history&liquid&close.notna()&(close>0)

def features(panels,fund_daily):
    close=panels['close'];vol=panels['volume'];tb=panels['taker_buy_volume']
    net=(2*tb-vol).rolling(7).sum();v7=vol.rolling(7).sum()
    qv=panels['quote_volume'];lr=np.log(close/close.shift(1))
    return dict(ret7=close/close.shift(7)-1,ret30=close/close.shift(30)-1,ret90=close/close.shift(90)-1,  # ret90: E023 long-horizon momentum
        fund7=fund_daily.rolling(7).sum().where(close.notna()),flow7=(net/v7).where(v7>0),
        # E018 risk/attention characteristics, all trailing windows requiring complete data
        vol30=lr.rolling(30).std(),abnvol7=qv.rolling(7).mean()/qv.rolling(90).mean(),
        amihud30=(lr.abs()/qv.where(qv>0)).rolling(30).mean())

def forward_open_return(open_panel,start=2,end=9):
    """Open(t+start) to open(t+end); a symbol missing at t+end exits at its last observed open."""
    entry=open_panel.shift(-start);exit_=open_panel.ffill().shift(-end)
    r=exit_/entry-1
    return r.where(entry.notna()&exit_.notna())

def rebalance_days(days,first_valid,step=7):
    return days[(days>=first_valid)][::step]

def quintile_weights(score,elig,direction,min_names=10):
    """Equal-weight top quintile +, bottom quintile -, each 50% gross; zero net."""
    s=score.where(elig).dropna()
    if len(s)<min_names:return pd.Series(dtype=float)
    n=max(1,int(np.floor(.2*len(s))));ranked=s.sort_values()
    w=pd.Series(0.,index=s.index);w[ranked.index[-n:]]=.5/n;w[ranked.index[:n]]=-.5/n
    return direction*w[w!=0]
