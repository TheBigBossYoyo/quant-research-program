# PHASE 10A — short-interest / short-positioning data audit

Audit date: **2026-09-22**. No backtest. No purchase. No locked data opened. No strategy cell added —
cumulative ledger stays **490**.

Evidence: `reports/phase10a/raw/` (13 files). Companion documents:
`PHASE10A_POINT_IN_TIME_AUDIT.md`, `PHASE10A_LITERATURE_SCREEN.md`, `PHASE10A_PROVIDER_MATRIX.csv`,
`PHASE10A_RECOMMENDATION.md`, `PHASE10B_DRAFT.md`.

---

## 1. The distinction that governs this audit

**Short interest** is the outstanding short position in a security, reported twice a month by FINRA
member firms under Rule 4560. **Short-sale volume** is the daily flow of short-marked executions.
They are different information families and are never substituted for one another here.

This matters immediately, because the free data is asymmetric: daily short-sale volume is published
by every venue in bulk, for free, going back years, and issue-level short *interest* is not. The NYSE
public FTP is the clearest illustration — `/ShortData/` contains six directories
(`NYSEshvol`, `ARCAshvol`, `Amexshvol`, `Chicagoshvol`, `Nationalshvol`, `Texasshvol`), all of them
short-sale **volume**. Nothing in that tree is short interest.

## 2. Result in one line

**The right data exists in two forms — a free API that starts one settlement date before our
development window ends, and a paid exchange file with a 1988 history whose price is not public and
whose licence is enterprise-shaped.** There is no free or cheap issue-level short-interest panel
covering 2010–2017.

## 3. NYSE

### 3.1 The free FTP is aggregate only

`https://ftp.nyse.com/NYSEGroupConsolidatedShortInterest/` is public, unauthenticated and browsable,
with year directories **2015 → 2026** plus `current/`. The earliest month directory is **201508**.

Each file is ~20 KB. Parsing one (`NYSE_Group_Consolidated_Short_Interest_20150811.xls`) shows why:
its sheet is a **market-level summary**, not a cross-section. The only labels in the workbook are

> `SETTLEMENT DATE`, `EXCHANGE`, `TOTAL CURRENT SHORT INTEREST`, `TOTAL PREVIOUS SHORT INTEREST (Revised)`,
> `NUMBER of SECURITIES with a SHORT POSITION`, `NUMBER of SECURITIES with a POSITION >= 5,000 SHARES`

with four rows: `NYSE`, `NYSE ARCA`, `NYSE MKT`, `NYSE GROUP`. The settlement date inside the
2015-08-11 file is **07/31/2015**, so the filename carries the *publication* date and the settlement
date sits in the sheet — a useful point-in-time property attached to a file with no issuer in it.

**Aggregate short interest is a market-timing series, not a cross-sectional signal.** It cannot
support the family in `PHASE10B_DRAFT.md`.

### 3.2 The issue-level product is paid and its price is not public

`NYSE Group Short Interest` (nyse.com/market-data/reference/nyse-group-short-interest): "reported
uncovered short positions of securities listed on NYSE, NYSE Arca and NYSE American", **history
January 1988 to present**, semi-monthly, delivered by SFTP and AWS S3.

The client specification (v1.6, 21 August 2024, retained in the evidence bundle) gives a 16-field
layout that is close to ideal for this family:

| # | field | note |
| --- | --- | --- |
| 1-2 | `Stock_Symbol`, `Standard_Suffix` | ticker |
| 3 | **`CUSIP`** | stable identifier — survives ticker reuse |
| 4-5 | `Legal_Issuer_Name`, `Issue_Name` | |
| 6 | `Primary_Market` | N = NYSE, A = NYSE American, P = NYSE Arca |
| 7 | `Revision_Indicator` | R = prior period revised |
| 8 | `Split_Indicator` | S = split during the period |
| 9 | **`Free_Float`** | "Public float at the Settlement Date… maintained on a best effort basis… when free float is not available, the field value shall be '0'" |
| 10-12 | `Current_` / `Previous_Short_Interest_Position`, **`Change_In_Short_Interest_Position`** | the primary signal, pre-computed |
| 13-14 | `Average_Daily_Volume`, `Change_In_Average_Daily_Volume` | |
| 15-16 | `Current_Days_To_Cover`, `Change_In_Days_To_Cover` | |

Filenames carry the **settlement date** (`EQY_US_NYSE_REF_SHORTINT_NEW_yyyymmdd`), and the separate
NYSE Group Short Interest Calendar maps every settlement date to a **NYSE Group Release Date**, with
the file "provided every two weeks on the day of the NYSE Group Release Date at 2:00pm ET". Point-in-time
timing is therefore fully determined. The spec's own revision history shows calendars were published
annually from 2016 onward, so historical release dates are recoverable.

Two hard problems:

- **Coverage is NYSE/American/Arca only.** Nasdaq-listed issuers — AAPL, MSFT, AMZN, most of the
  liquid US large-cap growth universe — are simply absent. A US panel needs Nasdaq's separate product.
- **No public price.** "Short interest" appears **zero times** in both the NYSE Proprietary Market
  Data Pricing Guide (36 pages, 14 May 2026) and the Historical Proprietary Market Data Pricing guide
  (11 pages). The general rule in the pricing guide is "A flat fee per NYSE Market Data product per
  organization applies. Fees apply on an enterprise-wide basis to the organization, any of its holding
  companies and its subsidiaries" — an enterprise market-data licence, not a retail subscription.

A two-date sample of the issue-level file exists on the public FTP
(`/Reference Data Samples/NYSE GROUP SHORT INTEREST/`, settlement dates 2026-04-15 and 2026-04-30,
734 KB each). **It was deliberately not downloaded**: both dates fall inside the 2022-01..2026-08
holdout. The client specification supplied the schema without touching it.

## 4. Nasdaq

Two separate things, and the brief was right to warn about conflating them.

**The public query interface is a rolling window.** `api.nasdaq.com/api/quote/{symbol}/short-interest`
answers unauthenticated and returns exactly **24 rows** for AAPL — 12 months, semi-monthly — oldest
**2025-09-15**. Delisted symbols return `status 400` with no table: `TWTR` and `BSC` both fail. So the
public interface is **12 months deep, survivor-only, one symbol per call**. Useless for history and
actively misleading on survivorship.

NasdaqTrader states it verbatim:

> "Nasdaq short interest is available by issue for a rolling 12 months and updated twice a month.
> Short Interest data is based on a mid-month and end of month settlement dates and **released after
> 4:00 p.m, ET, on the dissemination date**. Please note short interest for end of month settlement
> date became available as of September 2007."

**The bulk product is a paid subscription:** "Subscribe to access a comma-delimited text file (.txt)
via Secure File Transfer Protocol." No price is shown. The page's three supporting links —
*Report Overview & Publication Schedule*, *Data Fields & Definitions* and the subscription page — all
**404** (they redirect to `ErrorPage404.aspx`, having been pointed at Nasdaq Data Link). The official
publication schedule and field definitions for the Nasdaq product are therefore not currently
retrievable from Nasdaq's own site, which is itself a data risk.

## 5. FINRA — the best free source, and it starts in the wrong place

`api.finra.org` answers **without authentication, without an API key, and without registration**.
`GET/POST /data/group/otcMarket/name/consolidatedShortInterest` returns issue-level rows with exactly
the fields this family needs:

```
accountingYearMonthNumber, symbolCode, issueName, issuerServicesGroupExchangeCode, marketClassCode,
currentShortPositionQuantity, previousShortPositionQuantity, stockSplitFlag,
averageDailyVolumeQuantity, daysToCoverQuantity, revisionFlag, changePercent,
changePreviousNumber, settlementDate
```

Despite an OTC-centric description, the dataset is genuinely consolidated across listing venues. For
settlement date **2017-12-29** the API reports `record-total: 15,495` issues; the first 5,000
(alphabetical) break down as OTC 2,287, **NYSE 1,070, NNM 767, ARCA 393, SC 288, AMEX 125, BZX 64**,
OTCBB 6.

**Survivorship is safe within the window.** Querying 2017-12-29 by symbol returns live rows for issuers
that later disappeared: `TWTR` (Twitter, NYSE, 37,978,572 shares short), `CELG` (Celgene, NNM),
`RTN` (Raytheon, NYSE). Historical files preserve dead tickers even though the Nasdaq lookup page does not.

**And then the coverage.** Scanning every plausible semi-monthly settlement date back through 2015:

| period | result |
| --- | --- |
| 2015-01 → 2017-12-28 | **no data** (HTTP 204 on every candidate date) |
| **2017-12-29** | **first date with data** |
| 2018-01-12 onward | continuous, semi-monthly |

The free, correctly-structured, survivorship-safe, venue-consolidated US short-interest panel begins on
**the last settlement date of 2017** — one observation inside a development window that ends
2018-01-01. Everything else it holds lies in our validation and holdout segments.

An earlier scan using calendar 15ths produced false negatives (2018-01-15 was the MLK holiday,
2018-04-15 and 2018-07-15 were Sundays); the scan was redone on actual settlement dates before this
conclusion was drawn.

A sibling dataset, `equityShortInterest`, is **OTC-only** (`marketCategoryDescription = "Other OTC"`)
and also begins in 2018. Not relevant to a listed-equity panel.

## 6. Everything else

- **ORTEX** — the flagship series is *modelled*: "Short interest estimated through the trading day by
  our models"; "Estimates update through the trading day; **the official exchange print is published
  weeks behind**." That is a proprietary estimate with its own vintage and restatement behaviour, not
  the reported position this audit was asked to find. Their official-print data is the same free
  FINRA/exchange data. Third-party review reports Free / **$39** / **$129** per month; the vendor's own
  tiers did not render for verification, so those figures are **UNVERIFIED**. Bulk/full-day downloads
  are "Talk to sales" enterprise licensing.
- **S3 Partners, FactSet, LSEG, Morningstar** — institutional, quote-only. Recorded for comparison;
  not recommended.
- **Compustat Supplemental Short Interest File (via WRDS)** — this is what the academic literature
  actually uses. OSAP's `ShortInterest` predictor is defined verbatim as "Short-interest from Compustat
  (shortint) scaled by shares outstanding (shrout)". Institutional affiliation required; unavailable.
- **Nasdaq Data Link** — no short-interest datatable found under the obvious vendor codes; Nasdaq's own
  short-interest pages now redirect into the Data Link SPA, and Phase 9A already established that Data
  Link pricing is gated behind login with institution-only restrictions on the relevant publishers.
- **Polygon / Benzinga** — Phase 9A established $99/month per dataset for individuals; the Benzinga
  catalogue is ratings/targets/earnings, not short interest.

## 7. What we already hold, free, that bears on this family

`data/raw/phase9b/PredictorPortsFull_202510.csv` (OSAP October 2025, already downloaded and hashed in
Phase 9B) contains published portfolio returns for three short-interest predictors. Checked
structurally — signal names, port labels and dates only, **the `ret` column was not read**, because
Phase 10A does not compute returns:

| signal | source | ports | span | pre-2018 months | sign | weight |
| --- | --- | --- | --- | ---: | ---: | --- |
| `ShortInterest` | Dechow et al. 2001 | 01-05 + LS | 1973-02 → 2024-12 | **539** | **−1** | EW |
| `IO_ShortInterest` | Asquith, Pathak, Ritter 2005 | 01-03 + LS | 1979-11 → 2024-12 | 458 | +1 | EW |
| `Recomm_ShortInterest` | Drake, Rees, Swanson 2011 | 01-02 + LS | 1993-12 → 2024-12 | 289 | +1 | EW |

`Sign = −1` on `ShortInterest` means the long side is **low** short interest — which is precisely the
long-only interpretation this programme would need. OSAP's own definition also records the
point-in-time convention the literature uses: "Short-interest data are available bi-weekly with a four
day lag. We use the mid-month observation to make sure data would be available in re[al time]".

Note that **no "change in short interest" predictor exists in the OSAP set** — the brief's preferred
PRIMARY signal is not in the free replication corpus. Only the level is.

## 8. Honesty notes

- Nothing was purchased; no account was created; no form was submitted; no paid tier was probed.
- The NYSE issue-level sample files (2026-04-15, 2026-04-30) were **not downloaded** because they fall
  in the holdout window. The schema came from the published specification instead.
- One FINRA settlement date inside the development window (2017-12-29) was pulled to establish
  cross-section size, venue mix and delisted representation. **No price, return or performance figure
  was read**, and nothing from it forms or selects a signal.
- The 2018+ portion of the FINRA dataset was probed only for **existence** (HTTP 200 vs 204). No
  values from any locked window were read.
- Validation 2018-2021 and holdout 2022-01..2026-08 remain unopened. 376 tests pass. Ledger 490.
