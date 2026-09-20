"""Supplement documented archive gaps using public REST; never edit raw archives."""
import json,hashlib,zipfile
from datetime import datetime,timezone
import pandas as pd
from acquire import ROOT,get,now
from carry_backtest import parse_price_csv

def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    folder=ROOT/'data/raw/futures/mark_supplements';folder.mkdir(parents=True,exist_ok=True)
    with (ROOT/'data/metadata'/f'mark_repairs_{stamp}.jsonl').open('x') as log:
        for sym in ['BTCUSDT','ETHUSDT']:
            frames=[]
            for p in sorted((ROOT/'data/raw/futures/markPriceKlines').glob(f'{sym}*.zip')):
                with zipfile.ZipFile(p) as z:
                    with z.open(z.namelist()[0]) as f:frames.append(parse_price_csv(f))
            dates=pd.to_datetime(pd.concat(frames).open_time,unit='ms',utc=True)
            expected=pd.date_range('2022-01-01','2025-01-01',freq='h',inclusive='left',tz='UTC')
            missing=expected.difference(dates)
            for day in missing.normalize().unique():
                start=int(day.timestamp()*1000);end=start+86400000-1
                assert day.year in [2022,2023,2024]
                url=f'https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={sym}&interval=1h&startTime={start}&endTime={end}&limit=24'
                body=get(url);rows=json.loads(body)
                assert isinstance(rows,list) and all(start<=r[0]<=end for r in rows)
                name=f'{sym}_{day.strftime("%Y-%m-%d")}_{stamp}.json';(folder/name).write_bytes(body)
                log.write(json.dumps(dict(url=url,retrieved=now(),file=name,sha256=hashlib.sha256(body).hexdigest(),rows=len(rows)))+'\n');log.flush()
                print(sym,str(day),len(rows),'REST rows',flush=True)

if __name__=='__main__':main()
