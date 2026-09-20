"""E045: fixed statistical, portfolio, concentration and adversarial report."""
import json,hashlib
from datetime import datetime,timezone
import numpy as np,pandas as pd
from core import ROOT
from phase4_data import freeze_check,universe
from phase4_run import read_hourly,DAYS
from phase4_stats import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'figure.dpi':120,'axes.spines.top':False,'axes.spines.right':False,'font.size':9})

def table(df):
    return '| '+' | '.join(str(x) for x in df.columns)+' |\n|'+'|'.join(['---']*len(df.columns))+'|\n'+''.join('| '+' | '.join(f'{x:.5g}' if isinstance(x,(float,np.floating)) else str(x) for x in row)+' |\n' for row in df.itertuples(index=False,name=None))

def main(source_name=None,root_writes=True):
    import sys,locale
    if not sys.flags.utf8_mode and locale.getpreferredencoding(False).lower().replace('-','')!='utf8':raise RuntimeError('Run with PYTHONUTF8=1 so every report is written as UTF-8')
    freeze_check();assets=universe();source=ROOT/'reports'/(source_name or (ROOT/'reports/PHASE4_ACTIVE_REPLICATION.txt').read_text().strip())
    if not (source/'results.json').exists():raise ValueError('Replication incomplete')
    out=ROOT/'reports'/('E045_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'));out.mkdir(exist_ok=False);charts=out/'charts';charts.mkdir()
    docs=ROOT if root_writes else out/'root_documents';docs.mkdir(exist_ok=True)
    if root_writes:(ROOT/'reports/PHASE4_ACTIVE_ANALYSIS.txt').write_text(out.name)
    M=pd.read_csv(source/'metrics.csv');d=pd.read_csv(source/'daily_panel.csv',parse_dates=['date']);d.date=pd.to_datetime(d.date,utc=True)
    def panel(comp='equal',case='stress',col='ret',names=None):
        x=d[(d.component==comp)&(d.case==case)].pivot(index='date',columns='asset',values=col)
        return x.reindex(columns=names or assets).fillna(0.)
    B={}
    for sym in assets+['BTCUSDT','ETHUSDT']:
        z=pd.read_csv(source/sym/'underlying_daily.csv',index_col=0,parse_dates=True);B[sym]=z.iloc[:,0]
    B=pd.DataFrame(B);B.index=pd.to_datetime(B.index,utc=True)
    btc,_=read_hourly('BTCUSDT','klines');close=btc.close.resample('D').last();btc_r=close.pct_change(fill_method=None)
    vol=btc_r.rolling(30).std().shift(1)*np.sqrt(365);trend=np.sign(close-close.rolling(200).mean()).shift(1)
    market=B[assets].mean(1);factor_rows=[];adj={};matrices={};univar=[]
    for comp in ['trend','breakout','equal','inverse_vol']:
        R=panel(comp);adj[comp]={}
        for sym in assets:
            X=pd.DataFrame(dict(underlying=B[sym],BTC=B.BTCUSDT,market=market,volatility=vol.reindex(DAYS),trend_state=trend.reindex(DAYS)),index=DAYS)
            m,a=factor_fit(R[sym],X);u,_=factor_fit(R[sym],X[['underlying']]);adj[comp][sym]=a
            factor_rows.append(dict(asset=sym,component=comp,alpha=m['alpha_annual'],alpha_ci_low=m['alpha_ci95_low'],alpha_ci_high=m['alpha_ci95_high'],asset_beta=m['beta']['underlying'],btc_beta=m['beta']['BTC'],market_beta=m['beta']['market'],r_squared=m['r_squared'],residual_sharpe=m['residual_sharpe'],factor_adjusted_sharpe=m['factor_adjusted_sharpe'],univariate_alpha=u['alpha_annual'],univariate_beta=u['beta']['underlying']))
            if comp=='equal':matrices[sym]=X
        print('FACTORS',comp,flush=True)
    F=pd.DataFrame(factor_rows);F.to_csv(out/'factor_results.csv',index=False)
    primary=panel();alpha=pd.DataFrame(adj['equal']);meta=bootstrap_meta(primary,alpha,factor_matrices=matrices)
    (out/'meta_analysis.json').write_text(json.dumps(meta,indent=2));print('META',meta,flush=True)
    selected=M[(M.case=='stress')&(~M.discovery)].merge(F,on=['asset','component'],how='left')
    selected[selected.component=='equal'].to_csv(docs/'PHASE4_REPLICATION_RESULTS.csv',index=False)
    selected[selected.component.isin(['trend','breakout'])].to_csv(docs/'PHASE4_COMPONENT_RESULTS.csv',index=False)
    allport={};Wsave={};prows=[];portturn={};clusters_final=None
    for comp in ['equal','inverse_vol']:
        R=panel(comp)-panel(comp,col='extra_rebalance_cost');G=panel(comp,col='gross');N=panel(comp,col='net')
        for method in ['equal','inverse_vol','risk_parity']:
            W=allocation(R,method)
            for capped in [False,True]:
                wc,cl=cluster_caps(R,W) if capped else (W,None)
                name=comp+'__'+method+('__cluster_cap' if capped else '')
                pr,trn=portfolio(R,wc,G,.0014);allport[name]=pr;Wsave[name]=wc;portturn[name]=trn
                m=stats(pr);u,_=factor_fit(pr,pd.DataFrame(dict(BTC=B.BTCUSDT,market=market,volatility=vol.reindex(DAYS),trend_state=trend.reindex(DAYS)),index=DAYS))
                m.update(portfolio=name,alpha=u['alpha_annual'],alpha_ci_low=u['alpha_ci95_low'],alpha_ci_high=u['alpha_ci95_high'],annual_turnover=float(((wc*panel(comp,col='turnover')).sum(1)+trn).sum()*365/len(DAYS)),annual_cost=float(((wc*panel(comp,col='cost')).sum(1)+trn*.0014+(wc*panel(comp,col='extra_rebalance_cost')).sum(1)).sum()*365/len(DAYS)),gross_exposure=float((wc*G).sum(1).mean()),net_exposure=float((wc*N).sum(1).mean()),weight_hhi=float((wc**2).sum(1).mean()),max_asset_weight=float(wc.max().max()),average_invested_weight=float(wc.sum(1).mean()))
                prows.append(m);wc.to_csv(out/(name+'_weights.csv'))
                if capped:clusters_final=cl
    ports=pd.DataFrame(allport);ports.to_csv(out/'portfolio_daily.csv');P=pd.DataFrame(prows);P.to_csv(docs/'PHASE4_PORTFOLIO_RESULTS.csv',index=False)
    if clusters_final is not None:clusters_final.to_csv(out/'causal_clusters.csv')
    key='equal__equal';primary_port=ports[key];stress_summary=[]
    for case in ['base','stress','slippage_1_5','slippage_2','asset_conservative','delay1','adverse_funding']:
        R=panel(case=case)-panel(case=case,col='extra_rebalance_cost');W=allocation(R);rp,t=portfolio(R,W,panel(case=case,col='gross'),.0014)
        stress_summary.append(dict(case=case,**stats(rp),positive_asset_fraction=float((M[(M.case==case)&(M.component=='equal')&(~M.discovery)].total_net_return>0).mean())))
    stress=pd.DataFrame(stress_summary);stress.to_csv(out/'portfolio_stresses.csv',index=False)
    concentrations={};mc={};yearly=[];bear=[]
    for sym in assets:
        r=primary[sym];tr=pd.read_csv(source/sym/'equal_stress_trades.csv',parse_dates=['entry_time','exit_time'])
        concentrations[sym]=remove_diagnostics(r,tr);mc[sym]=montecarlo(r,tr)
        for year,g in r.groupby(r.index.year):
            fsub=matrices[sym].reindex(g.index);fm,_=factor_fit(g,fsub)
            yearly.append(dict(asset=sym,year=year,alpha=fm['alpha_annual'],**stats(g)))
        x=d[(d.asset==sym)&(d.component=='equal')&(d.case=='stress')].set_index('date');mask=x.index.year==2022
        legs={}
        for comp in ['trend','breakout']:
            pp=pd.read_csv(source/sym/f'{comp}_stress_path.csv',index_col=0,parse_dates=True);pp=pp[pp.index.year==2022]
            legs[comp]=dict(long_pnl=float(pp.long_pnl.sum()),short_pnl=float(pp.short_pnl.sum()))
        bear.append(dict(asset=sym,period='2022 calendar bear diagnostic',underlying_return=float((1+B.loc[B.index.year==2022,sym]).prod()-1),gross_exposure=float(x.loc[mask,'gross'].mean()),net_exposure=float(x.loc[mask,'net'].mean()),component_dollar_pnl=legs,**stats(r[r.index.year==2022])))
        print('STRESS/MC',sym,flush=True)
    for name,r in allport.items():
        mc[name]=montecarlo(r,samples=2000);concentrations[name]=remove_diagnostics(r)
    (out/'monte_carlo.json').write_text(json.dumps(mc,indent=2));(out/'concentration.json').write_text(json.dumps(concentrations,indent=2));pd.DataFrame(yearly).to_csv(out/'temporal_stability.csv',index=False);(out/'bear_markets.json').write_text(json.dumps(bear,indent=2))
    for name,R in [('asset',B[assets]),('strategy',primary),('trend',panel('trend')),('breakout',panel('breakout')),('drawdown',(1+primary).cumprod().div((1+primary).cumprod().cummax())-1)]:
        R.corr().to_csv(out/(name+'_correlations.csv'))
    crisis=primary.loc[(B.BTCUSDT<-.05)|(B.index.year==2022)].corr();crisis.to_csv(out/'crisis_correlations.csv')
    # Net dollar contribution assigned across real component episodes under the
    # primary equal allocation. Sum directly reconciles against portfolio PnL
    # apart from separately reported allocation-turnover costs.
    ep=(1+primary_port).cumprod()*10000;start=ep.shift(1).fillna(10000.);contrib=primary.mul(start/len(assets),axis=0)
    contrib.to_csv(out/'asset_dollar_contributions.csv');combo_equity=(1+primary).cumprod()*10000
    portfolio_trades=[];trade_daily=[]
    for sym in assets:
        for comp in ['trend','breakout']:
            pp=pd.read_csv(source/sym/f'{comp}_stress_path.csv',index_col=0,parse_dates=True)
            tt=pd.read_csv(source/sym/f'{comp}_stress_trades.csv',parse_dates=['entry_time','exit_time'])
            denom=pp.equity.resample('D').last().shift(1).fillna(10000.)
            scale=(start*.5/len(assets)/denom).reindex(pp.index.normalize()).to_numpy()
            for row in tt.to_dict('records'):
                v=pp.long_pnl if row['side']>0 else pp.short_pnl
                mask=(pp.index>=row['entry_time'])&(pp.index<=row['exit_time'])
                contributions=pd.Series(np.where(mask,v.to_numpy()*scale,0.),index=pp.index).resample('D').sum().reindex(DAYS).fillna(0.)
                pnl=float(contributions.sum());portfolio_trades.append(dict(asset=sym,component=comp,pnl=pnl,entry_time=row['entry_time'],exit_time=row['exit_time'],ret=pnl/float(start.loc[pd.Timestamp(row['entry_time']).normalize()])))
                trade_daily.append(contributions.to_numpy())
    pt=pd.DataFrame(portfolio_trades);pt.to_csv(out/'portfolio_trade_contributions.csv',index=False)
    td=np.array(trade_daily);np.savez_compressed(out/'portfolio_trade_daily_contributions.npz',contributions=td)
    costs_unassigned=float(contrib.sum().sum()-(ep.iloc[-1]-10000.))
    positive_trade_pnl=float(pt.pnl[pt.pnl>0].sum())
    port_top5=float(pt.pnl.nlargest(5).sum()/max(positive_trade_pnl-max(0,costs_unassigned),1e-9))
    concentrations[key].update(top5_trade_share_conservative=port_top5,unassigned_allocation_cost=costs_unassigned,trade_contribution_reconciliation_error=float(td.sum()-contrib.sum().sum()))
    for n in [1,5]:
        ids=pt.nlargest(n,'pnl').index.to_numpy();removed=td[ids].sum(0)
        counter=primary_port-pd.Series(removed,index=DAYS)/start
        concentrations[key][f'remove_best{n}_trade_contributions']=stats(counter)
    (out/'concentration.json').write_text(json.dumps(concentrations,indent=2))
    sm=selected[selected.component=='equal'];fa=F[F.component=='equal'];p=P[P.portfolio==key].iloc[0]
    positive=float((sm.total_net_return>0).mean());positive_alpha=float((fa.alpha>0).mean());lower=min(v['median_alpha_ci95'][0] for k,v in meta.items() if k in ['14','30','60'])
    gates=dict(asset_count=len(assets)>=8,positive_fraction=positive>=2/3,positive_alpha_fraction=positive_alpha>=2/3,median_sharpe=float(sm.sharpe.median())>=.3,median_alpha=float(fa.alpha.median())>0,common_block_lower_alpha=lower>0,portfolio_drawdown=p.max_dd>-.4,top5_trade_concentration=port_top5<.5,top_year_concentration=p.top_year_positive_pnl_share<.6,conservative_stress=float(stress.set_index('case').loc['asset_conservative','total_net_return'])>0,remove_best_year=concentrations[key]['remove_best_year']['total_net_return']>0,no_unresolved_accounting_or_data_defects=abs(concentrations[key]['trade_contribution_reconciliation_error'])<1e-6)
    # Operational lot sizes and spread proxies are disclosed separately from research validity; no automatic rejection solely for unknown account fees.
    if sm.total_net_return.median()<=0 and positive<=.5:verdict='REPLICATION_FAILURE'
    elif positive<2/3:verdict='MIXED_REPLICATION'
    elif all(gates.values()):verdict='VALIDATION_ELIGIBLE'
    elif all(gates[k] for k in ['positive_fraction','positive_alpha_fraction','median_sharpe','median_alpha','common_block_lower_alpha','conservative_stress']):verdict='CROSS_ASSET_RESEARCH_PROMISING'
    else:verdict='CROSS_ASSET_WEAK_SIGNAL'
    decision='OPEN_2025_ONCE' if verdict=='VALIDATION_ELIGIBLE' else 'DO_NOT_OPEN_2025'
    summary=dict(classification=verdict,decision=decision,assets=assets,positive_asset_fraction=positive,positive_alpha_fraction=positive_alpha,median_sharpe=float(sm.sharpe.median()),median_alpha=float(fa.alpha.median()),median_drawdown=float(sm.max_dd.median()),median_net_expectancy=float(sm.expectancy.median()),positive_expectancy_fraction=float((sm.expectancy>0).mean()),primary_portfolio=p.to_dict(),best_portfolio=P.sort_values('sharpe',ascending=False).iloc[0].to_dict(),gates=gates,meta_analysis=meta,validation_2025='LOCKED',holdout_2026='UNTOUCHED')

    # Capital feasibility scenarios: no fabricated account-specific filters.
    capital=[]
    for fx in [.9,1.,1.1]:
        usd=500*fx
        for minimum in [5.,10.,20.]:
            sizes=[]
            for sym in assets:
                for comp in ['trend','breakout']:
                    pp=pd.read_csv(source/sym/f'{comp}_stress_path.csv',index_col=0,parse_dates=True)
                    # Each actual component trade's notional as a fraction of
                    # starting EUR500 under the prescribed equal allocation.
                    frac=(pp.turnover/pp.equity.shift(1).fillna(10000.)/(2*len(assets)))
                    sizes.extend(frac[frac>1e-10].to_numpy())
            z=np.asarray(sizes);dollar=z*usd
            capital.append(dict(eur=500,usd_per_eur_assumption=fx,minimum_notional_usd_assumption=minimum,executions=len(z),fraction_below_min=float(np.mean(dollar<minimum)),capital_eur_for_99pct_orders=float(minimum/np.quantile(z,.01)/fx),capital_eur_for_all_observed_orders=float(minimum/z.min()/fx),status='SCENARIO_ONLY; quantity steps, split reversal fills, prices at execution and actual venue filters not verified'))
    pd.DataFrame(capital).to_csv(out/'capital_scenarios.csv',index=False)
    (docs/'PHASE4_CAPITAL_FEASIBILITY.md').write_text('# EUR500 operational feasibility\n\nNo deployment feasibility claim. Exact exchange/account minimum notionals and quantity steps have not been established without using current market endpoints. Candle volume does not establish spread or capacity. The table gives reproducible lower-bound scenarios for the frozen allocation; ignoring lot rounding is optimistic. Reversal turnover can combine an exit and entry, so these figures are optimistic bounds, not a complete order-validity simulation. FX is a scenario, not a2026 price observation.\n\n'+table(pd.DataFrame(capital))+'\nMinimum practical capital: UNVERIFIED. The99% execution figure is an indicative threshold allowing1% order omissions, which would itself change the strategy and is not adopted. The all-orders figure is a lower bound before lot rounding; no allocation is distorted to fit EUR500.\n')
    # Matched-horizon discovery comparisons and price-only crypto benchmark.
    compare=[]
    for sym in ['BTCUSDT','ETHUSDT']:
        rr=panel(names=[sym])[sym];compare.append(dict(benchmark=sym+' E040 corrected2022-24',**stats(rr)))
    br=panel(names=['BTCUSDT','ETHUSDT']).mean(1);compare.append(dict(benchmark='BTC/ETH E040 50/50',**stats(br)))
    compare.append(dict(benchmark='replication underlying price-only equal weight (no funding or fees)',**stats(market)))
    pd.DataFrame(compare).to_csv(out/'discovery_comparisons.csv',index=False)
    score=sm[['asset','history_start','history_end','sharpe','alpha','asset_beta','max_dd','trades','top5_trade_positive_pnl_share']].copy()
    for comp in ['trend','breakout']:score[comp+'_sharpe']=score.asset.map(selected[selected.component==comp].set_index('asset').sharpe)
    score['conservative_stress_sharpe']=score.asset.map(M[(M.component=='equal')&(M.case=='asset_conservative')].set_index('asset').sharpe)
    score['classification']=np.where(score.sharpe>0,'positive net risk-adjusted sign','negative/nonpositive sign')
    (docs/'PHASE4_SCOREBOARD.md').write_text('# Frozen replication scoreboard\n\n'+table(score)+'\n## Portfolios\n\n'+table(P)+'\n## Matched-horizon discovery comparisons\n\n'+table(pd.DataFrame(compare)))
    # Charts retain all12 names, including negative results.
    def save(name):plt.tight_layout();plt.savefig(charts/(name+'.png'),bbox_inches='tight');plt.close()
    (1+primary).cumprod().plot(figsize=(11,6),logy=True);plt.ylabel('Net wealth, initial1 (log)');plt.title('Frozen E040: all replication assets');save('net_equity_by_asset')
    fig,axes=plt.subplots(3,4,figsize=(14,9),sharex=True)
    for ax,sym in zip(axes.flat,assets):
        ax.plot(DAYS,(1+primary[sym]).cumprod(),label='E040 net');ax.plot(DAYS,(1+B[sym]).cumprod(),label='Underlying price');ax.set_title(sym);ax.tick_params(axis='x',rotation=45)
    axes.flat[0].legend(fontsize=7);save('strategy_vs_buyhold')
    for field,title in [('sharpe','Net Sharpe'),('alpha','Annual factor intercept'),('max_dd','Maximum drawdown')]:
        z=sm.set_index('asset')[field].reindex(assets);z.plot.bar(figsize=(10,4),color=np.where(z>=0,'#278d78','#b54a4a'));plt.axhline(0,color='black',lw=.6);plt.title(title);save(field+'_distribution')
    def heat(C,title,name):
        fig,ax=plt.subplots(figsize=(8,7));im=ax.imshow(C,vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks(range(len(C)),C.columns,rotation=90);ax.set_yticks(range(len(C)),C.index);fig.colorbar(im,ax=ax,shrink=.8);ax.set_title(title);save(name)
    heat(primary.corr(),'Strategy return correlation','strategy_correlation');heat(B[assets].corr(),'Underlying return correlation','asset_correlation')
    (1+ports[[key,'equal__inverse_vol','equal__risk_parity','equal__equal__cluster_cap']]).cumprod().plot(figsize=(11,5));plt.title('Predefined portfolios, net of allocation-cost estimates');save('portfolio_equity')
    eq=(1+ports[[key,'equal__inverse_vol','equal__equal__cluster_cap']]).cumprod();dd=eq/eq.cummax().clip(lower=1)-1;dd.plot(figsize=(11,4));plt.title('Portfolio drawdown');save('portfolio_drawdown')
    roll=primary_port.rolling(180).mean()/primary_port.rolling(180).std()*np.sqrt(365);roll.plot(figsize=(11,4));plt.axhline(0,color='black',lw=.6);plt.title('Primary portfolio: rolling180-day Sharpe');save('rolling_sharpe')
    beta=primary_port.rolling(180).cov(B.BTCUSDT)/B.BTCUSDT.rolling(180).var();beta.plot(figsize=(11,4));plt.title('Primary portfolio: rolling180-day BTC beta');save('rolling_beta')
    pd.DataFrame({'gross':panel(col='gross').mean(1),'net':panel(col='net').mean(1)}).plot(figsize=(11,4));plt.title('Primary allocation: average daily gross/net exposure');save('exposure')
    yrs=primary.groupby(primary.index.year).apply(lambda z:(1+z).prod()-1).T
    fig,ax=plt.subplots(figsize=(7,7));im=ax.imshow(yrs,cmap='RdBu',aspect='auto');ax.set_xticks(range(3),yrs.columns);ax.set_yticks(range(12),yrs.index)
    for i in range(12):
        for j in range(3):ax.text(j,i,f'{yrs.iloc[i,j]:.0%}',ha='center',va='center',fontsize=8)
    fig.colorbar(im,ax=ax);ax.set_title('Calendar-year net returns, all names');save('yearly_return_heatmap')
    contrib.sum().reindex(assets).plot.bar(figsize=(10,4));plt.ylabel('USDT per10,000 initial portfolio capital');plt.title('Net strategy contribution by asset, before allocation-transfer costs');save('contribution_by_asset')
    pt.groupby('component').pnl.sum().plot.bar(figsize=(6,4),rot=0);plt.title('Portfolio contribution by component, net sleeve P&L');save('contribution_by_component')
    fm='# Phase4 factor analysis\n\nDaily net returns regressed on underlying return, BTC, equal-weight replication market, lagged30-day BTC volatility and lagged200-day BTC trend sign. HAC14-day95% intervals. The market includes the tested name; common factors are correlated and coefficients can be unstable. Volatility and trend are state controls, not necessarily tradable factor portfolios. The intercept is conditional and depends on this specification. No claim of causal alpha. OLS residual Sharpe is approximately zero by construction; factor-adjusted Sharpe retains the fitted intercept. The asset-only regression is reported alongside the richer model.\n\n'+table(F)+'\n## Cross-asset inference\n\n'+json.dumps(meta,indent=2)+'\n\nCommon dates are resampled together and regressions are refitted within each resample. Asset-only bootstrap is descriptive because names are dependent. Random-effects pooling is omitted because independent-effect assumptions are inappropriate. Component analyses are supporting evidence; no unadjusted component significance claim is used for promotion.\n'
    (docs/'PHASE4_FACTOR_ANALYSIS.md').write_text(fm)
    (docs/'PHASE4_CONCENTRATION_AUDIT.md').write_text('# Concentration audit\n\nTop-trade shares use net dollar P&L, not sums of gross percentage returns. Combined sleeves are scaled by actual daily portfolio capital. All allocation-transfer costs are subtracted from the positive-trade denominator for a conservative portfolio top5 bound. Best-year removal drops that calendar year. Single-asset best-trade interval deletion is a coarse adverse diagnostic because other concurrent component trades are also removed; exact portfolio dollar-contribution deletion is reported separately. None changes the frozen strategy.\n\n'+table(sm[['asset','top1_trade_positive_pnl_share','top5_trade_positive_pnl_share','top10_trade_positive_pnl_share','top_month_positive_pnl_share','top_quarter_positive_pnl_share','top_year_positive_pnl_share']])+'\n\nPrimary portfolio diagnostics:\n\n'+json.dumps(concentrations[key],indent=2)+'\n\nFull per-asset/portfolio diagnostics: '+str(out/'concentration.json')+'\n')
    mcrows=[]
    for name,v in mc.items():
        for mode,z in v.items():mcrows.append(dict(unit=name,method=mode,**{k:a for k,a in z.items() if k!='note'}))
    (docs/'PHASE4_MONTE_CARLO.md').write_text('# Conditional sequence and drawdown stress\n\n2,000 resamples per method, seed20260909. Common14/60-day blocks within each return series, trade resampling where meaningful, and permutation of the full return sequence. These are conditional resampling frequencies, not calibrated future event probabilities. Equity-zero is an absorbing accounting floor; exact exchange liquidation requires maintenance/mark rules and is not estimated. Trade resampling does not recreate stateful risk sizing. Portfolio trade contributions overlap and are not treated as independent trades.\n\n'+table(pd.DataFrame(mcrows)))
    component_summary=selected[selected.component.isin(['trend','breakout'])].groupby('component').agg(median_sharpe=('sharpe','median'),positive_fraction=('total_net_return',lambda x:(x>0).mean()),median_alpha=('alpha','median'))
    limitations=['Same2022-2024 crypto regime across all assets;12 names are not12 independent time histories.','Historical2021 liquidity cohort avoids current-survivor selection, but archive coverage is not guaranteed exhaustive. The universe was previously used for other signal research.','The primary window is three years;2021 is excluded from performance and cannot explain the primary result. No new regime is manufactured.','Funding is now complete where audited but settlement marks remain hourly-open proxies; missing marks use disclosed trade-open proxies. Adverse funding stress is reported.','Open prices are execution proxies. Current spreads, lot rounding, minimum notionals and liquidation tiers are not fully verified; EUR500 feasibility is not established.','Targets preserve the original sizing; drift above1x can occur, so this is not hard-capped unlevered exposure.','Strategy-return sleeve combinations require external capital transfers; estimated costs are deducted for portfolio diagnostics.','BTC/ETH are shown solely as discovery comparators and never enter replication sign statistics.']
    red='# Phase4 red-team report\n\nVerdict: '+verdict+'. Decision: '+decision+'.\n\n'+''.join('- '+x+'\n' for x in limitations)+'\n## Direct attacks\n\nShared beta/bull bias: factor regressions and2022 bear results saved.\nOne2021 event: absent from primary performance by design.\nOne trade/year: concentration and removal diagnostics saved; no exclusions adopted.\nAsset-selection bias: universe hashed before E044, all12 retained including MATIC after notice-based exit.\nFunding omission: archive rates, jitter, mark substitutions and adverse stress saved per asset.\nData contamination: exact original reproduction; approved accounting fix; frozen source/config/universe checked before execution; all acquisition bounds end2024.\n\n## Frozen gate results\n\n'+table(pd.DataFrame([dict(gate=k,passed=bool(v)) for k,v in gates.items()]))+'\n\n## Component evidence\n\n'+table(component_summary.reset_index())+'\n\nNo signal changed after outcomes.\n'
    (docs/'PHASE4_RED_TEAM_REPORT.md').write_text(red)
    (docs/'PHASE4_PREVALIDATION_DECISION.md').write_text('# Prevalidation decision\n\n**'+decision+'**\n\nClassification: '+verdict+'.\n\n'+table(pd.DataFrame([dict(gate=k,passed=bool(v)) for k,v in gates.items()]))+'\n\nBased only on the frozen rules and2022-2024 replication evidence.2025 remains LOCKED;2026 UNTOUCHED. If every gate passes, a separate final freeze and explicit code authorization must precede any2025 access; this report itself does not bypass the firewall.\n')
    summary['limitations']=limitations;summary['component_summary']=component_summary.reset_index().to_dict('records');summary['source_replication']=source.name;summary['experiment_id']=out.name;summary['source_hashes']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted((ROOT/'research').glob('*.py'))};summary['frozen_hashes']=json.loads((ROOT/'PHASE4_FREEZE_HASHES.json').read_text());summary['universe_hash']=(ROOT/'PHASE4_UNIVERSE.sha256').read_text().strip()
    def serial(x):return x.item() if hasattr(x,'item') else str(x)
    (out/'results.json').write_text(json.dumps(summary,indent=2,default=serial))
    conclusion='# Phase4 conclusion\n\n**'+verdict+' - '+decision+'**\n\nThe exact E040 signals were reused, with user-approved accounting corrections tested before freeze.12 historically preregistered assets were evaluated over2022-2024, including later contract termination.\n\n'+f'Positive net assets: {positive:.1%}. Median Sharpe: {summary["median_sharpe"]:.3f}. Median factor-adjusted annual intercept: {summary["median_alpha"]:.2%}. Positive alpha fraction: {positive_alpha:.1%}. Median maximum drawdown: {summary["median_drawdown"]:.1%}. Primary portfolio Sharpe: {p.sharpe:.3f}; CAGR: {p.cagr:.2%}; maximum drawdown: {p.max_dd:.1%}.\n\n'+'## Results\n\n'+table(score)+'\n## Predefined stress cases\n\n'+table(stress)+'\n## Scientific limits\n\n'+''.join('- '+x+'\n' for x in limitations)+'\n2025 remains LOCKED.2026 remains UNTOUCHED. No live trading, subscriptions or capital exposure. No parameter changes or losing-asset exclusions.\n\nCharts and full statistical outputs: '+str(out)+'\n'
    (docs/'PHASE4_CONCLUSION.md').write_text(conclusion)
    checkpoint=f'\n\n## Phase4 completed - {out.name}\nClassification: {verdict}; decision: {decision}.12 assets,2022-2024; positive fraction {positive:.1%}; median Sharpe {summary["median_sharpe"]:.3f}; median factor alpha {summary["median_alpha"]:.2%}. Primary portfolio Sharpe {p.sharpe:.3f}, DD {p.max_dd:.1%}. E042 accounting audit, E043 universe/data, E044 one frozen replication hypothesis (cumulative385), E045 diagnostics (no additional hypotheses). Sources/config/universe/data hashes and seeds retained.2025 LOCKED;2026 UNTOUCHED. See PHASE4_CONCLUSION.md.\n'
    # Append bytes: the durable documents contain mixed legacy encodings and must never be re-decoded/re-encoded.
    for name in (['STATUS.md','PLAN.md','EXPERIMENTS.md','RESEARCH_JOURNAL.md'] if root_writes else []):
        with (ROOT/name).open('ab') as fh:fh.write(checkpoint.encode('utf-8'))
    print('FINAL',json.dumps({k:summary[k] for k in ['classification','decision','median_sharpe','median_alpha','positive_asset_fraction','gates']},default=serial),flush=True)
    print('OUTPUT',out,flush=True)

if __name__=='__main__':
    import sys
    _args=[a for a in sys.argv[1:] if not a.startswith('--')]
    main(_args[0] if _args else None,'--no-root' not in sys.argv)
