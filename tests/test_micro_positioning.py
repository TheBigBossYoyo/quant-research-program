import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_positioning import positioning_features

class PositioningTests(unittest.TestCase):
    def test_rows_at_or_before_t_and_prefix_invariance(self):
        day=pd.Timestamp('2024-03-01');ts=pd.to_datetime([day+pd.Timedelta(seconds=300*i) for i in range(288)])
        rng=np.random.default_rng(0);m=pd.DataFrame(dict(sum_toptrader_long_short_ratio=1+rng.uniform(0,1,288),count_long_short_ratio=1+rng.uniform(0,1,288),sum_taker_long_short_vol_ratio=1+rng.uniform(0,1,288)),index=ts)
        f=positioning_features(m,day);t=1500  # rows at 0..1500 available (6 rows); top shift uses row 1500 vs row 600
        self.assertAlmostEqual(f.top_pos_shift.loc[t],m.sum_toptrader_long_short_ratio.iloc[5]/m.sum_toptrader_long_short_ratio.iloc[2]-1)
        self.assertAlmostEqual(f.taker_ratio.loc[t],m.sum_taker_long_short_vol_ratio.iloc[3:6].mean())
        self.assertTrue(np.isnan(f.top_pos_shift.loc[600]))  # needs a row 15 minutes earlier
        t2=1499;self.assertAlmostEqual(f.top_pos_shift.loc[1440],m.sum_toptrader_long_short_ratio.iloc[4]/m.sum_toptrader_long_short_ratio.iloc[1]-1)  # row at 1500 not yet available at 1440
        m2=m.copy();m2.iloc[10:,:]*=5;g=positioning_features(m2,day)
        for c in ['top_pos_shift','retail_crowd','taker_ratio']:pd.testing.assert_series_equal(f[c].loc[:2999],g[c].loc[:2999])
        self.assertTrue(np.isnan(f.retail_crowd.loc[t]))  # 24h mean needs 96 rows

if __name__=='__main__':unittest.main()
