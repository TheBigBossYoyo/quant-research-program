"""Fixed Phase4 analysis helpers; no model or signal selection."""
import numpy as np,pandas as pd
import statsmodels.api as sm
from scipy.cluster.hierarchy import linkage,fcluster
from scipy.spatial.distance import squareform

SEED=20260909

def returns(path):
    e=path.equity.resample('D').last();r=e.pct_change(fill_method=None);r.iloc[0]=e.iloc[0]/10000-1
    # Absorbing zero NAV: subsequent returns zero, never resurrect the account.
    r=r.where(e.shift(1).ne(0),0.).fillna(0.)
    return r

def stats(r,trades=None):
    r=pd.Series(r).fillna(0.);e=(1+r).cumprod();dd=e/e.cummax().clip(lower=1)-1;vol=r.std()*np.sqrt(365);mu=r.mean()*365
    down=np.sqrt(np.mean(np.minimum(r,0)**2))*np.sqrt(365);years=len(r)/365
    cagr=float(e.iloc[-1]**(1/years)-1) if years and e.iloc[-1]>=0 else -1.
    run=mx=0
    for x in dd:run=run+1 if x<0 else 0;mx=max(mx,run)
    q=r.quantile(.05)
    out=dict(total_net_return=float(e.iloc[-1]-1),cagr=cagr,volatility=float(vol),sharpe=float(mu/vol) if vol else 0.,sortino=float(mu/down) if down else None,calmar=float(cagr/abs(dd.min())) if dd.min()<0 else None,max_dd=float(dd.min()),drawdown_duration_days=mx,expected_shortfall_95=float(r[r<=q].mean()),annual_arithmetic_return=float(mu))
    if trades is not None and len(trades):
        x=trades.ret;wins=x[x>0];loss=x[x<0];p=trades.pnl;positive=p[p>0].sum()
        out.update(trades=len(x),average_trade=float(x.mean()),median_trade=float(x.median()),win_rate=float((x>0).mean()),profit_factor=float(p[p>0].sum()/-p[p<0].sum()) if (p<0).any() else None,payoff_ratio=float(wins.mean()/-loss.mean()) if len(wins) and len(loss) else None,expectancy=float(x.mean()))
        for n in [1,5,10]:out[f'top{n}_trade_positive_pnl_share']=float(p.nlargest(n).sum()/positive) if positive>0 else None
    else:out.update(trades=0,average_trade=None,median_trade=None,win_rate=None,profit_factor=None,payoff_ratio=None,expectancy=None)
    pnl=e.diff();pnl.iloc[0]=e.iloc[0]-1
    for name,freq in [('month','M'),('quarter','Q'),('year','Y')]:
        z=pnl.groupby(pnl.index.tz_localize(None).to_period(freq)).sum();pos=z[z>0].sum();out[f'top_{name}_positive_pnl_share']=float(z.max()/pos) if pos>0 else None
    return out

def factor_fit(r,factors):
    d=pd.concat([r.rename('strategy'),factors],axis=1).replace([np.inf,-np.inf],np.nan).dropna()
    x=sm.add_constant(d.drop(columns='strategy'),has_constant='add');fit=sm.OLS(d.strategy,x).fit(cov_type='HAC',cov_kwds={'maxlags':14})
    ci=fit.conf_int().loc['const']*365;resid=fit.resid
    # OLS residuals include an intercept and have zero sample mean. Zero-intercept
    # factor-adjusted return retains the intercept, allowing a meaningful Sharpe.
    adjusted=resid+fit.params['const']
    return dict(alpha_annual=float(fit.params['const']*365),alpha_ci95_low=float(ci.iloc[0]),alpha_ci95_high=float(ci.iloc[1]),beta={k:float(v) for k,v in fit.params.items() if k!='const'},r_squared=float(fit.rsquared),residual_sharpe=float(resid.mean()/resid.std()*np.sqrt(365)),factor_adjusted_sharpe=float(adjusted.mean()/adjusted.std()*np.sqrt(365)),observations=len(d)),adjusted

def bootstrap_meta(R,adjusted,samples=2000,factor_matrices=None):
    g=np.random.default_rng(SEED);out={};R=R.fillna(0);adjusted=adjusted.dropna();a=adjusted.to_numpy();n=len(a)
    for block in [14,30,60]:
        estimates=[];signs=[];sharpes=[]
        for j in range(samples):
            starts=g.integers(0,n,int(np.ceil(n/block)));idx=((starts[:,None]+np.arange(block))%n).ravel()[:n]
            if factor_matrices is None:mean=a[idx].mean(0)*365
            else:
                mean=[]
                for sym in adjusted.columns:
                    X=factor_matrices[sym].reindex(adjusted.index).to_numpy();Y=R[sym].reindex(adjusted.index).to_numpy()
                    beta=np.linalg.lstsq(np.column_stack([np.ones(n),X[idx]]),Y[idx],rcond=None)[0];mean.append(beta[0]*365)
                mean=np.asarray(mean)
            estimates.append(np.median(mean));signs.append(np.mean(mean>0))
            raw=R.reindex(adjusted.index).to_numpy()[idx];sharpes.append(float(np.median(raw.mean(0)/raw.std(0,ddof=1)*np.sqrt(365))))
        out[str(block)]=dict(median_alpha_ci95=np.quantile(estimates,[.025,.975]).tolist(),median_sharpe_ci95=np.quantile(sharpes,[.025,.975]).tolist(),positive_fraction_ci95=np.quantile(signs,[.025,.975]).tolist(),note='Common calendar blocks across all assets; factor exposures estimated on full sample, paired return/factor bootstrap with coefficients re-estimated in each common time resample')
    means=a.mean(0)*365;draws=np.median(g.choice(means,size=(samples,len(means)),replace=True),axis=1)
    out['asset_bootstrap_descriptive']=np.quantile(draws,[.025,.975]).tolist()
    out['heterogeneity']=dict(alpha_std=float(means.std(ddof=1)),alpha_iqr=float(np.quantile(means,.75)-np.quantile(means,.25)),alpha_min=float(means.min()),alpha_max=float(means.max()),random_effects='Not used: correlated crypto units violate independent-effect sampling assumptions')
    return out

def montecarlo(r,trades=None,samples=2000):
    x=np.asarray(r,float);g=np.random.default_rng(SEED);n=len(x);out={}
    for mode in ['block14','block60','permutation']:
        dd=[]
        for j in range(samples):
            if mode=='permutation':z=g.permutation(x)
            else:
                b=int(mode.replace('block',''));st=g.integers(0,n,int(np.ceil(n/b)));ii=((st[:,None]+np.arange(b))%n).ravel()[:n];z=x[ii]
            eq=np.cumprod(1+z);dr=1-eq/np.maximum.accumulate(np.r_[1,eq])[1:];dd.append(float(dr.max()))
        dd=np.asarray(dd);out[mode]=dict(median_dd=float(np.median(dd)),dd90=float(np.quantile(dd,.9)),dd95=float(np.quantile(dd,.95)),p_dd20=float(np.mean(dd>.2)),p_dd30=float(np.mean(dd>.3)),p_dd40=float(np.mean(dd>.4)),p_total_loss=float(np.mean(dd>=1)))
    if trades is not None and len(trades):
        t=trades.ret.to_numpy();z=g.choice(t,size=(samples,len(t)),replace=True);eq=np.cumprod(1+z,axis=1);dd=1-eq/np.maximum.accumulate(np.c_[np.ones(samples),eq],axis=1)[:,1:];v=dd.max(1)
        out['trade_resampling']=dict(median_dd=float(np.median(v)),dd90=float(np.quantile(v,.9)),dd95=float(np.quantile(v,.95)),p_dd20=float(np.mean(v>.2)),p_dd30=float(np.mean(v>.3)),p_dd40=float(np.mean(v>.4)),note='Episode-equity returns; heuristic for changing allocations, not exact trade-capital replay')
    return out

def allocation(R,method='equal'):
    if method=='equal':return pd.DataFrame(1/R.shape[1],index=R.index,columns=R.columns)
    if method=='inverse_vol':
        v=R.rolling(60).std().shift(1);inv=1/v.replace(0,np.nan);return inv.div(inv.sum(axis=1),axis=0).fillna(0.)
    if method=='risk_parity':
        W=pd.DataFrame(0.,index=R.index,columns=R.columns)
        for i in range(120,len(R)):
            C=R.iloc[max(0,i-180):i].cov().to_numpy()
            if not np.isfinite(C).all() or np.linalg.cond(C)>1e6 or np.linalg.eigvalsh(C).min()<=0:continue
            x=np.ones(len(C));b=1/len(C)
            for _ in range(60):
                for j in range(len(C)):
                    c=C[j]@x-C[j,j]*x[j];x[j]=(-c+np.sqrt(c*c+4*C[j,j]*b))/(2*C[j,j])
            W.iloc[i]=x/x.sum()
        return W
    raise ValueError(method)

def cluster_caps(R,W,cap=.5):
    W=W.copy();clusters=pd.DataFrame(index=R.index,columns=R.columns,dtype=float)
    for i in range(120,len(R)):
        corr=R.iloc[max(0,i-180):i].corr().fillna(0).abs().to_numpy();groups=[];unseen=set(range(R.shape[1]))
        while unseen:
            todo=[unseen.pop()];group=[]
            while todo:
                j=todo.pop();group.append(j);near=[k for k in unseen if corr[j,k]>=.65]
                for k in near:unseen.remove(k);todo.append(k)
            groups.append(group)
        for g in groups:
            clusters.iloc[i,g]=min(g);total=float(W.iloc[i,g].sum())
            if total>cap:W.iloc[i,g]*=cap/total
    return W,clusters

def portfolio(R,W,G=None,cost=.0014):
    gross=pd.DataFrame(1.,index=R.index,columns=R.columns) if G is None else G
    theoretical=(R*W).sum(1);previous=W.shift(1).fillna(0.)*(1+R.shift(1).fillna(0.))
    previous=previous.div(1+theoretical.shift(1).fillna(0.),axis=0)
    extra_turn=((W-previous).abs()*gross.shift(1).fillna(0.)).sum(1)
    r=theoretical-extra_turn*cost
    return r,extra_turn


def remove_diagnostics(r,trades=None):
    out={};e=(1+r).cumprod();p=e.diff();p.iloc[0]=e.iloc[0]-1
    y=p.groupby(p.index.year).sum();best=int(y.idxmax())
    out['best_year']=best;out['remove_best_year']=stats(r[r.index.year!=best])
    if trades is not None and len(trades):
        for n in [1,5]:
            z=r.copy();selected=trades.nlargest(n,'pnl')
            # Remove the complete calendar-day return intervals, not just winning
            # dollar amounts; overlapping episodes are a deliberately coarse diagnostic.
            mask=pd.Series(False,index=r.index)
            for row in selected.itertuples():mask|=(r.index>=pd.Timestamp(row.entry_time).normalize())&(r.index<=pd.Timestamp(row.exit_time).normalize())
            z[mask]=0.;out[f'remove_best{n}_trade_intervals']=stats(z)
    return out
