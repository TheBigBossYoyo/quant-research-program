"""Phase 11C Stage 0 - U.S. Treasury term-structure risk premia / duration timing: returns-free audit utilities.

Nothing in this module reads a yield, a price, a return, an excess return or a term-premium series. It holds:

  1. the data-source registry (curve type, PIT classification) and the rule for which sources can carry an exact,
     an approximate, or only a *different* Cochrane-Piazzesi (CP) forward-rate construction;
  2. log forward rates from zero-coupon log yields (refuses par/CMT input: par yields are not zero yields);
  3. the causal timing convention: H.15/Treasury observation for U.S. business day D -> conservative publication
     time -> earliest London (XLON) session whose open is after publication -> execution at that session's close;
  4. the recursive-estimation guard: at decision date t a coefficient may use only (predictor, target) pairs whose
     h-month target has been realised by t; an expanding-window OLS built on it, with a leakage self-check;
  5. overlap / effective-sample / Stambaugh-bias / power arithmetic (analytic, from published magnitudes only);
  6. the FX decomposition for a EUR investor (unhedged USD line, EUR-hedged line) and the switch-cost model;
  7. the Stage 0 gate table for the three permitted signal classes and the decision rule.

CLI:  python phase11c_treasury_audit.py all      (from research/; writes reports/phase11c/treasury_audit/)
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "phase11c" / "treasury_audit"
UTC = dt.timezone.utc
NY = ZoneInfo("America/New_York")
LONDON = ZoneInfo("Europe/London")

# ---------------------------------------------------------------------------------------------------------------
# 1. Data-source registry
# ---------------------------------------------------------------------------------------------------------------

PIT_CLASSES = ("PIT_SAFE", "PIT_RECONSTRUCTABLE", "MINOR_REVISION_RISK", "PIT_BLOCKED")
CURVE_TYPES = ("PAR_CMT", "ZERO_UNSMOOTHED", "ZERO_SMOOTHED", "MODEL_TERM_PREMIUM")


@dataclass(frozen=True)
class DataSource:
    key: str
    name: str
    curve_type: str
    pit_class: str
    free: bool
    start: str
    note: str

    def __post_init__(self):
        if self.curve_type not in CURVE_TYPES:
            raise ValueError(f"unknown curve type {self.curve_type}")
        if self.pit_class not in PIT_CLASSES:
            raise ValueError(f"unknown PIT class {self.pit_class}")


# Classifications are the audit's conclusions (PHASE11C_STAGE0_AUDIT.md sections 5-7); tests pin them.
SOURCES: dict[str, DataSource] = {
    s.key: s
    for s in (
        DataSource("H15_CMT", "Federal Reserve H.15 / Treasury par yield curve (constant maturity), 3m-10y",
                   "PAR_CMT", "PIT_SAFE", True, "1962-01-02 (1y/3y/5y/10y/20y), 1969-07-01 (7y), 1976-06-01 (2y), "
                   "1981-09-01 (3m/6m), 2001-07-31 (1m)",
                   "measured (reports/phase11c/raw/pit_checks): ALFRED vintages from 2005-06-28; observations dated "
                   "before each of three vintages (2005, 2010, 2018) differ from the 2026-09-25 vintage in 0-3 "
                   "isolated dates per tenor (max 10 bp, mostly <= 2 bp) plus a 3->2 decimal formatting change; "
                   "FRED archive lag at month-ends 1-6 calendar days; Dec 2021 fitting change is prospective only"),
        DataSource("H15_LONG_END", "H.15 20y and 30y CMT", "PAR_CMT", "MINOR_REVISION_RISK", True,
                   "1962-01-02 (20y, backfilled), 1977-02-15 (30y)",
                   "backfill hazard (measured): 20y history before the 1993 reintroduction is absent from the 2005 and "
                   "2010 vintages and present today; 30y 2002-02-19..2006-02-08 (994 dates) missing in the 2010 "
                   "vintage and filled today - values not available in real time"),
        DataSource("GSW", "Gurkaynak-Sack-Wright Fed nominal curve (Svensson)", "ZERO_SMOOTHED",
                   "MINOR_REVISION_RISK", True, "1961-06-14",
                   "each day fitted on that day's prices, but the current file is a re-implemented vintage ('not "
                   "identical' to the original, Fed); archived vintages sparse (legacy .xls: 69 Wayback captures, 27 "
                   "distinct digests 2009-2025); smoothing removes the tent-shape signal (CP 2008 Table 1)"),
        DataSource("ACM", "NY Fed Adrian-Crump-Moench term premia", "MODEL_TERM_PREMIUM", "PIT_BLOCKED", True,
                   "1961-06-14",
                   "model re-estimated on the full sample; no archive of historical vintages; a value dated 2005 is "
                   "not an estimate available in 2005"),
        DataSource("FAMA_BLISS", "CRSP Fama-Bliss discount bonds", "ZERO_UNSMOOTHED", "PIT_SAFE", False, "1952-06",
                   "the canonical CP input; licensed (CRSP via WRDS), not obtainable by this programme"),
        DataSource("LIU_WU", "Liu-Wu (2021) reconstructed zero-coupon curve", "ZERO_UNSMOOTHED",
                   "MINOR_REVISION_RISK", True, "1961-06",
                   "free output of a date-by-date kernel fit to CRSP quotes; periodic re-releases; no vintage archive"),
    )
}


def cp_construction_status(source_key: str) -> str:
    """How faithfully a source can carry the CP five-forward factor.

    EXACT                    unsmoothed discount-bond prices of the kind CP used (Fama-Bliss) - licensed here;
    CLOSE                    another unsmoothed zero curve (Liu-Wu);
    DIFFERENT_CONSTRUCTION   a smoothed parametric curve (GSW): forwards exist, but they are a different object;
    NOT_VALID                par/CMT yields or a model term premium: canonical forwards cannot be read off them.
    """
    s = SOURCES[source_key]
    if s.curve_type == "ZERO_UNSMOOTHED":
        return "EXACT" if s.key == "FAMA_BLISS" else "CLOSE"
    if s.curve_type == "ZERO_SMOOTHED":
        return "DIFFERENT_CONSTRUCTION"
    return "NOT_VALID"


# ---------------------------------------------------------------------------------------------------------------
# 2. Forward rates from zero-coupon log yields
# ---------------------------------------------------------------------------------------------------------------

def log_forward_rates(zero_log_yields: Mapping[int, float], curve_type: str) -> dict[int, float]:
    """One-year log forwards f(n) = n*y(n) - (n-1)*y(n-1) for n >= 2, f(1) = y(1) (CP notation, annual maturities).

    Refuses anything but a zero-coupon curve: applying the formula to par yields is the error the brief warns about.
    """
    if curve_type not in ("ZERO_UNSMOOTHED", "ZERO_SMOOTHED"):
        raise ValueError(f"forward rates need zero-coupon yields, got {curve_type}")
    ns = sorted(zero_log_yields)
    if ns != list(range(1, len(ns) + 1)):
        raise ValueError("maturities must be consecutive whole years starting at 1")
    out = {1: zero_log_yields[1]}
    for n in ns[1:]:
        out[n] = n * zero_log_yields[n] - (n - 1) * zero_log_yields[n - 1]
    return out


# ---------------------------------------------------------------------------------------------------------------
# 3. Causal timing convention
# ---------------------------------------------------------------------------------------------------------------

# Conservative latest publication time for an H.15 / Treasury observation dated D (U.S. Eastern). Treasury quotes are
# taken at about 3:30 pm ET and the curve is usually posted in the late afternoon; H.15 posts its daily update after
# that. 18:00 ET is used as a deliberately late bound; the rule below also never executes on day D itself.
PUBLICATION_BOUND_ET = dt.time(18, 0)


def signal_date_for_month(observed_dates: Iterable[dt.date], year: int, month: int) -> dt.date:
    """Last date in (year, month) that carries an official observation (non-ND). Taken from the data's own dates,
    not from a calendar: bond-market closures (Columbus Day, Veterans Day, most Good Fridays) differ from NYSE."""
    cands = [d for d in observed_dates if d.year == year and d.month == month]
    if not cands:
        raise ValueError(f"no observation in {year}-{month:02d}")
    return max(cands)


def publication_bound_utc(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, PUBLICATION_BOUND_ET, tzinfo=NY).astimezone(UTC)


def _xlon():
    import exchange_calendars as xc  # local import: only the timing functions need it
    return xc.get_calendar("XLON")


def execution_session(d: dt.date, calendar=None) -> tuple[dt.date, dt.datetime]:
    """Earliest XLON session strictly after D whose open is after the publication bound; execute at its close.

    Returns (session date, close time UTC). Because the bound is ~23:00 London on D, this is normally the next London
    session; weekends and UK holidays roll forward. Execution is never on day D (London closes before the data exist).
    """
    cal = calendar or _xlon()
    pub = publication_bound_utc(d)
    import pandas as pd
    start = pd.Timestamp(d) + pd.Timedelta(days=1)
    sessions = cal.sessions_in_range(start, start + pd.Timedelta(days=14))
    for s in sessions:
        if cal.session_open(s).to_pydatetime() > pub:
            return s.date(), cal.session_close(s).to_pydatetime().astimezone(UTC)
    raise RuntimeError("no XLON session within 14 days")


def execution_session_backtest(d: dt.date, first_vintage_containing_d: dt.date, calendar=None
                               ) -> tuple[dt.date, dt.datetime]:
    """Backtest convention: the observation for D counts as known only when BOTH the same-evening publication bound
    has passed AND an ALFRED vintage containing D exists (vintage date V, treated as known at V 18:00 ET). Execution
    is the first XLON session whose open is after the later of the two. Measured month-end FRED lags were 1-6
    calendar days in 2006-2017, so this rule is stricter than live H.15 availability and never looser."""
    if first_vintage_containing_d < d:
        raise ValueError("a vintage cannot contain an observation dated after it")
    return execution_session(max(d, first_vintage_containing_d), calendar)


def monthly_schedule(observed_dates: Sequence[dt.date], months: Sequence[tuple[int, int]], calendar=None) -> list[dict]:
    cal = calendar or _xlon()
    rows = []
    for (y, m) in months:
        d = signal_date_for_month(observed_dates, y, m)
        sess, close = execution_session(d, cal)
        rows.append({"month": f"{y}-{m:02d}", "signal_date": d.isoformat(),
                     "publication_bound_utc": publication_bound_utc(d).isoformat(),
                     "execution_session": sess.isoformat(), "execution_close_utc": close.isoformat()})
    return rows


# ---------------------------------------------------------------------------------------------------------------
# 4. Recursive-estimation guard
# ---------------------------------------------------------------------------------------------------------------

def usable_training_pairs(t: int, horizon: int, first: int = 0) -> list[tuple[int, int]]:
    """Pairs (s, s + horizon) usable for a coefficient estimated at month index t.

    The target attached to predictor date s is the return from s to s + horizon, which is known only at s + horizon.
    So only s with s + horizon <= t are usable. Using s up to t (the common mistake) leaks horizon - 1 months of
    future returns into every estimate; a full-sample fit leaks everything.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    return [(s, s + horizon) for s in range(first, t - horizon + 1)]


def _ols(X: Sequence[Sequence[float]], y: Sequence[float]) -> list[float]:
    """Least squares with an intercept, by normal equations (small k; Gaussian elimination with pivoting)."""
    rows = [[1.0, *map(float, x)] for x in X]
    k = len(rows[0])
    A = [[sum(r[i] * r[j] for r in rows) for j in range(k)] for i in range(k)]
    b = [sum(r[i] * yy for r, yy in zip(rows, y)) for i in range(k)]
    M = [A[i] + [b[i]] for i in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-14:
            raise ValueError("singular design")
        M[c], M[p] = M[p], M[c]
        for r in range(k):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [a - f * bb for a, bb in zip(M[r], M[c])]
    return [M[i][k] / M[i][i] for i in range(k)]


def expanding_coefficients(predictors: Sequence[Sequence[float]], targets: Sequence[float | None], t: int,
                           horizon: int, min_pairs: int) -> list[float] | None:
    """Coefficients available at month t. targets[s] is the h-month return from s to s+h (None if unrealised).

    Only pairs from usable_training_pairs are touched, so targets[s] for s > t - horizon are never read.
    Returns None until min_pairs pairs exist (no forecast, hold the benchmark).
    """
    pairs = usable_training_pairs(t, horizon)
    if len(pairs) < min_pairs:
        return None
    X = [predictors[s] for s, _ in pairs]
    y = [targets[s] for s, _ in pairs]
    if any(v is None for v in y):
        raise ValueError("a usable pair has an unrealised target")
    return _ols(X, y)


# ---------------------------------------------------------------------------------------------------------------
# 5. Overlap, effective sample, bias and power (analytic; published magnitudes only)
# ---------------------------------------------------------------------------------------------------------------

def non_overlapping_obs(n_months: int, horizon: int) -> int:
    """Independent h-month outcomes in n_months: the honest count for overlapping annual regressions."""
    return n_months // horizon


def hansen_hodrick_lags(horizon: int) -> int:
    return max(horizon - 1, 0)


def stambaugh_bias(rho: float, n: int, sigma_uv_over_sigma_v2: float) -> float:
    """Kendall/Stambaugh first-order bias of the OLS slope with a persistent AR(1) predictor:
    E[b_hat - b] ~= -(sigma_uv / sigma_v^2) * (1 + 3 rho) / n."""
    return -sigma_uv_over_sigma_v2 * (1.0 + 3.0 * rho) / n


def timing_information_ratio(r2_per_period: float, periods_per_year: int) -> float:
    """Annualised information ratio of an unconstrained, correctly-signed linear timing rule with predictive R^2
    per period (Campbell-Thompson / Grinold approximation: IR_period ~= sqrt(R2 / (1 - R2)))."""
    if not 0 <= r2_per_period < 1:
        raise ValueError("R2 must be in [0, 1)")
    return math.sqrt(r2_per_period / (1.0 - r2_per_period)) * math.sqrt(periods_per_year)


def years_to_detect(ir_annual: float, t_crit: float = 1.96) -> float:
    """Years of data for the mean active return of a rule with annual IR to reach t_crit (t ~= IR * sqrt(years))."""
    if ir_annual <= 0:
        return math.inf
    return (t_crit / ir_annual) ** 2


def power_one_sided(ir_annual: float, years: float, t_crit: float = 1.645) -> float:
    """Probability the realised t-stat of mean active return exceeds t_crit, true IR given (normal approximation)."""
    z = ir_annual * math.sqrt(years) - t_crit
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


# ---------------------------------------------------------------------------------------------------------------
# 6. FX decomposition and costs
# ---------------------------------------------------------------------------------------------------------------

def eur_return_unhedged(r_usd: float, fx_usd_in_eur: float) -> float:
    """EUR return of a USD asset: (1 + r_usd)(1 + change in EUR value of 1 USD) - 1."""
    return (1.0 + r_usd) * (1.0 + fx_usd_in_eur) - 1.0


def eur_active_return_unhedged(r_strategy_usd: float, r_benchmark_usd: float, fx_usd_in_eur: float) -> float:
    """Active return in EUR when strategy and benchmark are BOTH unhedged USD Treasury lines:
    (r_s - r_b)(1 + fx). FX scales the active return but cannot create it; with fx = 0 it is exactly r_s - r_b."""
    return eur_return_unhedged(r_strategy_usd, fx_usd_in_eur) - eur_return_unhedged(r_benchmark_usd, fx_usd_in_eur)


def eur_return_hedged_approx(r_usd: float, eur_short_rate: float, usd_short_rate: float,
                             hedge_friction: float = 0.0) -> float:
    """Approximate EUR-hedged share-class return over one period: USD bond return plus the forward points
    (EUR minus USD short rate over the period) minus hedging friction. The carry term is common to every hedged
    Treasury line, so it cancels in hedged-versus-hedged active returns."""
    return r_usd + (eur_short_rate - usd_short_rate) - hedge_friction


def switch_cost_bps(half_spread_sell_bps: float, half_spread_buy_bps: float, fx_bps_each_way: float = 0.0,
                    fx_conversions: int = 0) -> float:
    """Cost of one full switch (sell one line, buy another), in bps of the switched notional."""
    return half_spread_sell_bps + half_spread_buy_bps + fx_bps_each_way * fx_conversions


def annual_cost_drag_bps(switches_per_year: float, cost_per_switch_bps: float) -> float:
    return switches_per_year * cost_per_switch_bps


# ---------------------------------------------------------------------------------------------------------------
# 7. Gate table and decision rule
# ---------------------------------------------------------------------------------------------------------------

DECISIONS = ("AUTHORIZE_STAGE1_PREREGISTRATION", "PIT_DATA_BLOCKED", "MECHANISM_TOO_WEAK",
             "REAL_TIME_OOS_EVIDENCE_TOO_WEAK", "IMPLEMENTATION_BLOCKED", "DUPLICATES_PRIOR_RESEARCH",
             "ABANDON_TREASURY_PROGRAMME")

# Gate -> the decision code a FAIL of that gate implies (ordered as the brief's selection criteria, plus the two
# eligibility gates: in-sample mechanism and distinctness from prior research).
GATES = (
    ("in_sample_mechanism", "MECHANISM_TOO_WEAK"),
    ("real_time_oos_evidence", "REAL_TIME_OOS_EVIDENCE_TOO_WEAK"),
    ("pit_reconstructable", "PIT_DATA_BLOCKED"),
    ("simple_preregistrable", "IMPLEMENTATION_BLOCKED"),
    ("long_only_economic_meaning", "REAL_TIME_OOS_EVIDENCE_TOO_WEAK"),
    ("low_turnover", "IMPLEMENTATION_BLOCKED"),
    ("no_proprietary_data", "PIT_DATA_BLOCKED"),
    ("distinct_from_prior_research", "DUPLICATES_PRIOR_RESEARCH"),
)
GATE_NAMES = tuple(g for g, _ in GATES)
GATE_VALUES = ("PASS", "FAIL", "UNRESOLVED")
DATA_CODE = "PIT_DATA_BLOCKED"


def class_decision(gates: Mapping[str, str]) -> dict:
    """Decision for one signal class. All PASS -> eligible. Otherwise the primary code comes from the first FAIL in
    GATES order (UNRESOLVED gates are listed but cannot set the code while something has FAILED); a class with no FAIL
    but some UNRESOLVED is not eligible and takes the code of its first UNRESOLVED gate."""
    missing = set(GATE_NAMES) - set(gates)
    if missing:
        raise ValueError(f"missing gates {sorted(missing)}")
    bad = {g: v for g, v in gates.items() if v not in GATE_VALUES}
    if bad:
        raise ValueError(f"bad gate values {bad}")
    fails = [g for g in GATE_NAMES if gates[g] == "FAIL"]
    unres = [g for g in GATE_NAMES if gates[g] == "UNRESOLVED"]
    code_of = dict(GATES)
    if not fails and not unres:
        return {"eligible": True, "code": "AUTHORIZE_STAGE1_PREREGISTRATION", "fails": [], "unresolved": []}
    first = fails[0] if fails else unres[0]
    data_blocked = any(code_of[g] == DATA_CODE for g in fails)
    return {"eligible": False, "code": code_of[first], "fails": fails, "unresolved": unres,
            "data_blocked": data_blocked}


def stage0_decision(class_gates: Mapping[str, Mapping[str, str]], preference: Sequence[str]) -> dict:
    """Programme decision over the ordered classes (preference = strongest-evidence-first order fixed in the audit).

    1. If one or more classes are eligible, authorise exactly ONE: the first eligible class in `preference`.
    2. Otherwise set aside every class with a data FAIL (PIT_DATA_BLOCKED). If nothing remains, PIT_DATA_BLOCKED.
    3. Among the remaining (data-feasible) classes, the programme code is the code of the first in `preference`.
    ABANDON_TREASURY_PROGRAMME is admissible only if every class fails its in-sample mechanism gate.
    """
    if set(preference) != set(class_gates):
        raise ValueError("preference must list every class exactly once")
    per = {c: class_decision(g) for c, g in class_gates.items()}
    eligible = [c for c in preference if per[c]["eligible"]]
    if eligible:
        return {"decision": "AUTHORIZE_STAGE1_PREREGISTRATION", "selected": eligible[0], "per_class": per}
    feasible = [c for c in preference if not per[c]["data_blocked"]]
    if all(class_gates[c]["in_sample_mechanism"] == "FAIL" for c in class_gates):
        return {"decision": "ABANDON_TREASURY_PROGRAMME", "selected": None, "per_class": per}
    if not feasible:
        return {"decision": "PIT_DATA_BLOCKED", "selected": None, "per_class": per}
    return {"decision": per[feasible[0]]["code"], "selected": None, "binding_class": feasible[0],
            "set_aside_data_blocked": [c for c in preference if per[c]["data_blocked"]], "per_class": per}


# The audit's gate table (PHASE11C_STAGE0_AUDIT.md section 14); tests pin the recorded decision against the rule.
#   A_CP_FACTOR        Cochrane-Piazzesi five-forward factor, recursive coefficients
#   B_SLOPE_FWD_SPREAD simple observable slope / Fama-Bliss forward spread, recursive sign rule
#   C_PIT_TERM_PREMIUM model-estimated term premium (ACM-type), only if recursively reconstructable
CLASS_GATES: dict[str, dict[str, str]] = {
    "B_SLOPE_FWD_SPREAD": {
        "in_sample_mechanism": "PASS",          # FB 1987; CP 2005 Table 3 replication R2 0.06-0.15; AJM 2019
        "real_time_oos_evidence": "FAIL",       # one positive recursive study (GPT 2019, gross, to 2011) vs TV 2012,
                                                # SSW 2016; no after-cost and no post-2011 OOS evidence
        "pit_reconstructable": "PASS",          # H.15 3m-10y measured PIT_SAFE
        "simple_preregistrable": "PASS",
        "long_only_economic_meaning": "UNRESOLVED",  # GPT [0,0.99] CER +0.46/+0.67%/yr at 4-5y only, gross
        "low_turnover": "PASS",                 # persistent predictor, monthly decision
        "no_proprietary_data": "PASS",          # H.15 CMT slope (a different construction from FB zero spreads)
        "distinct_from_prior_research": "PASS",  # yield-curve information, not price trend / vol (section 16)
    },
    "A_CP_FACTOR": {
        "in_sample_mechanism": "PASS",          # CP 2005 R2 0.34-0.44; Bauer-Hamilton concur on the core factor
        "real_time_oos_evidence": "FAIL",       # GPT OLS OOS R2 -1.58..+0.73%; Hodrick-Tomunen; B-H PC4/5 +21% MSE
        "pit_reconstructable": "UNRESOLVED",    # Liu-Wu free but revision practice undocumented; GSW smoothed
        "simple_preregistrable": "PASS",
        "long_only_economic_meaning": "FAIL",   # GPT [0,0.99] LIN CER -0.20..+0.18%/yr, not significant
        "low_turnover": "UNRESOLVED",
        "no_proprietary_data": "UNRESOLVED",    # exact inputs are licensed Fama-Bliss; Liu-Wu only 'close'
        "distinct_from_prior_research": "PASS",
    },
    "C_PIT_TERM_PREMIUM": {
        "in_sample_mechanism": "PASS",          # ACM 2013 in-sample pricing; excess-return fit
        "real_time_oos_evidence": "FAIL",       # SSW 2016 ACM-estimator robustness: negative OOS economic value
        "pit_reconstructable": "FAIL",          # published series re-estimated on the full sample; no vintages
        "simple_preregistrable": "FAIL",        # a five-factor model re-estimated monthly on GSW input
        "long_only_economic_meaning": "UNRESOLVED",
        "low_turnover": "UNRESOLVED",
        "no_proprietary_data": "PASS",
        "distinct_from_prior_research": "PASS",
    },
}
# Strongest credible real-time OOS evidence first (selection criterion 1).
PREFERENCE: tuple[str, ...] = ("B_SLOPE_FWD_SPREAD", "A_CP_FACTOR", "C_PIT_TERM_PREMIUM")


# ---------------------------------------------------------------------------------------------------------------
# 8. Ex-ante power and cost envelopes (analytic; no data)
# ---------------------------------------------------------------------------------------------------------------

# Published monthly OOS R2 range for the best simple yield-only predictor (GPT 2019 Table 3, FB forward spread,
# OLS, 3-5y bonds: 1.77-2.61%; 2y 0.22%). LONG_ONLY_CAPTURE is an ASSUMPTION (a switch between two long positions
# captures roughly half of an unconstrained linear timing rule's information ratio), not a published number.
R2_GRID = (0.005, 0.01, 0.02)
LONG_ONLY_CAPTURE = 0.5
# Remaining post-GPT calendar available to any future test: 2012-01..2026-08 = 14.67 years (overlaps the
# programme's 2018-2021 and 2022-01..2026-08 locked windows); GPT's own OOS window 1990-2011 = 22 years.
YEARS_GRID = (6.0, 14.67, 22.0, 30.0)


def power_table() -> list[dict]:
    rows = []
    for r2 in R2_GRID:
        ir_u = timing_information_ratio(r2, 12)
        ir_lo = ir_u * LONG_ONLY_CAPTURE
        row = {"monthly_r2": r2, "ir_unconstrained": round(ir_u, 3), "ir_long_only_assumed": round(ir_lo, 3),
               "years_to_t1.96_long_only": round(years_to_detect(ir_lo), 1)}
        for y in YEARS_GRID:
            row[f"power_one_sided_5pct_{y:g}y"] = round(power_one_sided(ir_lo, y), 3)
        rows.append(row)
    return rows


# Cost envelope per full switch (bps of switched notional). Half-spreads are ASSUMPTIONS (issuer spread statistics
# were not verified); FX 15 bps each way is Trading 212's documented Invest fee (PHASE6_COST_MODEL.md, 2026-09-09).
COST_CASES = {
    "usd_lines_held_in_usd_low": {"half_spread_bps": 3, "fx_conversions": 0},
    "usd_lines_held_in_usd_high": {"half_spread_bps": 10, "fx_conversions": 0},
    "eur_account_converting_each_switch": {"half_spread_bps": 5, "fx_conversions": 2},
    "eur_hedged_lines_eur_account": {"half_spread_bps": 8, "fx_conversions": 0},
}
T212_FX_BPS = 15.0


def cost_envelope(switches_per_year: Sequence[float] = (1, 2, 4)) -> dict:
    out = {}
    for name, c in COST_CASES.items():
        per = switch_cost_bps(c["half_spread_bps"], c["half_spread_bps"], T212_FX_BPS, c["fx_conversions"])
        out[name] = {"per_switch_bps": per,
                     **{f"annual_drag_bps_{s:g}_switches": annual_cost_drag_bps(s, per) for s in switches_per_year}}
    return out


def recorded_decision() -> dict:
    return stage0_decision(CLASS_GATES, PREFERENCE)


# ---------------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------------

def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, indent=2, sort_keys=False, default=str)
        fh.write("\n")


def main(argv: Sequence[str]) -> int:
    if not argv or argv[0] != "all":
        print(__doc__)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    dec = recorded_decision()
    _write_json(OUT / "gate_table.json", {"class_gates": CLASS_GATES, "preference": list(PREFERENCE),
                                          "gates_to_codes": dict(GATES)})
    _write_json(OUT / "decision_check.json", dec)
    _write_json(OUT / "sources_pit.json", {k: s.__dict__ | {"cp_construction": cp_construction_status(k)}
                                           for k, s in SOURCES.items()})
    _write_json(OUT / "power_table.json", {"assumption_long_only_capture": LONG_ONLY_CAPTURE,
                                           "r2_source": "GPT 2019 Table 3 (FB spread, OLS, monthly OOS R2)",
                                           "rows": power_table()})
    _write_json(OUT / "cost_envelope.json", {"t212_fx_bps_each_way": T212_FX_BPS, "cases": cost_envelope()})
    months = [(2026, m) for m in range(1, 9)]
    import pandas as pd
    # illustrative schedule on the observed-date rule, using weekday dates minus U.S. federal holidays as stand-in
    # observation dates (the real rule takes dates from the data's own non-ND observations)
    from pandas.tseries.holiday import USFederalHolidayCalendar
    hol = set(USFederalHolidayCalendar().holidays("2026-01-01", "2026-12-31").date)
    obs = [d.date() for d in pd.bdate_range("2026-01-01", "2026-08-31") if d.date() not in hol]
    _write_json(OUT / "timing_convention.json", {
        "publication_bound_et": PUBLICATION_BOUND_ET.isoformat(),
        "live_rule": "execute at the close of the first XLON session whose open is after D 18:00 ET",
        "backtest_rule": "same, measured from max(D, first ALFRED vintage containing D)",
        "illustrative_2026_schedule": monthly_schedule(obs, months)})
    manifest = {p.name: __import__("hashlib").sha256(p.read_bytes()).hexdigest()
                for p in sorted(OUT.glob("*.json")) if p.name != "MANIFEST.json"}
    _write_json(OUT / "MANIFEST.json", manifest)
    print(json.dumps({"decision": dec["decision"], "binding_class": dec.get("binding_class"),
                      "set_aside": dec.get("set_aside_data_blocked")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
