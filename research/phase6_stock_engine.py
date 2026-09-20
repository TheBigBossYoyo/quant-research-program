"""Monthly long-only top-N portfolio engine with Trading 212 cost cases and delisting bookings (Phase 6).

Inputs are aligned monthly frames (signal date x ticker): `scores` (higher = better; NaN = not ranked),
`eligible` (bool), `rank` (lagged liquidity rank, used by the stress cost case), and `ret` (open-to-open
holding return for the month that starts at the execution day after each signal date; the last signal date
has no return and is dropped). Selection at signal date k uses only row k; the return booked is row k of
`ret`, which starts at the open AFTER the signal close. No same-bar fills.

Cost cases (PHASE6_COST_MODEL.md section 3, bps per side of traded notional):
  optimistic 3 / 3.3; base 20 / 20.3; stress 30 / 31 (ranks 1-500) and 45 / 46 (ranks 501-1000).
Net return of a month = (1 - cost paid at the rebalance) x (1 + gross holding return) - 1.
"""
import numpy as np
import pandas as pd

COST_CASES = {
    'optimistic': dict(buy=0.0003, sell=0.00033, buy_far=0.0003, sell_far=0.00033),
    'base': dict(buy=0.0020, sell=0.00203, buy_far=0.0020, sell_far=0.00203),
    'stress': dict(buy=0.0030, sell=0.0031, buy_far=0.0045, sell_far=0.0046),
}
FAR_RANK = 500


def select_top(scores_row, eligible_row, n):
    s = scores_row.where(eligible_row)
    s = s.dropna().sort_values(ascending=False, kind='mergesort')
    return list(s.index[:n])


def simulate(scores, eligible, ret, rank=None, n=30, ended=None, venue=None, haircut=None, cost_case='base',
             exposure=None):
    """Run the monthly portfolio. `haircut(info, venue_of_code)` returns the delisting return for an ended
    position; `exposure` (Series indexed like scores, in [0, 1]) scales the invested fraction (overlays), the
    remainder is cash at 0.
    Returns dict(monthly=DataFrame, holdings=dict signal_date -> list, contributions=DataFrame)."""
    sig = scores.index[:len(ret)]
    cols = scores.columns
    ret = ret.reindex(columns=cols)
    c = COST_CASES[cost_case]
    prev_w = pd.Series(dtype=float)
    rows, holdings = [], {}
    contrib = {}
    ended = ended or {}
    for k, t in enumerate(sig):
        picks = select_top(scores.loc[t], eligible.loc[t], n)
        exp = 1.0 if exposure is None else float(exposure.loc[t])
        w = pd.Series(exp / len(picks), index=picks) if picks else pd.Series(dtype=float)
        r = ret.iloc[k].reindex(picks)
        skipped = int(r.isna().sum())
        r = r.fillna(0.0)
        n_delist = 0
        for code in picks:
            key = (ret.index[k], code)
            if key in ended and haircut is not None:
                h = haircut(ended[key], (venue or {}).get(code))
                r[code] = (1.0 + r[code]) * (1.0 + h) - 1.0
                n_delist += 1
        # turnover against drifted previous weights
        union = w.index.union(prev_w.index)
        target = w.reindex(union).fillna(0.0)
        drift = prev_w.reindex(union).fillna(0.0)
        delta = target - drift
        buys, sells = delta.clip(lower=0), (-delta).clip(lower=0)
        if rank is not None and cost_case == 'stress':
            rk = rank.loc[t].reindex(union).fillna(1e9)
            far = rk > FAR_RANK
            cost = float((buys * np.where(far, c['buy_far'], c['buy'])).sum() + (sells * np.where(far, c['sell_far'], c['sell'])).sum())
        else:
            cost = float(buys.sum() * c['buy'] + sells.sum() * c['sell'])
        gross = float((w * r).sum())
        net = (1.0 - cost) * (1.0 + gross) - 1.0
        rows.append(dict(signal=t, exec=ret.index[k], gross=gross, net=net, cost=cost, turnover_buy=float(buys.sum()),
                         turnover_sell=float(sells.sum()), n_held=len(picks), skipped=skipped, delisted=n_delist,
                         exposure=exp))
        holdings[t] = picks
        contrib[t] = (w * r)
        # drift weights to month end for next turnover computation (exposure cash stays cash)
        grown = w * (1.0 + r)
        total = grown.sum() + (1.0 - w.sum())
        prev_w = grown / total if total > 0 else pd.Series(dtype=float)
    monthly = pd.DataFrame(rows).set_index('signal')
    return dict(monthly=monthly, holdings=holdings, contributions=pd.DataFrame(contrib).T)


def equal_weight_benchmark(eligible, ret, ended=None, venue=None, haircut=None):
    """Equal-weight eligible universe rebalanced monthly, no costs, same delisting bookings."""
    scores = eligible.astype(float)
    return simulate(scores, eligible, ret, n=10 ** 9, ended=ended, venue=venue, haircut=haircut, cost_case='optimistic')['monthly'].assign(
        net=lambda d: d['gross'])


def ann_stats(x, periods=12):
    x = pd.Series(x).dropna()
    if len(x) < 2:
        return dict(mean=np.nan, sharpe=np.nan, cagr=np.nan, max_dd=np.nan, n=int(len(x)))
    idx = (1 + x).cumprod()
    years = len(x) / periods
    return dict(mean=float(x.mean()), sharpe=float(x.mean() / x.std(ddof=1) * np.sqrt(periods)) if x.std(ddof=1) > 0 else np.nan,
                cagr=float(idx.iloc[-1] ** (1 / years) - 1), max_dd=float((idx / idx.cummax() - 1).min()), n=int(len(x)))
