"""Phase 8 E058: event study and slot-portfolio backtest of insider open-market purchases (development only, frozen rules).

Timing: entry at the open of the first trading day strictly after FILING_DATE; exit at the open H trading days later
(H = 126 primary; 63/252 sensitivities); delisting inside the hold -> last vendor price with the Phase 6 haircut rule.
Portfolio: 20 equal slots (10/40 sensitivities), position = equity/slots at entry, skip when full or already held; costs
per PHASE8_COST_RULES.md; daily open-to-open accounting; monthly returns from the first open of each month.
Benchmarks: EW Tier 2 eligible universe (daily EW of members at the latest month-end, monthly from the E051 engine for
the gates) and SPY. Usage (from research/): PYTHONUTF8=1 python phase8_insider_backtest.py
"""
from datetime import datetime, timezone
import json

import numpy as np
import pandas as pd
from scipy import stats as sps
import statsmodels.api as sm

import phase6_eodhd_panel as pnl
import phase6_stock_universe as su
import phase6_stock_engine as se
import phase6_e051_run as run
from phase6_factor_screen import hac_mean, hac_alpha, sharpe, max_drawdown
from phase6_lock import ROOT, assert_development

DERIVED = ROOT / 'data/derived/phase8'
COSTS = {'MANUAL_USD': dict(buy=0.0005, sell=0.00053, buy_far=0.0010, sell_far=0.00103), 'AUTOMATED': dict(buy=0.0020, sell=0.00203, buy_far=0.0025, sell_far=0.00253),
         'STRESS': dict(buy=0.0030, sell=0.0031, buy_far=0.0045, sell_far=0.0046)}
FAR_RANK = 500
HORIZONS = (5, 21, 63, 126, 252)
CELLS = {'C1_ANY': lambda e: pd.Series(True, index=e.index), 'C2_CLUSTER': lambda e: e['cluster'], 'C3_OPPORTUNISTIC': lambda e: e['opportunistic'],
         'C4_OFFICER': lambda e: e['officer'], 'C5_DIRECTOR_ONLY': lambda e: e['director_only']}
WINDOWS = {'w2009_2012': ('2009-01-01', '2012-12-31'), 'w2013_2017': ('2013-01-01', '2017-12-31'), 'w2009_2017': ('2009-01-01', '2017-12-31')}
ENTRY_START, ENTRY_END = pd.Timestamp('2009-01-02'), pd.Timestamp('2017-12-28')
SEED = 20260912


def load_universe():
    close = pnl.load_panel('close'); open_ = pnl.load_panel('open'); adj = pnl.load_panel('adj_close'); vol = pnl.load_panel('volume'); sf = pnl.load_panel('split_factor')
    for p in (close, open_, adj, vol, sf):
        assert_development(p.index)
    cal = su.trading_calendar(close)
    close, open_, adj, vol, sf = (x.reindex(cal) for x in (close, open_, adj, vol, sf))
    me = su.month_end_dates(cal); sig = me[:-1]; ex = su.next_open_dates(cal, sig)
    ret, ended = su.holding_returns(open_, close, adj, ex, cal, run.DEV_END, split_factor=sf)
    sig_used = sig[:len(ret)]
    integrity = su.integrity_panels(close, adj, sf, sig_used)
    feats = su.features_at(sig_used, close, adj, vol, sf, integrity=integrity)
    membership = su.constituent_membership(sig_used)
    E, R, P = [], [], []
    for t in sig_used:
        ok, rk = su.eligibility(feats[t]); E.append(ok.rename(t)); R.append(rk.rename(t))
        okp, _ = su.eligibility(feats[t], membership=membership.loc[t] if t in membership.index else None, liquidity_rank=False)
        if t < su.PIT_FIRST_SIGNAL:
            okp[:] = False
        P.append(okp.rename(t))
    elig = pd.DataFrame(E).reindex(columns=close.columns).fillna(False).astype(bool)
    rank = pd.DataFrame(R).reindex(columns=close.columns)
    pit = pd.DataFrame(P).reindex(columns=close.columns).fillna(False).astype(bool)
    return dict(cal=cal, open=open_, close=close, adj=adj, sf=sf, sig=sig_used, ex=ex, ret=ret, ended=ended, elig=elig, rank=rank, pit=pit)


def prepare_events(U):
    ev = pd.read_parquet(DERIVED / 'events.parquet')
    cal = U['cal']
    pos = cal.searchsorted(ev['FILING_DATE'].to_numpy(), side='right')
    ev = ev[pos < len(cal)].copy(); pos = pos[pos < len(cal)]
    ev['entry_idx'] = pos; ev['entry'] = cal[pos]
    ev = ev[(ev['entry'] >= ENTRY_START) & (ev['entry'] <= ENTRY_END)]
    # eligibility at the last month-end strictly before entry
    sig = U['sig']
    sidx = sig.searchsorted(ev['entry'].to_numpy(), side='left') - 1
    ev = ev[sidx >= 0].copy(); sidx = sidx[sidx >= 0]
    ev['sig_date'] = sig[sidx]
    el = U['elig']; rk = U['rank']; pit = U['pit']
    ev['eligible'] = [bool(el.at[t, c]) if c in el.columns else False for t, c in zip(ev['sig_date'], ev['code'])]
    ev['rank'] = [float(rk.at[t, c]) if c in rk.columns else np.nan for t, c in zip(ev['sig_date'], ev['code'])]
    ev['pit'] = [bool(pit.at[t, c]) if c in pit.columns else False for t, c in zip(ev['sig_date'], ev['code'])]
    return ev


def daily_benchmarks(U):
    ao = U['open'] * U['adj'] / U['close']
    r = ao.pct_change()
    frames = run.load_etf_frames(); spy = frames['SPY']
    spy_ao = (spy['open'] * spy['adj_close'] / spy['close']).reindex(U['cal'])
    return ao, r, spy_ao, None


def bench_bh(sel, ao_np, cols_index, elig, cal, spy_ao_np, h):
    """Buy-and-hold benchmark returns over each event's window: EW mean of the members eligible at the event's signal
    date (names without both prices are dropped) and SPY."""
    ew = np.full(len(sel), np.nan); sp = np.full(len(sel), np.nan)
    n = len(cal)
    member_cache = {}
    for k, (ei, t) in enumerate(zip(sel['entry_idx'], sel['sig_date'])):
        xi = min(ei + h, n - 1)
        if t not in member_cache:
            member_cache[t] = np.where(elig.loc[t].reindex(cols_index).fillna(False).to_numpy())[0]
        m = member_cache[t]
        a, b = ao_np[ei, m], ao_np[xi, m]
        ok = np.isfinite(a) & np.isfinite(b) & (a > 0)
        if ok.sum() >= 50:
            ew[k] = np.mean(b[ok] / a[ok] - 1.0)
        if np.isfinite(spy_ao_np[ei]) and np.isfinite(spy_ao_np[xi]):
            sp[k] = spy_ao_np[xi] / spy_ao_np[ei] - 1.0
    return ew, sp


def event_returns(ev, ao, cal, ended_info, venue, horizon, haircut_mode='base'):
    """Per event: open-to-open return over `horizon` sessions from entry (delisting: last close + haircut, then flat)."""
    out = np.full(len(ev), np.nan); flags = np.zeros(len(ev), dtype=bool)
    n = len(cal)
    for k, (code, ei) in enumerate(zip(ev['code'], ev['entry_idx'])):
        s = ao[code].to_numpy() if code in ao.columns else None
        if s is None or ei >= n or not np.isfinite(s[ei]):
            continue
        xi = min(ei + horizon, n - 1)
        if np.isfinite(s[xi]):
            out[k] = s[xi] / s[ei] - 1.0
        else:
            seg = s[ei:xi + 1]; ok = np.where(np.isfinite(seg))[0]
            last = ok[-1]
            r = seg[last] / s[ei] - 1.0
            info = ended_info.get(code)
            if info is not None and info['last_idx'] <= xi:
                r = (1 + r) * (1 + su.delisting_haircut(info, venue.get(code), haircut_mode)) - 1
                flags[k] = True
            out[k] = r
    return out, flags


def ended_map(U):
    """Per code: last valid open index, 126-day drop before the last date, last unadjusted close (Phase 6 distress proxy)."""
    ao = U['open'] * U['adj'] / U['close']
    cal = U['cal']; out = {}
    lv = U['adj'].apply(lambda s: s.last_valid_index())
    for code, d in lv.items():
        if d is None or pd.isna(d) or d >= cal[-1]:
            continue
        i = cal.get_loc(d)
        prior = U['adj'][code].iloc[i - 126] if i >= 126 else np.nan
        drop = U['adj'][code].iloc[i] / prior - 1.0 if np.isfinite(prior) and prior > 0 else np.nan
        out[code] = dict(last_idx=i, last=d, drop126=float(drop) if np.isfinite(drop) else None, last_close=float(U['close'][code].iloc[i]) if np.isfinite(U['close'][code].iloc[i]) else None)
    return out


def car_stats(x, months, draws=1000, seed=SEED):
    """Mean with a month-cluster bootstrap CI (events resampled by entry month)."""
    x = np.asarray(x, dtype=float); months = np.asarray(months)
    ok = np.isfinite(x); x, months = x[ok], months[ok]
    if len(x) < 10:
        return dict(n=int(len(x)), mean=np.nan)
    groups = {m: x[months == m] for m in np.unique(months)}
    keys = list(groups); rng = np.random.default_rng(seed)
    means = []
    for _ in range(draws):
        pick = rng.integers(len(keys), size=len(keys))
        means.append(np.concatenate([groups[keys[p]] for p in pick]).mean())
    return dict(n=int(len(x)), mean=float(x.mean()), median=float(np.median(x)), ci=[float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
                t_cluster=float(x.mean() / np.std(means, ddof=1)) if np.std(means, ddof=1) > 0 else np.nan, share_positive=float((x > 0).mean()))


def simulate_slots(ev, ao, cal, ended_info, venue, horizon=126, slots=20, cost_case='MANUAL_USD', delay=0, haircut_mode='base', capital=None):
    """Daily slot portfolio. Returns equity series (indexed by trading day, marked at the open), trade log, skips."""
    c = COSTS[cost_case]; n = len(cal)
    by_day = {}
    for idx, r in ev.sort_values(['entry_idx', 'value'], ascending=[True, False]).iterrows():
        by_day.setdefault(int(r['entry_idx']) + delay, []).append(idx)
    cash = 1.0 if capital is None else float(capital)
    positions = {}   # code -> dict(shares, exit_idx, entry_idx, cost_basis, event)
    equity = np.full(n, np.nan); trades = []; skipped_full = skipped_held = skipped_min = 0; delisted = 0
    arrays = {code: ao[code].to_numpy() for code in ev['code'].unique() if code in ao.columns}
    min_order = None if capital is None else 1.0 * 1.1652   # EUR 1 minimum order in USD
    start = int(ev['entry_idx'].min()) if len(ev) else 0
    for d in range(start, n):
        # mark to open
        val = cash
        for code, p in positions.items():
            px = arrays[code][d]
            if not np.isfinite(px):
                px = p['last_px']
            p['last_px'] = px; val += p['shares'] * px
        equity[d] = val
        # exits: scheduled, or series ended
        for code in list(positions):
            p = positions[code]
            info = ended_info.get(code)
            ended_now = info is not None and d > info['last_idx']
            if d >= p['exit_idx'] or ended_now:
                px = arrays[code][d]
                if ended_now or not np.isfinite(px):
                    px = p['last_px']
                    if ended_now:
                        px = px * (1 + su.delisting_haircut(info, venue.get(code), haircut_mode)); delisted += 1
                far = p['far']
                proceeds = p['shares'] * px * (1 - (c['sell_far'] if far else c['sell']))
                cash += proceeds
                trades.append(dict(code=code, entry_idx=p['entry_idx'], exit_idx=d, pnl=proceeds - p['cost'], notional=p['cost'], event=p['event']))
                del positions[code]
        # entries
        for idx in by_day.get(d, []):
            r = ev.loc[idx]; code = r['code']
            if code not in arrays or not np.isfinite(arrays[code][d]):
                continue
            if code in positions:
                skipped_held += 1; continue
            if len(positions) >= slots:
                skipped_full += 1; continue
            val = cash + sum(p['shares'] * p['last_px'] for p in positions.values())
            notional = min(val / slots, cash)
            if notional <= 0 or (min_order is not None and notional < min_order):
                skipped_min += 1; continue
            far = (not np.isfinite(r['rank'])) or r['rank'] > FAR_RANK
            cost_rate = c['buy_far'] if far else c['buy']
            px = arrays[code][d]
            shares = notional * (1 - cost_rate) / px
            cash -= notional
            positions[code] = dict(shares=shares, exit_idx=d + horizon, entry_idx=d, cost=notional, far=far, last_px=px, event=idx)
    eq = pd.Series(equity, index=cal).dropna()
    return dict(equity=eq, trades=pd.DataFrame(trades), skipped_full=skipped_full, skipped_held=skipped_held, skipped_min=skipped_min, delisted=delisted)


def monthly_from_equity(eq, cal):
    """Return from the first open of month m to the first open of month m+1, labelled by month m (its end date)."""
    first_open = pd.Series(eq.index).groupby(pd.DatetimeIndex(eq.index).to_period('M')).first()
    m = eq.reindex(first_open.values)
    r = (m.shift(-1) / m - 1.0).dropna()
    r.index = pd.DatetimeIndex(r.index).to_period('M').to_timestamp('M')
    assert r.index.is_unique
    return r


def window_stats(net, bench, spy, rf):
    out = {}
    net = net.dropna(); idx = net.index
    ex = (net - bench.reindex(idx)).dropna(); exs = (net - spy.reindex(idx)).dropna()
    per = pd.DatetimeIndex(idx).to_period('M'); rfm = rf.reindex(per).to_numpy()
    for w, (a, b) in WINDOWS.items():
        x = ex[a:b]
        if len(x) < 12:
            continue
        nw = net[a:b]; sw = spy.reindex(idx)[a:b]; rw = rfm[(idx >= a) & (idx <= b)]
        capm = hac_alpha(nw - rw, pd.DataFrame({'m': sw - rw}, index=nw.index))
        yearly = x.groupby(x.index.year).sum()
        out[w] = dict(months=int(len(x)), excess_ann=float(x.mean() * 12), excess_t=hac_mean(x)['t'], excess_spy_ann=float(exs[a:b].mean() * 12),
                      net_cagr=se.ann_stats(nw)['cagr'], bench_cagr=se.ann_stats(bench.reindex(idx)[a:b])['cagr'], spy_cagr=se.ann_stats(sw)['cagr'],
                      net_sharpe=sharpe(nw - rw), spy_sharpe=sharpe(sw - rw), max_dd=max_drawdown(nw), spy_max_dd=max_drawdown(sw),
                      alpha_ann=float(capm['alpha'] * 12), alpha_t=capm['t'], beta=capm['betas'][0], years_positive=int((yearly > 0).sum()), years=int(len(yearly)),
                      yearly_excess={int(k): float(v) for k, v in yearly.items()})
    return out


def gates(ws, ws_auto, trades, months_2013):
    g = ws.get('w2013_2017', {}); e = ws.get('w2009_2012', {}); f = ws.get('w2009_2017', {})
    total_ex = sum(v for v in f.get('yearly_excess', {}).values()) if f else np.nan
    best_year = max(f.get('yearly_excess', {}).values()) if f else np.nan
    tr = trades[trades['entry_idx'].notna()] if len(trades) else trades
    top5 = float(tr['pnl'].nlargest(5).sum() / tr['pnl'].clip(lower=0).sum()) if len(tr) and tr['pnl'].clip(lower=0).sum() > 0 else np.nan
    top_ticker = float(tr.groupby('code')['pnl'].sum().max() / tr['pnl'].clip(lower=0).sum()) if len(tr) and tr['pnl'].clip(lower=0).sum() > 0 else np.nan
    checks = dict(G1_excess=g.get('excess_ann', np.nan) >= 0.03, G2_t=g.get('excess_t', np.nan) >= 2.0, G3_years=g.get('years_positive', 0) >= 4,
                  G4_alpha=g.get('alpha_t', np.nan) >= 1.5, G5_dd=f.get('max_dd', np.nan) >= f.get('spy_max_dd', np.nan) - 0.15,
                  G7_automated=ws_auto.get('w2013_2017', {}).get('excess_ann', np.nan) > 0,
                  G8_concentration=(best_year / total_ex <= 0.5 if total_ex > 0 else False) and (top5 <= 0.25) and (top_ticker <= 0.10),
                  G9_early=e.get('excess_ann', np.nan) >= 0 or (g.get('excess_ann', np.nan) >= 0.03 and g.get('excess_t', np.nan) >= 2.0),
                  G10_sample=months_2013 >= 150)
    return dict(checks={k: bool(v) for k, v in checks.items()}, best_year_share=float(best_year / total_ex) if total_ex else np.nan, top5_share=top5, top_ticker_share=top_ticker)


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
    out_dir = ROOT / 'reports' / f'E058_{stamp}'; out_dir.mkdir(parents=True)
    U = load_universe()
    ev_all = prepare_events(U)
    ao, r_daily, spy_ao, _ = daily_benchmarks(U)
    ao_np = ao.to_numpy(dtype=float); cols_index = ao.columns; spy_ao_np = spy_ao.to_numpy(dtype=float)
    ended_info = ended_map(U); venue = su.load_last_venue()
    cal = U['cal']
    # monthly benchmarks for the gates (E051 engine, with delisting bookings)
    haircut = lambda info, v: su.delisting_haircut(info, v, 'base')
    b = se.equal_weight_benchmark(U['elig'], U['ret'], ended=U['ended'], venue=venue, haircut=haircut)
    bench_m = b['net'][b['n_held'] > 0]; bench_m.index = (pd.DatetimeIndex(bench_m.index).to_period('M') + 1).to_timestamp('M')   # holding-month label
    _, etf_ret, _ = run.etf_monthly(run.load_etf_frames(), ['SPY'], U['sig'], U['ex'])
    spy_m = etf_ret['SPY'].copy(); spy_m.index = (pd.DatetimeIndex(U['sig'][:len(spy_m)]).to_period('M') + 1).to_timestamp('M')
    rf = run.load_ff3()['RF']
    ev = ev_all[ev_all['eligible']].copy()
    meta_counts = dict(events_in_window=int(len(ev_all)), eligible=int(len(ev)), pit_subset=int(ev['pit'].sum()),
                       by_year={int(y): int(len(g)) for y, g in ev.groupby(ev['entry'].dt.year)},
                       cells={k: int(f(ev).sum()) for k, f in CELLS.items()})
    print('events', meta_counts, flush=True)
    # ---- event study (descriptive)
    study = {}
    months = ev['entry'].dt.to_period('M').astype(str).to_numpy()
    for cell, f in CELLS.items():
        sel = ev[f(ev)]
        study[cell] = dict(n=int(len(sel)))
        for h in HORIZONS:
            rs, _ = event_returns(sel, ao, cal, ended_info, venue, h)
            ew_b, spy_b = bench_bh(sel, ao_np, cols_index, U['elig'], cal, spy_ao_np, h)
            ar_ew = rs - ew_b; ar_spy = rs - spy_b
            m = sel['entry'].dt.to_period('M').astype(str).to_numpy()
            study[cell][f'h{h}'] = dict(raw=car_stats(rs, m), ar_ew=car_stats(ar_ew, m), ar_spy=car_stats(ar_spy, m),
                                        ar_ew_2013=car_stats(ar_ew[sel['entry'].dt.year >= 2013], m[sel['entry'].dt.year >= 2013]),
                                        ar_ew_2009_2012=car_stats(ar_ew[sel['entry'].dt.year <= 2012], m[sel['entry'].dt.year <= 2012]))
        print(cell, {f'h{h}': (round(study[cell][f'h{h}']['ar_ew']['mean'], 4), round(study[cell][f'h{h}']['ar_ew_2013']['mean'], 4)) for h in HORIZONS}, flush=True)
    # diagnostics on C1: timely vs late, size, direct
    diag = {}
    for name, mask in [('timely', ev['timely']), ('late', ~ev['timely']), ('direct', ev['direct']), ('indirect_only', ~ev['direct']), ('pit_sp1500', ev['pit'])]:
        sel = ev[mask]
        rs, _ = event_returns(sel, ao, cal, ended_info, venue, 126)
        bb, _ = bench_bh(sel, ao_np, cols_index, U['elig'], cal, spy_ao_np, 126)
        diag[name] = car_stats(rs - bb, sel['entry'].dt.to_period('M').astype(str).to_numpy())
    med_val = ev['value'].rolling(1).median()
    ev['value_rank12'] = ev.groupby(ev['entry'].dt.to_period('12M'))['value'].transform(lambda x: x.rank(pct=True))
    for name, mask in [('value_top_half', ev['value_rank12'] >= 0.5), ('value_bottom_half', ev['value_rank12'] < 0.5)]:
        sel = ev[mask]; rs, _ = event_returns(sel, ao, cal, ended_info, venue, 126)
        bb, _ = bench_bh(sel, ao_np, cols_index, U['elig'], cal, spy_ao_np, 126)
        diag[name] = car_stats(rs - bb, sel['entry'].dt.to_period('M').astype(str).to_numpy())
    # ---- portfolios
    rows, results, monthly_out = [], {}, {}
    variants = [('primary', dict(horizon=126, slots=20, delay=0, haircut_mode='base')), ('h63', dict(horizon=63, slots=20, delay=0, haircut_mode='base')),
                ('h252', dict(horizon=252, slots=20, delay=0, haircut_mode='base')), ('slots10', dict(horizon=126, slots=10, delay=0, haircut_mode='base')),
                ('slots40', dict(horizon=126, slots=40, delay=0, haircut_mode='base')), ('delay1', dict(horizon=126, slots=20, delay=1, haircut_mode='base')),
                ('all100', dict(horizon=126, slots=20, delay=0, haircut_mode='all100')), ('all30', dict(horizon=126, slots=20, delay=0, haircut_mode='all30'))]
    for cell, f in CELLS.items():
        sel = ev[f(ev)]
        res = dict(n_events=int(len(sel)), n_2013=int((sel['entry'].dt.year >= 2013).sum()))
        for vname, kw in variants:
            for cc in COSTS:
                if vname != 'primary' and cc != 'MANUAL_USD':
                    continue
                sim = simulate_slots(sel, ao, cal, ended_info, venue, cost_case=cc, **kw)
                m = monthly_from_equity(sim['equity'], cal)
                ws = window_stats(m, bench_m, spy_m, rf)
                tr = sim['trades']
                to = float(tr['notional'].sum() / sim['equity'].reindex(cal).ffill().dropna().mean() / (len(m) / 12)) if len(tr) and len(m) else np.nan
                key = f'{vname}|{cc}'
                res[key] = dict(windows=ws, turnover_oneway_yr=to, n_trades=int(len(tr)), skipped_full=sim['skipped_full'], skipped_held=sim['skipped_held'], delisted=sim['delisted'],
                                avg_positions=float((tr['exit_idx'] - tr['entry_idx']).sum() / max(1, len(sim['equity']))) if len(tr) else 0.0)
                if key == 'primary|MANUAL_USD':
                    res['trades'] = tr; monthly_out[cell] = m
                for w, v in ws.items():
                    rows.append(dict(cell=cell, variant=vname, cost=cc, window=w, **{k: vv for k, vv in v.items() if k != 'yearly_excess'}, turnover=to, n_trades=int(len(tr))))
        prim = res['primary|MANUAL_USD']; auto = res['primary|AUTOMATED']
        res['gates'] = gates(prim['windows'], auto['windows'], res['trades'], res['n_2013'])
        w = prim['windows'].get('w2013_2017', {}); e9 = prim['windows'].get('w2009_2012', {})
        print(f"{cell:17} n {len(sel):5} | 2009-12 excess {e9.get('excess_ann', np.nan)*100:6.2f}% t {e9.get('excess_t', np.nan):5.2f} | 2013-17 excess {w.get('excess_ann', np.nan)*100:6.2f}% t {w.get('excess_t', np.nan):5.2f} yrs+ {w.get('years_positive', 0)}/5 "
              f"| net CAGR {w.get('net_cagr', np.nan)*100:5.1f} vs EW {w.get('bench_cagr', np.nan)*100:5.1f} vs SPY {w.get('spy_cagr', np.nan)*100:5.1f} | alpha t {w.get('alpha_t', np.nan):5.2f} | DD {prim['windows'].get('w2009_2017', {}).get('max_dd', np.nan)*100:5.0f} | to {prim['turnover_oneway_yr']:.2f} | avg pos {prim['avg_positions']:.1f} | skipped full {prim['skipped_full']} held {prim['skipped_held']} | AUTO 2013-17 {auto['windows'].get('w2013_2017', {}).get('excess_ann', np.nan)*100:6.2f}% | gates fail {[k for k, v in res['gates']['checks'].items() if not v]}", flush=True)
        results[cell] = {k: v for k, v in res.items() if k != 'trades'}
        res['trades'].to_csv(out_dir / f'trades_{cell}.csv', index=False)
    # multiplicity across the five cells
    pv = {c: 1 - sps.norm.cdf(results[c]['primary|MANUAL_USD']['windows'].get('w2013_2017', {}).get('excess_t', -9)) for c in CELLS}
    bh = run.bh_fdr(pv, 0.05)
    srs = [results[c]['primary|MANUAL_USD']['windows'].get('w2013_2017', {}).get('net_sharpe', np.nan) for c in CELLS]
    for c in CELLS:
        net = monthly_out[c]['2013-01-01':'2017-12-31']
        results[c]['bh_pass'] = c in bh
        results[c]['dsr'] = dict(zip(('prob', 'sr0_annual'), run.deflated_sharpe(results[c]['primary|MANUAL_USD']['windows']['w2013_2017']['net_sharpe'], len(net), 9, float(np.nanvar(srs, ddof=1)), float(sps.skew(net)), float(sps.kurtosis(net, fisher=False)))))
        results[c]['final_pass'] = bool(all(results[c]['gates']['checks'].values()) and results[c]['bh_pass'] and results[c]['dsr']['prob'] >= 0.90)
        print(c, 'BH', results[c]['bh_pass'], 'DSR', round(results[c]['dsr']['prob'], 3), 'FINAL', results[c]['final_pass'])
    (out_dir / 'results.json').write_text(json.dumps(dict(meta=dict(experiment='E058', stamp=stamp, counts=meta_counts, costs=COSTS, horizons=HORIZONS,
                                                                    prereg_hashes=(ROOT / 'PHASE8_PREREGISTRATION.sha256').read_text(encoding='utf8')),
                                                          event_study=study, diagnostics=diag, portfolios=results), indent=1, default=float), encoding='utf8')
    pd.DataFrame(rows).to_csv(out_dir / 'portfolios.csv', index=False)
    pd.DataFrame(monthly_out).to_csv(out_dir / 'monthly_net.csv'); bench_m.to_csv(out_dir / 'bench_monthly.csv'); spy_m.to_csv(out_dir / 'spy_monthly.csv')
    ev.to_parquet(out_dir / 'events_used.parquet', index=False)
    print(out_dir)


if __name__ == '__main__':
    main()
