# Phase 11C — Stage 0 Literature Audit (L1): Classic Term-Structure Risk-Premia Evidence

Sub-audit scope: classic bond-risk-premium predictability evidence (Fama-Bliss, Campbell-Shiller,
Cochrane-Piazzesi) and the main contradictory/out-of-sample literature. Companion sub-audits
(D1/D2 data-vintage audits, L2 modern/ML literature, V1 instrument metadata) are separate files
in this same directory; this file does not duplicate their scope.

Hard-rule compliance note: no price/yield/return time series were downloaded, loaded, or computed
anywhere in this audit. No regression, backtest, Sharpe, or CAGR was run. All numbers below are
**statistics published inside the cited papers**, transcribed by hand from extracted PDF text.
Every number is tagged `[FULL-TEXT, <location>]`, `[ABSTRACT]`, or `[UNVERIFIED]` per the source
rules. PDFs are archived in `reports/phase11c/raw/literature/` (git-ignored); see `SOURCES.txt`
in that folder for the full bibliography with local filenames.

---

## (a) Structured paper blocks

### 1. Cochrane & Piazzesi (2005), "Bond Risk Premia," AER 95(1):138-160

- **Version read**: NBER Working Paper 9178 (Sept. 2002 draft; tables match the published AER
  version per cross-checks against secondary citations) — read **in full text**, plus the
  authors' online appendix (`cpapp.pdf`), also read in full text.
- **Predictor**: single "tent-shaped" linear combination (γ'f) of the 1-year yield and four
  1-year-ahead forward rates (2→3, 3→4, 4→5, 5→6-year… i.e. maturities 1-5).
- **Data source**: Fama-Bliss/CRSP zero-coupon yields, unsmoothed, monthly, 1964:01-2001:12.
- **Horizon**: 1-year excess returns, overlapping monthly observations (12-month overlap).
- **In-sample vs OOS**: primarily in-sample full-sample regression; the paper also reports a
  genuine **real-time** recursive check (Section 5.2) and a small "trading rule" cumulative-profit
  exercise (Figure 8).
- **Coefficient estimation**: full-sample OLS for the headline result; a separate real-time
  version re-estimates γ recursively using only data available up to each date.
- **Maturities**: 2-5 year zero-coupon bonds.
- **Key result — R2**: single factor predicts 1-year excess returns on 1-5y bonds with
  **R2 = 0.34-0.37** (up to 0.44 with an added one-month lag of forwards)
  `[FULL-TEXT, Table 1, p.6 of NBER WP9178]`. Individual bond-level R2 values: n=2: 0.34, n=3:
  0.34, n=4: 0.37, n=5: 0.34 `[FULL-TEXT, Table 1]`.
- **Standard-error method**: "Large T" = Hansen-Hodrick GMM correction for overlap; "Small T" =
  95% bootstrap intervals from a 50,000-replication unconstrained 12-lag yield VAR; χ2 statistics
  use 18 Newey-West lags (needed for a positive-definite covariance matrix in the 5-variable
  joint test); an "EH" bootstrap imposes the expectations hypothesis on the DGP for a
  small-sample null distribution `[FULL-TEXT, notes to Table 1]`.
- **Stambaugh/small-sample bias treatment**: addressed via the bootstrap ("Small T"/"EH")
  columns rather than an explicit Stambaugh correction; the paper explicitly cites concern over
  small-sample properties (Bekaert, Hodrick and Marshall 1997) as motivation
  `[FULL-TEXT, p.6 footnote 1]`.
- **Lagged-forward / measurement-error checks**: the paper documents a moving-average structure
  in monthly yields "possibly induced by measurement error," such that a monthly AR(1)
  representation misses the 1-year predictability entirely — one must look at the annual horizon
  directly `[FULL-TEXT, p.3-4]`. Adding a one extra lagged month of forwards raises R2 by ~0.05 to
  0.39-0.43 and a χ2 test rejects the null that the extra lag's coefficients are zero
  `[FULL-TEXT, Table 11 discussion, p.28-29]`.
- **Subsample stability**: Table 9 reports the full-sample coefficients/R2 (γ0..γ5, R2=0.35) and
  eight subsamples: 1964-1999 (R2=0.40), 1964-1979:08 (R2=0.32), 1979:08-1982:10 (R2=0.78, the
  Volcker episode — "dramatic" per the authors but on a very short/volatile subsample), 1982:10-
  2001 (R2=0.27), and decade splits 1964-69 (0.31), 1970-79 (0.22), 1980-89 (0.42), 1990-99
  (0.71) `[FULL-TEXT, Table 9]`. The tent-shaped coefficient pattern recurs in every subsample.
- **Real-time / OOS check**: Figure 7 compares full-sample vs. real-time recursively re-estimated
  fitted values; "the full sample and real time forecasts are quite similar," though the real-time
  forecast is "a good deal lower" for the largest 1994 episode `[FULL-TEXT, p.24-25]`. The Figure 8
  cumulative-profit trading-rule exercise finds the real-time forecast "produces only about half
  of the cumulative profits" of the full-sample version, i.e. **the strategy degrades materially
  but does not vanish under real-time re-estimation** `[FULL-TEXT, p.25-26]`.
- **Data-construction robustness (measurement-error checks)**: Table 10 repeats the analysis on
  McCulloch-Kwon zero-coupon data (a different interpolation scheme than Fama-Bliss) over
  1964:1-1991:2 — R2 values are "very similar across the two datasets" (e.g., n=5: M-K R2=0.35 vs
  FB R2=0.37 using the all-forwards specification) and "the tent-shape of γ estimates is even more
  pronounced in McCulloch-Kwon data" `[FULL-TEXT, Table 10 and surrounding text, p.28-29]`.
- **Smoothed-curve discussion**: CP2005 itself does not test GSW (GSW was published in 2006/2007,
  after this 2002/2005 draft); the smoothed-curve weakening result is documented in the follow-up
  paper below (CP 2008).

### 2. Fama & Bliss (1987), AER 77(4):680-692, and Campbell & Shiller (1991), Rev. Econ. Studies 58(3):495-514

- **Fama & Bliss (1987)**: original PDF obtained (`fama_bliss_1987.pdf`) but it is a scanned image
  with **no extractable text layer**; OCR is not available in this environment (poppler/tesseract
  not installed), so the original paper's own tables could **not** be read in primary text. Two
  independent sources are used instead:
  - `[ABSTRACT]` WebSearch-derived secondary summary: R2 for the US forward-spread regression
    rises from "0% to 19%" across horizons j=1 to j=4 — **UNVERIFIED**, not independently
    confirmed against the primary table.
  - `[FULL-TEXT, Table 3, Cochrane & Piazzesi 2005 NBER WP9178]` — CP2005 **replicates** the
    classic Fama-Bliss single-forward-spread regression (rx_(n)_{t+1} = α + β·(f_{n-1→n,t} −
    y1_t) + ε) on their own 1964-2001 CRSP sample: β = 0.94 (n=2), 1.24 (n=3), 1.50 (n=4), 1.10
    (n=5); R2 = 0.14, 0.14, 0.15, 0.06 respectively. This is a modern-sample replication, not the
    original 1954-1985-ish Fama-Bliss sample, but it is read in full primary text and is the
    number this audit treats as decision-grade for "what the Fama-Bliss regression yields."
  - Standard errors in the CP2005 replication use the same Hansen-Hodrick/bootstrap apparatus as
    their Table 1 (see paper 1 above).
- **Campbell & Shiller (1991)**: PDF obtained and OCR text layer present — read **in full text**.
  - **Predictor**: yield spread S(n,m) = (R(n) − R(m)) between an n-period and m-period bond;
    regression of the change in the long yield or short-rate path onto the spread, per the
    "theoretical spread" S*(n,m) framework.
  - **Data**: postwar U.S. term-structure data, one month to ten years, various subsamples.
  - **Key result**: for almost every maturity pair, the regression coefficient (which the
    expectations hypothesis predicts should equal 1) is of the **wrong sign or far from one**; one
    explicit example quoted in text: "the coefficient in Table 1(a) for m=3 and n=6 is b = −1.279"
    `[FULL-TEXT, p.10 of PDF]`. Table 2 coefficients (regression of the perfect-foresight spread on
    the actual spread) are "almost always positive but also deviate substantially from one," with
    long-end coefficients showing the strongest EH violations `[FULL-TEXT, p.11]`.
  - **Standard errors**: Hansen-Hodrick (1980) with a White (1984) correction; footnoted that for
    one regression "Newey-West (1987) correction [was] used because [the] Hansen-Hodrick
    procedure gave a negative standard error" `[FULL-TEXT, Table 2 notes, p.11]` — i.e., the paper
    itself documents a known small-sample HH pathology.
  - **Subsample robustness**: Table 1(b) reports the m=1 regression over "a variety of" subsamples
    and states the wrong-sign pattern "is robust to the sample period" `[FULL-TEXT, p.9-10]`.
    A specific comparator is given: for the 1959-1979 sample the slope was 0.285 vs. different
    values in other cited papers' subsamples (Mankiw-Miron, Fama) `[FULL-TEXT, p.10]`.

### 3. Thornton & Valente (2012, RFS), "Out-of-Sample Predictions of Bond Excess Returns and Forward Rates: An Asset Allocation Perspective," RFS 25(10):3141-3168

- **Full text NOT obtained.** RFS (paywalled), SSRN abstract page (HTTP 403), the St. Louis Fed
  working-paper mirror (link rot / access-denied on the S3-hosted PDF), and the Essex University
  repository mirror (host unreachable from this network) were all tried and failed — see
  `L1_snapshots/INDEX.md` for the attempted URLs. Everything below is `[ABSTRACT]` or
  `[UNVERIFIED]`, sourced only from the RFS DOI abstract and WebSearch-rendered summaries of it.
- **Predictor**: empirical models based on long-term forward interest rates (Fama-Bliss- and
  Cochrane-Piazzesi-style).
- **Design** `[ABSTRACT]`: genuine out-of-sample recursive forecasting exercise embedded in a
  **dynamic asset-allocation** framework — i.e., this is explicitly designed as an OOS economic-
  value test, not an in-sample statistical test.
  `[UNVERIFIED — exact weight constraints (long-only vs. leveraged), the precise benchmark
  portfolio, and the specific economic-value metric and its magnitude were not visible in any
  accessible abstract text and are NOT reported here as numbers.]`
- **Headline finding** `[ABSTRACT]`: "the information content of forward rates does not generate
  any systematic economic value to investors" and the forward-rate models "do not outperform the
  no-predictability benchmark" — i.e., **statistical in-sample predictability failed to survive
  translation into realized OOS economic value for a dynamic asset allocator.** This is consistent
  with, and independently corroborated by, the primary-text-verified Sarno-Schneider-Wagner (2016)
  result below (different authors, same qualitative conclusion, methodologically related but not
  identical).
- Because no primary text was obtained, this paper is used in the SUPPORTIVE/CONTRADICTORY tables
  below strictly as a **directionally contradictory, UNVERIFIED-magnitude** data point.

### 4. Duffee (2011), "Information in (and Not in) the Term Structure," RFS 24(9):2895-2934

- **Version read**: author-hosted final draft (Jan. 2011) — read **in full text**.
- **Mechanism**: standard term-structure models assume yields span all pricing-relevant
  information (the "Markov"/spanning assumption). Duffee relaxes this and estimates a 5-factor
  affine model in which one factor is allowed to be "hidden" — nearly orthogonal to current yields
  contemporaneously, but still priced.
- **Estimation**: Kalman filter, **full-sample** estimation (not recursive/real-time; no OOS test
  is present anywhere in the paper — confirmed by an explicit full-text search for
  "out-of-sample"/"recursive"/"real time," none of which occur) `[FULL-TEXT — absence confirmed by
  direct text search of the extracted PDF]`.
- **Key result**: the "variance ratio" — Var(E[excess return|3 yield PCs]) / Var(E[excess
  return|full 5-factor state vector]) — is **0.53** in population, with a 95% CI upper bound of
  0.68. I.e., "close to half of the information in the state vector is hidden from the cross
  section of yields" `[FULL-TEXT, p.27-28, Table 2 discussion]`. The abstract's "almost half" claim
  is thus the same 0.53 number, read in full text, not just the abstract.
- **Filtering requirement**: yes — full-sample Kalman **smoothing** (not just one-sided filtering)
  is required to extract the hidden factor; the paper explicitly notes that using **filtered**
  (one-sided, causal) vs. **smoothed** (two-sided, full-sample) estimates changes the in-sample
  predictive R2 materially: "the predictive regression R2 is only 0.043, compared with the optimal
  filtering variance ratio of 0.085" `[FULL-TEXT, p.32-33]` — i.e., the paper itself flags that the
  in-sample smoothed-state regression **overstates** true forecastability relative to a causal
  filtered estimate, because smoothed states are constructed with look-ahead information within
  the estimation sample.
- **Economic activity link**: hidden factor is negatively correlated with aggregate economic
  activity but macro variables explain only "a small fraction" of its variation `[FULL-TEXT,
  abstract, p.1]`.

### 5. Adrian, Crump & Moench (2013), "Pricing the Term Structure with Linear Regressions," JFE 110(1):110-138

- **Version read**: NY Fed Staff Report 340 (revised April 2013) — read **in full text**.
- **Method**: three-step linear-regression (Fama-MacBeth-style) estimation of an affine term
  structure model; computationally fast, full-sample point estimates with asymptotic standard
  errors, but the model comparison exercise uses a **genuine expanding-window recursive** OOS test.
- **Data**: GSW smoothed yields (this is a direct, primary-text data point for the smoothing
  question — see below).
- **CP-factor replication under GSW data**: constructing their own version of the CP
  return-forecasting factor from **monthly** GSW excess returns regressed on 10 lagged one-year
  forward rates, the **average R2 across the individual one-month predictive regressions is
  7.5%** `[FULL-TEXT, p.23, Eq.37 discussion]` — much lower than CP's own 34-44% **annual**-horizon
  R2, though this is not an apples-to-apples comparison (monthly vs. annual horizon, GSW vs.
  Fama-Bliss data, and a different regressor set).
- **Full-sample vs. recursive**: the core term-structure-model estimates are **full-sample**; the
  five-vs-four-factor model comparison uses an **expanding-window recursive** OOS exercise,
  starting with a 1987:01-1991:12 training window and re-estimating monthly thereafter, forecasting
  average short rates up to 5 years ahead `[FULL-TEXT, p.26-27]`.
- **Key OOS result**: the 5-PC model "outperforms the [Cochrane and Piazzesi (2008)] four-factor
  specification in out-of-sample exercises" both for short-rate RMSE and cross-sectional yield fit
  at long maturities, while producing "similar in-sample term premium dynamics"
  `[FULL-TEXT, abstract; p.27-28]`. The 4-factor (CP-type) model "strongly understates the degree
  of persistence of the pricing factors" and its model-implied yields for maturities beyond 10
  years are "far below their realized values" `[FULL-TEXT, p.28]`.

### 6. Bauer & Hamilton (2018), "Robust Bond Risk Premia," RFS 31(2):399-448

- **Version read**: author-hosted version (revised May 22, 2017) — read **in full text**.
- **Mechanism**: standard Newey-West/Hansen-Hodrick inference for the "spanning hypothesis" tests
  (do variables beyond level/slope/curvature predict returns?) suffers severe small-sample size
  distortions when regressors are persistent and the sample is short. They propose a parametric
  bootstrap (with a bias-corrected variant) calibrated under the null.
- **Key general result**: for six widely cited spanning-hypothesis rejections (including
  Ludvigson-Ng macro factors), the **true size of conventional HAC tests is 19-36% instead of the
  nominal 5%** `[FULL-TEXT, p.20-21]`; using the bootstrap, evidence against spanning is "much
  weaker than it originally appeared" for most of the six studies.
- **What survives for CP specifically**: Bauer-Hamilton **do not reject** CP's core 3-PC
  tent-shaped factor as a stable predictor — "[CP's] central claim, with which we concur, is that
  the factor they have identified is a useful and stable predictor of bond returns... a result that
  we have been able to reproduce and confirm" `[FULL-TEXT, p.30]`.
- **What does NOT survive**: CP's claim that the 4th and 5th principal components of yields
  (beyond level/slope/curvature) contain **additional** predictive information. In the 1985-2016
  subsample, "the increase in R2 due to inclusion of higher-order PCs is comfortably inside the 95%
  bootstrap intervals, and the coefficients on PC4 and PC5 are not significant for any method of
  inference" `[FULL-TEXT, p.29]`. In a **true OOS** test using data after CP's original sample
  ended (their "longest true OOS period among the studies considered"), including PC4/PC5
  **reduces in-sample MSE by 11% but increases OOS MSE by 21%** relative to the restricted
  3-PC model `[FULL-TEXT, p.29-30]` — a clean, quantified example of in-sample overfitting that
  reverses sign out-of-sample.
- **Secondary citation, not independently verified**: a footnote states that Cattaneo & Crump
  (2014), using a different HAC test (Müller 2014), "did not reject the null hypothesis that the
  CP factor had no predictive power in a variety of in-sample and OOS specifications"
  `[FULL-TEXT — the footnote itself was read in primary text, but Cattaneo & Crump's own paper was
  not obtained, so THEIR underlying numbers are UNVERIFIED / secondary-citation only]`.

### 7. Sarno, Schneider & Wagner (2016), "The Economic Value of Predicting Bond Risk Premia," J. Empirical Finance 37:247-267

- **Version read**: CBS accepted-manuscript postprint (Feb. 10, 2016) — read **in full text**.
- **Method**: a new affine term-structure-model estimation ("extended estimation") that jointly
  fits yields and past excess returns, compared against a "standard estimation" (yields-only) and
  against the expectations hypothesis (EH, using historical-average excess returns as the
  EH-consistent forecast).
- **Investor types / weight constraints**: (i) mean-variance investors with a target volatility
  σ* = 2% p.a. and (ii) power-utility investors with constant relative risk aversion ρ=3. Both
  cases **impose a maximum leverage of 100%** `[FULL-TEXT, p.19, Eq.24 discussion]` — i.e. the
  risky-bond weight is capped, not literally long-only-with-no-shorting, but a bounded-leverage
  allocation, not an unconstrained arbitrage portfolio. Covariances are estimated via sample
  standard deviations / rolling and expanding windows, not model-implied, for the baseline results
  (robustness checked with model-implied covariances, "no impact on our conclusions"
  `[FULL-TEXT, p.18, fn.10]`).
- **Economic-value measure**: Θ, the Goetzmann et al. (2007) manipulation-proof performance
  measure — chosen explicitly because, unlike the Sharpe ratio, "Θ alleviates concerns related to
  non-normality" `[FULL-TEXT, p.19]`.
- **Key result — in-sample vs OOS divergence**: switching from standard to extended estimation of
  the latent-factor model generates Θ>0 in-sample for all 25 horizon/maturity combinations and in
  23 of 25 OOS combinations (statistical predictability replicates OOS), **but** relative to the
  EH benchmark, premium returns are positive in 21 of 25 combinations **in-sample** and only 13 of
  25 **out-of-sample** `[FULL-TEXT, p.19-20]`. Quantified magnitude: "out-of-sample, mean-variance
  investors with a one-year horizon would pay an annual premium of up to 3.5% to switch from the
  standard to the extended estimation... [but] relative to the EH, bond investors earn premium
  returns in-sample... but not out-of-sample" `[FULL-TEXT, p.20]`.
- **Headline conclusion**: "ATSMs generally cannot beat the EH out-of-sample in terms of economic
  value" — explicitly likened by the authors to "the bond market analogue to the result of Goyal
  and Welch (2008) for stock markets" `[FULL-TEXT, p.20]`.
- **Robustness to Adrian-Crump-Moench (2013) estimation**: repeating the exercise with the ACM
  regression-based estimator (1-month horizon) gives in-sample slope coefficients of 0.99-1.01 and
  R2 of 4-6%, positive economic value in-sample "in half of the cases," and negative economic
  value OOS `[FULL-TEXT, p.21]`.
- **Transaction costs**: not explicitly modeled as bid-ask/commission costs in the version read;
  the analysis is costs-**exclusive**, meaning the negative OOS economic-value finding is if
  anything conservative evidence *for* rejection (real transaction costs would only worsen it).
- **Robustness check citing Thornton & Valente (2012)** `[FULL-TEXT]`: "simple linear regression
  and rolling sample variance estimates, as for instance in Thornton and Valente (2012), lead to
  the same conclusions" `[FULL-TEXT, p.18, fn.10]` — this is the strongest primary-text corroboration
  obtained in this audit that Thornton-Valente's (unread) result direction is genuine.

### 8. Hodrick & Tomunen (2018), "Taking the Cochrane-Piazzesi Term Structure Model Out of Sample: More Data, Additional Currencies, and FX Implications," NBER WP 25092

*(Substituted/added as "another important contradictory OOS paper" per the audit's item 8 — found
during the search for CP's own follow-up work; read in full text.)*

- **Design**: extends CP(2005, 2008)'s one-factor model to additional currencies and to a genuine
  **recursive out-of-sample** forecasting exercise across a longer sample (pre-2004 vs. post-2003
  split, explicitly testing coefficient stability across the split).
- **Key result**: "the model fails to beat historical average returns in recursive out-of-sample
  forecasting of excess rates of return" `[FULL-TEXT, abstract, p.1]`; a one-factor structure is
  found again in post-2003 data for each currency but the paper **rejects equality of the
  coefficients** across the pre-/post-2003 samples `[FULL-TEXT, abstract]` — i.e., parameter
  instability across a natural chronological split, and a genuine historical-average benchmark
  beats the model OOS.
- **Relevance**: this is a clean, quantified, true-OOS, multi-currency falsification of the
  CP-style single-factor model's practical forecasting value, independent of and consistent with
  Bauer-Hamilton's and Sarno-Schneider-Wagner's OOS findings above.

### 9. Smoothed (GSW) vs. unsmoothed (Fama-Bliss) yield curves — direct evidence

- **Primary source, read in full text**: Cochrane & Piazzesi (2008), "Decomposing the Yield
  Curve" (authors' working-paper version, March 13, 2008). Table 1 (p.13) directly compares
  forecasting R2 for average excess returns using GSW vs. Fama-Bliss forward rates as regressors:

  | Right-hand variables | rxGSW on fGSW | rxGSW on fFB | rxFB on fFB | rxGSW on (fFB − y1) |
  |---|---|---|---|---|
  | f1-f5 | 0.29 | 0.35 | 0.33 | 0.32 |
  | f1,f3,f5 | 0.26 | 0.33 | 0.31 | 0.29 |
  | f1-f15 (GSW only) | 0.38 | — | — | — |
  | 3-mo MA, f1-f5 | 0.31 | 0.46 | 0.42 | 0.44 |

  `[FULL-TEXT, Table 1, cp_decomposing_2008_final.pdf, p.13]`

  The authors' own interpretation, quoted in full text: regressing GSW returns on **GSW** forwards
  gives R2=0.29 with coefficients showing a "strong W shape suggestive of multicollinearity rather
  than the tent-shape"; regressing the same GSW returns on **Fama-Bliss** forwards instead gives a
  *better* R2 (0.35) with the "exactly the same tent-shaped pattern" as the original 2005 result.
  Conclusion in the authors' own words: "This finding suggests ill effects of smoothing across
  maturities in the GSW data. The GSW smoothing removes some measurement error along with the
  forecasting signal" `[FULL-TEXT, p.13-14]`. Using 15 GSW forwards as regressors superficially
  raises R2 to 0.38 but with "an uninterpretable combination of strong positive and negative"
  coefficients, "the clear sign of extreme multicollinearity" — i.e. **not** a usable signal
  `[FULL-TEXT, p.14]`.

- **Corroborating primary source**: Liu & Wu (2021), "Reconstructing the Yield Curve," JFE
  142(3):1395-1425 (NBER WP 27266, read in full text). Liu-Wu construct a new kernel-smoothed
  curve and explicitly cite CP's own finding: "Cochrane and Piazzesi (2009) show that using the
  GSW dataset reduces return predictability because the yield curve is too smooth to capture
  information in higher order principal components" `[FULL-TEXT, p.2]`. Using their own curve
  instead of GSW, they find "a robust loading pattern over the five forward rates, as in Cochrane
  and Piazzesi (2005)... consistent... over different sample periods," whereas "estimates based on
  the GSW data do not produce a one-factor interpretation: the estimated loadings do not have a
  consistent pattern across maturity ranges or over time," with loadings that "differ by an order
  of magnitude between CP's original sample period up to 2003, and the sample extended through
  2019" `[FULL-TEXT, p.4-5]`. On the spanning-hypothesis test (4th/5th PC additional predictive
  power), their curve supports unspanned factors consistent with CP and Duffee (2011), while "with
  GSW data, the higher-order principal components fail to show additional predictive power using
  CP's original sample period" and loadings are unstable across the extended sample
  `[FULL-TEXT, p.5]`.
- **Net assessment**: this is a **decisive, primary-text-confirmed, multiply-corroborated**
  finding: **smoothed curves (GSW/Nelson-Siegel-Svensson-style) measurably weaken and destabilize
  the CP tent factor and its higher-order-PC extension**, relative to unsmoothed Fama-Bliss-style
  or Liu-Wu kernel-smoothed curves. This has direct data-feasibility implications: since this
  research program's available Treasury data construction choice was not yet re-verified at the
  time of this literature audit, **any subsequent empirical Stage 1 test of a CP-type factor must
  use an unsmoothed (Fama-Bliss-style) or Liu-Wu-style curve, not a GSW/Nelson-Siegel-Svensson
  smoothed curve, or the factor's measured strength will be understated and destabilized purely as
  a data-construction artifact.**

---

## (b) Supportive vs. Contradictory tables

### SUPPORTIVE (predictability is real, at least in some form)

| Paper | Result | Sample/design | Magnitude | Evidence class |
|---|---|---|---|---|
| Cochrane & Piazzesi (2005) | Tent-factor predicts 1y excess returns | Full-sample, 1964-2001, monthly overlap | R2 = 0.34-0.44 `[FULL-TEXT]` | A (in-sample); partial B (real-time check retains ~half the trading-rule profit) |
| Cochrane & Piazzesi (2005) | Subsample stability of tent shape | 8 subsamples 1964-1999 | R2 range 0.22-0.78 (excl. Volcker outlier) `[FULL-TEXT]` | A |
| Cochrane & Piazzesi (2005) | Cross-dataset robustness | McCulloch-Kwon vs Fama-Bliss, 1964-1991 | R2 within 0.01-0.05 of each other `[FULL-TEXT]` | A |
| Bauer & Hamilton (2018) | CP's 3-PC tent factor itself survives bootstrap-robust inference | Full-sample bootstrap, six studies re-examined | Explicitly "concur" it is stable `[FULL-TEXT]` | A/B hybrid (bootstrap-robust, not truly OOS for this specific claim) |
| Adrian, Crump & Moench (2013) | 5-PC model beats 4-factor CP-type model OOS for short-rate forecasts | Expanding-window recursive, 1987 start | Lower RMSE than CP-type 4-factor and random walk `[FULL-TEXT]` | B (true recursive OOS), but this supports a *different, richer* model, not the plain CP factor |
| Sarno, Schneider & Wagner (2016) | Extended-estimation ATSM beats standard-estimation ATSM OOS | True OOS, mean-variance/power utility | Θ>0 in 23/25 (mean-var) and other configs `[FULL-TEXT]` | B — but this is model-vs-model, NOT model-vs-EH |
| Liu & Wu (2021) | CP tent factor is robust across time when built on an unsmoothed/kernel-smoothed curve | Full CP replication + extended sample to 2019 | Consistent loadings, unlike GSW `[FULL-TEXT]` | A (in-sample robustness across time, not a real trading OOS test) |

### CONTRADICTORY (predictability fails to survive OOS / economic-value / robust-inference scrutiny)

| Paper | Result | Sample/design | Magnitude | Evidence class |
|---|---|---|---|---|
| Bauer & Hamilton (2018) | CP's 4th/5th-PC "extra" predictive information does not survive | 1985-2016 subsample + true post-CP-sample OOS | In-sample MSE −11%, OOS MSE **+21%** when PC4/PC5 included `[FULL-TEXT]` | B (true OOS) |
| Bauer & Hamilton (2018), citing Cattaneo & Crump (2014) | CP factor found to have no predictive power under a different robust HAC test | Secondary citation only | Not quantified here | **UNVERIFIED (secondary citation)** |
| Hodrick & Tomunen (2018) | CP-style model fails to beat historical-average benchmark OOS; coefficients unstable pre/post 2003 | Recursive OOS, multi-currency, split-sample | Model loses to historical average `[FULL-TEXT]` | B (true OOS) |
| Sarno, Schneider & Wagner (2016) | ATSM-based bond risk premium forecasts cannot beat the EH out-of-sample in economic value | True OOS, mean-variance & power-utility investors, Θ measure | Positive Θ in-sample vs. EH in 21/25 cases, only 13/25 OOS; up to 3.5% annual CE premium is for switching estimation method, not for beating EH `[FULL-TEXT]` | B (true OOS, economic value) |
| Thornton & Valente (2012) | Forward-rate-based bond return forecasts generate no systematic economic value to a dynamic asset allocator | OOS asset-allocation exercise | Not quantified here (full text unavailable) | **C-claimed but UNVERIFIED** (abstract only) |
| Ghysels, Horan & Moench (2014/2018) | Macro-variable return predictability is substantially inflated by look-ahead use of revised (non-real-time) data | Real-time vintage vs. final-revised data, 1982-2011 | R2 rises from 18-19% (yield-only benchmark) to 28%/23% (2y/5y) using revised macro data; degrades using real-time vintages `[FULL-TEXT]` | C (real-time implementable design) — **but this critique targets macro-variable predictors, not the CP yield-only factor itself, which the paper treats as an unaffected benchmark (see below)** |

---

## (c) Evidence classification per paper

- **Cochrane & Piazzesi (2005)** — **A** (strong in-sample) with a genuine but partial **B**
  component (real-time recursive check retains roughly half the trading-rule cumulative profit;
  this is real-time re-estimation, not a true expanding-window forecast-and-trade backtest with
  transaction costs, so it stops short of full **C**).
- **Fama & Bliss (1987) / Campbell & Shiller (1991)** — **A** (in-sample, full-sample regressions
  against the expectations hypothesis; no OOS design in either paper as read/summarized).
- **Thornton & Valente (2012)** — claimed **B/C** (genuine OOS asset-allocation design per the
  abstract) but this audit cannot verify the claim's exact numbers; treat as **UNVERIFIED**.
- **Duffee (2011)** — **A only**. Full-sample Kalman-filter/smoother estimation; no OOS test
  exists in the paper (confirmed by direct text search). Requires two-sided smoothing to identify
  the hidden factor, which is explicitly **not** real-time implementable in the form presented (the
  paper itself shows filtered/causal R2 of 0.043 vs. smoothed 0.085 — using only past information
  roughly halves the apparent predictability).
- **Adrian, Crump & Moench (2013)** — **A** for the main term-structure-model estimates
  (full-sample); **B** (true recursive expanding-window OOS) for the model-comparison exercise.
- **Bauer & Hamilton (2018)** — **A/B hybrid**: full-sample bootstrap-robust inference for the
  main spanning-hypothesis tests (rigorous but not OOS), plus one explicit **B** true-OOS
  comparison (PC4/PC5 MSE test) that is directly contradictory.
- **Sarno, Schneider & Wagner (2016)** — **B** (true out-of-sample, real economic-value metric,
  though costs-exclusive and leverage-capped at 100% rather than literally unconstrained).
- **Ghysels, Horan & Moench (2014/2018)** — **C** for its own design (uses actual real-time data
  vintages, the strongest standard in this list), but its critique is scoped to **macro-variable**
  predictors layered on top of yields, not to the yield-only CP factor.
- **Hodrick & Tomunen (2018)** — **B** (true recursive OOS across an extended, split sample).
- **Liu & Wu (2021)** — **A** (in-sample/full-sample robustness-of-construction exercise, not an
  OOS trading test); its contribution is about **data construction**, not new OOS evidence.

---

## (d) Long-only vs. long-short/leveraged economics

- **Cochrane & Piazzesi (2005)**: the "trading rule" cumulative-profit exercise (Figure 8) is not
  described with an explicit weight-constraint specification in the sections read; it appears to be
  an unconstrained directional signal-following exercise (long or short the bond based on forecast
  sign), not a formally risk-managed portfolio. No leverage figure is stated.
- **Sarno, Schneider & Wagner (2016)**: **explicitly bounded** — "impose a maximum leverage of
  100%" for both the mean-variance investor (target vol σ*=2% p.a.) and the power-utility investor
  (ρ=3) `[FULL-TEXT, p.19]`. This is a levered-but-capped long (and presumably occasionally short,
  since the optimal weight formula in Eq. 23 can go negative if the conditional expected excess
  return is negative) allocation, not a pure long-only buy-and-hold. Gains are **not** shown to
  require leverage beyond 100%; indeed the OOS result is that gains vs. the EH mostly **fail to
  appear at all**, regardless of the leverage cap.
- **Thornton & Valente (2012)**: weight-constraint details `[UNVERIFIED]` — not available from any
  accessible source in this audit.
- **Adrian, Crump & Moench (2013)** and **Hodrick & Tomunen (2018)**: these are forecast-accuracy
  (RMSE) exercises, not portfolio/economic-value exercises; no weight constraints apply.
- **General implication for this project**: the one paper with a fully documented, primary-text
  economic-value test under **realistic, bounded (not literally long-only, but leverage-capped)**
  constraints (Sarno-Schneider-Wagner 2016) finds that gains over a naive EH/historical-average
  benchmark **do not survive out-of-sample**, and this does **not** appear to be a leverage-access
  artifact — the in-sample vs. OOS gap is the dominant driver of the negative result, not the
  weight cap.

---

## (e) Modern-sample persistence (literature-defined periods only)

- **Bauer & Hamilton (2018)**: CP's core 3-PC tent factor is explicitly confirmed stable through
  their most recent subsample (up to 2016) `[FULL-TEXT]`. However, the **incremental** 4th/5th-PC
  information that CP originally emphasized is **not** stable post-1985 and specifically fails in
  the true-OOS post-CP-sample period (their "longest true OOS period among the studies
  considered," extending past CP's original ~2003 end date) `[FULL-TEXT]`.
- **Hodrick & Tomunen (2018)**: explicitly splits pre-2004 vs. post-2003 and **rejects coefficient
  equality** across that split — i.e., documents an explicit break rather than smooth persistence,
  and shows the model loses to the historical-average benchmark in the modern, post-2003 OOS
  period `[FULL-TEXT]`.
- **Liu & Wu (2021)**: extends the CP replication through 2019 and finds the tent-shaped loading
  pattern **persists** when the curve is built without GSW-style smoothing, but GSW-based loadings
  "differ by an order of magnitude" between the original CP sample and the 2019-extended sample —
  i.e., apparent modern-sample instability in prior GSW-based CP replications may be a smoothing
  artifact rather than a genuine regime change `[FULL-TEXT]`.
- **Ghysels, Horan & Moench (2014/2018)**: sample extends to 2011 with a note that findings are
  "robust to extending the sample to 2011" `[FULL-TEXT, p.11]`; this is about their macro-revision
  critique, not directly about CP-factor persistence.
- **No paper in this audit tests persistence into 2020+** (COVID / post-2020 hiking cycle); this is
  a genuine literature gap as of the papers read here, consistent with this program's own
  2025/2026 validation and holdout segments remaining unopened and therefore uninformed by any
  peeking into that period via the literature.

---

## (f) Full ledger of every decisive number, tagged

`[FULL-TEXT, Table 1, CP2005 NBER WP9178]` R2 = 0.34-0.37 (up to 0.44 with lag) for 1y excess
return tent-factor regression, 1964-2001.
`[FULL-TEXT, Table 9, CP2005]` Subsample R2: 0.35 (full), 0.40 (excl. last 2y), 0.32/0.78/0.27
(pre/Volcker/post), 0.31/0.22/0.42/0.71 (decades 1960s-1990s).
`[FULL-TEXT, Table 10, CP2005]` McCulloch-Kwon vs Fama-Bliss R2 comparison, within 0.01-0.05 of
each other across n=2..5.
`[FULL-TEXT, Table 3, CP2005]` Fama-Bliss-style single-spread regression replicated on 1964-2001
data: β=0.94-1.50, R2=0.06-0.15.
`[ABSTRACT/UNVERIFIED]` Original Fama & Bliss (1987) R2 "0% to 19%" across horizons — not
independently confirmed (source PDF has no extractable text).
`[FULL-TEXT, p.10, Campbell & Shiller 1991]` Example slope coefficient b = −1.279 (m=3, n=6),
expectations-hypothesis-implied value = 1.
`[FULL-TEXT, Table 1, CP 2008 "Decomposing the Yield Curve"]` R2 = 0.29 (GSW-on-GSW) vs 0.35
(GSW-return-on-FB-forwards) vs 0.33 (FB-on-FB) — smoothing-weakens-signal result.
`[FULL-TEXT, p.27-28, Duffee 2011]` Population variance ratio = 0.53 (95% CI upper bound 0.68);
in-sample filtered R2 = 0.043 vs smoothed 0.085.
`[FULL-TEXT, p.23, Adrian-Crump-Moench 2013]` Average monthly CP-factor-replication R2 = 7.5%
under GSW data (10-lag forward specification).
`[FULL-TEXT, p.29-30, Bauer & Hamilton 2018]` PC4/PC5 in-sample MSE improvement −11% vs. true-OOS
MSE deterioration +21%.
`[FULL-TEXT, p.20, Sarno-Schneider-Wagner 2016]` Up to 3.5% p.a. certainty-equivalent premium
(switching estimation method, latent-factor model, 1y horizon) — NOT a premium over the EH, which
mostly fails OOS (13/25 combinations positive).
`[FULL-TEXT, p.11, Ghysels-Horan-Moench 2014]` Yield-only benchmark R2 = 18% (2y) / 19% (5y);
rises to 28%/23% with revised-data macro factor.
`[ABSTRACT]` Hodrick & Tomunen (2018): "fails to beat historical average returns" OOS — direction
confirmed in full text, no specific R2/Sharpe number quoted here because none was extracted as a
single decisive scalar from the sections read.
`[ABSTRACT/UNVERIFIED]` Thornton & Valente (2012): "no systematic economic value" — full paper
inaccessible; treat any more specific number attributed to this paper elsewhere as unverified.

---

## (g) Bibliography

1. Cochrane, J.H. & Piazzesi, M. (2005). "Bond Risk Premia." *American Economic Review* 95(1):
   138-160. DOI: 10.1257/0002828053828581. NBER WP 9178:
   https://www.nber.org/system/files/working_papers/w9178/w9178.pdf . Local:
   `cochrane_piazzesi_2005_nber_w9178.pdf`. Version read: NBER WP (Sept. 2002). Retrieved
   2026-09-27.
2. Cochrane, J.H. & Piazzesi, M. (2005). Online Appendix to "Bond Risk Premia."
   https://web.stanford.edu/~piazzesi/cpapp.pdf . Local: `cochrane_piazzesi_2005_appendix.pdf`.
   Retrieved 2026-09-27.
3. Cochrane, J.H. & Piazzesi, M. (2008). "Decomposing the Yield Curve." Working paper, March 13,
   2008 (SSRN 1333274; presented AFA 2010). https://johnhcochrane.com/s/interest_rate_revised.pdf .
   Local: `cp_decomposing_2008_final.pdf`. Retrieved 2026-09-27.
4. Fama, E.F. & Bliss, R.R. (1987). "The Information in Long-Maturity Forward Rates." *American
   Economic Review* 77(4): 680-692. PDF (scanned, not text-extractable):
   http://marshallinside.usc.edu/dietrich/aer-1987-fama-bliss-infofwdrates.pdf . Local:
   `fama_bliss_1987.pdf`. Retrieved 2026-09-27.
5. Campbell, J.Y. & Shiller, R.J. (1991). "Yield Spreads and Interest Rate Movements: A Bird's Eye
   View." *Review of Economic Studies* 58(3): 495-514. DOI (JSTOR) 10.2307/2298008.
   http://gyanresearch.wdfiles.com/local--files/alpha/Campbell-Shiller.pdf . Local:
   `campbell_shiller_1991.pdf`. Retrieved 2026-09-27.
6. Thornton, D.L. & Valente, G. (2012). "Out-of-Sample Predictions of Bond Excess Returns and
   Forward Rates: An Asset Allocation Perspective." *Review of Financial Studies* 25(10):
   3141-3168. DOI: 10.1093/rfs/hhs069. Abstract only:
   https://academic.oup.com/rfs/article-abstract/25/10/3141/1573606 ; SSRN 1687953
   (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1687953, HTTP 403). No local file (full
   text not obtained). Retrieved 2026-09-27.
7. Duffee, G.R. (2011). "Information in (and Not in) the Term Structure." *Review of Financial
   Studies* 24(9): 2895-2934. http://www.econ2.jhu.edu/people/duffee/duffeeInfoInAndNotIn2011.pdf .
   Local: `duffee_2011_info_in_and_not_in.pdf`. Retrieved 2026-09-27.
8. Adrian, T., Crump, R.K. & Moench, E. (2013). "Pricing the Term Structure with Linear
   Regressions." *Journal of Financial Economics* 110(1): 110-138. DOI:
   10.1016/j.jfineco.2013.04.009. NY Fed Staff Report 340:
   https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr340.pdf . Local:
   `adrian_crump_moench_2013_sr340.pdf`. Retrieved 2026-09-27.
9. Bauer, M.D. & Hamilton, J.D. (2018). "Robust Bond Risk Premia." *Review of Financial Studies*
   31(2): 399-448. DOI: 10.1093/rfs/hhx096. https://econweb.ucsd.edu/~jhamilto/bh_robust.pdf .
   Local: `bauer_hamilton_2018_robust.pdf`. Retrieved 2026-09-27.
10. Sarno, L., Schneider, P. & Wagner, C. (2016). "The Economic Value of Predicting Bond Risk
    Premia." *Journal of Empirical Finance* 37: 247-267. DOI: 10.1016/j.jempfin.2016.02.001.
    https://research-api.cbs.dk/ws/files/45007490/christian_wagner_the_economic_value_postprint.pdf
    . Local: `sarno_schneider_wagner_2016_postprint.pdf`. Retrieved 2026-09-27.
11. Ghysels, E., Horan, C. & Moench, E. (2018, published; working paper 2012/rev. 2014).
    "Forecasting through the Rearview Mirror: Data Revisions and Bond Return Predictability."
    *Review of Financial Studies* 31(2): 678-714. NY Fed Staff Report 581:
    https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr581.pdf . Local:
    `ghysels_horan_moench_2014_sr581.pdf`. Retrieved 2026-09-27.
12. Hodrick, R.J. & Tomunen, T. (2018). "Taking the Cochrane-Piazzesi Term Structure Model Out of
    Sample: More Data, Additional Currencies, and FX Implications." NBER Working Paper 25092.
    https://www.nber.org/system/files/working_papers/w25092/w25092.pdf . Local:
    `taking_cp_oos_w25092.pdf`. Retrieved 2026-09-27.
13. Liu, Y. & Wu, J.C. (2021). "Reconstructing the Yield Curve." *Journal of Financial Economics*
    142(3): 1395-1425. DOI: 10.1016/j.jfineco.2021.05.059. NBER WP 27266:
    https://www.nber.org/system/files/working_papers/w27266/w27266.pdf . Local:
    `liu_wu_2021_nber_w27266.pdf`. Retrieved 2026-09-27.
14. Thornton, D.L. (2015 draft). "Understanding the Predictability of Excess Returns" (solo-authored
    working paper, distinct from item 6; cited here only for supporting discussion of the
    measurement-error/in-sample-fit critique of Fama-Bliss and Cochrane-Piazzesi).
    https://belkcollegeofbusiness.charlotte.edu/economicsseminar/wp-content/uploads/sites/885/2012/10/Thornton.pdf
    . Local: `thornton_valente_2012_belk_seminar.pdf`. Retrieved 2026-09-27.

All PDFs archived under `reports/phase11c/raw/literature/` (git-ignored per repository policy);
bibliographic index also appended to `reports/phase11c/raw/literature/SOURCES.txt`.
