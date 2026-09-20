"""ENV007: Binance volatility index (BVOL, per-second implied volatility index) archives, 2023-06-20..2024-12-31.

Public GET, checksum-verified, raw retained; derived to 1-minute closes. Nothing dated 2025+.
"""
import hashlib,io,json,sys,time,zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT
from micro_data import get

VOL={'BTCUSDT':'BTCBVOLUSDT','ETHUSDT':'ETHBVOLUSDT'};START=pd.Timestamp('2023-06-20');END=pd.Timestamp('2024-12-31')
BASE='https://data.binance.vision/data/option/daily/BVOLIndex';RAW=ROOT/'data/raw/option/BVOLIndex';DERIVED=ROOT/'data/derived/bvol'

def derive_minutes(zip_bytes,day):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:d=pd.read_csv(z.open(z.namelist()[0]))
    t=d.calc_time.to_numpy();assert (np.diff(t)>=0).all();base=int(pd.Timestamp(day).value//10**6);m=((t-base)//60000).astype(int);assert m.min()>=0 and m.max()<1440
    v=d.index_value.to_numpy(float);last=np.full(1440,np.nan);idx=np.unique(m[::-1],return_index=True);last[idx[0]]=v[::-1][idx[1]]
    return pd.DataFrame(dict(minute=np.arange(1440),bvol_close=last,ticks=np.bincount(m,minlength=1440)))

def one(job):
    sym,day=job;assert day.year<2025;vs=VOL[sym];name=f'{vs}-BVOLIndex-{day.strftime("%Y-%m-%d")}.zip';RAW.mkdir(parents=True,exist_ok=True);p=RAW/name;cp=RAW/(name+'.CHECKSUM')
    if p.exists() and cp.exists():body,checksum=p.read_bytes(),cp.read_bytes();cached=True
    else:
        url=f'{BASE}/{vs}/{name}';body=get(url)
        if body is None:return dict(symbol=sym,file=name,missing=True)
        checksum=get(url+'.CHECKSUM');cached=False
    digest=hashlib.sha256(body).hexdigest()
    if digest!=checksum.decode().split()[0]:return dict(symbol=sym,file=name,error='checksum mismatch')
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    outp=DERIVED/f'{sym}-bvol1m-{day.strftime("%Y-%m-%d")}.parquet'
    if not outp.exists():derive_minutes(body,day).to_parquet(outp,index=False)
    return dict(symbol=sym,file=name,sha256=digest,bytes=len(body),derived=outp.name,cached=cached)

def acquire():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');DERIVED.mkdir(parents=True,exist_ok=True);jobs=[(s,d) for s in VOL for d in pd.date_range(START,END,freq='D')];t0=time.time();n=0
    with (ROOT/'data/metadata'/f'bvol_acquisition_{stamp}.jsonl').open('x',encoding='utf8') as log:
        log.write(json.dumps(dict(started=datetime.now(timezone.utc).isoformat(),jobs=len(jobs)))+'\n')
        with ThreadPoolExecutor(8) as pool:
            for r in pool.map(one,jobs):
                log.write(json.dumps(r)+'\n');n+=1
                if n%100==0:log.flush();print('bvol',n,'of',len(jobs),'elapsed',round(time.time()-t0),flush=True)
        log.write(json.dumps(dict(finished=datetime.now(timezone.utc).isoformat()))+'\n')
    print('DONE',stamp,flush=True)

def load_bvol(sym,day):
    p=DERIVED/f'{sym}-bvol1m-{day.strftime("%Y-%m-%d")}.parquet';return pd.read_parquet(p) if p.exists() else None

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='acquire':acquire()
