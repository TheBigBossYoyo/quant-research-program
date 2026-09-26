"""Phase 11B Stage 0 - the literature evidence table, one row per paper x predictor.

Every value below was transcribed from the sub-audit reports in reports/phase11b/raw/sources/ (L1, L2, L3) and the
decisive statistics were re-checked against the local full texts (git-ignored) before entry. Writing this file
reads no data. Run from the repository root or research/:  python phase11b_evidence_rows.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase11b_onchain_audit as a  # noqa: E402

ROWS = [
    # paper_id, mechanism, predictor, location, verification,
    # f1 sample, f2 timing, f3 horizon, f4 info timestamp, f5 portfolio, f6 costs, f7 universe, f8 period,
    # f9 post2019, f10 proprietary, f11 current labels, f12 benchmarks, key_stat, stance
    ("LiuTsyvinski2018_w24877", "A_ACTIVITY", "BTC wallet-user price-to-dividend ratio",
     "NBER w24877 (Aug 2018 draft) Table 30 p.29", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1..7 days", "daily close t", "REGRESSION_ONLY", "NO", "BTC_ONLY", "2011-01..2018-05",
     "NO", "NO (blockchain.info)", "NA", "NO",
     "coefs 0.13 0.05 -0.13 -0.12 0.05 0.09 0.05; |t| <= 1.36; R2 0.00 at all 7 horizons", "CONTRADICTORY"),
    ("LiuTsyvinski2021_RFS", "A_ACTIVITY", "network factors (wallet users/active addresses/tx/payments growth)",
     "RFS 34(6) abstract (EconPapers); Cong et al. 2022 pp.5-6", "ABSTRACT_ONLY",
     "IS", "CONTEMPORANEOUS", "n/a (factor exposure)", "same period as return", "REGRESSION_ONLY", "NO", "BTC_ETH",
     "to 2018+ (final sample unverified)", "NO", "NO", "NA", "NOT_TESTED",
     "abstract: returns 'exposed to' network factors; momentum and attention 'forecast' returns",
     "NOT_PREDICTIVE_TEST"),
    ("BhambhwaniDelikourasKorniotis2023", "A_ACTIVITY", "network size and computing power factors",
     "JIFMIM 2023 abstract; CEPR DP13724", "ABSTRACT_ONLY",
     "IS", "CONTEMPORANEOUS", "n/a (SDF/factor pricing)", "same period", "REGRESSION_ONLY", "NO", "ALTCOIN_XS",
     "ten large coins; end date unverified", "PARTIAL", "NO", "NA", "PARTIAL",
     "priced-risk claim relative to return-based factors; no forecast test", "NOT_PREDICTIVE_TEST"),
    ("CongKarolyiTangZhao2022", "A_ACTIVITY", "NET: growth in addresses with balance (tercile long-short)",
     "EFMA 2022 draft Table 6 p.38; text p.14; RHS test p.18", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1 week", "formation week t -> week t+1", "LONG_SHORT", "NO", "ALTCOIN_XS",
     "2014-01-22..2021-01-04 (363 weeks); 616-745 coins", "PARTIAL", "YES (IntoTheBlock)", "NA", "PARTIAL",
     "NET mean 3.76%/week t 2.82 gross; weakest of five factors (intercept t 1.82 on the other four)", "SUPPORTIVE"),
    ("Koutmos2018_EL", "A_ACTIVITY", "BTC transaction activity (bivariate VAR)",
     "Economics Letters 167:81-85 abstract (search summary)", "SECONDARY",
     "IS", "REVERSE", "daily (unverified)", "n/a (VAR)", "REGRESSION_ONLY", "NO", "BTC_ONLY", "to ~2017 (unverified)",
     "NO", "NO", "NA", "NOT_TESTED",
     "return shocks move activity more than the reverse; activity does not explain returns", "CONTRADICTORY"),
    ("Kristoufek2015_PLOS", "A_ACTIVITY", "trade transactions vs BTC price (wavelet coherence)",
     "PLoS ONE 10(4) pp.7-8, Fig.3", "VERIFIED_FULLTEXT",
     "IS", "BOTH", "multi-scale (no fixed horizon)", "n/a", "REGRESSION_ONLY", "NO", "BTC_ONLY",
     "2011-09-14..2014-02-28", "NO", "NO", "NA", "NOT_TESTED",
     "transactions lead price at long scales but weaken and lose significance from 01/2013", "MIXED"),
    ("Kristoufek2015_PLOS", "A_ACTIVITY", "hash rate / difficulty vs BTC price",
     "PLoS ONE 10(4) Fig.3 technical drivers", "VERIFIED_FULLTEXT",
     "IS", "REVERSE", "multi-scale", "n/a", "REGRESSION_ONLY", "NO", "BTC_ONLY", "2011-09-14..2014-02-28",
     "NO", "NO", "NA", "NOT_TESTED", "price leads hash rate and difficulty", "CONTRADICTORY"),
    ("Polasik2015_IJEC", "A_ACTIVITY", "monthly change in blockchain transactions",
     "ECB conference version pp.21-24 (Table III)", "VERIFIED_FULLTEXT",
     "IS", "CONTEMPORANEOUS", "same month", "same calendar month as return", "REGRESSION_ONLY", "NO", "BTC_ONLY",
     "2010-07..2014-08", "NO", "NO", "NA", "NOT_TESTED",
     "positive same-month association; authors: 'it may be that the opposite is true'", "MIXED"),
    ("Wheatley2019_RSOS", "A_ACTIVITY", "Metcalfe fit: ln market cap on ln active addresses",
     "arXiv 1803.05663 p.4 and fn 6, 10", "VERIFIED_FULLTEXT",
     "IS", "CONTEMPORANEOUS", "n/a (valuation level)", "same day", "REGRESSION_ONLY", "NO", "BTC_ONLY",
     "2010-07-17..2018-02-26", "NO", "NO (bitinfocharts)", "NA", "NOT_TESTED",
     "beta 1.69, R2 0.956; authors flag spurious-regression and reverse-causality risk", "NOT_PREDICTIVE_TEST"),
    ("Alabi2017_ECRA", "A_ACTIVITY", "Metcalfe fit on BTC/ETH/DASH active addresses", "ECRA 24:23-29 abstract",
     "ABSTRACT_ONLY",
     "IS", "CONTEMPORANEOUS", "n/a (valuation level)", "same day", "REGRESSION_ONLY", "NO", "BOTH", "to 2017",
     "NO", "NO", "NA", "NOT_TESTED", "valuation-level fit", "NOT_PREDICTIVE_TEST"),
    ("Peterson2018_SSRN", "A_ACTIVITY", "Metcalfe fit on wallet counts", "SSRN 3078248 abstract", "ABSTRACT_ONLY",
     "IS", "CONTEMPORANEOUS", "n/a (valuation level)", "same period", "REGRESSION_ONLY", "NO", "BTC_ONLY", "to 2017",
     "NO", "NO", "NA", "NOT_TESTED", "valuation-level fit", "NOT_PREDICTIVE_TEST"),
    ("SakkasUrquhart2024_JIFMIM", "A_ACTIVITY", "P2A (price-to-active-addresses) and NVT factors",
     "JIFMIM 94:102012 Table 2 p.5; selection result pp.9-10", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1 week", "week t close -> week t+1", "LONG_SHORT", "NO", "ALTCOIN_XS",
     "2015-01..2021-11 weekly, 36 coins", "PARTIAL", "YES (Coin Metrics)", "NA", "NO",
     "after market and NDF: 'none of the remaining factors is able to explain the cross-section' (P2A, NVT fail)",
     "CONTRADICTORY"),
    ("LiuTsyvinskiWu2022_JF", "A_ACTIVITY", "price-to-new-address ratio",
     "cited in Cong et al. 2022 fn 11 p.10; absent from the Dec-2019 draft w25882", "SECONDARY",
     "IS", "PREDICTIVE", "unverified", "unverified", "LONG_SHORT", "NO", "ALTCOIN_XS", "unverified", "PARTIAL",
     "NO", "NA", "NOT_TESTED", "'negatively predict future cryptocurrency returns' (secondhand)", "SUPPORTIVE"),
    ("SebastiaoGodinho2021_FI", "A_ACTIVITY", "ML with trading and network-activity attributes",
     "Financial Innovation 7:3 abstract", "ABSTRACT_ONLY",
     "OOS", "PREDICTIVE", "daily", "prior day", "TIMING_LONG_CASH", "NA", "BOTH",
     "2015-08..2019-03 (test from 2018-04)", "NO", "unverified", "NA", "NOT_TESTED",
     "network features' individual contribution not verifiable", "MIXED"),
    ("YaeTian2022_PhysA", "GENERAL", "published in-sample crypto predictors, BTC/ETH/XRP daily",
     "Physica A 598:127379 abstract (IDEAS/EconPapers)", "ABSTRACT_ONLY",
     "OOS", "PREDICTIVE", "daily", "prior day", "REGRESSION_ONLY", "NO", "BTC_ETH", "unverified", "PARTIAL", "NO",
     "NA", "NO",
     "'investor attention and trading volume fail to produce statistically significant out-of-sample "
     "predictability'; only a change in stock-market correlation works (OOS R2 up to 2.69/1.71/2.12%); network "
     "metrics are NOT named in the abstract", "CONTRADICTORY"),
    ("Cakici2024_IRFA", "GENERAL", "ML cross-section (price, alpha, illiquidity, momentum dominate)",
     "IRFA 94:103244 abstract", "ABSTRACT_ONLY",
     "OOS", "PREDICTIVE", "weekly (unverified)", "prior week", "LONG_SHORT", "NA", "ALTCOIN_XS", "2014..2022",
     "YES", "NO", "NA", "NOT_TESTED",
     "alpha concentrated in small illiquid coins; on-chain variables not among the dominant predictors",
     "NOT_PREDICTIVE_TEST"),
    ("Fieberg2024_IRFA", "GENERAL", "non-standard errors across 20,736 crypto sort designs", "IRFA 2024 abstract",
     "ABSTRACT_ONLY",
     "IS", "PREDICTIVE", "monthly", "prior month", "LONG_SHORT", "NA", "ALTCOIN_XS", "unverified", "PARTIAL", "NO",
     "NA", "NOT_TESTED", "average non-standard error 0.19%/month exceeds the standard errors", "NOT_PREDICTIVE_TEST"),
    # ---- B: stablecoin supply
    ("Wei2018_EL", "B_STABLECOIN", "Tether grants (Omni mint events), daily VAR",
     "SSRN 3175876 pp.5-6 (Table 2 cells not quoted: layout ambiguous)", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "daily", "blockchain grant date", "REGRESSION_ONLY", "NO", "BTC_ONLY",
     "2016-12-30..2018-02-20", "NO", "NO", "NO", "NOT_TESTED",
     "'we do not find any evidence suggesting that Tether issuances cause subsequent increases in Bitcoin returns'; "
     "grants follow BTC falls; volume rises", "CONTRADICTORY"),
    ("GriffinShams2020_JF", "B_STABLECOIN", "Tether/BTC flows between exchange clusters after authorisation",
     "JF 75(4) Tables II, V-VII; Section IV.B.1", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1-3 hours; end-of-month", "on-chain tx time (own clustering)", "REGRESSION_ONLY", "NO",
     "BTC_ONLY", "2017-03..2018-03 hourly", "NO", "NO (own clustering, >200 GB)", "UNKNOWN", "PARTIAL",
     "3.855bp per 100 BTC flow (t 2.30) post-authorisation; EOM t -2.85 on all months, -1.26 excluding "
     "Dec-2017/Jan-2018; one wallet cluster", "SUPPORTIVE"),
    ("AnteFiedlerStrehle2021_FRL", "B_STABLECOIN", "issuance events >= USD 1m, 7 stablecoins",
     "BRL WP11 abstract; Table 2, Fig.2 pp.5-8", "VERIFIED_FULLTEXT",
     "IS", "BOTH", "hours (-24h..+24h)", "on-chain issuance time", "EVENT_STUDY", "NO", "BOTH",
     "2019-04..2020-03, 565 events", "YES", "NO", "NO", "NO",
     "market downturn in the prior week; no significant raw returns in the 24h after issuance; abnormal CAAR "
     "+0.31-0.47% pre (-12..-1h) and +0.47-0.69% post (0..24h) vs a falling estimation window; issuance size "
     "irrelevant; 'lack of significant effects for USDC and GUSD' (USDC n=191); authors: demand 'triggers the "
     "issuance'", "MIXED"),
    ("AnteFiedlerStrehle2021_TFSC", "B_STABLECOIN", "stablecoin transfers >= USD 1m by sender/receiver category",
     "TFSC 170:120851 abstract (IDEAS; closed access)", "ABSTRACT_ONLY",
     "IS", "CONTEMPORANEOUS", "hours", "on-chain transfer time (unverified)", "EVENT_STUDY", "NO", "BTC_ONLY",
     "2019-04..2020-03 (secondary)", "YES", "unverified", "UNKNOWN", "NOT_TESTED",
     "abstract: senders and receivers 'categorized as (1) unknown, (2) cryptocurrency exchange or (3) stablecoin "
     "treasury'; effects 'differ across the nine resulting subsamples' - label-dependent, not evidence for a "
     "label-free aggregate", "MIXED"),
    ("Kristoufek2021_FRL", "B_STABLECOIN", "aggregate free-float supply of 9 stablecoins",
     "FRL 43:101991 abstract; pp.2-4; Fig.2 rolling windows", "VERIFIED_FULLTEXT",
     "IS", "REVERSE", "daily VAR (H=100)", "daily close", "REGRESSION_ONLY", "NO", "BTC_ETH",
     "2016-01-01..2021-01-12 (1,839 days)", "YES", "NO (Coin Metrics public)", "NA", "NOT_TESTED",
     "'no evidence of stablecoins boosting the prices'; issuances 'come in reaction'; stable in rolling "
     "365-day windows", "CONTRADICTORY"),
    ("LyonsViswanathNatraj2020_w27136", "B_STABLECOIN", "aggregate Tether flow to the secondary market",
     "NBER w27136 pp.30-32, fn 33, Fig.11", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "h = 0,1,2.. days", "daily", "REGRESSION_ONLY", "NO", "BTC_ETH",
     "full sample and a 2017-03..2018-03 re-run", "YES", "NO", "NO", "PARTIAL",
     "'We find no significant effect on the prices of Bitcoin and Ethereum'; same on the Griffin-Shams window",
     "CONTRADICTORY"),
    ("Saggu2022_FRL", "B_STABLECOIN", "USDT mint/burn events, conditioned on Whale Alert tweets",
     "arXiv 2501.05232 Tables 2-5 pp.9-12", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "5-30 minutes (to 1 day)", "on-chain time vs tweet time", "EVENT_STUDY", "NO", "BTC_ONLY",
     "2014-10-06..2021-01-09 (367 mints)", "PARTIAL", "YES (Whale Alert)", "NA", "PARTIAL",
     "positive 5-30 min response to mints only when tweeted (222 of 367 tweeted); untweeted mints usually ignored; "
     "burns insignificant", "MIXED"),
    ("GrobysHuynh2022_FRL", "B_STABLECOIN", "USDT price jump x lagged USDT return (Bitfinex)",
     "FRL 47:102644 Table 2 p.4", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1 day", "prior day", "REGRESSION_ONLY", "NO", "BTC_ONLY", "2018-11..2021-06", "YES", "NO",
     "NA", "PARTIAL",
     "interaction -3.647 (t -1.92), -3.934 (t -1.99), -8.486 (t -4.24): NEGATIVE sign; R2 <= 0.021", "MIXED"),
    ("GrobysJunttilaKolariSapkota2021_JEF", "B_STABLECOIN", "stablecoin vs BTC volatility (Granger)",
     "JEF 64:207-223 abstract and body", "VERIFIED_FULLTEXT",
     "IS", "REVERSE", "daily", "daily", "REGRESSION_ONLY", "NO", "BTC_ONLY", "to 2020-11-22", "YES", "NO", "NA",
     "NOT_TESTED", "BTC volatility Granger-causes stablecoin volatility, not the reverse", "CONTRADICTORY"),
    # ---- C: exchange reserves / flows
    ("HoangBaur2022_JBF", "C_EXCHANGE_FLOW", "BTC exchange reserve changes",
     "JBF 144:106622 abstract (RePEc); vendor attribution unverified", "ABSTRACT_ONLY",
     "IS", "BOTH", "daily", "daily (vendor reserve series)", "REGRESSION_ONLY", "NO", "BTC_ONLY",
     "2016-01-01..2021-06-01 (secondary)", "PARTIAL", "YES (CryptoQuant per secondary; unverified)", "UNKNOWN",
     "NOT_TESTED",
     "reserve changes 'negatively related to contemporaneous and future bitcoin returns'; label vintage never "
     "discussed", "SUPPORTIVE"),
    ("GriffinShams2020_JF", "C_EXCHANGE_FLOW", "exchange-cluster BTC/USDT net flows",
     "JF 75(4) Section II.A, III.C", "VERIFIED_FULLTEXT",
     "IS", "PREDICTIVE", "1-3 hours", "on-chain tx time", "REGRESSION_ONLY", "NO", "BTC_ONLY", "2017-03..2018-03",
     "NO", "NO (own clustering)", "UNKNOWN", "PARTIAL",
     "top 1% of flow hours carry 58.8% of the BTC buy-and-hold return; BTC-side exchange addresses collected "
     "without dating", "SUPPORTIVE"),
    ("ChiChuHao2025_arXiv", "C_EXCHANGE_FLOW", "BTC/ETH exchange net inflows",
     "arXiv 2411.06327 abstract p.1; Table 1 p.20", "VERIFIED_FULLTEXT",
     "IS+OOS", "PREDICTIVE", "1-6 hours", "prior interval", "REGRESSION_ONLY", "NO", "BTC_ETH",
     "2017-12-16..2023-01-20", "YES", "YES (vendor and labels undisclosed)", "UNKNOWN", "NOT_TESTED",
     "ETH net inflow predicts ETH returns negatively; 'BTC net inflows generally lack predictive power for BTC "
     "returns (except at 4 hours)'", "MIXED"),
    ("ChiChuHao2025_arXiv", "C_EXCHANGE_FLOW", "USDT exchange net inflows", "arXiv 2411.06327 abstract p.1",
     "VERIFIED_FULLTEXT",
     "IS+OOS", "PREDICTIVE", "1-2 hours", "prior interval", "REGRESSION_ONLY", "NO", "BTC_ETH",
     "2017-12-16..2023-01-20", "YES", "YES (vendor and labels undisclosed)", "UNKNOWN", "NOT_TESTED",
     "USDT net inflow into exchanges positively predicts BTC and ETH returns at intraday intervals", "SUPPORTIVE"),
    ("HerremansLow2022_ESWA", "C_EXCHANGE_FLOW", "CryptoQuant flows + whale tweets -> volatility spikes",
     "arXiv 2211.08281 p.4", "VERIFIED_FULLTEXT",
     "IS+OOS", "PREDICTIVE", "next day", "prior day", "NA", "NA", "BTC_ONLY", "2018-01..2021-09", "YES",
     "YES (CryptoQuant)", "UNKNOWN", "NOT_TESTED", "predicts volatility, not return direction",
     "NOT_PREDICTIVE_TEST"),
    ("MagnerSanhueza2025_FRL", "C_EXCHANGE_FLOW", "Whale Alert exchange transfers (TVP-VAR contagion)",
     "FRL 85 abstract (secondary)", "SECONDARY",
     "IS", "PREDICTIVE", "1h/6h/24h", "alert time", "REGRESSION_ONLY", "NO", "BOTH", "unverified", "YES",
     "YES (Whale Alert)", "UNKNOWN", "NOT_TESTED", "effect larger for altcoins than for BTC itself", "MIXED"),
    ("MakarovSchoar2021_w29396", "C_EXCHANGE_FLOW", "entity identification methodology (no return test)",
     "NBER w29396 pp.10-13", "VERIFIED_FULLTEXT",
     "NA", "NA", "n/a", "n/a", "NA", "NA", "BTC_ONLY", "2015..2021-05", "YES",
     "YES (own scraping + Crystal Blockchain)", "UNKNOWN", "NOT_TESTED",
     "entity identification 'incomplete almost by design'", "NOT_PREDICTIVE_TEST"),
]


def rows() -> list[dict]:
    return [dict(zip(a.EVIDENCE_COLUMNS, r)) for r in ROWS]


def write(path: Path = a.EVIDENCE_CSV) -> list[str]:
    rs = rows()
    problems = a.validate_evidence_rows(rs)
    if problems:
        return problems
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=a.EVIDENCE_COLUMNS)
        w.writeheader()
        w.writerows(rs)
    return []


if __name__ == "__main__":
    probs = write()
    if probs:
        raise SystemExit("\n".join(probs))
    print(f"wrote {len(ROWS)} rows to {a.EVIDENCE_CSV}")
