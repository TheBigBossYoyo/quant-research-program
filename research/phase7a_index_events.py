"""E056: Phase 7A index-event study on the point-in-time S&P 500/400/600 constituent histories (development only).

Events are the StartDate (addition) and EndDate (deletion) of every membership spell effective 2012-04-04..2017-12-31
(no announcement dates exist in the data). Classification:
- migration: the same code leaves one S&P index and joins another within 5 calendar days (promotion if it moves to a
  larger-cap index 600->400->500, demotion otherwise);
- outside addition: addition that is not a migration; discretionary deletion: deletion that is not a migration and whose
  price series keeps trading >= 126 trading days after the effective date; merger/delisting deletion: series ends within
  42 trading days (reported, untradeable).
Abnormal returns: open-to-open returns from the first open after the effective date, minus the equal-weight PIT S&P 1500
universe return (same days), cumulated to +21/+63/+126/+252 trading days.
Calendar-time portfolios (monthly, base cost 20 bps per side, EW of events entered in the last 6 months): P1 discretionary
deletions + demotions (expected positive), P2 outside additions (expected non-positive), P3 promotions (expected non-positive).
Usage (from research/): PYTHONUTF8=1 python phase7a_index_events.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd

import phase6_eodhd as e
import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_stock_engine as se
import phase6_e051_run as run
from phase6_factor_screen import hac_mean
from phase6_lock import ROOT, assert_development

PIT_START, PIT_END = pd.Timestamp('2012-04-04'), pd.Timestamp('2017-12-31')
RANK = {'SML': 0, 'MID': 1, 'GSPC': 2}
HORIZONS = (21, 63, 126, 252)
HOLD_MONTHS = 6
GATE = dict(p1_excess=0.03, p1_t=1.5, p1_years_positive=4, p1_min_events=150)


def load_spells():
    rows = []
    for idx in ('GSPC', 'MID', 'SML'):
        comp = json.loads((e.RAW / 'constituents' / f'comp_{idx}.json').read_text(encoding='utf8'))
        for v in comp['HistoricalTickerComponents'].values():
            s = pd.Timestamp(v['StartDate']) if v.get('StartDate') else pd.NaT
            en = pd.Timestamp(v['EndDate']) if v.get('EndDate') else pd.NaT
            rows.append(dict(code=v['Code'], index=idx, start=s, end=en, is_delisted=int(v.get('IsDelisted') or 0)))
    return pd.DataFrame(rows)


def classify_events(spells, summary):
    """One row per event with type in {promotion, demotion, outside_addition, discretionary_deletion, merger_deletion}."""
    last = dict(zip(summary['code'], pd.to_datetime(summary['last'])))
    ev = []
    adds = spells[(spells['start'] >= PIT_START) & (spells['start'] <= PIT_END)]
    dels = spells[(spells['end'] >= PIT_START) & (spells['end'] <= PIT_END)]
    for _, r in adds.iterrows():
        prior = dels[(dels['code'] == r['code']) & ((dels['end'] - r['start']).abs() <= pd.Timedelta(days=5))]
        if len(prior):
            src = prior.iloc[0]['index']
            ev.append(dict(code=r['code'], date=r['start'], kind='promotion' if RANK[r['index']] > RANK[src] else 'demotion', src=src, dst=r['index']))
        else:
            ev.append(dict(code=r['code'], date=r['start'], kind='outside_addition', src=None, dst=r['index']))
    for _, r in dels.iterrows():
        nxt = adds[(adds['code'] == r['code']) & ((adds['start'] - r['end']).abs() <= pd.Timedelta(days=5))]
        if len(nxt):
            continue  # already recorded as a migration
        l = last.get(r['code'], pd.NaT)
        alive = (not pd.isna(l)) and (l - r['end']).days >= 180
        ended_soon = (pd.isna(l)) or (l - r['end']).days <= 60
        ev.append(dict(code=r['code'], date=r['end'], kind='discretionary_deletion' if alive else ('merger_deletion' if ended_soon else 'deletion_unclear'), src=r['index'], dst=None))
    return pd.DataFrame(ev).sort_values('date').reset_index(drop=True)


def car_table(events, cal, ao, bench_daily):
    """Cumulative abnormal open-to-open returns per event and horizon."""
    out = []
    r_daily = ao.pct_change()
    for _, ev in events.iterrows():
        if ev['code'] not in ao.columns:
            out.append(dict(event=ev.name, **{f'car_{h}': np.nan for h in HORIZONS}, priced=False)); continue
        pos = cal.searchsorted(ev['date'], side='right')   # first open strictly after the effective date
        if pos >= len(cal) - 2:
            continue
        rs = r_daily[ev['code']].iloc[pos + 1:pos + 1 + max(HORIZONS)]   # returns from open pos to open pos+1, ...
        rb = bench_daily.iloc[pos + 1:pos + 1 + max(HORIZONS)]
        rec = dict(event=ev.name, priced=bool(rs.notna().sum() >= 15))
        for h in HORIZONS:
            x, b = rs.iloc[:h], rb.iloc[:h]
            ok = x.notna() & b.notna()
            rec[f'car_{h}'] = float((np.log1p(x[ok]) - np.log1p(b[ok])).sum()) if ok.sum() >= min(h, 15) * 0.8 else np.nan
            rec[f'n_{h}'] = int(ok.sum())
        out.append(rec)
    return pd.DataFrame(out).set_index('event')


def calendar_portfolio(events, sig_used, ret, elig_pit, ended, venue, haircut, cost_case='base'):
    """EW portfolio of events whose date lies in the 6 months before each signal date (name must still be priced)."""
    scores = pd.DataFrame(np.nan, index=sig_used, columns=ret.columns)
    for t in sig_used:
        window = events[(events['date'] <= t) & (events['date'] > t - pd.DateOffset(months=HOLD_MONTHS))]
        codes = [c for c in window['code'].unique() if c in scores.columns]
        scores.loc[t, codes] = 1.0
    eligible = scores.notna()
    out = se.simulate(scores, eligible, ret, n=10 ** 6, ended=ended, venue=venue, haircut=haircut, cost_case=cost_case)
    m = out['monthly']
    return m[m['n_held'] > 0]


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E056_{stamp}'; out_dir.mkdir(parents=True)
    summary = pnl.load_summary()
    spells = load_spells()
    events = classify_events(spells, summary)
    counts = events['kind'].value_counts().to_dict()
    print('events', counts, flush=True)
    close = pnl.load_panel('close'); open_ = pnl.load_panel('open'); adj = pnl.load_panel('adj_close'); vol = pnl.load_panel('volume'); sf = pnl.load_panel('split_factor')
    cal = su.trading_calendar(close)
    close, open_, adj, vol, sf = (x.reindex(cal) for x in (close, open_, adj, vol, sf))
    assert_development(cal)
    me = su.month_end_dates(cal); sig = me[:-1]; ex = su.next_open_dates(cal, sig)
    ret, ended = su.holding_returns(open_, close, adj, ex, cal, run.DEV_END, split_factor=sf)
    sig_used = sig[:len(ret)]
    integrity = su.integrity_panels(close, adj, sf, sig_used)
    feats = su.features_at(sig_used, close, adj, vol, sf, integrity=integrity)
    membership = su.constituent_membership(sig_used)
    E = []
    for t in sig_used:
        ok, _ = su.eligibility(feats[t], membership=membership.loc[t] if t in membership.index else None, liquidity_rank=False)
        if t < su.PIT_FIRST_SIGNAL:
            ok[:] = False
        E.append(ok.rename(t))
    elig_pit = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
    # daily EW PIT benchmark for CARs: members on the latest signal date <= d
    ao = open_ * adj / close
    r_daily = ao.pct_change()
    member_daily = elig_pit.reindex(cal, method='ffill').fillna(False).astype(bool)
    bench_daily = r_daily.where(member_daily).mean(axis=1)
    cars = car_table(events, cal, ao, bench_daily)
    ev = events.join(cars)
    car_summary = {}
    for kind, g in ev.groupby('kind'):
        d = dict(n=int(len(g)), priced=int(g['priced'].sum()))
        for h in HORIZONS:
            x = g[f'car_{h}'].dropna()
            if len(x) >= 10:
                d[f'car_{h}_mean'] = float(x.mean()); d[f'car_{h}_median'] = float(x.median()); d[f'car_{h}_t'] = float(x.mean() / x.std(ddof=1) * np.sqrt(len(x))); d[f'car_{h}_n'] = int(len(x))
        car_summary[kind] = d
        print(kind, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}, flush=True)
    by_year = {kind: g.groupby(g['date'].dt.year)['car_126'].agg(['mean', 'count']).round(4).to_dict('index') for kind, g in ev.groupby('kind')}
    venue = su.load_last_venue()
    haircut = lambda info, v: su.delisting_haircut(info, v, 'base')
    frames = run.load_etf_frames()
    _, etf_ret, _ = run.etf_monthly(frames, ['SPY'], sig_used, ex)
    spy = etf_ret['SPY'].copy(); spy.index = sig_used[:len(spy)]
    rf = run.load_ff3()['RF']
    b = se.equal_weight_benchmark(elig_pit, ret, ended=ended, venue=venue, haircut=haircut)
    bench = b['net'][b['n_held'] > 0]
    ports = {'P1_deletions_demotions': ev[ev['kind'].isin(['discretionary_deletion', 'demotion'])], 'P2_outside_additions': ev[ev['kind'] == 'outside_addition'], 'P3_promotions': ev[ev['kind'] == 'promotion']}
    results = {}
    for name, evs in ports.items():
        res = dict(n_events=int(len(evs)))
        for cc in ('optimistic', 'base', 'stress'):
            m = calendar_portfolio(evs, sig_used, ret, elig_pit, ended, venue, haircut, cc)
            st = run.stats_block(m['net'], bench, spy, rf, 2000)
            st['turnover_oneway_yr'] = float((m['turnover_buy'] + m['turnover_sell']).mean() * 6); st['avg_held'] = float(m['n_held'].mean())
            yr = (m['net'] - bench.reindex(m.index)).groupby(m.index.year).mean() * 12
            st['yearly_excess'] = {int(k): float(v) for k, v in yr.items()}
            res[cc] = st
        bst = res['base']
        res['gate_B'] = dict(excess=bst['excess_ew']['mean'] * 12 >= GATE['p1_excess'], t=bst['excess_ew']['t'] >= GATE['p1_t'],
                             years=sum(1 for v in bst['yearly_excess'].values() if v > 0) >= GATE['p1_years_positive'], events=len(evs) >= GATE['p1_min_events'])
        res['gate_B']['passes'] = all(res['gate_B'].values())
        results[name] = res
        print(f"{name}: events {len(evs)} avg held {bst['avg_held']:.0f} | net CAGR {bst['net']['cagr']*100:.1f} vs EW {bst['bench']['cagr']*100:.1f} vs SPY {bst['spy']['cagr']*100:.1f} | excess {bst['excess_ew']['mean']*1200:.2f}%/yr t {bst['excess_ew']['t']:.2f} | "
              f"DD {bst['net']['max_dd']*100:.0f} | turnover {bst['turnover_oneway_yr']:.1f}x | yearly {{{', '.join(f'{k}:{v*100:.1f}' for k, v in bst['yearly_excess'].items())}}} | gate {res['gate_B']['passes']}", flush=True)
    ev.to_csv(out_dir / 'events.csv', index=False)
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E056', stamp=stamp, counts=counts, horizons=HORIZONS, hold_months=HOLD_MONTHS, gate=GATE),
                                                          car_summary=car_summary, car_by_year=by_year, portfolios=results), indent=1, default=float), encoding='utf8')
    print(out_dir)


if __name__ == '__main__':
    main()
