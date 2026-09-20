import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from ta_stats import block_bootstrap_sharpe,deflated_sharpe,benjamini_hochberg,pbo_cscv,walk_forward

class StatsTests(unittest.TestCase):
    def test_bootstrap_and_dsr_directions(self):
        rng=np.random.default_rng(0);good=rng.normal(.002,.01,800);noise=rng.normal(0,.01,800)
        g=block_bootstrap_sharpe(good,seed=1);n=block_bootstrap_sharpe(noise,seed=1)
        self.assertGreater(g['ci95'][0],0);self.assertLess(g['p_value_one_sided'],.01);self.assertGreater(n['p_value_one_sided'],.05)
        self.assertGreater(deflated_sharpe(g['sharpe'],800,10,good)['dsr'],deflated_sharpe(g['sharpe'],800,1000,good)['dsr'])
        self.assertLess(deflated_sharpe(n['sharpe'],800,50,noise)['dsr'],.5)
    def test_bh_and_pbo(self):
        self.assertEqual(benjamini_hochberg([.001,.02,.5,.9],q=.1).tolist(),[True,True,False,False])
        rng=np.random.default_rng(2);M=rng.normal(0,.01,(400,8));M[:,3]+=.004  # one genuinely better config
        self.assertLess(pbo_cscv(M,S=8)['pbo'],.5);self.assertGreater(pbo_cscv(rng.normal(0,.01,(400,8)),S=8)['pbo'],.3)
    def test_walk_forward_selects_in_sample_only(self):
        idx=pd.date_range('2019-01-01','2022-12-31',freq='D');rng=np.random.default_rng(3)
        a=pd.Series(rng.normal(.001,.01,len(idx)),index=idx);b=pd.Series(rng.normal(-.001,.01,len(idx)),index=idx)
        b[b.index.year==2022]+=.01  # b only good in the last year: must not be selected for 2022 using in-sample years
        wf=walk_forward({'a':a,'b':b},idx,[2019,2020,2021,2022]);self.assertEqual([w['selected'] for w in wf],['a','a','a'])

if __name__=='__main__':unittest.main()
