import sys,unittest,tempfile,hashlib
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
import zipfile,io
from universe import features,eligibility,forward_open_return,quintile_weights,daily_funding,load_klines,MIN_HISTORY_BARS,MIN_MEDIAN_QUOTE_VOLUME
from cross_sectional_screen import xs_ledger

def panel(n,syms,price=100.,qv=None):
    days=pd.date_range('2022-01-01',periods=n,freq='D',tz='UTC')
    p=pd.DataFrame(price,index=days,columns=syms)
    return dict(open=p.copy(),close=p.copy(),quote_volume=pd.DataFrame(qv if qv is not None else 1e8,index=days,columns=syms),
                volume=pd.DataFrame(1.,index=days,columns=syms),taker_buy_volume=pd.DataFrame(.5,index=days,columns=syms))

class UniverseTests(unittest.TestCase):
    def test_eligibility_point_in_time(self):
        p=panel(80,['A','B']);p['close'].iloc[:5,1]=np.nan;p['open'].iloc[:5,1]=np.nan;p['quote_volume'].iloc[:,1]=1e6
        e=eligibility(p)
        self.assertFalse(e.iloc[MIN_HISTORY_BARS-2,0]);self.assertTrue(e.iloc[MIN_HISTORY_BARS-1,0]);self.assertFalse(e.iloc[:,1].any())
        p['close'].iloc[70,0]=np.nan;self.assertFalse(eligibility(p).iloc[70,0]);self.assertTrue(eligibility(p).iloc[71,0])
    def test_forward_open_return_delisting_exit(self):
        days=pd.date_range('2022-01-01',periods=12,freq='D',tz='UTC')
        o=pd.DataFrame(dict(A=np.arange(100.,112.),B=np.r_[np.arange(100.,106.),[np.nan]*6]),index=days)
        r=forward_open_return(o,2,9)
        self.assertAlmostEqual(r.iloc[0,0],109/102-1)
        self.assertAlmostEqual(r.iloc[0,1],105/102-1)   # B delisted after day 5: last observed open
        self.assertTrue(np.isnan(r.iloc[4,1]))          # entry day 6 missing for B
    def test_quintile_weights_neutral(self):
        s=pd.Series(np.arange(20.),index=[f'S{i}' for i in range(20)]);e=pd.Series(True,index=s.index)
        w=quintile_weights(s,e,1)
        self.assertAlmostEqual(w.sum(),0.);self.assertAlmostEqual(w.abs().sum(),1.);self.assertEqual(len(w),8)
        self.assertEqual(w['S19'],.125);self.assertEqual(w['S0'],-.125);self.assertEqual(quintile_weights(s,e,-1)['S19'],-.125)
        e.iloc[:15]=False;self.assertEqual(len(quintile_weights(s,e,1)),0)
    def test_daily_funding_day_bucket(self):
        f=pd.DataFrame(dict(symbol=['A','A','A'],time=pd.to_datetime(['2022-01-02 00:00','2022-01-02 16:00','2022-01-02 23:59'],utc=True),rate=[.01,.02,.03],interval_hours=8))
        days=pd.date_range('2022-01-01',periods=3,freq='D',tz='UTC');g=daily_funding(f,days,['A','B'])
        self.assertAlmostEqual(g.loc['2022-01-02','A'],.06);self.assertEqual(g.loc['2022-01-01','A'],0.);self.assertEqual(g['B'].sum(),0.)
    def test_ledger_known_pnl_funding_and_delisting(self):
        days=pd.date_range('2022-01-01',periods=8,freq='D',tz='UTC')
        o=pd.DataFrame(dict(A=[100,100,100,110,110,110,110,110],B=[100,100,100,90,90,np.nan,np.nan,np.nan]),index=days,dtype=float)
        fund=pd.DataFrame(0.,index=days,columns=['A','B']);fund.loc[days[3],'A']=.01
        w={days[0]:pd.Series(dict(A=.5,B=-.5))}
        path=xs_ledger(o,fund,w,cost=0.)
        # execute at open day2: 50 units A long, -50 units B short; day2->day3: A +10 each, B -10 each => +1000 on 10000
        self.assertAlmostEqual(path.nav.iloc[3],11000.)
        # funding on day3 charged at open day4: 50*0.01*110=55 debit for the long
        self.assertAlmostEqual(path.nav.iloc[4],11000-55.)
        # B delisted (missing open day5): exit at last open 90, no further PnL; A flat
        self.assertAlmostEqual(path.nav.iloc[-1],11000-55.);self.assertEqual(path.names.iloc[5],1)
        costly=xs_ledger(o,fund,w,cost=.001);self.assertAlmostEqual(costly.nav.iloc[2],10000-10.)
    def test_ledger_no_future_dependence(self):
        rng=np.random.default_rng(0);days=pd.date_range('2022-01-01',periods=40,freq='D',tz='UTC')
        o=pd.DataFrame(100*np.cumprod(1+rng.normal(0,.02,(40,3)),axis=0),index=days,columns=['A','B','C'])
        fund=pd.DataFrame(0.,index=days,columns=o.columns);w={days[0]:pd.Series(dict(A=.5,B=-.5)),days[7]:pd.Series(dict(B=.5,C=-.5))}
        a=xs_ledger(o,fund,w,.001);o2=o.copy();o2.iloc[20:]*=3;b=xs_ledger(o2,fund,w,.001)
        pd.testing.assert_series_equal(a.nav.iloc[:20],b.nav.iloc[:20])
    def test_taker_above_volume_is_quarantined_not_dropped(self):
        header='open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore'
        r1='1641081600000,10,11,9,10,100,1641167999999,1000,5,150,1500,0';r2='1641168000000,10,11,9,10,100,1641254399999,1000,5,50,500,0'
        rows=chr(10).join([header,r1,r2])+chr(10)
        with tempfile.TemporaryDirectory() as d:
            buf=io.BytesIO()
            with zipfile.ZipFile(buf,'w') as z:z.writestr('XUSDT-1d-2022-01.csv',rows)
            body=buf.getvalue();p=Path(d)/'XUSDT-1d-2022-01.zip';p.write_bytes(body)
            (Path(d)/'XUSDT-1d-2022-01.zip.CHECKSUM').write_text(hashlib.sha256(body).hexdigest()+'  XUSDT-1d-2022-01.zip')
            panels,info=load_klines(Path(d))
        self.assertEqual(len(info['taker_volume_quarantined']),1);self.assertEqual(info['rows'],2)
        self.assertTrue(np.isnan(panels['taker_buy_volume'].loc['2022-01-02','XUSDT']));self.assertEqual(panels['volume'].loc['2022-01-02','XUSDT'],100.)
        self.assertEqual(panels['taker_buy_volume'].loc['2022-01-03','XUSDT'],50.)
    def test_risk_features_causal_and_complete_windows(self):
        rng=np.random.default_rng(4);p=panel(200,['A','B'])
        p['close']=pd.DataFrame(100*np.cumprod(1+rng.normal(0,.02,(200,2)),axis=0),index=p['close'].index,columns=['A','B'])
        p['quote_volume']=pd.DataFrame(rng.uniform(1e7,3e7,(200,2)),index=p['close'].index,columns=['A','B'])
        fund=pd.DataFrame(0.,index=p['close'].index,columns=['A','B'])
        f=features(p,fund)
        self.assertTrue(f['vol30'].iloc[:30].isna().all().all());self.assertFalse(f['vol30'].iloc[30:].isna().any().any())
        self.assertTrue(f['abnvol7'].iloc[:89].isna().all().all());self.assertFalse(f['abnvol7'].iloc[89:].isna().any().any())
        self.assertTrue(f['amihud30'].iloc[:30].isna().all().all())
        q=p.copy();q['close']=p['close'].copy();q['close'].iloc[150:]*=5;q['quote_volume']=p['quote_volume'].copy();q['quote_volume'].iloc[150:]*=9
        g=features(q,fund)
        for k in ['vol30','abnvol7','amihud30']:pd.testing.assert_frame_equal(f[k].iloc[:150],g[k].iloc[:150])
    def test_loader_refuses_validation_files(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'XUSDT-1d-2025-01.zip';p.write_bytes(b'x');(Path(d)/'XUSDT-1d-2025-01.zip.CHECKSUM').write_text(hashlib.sha256(b'x').hexdigest()+'  XUSDT-1d-2025-01.zip')
            with self.assertRaises(AssertionError):load_klines(Path(d))

if __name__=='__main__':unittest.main()
