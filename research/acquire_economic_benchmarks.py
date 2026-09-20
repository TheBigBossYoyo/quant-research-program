"""Public FRED historical references, exclusively pre-validation dates."""
from datetime import datetime,timezone
import hashlib,json,io,sys
import pandas as pd
from acquire import ROOT,get,now

def main():
    folder=ROOT/'data/raw/economic_references';folder.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    start=sys.argv[1] if len(sys.argv)>1 else '2021-12-01'  # E016: 2019-12-01 warmup for the 2020-2024 development sample
    with (ROOT/'data/metadata'/f'economic_references_{stamp}.jsonl').open('x') as log:
        for series in ['DEXUSUK','DGS3MO']:
            url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}&coed=2024-12-31'
            body=get(url);d=pd.read_csv(io.BytesIO(body))
            dates=pd.to_datetime(d.iloc[:,0]);assert dates.max()<pd.Timestamp('2025-01-01')
            assert dates.is_unique and dates.is_monotonic_increasing
            p=folder/f'{series}_{stamp}.csv';p.write_bytes(body)
            record=dict(url=url,retrieved_utc=now(),series=series,file=str(p.relative_to(ROOT)),sha256=hashlib.sha256(body).hexdigest(),rows=len(d),first=str(dates.min()),last=str(dates.max()))
            log.write(json.dumps(record)+'\n');log.flush();print(record,flush=True)

if __name__=='__main__':main()
