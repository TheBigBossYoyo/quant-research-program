"""Phase 5 cohort 2: objective as-of-2020-12-31 selection and overlap analysis. No strategy returns.

Rules (PHASE5_PLAN.md, fixed before any performance): archived USDT-M perpetuals with daily history,
listed on or before 2020-03-31, >= 90% of calendar days observed since listing within 2020, median daily
quote turnover >= 20m USDT over 2020-07-01..2020-12-31 with >= 180 observed days, active at 2020-12-31,
top 12 by that liquidity excluding BTC/ETH. Later delistings retained.
"""
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from core import ROOT
from phase4_data import freeze_check
from phase4_engine import verified_bytes
from universe import _csv, KLINE_COLS

ASOF = pd.Timestamp('2020-12-31', tz='UTC')
LAST_LISTING = pd.Timestamp('2020-03-31', tz='UTC')
LIQ_START = pd.Timestamp('2020-07-01', tz='UTC')
MIN_LIQ = 20e6
FOLDER = ROOT / 'data/raw/universe/klines_1d'


def daily(years):
    frames = []; sources = []
    for y in years:
        for p in sorted(FOLDER.glob(f'*-1d-{y}-*.zip')):
            raw, sha = verified_bytes(p); d = _csv(raw, KLINE_COLS); d['symbol'] = p.name.split('-1d-')[0]
            d['time'] = pd.to_datetime(d.open_time, unit='ms', utc=True); frames.append(d); sources.append(dict(file=str(p.relative_to(ROOT)), sha256=sha))
    return pd.concat(frames), sources


def select():
    freeze_check()
    d, sources = daily([2020])
    if d.time.max() > ASOF:
        raise ValueError('As-of leak')
    rows = []
    for sym, g in d.groupby('symbol'):
        g = g.sort_values('time'); start = g.time.min(); end = g.time.max(); w = g[g.time >= LIQ_START]
        days_since = (ASOF - start).days + 1; completeness = len(g) / days_since
        liq = float(w.quote_volume.median()) if len(w) else 0.
        quality = (not g.time.duplicated().any()) and (g[['open', 'high', 'low', 'close']] > 0).all().all()
        reasons = []
        if sym in ('BTCUSDT', 'ETHUSDT'): reasons.append('discovery asset')
        if start > LAST_LISTING: reasons.append('listed after 2020-03-31')
        if completeness < .9: reasons.append('history completeness below 90%')
        if end < ASOF: reasons.append('not active at selection')
        if len(w) < 180 or liq < MIN_LIQ: reasons.append('below liquidity/history threshold')
        if not quality: reasons.append('daily quality defect')
        rows.append(dict(asset=sym, eligibility_date=str(ASOF.date()), start=str(start.date()), end_at_selection=str(end.date()), history_days=days_since,
                         completeness=round(completeness, 4), median_quote_volume_2020H2=liq, contract_status_at_selection='active' if end >= ASOF else 'inactive',
                         preeligible=not reasons, reason='; '.join(reasons)))
    r = pd.DataFrame(rows).sort_values(['median_quote_volume_2020H2', 'asset'], ascending=[False, True])
    chosen = r[r.preeligible].head(12).asset.tolist(); r['eligible'] = r.asset.isin(chosen)
    r.loc[r.preeligible & ~r.eligible, 'reason'] = 'outside preregistered top-12 liquidity rank'
    r.loc[r.eligible, 'reason'] = 'selected by 2020H2 historical liquidity; later losses/delistings retained'
    out = ROOT / 'reports/E046_cohort2'; out.mkdir(exist_ok=False); r.to_csv(out / 'eligibility.csv', index=False)
    phase4 = json.loads((ROOT / 'PHASE4_UNIVERSE.json').read_text())['assets']
    overlap = sorted(set(chosen) & set(phase4)); new = [a for a in chosen if a not in phase4]
    # Overlap descriptors from underlying data only (2021-2024 daily returns, no strategy output).
    full, _ = daily([2021, 2022, 2023, 2024])
    px = full.pivot(index='time', columns='symbol', values='close').sort_index(); ret = px.pct_change(fill_method=None)
    names = sorted(set(chosen) | set(phase4) | {'BTCUSDT'}); ret = ret.reindex(columns=[n for n in names if n in ret.columns])
    ew2 = ret[chosen].mean(1); ew1 = ret[phase4].mean(1); ew_new = ret[new].mean(1) if new else ew2 * np.nan
    corr = ret.corr()
    within2 = corr.loc[chosen, chosen].values[~np.eye(len(chosen), dtype=bool)].mean()
    cross = corr.loc[new, phase4].values.mean() if new else float('nan')
    betas = {s: float(np.cov(ret[s].dropna(), ret.BTCUSDT.reindex(ret[s].dropna().index))[0, 1] / ret.BTCUSDT.reindex(ret[s].dropna().index).var()) for s in chosen}
    ov = dict(cohort2=chosen, cohort1=phase4, overlapping=overlap, new_names=new, overlap_count=len(overlap), new_count=len(new), overlap_share=len(overlap) / len(chosen),
              ew_basket_return_correlation_2021_2024=float(ew1.corr(ew2)), ew_basket_correlation_2022_2024=float(ew1[ew1.index.year >= 2022].corr(ew2[ew2.index.year >= 2022])),
              new_names_basket_vs_cohort1_basket_corr=float(ew1.corr(ew_new)) if new else None, mean_pairwise_corr_within_cohort2=float(within2),
              mean_pairwise_corr_new_names_vs_cohort1=float(cross), btc_beta_2021_2024=betas,
              liquidity_rank_cohort2={a: i + 1 for i, a in enumerate(chosen)}, cohort1_liquidity_rank={a: i + 1 for i, a in enumerate(phase4)},
              delisted_before_2025=[a for a in chosen if full[full.symbol == a].time.max() < pd.Timestamp('2024-12-31', tz='UTC')],
              last_observed_day={a: str(full[full.symbol == a].time.max().date()) for a in chosen})
    spec = dict(selection_date=str(ASOF.date()), rules=dict(last_listing='2020-03-31', min_completeness=.9, liquidity_window='2020-07-01..2020-12-31', min_median_quote_volume=MIN_LIQ, max_assets=12, exclude=['BTCUSDT', 'ETHUSDT']),
                assets=chosen, trend_spec_sha256=(ROOT / 'PHASE5_TREND_FROZEN_SPEC.sha256').read_text().strip(), sources=sources, created_utc=datetime.now(timezone.utc).isoformat(), strategy_performance_evaluated=False, overlap=ov)
    p = ROOT / 'PHASE5_COHORT2.json'; p.write_text(json.dumps(spec, indent=2), encoding='utf-8'); sha = hashlib.sha256(p.read_bytes()).hexdigest(); (ROOT / 'PHASE5_COHORT2.sha256').write_text(sha + '\n')
    md = ['# PHASE5_COHORT2_PREREGISTRATION', '', f'Cohort SHA256: {sha}. Eligibility date {ASOF.date()}, one year before the Phase 4 cohort. Rules: listed on or before {LAST_LISTING.date()}; >= 90% of calendar days observed since listing in 2020; median daily quote turnover >= 20m USDT over 2020-07-01..2020-12-31 (>= 180 days); active at selection; top 12 by that liquidity excluding BTC/ETH; later delistings retained. No strategy return has been computed on any of these names for 2021-2024 (cohort-1 overlap names have Phase 4 results for 2022-2024 only).', '',
          '| Asset | Eligibility date | History (start, days, completeness) | Liquidity (median 2020H2 quote volume USDT) | Contract status | Eligible? | Reason |', '| --- | --- | --- | ---: | --- | --- | --- |']
    for x in r.to_dict('records'):
        md.append(f"| {x['asset']} | {x['eligibility_date']} | {x['start']}, {x['history_days']} d, {x['completeness']:.3f} | {x['median_quote_volume_2020H2']:,.0f} | {x['contract_status_at_selection']} | {x['eligible']} | {x['reason']} |")
    md += ['', '## Overlap with the Phase 4 cohort (underlying data only)', '',
           f"Cohort 2: {', '.join(chosen)}.", f"Overlapping with Phase 4: {', '.join(overlap)} ({len(overlap)} of 12, {ov['overlap_share']:.0%}).", f"New names: {', '.join(new)} ({len(new)}).",
           f"Equal-weight underlying basket correlation cohort 1 vs cohort 2, daily 2021-2024: {ov['ew_basket_return_correlation_2021_2024']:.3f}; 2022-2024: {ov['ew_basket_correlation_2022_2024']:.3f}; new-names basket vs cohort-1 basket: {ov['new_names_basket_vs_cohort1_basket_corr']:.3f}.",
           f"Mean pairwise correlation within cohort 2: {within2:.3f}; between new names and cohort-1 names: {cross:.3f}.",
           'BTC betas 2021-2024: ' + ', '.join(f'{k} {v:.2f}' for k, v in betas.items()) + '.',
           f"Contracts whose daily archives end before 2024-12-31: {ov['delisted_before_2025'] or 'none'} (last observed day: {json.dumps({a: ov['last_observed_day'][a] for a in ov['delisted_before_2025']})}).", '',
           'Independence label (fixed now): the cohort adds (a) new names over 2021-2024 and (b) calendar 2021 for every name; it does NOT add an independent macro environment for 2022-2024, and the common crypto factor is shared. Evidence cells and gates: PHASE5_TREND_FROZEN_SPEC.md section 5.', '',
           'Delisting treatment (fixed now): a contract whose hourly archives end before 2024-12-31 exits at the last observed scheduled 4h open with ordinary costs and funding on incoming holdings, and its sleeve stays in cash in the denominator thereafter. Where an official termination notice with a known time is on record, the last scheduled 4h open before that time is used instead, as for MATIC in Phase 4.']
    (ROOT / 'PHASE5_COHORT2_PREREGISTRATION.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('COHORT2', chosen, 'HASH', sha); print('OVERLAP', {k: v for k, v in ov.items() if k not in ('btc_beta_2021_2024', 'liquidity_rank_cohort2', 'cohort1_liquidity_rank', 'last_observed_day')})


if __name__ == '__main__':
    select()
