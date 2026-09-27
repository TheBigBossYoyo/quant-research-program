# V1 — U.S. Treasury Duration UCITS ETF Deployment Metadata (Phase 11C Stage 0)

Retrieval date for all facts below: 2026-09-27, unless a source's own "as of" date is quoted.
No performance, price, NAV history, return, yield-history, or chart data is recorded anywhere in
this file. Where a source is a known review/opinion aggregator or third-party listing rather than
the issuer/exchange/broker itself, it is tagged `[SECONDARY]`. Unconfirmed items are tagged
`[UNVERIFIED]`. See `V1_snapshots/INDEX.md` for the full URL log.

Tag key: `[ISSUER, url]` = iShares/BlackRock or other fund manufacturer's own page.
`[EXCHANGE, url]` = exchange/venue listing. `[T212, url]` = Trading 212 page or listing.
`[SECONDARY]` = third-party aggregator (justETF, WebSearch synthesis, community forum).
`[UNVERIFIED]` = could not be confirmed from any source in the time available.

---

## Bucket: SHORT — 1-3 Year U.S. Treasuries

### Line 1: iShares $ Treasury Bond 1-3yr UCITS ETF — USD (Dist)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares $ Treasury Bond 1-3yr UCITS ETF | [ISSUER, ishares.com/uk/.../251715] |
| Share class | USD (Distributing) | [SECONDARY, justETF IE00B14X4S71] |
| Ticker — LSE | IDBT (USD line), IBTS (GBX line) | [SECONDARY, justETF] |
| Ticker — Xetra / gettex / Stuttgart | IUSU | [SECONDARY, justETF] |
| Ticker — Borsa Italiana | IBTS | [SECONDARY, justETF] |
| Ticker — Euronext Amsterdam | IBTS | [SECONDARY, justETF] |
| Ticker — SIX | IBTS | [SECONDARY, justETF] |
| ISIN | IE00B14X4S71 (WKN A0J202) | [SECONDARY, justETF] |
| Trading currency (per line) | EUR / USD / GBP / MXN depending on venue | [SECONDARY, justETF] |
| Fund base currency | USD | [ISSUER]/[SECONDARY] |
| Hedged? | No (this line) | [SECONDARY, justETF] |
| Acc/Dist | Distributing, semi-annual | [SECONDARY, justETF] |
| Fund inception | 2 June 2006 | [ISSUER, ishares.com product page] |
| Share-class inception | Not separately confirmed (same as fund launch for this original line) | [UNVERIFIED] |
| TER/OCF | 0.07% p.a. | [SECONDARY, justETF]; consistent across multiple sources |
| Benchmark index | ICE U.S. Treasury 1-3 Year Bond Index (index provider changed from Barclays US Treasury 1-3 Year Term Index, effective 26 May 2016) | [ISSUER, ishares.com product page] |
| Benchmark rules | US-dollar-denominated UST bonds, 1-3yr remaining maturity band | [ISSUER] |
| Rebalancing frequency | Not confirmed (ICE Treasury index family typically rebalances monthly) | [UNVERIFIED] |
| Effective duration / WAM | Not retrieved (fetch of official page returned only partial fields; factsheet PDF was unparseable binary) | [UNVERIFIED] |
| Number of holdings | 92 | [SECONDARY, justETF, undated snapshot] |
| Replication method | Physical (representative sampling) | [SECONDARY, justETF] |
| Domicile | Ireland | [ISSUER]/[SECONDARY] |
| Fund size / AUM | ~EUR 2,197m (justETF snapshot) / a separately dated WebSearch summary cited ~GBP 1.93bn — these are not necessarily the same date or currency base; treat as approximate and time-varying, not reconciled | [SECONDARY] |
| Trading 212 availability | Yes — https://www.trading212.com/trading-instruments/invest/IBTS.GB (title confirms "Invest in iShares USD Treasury Bond 1-3yr (Dist), London Stock Exchange: IBTS ETF — Commission-Free Investing") | [T212, trading212.com/.../IBTS.GB] — direct page fetch returned HTTP 403 (bot-protected); confirmed only via search-index title, not full page content |
| Fractional shares | Not directly confirmed for this line; Trading 212 generally supports fractional shares for ETFs per prior account-fact verification (see MEMORY: trading212-verified-facts) | [SECONDARY]/carried-over fact |

### Line 2: iShares $ Treasury Bond 1-3yr UCITS ETF — USD (Acc)

| Field | Value | Source |
|---|---|---|
| ISIN | IE00B3VWN179 (WKN A0X8SG) | [SECONDARY, WebSearch/justETF listing] |
| Ticker — LSE | IBTA | [T212, trading212.com/.../IBTA.GB] |
| Acc/Dist | Accumulating | [SECONDARY] |
| Other fields | Same fund/benchmark/TER/domicile as Line 1 (different share class) | inferred |
| Trading 212 availability | Yes — https://www.trading212.com/trading-instruments/invest/IBTA.GB (title confirms) | [T212] — 403 on direct fetch, confirmed via index title only |

### Line 3: iShares $ Treasury Bond 1-3yr UCITS ETF — EUR Hedged (Acc)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares USD Treasury Bond 1-3yr UCITS ETF EUR Hedged (Acc) | [SECONDARY, justETF IE00BDFK1573] |
| Ticker — Xetra/gettex | 2B7S | [SECONDARY, justETF] |
| Ticker — LSE | IBTE | [SECONDARY, justETF]; also appears in a Trading 212 community-forum thread title | [T212 community, UNVERIFIED re: availability] |
| ISIN | IE00BDFK1573 (WKN A2JE39) | [SECONDARY, justETF] |
| Trading currency | EUR | [SECONDARY, justETF] |
| Fund base currency | USD at fund level; EUR is the hedged share-class currency (justETF's own "base currency" field said EUR, which conflates share-class currency with fund base currency — flagged as a labeling inconsistency, not a confirmed fact) | [SECONDARY]/[UNVERIFIED — reconciliation needed] |
| Hedged? | Yes, to EUR | [SECONDARY, justETF] |
| Acc/Dist | Accumulating | [SECONDARY, justETF] |
| Share-class inception | 10 April 2018 | [SECONDARY, justETF] |
| TER/OCF | 0.10% p.a. | [SECONDARY, justETF] |
| Benchmark index | ICE US Treasury 1-3 Year (EUR Hedged) | [SECONDARY, justETF] |
| Number of holdings | 92 | [SECONDARY, justETF] |
| Replication | Physical (sampling) | [SECONDARY, justETF] |
| Domicile | Ireland | [SECONDARY, justETF] |
| Fund size / AUM | ~EUR 1,226m | [SECONDARY, justETF] |
| Trading 212 availability | **CONFLICTING** — justETF's broker-comparison table said "Yes"; but a Trading 212 Community thread titled "iShares USD Treasury Bond 1-3yr UCITS ETF EUR Hedged (Acc)" was found under the forum's requests-style URL pattern, which is ambiguous between "already added, discussion" and "still a pending feature request." No confirmed live `trading212.com/trading-instruments/invest/IBTE.*` page was found via search index (unlike IBTS/IBTA/IDTL/DTLE/IBB1, which do have such confirmed pages). **Marked UNVERIFIED/CONFLICTING — do not treat as confirmed available.** | [T212]/[UNVERIFIED] |

### Line 4: iShares $ Treasury Bond 1-3yr UCITS ETF — GBP Hedged (Dist)

| Field | Value | Source |
|---|---|---|
| Ticker | IBTG (LSE) | [T212, trading212.com/.../IBTG.GB — confirmed live "Invest in..." page]; [SECONDARY, Hargreaves Lansdown company page] |
| ISIN | Not confirmed | [UNVERIFIED] |
| Hedged | Yes, to GBP | [SECONDARY] |
| Trading 212 availability | Yes, live page confirmed by title | [T212] — 403 on direct fetch, title-only confirmation |
| Other fields | Not retrieved | [UNVERIFIED] |

### Non-iShares alternative (SHORT bucket)

- **SPDR Bloomberg 1-3 Year U.S. Treasury Bond UCITS ETF USD Unhedged (Dist)** — ISIN IE00BC7GZJ81, ticker SYBW/TRS3, launched 27 Aug 2013, Ireland-domiciled. [SECONDARY, justETF/WebSearch]
- **Xtrackers II US Treasuries 1-3 UCITS ETF 1D** — ISIN LU0429458895, ticker DBX0CU, Luxembourg-domiciled (physical replication per Xtrackers standard line naming). [SECONDARY, justETF/DWS listing]

---

## Bucket: INTERMEDIATE — 7-10 Year U.S. Treasuries

### Line 1: iShares $ Treasury Bond 7-10yr UCITS ETF — USD (Dist)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares $ Treasury Bond 7-10yr UCITS ETF | [ISSUER, ishares.com/uk/.../251716] |
| Ticker | IBTM (LSE) | [ISSUER]/[SECONDARY, justETF IE00B1FZS798] |
| ISIN | IE00B1FZS798 (WKN A0LGP4) | [SECONDARY, justETF] |
| Trading currency | USD (primary), also GBP/MXN variants across venues | [SECONDARY] |
| Fund base currency | USD | [ISSUER] |
| Hedged? | No | [SECONDARY] |
| Acc/Dist | Distributing, semi-annual | [SECONDARY] |
| Fund inception | 3 June 2009 | [ISSUER, ishares.com product page] |
| TER/OCF | 0.07% p.a. | [SECONDARY, justETF]; one WebSearch snippet on the SIX/CH literature page also gave 0.07% |
| Benchmark index | ICE U.S. Treasury 7-10 Year Bond Index | [ISSUER] |
| Benchmark rules | USD-denominated UST bonds, 7-10yr remaining maturity | [ISSUER] |
| Rebalancing frequency | Not confirmed | [UNVERIFIED] |
| Effective duration / WAM | Not retrieved (official factsheet PDF fetch returned unparseable binary) | [UNVERIFIED] |
| Number of holdings | 14 (as reported by justETF for this fund's portfolio; plausible given the narrow 7-10yr on/off-the-run maturity band, but not cross-verified against a second source) | [SECONDARY, justETF] |
| Replication method | Physical (sampling) | [SECONDARY] |
| Domicile | Ireland | [ISSUER] |
| Fund size / AUM | ~EUR 2,910m (Dist class, one WebSearch snippet) — not reconciled against a same-day issuer figure | [SECONDARY] |
| Trading 212 availability | Not confirmed — no live `trading212.com/trading-instruments/invest/IBTM.*` page found via search index in the time available. A ticker collision risk exists: the Acc share class's LSE ticker **CBU0** collides with an unrelated iShares Core GBP Corp Bond (Acc) fund that IS confirmed live on Trading 212 (`CBU0.DE`) — that is a **different fund**, not this Treasury ETF. **Marked UNVERIFIED to avoid a false positive from ticker collision.** | [UNVERIFIED] |

### Line 2: iShares $ Treasury Bond 7-10yr UCITS ETF — USD (Acc)

| Field | Value | Source |
|---|---|---|
| ISIN | IE00B3VWN518 (WKN A0X8SJ) | [SECONDARY, justETF] |
| Ticker | SXRM (Xetra); CBU0 (LSE, USD line — **collides with an unrelated GBP Corp Bond fund's Xetra ticker on Trading 212, see caution above**); CU01 (LSE, GBP line) | [SECONDARY, justETF]/[ISSUER WebSearch summary] |
| Fund size / AUM | ~EUR 4,338m | [SECONDARY, justETF] |
| Number of holdings | 14 | [SECONDARY, justETF] |
| Other fields | Same fund/benchmark/TER/domicile as Line 1 | inferred |

### Line 3: iShares $ Treasury Bond 7-10yr UCITS ETF — EUR Hedged (Dist)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares $ Treasury Bond 7-10yr UCITS ETF EUR Hedged (Dist) | [SECONDARY, justETF IE00BGPP6697] |
| Ticker | IBB1 (gettex, Stuttgart, Xetra) | [SECONDARY, justETF]; confirmed on Trading 212 as `IBB1.DE` | [T212] |
| ISIN | IE00BGPP6697 (WKN A2PDTS) | [SECONDARY, justETF] |
| Trading currency | EUR | [SECONDARY] |
| Fund base currency | USD at fund level; EUR is the hedged class currency (same labeling caveat as the 1-3yr EUR-hedged line above) | [SECONDARY]/[UNVERIFIED — reconciliation needed] |
| Hedged? | Yes, to EUR | [SECONDARY] |
| Acc/Dist | Distributing, semi-annual | [SECONDARY] |
| Share-class inception | 25 February 2019 | [SECONDARY, justETF] |
| TER/OCF | 0.10% p.a. | [SECONDARY, justETF] |
| Benchmark index | ICE US Treasury 7-10 Year (EUR Hedged) | [SECONDARY] |
| Number of holdings | 14 | [SECONDARY, justETF] |
| Replication | Physical (sampling) | [SECONDARY] |
| Domicile | Ireland | [SECONDARY] |
| Fund size / AUM | Two justETF-derived figures seen at different points in this research (~EUR 1,496m and ~EUR 1,445m) — not reconciled, likely different snapshot times; both discarded in favor of noting AUM is time-varying | [SECONDARY] |
| Trading 212 availability | **Confirmed** — `https://www.trading212.com/trading-instruments/invest/IBB1.DE` (title: "IBB1 ETF - iShares USD Treasury Bond 7-10yr (Dist)") | [T212] — 403 on direct fetch, title-only confirmation |

Note: additional tickers **IDTXX** and **IGTM** were seen in early search snippets in association with a
"7-10yr Hedged" iShares product page (ishares.com product IDs 316754 and 307496), but were not
independently confirmed against an ISIN in the time available — **UNVERIFIED**, possibly a GBP-hedged
line or a stale/renamed ticker; not included as a confirmed line above.

### Non-iShares alternative (INTERMEDIATE bucket)

- **Amundi US Treasury Bond 7-10Y UCITS ETF Dist** — ISIN LU1407888053, ticker LYX7, TER 0.06% p.a.; Acc class ISIN LU1407887915. [SECONDARY, justETF/Amundi site]
- **Xtrackers II US Treasuries 7-10 UCITS ETF 1D** — ISIN LU2662649685, ticker DBX0UV / XU10, Luxembourg-domiciled. [SECONDARY, justETF/DWS listing]

---

## Bucket: LONG — 20+ Year U.S. Treasuries

### Line 1: iShares $ Treasury Bond 20+yr UCITS ETF — USD (Dist)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares $ Treasury Bond 20+yr UCITS ETF USD (Dist) | [SECONDARY, justETF IE00BSKRJZ44] |
| Ticker — Xetra/gettex/Stuttgart | IS04 | [SECONDARY, justETF] |
| Ticker — LSE | IDTL (USD line), IBTL (GBX line) | [SECONDARY, justETF]; both confirmed live on Trading 212 | [T212] |
| Ticker — SIX | IDTL | [SECONDARY, justETF] |
| ISIN | IE00BSKRJZ44 (WKN A12HL9) | [SECONDARY, justETF] |
| Trading currency | EUR (Xetra/gettex/Stuttgart), USD/GBX (LSE), USD (SIX), MXN (Mexico) | [SECONDARY, justETF] |
| Fund base currency | USD | [ISSUER] |
| Hedged? | No | [SECONDARY] |
| Acc/Dist | Distributing, semi-annual | [SECONDARY] |
| Fund inception | 20 January 2015 | [ISSUER, ishares.com product page] |
| TER/OCF | 0.07% p.a. | [SECONDARY, justETF]; one WebSearch snippet said 0.08% — **discrepancy noted, not reconciled**, treat 0.07% as the better-supported figure (matches justETF profile and consistent with sibling 1-3yr/7-10yr TERs) but flag as **UNVERIFIED at the margin** | [SECONDARY]/[UNVERIFIED — TER discrepancy] |
| Benchmark index | ICE U.S. Treasury 20+ Year Bond Index (formerly Barclays US 20+ Year Treasury Bond Index, changed 26 May 2016) | [ISSUER] |
| Rebalancing frequency | Not confirmed | [UNVERIFIED] |
| Effective duration / WAM | Not retrieved (factsheet PDF unparseable) | [UNVERIFIED] |
| Number of holdings | 41 | [SECONDARY, justETF] |
| Replication method | Physical (sampling) | [SECONDARY] |
| Domicile | Ireland | [ISSUER] |
| Fund size / AUM | ~EUR 816m | [SECONDARY, justETF] |
| Trading 212 availability | **Confirmed** on three related tickers: `IDTL.GB`, `IBTL.GB`, and `DTLE.GB` (the latter is actually the EUR-hedged Dist line — see Line 2) all resolve to live "Invest in... Commission-Free Investing" pages per search-index titles | [T212] — 403 on direct fetch, title-only confirmation |

### Line 2: iShares $ Treasury Bond 20+yr UCITS ETF — USD (Acc)

| Field | Value | Source |
|---|---|---|
| ISIN | IE00BFM6TC58 (WKN A2JKTZ) | [SECONDARY, justETF listing found via WebSearch] |
| Ticker | Not independently confirmed in this audit | [UNVERIFIED] |
| Other fields | Same fund/benchmark/TER/domicile as Line 1 | inferred |

### Line 3: iShares $ Treasury Bond 20+yr UCITS ETF — EUR Hedged (Dist)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares USD Treasury Bond 20+yr UCITS ETF EUR Hedged (Dist) | [SECONDARY, justETF IE00BD8PGZ49] |
| Ticker — Xetra/gettex | IUSV (**caution: this ticker collides with an unrelated "iShares Core S&P U.S. Value" fund traded as a CFD on Trading 212 under `IUSV.US` — do not confuse the two; they are different products on different venues**) | [SECONDARY, justETF]/[T212 collision noted] |
| Ticker — LSE/SIX | DTLE | [SECONDARY, justETF]; confirmed live on Trading 212 as `DTLE.GB` | [T212] |
| ISIN | IE00BD8PGZ49 (WKN A2DXN8) | [SECONDARY, justETF] |
| Trading currency | EUR | [SECONDARY] |
| Fund base currency | USD at fund level; EUR is the hedged class currency (same labeling caveat as above) | [SECONDARY]/[UNVERIFIED — reconciliation needed] |
| Hedged? | Yes, to EUR | [SECONDARY] |
| Acc/Dist | Distributing, semi-annual | [SECONDARY] |
| Share-class inception | 21 September 2017 | [SECONDARY, justETF] |
| TER/OCF | 0.10% p.a. | [SECONDARY, justETF] |
| Benchmark index | ICE US Treasury 20+ Year (EUR Hedged) | [SECONDARY] |
| Number of holdings | 41 | [SECONDARY, justETF] |
| Replication | Physical (sampling) | [SECONDARY] |
| Domicile | Ireland | [SECONDARY] |
| Fund size / AUM | ~EUR 785m | [SECONDARY, justETF] |
| Trading 212 availability | **Confirmed** via `DTLE.GB` (title: "Invest in iShares USD Treasury Bond 20+yr, London Stock Exchange: DTLE ETF — Commission-Free Investing"). An older Trading 212 Community thread titled "Request: USD Treasury Bond 20+ Years (iShares ETF)" also exists but appears superseded (the instrument is now live under confirmed URLs), so it is not treated as evidence of non-availability. | [T212] — 403 on direct fetch, title-only confirmation |

### Non-iShares alternative (LONG bucket)

- **Amundi US Treasury Bond Long Dated UCITS ETF Dist** — ISIN LU1407890620, ticker LYX0Z9/LYX9, TER 0.06% p.a. **Caveat:** tracks a "10+ year minimum time to maturity" index, which is broader/shorter-duration-skewed than the 20+yr iShares bucket — noted as an approximate, not exact, alternative. [SECONDARY, justETF/Amundi site]
- (No SPDR/Xtrackers 20+yr-specific UCITS line was confirmed in the time available; not claiming one exists.)

---

## Cash-like: iShares $ Treasury Bond 0-1yr UCITS ETF (IB01 family)

### Line 1: USD (Acc)

| Field | Value | Source |
|---|---|---|
| Fund name | iShares $ Treasury Bond 0-1yr UCITS ETF | [ISSUER, ishares.com/uk/.../307243] |
| Ticker — gettex | IBC1 (EUR) | [SECONDARY, justETF] |
| Ticker — LSE / SIX | IB01 (USD) | [SECONDARY, justETF] |
| Ticker — Bolsa Mexicana | IB01N (MXN) | [SECONDARY, justETF] |
| ISIN | IE00BGSF1X88 (WKN A2PBNP) | [SECONDARY, justETF] |
| Trading currency | EUR (gettex) / USD (LSE, SIX) / MXN (Mexico) | [SECONDARY] |
| Fund base currency | USD | [ISSUER] |
| Hedged? | No | [SECONDARY] |
| Acc/Dist | Accumulating | [SECONDARY] |
| Fund/share-class inception | 20 February 2019 | [SECONDARY, justETF] |
| TER/OCF | 0.07% p.a. | [SECONDARY, justETF] |
| Benchmark index | **Conflicting names seen**: justETF/general summary called it "ICE U.S. Treasury Short Bond Index"; a separate fetch of the official iShares product page text referred to a "Bloomberg US Treasury 0-1 Year Index" (with a note that its Bloomberg ticker changed from IDCOTS4 to IDCOTS on 1 Dec 2023). These are two different index-provider names for what may or may not be the same benchmark — **not reconciled, flagged UNVERIFIED/CONFLICTING**, needs direct issuer-KIID confirmation before use. | [SECONDARY] vs [ISSUER] — **conflict** |
| Rebalancing frequency | Not confirmed | [UNVERIFIED] |
| Effective duration / WAM | Not retrieved | [UNVERIFIED] |
| Number of holdings | 71 | [SECONDARY, justETF] |
| Replication method | Physical (sampling) | [SECONDARY] |
| Domicile | Ireland | [ISSUER] |
| Fund size / AUM | ~EUR 17,703m (justETF) | [SECONDARY] |
| Trading 212 availability | **Partially verified** — a Trading 212 URL `IB01.GB` is indexed, but the search-engine title returned was the generic Trading 212 homepage-style title ("Invest in Stocks & ETFs worldwide"), not an instrument-specific title as seen for the other confirmed tickers. This is weaker evidence than the confirmed lines above. **Marked UNVERIFIED/PARTIAL** pending a clean instrument-specific title or direct page access. | [T212]/[UNVERIFIED] |

### Line 2: USD (Dist)

| Field | Value | Source |
|---|---|---|
| ISIN | IE00BGR7L912 (WKN A2PBNQ) | [SECONDARY, WebSearch/justETF listing] |
| Ticker | IBTU (LSE) | [T212, trading212.com/.../IBTU.GB — confirmed live page] |
| Acc/Dist | Distributing | [SECONDARY] |
| Trading 212 availability | **Confirmed** — title: "Invest in iShares USD Treasury Bond 0-1yr (Dist), London Stock Exchange: IBTU ETF — Commission-Free Investing" | [T212] — 403 on direct fetch, title-only confirmation |
| Other fields | Same fund/benchmark/TER/domicile as Line 1 | inferred |

### EUR Hedged 0-1yr (iShares)

**Not found.** No EUR-hedged share class of IB01 was located in this audit; the iShares 0-1yr line
appears to be offered only in unhedged USD/EUR-traded-but-unhedged/MXN forms. This is a genuine
gap for the "cash-like, EUR-hedged" use case — the closest available EUR-hedged cash-like option
found is the non-iShares alternative below. **Absence is not itself fully proven (could not
exhaustively enumerate all iShares share classes); treat as UNVERIFIED-absence, not confirmed-absence.**

### Non-iShares alternative (CASH-LIKE bucket)

- **Amundi US Treasury Bond 0-1Y UCITS ETF Acc** — ISIN LU2182388665. [SECONDARY, Amundi site]
- **Amundi US Treasury Bond 0-1Y UCITS ETF EUR Hedged Acc** — ISIN LU2182388749. This is the only
  confirmed EUR-hedged cash-like (0-1yr) UCITS Treasury line found in this audit. [SECONDARY, Amundi site]

---

## Hedged vs. unhedged share classes — general notes

- All EUR-hedged lines above are **share classes of the same underlying USD-base fund**, not
  separate funds. The unhedged USD line and the EUR-hedged line hold the same physical bond
  portfolio; only the currency-hedging overlay (FX forwards) at the share-class level differs.
  Several third-party (justETF-derived) records label the EUR-hedged class's "fund base currency"
  as EUR — this conflates the **share-class dealing/hedged currency** with the **fund's actual base
  currency (USD)**. This labeling inconsistency was seen consistently enough across several lines
  that it is flagged here as a general caution rather than a per-line error.
- General hedging methodology (from an iShares product brief, a US-market brochure describing the
  generic iShares currency-hedged-share-class mechanism, not a UCITS-specific prospectus text):
  hedged share classes use **rolling one-month forward FX contracts** to hedge the underlying
  currency exposure back to the share class's currency; the hedge is reset/rolled monthly, and it
  reduces but does not eliminate currency-driven NAV divergence between share classes. [ISSUER/SECONDARY,
  ishares.com/us/literature/brochure/ishares-currency-hedged-product-brief.pdf] The economic cost of
  that rolling forward hedge is, in general FX-forward theory, driven by the **short-term interest-
  rate differential** between the hedged currency (EUR) and the underlying currency (USD) — a wider
  USD-EUR short-rate gap makes EUR-hedging more expensive (or, when USD short rates exceed EUR short
  rates, can even make the EUR-hedged share class carry a a positive roll versus the unhedged share
  class). This general mechanism was **not independently confirmed against a UCITS-specific
  prospectus paragraph for these particular sub-funds** in the time available — flagged UNVERIFIED
  at the fund-specific-prospectus level, though the general FX-forward mechanism is well established
  market structure and applies conceptually.
- **Trading currency vs. underlying currency exposure**: the exchange-quotation currency of a line
  (e.g. EUR on Xetra) is independent of whether the share class is currency-hedged. An investor
  buying the **unhedged** USD-base fund's EUR-quoted line (e.g. IUSU on Xetra for the 1-3yr bucket)
  still has full USD/EUR currency exposure on the underlying bonds — only the trade settles and is
  quoted in EUR. Only the share classes explicitly labeled "EUR Hedged" (tickers IBTE, IBB1,
  IUSV/DTLE above) hedge the USD exposure back to EUR.

## Fields not verifiable (or not verified) in this Stage 0 pass

- Effective duration and weighted average maturity for every line (official factsheet PDFs returned
  unparseable binary via the fetch tool; the iShares product pages' JS-rendered "Fund Characteristics"
  tab was not fully captured by the text-mode fetch).
- Rebalancing frequency for the benchmark indices (documented as "monthly" for the general ICE US
  Treasury index family in market knowledge, but not independently confirmed per-index in this audit).
- Quoted bid-ask spread / iNAV-based spread statistics for any line — a general search surfaced a
  spread-methodology description ("average bid-ask spread as % of price") but no clean current
  spread-percentage figure could be extracted without also encountering live price/quote data, which
  this audit's hard rules require discarding; **field left UNVERIFIED rather than risk recording
  incidental price data**.
- Exact TER for the 20+yr USD (Dist) line has a 0.07%-vs-0.08% discrepancy between two sources,
  not reconciled.
- Benchmark index name for IB01 (ICE vs. Bloomberg naming conflict), not reconciled.
- ISIN for the GBP-hedged 1-3yr line (IBTG) and ticker for the 20+yr USD (Acc) line (IE00BFM6TC58).
- Whether Trading 212 supports fractional-share orders specifically for these bond ETFs (general
  fractional-share support for ETFs on Trading 212 was already verified for the account in a prior
  session per stored memory, but not re-confirmed per-instrument here since direct Trading 212 pages
  returned HTTP 403).
- iShares EUR-hedged 0-1yr line: not found; treated as UNVERIFIED-absence (see above), not proven
  non-existent.
- justETF's own "available at Trading 212" broker-comparison claims could not be independently
  cross-checked against Trading 212's own site (bot-protected) except by matching search-indexed
  page titles; where no matching title was found (IBTM/CBU0/IB01.GB-generic/IBTE), the justETF claim
  is flagged CONFLICTING/UNVERIFIED rather than accepted at face value.

**No performance, price, NAV history, return, or yield-history data was retrieved, recorded, or
saved anywhere in this file, the accompanying CSV, or the source index.**
