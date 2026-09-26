"""Phase 11B Stage 0 - tests for the returns-free on-chain audit utilities: keccak/event topics, the causal
timing convention (Bitcoin MTP closure, Ethereum finality), the stablecoin supply netting illustration, the
evidence-table schema and the decision rule. No price, return or on-chain metric series is read by these tests."""
import datetime as dt
import hashlib
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research"))

import phase11b_onchain_audit as a  # noqa: E402

UTC = dt.timezone.utc


class TestKeccak(unittest.TestCase):
    def test_published_vectors(self):
        self.assertEqual(a.keccak256(b"").hex(),
                         "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")
        self.assertEqual(a.keccak256(b"abc").hex(),
                         "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")

    def test_erc20_topics(self):
        self.assertEqual(a.event_topic("Transfer(address,address,uint256)"),
                         "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")
        self.assertEqual(a.event_topic("Approval(address,address,uint256)"),
                         "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925")

    def test_keccak_is_not_nist_sha3(self):
        self.assertNotEqual(a.keccak256(b"").hex(), hashlib.sha3_256(b"").hexdigest())

    def test_multi_block_message(self):
        # longer than one 136-byte rate block; must be deterministic and 32 bytes
        m = bytes(range(256)) * 3
        self.assertEqual(len(a.keccak256(m)), 32)
        self.assertEqual(a.keccak256(m), a.keccak256(bytes(m)))
        self.assertNotEqual(a.keccak256(m), a.keccak256(m[:-1]))

    def test_non_canonical_signature_rejected(self):
        for bad in ["Transfer(address from,address to,uint256 value)", "Transfer", "Transfer(address"]:
            with self.assertRaises(ValueError):
                a.event_topic(bad)

    def test_all_topics_distinct(self):
        topics = [v["topic0"] for v in a.event_topics().values()]
        self.assertEqual(len(topics), len(set(topics)))


def _random_valid_chain(rng, n, start=1_600_000_000, mean=600):
    """Timestamps obeying the Bitcoin consensus rule, with miner clock noise that makes them non-monotonic."""
    ts = [start + i * mean for i in range(11)]
    now = ts[-1]
    while len(ts) < n:
        now += int(rng.expovariate(1 / mean)) + 1
        lo = a.median_time_past(ts) + 1
        hi = now + a.BTC_MAX_FUTURE_SECONDS
        cand = now + rng.randint(-3600, 3600)
        ts.append(min(max(cand, lo), hi))
        assert a.btc_timestamp_valid(ts[:-1], ts[-1], now)
    return ts


class TestBitcoinTiming(unittest.TestCase):
    def test_mtp_is_median_of_last_eleven(self):
        ts = list(range(100, 120))
        self.assertEqual(a.median_time_past(ts), 114)  # last 11 = 109..119, median 114
        self.assertEqual(a.median_time_past([5, 1, 3]), 3)

    def test_timestamp_rule(self):
        prev = [100] * 6 + [200] * 5
        self.assertFalse(a.btc_timestamp_valid(prev, 100, 1_000))   # not above MTP (100)
        self.assertTrue(a.btc_timestamp_valid(prev, 101, 1_000))
        self.assertFalse(a.btc_timestamp_valid(prev, 1_000 + 7201, 1_000))

    def test_mtp_non_decreasing_on_valid_chains(self):
        rng = random.Random(20260926)
        for _ in range(50):
            ts = _random_valid_chain(rng, 200)
            mtps = [a.median_time_past(ts[: i + 1]) for i in range(11, len(ts))]
            self.assertTrue(all(x <= y for x, y in zip(mtps, mtps[1:])))

    def test_chains_are_actually_non_monotonic(self):
        rng = random.Random(1)
        ts = _random_valid_chain(rng, 400)
        self.assertTrue(any(y < x for x, y in zip(ts, ts[1:])))

    def test_closed_day_cannot_gain_blocks(self):
        rng = random.Random(7)
        for _ in range(30):
            ts = _random_valid_chain(rng, 300)
            cutoff = ts[150]
            k = next(i for i in range(len(ts)) if a.btc_day_closed(ts[: i + 1], cutoff))
            closed = ts[: k + 1]
            # try to append adversarial blocks stamped as early as consensus allows
            ext = list(closed)
            for _ in range(20):
                ext.append(a.median_time_past(ext) + 1)
                self.assertGreater(ext[-1], cutoff - 1)  # never before the cutoff
            before = a.btc_day_blocks(closed, 0, cutoff)
            after = a.btc_day_blocks(ext, 0, cutoff)
            self.assertEqual(before, after)

    def test_not_closed_returns_none(self):
        ts = [1000 + 600 * i for i in range(30)]
        self.assertIsNone(a.btc_day_blocks(ts, 0, ts[-1] + 1))
        self.assertFalse(a.btc_day_closed(ts[:3], 0))  # too short for 6 confirmations

    def test_out_of_order_block_is_bucketed_by_timestamp(self):
        base = 10_000
        ts = [base + 600 * i for i in range(20)]
        cutoff = ts[-1] + 1
        ts.append(cutoff + 30)        # stamped after the cutoff
        ts.append(cutoff - 50)        # later height, stamped before the cutoff (valid: above MTP)
        self.assertTrue(a.btc_timestamp_valid(ts[:-1], ts[-1], cutoff))
        ts += [cutoff + 600 * j for j in range(1, 16)]
        blocks = a.btc_day_blocks(ts, 0, cutoff)
        self.assertIsNotNone(blocks)
        self.assertIn(21, blocks)
        self.assertNotIn(20, blocks)

    def test_closure_delay_model(self):
        q = a.btc_closure_delay_quantiles(600.0)
        self.assertTrue(100 < q["p0.5"] < 110)        # Erlang(11) median ~ 107 min
        vals = list(q.values())
        self.assertEqual(vals, sorted(vals))
        self.assertLess(q["p0.9999"], 6 * 60)       # 06:00 compute time covers the normal-hashrate tail


class TestEthereumTiming(unittest.TestCase):
    def test_pos_finality(self):
        self.assertFalse(a.eth_pos_day_closed(999, 1000))
        self.assertTrue(a.eth_pos_day_closed(1000, 1000))

    def test_pow_depth(self):
        ts = list(range(1000, 1100))
        cutoff = 1030
        self.assertTrue(a.eth_pow_day_closed(ts, cutoff))
        self.assertFalse(a.eth_pow_day_closed(ts[:30 + 63], cutoff))    # the block stamped 1030 is 63 deep
        self.assertTrue(a.eth_pow_day_closed(ts[:30 + 64], cutoff))     # ... and now 64 deep


class TestSchedule(unittest.TestCase):
    def test_daily(self):
        s = a.schedule_for(dt.date(2021, 6, 13))
        self.assertEqual(s.cutoff, dt.datetime(2021, 6, 14, 0, 0, tzinfo=UTC))
        self.assertEqual(s.compute_not_before, dt.datetime(2021, 6, 14, 6, 0, tzinfo=UTC))
        self.assertEqual(s.execution, dt.datetime(2021, 6, 14, 12, 0, tzinfo=UTC))
        self.assertLess(s.cutoff, s.compute_not_before)
        self.assertLess(s.compute_not_before, s.execution)

    def test_weekly_uses_sunday_cutoff(self):
        s = a.weekly_schedule_for(dt.date(2021, 6, 14))
        self.assertEqual(s.day, dt.date(2021, 6, 13))
        self.assertEqual(s.day.weekday(), 6)
        with self.assertRaises(ValueError):
            a.weekly_schedule_for(dt.date(2021, 6, 15))

    def test_late_closure_is_not_used(self):
        s = a.schedule_for(dt.date(2021, 6, 13))
        self.assertTrue(a.signal_usable(s, s.cutoff + dt.timedelta(hours=2)))
        self.assertFalse(a.signal_usable(s, s.compute_not_before + dt.timedelta(seconds=1)))
        self.assertFalse(a.signal_usable(s, None))


class TestSupplyNetting(unittest.TestCase):
    def E(self, chain, kind, amt):
        return a.SupplyEvent(chain, kind, amt)

    def test_chain_swap(self):
        done = a.net_supply([self.E("ethereum", "CHAIN_SWAP_MINT", 100), self.E("omni", "CHAIN_SWAP_BURN", 100)])
        self.assertEqual(done["native_total_by_chain"]["ethereum"], 100)   # single-chain series sees 'issuance'
        self.assertEqual(done["native_total_all_chains"], 0)
        self.assertEqual(done["new_external_dollars"], 0)
        half = a.net_supply([self.E("ethereum", "CHAIN_SWAP_MINT", 100)])
        self.assertEqual(half["native_total_all_chains"], 100)            # transient double count
        self.assertEqual(half["new_external_dollars"], 0)

    def test_authorized_not_issued(self):
        r = a.net_supply([self.E("ethereum", "MINT_TO_TREASURY", 1000)])
        self.assertEqual(r["native_total_all_chains"], 1000)
        self.assertEqual(r["treasury_adjusted_circulating"], 0)
        self.assertEqual(r["new_external_dollars"], 0)
        r2 = a.net_supply([self.E("ethereum", "MINT_TO_TREASURY", 1000),
                           self.E("ethereum", "ISSUE_FROM_TREASURY", 400)])
        self.assertEqual(r2["treasury_adjusted_circulating"], 400)
        self.assertEqual(r2["new_external_dollars"], 400)
        self.assertIn("ISSUER_TREASURY_ADDRESS", r2["identification_required"])

    def test_bridge_wrap_double_counts_naive_sum(self):
        r = a.net_supply([self.E("ethereum", "BRIDGE_LOCK", 70), self.E("arbitrum", "BRIDGE_WRAPPED_MINT", 70)])
        self.assertEqual(r["native_total_all_chains"], 0)
        self.assertEqual(r["naive_sum_including_wrapped"], 70)
        self.assertEqual(r["new_external_dollars"], 0)

    def test_burn_and_mint_transfer_is_not_issuance(self):
        r = a.net_supply([self.E("ethereum", "BURN_AND_MINT_OUT", 50), self.E("base", "BURN_AND_MINT_IN", 50)])
        self.assertEqual(r["native_total_by_chain"], {"ethereum": -50, "base": 50})
        self.assertEqual(r["new_external_dollars"], 0)

    def test_direct_mint_and_destroy(self):
        self.assertEqual(a.net_supply([self.E("ethereum", "MINT_DIRECT_TO_CUSTOMER", 25)])["new_external_dollars"], 25)
        d = a.net_supply([self.E("ethereum", "DESTROY_FROZEN", 5)])
        self.assertEqual(d["native_total_all_chains"], -5)
        self.assertEqual(d["new_external_dollars"], 0)
        self.assertEqual(d["identification_required"], [])

    def test_identification_classes(self):
        by_class = {}
        for k, v in a.EVENT_KINDS.items():
            self.assertIn(v[2], a.IDENTIFICATION_CLASSES)
            by_class.setdefault(v[2], set()).add(k)
        self.assertEqual(by_class["NONE"], {"TRANSFER", "DESTROY_FROZEN"})
        # cross-chain protocol and bridge contracts are fixed public contracts, not changing entity labels
        self.assertEqual(by_class["FIXED_PUBLIC_CONTRACT"],
                         {"BURN_AND_MINT_OUT", "BURN_AND_MINT_IN", "BRIDGE_LOCK", "BRIDGE_WRAPPED_MINT"})
        self.assertEqual(by_class["OFF_CHAIN_ISSUER_RECORD"], {"CHAIN_SWAP_MINT", "CHAIN_SWAP_BURN"})

    def test_three_supply_objects(self):
        self.assertEqual(a.SUPPLY_OBJECTS["RAW_MINT_BURN_EVENTS"][0], "RAW_CHAIN_RECONSTRUCTABLE")
        self.assertEqual(a.SUPPLY_OBJECTS["TOKEN_TOTAL_SUPPLY"][0], "RAW_CHAIN_RECONSTRUCTABLE")
        self.assertEqual(a.SUPPLY_OBJECTS["ECONOMIC_CIRCULATING_AGGREGATE"][0], "RULE_DEPENDENT")
        # a direct mint/burn on one fixed contract needs no treasury, bridge or swap identification
        r = a.net_supply([self.E("ethereum", "MINT_DIRECT_TO_CUSTOMER", 10),
                          self.E("ethereum", "REDEEM_BURN_DIRECT", 4)])
        self.assertEqual(r["native_total_by_chain"], {"ethereum": 6})
        self.assertEqual(r["identification_required"], ["CONTRACT_ROLE"])

    def test_event_validation(self):
        with self.assertRaises(ValueError):
            a.SupplyEvent("ethereum", "PRINT", 1)
        with self.assertRaises(ValueError):
            a.SupplyEvent("ethereum", "TRANSFER", -1)


def _row(**kw):
    r = {"paper_id": "P1", "mechanism": "A_ACTIVITY", "predictor": "active addresses", "location": "Table 1 p.3",
         "verification": "VERIFIED_FULLTEXT", "f1_sample": "OOS", "f2_timing": "PREDICTIVE", "f3_horizon": "1 week",
         "f4_info_timestamp": "prior week", "f5_portfolio": "TIMING_LONG_CASH", "f6_costs": "YES",
         "f7_universe": "BTC_ONLY", "f8_period": "2015-2020", "f9_post2019": "PARTIAL", "f10_proprietary": "NO",
         "f11_current_labels": "NA", "f12_benchmarks": "YES", "key_stat": "fake", "stance": "SUPPORTIVE"}
    r.update(kw)
    return r


class TestEvidenceTable(unittest.TestCase):
    def test_valid_row(self):
        self.assertEqual(a.validate_evidence_rows([_row()]), [])

    def test_bad_enum_missing_and_duplicate(self):
        self.assertTrue(a.validate_evidence_rows([_row(f1_sample="maybe")]))
        r = _row()
        del r["key_stat"]
        self.assertTrue(a.validate_evidence_rows([r]))
        self.assertTrue(a.validate_evidence_rows([_row(), _row()]))

    def test_unverified_cannot_support(self):
        self.assertTrue(a.validate_evidence_rows([_row(verification="UNVERIFIED")]))
        self.assertEqual(a.validate_evidence_rows([_row(verification="UNVERIFIED", stance="MIXED")]), [])

    def test_summary_qualifying_logic(self):
        rows = [_row(), _row(paper_id="P2", f5_portfolio="LONG_SHORT"), _row(paper_id="P3", f6_costs="NO"),
                _row(paper_id="P4", f7_universe="ALTCOIN_XS"), _row(paper_id="P5", f1_sample="IS")]
        s = a.summarise_evidence(rows)["by_mechanism"]["A_ACTIVITY"]
        self.assertEqual(s["qualifying_rows"], ["P1:active addresses"])
        self.assertEqual(s["rows"], 5)


def _gates(value="PASS", **over):
    g = {k: value for k in a.GATES}
    g.update(over)
    return g


class TestDecisionRule(unittest.TestCase):
    def test_all_pass(self):
        self.assertEqual(a.mechanism_decision(_gates())["primary"], "AUTHORIZE_STAGE1_PREREGISTRATION")

    def test_primary_code_rests_on_hard_fails(self):
        r = a.mechanism_decision(_gates(Q3_oos_evidence="FAIL", Q11_protocol_comparability="UNRESOLVED"))
        self.assertEqual(r["primary"], "MECHANISM_TOO_WEAK")        # an open question does not outrank a failure
        self.assertEqual(r["codes"], ["DATA_BLOCKED", "MECHANISM_TOO_WEAK"])
        self.assertEqual(r["unresolved"], ["Q11_protocol_comparability"])
        r2 = a.mechanism_decision(_gates(Q3_oos_evidence="FAIL", Q11_protocol_comparability="FAIL"))
        self.assertEqual(r2["primary"], "DATA_BLOCKED")

    def test_precedence_and_unresolved(self):
        r = a.mechanism_decision(_gates(Q3_oos_evidence="FAIL", Q10_no_retrospective_labels="FAIL"))
        self.assertEqual(r["primary"], "PIT_LABEL_BLOCKED")
        self.assertEqual(r["codes"], ["PIT_LABEL_BLOCKED", "MECHANISM_TOO_WEAK"])
        r2 = a.mechanism_decision(_gates(Q13_capital_feasible="UNRESOLVED"))
        self.assertEqual(r2["primary"], "IMPLEMENTATION_BLOCKED")
        self.assertEqual(r2["hard_fail"], [])

    def test_gate_set_and_values_checked(self):
        g = _gates()
        del g["Q1_known_before_return"]
        with self.assertRaises(ValueError):
            a.mechanism_decision(g)
        with self.assertRaises(ValueError):
            a.mechanism_decision(_gates(Q1_known_before_return="MAYBE"))

    def test_programme_authorize_needs_exactly_one(self):
        per = {"A": _gates(), "B": _gates(Q3_oos_evidence="FAIL")}
        self.assertEqual(a.programme_decision(per, "AUTHORIZE_STAGE1_PREREGISTRATION"),
                         "AUTHORIZE_STAGE1_PREREGISTRATION")
        with self.assertRaises(ValueError):
            a.programme_decision({"A": _gates(), "B": _gates()}, "AUTHORIZE_STAGE1_PREREGISTRATION")
        with self.assertRaises(ValueError):
            a.programme_decision(per, "MECHANISM_TOO_WEAK")   # would discard a passing mechanism

    def test_programme_hierarchy_sets_aside_label_blocked_branches(self):
        per = {"A": _gates(Q3_oos_evidence="FAIL", Q11_protocol_comparability="UNRESOLVED"),
               "B": _gates(Q9_not_price_response="FAIL", Q8_survives_momentum_volume="UNRESOLVED"),
               "C": _gates(Q10_no_retrospective_labels="FAIL", Q5_long_only_evidence="FAIL")}
        self.assertEqual(a.derive_programme_outcome(per), "MECHANISM_TOO_WEAK")
        self.assertEqual(a.programme_decision(per, "MECHANISM_TOO_WEAK"), "MECHANISM_TOO_WEAK")
        with self.assertRaises(ValueError):
            a.programme_decision(per, "PIT_LABEL_BLOCKED")          # only one branch is label-blocked
        with self.assertRaises(ValueError):
            a.programme_decision(per, "ABANDON_ONCHAIN_PROGRAMME")  # A and B have no data/causality hard fail

    def test_programme_all_label_blocked_and_mixed_remainder(self):
        pit = _gates(Q10_no_retrospective_labels="FAIL", Q3_oos_evidence="FAIL")
        self.assertEqual(a.derive_programme_outcome({"A": pit, "B": pit}), "PIT_LABEL_BLOCKED")
        per = {"A": _gates(Q3_oos_evidence="FAIL"), "B": _gates(Q2_raw_chain_reconstructable="FAIL"), "C": pit}
        self.assertEqual(a.derive_programme_outcome(per), "DATA_BLOCKED")   # precedence among label-free branches
        with self.assertRaises(ValueError):
            a.programme_decision(per, "MECHANISM_TOO_WEAK")

    def test_programme_abandon(self):
        per = {"A": _gates(Q3_oos_evidence="FAIL", Q11_protocol_comparability="FAIL"),
               "B": _gates(Q9_not_price_response="FAIL", Q2_raw_chain_reconstructable="FAIL"),
               "C": _gates(Q10_no_retrospective_labels="FAIL", Q5_long_only_evidence="FAIL")}
        self.assertEqual(a.programme_decision(per, "ABANDON_ONCHAIN_PROGRAMME"), "ABANDON_ONCHAIN_PROGRAMME")


class TestFrozenStage0Record(unittest.TestCase):
    """The recorded evidence table and gate table: schema-valid and consistent with the phase decision."""

    def test_evidence_rows_validate(self):
        import phase11b_evidence_rows as ev
        rows = ev.rows()
        self.assertEqual(a.validate_evidence_rows(rows), [])
        mechs = {r["mechanism"] for r in rows}
        self.assertTrue({"A_ACTIVITY", "B_STABLECOIN", "C_EXCHANGE_FLOW"} <= mechs)
        for m in ("A_ACTIVITY", "B_STABLECOIN", "C_EXCHANGE_FLOW"):
            stances = {r["stance"] for r in rows if r["mechanism"] == m}
            self.assertTrue(stances & {"CONTRADICTORY", "MIXED"}, f"{m} has no contradictory/mixed evidence row")

    def test_gate_table_supports_recorded_decision(self):
        path = Path(__file__).resolve().parents[1] / "reports" / "phase11b" / "onchain_audit" / "gate_table.json"
        g = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(a.programme_decision(g["gates"], g["programme_decision"]), "MECHANISM_TOO_WEAK")
        with self.assertRaises(ValueError):
            a.programme_decision(g["gates"], "AUTHORIZE_STAGE1_PREREGISTRATION")
        with self.assertRaises(ValueError):   # only the exchange-flow branch is label-blocked
            a.programme_decision(g["gates"], "PIT_LABEL_BLOCKED")
        with self.assertRaises(ValueError):   # activity and label-free stablecoin supply have no data hard fail
            a.programme_decision(g["gates"], "ABANDON_ONCHAIN_PROGRAMME")
        primaries = {m: a.mechanism_decision(v)["primary"] for m, v in g["gates"].items()}
        self.assertEqual(primaries, {"A_ACTIVITY": "MECHANISM_TOO_WEAK", "B_STABLECOIN": "MECHANISM_TOO_WEAK",
                                     "C_EXCHANGE_FLOW": "PIT_LABEL_BLOCKED"})
        self.assertEqual(g["per_mechanism_decision"], primaries)


class TestFirewallAndCli(unittest.TestCase):
    def test_module_has_no_network_or_price_access(self):
        src = Path(a.__file__).read_text(encoding="utf-8")
        for token in ["import requests", "urllib", "http://", "https://", "PriceUSD", "ReferenceRate", "klines",
                      "read_parquet", "data/raw"]:
            self.assertNotIn(token, src, token)

    def test_run_all_writes_manifest(self):
        tmp = Path(tempfile.mkdtemp())
        old_out, old_ev, old_root = a.OUT, a.EVIDENCE_CSV, a.ROOT
        try:
            a.ROOT = tmp
            a.OUT = tmp / "reports" / "phase11b" / "onchain_audit"
            a.EVIDENCE_CSV = a.OUT / "evidence_table.csv"
            m = a.run_all()
            self.assertIn("reports/phase11b/onchain_audit/event_topics.json", m["outputs"])
            t = json.loads((a.OUT / "timing_convention.json").read_text(encoding="utf-8"))
            self.assertIn("btc_closure", t["rules"])
            s = json.loads((a.OUT / "supply_netting_examples.json").read_text(encoding="utf-8"))
            self.assertEqual(s["examples"]["chain_swap_completed"]["new_external_dollars"], 0)
        finally:
            a.OUT, a.EVIDENCE_CSV, a.ROOT = old_out, old_ev, old_root


if __name__ == "__main__":
    unittest.main()
