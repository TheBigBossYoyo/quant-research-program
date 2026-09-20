"""ENV008: hourly bar history for Phase 3 (spot 2017-08..2024-12; UM perpetual 2020-01..2021-12 to extend 2022-24).

Public monthly archives, checksum-verified, raw retained. Loaders build 1h/4h/1d bars with complete
buckets only and refuse anything dated 2025+. 15m bars come from the existing 5m spot archives.
"""
import hashlib,io,json,sys,time,zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,COLS,load_data,aggregate
from micro_data import get

SYMBOLS=['BTCUSDT','ETHUSDT'];SPOT_RAW=ROOT/'data/raw/spot_1h';UM_RAW=ROOT/'data/raw/futures/klines'
SPOT_MONTHS=[f'{y}-{m:02d}' for y in range(2017,2025) for m in range(1,13) if f'{y}-{m:02d}'>='2017-08'];UM_MONTHS=[f'{y}-{m:02d}' for y in (2020,2021) for m in range(1,13)]

def _one(kind,sym,month):
    assert month<'2025-01'
    if kind=='spot':folder=SPOT_RAW;name=f'{sym}-1h-{month}.zip';url=f'https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{name}'
    else:folder=UM_RAW;name=f'{sym}-1h-{month}.zip';url=f'https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{name}'
    folder.mkdir(parents=True,exist_ok=True);p=folder/name;cp=folder/(name+'.CHECKSUM')
    if p.exists() and cp.exists():body,checksum=p.read_bytes(),cp.read_bytes();cached=True
    else:
        body=get(url)
        if body is None:return dict(kind=kind,file=name,missing=True)
        checksum=get(url+'.CHECKSUM');cached=False
    digest=hashlib.sha256(body).hexdigest()
    if digest!=checksum.decode().split()[0]:return dict(kind=kind,file=name,error='checksum mismatch')
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    return dict(kind=kind,file=name,sha256=digest,bytes=len(body),cached=cached)

def acquire():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');jobs=[('spot',s,m) for s in SYMBOLS for m in SPOT_MONTHS]+[('um',s,m) for s in SYMBOLS for m in UM_MONTHS]
    with (ROOT/'data/metadata'/f'ta_acquisition_{stamp}.jsonl').open('x',encoding='utf8') as log:
        with ThreadPoolExecutor(8) as pool:
            for r in pool.map(lambda j:_one(*j),jobs):log.write(json.dumps(r)+'\n')
    print('DONE',stamp,len(jobs),flush=True)

def _read(p):
    body=p.read_bytes();assert hashlib.sha256(body).hexdigest()==p.with_name(p.name+'.CHECKSUM').read_text().split()[0]
    with zipfile.ZipFile(io.BytesIO(body)) as z:d=pd.read_csv(z.open(z.namelist()[0]),header=None)
    if not str(d.iloc[0,0]).lstrip('-').isdigit():d=d.iloc[1:].reset_index(drop=True)
    d=d.iloc[:,:12];d.columns=COLS;d=d.apply(pd.to_numeric,errors='raise')
    unit='us' if d.time.iloc[0]>10**14 else 'ms';d.index=pd.to_datetime(d.time,unit=unit,utc=True);return d

def load_hourly(sym,kind):
    """Hourly OHLCV on a full hourly grid (missing hours NaN); development only (< 2025-01-01)."""
    folder=SPOT_RAW if kind=='spot' else UM_RAW;months=SPOT_MONTHS if kind=='spot' else UM_MONTHS+[f'{y}-{m:02d}' for y in (2022,2023,2024) for m in range(1,13)]
    frames=[_read(folder/f'{sym}-1h-{m}.zip') for m in months if (folder/f'{sym}-1h-{m}.zip').exists()]
    d=pd.concat(frames);assert d.index.is_unique and d.index.is_monotonic_increasing;assert d.index.max()<pd.Timestamp('2025-01-01',tz='UTC')
    assert (d[['open','high','low','close']]>0).all().all() and (d.high>=d[['open','close','low']].max(axis=1)).all() and (d.low<=d[['open','close','high']].min(axis=1)).all()
    grid=pd.date_range(d.index.min(),d.index.max(),freq='h',tz='UTC');d=d.reindex(grid)
    return d[['open','high','low','close','volume','quote_volume','taker_base','trades']]

def bars(hourly,tf):
    """Resample hourly to tf ('1h','4h','1D') with complete buckets only; bucket open is executable at bucket start."""
    if tf=='1h':b=hourly.copy()
    else:
        g=hourly.resample(tf,label='left',closed='left',origin='epoch');n={'4h':4,'1D':24}[tf]
        b=g.agg(dict(open='first',high='max',low='min',close='last',volume='sum',quote_volume='sum',taker_base='sum',trades='sum'))
        b.loc[g.open.count()!=n,:]=np.nan
    b['tradable']=b.open.notna()&(b.volume>0);return b

def bars_15m(sym):
    raw,_=load_data(sym);a=aggregate(raw,15);b=a[['open','high','low','close','volume','quote_volume','taker_base','trades']].copy()
    b['tradable']=a.execution_open.notna()&(a.execution_volume>0);b['open']=a.execution_open;return b

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='acquire':acquire()
