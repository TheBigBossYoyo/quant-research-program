"""Point-in-time monthly universes and lagged features on the EODHD panel (Phase 6, development only).

Every function here consumes wide daily panels that were returned by phase6_eodhd_panel.load_panel(...)
(lock-enforced) or synthetic panels in tests. Nothing is read from disk in this module except the constituent
JSON (membership dates) and the ticker summary (last venue), neither of which carries prices or returns.

Timing convention (PHASE6_UNIVERSE_CONSTRUCTION.md section 10): signal date t = last trading day of month m
(features use closes up to and including t); orders execute at the open of the first trading day after t;
positions are held to the open of the first trading day after the next signal date.

Universes
- PIT_SP1500 (Tier 1): member of the S&P 500, 400 or 600 on t per HistoricalTickerComponents
  (StartDate <= t < EndDate), from 2012-04-30; plus price/history/data-quality filters (no liquidity rank).
- LIQ1000 (Tier 2, NO_PIT_MEMBERSHIP): all common stocks; history >= 252 priced days before t, unadjusted
  close >= 5, 63-day median dollar volume >= 1m, top 1000 by that median, no missing close in the last 21
  calendar trading days, no zero-volume day in the last 5; start year set by the coverage audit.
"""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

import phase6_eodhd as e
import phase6_eodhd_acquire as acq

MIN_HISTORY_DAYS = 252
MIN_PRICE = 5.0
MIN_DOLLAR_VOLUME = 1.0e6
RANK_CAP = 1000
LIQ_WINDOW = 63
QUALITY_WINDOW = 21
ZERO_VOLUME_WINDOW = 5
MIN_CALENDAR_NAMES = 300
PIT_FIRST_SIGNAL = pd.Timestamp('2012-04-30')
RESID_WINDOW = 36
RESID_MIN_OBS = 24
EXTREME_DAY_UP = 2.0        # I3
EXTREME_DAY_DOWN = -0.75    # I3
EXTREME_WINDOW = 252        # I3
CONSISTENCY_TOL = 0.10      # I4 / I5
CONSISTENCY_MONTHS = 12     # I4


def trading_calendar(close):
    """Days on which at least MIN_CALENDAR_NAMES tickers have a close (removes stray single-ticker dates)."""
    n = close.notna().sum(axis=1)
    return close.index[n >= MIN_CALENDAR_NAMES]


def month_end_dates(calendar):
    """Last calendar day of every month present in `calendar` (the final partial month is kept)."""
    cal = pd.DatetimeIndex(calendar)
    per = pd.Series(cal.to_period('M'))
    is_last = (per.shift(-1) != per).to_numpy()
    return cal[is_last]


def next_open_dates(calendar, signal_dates):
    """First calendar day strictly after each signal date (execution day); NaT if none."""
    cal = pd.DatetimeIndex(calendar)
    pos = cal.searchsorted(pd.DatetimeIndex(signal_dates), side='right')
    return pd.DatetimeIndex([cal[p] if p < len(cal) else pd.NaT for p in pos])


SPELL_TOLERANCE_DAYS = 30
SPELL_CLIP = (pd.Timestamp('2012-04-04'), pd.Timestamp('2017-12-31'))


def drop_uncovered_spells(spells):
    """Audit rule A4: a spell whose EOD series does not cover it (first date > start + 30 days or last date <
    end - 30 days, both clipped to the point-in-time window) is a ticker-reuse mismatch and is excluded."""
    s = pd.read_parquet(e.ROOT / 'data/derived/phase6/eodhd/summary.parquet', columns=['code', 'first', 'last', 'rows'])
    first = dict(zip(s['code'], pd.to_datetime(s['first'])))
    last = dict(zip(s['code'], pd.to_datetime(s['last'])))
    rows = dict(zip(s['code'], s['rows']))
    def covers(code, a, b):
        f, l = first.get(code), last.get(code)
        return rows.get(code, 0) > 0 and f is not None and not pd.isna(f) and f <= a + pd.Timedelta(days=SPELL_TOLERANCE_DAYS)             and l >= b - pd.Timedelta(days=SPELL_TOLERANCE_DAYS)

    keep, codes, stats = [], [], dict(spells=0, covered=0, remapped=0, dropped=0)
    for _, r in spells.iterrows():
        a, b = max(r['start'], SPELL_CLIP[0]), min(r['end'], SPELL_CLIP[1])
        code = r['code']
        if a > b:
            keep.append(True); codes.append(code)
            continue
        stats['spells'] += 1
        if covers(code, a, b):
            stats['covered'] += 1; keep.append(True); codes.append(code)
            continue
        # ticker reuse: the historical member may live under a delisted `_old` variant (mechanical remap, no return used)
        alt = next((code + suf for suf in ('_old', '_old1', '_old2', '_old3') if covers(code + suf, a, b)), None)
        if alt is not None:
            stats['remapped'] += 1; keep.append(True); codes.append(alt)
        else:
            stats['dropped'] += 1; keep.append(False); codes.append(code)
    out = spells.copy()
    out['code'] = codes
    out = out[np.array(keep, dtype=bool)]
    drop_uncovered_spells.last_stats = stats
    return out


def constituent_membership(signal_dates, indices=acq.INDICES, dev_end=None, exclude_uncovered=True):
    """Boolean frame (signal date x code): member of any of the indices on that date."""
    frames = []
    for idx in indices:
        comp = json.loads((e.RAW / 'constituents' / f'comp_{idx}.json').read_text(encoding='utf8'))
        for v in comp['HistoricalTickerComponents'].values():
            # StartDate None = member since before the vendor record begins (initial cohort); EndDate None = still a member
            start = pd.Timestamp(v['StartDate']) if v.get('StartDate') else pd.Timestamp('1900-01-01')
            end = pd.Timestamp(v['EndDate']) if v.get('EndDate') else pd.Timestamp('2262-01-01')
            frames.append((v['Code'], start, end))
    spells = pd.DataFrame(frames, columns=['code', 'start', 'end'])
    spells = spells[spells['start'] < spells['end']]
    if exclude_uncovered:
        spells = drop_uncovered_spells(spells)
    codes = sorted(spells['code'].unique())
    out = pd.DataFrame(False, index=pd.DatetimeIndex(signal_dates), columns=codes)
    for code, g in spells.groupby('code'):
        m = np.zeros(len(out), dtype=bool)
        for _, r in g.iterrows():
            m |= (out.index >= r['start']) & (out.index < r['end'])
        out[code] = m
    return out


def integrity_panels(close, adj_close, split_factor, signal_dates):
    """I3/I4: returns (unclean_daily bool frame, inconsistent_12m bool frame at signal dates)."""
    sp = close / split_factor
    r = sp / sp.shift(1) - 1.0
    extreme = ((r > EXTREME_DAY_UP) | (r < EXTREME_DAY_DOWN)).astype('float32')
    unclean = extreme.rolling(EXTREME_WINDOW, min_periods=1).max() > 0
    me = pd.DatetimeIndex(signal_dates)
    ma, mc = adj_close.reindex(me), sp.reindex(me)
    ra, rc = ma / ma.shift(1) - 1.0, mc / mc.shift(1) - 1.0
    incons = (((1.0 + ra) / (1.0 + rc) - 1.0).abs() > CONSISTENCY_TOL).astype('float32')
    incons12 = incons.rolling(CONSISTENCY_MONTHS, min_periods=1).max() > 0
    return unclean, incons12


def features_at(signal_dates, close, adj_close, volume, split_factor, integrity=None):
    """Lagged, causal features evaluated at each signal date (all use data <= t)."""
    cal = close.index
    dv = (close / split_factor) * volume
    priced = close.notna()
    cum_priced = priced.cumsum()
    if integrity is None:
        integrity = integrity_panels(close, adj_close, split_factor, signal_dates)
    unclean, incons12 = integrity
    rows = {}
    for t in signal_dates:
        i = cal.get_loc(t)
        lo = max(0, i - LIQ_WINDOW + 1)
        med_dv = dv.iloc[lo:i + 1].median(axis=0, skipna=True)
        n_dv = dv.iloc[lo:i + 1].notna().sum(axis=0)
        med_dv = med_dv.where(n_dv >= LIQ_WINDOW)
        hist = cum_priced.iloc[i - 1] if i >= 1 else pd.Series(0, index=close.columns)
        q_lo = max(0, i - QUALITY_WINDOW + 1)
        complete = priced.iloc[q_lo:i + 1].all(axis=0) & (i + 1 >= QUALITY_WINDOW)
        z_lo = max(0, i - ZERO_VOLUME_WINDOW + 1)
        no_zero = (volume.iloc[z_lo:i + 1].fillna(0) > 0).all(axis=0)
        clean = (~unclean.loc[t]) & (~incons12.loc[t].reindex(close.columns).fillna(False).astype(bool))
        rows[t] = pd.DataFrame(dict(price=close.iloc[i], med_dv=med_dv, history=hist, complete=complete, no_zero=no_zero, clean=clean))
    return rows


def eligibility(feat, membership=None, liquidity_rank=True):
    """Apply the preregistered filters to one signal date's feature frame; returns bool Series and rank."""
    ok = (feat['history'] >= MIN_HISTORY_DAYS) & (feat['price'] >= MIN_PRICE) & feat['complete'] & feat['no_zero']
    if 'clean' in feat.columns:
        ok &= feat['clean'].astype(bool)
    if membership is not None:
        ok &= membership.reindex(feat.index).fillna(False).astype(bool)
    rank = feat['med_dv'].where(ok).rank(ascending=False, method='first')
    if liquidity_rank:
        ok &= (feat['med_dv'] >= MIN_DOLLAR_VOLUME) & (rank <= RANK_CAP)
    return ok, rank


def monthly_prices(adj_close, signal_dates):
    """Month-end adjusted closes (signal dates x tickers)."""
    return adj_close.reindex(pd.DatetimeIndex(signal_dates))


def momentum(mp, lookback=12, skip=1):
    """Return over months t-lookback .. t-skip using month-end prices: P[t-skip]/P[t-lookback] - 1."""
    return mp.shift(skip) / mp.shift(lookback) - 1.0


def realized_vol_12m(mp):
    r = mp / mp.shift(1) - 1.0
    return r.rolling(12, min_periods=12).std()


def residual_momentum(mp, factors, window=RESID_WINDOW, min_obs=RESID_MIN_OBS):
    """Blitz-Huij-Martens residual momentum: FF3 regression over the trailing `window` months ending t-1,
    score = sum of residuals over months t-12..t-2 divided by their standard deviation over the window.
    `factors` has columns Mkt-RF, SMB, HML, RF indexed by month-end (decimal)."""
    r = (mp / mp.shift(1) - 1.0)
    f = factors.reindex(r.index)
    X = f[['Mkt-RF', 'SMB', 'HML']].to_numpy()
    ex = r.sub(f['RF'], axis=0).to_numpy()
    out = pd.DataFrame(np.nan, index=r.index, columns=r.columns)
    T = len(r)
    for ti in range(window, T):
        sl = slice(ti - window, ti)          # months t-window .. t-1
        Y = ex[sl]
        Xw = X[sl]
        valid_rows = np.isfinite(Xw).all(axis=1)
        if valid_rows.sum() < min_obs:
            continue
        Xv = np.column_stack([np.ones(valid_rows.sum()), Xw[valid_rows]])
        Yv = Y[valid_rows]
        good = np.isfinite(Yv).sum(axis=0) >= min_obs
        if not good.any():
            continue
        Yg = np.where(np.isfinite(Yv), Yv, 0.0)[:, good]
        mask = np.isfinite(Yv)[:, good]
        # per-column OLS with missing rows handled by masking (loop over columns with any NaN; vectorised otherwise)
        beta = np.linalg.lstsq(Xv, Yg, rcond=None)[0]
        resid = Yg - Xv @ beta
        resid[~mask] = np.nan
        nan_cols = np.where(~mask.all(axis=0))[0]
        for c in nan_cols:
            mc = mask[:, c]
            b = np.linalg.lstsq(Xv[mc], Yg[mc, c], rcond=None)[0]
            resid[mc, c] = Yg[mc, c] - Xv[mc] @ b
        # residual months relative to t: window rows correspond to t-window..t-1; take t-12..t-2 = last 11 rows excluding the final one
        last = resid[-12:-1]
        sd = np.nanstd(resid, axis=0, ddof=1)
        score = np.nansum(last, axis=0) / np.where(sd > 0, sd, np.nan)
        score[np.isfinite(last).sum(axis=0) < 11] = np.nan
        cols = np.where(good)[0]
        out.iloc[ti, cols] = score
    return out


def holding_returns(open_, close, adj_close, exec_dates, calendar, dev_end, split_factor=None):
    """Open-to-open holding returns per rebalance: entry at open of exec_dates[k], exit at open of exec_dates[k+1].
    I5: when `split_factor` is given, a month whose adjusted return differs from the split-adjusted return by more than
    CONSISTENCY_TOL books the split-adjusted return instead (count in holding_returns.substitutions).
    Returns (ret frame indexed by exec date, dict of delisting info per (exec date, code))."""
    adj_open = open_ * (adj_close / close)
    split_open = None if split_factor is None else open_ / split_factor
    cal = pd.DatetimeIndex(calendar)
    ret = pd.DataFrame(np.nan, index=pd.DatetimeIndex(exec_dates[:-1]), columns=close.columns)
    ended = {}
    substitutions = 0
    last_valid = adj_close.apply(lambda s: s.last_valid_index())
    last_close = close.apply(lambda s: s.dropna().iloc[-1] if s.notna().any() else np.nan)
    for k in range(len(exec_dates) - 1):
        d0, d1 = exec_dates[k], exec_dates[k + 1]
        entry = adj_open.loc[d0]
        exit_ = adj_open.loc[d1]
        r = exit_ / entry - 1.0
        if split_open is not None:
            r_split = split_open.loc[d1] / split_open.loc[d0] - 1.0
            bad = (((1.0 + r) / (1.0 + r_split) - 1.0).abs() > CONSISTENCY_TOL) & r.notna() & r_split.notna()
            substitutions += int(bad.sum())
            r = r.where(~bad, r_split)
        # names with an entry price but no exit open: series ended (or halted) inside the month
        missing = exit_.isna() & entry.notna()
        for code in close.columns[missing.to_numpy()]:
            lv = last_valid[code]
            if lv is None or pd.isna(lv) or lv < d0:
                continue
            seg = adj_close.loc[d0:d1, code].dropna()
            if seg.empty:
                continue
            r[code] = seg.iloc[-1] / entry[code] - 1.0
            if lv < d1 and lv <= dev_end:
                # distress proxy: 126-trading-day return to the last close <= -50% or last unadjusted close < 1
                pos = cal.get_loc(lv) if lv in cal else None
                prior = None
                if pos is not None and pos - 126 >= 0:
                    prior = adj_close[code].reindex(cal).iloc[pos - 126]
                drop = (adj_close.loc[lv, code] / prior - 1.0) if prior and np.isfinite(prior) else np.nan
                ended[(d0, code)] = dict(last=lv, drop126=float(drop) if np.isfinite(drop) else None,
                                         last_close=float(last_close[code]) if np.isfinite(last_close[code]) else None)
        ret.loc[d0] = r
    holding_returns.substitutions = substitutions
    return ret, ended


def load_last_venue():
    s = pd.read_parquet(e.ROOT / 'data/derived/phase6/eodhd/summary.parquet', columns=['code', 'exchange', 'list_status'])
    return dict(zip(s['code'], s['exchange']))


def delisting_haircut(info, venue, mode='base'):
    """Preregistered delisting return. mode: base (Shumway proxies), all100 (-100% on distress), all30 (-30% on every ending)."""
    distress = (info['drop126'] is not None and info['drop126'] <= -0.5) or (info['last_close'] is not None and info['last_close'] < 1.0)
    if mode == 'all30':
        return -0.30
    if not distress:
        return 0.0
    if mode == 'all100':
        return -1.0
    return -0.30 if venue in ('NYSE', 'AMEX', 'NYSE MKT', 'NYSE ARCA') else -0.55
