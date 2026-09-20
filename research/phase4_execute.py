"""Execute all frozen Phase4 cases only after verified universe/data readiness."""
import json,hashlib,sys
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT
from phase4_data import freeze_check,universe
from phase4_run import load,DAYS
from phase4_engine import ledger,combine
from phase4_stats import returns,stats

CASES={'base':.000705,'stress':.000905,'slippage_1_5':.001105,'slippage_2':.001305,'asset_conservative':.0014,'delay1':.000905,'adverse_funding':.000905}

def combo_trades(paths,trades,w,combo_r):
    ce=(1+combo_r).cumprod()*10000;start=ce.shift(1).fillna(10000.);items=[]
    for c in ['trend','breakout']:
        p=paths[c];weights=(w if c=='trend' else 1-w).fillna(0.)
        denom=p.equity.resample('D').last().shift(1).fillna(10000.)
        scale=(start*weights/denom).reindex(p.index.normalize()).to_numpy()
        for row in trades[c].to_dict('records'):
            side=row['side'];v=p.long_pnl if side>0 else p.short_pnl
            mask=(p.index>=row['entry_time'])&(p.index<=row['exit_time']);pnl=float((v.to_numpy()*scale)[mask].sum())
            entryday=pd.Timestamp(row['entry_time']).normalize();eq=float(start.loc[entryday]);row=dict(row,component=c,pnl=pnl,ret=pnl/eq)
            items.append(row)
    return pd.DataFrame(items)

def main():
    cfg=freeze_check();assets=universe();ready=ROOT/'reports/E043_universe/DATA_READY.sha256';meta=ROOT/'reports/E043_universe/data_integrity.json'
    if not ready.exists() or hashlib.sha256(meta.read_bytes()).hexdigest()!=ready.read_text().strip():raise RuntimeError('Integrity gate not passed')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S');out=ROOT/'reports'/('E044_'+stamp);out.mkdir(exist_ok=False)
    (ROOT/'reports/PHASE4_ACTIVE_REPLICATION.txt').write_text(out.name)
    starting={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'research').glob('*.py'))};records=[];all_daily=[]
    for sym in assets+['BTCUSDT','ETHUSDT']:
        b,sg,f,adverse,integrity=load(sym);folder=out/sym;folder.mkdir()
        (folder/'data_integrity.json').write_text(json.dumps(integrity,indent=2))
        price=b.valuation_close.resample('D').last().reindex(DAYS).ffill();bh=price.pct_change(fill_method=None).fillna(0.)
        # Price-only factor/benchmark: preserve cash after mandatory MATIC exit.
        bh.to_csv(folder/'underlying_daily.csv',header=['return'])
        for case,cost in CASES.items():
            P={};T={};R={};G={};N={};TO={};COST={}
            for comp in ['trend','breakout']:
                funding=f.copy()
                if case=='adverse_funding':
                    # First run exact path to observe incoming units; perturb funding
                    # against those causal holdings, then replay. A sign cannot be
                    # chosen from future PnL. Stateful sign changes are checked below.
                    p0,_=ledger(b,sg[comp],cost,comp,f,sg['atr'])
                    sign=np.sign(p0.units.shift(1).fillna(0.));funding=f+sign*adverse
                p,tr=ledger(b,sg[comp],cost,comp,funding,sg['atr'],delay=4 if case=='delay1' else 0)
                if case=='adverse_funding':
                    actual=np.sign(p.units.shift(1).fillna(0.));bad=(actual!=sign)&(adverse>0)&(actual!=0)
                    if bad.any():raise RuntimeError('Adverse funding requires online sign replay '+sym+' '+comp)
                P[comp]=p;T[comp]=tr;R[comp]=returns(p).reindex(DAYS).fillna(0.)
                daily_eq=p.equity.resample('D').last().shift(1).fillna(10000.)
                G[comp]=p.position.abs().resample('D').mean().reindex(DAYS).fillna(0.)
                N[comp]=p.position.resample('D').mean().reindex(DAYS).fillna(0.)
                TO[comp]=(p.turnover.resample('D').sum()/daily_eq).reindex(DAYS).fillna(0.)
                COST[comp]=(p.cost.resample('D').sum()/daily_eq).reindex(DAYS).fillna(0.)
                m=stats(R[comp],tr);m.update(asset=sym,case=case,component=comp,discovery=sym not in assets,gross_exposure=float(G[comp].mean()),net_exposure=float(N[comp].mean()),max_gross=float(p.position.abs().max()),annual_turnover=float(TO[comp].sum()*365/len(DAYS)),annual_transaction_cost=float(COST[comp].sum()*365/len(DAYS)),net_funding_usdt=float(p.funding.sum()),ruin=bool(p.ruin.any()),history_start=str(b.index.min()),history_end=str(b.index.max()))
                records.append(m)
                p.to_csv(folder/f'{comp}_{case}_path.csv');tr.to_csv(folder/f'{comp}_{case}_trades.csv',index=False)
                all_daily.append(pd.DataFrame(dict(date=DAYS,asset=sym,case=case,component=comp,ret=R[comp].to_numpy(),gross=G[comp].to_numpy(),net=N[comp].to_numpy(),turnover=TO[comp].to_numpy(),cost=COST[comp].to_numpy())))
            for method in ['equal','inverse_vol']:
                r,w=combine(R['trend'],R['breakout'],method);tr=combo_trades(P,T,w,r)
                gross=(w*G['trend']+(1-w)*G['breakout']).fillna(0);net=(w*N['trend']+(1-w)*N['breakout']).fillna(0)
                turn=(w*TO['trend']+(1-w)*TO['breakout']).fillna(0);fees=(w*COST['trend']+(1-w)*COST['breakout']).fillna(0)
                # Mandatory extra component-allocation turnover is separate from
                # frozen arithmetic E040; conservative executable-cost diagnostic.
                prev=w.shift(1).fillna(0.);drift=prev*(1+R['trend'].shift(1).fillna(0.))/(1+r.shift(1).fillna(0.))
                extra=(w-drift).abs()*(G['trend'].shift(1).fillna(0)+G['breakout'].shift(1).fillna(0));extra=extra.fillna(0.)
                m=stats(r,tr);m.update(asset=sym,case=case,component=method,discovery=sym not in assets,gross_exposure=float(gross.mean()),net_exposure=float(net.mean()),annual_turnover=float(turn.sum()*365/len(DAYS)),annual_transaction_cost=float(fees.sum()*365/len(DAYS)),extra_sleeve_rebalance_cost=float(extra.sum()*cost),executable_adjusted_sharpe=stats(r-extra*cost)['sharpe'],history_start=str(b.index.min()),history_end=str(b.index.max()))
                records.append(m);tr.to_csv(folder/f'{method}_{case}_trades.csv',index=False)
                all_daily.append(pd.DataFrame(dict(date=DAYS,asset=sym,case=case,component=method,ret=r.to_numpy(),gross=gross.to_numpy(),net=net.to_numpy(),turnover=turn.to_numpy(),cost=fees.to_numpy(),extra_rebalance_cost=(extra*cost).to_numpy())))
            print(sym,case,'equal Sharpe',round(records[-2]['sharpe'],3),'DD',round(records[-2]['max_dd'],3),flush=True)
        # Each name saved before the next; losing names cannot disappear.
        pd.DataFrame(records).to_csv(out/'metrics_partial.csv',index=False)
    pd.DataFrame(records).to_csv(out/'metrics.csv',index=False);pd.concat(all_daily).to_csv(out/'daily_panel.csv',index=False)
    ending={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'research').glob('*.py'))}
    if starting!=ending:raise RuntimeError('Source changed during run; retain outputs as superseded')
    result=dict(experiment_id=out.name,architecture='frozen E040',source_hashes=starting,config_sha256=json.loads((ROOT/'PHASE4_FREEZE_HASHES.json').read_text())['config_sha256'],universe_sha256=(ROOT/'PHASE4_UNIVERSE.sha256').read_text().strip(),seed=20260909,assets=assets,cases=CASES,classification='PENDING_DEPENDENCE_AND_RED_TEAM_AUDIT',economic_replication_hypotheses=1,cumulative_economic_hypotheses=385,validation_accessed=False,final_test_accessed=False)
    (out/'results.json').write_text(json.dumps(result,indent=2));print('FINISHED',out,flush=True)
if __name__=='__main__':main()
