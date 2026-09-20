"""E047: frozen slow-trend replication on cohort 2 (2021-2024), trend component only. No parameter search.

Loader and cost cases are Phase 4's with a 2021 start, funding archives from 2020-12 and an added
volatility-scaled slippage case (asset-specific constant at the 90th percentile of the lagged 30-day
vol ratio to BTC, capped at 4x, because the frozen ledger takes a scalar cost).
"""
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import freeze_check
from phase4_engine import ledger
from phase4_run import load, read_hourly
from phase4_stats import returns, stats

DAYS = pd.date_range('2021-01-01', '2025-01-01', inclusive='left', freq='D', tz='UTC')
CASES = {'base': .000705, 'stress': .000905, 'slippage_1_5': .001105, 'slippage_2': .001305, 'asset_conservative': .0014, 'delay1': .000905, 'adverse_funding': .000905, 'vol_scaled': None}


def cohort():
    p = ROOT / 'PHASE5_COHORT2.json'
    if hashlib.sha256(p.read_bytes()).hexdigest() != (ROOT / 'PHASE5_COHORT2.sha256').read_text().strip():
        raise RuntimeError('Cohort changed')
    return json.loads(p.read_text(encoding='utf-8'))['assets']


def btc_daily_vol():
    btc, _ = read_hourly('BTCUSDT', 'klines'); close = btc.close.resample('D').last()
    return close.pct_change(fill_method=None).rolling(30).std().shift(1)


def execution_descriptors(sym, b, mark_open):
    """Hourly gap and mark/trade deviation descriptors for 2021-2024 (execution risk, not fills)."""
    h = b.loc[b.index >= DAYS[0]]
    gap = (h.open / h.close.shift(1) - 1).abs().dropna()
    dev = (mark_open.reindex(h.index) / h.open - 1).abs().dropna()
    return dict(gap_p50=float(gap.quantile(.5)), gap_p99=float(gap.quantile(.99)), gap_max=float(gap.max()), gap_over_1pct_share=float((gap > .01).mean()),
                mark_dev_p50=float(dev.quantile(.5)) if len(dev) else None, mark_dev_p99=float(dev.quantile(.99)) if len(dev) else None, mark_dev_obs=int(len(dev)))


def main():
    cfg = freeze_check(); assets = cohort()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'); out = ROOT / 'reports' / ('E047_' + stamp); out.mkdir(exist_ok=False)
    (ROOT / 'reports/PHASE5_ACTIVE_REPLICATION.txt').write_text(out.name)
    starting = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'research').glob('*.py'))}
    bvol = btc_daily_vol(); records = []; all_daily = []; integrity_rows = []
    for sym in assets:
        b, sg, f, adverse, integrity = load(sym, DAYS=DAYS, funding_from=(2020, 12), termination='last_observed'); folder = out / sym; folder.mkdir()
        mark, _ = read_hourly(sym, 'markPriceKlines'); integrity['execution_descriptors'] = execution_descriptors(sym, b, mark.open)
        price = b.valuation_close.resample('D').last().reindex(DAYS).ffill(); bh = price.pct_change(fill_method=None).fillna(0.); bh.to_csv(folder / 'underlying_daily.csv', header=['return'])
        avol = price.pct_change(fill_method=None).rolling(30).std().shift(1); ratio = (avol / bvol.reindex(DAYS)).clip(lower=1, upper=4)
        vol_mult = float(ratio.quantile(.9)) if ratio.notna().any() else 1.; integrity['vol_scaled_slippage_multiplier_p90'] = vol_mult
        (folder / 'data_integrity.json').write_text(json.dumps(integrity, indent=2)); integrity_rows.append({k: v for k, v in integrity.items() if k not in ('sources', 'missing_timestamps')})
        for case, cost in CASES.items():
            if case == 'vol_scaled': cost = .000505 + .0004 * vol_mult
            funding = f.copy()
            if case == 'adverse_funding':
                p0, _ = ledger(b, sg['trend'], cost, 'trend', f, sg['atr']); sign = np.sign(p0.units.shift(1).fillna(0.)); funding = f + sign * adverse
            p, tr = ledger(b, sg['trend'], cost, 'trend', funding, sg['atr'], delay=4 if case == 'delay1' else 0)
            if case == 'adverse_funding':
                actual = np.sign(p.units.shift(1).fillna(0.)); bad = (actual != sign) & (adverse > 0) & (actual != 0)
                if bad.any(): raise RuntimeError('Adverse funding requires online sign replay ' + sym)
            r = returns(p).reindex(DAYS).fillna(0.); daily_eq = p.equity.resample('D').last().shift(1).fillna(10000.)
            G = p.position.abs().resample('D').mean().reindex(DAYS).fillna(0.); N = p.position.resample('D').mean().reindex(DAYS).fillna(0.)
            TO = (p.turnover.resample('D').sum() / daily_eq).reindex(DAYS).fillna(0.); C = (p.cost.resample('D').sum() / daily_eq).reindex(DAYS).fillna(0.)
            LP = (p.long_pnl.resample('D').sum() / daily_eq).reindex(DAYS).fillna(0.); SP = (p.short_pnl.resample('D').sum() / daily_eq).reindex(DAYS).fillna(0.)
            m = stats(r, tr); m.update(asset=sym, case=case, component='trend', cost_per_side=cost, gross_exposure=float(G.mean()), net_exposure=float(N.mean()), max_gross=float(p.position.abs().max()),
                                     annual_turnover=float(TO.sum() * 365 / len(DAYS)), annual_transaction_cost=float(C.sum() * 365 / len(DAYS)), net_funding_usdt=float(p.funding.sum()),
                                     long_pnl_usdt=float(p.long_pnl.sum()), short_pnl_usdt=float(p.short_pnl.sum()), ruin=bool(p.ruin.any()), history_start=str(b.index.min()), history_end=str(b.index.max()), new_name=sym not in json.loads((ROOT / 'PHASE4_UNIVERSE.json').read_text())['assets'])
            records.append(m); p.to_csv(folder / f'trend_{case}_path.csv'); tr.to_csv(folder / f'trend_{case}_trades.csv', index=False)
            all_daily.append(pd.DataFrame(dict(date=DAYS, asset=sym, case=case, ret=r.to_numpy(), gross=G.to_numpy(), net=N.to_numpy(), turnover=TO.to_numpy(), cost=C.to_numpy(), long_ret=LP.to_numpy(), short_ret=SP.to_numpy())))
            print(sym, case, 'Sharpe', round(m['sharpe'], 3), 'DD', round(m['max_dd'], 3), 'ret', round(m['total_net_return'], 3), flush=True)
        pd.DataFrame(records).to_csv(out / 'metrics_partial.csv', index=False)
    pd.DataFrame(records).to_csv(out / 'metrics.csv', index=False); pd.concat(all_daily).to_csv(out / 'daily_panel.csv', index=False)
    pd.DataFrame(integrity_rows).to_csv(out / 'integrity_summary.csv', index=False)
    ending = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'research').glob('*.py'))}
    if starting != ending: raise RuntimeError('Source changed during run; retain outputs as superseded')
    result = dict(experiment_id=out.name, architecture='frozen E040 slow-trend component only', source_hashes=starting, config_sha256=json.loads((ROOT / 'PHASE4_FREEZE_HASHES.json').read_text())['config_sha256'],
                  trend_spec_sha256=(ROOT / 'PHASE5_TREND_FROZEN_SPEC.sha256').read_text().strip(), cohort_sha256=(ROOT / 'PHASE5_COHORT2.sha256').read_text().strip(), seed=20260909, assets=assets, cases=CASES,
                  window=[str(DAYS[0].date()), str(DAYS[-1].date())], classification='PENDING_E048_ANALYSIS', economic_hypotheses=1, cumulative_economic_hypotheses=386, validation_accessed=False, final_test_accessed=False)
    (out / 'results.json').write_text(json.dumps(result, indent=2)); print('FINISHED', out, flush=True)


if __name__ == '__main__':
    main()
