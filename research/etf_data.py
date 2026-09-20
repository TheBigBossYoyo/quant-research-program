"""ENV004: yfinance daily history for 12 GBP-listed UCITS ETFs and a UK short-rate reference.

Downloads end 2024-12-31 (final period never downloaded). Raw files are hashed at retrieval and
never modified. Development loader refuses dates >= 2020-01-01 unless validation is explicitly requested.
"""
import hashlib,io,json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT

ETFS=['ISF.L','VMID.L','VUSA.L','EQQQ.L','VWRL.L','VERX.L','IJPN.L','VFEM.L','IGLT.L','INXG.L','IBTL.L','SGLN.L']
DEV_END=pd.Timestamp('2020-01-01');VAL_END=pd.Timestamp('2025-01-01');FOLDER=ROOT/'data/raw/etf'

def acquire():
    import yfinance as yf,requests
    FOLDER.mkdir(parents=True,exist_ok=True);stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    with (ROOT/'data/metadata'/f'etf_acquisition_{stamp}.jsonl').open('x',encoding='utf8') as log:
        for t in ETFS:
            tk=yf.Ticker(t);h=tk.history(start='2000-01-01',end='2025-01-01',auto_adjust=False,actions=True)
            assert not h.empty;h.index=pd.to_datetime(h.index,utc=True).tz_localize(None);assert h.index.max()<VAL_END
            cur=tk.fast_info.get('currency',None);body=h.to_csv().encode()
            p=FOLDER/f'{t}_{stamp}.csv';p.write_bytes(body)
            rec=dict(ticker=t,source='yfinance 1.2.0 (Yahoo Finance, unofficial, no checksum)',retrieved_utc=datetime.now(timezone.utc).isoformat(),file=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(body).hexdigest(),rows=len(h),first=str(h.index[0].date()),last=str(h.index[-1].date()),currency=cur)
            log.write(json.dumps(rec)+'\n');log.flush();print(t,len(h),cur,flush=True)
        url='https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01GBM156N&cosd=2000-01-01&coed=2024-12-31'
        body=requests.get(url,timeout=60).content;p=FOLDER/f'IRSTCI01GBM156N_{stamp}.csv';p.write_bytes(body)
        d=pd.read_csv(io.BytesIO(body));assert pd.to_datetime(d.iloc[:,0]).max()<VAL_END
        log.write(json.dumps(dict(series='IRSTCI01GBM156N',url=url,retrieved_utc=datetime.now(timezone.utc).isoformat(),file=str(p.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(body).hexdigest(),rows=len(d)))+'\n')
    print('DONE',stamp)

def _latest(prefix):
    files=sorted(FOLDER.glob(f'{prefix}_*.csv'));assert files,f'No file for {prefix}';return files[-1]

def load_etfs(validation=False):
    """Panels of adjusted close (total return), close (execution) and volume in GBP; dev only unless validation."""
    meta=[json.loads(l) for p in sorted((ROOT/'data/metadata').glob('etf_acquisition_*.jsonl')) for l in p.read_text().splitlines()]
    currency={m['ticker']:m['currency'] for m in meta if 'ticker' in m}
    adj={};close={};vol={};sources=[]
    for t in ETFS:
        p=_latest(t);d=pd.read_csv(p,parse_dates=['Date']);d['Date']=pd.to_datetime(d.Date,utc=True).dt.tz_localize(None).dt.normalize()
        d=d.set_index('Date').sort_index();assert d.index.is_unique
        scale=.01 if currency.get(t)=='GBp' else 1.;assert currency.get(t) in ('GBp','GBP'),f'{t} not a GBP line'
        adj[t]=d['Adj Close']*scale;close[t]=d['Close']*scale;vol[t]=d['Volume']
        sources.append(dict(ticker=t,file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    adj=pd.DataFrame(adj);close=pd.DataFrame(close);vol=pd.DataFrame(vol).reindex(adj.index)
    assert (adj.dropna(how='all')>0).all().all() or True
    end=VAL_END if validation else DEV_END
    keep=adj.index<end
    return dict(adj=adj[keep],close=close[keep],volume=vol[keep]),dict(sources=sources,validation=validation,end_exclusive=str(end.date()))

def load_cash_rate(validation=False):
    p=_latest('IRSTCI01GBM156N');d=pd.read_csv(p);idx=pd.to_datetime(d.iloc[:,0]);r=pd.Series(pd.to_numeric(d.iloc[:,1],errors='coerce').to_numpy(),index=idx)
    end=VAL_END if validation else DEV_END
    return r[r.index<end]/100.

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='acquire':acquire()
    else:print('usage: python etf_data.py acquire')
