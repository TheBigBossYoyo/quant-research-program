"""Phase 11C Stage 0 - tests for the returns-free Treasury audit utilities: source registry and CP construction
status, forward rates, the causal H.15 -> London timing convention, the recursive-estimation leakage guard,
overlap/power arithmetic, FX decomposition, and the decision rule. No yield, price or return series is read;
the only numbers are synthetic."""
import datetime as dt
import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))

import phase11c_treasury_audit as a  # noqa: E402

UTC = dt.timezone.utc
SRC = Path(a.__file__).read_text(encoding="utf-8")


class TestNoDataAccess(unittest.TestCase):
    def test_module_has_no_network_or_data_reads(self):
        for pat in (r"\brequests\b", r"urllib", r"http[s]?://", r"read_csv", r"read_parquet", r"yfinance",
                    r"fredapi", r"[\"']data[/\\]"):
            self.assertIsNone(re.search(pat, SRC), pat)


class TestSources(unittest.TestCase):
    def test_classes_are_valid(self):
        for s in a.SOURCES.values():
            self.assertIn(s.pit_class, a.PIT_CLASSES)
            self.assertIn(s.curve_type, a.CURVE_TYPES)

    def test_invalid_class_rejected(self):
        with self.assertRaises(ValueError):
            a.DataSource("X", "x", "PAR_CMT", "SAFE_ENOUGH", True, "", "")

    def test_cp_status(self):
        self.assertEqual(a.cp_construction_status("FAMA_BLISS"), "EXACT")
        self.assertEqual(a.cp_construction_status("LIU_WU"), "CLOSE")
        self.assertEqual(a.cp_construction_status("GSW"), "DIFFERENT_CONSTRUCTION")
        self.assertEqual(a.cp_construction_status("H15_CMT"), "NOT_VALID")
        self.assertEqual(a.cp_construction_status("ACM"), "NOT_VALID")

    def test_exact_cp_source_is_not_free(self):
        self.assertFalse(a.SOURCES["FAMA_BLISS"].free)

    def test_acm_blocked_h15_safe(self):
        self.assertEqual(a.SOURCES["ACM"].pit_class, "PIT_BLOCKED")
        self.assertEqual(a.SOURCES["H15_CMT"].pit_class, "PIT_SAFE")
        self.assertNotEqual(a.SOURCES["GSW"].pit_class, "PIT_SAFE")


class TestForwards(unittest.TestCase):
    def test_flat_curve_gives_flat_forwards(self):
        f = a.log_forward_rates({n: 0.04 for n in range(1, 6)}, "ZERO_UNSMOOTHED")
        for v in f.values():
            self.assertAlmostEqual(v, 0.04)

    def test_known_values(self):
        y = {1: 0.01, 2: 0.02, 3: 0.03}
        f = a.log_forward_rates(y, "ZERO_SMOOTHED")
        self.assertAlmostEqual(f[1], 0.01)
        self.assertAlmostEqual(f[2], 0.03)
        self.assertAlmostEqual(f[3], 0.05)

    def test_forwards_price_consistency(self):
        # sum of forwards f(1..n) equals n * y(n): log price of an n-year zero
        rnd = random.Random(7)
        y = {n: 0.02 + 0.003 * n + rnd.uniform(-1e-3, 1e-3) for n in range(1, 6)}
        f = a.log_forward_rates(y, "ZERO_UNSMOOTHED")
        for n in range(1, 6):
            self.assertAlmostEqual(sum(f[k] for k in range(1, n + 1)), n * y[n])

    def test_par_yields_refused(self):
        with self.assertRaises(ValueError):
            a.log_forward_rates({1: 0.01, 2: 0.02}, "PAR_CMT")
        with self.assertRaises(ValueError):
            a.log_forward_rates({1: 0.01, 2: 0.02}, "MODEL_TERM_PREMIUM")

    def test_gap_in_maturities_refused(self):
        with self.assertRaises(ValueError):
            a.log_forward_rates({1: 0.01, 3: 0.02}, "ZERO_UNSMOOTHED")


class TestTiming(unittest.TestCase):
    def test_signal_date_uses_observed_dates_not_calendar(self):
        # 2025-10-31 exists; pretend the last observation of Nov 2025 is the 28th (Thanksgiving week) - data decide
        obs = [dt.date(2025, 10, 30), dt.date(2025, 10, 31), dt.date(2025, 11, 26), dt.date(2025, 11, 28)]
        self.assertEqual(a.signal_date_for_month(obs, 2025, 10), dt.date(2025, 10, 31))
        self.assertEqual(a.signal_date_for_month(obs, 2025, 11), dt.date(2025, 11, 28))
        with self.assertRaises(ValueError):
            a.signal_date_for_month(obs, 2025, 12)

    def test_publication_bound_is_evening_new_york(self):
        self.assertEqual(a.publication_bound_utc(dt.date(2026, 1, 30)), dt.datetime(2026, 1, 30, 23, 0, tzinfo=UTC))
        self.assertEqual(a.publication_bound_utc(dt.date(2026, 7, 31)), dt.datetime(2026, 7, 31, 22, 0, tzinfo=UTC))

    def test_never_executes_on_day_d(self):
        d = dt.date(2026, 6, 30)
        sess, close = a.execution_session(d)
        self.assertGreater(sess, d)
        self.assertGreater(close, a.publication_bound_utc(d))

    def test_friday_rolls_to_monday(self):
        sess, _ = a.execution_session(dt.date(2026, 1, 30))
        self.assertEqual(sess, dt.date(2026, 2, 2))

    def test_uk_holidays_roll_forward(self):
        # Wed 2025-12-31 -> Thu 1 Jan (UK holiday) -> Fri 2 Jan
        self.assertEqual(a.execution_session(dt.date(2025, 12, 31))[0], dt.date(2026, 1, 2))
        # Thu 2025-04-17 -> Good Friday and Easter Monday closed in London -> Tue 22 Apr
        self.assertEqual(a.execution_session(dt.date(2025, 4, 17))[0], dt.date(2025, 4, 22))
        # Fri 2026-08-28 -> UK summer bank holiday Mon 31 Aug -> Tue 1 Sep
        self.assertEqual(a.execution_session(dt.date(2026, 8, 28))[0], dt.date(2026, 9, 1))

    def test_dst_mismatch_weeks(self):
        # US on DST, UK not yet (2026-03-13): bound 18:00 EDT = 22:00 UTC; next London open 08:00 GMT Monday
        d = dt.date(2026, 3, 13)
        self.assertEqual(a.publication_bound_utc(d), dt.datetime(2026, 3, 13, 22, 0, tzinfo=UTC))
        sess, close = a.execution_session(d)
        self.assertEqual(sess, dt.date(2026, 3, 16))
        self.assertEqual(close, dt.datetime(2026, 3, 16, 16, 30, tzinfo=UTC))

    def test_execution_open_strictly_after_publication_over_a_year(self):
        cal = a._xlon()
        d = dt.date(2024, 1, 2)
        while d < dt.date(2025, 1, 1):
            if d.weekday() < 5:
                sess, _ = a.execution_session(d, cal)
                import pandas as pd
                self.assertGreater(cal.session_open(pd.Timestamp(sess)).to_pydatetime(), a.publication_bound_utc(d))
                self.assertLessEqual((sess - d).days, 6)
            d += dt.timedelta(days=1)

    def test_monthly_schedule_rows(self):
        obs = [dt.date(2026, 1, 30), dt.date(2026, 2, 27)]
        rows = a.monthly_schedule(obs, [(2026, 1), (2026, 2)])
        self.assertEqual([r["execution_session"] for r in rows], ["2026-02-02", "2026-03-02"])


class TestRecursiveGuard(unittest.TestCase):
    def test_pairs_realised_by_t(self):
        self.assertEqual(a.usable_training_pairs(15, 12), [(0, 12), (1, 13), (2, 14), (3, 15)])
        for s, e in a.usable_training_pairs(100, 12):
            self.assertLessEqual(e, 100)
        self.assertEqual(a.usable_training_pairs(11, 12), [])
        self.assertEqual(len(a.usable_training_pairs(100, 1)), 100)

    def test_bad_horizon(self):
        with self.assertRaises(ValueError):
            a.usable_training_pairs(10, 0)

    def _synthetic(self, n=120, seed=3):
        rnd = random.Random(seed)
        X = [[rnd.gauss(0, 1)] for _ in range(n)]
        y = [0.5 * x[0] + rnd.gauss(0, 1) for x in X]
        return X, y

    def test_future_targets_cannot_change_coefficients(self):
        X, y = self._synthetic()
        t, h = 60, 12
        b0 = a.expanding_coefficients(X, y, t, h, min_pairs=24)
        y2 = list(y)
        for s in range(t - h + 1, len(y2)):
            y2[s] = 1e6  # poison every target not realised by t
        b1 = a.expanding_coefficients(X, y2, t, h, min_pairs=24)
        self.assertEqual(b0, b1)

    def test_unrealised_targets_may_be_none(self):
        X, y = self._synthetic()
        t, h = 60, 12
        y_none = [v if s <= t - h else None for s, v in enumerate(y)]
        self.assertEqual(a.expanding_coefficients(X, y_none, t, h, 24), a.expanding_coefficients(X, y, t, h, 24))

    def test_min_pairs_returns_none(self):
        X, y = self._synthetic()
        self.assertIsNone(a.expanding_coefficients(X, y, 20, 12, min_pairs=24))

    def test_ols_recovers_known_coefficients(self):
        X = [[float(i), float(i * i % 7)] for i in range(50)]
        y = [1.0 + 2.0 * x[0] - 3.0 * x[1] for x in X]
        b = a._ols(X, y)
        for got, want in zip(b, [1.0, 2.0, -3.0]):
            self.assertAlmostEqual(got, want, places=8)


class TestOverlapPower(unittest.TestCase):
    def test_overlap_counts(self):
        # 20 years of monthly annual-horizon regressions: 240 rows, 20 independent outcomes
        self.assertEqual(a.non_overlapping_obs(240, 12), 20)
        self.assertEqual(a.hansen_hodrick_lags(12), 11)
        self.assertEqual(a.hansen_hodrick_lags(1), 0)

    def test_stambaugh_bias_sign_and_scale(self):
        b = a.stambaugh_bias(0.95, 240, -1.0)
        self.assertGreater(b, 0)  # negative sigma_uv biases the slope upward
        self.assertAlmostEqual(b, (1 + 3 * 0.95) / 240)

    def test_ir_and_years(self):
        ir = a.timing_information_ratio(0.01, 12)
        self.assertAlmostEqual(ir, (0.01 / 0.99) ** 0.5 * 12 ** 0.5)
        self.assertAlmostEqual(a.years_to_detect(0.5), (1.96 / 0.5) ** 2)
        self.assertEqual(a.years_to_detect(0.0), float("inf"))
        with self.assertRaises(ValueError):
            a.timing_information_ratio(1.0, 12)

    def test_power_monotone(self):
        self.assertLess(a.power_one_sided(0.2, 10), a.power_one_sided(0.2, 40))
        self.assertAlmostEqual(a.power_one_sided(0.0, 10), 0.05, places=2)


class TestFX(unittest.TestCase):
    def test_fx_cannot_create_active_return(self):
        for fx in (-0.1, 0.0, 0.07):
            self.assertAlmostEqual(a.eur_active_return_unhedged(0.01, 0.01, fx), 0.0)

    def test_fx_scales_active_return(self):
        self.assertAlmostEqual(a.eur_active_return_unhedged(0.03, 0.01, 0.10), 0.02 * 1.10)
        self.assertAlmostEqual(a.eur_active_return_unhedged(0.03, 0.01, 0.0), 0.02)

    def test_fx_dominates_level_return(self):
        # a small bond return can be swamped by FX in the level (not active) return
        self.assertLess(a.eur_return_unhedged(0.01, -0.08), 0)

    def test_hedge_carry_cancels_between_hedged_lines(self):
        rs = a.eur_return_hedged_approx(0.03, 0.002, 0.004, 0.0001)
        rb = a.eur_return_hedged_approx(0.01, 0.002, 0.004, 0.0001)
        self.assertAlmostEqual(rs - rb, 0.02)

    def test_switch_costs(self):
        self.assertEqual(a.switch_cost_bps(5, 5), 10)
        self.assertEqual(a.switch_cost_bps(5, 5, 15, 2), 40)
        self.assertEqual(a.annual_cost_drag_bps(2, 10), 20)


def _gates(**over):
    g = {n: "PASS" for n in a.GATE_NAMES}
    g.update(over)
    return g


class TestDecisionRule(unittest.TestCase):
    def test_all_pass_eligible(self):
        self.assertTrue(a.class_decision(_gates())["eligible"])

    def test_first_fail_sets_code(self):
        d = a.class_decision(_gates(real_time_oos_evidence="FAIL", low_turnover="FAIL"))
        self.assertEqual(d["code"], "REAL_TIME_OOS_EVIDENCE_TOO_WEAK")
        self.assertEqual(d["fails"], ["real_time_oos_evidence", "low_turnover"])

    def test_unresolved_cannot_override_fail(self):
        d = a.class_decision(_gates(in_sample_mechanism="UNRESOLVED", pit_reconstructable="FAIL"))
        self.assertEqual(d["code"], "PIT_DATA_BLOCKED")

    def test_unresolved_only_not_eligible(self):
        d = a.class_decision(_gates(long_only_economic_meaning="UNRESOLVED"))
        self.assertFalse(d["eligible"])

    def test_missing_or_bad_gate(self):
        g = _gates()
        g.pop("low_turnover")
        with self.assertRaises(ValueError):
            a.class_decision(g)
        with self.assertRaises(ValueError):
            a.class_decision(_gates(low_turnover="MAYBE"))

    def test_authorises_exactly_one(self):
        r = a.stage0_decision({"X": _gates(), "Y": _gates()}, ["Y", "X"])
        self.assertEqual(r["decision"], "AUTHORIZE_STAGE1_PREREGISTRATION")
        self.assertEqual(r["selected"], "Y")

    def test_data_blocked_set_aside(self):
        r = a.stage0_decision({"X": _gates(pit_reconstructable="FAIL"),
                               "Y": _gates(real_time_oos_evidence="FAIL")}, ["X", "Y"])
        self.assertEqual(r["decision"], "REAL_TIME_OOS_EVIDENCE_TOO_WEAK")
        self.assertEqual(r["set_aside_data_blocked"], ["X"])

    def test_all_data_blocked(self):
        r = a.stage0_decision({"X": _gates(pit_reconstructable="FAIL"),
                               "Y": _gates(no_proprietary_data="FAIL")}, ["X", "Y"])
        self.assertEqual(r["decision"], "PIT_DATA_BLOCKED")

    def test_abandon_only_if_every_mechanism_fails(self):
        r = a.stage0_decision({"X": _gates(in_sample_mechanism="FAIL"),
                               "Y": _gates(in_sample_mechanism="FAIL", pit_reconstructable="FAIL")}, ["X", "Y"])
        self.assertEqual(r["decision"], "ABANDON_TREASURY_PROGRAMME")
        r = a.stage0_decision({"X": _gates(in_sample_mechanism="FAIL"),
                               "Y": _gates(real_time_oos_evidence="FAIL")}, ["X", "Y"])
        self.assertNotEqual(r["decision"], "ABANDON_TREASURY_PROGRAMME")

    def test_preference_must_cover_classes(self):
        with self.assertRaises(ValueError):
            a.stage0_decision({"X": _gates()}, ["X", "Y"])


class TestBacktestTiming(unittest.TestCase):
    def test_vintage_lag_delays_execution(self):
        d = dt.date(2009, 12, 31)
        live, _ = a.execution_session(d)
        bt, _ = a.execution_session_backtest(d, dt.date(2010, 1, 5))  # measured first vintage containing D
        self.assertEqual(live, dt.date(2010, 1, 4))
        self.assertEqual(bt, dt.date(2010, 1, 6))
        self.assertGreaterEqual(bt, live)

    def test_same_day_vintage_equals_live(self):
        d = dt.date(2016, 6, 30)
        self.assertEqual(a.execution_session_backtest(d, d), a.execution_session(d))

    def test_vintage_before_observation_rejected(self):
        with self.assertRaises(ValueError):
            a.execution_session_backtest(dt.date(2016, 6, 30), dt.date(2016, 6, 29))


class TestRecordedDecision(unittest.TestCase):
    def test_recorded_decision(self):
        r = a.recorded_decision()
        self.assertEqual(r["decision"], "REAL_TIME_OOS_EVIDENCE_TOO_WEAK")
        self.assertEqual(r["binding_class"], "B_SLOPE_FWD_SPREAD")
        self.assertEqual(r["set_aside_data_blocked"], ["C_PIT_TERM_PREMIUM"])
        self.assertIsNone(r["selected"])

    def test_three_classes_only(self):
        self.assertEqual(set(a.CLASS_GATES), {"A_CP_FACTOR", "B_SLOPE_FWD_SPREAD", "C_PIT_TERM_PREMIUM"})
        self.assertEqual(set(a.PREFERENCE), set(a.CLASS_GATES))

    def test_no_class_is_eligible(self):
        for c, g in a.CLASS_GATES.items():
            self.assertFalse(a.class_decision(g)["eligible"], c)

    def test_every_class_fails_real_time_oos(self):
        for g in a.CLASS_GATES.values():
            self.assertEqual(g["real_time_oos_evidence"], "FAIL")

    def test_abandon_not_admissible(self):
        self.assertTrue(any(g["in_sample_mechanism"] == "PASS" for g in a.CLASS_GATES.values()))

    def test_flipping_slope_oos_alone_does_not_authorise(self):
        # even if the OOS gate were PASS, the unresolved long-only gate blocks authorisation
        g = dict(a.CLASS_GATES)
        g["B_SLOPE_FWD_SPREAD"] = dict(g["B_SLOPE_FWD_SPREAD"], real_time_oos_evidence="PASS")
        self.assertNotEqual(a.stage0_decision(g, a.PREFERENCE)["decision"], "AUTHORIZE_STAGE1_PREREGISTRATION")

    def test_acm_set_aside_for_data(self):
        self.assertTrue(a.class_decision(a.CLASS_GATES["C_PIT_TERM_PREMIUM"])["data_blocked"])
        self.assertFalse(a.class_decision(a.CLASS_GATES["B_SLOPE_FWD_SPREAD"])["data_blocked"])

    def test_long_end_backfill_flagged(self):
        self.assertEqual(a.SOURCES["H15_LONG_END"].pit_class, "MINOR_REVISION_RISK")


class TestEnvelopes(unittest.TestCase):
    def test_power_is_low_in_remaining_calendar(self):
        for row in a.power_table():
            self.assertLess(row["power_one_sided_5pct_14.67y"], 0.5)
            self.assertGreater(row["years_to_t1.96_long_only"], 30)

    def test_cost_envelope(self):
        c = a.cost_envelope()
        self.assertEqual(c["eur_account_converting_each_switch"]["per_switch_bps"], 40)
        self.assertEqual(c["usd_lines_held_in_usd_low"]["annual_drag_bps_2_switches"], 12)


if __name__ == "__main__":
    unittest.main()
