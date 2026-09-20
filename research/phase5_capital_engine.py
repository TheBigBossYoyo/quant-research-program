"""E049 CAPITAL_EFFICIENCY_RESEARCH simulator (amendment 1: resize only on score change, >10% vol-scalar move, or a pending sub-minimum order; never to equity drift): pooled-capital slow-trend portfolio with exchange lot steps,
minimum notionals, accumulation buffer, dead-band and volatility-target overlay. New architecture; not E040.

Semantics mirror phase4_engine.ledger for the trend component: hourly marks, funding on incoming units at
settlement before orders, orders only at scheduled 4h opens, pending score set at completed 4h bars.
"""
import math

import numpy as np
import pandas as pd


def simulate(frames, scores, funding, rules, capital, cost=.000905, band=0., scalar=1., vol_lag=None, vol_target=None):
    """frames/scores/funding: dict sym -> aligned hourly-event data on a common index. rules: sym -> (step, min_notional).
    capital None = unconstrained reference (no rounding, no minimum). Returns daily equity path and diagnostics."""
    syms = list(frames); idx = frames[syms[0]].index; n = len(idx); N = len(syms)
    O = {s: frames[s].execution_open.to_numpy(float) for s in syms}; C = {s: frames[s].valuation_close.to_numpy(float) for s in syms}
    ORD = {s: frames[s].orderable.to_numpy(bool) for s in syms}; TR = {s: frames[s].tradable.to_numpy(bool) for s in syms}; CP = {s: frames[s].complete.to_numpy(bool) for s in syms}
    SC = {s: scores[s].to_numpy(float) for s in syms}; F = {s: funding[s].to_numpy(float) for s in syms}
    unconstrained = capital is None; eq = 10000. if unconstrained else float(capital)
    units = {s: 0. for s in syms}; mark = {s: math.nan for s in syms}; pending = {s: 0. for s in syms}; held = {s: 0. for s in syms}
    last_sc = {s: math.nan for s in syms}; pending_skip = {s: False for s in syms}; lag_hours = 0
    day_index = idx.normalize(); days = pd.DatetimeIndex(sorted(set(day_index))); day_pos = {d: i for i, d in enumerate(days)}
    eq_d = np.full(len(days), np.nan); turn = 0.; fees = 0.; skipped = 0; wanted = 0; werr = []; gross_d = np.zeros(len(days)); cnt_d = np.zeros(len(days)); ruin = False
    vt = None
    if vol_target is not None and vol_lag is not None: vt = vol_lag.reindex(days).to_numpy(float)
    for i in range(n):
        if ruin: eq_d[day_pos[day_index[i]]] = 0.; continue
        for s in syms:
            o = O[s][i]
            if np.isfinite(o):
                if np.isfinite(mark[s]): eq += units[s] * (o - mark[s])
                mark[s] = o
            eq -= units[s] * F[s][i]
        if eq <= 0: ruin = True; eq = 0.; eq_d[day_pos[day_index[i]]] = 0.; continue
        sc = scalar
        if vt is not None:
            v = vt[day_pos[day_index[i]]]
            if np.isfinite(v) and v > 0: sc = scalar * min(1., vol_target / v)
        for s in syms:
            o = O[s][i]
            if not (ORD[s][i] and TR[s][i] and np.isfinite(o)): continue
            want = pending[s]
            if band > 0 and abs(want - held[s]) <= band: want = held[s]
            score_changed = abs(want - held[s]) > 1e-12
            scalar_moved = np.isfinite(last_sc[s]) and last_sc[s] > 0 and abs(sc - last_sc[s]) / last_sc[s] > .10 and units[s] != 0.
            target = want * eq * sc / N; step, mn = rules[s]
            if not (score_changed or scalar_moved or pending_skip[s]):
                werr.append(abs(units[s] * o - target) / max(eq, 1e-9)); continue
            if unconstrained: desired = target / o
            else:
                q = math.floor(abs(target) / o / step) * step if step > 0 else abs(target) / o; desired = math.copysign(q, target) if q > 0 else 0.
            delta = desired - units[s]; notional = abs(delta) * o
            if score_changed and not pending_skip[s]: wanted += 1
            if abs(delta) > 1e-12 and (not unconstrained) and notional < mn:
                if score_changed and not pending_skip[s]: skipped += 1
                pending_skip[s] = True; lag_hours += 1
            else:
                if abs(delta) > 1e-12:
                    fee = notional * cost; eq -= fee; fees += fee; turn += notional; units[s] = desired
                held[s] = want; last_sc[s] = sc; pending_skip[s] = False
            werr.append(abs(units[s] * o - target) / max(eq, 1e-9))
        for s in syms:
            c = C[s][i]
            if np.isfinite(c):
                if np.isfinite(mark[s]): eq += units[s] * (c - mark[s])
                mark[s] = c
            if CP[s][i]: v = SC[s][i]; pending[s] = float(v) if np.isfinite(v) else 0.
        if eq <= 0: ruin = True; eq = 0.
        di = day_pos[day_index[i]]; eq_d[di] = eq; gross_d[di] += sum(abs(units[s] * (mark[s] if np.isfinite(mark[s]) else 0.)) for s in syms) / max(eq, 1e-9); cnt_d[di] += 1
    e = pd.Series(eq_d, index=days).ffill(); r = e.pct_change(fill_method=None); r.iloc[0] = e.iloc[0] / (10000. if unconstrained else capital) - 1; r = r.where(e.shift(1).ne(0), 0.).fillna(0.)
    return dict(returns=r, equity=e, turnover=turn, fees=fees, skipped=skipped, wanted=wanted, lag_hours=lag_hours, mean_weight_error=float(np.mean(werr)) if werr else 0., gross=float((gross_d / np.maximum(cnt_d, 1)).mean()), ruin=ruin)
