import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from positioning_screen import funding_features,positioning_features
from flow_screen import resample_bars

def hourly(n,seed=0):
    rng=np.random.default_rng(seed)
    idx=pd.date_range('2022-01-01',periods=n,freq='h',tz='UTC')
    price=100*np.cumprod(1+rng.normal(0,.01,n))
    return pd.DataFrame(dict(open=price,close=price*(1+rng.normal(0,.001,n)),volume=1.,taker_base=.5),index=idx)

class PositioningTests(unittest.TestCase):
    def test_funding_known_only_at_or_after_settlement(self):
        idx=pd.date_range('2022-01-01',periods=24,freq='h',tz='UTC')
        rates=pd.Series([.01,.02,.03],index=pd.to_datetime(['2022-01-01 00:00','2022-01-01 08:00','2022-01-01 16:00'],utc=True))
        f8,f24=funding_features(rates,idx,1)
        self.assertEqual(f8.loc['2022-01-01 07:00'],.02)   # bar closes 08:00, settlement at 08:00 is known
        self.assertEqual(f8.loc['2022-01-01 06:00'],.01)   # bar closes 07:00, only 00:00 settlement known
        self.assertEqual(f8.loc['2022-01-01 15:00'],.03)
        self.assertTrue(np.isnan(f24.loc['2022-01-01 07:00']));self.assertAlmostEqual(f24.loc['2022-01-01 15:00'],.06)
    def test_eight_hour_bars_align_to_funding_boundaries(self):
        b=resample_bars(hourly(72),8)
        self.assertTrue(set(b.index.hour)<={0,8,16});self.assertEqual(len(b),9)
    def test_basis_and_zscore_causal(self):
        p=hourly(2000,1);s=hourly(2000,2)
        rates=pd.Series(.0001,index=pd.date_range('2022-01-01',periods=250,freq='8h',tz='UTC'))
        a=positioning_features(p,s,rates,8);q=p.copy();q.iloc[1600:,:]*=2;b=positioning_features(q,s,rates,8)
        cut=a.index[a.index<p.index[1600]]
        for col in ['fund8','fund24','basis','basis_z']:pd.testing.assert_series_equal(a.loc[cut,col],b.loc[cut,col])
        self.assertAlmostEqual(a.basis.iloc[5],resample_bars(p,8).close.iloc[5]/resample_bars(s,8).close.iloc[5]-1)
        self.assertTrue(a.basis_z.iloc[:59].isna().all());self.assertFalse(a.basis_z.iloc[90:].isna().any())

if __name__=='__main__':unittest.main()
