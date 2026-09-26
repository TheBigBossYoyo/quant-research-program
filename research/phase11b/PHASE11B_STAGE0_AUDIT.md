# PHASE 11B — STAGE 0 AUDIT: native blockchain fundamentals

Date: 2026-09-26. **FINAL: `NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0` → decision D `MECHANISM_TOO_WEAK`; Stage 1 `NOT_AUTHORIZED`.**
**Information-source audit only. This is not a backtest. No price, return, or on-chain metric series of any date was loaded.**

Evidence: `reports/phase11b/raw/`. `literature/SOURCES.txt` is the tracked source log; the papers are local and git-ignored.
`sources/` holds six sub-audit reports (L1 network activity, L2 stablecoins, L3 exchange flows and wallet labels, D1 raw
chain and timing, S1 stablecoin mechanics, V1 venues). The web captures behind them are local and git-ignored, with URL
indexes tracked. `RAW_MANIFEST_SHA256.txt` hashes all 130 raw files. Machine outputs are in
`reports/phase11b/onchain_audit/`. Code: `research/phase11b_onchain_audit.py` (returns-free utilities) and
`research/phase11b_evidence_rows.py` (the evidence table). Tests: `tests/test_phase11b_onchain_audit.py` (40 tests).

---

## 0. Lock and scope declarations (read first)

| Item | Status |
| --- | --- |
| **Phase 11B** | **`NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0`** |
| **Decision** | **D — `MECHANISM_TOO_WEAK`** |
| **Stage 1** | **`NOT_AUTHORIZED`**: no preregistration, no experiment ID, no exploratory test |
| **Primary mechanism surviving** | **none (zero candidates)** |
| **Strategy cells added** | **0** |
| **Cumulative strategy-cell ledger** | **490** |
| BTC / ETH / altcoin returns, Sharpe, CAGR, event-study returns inspected | **NO** |
| Crypto price, OHLCV, reference-rate or market-cap series loaded | **NO** (no request was made for any) |
| On-chain metric *values* loaded (activity counts, supply, flows) | **NO.** Only metric catalogs and definitions (Coin Metrics catalog JSON: metric names, coverage dates, definitions) and anonymous S3 *object listings* of one 2021-06-15 partition (file names and sizes) were read. |
| Correlation, regression, ML fit or threshold search involving prices | **NONE** |
| Old crypto holdout (2025 validation, 2026 final) | **CLOSED.** No file under `data/` was opened; nothing dated 2025-01-01 or later was fetched except current documentation. |
| Equity validation 2018-01..2021-12 | **NOT OPENED** |
| Equity final holdout 2022-01..2026-08 | **NOT READ** |
| Old strategy-return files | **not opened** (only experiment *descriptions* in `EXPERIMENTS.md` and the phase conclusions were read, for the duplication audit in §11) |
| Third-party papers and web captures | local and git-ignored. Captures of ETP product pages that might embed prices were moved unread to `sources/V1_snapshots/QUARANTINE_UNREAD_MAY_CONTAIN_PRICE_DATA/`. |
| Literature numbers quoted below | published third-party results, not computed here. The decisive ones carry `[re-checked]`: the main audit re-read them in the local full text. |

**Crypto cell count, corrected for the record.** The brief refers to a 367-cell crypto search. That is the Phase 1–2
count. The crypto programme through Phase 5 consumed **388** cells (Phase 3 → 384, the Phase 4 frozen replication → 385,
Phase 5 → 388; `PLAN.md`). Independence in §11 is judged against all 388.

---

## 1. Executive conclusion

# STAGE 0 DECISION: D — MECHANISM_TOO_WEAK

No native-blockchain variable in the three permitted classes deserves a strategy cell. Each class fails on published
evidence. Each class also fails on at least one data or causality ground. The evidence failure is the one that binds all
three: it would survive every data remedy available to us.

| Class | Primary blocking code (precedence rule) | All blocking codes | One-line reason |
| --- | --- | --- | --- |
| A. Native network activity | `DATA_BLOCKED` (protocol comparability) | DATA, MECHANISM (+ duplication unresolved) | Activity co-moves with or follows price. The only BTC-level predictive test in full text has R² 0.00. Positive results are gross, long-short, altcoin cross-sections, and do not survive market controls in the most careful recent test. Raw counts also measure different things before and after SegWit/batching, inscriptions (2023), Runes (2024), L2 and blobs (2024). |
| B. Stablecoin net supply | `PIT_LABEL_BLOCKED` | PIT, DATA, MECHANISM | The broadest and longest studies find issuance *responds* to crypto prices. The one strong supply-push result is one wallet cluster in one 13-month episode, and it does not replicate in aggregate data. There is no OOS test and no long-only test anywhere. Net new issuance cannot be separated from chain swaps and bridges without issuer labels that Tether does not publish. |
| C. Exchange reserves / flows | `PIT_LABEL_BLOCKED` | PIT, DATA, MECHANISM, IMPLEMENTATION | No wallet-label source is point-in-time for 2019–2024. Glassnode PIT history starts at each metric's enablement (July 2025 for most); PoR address lists start in Nov 2022. The free Coin Metrics flow series is the restated kind. The published evidence is intraday and, for BTC, null. |

**Why D and not another code.** `programme_decision()` in the audit code only accepts a phase code that is a hard FAIL in
every mechanism, or ABANDON under a stricter rule (§15.2). Two codes qualify, `MECHANISM_TOO_WEAK` and `DATA_BLOCKED`. D is
chosen because it is the constraint we cannot remove. Perfect data would not create the missing evidence:
- label-free Bitcoin counts exist;
- USDC supply replays exactly from events;
- vendor PIT flows accrue from 2025.

Nothing in the literature shows a long-only, weekly or monthly, after-cost BTC/ETH effect for any of the three.
`evidence_summary.json` counts **zero qualifying rows** in every class, where a qualifying row is OOS, predictive,
BTC/ETH, long-only or long/cash, and after costs. ABANDON (G) is discussed and rejected in §15.2.

**What is not being claimed.** That blockchain data are useless, that no on-chain effect exists anywhere (§3 records an
altcoin cross-sectional factor that does survive), or that a Stage 1 test would certainly fail. The claim is narrower. On
the evidence available before any price is opened, no single simple, causal, reconstructable blockchain variable has
a case strong enough to spend one cell on it. The search has already used 490 cells, 388 of them in crypto.

---

## 2. Literature audit

Thirty-three paper×predictor rows are in `reports/phase11b/onchain_audit/evidence_table.csv`, each with the twelve
required fields. `research/phase11b_evidence_rows.py` validates the schema. An UNVERIFIED row cannot count as supportive.
Per-paper detail, quotes and page locations are in `sources/L1_*.md`, `L2_*.md` and `L3_*.md`. The two tables below are
the required summaries. Field key: (1) IS/OOS, (2) timing, (3) horizon, (4) information timestamp, (5) portfolio,
(6) costs, (7) universe, (8) period, (9) post-2019, (10) proprietary data, (11) current labels applied historically,
(12) survives benchmarks.

### 2.1 SUPPORTIVE_EVIDENCE_TABLE

| Paper | Mech | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) | Key statistic and location | Verif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cong, Karolyi, Tang & Zhao (EFMA 2022 draft) | A | IS | predictive | 1 week | formation week → next week | long-short | no | 616–745 altcoins | 2014-01..2021-01 | partial | IntoTheBlock | n/a | partial: weakest of five factors | NET (address-growth tercile spread) 3.76%/week, t 2.82, gross; its intercept against the other four factors has t 1.82. Table 6 p.38, p.14, p.18 [re-checked] | full text |
| Liu, Tsyvinski & Wu (JF 2022) | A | IS | predictive | ? | ? | long-short | no | altcoins | ? | partial | no | n/a | ? | "price-to-new-address ratios negatively predict" returns. Known only from Cong et al. fn 11; the Dec-2019 draft has no address variable. | secondary |
| Griffin & Shams (JF 2020) | B, C | IS | predictive | 1–3 h; EOM | on-chain tx time, own clustering | regression | no | BTC (+6 alts) | 2017-03..2018-03 | no | own pipeline | BTC-side exchange addresses undated | partial | +3.855 bp per 100 BTC flow (t 2.30) after authorisation (Table II). EOM t −2.85, but **−1.26 without Dec-2017 and Jan-2018** (IV.B.1) [re-checked]. One wallet cluster, one exchange. | full text |
| Hoang & Baur (JBF 2022) | C | IS | both | daily | vendor reserve series | regression | no | BTC | 2016-01..2021-06 | partial | CryptoQuant per secondary (unverified) | **never discussed** | not tested | exchange reserve changes "negatively related to contemporaneous and future" BTC returns (abstract) | abstract |
| Chi, Chu & Hao (arXiv 2411.06327, 2025) | C | IS+OOS | predictive | 1–2 h | prior interval | regression | no (options overlay only) | BTC, ETH | 2017-12..2023-01 | yes | vendor and labels undisclosed | unknown | not tested | USDT net inflow into exchanges predicts BTC and ETH returns positively at intraday intervals (abstract) [re-checked] | full text |

### 2.2 CONTRADICTORY_EVIDENCE_TABLE

| Paper | Mech | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) | Key statistic and location | Verif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Liu & Tsyvinski (NBER w24877, 2018 draft) | A | IS | predictive (null) | 1–7 days | daily close | regression | no | BTC | 2011-01..2018-05 | no | no | n/a | no | BTC wallet-user price-to-dividend ratio: coefficients 0.13/0.05/−0.13/−0.12/0.05/0.09/0.05, max \|t\| 1.36, **R² 0.00 at all seven horizons**. Table 30 p.29 [re-checked] | full text |
| Liu & Tsyvinski (RFS 2021) | A | IS | contemporaneous | factor exposure | same period | regression | no | BTC/ETH/XRP | to ≥2018 | no | no | n/a | n/a | returns are "exposed to" network factors, while momentum and attention "forecast" returns (published abstract) | abstract |
| Sakkas & Urquhart (JIFMIM 2024) | A | IS, multiple-testing aware | predictive | 1 week | week-t close | long-short | no | 36 coins | 2015-01..2021-11 | partial | Coin Metrics | n/a | **no** | after the market and NDF factors, "none of the remaining factors is able to explain the cross-section". P2A (price-to-active-addresses) and NVT fail. pp.9–10 [re-checked] | full text |
| Kristoufek (PLoS ONE 2015) | A | IS | price leads hash rate/difficulty; transactions lead only early | multi-scale | — | — | no | BTC | 2011-09..2014-02 | no | no | n/a | — | transaction lead "becomes weaker in time", not significant from 01/2013; price leads mining activity. Fig.3 | full text |
| Koutmos (Econ. Letters 2018) | A | IS | reverse | daily | — | VAR | no | BTC | ≤2017 | no | no | n/a | — | return shocks move transaction activity more than the reverse | secondary |
| Yae & Tian (Physica A 2022) | general | **OOS** | predictive | daily | prior day | regression | no | BTC/ETH/XRP | ≤2021 | partial | no | n/a | no | "investor attention and trading volume fail to produce statistically significant out-of-sample predictability"; only a change in stock-market correlation works (OOS R² ≤ 2.69%). **Network metrics are not named in the abstract** (the L1 claim that they were is corrected here). | abstract |
| Wei (Econ. Letters 2018) | B | IS | predictive (null) | daily | on-chain grant date | VAR | no | BTC | 2016-12..2018-02 | no | no | none | — | "we do not find any evidence suggesting that Tether issuances cause subsequent increases in Bitcoin returns". Grants follow BTC falls; volume rises. p.6 [re-checked] | full text |
| Kristoufek (FRL 2021) | B | IS, rolling | **reverse** | daily VAR | daily | FEVD | no | BTC/ETH/XRP | 2016-01..2021-01 | yes | Coin Metrics public | n/a | — | "no evidence of stablecoins boosting the prices"; issuances "come in reaction" to price changes. Holds in rolling 365-day windows [re-checked] | full text |
| Lyons & Viswanath-Natraj (NBER w27136, 2020) | B | IS | predictive (null) | days | daily | local projections | no | BTC/ETH | full sample; Griffin-Shams window re-run | yes | no | none | controls for hash rate, addresses | "no significant effect on the prices of Bitcoin and Ethereum", same on Mar-2017..Mar-2018. pp.30–32, fn 33 [re-checked] | full text |
| Grobys, Junttila, Kolari & Sapkota (JEF 2021) | B | IS | reverse | daily | — | Granger | no | BTC | to 2020-11 | yes | no | n/a | — | BTC volatility Granger-causes stablecoin volatility, not the reverse | full text |

### 2.3 Mixed and non-predictive rows (in the CSV, summarised)

- **Ante, Fiedler & Strehle (FRL 2021)** [re-checked]. Event study of 565 issuances of USD 1m or more, 2019-04..2020-03.
  Crypto markets fall in the week *before* issuance. The ±24 h window shows positive abnormal returns on both sides
  (CAAR +0.31–0.47% in the 12 h before, +0.47–0.69% in the 24 h after). Issuance *size* does not matter, and the sign of
  the pre-event move differs by issuer. This fits a response-plus-reversion pattern, not new information. The
  issuance events come from chain data, so chain-swap mints are counted as issuance (§9).
- **Saggu (FRL 2022)** [re-checked]. BTC responds to USDT mints within 5–30 minutes, but mostly when Whale Alert
  tweets them (222 of 367 were tweeted). Untweeted mints are "usually" ignored, and burns are insignificant. This is a
  news-arrival effect measured in minutes, not on-chain predictability.
- **Grobys & Huynh (FRL 2022)** [re-checked]. USDT price jumps predict *negative* next-day BTC returns (−3.65 to
  −8.49%, t −1.92 to −4.24), with R² at most 0.021. The sign is opposite to the supply-push story.
- **Chi, Chu & Hao (2025)**. ETH net inflows predict ETH returns negatively, but "BTC net inflows generally lack predictive
  power for BTC returns (except at 4 hours)" [re-checked].
- **Kristoufek (2015) transactions**, Polasik et al. (2015, same-month, the authors' own reverse-causality caveat),
  Sebastião & Godinho (2021, ML, abstract only), Ante et al. (TFSC 2021, closed access), Magner & Sanhueza (2025,
  secondary).
- **Valuation fits, not predictive tests**: Wheatley et al. (2019), Metcalfe fit R² 0.956, where the authors themselves
  flag spurious regression and reverse causality. Alabi (2017) and Peterson (2018), abstract only.
- **Methodology or context**: Makarov & Schoar (2021, entity identification "incomplete almost by design"),
  Herremans & Low (2022, volatility only), Bhambhwani et al. (2023, priced exposure), Cakici et al. (2024) and
  Fieberg et al. (2024), which are general crypto cross-section studies. BIS/NBER/Banque de France papers on stablecoin
  demand composition are in §10.

### 2.4 Version and verification caveats

- Liu & Tsyvinski: the full text held is the Aug-2018 draft. The published RFS version is abstract-only here. The
  abstract's own wording (exposure versus forecast) and Cong et al.'s paraphrase agree.
- Liu, Tsyvinski & Wu: the price-to-new-address result is secondhand and absent from the draft held.
- Griffin & Shams was read from the publisher's open-access HTML, rendered in a browser (no sign-in).
- Wei (2018), Table 2: VAR cells were not quoted because the layout is ambiguous. Only the author's prose conclusion is
  used.
- Hoang & Baur: data vendor unverified; two secondary accounts disagree (CryptoQuant vs WalletExplorer).
- "Wang, Ma & Wu (2020)", named in the brief, was not found and is not invented.
- The DR Press 2025 VAR paper is excluded. Its predictor is peg deviation, not issuance, and the venue is unverified.
- Web-search auto-summaries produced at least two false claims during the sub-audits: Makarov & Schoar using
  Chainalysis labels, and network metrics in Yae & Tian's abstract. Both were caught against primary text. No statistic
  from a search summary is used as decisive evidence.

---

## 3. The conflict: older OOS failure versus newer "OOS predictability"

The newer positive results and the older negative ones are mostly not about the same object:

| Driver of the difference | What the audited papers show |
| --- | --- |
| **Cross-sectional altcoin universes** | Every positive on-chain *return* result in full text is a weekly long-short sort across tens to hundreds of coins: Cong et al. (616–745), Sakkas & Urquhart (36). Cong et al.'s value/network sorts are strongest and monotonic in the *smallest* coins. The BTC-level tests are null (Liu & Tsyvinski Table 30) or reverse (Kristoufek 2015, Koutmos). |
| **Small / illiquid tokens and costs** | No positive result nets costs. The Phase 1–5 search already showed that altcoin cross-sectional spreads die on costs, minimum notionals and delistings (E016/E017: 860 of 8,508 positions below minimum notional at 500 USDT; top-ten names carry 106% of P&L). |
| **Long-short versus long-only** | Every positive result is a spread or an event-window CAAR. None reports the long leg. Sakkas & Urquhart's only long-only portfolio pairs the market with the NDF *concentration* factor, not an activity variable. |
| **Sample period and decay** | Kristoufek (2015): transactions lead price only until 2013. Griffin & Shams: 2017–18 only, and the EOM effect disappears without two months. The latest broad samples (Kristoufek 2021, to Jan-2021) show response, not prediction. No audited paper covers the 2024+ spot-ETF era. |
| **ML flexibility and factor mining** | The multiple-testing-aware procedure (Sakkas & Urquhart, Harvey-Liu bootstrap) *rejects* the activity variables. Fieberg et al. (abstract): non-standard errors across 20,736 designs exceed standard errors. Flexible ML results with on-chain features (Mudassir, Jagannath, Sebastião & Godinho) could not be verified in full text, and none reports after-cost long-only BTC/ETH value. |
| **Predictor definitions** | "On-chain" results mix price-scaled valuation ratios (P2A, NVT, MVRV — price in the numerator), activity growth, and label-dependent flows. Sakkas & Urquhart's survivor, NDF, is a *supply-concentration* variable, outside all three permitted classes. |
| **Data revisions and labels** | Flow results rest on vendor labels whose vintage is never disclosed (Hoang & Baur, Chi et al.). Vendors document retroactive recomputation (§7). |
| **Genuinely new structure** | The one well-identified newer finding is intraday: USDT exchange inflows lead BTC/ETH by 1–2 hours (Chi et al.). It is label-dependent, intraday, and at odds with the same paper's null for BTC's own flows. Nothing at weekly or monthly horizons. |

**Treating the conflict as evidence.** The pattern — positive in-sample on altcoin spreads, gross of costs, fading over
time and with better multiple-testing control, null or reversed on BTC — is what a weak or contemporaneous relationship
would produce. The newest paper is not privileged. The most careful recent test (Sakkas & Urquhart 2024) is on the
negative side for activity.

---

## 4. Source-quality classification of candidate metrics

A = RAW_CHAIN_RECONSTRUCTABLE, B = PUBLIC_VENDOR_REPRODUCIBLE, C = VENDOR_TRANSFORMED, D = PIT_LABEL_DEPENDENT,
E = PROPRIETARY. Sources: `sources/D1_*`, `S1_*`, `L3_*`; the Coin Metrics catalog was read from
`D1_snapshots/*catalog-v2*.json`.

| Metric | Class | Note |
| --- | --- | --- |
| BTC transaction count, block count, fees in BTC, issuance | **A** | Deterministic from raw blocks. Fees need prevout values (UTXO index or `getblock` verbosity 3 with undo data). |
| BTC active / new addresses | **A**, definition-dependent | Deterministic once the address rule is fixed. P2PK, bare multisig, OP_RETURN and non-standard scripts have no canonical address. Vendors differ. Llanos (2026) deliberately publishes no address series. |
| ETH transaction count, EOA senders, ERC-20 Transfer counts | **A** | From block and log history. A full node since EIP-4444 partial expiry (2025-07-08) needs era/era1 files for pre-Merge history. |
| ETH "active addresses" including internal transfers | **A** (needs traces) | Traces need historical-state re-execution (archive class) or the AWS `eth.traces` table (B). |
| USDC totalSupply on Ethereum | **A** | Exact replay of Mint/Burn (+Transfer 0x0) events from contract creation (S1 §4, verified contract source). |
| USDT totalSupply on Ethereum | **A** | Exact replay of Issue(+)/Redeem(−)/DestroyedBlackFunds(−). **None of the three emits Transfer**, so a Transfer-only replay is wrong. Assumes `deprecated` was never set. |
| USDT circulating (less treasury) | **D** | Treasury address from a third-party label (Etherscan "Tether: Treasury"). No issuer-published dated list was found. |
| Net new USDT+USDC issuance (ex chain swaps, CCTP, bridges) | **D** | Swap mints are indistinguishable on chain. USDC CCTP/bridge contracts are public (B-like), but USDT swap and treasury labels are not. |
| Coin Metrics Community AdrActCnt, TxCnt, SplyCur, FeeTotNtv (BTC, ETH, usdt_eth, usdc_eth, usdt_trx) | **B/C** | Free, CC BY-NC 4.0, definitions published. The implementation is not open (Llanos 2026: auditability "Medium"). AdrNewCnt and TxTfrValAdjNtv are **not** in the free tier. |
| Coin Metrics Community FlowInExNtv / FlowOutExNtv / SplyExNtv (BTC from 2011-04-24, ETH from 2015-07-30) | **D** | **Correction to L3**: the standard flows *are* in the free catalog (`community: true`). They are the series whose "past values can change when new entity addresses are discovered later". The PIT variant is separate. |
| Glassnode / CryptoQuant / Arkham / Nansen exchange balances | **D/E** | §7. |
| AWS Public Blockchain Data (s3://aws-public-blockchain) | **B** | Anonymous listing verified. BTC from Bitcoin Core v22.0 with resolved input addresses; ETH from Erigon with logs, token_transfers and traces. MIT-0 licence, marked "experimental". |
| Google BigQuery crypto datasets | **B** | Needs a GCP project (an account; the agent does not create one). |

A future strategy would have to use class A. A class-B source would be allowed for convenience only after a
demonstrated equivalence to A. That test was not run, because no candidate survived.

---

## 5. Raw-chain reconstruction audit

**Bitcoin** (`sources/D1_*` §1):
- An unpruned Core node is about 750 GB, and the ~740 GB download is one-off (bitcoin.org). Pruned mode can go to ~7 GB,
  but it is incompatible with `txindex`. The chainstate is a few GB. IBD takes about a day on NVMe.
- Address and value per input needs prevout resolution: a UTXO index, or `getblock` verbosity 3, which includes a
  `prevout` object only for unpruned blocks with undo data. The Core version that introduced verbosity 3 is
  conflicting (0.22 vs 23.0) and marked UNVERIFIED.
- **This machine has 244 GB free, which is not enough for an unpruned node.** A local build would need external storage.
  AWS's parquet tables remove the node requirement, at the cost of a class-B dependency.

**Ethereum** (`sources/D1_*` §2):
- Transactions, receipts and logs are *history*. They do not need an archive node. Historical *state* does: `eth_call`
  or `balanceOf` at old blocks, and traces.
- Disk sizes: Geth full ~1–1.3 TB (2026 estimates); Erigon full ~0.4 TB used / 2 TB recommended; Erigon archive
  ~2 TB used / 4 TB recommended; legacy Geth archive over 12 TB. None fits locally.
- Since **partial history expiry (2025-07-08)**, a default full node drops pre-Merge bodies and receipts, so rebuilding
  2015–2022 logs needs era1 files.
- ERC-20 supply reconstructs from logs without archive state (USDC, USDT; §9). Public RPCs cap `eth_getLogs` ranges at
  1k–10k blocks.

**Decision relevance.** Raw reconstruction is feasible in principle for BTC counts and for ETH-contract supply, so class A
exists for those metrics. Data availability is therefore not what blocks activity or gross supply. What blocks them is
the meaning of the series (§8, §9) and the evidence (§2).

---

## 6. Timing and finality audit; conservative convention

**Facts** (`sources/D1_*` §4; the consensus rules are also encoded and tested in `phase11b_onchain_audit.py`):

*Bitcoin*
- A block timestamp must exceed the median-time-past (MTP) of the previous 11 blocks and be at most network-adjusted
  time + 2 h. **Timestamps are non-monotonic in height** (tested: `test_chains_are_actually_non_monotonic`).
- Convention: 6 confirmations.
- Historical deep reorgs: 53 blocks in Aug 2010 (value overflow) and ≥24 blocks in Mar 2013 (BIP50).

*Ethereum*
- PoW until the Merge (2022-09-15): probabilistic finality only; exchanges used 12–35+ confirmations.
- PoS: 12 s slots and 32-slot epochs, finality in about 2 epochs (~12.8 min).
- Incidents: a 7-block reorg on 2022-05-25 (beacon chain, pre-Merge), and finality delays of 4 then 9 epochs on
  2023-05-11/12.

*Vendors*
- AWS: BTC compacted nightly at ~00:35 UTC, ETH nightly at ~01:45 UTC.
- Glassnode daily metrics: 00:00–03:00 UTC (secondary).
- Coin Metrics exposes `AssetEODCompletionTime` as a machine-readable completeness flag.

**Result used here: an exact day-closure rule for Bitcoin.** MTP never decreases along a valid chain: each new timestamp
exceeds the current MTP, so replacing one of eleven values by a larger one cannot lower the median (proved in the
`btc_day_closed` docstring and tested on 50 random consensus-valid chains). Hence the rule: once the block with 6
confirmations has MTP ≥ D+1 00:00, no block stamped inside day D can ever be appended above it, and every day-D block is
already 6 deep. Day D is then *closed* without any assumption about wall-clock arrival times. The residual risk is a
reorg deeper than 6.

With exponential block times and honest stamps, closure needs the 11th block after midnight: Erlang(11), not a
measurement.

| Mean block interval | Median | p99 | p99.9 | p99.99 |
| --- | --- | --- | --- | --- |
| 600 s | 107 min | 201 min | 241 min | 278 min |
| 900 s (slow hash rate, e.g. mid-2021) | 160 min | 302 min | 362 min | 416 min |

For Ethereum PoS, day D is closed once the finalized head is stamped ≥ D+1 00:00: slot timestamps strictly increase, so
all earlier blocks are finalized ancestors. For PoW, a block stamped ≥ cutoff must be 64 deep; children must be stamped
later than their parents.

**Convention (frozen for any reopening; `timing_convention.json`)**

| Element | Rule | Justification |
| --- | --- | --- |
| Bucket | UTC day D by block timestamp, [D 00:00, D+1 00:00) | deterministic, and matches vendors and OBM §3.3 |
| Closure | BTC: MTP of the 6-confirmation block ≥ D+1 00:00. ETH PoS: finalized head stamped ≥ D+1 00:00. ETH PoW: stamped ≥ cutoff and 64 deep | exact under consensus rules; covers the 2 h stamp tolerance with no assumed buffer |
| Compute not before | **D+1 06:00 UTC**, and only if every chain used has closed day D | past the normal-hash-rate p99.99 closure (4.6 h), May-2023-type finality delays (~1 h) and the vendor windows (≤ 03:00) |
| Execution | **D+1 12:00 UTC**, fixed | six hours after compute; no same-block or same-second execution |
| Late data | if day D is not closed by 06:00, **hold the previous position**; never back-fill the missed execution | `signal_usable()`; tested |
| Weekly | week = Mon–Sun UTC, cutoff Sunday 24:00, execution Monday 12:00 UTC | `weekly_schedule_for()` |
| Vendor series (if ever allowed) | gate on the vendor's completeness flag, record first-seen values, and keep revisions separately | restated values are not PIT |

---

## 7. Point-in-time wallet-label audit (exchange reserves)

From `sources/L3_*` Part B. The two vendor PIT statements were re-fetched by the main audit.

| Source | Versioned? | First-identified date knowable? | History restated? | PIT product | Verdict |
| --- | --- | --- | --- | --- | --- |
| Glassnode | only from each metric's PIT enablement | from 2024 (`computed_at`) | **yes**: 2023 launch post warns of "information leakage from future clustering knowledge" | PiT metrics. "Any metrics that had PIT enabled in July 2025 will not contain historical PIT data prior to that date"; before then BTC, ETH and select tokens only [re-checked] | PARTIAL_PIT from 2023–2025 |
| Coin Metrics | PIT Flows only | "from each address's date of discovery" | **yes**: standard flows' "past values can change when new entity addresses are discovered later" [re-checked]. Trade press reports a Sept-2026 correction of 60 ETF series (secondary). | Point-in-Time Flows; start date undisclosed | PARTIAL_PIT. The **free** series is the restated one (§4 correction). |
| CryptoQuant | no evidence | no | no disclosure | none found | NOT_PIT / UNKNOWN |
| Arkham, Nansen | no evidence | no | presumed (continuous crowdsourced labelling) | none | UNKNOWN, presumed NOT_PIT |
| Chainalysis | internal only | not researcher-accessible | — | enterprise/forensic | NOT_PIT for research |
| Etherscan | no public label API | — | — | — | N/A |
| GitHub label scrapes (brianleect/etherscan-labels) | yes, git commits | yes, 2022-07..2023-10 | additive scrapes | — | PARTIAL_PIT: 15 months, EVM only, abandoned |
| WalletExplorer.com | frozen since 2016 | ≈ 2016 vintage | no | — | PARTIAL_PIT ≤ 2016, BTC only |
| Exchange PoR address lists (Binance, OKX from Nov 2022) | dated self-disclosures | yes | n/a | by construction | PARTIAL_PIT from Nov 2022. Kraken publishes no addresses. |
| Academic sets (Maru92/EntityAddressBitcoin) | one vintage (Apr 2018) | yes | no | — | PARTIAL_PIT ≤ 2018 |

The academic record agrees:
- Makarov & Schoar identify entities by scraping plus a vendor, calling identification "incomplete almost by design".
- Griffin & Shams dated their Tether-side addresses with Internet Archive snapshots, but not their BTC-side exchange
  addresses.
- Hoang & Baur never discuss label vintage.

**Verdict: `PIT_LABEL_BLOCKED` for any 2019–2024 development window.** The clean routes start in Nov 2022 (PoR) or
2023–2025 (vendor PIT). Projecting them backwards would re-create the leakage they exist to prevent. The published
exchange-flow results are not rescued with current labels.

---

## 8. Active-address and activity economic-stability audit

Would growth in a raw count measure comparable economic activity through time? **No.** The breaks are large, dated and
go in both directions. Sources: D1 §1–2; protocol dates cross-checked there.

| Chain | Change | Date | Effect on raw counts |
| --- | --- | --- | --- |
| BTC | HD wallets and address non-reuse norms; change outputs | gradual | more addresses per user; addresses ≠ users |
| BTC | exchange withdrawal batching; SegWit (block 481,824) | 2017-08-24 onward | fewer transactions per payment |
| BTC | Taproot (block 709,632) | 2021-11-14 | new script type; enables the next row |
| BTC | Ordinals / inscriptions; BRC-20 | Jan 2023; Mar 2023 | large non-payment transaction counts that look like standard Taproot spends |
| BTC | Runes (block 840,000) | 2024-04-20 | another wave of token transactions |
| BTC | Lightning; custodial and ETF custody | 2018 onward; 2024 | payments and holders move off chain or into a few addresses |
| ETH | ERC-20 activity lives in logs, not ETH transfers | throughout | ETH-transfer counts miss token activity |
| ETH | contracts versus EOAs; internal transactions need traces | throughout | naive from/to counts mix people, bots and contracts |
| ETH | EIP-1559 (block 12,965,000) | 2021-08-05 | fee semantics change (burn) |
| ETH | the Merge | 2022-09-15 | block-time regime change |
| ETH | L2 migration; EIP-4844 blobs | 2021–2023; 2024-03-13 | activity leaves L1; after Dencun, L2 data sits in blobs (~18-day retention), not in the L1 history |
| ETH | ERC-4337 account abstraction; MEV bots; address-poisoning spam | 2023 onward | counts inflate or deflate without economic users |

The consequence for a trading signal: a trailing growth rate across one of these dates measures a protocol change, not
demand. A de-trended or regime-adjusted version would be a construction chosen after knowing the history. That is the
kind of free choice the protocol forbids when it cannot be fixed from the mechanism alone. Treated as a hard FAIL (Q11).

---

## 9. Stablecoin supply mechanics (USDT, USDC)

From `sources/S1_*`: verified contract source and issuer documents.

**The five terms are not equivalent** (`SUPPLY_TERMS`, `EVENT_KINDS` and `net_supply()` in the audit code; worked cases in
`supply_netting_examples.json`):

| Term | USDT | USDC |
| --- | --- | --- |
| MINTED | `issue()` credits the **owner's** balance and `_totalSupply`, and emits `Issue` only. The same call serves new issuance, chain-swap inventory and "authorized but not issued" stock. | `mint(to, amount)` by any minter with an allowance (Circle's minters, CCTP `TokenMessenger`). Emits `Mint` and `Transfer(0x0,…)`. |
| AUTHORIZED | Minted but held in the treasury. An off-chain accounting category with no on-chain marker. | Concept not used (mints go straight to the recipient). |
| ISSUED | Transfer out of the treasury to a customer. Recognising it needs the treasury label. | Equal to minted, except CCTP/bridge mints. |
| CIRCULATING | Issuer's own daily figure (transparency page); vendors' "free float" definitions differ. | Issuer monthly attestations (Deloitte). |
| TRANSFERRED | changes no supply | changes no supply |

**Why net new issuance is not label-free.**
- **Chain swaps** mint on the destination and burn on the source. They are indistinguishable from real issuance on
  chain. A documented case is 300m USDT moved Omni → Ethereum on 2019-10-29, with the mint *before* the burn, so a
  multi-chain sum was transiently double-counted.
- **CCTP** is a burn-and-mint transfer, not issuance: V1 from 2023-04-26, V2 from 2025-03-11.
- **Bridges and OFTs** lock on Ethereum and mint elsewhere, so per-chain sums double-count: USDC.e, bridged USDT, and
  USDT0 from 2025-01-16.
- **`destroyBlackFunds`** cuts supply administratively, with no fiat leaving.
- **Chains through time**:
  - USDT: Omni from 2014, Ethereum from Nov 2017, Tron announced 2019-03-04; Omni/SLP/Kusama minting halted 2023,
    EOS/Algorand 2024; issuance and redemption end 2025-09-01 on all five.
  - USDC: Ethereum from 2018-09-26; native Arbitrum 2023-06-08, OP/Base Sept 2023, Polygon 2023-10-10; Tron minting
    halted 2024-02-21.
- **Treasury identity** for USDT comes from a third-party explorer label. No issuer-published, dated, complete list was
  found. Issuer circulation pages exist, but whether their history is archived was not verified: the archive route was
  blocked, and fetching historic supply numbers was out of scope.

**Classification.** Gross per-contract supply is A. Ethereum-only USDC supply is A, but migrations and CCTP contaminate it
as an issuance measure from 2023. Ethereum-only USDT is A, less a D treasury term, and the 2018–21 Omni→ETH→Tron shifts
contaminate it. Aggregate net new USDT+USDC issuance is **D (PIT_LABEL_DEPENDENT)**.

**Circulating ≠ economically deployable crypto purchasing power.** The demand mix is broader than crypto trading:
payments, remittances and EM dollarisation (Tron), DeFi collateral and T-bill demand. Evidence: NBER w34475 (2025);
Ahmed & Aldasoro (BIS WP 1270), where stablecoin inflows lower 3-month T-bill yields by 2–2.5 bp within 10 days; Banque
de France WP 908. The GENIUS Act (2025) formalises stablecoins as payment instruments. USDT has been delisted from
MiCA-licensed EU venues since 2026-07-01 (V1, secondary).

Event topics a log replay would filter on were computed with a pure-Python keccak, checked against published vectors
(`event_topics.json`):

| Event | topic0 |
| --- | --- |
| Transfer | `0xddf252ad…3b3ef` |
| USDT Issue | `0xcb8241ad…4176a` |
| USDT Redeem | `0x702d5967…b9a44` |
| USDT DestroyedBlackFunds | `0x61e6e66b…698c6` |
| USDC Mint | `0xab8530f8…0c9f8` |
| USDC Burn | `0xcc16f5db…97ca5` |

---

## 10. Economic causal graphs

**A. Activity**

```
Response   : price up -> attention/speculation, exchange deposits & withdrawals, arbitrage/DeFi, fee bidding
             -> more transactions, more active addresses              (same period or lagging)
Predictive : adoption (new users, demand for block space) -> future token demand -> future price
Confounders: batching, L2/Lightning migration, inscriptions/spam, custody aggregation, USD-denominated metrics
             (= native units x price, i.e. trailing return by construction)
```

Support:
- Response/contemporaneous: Kristoufek 2015 (price leads mining activity), Koutmos 2018, Polasik 2015 (the authors'
  caveat), Wheatley 2019 (the authors' caveat), and Liu & Tsyvinski's published framing (exposure, not forecast).
- Predictive: a lead of transactions before 2013 that decays (Kristoufek 2015), and a gross weekly altcoin spread that
  is the weakest of five factors (Cong et al.).

The theory (Biais et al., Cong-Li-Wang tokenomics) implies activity is valued, not that its *growth* is under-priced at
weekly horizons. **Response is better supported.**

**B. Stablecoin supply**

```
Response   : crypto demand/price (or leverage demand, peg premium) up -> demand for USDT/USDC on venues
             -> premium over peg -> authorised institution wires USD -> issuer mints       (Kristoufek 2021)
             also: price DOWN -> flight to stablecoins -> mint                        (Wei 2018; Ante et al. 2021)
Predictive : institution intends to buy crypto -> mints -> sends to exchange -> buys over hours/days
Non-crypto : payments / remittances / EM dollarisation / T-bill yield -> mint -> no crypto buying
Mechanics  : treasury stock, chain swaps, burn-and-mint, bridges -> 'supply' moves with no new dollars
```

Support:
- Response: Kristoufek 2021 (the broadest aggregate, 2016–2021, stable in rolling windows); Wei 2018 (grants follow
  falls; no return effect); Lyons & Viswanath-Natraj 2020 (no aggregate effect, including on the Griffin-Shams window);
  Ante et al. 2021 (downturns in the week before; positive returns *before* the event too); Grobys et al. 2021.
- Predictive: Griffin & Shams, one cluster in 2017–18 with the monthly effect gone without two months; Saggu, where the
  effect is the news of the mint within minutes. **Response is better supported**, and the non-crypto path has grown
  since 2020.

**C. Exchange flows**

```
Predictive : deposit to exchange -> intent to sell -> later selling pressure
Response   : price move -> deposits to trade or take profit, inter-venue arbitrage, internal wallet reshuffles
Measurement: labels discovered later -> history restated -> in-sample fit to today's labels
```

The measurement path alone blocks it (§7). The BTC own-flow result is null (Chi et al.).

---

## 11. Duplication versus Phases 1–5

The crypto information sets used in Phases 1–5 were all exchange-side (Binance). Across E001–E049, no experiment used an
on-chain quantity. Phase 2's conclusion excluded on-chain flows as "not causally timestamped at the required quality for
free".

| Phase 11B construction | Nearest prior family (E-ID) | Prior result | Same economic signal? |
| --- | --- | --- | --- |
| Growth in native activity counts | participation/attention: E018 abnvol7 (cross-sectional abnormal volume), E019 breadth30 (weekly BTC timing) | both rejected at Stage 1 | **Partial duplicate (UNRESOLVED)**: new data, overlapping mechanism. Distinct only under the slow adoption story, which the evidence in §10 does not support at weekly horizons. |
| USD-valued transferred value or fees | price momentum (E001, E010, E014–E016, E023, E032–E036) + volume | rejected / weak signal | **Duplicate by construction** (USD value = native value × price). Excluded. |
| On-chain transaction-volume momentum | volume (E018), taker flow (E012) | rejected | Largely duplicate: settlement volume co-moves with exchange volume. |
| Stablecoin net issuance | taker flow (E012, E014/E016 flow7), leveraged demand (E013, E019 agg_fund7) | rejected; flow7 rejected for promotion | **Not a duplicate**: primary-market creation of crypto dollars is a different layer from secondary-market aggression or leverage cost (Q14 PASS). |
| Exchange reserves / netflows | order book and flow (E012, E024–E030) | rejected | New data, related mechanism (UNRESOLVED). PIT-blocked in any case. |

B was the only class with a clean independence case. It fails on causality and evidence, not on duplication.

---

## 12. Retail deployability and venue audit

From `sources/V1_*`, retrieved 2026-09-26. This is fee documentation, not measured spreads.

- **Binance** does not serve new EU/EEA spot business: it failed to obtain a MiCA licence and halted EU/EEA spot orders,
  deposits and sign-ups from 2026-07-01 (Binance blog plus trade press; AMF application pending, no grant found). The
  0.10% fee assumed in Phases 1–5 is therefore **not currently executable for an EU/EEA resident**. This is flagged for
  any future crypto work.
- **MiCA-licensed** venues, lowest-tier taker fees: Bitvavo 0.25% (AFM), Bitstamp 0.40% (CSSF, secondary), Coinbase
  Advanced EU 0.50% (CSSF, secondary), Kraken Pro 0.80% after the 2026-07-09 restructure (Central Bank of Ireland).
- **Trading 212 Crypto** (Cyprus entity, MiCA CASP): off-chain settlement, no commission, spread about 0.30% (secondary),
  €2 minimum.
- **UK Trading 212 accounts** can hold LSE-listed BTC/ETH ETNs after a restricted-investor approval with a 24 h cooling
  period. New ISA purchases have been barred since 2026-04-06.
- **ETP TERs**: 0.10–0.35% p.a., several under expiring waivers.

**Cost arithmetic for a binary BTC-or-cash rule**, worst case with a switch every period: weekly 15.6% of notional per year
at ~0.30% one-way (up to 44% at Kraken's tier), monthly 3.6% (up to 10.2%). **Weekly switching is not viable, and monthly
is the only plausible cadence.** €500–1,000 clears every minimum order. Capital is not the constraint; the edge is.

**Feasible assets**, if any mechanism had survived: BTC and ETH spot only, unlevered and long-only, through a
MiCA-licensed venue or Trading 212 Crypto (EU), or LSE ETNs (UK). Cash between signals: EUR fiat or a MiCA e-money token,
not USDT.

---

## 13. The fourteen Stage 0 questions × three mechanisms

`gate_table.json`, checked by `mechanism_decision()` / `programme_decision()`; `decision_check.json`. UNRESOLVED counts as
not passing.

| # | Question | A. Activity | B. Stablecoin supply | C. Exchange flows |
| --- | --- | --- | --- | --- |
| 1 | Known before the return begins? | PASS (MTP/finality closure, §6) | PASS (mint events timestamped) | **FAIL** (restated labels: today's value is not what was knowable) |
| 2 | Recreatable from raw chain? | PASS (A-class counts) | **FAIL** (net issuance is D) | **FAIL** (needs labels) |
| 3 | Survives OOS? | **FAIL** (no verified OOS support; general OOS failure of published predictors, Yae & Tian) | **FAIL** (no OOS test exists) | **FAIL** (OOS only intraday, label-dependent) |
| 4 | BTC/ETH evidence? | **FAIL** (BTC tests null or reverse; positives are altcoin spreads) | **FAIL** (at weekly/monthly: contradictory; supportive only intraday) | **FAIL** (BTC own-flow null in Chi et al.; Hoang & Baur IS, abstract only) |
| 5 | Long-only evidence? | **FAIL** (none) | **FAIL** (none) | **FAIL** (none) |
| 6 | Large versus spot costs? | **FAIL** (no BTC/ETH magnitude) | **FAIL** (0.3–0.7% within 24 h, event-bound; costs 0.3–0.85% one way) | **FAIL** (intraday bp-scale) |
| 7 | No decay? | **FAIL** (lead gone by 2013) | **FAIL** (the 2017–18 episode does not replicate; 2019 reforms) | UNRESOLVED |
| 8 | Survives momentum/volume? | **FAIL** (P2A/NVT fail after market + NDF) | UNRESOLVED (never tested) | UNRESOLVED |
| 9 | Not merely a response to price? | **FAIL** (response better supported) | **FAIL** (issuance follows prices and falls) | UNRESOLVED |
| 10 | Free of retrospective labels? | PASS (raw counts) | **FAIL** (USDT treasury and swap labels) | **FAIL** (PIT_LABEL_BLOCKED) |
| 11 | Comparable through protocol evolution? | **FAIL** (§8) | **FAIL** (chain migrations, CCTP, OFT, demand mix) | UNRESOLVED |
| 12 | Works at weekly/monthly frequency? | PASS | PASS | PASS |
| 13 | €500–1,000 enough? | PASS | PASS | PASS |
| 14 | Independent of the prior 388-cell crypto search? | UNRESOLVED (attention/participation overlap) | PASS | UNRESOLVED (flow family) |

Primary codes by precedence (PIT > DATA > DUPLICATION > MECHANISM > IMPLEMENTATION): A → DATA_BLOCKED,
B → PIT_LABEL_BLOCKED, C → PIT_LABEL_BLOCKED. Two hard-fail codes are common to all three: MECHANISM_TOO_WEAK and
DATA_BLOCKED. The phase decision is MECHANISM_TOO_WEAK (§1, §15.2).

---

## 14. Candidate selection

**Result: ZERO candidates.** The selection used mechanism, data quality, causality, independent literature and
deployability, never our own returns. Stage 0 ends without a primary candidate.

**Nearest construction, recorded so it is not rediscovered as "new".** Weekly growth in label-free gross USDC supply
summed over its native chains, predicting next-month BTC/ETH returns. It is class A for supply, needs no issuer label
before CCTP, and is independent of Phases 1–5. It is not proposed:
- the causal evidence says supply follows price;
- no study tests it at a weekly or monthly horizon, or out of sample;
- USDC is the smaller issuer, so it measures a subset of the claimed mechanism;
- CCTP (2023+) and native-L2 launches break its meaning mid-sample;
- choosing USDC-only because it is clean would be a data-driven rescue of the B mechanism.

**Plain-English hypothesis that would have been preregistered had evidence supported it (NOT authorized):** "Weekly
growth in deterministic, label-free stablecoin issuance predicts the following month's BTC and ETH spot returns, because
new crypto-dollar liquidity arrives before it is deployed into crypto assets." Horizon and lookback would have come from
the mechanism (a 4-week lookback, a 1-month hold, monthly execution by the §12 cost arithmetic), not from returns.

**Cell burden (hypothetical, not incurred).** One primary cell plus three falsification cells: an Ethereum-only USDT
variant, a sign-reversal response test (supply growth on *past* returns), and a delay-stress cell. Four cells would have
taken the ledger from 490 to 494. **Actual cells added: 0. Ledger: 490.**

**Likely turnover if anything had survived:** monthly at most. Weekly costs 15–44% of notional per year in the worst
case.

---

## 15. Final Stage 0 decision (closure record, 2026-09-26)

### 15.1 Record

```
Phase 11B:                      NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0
Decision:                       D  MECHANISM_TOO_WEAK
Stage 1:                        NOT_AUTHORIZED
Primary mechanism surviving:    NONE (zero candidates)
Per-mechanism:                  A activity -> DATA_BLOCKED + MECHANISM_TOO_WEAK
                                B stablecoin supply -> PIT_LABEL_BLOCKED + DATA_BLOCKED + MECHANISM_TOO_WEAK
                                C exchange flows -> PIT_LABEL_BLOCKED (+ DATA, MECHANISM, IMPLEMENTATION)
Strategy cells added:           0
Cumulative strategy-cell ledger: 490
Crypto/strategy returns inspected: NO
Old crypto holdout (2025, 2026): CLOSED
Equity validation / holdout:     NOT OPENED / NOT READ
```

### 15.2 Why D and not G (`ABANDON_ONCHAIN_PROGRAMME`)

The gate table would also admit G: every mechanism hard-fails on evidence and on data or causality. G is not chosen for
two reasons:
1. The audit was confined by instruction to three classes. Declaring the on-chain source dead in general would extend
   the conclusion to classes not audited.
2. Two of the data blockers are time-remediable, not structural. Vendor PIT flow histories accumulate from 2023–2025,
   and issuers could publish dated swap and treasury records.

The practical effect is still close to closure. No on-chain construction is proposed, and reopening needs *external*
evidence (§15.3), not another audit of ours.

### 15.3 Reopening conditions (external only; our own diagnostics cannot qualify)

- **A:** an independent study using post-2019 data showing that a raw, label-free activity count predicts BTC or ETH
  returns at a weekly-or-longer horizon out of sample, after momentum and volume controls. The construction must be
  stated to be robust to the 2023–2024 inscription and L2/blob regimes.
- **B:** an independent OOS study showing that issuance net of chain swaps and bridges predicts BTC/ETH returns at a
  weekly-or-longer horizon with the response channel controlled. In addition, issuer-published, dated treasury and
  chain-swap records, or an explicit decision to accept a USDC-only measure *before* seeing any evidence of how it
  performs.
- **C:** a point-in-time exchange-flow history of at least five years (vendor PIT products accrue from 2023–2025, so not
  before about 2030), plus an independent OOS study at a weekly-or-longer horizon on it.

### 15.4 Excluded as post-hoc rescue (not hypotheses)

The following are not to be proposed:
- altcoin cross-sectional versions (the NET address-growth factor; the NDF supply-concentration factor, which is
  outside the three classes and long-short);
- entity-adjusted active addresses;
- USD-valued activity metrics;
- price-scaled valuation ratios (P2A, NVT, MVRV, NUPL);
- trading Whale Alert tweets;
- intraday exchange-flow or USDT-inflow signals;
- peg-deviation signals;
- re-running Stage 0 with other metrics from the same three classes;
- any on-chain diagnostic computed against prices.

---

## 16. Deliverables, reproducibility, tests

- `research/phase11b/PHASE11B_STAGE0_AUDIT.md` (this file).
- `research/phase11b_onchain_audit.py`: keccak/event topics, Bitcoin MTP closure, Ethereum finality closure, D→D+1
  schedule, the Erlang closure model, the stablecoin netting illustration, the evidence-table schema and the decision
  rule. It has no network access and no price access; a test greps the source to confirm this.
- `research/phase11b_evidence_rows.py`: the 33-row evidence table.
- `reports/phase11b/onchain_audit/`: `evidence_table.csv`, `evidence_summary.json`, `gate_table.json`,
  `decision_check.json`, `event_topics.json`, `timing_convention.json`, `supply_netting_examples.json`, and
  `MANIFEST.json` (SHA-256 of source, inputs and outputs). Reproduce from `research/`:
  `python phase11b_evidence_rows.py`, then `python phase11b_onchain_audit.py all`.
- `reports/phase11b/raw/`:
  - `sources/`: six sub-audit reports, tracked;
  - `literature/SOURCES.txt`: tracked; papers local;
  - `RAW_MANIFEST_SHA256.txt`: tracked; covers all 130 raw files;
  - web captures: local, with tracked URL indexes.
- Tests: `tests/test_phase11b_onchain_audit.py`, 40 tests (keccak vectors, MTP monotonicity and closure on random valid
  chains, non-monotonic stamps, ETH closure, schedule, late-data rule, netting cases, evidence schema, decision rule,
  recorded-gate consistency, firewall, CLI).
- No EXPERIMENTS.md entry. The phase is audit-only with zero cells, following the Phase 9A/10A/11A convention.
