import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_stack import ridge_fit,logistic_fit,stacked_positions

class StackTests(unittest.TestCase):
    def test_fits_recover_sign_and_positions_use_prior_years_only(self):
        rng=np.random.default_rng(0);n=6000;idx=pd.date_range('2020-01-01',periods=n,freq='4h');X=pd.DataFrame(rng.normal(size=(n,3)),index=idx,columns=list('abc'))
        y=pd.Series(.5*X.a.to_numpy()+rng.normal(0,.5,n),index=idx)
        w=ridge_fit(X.to_numpy(),y.to_numpy(),10.);self.assertGreater(w[1],.3);self.assertLess(abs(w[2]),.1)
        wl=logistic_fit(X.to_numpy(),y.to_numpy(),10.);self.assertGreater(wl[1],0)
        pos=stacked_positions(X,y,'ridge');self.assertTrue((pos[pos.index.year<2022]==0).all());self.assertGreater((pos[pos.index.year>=2022]!=0).mean(),.5)
        y2=y.copy();y2[y2.index.year>=2023]*=-1;pos2=stacked_positions(X,y2,'ridge');pd.testing.assert_series_equal(pos[pos.index.year==2022],pos2[pos2.index.year==2022])  # 2022 positions unaffected by later years

if __name__=='__main__':unittest.main()
