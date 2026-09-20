"""ENV006: Binance spot aggTrades for the ENV005 sampled days, derived to the same 1-second bars.

Spot daily archives are header-less with eight columns; is_buyer_maker True means the buyer was the
maker, i.e. the seller aggressed. Verified by archive checksum; raw retained; nothing dated 2025+.
"""
import hashlib,io,json,sys,time,zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import pandas as pd
from core import ROOT
from micro_data import SYMBOLS,sample_days,get,derive_from_frame

BASE='https://data.binance.vision/data/spot/daily/aggTrades';RAW=ROOT/'data/raw/micro/spot_aggTrades';DERIVED=ROOT/'data/derived/micro_spot'
COLS=['agg_trade_id','price','quantity','first_trade_id','last_trade_id','transact_time','is_buyer_maker','is_best_match']

def parse_spot(zip_bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        d=pd.read_csv(z.open(z.namelist()[0]),header=None)
    if not str(d.iloc[0,0]).lstrip('-').isdigit():d=d.iloc[1:].reset_index(drop=True)
    assert d.shape[1]==len(COLS),f'Unexpected spot schema width {d.shape[1]}';d.columns=COLS
    d['price']=d.price.astype(float);d['quantity']=d.quantity.astype(float);d['transact_time']=d.transact_time.astype('int64')
    d['is_buyer_maker']=d.is_buyer_maker.astype(str).str.lower().eq('true')
    return d[['price','quantity','transact_time','is_buyer_maker']]

def one(job):
    sym,day=job;assert day.year<2025;name=f'{sym}-aggTrades-{day.strftime("%Y-%m-%d")}.zip';RAW.mkdir(parents=True,exist_ok=True);p=RAW/name;cp=RAW/(name+'.CHECKSUM')
    if p.exists() and cp.exists():body,checksum=p.read_bytes(),cp.read_bytes();cached=True
    else:
        url=f'{BASE}/{sym}/{name}';body=get(url)
        if body is None:return dict(symbol=sym,file=name,missing=True)
        checksum=get(url+'.CHECKSUM');cached=False
    digest=hashlib.sha256(body).hexdigest()
    if digest!=checksum.decode().split()[0]:return dict(symbol=sym,file=name,error='checksum mismatch')
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    outp=DERIVED/f'{sym}-1s-{day.strftime("%Y-%m-%d")}.parquet'
    if not outp.exists():derive_from_frame(parse_spot(body),day).to_parquet(outp,index=False)
    return dict(symbol=sym,file=name,sha256=digest,bytes=len(body),derived=outp.name,cached=cached)

def acquire():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');DERIVED.mkdir(parents=True,exist_ok=True);jobs=[(s,d) for s in SYMBOLS for d in sample_days()];t0=time.time();n=0
    with (ROOT/'data/metadata'/f'spot_micro_acquisition_{stamp}.jsonl').open('x',encoding='utf8') as log:
        log.write(json.dumps(dict(started=datetime.now(timezone.utc).isoformat(),jobs=len(jobs)))+'\n')
        with ThreadPoolExecutor(4) as pool:
            for r in pool.map(one,jobs):
                log.write(json.dumps(r)+'\n');log.flush();n+=1
                if n%20==0:print('spot',n,'of',len(jobs),'elapsed',round(time.time()-t0),flush=True)
        log.write(json.dumps(dict(finished=datetime.now(timezone.utc).isoformat()))+'\n')
    print('DONE',stamp,flush=True)

def load_spot_seconds(sym,day):
    p=DERIVED/f'{sym}-1s-{day.strftime("%Y-%m-%d")}.parquet';return pd.read_parquet(p) if p.exists() else None

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='acquire':acquire()
    else:print('usage: python spot_micro_data.py acquire')
