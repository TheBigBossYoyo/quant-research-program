import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'research'))
from phase4_engine import *
from ta_ensemble import fractional_ledger
from ta_engine import run_ledger

def sample(n=12):
    idx=pd.date_range('2024-01-01',periods=n,freq='h',tz='UTC')
    return pd.DataFrame({k:np.full(n,v) for k,v in dict(open=100.,high=101.,low=99.,close=100.,volume=10.,quote_volume=1000.,taker_base=5.,trades=10.).items()},index=idx)

class Phase4Tests(unittest.TestCase):
    def test_future_outage_does_not_cancel_earlier_open(self):
        h=sample();a=aggregate(h);h.iloc[6,:]=np.nan;b=aggregate(h)
        t=pd.Series(1.,index=a.index)
        pa,_=ledger(a,t,0.,'trend');pb,_=ledger(b,t,0.,'trend')
        self.assertEqual(pa.units.iloc[1],pb.units.iloc[1]);self.assertEqual(pb.units.iloc[1],100.)
    def test_funding_precedes_stop(self):
        b=aggregate(sample());b.loc[b.index[2],['low','observed_low']]=95.
        b[['high','observed_high']]=100.
        f=pd.Series([0.,0.,1.],index=b.index);t=pd.Series(1.,index=b.index);a=t.copy()
        p,tr=ledger(b,t,0.,'breakout',f,a)
        self.assertEqual(p.equity.iloc[-1],9600.);self.assertEqual(p.funding.sum(),100.)
        self.assertAlmostEqual(tr.pnl.sum(),-400.)
    def test_no_entry_funding_and_exit_funding(self):
        b=aggregate(sample(16));t=pd.Series([1.,0.,0.,0.],index=b.index)
        f=pd.Series([0.,1.,1.,0.],index=b.index)
        p,_=ledger(b,t,0.,'trend',f)
        self.assertEqual(p.funding.iloc[1],0.);self.assertEqual(p.funding.iloc[2],100.)
        self.assertEqual(p.equity.iloc[-1],9900.)
    def test_short_funding_credit(self):
        b=aggregate(sample());t=pd.Series(-1.,index=b.index);f=pd.Series([0.,0.,1.],index=b.index)
        p,_=ledger(b,t,0.,'trend',f);self.assertEqual(p.equity.iloc[-1],10100.)
    def test_costs_and_net_trade_reconcile(self):
        b=aggregate(sample(16));t=pd.Series([1.,0.,0.,0.],index=b.index)
        p,tr=ledger(b,t,.001,'trend');self.assertEqual(p.cost.sum(),20.)
        self.assertEqual(p.equity.iloc[-1],9980.);self.assertEqual(tr.pnl.sum(),-20.)
    def test_unchanged_trend_ledger_without_defects(self):
        b=aggregate(sample(24));t=pd.Series([.5,1.,-.5,0.,1.,1.],index=b.index)
        p,_=ledger(b,t,.000905,'trend');old=fractional_ledger(b,t,.000905)
        np.testing.assert_allclose(p.equity,old.equity,rtol=1e-12)
    def test_unchanged_breakout_without_funding(self):
        b=aggregate(sample(24));t=pd.Series([1.,1.,-1.,-1.,0.,0.],index=b.index);a=pd.Series(1.,index=b.index)
        p,_=ledger(b,t,.000905,'breakout',atr_series=a);old,_=run_ledger(b,t,.000905,stop_atr=3.,atr_series=a,trail=True)
        np.testing.assert_allclose(p.equity,old.equity,rtol=1e-12)
    def test_frozen_rules_have_no_asset_argument_and_prefix_invariance(self):
        b=aggregate(sample(1600));x=signals(b);changed=b.copy();changed.iloc[300:,changed.columns.get_loc('close')]*=2
        y=signals(changed)
        for k in x:pd.testing.assert_series_equal(x[k].iloc[:300],y[k].iloc[:300])
        import inspect
        self.assertEqual(list(inspect.signature(signals).parameters),['b'])
    def test_4h_alignment(self):
        b=aggregate(sample());self.assertTrue((b.index.hour%4==0).all());self.assertEqual(len(b),3)
        self.assertEqual(b.execution_open.iloc[1],100.)
    def test_weighting_is_causal(self):
        i=pd.date_range('2024-01-01',periods=100,tz='UTC');g=np.random.default_rng(1)
        a=pd.Series(g.normal(0,.01,100),index=i);b=pd.Series(g.normal(0,.02,100),index=i)
        r,w=combine(a,b,'inverse_vol');a2=a.copy();a2.iloc[80:]*=3
        _,w2=combine(a2,b,'inverse_vol');pd.testing.assert_series_equal(w.iloc[:81],w2.iloc[:81])
        eq,_=combine(a,b);np.testing.assert_allclose(eq,(a+b)/2)
    def test_2025_firewall(self):
        with self.assertRaises(ProtectedValidationError):guard_dates('2024-01-01','2025-01-02')
        with self.assertRaises(ProtectedValidationError):guard_path('SOLUSDT-1h-2025-01.zip')
    def test_2026_firewall(self):
        with self.assertRaises(FinalHoldoutProtectedError):guard_dates('2026-01-01','2026-02-01')
        with self.assertRaises(FinalHoldoutProtectedError):guard_path('SOLUSDT-1h-2026-01.zip')
    def test_protected_access_fails_before_open(self):
        with self.assertRaises(ProtectedValidationError):verified_bytes('nonexistent/SOLUSDT-1h-2025-01.zip')
    def test_insolvency_is_absorbing(self):
        b=aggregate(sample(16));b.loc[b.index[2],['close','valuation_close']]=220.
        p,_=ledger(b,pd.Series(-1.,index=b.index),0.,'trend');self.assertEqual(p.equity.iloc[-1],0.)
        self.assertTrue(p.ruin.iloc[-1]);self.assertEqual(p.units.iloc[-1],0.)

if __name__=='__main__':unittest.main()


class Phase4InferenceTests(unittest.TestCase):
    def test_frozen_files_and_universe_unchanged(self):
        from phase4_data import freeze_check,universe
        freeze_check();self.assertEqual(len(universe()),12)
    def test_first_day_return_and_absorbing_zero(self):
        from phase4_stats import returns
        p=pd.DataFrame({'equity':[9000.,0.,0.]},index=pd.date_range('2024-01-01',periods=3,tz='UTC'))
        np.testing.assert_allclose(returns(p),[-.1,-1.,0.])
    def test_factor_residual_mean_not_mislabelled_alpha(self):
        from phase4_stats import factor_fit
        i=pd.date_range('2024-01-01',periods=200,tz='UTC');g=np.random.default_rng(1)
        x=pd.DataFrame({'asset':g.normal(0,.01,200)},index=i);y=.001+.3*x.asset+g.normal(0,.002,200)
        m,adj=factor_fit(y,x);self.assertAlmostEqual(m['residual_sharpe'],0.,places=10)
        self.assertGreater(m['factor_adjusted_sharpe'],0.)
    def test_portfolio_weights_and_cluster_cap(self):
        from phase4_stats import allocation,cluster_caps
        i=pd.date_range('2024-01-01',periods=150,tz='UTC');z=np.random.default_rng(2).normal(0,.01,150)
        r=pd.DataFrame({'a':z,'b':z},index=i);w=allocation(r);wc,_=cluster_caps(r,w)
        self.assertAlmostEqual(wc.iloc[-1].sum(),.5)
        altered=r.copy();altered.iloc[140:]*=4;w2,_=cluster_caps(altered,allocation(altered))
        pd.testing.assert_frame_equal(wc.iloc[:141],w2.iloc[:141])
    def test_net_combo_trade_contributions_reconcile(self):
        from phase4_execute import combo_trades
        from phase4_stats import returns
        b=aggregate(sample(240));t=pd.Series(np.tile([1.,1.,-1.,0.,0.],12),index=b.index)
        p,tr=ledger(b,t,.001,'trend');paths={'trend':p,'breakout':p};trades={'trend':tr,'breakout':tr}
        r=returns(p);w=pd.Series(.5,index=r.index);ct=combo_trades(paths,trades,w,r)
        self.assertAlmostEqual(ct.pnl.sum(),p.equity.iloc[-1]-10000.,places=7)


class Phase4SupplementTests(unittest.TestCase):
    """Official daily archives may only fill documented gaps; they never override or conflict."""
    @staticmethod
    def frame(ix,price):
        from core import COLS
        d=pd.DataFrame({c:0. for c in COLS},index=ix);d['time']=ix.asi8//10**6;d['close_time']=d.time+3599999
        for c in ['open','high','low','close']:d[c]=price
        return d
    def test_supplement_fills_only_missing_hours(self):
        from phase4_run import merge_supplements
        idx=pd.date_range('2024-01-01',periods=48,freq='h',tz='UTC')
        monthly=self.frame(idx[:24].append(idx[36:]),100.);supp=self.frame(idx[24:36],200.)
        merged,added=merge_supplements(monthly,supp)
        self.assertEqual(len(merged),48);self.assertEqual(len(added),12);self.assertTrue(merged.index.is_monotonic_increasing)
        self.assertTrue((merged.loc[idx[:24],'open']==100.).all());self.assertTrue((merged.loc[idx[24:36],'open']==200.).all())
    def test_identical_overlap_ignored_and_conflict_fails(self):
        from phase4_run import merge_supplements
        idx=pd.date_range('2024-01-01',periods=48,freq='h',tz='UTC')
        monthly=self.frame(idx[:24].append(idx[36:]),100.)
        same=self.frame(idx[20:36],100.);same.loc[idx[24:36],['open','high','low','close']]=200.
        merged,added=merge_supplements(monthly,same);self.assertEqual(len(merged),48);self.assertEqual(len(added),12)
        conflict=self.frame(idx[20:36],200.)
        with self.assertRaises(ValueError):merge_supplements(monthly,conflict)
    def test_on_disk_supplements_close_documented_gaps(self):
        from phase4_run import read_hourly
        d,sources=read_hourly('SOLUSDT','klines');supp=[s for s in sources if s.get('role')=='daily_gap_supplement']
        self.assertEqual(len(supp),5);self.assertEqual(sum(len(s['hours_added']) for s in supp),120)
        for day in ['2022-02-26','2022-02-27','2022-02-28','2022-04-01','2022-04-02']:
            self.assertEqual(int((d.index.strftime('%Y-%m-%d')==day).sum()),24)
        grid=pd.date_range('2022-01-01','2024-12-31 23:00',freq='h',tz='UTC');self.assertEqual(len(grid.difference(d.index)),0)
        m,msources=read_hourly('SOLUSDT','markPriceKlines');self.assertFalse(any(s.get('role')=='daily_gap_supplement' for s in msources))


class Phase4HourlyEventTests(unittest.TestCase):
    def test_nonboundary_funding_and_4h_orders(self):
        b=sample(12);b['tradable']=True;b['orderable']=b.index.hour%4==0;b['complete']=b.index.hour%4==3
        t=pd.Series(1.,index=b.index);f=pd.Series(0.,index=b.index);f.iloc[6]=1.
        p,_=ledger(b,t,0.,'trend',f)
        self.assertTrue((p.units.iloc[:4]==0).all());self.assertEqual(p.units.iloc[4],100.)
        self.assertEqual(p.funding.iloc[6],100.);self.assertEqual(p.equity.iloc[-1],9900.)
        b.loc[b.index[4],'tradable']=False;p,_=ledger(b,t,0.,'trend')
        self.assertTrue((p.units.iloc[:8]==0).all());self.assertEqual(p.units.iloc[8],100.)
    def test_trailing_stop_ratchets_only_after_full4h_bar(self):
        b=sample(12);b['tradable']=True;b['orderable']=b.index.hour%4==0;b['complete']=b.index.hour%4==3
        b['trailing_high']=b.high;b['trailing_low']=b.low
        b.loc[b.index[5],['high','close']]=110.
        b.loc[b.index[7],'trailing_high']=110.
        b.loc[b.index[8],['open','high','low','close']]=106.
        p,tr=ledger(b,pd.Series(1.,index=b.index),0.,'breakout',atr_series=pd.Series(1.,index=b.index))
        self.assertEqual(tr.exit_time.iloc[0],b.index[8]);self.assertEqual(tr.reason.iloc[0],'stop')
        self.assertEqual(p.units.iloc[6],100.)
