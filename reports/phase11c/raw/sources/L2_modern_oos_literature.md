# Phase 11C — L2: Modern Out-of-Sample / Real-Time / State-Dependent / Long-Only Literature Audit
## U.S. Treasury Term-Structure Risk Premia and Duration-Timing Predictability

Auditor: Stage-0 literature sub-agent. Date: 2026-09-27.
Scope restriction observed: no price/return/yield time series were downloaded, loaded, or computed;
no regression/backtest/Sharpe/CAGR was run. All numbers below are as PUBLISHED inside the cited papers.
Full-text PDFs (where legally obtainable, working-paper/preprint versions) were downloaded to
`reports/phase11c/raw/literature/` (git-ignored) and text-searched; per-line citations below give the
approximate location found in the extracted text. Two WebFetch attempts on paywalled abstract pages
(ScienceDirect, Oxford Academic) returned HTTP 403 and produced no snapshot content — see
`L2_snapshots/INDEX.md`. Where only a WebSearch synthesis was available, this is explicitly tagged
`[ABSTRACT]` or `[UNVERIFIED]` and should not be treated as reliable — per project rules, search-engine
summaries are known to sometimes invent numbers.

---

## (a) Structured blocks per paper

### 1. Rebonato & Nyholm (2025), "Why does the Cochrane–Piazzesi model predict Treasury returns?"
Journal of Empirical Finance, Vol. 84 (Sept 2025), DOI via ScienceDirect S0927539825000726; SSRN
working paper id 4846843 (PDF download blocked, HTTP 403 from SSRN delivery servers; ScienceDirect
abstract page also 403'd via WebFetch).
- Claim [ABSTRACT, WebSearch synthesis of SSRN/RePEc listing]: uses a resampling test to argue CP
  predictability is **not** an artefact of in-sample overfitting. Finds neither the specific "tent" shape
  of factor loadings nor the 4-to-5-year forward spread is essential; instead attributes CP's predictive
  power to identifying a cointegrating combination of the quasi-unit-root forward-rate regressors needed
  to make excess returns stationary.
- Real-time / OOS / economic value: **not established from what was retrievable.** The abstract synthesis
  describes a statistical/econometric argument (resampling-based significance test), not an OOS forecasting
  exercise, real-time implementation, or a portfolio/CER calculation. Full text was not obtained (SSRN and
  ScienceDirect both blocked); classification below treats this as **UNVERIFIED for OOS/real-time/economic
  value content** — it should be read as a defense of CP's in-sample statistical validity, not as OOS proof.
- Category: **A (strong in-sample / econometric-validity defense)**, pending full text.

### 2. Gargano, Pettenuzzo & Timmermann (2019, Management Science 65(2):508-540)
"Bond Return Predictability: Economic Value and Links to the Macroeconomy." Full working paper PDF
obtained (Brandeis WP 75R, July 28 2016 version) — **FULL TEXT** read directly.
- Predictors: Fama-Bliss (1987) forward spread (FB), Cochrane-Piazzesi (2005) factor (CP), Ludvigson-Ng
  (2009) macro factor (LN); combined via Bayesian model-averaging with time-varying parameters (TVP) and
  stochastic volatility (SV).
- Estimation: **recursive** Gibbs-sampling recursion "for all time periods between 1990:01 and 2011:12"
  [FULL-TEXT, p.~18 / line 806 of extracted text]. Out-of-sample period 1990:01–2011:12 [FULL-TEXT, Fig.
  captions e.g. line 3200].
- Horizon: primarily **monthly**; robustness also run at quarterly and annual non-overlapping horizons —
  "the quarterly and annual R2_OoS values decline somewhat... substantially smaller at the annual horizon"
  [FULL-TEXT, ~line 1188-1198].
- Real-time / revised data: macro factor is the Ludvigson-Ng (2009) factor built from a large panel of
  **fully-revised (final vintage)** macro series — no ALFRED/real-time vintage construction is mentioned
  anywhere in the text (`vintage`/`ALFRED`/`real-time data`/`revised data` search returned zero hits). This
  is a a material real-time-implementability gap the paper itself does not address.
- Weight constraints — **two explicit scenarios** [FULL-TEXT, lines 1093-1097]:
  - Scenario 1 (**long-only, no leverage**): ω ∈ [0, 0.99].
  - Scenario 2 (**short + leverage allowed**): ω ∈ [-2, 3], monthly return distribution bounded [-100%,100%].
- Economic value / CER (relative to Expectations-Hypothesis benchmark, A=10) [FULL-TEXT, lines 1112-1127]:
  - Long-only Scenario 1: TVP-SV three-factor model CER ranges **~0.24% (n=2) to 1.2%-1.6% p.a. (longest
    maturity)**.
  - Levered/short Scenario 2: same model CER **0.24%→2.95% (2-yr bond)**, **1.55%→1.96% (5-yr bond)**;
    "CER gains above 200 basis points per year for the models that include the LN predictor" — i.e., the
    largest reported gains require the non-long-only, levered/short weight scenario.
- Transaction costs [FULL-TEXT, lines 1171-1174]: "assuming a one-way transaction cost of 10 basis points,
  the CER value... is reduced from 2.95% to 1.80% (two-year bond) and from 1.96% to 1.48% (five-year
  bond)" — costed only for the Scenario-2 (short/levered) case; Scenario-1 CER after costs is not separately
  reported.
- Recession concentration [FULL-TEXT, lines 1233-1272]: R² generally higher in recessions than expansions,
  but the recession/expansion split analysis explicitly "use[s] full-sample information" [line 1235] (i.e.
  the NBER recession dummy is used ex post, **not real-time-known**) "because there are only three
  recessions in our out-of-sample period, 1990-2011" [line 1236]. The paper is explicit that this
  particular breakdown is not a real-time-implementable state split.
- SE / bias treatment: Diebold-Mariano test for CER significance [line ~1112]; standard OOS R² (Campbell-
  Thompson style) elsewhere in the paper.
- Category: **B (true OOS, recursive)** for the headline forecasting exercise; the long-only CER numbers
  are modest (≤1.6%/yr before costs) and the large (>2%/yr) numbers require Scenario-2 leverage/shorting.
  Real-time-vintage macro data is **not used**, which is a caveat against calling this real-time-implementable.

### 3. Andreasen, Engsted, Møller & Sander (2021, RFS 34(6):2773-2812)
"The Yield Spread and Bond Return Predictability in Expansions and Recessions." Full text not obtained
(RFS/Oxford Academic paywalled; WebFetch of abstract page returned only navigation chrome, no abstract text
— see `L2_snapshots/INDEX.md`).
- Claim [ABSTRACT, WebSearch synthesis of Oxford Academic listing]: expected excess bond returns are
  **positively** correlated with the yield-curve slope in expansions but **negatively** correlated in
  recessions; the paper builds a macro-finance term-structure model attributing this to the Fed's
  inflation-stabilization behavior.
- Real-time state issue: **not verified** — could not confirm from retrievable text whether the
  expansion/recession split uses NBER dates (not real-time-known, published with a multi-month/-quarter lag)
  or a real-time-available proxy. Given that Gargano-Pettenuzzo-Timmermann (2019, above) and Borup et al.
  (below) both explicitly flag the NBER-dating real-time problem in this same literature, this is treated as
  an **open, UNVERIFIED weakness** rather than assumed resolved.
- Category: **A (in-sample state-dependence claim)** pending full text; not confirmed as OOS or real-time.

### 4. Borup, Eriksen, Kjær & Thyrsgaard (Management Science 70(2):931-951, 2024)
"Predicting Bond Return Predictability." Full manuscript PDF (Northwestern-hosted preprint, ~2020 draft)
obtained — **FULL TEXT** read directly.
- Mechanism: state-dependent predictability is itself forecastable; propose a real-time-implementable
  dynamic ranking/model-confidence-set-style combination scheme, "a new multivariate test for equal
  conditional predictive ability [that] can be used in real-time" [FULL-TEXT, line 6].
- State variables used: NBER recession dummy **and** real-time-available proxies — "recession
  probabilities of Chauvet and Piger (2008), the Chicago Fed National Activity Index (CFNAI)" [FULL-TEXT,
  line 1153] — i.e., unlike a pure NBER-dummy exercise, they explicitly bring in indicators that are
  available contemporaneously, partially addressing the real-time-dating critique (though the NBER dummy
  itself, used for exposition/robustness, is not real-time-known).
- Recursive/real-time construction: "All variables are constructed recursively in the out-of-sample
  exercise" [FULL-TEXT, line 307].
- Real-time-data critique cited: "bond returns originates largely from data revisions not available to
  forecasters in real-time (see also Fulop, Li, ...)" [FULL-TEXT, line 328] — the paper is aware of, and
  partly motivated by, the same real-time-macro-data problem documented by Wan-Fulop-Li (2021) below.
- Out-of-sample R²: "dynamically combined forecasts deliver positive and sizeable out-of-sample R²"
  [FULL-TEXT, line 113]; countercyclical, peaking in recessions [line 123, 1119].
- Economic value / weight constraints [FULL-TEXT, lines 1240-1270]: mean-variance investor,
  weights **winzorized to ω ∈ [-1, 2]** ("reasonable shorting and leverage constraints, similarly to
  Thornton and Valente (2012) and Gargano et al. (2019)") — again **not long-only**. Individual predictor
  CER gains vs. EH benchmark are weak/insignificant on average ("we find little evidence that predictable
  deviations from the EH can be exploited to generate economic value on average when considering individual
  methods (Panel A)" [line 1266]); only the paper's own dynamic-combination method and the equal-weight (EW)
  combination show reliable positive CER.
- Transaction costs: asserted rather than modeled — "Trading costs are generally small in U.S. Treasury
  bond markets (Adrian, Fleming, and Vogt, 2017)" [FULL-TEXT, footnote 34] — no explicit cost deduction from
  the CER numbers as GPT(2019) do.
- Category: **B/C hybrid** — genuinely recursive OOS with an explicitly real-time-motivated combination
  method and OOS-R² evidence, but the headline economic-value results depend on a levered/short [-1,2]
  weight set and on the authors' own novel combination scheme, not a naive single-predictor long-only rule.

### 5. Bianchi, Büchner & Tamoni (2021, RFS 34(2):1046-1089) + Corrigendum (RFS 34(2):1090-1103)
"Bond Risk Premiums with Machine Learning." Full text not obtained (RFS paywalled; only WebSearch
synthesis available).
- Original claim [ABSTRACT, WebSearch synthesis]: extreme trees and neural networks (NN) provide strong
  statistical evidence of bond-return predictability; NN forecasts using macro+yield information generate
  larger economic gains than yield-only forecasts.
- Corrigendum [ABSTRACT, WebSearch synthesis — **UNVERIFIED**, not read in full text]: the authors
  "revisited empirical results after correcting for using information not available at the time the
  forecast was made" (a look-ahead-bias fix); out-of-sample R² **decreased** after the correction, though
  NN-based predictability "remained statistically and economically significant" per the search-engine
  summary. No exact before/after R² numbers were confirmed from primary text — **flag as UNVERIFIED
  magnitude**, though the qualitative existence of a corrigendum for a look-ahead defect is corroborated by
  three independent listings (Rutgers, EconPapers, RePEc/IDEAS) agreeing on volume/page numbers (34(2):
  1090-1103).
- Real-time relevance: this corrigendum is itself direct evidence that even a leading recent ML bond-
  premium paper initially used **fully-revised, non-real-time macro data / look-ahead information**, and
  had to be corrected — reinforcing the Ghysels-Horan-Moench / Wan-Fulop-Li real-time critique below.
- Category: **A→B with an admitted correction** — genuine machine-learning OOS R² claimed, but the
  original version had a look-ahead defect; post-correction magnitude not independently confirmed here.

### 6. Cieslak & Povala (2015, RFS 28(10):2859-2901), "Expected Returns in Treasury Bonds"
Full text (JSTOR/author-hosted PDF) obtained — **FULL TEXT** read directly.
- Mechanism: decomposes yields into trend inflation (a real-time-constructible discounted moving average
  of core CPI, "a simple real-time measure of trend inflation" [FULL-TEXT, line ~88]) and a "cycle" factor
  (τ(cp)) that subsumes/improves on the Cochrane-Piazzesi combination of forward rates.
  Reported explicitly as real-time-computable: "We rely on a simple real-time measure of trend
  inflation... can be treated as real-time data" [FULL-TEXT, lines 88, 289].
- In-sample R²: **0.24 (3-year), 0.18/0.54/0.53** across specifications in Table 2 (univariate/bivariate
  regressions of excess returns on the cycle factor) [FULL-TEXT, lines 577-609]; up to **R²≈0.71-0.998**
  in later robustness/measurement-error tables (Table 4/Figure 5 area) [lines 2038-2049] — these are
  **full-sample, in-sample** regression R²s.
  Small-sample null distribution under the Expectations Hypothesis is simulated: 95th percentile R² under
  the null is only **0.23**, so the actual 0.54-type R²s are well above what pure overfitting under EH would
  produce [FULL-TEXT, lines 552-763].
- Out-of-sample evidence for **bond excess returns specifically**: the paper asserts qualitatively "our
  approach allows us to predict bond excess returns not only in sample but also out of sample" [FULL-TEXT,
  line 78] but **no OOS-R² table for bond excess returns appears in the main text** (grep for
  "out-of-sample"+"excess"/"bond"/"return" found only this one qualitative sentence plus two bibliography
  references to other papers). The paper's own explicit, tabulated **out-of-sample exercise is for
  inflation forecasting**, not bond excess returns (RMSE-ratio Table 6, OOS starting 1979:Q4/1984:Q4/
  1995:Q1 vs. an ARMA(1,1) benchmark) [FULL-TEXT, lines 1368-1759]. Any OOS bond-return-predictability claim
  therefore rests on material presumably in the (unretrieved) Online Appendix — **UNVERIFIED**.
- Economic value / CER / transaction costs / weight constraints: **not present in the main text at all** —
  no asset-allocation or portfolio exercise was found.
- Category: **A (strong in-sample)**, with a **real-time-constructible predictor** (a genuine strength) but
  **no confirmed OOS-R² or economic-value table for bond excess returns** in the retrievable text.

### 7. Bauer & Rudebusch (2020, AER 110(5):1316-1354), "Interest Rates Under Falling Stars"
Full text (FRBSF working-paper version) obtained — **FULL TEXT** read directly.
- Mechanism: shifting endpoints (trend inflation π*, equilibrium real rate r*, combined i* = π*+r*) in an
  arbitrage-free DTSM; shows the yield-curve level (not just slope) becomes a significant excess-bond-return
  predictor once yields are viewed relative to i*, and that **detrending materially increases predictive
  R²**.
- Real-time treatment: uses a "**pseudo real-time**" estimate of r* — explicitly constructed to avoid
  "look-ahead bias in our analysis of predictive power" using only information investors would have had:
  "we consider (pseudo) real-time estimates" [FULL-TEXT, lines 409-412], built from six contemporaneous
  r*-estimation methods (their average) [lines 414-460] and from the Blue Chip / Survey of Professional
  Forecasters' long-range short-rate forecasts for π* ("the PTR estimate was available in real time from
  the Survey..." [line 362]).
- Excess-bond-return R² gain (in-sample, full sample): adding i* to the first three yield PCs gives
  **ΔR² of 12 percentage points** [FULL-TEXT, Table 4 discussion, lines 1039-1048], compared with a
  Monte-Carlo-simulated upper bound of only 4pp under the null that i* has no true predictive power (FE
  model) — rejecting pure overfitting; a model with a genuine trend (OSE) reproduces a mean ΔR² of 9pp,
  "comfortably" containing the actual 12pp.
- **Post-1985 persistence** [FULL-TEXT, lines 667-693]: "In the post-1985 sample, the R² does not increase
  when detrending with only π*, but it increases by **9 and 6 percentage points**, respectively, when
  detrending with either both π* and r*, or with only i*" — i.e., the excess-return-predictability gain from
  the real-time-constructible i* **persists (at reduced magnitude) after 1985**, though the paper does not
  test 2000/2008/2015/2020 breakpoints specifically.
- Out-of-sample forecasts: **yes, but for the level of long-term interest rates, not directly for a bond
  excess-return trading rule.** Recursive/expanding-window estimation starting 1976:Q1, forecasting the
  10-year yield 4-40 quarters ahead, benchmarked against a random walk and against the no-trend (FE) model,
  using Diebold-Mariano tests [FULL-TEXT, lines 1226-1250]. Result: the trend-based (OSE) model "lowers the
  RMSE by about 40 percent relative to the FE model" at the 10-year-ahead horizon, and also beats the random
  walk (smaller but still significant) [lines ~1270-1280], and beats Blue Chip professional-forecaster
  survey RMSEs too.
- Economic value / CER / transaction costs / weight constraints: **not present** — this is a
  forecast-accuracy (RMSE/R²) paper, not a portfolio/economic-value paper.
- Category: **B (true OOS, recursive, real-time-constructible state variable)** for **yield-level
  forecasting**; the bond-excess-return predictability evidence itself is **in-sample (A)** — the paper does
  not report OOS-R² or CER specifically for an excess-return/duration-timing trading rule.

### 8. Wan, Fulop & Li (2021, J. Econometrics 230(1):114-130), "Real-Time Bayesian Learning and Bond Return Predictability"
SSRN PDF blocked (HTTP 403). **Full primary text was not obtained.** However, a closely related 2022
follow-up paper by an overlapping author (Fulop) — Fan, Feng, Fulop & Li (2022), "Real-Time Macro
Information and Bond Return Predictability: A Weighted Group Deep Learning Approach" (QMUL-hosted PDF) —
was obtained in **FULL TEXT** and cites/describes Wan-Fulop-Li (2021) directly and repeatedly in its own
literature review and conclusion. This is used as a **secondary FULL-TEXT citation** (not a primary read of
WFL2021 itself) — tagged accordingly below.
- **Decisive citing quote** [FULL-TEXT of Fan/Feng/Fulop/Li 2022, describing WFL2021]: "Wan, Fulop, and Li
  (2021) use different types of real-time macro data to implement empirical analysis based on linear
  predictive models with and without stochastic volatility. They find **no statistical or economic evidence
  for forecasting non-overlapping one-month holding period excess bond returns whenever real-time, instead
  of fully-revised, macro factors are used as predictors**." (repeated near-verbatim in both the introduction
  and the conclusion of the citing paper.)
- Real-time vs. revised: this is precisely the mechanism-killing result the audit needed — when a
  standard linear predictive-regression architecture is fed **real-time-vintage** macro data (instead of the
  final-revised data used by Ludvigson-Ng/Gargano-Pettenuzzo-Timmermann/Cieslak-Povala-style studies), both
  statistical (R²) and economic (CER) evidence for one-month-holding-period bond-return predictability
  **vanishes**.
- The citing paper's own (2022, deep-learning) results, by contrast, DO recover some statistical evidence
  using real-time macro vintage data + news-based topic attention with a nonlinear (WGNN) model: e.g. OOS
  R² "about 2.8% for two-year excess bond returns" [FULL-TEXT, non-overlapping], and OOS R² "ranging from
  1.69% for 5-year... to 8.21% for 2-year overlapping excess bond returns" — **but** explicitly states that
  translating this into economic gains for long-term bonds requires that "**investors are allowed to
  leverage their investments**" [FULL-TEXT, abstract and conclusion] — i.e., even the paper that revives
  real-time predictability via ML says the economic value is **leverage-dependent, not a long-only result**.
- Category: WFL2021 itself = **C-negative** (a real, if negative, real-time-implementable finding: real-time
  macro data kills the mechanism for standard linear models). The 2022 ML follow-up = **B** (true OOS,
  real-time data) but requires leverage for economic value, so not long-only-implementable as reported.

### 9. Long-only / practitioner duration-timing evidence
**Ilmanen (1995, JF 50(2):481-506)**, "Time-Varying Expected Returns in International Bond Markets."
[ABSTRACT, WebSearch synthesis only — full text not obtained]. Finds a small set of global instruments
forecasts 4%-12% of monthly excess-bond-return variation across six countries, statistically and
economically significant, expected returns correlated across countries. No detail on long-only vs.
long-short obtained; **UNVERIFIED** on cost treatment.

**Ilmanen (1997, J. Fixed Income)**, "Forecasting U.S. Bond Returns" — not independently retrieved this
session; treated as **UNVERIFIED / not audited** (time-boxed out).

**Asness, Ilmanen & Maloney (2017, JOIM 15(3):23-40)**, "Market Timing: Sin a Little." AQR-hosted PDF
obtained — **FULL TEXT** read directly, including the bond-market-timing appendix (Table A.2).
- U.S. 10-year Treasury value+momentum timing, **1900-2015 and 1958-2015** samples [FULL-TEXT, Table A.2]:

  | Metric (1958-2015) | Buy-and-hold | Value timing | Momentum timing | Value+Momentum |
  |---|---|---|---|---|
  | Excess return | 2.1% | 2.6% | 3.1% | 2.8% |
  | Volatility | 7.9% | 9.4% | 8.2% | 8.5% |
  | **Sharpe ratio** | **0.27** | **0.27** | **0.38** | **0.33** |
  | Max drawdown | -21% | -29% | -13% | -18% |
  | **Avg position size** | 100% | 107% | 104% | 106% |

  [FULL-TEXT, exact table extracted from PDF]. Value-only timing produces **zero** Sharpe improvement over
  buy-and-hold (0.27→0.27); momentum timing gives the largest improvement (0.27→0.38); combined V+M is
  0.33. Average position sizes stay in the 86%-107% band across both sub-periods and all four strategies —
  i.e., this is a genuine **long-only, near-100%-notional duration TILT**, not a levered or heavily
  short-duration strategy.
- Costs: table footnote states explicitly "**Hypothetical performance excess of cash, gross of transaction
  costs and fees**" [FULL-TEXT] — **no cost deduction applied**. A footnote elsewhere in the paper (footnote
  21) states costs were deliberately omitted "to focus on the fundamental challenges" of timing, not because
  they are believed immaterial.
- Real-time note: value signal uses a "real bond yield... nominal yield minus a **survey-based forecast** of
  long-term inflation" [FULL-TEXT] — survey data has a real-time-availability lag but is not simulated with
  hindsight-only (final/revised) inflation.
- Category: **C-partial** — a genuine long-only duration-tilt backtest with no leverage/shorting, but
  reported **gross of costs**, and the standalone value signal (the yield-curve-adjacent one, closest to the
  academic literature above) shows **no** risk-adjusted improvement; only adding momentum helps.

**Koijen, Moskowitz, Pedersen & Vrugt (2018, JFE 127(2):197-225)**, "Carry." NBER working-paper version
obtained — **FULL TEXT** read directly (bond-specific sections).
- Time-series carry strategy is explicitly compared against, and is **distinct from**, "the long-only
  passive portfolio in each asset class" [FULL-TEXT, line ~1847] — i.e. the Carry strategy itself is a
  **long-short, time-series-scaled** strategy (goes short when carry is negative), not long-only.
  During "carry drawdowns" (bad states, concentrated in NBER-recession-like global-recession periods) carry
  strategies are "consistently negative" while roughly half of the corresponding long-only passive exposures
  are still positive — carry's edge over passive is a **crash-risk-bearing, not a simple duration-tilt,**
  story.
- Costs/leverage: "the carry strategy faces larger transaction costs, greater funding issues, and limits to
  arbitrage than a passive strategy" [FULL-TEXT, line ~1404] — an explicit qualitative acknowledgement of
  higher costs, without a quantified after-cost Sharpe in the sections read.
- Category: **A/B mixed, but explicitly NOT long-only** — gains are largest for a strategy design that goes
  short duration/carry when carry is negative.

**Brooks & Moskowitz (2017, AQR/Yale working paper)**, "Yield Curve Premia." Full text (Yale-hosted PDF)
obtained — **FULL TEXT** read directly.
- Value/momentum/carry applied to level/slope/butterfly portfolios are constructed as **cross-country,
  dollar-neutral long-short** strategies ("creates a set of positive weights and a set of negative weights
  that sum to zero... scale each side... to a dollar long and a dollar short" [FULL-TEXT]) — **not
  long-only**.
- Genuine **out-of-sample "live" test**: "We use the live bond sample to construct trading strategies that
  could be deployed in real time... immune to [in-sample PC-persistence] concerns since the trading strategy
  depends solely on ex ante information" [FULL-TEXT] — this is a real out-of-sample, real-time-constructible
  test (Category B/C), reporting e.g. level-value Sharpe **0.65**, level multi-style Sharpe **1.01**,
  slope-carry Sharpe **0.69**, alpha of value strategy to a **long-only bond benchmark (GBI) of 3.0%/yr**
  (t=2.3) with only 0.13 correlation to that benchmark.
- Costs: explicit footnote — "**All returns are reported gross of transaction costs.** As the long-short
  butterfly portfolios require considerably more leverage per unit of volatility than either country or
  slope strategies, the portfolio is likely to incur **higher** transaction costs" [FULL-TEXT, footnote 17]
  — i.e. the paper itself flags that its highest-Sharpe results are also its highest-cost/highest-leverage
  ones, uncosted.
- Category: **B/C hybrid, but long-short/leveraged, and explicitly gross-of-cost.**

### 10. Post-2020 ZLB/QE-era persistence
**Andreasen, Jørgensen & Meldrum (2019), "Bond Risk Premiums at the Zero Lower Bound"** (Fed FEDS 2019-040).
Full text obtained — **FULL TEXT** read directly. (Note: sample covers 2008-2015/2018, not literally
2020-2026; it is the closest rigorously-sourced ZLB-era predictability-shift paper located in the time
available, and is exactly the mechanism a 2020-2026-persistence paper would need to update.)
- Finding: yield-spread coefficients in excess-bond-return regressions are **larger and increase faster with
  maturity** during the Oct-2008–Nov-2015 near-zero-rate regime than in the Jan-1990–Sep-2008 regime;
  for the 10-year bond, **R² doubles from about 10% to about 20%** [FULL-TEXT, lines ~330-337] between the
  two regimes.
- Real-time character of the state: the conditioning "state" is simply the observed short rate (federal
  funds rate) being above or below 1% — this **is** a real-time-observable state variable (unlike NBER
  dating), a genuine strength.
- Robust to: biannual (h=6) horizon, using PC2 instead of the raw slope, using the forward spread instead of
  the yield spread, and to adding CFNAI and the Cieslak-Povala trend-inflation factor as macro controls
  [FULL-TEXT, Table 1 description].
- OOS / economic value / costs: **none found** — this is a full-sample, split-regime in-sample regression
  and DTSM-fitting exercise; no recursive/expanding-window OOS test and no CER/Sharpe/portfolio exercise was
  located in the retrieved text.
- Category: **A (in-sample, real-time-observable state, no OOS or economic-value test)**. No independently
  confirmed 2020-2026-specific persistence paper was located within the time budget; this is flagged as a
  **gap** for a follow-up L2/L3 search pass (search terms to try next: "term premium predictability
  post-COVID", "duration timing 2022 rate hike cycle", "bond return predictability quantitative tightening").

---

## (b) Supportive vs. Contradictory tables

### SUPPORTIVE (of yield-curve-only duration-timing having genuine, not purely in-sample-overfit, value)
| Paper | What supports | Caveat |
|---|---|---|
| Rebonato & Nyholm (2025) | Argues CP predictability is not overfitting (resampling test) | Abstract-level only; no OOS/real-time/economic-value evidence confirmed |
| Gargano-Pettenuzzo-Timmermann (2019) | Genuine recursive OOS, positive long-only CER (≤1.6%/yr) | Real-time-vintage macro data NOT used; big (>2%/yr) gains need levered/short weights |
| Bauer-Rudebusch (2020) | Real-time-constructible i*; recursive OOS yield forecasts beat RW/FE/survey by ~40% RMSE at 10yr | Excess-return predictability itself shown in-sample only; no CER/Sharpe for a trading rule |
| Cieslak-Povala (2015) | Real-time-constructible trend-inflation predictor; in-sample R² far above EH-null 95th pctile | No confirmed OOS-R² or economic-value table for bond excess returns in main text |
| Borup et al. (2024) | Genuine recursive OOS-R², real-time-motivated combination scheme, uses CFNAI/Chauvet-Piger real-time state proxies | Individual-predictor CER weak; only novel combination method shows value; weights not long-only ([-1,2]) |
| Fan/Feng/Fulop/Li (2022, citing WFL2021) | Recovers OOS R² (up to ~8%) with real-time macro data + deep learning | Economic value explicitly requires leverage |
| Asness-Ilmanen-Maloney (2017) | Genuine long-only (near-100% notional) duration tilt, momentum leg improves Sharpe 0.27→0.38 | Gross of costs; value-only leg shows zero improvement |
| Andreasen-Jørgensen-Meldrum (2019) | Real-time-observable state (short rate <1%); R² doubles at ZLB, robust to several specs | In-sample only, no OOS/economic-value test |

### CONTRADICTORY (evidence against exploitable, real-world, long-only value)
| Paper | What contradicts |
|---|---|
| **Wan, Fulop & Li (2021)** (via Fan/Feng/Fulop/Li 2022 citation) | **No statistical or economic evidence** for one-month bond-return predictability once real-time (vs. fully-revised) macro data is used in standard linear models — directly falsifies the macro-augmented mechanism's real-time tradability |
| Bianchi-Büchner-Tamoni (2021) corrigendum | Original OOS-R² had a look-ahead-bias defect; had to be corrected downward (magnitude UNVERIFIED) |
| Gargano-Pettenuzzo-Timmermann (2019) | Their own recession/expansion predictability breakdown explicitly uses **non-real-time** (full-sample) NBER dating; largest CER gains need leverage/shorting, not long-only |
| Borup et al. (2024) | Individual (non-combined) predictor CER gains statistically indistinguishable from zero on average |
| Koijen-Moskowitz-Pedersen-Vrugt (2018) | Carry's edge is explicitly a short-duration/short-carry, crash-risk-bearing strategy, not a long-only tilt; higher costs acknowledged, unquantified |
| Brooks & Moskowitz (2017) | Highest-Sharpe results are also the most levered/long-short and are explicitly reported gross of transaction costs; footnote flags likely-higher realized costs there |
| Asness-Ilmanen-Maloney (2017) | Value-only bond timing signal (closest analogue to the academic yield-curve literature) shows **zero** Sharpe improvement over buy-and-hold |
| Ghysels-Horan-Moench (2018) [cited inside Borup et al. and WFL-citing paper, not independently read this session — UNVERIFIED primary] | Predictive power of macro variables for excess bond returns is "**mostly from data revisions**" — i.e. an artifact of using revised, non-real-time data |

---

## (c) Classification: A (strong in-sample) / B (true OOS) / C (real-time implementable)

| Paper | Class | Why |
|---|---|---|
| Rebonato & Nyholm (2025) | A (pending) | Statistical/overfitting defense only; OOS/real-time/econ-value not confirmed |
| Gargano-Pettenuzzo-Timmermann (2019) | B | Genuine recursive OOS 1990-2011, but non-real-time macro vintage and non-real-time recession split |
| Andreasen-Engsted-Møller-Sander (2021) | A (pending) | Full text not obtained; real-time character of state unverified |
| Borup-Eriksen-Kjær-Thyrsgaard (2024) | B/C | Recursive OOS + explicitly real-time-available state proxies (CFNAI, Chauvet-Piger), but combination-method-dependent and not long-only |
| Bianchi-Büchner-Tamoni (2021)+corrigendum | A→B (corrected) | ML OOS R² claimed, but a look-ahead defect had to be fixed; post-fix magnitude unverified here |
| Cieslak-Povala (2015) | A | In-sample R² only for bond excess returns in the retrievable main text, despite a real-time-constructible predictor |
| Bauer-Rudebusch (2020) | B (for yields) / A (for excess returns) | Recursive real-time OOS beats RW/FE for yield LEVEL forecasts; excess-return predictability shown in-sample only |
| Wan-Fulop-Li (2021) | C-negative | Real, real-time-implementable test — result is that predictability disappears |
| Fan/Feng/Fulop/Li (2022) | B | True OOS with real-time macro+news data; leverage-dependent economic value |
| Ilmanen (1995) | A (abstract only) | Not independently verified |
| Asness-Ilmanen-Maloney (2017) | C | Genuine long-only, real backtest, near-100% notional, but gross-of-cost and value leg alone shows no gain |
| Koijen-Moskowitz-Pedersen-Vrugt (2018) | B, not long-only | Real time-series OOS-style carry evidence, but long-short by construction |
| Brooks-Moskowitz (2017) | B/C, not long-only | Genuine "live"/real-time OOS test, but cross-country long-short, levered, gross-of-cost |
| Andreasen-Jørgensen-Meldrum (2019) | A | In-sample regime-split regression only; state variable is real-time-observable (a strength) but no OOS/econ-value test |

---

## (d) Does ANY later positive paper establish REAL-TIME + OOS + LONG-ONLY + AFTER-COST economic value for a yield-curve-only duration-timing rule?

**No.** Across the ten papers/groups audited, no single paper simultaneously satisfies all four conditions:

1. Papers with genuine **recursive/real-time OOS** evidence and **positive economic value**
   (Gargano-Pettenuzzo-Timmermann 2019; Borup et al. 2024; Fan/Feng/Fulop/Li 2022) all report their
   largest/decisive economic-value numbers under **levered and/or short-allowed weight constraints**
   ([-2,3], [-1,2], or explicit leverage), not long-only, and/or use **fully-revised (non-real-time) macro
   data** for the predictor itself (GPT 2019).
2. The one genuinely **long-only, near-100%-notional, real backtest** found (Asness-Ilmanen-Maloney 2017)
   is reported **gross of transaction costs**, and its value-only signal — the closest analogue to the
   academic yield-curve/CP-style literature — shows **zero** Sharpe-ratio improvement over buy-and-hold; only
   adding a momentum overlay produces a (still uncosted) gain.
3. The most directly relevant **real-time-data stress test** of the mechanism (Wan-Fulop-Li 2021, as cited
   in Fan/Feng/Fulop/Li 2022) finds predictability **vanishes** for standard models once real-time (as
   opposed to fully-revised) macro data are used; the deep-learning paper that partially revives it
   explicitly requires **leverage** for economic value.
4. Papers with real-time-observable state splits (Andreasen-Jørgensen-Meldrum 2019 ZLB regime; Borup et al.
   2024's CFNAI/Chauvet-Piger proxies) do not pair this with a costed, long-only economic-value calculation.

Conclusion for gate purposes: **the literature does not currently support promoting a yield-curve-only,
long-only, after-cost, real-time duration-timing rule past a Stage-0 mechanism screen** on the strength of
positive results alone — every positive economic-value number found required either leverage/shorting or
used non-real-time data, and the one clean long-only/near-neutral backtest found no edge from the
value-style signal itself before costs.

## (e) Do gains come from shorting duration / leverage?

**Predominantly yes, for the largest reported numbers.** Specifically:
- GPT (2019): headline CER gains >2%/yr and "above 200 bps/yr" require the ω∈[-2,3] scenario, not the
  long-only ω∈[0,0.99] scenario (which caps out around 1.2%-1.6%/yr, pre-cost).
- Borup et al. (2024): CER exercise uses ω∈[-1,2].
- Koijen-Moskowitz-Pedersen-Vrugt (2018) Carry: strategy is long-short by construction; the paper's central
  finding is that carry's edge is precisely its short-duration/short-carry crash exposure.
- Brooks-Moskowitz (2017): dollar-neutral long-short across countries, with the highest-Sharpe (butterfly)
  legs flagged by the authors themselves as the most levered and highest-cost.
- Fan/Feng/Fulop/Li (2022): economic gains from real-time macro data explicitly stated to require leverage.
- The one paper found NOT requiring leverage/shorting (Asness-Ilmanen-Maloney 2017, near-100% notional) shows
  no risk-adjusted edge from the value/yield-curve signal alone, only from adding momentum, and even then
  only gross of costs.

## (f) Modern-period persistence at literature-defined breakpoints

- **Post-1985** (Bauer-Rudebusch 2020): the i*-detrending R² gain **persists but shrinks** — from 12pp
  (full sample) to 6-9pp (post-1985), depending on detrending method; a "no gain" result only for the
  π*-only detrending, not for the r*/i* versions.
- **ZLB/2008-2015** (Andreasen-Jørgensen-Meldrum 2019): predictability **strengthens**, not weakens — R²
  roughly doubles (10%→20% for the 10-year bond) versus the pre-2008 regime, robust to several
  specifications.
- **Post-2000/post-2020**: no independently full-text-confirmed breakpoint test was located for these
  specific years within the time budget; this is a genuine gap (see item 10 above) rather than a documented
  null or positive result, and should not be treated as either supportive or contradictory.

## (g) Numbers tagged by verification level

- [FULL-TEXT] R² 0.24-1.6%/yr CER, long-only, GPT (2019) Table 5 discussion.
- [FULL-TEXT] R² >2%/yr, "above 200bps/yr" CER, levered/short [-2,3], GPT (2019).
- [FULL-TEXT] 10bps one-way cost reduces CER from 2.95%→1.80% (2yr) and 1.96%→1.48% (5yr), GPT (2019).
- [FULL-TEXT] Weight constraints ω∈[0,0.99] and ω∈[-2,3], GPT (2019).
- [FULL-TEXT] Weight constraints ω∈[-1,2], Borup et al. (2024).
- [FULL-TEXT] "Little evidence" of individual-predictor CER gain on average, Borup et al. (2024).
- [FULL-TEXT, secondary citation via Fan/Feng/Fulop/Li 2022] "No statistical or economic evidence" for
  real-time-macro-data bond return predictability, Wan-Fulop-Li (2021).
- [FULL-TEXT] OOS R² 2.8%(2yr, non-overlap), 1.69%-8.21% (overlapping, by maturity), 2.61% (all-maturity
  WGNN), Fan/Feng/Fulop/Li (2022); requires leverage for economic value.
- [FULL-TEXT] R² 0.24 / 0.18 / 0.54 / 0.53 (in-sample, Table 2 specs), Cieslak-Povala (2015).
- [FULL-TEXT] EH-null 95th-percentile in-sample R² = 0.23 (small-sample simulation), Cieslak-Povala (2015).
- [FULL-TEXT] ΔR² = 12pp (full sample), 6-9pp (post-1985), Bauer-Rudebusch (2020) Table 4.
- [FULL-TEXT] ~40% RMSE reduction at 10-yr-ahead yield forecast (OSE vs FE model), Bauer-Rudebusch (2020).
- [FULL-TEXT] Sharpe ratios 0.27 (buy-and-hold)/0.27 (value)/0.38 (momentum)/0.33 (V+M), 1958-2015,
  Asness-Ilmanen-Maloney (2017) Table A.2; gross of costs.
- [FULL-TEXT] Avg position size 86%-107% (long-only, near-neutral), Asness-Ilmanen-Maloney (2017).
- [FULL-TEXT] Level-value Sharpe 0.65, multi-style Sharpe 1.01, slope-carry Sharpe 0.69, alpha-to-GBI 3.0%
  (t=2.3), Brooks-Moskowitz (2017); long-short, gross of costs.
- [FULL-TEXT] R² doubles ~10%→~20% (10yr bond, ZLB vs pre-ZLB), Andreasen-Jørgensen-Meldrum (2019).
- [ABSTRACT] CP-predictability-is-not-overfitting claim, Rebonato-Nyholm (2025) — full text not obtained.
- [ABSTRACT] Slope-sign-flips-by-state claim, Andreasen-Engsted-Møller-Sander (2021) — full text not
  obtained (WebFetch returned only page chrome, no abstract text).
- [ABSTRACT/UNVERIFIED] Corrigendum "R² decreased but remained significant," Bianchi-Büchner-Tamoni (2021)
  — search-engine synthesis only, no primary text read; exact numbers not confirmed.
- [ABSTRACT] 4%-12% monthly R² across six countries, Ilmanen (1995) — full text not obtained.
- [UNVERIFIED] Ilmanen (1997) J. Fixed Income paper — not retrieved this session at all.
- [UNVERIFIED] "Mostly from data revisions" claim attributed to Ghysels-Horan-Moench (2018) — read only as
  quoted inside two other full-text papers (Borup et al.; Fan/Feng/Fulop/Li), not independently confirmed
  from Ghysels-Horan-Moench's own text.
- [UNVERIFIED] No 2020-2026-specific persistence paper was confirmed; Andreasen-Jørgensen-Meldrum (2019)
  substituted as the closest available ZLB-era breakpoint study (sample ends 2015/2018).

---

## (h) Bibliography

1. Rebonato, R. & Nyholm, K. (2025). "Why does the Cochrane–Piazzesi model predict treasury returns?"
   Journal of Empirical Finance, 84. DOI/URL: https://www.sciencedirect.com/science/article/abs/pii/S0927539825000726 ;
   SSRN working paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4846843 (PDF delivery blocked).
   Retrieved (search/abstract only): 2026-09-27.
2. Gargano, A., Pettenuzzo, D. & Timmermann, A. (2019). "Bond Return Predictability: Economic Value and
   Links to the Macroeconomy." Management Science 65(2):508-540. Working paper (July 28, 2016, Brandeis WP
   75R) used for full text: https://www.brandeis.edu/economics/RePEc/brd/doc/Brandeis_WP75R.pdf .
   Local file: reports/phase11c/raw/literature/gpt_brandeis.pdf . Retrieved: 2026-09-27.
3. Andreasen, M.M., Engsted, T., Møller, S.V. & Sander, M. (2021). "The Yield Spread and Bond Return
   Predictability in Expansions and Recessions." Review of Financial Studies 34(6):2773-2812.
   DOI: 10.1093/rfs/hhaa107 ; https://academic.oup.com/rfs/article-abstract/34/6/2773/5902842 (403/no
   abstract text retrieved). Retrieved (search only): 2026-09-27.
4. Borup, D., Eriksen, J.N., Kjær, M.M. & Thyrsgaard, M. (2024). "Predicting Bond Return Predictability."
   Management Science 70(2):931-951. Preprint used for full text:
   https://bpb-us-e1.wpmucdn.com/sites.northwestern.edu/dist/9/5191/files/2020/11/manuscript.pdf .
   Local file: reports/phase11c/raw/literature/borup_eriksen_kjaer_thyrsgaard_manuscript.pdf . Retrieved: 2026-09-27.
5. Bianchi, D., Büchner, M. & Tamoni, A. (2021). "Bond Risk Premiums with Machine Learning." Review of
   Financial Studies 34(2):1046-1089, and Corrigendum, 34(2):1090-1103. DOI (original):
   https://academic.oup.com/rfs/article-abstract/34/2/1046/5843806 . Retrieved (search only): 2026-09-27.
6. Cieslak, A. & Povala, P. (2015). "Expected Returns in Treasury Bonds." Review of Financial Studies
   28(10):2859-2901. Author-hosted PDF: https://pavol.povala.com/publication/2015_journal_cieslak_povala_rfs/2015_journal_cieslak_povala_rfs.pdf .
   Local file: reports/phase11c/raw/literature/cieslak_povala_rfs2015.pdf . Retrieved: 2026-09-27.
7. Bauer, M.D. & Rudebusch, G.D. (2020). "Interest Rates Under Falling Stars." American Economic Review
   110(5):1316-1354. FRBSF working-paper version: https://www.frbsf.org/wp-content/uploads/wp2017-16.pdf .
   Local file: reports/phase11c/raw/literature/bauer_rudebusch_fallingstars_frbsf.pdf . Retrieved: 2026-09-27.
8. Wan, R., Fulop, A. & Li, J. (2021). "Real-Time Bayesian Learning and Bond Return Predictability."
   Journal of Econometrics 230(1):114-130. SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2979332
   (PDF delivery blocked, HTTP 403). Cited/described via: Fan, Y., Feng, G., Fulop, A. & Li, J. (2022),
   "Real-Time Macro Information and Bond Return Predictability: A Weighted Group Deep Learning Approach"
   (First version Oct 2019, this version April 2022). PDF:
   https://www.qmul.ac.uk/sef/media/econ/images/documents/Real-Time-Macro-Information-and-Bond-Return-Predictability_compressed.pdf ;
   SSRN abstract: https://doi.org/10.2139/ssrn.3517081 . Local file:
   reports/phase11c/raw/literature/wan_fulop_li_qmul.pdf (note: filename reflects search target; actual
   content is the Fan/Feng/Fulop/Li 2022 citing paper — see note in block 8 above). Retrieved: 2026-09-27.
9a. Ilmanen, A. (1995). "Time-Varying Expected Returns in International Bond Markets." Journal of Finance
   50(2):481-506. DOI: 10.1111/j.1540-6261.1995.tb04792.x . Retrieved (search only): 2026-09-27.
9b. Ilmanen, A. (1997). "Forecasting U.S. Bond Returns." Journal of Fixed Income. Not retrieved this
   session.
9c. Asness, C., Ilmanen, A. & Maloney, T. (2017). "Market Timing: Sin a Little (Resolving the Valuation
   Timing Puzzle)." Journal of Investment Management 15(3):23-40. AQR-hosted PDF:
   https://www.aqr.com/-/media/AQR/Documents/Insights/White-Papers/Market-Timing-Sin-a-Little.pdf . Local
   file: reports/phase11c/raw/literature/asness_ilmanen_maloney_sinalittle_aqr.pdf . Retrieved: 2026-09-27.
9d. Koijen, R.S.J., Moskowitz, T.J., Pedersen, L.H. & Vrugt, E.B. (2018). "Carry." Journal of Financial
   Economics 127(2):197-225. NBER working paper version (w19325):
   https://www.nber.org/system/files/working_papers/w19325/w19325.pdf . Local file:
   reports/phase11c/raw/literature/koijen_moskowitz_pedersen_vrugt_carry_nber.pdf . Retrieved: 2026-09-27.
9e. Brooks, J. & Moskowitz, T.J. (2017/2018). "Yield Curve Premia." SSRN 2956411. Yale-hosted working
   paper PDF: https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2021/08/Yield-Curve-Premia.pdf .
   Local file: reports/phase11c/raw/literature/brooks_moskowitz_yieldcurvepremia_yale.pdf . Retrieved:
   2026-09-27.
10. Andreasen, M.M., Jørgensen, K. & Meldrum, A. (2019). "Bond Risk Premiums at the Zero Lower Bound."
   Federal Reserve Board FEDS 2019-040. DOI: 10.17016/FEDS.2019.040 . PDF:
   https://www.federalreserve.gov/econres/feds/files/2019040pap.pdf . Local file:
   reports/phase11c/raw/literature/andreasen_jorgensen_meldrum_zlb_fed2019.pdf . Retrieved: 2026-09-27.

All retrieval dates: 2026-09-27. All local files are git-ignored per repository policy
(`reports/phase11a/raw/literature/*` pattern, extended by convention to phase11c).
