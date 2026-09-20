"""Phase 3 statistics: block-bootstrap Sharpe intervals and p-values, Deflated Sharpe Ratio, CSCV probability of
backtest overfitting, Benjamini-Hochberg, and expanding-window walk-forward selection."""
import numpy as np,pandas as pd
from scipy.stats import norm,skew,kurtosis

def daily_returns(path,initial=10000.):
    e=path.equity.resample('1D').last().dropna();r=e.pct_change().dropna();return r

def block_bootstrap_sharpe(r,block=7,samples=5000,seed=0):
    x=np.asarray(r,float);n=len(x);rng=np.random.default_rng(seed)
    if n<block*4 or x.std()==0:return dict(sharpe=0.,ci95=[0.,0.],p_value_one_sided=1.)
    starts=rng.integers(0,n,size=(samples,int(np.ceil(n/block))));idx=((starts[:,:,None]+np.arange(block))%n).reshape(samples,-1)[:,:n];bx=x[idx]
    sh=bx.mean(axis=1)/bx.std(axis=1,ddof=1)*np.sqrt(365);obs=float(x.mean()/x.std(ddof=1)*np.sqrt(365))
    return dict(sharpe=obs,ci95=np.quantile(sh,[.025,.975]).tolist(),p_value_one_sided=float(np.mean(sh<=0)))

def deflated_sharpe(sr_annual,n_obs_daily,n_trials,r,var_trials=None):
    """Bailey & Lopez de Prado DSR: probability that the observed Sharpe exceeds the expected maximum of n_trials null Sharpes."""
    x=np.asarray(r,float);sr=sr_annual/np.sqrt(365);T=n_obs_daily
    if T<30 or n_trials<1:return dict(dsr=0.,sr0_daily=None)
    v=var_trials if (var_trials is not None and var_trials>0) else 1./T  # variance of null daily-Sharpe estimates when trial variance is unknown
    emax=np.sqrt(v)*((1-np.euler_gamma)*norm.ppf(1-1/n_trials)+np.euler_gamma*norm.ppf(1-1/(n_trials*np.e))) if n_trials>1 else 0.
    g3=float(skew(x));g4=float(kurtosis(x,fisher=False))
    z=(sr-emax)*np.sqrt(T-1)/np.sqrt(1-g3*sr+(g4-1)/4*sr**2) if (1-g3*sr+(g4-1)/4*sr**2)>0 else 0.
    return dict(dsr=float(norm.cdf(z)),sr0_daily=float(emax),n_trials=int(n_trials))

def benjamini_hochberg(pvals,q=.10):
    p=np.asarray(pvals,float);m=len(p);order=np.argsort(p);ranked=p[order];thresh=q*np.arange(1,m+1)/m;passed=ranked<=thresh
    k=np.max(np.flatnonzero(passed))+1 if passed.any() else 0;out=np.zeros(m,bool);out[order[:k]]=True;return out

def pbo_cscv(matrix,S=16):
    """matrix: T x N array of per-period returns for N parameter configurations. Returns PBO (Bailey et al. 2017)."""
    from itertools import combinations
    M=np.asarray(matrix,float);T,N=M.shape;S=min(S,T//10*0+S);blocks=np.array_split(np.arange(T),S);combos=list(combinations(range(S),S//2));logits=[]
    def sh(a):s=a.std(axis=0,ddof=1);return np.where(s>0,a.mean(axis=0)/np.where(s>0,s,1),0.)
    for comb in combos:
        tr=np.concatenate([blocks[i] for i in comb]);te=np.concatenate([blocks[i] for i in range(S) if i not in comb])
        best=int(np.argmax(sh(M[tr])));rank=(np.argsort(np.argsort(sh(M[te])))[best]+1)/N;logits.append(np.log(rank/(1-rank)) if 0<rank<1 else (np.inf if rank>=1 else -np.inf))
    logits=np.array(logits);return dict(pbo=float(np.mean(logits<=0)),combinations=len(combos))

def walk_forward(returns_by_config,index,years):
    """returns_by_config: dict config -> daily return Series. Expanding-window: select best in-sample Sharpe on years < y, evaluate on year y."""
    out=[];configs=list(returns_by_config)
    for y in years[1:]:
        ins={c:returns_by_config[c][returns_by_config[c].index.year<y] for c in configs};oos={c:returns_by_config[c][returns_by_config[c].index.year==y] for c in configs}
        def s(r):return float(r.mean()/r.std()*np.sqrt(365)) if len(r)>20 and r.std()>0 else -np.inf
        best=max(configs,key=lambda c:s(ins[c]));out.append(dict(year=int(y),selected=best,is_sharpe=s(ins[best]),oos_sharpe=s(oos[best]),oos_return=float((1+oos[best]).prod()-1) if len(oos[best]) else 0.))
    return out
