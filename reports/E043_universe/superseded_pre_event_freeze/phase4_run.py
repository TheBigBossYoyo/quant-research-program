"""Frozen E040 replication data verification and execution. No parameter search."""
import io,json,hashlib,zipfile,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,COLS
from phase4_engine import verified_bytes,guard_dates,aggregate,signals,ledger,combine
from phase4_data import freeze_check,universe
from universe import _csv,FUNDING_COLS
from phase4_stats import returns,stats

DAYS=pd.date_range('2022-01-01','2025-01-01',inclusive='left',freq='D',tz='UTC')
END=pd.Timestamp('2025-01-01',tz='UTC')

def read_hourly(sym,kind):
    frames=[];sources=[]
    for y in range(2020,2025):
        for m in range(1,13):
            name=f'{sym}-1h-{y}-{m:02d}.zip';p=ROOT/'data/raw/phase4'/kind/name
            if not p.exists():p=ROOT/'data/raw/futures'/kind/name
            if not p.exists():continue
            raw,sha=verified_bytes(p)
            with zipfile.ZipFile(io.BytesIO(raw)) as z:d=pd.read_csv(z.open(z.namelist()[0]),header=None)
            if not str(d.iloc[0,0]).isdigit():d=d.iloc[1:].reset_index(drop=True)
            d.columns=COLS;d=d.apply(pd.to_numeric,errors='raise');d.index=pd.to_datetime(d.time,unit='ms',utc=True)
            guard_dates(d.index.min(),d.index.max()+pd.Timedelta(hours=1))
            frames.append(d);sources.append(dict(file=str(p.relative_to(ROOT)),sha256=sha))
    if not frames:raise ValueError('No data '+sym+' '+kind)
    d=pd.concat(frames).sort_index()
    if not d.index.is_unique:raise ValueError('Duplicate '+sym+' '+kind)
    if not ((d.index.minute==0)&(d.index.second==0)).all():raise ValueError('Timestamp alignment')
    if not np.isfinite(d[['open','high','low','close']]).all().all():raise ValueError('Nonfinite OHLC')
    if not (d[['open','high','low','close']]>0).all().all():raise ValueError('Nonpositive prices')
    if not ((d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1))).all():raise ValueError('OHLC consistency')
    if not ((d.close_time>=d.time)&(d.close_time<d.time+3600000)).all():raise ValueError('Candle close timestamp')
    return d,sources

def load(sym):
    d,sources=read_hourly(sym,'klines');mark,msources=read_hourly(sym,'markPriceKlines');sources+=msources
    if sym=='MATICUSDT':
        # Notice predates event. Exit at the last scheduled4h open (08UTC)
        # before known09UTC automatic settlement, not a hindsight terminal close.
        termination=pd.Timestamp('2024-09-04 08:00',tz='UTC')
    else:termination=None
    expected_end=termination if termination is not None else END-pd.Timedelta(hours=1)
    if d.index.max()<expected_end:raise ValueError('Unexpected truncation '+sym+' '+str(d.index.max()))
    volume_bad=d[(d.taker_base>d.volume*(1+1e-8))|(d.taker_quote>d.quote_volume*(1+1e-8))|(d.volume<0)|(d.quote_volume<0)]
    anomalies=d[d.close.pct_change(fill_method=None).abs()>.25]
    grid=pd.date_range(d.index.min(),expected_end,freq='h',tz='UTC');missing=grid.difference(d.index);h=d.reindex(grid)
    bfull=aggregate(h[['open','high','low','close','volume','quote_volume','taker_base','trades']]);sg=signals(bfull)
    b=bfull[bfull.index>=DAYS[0]].copy();sg={k:v.reindex(b.index) for k,v in sg.items()}
    if termination is not None:
        b=b.loc[:termination];sg={k:v.reindex(b.index) for k,v in sg.items()}
        o=float(d.open.loc[termination])
        for col in ['open','high','low','close','execution_open','valuation_close','observed_high','observed_low']:b.loc[termination,col]=o
        b.loc[termination,'complete']=False
        for c in ['trend','breakout']:sg[c].iloc[-2]=0.
    fframes=[]
    for y in [2021,2022,2023,2024]:
        for m in range(1,13):
            if y==2021 and m<12:continue
            p=ROOT/'data/raw/universe/fundingRate'/f'{sym}-fundingRate-{y}-{m:02d}.zip'
            if not p.exists():continue
            raw,sha=verified_bytes(p);fd=_csv(raw,FUNDING_COLS);fframes.append(fd);sources.append(dict(file=str(p.relative_to(ROOT)),sha256=sha))
    f=pd.concat(fframes).sort_values('calc_time');f['time']=pd.to_datetime(f.calc_time,unit='ms',utc=True)
    if f.time.duplicated().any():raise ValueError('Duplicate funding '+sym)
    f['scheduled']=f.time.dt.round('h');jitter=(f.time-f.scheduled).dt.total_seconds().abs()*1000
    if jitter.max()>60000:raise ValueError('Non-resolvable funding timestamp '+sym)
    f=f[(f.scheduled>=DAYS[0])&(f.scheduled<=b.index.max())]
    if not (f.scheduled.dt.hour%4==0).all():raise ValueError('Non-boundary funding needs event ledger '+sym)
    if f.scheduled.duplicated().any():raise ValueError('Multiple settlements same scheduled boundary')
    dates=pd.DatetimeIndex(f.scheduled);rates=pd.Series(f.last_funding_rate.to_numpy(),index=dates)
    used=mark.open.reindex(dates);fallback=used.isna();used=used.fillna(d.open.reindex(dates))
    if used.isna().any():raise ValueError('No observable funding price '+sym)
    gaps=f.scheduled.diff().dt.total_seconds()/3600
    missing_funding=f.loc[gaps>f.funding_interval_hours.clip(lower=8)+.01,['scheduled','funding_interval_hours']]
    fcash=(used*rates).reindex(b.index).fillna(0.)
    stress_cash=(used*.0001).reindex(b.index).fillna(0.)
    integrity=dict(symbol=sym,start=str(d.index.min()),end=str(d.index.max()),primary_bars=len(b),missing_hours=len(missing),missing_timestamps=[str(x) for x in missing],incomplete_4h_bars=int((~b.complete).sum()),zero_volume_hours=int((d.volume==0).sum()),volume_inconsistencies=volume_bad[['time','volume','taker_base','quote_volume','taker_quote']].to_dict('records'),large_hourly_moves=anomalies[['time','open','close']].to_dict('records'),funding_events=len(f),funding_nonzero_jitter=int((jitter>0).sum()),funding_max_jitter_ms=float(jitter.max()),missing_funding_intervals=missing_funding.astype(str).to_dict('records'),funding_mark_fallbacks=int(fallback.sum()),contract_exit=str(termination) if termination is not None else None,contract_exit_source='https://www.binance.com/en/support/announcement/detail/6a6de383727f4659a3050f7982e1620f' if termination is not None else None,sources=sources)
    if len(missing_funding):raise ValueError('Funding coverage gaps '+sym+' '+str(integrity['missing_funding_intervals']))
    return b,sg,fcash,stress_cash,integrity

def integrity():
    freeze_check();out=ROOT/'reports/E043_universe';rows=[]
    for sym in universe()+['BTCUSDT','ETHUSDT']:
        try:
            b,s,f,a,meta=load(sym);meta['status']='PASS_WITH_DISCLOSED_LIMITATIONS';rows.append(meta)
            print(sym,'rows',len(b),'gaps',meta['missing_hours'],'funding',meta['funding_events'],'fallbacks',meta['funding_mark_fallbacks'],flush=True)
        except Exception as e:
            rows.append(dict(symbol=sym,status='BLOCKED',error=repr(e)));print(sym,'BLOCKED',repr(e),flush=True)
    p=out/'data_integrity.json';p.write_text(json.dumps(rows,indent=2));print('INTEGRITY',p,flush=True)
    if any(x['status']=='BLOCKED' for x in rows):raise RuntimeError('Data integrity not passed; no strategy evaluation')
    (out/'DATA_READY.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest())

if __name__=='__main__':integrity()
