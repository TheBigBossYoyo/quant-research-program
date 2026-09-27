# PHASE 11C — STAGE 0 AUDIT: U.S. Treasury term-structure risk premia / duration timing

Date: 2026-09-27. **`TREASURY_TERM_PREMIA_STAGE0` → decision `REAL_TIME_OOS_EVIDENCE_TOO_WEAK`; Stage 1 `NOT_AUTHORIZED`.**
**Literature + mechanism + point-in-time data + deployment audit only. This is not a backtest. No Treasury, ETF, SPY or
strategy return series was loaded, and no signal was constructed.**

Evidence lives in `reports/phase11c/raw/`:
- `sources/` holds five sub-audit reports: L1 classic literature, L2 modern OOS / real-time literature, D1 H.15 and
  Treasury PIT, D2 GSW / ACM / Fama-Bliss / Liu-Wu vintages, V1 Treasury UCITS metadata (+ CSV). They are preserved as
  agent artifacts. Where this audit corrects or supersedes them, §23 says so.
- `pit_checks/` holds the main audit's own measurements: FRED observation starts, ALFRED vintage counts, the blind
  vintage-equality check, the month-end release-lag check, and Wayback CDX capture metadata. The raw vintage files are
  in `pit_checks/QUARANTINE_VALUES_NOT_INSPECTED/` (git-ignored, hashed).
- `literature/SOURCES.txt` is the tracked source log; the papers themselves are local and git-ignored.
- `RAW_MANIFEST_SHA256.txt` hashes every raw file, including the quarantine folders.

Machine outputs are in `reports/phase11c/treasury_audit/`. Code: `research/phase11c_treasury_audit.py` (returns-free
utilities, gate table and decision rule). Tests: `tests/test_phase11c_treasury_audit.py` (57 tests).

---

## 0. Lock and scope declarations (read first)

| Item | Status |
| --- | --- |
| **Phase 11C** | **`TREASURY_TERM_PREMIA_STAGE0`** |
| **Decision** | **`REAL_TIME_OOS_EVIDENCE_TOO_WEAK`** |
| **Stage 1** | **`NOT_AUTHORIZED`**: no preregistration, no experiment ID, no exploratory test |
| **Primary construction surviving** | **none (zero candidates)** |
| **Strategy cells added** | **0** |
| **Cumulative strategy-cell ledger** | **490** |
| Treasury ETF returns, Treasury excess-return series, SPY returns, old equity or crypto strategy returns | **NOT loaded, NOT inspected** |
| Regression, Sharpe, CAGR, parameter scan, duration-switching backtest | **NONE** |
| Yield *values* | **Loaded only for a blind PIT check (§9.3), never printed, plotted or summarised.** Eleven ALFRED vintage files per tenor were compared by exact string equality, for observation dates up to 2017-12-31. Only counts, mismatch dates and the size of any revision were output. A presence-of-date check measured FRED release lags at 24 month-ends in 2006–2017. The downloaded files also contain rows after 2017 (the current vintage runs to 2026-09-24). Those rows were parsed only for their dates, to find each vintage's last observation. No yield-curve signal (slope, forward, CP factor) was computed at any date. |
| Equity validation 2018-01..2021-12 | **NOT OPENED** |
| Equity final holdout 2022-01..2026-08 | **NOT READ** |
| Old crypto holdouts (2025 validation, 2026 final) | **CLOSED**. No file under `data/` was opened. |
| Old strategy-result files | **Not opened.** Only `PHASE6B_CONCLUSION.md` and the E020 / E053 experiment *descriptions* in `EXPERIMENTS.md` were read, for §18. The brief requires this. These documents quote summary statistics of old experiments that were already recorded in `STATUS.md`. |
| ETF product pages | Metadata only (V1). The V1 sub-agent reports that a dividend yield, a weighted-average YTM, one bid/ask quote and one traded price appeared incidentally in its tool output. They were discarded and never written to a file or passed to this audit. No performance data was recorded. The quarantine folder is empty. |
| Third-party papers | Local and git-ignored. Published statistics were read and are cited with their locations. `[verified]` means the main audit re-read the number in the local full text. |

---

## 1. Executive conclusion

# STAGE 0 DECISION: REAL_TIME_OOS_EVIDENCE_TOO_WEAK

**The yield curve carries information about future Treasury excess returns in sample. But no simple, causal,
long-only construction has published real-time out-of-sample evidence of after-cost economic value strong enough to
justify a strategy cell. A future test would also have too little independent data to settle the question.**

The mechanism is not disproven. The brief anticipates this case: *strong in sample, weak in real-time OOS evidence
→ D, not "the mechanism does not exist"*.

The decision in six points (all numbers are third-party published statistics):

1. **In-sample evidence is real.**
   - Cochrane–Piazzesi: R² 0.34–0.37 for 1-year excess returns, 1964–2001 (up to 0.44 with a lag). Tent-shaped
     loadings recur in every subsample.
   - Fama–Bliss forward spread: R² 0.06–0.15 in the CP 2005 Table 3 replication.
   - Bauer–Hamilton (2018) "concur" that the core CP factor is a stable predictor.
2. **Recursive OOS evidence for the CP factor is essentially nil.**
   - GPT 2019 Table 3 `[verified]`: monthly OOS R², constant-coefficient OLS, 1990–2011, is **−1.58%, −0.45%, 0.25%,
     0.73%** for 2–5-year bonds.
   - Hodrick–Tomunen (2018) `[verified]`: the model "fails to beat historical average returns" recursively, and its
     coefficients are unstable across 2003.
   - Bauer–Hamilton `[verified]`: adding PC4/PC5 cuts in-sample MSE by 11% but *raises* OOS MSE by 21%.
   - Sarno–Schneider–Wagner (2016) `[verified]`: "ATSMs generally cannot beat the EH out-of-sample in terms of economic
     value".
3. **The simple forward spread has the only positive long-only recursive result, and it is thin.**
   - GPT 2019 Table 5 `[verified]` gives long-only weights [0, 0.99] in bond versus T-bill, A = 10, gross of costs,
     1990–2011, Fama-Bliss data. The linear FB model's CER versus the EH benchmark is **−0.23%, +0.06%, +0.46%\*,
     +0.67%\*\*** a year for 2–5 years.
   - It was not costed. It stops in 2011. Thornton–Valente (2012) at the 12-month horizon and Sarno et al. (2016) find
     no economic value.
4. **Every large economic value in the literature needs shorting, leverage or revised macro data.**
   - GPT: 2.95% needs weights in [−2, 3] and the macro factor `[verified]`.
   - Borup et al. (2024): weights in [−1, 2], and "little evidence" of value for individual predictors `[verified]`.
   - Fan–Feng–Fulop–Li (2022): gains require that "investors are allowed to leverage" `[verified]`.
   - Koijen et al. and Brooks–Moskowitz: long-short, gross of costs.
   - The one long-only practitioner test (Asness–Ilmanen–Maloney 2017, Table A.2 `[verified]`) finds value-based
     Treasury timing Sharpe **0.27 vs 0.27** buy-and-hold, gross of costs.
5. **Independent data are exhausted.** GPT's OOS window 1990–2011 is the literature's; any future test on it would
   replicate, not test. The remaining calendar (2012-01..2026-08, 14.7 years) overlaps the programme's locked
   2018–2021 and 2022–2026 windows. Treasury ETF returns for 2004–2017 (IEF, E053) and 2009–2019 (IBTL, E020) have
   already been read by this programme. At the literature's best monthly OOS R² (2%), with an assumed 50% long-only
   capture, one-sided power over 14.7 years is **~24%**. At R² 1% it is ~16% (§20).
6. **Costs can absorb the whole published long-only edge.** Two switches a year cost 12–80 bps (§19), against a gross
   CER of 46–67 bps at the 4–5-year maturities where any edge was found.

Data are **not** the binding problem:
- H.15 3m–10y yields are **PIT_SAFE by measurement** (§9).
- ACM is **PIT_BLOCKED** and is set aside (§11).
- Exact CP needs licensed Fama-Bliss, and GSW smoothing degrades the CP signal (§10, §12). But the slope class, which
  binds the decision, is fully PIT-safe and free.

---

## 2. Literature audit: per-paper records

Legend: **IS** = in sample, **OOS** = out of sample; **Rec** = recursive/expanding coefficients, **Full** = full-sample
coefficients; **RT** = real-time data. "L/S" = long-short or leverage allowed. Location tags: `[verified]` = re-read by
the main audit in local full text; `[FT]` = sub-agent full text, not re-read; `[ABS]` = abstract or secondary only;
`[UNV]` = unverified.

| Paper | Predictor | Data | Window | Horizon | IS / OOS | Coefficients | RT data | Maturities | Economic value | Costs | Long-only? | Needs leverage? | Modern persistence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cochrane & Piazzesi (2005, AER) | tent factor of y1 + 4 forwards | Fama-Bliss (CRSP), unsmoothed | 1964–2001 | 12m overlapping | IS; one real-time recursive check | Full (headline); Rec (check) | yields unrevised | 2–5y zeros | trading rule: real-time recursive estimate earns "only about half" the full-sample cumulative profit `[verified]` | no | unspecified directional rule | not stated | subsample R² 0.22–0.78 (Table 9) `[FT]`; sample ends 2001 |
| Fama & Bliss (1987, AER) | n-year forward − 1y yield | CRSP | to 1985 | 12m | IS | Full | – | 2–5y | none | no | – | – | CP 2005 replication 1964–2001: R² 0.06–0.15 `[FT]`; original PDF image-only `[UNV]` |
| Campbell & Shiller (1991, RES) | yield spread | postwar Treasuries | postwar (see L1) | various | IS | Full | – | 1m–10y | none | no | – | – | wrong-sign EH coefficients robust to subsamples `[FT]` |
| Thornton & Valente (2012, RFS) | FB and CP forward-rate models | Fama-Bliss | `[UNV]` | 12m | OOS asset allocation | Rec / rolling | – | 2–5y | "no systematic economic value" `[ABS]`; GPT 2019 describes it as failing to beat EH utility `[verified]` | – | weights bounded with shorting and leverage (Borup et al. "similarly to TV" `[verified]`) | L/S | reported deterioration over time `[ABS]` |
| Duffee (2011, RFS) | hidden factor (Kalman) | Treasury yields | see L1 | 1m / 12m | IS only | Full, two-sided smoothing | – | 1–5y | none | – | – | – | filtered (causal) R² 0.043 vs smoothed 0.085 `[FT]`; no OOS test in paper |
| Adrian, Crump & Moench (2013, JFE) | 5 PCs, regression ATSM | GSW | 1987–2011 recursive short-rate test | 1m | IS + Rec OOS (short-rate RMSE) | Full + Rec | – | 1–10y | none (forecast accuracy) | – | – | – | monthly CP-type R² 7.5% on GSW `[FT]` |
| Bauer & Hamilton (2018, RFS) | spanning tests; PC1–3 vs PC4–5 | several | to 2016 | 12m | bootstrap IS + true OOS | Full / OOS | – | 2–5y | none | – | – | – | PC4/5: OOS MSE +21% `[verified]`; CP trend variant: post-2011 MSE +221% `[verified]` |
| Sarno, Schneider & Wagner (2016, JEF) | ATSM risk premia (incl. ACM estimator) | GSW | see L1 | 1m–12m | OOS | Rec | – | 1–10y | cannot beat EH OOS `[verified]`; ACM estimator: negative OOS value `[FT]` | no | max leverage 100% `[FT]` | capped | – |
| Hodrick & Tomunen (2018, NBER 25092) | CP factor, several currencies | various | pre-2004 / post-2003 | 12m | Rec OOS | Rec | – | 2–5y | loses to historical mean `[verified]` | – | – | – | coefficient equality rejected across 2003 `[verified]` |
| Gargano, Pettenuzzo & Timmermann (2019, MS) | FB, CP, LN (macro), TVP-SV | Fama-Bliss; LN revised macro | warm-up 1962–1989, OOS 1990–2011 | 1m (also 3m, 12m) | OOS | Rec (Bayesian) | yields yes; macro revised | 2–5y | long-only [0, 0.99]: FB LIN −0.23/+0.06/+0.46/+0.67%; CP LIN −0.20/−0.15/+0.04/+0.18% `[verified]`; [−2, 3] up to 2.95% `[verified]` | only for the [−2, 3] case (10 bps one-way: 2.95→1.80%) `[verified]` | Scenario 1 yes (bond vs bill) | largest gains yes | "best performance … 1990 to 1993 and from 2001 onwards" `[verified]`; ends 2011 |
| Borup, Eriksen, Kjær & Thyrsgaard (2024, MS) | forecast combination, real-time state proxies | FB-type | recursive OOS | 1m | OOS | Rec | state proxies real-time (CFNAI, Chauvet-Piger) | 2–5y | individual predictors: "little evidence" `[verified]`; combination positive | asserted small, not deducted | no, ω ∈ [−1, 2] `[verified]` | yes | – |
| Wan, Fulop & Li (2021, JEconometrics) | macro factors, real-time vintages | ALFRED-type | – | 1m | OOS | Rec | **yes** | – | "no statistical or economic evidence" with real-time macro `[verified via Fan et al. 2022]` | – | – | – | concerns *macro* predictors, not yields |
| Fan, Feng, Fulop & Li (2022, WP) | deep learning, real-time macro + news | – | – | 1m | OOS | Rec | yes | 2–10y | gains require leverage `[verified]` | – | no | yes | – |
| Ghysels, Horan & Moench (2018, RFS) | macro factors, real-time vs revised | ALFRED | 1982–2011 | 12m | IS / pseudo-OOS | – | yes | 2–5y | – | – | – | – | macro predictability largely from revisions; yield-only benchmark unaffected `[FT]` |
| Cieslak & Povala (2015, RFS) | cycle factor (yields − trend inflation) | Fama-Bliss, CPI | see L2 | 12m | IS (OOS asserted, not tabulated) | Full | trend inflation real-time | 2–20y | none | – | – | – | Bauer–Hamilton: post-2011 OOS MSE +221% with the trend `[verified]` |
| Bauer & Rudebusch (2020, AER) | yields relative to i* | GSW / surveys | see L2 | 12m | IS for returns; Rec OOS for yield levels | Full / Rec | pseudo real-time i* | 1–10y | none | – | – | – | ΔR² 12 pp full sample, 6–9 pp post-1985 `[FT]` |
| Andreasen, Engsted, Møller & Sander (2021, RFS) | slope × expansion/recession | – | – | 12m | IS | Full | state timing `[UNV]` | – | – | – | – | – | `[ABS]` only |
| Andreasen, Jørgensen & Meldrum (2019, FEDS) | slope, ZLB regime (short rate < 1%) | GSW | 1990-01..2008-09 vs 2008-10..2015-11 `[FT]` | 12m | IS | Full | state is real-time | 2–10y | none | – | – | – | 10y R² ~10% → ~20% at the ZLB `[FT]` |
| Rebonato & Nyholm (2025, JEF) | CP factor, resampling test | – | – | 12m | IS (econometric validity) | – | – | – | none found | – | – | – | `[ABS]`: CP power attributed to a cointegrating combination of quasi-unit-root forwards, not to overfitting |
| Asness, Ilmanen & Maloney (2017, JOIM) | real-yield value; momentum | GFD / Ibbotson | 1900–2015, 1958–2015 | 1m | IS backtest | – | survey inflation | US 10y | Sharpe 1958–2015: B&H 0.27, value 0.27, momentum 0.38, V+M 0.33 `[verified]` | gross `[verified]` | long-biased tilt, average position 86–107% `[verified]` | occasionally > 100% | – |
| Koijen, Moskowitz, Pedersen & Vrugt (2018, JFE) | bond carry (slope + roll-down) | global | see L2 | 1m | IS / TS | – | – | 10y | carry premium | gross | no (long-short) | yes | – |
| Brooks & Moskowitz (2017, WP) | value/momentum/carry on level/slope | global | "live" OOS sample | 1m | OOS (ex-ante signals) | – | – | global | Sharpe 0.65–1.01 | gross `[FT]` | no (dollar-neutral) | yes | – |

Records per paper, with page and table locations, are in `raw/sources/L1_classic_literature.md` and
`raw/sources/L2_modern_oos_literature.md`.

### 2.1 Evidence categories

| Category | Papers | What it establishes |
| --- | --- | --- |
| **A. Strong in-sample** | CP 2005; Fama–Bliss; Campbell–Shiller; Duffee; Cieslak–Povala; Bauer–Rudebusch (returns); AJM 2019; Andreasen et al. 2021; Rebonato–Nyholm | Yield-curve variables correlate with subsequent excess returns in full-sample regressions, with stable tent loadings on unsmoothed data |
| **B. True out-of-sample** | GPT 2019; Thornton–Valente 2012; Sarno et al. 2016; Hodrick–Tomunen 2018; Bauer–Hamilton OOS test; Borup et al. 2024; ACM model comparison | Mixed. Positive statistical OOS R² for FB-type spreads (GPT); economic value versus EH fails in TV, SSW and HT; positive values mostly need leverage or combinations |
| **C. Real-time implementable, long-only, after costs** | **none** | No paper delivers real-time data + recursive OOS + long-only weights + explicit costs + positive value. GPT long-only FB (gross) is the closest; AIM 2017 is long-biased and gross, and its yield-based signal adds nothing |

---

## 3. SUPPORTIVE and CONTRADICTORY evidence tables

### 3.1 SUPPORTIVE_EVIDENCE_TABLE

| # | Evidence | Strength for *our* question | Why not enough |
| --- | --- | --- | --- |
| S1 | CP 2005 R² 0.34–0.44, subsample-stable tent | in-sample only | full-sample coefficients; real-time re-estimation halves trading profit |
| S2 | Bauer–Hamilton concur the core CP factor is stable | robust IS inference | not OOS economic value |
| S3 | Liu–Wu 2021: tent loadings persist to 2019 on an unsmoothed curve | construction robustness | IS |
| S4 | GPT 2019 FB spread: monthly OOS R² 1.77–2.61% (3–5y), long-only CER +0.46% / +0.67% (4–5y) | the only recursive, long-only, positive result | gross; ends 2011; 2y and 3y ≈ 0; bond vs T-bill, not short vs long duration |
| S5 | AJM 2019: slope predictability doubles at the ZLB | real-time state | IS only |
| S6 | Rebonato–Nyholm 2025: CP not an overfitting artefact | IS validity | abstract only; no OOS or value |
| S7 | Borup et al. 2024: combined forecasts give positive OOS R² and CER | OOS | combination scheme; ω ∈ [−1, 2] |

### 3.2 CONTRADICTORY_EVIDENCE_TABLE

| # | Evidence | Verified |
| --- | --- | --- |
| C1 | GPT 2019 CP (constant coefficients): monthly OOS R² −1.58%, −0.45%, 0.25%, 0.73%; long-only CER −0.20%, −0.15%, +0.04%, +0.18%, none significant | yes |
| C2 | Thornton & Valente 2012: forward-rate models give no systematic economic value to a dynamic allocator (12-month) | abstract + GPT's description |
| C3 | Sarno, Schneider & Wagner 2016: ATSMs "cannot beat the EH out-of-sample in terms of economic value"; ACM estimator negative OOS | yes (main text) |
| C4 | Hodrick & Tomunen 2018: CP "fails to beat historical average returns" recursively; coefficients unstable across 2003 | yes |
| C5 | Bauer & Hamilton 2018: PC4/PC5 OOS MSE +21%; conventional HAC size 19–36% instead of 5% | yes / FT |
| C6 | Bauer & Hamilton 2018: Cieslak–Povala trend variant post-2011 OOS MSE +221% | yes |
| C7 | Borup et al. 2024: "little evidence that predictable deviations from the EH can be exploited" for individual predictors | yes |
| C8 | Asness, Ilmanen & Maloney 2017: yield-based value timing of US Treasuries Sharpe 0.27 = buy-and-hold (1958–2015), gross | yes |
| C9 | GPT 2019: annual-horizon CER "substantially smaller"; the largest gains need [−2, 3] weights and revised macro data | yes |
| C10 | Wan, Fulop & Li 2021: no evidence with real-time macro data (macro predictors only) | via Fan et al. |
| C11 | CP 2008 Table 1: GSW-smoothed forwards give a W-shaped, multicollinear fit (R² 0.29 vs 0.35 on FB forwards) | FT |

---

## 4. Reconciling Cochrane–Piazzesi, Thornton–Valente and the newer positive literature

The three positions are mostly about **different objects**, so all three can be true together:

1. **CP (2005) is about in-sample population predictability at a 12-month horizon.** Its R² comes from full-sample
   coefficients on overlapping annual returns. Bauer–Hamilton and Rebonato–Nyholm defend it against the charge of
   *statistical* overfitting. Neither shows that an investor estimating the coefficients as data arrive could profit.
   CP's own real-time check is the first warning: recursive re-estimation earned "only about half" the full-sample
   trading profit, and the shortfall was concentrated in the 1983 episode.
2. **Thornton–Valente ask the real question:** would a recursive investor have gained utility over the no-predictability
   benchmark? At the 12-month horizon, with bounded long/short weights, the answer is no, and it gets worse over time.
   Sarno et al. (ATSMs, one month) and Hodrick–Tomunen (more data, more currencies) reach the same answer.
3. **The newer positive papers change the question to recover a yes.** GPT (2019) attributes their disagreement with TV
   to horizon (one month versus twelve), time-varying parameters, stochastic volatility, the LN macro factor, and
   looser weights. Their own table isolates the ingredients:
   - constant-coefficient CP has no OOS value even monthly (C1);
   - the monthly FB spread has small positive long-only value at 4–5 years only (S4);
   - the large gains come from TVP-SV machinery, the revised-data macro factor, and [−2, 3] weights.

   Borup et al. get value only from their own combination scheme under [−1, 2] weights. The deep-learning revival
   (Fan et al.) needs leverage.

**Verdict.** The later positive evidence does **not** establish REAL-TIME + OUT-OF-SAMPLE + LONG-ONLY + AFTER-COST
value for a simple yield-curve rule:
- *Real-time*: yes for yields; no for the macro inputs that carry the big results.
- *OOS*: yes.
- *Long-only*: only in GPT Scenario 1.
- *After-cost*: nowhere for the long-only case.

The one surviving fragment (monthly FB spread, 4–5 years, +0.5–0.7% CER gross, 1990–2011) is too thin, too
contested, and too dependent on one study and one era to carry a strategy cell.

---

## 5. Real-time coefficient estimation (the leakage issue besides data vintages)

- Every CP-type and FB-type rule needs coefficients estimated from returns. The trap: at a monthly decision date t with
  a 12-month target, the latest usable pair is (t − 12, t). Using pairs up to t leaks eleven months of future returns;
  a full-sample fit leaks everything. `usable_training_pairs` and `expanding_coefficients` implement the correct cut.
  A test poisons every target not realised by t and confirms the coefficients do not change.
- Does the published edge survive real-time estimation?
  - **For CP, largely not:** GPT constant-coefficient OLS OOS R² ≤ 0.73%, Hodrick–Tomunen, and CP's own halved profit.
  - **For the FB spread, partly:** GPT recursive OOS R² 1.8–2.6% at 3–5 years, monthly.
  - **Neither survives as after-cost long-only value** in any published study.
- A threshold rule with *no* return-estimated coefficient (e.g. "long duration when the slope is positive") avoids the
  leakage. But it is a different hypothesis with no OOS evidence at all, and in normal curves it collapses into "almost
  always long duration".

---

## 6. Must a low forecast mean *short* duration?

**In the literature, usually yes.**
- The unconstrained mean-variance weight is proportional to the forecast, so a negative forecast implies a short bond
  position.
- The headline economic values use weights of [−2, 3] (GPT), [−1, 2] (Borup; TV "similarly"), up to 100% leverage
  (SSW), or long-short construction (Koijen et al.; Brooks–Moskowitz).

**Our mandate cannot short.** It can only move between short-, intermediate- and long-duration Treasury lines, and
possibly a 0–1-year line. The only published long-only evidence is:
- GPT Scenario 1, a bond-versus-T-bill weight in [0, 0.99]: CP ≈ 0; FB +0.46/+0.67% at 4–5 years, gross;
- AIM 2017, a long-biased tilt with average position 86–107%: yield-based value timing adds nothing, and momentum (a
  price-trend signal, see §18) adds Sharpe 0.11, gross.

**The long-only evidence is therefore insufficient.**

---

## 7. Persistence in modern samples (literature-defined breakpoints only)

| Period | Evidence |
| --- | --- |
| after 2000 | GPT: best performance 1990–1993 and "from 2001 onwards", to 2011 `[verified]`. HT: coefficients unstable across 2003, OOS loss. Liu–Wu: tent loadings persist to 2019 on an unsmoothed curve (IS). |
| after 2008 | AJM: slope predictability *higher* at the ZLB, 2008–2015 (IS). GPT's OOS includes 2008–2011. |
| after 2011 / 2015 | Bauer–Hamilton: the trend-inflation (Cieslak–Povala) variant deteriorates sharply after 2011 (+221% MSE). No OOS test of FB or CP after 2011 was found. |
| after 2020 | **No audited paper tests 2020+** (QT, 2022 hiking cycle). |

**Answer to the fundamental question.** Yield-curve *correlation* with future returns persists in sample into the ZLB
era. *Real-time economic* meaning after 2011 is undocumented, and the one tested successor construction broke.
Decades of publication plus QE/ZIRP leave the modern real-time case unproven, not refuted.

---

## 8. Signal classes in scope

Only the three literature-motivated classes in the brief were audited:
- **A.** Cochrane–Piazzesi five-forward factor, recursive coefficients.
- **B.** A simple observable slope or forward spread (Fama–Bliss style; with H.15, a CMT slope such as 10y − 1y).
- **C.** A point-in-time, model-estimated term premium, only if the model can be reconstructed recursively.

No other yield-curve signal was considered.

---

## 9. H.15 / Treasury constant-maturity yields: PIT audit

### 9.1 What they are

- CMT yields are **par yields**, not zero-coupon yields. They are read off Treasury's fitted par curve. `[OFFICIAL,
  Treasury Yield Curve Methodology; D1]`
- Inputs are indicative bid-side quotes for on-the-run securities, collected by FRBNY at about 3:30 pm ET.
- The fitting method changed from quasi-cubic Hermite spline to monotone convex on **2021-12-06**. Treasury also notes
  that the historical input set changed ("interpolated yields and rolled down securities").
- The 30-year was discontinued **2002-02-18** and reintroduced **2006-02-09** (H.15 archival footnote). No 2-month or
  4-month CMT exists on FRED (HTTP 404).

### 9.2 Series starts (measured, ALFRED metadata; `raw/pit_checks/fred_observation_start_and_vintage_counts.json`)

| FRED ID | first observation | ALFRED vintages (first vintage) |
| --- | --- | --- |
| DGS1MO | 2001-07-31 | 5,113 (2005-06-28) |
| DGS3MO, DGS6MO | 1981-09-01 | 5,117–5,118 (2005-06-28) |
| DGS1, DGS3, DGS5, DGS10 | 1962-01-02 | 5,114–5,118 (2005-06-28) |
| DGS2 | 1976-06-01 | 5,118 |
| DGS7 | 1969-07-01 | 5,116 |
| DGS20 | 1962-01-02 (see backfill below) | 5,113 |
| DGS30 | 1977-02-15 | 5,066 |

DGS10 vintages number 223–250 a year from 2006. That is one per release: every new observation creates a vintage. The
count therefore says nothing about revisions, which is why §9.3 was needed.

### 9.3 Revisions (measured by blind equality; `h15_vintage_equality_check.json`, `h15_vintage_mismatch_diagnosis.json`)

Method: for three vintages (2005-06-28, 2010-01-04, 2018-01-02), every observation dated before the vintage and no
later than 2017-12-31 was compared with the 2026-09-25 vintage. Only counts and dates were output.

- **3m, 6m, 1y, 2y, 3y, 5y, 7y, 10y:** 0–3 numeric revisions per tenor in 55 years of history, at isolated dates. For
  example DGS10 1991-01-29 (2 bp), DGS3MO 1999-10-01 (10 bp), DGS2 1990-11-21 / 1994-11-23 / 1995-11-29 (≤ 2 bp).
  DGS5 has zero. The 2005 vintage stored DGS1, DGS2 and DGS20 at three decimals; today they are rounded to two
  (≤ 1 bp).
- **20y: backfill hazard.** Early history (from 1962) is absent from the 2005 and 2010 vintages and present today. It
  was not available in real time.
- **30y: backfill hazard.** 994 dates from 2002-02-19 to 2006-02-08 are missing in the 2010 vintage and carry values
  today. A 30y series across 2002–2006 is not real-time.

### 9.4 Publication timing

- H.15 is posted about 4:15 pm ET `[OFFICIAL-leaning, D1]`. The FRBNY quote time is about 3:30 pm ET.
- Treasury's own posting "by about 6 pm ET" is `[UNVERIFIED]`. The rule below assumes 18:00 ET, so it does not depend
  on it.
- **FRED/ALFRED archive lag at month-ends (measured, 24 month-ends, 2006–2017):** 1–6 calendar days. It was often 3–5
  in 2006–2011 and 1 day by 2014–2016. So a backtest must gate on ALFRED's first vintage containing D, not merely on
  the H.15 posting time (§13).

### 9.5 Classification

| Series | Class | Reason |
| --- | --- | --- |
| **H.15 CMT, 3m–10y** | **PIT_SAFE** | Measured revisions are immaterial; vintages are preserved from 2005 and can be checked for every date |
| **H.15 20y, 30y** | **MINOR_REVISION_RISK** | Measured backfills that were not available in real time; use only tenors ≤ 10y, or ALFRED vintages |

The D1 sub-agent's provisional PIT_RECONSTRUCTABLE is superseded by measurement (§23).

---

## 10. Gürkaynak–Sack–Wright: PIT audit

- **Published:** zero-coupon yields (SVENY), par yields (SVENPY), instantaneous forwards (SVENF), one-year forwards
  (SVEN1F) and parameters (BETA0–3, TAU1–2) for 1961 to date. The fit is Nelson–Siegel for 1961–1979 and Svensson from
  1980. Bills and on-the-run issues are excluded. Updates are weekly (Tuesday). `[OFFICIAL, D2]`
- **Vintage note (Fed, quoted by D2):** the current vintage is "generally pretty close" to the original data "but they
  are not identical, as small modifications have been made over time". The file moved on 2019-11-05; the legacy page
  `feds200628_1.html` is still live.
- **Magnitude of revisions:** no published quantification was found `[UNV]`.
- **Archive (measured by the main audit, Wayback CDX, metadata only):** the legacy `econresdata/…/feds200628.xls` has
  **69 captures with 27 distinct digests, 2009–2025**, typically 2–12 captures a year. The current `.csv` CDX query
  returned 504 twice. So only **sparse, irregular vintages** exist, not a weekly archive.
- **Fitting:** each day is fitted only on that day's prices. There is no look-ahead in time, but today's file reflects
  today's filters.
- **Signal damage:** CP 2008 Table 1 shows GSW-on-GSW R² 0.29 with W-shaped, multicollinear loadings, against 0.35
  using FB forwards. Liu–Wu report GSW loadings that "differ by an order of magnitude" between pre-2003 and to-2019
  samples.

**Classification: MINOR_REVISION_RISK** (not PIT_SAFE; partially reconstructable from sparse archived vintages). It is
unsuitable as the input for a CP factor on signal grounds, independently of PIT.

---

## 11. Adrian–Crump–Moench term premia (and Kim–Wright): PIT audit

- ACM is a five-factor regression-based affine model on GSW yields, 1–10y, from 1961. Its published history comes from
  estimation on the whole sample and is re-estimated as data arrive. Neither the NY Fed nor the Board (Kim–Wright)
  publishes historical vintages `[D2; SECONDARY for update practice]`. The Wayback CDX query for the NY Fed file
  returned 503/504, so it was not measured.
- **A value dated 2005 in today's file is not the estimate an investor could have had in 2005.**
- Recursive reconstruction is possible in principle: re-estimate ACM each month on data then available, on a GSW
  input that is itself MINOR_REVISION_RISK. But that is a new generated regressor from a five-factor model, not a
  simple preregistrable rule. Its published OOS economic value is negative (SSW 2016, ACM-estimator robustness).

**Classification: PIT_BLOCKED** for the standard series. It is unsuitable as the primary signal. The class is set aside
by the decision rule (data FAIL).

---

## 12. Cochrane–Piazzesi data feasibility

| Route | Status |
| --- | --- |
| Fama–Bliss discount bonds (CRSP via WRDS) | **Exact CP input; licensed.** Institutional contracts; no individual price found; no free redistribution. Not obtainable by this programme. |
| Liu–Wu (2021) zero curve | **Close, free** (author's site; monthly/daily, 1–360 months, 1961–2025). Built from CRSP quotes by a date-by-date kernel fit. Revision-on-update practice undocumented → MINOR_REVISION_RISK, unverified. Reproduces the tent pattern (Liu–Wu 2021). |
| GSW | **Different construction** (smoothed; §10). |
| H.15 par yields | **Not valid** for canonical forwards. Bootstrapping zeros from 11 par nodes needs an interpolation model between nodes, a design choice that the literature never tested. `log_forward_rates` refuses par input (tested). |

A **CMT slope** (e.g. DGS10 − DGS1) is therefore a **different hypothesis** from the FB forward spread. It is close in
spirit, but no audited study provides OOS evidence for it. Exact CP replication requires CRSP / Fama–Bliss.

---

## 13. Timing convention (frozen for any reopening)

- **Observation.** H.15 yields for U.S. business day D. The signal date for a month is the last date in that month
  carrying a non-ND observation. It is taken from the data's own dates: bond-market closures such as Columbus Day,
  Veterans Day and most Good Fridays differ from NYSE.
- **Live availability.** Assume publication no earlier than **18:00 ET on D**. That is 22:00–23:00 London, depending on
  the DST mismatch weeks, and after both the LSE close (16:30) and the Xetra close (17:30 CET). Day-D data can
  therefore **never** trade on day D.
- **Live execution.** At the close of the **first XLON session whose open is after 18:00 ET on D**. Weekends and UK
  holidays roll forward. Examples (tested):
  - Fri 2026-01-30 → Mon 2026-02-02;
  - Wed 2025-12-31 → Fri 2026-01-02;
  - Thu 2025-04-17 → Tue 2025-04-22;
  - Fri 2026-08-28 → Tue 2026-09-01.
- **Backtest execution.** The same rule, measured from **max(D, first ALFRED vintage containing D)**. This absorbs the
  measured 1–6-day FRED lag. Example (tested): D = 2009-12-31, first vintage 2010-01-05, execution 2010-01-06 instead of
  2010-01-04.
- The month-end signal feeds a **monthly** decision.

Code: `execution_session`, `execution_session_backtest`, `signal_date_for_month`. Output:
`treasury_audit/timing_convention.json`.

---

## 14. Candidate selection: gate table and decision

Gates follow the brief's selection criteria (1–6) plus the two eligibility gates (in-sample mechanism; distinctness
from prior research). Rule (`stage0_decision`):
1. If any class passes every gate, authorise exactly one: the first in preference order.
2. Otherwise set aside data-blocked classes.
3. Take the code of the first remaining class in preference order.
4. ABANDON is admissible only if every class fails its mechanism gate.

Preference order is by strongest credible real-time OOS evidence: **B, A, C**.

| Gate | B slope / forward spread | A CP factor | C PIT term premium |
| --- | --- | --- | --- |
| in-sample mechanism | PASS | PASS | PASS |
| real-time OOS evidence | **FAIL** (one gross positive study to 2011 vs TV / SSW; no after-cost, no post-2011 evidence) | **FAIL** | **FAIL** (SSW ACM negative) |
| PIT reconstructable | PASS (H.15 PIT_SAFE) | UNRESOLVED (Liu–Wu) | **FAIL** |
| simple / preregistrable | PASS | PASS | **FAIL** |
| long-only economic meaning | UNRESOLVED (+0.46 / +0.67% gross, 4–5y only) | **FAIL** (CER ≈ 0) | UNRESOLVED |
| low turnover | PASS | UNRESOLVED | UNRESOLVED |
| no proprietary data | PASS | UNRESOLVED (exact = Fama–Bliss) | PASS |
| distinct from prior research | PASS (§18) | PASS | PASS |
| **class code** | **REAL_TIME_OOS_EVIDENCE_TOO_WEAK** | REAL_TIME_OOS_EVIDENCE_TOO_WEAK | set aside (PIT FAIL) |

**Programme decision: `REAL_TIME_OOS_EVIDENCE_TOO_WEAK`.** Binding class: B. Set aside for data: C.

A test shows that even with B's OOS gate flipped to PASS, the unresolved long-only gate still blocks authorisation. The
decision does not rest on a single judgement.

Alternatives considered:
- **PIT_DATA_BLOCKED:** rejected. The binding class has PIT_SAFE, free data.
- **MECHANISM_TOO_WEAK:** rejected. In-sample evidence is strong and robustly inferred; the brief reserves D for this
  pattern.
- **IMPLEMENTATION_BLOCKED:** not primary. The instruments exist (§15) and costs are material but not prohibitive
  (§19).
- **DUPLICATES_PRIOR_RESEARCH:** rejected (§18).
- **ABANDON_TREASURY_PROGRAMME:** not admissible. Every class passes the mechanism gate (tested). It would also
  overstate the finding.

---

## 15. Retail Treasury UCITS audit (metadata only; `raw/sources/V1_treasury_ucits_metadata.*`)

| Bucket | Line (ISIN) | Currency / type | Inception (fund; class) | TER | Benchmark | Trading 212 |
| --- | --- | --- | --- | --- | --- | --- |
| Short 1–3y | iShares $ Treasury 1–3yr, USD Dist IE00B14X4S71 (IDBT USD / IBTS GBX) | unhedged | 2006-06-02 | 0.07% | ICE US Treasury 1–3 Year | IBTS: confirmed (secondary) |
| | same, USD Acc IE00B3VWN179 (IBTA) | unhedged | 2006-06-02 | 0.07% | same | confirmed (secondary) |
| | EUR Hedged Acc IE00BDFK1573 (IBTE / 2B7S) | EUR-hedged | class 2018-04-10 | 0.10% | same, EUR hedged | **conflicting / unverified** |
| Intermediate 7–10y | USD Dist IE00B1FZS798 (IBTM) | unhedged | 2009-06-03 (per V1) | 0.07% | ICE US Treasury 7–10 Year | **unverified** |
| | USD Acc IE00B3VWN518 (CU01 / CBU0 / SXRM) | unhedged | 2009-06-03 | 0.07% | same | unverified; **ticker collision (CBU0)** |
| | EUR Hedged Dist IE00BGPP6697 (IBB1) | EUR-hedged | class 2019-02-25 | 0.10% | same, EUR hedged | confirmed (secondary) |
| Long 20+y | USD Dist IE00BSKRJZ44 (IDTL USD / IBTL GBX) | unhedged | 2015-01-20 | 0.07% | ICE US Treasury 20+ Year | confirmed (secondary) |
| | EUR Hedged Dist IE00BD8PGZ49 (DTLE; **IUSV collides** with an unrelated fund) | EUR-hedged | class 2017-09-21 | 0.10% | same, EUR hedged | confirmed (secondary) |
| Cash-like 0–1y | USD Acc IE00BGSF1X88 (IB01); USD Dist IE00BGR7L912 (IBTU) | unhedged | 2019-02-20 | 0.07% | name conflict (ICE vs Bloomberg) | IBTU confirmed; IB01 partial |
| | Amundi 0–1Y EUR Hedged Acc LU2182388749 | EUR-hedged | – | – | – | not checked |

Caveats:
- Trading 212 pages returned HTTP 403 to scripts, so every "confirmed" is a search-index title only (SECONDARY).
  Fractional availability is **UNVERIFIED** per line.
- Effective duration, weighted-average maturity, rebalancing frequency and indicative spreads are **UNVERIFIED**
  (factsheets were not parseable).
- Durations of roughly 2 / 7 / 17 years are commonly reported for these indices but were **not** verified here.

### 15.1 Mapping: predicted zero-coupon excess return → ETF exposure

- The literature forecasts the one-month (or one-year) excess return of a **2–5-year zero-coupon bond** over a T-bill.
- The ETFs are **coupon-bond portfolios, rebalanced monthly within a maturity band**. That makes them close to
  constant-maturity exposures, with duration drift inside the band, coupon income, sampling and tracking difference,
  and TER.
- **Short ↔ intermediate (1–3y ↔ 7–10y): MODERATE.** The switch changes duration by roughly five years, which is
  comparable to the 5-year-zero-versus-bill exposure where GPT found its only long-only value. But the maturity points
  differ: 7–10y lies beyond the 2–5-year range of every audited OOS study.
- **Anything ↔ 20+y: POOR.** No audited OOS study covers the long end. H.15 20y and 30y also carry the backfill hazard.
  Long-end premia differ (supply, convexity).
- **Deployable history:** the 1–3y fund starts in 2006, the 7–10y fund in 2009 (per V1), the 20+y fund in 2015, and
  the EUR-hedged classes in 2017–2019. Any test on the actual instruments is essentially confined to the programme's
  locked windows.

---

## 16. FX treatment for a EUR (or TND) based investor

- **Trading currency is not economic exposure.** An IBTS (GBX) or IDTL (USD) line on the LSE is a **USD** bond
  exposure whatever the quote currency. A GBX quote only adds a GBP conversion step.
- **Unhedged lines:** the EUR return is (1 + r_USD)(1 + fx) − 1. USD/EUR volatility is comparable to or larger than the
  bond return itself, so *levels* are FX-dominated.
- **The duration decision is nearly FX-neutral against a Treasury benchmark when every leg is USD.** The active return
  is (r_s − r_b)(1 + fx): FX scales it and cannot create it (tested). FX must never be reported as timing alpha.
- **EUR-hedged lines:** return ≈ r_USD + (r_EUR − r_USD short rates) − hedge friction. The carry term is common to all
  hedged lines and cancels in hedged-versus-hedged active returns (tested). TER is 0.10% against 0.07%.
- **Trading 212 conversion:** 0.15% each way on conversions (documented, verified 2026-09-09, `PHASE6_COST_MODEL.md`).
  - Manual orders against a multi-currency USD balance avoid FX when switching between USD lines.
  - The API executes only in the primary currency, so an automated EUR account converts on every switch.
- **Frozen evaluation rule for any reopening:**
  - primary metric = active return **in USD**, all legs unhedged USD lines (or all legs EUR-hedged lines);
  - EUR-level returns are diagnostic only;
  - T212 FX costs are charged in the cost model whenever the execution path converts.

---

## 17. Benchmarks: what a future test would compare

- **Economic question:** does dynamic duration allocation improve on a **predetermined** Treasury allocation after
  costs?
- **Primary benchmark (fixed before any return, for a reopening): a static 50/50 blend of the two legs the rule
  switches between**, rebalanced on the same monthly schedule. It has the same average duration exposure as a rule
  that is long duration half the time, so the comparison isolates timing from average-duration choice.
- **Reported alongside, not selected among:** always short (1–3y), always intermediate (7–10y).
- **Total-return improvement vs risk reduction.** A rule that cuts duration after rates rise can lower drawdown while
  earning less. That is risk reduction, not a term-premium alpha. The frozen primary test is **mean active return
  versus the blend**; drawdown is secondary.
- **Known history.** Everyone knows 2022 was the worst Treasury year in decades. Any rule that happened to hold short
  duration then will look good for reasons the researcher knew in advance, so the 2022 contribution must be reported
  separately.

---

## 18. Overlap with Phase 6B and earlier ETF work

Prior tests that used Treasury exposure:
- **E053 G1a:** SPY versus IEF by 12-month absolute momentum.
- **E053 G1b:** SPY versus IEF by the 10-month SMA.
- **E053 G3:** volatility-managed SPY with an IEF remainder.
- **E053b:** GTAA sleeves including IEF and TLT, each on its 10-month SMA.
- **E020:** trend and momentum rules over 12 GBP ETFs including IBTL, H-T1 / H-T2.

All of them are **price-trend, volatility or equity-risk-off switches**, and most choose between equities and bonds.

Phase 11C's information source is the **cross-section of yields at a point in time** (expected-return / term-premium
proxies). It allocates *within* Treasuries. That is a distinct mechanism, so the gate is **PASS, not
DUPLICATES_PRIOR_RESEARCH**.

Two collapse risks are recorded for any reopening:
1. **Bond momentum.** AIM's only long-only gain came from momentum, which is a price trend already tested (E020, E053).
   A reopened slope cell must carry a **falsification cell against 12-month Treasury time-series momentum**. If the
   slope rule's active return is explained by it, the result is DUPLICATES_PRIOR_RESEARCH.
2. **The monetary cycle.** A slope rule can proxy for "after a hiking cycle". That is not duplication, but it is the
   same few episodes.

---

## 19. Costs and turnover (ex ante; `treasury_audit/cost_envelope.json`)

Half-spreads are **assumptions** (issuer spread statistics unverified). T212 FX is documented.

| Execution path | per switch | 1 / 2 / 4 switches a year |
| --- | --- | --- |
| USD lines held in USD, tight (3 bps half-spread) | 6 bps | 6 / 12 / 24 bps |
| USD lines held in USD, wide (10 bps) | 20 bps | 20 / 40 / 80 bps |
| EUR account converting each switch (5 bps + 2 × 15 bps FX) | 40 bps | 40 / 80 / 160 bps |
| EUR-hedged lines, EUR account (8 bps) | 16 bps | 16 / 32 / 64 bps |

Add TER (0.07%, or 0.10% hedged) and tracking difference, which are common to both legs.

The only published long-only gross edge is **46–67 bps** a year of CER (4–5-year maturities). At 2 switches a year it is
consumed entirely on the converting path, and a third to all of it on the other paths. Slope-type predictors are
persistent, so monthly decisions should switch rarely. But a sign rule near zero can flip repeatedly; a reopening would
need a preregistered no-trade band, which is itself a parameter.

**Preference: monthly or slower.** Frequent duration flipping is not viable.

---

## 20. Statistical power, overlap and effective sample (`treasury_audit/power_table.json`)

- **Overlap.** 20 years of monthly 12-month regressions give 240 rows but only **20 independent outcomes**
  (`non_overlapping_obs`). Hansen–Hodrick needs h − 1 = 11 lags. Bauer–Hamilton show conventional HAC tests have
  **19–36% true size** with persistent regressors.
- **Stambaugh bias.** Slope and forwards are near-unit-root at the monthly frequency. A negative correlation between
  predictor and return innovations biases the slope coefficient upward, by −(σ_uv / σ_v²)(1 + 3ρ)/T
  (`stambaugh_bias`).
- **Generated regressors and estimation noise.** Recursive coefficients (A, B) and model-estimated premia (C) add
  estimation noise that full-sample R² hides. Duffee's causal R² is half the smoothed one.
- **Power (analytic).** From the published monthly OOS R², with an **assumed** 50% capture for a long-only switch:

| monthly OOS R² | IR (unconstrained) | IR (long-only, assumed) | years to t = 1.96 | power over 14.7 y | power over 22 y |
| --- | --- | --- | --- | --- | --- |
| 0.5% | 0.25 | 0.12 | 255 | 0.12 | 0.14 |
| 1.0% | 0.35 | 0.17 | 127 | 0.16 | 0.20 |
| 2.0% | 0.49 | 0.25 | 63 | 0.24 | 0.31 |

**Available independent data:**
- 1990–2011 is the literature's own OOS window, so testing on it would replicate GPT, not test it.
- 1962–1989 is GPT's warm-up period, and the in-sample CP / FB literature already covers it.
- Treasury ETF returns for 2004–2017 (IEF, E053) and 2009–2019 (IBTL, E020) were already read by this programme.
- What remains is roughly 2012–2026, 14.7 years, overlapping the locked 2018–2021 / 2022–2026 windows and the
  common-knowledge 2022 episode.

**A modern ETF-era test would not have enough independent observations.** It would likely end ambiguous whatever the
truth.

---

## 21. Final Stage 0 decision (closure record, 2026-09-27)

### 21.1 Record

```
Phase 11C:                              TREASURY_TERM_PREMIA_STAGE0
Decision:                               REAL_TIME_OOS_EVIDENCE_TOO_WEAK
Stage 1:                                NOT_AUTHORIZED
Binding class:                          B simple slope / forward spread (strongest evidence; still insufficient)
CP factor (A):                          REAL_TIME_OOS_EVIDENCE_TOO_WEAK (exact inputs licensed; GSW degrades it)
PIT term premium (C):                   set aside - ACM PIT_BLOCKED
H.15 3m-10y:                            PIT_SAFE (measured)   | H.15 20y/30y: MINOR_REVISION_RISK (backfills)
GSW:                                    MINOR_REVISION_RISK (sparse archived vintages; smoothing damages CP)
ACM:                                    PIT_BLOCKED
Primary construction surviving:         NONE (zero candidates)
Strategy cells added:                   0
Cumulative strategy-cell ledger:        490
Strategy returns inspected:             NO
Old crypto holdout touched:             NO
Equity validation touched:              NO
Equity final holdout touched:           NO
```

### 21.2 Reserved construction (NOT authorised; recorded only to prevent forking at any reopening)

If external evidence reopens the question (§21.3), the only construction to be preregistered is the following. It
consumes **zero** cells now.

- **Signal:** S_t = DGS10 − DGS1 (H.15 CMT, both PIT_SAFE, 1962+), at the month's last non-ND date.
- **Forecast:** the one-month excess return of the intermediate leg over the short leg, forecast by expanding-window
  OLS on S_t. Coefficients use only pairs whose target is realised by t (`expanding_coefficients`), with a minimum of
  120 monthly pairs.
- **Allocation:** hold intermediate (7–10y) if the forecast is > 0, else short (1–3y). 100% in one leg; no 20+y line
  (§15.1).
- **Timing and cost:** backtest timing per §13; cost model per §19; primary benchmark 50/50 static blend (§17); metric
  = USD active return, HAC and block-bootstrap inference.
- **Eventual burden:** 1 primary cell + 2 falsification cells:
  - (i) 12-month Treasury TSMOM in the same two-leg frame (duplication check, §18);
  - (ii) one extra month of signal delay.
- **Development/validation/holdout concept:**
  - replication check on 1990–2011 (not evidence);
  - validation 2012-01..2017-12 (partially contaminated by E053/E020 reads, disclosed);
  - holdout aligned with the programme locks: 2018-01..2021-12 and 2022-01..2026-08, opened once, 2022 reported
    separately.

### 21.3 Reopening conditions (external only; our own diagnostics cannot qualify)

- An independent study, **covering 2012 or later**, showing **recursive, real-time, long-only (no shorting, no
  leverage)** duration timing from a yield-curve-only predictor with positive value **after explicit transaction
  costs**; or
- A study showing that a **CMT-based slope** (not Fama–Bliss forwards) delivers GPT-like recursive OOS value, so that
  the free PIT-safe construction inherits evidence; or
- Access to Fama–Bliss/CRSP at no cost **and** a published after-cost long-only result for the FB spread.

### 21.4 Excluded as post-hoc rescue (not hypotheses)

The following are not to be proposed:
- TVP / stochastic-volatility Bayesian variants;
- macro-augmented predictors (Ludvigson–Ng, CFNAI, real-time macro panels);
- ML or forecast combinations;
- recession or ZLB conditioning;
- the Cieslak–Povala cycle factor and i*-detrended yields (Bauer–Rudebusch) as rescues of this phase. A genuinely new
  proposal would need its own Stage 0;
- alternative slope pairs (10y−3m, 5y−2y, 30y−5y …) or thresholds;
- 20+y legs;
- bond momentum or SMA overlays (already tested: E020, E053);
- any yield-curve diagnostic computed against Treasury or ETF returns.

---

## 22. Deliverables, reproducibility, tests

- `research/phase11c/PHASE11C_STAGE0_AUDIT.md` (this file).
- `research/phase11c_treasury_audit.py`. It has no network or data access (a test greps the source). Contents:
  - `SOURCES` registry, `cp_construction_status`, `log_forward_rates` (refuses par yields);
  - timing: `signal_date_for_month`, `execution_session`, `execution_session_backtest`;
  - recursive guard: `usable_training_pairs`, `expanding_coefficients`;
  - overlap and power: `non_overlapping_obs`, `stambaugh_bias`, `timing_information_ratio`, `power_one_sided`;
  - FX: `eur_active_return_unhedged`, `eur_return_hedged_approx`;
  - costs: `switch_cost_bps`, `cost_envelope`;
  - `CLASS_GATES`, `stage0_decision`, `recorded_decision`.
- `reports/phase11c/treasury_audit/`: `gate_table.json`, `decision_check.json`, `sources_pit.json`,
  `power_table.json`, `cost_envelope.json`, `timing_convention.json`, `MANIFEST.json`.

  Reproduce from `research/`: `python phase11c_treasury_audit.py all`.
- `reports/phase11c/raw/`:
  - `sources/` (five sub-audits + V1 CSV; snapshot indexes tracked, captures ignored);
  - `pit_checks/` (tracked JSON measurements; quarantine ignored);
  - `literature/SOURCES.txt` (tracked);
  - `RAW_MANIFEST_SHA256.txt` (tracked).
- Tests: `tests/test_phase11c_treasury_audit.py`, 57 tests.
- No EXPERIMENTS.md entry (audit only, zero cells; Phase 9A/10A/11A/11B convention).

---

## 23. Corrections to the sub-audit reports

1. **D1 H.15 classification** PIT_RECONSTRUCTABLE → **PIT_SAFE** (3m–10y) / **MINOR_REVISION_RISK** (20y, 30y). D1
   did not load the ALFRED vintage list; the main audit measured revisions, backfills, series starts and release lags
   (§9).
2. **D1 series starts** (SECONDARY / UNVERIFIED in D1) are replaced by measured ALFRED metadata (§9.2). D1's "DGS3MO
   1954" was wrong: FRED starts 1981-09-01. D1's flags for DGS3 and DGS7 gaps are not borne out as missing FRED history
   (7y starts 1969-07-01).
3. **D1 on the 30y gap.** D1 said the gap must be treated as missing. The current FRED vintage **fills** it, which is
   the backfill hazard in §9.3.
4. **D2 Wayback** "blocked by outage" is partly resolved: the legacy `.xls` has 69 captures / 27 digests (2009–2025).
   The current `.csv` and the NY Fed ACM file could still not be queried (504/503).
5. **L1 Thornton–Valente.** Full text was still not obtainable (SSRN 403; Essex unreachable; the St. Louis Fed WP
   number tried was a different paper). The decisive direction is taken from GPT 2019's full-text description and
   SSW's footnote; the weight bounds come from Borup et al. `[verified]`. Magnitudes remain UNVERIFIED.
6. **L2 "Wan–Fulop–Li"** local file is Fan–Feng–Fulop–Li (2022). An earlier Fulop–Li–Wan draft (2017, revised data)
   *found* predictability. The published negative result concerns **real-time macro** predictors and does not bear on
   yield-only signals, whose vintages are measured as unrevised (§9).
7. **L1's Thornton file** `thornton_valente_2012_belk_seminar.pdf` is Thornton (2015), "Understanding the
   Predictability of Excess Returns", not TV (2012).
