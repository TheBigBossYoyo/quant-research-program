# L1 — Network Activity / "Blockchain Fundamentals" Literature Audit

Phase 11B, Stage 0. Literature + data audit only — **no price/return/OHLCV/market-cap data was downloaded,
read, or computed on for this report.** All statistics below are numbers *reported inside papers*, transcribed
from the PDF text (and, where flagged, from PDF word coordinates for multi-column tables). Date of audit:
2026-09-26.

## How to read this document

Each paper gets a fields table with columns 1–12 as specified in the task, then a short discussion of the key
statistic(s), its exact table/page location, and a verification tag:

- **VERIFIED_FULLTEXT** — I hold the PDF (in `reports/phase11b/raw/literature/`, git-ignored) and the exact
  table/page is cited.
- **ABSTRACT_ONLY** — I could read only the abstract/summary (paywalled full text), from the publisher page,
  EconPapers/RePEc, or a WebFetch of the abstract page.
- **SECONDARY** — the claim is reported the way another paper in this audit cites/describes it, not from the
  original source directly.

Field legend (columns 1–12 in each table):

| # | Field |
|---|-------|
| 1 | In-sample (IS) or out-of-sample (OOS) |
| 2 | Contemporaneous (C) or genuinely predictive (P) |
| 3 | Exact forecast horizon |
| 4 | Information timestamp of the predictor relative to the return window |
| 5 | Long-short (LS), long-only (LO), or regression-only (RO) |
| 6 | Transaction costs included? |
| 7 | BTC/ETH-only vs. broad altcoin cross-section |
| 8 | Sample period |
| 9 | Any post-2019 evidence? |
| 10 | Proprietary/vendor data needed (which vendor) |
| 11 | Current-entity labels applied historically? |
| 12 | Survives economically meaningful benchmarks (momentum/volume controls, buy-and-hold, historical mean)? |

**Important version-control note established during this audit:** the NBER working-paper PDFs of both
Liu & Tsyvinski and Liu, Tsyvinski & Wu that I was able to download are **early drafts** (Aug-2018 and
Dec-2019 respectively) that materially differ from the final published RFS-2021 / JF-2022 versions. I flag
every claim accordingly — this is exactly the kind of version confusion the task asked me to watch for.

---

## 1. Liu & Tsyvinski (2021), "Risks and Returns of Cryptocurrency," *Review of Financial Studies* 34(6):2689–2727
(NBER Working Paper No. 24877; SSRN 3226952). **This is the critical paper for the whole audit.**

### What I actually hold vs. the published paper

- I downloaded and read in full the **NBER working paper w24877, dated August 2018**
  (`liu_tsyvinski_nber_w24877.pdf`, 68 pp.). Its abstract (p.1) talks only about momentum, investor attention,
  and industry-exposure indices; it does **not** use the phrase "network factors," and it contains exactly
  **one** on-chain variable: Bitcoin Wallet User count, used solely to build a Bitcoin "price-to-dividend"
  ratio (p.4, footnote 2; p.29 §4.4).
- The **published RFS-2021 abstract** (confirmed via WebFetch of the EconPapers/RePEc abstract mirror,
  `econpapers.repec.org/RePEc:oup:rfinst:v:34:y:2021:i:6:p:2689-2727.`, since the OUP page itself is paywalled)
  reads verbatim: *"We establish that cryptocurrency returns are driven and can be predicted by factors that
  are specific to cryptocurrency markets. Cryptocurrency returns are exposed to cryptocurrency network
  factors but not cryptocurrency production factors. We construct the network factors to capture the user
  adoption of cryptocurrencies... Moreover, there is a strong time-series momentum effect, and proxies for
  investor attention strongly forecast future cryptocurrency returns."* — This is **ABSTRACT_ONLY** for the
  final version, but the wording is precise and decisive for the "critical" question: momentum and attention
  are explicitly said to be **"predicted"/"forecast"**; network factors are explicitly said to be
  **"exposed to"** — i.e., the published paper itself draws the same contemporaneous-exposure vs.
  genuinely-predictive distinction the task asks about, and places network factors on the "exposure" side.
- Independent confirmation (**SECONDARY**, via Cong, Karolyi, Tang & Zhao, EFMA-2022 draft, p.5 — full text
  held, see paper 4 below): *"Liu and Tsyvinski (2021) show that returns of the index of cryptocurrencies
  they construct are significantly predicted by momentum and investor attention, not valuation ratios, while
  being exposed to a network growth factor, but not common factors, from other asset markets."* This
  independently corroborates the "predicted by momentum/attention" vs. "exposed to network factor" split, and
  explicitly states that **valuation ratios (which is exactly what the Bitcoin-wallet-user "price-to-dividend"
  ratio is) do NOT predict returns.**
- Also SECONDARY (same source, p.6): *"Liu and Tsyvinski (2021) and Bhambhwani, Delikouras and Korniotis
  (2022) use the growth of fundamental indicators, such as the number of addresses of Bitcoin ... to measure
  the network effect directly"* — i.e., the published network factor is constructed as a **growth-rate /
  factor-mimicking-portfolio exposure test** (a Fama-French-style time-series regression of returns on a
  contemporaneously-dated network-growth factor), not a lagged forecasting regression.

### Field table

| Predictor | (1) | (2) | (3) Horizon | (4) Info timestamp | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmarks | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bitcoin Wallet User count, as price-to-"dividend" ratio | IS | P (tested as predictive; result negative) | Daily, t+1…t+7 | Ratio known at close of day t, used to predict t+1..t+7 | RO | No | BTC only | 2011-01-01 to 2018-05-31 | No (ends 2018) | blockchain.info (free) | N/A (no entity classification needed for wallet counts) | No — R²≈0.00 at every horizon | Table 30, p.29 of NBER w24877: coefficients on lagged Bitcoin P/D ratio for R(t+1)…R(t+7): 0.13, 0.05, −0.13, −0.12, 0.05, 0.09, 0.05 (t-stats 1.34, 0.49, −1.36, −1.25, 0.57, 0.99, 0.55); R²=0.00 all seven columns | NOT_PREDICTIVE_TEST | **VERIFIED_FULLTEXT** (2018 draft) |
| "Network factors" (wallet users/active addresses/transaction count/payment count growth) as **contemporaneous exposures** in the published model | IS (full sample used for factor construction and loadings) | **C** (abstract explicitly separates this from the "predicted" momentum/attention factors) | N/A — contemporaneous factor-loading regression, not a forecast horizon | Same-period (network-factor value/return dated same period as the cryptocurrency return it explains) | Regression-only / factor-exposure test (β on a constructed factor), not a trading strategy | Not applicable (no trading strategy is proposed for this factor) | BTC (primary), some ETH/XRP | Not disclosed in the abstract; the 2018 draft's BTC sample runs to 2018-05-31, so ≥2018 for the earliest network-factor version, final published version could extend further (undated in what I could access) | Unverified from what I could access (RFS published version paywalled) | Unclear/likely blockchain.info-style public explorer data (as in the 2018 draft) | N/A | Not a "beats buy-and-hold" question — it is a risk-exposure claim, not a trading claim | RFS-2021 published abstract (EconPapers mirror); Cong et al. (2022 EFMA draft) pp.5–6 | CONTEMPORANEOUS / MIXED (task's own framing: this is the "priced exposure, not forecast" case) | **ABSTRACT_ONLY** (own abstract) + **SECONDARY** (Cong et al. description) |

**Bottom line on the "critical" question:** based on the primary abstract's own wording and an independent
paper's paraphrase, Liu & Tsyvinski's published "network factors" are used as **contemporaneous risk exposures
in a factor-pricing sense** (cryptocurrency returns load on a network-growth factor, analogous to a market-beta
test), **not** as lagged return-forecasting variables. The one place in the paper I could fully verify where a
network-derived (wallet-user) variable *was* used in a genuinely predictive regression — the Bitcoin
price-to-"dividend" ratio — **failed** to predict returns at any of seven daily horizons (R²≈0.00 throughout,
Table 30). I was not able to obtain the RFS-2021 full text (Oxford Academic is paywalled and SSRN blocks
scripted downloads with a 403), so I cannot report the exact updated table numbers for the multi-variable
network factor (active addresses, transaction count, payment count growth) in the published version; anything
about that fuller variable set here is ABSTRACT_ONLY/SECONDARY, not VERIFIED_FULLTEXT.

---

## 2. Yae & Tian (2022), "Out-of-sample forecasting of cryptocurrency returns: A comprehensive comparison of predictors and algorithms," *Physica A* 598:127379

I could not obtain full text (ScienceDirect returns HTTP 403 to both direct download and WebFetch; no open
working-paper mirror located under this title — the SSRN entry found in search, "Sequential Learning, Asset
Allocation, and Bitcoin Returns" by the same authors, doi 10.2139/ssrn.3896611, appears to be a **different**
paper and I have not verified it is a preprint of this one). Everything below is **ABSTRACT_ONLY / SECONDARY**
(from EconPapers/RePEc listing text and search-engine summaries of the abstract).

| Predictor set | (1) | (2) | (3) Horizon | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmark | Key stat | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Investor attention, trading volume, **network metrics** (unspecified which on-chain series) | **OOS** (explicit rolling/expanding-window OOS design, per title) | P (tested for OOS predictive power) | Not confirmed (likely daily/weekly; unconfirmed) | Not confirmed | RO (R²-based comparison against historical-mean benchmark; unconfirmed whether a trading strategy is also built) | Not confirmed | BTC, ETH, XRP only (per secondary description) | Not confirmed exactly; likely ends ~2020–2021 given 2022 publication | Not confirmed | Not confirmed | N/A | **No** — reported headline finding is that "well-known in-sample predictors fail out-of-sample"; only cross-market stock correlation gave modest OOS R² (up to ~2.7% for BTC, ~1.7% ETH, ~2.1% XRP per one secondary source) | EconPapers abstract mirror + search-engine summaries of ScienceDirect abstract | **NOT_PREDICTIVE_TEST** for network metrics specifically (they are named among the predictors that fail OOS) | **SECONDARY / ABSTRACT_ONLY** |

This paper is directly on point for the task's core question (do on-chain/network predictors survive OOS) and
its headline message — that a comprehensive, honestly-run OOS test finds in-sample network/volume/attention
predictors do **not** survive, while only a non-network variable (cross-market correlation) gives modest OOS
R² — is an important negative data point. I flag it as SECONDARY/ABSTRACT_ONLY because I have not verified the
exact numbers against the primary text and cannot confirm exactly which on-chain series were tested or their
individual OOS R² (as opposed to the winning non-network predictor's R²).

---

## 3. Bhambhwani, Delikouras & Korniotis, "Blockchain characteristics and cryptocurrency returns," *Journal of International Financial Markets, Institutions and Money* (2023); earlier CEPR DP13724 (2019), "Blockchain Characteristics and the Cross-Section of Cryptocurrency Returns"

Full text is paywalled on ScienceDirect (403) and the CEPR/SSRN PDFs could not be retrieved by script (SSRN
returns 403 to automated downloads; the CEPR publication page for DP13724 returned 404 on WebFetch). Everything
below is **ABSTRACT_ONLY/SECONDARY**.

| Predictor | (1) | (2) | (3) | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) | Key stat | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Network size (user adoption/usage proxy) | Not confirmed, likely IS full-sample factor-pricing test (SDF-style) | **C** — described as a "risk exposure" priced factor, not a forecast | N/A (asset-pricing/SDF test, not a forecast horizon) | Same-period | RO (stochastic-discount-factor / two-pass cross-sectional test), not obviously a trading strategy in the abstract | Not confirmed | Per Cong et al.'s description (SECONDARY, see paper 4): "the ten-coin sample in Bhambhwani, Delikouras and Korniotis (2022)" — i.e. **ten major coins**, not a broad altcoin cross-section | CEPR DP first posted 2019; JIFMIM publication 2023 | Not confirmed (JIFMIM 2023 publication implies the analysis window could reach into 2020s, unconfirmed) | Not confirmed (likely public block-explorer aggregates, e.g. blockchain.info-style address counts, per the "growth of ... addresses" description) | N/A | Abstract claims aggregate network+computing-power factors "explain expected cryptocurrency returns at least as well as models with return-based factors (market, size, momentum)" — a relative, not absolute, benchmark claim | Publisher/SSRN abstract via WebSearch summaries; corroborated description in Cong et al. (2022 EFMA draft), p.6: "Liu and Tsyvinski (2021) and Bhambhwani, Delikouras and Korniotis (2022) use the growth of fundamental indicators, such as the number of addresses of Bitcoin and of ten cryptocurrencies, to measure the network effect directly" | **CONTEMPORANEOUS / MIXED** (a priced-exposure claim, structurally analogous to Liu & Tsyvinski's network factor, not a genuine forecasting claim) | **ABSTRACT_ONLY + SECONDARY** |
| Computing power (hash rate / mining cost proxy) | Same as above | **C** | N/A | Same-period | RO | Not confirmed | Ten-coin sample | Same as above | Not confirmed | Not confirmed | N/A | Same relative claim as above | Same sources | CONTEMPORANEOUS / MIXED | ABSTRACT_ONLY + SECONDARY |

Note: two distinct SSRN IDs exist for what appears to be the same underlying research at different stages
(3342842 "Blockchain Characteristics and Cryptocurrency Returns"; 3387313 "Blockchain Characteristics and the
Cross-Section of Cryptocurrency Returns"), plus the CEPR DP13724 working-paper version (2019) and the
JIFMIM-2023 published version — a version history I could not fully reconcile without full text. I did **not**
verify the "computing power" claim represents a genuinely predictive test at any point; every description I
found (including the authors' own framing, secondhand) is consistent with a contemporaneous asset-pricing
(SDF/beta) exercise, structurally identical to Liu & Tsyvinski's approach.

---

## 4. Cong, Karolyi, Tang & Zhao, "Value Premium, Network Adoption, and Factor Pricing of Crypto Assets" (working paper)

**VERIFIED_FULLTEXT.** I hold the EFMA-2022 conference full-paper draft
(`cong_karolyi_tang_zhao_efma2022.pdf`, 65 pp., dated question-full-paper ID 231, EFMA 2022 Rome meetings).
This is a working paper; I could not confirm whether it has since appeared in a journal, so treat venue as
"working paper, EFMA 2022 draft" and note the possibility of a different final published version.

| Predictor | (1) | (2) | (3) Horizon | (4) Info timestamp | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmark | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NET factor: weekly long-short portfolio sorted on growth rate of "total addresses with balances" | IS (full-sample factor construction/backtest; no train/test split) | **P at 1-week lag** — characteristic measured in "portfolio formation week," return realized in the *following* week (standard Fama–French-style timing; text: p.13, "portfolio formation week... rebalanced weekly") | 1 week ahead | Characteristic known at end of formation week t, applied to week t+1 return | **LS** (top-tercile minus bottom-tercile address-growth portfolio, value-weighted within group) | **Not modeled** — no bid/ask, funding, or slippage in the reported returns (gross factor returns only) | Broad cross-section: "Core Sample" of 616–745 crypto assets (source: intotheblock), vs. "Full Sample" of 4,007 tokens (CoinMarketCap) for the size/value/momentum factors | 2014-01-01 (Full Sample) / 2014-01-22 (Core Sample) to 2021-01-04, weekly (366/363 weeks) | Yes — sample explicitly extends through Jan 2021 | intotheblock (paid on-chain data vendor); CoinMarketCap for prices/market cap | Not addressed — survivorship/relisting of historical addresses under later entity names is not discussed | **Weak** — NET has the *smallest* marginal contribution to the C-5 model's explanatory power among 5 factors (MKT 1.37%, SMB 6.69%, MOM 3.74%, VAL 8.93%, **NET 1.87%**); no cost-adjusted comparison to buy-and-hold reported | Table 6 (mean weekly factor returns, p.13-14 text): NET mean = 3.76%/week, t-stat = 2.82; C-5 model marginal contribution figures, p.5 (in-text, not a numbered table in my extract) | **MIXED** (statistically significant gross long-short spread, but weakest of five factors, no costs, no distinct OOS split) | **VERIFIED_FULLTEXT** |
| "Fundamental-to-market value" (value characteristic, partly network/user-based; only available for Core Sample) | IS | P at 1-week lag (same construction) | 1 week | Same-week-ahead as NET | LS | Not modeled | Core Sample (616 coins) | 2014–2021 | Yes | intotheblock | Not addressed | Long-short spread 5.7%/week (t=2.71), monotonic decile pattern — one of the strongest single-sort results in the paper, but this is the **value**, not pure activity, characteristic | Table 4, Panel A, p.10 | SUPPORTIVE (value/fundamental characteristic, adjacent to but distinct from pure "activity") | **VERIFIED_FULLTEXT** |
| Price-to-new-address ratio (cited from a companion paper, Liu, Tsyvinski & Wu 2021 draft) | Not stated in Cong et al.'s footnote | **P** (footnote text: "negatively predict future cryptocurrency returns") | Not stated | Not stated | Not stated | Not stated | Not stated | Not stated | 2021 draft cited, so presumably yes | Not stated | Not stated | Not stated | Footnote 11, p.10: *"In a recent study, Liu, Tsyvinski and Wu (2021) find that the price-to-new address ratios negatively predict future cryptocurrency returns."* | **SUPPORTIVE** (genuinely predictive claim, but only as reported secondhand) | **SECONDARY** (I hold the Dec-2019 NBER draft w25882 of this same author team's "Common Risk Factors in Cryptocurrency" paper, and it contains **zero** address/on-chain variables — see paper 9 below — confirming this price-to-new-address result was added in a *later*, 2021 revision I do not have) |

This is the most useful **full-text-verified, genuinely predictive, on-chain-based** long-short result found in
this audit (the NET factor), and it is honestly modest: statistically significant (t=2.82) but the smallest
contributor of five factors to cross-sectional fit, computed gross of costs, on a vendor (intotheblock) data
feed, over a single continuous sample with no held-out test window.

---

## 5. Contradictory / reverse-causality evidence (activity following price)

### 5a. Koutmos (2018), "Bitcoin returns and transaction activity," *Economics Letters* 167:81–85

**ABSTRACT_ONLY/SECONDARY** — Economics Letters is Elsevier-paywalled; ResearchGate blocked the direct PDF
(403); no free working-paper mirror located.

| Predictor | (1) | (2) | (3) | (4) | (5) | (6) | (7) | (8) | (9) | (10) | (11) | (12) | Key stat | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bitcoin transaction-count activity (bivariate VAR/Granger with returns) | IS | **C/bidirectional**, tested via Granger causality | Not confirmed (daily, per typical VAR design in this literature) | N/A — VAR test of lead-lag, not a forecast deployed live | RO | No | BTC only | Not confirmed exactly (2018 publication; likely ~2013–2017) | No | Public blockchain explorer (unconfirmed which) | N/A | N/A — this is a causality test, not a trading test | Search-engine summary of abstract: "evidence of bidirectional linkages between Bitcoin price returns and transaction activity, with the impact of return shocks on transaction activity being larger in magnitude... no evidence that returns can be explained by the change in transaction activity" (bivariate VAR) | **CONTRADICTORY** (returns→activity effect dominates; activity does not explain returns in the bivariate VAR) | **SECONDARY** (search-engine paraphrase of abstract; I could not access the paper directly) |

### 5b. Kristoufek (2015), "What Are the Main Drivers of the Bitcoin Price? Evidence from Wavelet Coherence Analysis," *PLoS ONE* 10(4):e0123923

**VERIFIED_FULLTEXT** (open access; `kristoufek_2015_plosone.pdf`, 15 pp.).

| Predictor | (1) | (2) | (3) | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trade transactions (blockchain tx count, ex-exchange) vs. Bitcoin price, wavelet coherence & phase (leads/lags) | IS (whole-sample, non-stationary wavelet coherence — not a forecast/backtest) | **Mixed — tested for lead-lag direction, not point forecasts** | Not a fixed horizon; coherence analyzed across time-scales | N/A | RO (no portfolio; a leads/lags correlation-in-time-frequency method) | No | BTC only (BTC/USD exchange rate, CoinDesk BPI) | **2011-09-14 to 2014-02-28**, daily | No | Blockchain.info-style public chain data + CoinDesk BPI | N/A | N/A | p.7–8 (§"Transaction drivers," Fig. 3): "for the trade transactions, it is clear that the relationship is positive and that **the transactions lead the price**... However, the effect becomes weaker in time" and loses significance "from 01/2013." Separately (§"Technical drivers," Fig. 3): hash rate and difficulty are positively correlated with price in the long-term, but **"the price leads both relationships"** (mining/computational activity responds to price, not vice versa) | **MIXED**: transactions→price found (weak, decaying, early-sample only) = one of the few genuinely SUPPORTIVE lead-lag results for activity leading price; but hash-rate/difficulty result is **CONTRADICTORY** (price leads mining activity, i.e., reverse causality) | **VERIFIED_FULLTEXT** |

This single paper is directly useful for answering task question (a): it finds **both directions** depending
on which "activity" series is used — trade/transaction counts weakly and decayingly lead price early in the
sample (2011–2013), while hash rate/difficulty (mining "activity") is led by price, not the other way round.

### 5c. Ciaian, Rajcaniova & Kancs (2016), "The Economics of BitCoin Price Formation," *Applied Economics* 48(19):1799–1815

**Could not obtain.** I attempted to retrieve this exact paper via a JRC working-paper mirror and instead
downloaded a **different** paper by the same two co-authors — Ciaian, Kancs & Rajcaniova (2017), "Virtual
Relationships: Short- and Long-run Evidence from BitCoin and Altcoin Markets," JRC Working Papers in Economics
and Finance 2017/5 (`ciaian_rajcaniova_kancs_2017_jrc_wp.pdf`, 41 pp., VERIFIED_FULLTEXT for *that* paper only,
sample 2013–2016, altcoin/BTC interdependence, headline conclusion p.2: *"the virtual currency supply is
exogenous and therefore plays only a limited role in the price formation"*). This is **not** a substitute for
the target 2016 Applied Economics paper and I do not use it to fill the table below.

For the actual target paper, everything is **ABSTRACT_ONLY** (Applied Economics is Taylor & Francis
paywalled): search-engine summaries describe it as deriving "testable hypotheses of BitCoin price formation"
from (i) market forces of supply/demand (including transaction counts as a demand proxy), (ii) BitCoin
attractiveness for investors/users, (iii) macro-financial developments, using a supply/demand structural
framework, but I could not confirm exact regression timing (contemporaneous vs. lagged), sample dates, or
whether transaction-count demand proxies were found to be contemporaneous or predictive. I flag this row as
**data not obtained — do not rely on it** rather than guessing.

### 5d. Polasik, Piotrowska, Wisniewski, Kotkowski & Lightfoot (2015), "Price Fluctuations and the Use of Bitcoin: An Empirical Inquiry," *International Journal of Electronic Commerce* 20(1):9–49

**VERIFIED_FULLTEXT** — I obtained what appears to be an ECB conference/working-paper version
(`polasik_et_al_2015_ecb.pdf`, 59 pp., hosted at ecb.europa.eu, presented at the June 2015 ECB retail-payments
conference) matching the published paper's abstract, title, and authorship; treat as a **pre-publication /
conference-proceedings version**, not necessarily identical page-for-page to the final IJEC 2015 typeset
version (page numbers below refer to my copy).

| Predictor | (1) | (2) | (3) Horizon | (4) Info timestamp | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmark | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Change in total number of blockchain transactions (Δln(Transactions)), alongside popularity (news articles, Google searches) and media tone | **IS** | **C** — explicitly a same-period (same-month) regression; authors flag this themselves as an endogeneity/simultaneity concern and instrument with 2SLS (lagged endogenous vars, time trend, ln(Cryptography)-mentions instrument) to try to address it, but the specification tested is contemporaneous, not a lagged forecast | Monthly, same-month | Same calendar month as the return (contemporaneous regressor) | RO (regression only; no portfolio/trading strategy) | No | BTC only | **2010-07 to 2014-08** (regressions start 2011-04 because popularity variables are undefined earlier) | No | Blockchain.info-style public chain data (raw tx count) | N/A | R² "quite high and can exceed a half" in-sample; **no OOS or cost-adjusted test reported** | p.21–24 (§3.2, Table III description): *"The increase in transaction volume proves to be important, particularly in Panel A... This result is consistent with the presence of network effect"*; popularity effects are larger and more robust (Google-search coefficient: +53 to +62 bps return per 1% search increase) than the transaction-count effect | **MIXED/CONTEMPORANEOUS** — positive same-month association, authors' own framing is "popularity/sentiment/transactions drive price **but it may be that the opposite is true**" (their words, explicit reverse-causality caveat, p.22) | **VERIFIED_FULLTEXT** |

---

## 6. Metcalfe's-law papers: valuation-fit vs. genuinely predictive

### 6a. Wheatley, Sornette, Huber, Reppen & Gantner, "Are Bitcoin Bubbles Predictable? Combining a Generalized Metcalfe's Law and the LPPLS Model," *Royal Society Open Science* 6(6):180538 (2019); arXiv:1803.05663 (March 2018 preprint)

**VERIFIED_FULLTEXT** (arXiv preprint version, `wheatley_sornette_2018_arxiv.pdf`, 20 pp.; I could not retrieve
the RSOS-hosted final-typeset PDF directly — royalsocietypublishing.org returned HTTP 403 to scripted
download — so treat the numbers below as the **March-2018 arXiv v1 preprint**, which may differ in minor
respects from the final June-2019 RSOS version).

| Predictor | (1) | (2) | (3) | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmark | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Generalized Metcalfe's law: ln(market cap) = α + β·ln(active addresses) + ε | **IS** — single full-sample log-linear regression, explicitly **not** a forecasting exercise (used to define a "fundamental value" support level for bubble diagnosis) | **C** — same-day market cap and same-day active-address count; authors themselves flag this is a **contemporaneous, non-causal-identified** fit | N/A — no forecast horizon; this is a valuation-level fit, not a return prediction | Same-day | RO (no trading strategy; used only to flag overvaluation for the separate LPPLS bubble-timing model) | No | BTC only | 2,782 daily obs., **2010-07-17 to 2018-02-26** | No | bitinfocharts.com (public, free) | N/A (active-address proxy, not entity-labeled) | N/A — not a trading-benchmark comparison | p.4 (§2): slope β=1.69 (SE 0.0076), intercept α=1.51 (SE 0.087), **R²=0.956**; forcing β=2 (pure Metcalfe) is "significantly worse" (ANOVA/F-test p<10⁻¹⁶); on 83% of rolling 1-year windows, β<2 (75% significantly so, p=0.05) | **VALUATION_FIT, NOT_PREDICTIVE_TEST** — the authors explicitly warn (same page, footnotes 6 and 10): *"one often obtains high coefficients of determination when regressing unrelated trending/non-stationary series onto each-other [i.e., spurious regression]"* and *"endogeneity is an issue, as the number of active users may determine market cap in the long term, but large fluctuations in market cap can also plausibly trigger fluctuations in active users on shorter time scales"* — i.e., the authors themselves flag both spurious-regression risk and reverse-causality risk in their own headline R²=0.956 result | **VERIFIED_FULLTEXT** |
| LPPLS bubble/crash-hazard model (uses the Metcalfe fundamental-value gap as one input, not itself a network-activity variable) | IS calibration, "ex-ante warning" framing | P (of crash *timing*, within a probabilistic bracket) — but this predicts bubble/crash events, not ordinary expected returns | Event-based (crash-hazard window), not a fixed return horizon | N/A | RO (no strategy backtest reported in the sections I read) | No | BTC only | Same sample | No | N/A | N/A | Not evaluated against a trading benchmark in what I read | Abstract + §1 (p.1–2) | Out of scope for "network activity as return predictor" (this is a bubble-detection model layered on top of the Metcalfe fit) — **NOT_PREDICTIVE_TEST** for the network-activity question specifically | **VERIFIED_FULLTEXT** |

This is the cleanest, most self-aware VALUATION_FIT case in the whole audit: an R²=0.956 in-sample level-fit
between price and active addresses, with the authors themselves explicitly naming both the spurious-regression
and the reverse-causality (price→addresses) risk in their own result.

### 6b. Alabi (2017), "Digital blockchain networks appear to be following Metcalfe's Law," *Electronic Commerce Research and Applications* 24:23-29

**ABSTRACT_ONLY/SECONDARY** — Elsevier-paywalled, not retrieved. Per search-engine summaries: BTC, ETH, and
Dash market caps regressed against unique daily active addresses; "netoid" growth-curve fitting used to predict
growth-rate turning points (e.g., a predicted October-2017 growth-rate peak for BTC). This is again a
**contemporaneous, in-sample level-fit** exercise (valuation-fit), not a return-forecasting backtest, based on
what I could verify from secondary descriptions — same VALUATION_FIT classification as Wheatley et al., but
unverified in detail. **Status: ABSTRACT_ONLY.**

### 6c. Peterson (2018), "Metcalfe's Law as a Model for Bitcoin's Value," SSRN 3078248

**ABSTRACT_ONLY/SECONDARY** — SSRN blocks scripted PDF download (403 on both the abstract page and the
Delivery.cfm direct-download URL pattern). Per search-engine summaries: models Bitcoin price as a function of
wallet-count-based supply/demand, claims ">70% of variance in Bitcoin value explained" by a Metcalfe-law fit to
network-size growth. Same caveat as above — this reads as an in-sample, contemporaneous valuation fit (like
Wheatley et al. and Alabi), not an OOS forecast; I cannot verify sample period, exact R², or whether any
forward-looking test was attempted. **Status: ABSTRACT_ONLY.**

**Summary for §6:** of the three Metcalfe papers, only Wheatley et al. is VERIFIED_FULLTEXT, and it is
unambiguously a **valuation-level (contemporaneous) fit**, not a genuine OOS return predictor, with the authors
explicitly flagging spurious-regression and reverse-causality risk in their own headline statistic. Alabi and
Peterson appear (per secondary description only) to be doing the same style of exercise; I found no evidence
in any of the three that Metcalfe's law was ever tested as an OOS, cost-adjusted, long-short trading signal.

---

## 7. Recent (2024–2026) literature on blockchain fundamentals and return prediction

### 7a. Sakkas & Urquhart (2024), "Blockchain factors," *Journal of International Financial Markets, Institutions and Money* 94:102012 — **the strongest, most rigorous recent paper found in this audit**

**VERIFIED_FULLTEXT** (open access, CC-BY; `sakkas_urquhart_2024_blockchain_factors_bham.pdf`, 14 pp., via
University of Birmingham research repository — matches the published DOI 10.1016/j.intfin.2024.102012).

| Predictor | (1) | (2) | (3) Horizon | (4) Info timestamp | (5) | (6) Costs | (7) | (8) Sample | (9) Post-2019? | (10) Vendor | (11) | (12) Survives benchmark | Key stat / location | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 candidate on-chain factors tested jointly with 3 market-based factors via Harvey & Liu (2021) multiple-testing-aware factor selection: MVRV, NUPL, SER, **NDF** (supply-distribution/whale-concentration), **NVT** (network-value-to-transactions), **X1YAS** (1-yr active-supply %), VTTA (whale share), Active Mkt Cap, Realized Mkt Cap, **P2A** (price-to-active-addresses) | **IS full-sample factor-selection test** (Harvey-Liu bootstrap procedure is designed to be robust to multiple testing/data-mining, but it is not a chronological train/test OOS split) | **P at weekly-portfolio-formation lag** (characteristic-sorted terciles, standard weekly rebalancing; not literally same-instant contemporaneous) | 1 week | Characteristic known at week-t close, portfolio held over week t+1 | **LS** for factor construction; separately tested **LO** (no-short) combination portfolios for practical implementation | **Not modeled** — no explicit transaction-cost/slippage deduction on the reported Sharpe ratios | 36 cryptocurrencies (cap-weighted market; broader than BTC/ETH but far short of "broad altcoin universe") | **Jan 2015 – Nov 2021**, weekly | Yes — sample runs through Nov 2021 | **CoinMetrics** (paid API; acknowledged in paper) | Not addressed (36-coin fixed list; no explicit discussion of survivorship in address/entity relabeling) | Of the 10 on-chain factors, only **NDF** (a supply-concentration/whale measure, not a pure "activity" metric) is selected; **P2A (price-to-active-addresses) and NVT — the two variables closest to genuine "network activity" — do NOT survive** once market + NDF are in the model (p.9-10: "none of the remaining factors is able to explain the cross-section... in addition to the value-weighted market and NDF factors") | Table 2 (factor definitions, p.5); selection result p.9 ("...the following most dominant factor is the long-short NDF... p-value equal to 0.035... none of the remaining factors is able to explain the cross-section"); portfolio Sharpe ratios p.2 abstract-adjacent (weekly SR: market-only 0.166 vs. market+long-only-NDF mean-variance 0.202; range 0.195–0.225 across construction rules) | **CONTRADICTORY / NOT_PREDICTIVE_TEST** for pure network-activity metrics specifically (P2A, NVT, active-supply% all fail selection); the one metric that *does* survive (NDF) measures supply concentration/decentralization, not activity level, so it sits outside the L1 "network activity" definition even though it is on-chain | **VERIFIED_FULLTEXT** |

This is the single most decision-relevant recent result for the project's specific hypothesis (aggregate
network-activity variables as return predictors): a 2024, open-access, multiple-testing-aware, weekly,
36-coin cross-sectional test that explicitly includes price-to-active-addresses and network-value-to-transactions
and finds **neither survives** once a market factor and a (non-activity) whale-concentration factor are
accounted for.

### 7b. Chi, Chu & Hao (2025), "Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets," arXiv:2411.06327

**VERIFIED_FULLTEXT** (`arxiv_2411.06327_onchain_flows.pdf`, 29 pp.; not yet confirmed published in a
peer-reviewed venue — dated a June-2025 revision on arXiv, econ.EM-style working paper).

| Predictor | (1) | (2) | (3) Horizon | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) | (10) Vendor | (11) | (12) | Key stat | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Exchange net inflows/outflows (BTC, ETH, USDT) — an on-chain **flow**, not a pure activity-count metric, but adjacent | Both **IS and OOS** explicitly reported ("we perform in-sample and out-of-sample regression tests," p.2) | **P** — explicit multi-hour-ahead predictive regressions | Intraday, **1–6 hours ahead** | Flow measured over the prior interval, used to predict the next 1/2/3/4/6-hour return/volatility | RO (predictive regressions) with a supplementary **options-strategy P&L overlay** (not a plain long-short backtest) | Not confirmed in the sections I read (options P&L section may embed some cost proxy via option premia, but no explicit spread/slippage treatment for the spot flows themselves was found) | BTC and ETH (also USDT flows as a predictor for both) — **not** a broad altcoin cross-section | **2017-12-16 to 2023-01-20** (main sample); a secondary robustness sample 2021-01-01 to 2022-12-31 | **Yes** — sample extends to Jan 2023, the most recent end-date of any paper in this audit | Exchange-flow data provider (specific vendor not confirmed from the pages read) | Not addressed | Mixed and asset-dependent — reported directly: BTC net inflows "generally lack predictive power for BTC returns (except at 4 hours)"; ETH net inflows **negatively** predict ETH returns/volatility; USDT net inflows into exchanges positively predict both BTC and ETH returns at multiple intervals | Abstract, p.1; sample-period statements pp. multiple (headers of Tables 2–5) | **MIXED** — genuinely predictive, OOS-tested design (rare in this literature), but effects are asset-specific, sign-flip between BTC and ETH, and the strongest, most consistent driver (USDT exchange inflows) is a stablecoin-flow proxy, not a "native" activity metric like address/tx counts | **VERIFIED_FULLTEXT** |

### 7c. Cakici, Shahzad, Będowska-Sójka & Zaremba (2024), "Machine learning and the cross-section of cryptocurrency returns," *International Review of Financial Analysis* 94:103244

**ABSTRACT_ONLY/SECONDARY** — SSRN blocked scripted download (403); ScienceDirect paywalled. Per search-engine
summaries: thousands of cryptocurrencies, 2014–2022, ML (mainly simple models) predicts cross-sectional
returns; **key predictors are price, past alpha, illiquidity, and momentum** — network/on-chain variables are
**not** reported among the dominant predictors in any summary I could find; alpha concentrates in small,
illiquid, volatile coins; profitable despite high turnover/costs claimed but not independently verified by me.
**This paper does not appear to feature network-activity variables as a first-order predictor** based on what
is available; I flag this as a plausible omission rather than a confirmed one, since I lack full text.

### 7d. Fieberg, Günther, Poddig & Zaremba (2024), "Non-standard errors in the cryptocurrency world," *International Review of Financial Analysis*

**ABSTRACT_ONLY/SECONDARY.** Per search summary: 10 methodological choices × 43 sorting variables → 20,736
research designs; average monthly non-standard error 0.19%, exceeding standard errors; most premia robust in
sign/significance/monotonicity despite this dispersion. I could not confirm whether any of the 43 sorting
variables include on-chain/network-activity characteristics (the summary emphasizes size/momentum/volume/
distress-style equity-style sorts, not on-chain metrics) — **relevance to L1 is unconfirmed; flagged as
likely NOT_APPLICABLE but not verified.**

### 7e. Machine-learning-on-price-plus-on-chain papers (Mudassir et al. 2020; Sebastião & Godinho 2021; Jagannath et al. 2021; Chen, Li & Sun 2020)

- **Mudassir, Bennbaia, Unal & Hammoudeh (2020)**, *Neural Computing and Applications* 33(15):9155–9177 —
  attempted download of the author-repository PDF (e-space.mmu.ac.uk) returned HTTP 202 with an empty body
  (likely a redirect/embargo page); **not obtained**. Per search summary: ANN/LSTM/SVM models for 1/7/30/90-day
  BTC forecasts, up to ~65% next-day directional accuracy; feature set described as "high-dimensional" but the
  specific role of on-chain/network features (vs. purely price/technical features) is **not confirmed** from
  what I could read. **Status: ABSTRACT_ONLY, feature set unconfirmed.**
- **Sebastião & Godinho (2021)**, *Financial Innovation* 7(1) — open-access (PMC7785332) but my scripted
  download attempt returned an HTML error page rather than the PDF; **not obtained** in this session. Per
  search summary: BTC/ETH/LTC forecasting, Aug-2015–Mar-2019 training + test from Apr-2018 (explicit OOS test
  window spanning a bear market), attributes drawn from "trading and network activity" — i.e., this paper
  **does claim to use network-activity attributes**, and does run a genuine chronological OOS split with a
  regime change between validation and test, which is a relatively strong design — but I cannot confirm which
  specific network variables, their individual importance, or cost treatment without the full text.
  **Status: ABSTRACT_ONLY.**
- **Jagannath et al. (2021)**, "An on-chain analysis-based approach to predict Ethereum prices," *IEEE Access*
  9:167972–167989 — not obtained; per search summary, uses transaction-graph/on-chain features for ETH price
  forecasting. **Status: ABSTRACT_ONLY**, no further detail confirmed.
- **Chen, Li & Sun (2020)** — search results returned a paper title ("Bitcoin price prediction using machine
  learning: An approach to sample dimension engineering," *J. Comput. Appl. Math.* 365:112395) whose feature
  set was **not confirmed** to include on-chain/network variables (results describe 5-min and daily BTC
  prediction comparing statistical vs. ML methods, with no on-chain-specific description found). **I cannot
  confirm this is the same paper the task intended**, and flag it as an unresolved bibliographic match.

None of the four ML papers in this sub-section could be verified full-text in this session; all are
ABSTRACT_ONLY at best, and in two cases (Mudassir; Chen/Li/Sun) I could not even confirm the on-chain-feature
premise from what was retrievable.

---

## 8. Evidence that on-chain predictability decayed post-2019 / into the ETF era (2024+)

I found **no dedicated paper** directly testing "did on-chain/network-activity predictability decay after
2019 or after the 2024 spot-ETF launches." What can be assembled indirectly, all from papers already covered
above:

- Yae & Tian (2022, §2 above): a comprehensive OOS test finds in-sample network/attention/volume predictors
  fail OOS — but the sample almost certainly predates the ETF era (paper published 2022), so this is evidence
  of general OOS fragility, not specifically of post-ETF decay. **ABSTRACT_ONLY, indirect.**
- Sakkas & Urquhart (2024, §7a above; VERIFIED_FULLTEXT): sample ends Nov-2021, i.e., **also pre-ETF**, but is
  the most recent *rigorous* rejection of pure activity metrics (P2A, NVT) as priced factors that I could
  verify full-text.
- Chi, Chu & Hao (2025, §7b above; VERIFIED_FULLTEXT): the only paper in this audit whose sample runs into
  2023, and it finds genuine (if asset-specific and sign-flipping) intraday predictability from on-chain
  **flows** — this is at least consistent with activity/flow-based signals not being fully arbitraged away as
  of 2023, but it is a flow (exchange in/outflow) rather than a pure activity-count (addresses/tx) metric, and
  it does not extend into the 2024 spot-ETF period.
- I found no paper in this audit with a sample window overlapping 2024–2026 spot-ETF-era data. **This is a
  genuine gap**: the project cannot currently cite direct evidence on whether the 2024+ institutionalization
  of BTC/ETH (spot ETFs, greater derivatives depth) has changed the activity→return relationship, in either
  direction.

---

## 9. Large-scale crypto factor studies and non-standard-error/robustness literature, re: inclusion of network variables

### 9a. Liu, Tsyvinski & Wu (2022), "Common Risk Factors in Cryptocurrency," *Journal of Finance* 77(2):1133–1177 (NBER w25882)

**VERIFIED_FULLTEXT for an early draft only.** I hold NBER working paper w25882
(`liu_tsyvinski_wu_nber_w25882.pdf`, 48 pp.), which its own front matter does not date explicitly in the text I
extracted, but which is the **pre-2022, non-final** NBER-hosted draft (the JF-2022 published version has a
different variable set, per the Cong et al. footnote quoted in §4 above). I ran a full-text search for the
string "address" across all 48 pages of this draft: **zero matches**. The draft's factor set is explicitly
described (p.2 area) as **"broadly four groups of factors: size, momentum, volume, and volatility"** built
purely from **CoinMarketCap price/volume/market-cap data** — i.e., this draft contains **no on-chain/network
variable of any kind**. The "price-to-new-address ratio negatively predicts returns" finding attributed to
"Liu, Tsyvinski and Wu (2021)" by Cong et al. (§4 above, footnote 11) must therefore come from a **later,
distinct 2021 revision** of this paper that I do not hold. I flag this explicitly as an unresolved version gap:
**do not conflate my full-text confirmation of "no address variables in the Dec-2019 draft" with the final
published paper, which (per secondhand citation only) apparently does include one.**

| Predictor | (1) | (2) | (3) | (4) | (5) | (6) Costs | (7) | (8) Sample | (9) | (10) | (11) | (12) | Key stat | Class. | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| (draft contains no network/address variables — size/momentum/volume/volatility only) | IS | P (1-week-ahead quintile sorts, standard design) | 1 week | Formation-week characteristic → next-week return | LS | Not modeled in what I read | Broad — "market-based factors" universe (CoinMarketCap-listed coins) | 2013 (per data-availability note) to end of 2018 | No (ends 2018) | CoinMarketCap (free) | N/A | Dollar-volume long-short ≈ −3.2%/week; market-cap and momentum strategies also significant | pp. as cited (Table 5 etc., dollar-volume factor) | **NOT_APPLICABLE to L1** (this draft has no network-activity variable to classify) | **VERIFIED_FULLTEXT (early draft only)** |
| Price-to-new-address ratio (final JF-2022 version only, not in my draft) | Unconfirmed | **P** (per secondary citation: "negatively predict future cryptocurrency returns") | Unconfirmed | Unconfirmed | Unconfirmed | Unconfirmed | Unconfirmed | Unconfirmed | Presumably yes (2021+ revision) | Unconfirmed | Unconfirmed | Unconfirmed | Cong et al. (2022 EFMA draft), footnote 11, p.10 | **SUPPORTIVE** (genuinely predictive claim, on-chain, but entirely secondhand) | **SECONDARY ONLY — not independently verified** |

### 9b. Cakici et al. (2024) — see §7c above (network variables not confirmed present).

### 9c. Fieberg et al. (2024) non-standard errors — see §7d above (relevance to on-chain variables unconfirmed).

**Overall for §9:** the two "large-scale crypto factor" studies most often cited alongside network-activity
research (Liu-Tsyvinski-Wu / Common Risk Factors, and Cakici et al.'s ML cross-section) are, as far as I could
verify, built primarily on **price/volume/market-cap** characteristics, with on-chain/network variables either
entirely absent (confirmed for the Dec-2019 LTW draft) or unconfirmed/likely-secondary in the ML paper. This is
consistent with a broader pattern across this audit: the "mainstream" crypto cross-sectional-return-prediction
literature is overwhelmingly price-based, and network-activity variables appear mainly as a **smaller,
separate, "priced as an exposure" or "fails to survive alongside other on-chain factors"** sub-literature
(Liu & Tsyvinski's network factor; Bhambhwani et al.'s network size/computing power; Sakkas & Urquhart's P2A/NVT
rejection), not as a first-order predictor in the dominant factor-zoo papers.

---

## Answers to the three evidence-based questions

### (a) Does activity lead returns, or respond contemporaneously to price/speculation? What is the strongest evidence each way?

Both directions have support, and the honest summary is that **the contemporaneous/reverse-causality reading
is better supported by the full-text evidence I could verify, while activity-leads-price evidence is weaker,
older, and decays within-sample**:

- **Strongest evidence for activity → price (leads):** Kristoufek (2015), VERIFIED_FULLTEXT, wavelet-coherence
  analysis: trade/transaction counts positively lead the Bitcoin price at long time-scales, but **only in the
  2011–2013 portion of the 2011-09 to 2014-02 sample**, with the relationship explicitly described as
  "becoming weaker in time" and losing significance from January 2013. Cong et al.'s NET factor (VERIFIED_FULLTEXT,
  §4) is also technically "predictive" in timing (1-week-lag address-growth sort → next-week return, t=2.82),
  though it is the weakest of five factors and reported gross of costs.
- **Strongest evidence for price → activity (reverse causality / contemporaneous):** (i) Kristoufek (2015),
  same paper: hash rate and mining difficulty are **led by price**, not the reverse — miners respond to price,
  they do not predict it. (ii) Wheatley et al. (2019/2018 preprint), VERIFIED_FULLTEXT: the authors of the
  headline Metcalfe R²=0.956 result **themselves** state "large fluctuations in market cap can also plausibly
  trigger fluctuations in active users on shorter time scales," i.e., they flag their own central result as
  possibly reflecting reverse causality. (iii) Polasik et al. (2015), VERIFIED_FULLTEXT: the authors run a
  same-month (contemporaneous) regression of returns on transaction-count changes and explicitly write that
  "popularity and media sentiment drive price changes – but it may be that the opposite is true," using 2SLS
  instrumentation to try to address it rather than eliminating the concern. (iv) Koutmos (2018), SECONDARY
  only: bivariate VAR/Granger evidence that return shocks affect transaction activity more than the reverse,
  and that "no evidence that returns can be explained by the change in transaction activity." (v) Liu &
  Tsyvinski's own published abstract (ABSTRACT_ONLY) frames network factors as return **exposures**, not
  predictors, in explicit contrast to momentum/attention, which the same abstract calls predictive.
- **Net read:** the cleanest, most recent, most methodologically careful test in this audit (Sakkas &
  Urquhart 2024, VERIFIED_FULLTEXT) finds that price-to-active-addresses and network-value-to-transactions —
  the two closest matches to "network activity" in their candidate set — **do not survive** a multiple-testing-
  aware factor-selection procedure once market and a whale-concentration factor are included. Combined with
  the pattern above, the weight of full-text-verified evidence leans toward **activity responding to price
  (or being a weak, decaying, non-causally-identified co-mover)** rather than activity being a robust,
  standalone forward-looking driver.

### (b) Why might older/broader OOS studies find failure while newer papers report stronger OOS predictability?

Based only on what is verifiable in this audit (not speculation beyond the evidence):

- **Altcoin cross-sections / small illiquid tokens:** Cong et al. (VERIFIED_FULLTEXT) explicitly show the
  value/network-adjacent characteristic effect is far stronger and monotonic in **small-cap** deciles than
  large-cap (Table 4 double-sorts, §4 above) — consistent with the general finding (also reported, SECONDARY,
  for Cakici et al. 2024) that crypto anomalies concentrate in small/illiquid coins. Older studies restricted
  to BTC/ETH/XRP (Liu & Tsyvinski 2018 draft; Yae & Tian 2022) mechanically exclude the part of the
  cross-section where on-chain effects appear strongest.
  Caveat: because these small/illiquid-coin results are gross-of-cost (Cong et al. do not model costs; Cakici
  et al.'s cost claims are SECONDARY/unverified), this is also exactly the part of the cross-section where
  transaction costs and slippage are most likely to erode the effect — the "decay" from IS to a genuinely
  tradeable OOS test could be a **cost artifact of the small-cap concentration**, not only a sample-period
  effect.
- **ML flexibility:** the recent Chi-Chu-Hao (2025) and Sakkas-Urquhart (2024) results both use more
  sophisticated statistical machinery (an intraday multi-horizon regression design with an explicit IS/OOS
  split, and a bootstrap multiple-testing-aware factor-selection procedure, respectively) than older
  single-regression studies — but note that Sakkas & Urquhart's more rigorous method is the one that
  **rejects**, not confirms, the pure activity metrics (P2A, NVT); it is the *concentration* metric (NDF) that
  survives. So "newer/more flexible methodology" does not uniformly favor activity-based predictability in
  what I verified — it depends heavily on which specific on-chain construct is tested.
- **Sample periods / data revisions / vendor quality:** every VERIFIED_FULLTEXT paper with a sample ending
  before ~2019 (Liu & Tsyvinski 2018 draft, Kristoufek 2015, Wheatley 2018, Polasik 2015) either fails to find
  predictability or explicitly caveats reverse causality; the two papers with samples reaching 2021 (Cong et
  al.; Sakkas & Urquhart) and 2023 (Chi-Chu-Hao) show a mixed and increasingly nuanced picture (some things
  survive — NDF, USDT flows — most do not — P2A, NVT, price-to-dividend). This is at least *consistent with*
  vendor data quality and market maturity improving over time, but I found no paper that isolates this
  mechanism specifically for network-activity variables (vs. sample-period or universe-composition effects).
- **Factor mining / multiplicity:** I found no dedicated non-standard-errors-style robustness audit that
  specifically targets on-chain/network variables (Fieberg et al. 2024's forty-three sorting variables are,
  as far as I can confirm, predominantly price/volume/distress-style, not on-chain) — this remains an
  **open gap**, not a resolved question, for the network-activity family specifically.

### (c) Is there ANY evidence of long-only, BTC/ETH, weekly/monthly, after-cost value from a single simple network-activity variable?

**No — I found no such evidence, and several full-text results point the other way.** Specifically:

- The one BTC-only, weekly-or-lower-frequency, simple, single-variable test I could fully verify — the
  Bitcoin wallet-user-count-based price-to-"dividend" ratio in Liu & Tsyvinski's 2018 NBER draft — found
  **zero** predictive power at daily horizons 1–7 (R²=0.00 throughout, Table 30).
- Sakkas & Urquhart (2024), the only recent (2015–2021, weekly) rigorous multi-factor selection test that
  specifically includes a **price-to-active-addresses** variable, finds it does **not** survive as a priced
  factor even before considering costs; the one factor that does survive (NDF) is a whale-concentration
  measure, not an activity-level measure, and the paper's long-only portfolio results **combine NDF with the
  market factor** — they do not report a long-only Sharpe ratio for any single, standalone network-activity
  variable in isolation, let alone one net of costs.
- No paper in this audit reports transaction costs explicitly alongside a network-activity-only trading
  strategy (Cong et al.'s NET factor and Sakkas & Urquhart's combination portfolios are both reported gross of
  costs).
- Chi-Chu-Hao (2025) is the one paper with a genuine BTC/ETH, cost-adjacent (via an options overlay),
  post-2019 test, but its horizon is intraday (1–6 hours, not weekly/monthly), its strongest and most
  consistent predictor is a **stablecoin exchange-flow** variable (USDT net inflow), not a native
  activity-count metric, and results sign-flip between BTC and ETH.

**Conclusion for (c): based on the full-text evidence gathered in this audit, no paper demonstrates long-only,
BTC/ETH, weekly-or-monthly, after-cost value from a single simple network-activity variable (active addresses,
transaction count, fees, or hash rate). The closest candidates either fail out-of-sample/factor-selection
tests (price-to-"dividend"/wallet-users; price-to-active-addresses; NVT), are framed by their own authors as
contemporaneous exposures rather than predictors (Liu & Tsyvinski's published network factor; Bhambhwani et
al.'s network size/computing power), or are valuation-level fits explicitly flagged by their authors as
possibly spurious/reverse-caused (Wheatley et al.'s Metcalfe regression).**

---

## Bibliography

Entries marked **[FULLTEXT]** have a local PDF under `reports/phase11b/raw/literature/` (git-ignored per
`.gitignore` lines 52-54; not committed). Entries marked **[ABSTRACT]** were not obtained in full text in this
session.

1. **[FULLTEXT, early 2018 draft only]** Liu, Y., & Tsyvinski, A. "Risks and Returns of Cryptocurrency." NBER
   Working Paper No. 24877, August 2018. https://www.nber.org/papers/w24877 —
   local file `liu_tsyvinski_nber_w24877.pdf`. Published version: *Review of Financial Studies* 34(6):2689–2727
   (2021), DOI: 10.1093/rfs/hhaa113 [ABSTRACT only, via EconPapers mirror
   `econpapers.repec.org/RePEc:oup:rfinst:v:34:y:2021:i:6:p:2689-2727.`]. SSRN 3226952.
2. **[ABSTRACT]** Yae, J., & Tian, G. Z. "Out-of-sample forecasting of cryptocurrency returns: A comprehensive
   comparison of predictors and algorithms." *Physica A* 598:127379 (2022). DOI: 10.1016/j.physa.2022.127379.
3. **[ABSTRACT]** Bhambhwani, S., Delikouras, S., & Korniotis, G. M. "Blockchain characteristics and
   cryptocurrency returns." *Journal of International Financial Markets, Institutions and Money* (2023).
   DOI: 10.1016/j.intfin.2023.101782 (SSRN 3342842 / 3387313; earlier CEPR DP13724, 2019).
4. **[FULLTEXT]** Cong, L. W., Karolyi, G. A., Tang, K., & Zhao, W. "Value Premium, Network Adoption, and
   Factor Pricing of Crypto Assets." Working paper, EFMA 2022 Rome meetings full-paper draft —
   local file `cong_karolyi_tang_zhao_efma2022.pdf`,
   https://www.efmaefm.org/0efmameetings/efma%20annual%20meetings/2022-rome/papers/efma%202022_stage-3032_question-full%20paper_id-231.pdf
5. **[ABSTRACT]** Koutmos, D. "Bitcoin returns and transaction activity." *Economics Letters* 167:81–85 (2018).
   DOI: 10.1016/j.econlet.2018.03.021.
6. **[FULLTEXT]** Kristoufek, L. "What Are the Main Drivers of the Bitcoin Price? Evidence from Wavelet
   Coherence Analysis." *PLoS ONE* 10(4):e0123923 (2015). DOI: 10.1371/journal.pone.0123923 — local file
   `kristoufek_2015_plosone.pdf`.
7. **[ABSTRACT — target paper not obtained; a different paper by the same authors was substituted for
   context only]** Ciaian, P., Rajcaniova, M., & Kancs, d'A. "The Economics of BitCoin Price Formation."
   *Applied Economics* 48(19):1799–1815 (2016). DOI: 10.1080/00036846.2015.1109038.
   Related but distinct paper actually obtained: Ciaian, P., Kancs, d'A., & Rajcaniova, M. "Virtual
   Relationships: Short- and Long-run Evidence from BitCoin and Altcoin Markets." JRC Working Papers in
   Economics and Finance No. 2017/5. DOI: 10.2760/133614 — local file
   `ciaian_rajcaniova_kancs_2017_jrc_wp.pdf`.
8. **[FULLTEXT, pre-publication/conference version]** Polasik, M., Piotrowska, A., Wisniewski, T. P.,
   Kotkowski, R., & Lightfoot, G. "Price Fluctuations and the Use of Bitcoin: An Empirical Inquiry."
   *International Journal of Electronic Commerce* 20(1):9–49 (2015). DOI: 10.1080/10864415.2016.1061413 —
   local file `polasik_et_al_2015_ecb.pdf` (ECB conference-hosted version).
9. **[FULLTEXT, arXiv preprint]** Wheatley, S., Sornette, D., Huber, T., Reppen, M., & Gantner, R. N. "Are
   Bitcoin Bubbles Predictable? Combining a Generalized Metcalfe's Law and the Log-Periodic Power Law
   Singularity Model." *Royal Society Open Science* 6(6):180538 (2019); arXiv:1803.05663 (2018 preprint) —
   local file `wheatley_sornette_2018_arxiv.pdf`.
10. **[ABSTRACT]** Alabi, K. "Digital blockchain networks appear to be following Metcalfe's Law."
    *Electronic Commerce Research and Applications* 24:23–29 (2017). DOI: 10.1016/j.elerap.2017.06.003.
11. **[ABSTRACT]** Peterson, T. "Metcalfe's Law as a Model for Bitcoin's Value." SSRN 3078248 (2018).
    DOI: 10.2139/ssrn.3078248.
12. **[FULLTEXT]** Sakkas, A., & Urquhart, A. "Blockchain factors." *Journal of International Financial
    Markets, Institutions and Money* 94:102012 (2024). DOI: 10.1016/j.intfin.2024.102012 — local file
    `sakkas_urquhart_2024_blockchain_factors_bham.pdf` (University of Birmingham open-access repository copy).
13. **[FULLTEXT]** Chi, Y., Chu, Q. R., & Hao, W. "Return and Volatility Forecasting Using On-Chain Flows in
    Cryptocurrency Markets." arXiv:2411.06327 (June 2025 revision) — local file
    `arxiv_2411.06327_onchain_flows.pdf`.
14. **[ABSTRACT]** Cakici, N., Shahzad, S. J. H., Będowska-Sójka, B., & Zaremba, A. "Machine learning and the
    cross-section of cryptocurrency returns." *International Review of Financial Analysis* 94:103244 (2024).
    DOI: 10.1016/j.irfa.2024.103244. SSRN 4295427.
15. **[ABSTRACT]** Fieberg, C., Günther, T., Poddig, T., & Zaremba, A. "Non-standard errors in the
    cryptocurrency world." *International Review of Financial Analysis* (2024). DOI: 10.1016/j.irfa.2024.103107.
16. **[FULLTEXT, early Dec-2019 draft only]** Liu, Y., Tsyvinski, A., & Wu, X. "Common Risk Factors in
    Cryptocurrency." NBER Working Paper No. 25882 — local file `liu_tsyvinski_wu_nber_w25882.pdf`. Published:
    *Journal of Finance* 77(2):1133–1177 (2022). DOI: 10.1111/jofi.13119. SSRN 3379131.
17. **[ABSTRACT, not obtained]** Mudassir, M., Bennbaia, S., Unal, D., & Hammoudeh, M. "Time-series
    forecasting of Bitcoin prices using high-dimensional features: a machine learning approach." *Neural
    Computing and Applications* 33(15):9155–9177 (2021, first published online 2020). DOI:
    10.1007/s00521-020-05129-6.
18. **[ABSTRACT, not obtained]** Sebastião, H., & Godinho, P. "Forecasting and trading cryptocurrencies with
    machine learning under changing market conditions." *Financial Innovation* 7(1):3 (2021). DOI:
    10.1186/s40854-020-00217-x. PMC7785332.
19. **[ABSTRACT, not obtained]** Jagannath, N., et al. "An on-chain analysis-based approach to predict Ethereum
    prices." *IEEE Access* 9:167972–167989 (2021). DOI: 10.1109/ACCESS.2021.3135620.
20. **[ABSTRACT, bibliographic match unconfirmed]** Chen, Z., Li, C., & Sun, W. "Bitcoin price prediction
    using machine learning: An approach to sample dimension engineering." *Journal of Computational and
    Applied Mathematics* 365:112395 (2020). DOI: 10.1016/j.cam.2019.112395.

## Data-provenance note on the shared literature folder

`reports/phase11b/raw/literature/` also contains PDFs I did **not** download (e.g. `makarov_schoar_nber_w29396.pdf`,
several stablecoin/order-flow/decentralization papers) — evidence of a concurrent, differently-scoped Stage 0
sub-task writing to the same shared directory. I left those files untouched and did not rely on them for any
claim in this report; every source cited above was independently located and downloaded by this task.
