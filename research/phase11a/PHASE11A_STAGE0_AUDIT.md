# PHASE 11A — STAGE 0 AUDIT: commodity hedging pressure / CFTC positioning

Date: 2026-09-26. **FINALIZED 2026-09-26: `COMMODITY_HEDGING_PRESSURE_STAGE0` → `MECHANISM_TOO_WEAK`; Stage 1 `NOT_AUTHORIZED`.**
**Mechanism + data + deployability audit only. This is not a backtest. No return series of any kind was loaded.**

Evidence: `reports/phase11a/raw/`: `literature/` (tracked source log `SOURCES.txt`; the downloaded papers are kept
locally and git-ignored), `cftc/` (official cftc.gov pages;
each `.txt` extract carries its cftc.gov path; archived schedules in `cftc/wayback/`, named by Internet Archive capture
timestamp) and `products/` (each file records its source URL, retrieval date and method; the directory is labelled
`INTERRUPTED_UNVERIFIED_ARTIFACT`); machine outputs in
`reports/phase11a/cftc_audit/`. Code: `research/phase11a_cftc_audit.py` (metadata/calendar only), tests
`tests/test_phase11a_cftc_audit.py` (22 tests).

---

## 0. Lock and scope declarations (read first)

| Item | Status |
| --- | --- |
| **Phase 11A** | **`COMMODITY_HEDGING_PRESSURE_STAGE0`** |
| **Decision** | **`MECHANISM_TOO_WEAK`** (Stage 0 decision D; final, 2026-09-26) |
| **Stage 1** | **`NOT_AUTHORIZED`**: no preregistration, no experiment ID, no exploratory backtest |
| **Strategy cells added** | **0** |
| **Cumulative strategy-cell ledger** | **490** |
| **Commodity strategy returns inspected** | **NO** |
| **Commodity ETP return series loaded** | **NO** |
| **Existing equity validation window touched** | **NO** (2018-01-01..2021-12-31; no equity file opened) |
| **Existing equity final holdout touched** | **NO** (2022-01-01..2026-08-31; no equity file opened) |
| **Product audit** | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** (§6–§10) |
| **Historical release-map audit** | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** (§4.1) |
| Commodity futures, ETC/ETP/ETF price, NAV, index-level or return series | **none requested, downloaded or read** |
| Performance figures from factsheets / issuer pages | **none recorded** (the product audit was instructed to ignore them) |
| CFTC position values (long/short/spreading/OI/%/changes/trader counts/concentration) | **never parsed.** Every CFTC read goes through `read_metadata()`, whose whitelist admits only market name, report date and contract/commodity codes and raises if anything else is returned (tested). Only file headers were read in full. |
| Existing experiment results | **unchanged** (one tracked Phase 8B artefact, `research/phase8b/phase8b_gold2_preflight.json`, has its `checked_utc` timestamp rewritten by an existing test on every suite run; it was restored with `git checkout` and is not part of this commit) |
| Third-party papers | downloaded PDFs and full-text conversions kept locally and **git-ignored**; bibliographic details, URLs and table locations are in the tracked `SOURCES.txt` |
| Literature numbers quoted below | published third-party results, not computed here |

### 0.1 Workstream completion status (finalization record)

Stage 0 was stopped on the user's instruction of 2026-09-26, after the mechanism gate had already failed. Two
workstreams were still open at that point. They were **terminated, not completed**, and are reported below as partial.

| Workstream | Status | Section | State at closure |
| --- | --- | --- | --- |
| Literature audit | **COMPLETED** | §2 | 11 papers tabulated with timing class; the decisive statistics in §1.1 were re-checked at finalization against table positions in the saved documents, and the misreadings found are corrected (§15) |
| CFTC schema / timing audit | **COMPLETED** | §3, §4.3, §4.4 | 22 official files hashed; schema, report-date calendar, abnormal periods, revisions, venue close vs release time, causal convention |
| Signal-definition / sign-convention audit | **COMPLETED** | §5 | canonical AHP-PMPU(52); five published conventions reconciled; tested |
| Causal issues | **COMPLETED** | §2.3, §3.2, §3.6, §4.4 | Tuesday alignment in the literature, 1992–2000 biweekly discrepancy, 2007–08 restatement, 2006–09 backcast, "schedule is not a record" |
| Analytic power analysis | **COMPLETED** | §12 | ex-ante analytic power calculation from published effect magnitudes; no data used; not a backtest |
| Historical release-map audit (archived release-calendar reconstruction) | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** | §4.1–§4.2 | archive acquisition rate-limited, then stopped; the recovered archive is incomplete (2008 and 2025 unusable, 2009 nearly empty); no historical release map was built |
| Product audit (Trading 212, mapping, price data, costs, survivorship) | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** | §6–§10 | product agent interrupted; partial metadata recovered (16 of 47 candidate rows checked on Trading 212); `product_metadata.csv` labelled `INTERRUPTED_UNVERIFIED_ARTIFACT`; no CFTC → ETP mapping certified |

**Why these two were terminated rather than finished.** Neither could reverse the decision. The decision rests on
published evidence (§1.1) computed with timing at least as favourable as a Friday release and with costless, perfectly
tracked futures. A perfect causal release reconstruction could only confirm that our implementable signal arrives no
earlier than the literature's, which leaves the premium the same or smaller, never larger. Perfect ETP availability could
only remove a second-order implementation drag. It cannot create a long-only premium that no study documents, lift a
post-2004 t of 1.84 or a producer-category t of 1.61 over the gate, or raise the power in §12, which already assumes
perfect tracking at zero cost. Finishing either workstream would have spent more time and more archive and web requests
on an answer that could not change the outcome. Both were already idle when the stop instruction arrived (the last
artefact was written at 17:47; no fetch process was running). No further archive, issuer or broker request was made.

---

## 1. Executive conclusion

# STAGE 0 DECISION: D — MECHANISM_TOO_WEAK

**Stage 1: `NOT_AUTHORIZED`. Strategy cells added: 0. Cumulative ledger: 490. Commodity strategy returns inspected: NO.**

### 1.1 Core stopping argument

The mechanism fails in the form a EUR 500–1,000 long-only investor could actually trade. Every statistic below is a
published third-party result, not computed here. Each was re-checked at finalization against the table positions in the
saved documents; `literature/SOURCES.txt` records the table locations.

**A. The contemporaneous relationship is not sufficient.** The canonical hedging-pressure relationship is
contemporaneous. Gorton-Hayashi-Rouwenhorst (RoF 2013) find hedging pressure related to returns contemporaneously
(R² ≈ 10%), but not when it is measured at the start of the return interval (R² < 1%), and their HP-sorted portfolios were
"not informative". CFTC positions become public only on the Friday after the Tuesday they describe (§3.3). A signal
this programme can trade must survive that public-information lag, and a contemporaneous correlation cannot be traded.

**B. Ordinary lagged hedging pressure does not predict future returns.** In the KRT evidence recovered here
(Kang-Rouwenhorst-Tang, December 2016 version of JF 2020, Table 6, column 1), the weekly Fama-MacBeth slope of next-week
excess returns on lagged hedging pressure, with expected-return controls, is −0.07 (**t ≈ −0.43**). This is consistent
with two other studies. Szymanowska et al. (JF 2014) find HP-sorted spreads with t = 1.31–1.77, spanned by basis.
Sanders-Irwin-Merrin (2009) find no pervasive Granger forecasting. All of these use timing at least as favourable as the
Friday release.

**C. The 52-week smoothed construction is materially stronger, but specialised.** The same KRT table replaces HP with
its trailing 52-week mean and obtains 0.54 (**t 3.35**). That uses Legacy commercial positions for 26 commodities,
1994-01 to 2014-11, with controls. This is a different and more specialised construction: a slow "insurance demand"
component that KRT deliberately separate from short-term liquidity demand. It is not a robust result for generic COT
positioning. It is the only construction in the audited literature that survives a lag, and its pre-release
contamination is ≤ 1/52 of the signal.

**D. On Disaggregated producer/merchant data it weakens materially.** KRT Table 9 uses Disaggregated COT data with
producers/merchants as the hedger proxy, weekly from 2006-01-03 to 2014-11-01, with position changes Q included in both
columns. There the smoothed-HP coefficient falls from **0.85 (t 2.64)** to **0.58 (t 1.61)** once log-basis, past-return
and idiosyncratic-risk expected-return controls are added. The 2006–2009 part of that window is CFTC backcast data
(§3.6).

**E. The newer and sub-period evidence does not establish a robust modern within-commodity effect.** The source is
Maréchal's replication (slides dated 2022-08-16; the published JFM 2023 version was not read). The extracted tables show
exactly this:
* **Fama-MacBeth (slide 12).**
  * Full-period specifications are significant or borderline: KRT specification 0.43 (t 2.67); 1994–2020 0.41 (t 2.33);
    CIT 0.38 (t 2.04); "3+" 0.55 (t 1.98); optimal risk adjustment 0.34 (t 1.93).
  * The separately estimated sub-periods are both insignificant: **pre-2004 0.25 (t 0.92)** and **post-2004 0.43
    (t 1.84)**.
* **Panel (slide 13).**
  * 1994–2017: 0.33 (t 2.28); with basis, momentum, basis-momentum and crowding controls, 0.33 (t 2.24).
  * Pre-2004: 0.48 (t 2.26); with controls, 0.50 (t 2.36).
  * **Post-2004: 0.25 (t 1.34); with controls, −0.37 (t −0.76).** Commodity fixed effects are ticked only for this last
    column, so it is the only within-commodity estimate. It is insignificant, and its negative point estimate is not a
    significant negative result.
* **The author's own summary** has two parts. KRT's results are robust to the financialization period in the
  Fama-MacBeth regressions. The panel, however, shows a reduction of the insurance price in the post-financialization
  period.

In short, no post-2004 estimate is significant in either method, and the single within-commodity post-2004 estimate is
insignificant.

**F. The classic evidence is long-short, cross-sectional and in futures.** Basu-Miffre (JBF 2013; abstract and a
secondary description only, since the full text was not obtained), Szymanowska et al., KRT and Maréchal all report
long-short portfolio spreads or cross-sectional slopes over roughly 20–31 futures, gross of costs. De Roon et al. use
per-market futures regressions, also gross of costs. No adequate
evidence was found that the component this programme could use has a sufficiently strong standalone premium. That
component must be **LONG-ONLY, PUBLICATION-LAGGED and RETAIL-ETP-IMPLEMENTABLE**. No audited study reports the long leg
alone, measures it after the public release, models costs, or trades it through ETPs. The one post-release split in the
literature (KRT days 5–20) concerns position changes (Q), not the smoothed level.

**G. The retail implementation adds frictions; it cannot strengthen the prior.** The partial material in §6–§10 shows
five of them:
* **futures-to-ETP proxy risk:** physical-metal ETCs earn spot; futures ETCs track index subindices, not the contracts
  whose positions form the signal; LME-priced industrial metals are not CFTC-reported;
* **product-structure and roll-methodology differences:** WisdomTree WTI moved to a multi-tenor index on 2020-08-04;
  Natural Gas and Lean Hogs have unexplained ISIN reissuance; about 192 WisdomTree/ETFS products closed in 2018–19;
* **bid/ask spreads:** not measured;
* **possible FX cost:** 0.15% each way on any line not quoted in the account currency;
* **small-capital concentration:** EUR 500–1,000 spread across about 5 lines.

**Power (§12: an EX-ANTE ANALYTIC POWER CALCULATION FROM PUBLISHED EFFECT MAGNITUDES, not an empirical Phase 11A
backtest).** Under plausible modern attenuation, the only realistically available test (2011–2018) has power of roughly
5–25%. A null result would therefore be only weakly informative, while a positive result would carry substantial
false-positive risk given the programme's broader search burden.

**Therefore** the expected value of spending another strategy cell is insufficient given the programme's existing search
burden (490 cells). **No Stage 1 preregistration is authorised.** The data, timing and sign-convention work is preserved,
so a reopening (§14) would start from it rather than from nothing.

### 1.2 What the decision does not rest on

Data availability was not the binding constraint. CFTC Legacy and Disaggregated histories are free and schema-stable
(byte-identical headers across every annual file), and they carry stable contract codes. The release is at 15:30 ET,
after every European ETC venue has closed, so the first tradeable price is the next European session (§4.3). Publication
dates from 2004 onward **appear** reconstructible from archived official schedules plus the CFTC's special announcements
and shutdown press releases. However, that reconstruction was **terminated partial** (§4.1). **No verified
report-to-release map exists**, and nothing in this document should be read as saying one does.

### 1.3 Secondary finding: recorded, not a hypothesis

The *other* KRT premium is short-term liquidity provision, measured from week-to-week position changes (Q). In the paper
it partly survives into the post-release window (days 5–20: 0.433% of a 0.667% 20-day long-short quintile spread). It
is a different mechanism and requires weekly turnover. Even a symmetric long-leg share of that gross spread (≈ 0.22%) is
below the 0.30% FX round trip on any line not quoted in the account currency (§9; spreads were not measured). For this
investor it is **IMPLEMENTATION_BLOCKED**, and it is not the object of this Stage 0 decision.

### 1.4 Excluded as post-hoc rescue

None of the following is a hypothesis, and none may be proposed as a follow-on to this Stage 0:

* net-trading or position-change (Q) signals;
* managed-money or other speculator positioning;
* alternative smoothing windows or normalisations;
* carry- or basis-conditioned positioning;
* Legacy-commercial or any other neighbouring COT construction;
* any further COT diagnostic.

Each would reuse the mechanism that just failed, with a new degree of freedom chosen after seeing the literature's
results.

---

## 2. Literature audit

The per-paper extraction was done from the papers downloaded to `reports/phase11a/raw/literature/`. Those PDFs and
full-text conversions are third-party copyrighted material, kept locally and git-ignored. The tracked record is
`SOURCES.txt`, which holds bibliographic details, URLs and the table locations of the decision-relevant statistics.
Timing class: **A** contemporaneous; **B** predictive but using information possibly unpublished at formation;
**C** implementable (uses only information public at formation).

### 2.1 Per-paper table

| Paper | Positioning variable, normalisation, sign | Category / data | Construction, holding | Publication-timing assumption | Class | Universe / sample | Long-only leg | Costs | Post-2005 | Subsumed by basis/carry? | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| De Roon, Nijman & Veld (JF 2000) | q = (short hedge − long hedge)/(total hedge positions); **positive = hedgers net short → higher long return** | Legacy commercial ("hedgers") via Futures Industry Institute | own- and cross-market time-series regressions, semi-monthly | not discussed; GHR: "appear to be studying the contemporaneous correlation" | A/B | 20 futures, 1986–1994 | n/a (time-series slopes) | none | n/a | never tested vs basis | supportive but timing-suspect; **not replicated** by GHR |
| Bessembinder (RFS 1992) | conditional mean return by sign of net hedging | Legacy | conditional means | not verifiable (paper not obtained; secondary only) | A (inferred) | ~20 futures | n/a | none | n/a | not tested | supportive, UNVERIFIED primary text |
| Wang (JFM 2001) | 3-year min-max normalised net position ("sentiment index"); hedger SI high → **lower** future return | Legacy large hedgers / speculators / small | non-overlapping K = 2–12 week regressions | states Friday publication of Tuesday data, but regressions start at the Tuesday | B | 6 ag futures, 1993–2000 | n/a | none | n/a | not tested | supportive, narrow, pre-2000 |
| Sanders, Boris & Manfredo (EE 2004) | DNV-type measure | Legacy | Granger tests, weekly | not verifiable (secondary) | B | 4 energy, 1990s–2003 | n/a | none | n/a | n/a | **negative** (secondary only) |
| Gorton, Hayashi & Rouwenhorst (RoF 2013; NBER 2007) | commercial **net LONG** / OI (opposite sign: **negative** slope expected) | Legacy | monthly HP at t vs t−1; portfolio sorts | lagged one full month (still no publication-lag modelling) | A (works) → B (fails) | 31 commodities, 1969–2006 | sorts "not informative" | none | n/a | **yes** — inventories/basis drive premia | **negative**: "we reject the Keynesian 'hedging pressure' hypothesis" |
| Sanders, Irwin & Merrin (JAAE 2009) | percent net long (DNV-style) and Wang SI | Legacy, 3 categories | Granger causality, weekly | **explicitly Tuesday-coincident**: "the collected prices are coincidental with the reported positions" | B | 10 ag, 1995–2006 | n/a | none | to 2006 | n/a | **negative**: commercials lead returns in 3/10 markets, "not a pervasive theme" |
| Basu & Miffre (JBF 2013) | hedgers' HP = **long/(long+short)** — buy the **lowest** (per Miffre-Brooks 2013, secondary) | Legacy hedgers & speculators | single and double quintile sorts on R-week mean HP, hold H weeks, long-short | full text not obtained; secondary: "for the previous week" | UNVERIFIED | ~27 commodities, 1992–2011 | abstract: long-short Sharpe "exceed[s] ... long-only commodity portfolios" | UNVERIFIED | UNVERIFIED | Miffre-Brooks equate low hedger HP with backwardation | supportive, long-short, body UNVERIFIED |
| Szymanowska, de Roon, Nijman & van den Goorbergh (JF 2014) | DNV formula verbatim | Legacy | bimonthly quartile sorts | not discussed | B | 21 commodities, 1986–2010 | not reported for HP | none | not reported for HP | **yes** — "spot premia are better characterized by the basis factor"; HP "shows up only marginally, if at all" | **negative**: P4−P1 5.58/5.75/4.17/5.09%, t 1.66/1.77/1.31/1.64 |
| Bhardwaj, Gorton & Rouwenhorst (NBER 2015) | no HP test | — | basis sorts out of sample 2005–2014 | — | — | — | — | — | basis premium survives | — | context only: basis, not HP, is the robust post-2005 driver |
| Kang, Rouwenhorst & Tang (JF 2020; 2016 draft read in full) | HP = (hedger **short − long**)/OI; **smoothed HP** = trailing 52-week mean; Q = Δ net long / OI | Legacy commercial; DCOT robustness | weekly Fama-MacBeth with basis, past-return, idiosyncratic-risk controls; double sorts | FM: Tuesday HP → next Tuesday-to-Tuesday return (includes 3 pre-release sessions); sorts split days 1–4 (pre-release) vs 5–20 | raw HP: B, **t −0.43**; smoothed HP: B but ≈C (1/52 of signal is pre-release) | 26 commodities, 1994-01..2014-11 in the Dec-2016 version read (DCOT 2006-01..2014-11) | not reported | none | COT smoothed HP 0.54, t 3.35 (full); **DCOT producers 0.85 (t 2.64) → 0.58 (t 1.61) with controls** | smoothed HP survives basis control on Legacy; **not significant on DCOT with controls** | **mixed**: the only construction that survives a lag |
| Maréchal (JFM 2023; 2022 slides) | AHP = 52-week mean of (commercial short − long)/OI | COT 1994–, DCOT 2006– | FMB 1994–2020; panel 1994–2017 (commodity fixed effects in one column only) | Tuesday-to-Tuesday on AHP(t−1) | as KRT | 26 futures | not reported | none | **FMB: full-period significant (t 2.33–2.67); separately estimated pre-2004 t 0.92 and post-2004 t 1.84, both insignificant. Panel: post-2004 0.25 (t 1.34); with controls and commodity FE −0.37 (t −0.76); pre-2004 significant (t 2.26–2.36)** | FMB with optimal risk adjustment 0.34 (t 1.93); panel with B/M/BM/CR controls: post-2004 insignificant | **does not establish a robust modern effect**; author: FMB results robust to the financialization period, but the panel shows a "Reduction of the insurance price in the post-financialization period" |

### 2.2 Supportive vs negative / contradictory evidence

| SUPPORTIVE | NEGATIVE / CONTRADICTORY |
| --- | --- |
| DNV 2000: own-HP slopes positive and significant in 18/20 futures (1986–94) — but contemporaneous per GHR, no basis control, not replicated | GHR 2013: lagged HP insignificant, R² < 1% vs 10% contemporaneous; HP sorts uninformative; hypothesis rejected |
| Wang 2001: hedger sentiment predicts reversals up to 8 weeks (6 ag futures, 1993–2000) | KRT 2020: raw lagged HP t = −0.43 |
| Basu-Miffre 2013 (abstract): long-short HP factors significant | Szymanowska 2014: HP sorts t 1.3–1.8; spanned by basis |
| KRT 2020: smoothed 52-week HP 0.54, t 3.35 (Legacy, 1994-01..2014-11) with log-basis, past-return and idiosyncratic-risk controls | KRT 2020 Table 9: DCOT producers 0.85 (t 2.64) without controls → 0.58 (t 1.61) with them |
| Maréchal (2022 slides): FMB full period 1994–2020 t 2.33 (KRT specification t 2.67); panel 1994–2017 t 2.24–2.28 and pre-2004 t 2.26–2.36; author calls the FMB results robust to the financialization period | Maréchal: separately estimated FMB sub-periods pre-2004 t 0.92 and post-2004 t 1.84 (both insignificant); panel post-2004 t 1.34, and −0.37 (t −0.76) with controls and commodity FE; author: reduced insurance price post-financialization in the panel |
| KRT 2020 liquidity premium (Q): survives basis control and partly survives into the post-release window | Sanders-Irwin-Merrin 2009, Sanders-Boris-Manfredo 2004: no forecasting power |
| — | No study reports a long-only / long-leg-alone HP result; no study models costs |

### 2.3 Who uses Tuesday positions as if known on Tuesday?

* **Explicitly Tuesday-coincident:** Sanders-Irwin-Merrin ("coincidental with the reported positions").
* **Formation at the Tuesday although the Friday release is acknowledged:** Wang (2001); KRT and Maréchal Fama-MacBeth
  regressions (Tuesday-to-Tuesday returns on prior-Tuesday HP — the first three trading days of each return precede
  the release). KRT's portfolio sorts are the exception: they report days 1–4 and 5–20 separately.
* **Not discussed at all:** DNV (2000), Szymanowska et al. (2014); Bessembinder (1992) and Basu-Miffre (2013) not
  verifiable from primary text.
* **Consequence.** For raw weekly HP or position changes the pre-release window is the whole signal; for a 52-week
  smoothed HP the pre-release contamination is about 1/52 of the signal and immaterial. That is the one reason the
  smoothed construction can be called approximately implementable (class ≈ C) despite the papers' Tuesday alignment.

### 2.4 The ten Stage 0 questions

| # | Question | Answer |
| --- | --- | --- |
| 1 | Does hedging pressure predict returns after the Friday delay? | **Raw level: no** (fails under any lag). **52-week smoothed level: yes in Legacy cross-sections (KRT, 1994-01..2014-11, t 3.35); not significant in the separately estimated post-2004 FMB (t 1.84) or on DCOT producers with controls (t 1.61).** Position *changes* (KRT Q): partly, days 5–20. |
| 2 | Does the strongest effect require long-short cross-sections? | **Yes.** Every significant result is a long-short or cross-sectional slope over ~26 futures; no long-only evidence exists. |
| 3 | Evidence for the long leg alone? | **None found** (vs EW commodity benchmark or vs cash). Szymanowska report leg splits only for basis sorts. |
| 4 | Carry / backwardation in disguise? | **Raw HP: largely yes** (Szymanowska span test; GHR inventory/basis; Miffre-Brooks equate low hedger HP with backwardation). **Smoothed HP:** survives the expected-return controls on Legacy 1994–2014; on DCOT producers the basis/past-return controls cut it from t 2.64 to t 1.61. |
| 5 | Survives post-2005 / financialization? | **Not established.** No post-2004 estimate in the audited tables is significant: Maréchal FMB 0.43 (t 1.84); panel 0.25 (t 1.34), and −0.37 (t −0.76) with controls and commodity FE. The author calls the FMB results robust to the financialization period, but the panel shows a reduced insurance price post-financialization. |
| 6 | Can CFTC contracts map to retail ETPs? | **Provisionally and only partly; that workstream was terminated (§7).** Precious metals are available on Trading 212, but only as physical-spot proxies. WTI and copper are available with index/methodology caveats. Most agriculture, livestock and remaining energy single-commodity lines were not checked on Trading 212. Soybean oil/meal, feeder cattle and standalone cocoa have no confirmed single-commodity ETC. LME metals are out of scope. |
| 7 | European hours vs 15:30 ET release? | Release is always after LSE/Xetra/Borsa Italiana close (even in DST mismatch weeks) ⇒ **next European session only**; no same-session lookahead is possible if the rule is followed. |
| 8 | Is turnover low enough? | **Smoothed HP: yes** (52-week window, monthly rebalance). Position-change (Q) variant: no. |
| 9 | Economic enough despite public, decades-old data? | A risk premium can persist despite publicity, but the measured post-2004 premium is statistically marginal in costless long-short form; for a long-only EUR 500–1,000 book it is not demonstrably economic. |
| 10 | Are CFTC revisions a material PIT problem? | **For Legacy 2007–2008 energy and Disaggregated 2006–2009: yes** (retroactive restatement; backcast classification). **For a Disaggregated 52-week signal from 2011: minor** (single-week corrections dilute to ≤ 2% of the signal; forward-only reclassifications create level breaks, listed in §3.6). |

---

## 3. CFTC schema and history audit (official sources; machine inventory)

Official sources saved in `reports/phase11a/raw/cftc/`: About the COT Reports, Explanatory Notes, Disaggregated
Explanatory Notes, Release Schedule (current + archived captures 2004–2026), Historical Compressed index, Historical
Special Announcements 2008–2025, press releases 6745-13, 7864-19, 9138-25, 9147-25. Machine outputs:
`reports/phase11a/cftc_audit/` (file manifest with SHA-256, schema stability, per-year report-date calendars,
target-contract coverage and name history). Raw zips: `data/raw/phase11a/cftc/` (not committed; hashed in the manifest).

### 3.1 Summary table

| Property | A. Legacy Futures Only | B. Disaggregated Futures Only |
| --- | --- | --- |
| Earliest date in file | 1986-01-15 | 2006-06-13 |
| Earliest **real-time published** date | monthly/semi-monthly from 1986 (see 3.2); weekly publication from 2000 | **2009-09-04** (22 markets); **2009-12-04** (remaining physical markets) |
| Backfill | pre-1990 mid-month data "not published" at the time (CFTC note) | 2006-06-13..2009 history **published 2009-10-20** (22 markets) and **2010-05-07** (rest), classified with **2009 classifications** ("CFTC does not maintain a history of large-trader classifications … backcasting approach diminishes the data's accuracy") |
| Schema | 129 columns, **identical** in all 11 files (1986–2016 file and each annual file to 2026) | 191 columns, **identical** in all 11 files |
| Rows / contract codes | 289,653 / 956 | 185,348 / 656 |
| Trader categories | Commercial (long, short); Noncommercial (long, short, spreading); Nonreportable (long, short) | Producer/Merchant/Processor/User (long, short); Swap Dealers, Managed Money, Other Reportables (long, short, spreading); Nonreportable |
| Open interest | `Open Interest (All/Old/Other)` | `Open_Interest_All/Old/Other` |
| Contract identifier | `CFTC Contract Market Code` (stable across renames) | `CFTC_Contract_Market_Code` (same codes) |
| Release date field | **absent** (only `As of Date`) | **absent** (only `Report_Date_as_YYYY-MM-DD`) |
| Frequency in file | 24/yr 1986–1991; weekly from 1992-10-06 | weekly |
| Duplicated code×date rows | 0 | 0 |
| Last report date on disk | 2026-09-22 (dates only) | 2026-09-22 (dates only) |

### 3.2 Frequency and publication-lag history (official, verbatim)

* "Beginning as of June 30, 1962, COT data were published each month … published on the 11th or 12th calendar day of
  the following month." (About the COT Reports)
* "switching to mid-month and month-end in 1990, to every two weeks in 1992, and to weekly in 2000." and "moving the
  publication to the sixth business day after the 'as of' date in 1990 and then to the third business day after the
  'as of' date in 1992."
* "For dates before September 30, 1992, only mid-month and month-end data is available … since the mid-month data was
  not published before that time, it may contain identifiable data errors and because a significant period elapsed
  between the report date for that data and its eventual compilation, it is not possible to correct the errors."
  (Historical Compressed page)
* **Discrepancy found:** the Legacy file is **weekly from 1992-10-06**, but publication was **every two weeks until
  2000**. Whether each 1992–2000 biweekly release carried both Tuesdays could not be established from official text —
  **UNRESOLVED**. Any study using weekly 1992–2000 Legacy data (Basu-Miffre start 1992; KRT and Maréchal start 1994)
  may therefore use off-week observations that were not public three business days after the as-of date. Irrelevant
  for a ≥ 2010 window; relevant to how much weight the pre-2000 literature deserves.
* "Beginning in 1998, Commitments of Traders grain data has been reported in contracts rather than bushels" — the
  CBOT grain codes 001602/001612/002602/005602 begin 1998-01-06.

### 3.3 Normal release timing

"The weekly reports for Futures-Only … and for Futures-and-Options-Combined … are released every Friday at 3:30 p.m.
Eastern time" and "The COT reports provide a breakdown of each Tuesday's open interest". The release-schedule page:
"Federal holidays may delay release by one or two days" (2010 wording: "by one day"). Archived schedules mark
holiday-delayed releases with `*` (typically Monday; Tuesday on 2014-12-30).

### 3.4 Non-Tuesday report dates after 1993 (from the file)

1995-07-03, 1997-12-19 (Fri), 2000-07-05 (Wed), 2001-09-10, 2001-12-21 (Fri), 2001-12-28 (Fri), 2002-12-23,
2003-02-14 (Fri), 2003-12-22, 2004-04-12, 2006-07-03, 2007-01-03 (Wed), 2007-12-24, 2007-12-31, 2008-12-22,
2009-11-09, 2012-12-24, 2012-12-31, 2017-07-03, 2018-12-24, 2018-12-31, 2020-12-21, 2023-07-03, 2025-11-10 (all Monday
unless stated). A future loader must key on the report date, never assume Tuesday.

### 3.5 Abnormal publication periods (official)

| Period | Event | Source | Treatment in the release map |
| --- | --- | --- | --- |
| 2008-07-18 / 2008-07-25 | energy positions reclassified Commercial → Noncommercial; reports **revised back to 2007-07-03**; NYMEX html reports removed and reposted | HSA | revision (§3.6) |
| 2009-09-04 / 2009-12-04 | Disaggregated starts (22 / all physical markets) | Disaggregated Explanatory Notes | real-time start |
| 2011-04-08 notice | COT not published in any week with a funding-lapse furlough Wed–Fri | HSA | policy |
| 2011-11 | MF Global transfers; some contracts unpublished for 2011-11-08 | HSA | not our contracts |
| 2012-11-27 report | reports incomplete; **updated reports published 2012-12-05** | HSA | override → 2012-12-05 |
| **2013-10-01..10-29 reports** | lapse in appropriations; first catch-up 2013-10-25, rolling, "back on schedule by November 8" | PR 6745-13 | **conservative upper bounds** (10-25, 11-01, 11-01, 11-08, 11-08) |
| 2014-07-04 | reports inadvertently published a business day early (identical data) | HSA | harmless (earlier) |
| 2014-12-23 report | released **Tuesday 2014-12-30** | HSA | override |
| 2015-07-03 | "premature and incomplete" release; complete report 2015-07-06 | HSA | override → 07-06 |
| **2018-12-24..2019-03 reports** | lapse in appropriations; from 2019-02-01 one report every Tuesday and Friday until current | HSA, PR 7864-19 | see §4 |
| 2020-12-21 report | published 2020-12-28 | HSA | override |
| 2021-06-15 report | published 2021-06-21 (new Juneteenth holiday) | HSA | override |
| **2023-01-31..03-14 reports** | ION cyber incident; issued 2023-02-24 … 2023-03-21 | HSA | overrides (7 rows) |
| 2025-01-07 report | published 2025-01-13 (National Day of Mourning) | HSA | override |
| **2025-09-30..12-23 reports** | lapse in appropriations 2025-10-01..11-12; catch-up table 2025-11-19..12-29 | HSA, PR 9138-25, 9147-25 | overrides (13 rows) |

### 3.6 Revisions, corrections and reclassifications

1. **Retroactive restatement (Legacy, energy, 2007-07-03..2008-07-08).** "the Commission has now revised Commitments
   reports for markets affected by reclassified positions, for reports as of July 3, 2007, to date … the historical
   Compressed Reports … now reflect the improved data." The as-published values are not in any official file; even the
   html archive was replaced. **Material** for any Legacy energy signal in 2007–2008.
2. **Backcast classification (Disaggregated, 2006-06..2009).** Not public in real time; classified with 2009
   classifications. **Material**: non-causal before the publication dates in 3.1.
3. **Single-week corrections** (historical files hold the corrected values): cocoa 2009-06-23; cocoa/coffee
   2010-05-18; corn options 2010-08-17; all markets 2012-11-27; soybean options 2014-03-11; wheat/HRS wheat/corn/
   soybeans/sugar 2017-03-28; wheat SRW/HRW, corn, soybeans, soy oil, soy meal, lean hogs, palladium, platinum, silver,
   gold, cotton, cocoa, sugar, coffee 2019-03-26; corn/soy complex 2019-10-15; ION-period adjustments 2023 (not our
   contracts). **Minor** for a 52-week average (≤ 1/52 weight); material for weekly signals.
4. **Forward-only reclassifications (level breaks, no restatement):** copper Noncommercial → Commercial (Legacy,
   2009-08-21); copper Swap Dealer → PMPU (Disaggregated, 2009-11-13); cocoa Noncommercial → Commercial (Legacy,
   2013-07-19); index-supplement reclassifications 2015, 2018. A 52-week average carries such a break for a year.
5. The CFTC states that classification is by judgement, per trader, can change over time, and that it "classifies
   traders not their trading activity" — the hedger category is a label, not a measured hedge.

**Revision conclusion:** PIT-safe from 2011 onward for a Disaggregated smoothed signal, with the listed breaks; not
PIT-safe for Legacy energy 2007–2008 or any Disaggregated data before its publication dates. Magnitude of the 2008
restatement was **not quantified** (it would require a Wayback vintage of the 2007–2008 NYMEX pages); unnecessary for
the decision.

---

## 4. Causal timing audit

### 4.1 Historical release-map audit

**STATUS: PARTIAL / TERMINATED AS NON-DECISION-CRITICAL** (`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`)

* Archived CFTC schedule acquisition was rate-limited. The Internet Archive refuses connections under load, and the
  fetcher skipped refused requests without logging them. The acquisition was then stopped. **The recovered archive is
  incomplete.**
* Some years have substantial gaps, and coverage in some is effectively unusable: 2008 and 2025 yielded no parsable
  schedule dates, and 2009 yielded 4. Whether every intended capture was retrieved is not recorded.
* **No exhaustive historical release-date map was completed.** `python phase11a_cftc_audit.py releasemap` was never run,
  and no report-to-release mapping file exists (`legacy_report_to_release_map.csv`,
  `legacy_release_map_status_by_year.csv` and `legacy_release_map_summary.json` were never produced). The rolling
  2018–19 catch-up (PR 7864-19) was not transcribed into per-report dates. The size of the 2007–08 restatement was not
  quantified.
* The recovered schedules are **tentative published schedules, not records of actual releases**, and nothing in this
  document presents them as actual release dates. During the 2013 lapse the CFTC's own archived schedule still listed
  releases that never happened (§4.4).
* Official CFTC documentation was sufficient to establish that historical publication timing contains exceptions and
  delays that cannot be inferred from the nominal Friday schedule (§3.5). These include holiday delays; the 2013,
  2018–19 and 2025 funding lapses; the 2023 ION incident; and incomplete or re-issued reports.
* Once the Stage 0 mechanism gate had failed, completing the historical release map could not alter the programme
  decision (§4.2), so further acquisition was stopped.

Recovered material, preserved as found. These are research artefacts, not a release map:

| Item | State |
| --- | --- |
| Code | `fetch_schedules`, `parse_schedule_text`, `schedules`, `map_releases` and `release_map` in `research/phase11a_cftc_audit.py`; 3 parsing tests and 7 mapping tests pass on synthetic inputs |
| Documented exceptions transcribed from official text | 26 exact overrides (2012–2025); 5 conservative upper bounds (2013 lapse, PR 6745-13); 3 shutdown windows (2013, 2018–19, 2025) that force `UNRESOLVED` |
| Archived official schedule pages (cftc.gov, U.S. government) | 151 Internet Archive captures in `reports/phase11a/raw/cftc/wayback/`, 2004-02 to 2026-02 |
| Parsed **tentative** schedule | `reports/phase11a/cftc_audit/cftc_release_schedule_parsed.csv`: 1,057 tentative scheduled dates, 2003-12 to 2026-12, with holes in 2008, 2009 and 2025 |

A reopening (§14) must finish this before any signal is formed: diagnose the missing years, log fetch failures, run
`releasemap`, and reconcile every report date. The §4.4 buffer reduces dependence on exact dates, but it does not
replace them.

### 4.2 Why the reconstruction was not decision-critical

Every result in §1.1 is computed with Tuesday-aligned or otherwise *earlier* information than a Friday-release rule
allows (§2.3). A perfect release map can only certify that an implementable signal arrives no earlier than the
literature's, which leaves the premium the same or smaller. It cannot turn t = −0.43, 1.61, 1.84 or −0.76 into a pass.
For the 52-week signal the pre-release share is ≤ 1/52 in any case.

### 4.3 European venues versus the 15:30 ET release

| Venue | Continuous trading ends / closing auction | 15:30 ET in local time (normal) | In DST mismatch weeks |
| --- | --- | --- | --- |
| London Stock Exchange | 16:30 UK (closing auction ~16:30–16:35) | 20:30 UK | 19:30 UK |
| Xetra | 17:30 CET (closing auction to ~17:35) | 21:30 CET | 20:30 CET |
| Borsa Italiana ETFplus | 17:30 CET | 21:30 CET | 20:30 CET |

(Exchange hours per the official sources in `reports/phase11a/raw/products/`.) US DST starts on the second Sunday of
March and ends on the first Sunday of November; the UK/EU change on the last Sundays of March and October. In every
configuration the CFTC release is **≥ 3 hours after** the European close, so the release-day European price is never
available to the signal.

### 4.4 Causal convention (for any reopening)

1. Each report is usable only from the **first European trading session of the execution venue strictly after its
   documented release date** (`first_session_after`, tested).
2. Execution price: that session's **closing-auction price**. The open is not used (ETC opening prints are thin and
   often stale).
3. Rebalancing: monthly, on the first session of the month D, using the latest report that satisfies **both**
   (a) its documented release date is strictly before D, and (b) its report date is **≤ D − 11 calendar days**. Rule (b)
   is a one-week safety buffer: a normal report is then at least 8 days past its Friday release, so any undocumented
   delay of up to a week cannot leak into the signal. For a 52-week average the buffer costs nothing.
4. Reports with status `UNRESOLVED_*` are never used; if the latest usable report is more than 21 calendar days old, the
   portfolio is held unchanged.
5. The Tuesday/Wednesday/Thursday/Friday closes of the report week are **never** used for entry.

Why the buffer is necessary: the archived tentative schedule is **not** a record of actual releases. The captures of
2013-11-06 and 2013-12-02 still list 2013-10-04/11/18/25 releases that never happened (the 2013 lapse), and the CFTC
Historical Special Announcements page, which documents every other disruption since 2008, **does not mention the 2013
shutdown at all** — it is documented only in press release 6745-13. The exception list is therefore demonstrably not
exhaustive, and the reconstruction "tentative schedule + documented exceptions" must be treated as a lower bound on
lags, with the buffer absorbing short undocumented delays and the shutdown windows handled explicitly.

---

## 5. Canonical signal definition and sign convention

### 5.1 The one construction a reopening should use

**AHP-PMPU(52)** — Kang-Rouwenhorst-Tang smoothed hedging pressure on the Disaggregated producer category:

    HP_c,w   = (PMPU_Short_c,w − PMPU_Long_c,w) / OpenInterest_c,w        (Disaggregated, futures only, "All")
    AHP_c,t  = mean of HP_c,w over the last 52 weekly reports whose documented release precedes t

Direction: **long the commodities with the HIGHEST AHP** (producers most net short relative to the market).

Why this and nothing else:

| Criterion | Choice | Reason |
| --- | --- | --- |
| Mechanism | level of hedging demand, smoothed | KRT: raw HP mixes insurance demand (+) with liquidity demand (−); only the slow component carries the Keynes-Hicks premium |
| Precedent | KRT (JF 2020), Maréchal (JFM 2023) | the only construction that survives a lag in the modern literature |
| Category | PMPU, not Legacy commercial | the CFTC itself: the commercial category "has also included swap dealers … regardless of whether their OTC counterparty was a commercial trader or a speculator" |
| Denominator | open interest | KRT/Maréchal precedent; measures hedging demand relative to the market that must absorb it |
| Causality | 52-week mean | pre-release contamination ≤ 1/52; documented release dates enforced anyway |
| History | real-time Disaggregated from 2009-12 ⇒ first full real-time 52-week window 2010-12 | see §11 |

Rejected alternatives (not to be run as variants): raw weekly HP (fails under lag); DNV/Basu-Miffre share measures
(monotone transforms of raw HP — same failure); Legacy commercial (swap-dealer contamination; 2007–08 restatement);
managed-money/speculator positioning (a different, trend-following mechanism); position changes Q (liquidity premium,
implementation-blocked).

### 5.2 Sign conventions in the literature (the Phase 10 hazard)

| Source | Formula | Higher value means | Long leg buys |
| --- | --- | --- | --- |
| De Roon et al. 2000; Szymanowska et al. 2014 | (short − long)/(short + long) of hedgers | hedgers more net short | **high** |
| Basu & Miffre 2013; Miffre & Brooks 2013 | long/(long + short) of hedgers | hedgers more net **long** | **low** |
| Gorton, Hayashi & Rouwenhorst 2013 | commercial net long / OI | hedgers more net **long** | **low** (negative slope expected) |
| Kang, Rouwenhorst & Tang 2020; Maréchal 2023 | (hedger short − hedger long)/OI | hedgers more net short | **high** |
| Wang 2001 | 3-yr min-max of hedger net long | hedgers more bullish | **low** |

Two of the five conventions are inverted relative to the other three. A future loader must compute the KRT form from
the raw `Prod_Merc_Positions_Short_All`, `Prod_Merc_Positions_Long_All` and `Open_Interest_All` columns and must carry
the test `test_krt_positive_means_hedgers_net_short` / `test_ghr_convention_is_the_negative`.

### 5.3 Worked example (FAKE numbers — no real data)

| Week | PMPU long | PMPU short | Open interest | HP = (S − L)/OI |
| --- | --- | --- | --- | --- |
| Commodity X, a typical week | 100,000 | 250,000 | 500,000 | **+0.30** |
| Commodity Y, a typical week | 180,000 | 150,000 | 400,000 | **−0.075** |

If X's HP averaged +0.30 and Y's −0.075 over the last 52 released reports, AHP_X = 0.30 > AHP_Y = −0.075.
Interpretation: X's producers sell forward far more than its users buy forward, so speculators must be paid to carry
the residual long risk — the insurance premium predicts a **higher** expected return on long X. The rule buys X, not Y.
Sanity check against the other conventions: DNV q_X = (250 − 100)/350 = +0.43 (high → buy); Basu-Miffre long share
= 100/350 = 0.29 (low → buy); GHR = −0.30 (low → buy). All agree on X once each sign is applied correctly.

---

> **§6–§10: Product audit. STATUS: PARTIAL / TERMINATED AS NON-DECISION-CRITICAL** (`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`)
>
> * The product agent was interrupted before it produced a complete, verified inventory.
> * The partial metadata files were recovered: `reports/phase11a/raw/products/`, 16 files, labelled by
>   `README_INTERRUPTED_UNVERIFIED_ARTIFACT.md`.
> * Some rows and artefacts are malformed or incomplete. `product_metadata.csv` is an **`INTERRUPTED_UNVERIFIED_ARTIFACT`**.
> * The partial material contains metadata only. It was **not** used to select instruments or to inspect returns.
> * **No final CFTC → ETP mapping was certified.**
> * Because the upstream mechanism gate failed, product verification was deliberately stopped. Nothing was re-fetched
>   at finalization, and the sections below summarise the partial material as it stood.

## 6. Trading 212 instrument audit: **PARTIAL / TERMINATED**

Source material: `reports/phase11a/raw/products/` (product agent, 2026-09-26). The agent's recorded method: individual
Trading 212 public instrument pages, with non-essential cookies declined and only name / ticker / market / ISIN
extracted. **No price, NAV or performance figure was recorded.** The agent's browser page-scripting permission was
withdrawn part-way through, which left several rows half-checked.

| Outcome on Trading 212 | Count | Instruments |
| --- | --- | --- |
| Listed; ticker, market and ISIN read from the T212 page | 10 | COMM, PHAU, PHAG, PHPT, IGLN, ISLN, SGLD, XGLD, AIGA (LSE); 4GLD (Xetra) |
| Listed; page title confirmed, ISIN only from an aggregator | 3 | CRUD, COPA, AIGI |
| Page exists, fields not extracted | 1 | PHPD |
| The ticker tried did not resolve (provisional negative; site search not tried) | 2 | CMOD.GB, BCFU.DE |
| **Not checked** | **31** | includes every remaining single-commodity energy, agriculture and livestock ETC (BRNT, NGAS, HEAT, UGAS, WEAT, CORN, SOYB, SUGA, COFF, COTN, CATL, HOGS), the grains and livestock baskets, the LME metals, the Invesco/Xtrackers silver/platinum/palladium lines and most broad-basket funds |

Verified platform facts (T212 help centre, retrieved 2026-09-26):
* ETCs are an offered Invest instrument class.
* Commission and custody are free.
* The FX fee is 0.15%, unchanged since the 2026-09-09 verification.
* "Most instruments" can be traded fractionally.

Unverified: the minimum order value (GBP 1 per a community thread only), per-ETC fractional eligibility, and Xetra
extended-hours access. The help-centre hours page labels UTC times "GMT" year-round; the in-app calendar is
authoritative.

**`product_metadata.csv`: `INTERRUPTED_UNVERIFIED_ARTIFACT`.** The header declares 21 columns, but 18 of the 47 data rows
have 22–23 fields (unquoted commas) and one has 20. A strict parser cannot read it, and positional parsing silently shifts
columns. It is **not repaired and must not be used analytically**; its SHA-256 is recorded in the directory's label file.
The counts above come from the agent's text log `t212_product_availability_checks.txt`, not from parsing the CSV.

## 7. CFTC contract → commodity → retail product mapping: **PARTIAL / TERMINATED**

**This is not a certified mapping.** It summarises what the interrupted material suggests. The grades are provisional,
not verified, and no index methodology document or KID was parsed in full.

| CFTC code(s) | Commodity | Candidate retail line(s) | Exposure actually delivered | T212 | Provisional grade |
| --- | --- | --- | --- | --- | --- |
| 088691 | Gold | PHAU, IGLN, SGLD, XGLD, 4GLD | physical spot, not a futures excess return | listed | available; proxy basis |
| 084691 | Silver | PHAG, ISLN | physical spot | listed | available; proxy basis |
| 076651 | Platinum | PHPT | physical spot | listed | available; proxy basis |
| 075651 | Palladium | PHPD | physical spot | page exists; ISIN unverified | unconfirmed |
| 085692 | Copper | COPA (Bloomberg Copper subindex) | futures/swap; COMEX vs LME reference **unconfirmed** | listed (title) | medium, unconfirmed |
| 067651 | WTI crude | CRUD | futures/swap; index changed to multi-tenor 2020-08-04 | listed (title) | medium; methodology break |
| 06765T | Brent | BRNT | futures/swap | not checked | unknown |
| 023651 | Henry Hub gas | NGAS | futures/swap; two ISINs unresolved | not checked | unknown |
| 022651 / 111659 | Heating oil / RBOB | HEAT / UGAS | futures/swap | not checked | unknown |
| 001602 / 001612 | Wheat SRW / HRW | WEAT (SRW vs HRW unconfirmed) | futures/swap | not checked | unknown |
| 002602 / 005602 | Corn / soybeans | CORN / SOYB (ISINs not captured) | futures/swap | not checked | unknown |
| 007601 / 026603 | Soybean oil / meal | no single-commodity line found | basket component only | — | unusable as single lines |
| 080732 / 083731 / 033661 | Sugar / coffee / cotton | SUGA / COFF / COTN | futures/swap | not checked | unknown |
| 073732 | Cocoa | standalone ETC not confirmed | — | — | unknown |
| 057642 / 054642 | Live cattle / lean hogs | CATL / HOGS (HOGS has two ISINs) | futures/swap | not checked | unknown |
| 061641 | Feeder cattle | none found | — | — | unusable |
| (not CFTC-reported) | Aluminium, nickel, zinc; AIGI basket | ALUM, NICK, ZINC, AIGI | LME-priced | AIGI listed | out of scope |

Only the precious-metal rows are confirmed tradeable, and they deliver spot rather than the futures returns whose
hedging demand forms the signal. The eligible universe of about 15 lines assumed in §12 was therefore **not**
established.

## 8. Price-data availability audit: **PARTIAL / TERMINATED**

Only sources were identified (`historical_data_sources.txt`). **No price, NAV or return file was requested, downloaded
or opened.**

* Issuer: WisdomTree factsheet/KID endpoints are reachable but the main site returned 403; iShares performance tabs were
  not opened; DWS sits behind a gateway page; Xetra-Gold has no NAV in the fund sense.
* Exchange: LSE Data Shop and Deutsche Börse market data (paid; not priced).
* Vendors: EODHD (the existing subscription) claims LSE/Xetra coverage, but its **ETC coverage depth and retention of
  delisted lines are untested**. LSEG and Bloomberg are out of scale for this project.
* Hazards recorded: ISIN-changing consolidations (confirmed on leveraged lines only), duplicate currency lines of one
  exposure, retention of delisted products, and the CRUD methodology splice.

Not done: any coverage test, vendor quote or point-in-time check for the specific ISINs.

## 9. Cost-model plan: **PARTIAL / TERMINATED**

No cost model was built.

Inputs obtained:
* Trading 212 commission 0 and custody 0.
* FX 0.15% each way on any line not quoted in the account currency. Most LSE ETC lines are USD-quoted; EUR-quoted Xetra
  lines avoid the fee.
* Product TERs of 0.12–0.49%, mostly aggregator-sourced, several UNVERIFIED.

Not obtained: bid/ask spreads (the Xetra Liquidity Measure and issuer indicative spreads were deliberately not opened),
closing-auction depth, and the minimum order size. A reopening would need measured spreads for each line before a
single cell is run.

## 10. Survivorship analysis: **PARTIAL / TERMINATED**

Documented in `products/` (mostly secondary sources; primary press releases where stated):

| Event | Evidence level | Relevance |
| --- | --- | --- |
| WisdomTree acquired ETF Securities' ETC business on 2018-04-12; about 192 duplicate or stale products closed by 2019-09 | secondary (aggregated) | a universe built from today's live list misses the closed lines |
| WisdomTree WTI Crude Oil (CRUD) index changed to Bloomberg WTI multi-tenor on 2020-08-04 | primary press release | one ticker splices two return processes |
| Leveraged WTI/Brent 3x ETCs compulsorily redeemed in 2020-03 | primary press release | leveraged, so outside scope; a family-level risk |
| Natural Gas and Lean Hogs each carry two ISINs (GB00… and JE00BN7KB…) | aggregator | unexplained ISIN discontinuity on unleveraged lines |
| db x-trackers closed five ETFs in 2017 | secondary (title/snippet) | unverified whether the DBLCI commodity fund was among them |
| Share consolidations with an ISIN change | confirmed on leveraged lines only | the mechanism exists issuer-wide |

Not done: the list of closed products, the dates and causes of the ISIN reissuances, and a rule-based point-in-time
universe.

---

## 11. Recommended split for this programme (if ever reopened)

This is a proposal only. No data from any segment was loaded, and it is void unless the branch is reopened under §14.

| Segment | Dates | Rationale |
| --- | --- | --- |
| DEVELOPMENT | 2011-01-01 .. 2018-12-31 (8 years) | first date at which a 52-week AHP can be built **only** from Disaggregated reports published in real time for all physical markets (all markets from 2009-12-04; 52 weeks ⇒ 2010-12); no backcast classification enters any signal |
| VALIDATION | 2019-01-01 .. 2022-12-31 (4 years) | contains the 2019 shutdown catch-up, 2020 (negative WTI; ETC roll events) and 2022 |
| FINAL HOLDOUT | 2023-01-01 .. 2026-08-31 (3.7 years) | contains the 2023 ION delay and the 2025 shutdown; genuinely untouched — no commodity price or return of any date has been loaded by this programme |

This is deliberately not the equity split (validation 2018–2021, holdout 2022–2026-08). It cannot be lengthened
honestly: moving DEVELOPMENT earlier requires either backcast Disaggregated data (non-causal) or Legacy commercial data
(swap-dealer contamination and the 2007–2008 energy restatement). **8 years is the real limit, and it is the main
reason a Stage 1 test would be weak.**

## 12. EX-ANTE ANALYTIC POWER CALCULATION FROM PUBLISHED EFFECT MAGNITUDES (not an empirical Phase 11A backtest)

**If** the branch were reopened under §14, Stage 1 would be: 1 primary cell (AHP-PMPU(52), long-only top tercile of
the eligible ETC universe, equal weight, monthly, next-session close execution) + 2 preregistered falsification cells
(publication lag + 5 sessions; Legacy-commercial AHP as a mechanism contrast) ⇒ **3 cells, ledger 490 → 493.** No
lookback, threshold or holding-period neighbours. **This hypothetical design exists only to size the power and the
multiplicity cost. It is not a preregistration and authorises nothing; Stage 1 is `NOT_AUTHORIZED`.**

The inputs are published magnitudes only; no position value, price or return was read:
* `σ` = 28.1% average commodity volatility (KRT Table 1);
* a 5-of-15 equal-weight basket against an equal-weight universe with ρ = 0.3, which gives a tracking error of about 8.6%;
* a slope of 0.43–0.58 %/week per unit AHP;
* a cross-sectional AHP gap Δ of 0.10–0.25 between the basket and the universe mean. Δ is **unknown**, because no
  position value was read.

Each row below spans Δ = 0.10–0.25:

| Scenario (8-year development window 2011–2018; gate t ≥ 2; gross, costless, perfect futures tracking) | Expected t | Power |
| --- | --- | --- |
| Modern slope (Maréchal post-2004 FMB, 0.43), 50% post-publication attenuation | ≈ 0.4–0.9 | ≈ 5–15% |
| KRT DCOT producer slope with controls (0.58), 50% attenuation | ≈ 0.5–1.2 | ≈ 5–20% |
| Modern slope, no attenuation | ≈ 0.7–1.8 | ≈ 10–45% |
| KRT DCOT slope, no attenuation (most favourable) | ≈ 1.0–2.5 | ≈ 15–70% |

**Interpretation.** Under plausible modern attenuation assumptions, the realistically available test has power poor
enough that a null result would be only weakly informative. A positive result would carry substantial false-positive
risk given the programme's broader search burden. Every real-world departure (costs, ETP proxy basis, a smaller Δ)
lowers power further. The slopes themselves carry t-statistics of only 1.61–1.84 in their sources, so even the
favourable rows assume the most favourable reading of evidence that is not itself significant. This is not an
optimisation problem, and no parameter here is to be tuned.

## 13. Risks and falsification points (for the record)

* The insurance premium is a between-commodity, near-static tilt: 52-week AHP ranks change slowly, so a long-only
  implementation is close to a fixed basket and its "effective sample" is a handful of commodities, not weeks.
* Proxy basis (§7): physical metal ETCs earn spot, not futures excess returns; futures ETCs follow index roll schedules
  (BCOM/other) rather than the front contract the positioning describes.
* FX: EUR/GBP account versus USD-denominated product lines (§9).
* Category labels are CFTC judgements that change over time (§3.6).
* Falsifiers that would have killed a Stage 1 cell: lag +5 sessions removes > 50% of the effect (would mean the result is
  pre-release leakage); Legacy-commercial version stronger than PMPU (would mean swap-dealer/index flow, not hedging
  demand); excess vs EW positive but return below cash (a carry-beta, not a premium, for this investor).

## 14. Final Stage 0 decision (closure record, 2026-09-26)

| Record | Value |
| --- | --- |
| Phase 11A | **`COMMODITY_HEDGING_PRESSURE_STAGE0`** |
| Decision | **`MECHANISM_TOO_WEAK`** |
| Stage 1 | **`NOT_AUTHORIZED`** |
| Strategy cells added | **0** |
| Cumulative strategy-cell ledger | **490** |
| Commodity strategy returns inspected | **NO** |
| Commodity ETP return series loaded | **NO** |
| Existing equity validation window touched | **NO** |
| Existing equity final holdout touched | **NO** |
| Product audit | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** |
| Historical release-map audit | **`PARTIAL_TERMINATED_NON_DECISION_CRITICAL`** |
| Experiment ID / preregistration / exploratory backtest | none / none / none |

Reopening conditions (any one would justify a fresh Stage 0 → Stage 1). Each must be documented from **external primary
sources**; none may be manufactured by our own diagnostics on COT data:

1. an out-of-sample study, 2010 or later, of smoothed **PMPU** hedging pressure with basis and momentum controls and
   t ≥ 2, ideally reporting the long leg separately;
2. evidence that the long leg alone beats an equal-weight commodity benchmark **and** cash after costs;
3. a data change that lengthens the causal Disaggregated history (none is possible retroactively), or a futures-based
   retail implementation within policy that removes the ETC proxy basis.

Not reopening conditions: the data being free; the timing being clean; top-journal full-sample t-statistics that do not
survive the post-2004, producer-category, controlled reading; finishing the partial workstreams in §4.1 and §6–§10; or
any construction listed in §1.4.

## 15. Corrections made at finalization (2026-09-26)

These were found while re-checking the decisive statistics against table positions in the saved documents. None of
them changes the decision.

1. **Maréchal panel columns.** The earlier source-log entry (`SOURCES.txt`, now annotated) and the draft of §1.1
   misassigned columns. The period headers on slide 13 each span two columns: 1994–2017 = (1)–(2), pre-2004 = (3)–(4),
   post-2004 = (5)–(6). Commodity fixed effects are ticked only for (6). The correct reading: 0.25 (t 1.34) is
   **post-2004 without controls**, not pre-2004. The pre-2004 panel estimates are **significant** (t 2.26–2.36). The
   only within-commodity estimate is post-2004 with controls, −0.37 (t −0.76), which is insignificant.
2. **Maréchal conclusion.** The author also states that KRT's FMB results are robust to the financialization period.
   That half of his summary is now recorded next to the panel-based "reduction of the insurance price" conclusion.
3. **KRT sample and controls.** The t = 3.35 and t = −0.43 statistics come from the December 2016 version. Its Legacy
   sample is 1994-01-02..2014-11-01 (the draft said 1994–2012). Both specifications include the log-basis, past-return
   and idiosyncratic-risk controls; the draft said "basis and momentum".
4. **Release map.** A draft sentence said publication dates "can be mapped" from 2004. No map was built, so §1.2 and §4.1
   now say so.
