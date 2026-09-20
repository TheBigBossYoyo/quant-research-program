"""Branch B small-capital universe from venue rules and history only (PHASE5_CAPITAL_SPEC.md). No performance input."""
import hashlib
import json

import pandas as pd

from core import ROOT
from phase4_run import read_hourly

SNAPSHOT = ROOT / 'data/metadata/futures_exchangeInfo_20260908T094615.json'


def main():
    info = json.loads(SNAPSHOT.read_text(encoding='utf-8')); rules = {}
    for s in info['symbols']:
        f = {x['filterType']: x for x in s['filters']}
        rules[s['symbol']] = dict(status=s['status'], step=float(f['LOT_SIZE']['stepSize']), min_notional=float(f['MIN_NOTIONAL']['notional']), tick=float(f['PRICE_FILTER']['tickSize']))
    elig = pd.read_csv(ROOT / 'reports/E043_universe/eligibility.csv'); rows = []
    for r in elig.itertuples():
        sym = r.asset; start = pd.Timestamp(r.start); on_disk = (ROOT / 'data/raw/phase4/klines' / f'{sym}-1h-2024-12.zip').exists() or (ROOT / 'data/raw/futures/klines' / f'{sym}-1h-2024-12.zip').exists()
        v = rules.get(sym); reasons = []
        if v is None: reasons.append('absent from rule snapshot')
        elif v['status'] != 'TRADING': reasons.append(f"status {v['status']}")
        if start > pd.Timestamp('2020-12-31', tz='UTC'): reasons.append('listed after 2020-12-31')
        if not on_disk: reasons.append('no complete hourly history on disk')
        lot_value = None; price = None
        if on_disk and v is not None:
            d, _ = read_hourly(sym, 'klines'); price = float(d[d.index < pd.Timestamp('2025-01-01', tz='UTC')].close.iloc[-1]); lot_value = v['step'] * price
            if v['min_notional'] > 20: reasons.append('minimum notional above 20 USDT')
            if lot_value > 5: reasons.append('lot value above 5 USDT')
        rows.append(dict(asset=sym, liquidity_rank_source='Phase 4 as-of-2021-12-31 median daily quote volume', liquidity=float(r.median_quote_volume), listed=str(start.date()), status=v['status'] if v else 'ABSENT', step=v['step'] if v else None,
                         min_notional=v['min_notional'] if v else None, scenario_price_2024_12_31=price, lot_value_usdt=lot_value, hourly_on_disk=on_disk, eligible=not reasons, reason='; '.join(reasons) or 'passes all rules'))
    U = pd.DataFrame(rows).sort_values(['eligible', 'liquidity'], ascending=[False, False]); chosen = U[U.eligible].asset.tolist()
    subsets = {n: chosen[:n] for n in [2, 3, 4, 5]}
    spec = dict(rules='TRADING; min notional <= 20; lot value <= 5 USDT at 2024-12-31 close; listed <= 2020-12-31; hourly history on disk', snapshot=SNAPSHOT.name, eligible_ranked=chosen, subsets=subsets)
    p = ROOT / 'PHASE5_CAPITAL_UNIVERSE.json'; p.write_text(json.dumps(spec, indent=2), encoding='utf-8'); sha = hashlib.sha256(p.read_bytes()).hexdigest(); (ROOT / 'PHASE5_CAPITAL_UNIVERSE.sha256').write_text(sha + '\n')
    phase4 = json.loads((ROOT / 'PHASE4_UNIVERSE.json').read_text())['assets']
    md = ['# PHASE5_CAPITAL_UNIVERSE (Branch B, CAPITAL_EFFICIENCY_RESEARCH)', '', f'Universe SHA256 {sha}. Rules: contract TRADING in the 2026-09-08 rule snapshot; minimum notional <= 20 USDT; lot value <= 5 USDT at the 2024-12-31 close (scenario price); listed on or before 2020-12-31; complete hourly history on disk. Ranked by the Phase 4 as-of-2021-12-31 liquidity table. Subsets are top-N by that rank. No performance input; Phase 4/5 outcomes of the chosen names are disclosed in PHASE5_CAPITAL_FEASIBILITY.md.', '',
          '| Asset | Liquidity (2021H2 median quote volume) | Listed | Status | Lot step | Min notional | Lot value (USDT) | Hourly on disk | Eligible | Reason |', '| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- | --- |']
    for x in U.to_dict('records'):
        md.append(f"| {x['asset']} | {x['liquidity']:,.0f} | {x['listed']} | {x['status']} | {x['step'] if x['step'] is not None else 'n/a'} | {x['min_notional'] if x['min_notional'] is not None else 'n/a'} | {x['lot_value_usdt']:.2f} | {x['hourly_on_disk']} | {x['eligible']} | {x['reason']} |" if x['lot_value_usdt'] is not None else f"| {x['asset']} | {x['liquidity']:,.0f} | {x['listed']} | {x['status']} | n/a | n/a | n/a | {x['hourly_on_disk']} | {x['eligible']} | {x['reason']} |")
    md += ['', 'Eligible, ranked: ' + ', '.join(chosen), '', 'Subsets: ' + '; '.join(f'N={n}: ' + ', '.join(v) for n, v in subsets.items()), '', 'Overlap with the Phase 4 cohort: ' + ', '.join(a for a in chosen if a in phase4) + '. ETH is a discovery asset (Phase 3), not a replication name.']
    (ROOT / 'PHASE5_CAPITAL_UNIVERSE.md').write_text('\n'.join(md) + '\n', encoding='utf-8'); print('CAPITAL_UNIVERSE', chosen, subsets, sha)


if __name__ == '__main__':
    main()
