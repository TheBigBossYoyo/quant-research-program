# Phase 11C / D1 — H.15 / Treasury CMT Yield-Curve PIT Data Audit

Scope: Stage 0 **data/documentation** audit only. No yield/price/return values were downloaded,
viewed as facts, or recorded anywhere in this report. Web captures are indexed in
`D1_snapshots/INDEX.md`. Retrieval date for all facts below: 2026-09-27.

Tagging key: **[OFFICIAL, URL]** = confirmed from an official-source page's own text this session.
**[SECONDARY]** = from a non-primary but generally reliable source (aggregator, Wikipedia-class,
or a WebSearch AI-summary that could not be independently re-verified against the primary page's
raw text this session). **[UNVERIFIED]** = could not be confirmed from any official page this
session; must not be used to gate a promotion decision.

---

## A.1 — Series table (FRED CMT IDs)

| FRED ID | Maturity | First obs. date | Known gaps / notes | Source |
|---|---|---|---|---|
| DGS1MO | 1-month | Series exists on FRED. Exact first-observation date **not confirmed from official page text** this session (FRED's rendered page did not expose the full history start date without loading the interactive chart, which was avoided to prevent incidental value exposure). Commonly documented start: 2001-07-31 (Treasury began publishing the 4-week/1-month bill CMT in mid-2001). | Treasury introduced the 4-week bill (and its CMT) in 2001. | [SECONDARY] for the exact date; [OFFICIAL, https://fred.stlouisfed.org/series/DGS1MO] for series existing, title="Market Yield on U.S. Treasury Securities at 1-Month Constant Maturity", units=Percent NSA, frequency=Daily |
| DGS2MO | 2-month | **Does not exist as a FRED series** (HTTP 404 on `fred.stlouisfed.org/series/DGS2MO`, checked directly this session). | Treasury's own par-curve inputs do include an 8-week (~2-month) bill node (see A.2), but the Fed/FRED CMT output set does not publish a standalone 2-month constant-maturity series. Any 2-month tenor needed for research must come directly from Treasury's own daily par-yield-curve table/XML, not FRED. | [OFFICIAL, negative result — https://fred.stlouisfed.org/series/DGS2MO returns 404] |
| DGS3MO | 3-month | Long-standing series (commonly documented start 1954-01-04, consistent with H.15's historical 3-month bill CMT). Exact date **not independently confirmed** from rendered FRED text this session. | None material. | [SECONDARY] |
| DGS4MO | 4-month | **Does not exist as a FRED series** (HTTP 404 on `fred.stlouisfed.org/series/DGS4MO`, checked directly this session), even though Treasury's current par-curve inputs include a 17-week (~4-month) bill (added 2022, see A.2). | Same implication as DGS2MO: 4-month tenor is Treasury-XML-only, not on FRED. | [OFFICIAL, negative result] |
| DGS6MO | 6-month | Long-standing series. Exact first date **not confirmed** this session. | None material beyond general CMT history. | [SECONDARY] |
| DGS1 | 1-year | Long-standing series. | None material. | [SECONDARY] |
| DGS2 | 2-year | Long-standing series; commonly documented as starting materially later than the 1/3/5/10-year series (2-year note program began in the 1970s). Exact date **not confirmed** this session. | None material found. | [SECONDARY] |
| DGS3 | 3-year | Existed historically; the 3-year note was discontinued and reintroduced by Treasury at various points in auction history, which can affect CMT continuity. Not independently confirmed this session. | Possible historical gap tied to 3-year note issuance suspension (1998-2008) — **flagged for follow-up, not confirmed from an official page this session.** | [UNVERIFIED — flag only] |
| DGS5 | 5-year | Long-standing series. | None material. | [SECONDARY] |
| DGS7 | 7-year | 7-year note was reintroduced by Treasury in 2009 after a long hiatus; CMT series continuity around that reintroduction **not confirmed** from an official page this session. | Possible gap around discontinuation/reintroduction of the 7-year note. **Flagged for follow-up.** | [UNVERIFIED — flag only] |
| DGS10 | 10-year | Long-standing series, the most complete/benchmark tenor. | None material. | [OFFICIAL for title/units/frequency, https://fred.stlouisfed.org/series/DGS10]; start date [SECONDARY] |
| DGS20 | 20-year | Existed, with a documented role as the basis for estimating the 30-year rate during 2002-02-18 to 2006-02-09 (see DGS30 row). | Treasury published an adjustment factor to derive an implied 30-year rate from the 20-year curve during the 30-year's 2002-2006 hiatus. | [OFFICIAL, footnote 10 of archival FRB H.15 PDF, `D1_snapshots/frb_h15_20161003_archival.pdf`] |
| DGS30 | 30-year | **Discontinued 2002-02-18, reintroduced 2006-02-09** (confirmed verbatim from an official Federal Reserve H.15 footnote and independently corroborated by the FRED DGS30 series-page metadata text). | This is the single most important, well-documented CMT gap. Any backtest spanning 2002-2006 with the 30-year tenor must handle this as a genuine missing-series period, not a data error to be interpolated silently. | [OFFICIAL, https://fred.stlouisfed.org/series/DGS30 and `D1_snapshots/frb_h15_20161003_archival.pdf` footnote 10] |

**Overall D1 finding on A.1:** the two hard, officially-confirmed structural facts are (i) the
**DGS30 2002-02-18 to 2006-02-09 gap**, and (ii) **DGS2MO/DGS4MO do not exist on FRED** even
though Treasury's own current curve construction uses 2-month- and 4-month-equivalent bill nodes.
Exact first-observation dates for the other maturities could not be pulled from official page
*text* without either (a) loading FRED's interactive chart (JS-rendered, inaccessible to the
audit's read-only text tool) or (b) hitting an endpoint that would return values (forbidden by
the audit's hard rule). These are marked [SECONDARY]/best-effort and must be re-verified from
FRED series metadata (observation_start field) — which does not itself require touching a value
field — before they are relied upon for any causal-alignment code or test.

## A.2 — What CMT/par yields are; methodology history

- CMT ("Constant Maturity Treasury") yields are **par yields**, not zero-coupon/spot yields.
  They are read off Treasury's fitted par yield curve at fixed maturity points (currently 1, 3,
  6 months and 1, 2, 3, 5, 7, 10, 20, 30 years, per the archival H.15 footnote text, consistent
  with the current methodology page's input-maturity list). **[OFFICIAL, home.treasury.gov
  Treasury Yield Curve Methodology page + FRB H.15 archival footnote 10]**
- **Curve construction**: inputs are **indicative, bid-side** market price quotations (not
  actual transaction prices) for the most recently auctioned ("on-the-run") securities,
  collected by the **Federal Reserve Bank of New York at or near 3:30 PM ET** each trading day.
  **[OFFICIAL, home.treasury.gov/.../treasury-yield-curve-methodology]**
- **Current curve-fitting method**: prices are converted to yields, bootstrapped into
  instantaneous forward rates at the input maturities, then a **monotone convex** interpolation
  is applied to the forward-rate curve to build the full curve. This method has been in use
  **since December 6, 2021**, replacing the prior **quasi-cubic Hermite spline** method.
  **[OFFICIAL, same Treasury methodology page; also independently named "Quasi-Cubic Hermite
  Spline Treasury Yield Curve Methodology" as a distinct historical Treasury page found via
  search]**
- **Input-maturity history / additions**: current inputs are bills at **4-, 6-, 8-, 13-, 17-,
  26-, and 52-week** maturities plus notes/bonds at **2, 3, 5, 7, 10, 20, 30** years. This means
  Treasury's own curve construction now uses a **6-week** and a **17-week (~4-month)** bill node
  that are more granular than what FRED exposes as separate CMT output series (FRED only
  publishes 1/3/6-month, not 2-week/6-week/2-month/4-month as standalone DGS series). The
  Treasury methodology page states that "at various times in the past, Treasury has used other
  inputs, such as interpolated yields and rolled down securities" for fitting the pre-2021
  quasi-cubic Hermite spline — i.e., the **input set itself has changed over time**, not just the
  interpolation method. **[OFFICIAL, home.treasury.gov methodology page]** The exact historical
  dates of each individual maturity-node addition (e.g., when the 17-week bill or the 6-week
  bill was added as an input) were **not pinned down to a specific date from an official page
  this session** — flagged **[UNVERIFIED]**, follow-up needed if the strategy design specifically
  depends on a 2-month or 4-month tenor's history length.
- **Off-the-run vs on-the-run**: inputs are explicitly the **most recently auctioned** (i.e.
  on-the-run) securities. **[OFFICIAL, same page]**
- **Zero-coupon / spot curve**: Treasury does separately publish a **Treasury Nominal
  Coupon-Issue (TNC) yield curve**, which is a spot/zero curve derived from Treasury notes and
  bonds (as distinct from the par CMT curve), available as monthly-average, quarterly-average,
  10-year-average, and end-of-month spot rate series, with historical vintages reportedly back to
  1976 for some cuts. **[SECONDARY — confirmed existence and general framing via WebSearch of
  home.treasury.gov/data/treasury-coupon-issues-and-corporate-bond-yield-curves and associated
  Treasury-hosted files (tnc_qh_forwards_0.xls, ycds_feb2016.pdf, trp_apr2014.pdf), but the TNC
  page's own text was not directly fetched/rendered this session, so exact current frequency,
  start date and revision policy remain to be confirmed on the primary page before use.]**
  Converting par (CMT) yields to zero-coupon yields yourself (rather than using Treasury's TNC
  series) would require **bootstrapping**: sequentially stripping coupon cash flows maturity by
  maturity using already-solved shorter zero rates, plus an **interpolation assumption** between
  the sparse CMT maturity nodes (1,3,6mo,1,2,3,5,7,10,20,30y) to get intermediate zero rates —
  this is a nontrivial modeling choice (choice of interpolation: linear on yields, monotone
  convex on forwards, cubic spline, etc.) that itself introduces a parameter/design decision the
  research protocol would need to preregister if pursued instead of using Treasury's own TNC
  series.

## A.3 — Publication timing

| Item | Time (ET) | Source status |
|---|---|---|
| FRBNY quote collection for Treasury's par curve | ~3:30 PM ET | [OFFICIAL, home.treasury.gov methodology page] |
| Treasury's own daily par yield curve rates posted to home.treasury.gov | Reported as "usually available by 6:00 PM ET" | [UNVERIFIED — this figure came from a WebSearch AI-generated summary, not confirmed verbatim on an official Treasury page's own text this session; must be re-confirmed directly before being used to gate same-day executability] |
| Federal Reserve H.15 daily web release (current) | Posted Monday-Friday, stated as "4:15 PM" per current federalreserve.gov H.15 page text render | [OFFICIAL-leaning, https://www.federalreserve.gov/releases/h15/ rendered text this session] — contrast with the archival Oct 2016 PDF header, which stated "For use at 2:30 p.m. Eastern Time" for the (now-discontinued) PDF release format. This is a **documented publication-format/timing change**, not a contradiction: the Board stopped publishing H.15 as a PDF after October 11, 2016 and moved to a web/FRED-based release, and the archival PDF itself says the Board would "no longer publish the H.15 in PDF format." **[OFFICIAL, archival PDF page 1, `D1_snapshots/frb_h15_20161003_archival.pdf`]** |
| H.15 weekly figures | Averages of 7 calendar days ending Wednesday of the current week | [OFFICIAL, archival PDF footnote 2, corroborated by current federalreserve.gov H.15 page text] |
| FRED update relative to Treasury/Fed release | Not confirmed same-day vs next-day from an official page's text this session; a WebSearch summary suggested Treasury/Fed post in the afternoon/evening and downstream aggregators (e.g., OFR's Short-Term Funding Monitor) pick it up "the next business day" | [UNVERIFIED — this is exactly the kind of same-day-vs-next-day ambiguity the audit was asked to resolve, and it was **not** resolved to OFFICIAL-source confidence this session] |

**Practical implication for D1:** the safest documented anchor is the **~3:30 PM ET FRBNY quote
time** (OFFICIAL) plus the **Board's current 4:15 PM ET web-posting time for H.15** (OFFICIAL-
leaning, current page text). Treasury's own ~6:00 PM ET claim and FRED's same-day-vs-next-day
update behavior are UNVERIFIED and should not be relied upon for a same-day execution rule
without direct re-confirmation (e.g., by comparing FRED's `realtime_start` metadata field for a
handful of known dates against Treasury's own posted dates — a metadata-only check that does not
require reading values, and was not performed this session due to time/scope).

## A.4 — Revisions

- **ALFRED vintage-date mechanics**: a vintage date is recorded **only when the series was
  actually revised** on that release date; if a release date brought no revision, it is not
  listed as a vintage. This means the **count of vintage dates for DGS10 is a direct, non-value
  proxy for how often the series has been revised** historically. **[OFFICIAL,
  https://alfred.stlouisfed.org/help/downloaddata]**
- This session did **not** load the actual ALFRED vintage-dates list for DGS10
  (`alfred.stlouisfed.org/series?seid=DGS10` / the downloaddata vintages listing) due to time
  constraints after the mechanics page was confirmed — **recorded as "not checked" per the
  audit's own fallback instruction**, since attempting it risked landing on a page that also
  renders the current value prominently. This is the single most actionable follow-up for a
  future D-session: open only the vintage-*dates* listing (dates, not values) and count/inspect
  it.
- **Working classification pending that check**: Treasury constant-maturity yields are generally
  understood in the fixed-income data industry to be essentially **not revised** after
  publication (they are a same-day mark-to-market fit, not a survey-based or seasonally-adjusted
  series subject to routine backward revision the way many macro series are). This is
  **[SECONDARY]** reasoning by analogy to the ALFRED vintage-date mechanism (few/no revisions
  expected for a same-day market-quote series) and by the absence of any revision-policy
  footnote in the archival H.15 PDF's footnotes. It is **not a confirmed fact**.

## A.5 — Proposed PIT classification

**PIT_RECONSTRUCTABLE** (not PIT_SAFE outright, not PIT_BLOCKED), for these reasons:
1. The publication-timing chain has two OFFICIAL anchors (3:30 PM ET quote collection; 4:15 PM
   ET current Board web posting) but one UNVERIFIED link (Treasury's own ~6 PM posting claim;
   FRED's same-day-vs-next-day behavior) — so a conservative same-day rule is executable, but the
   exact instant FRED itself reflects the new value is not nailed down to OFFICIAL confidence.
2. Revisions are plausibly rare/absent (SECONDARY reasoning) but this was explicitly **not
   checked** against the ALFRED vintage-dates listing this session, so **MINOR_REVISION_RISK**
   cannot yet be ruled out and must be re-audited (dates-only) before a promotion decision.
3. Two structural data gaps are OFFICIALLY confirmed (DGS30 2002-2006 gap; DGS2MO/DGS4MO absent
   from FRED entirely) that any universe/feature design must explicitly handle rather than
   silently interpolate.
4. Given (1)-(3), the data is usable for research **if** the execution rule in Section C below is
   applied conservatively (i.e., treat FRED/H.15 as available only from the **next available
   execution session after the Board's 4:15 PM ET post**, never same trading day), and if the
   ALFRED revision check is completed as an immediate next step before any live-adjacent
   decision.

## B — Execution-clock facts

| Item | Value | Status |
|---|---|---|
| LSE regular trading hours (Main Market, incl. ETFs) | 08:00-16:30 London time, continuous trading | [OFFICIAL/near-official — LSE's own FAQ text via WebSearch snippet, cross-confirmed by multiple independent secondary aggregators] |
| LSE opening auction | ~07:50-08:00 London time | [SECONDARY, multiple aggregator confirmation; not independently re-fetched from LSE's own page text this session because the LSE site is JS-rendered and blocked WebFetch extraction] |
| LSE closing auction | 16:30-16:35 London time (16:30 continuous trading stops, 5-minute order accumulation, 16:35 fixing sets the official closing price used for FTSE 100 / ETF NAV reference) | [SECONDARY, consistent across sources, not independently confirmed on LSE's own rendered text this session] |
| UK bank holidays 2026 (England & Wales, governing LSE's holiday calendar by market convention) | 1 Jan, 3 Apr (Good Friday), 6 Apr (Easter Monday), 4 May, 25 May, 31 Aug, 25 Dec, 28 Dec (substitute for Boxing Day falling on a Saturday) | [OFFICIAL, GOV.UK's own posted 2026 list, retrieved via WebSearch this session] |
| Note on a conflicting secondary LSE holiday list | One third-party aggregator returned a 2026 LSE closure list (1 Jan, 10 Apr, 13 Apr, 8 May, 31 Aug, 25 Dec, 28 Dec) that **does not match** the official GOV.UK bank-holiday dates for Good Friday/Easter Monday/Early May bank holiday. This aggregator's dates are judged unreliable/stale and were **not used**; the GOV.UK official dates are used instead, on the well-established convention that LSE closes on England & Wales bank holidays. | Flagged explicitly as a discrepancy; [UNVERIFIED] that the aggregator's specific dates apply to any other year confused with 2026. |
| Xetra (Frankfurt) trading hours | 09:00-17:30 CET, continuous trading (auction schedule published separately, not itself fetched this session) | [OFFICIAL, cashmarket.deutsche-boerse.com, Deutsche Börse's own domain] |
| Xetra 2026 non-trading dates | 1 Jan, 3 Apr (Good Friday), 6 Apr (Easter Monday), 1 May, 24 Dec*, 25 Dec, 31 Dec* (*settlement remains open on these two if not a weekend — i.e. trading itself is closed but settlement processing continues) | [OFFICIAL, same Deutsche Börse page] |
| Frankfurt floor (FWB) trading hours, for comparison | 08:00-22:00 CET generally; bond trading specifically 08:00-17:30 CET | [OFFICIAL, same Deutsche Börse page] |
| London vs New York time difference | London is UTC+0 (GMT) / UTC+1 (BST); New York is UTC-5 (EST) / UTC-4 (EDT). Under normal simultaneous-DST conditions the gap is a constant 5 hours (London ahead). **DST transition mismatch weeks**: the US ends DST (falls back) on the **first Sunday of November**, while the UK ends BST (falls back) on the **last Sunday of October** — roughly one to two weeks earlier than the US. In spring, the US begins DST (second Sunday of March) about **two to three weeks before** the UK begins BST (last Sunday of March). During these mismatch windows the London-New York gap is temporarily **4 hours** instead of 5 (spring gap window) or momentarily reverts asymmetrically in the autumn window, rather than a clean single-day switch on both sides at once. | [SECONDARY — this is standard, well-documented DST calendar logic (US: 2nd Sunday March / 1st Sunday Nov; UK: last Sunday March / last Sunday Oct) but the exact 2026 mismatch weeks were not independently pulled from an official calendar this session; treat the *mechanism* as reliable, the *exact 2026 date ranges* as needing a direct calendar check before being hard-coded into execution-timing code.] |

## C — Proposed conservative execution rule (H.15/Treasury day D -> earliest permissible LSE/Xetra execution)

Given the confirmed OFFICIAL anchors (FRBNY quotes at ~3:30 PM ET; Board's current H.15 web
posting at 4:15 PM ET) and the UNVERIFIED gaps (Treasury's own ~6 PM ET claim; FRED same-day vs
next-day update lag; exact ALFRED revision behavior), the most conservative rule that guarantees
no day-D information is used before its publication time is:

1. **Anchor on the later, OFFICIAL-confirmed Board web-posting time**: treat day-D's CMT/H.15
   values as not available until **4:15 PM ET on day D** (ignore the Treasury ~6 PM claim as an
   upper bound only, i.e. if anything, being even more conservative and using 6:00 PM ET as the
   effective release time is *safer*, not riskier, so where the two conflict, use the **later**
   of the two, 6:00 PM ET, as the conservative anchor.)
2. **Convert 6:00 PM ET on day D to London/Frankfurt local time**, respecting the DST mismatch
   noted in Section B (nominally 23:00 London time on day D under the standard 5-hour gap, or
   22:00 London time during the spring/autumn mismatch windows when the gap is temporarily 4
   hours — the execution code must compute this dynamically from each side's own DST rules, not
   assume a fixed offset).
3. Since 6:00 PM ET / ~22:00-23:00 London time on day D is **after** both the LSE close (16:30
   London) and the Xetra close (17:30 CET) on day D itself, day-D's Treasury/H.15 data can never
   be used for a same-day (day-D) LSE or Xetra execution under this conservative rule. **The
   earliest permissible execution is the next LSE/Xetra trading session that opens after 6:00 PM
   ET on day D** — in practice, this is normally the LSE/Xetra open on **calendar day D+1**,
   subject to:
   - **If D+1 is a US day but not a UK/Eurozone trading day** (a UK bank holiday or Xetra
     holiday that is not also a US SIFMA holiday — e.g. UK Early May bank holiday, which has no
     US equivalent), roll forward to the next day that is open on the **execution** venue (LSE or
     Xetra), while still respecting that the underlying data's "day D" origin does not change
     (do not re-stamp the data as being from the later date).
   - **If day D itself was a US bond-market holiday (SIFMA full close, e.g. Columbus Day,
     Veterans Day, or a day NYSE is open but SIFMA recommends a bond-market close)**, H.15 will
     show **"n.a."/no observation for day D** (see H.15's own "n.a. Not available" convention
     confirmed in the archival footnotes). The execution rule must **skip day D as a data day
     entirely** (carry forward the last valid prior-day observation, or treat it as a genuine
     gap depending on the feature's own missing-data policy) rather than treating "n.a." as a
     zero or interpolated value.
   - **If day D is a US trading/quoting day but falls on a UK or Eurozone holiday** (e.g. the UK
     Early May bank holiday, when NYSE and the Treasury market are open), the data for day D still
     exists and is still governed by the same 6:00 PM ET / next-available-execution-session rule;
     it simply means the "next available LSE/Xetra session" may be more than one calendar day
     after D.
4. **Weekend handling**: if day D is a Friday, the 6:00 PM ET publication instant falls on Friday
   evening; the earliest permissible execution is the **next open LSE/Xetra Monday session**
   (or later if Monday is itself a UK/Eurozone holiday), never a Saturday/Sunday session (LSE and
   Xetra do not trade weekends).
5. **Do not use Treasury/H.15 day-D data for any LSE/Xetra session that opens before 6:00 PM ET
   on day D**, even if that session's local calendar date is already D+1 in London/Frankfurt time
   under certain UTC-offset edge cases late in the US trading day — always gate on the actual
   ET publication instant converted through each side's own current DST rule, not on a naive
   calendar-date-plus-one heuristic.

This rule is deliberately conservative: it assumes the later (6 PM ET) of the two candidate
Treasury-side publication times, and it always requires a full venue-open/close cycle to separate
data availability from execution, which absorbs both the UNVERIFIED FRED-lag risk and the
UNVERIFIED exact-Treasury-post-time risk without needing them resolved to use the data safely.
Before this rule is hard-coded into execution/backtest logic, two follow-ups from this audit
should be closed: (a) confirm FRED's `realtime_start` behavior for a small number of known dates
(a metadata-only, non-value check), and (b) load the ALFRED DGS10 vintage-dates listing (dates
only) to convert the Section A.4 classification from PIT_RECONSTRUCTABLE to either PIT_SAFE or
MINOR_REVISION_RISK with actual evidence rather than analogy-based reasoning.
