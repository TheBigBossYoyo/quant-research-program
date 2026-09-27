# Phase 11C — D2: GSW / ACM / Fama-Bliss / Liu-Wu Point-in-Time Data Audit

Scope: Stage-0 documentation-only audit for a prospective U.S. Treasury yield-curve duration-timing branch. No yield, term-premium, or return VALUES were downloaded, opened, or inspected. Only official documentation pages, a methodology paper (fetched but not content-extracted), author pages, and Wayback CDX metadata (attempted, blocked by an outage) were consulted. Today's date: 2026-09-27. All facts below are tagged by source reliability.

---

## A. Gürkaynak–Sack–Wright (GSW) Fed nominal yield curve

### A1. What is published, coverage, frequency, current update practice
[OFFICIAL, federalreserve.gov/data/nominal-yield-curve.htm, retrieved 2026-09-27]: The Fed publishes "daily estimated nominal yield curve parameters, and smoothed yields on hypothetical Treasury securities," in CSV and HTML, spanning **1961 to present**. The Board uses the **Nelson–Siegel** functional form for **1961–1979** and the six-parameter **Svensson** form from **1980 onward** (more long-maturity securities became available over time, which is why the richer Svensson form was only usable later — see A2). The curve is fit to **off-the-run** Treasury coupon securities, **excluding bills, floating-rate notes, and highly liquid on-the-run issues**. Update cadence: **approximately weekly, data typically posted on Tuesdays**, covering the prior week through the preceding Friday (i.e., roughly a 1–4 business-day publication lag depending on weekday).

[SECONDARY, WebSearch corroboration]: GSW "excluded all bills and those coupon securities with less than three months of remaining maturity from the estimation" — consistent with the official page's on/off-the-run and bill-exclusion description.

Series names (SVENYxx zero-coupon par-equivalent yields, SVENPYxx par yields, SVENFxx instantaneous forwards, SVEN1Fxx one-year-ahead forwards, BETA0/BETA1/BETA2/TAU1/TAU2 Svensson parameters) are the standard published column names on the current feds200628.csv file per the Fed's data dictionary and are referenced consistently across secondary sources (finsets summary lists BETA0–3 and SVENY1–30); I was not able to independently re-derive the exact full column list from the paper PDF itself because WebFetch could not decode the PDF's binary/compressed text stream — this is marked **[UNVERIFIED — exact column list beyond what the official page's HTML table already shows]**, though the standard names above are widely and consistently used in the literature and by the Fed's own page.

**Maturity coverage by start date**: **[UNVERIFIED]** — I could not obtain an explicit official statement of the exact year long maturities (20y, 30y) become available (candidates suggested by general familiarity with the series are ~1971 for ~20y and ~1985 for 30y, matching when the 20-year and 30-year Treasury bond programs existed/reopened), but no official-page or paper-abstract text fetched in this audit confirmed these specific cutoffs verbatim. Do not rely on this without a follow-up read of the paper's tables (methodology-only, not data values, so a future session could safely quote the paper's own maturity-availability table without violating the hard rules).

### A2. Historical publication practice
[SECONDARY, WebSearch]: The daily CSV/HTML file at its current URL (`federalreserve.gov/data/yield-curve-tables/feds200628.csv`) was updated weekly at least as far back as **November 5, 2019**, when the page's *location* changed (see A3). Whether public daily posting existed continuously back to the original 2006 FEDS paper's release could not be confirmed from documentation alone in this session; this predates readily surfaced web documentation and is **[UNVERIFIED]** absent Wayback capture history (blocked — see D2_snapshots/INDEX.md).

### A3. The "current vintage ≠ original GSW data" note
[OFFICIAL, federalreserve.gov/data/nominal-yield-curve.htm, retrieved 2026-09-27] — exact quote captured: **"The current vintage data are generally pretty close to the original Gurkaynak, Sack, and Wright data, but they are not identical, as small modifications have been made over time in the way these models are implemented."** The same page adds the standard disclaimer that this is **"a staff research product and not an official statistical release"**, subject to **"delay, revision, or methodological changes without advance notice."**

Date of change: [SECONDARY, WebSearch corroborated by the still-live legacy URL] — **November 5, 2019** is the date the data's *location* moved (old files remained at a legacy path, e.g. `federalreserve.gov/data/yield-curve-tables/feds200628_1.html`, which is **still live** as of 2026-09-27 and was fetched in this audit). I could not obtain an explicit, itemized official list of *what* changed (e.g., specific security-filter or bill/note exclusion-rule changes) beyond the generic "small modifications... in the way these models are implemented" language — the exact enumerated change-list, if published, is likely inside the paper PDF or a FEDS Note not surfaced by search in this session. **Classify this specific sub-fact as [UNVERIFIED — magnitude/itemization of the 2019 change]**; the *existence* of the note and the *fact that a pre-change vintage URL persists* are OFFICIAL and confirmed.

No quantification of revision magnitude (e.g., "average difference of X bp") was found in the fetched official pages; **[UNVERIFIED]**.

### A4. Reconstructing historical vintages via Wayback Machine
**BLOCKED THIS SESSION BY INFRASTRUCTURE OUTAGE**, not by the hard rules. 9 attempts to query the Wayback CDX API (`web.archive.org/cdx/search/cdx?url=federalreserve.gov/data/yield-curve-tables/feds200628.csv&output=json&fl=timestamp,digest,length`) over ~6 minutes on 2026-09-27 returned HTTP 503 "Internet Archive: Temporarily Offline" in 7/9 attempts, one connection failure (HTTP 000), and one anomalous HTTP 200 with an empty result for a differently-shaped query (inconclusive, not a real zero-count). archive.org's own homepage returned HTTP 200 at the same time, so this is a backend (CDX/Wayback) outage, not a total site outage. Full log in `reports/phase11c/raw/sources/D2_snapshots/INDEX.md`. **No content was downloaded from any capture** — only the metadata-listing API was targeted, per the hard rules, and even that failed for infrastructure reasons.

Because of this, question A4 (distinct captures per year, distinct digests, whether weekly vintages are archivable) is **[UNVERIFIED — retry needed in a later session once the Wayback CDX API is confirmed reachable]**. This is an operational gap, not evidence against archivability — the Fed page itself has existed at a stable URL since well before 2019 and is the kind of page the Wayback Machine crawls routinely, so a priori PIT_RECONSTRUCTABLE is plausible but not yet demonstrated.

### A5. Day-independent fitting and PIT implications
[SECONDARY, WebSearch, corroborating well-established methodological description]: GSW fit the Svensson (or restricted Nelson-Siegel pre-1980) curve **cross-sectionally, independently each day**, using only that day's outstanding, actively-traded, filtered set of Treasury securities' prices — there is no smoothing across time and no use of future days' prices in a given day's fit. This means the *economic estimation* for a given historical date does not use look-ahead information from later dates.

**Implication for PIT status**: the *day-by-day fitting procedure itself* is causal/PIT-safe in the sense that day t's curve uses only day-t inputs. However, the *file currently served* reflects the *current* implementation of that fitting procedure (bond filters, optimization settings, numerical implementation), which the Fed has explicitly stated has been "modified... in the way these models are implemented" over time (A3). So a backtest that pulls "history" from today's file is not exposed to look-ahead in the return-generating sense, but it IS exposed to **methodology-revision risk**: the curve value the Fed reports today for, say, 2015-03-02 may differ slightly from what a filter/estimation vintage in use in 2015 would have produced or reported. This is a **research-integrity/reproducibility risk**, not a classic look-ahead-into-the-future risk, but it can still matter for precise backtests (e.g., regime-dependent duration timing sensitive to small curve differences) and for anyone trying to reproduce a paper's exact historical GSW-based signal.

### A6. Smoothing and the Cochrane-Piazzesi tent shape
[SECONDARY, WebSearch]: The Cochrane-Piazzesi (CP) "tent-shaped" single factor is constructed from **unsmoothed** forward rates (Fama-Bliss) and predicts one-to-five-year excess bond returns with R² up to ~0.44 in the original CP framework. A more recent (2025) paper revisits this and argues the tent shape *per se* and the specific 4y–5y spread are not what drives predictive power; instead it is the cointegrating relationship among the near-unit-root forward rates. I did **not** find an explicit GSW-authored or Fed-official statement that Svensson smoothing specifically destroys the CP signal, nor a direct Liu-Wu (2021) quantitative comparison statement in the pages actually fetched this session. This should be treated as **[UNVERIFIED — precise GSW/Liu-Wu quantitative statement not directly retrieved]**, though it is consistent with the general, widely-cited concern in the term-structure literature that a smooth parametric curve (Svensson, only 6 free parameters per day) mechanically cannot reproduce the higher-frequency-across-maturity variation (the "tent" bumps) that an unsmoothed curve (Fama-Bliss, Liu-Wu) can, by construction of the model class itself (a 6-parameter Svensson curve is smooth in maturity by design, so any factor requiring maturity-local curvature beyond what 6 parameters can span is necessarily attenuated or absent). This mechanical argument is a priori/structural, not a cited empirical finding from this session's fetches.

### GSW classification
**PIT_RECONSTRUCTABLE (day-level fit is causal), with MINOR_REVISION_RISK (documented but unquantified methodology drift in the currently-served historical file), and vintage-archivability UNVERIFIED this session (Wayback outage).**

Reasons: (a) daily cross-sectional fitting means no look-ahead in the core estimation; (b) Fed explicitly documents current-vintage ≠ original-vintage differences without magnitude; (c) a legacy pre-Nov-2019 vintage URL persists and is live, suggesting genuine historical vintages may be directly obtainable from the Fed itself (not just Wayback) — this is actually a **stronger** reconstruction path than Wayback and should be pursued first in a follow-up session; (d) Wayback-based reconstruction is neither confirmed nor ruled out (retry needed).

---

## B. New York Fed ACM Treasury term premia (and Kim-Wright comparator)

[OFFICIAL, newyorkfed.org/research/data_indicators/term-premia-tabs, retrieved 2026-09-27]: fetch returned only a navigation stub; the target technical content did not surface in the extracted text.

[SECONDARY, WebSearch, corroborated across Liberty Street Economics and FRB Board pages]: ACM covers maturities **1–10 years**, daily frequency, back to **June 14, 1961**, from a five-factor no-arbitrage term-structure model (Adrian, Crump, Moench 2013). Update practice: **the series is updated (end-of-month observations posted monthly per one source; the NY Fed's own tabs page is also described as updating daily)** — sources are not perfectly consistent on daily-vs-monthly cadence, but they agree on the decisive point: **"the model is re-estimated periodically, which can lead to small revisions in historical values when new sample periods are added."** This directly answers the question: ACM is a **full-sample-refit model**, so **historical estimates for a given date DO change over time** as more recent data is appended and the model is re-run.

**Distinguishing "series dated 2005" from "estimate available in 2005"**: because ACM (and Kim-Wright) are re-estimated on the whole sample each update, **the term-premium value the NY Fed reports today for, e.g., 2005-06-01 is not necessarily the same number that would have been reported by the model as configured/estimated in 2005.** A researcher must not treat a currently-downloaded historical ACM series as if it were point-in-time information available to a trader on that historical date — it reflects today's re-estimated model applied backward. This is a materially different (weaker) PIT status than GSW's day-independent fit.

**Kim-Wright comparator** [SECONDARY, WebSearch, Fed Board page + FEDS note "Robustness of long-maturity term premium estimates"]: Kim-Wright is also a latent-factor no-arbitrage model (using Kim-Orphanides methodology, incorporating Blue Chip survey expectations), published on FRED and the Board's site, updated on the same roughly-weekly Tuesday cadence as other Board yield-curve products. As a re-estimated dynamic term-structure model it shares the same full-sample re-estimation vintage problem as ACM — historical Kim-Wright values are also subject to revision when re-estimated.

Wayback CDX capture counts for ACM/Kim-Wright data files: **not obtained (same outage as A4)**.

### ACM/Kim-Wright classification
**PIT_BLOCKED for naive use of "historical series as downloaded today."** Reasons: model is fit on the full sample and periodically re-estimated; historical values are explicitly stated to be revised; there is no confirmed archived-vintage mechanism (Wayback blocked this session); unlike GSW, there is no day-independent-fit property to fall back on — the entire estimated curve/premium history moves when the model updates. Any duration-timing signal built on ACM/Kim-Wright term premia needs either (a) genuine historical vintage files (not currently confirmed to exist publicly) or (b) an explicit acknowledgment that the backtest is not strictly PIT and a sensitivity/robustness check against this revision risk.

---

## C. Fama–Bliss (CRSP) and Liu–Wu (2021 JFE) free alternative

[SECONDARY, WebSearch, crsp.org / crsp.com pages]: **Fama-Bliss Discount Bonds** are a **supplemental file inside the CRSP US Treasury Database**, requiring a **CRSP/WRDS institutional licence**; no explicit individual-researcher price list surfaced. WRDS is reported (per search result) to generally sell **annual contracts only**; a faculty/PhD researcher without an existing subscription is advised to contact WRDS support for a trial/sample/pricing quote, or to contact CRSP/Morningstar Indexes directly (CRSP was acquired by Morningstar as of 2/2/2026) for a one-time custom data-pull quote, which is described as "typically more cost effective than an annual contract" for narrow one-off needs. **No free redistribution of Fama-Bliss discount-bond data was found.** **[UNVERIFIED — exact $ figures]**, since no price list was located; this should be treated as a **cost/access blocker requiring either an institutional affiliation or a paid one-time quote**, consistent with typical CRSP/WRDS practice.

[OFFICIAL, sites.google.com/view/jingcynthiawu/yield-data, retrieved 2026-09-27]: **Liu-Wu (2021, JFE) zero-coupon yields** are **free**, hosted on the author's (Jing Cynthia Wu) own site via downloadable Google Sheets, at **both monthly and daily frequency**, spanning **1961–2025** (i.e., maintained and updated online, current as of at least 2025), maturities **1 to 360 months** (1 month to 30 years). The page does not state update cadence explicitly, nor whether historical values are revised on update, nor the precise input-data lineage on the page itself (though the underlying JFE paper is understood — from the paper's own framing, corroborated by search results — to use CRSP Treasury data as its raw input, with a non-parametric adaptive-bandwidth kernel-smoothing method, distinct from Fama-Bliss's own filtering and distinct from GSW's global 6-parameter Svensson form). Whether Liu-Wu revises past-dated values when new data is appended is **[UNVERIFIED]** — this needs a direct look at the site's changelog/version notes (methodology/documentation, not data values, so permissible in a follow-up) before relying on it as strictly PIT.

No other confirmed **free unsmoothed** zero-coupon curve source was identified in this session beyond Liu-Wu.

### C classification
- **Fama-Bliss/CRSP: PIT_BLOCKED for this project** absent an institutional CRSP/WRDS licence or a paid one-time quote — an access/cost blocker, not a data-quality problem. If accessible, it would likely be close to PIT_SAFE for the historical values themselves (CRSP methodology is generally static/documented per vintage), but this was not independently confirmed this session.
- **Liu-Wu: PIT_RECONSTRUCTABLE / free**, but revision behavior on update is **[UNVERIFIED]** — treat as MINOR_REVISION_RISK until confirmed otherwise.

---

## D. Can the CP forward-rate factor be built from free PIT data?

| Source | Exactness of CP construction | Access | Verdict |
|---|---|---|---|
| Fama-Bliss (CRSP) | **Exact** — this is the data CP (2005) itself used; 1–5y one-year-ahead forwards computed directly from the same discount-bond construction. | Licensed (WRDS/CRSP), cost unconfirmed, no free redistribution found. | Not free; exact if obtained. |
| Liu-Wu (2021 JFE) | **Close but not identical** — different (kernel, adaptive-bandwidth) unsmoothed/near-unsmoothed construction from CRSP inputs; monthly/daily 1–360 month maturities allow computing the needed 1..5y one-year forwards directly, but numerically will not exactly reproduce Fama-Bliss/CP's original values because the curve-fitting method differs. | Free (author's site). | Best free approximation; economically should behave similarly to CP's original tent factor, but not bit-for-bit identical — must be validated empirically before assuming equivalence. |
| GSW (Fed) | **Different construction** — global 6-parameter Svensson smoothing is structurally too smooth to recover the maturity-local "tent" curvature CP relies on; forwards from GSW are a materially different (more smoothed) object than the CP factor's inputs. | Free (Fed). | Free but likely a degraded/attenuated version of the CP signal — not a faithful substitute without separate validation. |
| H.15 par yields, bootstrapped | **Approximate, model-dependent** — H.15 gives only a sparse set of on-the-run par yields at standard tenors; converting to zero-coupon/forward rates requires an added bootstrapping/interpolation model, introducing another layer of assumptions on top of already-sparse inputs. | Free (Fed H.15). | Weakest / most assumption-laden route; only useful as a last resort or cross-check. |

---

## PIT classification summary table

| Source | What | Coverage | Revisions | Vintages available? | Classification | Reasons |
|---|---|---|---|---|---|---|
| GSW (Fed nominal yield curve) | Zero/par yields, forwards, Svensson params | 1961–present, daily | "Not identical" to original GSW, undated/unquantified "small modifications"; change of file location Nov 5 2019 | Legacy pre-2019 URL still live (OFFICIAL); Wayback CDX blocked this session (outage, unverified) | **PIT_RECONSTRUCTABLE / MINOR_REVISION_RISK** | Day-independent cross-sectional fit is causal; but currently-served history reflects present-day implementation, with an official but unquantified revision-risk disclosure |
| ACM term premia (NY Fed) | Term premium, 1–10y | 1961–present | Full-sample model, re-estimated periodically; historical values explicitly revised | Not confirmed | **PIT_BLOCKED** (for naive historical use) | Whole-history re-estimation on each update; "2005 series value" ≠ "2005 estimate" |
| Kim-Wright (Fed Board) | Term premium | ~1990–present (model est. sample) | Same re-estimation issue as ACM | Not confirmed | **PIT_BLOCKED** (comparator, same reasoning) | Latent-factor model refit over time |
| Fama-Bliss (CRSP) | Discount bonds, 1–5y | Long historical, monthly | Not established this session | Licensed, no free version found | **PIT_BLOCKED (access)**, data-quality otherwise likely PIT_SAFE if licensed | CRSP/WRDS paywall; cost unconfirmed |
| Liu-Wu (2021 JFE) | Zero-coupon, 1–360mo | 1961–2025, monthly/daily | Unconfirmed | Free, author-hosted | **PIT_RECONSTRUCTABLE**, revision behavior UNVERIFIED | Free, close-to-unsmoothed, CRSP-derived; update/revision practice not documented on the page itself |

## Wayback CDX capture-count table
| URL queried | Captures per year | Distinct digests | Status |
|---|---|---|---|
| federalreserve.gov/data/yield-curve-tables/feds200628.csv | N/A | N/A | **BLOCKED — Wayback CDX API returned HTTP 503 "Temporarily Offline" in 7/9 attempts, 1 connection failure, 1 inconclusive empty 200, over 2026-09-27; retry in a future session** |
| federalreserve.gov/econresdata/researchdata/feds200628.csv (legacy) | N/A | N/A | Same outage, not queried successfully |
| ACM / Kim-Wright data files | N/A | N/A | Not attempted (CDX already down) |

---

## Bibliography (URL, tag, retrieval date)
- https://www.federalreserve.gov/data/nominal-yield-curve.htm — OFFICIAL — 2026-09-27
- https://www.federalreserve.gov/data/yield-curve-tables/feds200628_1.html — OFFICIAL (legacy vintage page, still live) — 2026-09-27
- https://www.federalreserve.gov/pubs/feds/2006/200628/200628abs.html — OFFICIAL — 2026-09-27
- https://www.federalreserve.gov/econres/feds/the-us-treasury-yield-curve-1961-to-the-present.htm — OFFICIAL — 2026-09-27
- https://www.federalreserve.gov/data/yield-curve-models.htm — OFFICIAL — 2026-09-27
- https://www.federalreserve.gov/pubs/feds/2006/200628/200628pap.pdf — OFFICIAL (fetched, not text-extractable via WebFetch this session) — 2026-09-27
- https://www.federalreserve.gov/econresdata/researchdata/feds200628.html — OFFICIAL — HTTP 404 (retired URL) — 2026-09-27
- https://www.newyorkfed.org/research/data_indicators/term-premia-tabs — OFFICIAL (thin extraction) — 2026-09-27
- https://libertystreeteconomics.newyorkfed.org/2014/05/treasury-term-premia-1961-present/ — OFFICIAL (Fed blog) — SECONDARY-corroborated, via WebSearch — 2026-09-27
- https://www.federalreserve.gov/econres/notes/feds-notes/robustness-of-long-maturity-term-premium-estimates-20170403.html — OFFICIAL — via WebSearch — 2026-09-27
- https://sites.google.com/view/jingcynthiawu/yield-data — OFFICIAL (author's site) — 2026-09-27
- https://www.nber.org/papers/w27266 (Liu & Wu, "Reconstructing the Yield Curve") — PAPER — via WebSearch — 2026-09-27
- https://ionmihai.github.io/finsets/02_papers/gurkaynak_etal_2007.html — SECONDARY — 2026-09-27
- https://www.crsp.org/research/crsp-us-treasury-database/ ; https://www.crsp.com/products/documentation/fama-bliss-discount-bonds-–-monthly-only — OFFICIAL (vendor docs) — via WebSearch — 2026-09-27
- Cochrane-Piazzesi (2005) "Bond Risk Premia," NBER w9178 / johnhcochrane.com/cochrane_piazzesi_bond_risk_premia.pdf — PAPER — via WebSearch — 2026-09-27
- ScienceDirect (2025), "Why does the Cochrane–Piazzesi model predict treasury returns?" — PAPER (secondary re-analysis) — via WebSearch — 2026-09-27
- Wayback Machine CDX API, web.archive.org/cdx/search/cdx — attempted 2026-09-27, blocked by service outage (see D2_snapshots/INDEX.md for full log)
