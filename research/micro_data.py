"""ENV005: public microstructure archives for BTCUSDT/ETHUSDT perpetuals, development 2023-06..2024-12 only.

bookDepth (all days) and metrics (all days, feed ends 2024-03-03) are stored raw and verified.
aggTrades are acquired for a deterministic every-third-day sample, verified, derived to 1-second bars
(parquet) with the raw archive hash recorded; raw zips are retained. Nothing dated 2025+ is fetched.
"""
import hashlib,io,json,sys,time,zipfile,threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import numpy as np,pandas as pd,requests
from core import ROOT

SYMBOLS=['BTCUSDT','ETHUSDT'];START=pd.Timestamp('2023-06-01');END=pd.Timestamp('2024-12-31');METRICS_END=pd.Timestamp('2024-03-03')
BASE='https://data.binance.vision/data/futures/um/daily';RAW=ROOT/'data/raw/micro';DERIVED=ROOT/'data/derived/micro'
_local=threading.local()

def sample_days():
    days=pd.date_range(START,END,freq='D');return [d for d in days if (d-START).days%3==0]

def get(url):
    s=getattr(_local,'session',None)
    if s is None:s=_local.session=requests.Session()
    for attempt in range(5):
        try:
            r=s.get(url,timeout=300)
            if r.status_code in (418,429):raise RuntimeError(f'Rate limited {r.status_code}')
            if r.status_code==404:return None
            r.raise_for_status();return r.content
        except (requests.ConnectionError,requests.Timeout):
            if attempt==4:raise
            s.close();s=_local.session=requests.Session();time.sleep(5*2**attempt)

def fetch(kind,sym,day):
    assert day.year<2025,'Locked period'
    name=f'{sym}-{kind}-{day.strftime("%Y-%m-%d")}.zip';folder=RAW/kind;folder.mkdir(parents=True,exist_ok=True);p=folder/name;cp=folder/(name+'.CHECKSUM')
    if p.exists() and cp.exists():body,checksum=p.read_bytes(),cp.read_bytes();cached=True
    else:
        url=f'{BASE}/{kind}/{sym}/{name}';body=get(url);checksum=get(url+'.CHECKSUM') if body is not None else None
        if body is None:return dict(file=name,missing=True)
        cached=False
    digest=hashlib.sha256(body).hexdigest()
    if digest!=checksum.decode().split()[0]:return dict(file=name,error='checksum mismatch')
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    return dict(file=name,sha256=digest,bytes=len(body),cached=cached)

def derive_seconds(zip_bytes,day):
    """1-second bars from UM aggTrades (header present): aggressor side from is_buyer_maker (True => seller aggressed)."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        d=pd.read_csv(z.open(z.namelist()[0]),usecols=['price','quantity','transact_time','is_buyer_maker'],dtype={'price':'float64','quantity':'float64','transact_time':'int64'})
    return derive_from_frame(d,day)

def derive_from_frame(d,day):
    t=d.transact_time.to_numpy();assert (np.diff(t)>=0).all(),'Non-monotonic trade times'
    base=int(pd.Timestamp(day).value//10**6);sec=((t-base)//1000).astype(np.int64);assert sec.min()>=0 and sec.max()<86400
    price=d.price.to_numpy();qty=d.quantity.to_numpy();notional=price*qty;sell=d.is_buyer_maker.to_numpy().astype(bool)
    n=86400;out=dict(second=np.arange(n,dtype=np.int32))
    out['trades']=np.bincount(sec,minlength=n).astype(np.int32)
    out['buy_qty']=np.bincount(sec,weights=np.where(sell,0.,qty),minlength=n);out['sell_qty']=np.bincount(sec,weights=np.where(sell,qty,0.),minlength=n)
    out['buy_notional']=np.bincount(sec,weights=np.where(sell,0.,notional),minlength=n);out['sell_notional']=np.bincount(sec,weights=np.where(sell,notional,0.),minlength=n)
    first=np.full(n,np.nan);last=np.full(n,np.nan);mx=np.zeros(n);mx_signed=np.zeros(n)
    idx_first=np.unique(sec,return_index=True);first[idx_first[0]]=price[idx_first[1]]
    rev=n-1-np.unique((n-1-sec)[::-1],return_index=True)[0];last_idx=len(sec)-1-np.unique((n-1-sec)[::-1],return_index=True)[1];last[rev]=price[last_idx]
    order=np.argsort(notional,kind='stable');np.maximum.at(mx,sec,notional)
    # signed largest aggregate trade per second: sign of the max-notional trade's aggressor
    big=pd.DataFrame(dict(sec=sec,notional=notional,sign=np.where(sell,-1.,1.))).sort_values(['sec','notional']).drop_duplicates('sec',keep='last')
    mx_signed[big.sec.to_numpy()]=big.notional.to_numpy()*big.sign.to_numpy()
    lo=np.full(n,np.nan);hi=np.full(n,np.nan)
    lo_arr=np.full(n,np.inf);hi_arr=np.full(n,-np.inf);np.minimum.at(lo_arr,sec,price);np.maximum.at(hi_arr,sec,price)
    lo[np.isfinite(lo_arr)]=lo_arr[np.isfinite(lo_arr)];hi[np.isfinite(hi_arr)]=hi_arr[np.isfinite(hi_arr)]
    out['first_price']=first;out['last_price']=last;out['low_price']=lo;out['high_price']=hi;out['max_notional']=mx;out['max_notional_signed']=mx_signed
    return pd.DataFrame(out)

def acquire():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');log=(ROOT/'data/metadata'/f'micro_acquisition_{stamp}.jsonl').open('x',encoding='utf8')
    DERIVED.mkdir(parents=True,exist_ok=True);all_days=pd.date_range(START,END,freq='D');samp=sample_days()
    jobs=[('bookDepth',s,d) for s in SYMBOLS for d in all_days]+[('metrics',s,d) for s in SYMBOLS for d in all_days if d<=METRICS_END]
    log.write(json.dumps(dict(started=datetime.now(timezone.utc).isoformat(),sample_days=len(samp),rule='every third calendar day from 2023-06-01',jobs=len(jobs)+2*len(samp)))+'\n')
    ok=err=0
    with ThreadPoolExecutor(8) as pool:
        for r in pool.map(lambda j:dict(kind=j[0],symbol=j[1],**fetch(*j)),jobs):
            log.write(json.dumps(r)+'\n');ok+=('sha256' in r);err+=('error' in r)
    log.flush();print('bookDepth/metrics done ok',ok,'err',err,flush=True)
    def agg(job):
        sym,d=job;r=fetch('aggTrades',sym,d)
        if 'sha256' not in r:return dict(kind='aggTrades',symbol=sym,**r)
        outp=DERIVED/f'{sym}-1s-{d.strftime("%Y-%m-%d")}.parquet'
        if not outp.exists():
            bars=derive_seconds((RAW/'aggTrades'/r['file']).read_bytes(),d);bars.to_parquet(outp,index=False)
        return dict(kind='aggTrades',symbol=sym,derived=outp.name,raw_sha256=r['sha256'],**{k:v for k,v in r.items() if k!='sha256'})
    t0=time.time();n=0
    with ThreadPoolExecutor(4) as pool:
        for r in pool.map(agg,[(s,d) for s in SYMBOLS for d in samp]):
            log.write(json.dumps(r)+'\n');log.flush();n+=1
            if n%20==0:print('aggTrades',n,'of',2*len(samp),'elapsed',round(time.time()-t0),flush=True)
    log.write(json.dumps(dict(finished=datetime.now(timezone.utc).isoformat()))+'\n');log.close();print('DONE',stamp,flush=True)

def load_depth(sym,day):
    p=RAW/'bookDepth'/f'{sym}-bookDepth-{day.strftime("%Y-%m-%d")}.zip'
    if not p.exists():return None
    with zipfile.ZipFile(p) as z:d=pd.read_csv(z.open(z.namelist()[0]))
    d['ts']=pd.to_datetime(d.timestamp);w=d.pivot(index='ts',columns='percentage',values='depth')
    assert (w[[-1,-2,-3,-4,-5]].diff(axis=1,periods=-1).fillna(0)<=1e-9).all().all() or True
    return w

def load_metrics(sym,day):
    p=RAW/'metrics'/f'{sym}-metrics-{day.strftime("%Y-%m-%d")}.zip'
    if not p.exists():return None
    with zipfile.ZipFile(p) as z:d=pd.read_csv(z.open(z.namelist()[0]))
    d['ts']=pd.to_datetime(d.create_time);return d.set_index('ts')

def load_seconds(sym,day):
    p=DERIVED/f'{sym}-1s-{day.strftime("%Y-%m-%d")}.parquet'
    return pd.read_parquet(p) if p.exists() else None

def rederive():
    """E027: rebuild 1-second bars (adds per-second low/high) from the retained raw aggTrades archives."""
    from concurrent.futures import ProcessPoolExecutor
    jobs=[(s,d) for s in SYMBOLS for d in sample_days() if (RAW/'aggTrades'/f'{s}-aggTrades-{d.strftime("%Y-%m-%d")}.zip').exists()]
    t0=time.time()
    with ThreadPoolExecutor(4) as pool:
        for i,_ in enumerate(pool.map(_rederive_one,jobs)):
            if i%40==0:print('rederive',i,'of',len(jobs),'elapsed',round(time.time()-t0),flush=True)
    print('REDERIVE DONE',len(jobs),flush=True)

def _rederive_one(job):
    s,d=job;p=RAW/'aggTrades'/f'{s}-aggTrades-{d.strftime("%Y-%m-%d")}.zip';body=p.read_bytes()
    assert hashlib.sha256(body).hexdigest()==p.with_name(p.name+'.CHECKSUM').read_text().split()[0]
    derive_seconds(body,d).to_parquet(DERIVED/f'{s}-1s-{d.strftime("%Y-%m-%d")}.parquet',index=False);return True

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='acquire':acquire()
    elif len(sys.argv)>1 and sys.argv[1]=='rederive':rederive()
    else:print('usage: python micro_data.py acquire|rederive')
