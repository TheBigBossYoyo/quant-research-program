"""E049: run the CAPITAL_EFFICIENCY_RESEARCH grid (PHASE5_CAPITAL_SPEC.md). New architectures, not E040."""
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import freeze_check
from phase4_run import load, DAYS
from phase4_stats import stats
from phase5_capital_engine import simulate

CAPITALS = [500., 1000., 2500., 5000., None]; BANDS = [0., .10, .25]; SCALARS = [1., .5]; VOLT = [None, .20]; COST = .000905


def main():
    freeze_check(); spec = json.loads((ROOT / 'PHASE5_CAPITAL_UNIVERSE.json').read_text(encoding='utf-8'))
    if hashlib.sha256((ROOT / 'PHASE5_CAPITAL_UNIVERSE.json').read_bytes()).hexdigest() != (ROOT / 'PHASE5_CAPITAL_UNIVERSE.sha256').read_text().strip(): raise RuntimeError('Universe changed')
    info = json.loads((ROOT / 'data/metadata/futures_exchangeInfo_20260908T094615.json').read_text(encoding='utf-8'))
    rules = {s['symbol']: (float({x['filterType']: x for x in s['filters']}['LOT_SIZE']['stepSize']), float({x['filterType']: x for x in s['filters']}['MIN_NOTIONAL']['notional'])) for s in info['symbols']}
    out = ROOT / 'reports' / ('E049_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')); out.mkdir(exist_ok=False); (ROOT / 'reports/PHASE5_ACTIVE_CAPITAL.txt').write_text(out.name)
    names = spec['subsets']['5']; data = {}
    for s in names:
        b, sg, f, adverse, integrity = load(s); data[s] = (b, sg['trend'], f)
    idx = None
    for s in names: idx = data[s][0].index if idx is None else idx.intersection(data[s][0].index)
    frames = {s: data[s][0].reindex(idx) for s in names}; scores = {s: data[s][1].reindex(idx) for s in names}; funding = {s: data[s][2].reindex(idx).fillna(0.) for s in names}
    rows = []; daily = {}
    for n, subset in spec['subsets'].items():
        sub = subset; fr = {s: frames[s] for s in sub}; sc = {s: scores[s] for s in sub}; fu = {s: funding[s] for s in sub}; rl = {s: rules[s] for s in sub}
        for scalar in SCALARS:
            for band in BANDS:
                base = simulate(fr, sc, fu, rl, None, COST, band, scalar); vol_lag = (base['returns'].rolling(30).std() * np.sqrt(365)).shift(1)
                for vt in VOLT:
                    ref = base if vt is None else simulate(fr, sc, fu, rl, None, COST, band, scalar, vol_lag, vt); rref = ref['returns'].reindex(DAYS).fillna(0.); mref = stats(rref)
                    for cap in CAPITALS:
                        res = ref if cap is None else simulate(fr, sc, fu, rl, cap, COST, band, scalar, vol_lag, vt); r = res['returns'].reindex(DAYS).fillna(0.); m = stats(r)
                        te = float((r - rref).std() * np.sqrt(365)); start = 10000. if cap is None else cap
                        m.update(assets=int(n), names=','.join(sub), risk_scalar=scalar, dead_band=band, vol_target=vt if vt is not None else 0., capital=cap if cap is not None else 'unconstrained', annual_turnover=res['turnover'] / start / 3, annual_cost=res['fees'] / start / 3,
                                 skipped_order_fraction=res['skipped'] / res['wanted'] if res['wanted'] else 0., resize_opportunities=res['wanted'], pending_order_hours=res['lag_hours'], mean_weight_error=res['mean_weight_error'], gross_exposure=res['gross'], tracking_error=te, tracking_error_vs_vol=te / mref['volatility'] if mref['volatility'] else np.nan,
                                 sharpe_retention=m['sharpe'] / mref['sharpe'] if mref['sharpe'] else np.nan, unconstrained_sharpe=mref['sharpe'], unconstrained_cagr=mref['cagr'], unconstrained_max_dd=mref['max_dd'], drawdown_difference=m['max_dd'] - mref['max_dd'], ruin=res['ruin'])
                        rows.append(m); daily[f"N{n}_s{scalar}_b{band}_vt{vt or 0}_cap{cap or 'inf'}"] = r
                        print(f"N={n} s={scalar} band={band} vt={vt} cap={cap}: Sharpe {m['sharpe']:.3f} (ref {mref['sharpe']:.3f}) DD {m['max_dd']:.3f} skipped {m['skipped_order_fraction']:.1%} TE {te:.3f}", flush=True)
                pd.DataFrame(rows).to_csv(out / 'capital_results_partial.csv', index=False)
    R = pd.DataFrame(rows); R.to_csv(out / 'capital_results.csv', index=False); R.to_csv(ROOT / 'PHASE5_CAPITAL_RESULTS.csv', index=False); pd.DataFrame(daily).to_csv(out / 'daily_returns.csv')
    result = dict(experiment_id=out.name, label='CAPITAL_EFFICIENCY_RESEARCH', architectures=['pooled-capital score positioning (B1/B2/B3)', 'volatility-target overlay'], universe_sha256=(ROOT / 'PHASE5_CAPITAL_UNIVERSE.sha256').read_text().strip(), spec='PHASE5_CAPITAL_SPEC.md', window=[str(DAYS[0].date()), str(DAYS[-1].date())],
                  cost_per_side=COST, grid=dict(capitals=[c for c in CAPITALS if c] + ['unconstrained'], bands=BANDS, scalars=SCALARS, vol_targets=[v or 0 for v in VOLT]), new_architecture_hypotheses=2, cumulative_hypotheses=388,
                  source_hashes={str(q.relative_to(ROOT)): hashlib.sha256(q.read_bytes()).hexdigest() for q in sorted((ROOT / 'research').glob('*.py'))}, validation_accessed=False, final_test_accessed=False)
    (out / 'results.json').write_text(json.dumps(result, indent=2)); print('FINISHED', out, flush=True)


if __name__ == '__main__':
    main()
