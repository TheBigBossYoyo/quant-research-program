"""GET-only historical funding diagnostic, strictly before validation/holdout."""
import json
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import time
from acquire import get,now,ROOT

def main():
    out=ROOT/'data/raw/funding';out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    meta=ROOT/'data/metadata'
    with (meta/f'funding_acquisition_{stamp}.jsonl').open('x') as log:
        for route in ['exchangeInfo','premiumIndex']:
            url=f'https://fapi.binance.com/fapi/v1/{route}'
            body=get(url);p=meta/f'futures_{route}_{stamp}.json';p.write_bytes(body)
            log.write(json.dumps(dict(url=url,retrieved=now(),file=p.name,sha256=hashlib.sha256(body).hexdigest()))+'\n');log.flush()
        for sym in ['BTCUSDT','ETHUSDT']:
            start=int(datetime(2022,1,1,tzinfo=timezone.utc).timestamp()*1000)
            end=int(datetime(2025,1,1,tzinfo=timezone.utc).timestamp()*1000)-1
            all_rows=[]
            while start<end:
                url=f'https://fapi.binance.com/fapi/v1/fundingRate?symbol={sym}&startTime={start}&endTime={end}&limit=1000'
                body=get(url);rows=json.loads(body)
                if not rows:break
                assert all(start<=r['fundingTime']<=end and r['symbol']==sym for r in rows)
                assert rows[-1]['fundingTime']>=start
                name=f'{sym}_{start}_{stamp}.json';(out/name).write_bytes(body)
                log.write(json.dumps(dict(url=url,retrieved=now(),file=name,sha256=hashlib.sha256(body).hexdigest(),rows=len(rows)))+'\n');log.flush()
                all_rows.extend(rows);start=rows[-1]['fundingTime']+1
                time.sleep(.2)
            p=out/f'{sym}_2022_2024_{stamp}_combined.json'
            p.write_text(json.dumps(all_rows,indent=2))
            print(sym,len(all_rows),p.name,flush=True)

if __name__=='__main__':main()
