"""E014: preregistered cross-sectional screen on the survivorship-aware perpetual universe.

Stage 1: weekly cross-sectional IC gate. Stage 2: weight ledger with funding, costs,
delisting exits. Development 2022-2024 only; no leverage; no validation/final access.
"""
import json
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.stats import spearmanr,norm
from core import ROOT,code_hash
from universe import load_klines,load_funding,daily_funding,eligibility,features,forward_open_return,rebalance_days,quintile_weights,MIN_HISTORY_BARS

FEATURE_SETS={'flow':dict(cells=['ret7','ret30','fund7','flow7'],prior=199,eid='E016'),  # E016 rerun on 2020-2024 counted again
              'risk':dict(cells=['vol30','abnvol7','amihud30'],prior=209,eid='E018'),   # E018 risk/attention characteristics
              'horizon':dict(cells=['ret90'],prior=239,eid='E023')}                       # E023 long-horizon momentum (after E021/E022)
import sys as _sys
_SET=FEATURE_SETS[next((a for a in _sys.argv[1:] if a in FEATURE_SETS),'flow')]
FEATURE_CELLS=_SET['cells'];PRIOR_HYPOTHESES=_SET['prior'];NEW_HYPOTHESES=2*len(FEATURE_CELLS);EXPERIMENT_PREFIX=_SET['eid']
COST_CASES=[('base',.0007),('stress',.0014),('severe',.0028)];STEP=7;DELAY=2

def xs_ledger(open_panel,fund_daily,weights_by_day,cost,initial=10000.,delay=DELAY,attribution=False):
    """Unit-based dollar-neutral ledger marked at daily opens.

    Targets decided at day r execute at open(r+DELAY). Funding settled during day d
    is charged at open(d+1) on units held through day d, using close-of-day proxy
    notional. A held symbol with no open on day d exits at its last observed open.
    """
    days=open_panel.index;opens=open_panel.to_numpy();cols=list(open_panel.columns)
    last_open=open_panel.ffill().to_numpy();fund=fund_daily.reindex(index=days,columns=cols).fillna(0.).to_numpy()
    nav=initial;units=np.zeros(len(cols));exec_map={};pnl_sym=np.zeros(len(cols));fund_total=0.;cost_total=0.
    for r,w in weights_by_day.items():
        pos=days.get_loc(r)+delay
        if pos<len(days):exec_map[pos]=w
    rows=[]
    for i in range(len(days)):
        px=opens[i]
        # 1) funding on units held through the previous day, settled at that day's close proxy
        if i>0:
            proxy=np.where(np.isfinite(opens[i]),opens[i],last_open[i])
            f=float(np.nansum(units*fund[i-1]*proxy));nav-=f;fund_total-=f
        # 2) mark to market using last observed opens (missing today => exit at last open)
        held=units!=0
        if held.any():
            missing=held&~np.isfinite(px)
            if missing.any():
                c=float(np.sum(np.abs(units[missing])*last_open[i][missing]*cost));nav-=c;cost_total+=c;units[missing]=0.
        # 3) execute targets
        if i in exec_map:
            w=exec_map[i];target=np.zeros(len(cols))
            for sym,val in w.items():
                j=cols.index(sym)
                if np.isfinite(px[j]):target[j]=val*nav/px[j]
            delta=target-units;notional=np.nansum(np.abs(delta)*np.where(np.isfinite(px),px,0.))
            nav-=float(notional*cost);cost_total+=float(notional*cost);units=target
            turnover=float(notional)
        else:turnover=0.
        # 4) NAV change to next open
        if i+1<len(days):
            nxt=np.where(np.isfinite(opens[i+1]),opens[i+1],last_open[i+1]);cur=np.where(np.isfinite(px),px,last_open[i])
            contrib=units*(nxt-cur);pnl=float(np.nansum(contrib));pnl_sym+=np.nan_to_num(contrib)
        else:pnl=0.
        gross=float(np.nansum(np.abs(units)*np.where(np.isfinite(px),px,last_open[i])))/nav if nav>0 else float('inf')
        rows.append(dict(time=days[i],nav=nav,turnover_notional=turnover,gross=gross,names=int((units!=0).sum())))
        nav+=pnl
        if nav<=0:raise ValueError('Necessary insolvency; no ghost account')
    path=pd.DataFrame(rows).set_index('time')
    if attribution:return path,dict(pnl_by_symbol=pd.Series(pnl_sym,index=cols),funding_pnl=fund_total,cost_paid=cost_total)
    return path

def performance(path,initial=10000.):
    nav=path.nav;r=nav.pct_change();r.iloc[0]=nav.iloc[0]/initial-1
    dd=nav/nav.cummax().clip(lower=initial)-1
    return dict(ending_equity=float(nav.iloc[-1]),cagr=float((nav.iloc[-1]/initial)**(365.25/len(nav))-1),
        daily_sharpe=float(r.mean()/r.std()*np.sqrt(365.25)) if r.std()>0 else 0.,max_daily_drawdown=float(dd.min()),
        max_gross=float(path.gross.max()),mean_names=float(path.names[path.names>0].mean()) if (path.names>0).any() else 0.,
        annual_turnover=float(path.turnover_notional.sum()/nav.mean()/(len(nav)/365.25)),
        calendar_returns={str(y):float((1+x).prod()-1) for y,x in r.groupby(r.index.year)})

def stage1(feat,elig,open_panel,days_rb):
    fwd=forward_open_return(open_panel,DELAY,DELAY+STEP);crit=norm.ppf(1-.05/len(FEATURE_CELLS)/2);out={}
    for name in FEATURE_CELLS:
        ics=[];dates=[]
        for d in days_rb:
            s=feat[name].loc[d].where(elig.loc[d]);f=fwd.loc[d];m=s.notna()&f.notna()
            if m.sum()>=10:ics.append(float(spearmanr(s[m],f[m]).statistic));dates.append(d)
        ic=pd.Series(ics,index=pd.DatetimeIndex(dates));t=float(ic.mean()/ic.std(ddof=1)*np.sqrt(len(ic))) if len(ic)>2 else 0.
        decay={}
        for k in [1,2,4]:
            fk=forward_open_return(open_panel,DELAY,DELAY+STEP*k);vals=[]
            for d in days_rb:
                s=feat[name].loc[d].where(elig.loc[d]);f=fk.loc[d];m=s.notna()&f.notna()
                if m.sum()>=10:vals.append(float(spearmanr(s[m],f[m]).statistic))
            decay[str(k)]=float(np.mean(vals)) if vals else float('nan')
        early=ic[ic.index<pd.Timestamp('2022-01-01',tz='UTC')]
        subsample={'2020_2021':dict(mean_ic=float(early.mean()),t=float(early.mean()/early.std(ddof=1)*np.sqrt(len(early))),weeks=int(len(early)))} if len(early)>2 else {}
        out[name]=dict(feature=name,mean_ic=float(ic.mean()),ic_t=t,weeks=int(len(ic)),critical_t=float(crit),passes_stage1=bool(abs(t)>crit),fresh_subsample=subsample,
            direction=int(np.sign(ic.mean())) if abs(t)>crit else 0,ic_by_year={str(y):float(v.mean()) for y,v in ic.groupby(ic.index.year)},
            decay_mean_ic_by_weeks=decay,mean_eligible=float(np.mean([int(elig.loc[d].sum()) for d in days_rb])))
    return out

def main():
    eid=EXPERIMENT_PREFIX+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();panels,ki=load_klines();funding,fi=load_funding()
    days=panels['close'].index;syms=list(panels['close'].columns)
    fund_daily=daily_funding(funding,days,syms);elig=eligibility(panels);feat=features(panels,fund_daily)
    first=days[MIN_HISTORY_BARS]  # first day on which a full-history symbol can be eligible
    days_rb=rebalance_days(days,first,STEP);days_rb=days_rb[days_rb<=days[-1]-pd.Timedelta(days=DELAY+STEP)]
    s1=stage1(feat,elig,panels['open'],days_rb)
    for k,v in s1.items():print(k,'meanIC',round(v['mean_ic'],4),'t',round(v['ic_t'],2),'pass',v['passes_stage1'],flush=True)
    stage2=[];rb_all=rebalance_days(days,first,STEP)
    def weights(fn):
        return {d:w for d in rb_all for w in [fn(d)] if len(w)}
    baselines={'ew_long':weights(lambda d:(lambda e:pd.Series(1./e.sum(),index=e[e].index) if e.sum()>=10 else pd.Series(dtype=float))(elig.loc[d])),
        'btc_long':weights(lambda d:pd.Series({'BTCUSDT':1.}) if 'BTCUSDT' in syms and np.isfinite(panels['open'].loc[d,'BTCUSDT']) else pd.Series(dtype=float))}
    for name,w in baselines.items():
        for case,c in COST_CASES:
            stage2.append(dict(hypothesis=name,feature=name,direction=1,case=case,cost=c,**performance(xs_ledger(panels['open'],fund_daily,w,c))))
    for name,r in s1.items():
        if not r['passes_stage1']:continue
        d=r['direction'];w=weights(lambda day:quintile_weights(feat[name].loc[day],elig.loc[day],d))
        for case,c in COST_CASES:
            m=performance(xs_ledger(panels['open'],fund_daily,w,c))
            stage2.append(dict(hypothesis=f'{name}_{"continuation" if d>0 else "reversal"}',feature=name,direction=d,case=case,cost=c,**m))
            print(name,d,case,'cagr',round(m['cagr'],4),'sharpe',round(m['daily_sharpe'],3),'dd',round(m['max_daily_drawdown'],3),flush=True)
    survivors=[]
    for r in stage2:
        if r['case']!='stress' or r['hypothesis'] in baselines:continue
        if r['cagr']>0 and r['daily_sharpe']>0 and sum(v>0 for v in r['calendar_returns'].values())>=2 and r['max_daily_drawdown']>-.30:
            survivors.append(dict(hypothesis=r['hypothesis'],feature=r['feature'],direction=r['direction']))
    assert starting==code_hash(),'Source changed during experiment'
    result=dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=None,cumulative_hypotheses=PRIOR_HYPOTHESES+NEW_HYPOTHESES,new_hypotheses=NEW_HYPOTHESES,
        integrity=dict(klines={k:v for k,v in ki.items() if k!='sources'},funding={k:v for k,v in fi.items() if k!='sources'}),
        stage1=list(s1.values()),stage2=stage2,stage2_survivors=survivors,rebalance_weeks=int(len(rb_all)),
        validation_accessed=False,final_test_accessed=False,
        verdict='CHEAP DEVELOPMENT SCREEN; close-proxy funding notional, uncalibrated alt friction, no depth/queue model, delisting exit at last open assumed.')
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    (out/'sources.json').write_text(json.dumps(dict(klines=ki['sources'],funding=fi['sources'])))
    pd.DataFrame([{k:v for k,v in r.items() if k!='calendar_returns'} for r in stage2]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'STAGE1',[k for k,v in s1.items() if v['passes_stage1']],'STAGE2',survivors)

if __name__=='__main__':main()
