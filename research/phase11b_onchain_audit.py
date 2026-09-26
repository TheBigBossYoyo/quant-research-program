"""Phase 11B Stage 0 - native blockchain fundamentals: returns-free audit utilities.

Nothing in this module reads a price, a return, or any on-chain metric time series. It holds:

  1. keccak-256 (pure Python; hashlib's sha3_256 is NOT keccak) and the event topics a log-only
     reconstruction of USDT/USDC supply on Ethereum would filter on;
  2. the causal timing convention: Bitcoin day closure through median-time-past (MTP), Ethereum closure
     through finality (PoS) or confirmation depth (PoW), and the fixed D -> D+1 compute/execution schedule,
     with a model-based (not data-based) estimate of how long Bitcoin day closure takes;
  3. a stablecoin supply taxonomy (minted / authorized / issued / circulating / transferred) and a netting
     illustration that shows where single-chain or summed per-chain supply mismeasures new issuance, and
     which event types can only be recognised with an address label;
  4. the Stage 0 evidence-table schema and validator, the per-mechanism gate table and the decision rule.

CLI:  python phase11b_onchain_audit.py all      (from research/; writes reports/phase11b/onchain_audit/)
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "phase11b" / "onchain_audit"
EVIDENCE_CSV = OUT / "evidence_table.csv"
UTC = dt.timezone.utc

# ---------------------------------------------------------------------------------------------------------------
# 1. keccak-256 and event topics
# ---------------------------------------------------------------------------------------------------------------

_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
# rotation offsets r[x][y]
_ROT = [
    [0, 36, 3, 41, 18],
    [1, 44, 10, 45, 2],
    [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56],
    [27, 20, 39, 8, 14],
]
_MASK = (1 << 64) - 1


def _rotl(v: int, n: int) -> int:
    return ((v << n) | (v >> (64 - n))) & _MASK if n else v


def _keccak_f(a: list[int]) -> list[int]:
    for rnd in range(24):
        c = [a[x] ^ a[x + 5] ^ a[x + 10] ^ a[x + 15] ^ a[x + 20] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rotl(c[(x + 1) % 5], 1) for x in range(5)]
        a = [a[i] ^ d[i % 5] for i in range(25)]
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[y + 5 * ((2 * x + 3 * y) % 5)] = _rotl(a[x + 5 * y], _ROT[x][y])
        a = [b[i] ^ ((~b[(i % 5 + 1) % 5 + 5 * (i // 5)]) & b[(i % 5 + 2) % 5 + 5 * (i // 5)]) for i in range(25)]
        a[0] ^= _RC[rnd]
    return a


def keccak256(data: bytes) -> bytes:
    """Original Keccak-256 as used by Ethereum (padding 0x01...0x80, rate 136 bytes)."""
    rate = 136
    msg = bytearray(data)
    msg.append(0x01)
    while len(msg) % rate:
        msg.append(0x00)
    msg[-1] |= 0x80
    state = [0] * 25
    for off in range(0, len(msg), rate):
        block = msg[off:off + rate]
        for i in range(rate // 8):
            state[i] ^= int.from_bytes(block[8 * i:8 * i + 8], "little")
        state = _keccak_f(state)
    return b"".join(state[i].to_bytes(8, "little") for i in range(4))


def event_topic(signature: str) -> str:
    """topic0 of a Solidity event: keccak256 of the canonical signature (no spaces, no argument names)."""
    if " " in signature or "(" not in signature or not signature.endswith(")"):
        raise ValueError(f"not a canonical event signature: {signature!r}")
    return "0x" + keccak256(signature.encode("ascii")).hex()


# Supply-changing and supply-relevant events a log-only reconstruction would have to replay. The per-contract
# assignment (which contract emits which) is documented in the audit from verified contract source; this table
# only fixes the canonical signatures and their topics.
EVENT_SIGNATURES = {
    "ERC20_Transfer": "Transfer(address,address,uint256)",
    "ERC20_Approval": "Approval(address,address,uint256)",
    "USDT_Issue": "Issue(uint256)",
    "USDT_Redeem": "Redeem(uint256)",
    "USDT_DestroyedBlackFunds": "DestroyedBlackFunds(address,uint256)",
    "USDT_AddedBlackList": "AddedBlackList(address)",
    "USDT_Deprecate": "Deprecate(address)",
    "USDC_Mint": "Mint(address,address,uint256)",
    "USDC_Burn": "Burn(address,uint256)",
    "USDC_Blacklisted": "Blacklisted(address)",
}


def event_topics() -> dict[str, dict[str, str]]:
    return {k: {"signature": s, "topic0": event_topic(s)} for k, s in EVENT_SIGNATURES.items()}


# ---------------------------------------------------------------------------------------------------------------
# 2. Causal timing convention
# ---------------------------------------------------------------------------------------------------------------

BTC_MTP_WINDOW = 11            # consensus: a block's timestamp must exceed the median of the previous 11
BTC_MAX_FUTURE_SECONDS = 7200  # consensus: and must not exceed network-adjusted time + 2 hours
BTC_CONFIRMATIONS = 6          # convention for the signal: the MTP-bearing block must be 6 deep
ETH_POW_CONFIRMATIONS = 64     # conservative depth for PoW-era Ethereum (no protocol finality before the Merge)

COMPUTE_OFFSET = dt.timedelta(hours=6)     # signal for day D may be computed from D+1 06:00 UTC
EXECUTION_OFFSET = dt.timedelta(hours=12)  # and is executed at D+1 12:00 UTC


def median_time_past(timestamps: Sequence[int]) -> int:
    """MTP of the chain ending at the last element: median of the last (up to) 11 timestamps."""
    if not timestamps:
        raise ValueError("empty chain")
    window = sorted(timestamps[-BTC_MTP_WINDOW:])
    return window[len(window) // 2]


def btc_timestamp_valid(prev_timestamps: Sequence[int], ts: int, adjusted_now: int) -> bool:
    """Bitcoin consensus timestamp rule for a new block on top of prev_timestamps."""
    return ts > median_time_past(prev_timestamps) and ts <= adjusted_now + BTC_MAX_FUTURE_SECONDS


def btc_day_closed(timestamps: Sequence[int], cutoff: int, confirmations: int = BTC_CONFIRMATIONS) -> bool:
    """True when no block with timestamp < cutoff can ever be appended to this chain above the confirmed part.

    Take h = the highest block with at least `confirmations` confirmations (tip counts as 1). Any later block j
    satisfies t_j > MTP_{j-1} >= MTP_h because MTP is non-decreasing. So if MTP_h >= cutoff, every block with a
    timestamp before the cutoff is at height <= h and is already `confirmations` deep. The residual risk is a reorg
    deeper than `confirmations`.
    """
    n = len(timestamps)
    h = n - confirmations  # index of the block with exactly `confirmations` confirmations
    if h < 0:
        return False
    return median_time_past(timestamps[: h + 1]) >= cutoff


def btc_day_blocks(timestamps: Sequence[int], start: int, cutoff: int,
                   confirmations: int = BTC_CONFIRMATIONS) -> list[int] | None:
    """Heights (0-based indices) whose timestamp lies in [start, cutoff), or None if the day is not closed yet.

    Bucketing is by block timestamp, which is NOT monotonic in height; a block in day D can sit above a block
    stamped in day D+1."""
    if not btc_day_closed(timestamps, cutoff, confirmations):
        return None
    h = len(timestamps) - confirmations
    return [i for i in range(h + 1) if start <= timestamps[i] < cutoff]


def eth_pos_day_closed(finalized_block_timestamp: int, cutoff: int) -> bool:
    """PoS Ethereum: timestamps are slot times and strictly increase with height, so once the finalized head is
    stamped at or after the cutoff, every block before the cutoff is an ancestor of a finalized block."""
    return finalized_block_timestamp >= cutoff


def eth_pow_day_closed(timestamps: Sequence[int], cutoff: int, confirmations: int = ETH_POW_CONFIRMATIONS) -> bool:
    """PoW Ethereum (to the Merge): child timestamp > parent timestamp, so the day is closed once some block
    stamped >= cutoff is `confirmations` deep. No protocol finality existed; the depth is a convention."""
    h = len(timestamps) - confirmations
    return h >= 0 and timestamps[h] >= cutoff


@dataclass(frozen=True)
class Schedule:
    day: dt.date
    cutoff: dt.datetime
    compute_not_before: dt.datetime
    execution: dt.datetime


def schedule_for(day: dt.date) -> Schedule:
    cutoff = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(0, 0), tzinfo=UTC)
    return Schedule(day, cutoff, cutoff + COMPUTE_OFFSET, cutoff + EXECUTION_OFFSET)


def weekly_schedule_for(execution_monday: dt.date) -> Schedule:
    """Weekly cadence: the signal week is Monday..Sunday UTC by block timestamp, cut at Sunday 24:00, executed
    Monday 12:00 UTC."""
    if execution_monday.weekday() != 0:
        raise ValueError("weekly execution day must be a Monday")
    return schedule_for(execution_monday - dt.timedelta(days=1))


def signal_usable(sched: Schedule, closed_at: dt.datetime | None) -> bool:
    """A day's signal is usable only if the chain closed the day no later than the compute time. Otherwise the
    previous position is held; a late signal is never back-filled into the missed execution."""
    return closed_at is not None and closed_at <= sched.compute_not_before


def btc_closure_delay_quantiles(mean_block_seconds: float = 600.0,
                                probs: Iterable[float] = (0.5, 0.9, 0.99, 0.999, 0.9999)) -> dict[str, float]:
    """MODEL, not data. With exponential inter-block times and honest timestamps, MTP_h >= cutoff once block h is
    the 6th block stamped after the cutoff, and h is 6 deep when the 11th block after the cutoff arrives, so the
    closure delay is Erlang(11, mean_block_seconds). Returns quantiles in minutes."""
    k = (BTC_MTP_WINDOW + 1) // 2 + BTC_CONFIRMATIONS - 1  # 6 + 5 = 11
    from scipy.stats import gamma
    return {f"p{p}": float(gamma.ppf(p, a=k, scale=mean_block_seconds) / 60.0) for p in probs}


# ---------------------------------------------------------------------------------------------------------------
# 3. Stablecoin supply taxonomy and netting illustration
# ---------------------------------------------------------------------------------------------------------------

SUPPLY_TERMS = {
    "MINTED": "created on one chain by the token contract; includes treasury mints, chain-swap mints and "
              "burn-and-mint transfer mints",
    "AUTHORIZED": "minted to the issuer's treasury but not yet sold to a customer (Tether: 'authorized but not "
                  "issued'); on-chain totalSupply includes it",
    "ISSUED": "sold to a customer against fiat and moved out of the treasury; the issuer's liability",
    "CIRCULATING": "issued supply less issuer-held, destroyed/frozen and bridge-locked balances; definition is "
                   "vendor-specific",
    "TRANSFERRED": "moved between holders; changes no supply measure",
}

# kind -> (effect on the emitting chain's native totalSupply, effect on new external dollars, label needed to
# recognise the kind from chain data alone)
EVENT_KINDS: dict[str, tuple[int, int, str | None]] = {
    "MINT_TO_TREASURY": (+1, 0, "issuer treasury address"),
    "ISSUE_FROM_TREASURY": (0, +1, "issuer treasury address"),
    "RETURN_TO_TREASURY": (0, -1, "issuer treasury address"),
    "BURN_FROM_TREASURY": (-1, 0, "issuer treasury address"),
    "MINT_DIRECT_TO_CUSTOMER": (+1, +1, "issuer minter role (contract-visible) and absence of a matching burn"),
    "REDEEM_BURN_DIRECT": (-1, -1, "issuer minter role and absence of a matching mint elsewhere"),
    "CHAIN_SWAP_MINT": (+1, 0, "pairing with a burn on another chain (issuer operation, not labelled on chain)"),
    "CHAIN_SWAP_BURN": (-1, 0, "pairing with a mint on another chain"),
    "BURN_AND_MINT_OUT": (-1, 0, "cross-chain transfer protocol contract (e.g. CCTP)"),
    "BURN_AND_MINT_IN": (+1, 0, "cross-chain transfer protocol contract (e.g. CCTP)"),
    "BRIDGE_LOCK": (0, 0, "bridge escrow contract"),
    "BRIDGE_WRAPPED_MINT": (0, 0, "bridge token contract on the destination chain"),  # separate token contract
    "DESTROY_FROZEN": (-1, 0, None),  # own event on USDT; administrative, not a fiat redemption
    "TRANSFER": (0, 0, None),
}


@dataclass(frozen=True)
class SupplyEvent:
    chain: str
    kind: str
    amount: float

    def __post_init__(self):
        if self.kind not in EVENT_KINDS:
            raise ValueError(f"unknown event kind {self.kind}")
        if self.amount < 0:
            raise ValueError("amount is a magnitude; direction comes from the kind")


def net_supply(events: Iterable[SupplyEvent], wrapped_on: dict[str, str] | None = None) -> dict:
    """Compare supply measures over a set of events.

    native_total_by_chain: change in the issuer contract's totalSupply per chain (what a single-chain log replay
        measures);
    naive_sum_including_wrapped: sum over chains of every token that calls itself USDT/USDC, including bridge-wrapped
        tokens (what a naive multi-chain dashboard sums);
    treasury_adjusted_circulating: native supply less treasury-held balance (needs the treasury label);
    new_external_dollars: fiat that entered minus fiat that left the issuer (the economic quantity of interest);
    labels_required: every label needed to separate the kinds that occurred.
    """
    wrapped_on = wrapped_on or {}
    native: dict[str, float] = {}
    wrapped = 0.0
    treasury = 0.0
    dollars = 0.0
    labels: set[str] = set()
    for e in events:
        d_supply, d_dollars, label = EVENT_KINDS[e.kind]
        native[e.chain] = native.get(e.chain, 0.0) + d_supply * e.amount
        dollars += d_dollars * e.amount
        if e.kind == "MINT_TO_TREASURY":
            treasury += e.amount
        elif e.kind in ("ISSUE_FROM_TREASURY", "BURN_FROM_TREASURY"):
            treasury -= e.amount
        elif e.kind == "RETURN_TO_TREASURY":
            treasury += e.amount
        elif e.kind == "BRIDGE_WRAPPED_MINT":
            wrapped += e.amount
        if label:
            labels.add(label)
    total_native = sum(native.values())
    return {
        "native_total_by_chain": native,
        "native_total_all_chains": total_native,
        "naive_sum_including_wrapped": total_native + wrapped,
        "treasury_adjusted_circulating": total_native - treasury,
        "new_external_dollars": dollars,
        "labels_required": sorted(labels),
    }


# ---------------------------------------------------------------------------------------------------------------
# 4. Evidence table, gates and decision rule
# ---------------------------------------------------------------------------------------------------------------

EVIDENCE_COLUMNS = [
    "paper_id", "mechanism", "predictor", "location", "verification",
    "f1_sample", "f2_timing", "f3_horizon", "f4_info_timestamp", "f5_portfolio", "f6_costs", "f7_universe",
    "f8_period", "f9_post2019", "f10_proprietary", "f11_current_labels", "f12_benchmarks", "key_stat", "stance",
]
EVIDENCE_ENUMS = {
    "mechanism": {"A_ACTIVITY", "B_STABLECOIN", "C_EXCHANGE_FLOW", "GENERAL"},
    "verification": {"VERIFIED_FULLTEXT", "ABSTRACT_ONLY", "SECONDARY", "UNVERIFIED"},
    "f1_sample": {"IS", "OOS", "IS+OOS", "NA"},
    "f2_timing": {"CONTEMPORANEOUS", "PREDICTIVE", "BOTH", "REVERSE", "NA"},
    "f5_portfolio": {"LONG_SHORT", "LONG_ONLY", "REGRESSION_ONLY", "EVENT_STUDY", "TIMING_LONG_CASH", "NA"},
    "f6_costs": {"YES", "NO", "NA"},
    "f7_universe": {"BTC_ETH", "BTC_ONLY", "ALTCOIN_XS", "BOTH", "NA"},
    "f9_post2019": {"YES", "NO", "PARTIAL"},
    "f11_current_labels": {"YES", "NO", "NA", "UNKNOWN"},
    "f12_benchmarks": {"YES", "NO", "PARTIAL", "NOT_TESTED"},
    "stance": {"SUPPORTIVE", "CONTRADICTORY", "MIXED", "NOT_PREDICTIVE_TEST"},
}


def validate_evidence_rows(rows: Sequence[dict]) -> list[str]:
    """Schema check; returns a list of problems (empty = valid)."""
    problems = []
    seen = set()
    for i, r in enumerate(rows):
        missing = [c for c in EVIDENCE_COLUMNS if c not in r or str(r[c]).strip() == ""]
        if missing:
            problems.append(f"row {i}: missing {missing}")
            continue
        for col, allowed in EVIDENCE_ENUMS.items():
            if r[col] not in allowed:
                problems.append(f"row {i}: {col}={r[col]!r} not in {sorted(allowed)}")
        key = (r["paper_id"], r["predictor"], r["mechanism"])
        if key in seen:
            problems.append(f"row {i}: duplicate {key}")
        seen.add(key)
        if r["verification"] == "UNVERIFIED" and r["stance"] == "SUPPORTIVE":
            problems.append(f"row {i}: an UNVERIFIED row cannot be counted as SUPPORTIVE")
    return problems


def load_evidence(path: Path = EVIDENCE_CSV) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarise_evidence(rows: Sequence[dict]) -> dict:
    """Counts that answer the Stage 0 questions directly. 'qualifying' = the combination a retail long-only
    BTC/ETH strategy would need: out-of-sample, predictive, BTC/ETH (or BTC), long-only or timing, with costs."""
    out: dict = {"rows": len(rows), "by_mechanism": {}}
    for mech in sorted(EVIDENCE_ENUMS["mechanism"]):
        sub = [r for r in rows if r["mechanism"] == mech]
        if not sub:
            continue
        qual = [r for r in sub
                if r["f1_sample"] in ("OOS", "IS+OOS") and r["f2_timing"] in ("PREDICTIVE", "BOTH")
                and r["f7_universe"] in ("BTC_ETH", "BTC_ONLY", "BOTH")
                and r["f5_portfolio"] in ("LONG_ONLY", "TIMING_LONG_CASH") and r["f6_costs"] == "YES"
                and r["verification"] != "UNVERIFIED"]
        out["by_mechanism"][mech] = {
            "rows": len(sub),
            "stance": {s: sum(r["stance"] == s for r in sub) for s in sorted(EVIDENCE_ENUMS["stance"])},
            "oos_rows": sum(r["f1_sample"] in ("OOS", "IS+OOS") for r in sub),
            "predictive_rows": sum(r["f2_timing"] in ("PREDICTIVE", "BOTH") for r in sub),
            "btc_eth_rows": sum(r["f7_universe"] in ("BTC_ETH", "BTC_ONLY", "BOTH") for r in sub),
            "with_costs_rows": sum(r["f6_costs"] == "YES" for r in sub),
            "current_labels_applied_rows": sum(r["f11_current_labels"] == "YES" for r in sub),
            "qualifying_rows": [r["paper_id"] + ":" + r["predictor"] for r in qual],
        }
    return out


# The fourteen Stage 0 questions as gates. Each maps to the decision code it would trigger on FAIL.
GATES = {
    "Q1_known_before_return": "IMPLEMENTATION_BLOCKED",
    "Q2_raw_chain_reconstructable": "DATA_BLOCKED",
    "Q3_oos_evidence": "MECHANISM_TOO_WEAK",
    "Q4_btc_eth_evidence": "MECHANISM_TOO_WEAK",
    "Q5_long_only_evidence": "MECHANISM_TOO_WEAK",
    "Q6_large_vs_spot_costs": "MECHANISM_TOO_WEAK",
    "Q7_no_decay": "MECHANISM_TOO_WEAK",
    "Q8_survives_momentum_volume": "MECHANISM_TOO_WEAK",
    "Q9_not_price_response": "MECHANISM_TOO_WEAK",
    "Q10_no_retrospective_labels": "PIT_LABEL_BLOCKED",
    "Q11_protocol_comparability": "DATA_BLOCKED",
    "Q12_low_frequency_viable": "IMPLEMENTATION_BLOCKED",
    "Q13_capital_feasible": "IMPLEMENTATION_BLOCKED",
    "Q14_independent_of_prior_search": "DUPLICATES_PRIOR_CRYPTO_SEARCH",
}
GATE_VALUES = {"PASS", "FAIL", "UNRESOLVED"}
# precedence of blocking codes when several gates fail: causality of the data first, then data availability,
# then duplication, then evidence, then execution
CODE_PRECEDENCE = ["PIT_LABEL_BLOCKED", "DATA_BLOCKED", "DUPLICATES_PRIOR_CRYPTO_SEARCH", "MECHANISM_TOO_WEAK",
                   "IMPLEMENTATION_BLOCKED"]
DECISIONS = {
    "A": "AUTHORIZE_STAGE1_PREREGISTRATION", "B": "DATA_BLOCKED", "C": "PIT_LABEL_BLOCKED",
    "D": "MECHANISM_TOO_WEAK", "E": "DUPLICATES_PRIOR_CRYPTO_SEARCH", "F": "IMPLEMENTATION_BLOCKED",
    "G": "ABANDON_ONCHAIN_PROGRAMME",
}


def mechanism_decision(gates: dict[str, str]) -> dict:
    """UNRESOLVED counts as not passing: a gate that cannot be shown to pass cannot authorise a cell."""
    if set(gates) != set(GATES):
        raise ValueError(f"gate set mismatch: {sorted(set(GATES) ^ set(gates))}")
    bad = {k: v for k, v in gates.items() if v not in GATE_VALUES}
    if bad:
        raise ValueError(f"invalid gate values {bad}")
    failing = [k for k, v in gates.items() if v != "PASS"]
    if not failing:
        return {"primary": DECISIONS["A"], "codes": [], "failing": []}
    codes = sorted({GATES[k] for k in failing}, key=CODE_PRECEDENCE.index)
    return {"primary": codes[0], "codes": codes, "failing": failing,
            "hard_fail": [k for k in failing if gates[k] == "FAIL"]}


def programme_decision(per_mechanism: dict[str, dict[str, str]], chosen: str) -> str:
    """Check that the phase decision `chosen` (a DECISIONS value) is consistent with the gate tables.

    - AUTHORIZE is allowed only when exactly one mechanism passes every gate.
    - With no passing mechanism, the decision must be a blocking code that actually binds: one appearing among
      the hard FAIL codes of every mechanism (it closes all of them), or ABANDON_ONCHAIN_PROGRAMME when every
      mechanism hard-fails on at least one evidence gate AND on at least one data/causality gate, so that neither
      new data nor new evidence alone would reopen it.
    """
    results = {m: mechanism_decision(g) for m, g in per_mechanism.items()}
    passing = [m for m, r in results.items() if r["primary"] == DECISIONS["A"]]
    if chosen == DECISIONS["A"]:
        if len(passing) != 1:
            raise ValueError(f"AUTHORIZE requires exactly one passing mechanism, found {passing}")
        return chosen
    if passing:
        raise ValueError(f"{passing} pass every gate; a blocking decision would discard it")
    hard_codes = {m: {GATES[k] for k in r["hard_fail"]} for m, r in results.items()}
    if chosen == DECISIONS["G"]:
        data_codes = {"PIT_LABEL_BLOCKED", "DATA_BLOCKED"}
        ok = all("MECHANISM_TOO_WEAK" in c and c & data_codes for c in hard_codes.values())
        if not ok:
            raise ValueError("ABANDON requires every mechanism to hard-fail on evidence and on data/causality")
        return chosen
    if chosen not in DECISIONS.values():
        raise ValueError(f"unknown decision {chosen}")
    if not all(chosen in c for c in hard_codes.values()):
        raise ValueError(f"{chosen} is not a hard-fail code of every mechanism: {hard_codes}")
    return chosen


# ---------------------------------------------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------------------------------------------

def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def run_all() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    _write_json(OUT / "event_topics.json", {
        "note": "topic0 = keccak256(canonical signature); pure-Python keccak verified against published vectors "
                "in tests/test_phase11b_onchain_audit.py",
        "topics": event_topics()})
    written.append(OUT / "event_topics.json")

    ex_day = dt.date(2021, 6, 13)  # illustrative calendar date only; no data of any kind is read
    sch = schedule_for(ex_day)
    wk = weekly_schedule_for(dt.date(2021, 6, 14))
    _write_json(OUT / "timing_convention.json", {
        "daily_example": sch.__dict__,
        "weekly_example": wk.__dict__,
        "rules": {
            "bucket": "UTC day D by block timestamp, [D 00:00, D+1 00:00)",
            "btc_closure": f"MTP of the block with {BTC_CONFIRMATIONS} confirmations >= D+1 00:00",
            "eth_pos_closure": "finalized head timestamp >= D+1 00:00",
            "eth_pow_closure": f"a block stamped >= D+1 00:00 is {ETH_POW_CONFIRMATIONS} deep",
            "compute_not_before": "D+1 06:00 UTC, and only if every required chain closed day D by then",
            "execution": "D+1 12:00 UTC; if the signal is not usable, hold the previous position",
        },
        "btc_closure_delay_minutes_model": {
            "mean_block_600s": btc_closure_delay_quantiles(600.0),
            "mean_block_900s_slow_hashrate": btc_closure_delay_quantiles(900.0),
            "note": "Erlang(11) model under exponential block arrivals; not an empirical measurement",
        },
    })
    written.append(OUT / "timing_convention.json")

    swap = [SupplyEvent("ethereum", "CHAIN_SWAP_MINT", 100.0), SupplyEvent("omni", "CHAIN_SWAP_BURN", 100.0)]
    _write_json(OUT / "supply_netting_examples.json", {
        "terms": SUPPLY_TERMS,
        "event_kinds": {k: {"native_supply_sign": v[0], "external_dollar_sign": v[1], "label_needed": v[2]}
                        for k, v in EVENT_KINDS.items()},
        "examples": {
            "chain_swap_completed": net_supply(swap),
            "chain_swap_mint_leg_only": net_supply(swap[:1]),
            "authorized_not_issued": net_supply([SupplyEvent("ethereum", "MINT_TO_TREASURY", 1000.0)]),
            "authorized_then_issued": net_supply([SupplyEvent("ethereum", "MINT_TO_TREASURY", 1000.0),
                                                  SupplyEvent("ethereum", "ISSUE_FROM_TREASURY", 400.0)]),
            "burn_and_mint_transfer": net_supply([SupplyEvent("ethereum", "BURN_AND_MINT_OUT", 50.0),
                                                  SupplyEvent("base", "BURN_AND_MINT_IN", 50.0)]),
            "bridge_lock_and_wrap": net_supply([SupplyEvent("ethereum", "BRIDGE_LOCK", 70.0),
                                                SupplyEvent("arbitrum", "BRIDGE_WRAPPED_MINT", 70.0)]),
            "direct_mint_to_customer": net_supply([SupplyEvent("ethereum", "MINT_DIRECT_TO_CUSTOMER", 25.0)]),
        },
    })
    written.append(OUT / "supply_netting_examples.json")

    summary = None
    if EVIDENCE_CSV.exists():
        rows = load_evidence()
        problems = validate_evidence_rows(rows)
        if problems:
            raise SystemExit("evidence table invalid:\n" + "\n".join(problems))
        summary = summarise_evidence(rows)
        _write_json(OUT / "evidence_summary.json", summary)
        written.append(OUT / "evidence_summary.json")

    gate_file = OUT / "gate_table.json"
    if gate_file.exists():
        g = json.loads(gate_file.read_text(encoding="utf-8"))
        per = {m: mechanism_decision(v) for m, v in g["gates"].items()}
        programme_decision(g["gates"], g["programme_decision"])
        _write_json(OUT / "decision_check.json", {"per_mechanism": per,
                                                   "programme_decision": g["programme_decision"],
                                                   "consistent_with_gates": True})
        written.append(OUT / "decision_check.json")

    manifest = {"source": {"research/phase11b_onchain_audit.py": _sha256(Path(__file__))},
                "outputs": {str(p.relative_to(ROOT)).replace("\\", "/"): _sha256(p) for p in written}}
    if EVIDENCE_CSV.exists():
        manifest["inputs"] = {str(EVIDENCE_CSV.relative_to(ROOT)).replace("\\", "/"): _sha256(EVIDENCE_CSV)}
    if gate_file.exists():
        manifest.setdefault("inputs", {})[str(gate_file.relative_to(ROOT)).replace("\\", "/")] = _sha256(gate_file)
    _write_json(OUT / "MANIFEST.json", manifest)
    return manifest


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] != "all":
        raise SystemExit("usage: python phase11b_onchain_audit.py all")
    print(json.dumps(run_all(), indent=2))
