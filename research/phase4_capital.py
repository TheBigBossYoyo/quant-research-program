"""EUR 500 feasibility and minimum practical capital for the frozen 12-asset equal-weight E040 portfolio.

Inputs: documented venue filters from the dated exchangeInfo snapshot on disk (rules, not market
observations), the last development close on disk (2024-12-31, labelled scenario price), and the
actual order-notional distribution from the supplemented replication paths. No 2025/2026 data,
no live endpoints, no strategy change. Writes PHASE4_CAPITAL_FEASIBILITY.md and
reports/<E045>/capital_feasibility.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import universe
from phase4_run import read_hourly

SNAPSHOT = ROOT / 'data/metadata/futures_exchangeInfo_20260908T094615.json'
FX = {'EUR->USDT 0.9': .9, 'EUR->USDT 1.0': 1., 'EUR->USDT 1.1': 1.1}
GRANULARITY = {'lot <= 10% of order (rounding error <= 5%)': .10, 'lot <= 25% of order (rounding error <= 12.5%)': .25}


def filters():
    info = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    out = {}
    for s in info['symbols']:
        f = {x['filterType']: x for x in s['filters']}
        out[s['symbol']] = dict(status=s.get('status'), step=float(f['LOT_SIZE']['stepSize']), min_qty=float(f['LOT_SIZE']['minQty']),
                                min_notional=float(f['MIN_NOTIONAL']['notional']), tick=float(f['PRICE_FILTER']['tickSize']))
    return out, pd.Timestamp(int(info['serverTime']), unit='ms', tz='UTC')


def order_fractions(source, sym, comp):
    p = pd.read_csv(source / sym / f'{comp}_stress_path.csv', index_col=0, parse_dates=True)
    f = p.turnover / p.equity.shift(1).fillna(10000.)
    return f[f > 1e-10]


def main():
    assets = universe()
    source = ROOT / 'reports' / (ROOT / 'reports/PHASE4_ACTIVE_REPLICATION.txt').read_text().strip()
    analysis = ROOT / 'reports' / (ROOT / 'reports/PHASE4_ACTIVE_ANALYSIS.txt').read_text().strip()
    flt, snap_time = filters()
    sleeves = 2 * len(assets)
    rows = []; fractions = {}
    for sym in assets:
        d, _ = read_hourly(sym, 'klines'); last = d[d.index < pd.Timestamp('2025-01-01', tz='UTC')]
        price = float(last.close.iloc[-1]); price_time = str(last.index[-1])
        fr = {c: order_fractions(source, sym, c) for c in ['trend', 'breakout']}; fractions[sym] = fr
        v = flt.get(sym)
        row = dict(asset=sym, listed_in_snapshot=v is not None, status=v['status'] if v else 'ABSENT (contract terminated)',
                   step=v['step'] if v else None, min_notional=v['min_notional'] if v else None, scenario_price=price, scenario_price_time=price_time,
                   lot_value_usdt=v['step'] * price if v else None, trend_median_order_fraction=float(fr['trend'].median()), trend_p05_order_fraction=float(fr['trend'].quantile(.05)),
                   breakout_median_order_fraction=float(fr['breakout'].median()), trend_orders=int(len(fr['trend'])), breakout_orders=int(len(fr['breakout'])))
        rows.append(row)
    R = pd.DataFrame(rows)
    # Feasibility at EUR 500 and minimum capital: sleeve equity = capital / 24; an order is placeable if its
    # notional >= min_notional and representable if the lot value is a small fraction of the order notional.
    scen = []
    for fxname, fx in FX.items():
        sleeve = 500 * fx / sleeves
        for r in rows:
            if not r['listed_in_snapshot']:
                continue
            for comp in ['trend', 'breakout']:
                f = fractions[r['asset']][comp] * sleeve
                below_min = float((f < r['min_notional']).mean()); below_lot = float((f < r['lot_value_usdt']).mean())
                scen.append(dict(fx=fxname, asset=r['asset'], component=comp, sleeve_usdt=sleeve, median_order_usdt=float(f.median()),
                                 share_below_min_notional=below_min, share_below_one_lot=below_lot))
    S = pd.DataFrame(scen)
    minimum = []
    for gname, g in GRANULARITY.items():
        req = []
        for r in rows:
            if not r['listed_in_snapshot']:
                continue
            for comp, frac in [('trend', r['trend_p05_order_fraction']), ('breakout', r['trend_p05_order_fraction'] if False else None)]:
                if comp == 'breakout':
                    frac = float(fractions[r['asset']]['breakout'].quantile(.05))
                need = max(r['min_notional'] / frac, r['lot_value_usdt'] / (frac * g))
                req.append(dict(granularity=gname, asset=r['asset'], component=comp, required_sleeve_usdt=need, binding='lot granularity' if r['lot_value_usdt'] / (frac * g) >= r['min_notional'] / frac else 'minimum notional'))
        Q = pd.DataFrame(req); worst = Q.sort_values('required_sleeve_usdt').iloc[-1]
        minimum.append(dict(granularity=gname, minimum_capital_usdt=float(sleeves * Q.required_sleeve_usdt.max()), binding_asset=worst.asset, binding_component=worst.component, binding_reason=worst.binding,
                            minimum_capital_eur_at_fx_1=float(sleeves * Q.required_sleeve_usdt.max()), per_sleeve=Q.to_dict('records')))
    scenario_csv = analysis / 'capital_scenarios.csv'
    out = dict(snapshot=str(SNAPSHOT.relative_to(ROOT)), snapshot_time=str(snap_time), sleeves=sleeves, assets=R.to_dict('records'), eur500=S.to_dict('records'), minimum=minimum,
               status='SCENARIO; exchange filters are documented rules from a dated snapshot; prices are the last development close; no account-specific fees or tiers used')
    (analysis / 'capital_feasibility.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    at1 = S[S.fx == 'EUR->USDT 1.0']
    md = ['# EUR 500 implementation feasibility and minimum practical capital', '',
          f'Venue filters: documented rules from the dated snapshot {SNAPSHOT.name} (server time {snap_time:%Y-%m-%d}); this is rule documentation, not a market observation, and it does not verify account-specific fees, margin tiers or spreads. '
          'Prices used to convert lot sizes to notionals are the last development close on disk (2024-12-31) and are labelled scenario prices; no 2025/2026 data is used. '
          'Order sizes are the actual order notionals of the supplemented replication (stress case) expressed as fractions of the component sleeve equity.', '',
          f'Structure being sized: {len(assets)} assets x 2 components = {sleeves} equal sleeves. At EUR 500 and 1.0 USDT per EUR each sleeve holds {500 / sleeves:.2f} USDT. '
          'The trend sleeve resizes in fractional steps (median order about 0.29 x sleeve, a one-vote change out of seven); the breakout sleeve enters at about 1 x sleeve.', '',
          '## Contract status and filters', '',
          '| Asset | Status in snapshot | Lot step | Lot value (USDT, scenario price) | Min notional (USDT) | Trend median order / sleeve | Breakout median order / sleeve |', '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in rows:
        md.append(f"| {r['asset']} | {r['status']} | {r['step'] if r['step'] is not None else 'n/a'} | {r['lot_value_usdt']:.2f} | {r['min_notional']:.0f} | {r['trend_median_order_fraction']:.3f} | {r['breakout_median_order_fraction']:.3f} |" if r['listed_in_snapshot']
                  else f"| {r['asset']} | {r['status']} | n/a | n/a | n/a | {r['trend_median_order_fraction']:.3f} | {r['breakout_median_order_fraction']:.3f} |")
    md += ['', '## At EUR 500 (1.0 USDT per EUR)', '', '| Asset | Component | Sleeve (USDT) | Median order (USDT) | Share of orders below min notional | Share of orders below one lot |', '| --- | --- | ---: | ---: | ---: | ---: |']
    for _, s in at1.iterrows():
        md.append(f"| {s.asset} | {s.component} | {s.sleeve_usdt:.2f} | {s.median_order_usdt:.2f} | {s.share_below_min_notional:.0%} | {s.share_below_one_lot:.0%} |")
    md += ['', '## Minimum practical capital', '',
           'Required sleeve equity per asset/component is the larger of (min notional / 5th-percentile order fraction) and (lot value / (5th-percentile order fraction x granularity)); portfolio capital is 24 x the largest requirement because the frozen allocation is equal-weight and cannot be distorted to fit a budget.', '',
           '| Granularity rule | Minimum capital (USDT, = EUR at 1.0) | Binding asset | Binding component | Binding constraint |', '| --- | ---: | --- | --- | --- |']
    for m in minimum:
        md.append(f"| {m['granularity']} | {m['minimum_capital_usdt']:,.0f} | {m['binding_asset']} | {m['binding_component']} | {m['binding_reason']} |")
    md += ['', 'Verdict: the diversified 12-asset E040 portfolio is NOT implementable at EUR 500. Most trend-sleeve orders fall below the 5-20 USDT minimum notionals, and whole-lot quantity steps on several contracts (for example one whole coin per lot) make the fractional trend resizing unrepresentable at that size. '
           'MINIMUM PRACTICAL CAPITAL is given above for two rounding-tolerance rules; it is a scenario figure, not a promotion. Two contracts in the frozen universe are not tradeable today in their original form (MATICUSDT terminated 2024-09; FTMUSDT marked SETTLING in the snapshot), which is disclosed, not corrected, because Phase 4 evaluates the 2022-2024 frozen universe.', '',
           f'Supporting scenario table from the analysis run: {scenario_csv.relative_to(ROOT)} (its all-orders column is dominated by microscopic resize orders and is not a capital figure).', '']
    (ROOT / 'PHASE4_CAPITAL_FEASIBILITY.md').write_text('\n'.join(md), encoding='utf-8')
    print('CAPITAL', json.dumps([{k: v for k, v in m.items() if k != 'per_sleeve'} for m in minimum], indent=1))
    print(at1.groupby('component')[['share_below_min_notional', 'share_below_one_lot']].mean())


if __name__ == '__main__':
    main()
