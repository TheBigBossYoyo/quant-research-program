"""Bounded parallel public archive GETs for carry feasibility, development only."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib,json
from acquire import get,now,ROOT

def one(item):
    sym,kind,year,month=item
    assert 2022<=year<=2024
    folder=ROOT/'data/raw/futures'/kind;folder.mkdir(parents=True,exist_ok=True)
    name=f'{sym}-1h-{year}-{month:02}.zip'
    p=folder/name; cp=folder/(name+'.CHECKSUM')
    url=f'https://data.binance.vision/data/futures/um/monthly/{kind}/{sym}/1h/{name}'
    cached=p.exists() and cp.exists()
    body,checksum=(p.read_bytes(),cp.read_bytes()) if cached else (get(url),get(url+'.CHECKSUM'))
    digest=hashlib.sha256(body).hexdigest();assert digest==checksum.decode().split()[0]
    if not cached:p.write_bytes(body);cp.write_bytes(checksum)
    return dict(url=url,retrieved=now(),file=str(p.relative_to(ROOT)),sha256=digest,bytes=len(body),cached=cached)

def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    items=[(s,k,y,m) for s in ['BTCUSDT','ETHUSDT'] for k in ['klines','markPriceKlines'] for y in range(2022,2025) for m in range(1,13)]
    with (ROOT/'data/metadata'/f'carry_prices_{stamp}.jsonl').open('x') as log:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(one,items):
                log.write(json.dumps(result)+'\n');log.flush()
                print(result['file'],'verified',flush=True)

if __name__=='__main__':main()
