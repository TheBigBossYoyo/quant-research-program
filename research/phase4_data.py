"""Phase4 preregistration and bounded official-archive acquisition. No strategy returns."""
import io,json,hashlib,zipfile,time,sys
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np,pandas as pd,requests
from core import ROOT,COLS
from phase4_engine import guard_dates,guard_path,verified_bytes
from universe import _csv,KLINE_COLS,FUNDING_COLS

def freeze_check():
    c=json.loads((ROOT/'phase4_e040_frozen_config.yaml').read_text());h=json.loads((ROOT/'PHASE4_FREEZE_HASHES.json').read_text())
    for p,v in c['source_hashes'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=v:raise RuntimeError('Frozen source changed: '+p)
    for p,v in [('phase4_e040_frozen_config.yaml',h['config_sha256']),('PHASE4_E040_FROZEN_SPEC.md',h['FROZEN_E040_HASH'])]:
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=v:raise RuntimeError('Freeze changed: '+p)
    return c

def select():
    freeze_check();frames=[];sources=[]
    folder=ROOT/'data/raw/universe/klines_1d'
    for y in [2020,2021]:
        for p in sorted(folder.glob(f'*-1d-{y}-*.zip')):
            raw,sha=verified_bytes(p);d=_csv(raw,KLINE_COLS);d['symbol']=p.name.split('-1d-')[0]
            d['time']=pd.to_datetime(d.open_time,unit='ms',utc=True)
            if d.time.max()>=pd.Timestamp('2022-01-01',tz='UTC'):raise ValueError('Universe asof leak')
            frames.append(d);sources.append(dict(file=str(p.relative_to(ROOT)),sha256=sha))
    d=pd.concat(frames);rows=[]
    for sym,g in d.groupby('symbol'):
        g=g.sort_values('time');start=g.time.min();end=g.time.max();w=g[g.time>=pd.Timestamp('2021-07-01',tz='UTC')]
        age=(pd.Timestamp('2021-12-31',tz='UTC')-start).days+1;n=int((g.time.dt.year==2021).sum());liq=float(w.quote_volume.median()) if len(w) else 0.
        quality=not g.time.duplicated().any() and (g[['open','high','low','close']]>0).all().all()
        reasons=[]
        if sym in ['BTCUSDT','ETHUSDT']:reasons.append('discovery asset')
        if age<365 or n<360:reasons.append('insufficient asof history')
        if end<pd.Timestamp('2021-12-31',tz='UTC'):reasons.append('not active at selection')
        if len(w)<180 or liq<20e6:reasons.append('below liquidity/history threshold')
        if not quality:reasons.append('daily quality defect')
        rows.append(dict(asset=sym,start=str(start),end=str(end),history_days=age,valid_days_2021=n,median_quote_volume=liq,data_quality='pass' if quality else 'fail',preeligible=not reasons,reason='; '.join(reasons)))
    r=pd.DataFrame(rows).sort_values(['median_quote_volume','asset'],ascending=[False,True]);chosen=r[r.preeligible].head(12).asset.tolist();r['eligible']=r.asset.isin(chosen)
    r.loc[r.preeligible&~r.eligible,'reason']='outside preregistered top12 liquidity rank'
    r.loc[r.eligible,'reason']='selected by historical liquidity; later losses/delistings retained'
    out=ROOT/'reports/E043_universe';out.mkdir(exist_ok=False);r.to_csv(out/'eligibility.csv',index=False)
    spec=dict(selection_date='2021-12-31',assets=chosen,rule_config_sha256=json.loads((ROOT/'PHASE4_FREEZE_HASHES.json').read_text())['config_sha256'],sources=sources,created_utc=datetime.now(timezone.utc).isoformat(),strategy_performance_evaluated=False)
    p=ROOT/'PHASE4_UNIVERSE.json';p.write_text(json.dumps(spec,indent=2));sha=hashlib.sha256(p.read_bytes()).hexdigest();(ROOT/'PHASE4_UNIVERSE.sha256').write_text(sha+'\n')
    md='# Phase4 historical universe preregistration\n\nUniverse SHA256: '+sha+'\n\nAll eligibility is measured as of2021-12-31. The full candidate table is reports/E043_universe/eligibility.csv. Historical archive presence includes subsequently delisted contracts. No E040 returns on these assets have been computed. Spread/lot constraints are not inferred from candle volume; unavailable observations remain unverified operational limitations. Later delistings remain in all portfolio denominators, with no replacement.\n\n|Asset|Start date|End date at selection|History days|Median daily quote volume USDT|Data quality|Eligible|Reason|\n|---|---|---|---:|---:|---|---|---|\n'
    for x in r.to_dict('records'):md+='|'+ '|'.join(str(x[k]) for k in ['asset','start','end','history_days','median_quote_volume','data_quality','eligible','reason'])+'|\n'
    (ROOT/'PHASE4_UNIVERSE_PREREGISTRATION.md').write_text(md)
    print('UNIVERSE',chosen,'HASH',sha,flush=True)

def universe():
    p=ROOT/'PHASE4_UNIVERSE.json'
    if hashlib.sha256(p.read_bytes()).hexdigest()!=(ROOT/'PHASE4_UNIVERSE.sha256').read_text().strip():raise RuntimeError('Universe changed')
    return json.loads(p.read_text())['assets']

def get(url):
    for attempt in range(3):
        try:
            r=requests.get(url,timeout=(15,40))
            if r.status_code==404:return None
            if r.status_code in (418,429):raise RuntimeError('Rate limited; stop acquisition')
            r.raise_for_status();return r.content
        except (requests.Timeout,requests.ConnectionError):
            if attempt==2:raise
            time.sleep(1+attempt)

def one(job):
    sym,month,kind=job;guard_dates(month+'-01',pd.Timestamp(month+'-01')+pd.offsets.MonthBegin(1))
    if kind=='klines':folder=ROOT/'data/raw/phase4/klines';name=f'{sym}-1h-{month}.zip';url=f'https://data.binance.vision/data/futures/um/monthly/klines/{sym}/1h/{name}'
    else:folder=ROOT/'data/raw/phase4/markPriceKlines';name=f'{sym}-1h-{month}.zip';url=f'https://data.binance.vision/data/futures/um/monthly/markPriceKlines/{sym}/1h/{name}'
    p=folder/name;cp=p.with_name(p.name+'.CHECKSUM');folder.mkdir(parents=True,exist_ok=True)
    legacy=ROOT/'data/raw/futures'/kind/name
    if legacy.exists():p=legacy;cp=p.with_name(p.name+'.CHECKSUM')
    meta=dict(symbol=sym,month=month,kind=kind,url=url,retrieved_utc=datetime.now(timezone.utc).isoformat())
    if p.exists() and cp.exists():raw,sha=verified_bytes(p);meta.update(cached=True,sha256=sha,file=str(p.relative_to(ROOT)),bytes=len(raw));return meta
    raw=get(url)
    if raw is None:return dict(**meta,missing=True)
    check=get(url+'.CHECKSUM')
    if check is None:raise ValueError('Missing checksum '+url)
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=check.decode().split()[0]:raise ValueError('Checksum '+url)
    p.write_bytes(raw);cp.write_bytes(check)
    return dict(**meta,cached=False,sha256=sha,file=str(p.relative_to(ROOT)),bytes=len(raw))

def acquire():
    freeze_check();assets=universe();elig=pd.read_csv(ROOT/'reports/E043_universe/eligibility.csv').set_index('asset')
    jobs=[]
    for sym in assets+['BTCUSDT','ETHUSDT']:
        start=pd.Timestamp(elig.loc[sym,'start']).strftime('%Y-%m')
        for month in pd.period_range(start,'2024-12',freq='M').astype(str):
            jobs.append((sym,month,'klines'))
            if month>='2021-12':jobs.append((sym,month,'markPriceKlines'))
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');p=ROOT/'data/metadata'/f'phase4_acquisition_{stamp}.jsonl'
    with p.open('x') as log:
        with ThreadPoolExecutor(6) as pool:
            for n,res in enumerate(pool.map(one,jobs),1):
                log.write(json.dumps(res)+'\n');log.flush()
                if n%50==0:print('ARCHIVES',n,'/',len(jobs),flush=True)
    print('COMPLETE',p,flush=True)

if __name__=='__main__':
    {'select':select,'acquire':acquire}[sys.argv[1]]()
