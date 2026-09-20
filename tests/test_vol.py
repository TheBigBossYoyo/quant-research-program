import sys,unittest,io,zipfile
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from vol_data import derive_minutes
from vol_screen import iv_shock_features,daily_features

class VolTests(unittest.TestCase):
    def test_minute_derivation_last_value(self):
        day=pd.Timestamp('2024-03-05');base=int(day.value//10**6);rows='calc_time,symbol,base_asset,quote_asset,index_value\n'+f'{base+1000},X,X,USDT,70.0\n{base+59000},X,X,USDT,71.0\n{base+120000},X,X,USDT,72.0\n'
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('x.csv',rows)
        m=derive_minutes(buf.getvalue(),day);self.assertEqual(m.bvol_close.iloc[0],71.);self.assertTrue(np.isnan(m.bvol_close.iloc[1]));self.assertEqual(m.bvol_close.iloc[2],72.);self.assertEqual(m.ticks.iloc[0],2)
    def test_iv_shock_uses_completed_minutes_only(self):
        day=pd.Timestamp('2024-03-05');idx=pd.date_range(day-pd.Timedelta(days=1),day+pd.Timedelta(days=1),freq='min',inclusive='left')
        rng=np.random.default_rng(0);bv=pd.Series(60+np.cumsum(rng.normal(0,.05,len(idx))),index=idx)
        z=iv_shock_features(bv,day);t=3600  # 01:00:00 -> last completed minute is 00:59
        m=pd.Timestamp('2024-03-05 00:59');ch=(bv-bv.shift(15));sd=ch.rolling(1440,min_periods=720).std();self.assertAlmostEqual(z.loc[t],(ch/sd).loc[m])
        bv2=bv.copy();bv2.loc[pd.Timestamp('2024-03-05 01:00'):]+=50;self.assertAlmostEqual(iv_shock_features(bv2,day).loc[t],z.loc[t])
    def test_daily_features_exclude_current_day(self):
        days=pd.date_range('2023-06-01',periods=200,freq='D');rng=np.random.default_rng(1);close=pd.Series(100*np.cumprod(1+rng.normal(0,.02,200)),index=days)
        idx=pd.date_range('2023-06-01',periods=200*1440,freq='min');bv=pd.Series(60.,index=idx)
        D=daily_features('X',bv,close);d=days[100]
        lr=np.log(close/close.shift(1));expected=lr.iloc[70:100].std()*np.sqrt(365)*100  # 30 closes before d, excluding d
        self.assertAlmostEqual(D.rv.loc[d],expected);self.assertAlmostEqual(D.vrp.loc[d],60-expected)

if __name__=='__main__':unittest.main()
