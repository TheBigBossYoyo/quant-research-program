"""ENV002: public GET-only acquisition of USDT-M perpetual daily klines and funding archives.

Development months 2020-01..2024-12 only (extended in ENV003); 2025 not acquired here; 2026 never.
Files are SHA256-verified against the archive checksums and logged with provenance.
No credentials, no order endpoints.
"""
import json,hashlib,time,sys,threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import requests
from acquire import now,ROOT

_local=threading.local()
def get(url):
    """Keep-alive GET with bounded retries; never retries a 418/429."""
    s=getattr(_local,'session',None)
    if s is None:s=_local.session=requests.Session()
    for attempt in range(5):
        try:
            r=s.get(url,timeout=40)
            if r.status_code in (418,429):raise RuntimeError(f'Rate limited; stop without retry: {r.status_code}')
            r.raise_for_status();return r.content
        except (requests.ConnectionError,requests.Timeout):
            # Transient outage: rebuild the session and back off (5s..80s) instead of failing fast.
            if attempt==4:raise
            s.close();s=_local.session=requests.Session();time.sleep(5*2**attempt)

DEV_MONTHS=[f'{y}-{m:02d}' for y in (2020,2021,2022,2023,2024) for m in range(1,13)]  # ENV003 extended development sample
BASE='https://data.binance.vision/data/futures/um/monthly'

def listing():
    p=sorted((ROOT/'data/metadata').glob('um_archive_listing_*.json'))[-1]
    return json.loads(p.read_text(encoding='utf8'))['symbols'],p.name

def items():
    symbols,name=listing();out=[]
    for sym,v in symbols.items():
        assert sym.endswith('USDT') and '_' not in sym
        for m in v['klines_1d_months'] or []:
            if m in DEV_MONTHS:out.append((sym,'klines_1d',m))
        for m in v['funding_months'] or []:
            if m in DEV_MONTHS:out.append((sym,'fundingRate',m))
    return out,name

def one(item):
    sym,kind,month=item
    assert month<'2025-01','Validation/holdout acquisition blocked here'
    folder=ROOT/'data/raw/universe'/kind;folder.mkdir(parents=True,exist_ok=True)
    if kind=='klines_1d':
        name=f'{sym}-1d-{month}.zip';url=f'{BASE}/klines/{sym}/1d/{name}'
    else:
        name=f'{sym}-fundingRate-{month}.zip';url=f'{BASE}/fundingRate/{sym}/{name}'
    p=folder/name;cp=folder/(name+'.CHECKSUM')
    cached=p.exists() and cp.exists()
    try:
        body,checksum=(p.read_bytes(),cp.read_bytes()) if cached else (get(url),get(url+'.CHECKSUM'))
    except Exception as exc:
        return dict(url=url,retrieved=now(),error=f'{type(exc).__name__}: {exc}')
    digest=hashlib.sha256(body).hexdigest()
    if digest!=checksum.decode().split()[0]:
        return dict(url=url,retrieved=now(),error='checksum mismatch',sha256=digest)
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    return dict(url=url,retrieved=now(),file=str(p.relative_to(ROOT)).replace('\\','/'),sha256=digest,bytes=len(body),cached=cached)

def main():
    work,listing_name=items();stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    log_path=ROOT/'data/metadata'/f'universe_acquisition_{stamp}.jsonl'
    print('items',len(work),'listing',listing_name,flush=True);ok=err=0;t=time.time()
    with log_path.open('x',encoding='utf8') as log:
        log.write(json.dumps(dict(listing=listing_name,items=len(work),started=now(),months=DEV_MONTHS[0]+'..'+DEV_MONTHS[-1]))+'\n')
        with ThreadPoolExecutor(max_workers=8) as pool:
            for i,r in enumerate(pool.map(one,work)):
                log.write(json.dumps(r)+'\n')
                if 'error' in r:
                    err+=1
                    if 'Rate limited' in r['error']:
                        log.write(json.dumps(dict(abort='rate limited',at=i,retrieved=now()))+'\n');print('ABORT rate limited',flush=True);sys.exit(2)
                else:ok+=1
                if i%500==0:log.flush();print(i,'ok',ok,'err',err,'elapsed',round(time.time()-t),flush=True)
        log.write(json.dumps(dict(finished=now(),ok=ok,errors=err))+'\n')
    print('DONE ok',ok,'errors',err,'log',log_path.name,flush=True)

if __name__=='__main__':main()
