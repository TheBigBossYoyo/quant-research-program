"""E021 (session/funding-hour seasonality on spot) and E022 (BTC/ETH lead-lag on perpetual hours).

Development 2022-2024 only. Reuses core.simulate (spot long/cash) and the E010/E012 perpetual machinery.
"""
import json,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT,config,code_hash,load_data,simulate,metrics
from audit import uncertainty
from perpetual_screen import prepare,signed_ledger,performance
from flow_screen import resample_bars,stage1,following_target,threshold_target,to_hourly_target,COST_CASES,THRESHOLD_DAYS

US_SESSION=(13*60+30,20*60);FUNDING_HOURS=(7,15,23)

def session_signal(index,window,delay=2,invert=False):
    """Signal at bar t is 1 when the bar `delay` steps ahead lies inside the window (minutes of day)."""
    ahead=index+pd.Timedelta(minutes=5*delay);mod=ahead.hour*60+ahead.minute
    inside=(mod>=window[0])&(mod<window[1])
    return pd.Series((~inside if invert else inside).astype(float),index=index)

def funding_hour_signal(index,delay=2,invert=False):
    ahead=index+pd.Timedelta(minutes=5*delay);inside=np.isin(ahead.hour,FUNDING_HOURS)
    return pd.Series((~inside if invert else inside).astype(float),index=index)

def hour_profile(d):
    r=d.close/d.open-1;return {str(y):{int(h):float(v*1e4) for h,v in r[r.index.year==y].groupby(r[r.index.year==y].index.hour).mean().items()} for y in sorted(set(r.index.year))}

def run_session():
    cfg=config();eid='E021_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();rows=[];profiles={};k=0;hyps=8
    for sym in cfg['symbols']:
        raw,integ=load_data(sym);d=raw.copy();d['execution_open']=d.open;d['execution_volume']=d.volume;profiles[sym]=hour_profile(d)
        rules={'us_session_long':session_signal(d.index,US_SESSION),'us_session_mirror':session_signal(d.index,US_SESSION,invert=True),
               'pre_funding_hour_long':funding_hour_signal(d.index),'pre_funding_hour_mirror':funding_hour_signal(d.index,invert=True)}
        bh=simulate(d,pd.Series(1.,index=d.index),cfg['one_way_cost_bps']['stress']);bhm=metrics(bh,5)
        for name,s in rules.items():
            for case,cost in cfg['one_way_cost_bps'].items():
                b=simulate(d,s,cost);m=metrics(b,5);rec=dict(symbol=sym,rule=name,case=case,cost_bps=cost,**m)
                if case=='stress':
                    daily=(1+b.net).resample('1D').prod()-1
                    u=uncertainty(daily,np.zeros(len(daily)),20260908+500+k,trials=hyps,samples=2000,block=7);k+=1
                    rec['stress_uncertainty']=u;rec['passes']=bool(m['cumulative_return']>0 and m['sharpe']>bhm['sharpe'] and u['simultaneous_lower_mean_daily']>0)
                    print(sym,name,'stress cum',round(m['cumulative_return'],4),'sharpe',round(m['sharpe'],3),'bh sharpe',round(bhm['sharpe'],3),'adj lower bps',round(u['simultaneous_lower_mean_daily']*1e4,2),'pass',rec['passes'],flush=True)
                rows.append(rec)
        rows.append(dict(symbol=sym,rule='buy_hold',case='stress',cost_bps=cfg['one_way_cost_bps']['stress'],**bhm))
    survivors=[dict(symbol=r['symbol'],rule=r['rule']) for r in rows if r.get('passes')]
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=20260908+500,new_hypotheses=hyps,cumulative_hypotheses=223+hyps,rows=rows,
        hour_of_day_mean_return_bps_by_year=profiles,survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    pd.DataFrame([{k:v for k,v in r.items() if k not in ('calendar_returns','stress_uncertainty')} for r in rows]).to_csv(out/'metrics.csv',index=False)
    print('OUTPUT',out,'SURVIVORS',survivors)

def run_leadlag():
    eid='E022_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/eid;out.mkdir(parents=True,exist_ok=False)
    starting=code_hash();data={s:prepare(s) for s in ['BTCUSDT','ETHUSDT']};stage1_rows=[];stage2_rows=[];cell=0;rule_b=0
    for leader,follower in [('BTCUSDT','ETHUSDT'),('ETHUSDT','BTCUSDT')]:
        fl,px,funding,meta=data[follower];fe=data[leader][0];mn=50 if follower=='BTCUSDT' else 20
        for tf in [1,4]:
            lb=resample_bars(fe,tf);fb=resample_bars(fl,tf)
            cf=pd.DataFrame(index=fb.index);cf['leader_ret1']=lb.close/lb.close.shift(1)-1;cf['exec_open']=fb.open;cf['bar_return']=fb.close/fb.open-1
            s1=stage1(cf,cell,tf,features=['leader_ret1'],cells=4,seed=20260908+600,horizons=(1,4,24));cell+=1
            r=s1['leader_ret1'];stage1_rows.append(dict(leader=leader,follower=follower,timeframe_hours=tf,**r))
            print(leader,'->',follower,tf,'IC',round(r['ic'],4),'adj CI',[round(r['ci_lower_adjusted'],4),round(r['ci_upper_adjusted'],4)],'pass',r['passes_stage1'],flush=True)
            if not r['passes_stage1']:continue
            d=r['direction'];s=cf['leader_ret1'];window=int(THRESHOLD_DAYS*24/tf)
            long_target=to_hourly_target(pd.Series(1.,index=cf.index),px.index)
            for case,fee in COST_CASES:stage2_rows.append(dict(leader=leader,follower=follower,timeframe_hours=tf,rule='long_baseline',case=case,**performance(signed_ledger(px,long_target,funding,fee=fee,min_notional=mn))))
            for rule,t in [('a_following',following_target(s,d)),('b_threshold',threshold_target(s,d,window))]:
                if rule=='b_threshold':rule_b+=1
                target=to_hourly_target(t,px.index)
                for case,fee in COST_CASES:
                    m=performance(signed_ledger(px,target,funding,fee=fee,min_notional=mn));stage2_rows.append(dict(leader=leader,follower=follower,timeframe_hours=tf,rule=rule,direction=d,case=case,**m))
                print('  ',rule,'stress cagr',round(stage2_rows[-1]['cagr'],4),flush=True)
    survivors=[]
    for r in stage2_rows:
        if r['case']!='stress' or r['rule']=='long_baseline':continue
        b=next(x for x in stage2_rows if x['follower']==r['follower'] and x['timeframe_hours']==r['timeframe_hours'] and x['rule']=='long_baseline' and x['case']=='stress')
        if r['cagr']>0 and r['daily_sharpe']>max(0.,b['daily_sharpe']) and sum(v>0 for v in r['calendar_returns'].values())>=2 and not r['halted']:survivors.append({k:r[k] for k in ['leader','follower','timeframe_hours','rule','direction']})
    assert starting==code_hash()
    (out/'results.json').write_text(json.dumps(dict(experiment_id=eid,code_hash=starting,git_commit=None,seed=20260908+600,new_hypotheses=8,rule_b_trials=rule_b,cumulative_hypotheses=231+8+rule_b,
        stage1=stage1_rows,stage2=stage2_rows,survivors=survivors,validation_accessed=False,final_test_accessed=False),indent=2,allow_nan=False,default=float))
    print('OUTPUT',out,'SURVIVORS',survivors)

if __name__=='__main__':
    {'session':run_session,'leadlag':run_leadlag}[sys.argv[1]]()
