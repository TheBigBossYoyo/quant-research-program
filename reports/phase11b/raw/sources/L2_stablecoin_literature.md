# L2 — Stablecoin Issuance / Net Supply / Mint-Burn / Transfers as Crypto Return Predictors: Literature Audit

**Phase:** 11B Stage 0 (literature + data audit only — **not a backtest**; no price/return/OHLCV/market-cap/stablecoin-supply time series were downloaded, read, or computed anywhere in the production of this report)
**Retrieval date (all sources):** 2026-09-26
**Central question:** Is stablecoin issuance a **response** to crypto demand (crypto price/demand rises → stablecoin demand rises → issuer mints) or a **predictor** (new dollar liquidity arrives before deployment → future buying pressure)?
**Status legend:** `VERIFIED_FULLTEXT` (full text read directly — PDF or, for one paper, the publisher's own open-access HTML rendering, cited by page/table/section), `ABSTRACT_ONLY` (only the abstract/summary could be verified directly; body claims below that source are marked as such), `SECONDARY` (claim sourced from a citing paper or a search-engine summary of the source, not from the primary text itself).
**Copyright note:** all downloaded PDFs and one HTML→text conversion are saved under `reports/phase11b/raw/literature/` (git-ignored; not committed). Quotes below are each ≤25 words.

---

## 0. What was and was not done (compliance)

- No crypto price, return, OHLCV, market-cap, or stablecoin-supply time series was downloaded, opened, or computed. Every number below is a statistic **reported inside a paper**, read from that paper's own text/tables.
- Papers were obtained via public GETs (arXiv, SSRN mirrors, institutional repositories — UTIA/Czech Academy of Sciences, University of Vaasa OSUVA, University of Jyväskylä JYX, Warwick WRAP, NBER, BIS, Banque de France, Cleveland Fed conference mirror, EconStor/ZBW, Blockchain Research Lab) and one publisher open-access page (Wiley/*Journal of Finance*, "Open Access" tag, read via browser render, not paywalled). No sign-in, account creation, or form submission was used anywhere.
- Where a paper is genuinely paywalled with no free copy located (confirmed via the Unpaywall API, which returned `is_oa: false` / `oa_status: closed`), it is marked `ABSTRACT_ONLY` / `SECONDARY` rather than fabricated.
- For every table-based statistic quoted below, the underlying PDF was parsed with PyMuPDF (`fitz`); for papers where linear `get_text()` reading order scrambled multi-column tables (checked against `page.get_text("words")` word-coordinate positions), the ambiguous cell values are **not** quoted — only the qualitative, unambiguous prose conclusions are reported for those papers (flagged explicitly below, Wei 2018). For papers whose PDF tables parsed cleanly in reading order (Grobys & Huynh 2022; Ante, Fiedler & Strehle 2021), exact coefficients are quoted with table/page numbers.

---

## 1. Per-paper audit (12-field template + supply measure + key stat + classification)

### 1.1 Wei, W.C. (2018), "The impact of Tether grants on Bitcoin," *Economics Letters* 171:19–22

**Status:** `VERIFIED_FULLTEXT` (SSRN working-paper text, identical qualitative content to the published abstract; PDF: `Wei_2018_SSRN3175876.pdf`, 11pp; mirror of SSRN id 3175876, DOI 10.2139/ssrn.3175876)

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample only |
| 2. Contemporaneous or predictive | Predictive test (VAR, lagged grants → returns), but null result |
| 3. Forecast horizon | Daily |
| 4. Information timestamp | Daily aggregate "Tether grant" (mint) events from Omni Explorer; timestamp = blockchain issuance date, not a public-disclosure/tweet date |
| 5. Design | Regression-only (unrestricted 4-variable VAR: Tether grants, Tether volume, BTC volume, BTC return) |
| 6. Transaction costs | Not modeled (not a trading strategy) |
| 7. BTC/ETH vs altcoins | BTC only (vs. Tether) |
| 8. Sample period | 30-Dec-2016 to 20-Feb-2018 (daily) |
| 9. Post-2019 evidence | None (sample ends Feb 2018) |
| 10. Proprietary/vendor data | No — public blockchain data (Omni Explorer) + CoinMarketCap |
| 11. Current entity/exchange labels applied historically | No wallet-clustering/exchange-attribution at all; grants measured as aggregate Tether-Limited-issuing-address activity, no venue decomposition |
| 12. Survives benchmarks/controls | N/A — no return effect found to survive; volume effect controls for lagged returns/volume in VAR sense |

**Supply measure used:** Tether **grants** (raw on-chain "Grant Property Tokens" issuance events by Tether Limited), not free-float/circulating supply and not net of the "authorized-but-not-issued" treasury distinction.

**Key finding (quoted, PDF pp.5–6):** "we do not find any evidence suggesting that Tether issuances cause subsequent increases in Bitcoin returns" but "Tether issuances are highly autocorrelated and cause subsequent increases in Bitcoin (and Tether) trading volume." Separately: "we find evidence that Tether trading increases following prior day negative Bitcoin returns" and "Tether grants are more likely to be issued following a fall in Bitcoin price" (PDF p.6) — the paper explicitly notes this is consistent with *either* deliberate downturn-timed printing *or* "Tether grants are in response to greater Tether (or stable coin) demand in periods where Bitcoin returns have fallen" (PDF p.6), i.e. it does not adjudicate the endogeneity question itself.

**Table location caveat:** Table 2 ("VAR Model Estimates," PDF p.7 of the SSRN typeset draft) contains the individual coefficient/t-stat/p-value cells for all 4 equations × 4 lag regressors. When parsed with `page.get_text("words")` word-coordinates, the table's 12–14 numeric columns per row could not be reliably re-associated with their correct equation/regressor headers from the extracted geometry alone (the SSRN PDF places the table as an appended block disconnected from its caption's reading-order position). Per the hard rule against fabricating table cells, **individual VAR coefficients from Table 2 are not quoted here** — only the paper's own prose conclusions (which are unambiguous) are used.

**Classification:** **CONTRADICTORY** to the "issuance predicts returns" hypothesis; **weakly supportive** of the endogenous-demand-response interpretation (grants follow price declines, consistent with reverse causality).

---

### 1.2 Griffin, J.M. & Shams, A. (2020), "Is Bitcoin Really Untethered?," *The Journal of Finance* 75(4):1913–1964

**Status:** `VERIFIED_FULLTEXT` — read via the publisher's own **Open Access** HTML rendering (Wiley Online Library; article carries an "Open Access" tag and CC-BY-NC license per Unpaywall). Raw PDF download attempts via `requests`/`curl` were blocked by Wiley's bot-detection (403) even with browser-identical headers; the built-in browser tool rendered the page successfully (a real, JS-capable browser session, not a credential bypass — the article requires no sign-in). Full extracted text (~102k characters, through Table VIII) saved as a text conversion: `GriffinShams_2020_JoF_fulltext_htmlrender.txt`. Citations below use the paper's own Table/Section numbers (Wiley does not expose PDF page breaks in the HTML render, so "PDF page" is not separately given — journal pagination is 1913–1964).

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample (single historical episode) |
| 2. Contemporaneous or predictive | Predictive at short (3-hour) horizon; contemporaneous/concurrent framing for round-number and EOM tests |
| 3. Forecast horizon | Hourly to 3-hour rolling average forward return; also EOM (monthly) and full-sample (13-month) cumulative effects |
| 4. Information timestamp | **On-chain blockchain transaction timestamp** (Bitcoin and Tether/Omni blockchains), reconstructed via wallet-clustering algorithms — **not** Whale Alert or any public-disclosure timestamp (Whale Alert did not exist as a monitored data source in this paper; it predates that literature) |
| 5. Design | Regression (OLS, 2SLS/IV via round-number discontinuity) + event-study/bootstrap |
| 6. Transaction costs | Not modeled |
| 7. BTC/ETH vs altcoins | BTC primary; spillover tested to 6 large altcoins (DASH, ETC, ETH, LTC, XMR, ZEC) |
| 8. Sample period | March 2017 – March 2018 (hourly); EOM tests use March 2016 – March 2018 (225 daily obs) |
| 9. Post-2019 evidence | **None** — sample ends March 2018 |
| 10. Proprietary/vendor data | No public vendor feed, but a **bespoke, non-replicable wallet-clustering pipeline** (own construction from raw blockchain data, "over 200 GB from more than 10 sources") |
| 11. Current entity/exchange labels applied historically | **Yes, and this is the paper's central methodological device**: exchange identities (Bitfinex/Poloniex/Bittrex) assigned via same-input clustering + manually collected wallet addresses "from public forums and individual investors" (Section II.A) and from the historical Tether "rich list" via Internet Archive snapshots — labels reconstructed for the 2017–18 period, not sourced from a live/current vendor list |
| 12. Survives benchmarks/controls | Controls for lagged returns, 24h volatility, and their interaction (Table II); reversal-vs-flow disentangled via matched-sample placebo (Internet Appendix Fig. IA.11) |

**Supply measure used:** Net hourly **flow** of Tether/Bitcoin between specific exchange wallet clusters (Bitfinex→Poloniex/Bittrex and back), not aggregate issuance/authorization directly — issuance ("authorization") is used only as a conditioning dummy (whether an authorization occurred in the prior 72 hours).

**Key statistics (all VERIFIED_FULLTEXT with table numbers):**
- Table II: for a 100-BTC lagged flow increase, 3-hour forward BTC return rises 3.855bp (t=2.30) in the 72h after Tether authorization, vs. an insignificant −0.354bp with no authorization; rises to 8.134bp (t=2.93) when conditioned jointly on post-authorization **and** a prior negative return.
- Table III: spillover to 6 altcoins of 7.89–10.19bp under the same joint conditioning.
- Section III.C: the top 1% of hours (95 of 9,504) by lagged flow are associated with **58.8%** of Bitcoin's 481.8% buy-and-hold return over the sample, and 64.5% of the six-altcoin average buy-and-hold return; a 10,000-draw bootstrap places the actual path far outside the simulated distribution.
- Table IV: conditional on the top-1% flow/volatility bucket, a 1% BTC price drop is followed by a 61bp reversal in the next hour (β=−0.6091, t=−2.56) vs. an insignificant ~6bp reversal otherwise.
- Table V/VI: net flow and forward returns are elevated just **below** $500 round-number thresholds only after authorization (t=3.71 for the dominant "1LSg" wallet); a fuzzy-RD instrumenting flow with this discontinuity gives a **causal** 2SLS estimate of 26.42bp (all, t=2.06) to 65.44bp (1LSg-only, post-authorization, t=2.03) per 100-BTC flow.
- Table VII (EOM test): −2.3% average end-of-month BTC return in high-Tether-issuance months vs. ~0% in no-issuance months (t=−3.65 for the issuance subsample); **but** the paper itself flags fragility — "in a simple regression... we obtain a t-statistic of −2.85 with all observations, but an insignificant t-statistic of −1.26 when excluding the two [largest-issuance] months" (Dec 2017, Jan 2018) (Section IV.B.1).
- Table VIII: Tether flow is "highly sensitive to the BTC-USD pair... but bears little relation to the Tether-USD [premium] pair," used to reject the demand-pulled ("H1A") hypothesis in favor of the supply-pushed interpretation, for this specific episode.

**Classification:** **SUPPORTIVE** of a predictive/supply-driven effect, but narrowly scoped: the entire effect is statistically and economically concentrated in flows from **one wallet cluster** ("1LSg") on **one exchange** (Bitfinex) during **one 13-month episode** (2017–2018), and the headline EOM result loses significance when the two largest-issuance months are excluded.

---

### 1.3 Ante, L., Fiedler, I. & Strehle, E. (2021), "The influence of stablecoin issuances on cryptocurrency markets," *Finance Research Letters* 41:101867

**Status:** `VERIFIED_FULLTEXT` (Blockchain Research Lab Working Paper No. 11 pre-print, content matches the published abstract; PDF `AnteFiedlerStrehle_2021_issuances_BRLWP11.pdf`, 15pp; DOI 10.1016/j.frl.2020.101867 per journal citation, URL https://www.sciencedirect.com/science/article/pii/S1544612320316810)

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample |
| 2. Contemporaneous / predictive | Event study: both pre-event (anticipation/reverse-causality window) and post-event (predictive) windows tested |
| 3. Forecast horizon | Hourly, cumulated over ±24h around each event (also ±12h, 0–12h, 0–24h sub-windows; Table A.2/A.3 report additional windows) |
| 4. Information timestamp | **On-chain issuance transaction timestamp** (blockchain event time), not a public-disclosure timestamp |
| 5. Design | Event study (AAR/CAAR with 95% CI), estimation window −150h to −30h before event |
| 6. Transaction costs | Not modeled |
| 7. BTC/ETH vs altcoins | Four cryptocurrencies tested: BTC, ETH, XRP, LTC (pooled result) plus BTC-specific per-stablecoin breakdown |
| 8. Sample period | April 2019 – March 2020 |
| 9. Post-2019 evidence | Yes — entire sample is post-2019 (April 2019–March 2020), i.e. explicitly **post**-Griffin-Shams episode |
| 10. Proprietary/vendor data | No — public blockchain issuance data for 7 stablecoins (USDC, USDT, PAX, HUSD, BUSD, DAI, GUSD) |
| 11. Current entity/exchange labels applied historically | No exchange-wallet attribution used; issuance identified directly from each stablecoin's own issuing/treasury contract, not from exchange flow reconstruction |
| 12. Survives benchmarks/controls | Robustness checked across stablecoins and windows (Table A.2/A.3); issuance **size** found to not significantly affect abnormal returns |

**Supply measure used:** Discrete **issuance events ≥ $1,000,000** ("grants"/mints), 565 events across 7 stablecoins — an event-count measure, not continuous net supply.

**Key statistics (VERIFIED_FULLTEXT, Table 2/Figure 2, PDF pp.5–8):**
- Pooled 4-currency CAAR: **+0.31% to +0.47%** for the −12h to −1h pre-event window (all four currencies, highly significant); **+0.33% to +0.44%** for 0–12h post-event; **+0.47% to +0.69%** for 0–24h post-event; full ±24h window CAAR of **+0.72% (Ripple) to +1.1% (Litecoin)**.
- BTC-specific, per-stablecoin (pre-event window): for HUSD and BUSD, BTC returns over the estimation period preceding issuance are **significantly negative** (BTC total −1.4% before HUSD/BUSD events); for USDT, PAX and BUSD, the pre-event BTC CAAR is instead **significantly positive** (+0.88% in the 24h before USDT issuances, +0.54%/+0.47% in the 12h before PAX/BUSD issuances) — i.e. the pre-event direction is **not uniform across issuers**.
- Post-event: HUSD and BUSD show the strongest significant positive CAAR (0–12h and 0–24h); USDT shows a significant CAAR only for 0–24h (+0.63%); DAI and GUSD show significant 12h post-event effects despite small event counts (11 and 6 events respectively); USDC and GUSD show weaker/insignificant effects in some windows.

**Classification:** **MIXED**. The pooled, multi-currency result reads as modestly SUPPORTIVE of a short-horizon (hours) positive association around issuance, but (i) issuance-size is explicitly found not to matter (inconsistent with a simple liquidity-injection mechanism), (ii) the pre-event direction is heterogeneous and issuer-specific rather than a uniform "issuance follows crash" pattern, and (iii) no long-horizon, portfolio-level, or after-cost test is attempted.

---

### 1.4 Ante, L., Fiedler, I. & Strehle, E. (2021), "The impact of transparent money flows: Effects of stablecoin transfers on the returns and trading volume of Bitcoin," *Technological Forecasting and Social Change* 170:120851

**Status:** `ABSTRACT_ONLY` / `SECONDARY`. Confirmed **paywalled with no free copy**: queried the Unpaywall API directly on the article DOI (10.1016/j.techfore.2021.120851) → `"is_oa": false, "oa_status": "closed", "oa_locations": []`. No SSRN/working-paper mirror, no author-hosted PDF, and no BRL working-paper-series PDF for this specific paper could be located (the Blockchain Research Lab's own site lists the paper only as a journal citation with a ScienceDirect link, not a hosted PDF). All content below is therefore from the publicly visible abstract and third-party citing summaries, not the paper's own body/tables — no page/table citations are given because the underlying text was not read.

| Field | Answer (ABSTRACT_ONLY/SECONDARY) |
|---|---|
| 1. In/out-of-sample | In-sample (abstract does not describe an OOS test) |
| 2. Contemporaneous / predictive | Described (secondary) as examining returns/volume "in the hours around" transfers — reads as contemporaneous/short-window, not a forward-looking forecast |
| 3. Forecast horizon | Hours (per secondary summaries) |
| 4. Information timestamp | Described as **on-chain transfer** timestamp (not confirmed first-hand) |
| 5. Design | Event study (per abstract/secondary description) |
| 6. Transaction costs | Not modeled (per available description) |
| 7. BTC/ETH vs altcoins | BTC only |
| 8. Sample period | April 2019 – March 2020 (per secondary description, matching the companion 2021 FRL paper's sample) |
| 9. Post-2019 evidence | Yes (same window as above, per secondary description) |
| 10. Proprietary/vendor data | Description references "Whale Alert"-style large-transfer identification (≥$1m transfers); **could not confirm from primary text whether Whale Alert itself or an independent on-chain filter was used** — flagged `UNVERIFIED` pending full-text access |
| 11. Current entity/exchange labels | Unknown — not confirmed from primary text |
| 12. Survives benchmarks | Unknown — not confirmed from primary text |

**Supply measure used:** Stablecoin **transfers** ≥$1,000,000 (distinct from the companion paper's issuance-event measure) — per secondary description, 1,587 transfers analyzed.

**Reported finding (secondary, not independently verified):** "highly significant positive abnormal trading volume and significant abnormal returns in the hours around stablecoin transfers" (language from search-engine/ResearchGate summaries of the abstract, reproduced here only as a paraphrase, not a direct quote from the paper itself).

**Classification:** **SUPPORTIVE per secondary description only** — this paper could **not** be verified beyond its public abstract and should be weighted accordingly (i.e., essentially not usable as primary evidence for this audit; flagged for future full-text retrieval if institutional access becomes available).

---

### 1.5 Kristoufek, L. (2021), "Tethered, or Untethered? On the interplay between stablecoins and major cryptoassets," *Finance Research Letters* 43:101991

**Status:** `VERIFIED_FULLTEXT` (author's own institutional copy via UTIA/Czech Academy of Sciences library; PDF `Kristoufek_2021_FRL_UTIA.pdf`, 5pp; DOI 10.1016/j.frl.2021.101991)

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample, but with an explicit **time-stability/rolling-window robustness check** (closest thing to an OOS-style test in this set of papers) |
| 2. Contemporaneous / predictive | Forecast-error-variance-decomposition (FEVD) spillover framework — captures joint predictive/contemporaneous dynamics, not a single-horizon point forecast |
| 3. Forecast horizon | H=100 (period-ahead, daily data) for the global VAR; rolling 365-day windows re-estimated daily for the time-varying analysis |
| 4. Information timestamp | Daily aggregate supply levels (own-day close), not intraday |
| 5. Design | Regression-only: generalized VAR (Koop/Pesaran-Shin) + Diebold-Yilmaz-style spillover/FEVD, not an event study or trading rule |
| 6. Transaction costs | Not modeled (not a trading strategy) |
| 7. BTC/ETH vs altcoins | BTC, ETH, XRP (system of 3 major cryptoassets) vs. aggregate stablecoin supply |
| 8. Sample period | 1 Jan 2016 – 12 Jan 2021 (1,839 daily observations) |
| 9. Post-2019 evidence | Yes — sample runs through Jan 2021, explicitly spanning the 2020 stablecoin-supply growth period |
| 10. Proprietary/vendor data | No — free-float/current supply from coinmetrics.io (public) |
| 11. Current entity/exchange labels | Not applicable — uses aggregate total supply, no exchange-level wallet attribution |
| 12. Survives benchmarks | VAR system already nets out own-lag dynamics; AIC-selected lag length (3 lags on ~30-lag max grid) |

**Supply measure used:** **Aggregate free-float supply** summed across 9 stablecoins (USDT across Omni/ETH/TRX, BUSD, HUSD, PAX, USDC — free float; plus DAI, GUSD, SAI, TUSD — current supply), i.e. the broadest "total dollar liquidity" measure of any paper reviewed here.

**Key finding (quoted/paraphrased, main text pp.2–4):** "we find no evidence of stablecoins boosting the prices of other cryptoassets" and the supply/price dynamics instead "suggest they rather reflect increasing demand in investing into the cryptomarkets that gets materialized in demand for the 'digital fiat'" (abstract, verbatim ≤25 words each). The paper states directly: "the increase in stablecoins supply, i.e., new allowances, come after the price increases in the cryptomarkets, pointing towards the demand hypothesis of the stablecoins issuances." A rolling 365-day-window re-estimation (Fig. 2) shows this direction is **stable through time**, not an artifact of one sub-period — "the global picture of the stablecoins supply being boosted by the other cryptoassets price increases is translated into the local dynamics."

**Classification:** **CONTRADICTORY** to the predictive/supply-driven hypothesis; directly **SUPPORTIVE** of the demand-response/endogeneity interpretation, using the broadest supply aggregate and longest, most recent sample of any paper in this set.

---

### 1.6 Lyons, R.K. & Viswanath-Natraj, G. — two versions, treated separately per version-difference instruction

**(a) NBER Working Paper 27136 (May 2020), "What Keeps Stablecoins Stable?"**
**Status:** `VERIFIED_FULLTEXT` (PDF `LyonsViswanathNatraj_2020_NBERw27136.pdf`, 63pp)

This 2020 draft contains a section directly on point ("Stablecoin's role as a vehicle currency: Effect on cryptoasset prices," pp.30–32) that is **explicitly framed as a test of the Griffin & Shams (2020) hypothesis using aggregate rather than single-wallet data**.

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample |
| 2. Contemporaneous / predictive | Predictive (local-projection response of forward BTC/ETH price changes to lagged Tether secondary-market flow) |
| 3. Forecast horizon | h=0,1,2,... days (local projections) |
| 4. Information timestamp | Daily secondary-market issuance/flow (Omniexplorer/Etherscan) |
| 5. Design | Regression-only (local projections, Eq. 20) |
| 6. Transaction costs | Not modeled |
| 7. BTC/ETH vs altcoins | BTC and ETH |
| 8. Sample period | Full available sample, **explicitly re-run restricted to March 2017–March 2018** (the exact Griffin-Shams window) as a robustness check (footnote 33) |
| 9. Post-2019 evidence | Yes — the full-sample test extends beyond the 2017–18 episode |
| 10. Proprietary/vendor data | No — public blockchain flow data |
| 11. Current entity/exchange labels | No wallet-level exchange attribution; uses **aggregate** flow-to-secondary-market, explicitly noted by the authors as *not* capturing the single-wallet ("1LSg"-type) micro-flows Griffin-Shams identify |
| 12. Survives benchmarks | Controls for lagged BTC/ETH price changes, hash rate, and unique-address growth (network-value proxies from Bhambhwani et al. 2019) |

**Key finding (quoted, p.31):** "We find no significant effect on the prices of Bitcoin and Ethereum: These prices are not responding to Tether flows to the secondary market." The authors are explicit about scope: "Our analysis here is limited to aggregate issuance data, and is robust to the choice of sample period, finding qualitatively similar results by restricting our sample from March 2017 to March 2018" — i.e. **directly re-testing the Griffin-Shams window and failing to replicate an aggregate-level effect** — but they also concede: "Aggregate flows to the secondary market do not capture these microeconomic flows [to one wallet]" (footnote 33), i.e. this is **not** a claim that Griffin-Shams' single-entity finding is wrong, only that it does not generalize to the aggregate data.

**(b) Published version, *Journal of International Money and Finance* 131 (2023), art. no. corresponds to WRAP PDF**
**Status:** `VERIFIED_FULLTEXT` (PDF `LyonsViswanathNatraj_2023_WRAP.pdf`, 20pp, University of Warwick repository copy of the published JIMF article)

**Version difference (explicitly flagged per instructions):** the published 2023 JIMF version's focus **narrows entirely to peg-stability/arbitrage-design mechanics** (Tether's 2019 Omni→Ethereum migration and issuance decentralization; the DAI Peg Stability Module; WBTC merchant arbitrage) and **does not appear to retain the aggregate BTC/ETH-price non-effect test** from the 2020 NBER draft in its main text (searched for "Griffin"/"Shams"/"no systematic effect" in the WRAP PDF — found only in the literature-review/motivation paragraphs, not as a standalone empirical section with its own table). The crypto-price test above is therefore attributed to the **2020 working-paper version only**; readers should treat the 2020 and 2023 papers as related but not identical in scope.

**Supply measure used (2020 version):** aggregate net **secondary-market issuance/flow** of USDT (not raw grants); **(2023 version):** arbitrage **flow** volumes tied to peg-price deviations, not a return-predictor measure at all.

**Classification:** **CONTRADICTORY** to the aggregate-level predictive/supply-driven hypothesis (2020 version); **not directly on-topic** for the issuance→return question in its final 2023 published form (peg-mechanics paper).

---

### 1.7 Saggu, A. (2022), "The Intraday Bitcoin Response to Tether Minting and Burning Events: Asymmetry, Investor Sentiment, and 'Whale Alerts' on Twitter," *Finance Research Letters* 49:103096

**Status:** `VERIFIED_FULLTEXT` (author's own arXiv repost of the published paper with a retrospective preface, Jan 2025; PDF `Saggu_2022_arxiv2501.05232.pdf`, 18pp; journal DOI 10.1016/j.frl.2022.103096)

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample (full population of events, no holdout) |
| 2. Contemporaneous / predictive | Predictive at very short (intraday) horizon from event to forward return |
| 3. Forecast horizon | 5, 10, 15, 30, 60, and 1,440 minutes post-event |
| 4. Information timestamp | **Two distinct timestamps tested separately**: (i) the raw **on-chain minting/burning transaction time** (baseline model, Tables 3–4), and (ii) conditional on whether a **Whale Alert tweet** publicly announced that event (Table 5) — the paper's central finding is that the return response is concentrated in case (ii) |
| 5. Design | Event-study regression (dummy-interaction OLS/MM-estimator), full population of events, not a portfolio backtest |
| 6. Transaction costs | Not modeled |
| 7. BTC/ETH vs altcoins | BTC only |
| 8. Sample period | 6 Oct 2014 – 9 Jan 2021 (full history of USDT mint/burn events to that date) |
| 9. Post-2019 evidence | Yes, sample extends through Jan 2021, though event counts are not broken out by sub-period in the extracted text |
| 10. Proprietary/vendor data | **Yes for the key conditioning variable** — Whale Alert Twitter announcements (a specific third-party vendor feed); the on-chain-only baseline does not require vendor data |
| 11. Current entity/exchange labels | Not applicable (issuer-side mint/burn only, no exchange attribution) |
| 12. Survives benchmarks | Wald tests for coefficient-equality across minting/burning and sentiment states; robustness to a Baker et al. (2021) alternative jump classification (Table A1) |

**Supply measure used:** Discrete **minting and burning events** (any size; 367 minting + 220 burning events after merging same-timestamp duplicates), a raw count/dummy measure, not net supply level.

**Key statistics (VERIFIED_FULLTEXT, Tables 2–5, pp.9–12):** Bitcoin responds **positively and significantly** to minting events over 5–30-minute windows, declining after 60 minutes; the burning-event coefficient (β2) is "mostly positive but insignificant for all event windows" — a pure **asymmetry**, not a symmetric mint-up/burn-down relationship. Conditioning on sentiment (Table 4) shows the minting response is larger during periods of positive investor sentiment. **Critically (Table 5, p.12):** "Whale Alert published 222 of 367 USD₮ minting events (60%)... To account for the possibility that Bitcoin investors respond to Whale Alert tweets... Bitcoin investors usually **do not respond to USD₮ minting events that are not tweeted by Whale Alert** during periods of positive or negative sentiment" — i.e., the on-chain event alone is largely **not** priced; the effect is concentrated in the subset that is publicly, vendor-announced.

**Classification:** **SUPPORTIVE**, but with an important qualifier: this is evidence of a market reacting to a **public news announcement** (an information-arrival effect), not evidence that the underlying on-chain issuance itself carries exploitable forward information independent of disclosure. No out-of-sample test; entirely in-sample population statistics; R² and economic magnitude after costs are not reported.

---

### 1.8 Grobys, K. & Huynh, T.L.D. (2022), "When Tether says 'JUMP!' Bitcoin asks 'How low?'," *Finance Research Letters* 47:102644

**Status:** `VERIFIED_FULLTEXT` (University of Vaasa OSUVA institutional repository copy; PDF `GrobysHuynh_2022_FRL_OSUVA.pdf`, 11pp; tables parsed cleanly in native reading order, verified against `page.get_text("words")` coordinates)

| Field | Answer |
|---|---|
| 1. In/out-of-sample | In-sample |
| 2. Contemporaneous / predictive | Predictive: lagged USDT jump/return → next-day BTC return |
| 3. Forecast horizon | 1 trading day ahead |
| 4. Information timestamp | Daily aggregation of hourly Bitfinex USDT/BTC prices; jump identified per trading day via Barndorff-Nielsen-Shephard bipower variation at hourly frequency, then used as a lagged daily predictor |
| 5. Design | Regression-only (OLS with jump-dummy interactions; VAR-based Granger-causality test as robustness) |
| 6. Transaction costs | Not modeled |
| 7. BTC/ETH vs altcoins | BTC only, vs. USDT, both priced on Bitfinex |
| 8. Sample period | November 2018 – June 2021 (992 daily observations from hourly data; regressions run on 922 obs after lag construction) |
| 9. Post-2019 evidence | Yes — entire sample is post-2018, explicitly **post**-dating the Griffin-Shams episode |
| 10. Proprietary/vendor data | No — Bitfinex exchange price data only |
| 11. Current entity/exchange labels | Not applicable (price-based jump detection, no wallet attribution) |
| 12. Survives benchmarks | Robust to volatility controls (Threshold-GARCH, Table A2), to lagged-return controls, and to an alternative jump-classification method (Baker et al. 2021, Table A1); Granger-causality confirmed via VAR-interaction Wald test (χ²=8.364, df=4) |

**Supply measure used:** Binary **jump indicator** in the USDT/USD price series (a proxy for abrupt large mint/burn-driven price moves on Bitfinex), interacted with the lagged USDT return — not a level or volume measure of issuance.

**Key statistic (VERIFIED_FULLTEXT, Table 2, journal p.4, "Prediction of Bitcoin returns with USDT and BTC jumps"):** the interaction term "Positive USDT Jump(t−1) × USDT Return(t−1)" is **−3.647 (t=−1.918, Model 3)**, **−3.934 (t=−1.993, Model 4)**, and **−8.4857 (t=−4.2367, Model 5)** — i.e. a positive Tether jump combined with a positive prior-day Tether return predicts a **negative**, not positive, next-day Bitcoin return, ranging from −3.65% to −8.49% as stated in the abstract. Model R² across all five specifications in Table 2 remains low (0.000 to 0.021), meaning the effect is statistically detectable but explains very little day-to-day return variance.

**Classification:** **SUPPORTIVE of predictability in a statistical sense, but the sign is opposite to the naive "more USDT printed → BTC up" narrative**, and the finding is a genuinely distinct, not-yet-reconciled result relative to Griffin-Shams' positive-sign, single-episode finding — a useful falsification-relevant data point on its own (same-direction predictors, opposite-sign, different-sample outcomes should reduce confidence in either being a stable, tradeable effect). Weakness: economically tiny R², daily-frequency Bitfinex-only sample, no cost modeling, no OOS test.

---

### 1.9 Grobys, K., Junttila, J.-P., Kolari, J.W. & Sapkota, N. (2021), "On the Stability of Stablecoins," *Journal of Empirical Finance* 64:207–223

**Status:** `VERIFIED_FULLTEXT` (University of Jyväskylä JYX open-access repository copy, CC-BY-4.0; PDF `GrobysJuntillaKolariSapkota_2021_JEF_JYX.pdf`, 18pp)

**Note on relevance:** this paper studies **volatility**, not returns or issuance/supply levels, so it does not map cleanly onto the 12-field template built for return-predictor papers. It is included because it bears directly on the **direction-of-causality** question using an independent methodology (power-law/Granger-causality on volatility) and independent sample.

**Key finding (quoted, abstract & pp. body, sample to 22 Nov 2020, BTC sample from 29 Apr 2013):** "the volatilities of stablecoins are statistically unstable and contemporaneously respond to Bitcoin volatility, whereas Bitcoin volatility exhibits Granger-causal effects on the volatilities of stablecoins" — explicitly **not** the reverse: "we conclude that... the volatilities of stablecoins (Tether) do not spillover to Bitcoin volatility... we find strong volatility spillover effects in a Granger-causal sense from Bitcoin volatility to volatilities of stablecoins." This corroborates Kristoufek's (2021) direction-of-causality finding using a wholly different variable (volatility rather than supply level) and methodology (power-law/Granger rather than VAR-FEVD).

**Classification:** **CONTRADICTORY** to a stablecoin→Bitcoin predictive channel (for volatility; by extension, weak corroborating evidence against a supply-driven return channel, since the same BTC-leads-stablecoin directionality recurs across two independent studies and two independent variables).

---

### 1.10 Baumöhl, E. & Výrost, T. (2020), "Stablecoins as a crypto safe haven? Not all of them!," EconStor/ZBW Preprint 215484

**Status:** `VERIFIED_FULLTEXT` (EconStor/ZBW direct bitstream; PDF `BaumohlVyrost_2020_EconStor.pdf`, 11pp)

**Note on relevance:** this paper tests **safe-haven/hedge/diversifier properties** (quantile-coherency cross-spectral correlation with BTC/ETH/XRP/BCH/LTC), not issuance-driven return prediction. Included as required background on structural heterogeneity across "stablecoins" as a category.

**Key finding:** using 1-minute volume-weighted data across 18 exchanges, "only TUSD, PAX, and GUSD can serve as safe havens" against major non-stable cryptoassets, while USDT, USDC and DAI do **not** show the same property — i.e., **not all stablecoins behave alike**, a caution against treating "aggregate stablecoin supply" as a economically homogeneous quantity (relevant to answer (c) below).

**Classification:** Not directly SUPPORTIVE/CONTRADICTORY of the return-predictor hypothesis (different question); relevant context only.

---

### 1.11 Ahmed, R. & Aldasoro, I. (2025), "Stablecoins and safe asset prices," BIS Working Paper 1270 / Cleveland Fed conference draft

**Status:** `VERIFIED_FULLTEXT`. The official `bis.org/publ/work1270.pdf` URL returned the BIS **website navigation shell**, not the paper (confirmed by opening the downloaded "PDF" with PyMuPDF and finding only site-navigation text — "Skip to main content... About... Research & publications..." — across all 19 pages; this file was **discarded**, not used as a source). A working free mirror was located and used instead: the authors' own conference-paper PDF hosted by the Cleveland Fed (`AhmedAldasoro_2025_ClevelandFedMirror.pdf`, 32pp, August 2025 draft, matches the BIS WP abstract).

**Note on relevance:** this paper studies the effect of **dollar-backed stablecoin flows on short-term US Treasury yields**, not crypto returns. Included per the task's explicit instruction to cover BIS/Fed/IMF work on stablecoin demand composition and safe-asset-price spillovers.

**Key finding:** using daily data 2021–2025 and instrumented local projections, "a 2-standard deviation inflow into stablecoins lowers 3-month Treasury yields by 2-2.5 basis points within 10 days," with asymmetric, strengthening-over-time effects, and the yield impact is larger for USDT than USDC "consistent with their relative size." This documents a **real, growing macro-financial channel running from stablecoin flows into traditional safe-asset markets** — reinforcing that stablecoin issuance is plausibly driven by (and feeds back into) broad safe-asset/liquidity demand dynamics that are largely orthogonal to any single crypto-return-prediction mechanism.

**Classification:** Not a direct test of crypto-return predictability; relevant macro-structural context for the endogeneity question (answer (c) below).

---

### 1.12 Ahmed, R., Clouse, J.A., Natalucci, F., Rebucci, A. & Sun, G. (2025), "Stablecoins: A Revolutionary Payment Technology with Financial Risks," NBER Working Paper 34475

**Status:** `VERIFIED_FULLTEXT` (PDF `NBER_w34475_...pdf`, 54pp)

**Note on relevance:** background/context paper (survey + original "podcast survey of experts" text-analysis methodology on stablecoin use cases), not a returns-predictability study. Directly responsive to the task's explicit request re: GENIUS Act (2025) and demand-composition evolution.

**Key findings relevant to structural stability of the "issuance = crypto purchasing power" mechanism:** the GENIUS Act (signed 2025) requires full 1:1 backing by designated USD assets and creates a formal federal/state dual regulatory track; the authors' own survey of expert commentary identifies the top use cases as "a medium of exchange for crypto trading, a domestic or international means of payment," "store of value" (including "in dollarized economies"), and DeFi collateral — i.e., **multiple, growing non-trading use cases** alongside the original crypto-trading-liquidity role. Market concentration: "just two issuers, Circle and Tether, [are] responsible for over 85 percent" of the ~$270bn USD-stablecoin market (Aug 2025).

**Classification:** Context only; supports answer (c) (structural dilution of the issuance→crypto-purchasing-power link as payments/EM-dollarization/DeFi use cases grow).

---

### 1.13 Barthélemy, J., Gardin, P. & Nguyen, B. (2023, rev.), "Stablecoins and the Financing of the Real Economy," Banque de France Working Paper 908

**Status:** `VERIFIED_FULLTEXT` (PDF `BarthelemyGardinNguyen_2023_BdF_WP908.pdf`, 64pp; SSRN 10.2139/ssrn.4359660)

**Note on relevance:** studies whether stablecoin reserve-asset demand affects the **US commercial paper (CP) market**, not crypto returns. Directly relevant to the endogeneity chain: it documents an additional causal link **downstream of** stablecoin growth (stablecoin growth → CP issuance), reinforcing that stablecoin-supply growth is treated in this literature as the **causally prior, demand-driven** variable, with effects flowing outward into TradFi rather than a variable that is itself driven by an intent to move crypto prices.

**Key finding (abstract, quoted ≤25 words):** "CP issuers catered to the additional demand from stablecoins by issuing more [CP], with no impact on CP rates," identified using "plausibly exogenous changes in reserve assets" policy across stablecoins (e.g., timing of when a stablecoin stopped using CP as reserve backing) to support a causal (not merely correlational) reading.

**Classification:** Context only; supports the "issuance is a downstream/response variable" reading, applied here to TradFi rather than crypto markets.

---

### 1.14 [Lower-confidence / quality-flagged] "The Impact of Stablecoins on Bitcoin Returns: An Empirical Analysis Based on VAR Model," *Academic Journal of Management and Social Sciences* (DR Press platform), 2025

**Status:** `VERIFIED_FULLTEXT` for content (PDF `drpress_VAR_StablecoinsBitcoinReturns_2025.pdf`, 8pp) but **journal-quality UNVERIFIED** — "Academic Journal of Management and Social Sciences" on the drpress.org platform could not be confirmed as an indexed, peer-reviewed venue within this audit's budget (no ISSN/indexing record checked; drpress.org hosts a large number of rapidly-published conference-style short papers). Treat all numbers below with **materially lower confidence** than the peer-reviewed FRL/JoF/JEF/JIMF papers above.

**Important scope distinction:** despite the task's framing question being about issuance/supply, this paper's actual predictor is **peg deviation** (percentage deviation of USDT/USDC market price from the $1.00 peg), **not** issuance, net supply, or mint/burn volume. It is a genuinely different variable (a demand/liquidity-stress signal, closer in spirit to Lyons-Viswanath-Natraj's arbitrage work than to a supply/issuance measure) and is included only because the task explicitly asked for any 2023–2026 "stablecoin supply"/"predict" hits and this was the closest recent match found.

**Reported design:** daily VAR (USDT-BTC system, 5 lags; USDC-BTC system, 4 lags), sample Jan 2020 – Aug 2025, Granger-causality tests, impulse responses. **Reported finding:** "USDT and USDC deviations significantly Granger-cause Bitcoin returns, whereas the reverse causality is weaker," with impulse responses showing "stablecoin deviations first produce positive shocks to Bitcoin returns, followed by negative corrections."

**Classification:** **Excluded from the main SUPPORTIVE/CONTRADICTORY tally below** given (i) the variable mismatch (peg deviation ≠ issuance/supply) and (ii) unverified journal quality; listed here only for completeness per the task's explicit search terms, and because in-sample Granger-causality (without cost, without portfolio construction, without true holdout) is a weak evidentiary standard regardless of venue.

---

### 1.15 Ante, L., Fiedler, I., Willruth, J.M. & Steinmetz, F. (2023), "A Systematic Literature Review of Empirical Research on Stablecoins," *FinTech* 2(1):3-47 (MDPI)

**Status:** `SECONDARY` (MDPI's own PDF endpoint returned an Akamai "Access Denied" error page on direct fetch; not re-attempted via browser given time budget — this is a survey/meta-paper, not primary evidence, so full-text access was deprioritized). Per search-engine summaries: reviews 22 peer-reviewed empirical stablecoin articles, clustering them into (i) stability/volatility/safe-haven studies, (ii) interrelations with Bitcoin/other cryptoassets, (iii) macro-factor relationships. Not used to support any classification below; listed for bibliographic completeness only.

---

## 2. Summary tables

### 2.1 SUPPORTIVE (issuance/mint/transfer → predicts subsequent returns)

| Paper | Horizon | Magnitude | Scope limitation |
|---|---|---|---|
| Griffin & Shams (2020) | Hourly/3h; also EOM (monthly) | 3.9–8.1bp/100BTC flow; 58.8% of 13-month BTC return from top 1% of hours; causal 2SLS 26–65bp | Single wallet cluster, single exchange, single 13-month episode (2017–18); EOM effect loses significance ex-2 months |
| Ante, Fiedler & Strehle (2021, issuances) | 0–24h post-event | CAAR +0.33% to +0.69% pooled across 4 coins | Issuance-size irrelevant to effect; heterogeneous/non-uniform pre-event direction by issuer; no cost/OOS test |
| Ante, Fiedler & Strehle (2021, transfers) | Hours | "Significant abnormal returns" (secondary description only) | **Full text not verified — ABSTRACT_ONLY** |
| Saggu (2022) | 5–30 min | Positive, significant only for minting + only when Whale-Alert-announced | Effect requires public vendor disclosure, not the on-chain event alone; 40% of mints never tweeted show no response |
| Grobys & Huynh (2022) | 1 day | −3.65% to −8.49% (note: **negative** sign) | Opposite sign to the "naive" narrative; R²≤0.021; single-exchange (Bitfinex) daily data |

### 2.2 CONTRADICTORY (no effect, or reverse-direction causality: crypto returns → stablecoin supply)

| Paper | Sample | Finding |
|---|---|---|
| Wei (2018) | Dec 2016–Feb 2018, daily | No effect of grants on BTC returns; grants follow negative returns (reverse-causality-consistent) |
| Kristoufek (2021) | Jan 2016–Jan 2021, daily, 9 stablecoins aggregated | "No evidence of stablecoins boosting the prices of other cryptoassets"; price rises precede supply increases; stable across rolling 365-day windows |
| Lyons & Viswanath-Natraj (2020 NBER draft) | Full sample + exact 2017–18 replication of Griffin-Shams | "No significant effect on the prices of Bitcoin and Ethereum" from aggregate secondary-market Tether flow |
| Grobys, Junttila, Kolari & Sapkota (2021) | Apr 2013(BTC)/–Nov 2020, volatility not returns | Stablecoin volatility does not Granger-cause BTC volatility; BTC volatility Granger-causes stablecoin volatility (reverse direction) |

### 2.3 MIXED / context-only (not classified either way)

Ante, Fiedler & Strehle (2021, issuances) — see above, listed in both tables given genuinely heterogeneous per-issuer results. Baumöhl & Výrost (2020), Lyons & Viswanath-Natraj (2023 published version), Ahmed & Aldasoro (2025), NBER WP 34475, Barthélemy/Gardin/Nguyen (2023) — background/context, not direct return-predictor tests. DR Press VAR paper (2025) — excluded (variable mismatch + unverified venue). Ante, Fiedler, Willruth & Steinmetz (2023) — survey only, SECONDARY.

---

## 3. Answers to the four questions

**(a) Which causal interpretation — response vs. predictor — has stronger empirical/theoretical support, and at what horizon?**

The **demand-response ("pulled") interpretation has the broader and more recent empirical support**, especially at daily-and-longer horizons and using aggregate (multi-stablecoin, multi-year) data: Wei (2018), Kristoufek (2021, the longest and most recent sample of any paper here — through Jan 2021, 9 stablecoins), Lyons & Viswanath-Natraj's own 2020 aggregate re-test of the *exact* Griffin-Shams window, and Grobys/Junttila/Kolari/Sapkota's (2021) independent volatility-based Granger-causality test all converge on the same directionality: crypto price/volatility moves **lead**, and stablecoin supply/volatility **follows**. The **supply-push ("pushed") interpretation's strongest evidence is Griffin & Shams (2020)**, which remains an important, carefully-executed paper, but its effect is identified almost entirely within **one wallet cluster, one exchange, and one 13-month historical episode (March 2017–March 2018)** that has not been replicated in aggregate data by a subsequent, closely-related study using the same window (Lyons & Viswanath-Natraj 2020, footnote 33). At the **intraday/hourly horizon**, event studies (Saggu 2022; Ante et al. 2021 issuances) do find statistically significant short-lived positive reactions around minting/issuance events, but Saggu's own results show this is conditional on **public disclosure** (Whale Alert) rather than the raw on-chain event, which is a materially weaker and more fragile claim than "issuance predicts returns" — it is closer to "markets react to salient news," which is a much narrower, harder-to-monetize edge (60% Whale-Alert coverage, timing/latency-dependent, likely arbitraged away by anyone already watching Whale Alert). **Net assessment: response-side evidence dominates at daily-to-monthly horizons and in the most recent, broadest samples; predictor-side evidence is real but narrow, episode-specific, and partially conditional on public disclosure rather than the underlying on-chain fact.**

**(b) Is there ANY evidence of long-only, weekly/monthly, after-cost BTC/ETH value from aggregate stablecoin supply growth? Any OOS test at all?**

**No.** Across all 14 sources audited, **no paper constructs a long-only weekly or monthly rebalanced portfolio conditioned on stablecoin supply/issuance growth and reports a return net of realistic transaction costs.** The closest approximations are: (i) Griffin & Shams' EOM/monthly regression (Table VII) — but this is a monthly-frequency return-attribution regression, not a tradeable strategy, has no cost accounting, and loses significance ex-2 outlier months; (ii) Kristoufek's (2021) VAR/FEVD framework, which characterizes spillover shares, not tradeable returns; (iii) the DR Press (2025, quality-unverified) paper's claim of "out-of-sample forecasts over 472 observations," which is a peg-deviation forecasting-error exercise, not a stablecoin-issuance trading strategy, and whose venue quality could not be confirmed. **No genuine out-of-sample (train/test-split, walk-forward, or truly held-out) test of a stablecoin-issuance-based trading rule was found in this literature at all.** This is a clear, confirmed gap — consistent with this being Stage 0 (audit) rather than a promotable candidate.

**(c) Has the effect (if any) decayed after 2018–2020?**

The evidence is consistent with **decay/non-replication rather than persistence**: (i) Griffin & Shams' mechanism is tied to a specific, historically contingent microstructure (one dominant wallet, thin Tether-USD arbitrage via Kraken, pre-reform Omni-layer issuance) that Lyons & Viswanath-Natraj (2023) document was **structurally altered by 2019 reforms** (migration to Ethereum, decentralization of issuance) explicitly intended to improve arbitrage efficiency; (ii) the papers with the most recent samples and the broadest supply definitions (Kristoufek 2021 through Jan 2021; Grobys/Junttila/Kolari/Sapkota through Nov 2020) find the demand-response direction, not the supply-push direction, and Ante et al.'s (2021) post-2019 event-study sample finds only small, heterogeneous, largely disclosure-conditional effects rather than the large, entity-concentrated effects of the 2017–18 episode; (iii) structurally, the composition of stablecoin demand has diversified since 2020 — NBER WP 34475's own expert survey identifies payments, remittances, EM-dollarization store-of-value, and DeFi collateral as growing, independent use cases alongside crypto-trading liquidity, and the 2025 GENIUS Act imposes full-reserve/regulatory requirements that further formalize stablecoins as payment instruments rather than purely speculative crypto "dry powder." Both effects would mechanically weaken any "new stablecoin supply → imminent crypto buying" link over time, independent of any change in market efficiency.

**(d) Evidence on the pre-event pattern (issuance following price declines) — mechanical mean-reversion or new information?**

The weight of evidence favors a **mechanical/demand-timing reading over a new-information reading**, though the picture is not unanimous: Wei (2018) finds grants follow negative returns but have **no** effect on subsequent returns — the textbook signature of reverse causality/demand-timing, not information content. Kristoufek (2021) and Grobys/Junttila/Kolari/Sapkota (2021), using two different variables (supply level; volatility) and two different methodologies (VAR-FEVD; power-law Granger-causality) both independently find crypto-side moves **lead** stablecoin-side moves, not the reverse — consistent with issuance/volatility responding mechanically to prior crypto price action (e.g., investors and/or issuers replenishing stablecoin float after a drawdown in anticipation of re-entry or redemption demand) rather than issuance carrying fresh, forward-looking price information. Griffin & Shams (2020) is the clearest counter-case: they explicitly test and reject pure mechanical reversion for their specific top-1%-flow hour sample via a matched-sample placebo (hours with similarly negative preceding returns but *without* high flow show ~0% subsequent return, statistically distinct from the ~+1.2% found after high-flow hours) — but this rejection is scoped to their narrow wallet/exchange/episode sample, not the aggregate market. Ante et al.'s (2021) issuance-event data show the pre-event pattern is **not even directionally consistent across issuers** (HUSD/BUSD preceded by significant BTC declines; USDT/PAX/BUSD preceded by significant BTC *increases*), which itself argues against a single, universal "issuance follows crash" mechanism and points toward issuer-specific liquidity/redemption-cycle timing rather than a market-wide informational signal.

---

## 4. Bibliography (with DOI/URL and local filename where downloaded)

1. Wei, W.C. (2018). "The impact of Tether grants on Bitcoin." *Economics Letters* 171:19–22. DOI (journal): 10.1016/j.econlet.2018.07.001 (not independently confirmed digit-for-digit; cite via SSRN DOI 10.2139/ssrn.3175876, https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3175876). Local: `Wei_2018_SSRN3175876.pdf`.
2. Griffin, J.M. & Shams, A. (2020). "Is Bitcoin Really Untethered?" *The Journal of Finance* 75(4):1913–1964. DOI: 10.1111/jofi.12903. Open access. Local text conversion: `GriffinShams_2020_JoF_fulltext_htmlrender.txt`.
3. Ante, L., Fiedler, I. & Strehle, E. (2021). "The influence of stablecoin issuances on cryptocurrency markets." *Finance Research Letters* 41:101867. https://www.sciencedirect.com/science/article/pii/S1544612320316810. Local (working-paper text, BRL WP No. 11): `AnteFiedlerStrehle_2021_issuances_BRLWP11.pdf`.
4. Ante, L., Fiedler, I. & Strehle, E. (2021). "The impact of transparent money flows: Effects of stablecoin transfers on the returns and trading volume of Bitcoin." *Technological Forecasting and Social Change* 170:120851. DOI: 10.1016/j.techfore.2021.120851. **Confirmed closed access via Unpaywall API; no local copy obtained.**
5. Kristoufek, L. (2021). "Tethered, or Untethered? On the interplay between stablecoins and major cryptoassets." *Finance Research Letters* 43:101991. DOI: 10.1016/j.frl.2021.101991. Local: `Kristoufek_2021_FRL_UTIA.pdf`.
6. Lyons, R.K. & Viswanath-Natraj, G. (2020). "What Keeps Stablecoins Stable?" NBER Working Paper 27136. https://www.nber.org/papers/w27136. Local: `LyonsViswanathNatraj_2020_NBERw27136.pdf`.
7. Lyons, R.K. & Viswanath-Natraj, G. (2023). "What keeps stablecoins stable?" *Journal of International Money and Finance* 131. https://wrap.warwick.ac.uk/id/eprint/173269/. Local: `LyonsViswanathNatraj_2023_WRAP.pdf`.
8. Saggu, A. (2022). "The Intraday Bitcoin Response to Tether Minting and Burning Events: Asymmetry, Investor Sentiment, and 'Whale Alerts' on Twitter." *Finance Research Letters* 49:103096. DOI: 10.1016/j.frl.2022.103096. Local (author arXiv repost): `Saggu_2022_arxiv2501.05232.pdf`.
9. Grobys, K. & Huynh, T.L.D. (2022). "When Tether says 'JUMP!' Bitcoin asks 'How low?'" *Finance Research Letters* 47:102644. https://www.sciencedirect.com/science/article/pii/S1544612321005778. Local: `GrobysHuynh_2022_FRL_OSUVA.pdf`.
10. Grobys, K., Junttila, J.-P., Kolari, J.W. & Sapkota, N. (2021). "On the Stability of Stablecoins." *Journal of Empirical Finance* 64:207–223. Local: `GrobysJuntillaKolariSapkota_2021_JEF_JYX.pdf`.
11. Baumöhl, E. & Výrost, T. (2020). "Stablecoins as a crypto safe haven? Not all of them!" EconStor/ZBW Preprint 215484. https://www.econstor.eu/handle/10419/215484. Local: `BaumohlVyrost_2020_EconStor.pdf`.
12. Ahmed, R. & Aldasoro, I. (2025). "Stablecoins and safe asset prices." BIS Working Paper 1270 / SSRN 10.2139/ssrn.5242448. Local (Cleveland Fed conference mirror, content-verified identical to BIS abstract): `AhmedAldasoro_2025_ClevelandFedMirror.pdf`. **Caveat:** the official `bis.org/publ/work1270.pdf` URL served the BIS website navigation shell, not the paper — that file was discarded.
13. Ahmed, R., Clouse, J.A., Natalucci, F., Rebucci, A. & Sun, G. (2025). "Stablecoins: A Revolutionary Payment Technology with Financial Risks." NBER Working Paper 34475. Local: `NBER_w34475_Stablecoins_Ahmed_Clouse_Natalucci_Rebucci_Sun_2025.pdf`.
14. Barthélemy, J., Gardin, P. & Nguyen, B. (2023, rev.). "Stablecoins and the Financing of the Real Economy." Banque de France Working Paper 908 / SSRN 10.2139/ssrn.4359660. Local: `BarthelemyGardinNguyen_2023_BdF_WP908.pdf`.
15. [Quality-unverified] "The Impact of Stablecoins on Bitcoin Returns: An Empirical Analysis Based on VAR Model." *Academic Journal of Management and Social Sciences* (DR Press), 2025. https://drpress.org/ojs/index.php/ajmss/article/view/32611. Local: `drpress_VAR_StablecoinsBitcoinReturns_2025.pdf`.
16. Ante, L., Fiedler, I., Willruth, J.M. & Steinmetz, F. (2023). "A Systematic Literature Review of Empirical Research on Stablecoins." *FinTech* 2(1):3–47. https://www.mdpi.com/2674-1032/2/1/3. **SECONDARY only — full-text fetch blocked (Akamai access-denied), not re-attempted.**

**Papers named in the task brief that were searched but not separately treated above:** "Wang, Ma & Wu (2020)" — no matching paper could be identified under this exact author combination despite multiple targeted searches; likely a mis-specification or a paper not indexed under this name in the sources searched (Semantic Scholar, Google via WebSearch, IDEAS/RePEc). Not fabricated; flagged as not found.

