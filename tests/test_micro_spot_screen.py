import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from micro_spot_screen import spot_perp_features

def venue(seed,n=86400):
    rng=np.random.default_rng(seed);price=100+np.cumsum(rng.normal(0,.01,n))
    return pd.DataFrame(dict(second=np.arange(n),trades=1,buy_qty=rng.uniform(0,2,n),sell_qty=rng.uniform(0,2,n),first_price=price,last_price=price))

class SpotPerpTests(unittest.TestCase):
    def test_features_causal_and_basis_uses_last_completed_second(self):
        perp=venue(1);spot=venue(2);f=spot_perp_features(perp,spot);t=f.index[200]
        basis=(perp.last_price-spot.last_price)/spot.last_price
        expected=basis.iloc[t-1]-basis.iloc[t-3600:t].mean();self.assertAlmostEqual(f.basis_dev.loc[t],expected)
        sflow=(spot.buy_qty-spot.sell_qty).iloc[t-60:t].sum();sabs=np.abs(spot.buy_qty-spot.sell_qty).iloc[t-3600:t].mean()*60
        self.assertAlmostEqual(f.spot_flow.loc[t],sflow/sabs)
        p2=perp.copy();p2.iloc[t:,2:]=999.;s2=spot.copy();s2.iloc[t:,2:]=999.;g=spot_perp_features(p2,s2)
        for c in ['basis_dev','spot_flow','flow_div']:self.assertAlmostEqual(g[c].loc[t],f[c].loc[t])
        self.assertTrue(np.isnan(f.basis_dev.iloc[0]))  # warm-up: fewer than 600 seconds of history

if __name__=='__main__':unittest.main()
