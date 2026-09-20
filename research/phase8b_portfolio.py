"""Phase 8B primary portfolio accounting (preregistration section 8): hold every qualifying event, equal weight.

Daily loop over trading sessions, everything marked and traded at the session's adjusted open:
1. exits due today (exit session reached, or the price series ended -> last price with the Phase 6 delisting haircut);
2. entries due today (an issuer already held opens no second position and gets no extension; counted);
3. on any session with an exit or an entry the book is re-equalised: every active position is set to 1/N of the
   post-exit equity (sells first, then buys, never more cash than available); on other sessions nothing is traded.
Costs per side on every traded notional (entry, exit, re-equalisation legs) by liquidity rank (far = rank > 500 or
unknown). Cash earns 0. Equity is recorded at the open of each session; monthly returns are first-open-to-first-open.
The function is pure (inputs are arrays and frames); nothing is read from disk here.
"""
import numpy as np
import pandas as pd

import phase6_stock_universe as su
from phase8_insider_backtest import COSTS, FAR_RANK, monthly_from_equity  # noqa: F401  (re-exported)
from phase8b_lock import guard_dates


def simulate_hold_all(events, ao, cal, ended_info=None, venue=None, cost_case='MANUAL_USD', delay=0, haircut_mode='base', costs=None):
    """events: DataFrame with code, entry_idx, exit_idx, rank (NaN allowed), event_id. ao: adjusted-open panel (cal x codes).
    Returns dict(equity Series at the open, trades DataFrame, turnover parts, counters)."""
    guard_dates(cal, 'portfolio calendar')
    c = (costs or COSTS)[cost_case]; ended_info = ended_info or {}; venue = venue or {}
    n = len(cal)
    arrays = {code: ao[code].to_numpy(dtype=float) for code in events['code'].unique() if code in ao.columns}
    by_day = {}
    for idx, r in events.sort_values(['entry_idx', 'event_id']).iterrows():
        by_day.setdefault(int(r['entry_idx']) + delay, []).append(idx)
    cash = 1.0; positions = {}
    equity = np.full(n, np.nan); trades = []; legs = dict(entry=0.0, exit=0.0, rebalance=0.0); cost_paid = 0.0
    counters = dict(skipped_held=0, skipped_noprice=0, delisted=0, entries=0, exits=0, rebalance_days=0)
    start = int(events['entry_idx'].min()) + delay if len(events) else 0

    def rate(far, side):
        return c[f'{side}_far'] if far else c[side]

    for d in range(start, n):
        for code, p in positions.items():
            px = arrays[code][d]
            if np.isfinite(px):
                p['last_px'] = px
        equity[d] = cash + sum(p['shares'] * p['last_px'] for p in positions.values())
        changed = False
        # 1. exits
        for code in list(positions):
            p = positions[code]; info = ended_info.get(code)
            ended_now = info is not None and d > info['last_idx']
            if d >= p['exit_idx'] or ended_now:
                px = p['last_px']
                if ended_now:
                    px = px * (1 + su.delisting_haircut(info, venue.get(code), haircut_mode)); counters['delisted'] += 1
                notional = p['shares'] * px; fee = notional * rate(p['far'], 'sell')
                cash += notional - fee; cost_paid += fee; legs['exit'] += notional
                trades.append(dict(event_id=p['event_id'], code=code, entry_idx=p['entry_idx'], exit_idx=d, bought=p['bought'], sold=p['sold'] + notional - fee,
                                   pnl=p['sold'] + notional - fee - p['bought'], delisted=ended_now))
                del positions[code]; counters['exits'] += 1; changed = True
        # 2. entries
        new = []
        for idx in by_day.get(d, []):
            r = events.loc[idx]; code = r['code']
            if code not in arrays or not np.isfinite(arrays[code][d]):
                counters['skipped_noprice'] += 1; continue
            if code in positions or code in [x[0] for x in new]:
                counters['skipped_held'] += 1; continue
            new.append((code, idx))
        # 3. re-equalise on membership change
        if changed or new:
            counters['rebalance_days'] += int(bool(new) or changed)
            value = cash + sum(p['shares'] * p['last_px'] for p in positions.values())
            N = len(positions) + len(new)
            if N > 0:
                target = value / N
                for code, p in positions.items():                      # sells first
                    v = p['shares'] * p['last_px']
                    if v > target * (1 + 1e-9):
                        notional = v - target; fee = notional * rate(p['far'], 'sell')
                        p['shares'] -= notional / p['last_px']; cash += notional - fee; cost_paid += fee; legs['rebalance'] += notional; p['sold'] += notional - fee
                buys = [(code, target - positions[code]['shares'] * positions[code]['last_px'], 'rebalance') for code in positions
                        if positions[code]['shares'] * positions[code]['last_px'] < target * (1 - 1e-9)]
                buys += [(code, target, 'entry') for code, _ in new]
                need = sum(b[1] for b in buys)                            # fee is paid out of the notional (Phase 8 convention)
                scale = min(1.0, cash / need) if need > 0 else 1.0
                for code, notional, leg in buys:
                    notional *= scale
                    if notional <= 0:
                        continue
                    if leg == 'entry':
                        idx = dict(new)[code]; r = events.loc[idx]
                        far = (not np.isfinite(r['rank'])) or r['rank'] > FAR_RANK
                        px = arrays[code][d]
                        positions[code] = dict(shares=0.0, exit_idx=int(r['exit_idx']) + delay, entry_idx=d, far=far, last_px=px, event_id=r['event_id'], bought=0.0, sold=0.0)
                        counters['entries'] += 1
                    p = positions[code]
                    fee = notional * rate(p['far'], 'buy')
                    p['shares'] += (notional - fee) / p['last_px']; cash -= notional; cost_paid += fee; legs[leg] += notional; p['bought'] += notional
                if cash < 0:
                    assert cash > -1e-9 * max(1.0, value), 'cash went negative'
                    cash = 0.0
    eq = pd.Series(equity, index=cal).dropna()
    mean_eq = float(eq.mean()) if len(eq) else np.nan
    years = len(eq) / 252 if len(eq) else np.nan
    turnover = {k: float(v / mean_eq / years) if years else np.nan for k, v in legs.items()}
    turnover['oneway_total'] = float(sum(legs.values()) / 2 / mean_eq / years) if years else np.nan
    return dict(equity=eq, trades=pd.DataFrame(trades), turnover=turnover, counters=counters, cost_paid=cost_paid, legs=legs)
