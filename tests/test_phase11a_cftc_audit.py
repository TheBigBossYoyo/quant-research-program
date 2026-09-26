"""Phase 11A Stage 0 - tests for the CFTC metadata firewall, release-calendar mapping, execution timing
and the hedging-pressure sign convention. No position value, price or return is read by these tests."""
import datetime as dt
import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))

import phase11a_cftc_audit as a  # noqa: E402


def _zip_with(csv_text: str) -> Path:
    tmp = Path(tempfile.mkdtemp()) / "fake.zip"
    with zipfile.ZipFile(tmp, "w") as z:
        z.writestr("annual.txt", csv_text)
    return tmp


class TestMetadataFirewall(unittest.TestCase):
    def test_whitelist_is_not_position_derived(self):
        for cols in a.METADATA_COLUMNS.values():
            for c in cols:
                self.assertFalse(a.is_forbidden(c), c)

    def test_position_columns_are_forbidden(self):
        for c in ["Open Interest (All)", "Commercial Positions-Short (All)", "% of OI-Commercial-Long (All)",
                  "Change in Commercial-Long (All)", "Traders-Commercial-Short (All)",
                  "Concentration-Net LT =4 TDR-Long (All)", "Prod_Merc_Positions_Short_All",
                  "Swap__Positions_Spread_All", "Pct_of_OI_M_Money_Long_All", "Traders_Tot_All",
                  "Conc_Net_LE_4_TDR_Long_All", "Open_Interest_All", "NonRept_Positions_Long_All"]:
            self.assertTrue(a.is_forbidden(c), c)

    def test_exchange_is_not_mistaken_for_change(self):
        self.assertFalse(a.is_forbidden("Market and Exchange Names"))
        self.assertFalse(a.is_forbidden("Market_and_Exchange_Names"))

    def test_read_metadata_returns_only_identity_and_date(self):
        hdr = ",".join(f'"{c}"' for c in a.METADATA_COLUMNS["legacy"] + ["Open Interest (All)",
                                                                          "Commercial Positions-Long (All)"])
        row = '"GOLD - COMMODITY EXCHANGE INC.",240102,2024-01-02,088691,CMX,00,088,512345,123456'
        p = _zip_with(hdr + "\n" + row + "\n")
        df = a.read_metadata(p, "legacy")
        self.assertNotIn("Open Interest (All)", df.columns)
        self.assertNotIn("Commercial Positions-Long (All)", df.columns)
        self.assertEqual(set(df.columns) - {"report_date"}, set(a.METADATA_COLUMNS["legacy"]))
        self.assertEqual(df.report_date.iloc[0], __import__("pandas").Timestamp("2024-01-02"))

    def test_read_metadata_raises_when_identity_missing(self):
        p = _zip_with('"Market and Exchange Names","Open Interest (All)"\n"X",1\n')
        with self.assertRaises(KeyError):
            a.read_metadata(p, "legacy")


class TestScheduleParsing(unittest.TestCase):
    def test_old_layout(self):
        text = ("Release Dates Monday November 27, 2006* Friday December 1, 2006 "
                "Monday July 9, 2007 * Friday July 13, 2007")
        got = a.parse_schedule_text(text)
        self.assertIn((dt.date(2006, 11, 27), True), got)
        self.assertIn((dt.date(2006, 12, 1), False), got)
        self.assertIn((dt.date(2007, 7, 9), True), got)
        self.assertIn((dt.date(2007, 7, 13), False), got)

    def test_new_layout(self):
        text = ("The following is a tentative schedule of releases through 2010. 2009 Dates December 4 11 18 28* "
                "2010 Dates January 4* 8 15 *Delayed release date due to a Federal holiday.")
        got = a.parse_schedule_text(text)
        self.assertIn((dt.date(2009, 12, 28), True), got)
        self.assertIn((dt.date(2010, 1, 4), True), got)
        self.assertIn((dt.date(2010, 1, 8), False), got)
        self.assertEqual(len(got), 7)

    def test_thin_keeps_three_captures_per_year(self):
        stamps = ["20190105000000", "20190301000000", "20190416000000", "20190601000000",
                  "20191101000000", "20191215000000", "20200110000000"]
        self.assertEqual(a._thin(stamps), ["20190105000000", "20190601000000", "20191101000000",
                                           "20200110000000"])


class TestReleaseMapping(unittest.TestCase):
    def test_normal_week_maps_to_friday(self):
        df = a.map_releases(["2016-03-01"], ["2016-03-04", "2016-03-11"], overrides=[], bounds=[],
                            shutdown_windows=[])
        self.assertEqual(df.release_used.iloc[0], dt.date(2016, 3, 4))
        self.assertEqual(df.lag_days.iloc[0], 3)

    def test_holiday_delay_maps_to_monday(self):
        df = a.map_releases(["2016-11-22"], ["2016-11-28"], overrides=[], bounds=[], shutdown_windows=[])
        self.assertEqual(df.release_used.iloc[0], dt.date(2016, 11, 28))

    def test_override_beats_schedule(self):
        df = a.map_releases(["2014-12-23"], ["2014-12-26"], overrides=[("2014-12-23", "2014-12-30", "x")],
                            bounds=[], shutdown_windows=[])
        self.assertEqual(df.release_used.iloc[0], dt.date(2014, 12, 30))
        self.assertEqual(df.status.iloc[0], "documented_override")

    def test_shutdown_without_documentation_is_unresolved(self):
        df = a.map_releases(["2019-01-08"], ["2019-01-11"], overrides=[], bounds=[],
                            shutdown_windows=[("2018-12-24", "2019-03-05", "lapse")])
        self.assertTrue(df.release_used.isna().iloc[0])
        self.assertEqual(df.status.iloc[0], "UNRESOLVED_shutdown")

    def test_upper_bound_used_inside_shutdown(self):
        df = a.map_releases(["2013-10-08"], ["2013-10-11"], overrides=[],
                            bounds=[("2013-10-08", "2013-11-01", "PR")],
                            shutdown_windows=[("2013-10-01", "2013-11-05", "lapse")])
        self.assertEqual(df.release_used.iloc[0], dt.date(2013, 11, 1))
        self.assertEqual(df.status.iloc[0], "documented_upper_bound")

    def test_real_2025_catchup_rows(self):
        df = a.map_releases(["2025-09-30", "2025-11-10"], ["2025-10-03", "2025-11-14"])
        self.assertEqual(list(df.release_used), [dt.date(2025, 11, 19), dt.date(2025, 12, 10)])

    def test_release_never_precedes_report(self):
        for a_, b_, _ in a.OVERRIDES + a.UPPER_BOUNDS:
            self.assertGreater(dt.date.fromisoformat(b_), dt.date.fromisoformat(a_))


class TestExecutionTiming(unittest.TestCase):
    def test_friday_release_trades_monday(self):
        sessions = [dt.date(2024, 3, d) for d in (7, 8, 11, 12)]
        self.assertEqual(a.first_session_after(dt.date(2024, 3, 8), sessions), dt.date(2024, 3, 11))

    def test_release_day_itself_is_never_tradeable(self):
        sessions = [dt.date(2024, 3, 8), dt.date(2024, 3, 11)]
        self.assertNotEqual(a.first_session_after(dt.date(2024, 3, 8), sessions), dt.date(2024, 3, 8))

    def test_monday_release_with_european_holiday_skips_to_next_session(self):
        # e.g. a Monday CFTC release followed by a European holiday on Tuesday
        sessions = [dt.date(2024, 5, 6), dt.date(2024, 5, 8)]
        self.assertEqual(a.first_session_after(dt.date(2024, 5, 6), sessions), dt.date(2024, 5, 8))


class TestSignConvention(unittest.TestCase):
    def test_short_share(self):
        self.assertAlmostEqual(a.hedging_pressure_short_share(20_000, 60_000), 0.75)
        self.assertLess(a.hedging_pressure_short_share(60_000, 20_000), 0.5)

    def test_krt_positive_means_hedgers_net_short(self):
        hp = a.hedging_pressure_net_short_oi(hedger_long=100_000, hedger_short=250_000, open_interest=500_000)
        self.assertAlmostEqual(hp, 0.30)
        self.assertGreater(hp, 0)
        self.assertLess(a.hedging_pressure_net_short_oi(250_000, 100_000, 500_000), 0)

    def test_ghr_convention_is_the_negative(self):
        # Gorton-Hayashi-Rouwenhorst: commercial net LONG / OI -> exactly minus the KRT measure
        long_, short_, oi = 100_000, 250_000, 500_000
        ghr = (long_ - short_) / oi
        self.assertAlmostEqual(ghr, -a.hedging_pressure_net_short_oi(long_, short_, oi))

    def test_smoothing_requires_full_window(self):
        with self.assertRaises(ValueError):
            a.smoothed_hedging_pressure([0.1] * 51)
        self.assertAlmostEqual(a.smoothed_hedging_pressure([0.0] * 26 + [0.2] * 26), 0.1)
        self.assertAlmostEqual(a.smoothed_hedging_pressure([9.9] + [0.1] * 52), 0.1)


if __name__ == "__main__":
    unittest.main()
