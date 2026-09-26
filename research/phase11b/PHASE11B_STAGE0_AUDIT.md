# PHASE 11B — STAGE 0 AUDIT: native blockchain fundamentals

Date: 2026-09-26. **FINAL (finalization pass of 2026-09-26; corrections listed in §17):
`NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0` → decision `MECHANISM_TOO_WEAK`; Stage 1 `NOT_AUTHORIZED`.**
**Information-source audit only. This is not a backtest. No price, return, or on-chain metric series of any date was loaded.**

Evidence lives in `reports/phase11b/raw/`:
- `literature/SOURCES.txt` is the tracked source log; the papers themselves are local and git-ignored.
- `sources/` holds six sub-audit reports (L1 network activity, L2 stablecoins, L3 exchange flows and wallet labels,
  D1 raw chain and timing, S1 stablecoin mechanics, V1 venues). These are preserved as source-agent artifacts; where
  this audit corrects them, §17 says so. The web captures behind them are local and git-ignored, with URL indexes
  tracked.
- `RAW_MANIFEST_SHA256.txt` hashes all raw files, including the quarantine folder.

Machine outputs are in `reports/phase11b/onchain_audit/`. Code: `research/phase11b_onchain_audit.py` (returns-free
utilities) and `research/phase11b_evidence_rows.py` (the evidence table). Tests: `tests/test_phase11b_onchain_audit.py`
(43 tests).

---

## 0. Lock and scope declarations (read first)

| Item | Status |
| --- | --- |
| **Phase 11B** | **`NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0`** |
| **Decision** | **`MECHANISM_TOO_WEAK`** |
| **Stage 1** | **`NOT_AUTHORIZED`**: no preregistration, no experiment ID, no exploratory test |
| **Exchange-flow submechanism** | **`PIT_LABEL_BLOCKED`** |
| **Network-activity submechanism** | **`MECHANISM_TOO_WEAK`** |
| **Label-free stablecoin submechanism** | **`MECHANISM_TOO_WEAK`** |
| **Primary mechanism surviving** | **none (zero candidates)** |
| **Strategy cells added** | **0** |
| **Cumulative strategy-cell ledger** | **490** |
| BTC / ETH / altcoin / ETP returns, Sharpe, CAGR, event-study returns inspected | **NO** |
| Crypto price, OHLCV, reference-rate or market-cap series loaded | **NO** (none requested) |
| On-chain metric *values* loaded (activity counts, supply, flows) | **NO.** Only metric catalogs and definitions (Coin Metrics catalog JSON), anonymous S3 *object listings* (names and sizes) of one 2021-06-15 partition, and three zero-row Coin Metrics access probes (§4.1). Each probe asked for a time range before the metric's coverage starts, so no value could be returned; none was. |
| Correlation, regression, ML fit or threshold search involving prices | **NONE** |
| Old crypto holdout (2025 validation, 2026 final) | **CLOSED.** No file under `data/` was opened; nothing dated 2025-01-01 or later was fetched except current documentation and metadata. |
| Equity validation 2018-01..2021-12 | **NOT OPENED** |
| Equity final holdout 2022-01..2026-08 | **NOT READ** |
| Old strategy-return files | **not opened.** Only experiment *descriptions* in `EXPERIMENTS.md` and the phase conclusions were read, for §11. |
| Third-party papers and web captures | local and git-ignored. Captures of ETP product pages that may embed prices are in `sources/V1_snapshots/QUARANTINE_UNREAD_MAY_CONTAIN_PRICE_DATA/`, unread, and hashed in the manifest. |
| Literature numbers quoted below | published third-party results, not computed here. `[re-checked]` means the main audit re-read the number in the local full text or the official abstract. |

**Crypto cell count, corrected for the record.** The brief's "367-cell crypto search" is the Phase 1–2 count. Through
Phase 5 the crypto programme consumed **388** cells:
- Phase 3 → 384;
- the Phase 4 frozen replication → 385;
- Phase 5 → 388 (`PLAN.md`).

Independence (§11) is judged against all 388.

---

## 1. Executive conclusion

# STAGE 0 DECISION: MECHANISM_TOO_WEAK

**No native on-chain mechanism satisfying the programme's causal, reproducible, long-only and small-capital constraints had
sufficiently strong prior predictive evidence to justify Stage 1.**

This does not say that on-chain information is disproven, or that active-address or stablecoin data are unusable in
research. It says only that the prior evidence falls short of the burden for a new strategy cell. That burden is high,
because the programme has already used 490 cells, 388 of them in crypto.

### 1.1 Mechanism-level decisions

**Exchange reserves / flows → `PIT_LABEL_BLOCKED`. Do not proceed.**

The mechanism is economically plausible: coins moved onto an exchange are sellable supply. But every published and
vendor measure depends on identifying exchange addresses, and historical values change as more addresses are identified.
- Glassnode's point-in-time history does not exist before a metric's PIT enablement (July 2025 for most metrics).
- Coin Metrics states that standard flows' "past values can change when new entity addresses are discovered later".
- Its flow metric definition says values "reflect activity of addresses currently known to belong to the entity, from
  each address's first non-zero balance" [re-checked].
- Exchange proof-of-reserve address lists begin in Nov 2022.

No point-in-time label history covering 2019–2024 was established, so current labels cannot be projected backward.
Vendor availability does not fix causal-label leakage (§4, §7).

**Native network activity → `MECHANISM_TOO_WEAK`.**

The raw metrics are comparatively clean. Bitcoin and Ethereum counts can be rebuilt from chain data without labels (§4,
§5). The failure is in the evidence:
- The only BTC-level predictive test in full text has R² 0.00 at all seven daily horizons (Liu & Tsyvinski draft,
  Table 30) [re-checked].
- The published version of that paper frames network factors as contemporaneous *exposures*.
- The positive results are gross, long-short, weekly altcoin sorts. The NET address-growth factor (Cong et al.) is the
  weakest of five.
- The most careful recent test (Sakkas & Urquhart 2024, multiple-testing aware) finds P2A and NVT do not survive market
  and NDF [re-checked].
- Lead-lag evidence favours activity responding to price (Kristoufek 2015, Koutmos 2018).
- Nothing establishes an out-of-sample, predictive, BTC/ETH, long-only, after-cost effect.

The semantic instability is documented as a risk: addresses are not users, UTXO change and batching, custody
aggregation, Lightning, Ethereum contracts/bots/MEV, L2 migration and protocol evolution (§8). It does not make the
metrics unusable. It weakens how a fixed rule could be read across 2017–2024.

**Label-free stablecoin mint/burn/supply → `MECHANISM_TOO_WEAK` (not `PIT_LABEL_BLOCKED`).**

The construction audited is label-free: raw mint/burn events, equivalently token totalSupply, of predetermined issuer
contracts on predetermined chains (§9). Those raw objects can be reconstructed from chain data. The hard problems belong
to the economic/circulating aggregate — treasury stock, chains, migrations, bridges, swaps — and they are
semantic/aggregation problems. They are not exchange-wallet label leakage.

The mechanism fails on evidence and on endogeneity:
- **Wei (2018)**: Tether grants do not predict subsequent BTC returns; the effect is on trading volume, and grants
  follow BTC falls [re-checked].
- **Ante, Fiedler & Strehle (FRL 2021, 565 events)**: markets are weak in the week before issuance. Raw returns in the
  24 h after issuance are not significant. Abnormal returns appear on both sides of the event, measured against a
  falling estimation window. Effects differ by stablecoin, with a "lack of significant effects for USDC and GUSD" (USDC
  is the largest subsample, n = 191). Issuance size is irrelevant, and the authors themselves suggest crypto demand
  "triggers the issuance" [re-checked].
- **Large-transfer study (TFSC 2021)**: effects sit around transfers, but differ across sender/receiver categories
  (unknown / exchange / treasury). That is label-dependent evidence, not support for a label-free aggregate
  [re-checked, abstract].
- **Response papers**: Kristoufek (2021) and Lyons & Viswanath-Natraj (2020) find issuance responds to prices, the
  latter also on the Griffin-Shams window [re-checked].
- **Griffin & Shams (2020)**, the strongest supply-push paper, covers one wallet cluster in 2017–18. Its monthly effect
  loses significance without two months [re-checked].

No study tests a publication-safe, raw-chain, long-only BTC/ETH rule on mint/burn/supply at any horizon, in or out of
sample. The plausible causal chain runs crypto demand or market stress → demand for stablecoin liquidity → mint, rather
than mint → exogenous purchasing power → predictable appreciation (§10).

### 1.2 Why the programme outcome is MECHANISM_TOO_WEAK, not PIT_LABEL_BLOCKED

The hierarchy is:
1. One attractive mechanism, exchange flows/reserves, is independently `PIT_LABEL_BLOCKED` and is set aside.
2. The two remaining candidates are label-free and reconstructable: native activity counts and raw stablecoin
   mint/burn/supply.
3. Neither has strong enough prior predictive evidence to justify a strategy cell.
4. The binding constraint of the programme is therefore the evidence, `MECHANISM_TOO_WEAK`.

`derive_programme_outcome()` encodes this ordering and `programme_decision()` checks the recorded decision against it
(tests: `test_programme_hierarchy_sets_aside_label_blocked_branches`, `test_gate_table_supports_recorded_decision`).

The fourteen-question gate table (§13) and the 33-row evidence table (§2) are structured summaries of the audit. The
evidence table's count of zero rows that are simultaneously OOS, predictive, BTC/ETH, long-only and after costs is
consistent with the decision. It is **not** its sole basis; the decision rests on the per-mechanism evidence above.

---

## 2. Literature audit

Thirty-three paper×predictor rows are in `reports/phase11b/onchain_audit/evidence_table.csv`, each with the twelve
required fields. `research/phase11b_evidence_rows.py` validates the schema, and an UNVERIFIED row cannot count as
supportive. Per-paper detail, quotes and locations are in `sources/L1_*.md`, `L2_*.md` and `L3_*.md`.

Field key: (1) IS/OOS, (2) timing, (3) horizon, (4) information timestamp, (5) portfolio, (6) costs, (7) universe,
(8) period, (9) post-2019, (10) proprietary data, (11) current labels applied historically, (12) survives benchmarks.

### 2.1 SUPPORTIVE_EVIDENCE_TABLE

| Paper | Mech | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) | Key statistic and location | Verif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cong, Karolyi, Tang & Zhao (EFMA 2022 draft) | activity | IS | predictive | 1 week | formation week → next week | long-short | no | 616–745 altcoins | 2014-01..2021-01 | partial | IntoTheBlock | n/a | partial (weakest of five factors) | NET (address-growth tercile spread) 3.76%/week, t 2.82, gross; intercept against the other four factors t 1.82. Table 6 p.38, p.14, p.18 [re-checked] | full text |
| Liu, Tsyvinski & Wu (JF 2022) | activity | IS | predictive | ? | ? | long-short | no | altcoins | ? | partial | no | n/a | ? | "price-to-new-address ratios negatively predict" returns; known only from Cong et al. fn 11 (absent from the Dec-2019 draft) | secondary |
| Griffin & Shams (JF 2020) | stablecoin, flows | IS | predictive | 1–3 h; EOM | on-chain tx time, own clustering | regression | no | BTC (+6 alts) | 2017-03..2018-03 | no | own pipeline | BTC-side exchange addresses undated | partial | +3.855 bp per 100 BTC flow (t 2.30) after authorisation (Table II). EOM t −2.85, but −1.26 without Dec-2017/Jan-2018 (IV.B.1) [re-checked]. One wallet cluster, one exchange. | full text |
| Hoang & Baur (JBF 2022) | flows | IS | both | daily | vendor reserve series | regression | no | BTC | 2016-01..2021-06 | partial | CryptoQuant per secondary (unverified) | never discussed | not tested | exchange reserve changes "negatively related to contemporaneous and future" BTC returns (abstract) | abstract |
| Chi, Chu & Hao (arXiv 2411.06327, 2025) | flows | IS+OOS | predictive | 1–2 h | prior interval | regression | no (options overlay only) | BTC, ETH | 2017-12..2023-01 | yes | vendor and labels undisclosed | unknown | not tested | USDT net inflow into exchanges predicts BTC and ETH returns positively, intraday (abstract) [re-checked] | full text |

### 2.2 CONTRADICTORY_EVIDENCE_TABLE

| Paper | Mech | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) | Key statistic and location | Verif. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Liu & Tsyvinski (NBER w24877, 2018 draft) | activity | IS | predictive (null) | 1–7 days | daily close | regression | no | BTC | 2011-01..2018-05 | no | no | n/a | no | BTC wallet-user price-to-dividend ratio: coefficients 0.13/0.05/−0.13/−0.12/0.05/0.09/0.05, max \|t\| 1.36, R² 0.00 at all seven horizons. Table 30 p.29 [re-checked] | full text |
| Liu & Tsyvinski (RFS 2021) | activity | IS | contemporaneous | factor exposure | same period | regression | no | BTC/ETH/XRP | to ≥2018 | no | no | n/a | n/a | returns "exposed to" network factors, while momentum and attention "forecast" returns (published abstract) | abstract |
| Sakkas & Urquhart (JIFMIM 2024) | activity | IS, multiple-testing aware | predictive | 1 week | week-t close | long-short | no | 36 coins | 2015-01..2021-11 | partial | Coin Metrics | n/a | no | after market and NDF, "none of the remaining factors is able to explain the cross-section" (P2A, NVT fail). pp.9–10 [re-checked] | full text |
| Kristoufek (PLoS ONE 2015) | activity | IS | price leads hash rate/difficulty; transactions lead early only | multi-scale | — | — | no | BTC | 2011-09..2014-02 | no | no | n/a | — | transaction lead "becomes weaker in time", not significant from 01/2013; price leads mining activity. Fig.3 | full text |
| Koutmos (Econ. Letters 2018) | activity | IS | reverse | daily | — | VAR | no | BTC | ≤2017 | no | no | n/a | — | return shocks move transaction activity more than the reverse | secondary |
| Wei (Econ. Letters 2018) | stablecoin | IS | predictive (null) | daily | on-chain grant date | VAR | no | BTC | 2016-12..2018-02 | no | no | none | — | "we do not find any evidence suggesting that Tether issuances cause subsequent increases in Bitcoin returns"; grants raise volume and follow BTC falls. p.6 [re-checked] | full text |
| Kristoufek (FRL 2021) | stablecoin | IS, rolling | reverse | daily VAR | daily | FEVD | no | BTC/ETH/XRP | 2016-01..2021-01 | yes | Coin Metrics public | n/a | — | "no evidence of stablecoins boosting the prices"; issuances "come in reaction"; stable in rolling 365-day windows [re-checked] | full text |
| Lyons & Viswanath-Natraj (NBER w27136, 2020) | stablecoin | IS | predictive (null) | days | daily | local projections | no | BTC/ETH | full sample + Griffin-Shams window | yes | no | none | controls for hash rate, addresses | "no significant effect on the prices of Bitcoin and Ethereum", also on Mar-2017..Mar-2018. pp.30–32, fn 33 [re-checked] | full text |
| Grobys, Junttila, Kolari & Sapkota (JEF 2021) | stablecoin | IS | reverse | daily | — | Granger | no | BTC | to 2020-11 | yes | no | n/a | — | BTC volatility Granger-causes stablecoin volatility, not the reverse | full text |

**General OOS caution (not a test of on-chain variables).** Yae & Tian (Physica A 2022; abstract only, via IDEAS)
test BTC, ETH and XRP out of sample. Their abstract reports that "investor attention and trading volume fail to produce
statistically significant out-of-sample predictability", and that only a change in stock-market correlation works (OOS
R² ≤ 2.69%). The accessible material does not show native network or on-chain metrics being tested, so the paper is
recorded as general out-of-sample caution about popular in-sample crypto predictors. **It is not evidence against
on-chain metrics specifically** (§17 corrects the sub-audit on this).

### 2.3 Mixed and non-predictive rows (in the CSV, summarised)

- **Ante, Fiedler & Strehle (FRL 2021)** [re-checked]:
  - 565 issuances of USD 1m or more, 2019-04..2020-03.
  - Markets fall in the week before issuance.
  - "We do not observe significant returns for the hour of the issuance and the next 24 hours." The abnormal CAAR is
    +0.31–0.47% in the 12 h before and +0.47–0.69% in the 24 h after, relative to a falling estimation window.
  - "Lack of significant effects for USDC and GUSD"; issuance size is irrelevant.
  - The authors' own reading is that crypto demand "triggers the issuance of stablecoins in the first place".
  - Issuance events are taken from chain data, so chain-swap mints count as issuance (§9).
- **Ante, Fiedler & Strehle (TFSC 2021)**, abstract [re-checked] via IDEAS; the paper is closed access. Transfers of
  USD 1m or more have senders and receivers "categorized as (1) unknown, (2) cryptocurrency exchange or (3) stablecoin
  treasury", and the effects "differ across the nine resulting subsamples". This is label-dependent and short-window. It
  is not evidence for a label-free aggregate supply strategy.
- **Saggu (FRL 2022)** [re-checked]: BTC responds to USDT mints within 5–30 minutes mainly when Whale Alert tweets them
  (222 of 367 were tweeted). Untweeted mints are "usually" ignored, and burns are insignificant. This is a news-arrival
  effect.
- **Grobys & Huynh (FRL 2022)** [re-checked]: USDT price jumps predict *negative* next-day BTC returns (−3.65 to −8.49%,
  t −1.92 to −4.24), with R² ≤ 0.021.
- **Chi, Chu & Hao (2025)**: ETH net inflows predict ETH returns negatively, and "BTC net inflows generally lack
  predictive power for BTC returns (except at 4 hours)" [re-checked].
- **Other mixed rows**: Kristoufek (2015) on transactions; Polasik et al. (2015), same-month, with the authors' own
  reverse-causality caveat; Sebastião & Godinho (2021), abstract only; Magner & Sanhueza (2025), secondary.
- **Valuation fits, not predictive tests**: Wheatley et al. (2019), R² 0.956, where the authors themselves flag
  spurious regression and reverse causality; Alabi (2017) and Peterson (2018), abstract only.
- **Methodology or context**:
  - Makarov & Schoar (2021): entity identification is "incomplete almost by design".
  - Herremans & Low (2022): volatility only.
  - Bhambhwani et al. (2023): priced exposure.
  - Cakici et al. (2024) and Fieberg et al. (2024): general crypto cross-section.
  - BIS, NBER and Banque de France papers on stablecoin demand composition (§10).

### 2.4 Version and verification caveats

- Liu & Tsyvinski: the full text held is the Aug-2018 draft; the published RFS version is abstract-only here.
- Liu, Tsyvinski & Wu: the price-to-new-address result is secondhand.
- Griffin & Shams: read from the publisher's open-access HTML, rendered without sign-in.
- Wei: the Table 2 VAR cells were not quoted because the layout is ambiguous; only the author's prose conclusion is used.
- Hoang & Baur: the data vendor is unverified.
- "Wang, Ma & Wu (2020)" was not found and is not invented.
- The DR Press 2025 VAR paper is excluded: its predictor is peg deviation, and the venue is unverified.
- Search-engine summaries in the sub-audits produced at least two false claims: Chainalysis labels in Makarov & Schoar,
  and network metrics in the Yae & Tian abstract. Both were caught against primary text. No search-summary statistic is
  decisive anywhere in this audit.

---

## 3. The conflict: older OOS failure versus newer "OOS predictability"

| Driver | What the audited papers show |
| --- | --- |
| **Cross-sectional altcoin universes** | Every positive on-chain *return* result in full text is a weekly long-short sort over tens to hundreds of coins: Cong et al. (616–745), Sakkas & Urquhart (36). Cong et al.'s value/network sorts are strongest in the smallest coins. BTC-level tests are null (Liu & Tsyvinski Table 30) or reverse (Kristoufek 2015, Koutmos). |
| **Small/illiquid tokens and costs** | No positive result nets costs. Phases 1–5 already showed altcoin cross-sectional spreads dying on costs, minimum notionals and delistings: E016/E017 found 860 of 8,508 positions below minimum notional at 500 USDT, and the top-ten names carrying 106% of P&L. |
| **Long-short versus long-only** | Every positive result is a spread or an event-window CAAR, and none reports the long leg. Sakkas & Urquhart's long-only portfolio pairs the market with the NDF *concentration* factor, not an activity variable. |
| **Sample period and decay** | Transactions lead price only until 2013 (Kristoufek 2015). Griffin & Shams covers 2017–18 only. The broadest recent aggregate sample shows response (Kristoufek 2021, to Jan-2021). No audited paper covers the 2024+ spot-ETF era. |
| **ML flexibility and factor mining** | The multiple-testing-aware procedure (Sakkas & Urquhart) rejects the activity variables. Non-standard errors exceed standard errors across 20,736 designs (Fieberg et al., abstract). ML results with on-chain features could not be verified in full text. |
| **Predictor definitions** | "On-chain" results mix three kinds of variable: price-scaled valuation ratios (P2A, NVT, MVRV), activity growth, and label-dependent flows. Sakkas & Urquhart's survivor, NDF, is a supply-concentration variable outside the three classes. |
| **Data revisions and labels** | Flow results rest on vendor labels of undisclosed vintage (Hoang & Baur, Chi et al.). Vendors document retroactive recomputation (§7). |
| **Genuinely new structure** | The one well-identified newer finding is intraday and label-dependent: USDT exchange inflows lead BTC/ETH by 1–2 h (Chi et al.). |

A weak or contemporaneous relationship would produce exactly this pattern:
- positive in-sample results on altcoin spreads, gross of costs;
- effects that fade over time and under better multiple-testing control;
- null or reversed results on BTC.

The newest paper is not privileged.

---

## 4. Source-quality classification of candidate metrics

A = RAW_CHAIN_RECONSTRUCTABLE, B = PUBLIC_VENDOR_REPRODUCIBLE, C = VENDOR_TRANSFORMED, D = PIT_LABEL_DEPENDENT,
E = PROPRIETARY. Sources: `sources/D1_*`, `S1_*`, `L3_*`, the Coin Metrics catalog snapshots and §4.1.

| Metric | Class | Note |
| --- | --- | --- |
| BTC transaction count, block count, fees in BTC, issuance | **A** | Deterministic from raw blocks. Fees need prevout values. |
| BTC active / new addresses | **A**, definition-dependent | Deterministic once the address rule is fixed. P2PK, bare multisig, OP_RETURN and non-standard scripts have no canonical address. Llanos (2026) publishes no address series. |
| ETH transaction count, EOA senders, ERC-20 Transfer counts | **A** | From block and log history. Pre-Merge history needs era1 files since partial history expiry (2025-07-08). |
| ETH active addresses including internal transfers | **A** (needs traces) | Traces need historical-state re-execution, or the AWS `eth.traces` table (B). |
| **Raw mint/burn events of a predetermined stablecoin contract** | **A** | USDC: `Mint`/`Burn` (+`Transfer` 0x0). USDT: `Issue`/`Redeem`/`DestroyedBlackFunds`, **none of which emits `Transfer`**, so a Transfer-only replay is wrong. Verified contract source (S1). |
| **Token totalSupply of a fixed contract** | **A** | Exact event replay from contract creation (USDT assumes `deprecated` never set). Migrations and new chain deployments need explicit rules fixed in advance. |
| **Economic / circulating aggregate supply** | **rule-dependent** | Needs rules for treasury inventory, authorized-but-not-issued stock, chains, migrations, bridges, chain swaps, frozen tokens and double counting. These are semantic/aggregation problems. They are D only where a rule uses historically changing entity labels (e.g. excluding a USDT treasury identified by a later third-party explorer label). CCTP and bridge contracts are fixed public contracts, not changing labels. |
| Coin Metrics Community AdrActCnt, TxCnt, SplyCur, FeeTotNtv (BTC, ETH, usdt_eth, usdc_eth, usdt_trx) | **B/C** | Definitions published; implementation not open (Llanos 2026: auditability "Medium"). AdrNewCnt and TxTfrValAdjNtv are not in the free tier. |
| **Coin Metrics exchange flows (FlowInExNtv, FlowOutExNtv, SplyExNtv)** | **C + D** | **VENDOR_TRANSFORMED + PIT_LABEL_DEPENDENT.** Access (§4.1): the flow product family is professional (Network Data Pro, per Coin Metrics' categorisation as stated in the finalization brief and in L3; not re-fetched). A **daily BTC/ETH subset** is exposed in Community (measured). Block-level and hourly frequencies are forbidden without credentials, and the Point-in-Time Flows product is separate. Free daily access does not help, because that series is the one built from "addresses currently known to belong to the entity, from each address's first non-zero balance". |
| Glassnode / CryptoQuant / Arkham / Nansen exchange balances | **C/D/E** | §7. |
| AWS Public Blockchain Data (s3://aws-public-blockchain) | **B** | Anonymous listing verified; open-source ETL; MIT-0; "experimental". |
| Google BigQuery crypto datasets | **B** | Needs a GCP project, i.e. an account (not created). |

A future strategy would have to use class A, and class B only after a demonstrated equivalence to A. That equivalence
test was not run, because no candidate survived.

### 4.1 Coin Metrics access check (finalization; `onchain_audit/coinmetrics_access_check.json`)

The two sub-audits disagreed: L3 said flows are Pro-only, D1 said they are in the free tier. The finalization brief
stated that `FlowIn…` entries are not community-flagged. The check below was run on 2026-09-26 against
community-api.coinmetrics.io with no key, using metadata requests and zero-row probes only:
- `catalog-v2` and `catalog-all-v2` list FlowInExNtv, FlowOutExNtv and SplyExNtv for BTC and ETH at **1d with
  `community: true`**. FlowInExNtv and FlowOutExNtv at **1b and 1h** carry no community flag.
- A probe for FlowInExNtv 1d, over a range before coverage begins, returned HTTP 200 with zero rows and no error.
- The same probe at 1h returned **HTTP 403 `forbidden`**: "not available with supplied credentials".
- A control on TxCnt 1d returned HTTP 200 with zero rows.

**Conclusion.** Daily BTC/ETH exchange-flow series are accessible through Community. Finer frequencies, other flow
products and the PIT flows are professional. The durable classification is therefore VENDOR_TRANSFORMED +
PIT_LABEL_DEPENDENT, with access **partial: daily BTC/ETH subset in Community, otherwise professional**. "Coin Metrics
exchange flows are free" is not asserted anywhere in this audit. The brief's premise is correct for the block and hourly
entries, but not for the daily BTC/ETH entries, and §17 records this. The PIT decision does not depend on access in any
way.

---

## 5. Raw-chain reconstruction audit

**Bitcoin** (`sources/D1_*` §1):
- An unpruned Core node is about 750 GB, and the ~740 GB download is one-off. Pruned mode is incompatible with
  `txindex`. IBD takes about a day on NVMe.
- Input attribution needs prevout resolution: a UTXO index, or `getblock` verbosity 3 with undo data. The Core version
  that introduced verbosity 3 is conflicting (0.22 vs 23.0) and marked UNVERIFIED.
- **This machine has 244 GB free, which is not enough for an unpruned node.** A local build would need external storage.
  AWS's parquet removes the node requirement, but as a class-B dependency.

**Ethereum** (`sources/D1_*` §2):
- Transactions, receipts and logs are history and do not need an archive node. Historical state does (`eth_call` at old
  blocks, traces).
- Disk sizes: Geth full ~1–1.3 TB; Erigon full ~0.4 TB used / 2 TB recommended; Erigon archive ~2 TB used / 4 TB
  recommended; legacy Geth archive over 12 TB. None fits locally.
- Since partial history expiry (2025-07-08), rebuilding pre-Merge logs needs era1 files.
- ERC-20 supply reconstructs from logs without archive state. Public RPCs cap `eth_getLogs` ranges.

Raw reconstruction is feasible in principle for BTC counts and for per-contract stablecoin supply, so class A exists for
the two label-free mechanisms. Data availability is not what blocks them; the evidence is (§1).

---

## 6. Timing and finality audit; conservative convention

**Facts** (`sources/D1_*` §4; the consensus rules are also encoded and tested in `phase11b_onchain_audit.py`):

*Bitcoin*
- A block timestamp must exceed the median-time-past (MTP) of the previous 11 blocks and be at most network-adjusted
  time + 2 h. Timestamps are therefore **non-monotonic in height** (tested).
- Convention: 6 confirmations.
- Deep reorgs: 53 blocks in Aug 2010, ≥24 blocks in Mar 2013.

*Ethereum*
- PoW until 2022-09-15: probabilistic finality only; exchanges used 12–35+ confirmations.
- PoS: 12 s slots, 32-slot epochs, finality in about 2 epochs (~12.8 min).
- Incidents: a 7-block reorg on 2022-05-25 (beacon chain), and finality delays of 4 then 9 epochs on 2023-05-11/12.

*Vendors*
- AWS nightly jobs at ~00:35 UTC (BTC) and ~01:45 UTC (ETH).
- Glassnode daily metrics 00:00–03:00 UTC (secondary).
- Coin Metrics exposes `AssetEODCompletionTime` as a completeness flag.

**Exact Bitcoin day closure.** MTP never decreases along a valid chain: each new timestamp exceeds the current MTP, so
replacing one of eleven values by a larger one cannot lower the median (docstring proof, tested on 50 random
consensus-valid chains). Hence the rule: once the block with 6 confirmations has MTP ≥ D+1 00:00, no block stamped in
day D can ever be appended above it, and every day-D block is already 6 deep. The residual risk is a reorg deeper than 6.

The closure-delay model below is not a measurement. With exponential block times it is Erlang(11):

| Mean block interval | Median | p99 | p99.9 | p99.99 |
| --- | --- | --- | --- | --- |
| 600 s | 107 min | 201 min | 241 min | 278 min |
| 900 s (slow hash rate) | 160 min | 302 min | 362 min | 416 min |

Ethereum PoS closes once the finalized head is stamped ≥ D+1 00:00. PoW closes once a block stamped ≥ cutoff is 64 deep.

**Convention (frozen for any reopening; `timing_convention.json`)**

| Element | Rule | Justification |
| --- | --- | --- |
| Bucket | UTC day D by block timestamp | deterministic; matches vendors and OBM §3.3 |
| Closure | BTC: MTP of the 6-confirmation block ≥ D+1 00:00. ETH PoS: finalized head ≥ D+1 00:00. ETH PoW: 64 deep | exact under consensus rules; no guessed buffer |
| Compute not before | **D+1 06:00 UTC**, and only if every chain used has closed day D | past the normal-hash-rate p99.99 closure (4.6 h), finality incidents and vendor windows |
| Execution | **D+1 12:00 UTC**, fixed | no same-block or same-second execution |
| Late data | hold the previous position; never back-fill | `signal_usable()`, tested |
| Weekly | Mon–Sun UTC week, Sunday 24:00 cutoff, Monday 12:00 UTC execution | `weekly_schedule_for()` |
| Vendor series (if ever allowed) | gate on the completeness flag; record first-seen values; keep revisions separately | restated values are not PIT |

---

## 7. Point-in-time wallet-label audit (exchange reserves)

Source: `sources/L3_*` Part B, with the two vendor PIT statements and the Coin Metrics catalog re-checked by the main
audit.

| Source | Versioned? | First-identified date knowable? | History restated? | PIT product | Verdict |
| --- | --- | --- | --- | --- | --- |
| Glassnode | only from each metric's PIT enablement | from 2024 (`computed_at`) | yes (2023 post: "information leakage from future clustering knowledge") | PiT metrics; "any metrics that had PIT enabled in July 2025 will not contain historical PIT data prior to that date" [re-checked] | PARTIAL_PIT from 2023–2025 |
| Coin Metrics | PIT Flows only | "from each address's date of discovery" | **yes**: standard flows' "past values can change when new entity addresses are discovered later" [re-checked]. The flow definition uses "addresses currently known to belong to the entity" [re-checked]. | Point-in-Time Flows (professional; start date undisclosed) | PARTIAL_PIT. The standard daily BTC/ETH series (Community-accessible, §4.1) is the restated kind. |
| CryptoQuant | no evidence | no | no disclosure | none found | NOT_PIT / UNKNOWN |
| Arkham, Nansen | no evidence | no | presumed | none | UNKNOWN, presumed NOT_PIT |
| Chainalysis | internal only | not researcher-accessible | — | enterprise | NOT_PIT for research |
| GitHub label scrapes (brianleect/etherscan-labels) | git commits | yes, 2022-07..2023-10 | additive | — | PARTIAL_PIT: 15 months, EVM only, abandoned |
| WalletExplorer.com | frozen since 2016 | ≈ 2016 vintage | no | — | PARTIAL_PIT ≤ 2016, BTC only |
| Exchange PoR address lists | dated self-disclosures | yes | n/a | by construction | PARTIAL_PIT from Nov 2022; Kraken publishes no addresses |
| Academic sets (Maru92) | one vintage (Apr 2018) | yes | no | — | PARTIAL_PIT ≤ 2018 |

The academic record agrees:
- Makarov & Schoar call entity identification "incomplete almost by design".
- Griffin & Shams dated their Tether-side addresses via Internet Archive snapshots, but not their BTC-side exchange
  addresses.
- Hoang & Baur never discuss label vintage.

**Verdict: `PIT_LABEL_BLOCKED` for any 2019–2024 development window.** Published exchange-flow results are not rescued
with current labels.

---

## 8. Activity economic-stability audit

**Does growth in a raw activity count measure comparable economic activity through time?** Only partly. There are large,
dated semantic breaks in both directions. This is recorded as a documented risk (gate Q11 UNRESOLVED), not as a claim
that activity metrics are unusable in research.

| Chain | Change | Date | Effect on raw counts |
| --- | --- | --- | --- |
| BTC | addresses ≠ users: HD wallets, non-reuse norms, change outputs | gradual | more addresses per user |
| BTC | exchange withdrawal batching; SegWit (block 481,824) | 2017-08-24 onward | fewer transactions per payment |
| BTC | Taproot (block 709,632) | 2021-11-14 | enables the next row |
| BTC | Ordinals/inscriptions; BRC-20 | Jan 2023; Mar 2023 | large non-payment transaction counts |
| BTC | Runes (block 840,000) | 2024-04-20 | another token-transaction wave |
| BTC | Lightning; custodial and ETF custody aggregation | 2018 onward; 2024 | payments and holders move off chain or into a few addresses |
| ETH | ERC-20 activity lives in logs, not ETH transfers | throughout | ETH-transfer counts miss token activity |
| ETH | contracts versus EOAs; internal transactions need traces; bots and MEV | throughout | naive counts mix people, bots and contracts |
| ETH | EIP-1559 (block 12,965,000) | 2021-08-05 | fee semantics change |
| ETH | the Merge | 2022-09-15 | block-time regime change |
| ETH | L2 migration; EIP-4844 blobs | 2021–2023; 2024-03-13 | activity leaves L1 |
| ETH | ERC-4337; address-poisoning spam | 2023 onward | counts move without economic users |

For a trading rule, a trailing growth rate that crosses one of these dates partly measures a protocol change. Adjusting
for the breaks after seeing the history would be a free choice. That is why the gate is not a PASS. The decision still
rests on the evidence in §1.1.

---

## 9. Stablecoin supply mechanics (USDT, USDC)

Source: `sources/S1_*` (verified contract source and issuer documents). Three objects must be kept apart
(`SUPPLY_OBJECTS` in the audit code):

| Object | Class | What it takes |
| --- | --- | --- |
| **Raw contract mint/burn events** (predetermined contract) | **RAW_CHAIN_RECONSTRUCTABLE** | Read the issuer contract's events. USDT: `issue()` credits the owner's balance and emits `Issue` only; `redeem()` emits `Redeem` only; `destroyBlackFunds()` emits `DestroyedBlackFunds` only. USDC: `mint()` emits `Mint` + `Transfer(0x0,…)`; `burn()` emits `Burn` + `Transfer(…,0x0)`. No supply change without an event was found in the inspected versions. |
| **Token totalSupply** (fixed contract) | **RAW_CHAIN_RECONSTRUCTABLE** | Exact replay from contract creation, or state. Handle explicitly, in advance: USDT's `deprecate()` path (never known to be invoked on Ethereum); USDC proxy upgrades (same address); each new chain deployment, which is a new contract. |
| **Economic / circulating aggregate** | **RULE_DEPENDENT** | Rules for: treasury inventory (Tether's "authorized but not issued" is an off-chain accounting category with no on-chain marker); multiple chains; chain swaps (mint on the destination, burn on the source, e.g. 300m USDT Omni→Ethereum on 2019-10-29 with the mint first); CCTP burn-and-mint (V1 2023-04-26, V2 2025-03-11); bridges and OFTs (USDC.e, bridged USDT, USDT0 from 2025-01-16); frozen/destroyed tokens; double counting. |

The aggregate's problems are semantic and aggregation problems, not the exchange-wallet leakage of §7:
- CCTP and bridge contracts are fixed public contracts.
- Chain-swap pairing appears only in issuer announcements.
- A USDT treasury exclusion becomes PIT-label-dependent **only** if it uses a treasury address identified later by a
  third party (the explorer label found; no dated issuer list was found).

The audited construction avoids all of these rules by using the raw objects of predetermined contracts. It is therefore
label-free. It measures *gross* contract supply, which also moves with migrations and swaps. That is a limitation of
meaning (Q11 UNRESOLVED), not a label block.

**Chains through time.**
- USDT: Omni from 2014; Ethereum from Nov 2017; Tron announced 2019-03-04. Omni, SLP and Kusama minting halted 2023;
  EOS and Algorand 2024; issuance and redemption end 2025-09-01 on all five.
- USDC: Ethereum from 2018-09-26; native Arbitrum 2023-06-08; OP and Base Sept 2023; Polygon 2023-10-10; Tron minting
  halted 2024-02-21.

**Circulating supply ≠ crypto purchasing power.**
- The demand mix includes payments, remittances and EM dollarisation (Tron), DeFi collateral and T-bill demand: NBER
  w34475; Ahmed & Aldasoro (BIS WP 1270: inflows lower 3-month T-bill yields by 2–2.5 bp within 10 days); Banque de
  France WP 908.
- The GENIUS Act (2025) formalises payment use.
- USDT has been delisted from MiCA-licensed EU venues since 2026-07-01 (V1, secondary).

Log-replay topics, computed with a keccak implementation checked against published test vectors (`event_topics.json`):

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

Response or contemporaneous: Kristoufek 2015 (price leads mining activity), Koutmos 2018, Polasik 2015 and Wheatley 2019
(the authors' own caveats), and Liu & Tsyvinski's published framing. Predictive: a pre-2013 lead that decays, and a
gross weekly altcoin spread that is the weakest of five factors. Theory values activity; it does not imply that activity
growth is under-priced weekly. **Response is better supported.**

**B. Stablecoin supply**

```
Response   : crypto demand/price (or leverage demand, peg premium) up -> demand for USDT/USDC on venues
             -> premium over peg -> authorised institution wires USD -> issuer mints       (Kristoufek 2021)
             also: market stress / price DOWN -> demand for stablecoin liquidity -> mint (Wei 2018; Ante et al. 2021)
Predictive : institution intends to buy crypto -> mints -> sends to exchange -> buys over hours/days
Non-crypto : payments / remittances / EM dollarisation / T-bill yield -> mint -> no crypto buying
```

Response:
- Kristoufek 2021: the broadest aggregate, stable in rolling windows.
- Wei 2018: grants follow falls, with no return effect.
- Lyons & Viswanath-Natraj 2020: no aggregate effect, including on the Griffin-Shams window.
- Ante et al. 2021: weakness before issuance, no significant raw post-issuance returns, and the authors' own "demand
  triggers the issuance" reading.
- Grobys et al. 2021.

Predictive: Griffin & Shams (one cluster in 2017–18, with the monthly effect gone without two months) and Saggu (the
news of the mint, within minutes). **Response is better supported**, and the non-crypto demand path has grown since 2020.

**C. Exchange flows**

```
Predictive : deposit to exchange -> intent to sell -> later selling pressure
Response   : price move -> deposits to trade or take profit, inter-venue arbitrage, internal wallet reshuffles
Measurement: labels discovered later -> history restated -> in-sample fit to today's labels
```

The measurement path blocks it (§7), whatever the economics.

---

## 11. Duplication versus Phases 1–5

The crypto information sets of Phases 1–5 were all exchange-side (Binance). Across E001–E049, no experiment used an
on-chain quantity. Phase 2 excluded on-chain flows as "not causally timestamped at the required quality for free".

| Phase 11B construction | Nearest prior family (E-ID) | Prior result | Same economic signal? |
| --- | --- | --- | --- |
| Growth in native activity counts | participation/attention: E018 abnvol7, E019 breadth30 | both rejected at Stage 1 | Partial overlap (UNRESOLVED): new data, overlapping mechanism. Distinct only under the slow adoption story. |
| USD-valued transferred value or fees | price momentum (E001, E010, E014–E016, E023, E032–E036) + volume | rejected / weak signal | **Duplicate by construction**; excluded. |
| On-chain transaction-volume momentum | volume (E018), taker flow (E012) | rejected | largely duplicate |
| Raw stablecoin mint/burn/supply | taker flow (E012, E014/E016 flow7), leveraged demand (E013, E019) | rejected | **Not a duplicate**: primary-market creation of crypto dollars is a different layer (Q14 PASS) |
| Exchange reserves / netflows | order book and flow (E012, E024–E030) | rejected | new data, related mechanism (UNRESOLVED); PIT-blocked in any case |

Stablecoin supply was the one class with a clean independence case. It fails on evidence and endogeneity, not on
duplication.

---

## 12. Retail deployability and venue audit

Source: `sources/V1_*`, 2026-09-26. These are documented fees, not measured spreads.

- **Binance** has not served new EU/EEA spot business since 2026-07-01 (no MiCA licence; Binance blog + trade press).
  The 0.10% fee assumed in Phases 1–5 is therefore not currently executable for an EU/EEA resident. Flagged for any
  future crypto work.
- **MiCA-licensed lowest-tier taker fees**: Bitvavo 0.25%, Bitstamp 0.40% (fee secondary), Coinbase Advanced EU 0.50%
  (secondary), Kraken Pro 0.80% after the 2026-07-09 restructure.
- **Trading 212 Crypto** (Cyprus entity, MiCA CASP): off-chain settlement, no commission, spread about 0.30% (secondary),
  €2 minimum.
- **UK Trading 212 accounts**: LSE-listed BTC/ETH ETNs after restricted-investor approval; no new ISA purchases since
  2026-04-06.
- **ETP TERs**: 0.10–0.35% p.a.

**Cost arithmetic.** For a binary BTC-or-cash rule switching every period (worst case):
- weekly: 15.6% of notional per year at ~0.30% one-way, up to 44% at Kraken's tier — **not viable**;
- monthly: 3.6%, up to 10.2% — the only plausible cadence.

€500–1,000 clears every minimum order.

**Feasible assets, had a mechanism survived:** BTC and ETH spot only, unlevered and long-only, through a MiCA-licensed
venue or Trading 212 Crypto (EU), or LSE ETNs (UK). Cash between signals would be EUR or a MiCA e-money token, not USDT.

---

## 13. The fourteen Stage 0 questions × three mechanisms

Sources: `gate_table.json`, checked by `mechanism_decision()`, `derive_programme_outcome()` and `programme_decision()`;
results in `decision_check.json`. UNRESOLVED counts as not passing but does not set a mechanism's primary code when a gate
has hard-failed.

| # | Question | A. Network activity | B. Label-free stablecoin mint/burn/supply | C. Exchange flows |
| --- | --- | --- | --- | --- |
| 1 | Known before the return begins? | PASS (MTP/finality closure) | PASS (mint events timestamped) | **FAIL** (restated labels: today's value was not knowable then) |
| 2 | Recreatable from raw chain? | PASS | PASS (raw events / totalSupply of fixed contracts) | **FAIL** (needs labels) |
| 3 | Survives OOS? | **FAIL** (no verified OOS support for any native activity variable; Yae & Tian is only general caution) | **FAIL** (no OOS test exists) | **FAIL** (OOS only intraday, label-dependent) |
| 4 | BTC/ETH evidence? | **FAIL** (BTC tests null or reverse; positives are altcoin spreads) | **FAIL** (weekly/monthly contradictory; supportive only within hours or conditional on tweets/labels) | **FAIL** (BTC own-flow null) |
| 5 | Long-only evidence? | **FAIL** | **FAIL** | **FAIL** |
| 6 | Large versus spot costs? | **FAIL** | **FAIL** (no significant raw returns in the 24 h after issuance; abnormal 0.3–0.7% within 24 h; costs 0.3–0.85% one way) | **FAIL** |
| 7 | No decay? | **FAIL** (lead gone by 2013) | **FAIL** (the 2017–18 episode does not replicate; 2019 reforms) | UNRESOLVED |
| 8 | Survives momentum/volume? | **FAIL** (P2A/NVT fail after market + NDF) | UNRESOLVED (never tested) | UNRESOLVED |
| 9 | Not merely a response to price? | **FAIL** | **FAIL** (issuance follows prices and stress) | UNRESOLVED |
| 10 | Free of retrospective labels? | PASS | PASS (predetermined contracts; no entity labels) | **FAIL** (PIT_LABEL_BLOCKED) |
| 11 | Comparable through protocol evolution? | UNRESOLVED (semantic breaks, §8) | UNRESOLVED (migrations, swaps, CCTP, OFT, demand mix, §9) | UNRESOLVED |
| 12 | Works at weekly/monthly frequency? | PASS | PASS | PASS |
| 13 | €500–1,000 enough? | PASS | PASS | PASS |
| 14 | Independent of the prior 388-cell search? | UNRESOLVED (attention/participation overlap) | PASS | UNRESOLVED (flow family) |
| — | **Mechanism decision** | **MECHANISM_TOO_WEAK** | **MECHANISM_TOO_WEAK** | **PIT_LABEL_BLOCKED** |

**Programme outcome** (§1.2): set aside the label-blocked branch (C). The remaining label-free branches (A, B) are both
MECHANISM_TOO_WEAK, so the outcome is **MECHANISM_TOO_WEAK**.

---

## 14. Candidate selection

**Result: ZERO candidates.** Selection used mechanism, data quality, causality, independent literature and
deployability, never our own returns.

**Nearest construction, recorded so it is not rediscovered as "new":** the B construction itself, i.e. weekly change in
raw mint-minus-burn of predetermined USDT and USDC contracts, predicting next-month BTC/ETH returns. It is label-free,
class A and independent of Phases 1–5. It is not proposed:
- the causal evidence says supply follows prices and stress;
- no study tests any such rule at a weekly or monthly horizon, or out of sample;
- the best event study finds no significant raw returns after issuance;
- migrations and swaps make gross contract supply an unstable measure of new dollars.

A USDC-only or other "cleaner" subset chosen because it is clean would be a data-driven rescue (§15.4).

**Plain-English hypothesis that would have been preregistered had evidence supported it (NOT authorized):** "Weekly
change in raw, label-free stablecoin mint-minus-burn predicts the following month's BTC and ETH spot returns, because new
crypto-dollar liquidity arrives before it is deployed into crypto assets." Lookback and horizon would have come from the
mechanism and the cost arithmetic (a 4-week lookback, 1-month hold, monthly execution), not from returns.

**Cell burden (hypothetical, not incurred).** One primary plus three falsification cells would have taken the ledger
from 490 to 494:
- USDT-only contract variant;
- a response test (supply change regressed on *past* returns);
- a one-day delay stress.

**Actual cells added: 0. Ledger: 490.** Likely turnover, had anything survived: monthly at most.

---

## 15. Final Stage 0 decision (closure record, 2026-09-26)

### 15.1 Record

```
Phase 11B:                          NATIVE_BLOCKCHAIN_FUNDAMENTALS_STAGE0
Decision:                           MECHANISM_TOO_WEAK
Stage 1:                            NOT_AUTHORIZED
Exchange-flow submechanism:         PIT_LABEL_BLOCKED
Network-activity submechanism:      MECHANISM_TOO_WEAK
Label-free stablecoin submechanism: MECHANISM_TOO_WEAK
Primary mechanism surviving:        NONE (zero candidates)
Strategy cells added:               0
Cumulative strategy-cell ledger:    490
Strategy returns inspected:         NO
Old crypto holdout touched:         NO
Equity validation touched:          NO
Equity final holdout touched:       NO
```

### 15.2 Alternatives considered

- **PIT_LABEL_BLOCKED** at programme level is rejected. Only the exchange-flow branch needs historically changing
  entity labels; the other two are label-free (§1.2).
- **DATA_BLOCKED** is rejected. Raw reconstruction is feasible for both label-free branches (§5). Their semantic
  instability is a documented risk, not an established data block.
- **ABANDON_ONCHAIN_PROGRAMME (G)** is not admissible under the finalized gate table: A and B have no data/causality hard
  fail (tested). It would also overstate the finding: this audit covered three classes and does not show on-chain
  information to be useless.

### 15.3 Reopening conditions (external only; our own diagnostics cannot qualify)

- **Network activity:** an independent study on post-2019 data showing that a raw, label-free activity count predicts BTC
  or ETH returns at a weekly-or-longer horizon out of sample, after momentum and volume controls. The construction must
  be robust to the 2023–2024 inscription and L2/blob regimes.
- **Label-free stablecoin supply:** an independent OOS study showing that raw or rule-defined issuance predicts BTC/ETH
  returns at a weekly-or-longer horizon with the response channel controlled. Rules for migrations and swaps must be
  fixed before any performance evidence is seen.
- **Exchange flows:** a point-in-time exchange-flow history of at least five years (vendor PIT products accrue from
  2023–2025, so not before about 2030), plus an independent OOS study at a weekly-or-longer horizon on it.

### 15.4 Excluded as post-hoc rescue (not hypotheses)

The following are not to be proposed:
- altcoin cross-sectional versions (NET address growth; NDF supply concentration);
- entity-adjusted active addresses;
- USD-valued activity metrics;
- price-scaled ratios (P2A, NVT, MVRV, NUPL);
- hash ribbons and miner flows;
- whale or Whale Alert signals;
- intraday exchange-flow or USDT-inflow signals;
- peg-deviation signals;
- alternative stablecoin constructions or subsets (e.g. USDC-only, treasury-netted, chain-filtered);
- re-running Stage 0 with other metrics from the same three classes;
- any on-chain diagnostic computed against prices.

---

## 16. Deliverables, reproducibility, tests

- `research/phase11b/PHASE11B_STAGE0_AUDIT.md` (this file).
- `research/phase11b_onchain_audit.py`, which has no network or price access (a test greps the source to confirm):
  - keccak and event topics;
  - Bitcoin MTP closure and Ethereum finality closure;
  - the D→D+1 schedule and the Erlang closure model;
  - `SUPPLY_OBJECTS`, identification classes and the netting illustration;
  - the evidence schema;
  - `mechanism_decision` / `derive_programme_outcome` / `programme_decision`.
- `research/phase11b_evidence_rows.py`: the 33-row evidence table.
- `reports/phase11b/onchain_audit/`:
  - `evidence_table.csv`, `evidence_summary.json`;
  - `gate_table.json` (records per-mechanism decisions), `decision_check.json`;
  - `event_topics.json`, `timing_convention.json`, `supply_netting_examples.json`;
  - `coinmetrics_access_check.json`;
  - `MANIFEST.json`.

  Reproduce from `research/`: `python phase11b_evidence_rows.py`, then `python phase11b_onchain_audit.py all`.
- `reports/phase11b/raw/`:
  - `sources/`: six sub-audit reports, tracked and preserved as agent artifacts;
  - `literature/SOURCES.txt`: tracked; the papers are local;
  - `RAW_MANIFEST_SHA256.txt`: tracked; it covers every raw file, including the quarantine folder;
  - web captures: local, with tracked URL indexes.
- Tests: `tests/test_phase11b_onchain_audit.py`, 43 tests.
- No EXPERIMENTS.md entry (audit-only, zero cells; Phase 9A/10A/11A convention).

---

## 17. Corrections made at finalization (2026-09-26, after commit 1aacdaa)

1. **Coin Metrics access.**
   - *Before:* "The standard flows are in the free catalog" (§4) and "The free Coin Metrics flow series is the restated
     kind" (§1).
   - *After:* exchange flows are VENDOR_TRANSFORMED + PIT_LABEL_DEPENDENT. Access is partial: the flow family is
     professional (Network Data Pro, per the brief and L3), a daily BTC/ETH subset is Community-accessible (measured),
     and block-level/hourly frequencies
     and PIT Flows are professional. This was measured by metadata and zero-row probes (§4.1).
   - The finalization brief's premise that `FlowIn…` entries are not community-flagged holds for the 1b/1h entries, but
     **not** for the daily BTC/ETH entries (`community: true`; HTTP 200 versus HTTP 403 at 1h). The audit records the
     measured state. It does not assert either "free" or "not free" as a blanket statement. The PIT decision is
     unaffected.
   - The sub-audit reports keep their original wording: L3 said "Pro-tier only", D1 said "free tier includes FlowInEx*".
2. **Stablecoin label wording.**
   - *Before:* the mechanism was classified `PIT_LABEL_BLOCKED` (§1, §13), and "net new issuance cannot be separated
     from chain swaps and bridges without issuer labels that Tether does not publish" was used as a blocking reason.
   - *After:* three objects are separated (raw mint/burn events; token totalSupply; economic/circulating aggregate).
     The first two are RAW_CHAIN_RECONSTRUCTABLE. The aggregate is rule-dependent, and its problems are
     semantic/aggregation problems, which become PIT-label-dependent only if a rule uses historically changing entity
     labels.
   - The audited construction is the label-free raw-contract one. Gate Q2 FAIL→PASS, Q10 FAIL→PASS, Q11 FAIL→UNRESOLVED.
     Mechanism decision: `MECHANISM_TOO_WEAK`.
   - The code's `labels_required` became `identification_required`, with explicit classes: fixed public contracts are
     not changing labels.
3. **Network activity.** Gate Q11 FAIL→UNRESOLVED. Semantic instability is a documented risk, not an established data
   block, and the decision rests on evidence. The previous primary code, DATA_BLOCKED, is withdrawn.
4. **Decision rule.**
   - `mechanism_decision` now takes the primary code from established FAILs (UNRESOLVED gates are listed but cannot set
     it when something has hard-failed).
   - `derive_programme_outcome` encodes the hierarchy: set aside PIT-label-blocked branches, then take the binding code
     of the label-free branches.
   - The earlier "common hard-fail code" rule and the tests built on it were replaced. The replacement tests cover the
     hierarchy, the all-blocked case and a mixed remainder.
   - Under the finalized table, ABANDON is no longer admissible (tested).
5. **Yae & Tian.** Recorded as general OOS caution about attention and trading volume. The accessible material does not
   show on-chain metrics being tested, and the paper is not used as evidence against them.
6. **Transfer study (TFSC 2021).** Now verified from the public abstract: senders and receivers are categorised as
   unknown, exchange or stablecoin treasury, and effects differ across the nine subsamples. It is label-dependent
   evidence.
7. **Ante, Fiedler & Strehle (FRL 2021).** Added the verified points: no significant raw returns in the 24 h after
   issuance; "lack of significant effects for USDC and GUSD"; the authors' "demand triggers the issuance" reading.
8. **The 0/33 count.** It is now a structured summary consistent with the decision, not its basis (§1.2).
