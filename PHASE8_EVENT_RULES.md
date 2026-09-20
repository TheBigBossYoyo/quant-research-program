# PHASE8_EVENT_RULES - insider-purchase event definition (frozen 2026-09-12 before any event return was computed)

Source: SEC Insider Transactions Data Sets, quarterly ZIPs 2006Q1..2017Q4 (data/raw/phase8/sec_insider, hashed in data/metadata/phase8_sec_acquisition_*.jsonl). Tables used: SUBMISSION, REPORTINGOWNER, NONDERIV_TRANS. Field meanings from the SEC readme inside each ZIP.

## 1. Information timestamp and execution timing (causal rule)

- The information timestamp of a filing is its EDGAR FILING_DATE. EDGAR assigns the filing date from the acceptance time; filings accepted after 17:30 ET receive the next business day's date, so FILING_DATE is never earlier than the true acceptance date.
- Entry: the open of the FIRST TRADING DAY STRICTLY AFTER FILING_DATE, whatever the acceptance hour. No same-session fill, no same-day fill.
- Exit (primary): the open 126 trading days after the entry day (about six months), or the last vendor price plus the Phase 6 delisting rule if the series ends first; positions still open at the development end are closed at the last development open (2017-12-29) and their partial return is booked.
- Sensitivities (not independent hypotheses): 63 and 252 trading days; one extra session of delay (entry at the second open after FILING_DATE).

## 2. Transaction filter (row level, NONDERIV_TRANS joined to SUBMISSION and REPORTINGOWNER)

Included only if ALL hold:
1. DOCUMENT_TYPE = '4' (original Form 4). Amendments (4/A), Forms 3, 5, 3/A and 5/A are excluded from the signal. Rationale: the original is what the market saw at FILING_DATE; amendments correct earlier filings and their timestamp is not the information time. Diagnostic: the count of originals later amended is reported and a rerun excluding them is a red-team item.
2. TRANS_CODE = 'P' (open-market or private purchase) and TRANS_ACQUIRED_DISP_CD = 'A'. Every other code (A award, M exercise, F tax withholding, G gift, C conversion, D disposition to issuer, J other, X, I, W, Z, S sale) is excluded.
3. TRANS_FORM_TYPE = '4'.
4. SECURITY_TITLE, lower-cased, matches (common|ordinary|class [abc]\b|capital stock|shares of beneficial interest) and does NOT match (preferred|warrant|unit|note|debenture|right|option|convertible|restricted|deposit|adr|preference). Rationale: only listed common equity; "restricted" purchases are private placements.
5. TRANS_SHARES > 0 and TRANS_PRICEPERSHARE > 0.
6. Price plausibility (excludes private placements at a discount and data errors): TRANS_PRICEPERSHARE within [0.80, 1.20] of the EODHD unadjusted close of the mapped ticker on TRANS_DATE (or the last trading day before it). Rows failing this are excluded and counted.
7. Minimum size (coarse, preregistered, no market-cap scaling): TRANS_SHARES x TRANS_PRICEPERSHARE >= USD 10,000 per row. Rationale: token purchases and dividend-reinvestment-sized trades carry no information.
8. EQUITY_SWAP_INVOLVED = 0 or blank.

Duplicates: within an accession, rows identical on (TRANS_DATE, TRANS_SHARES, TRANS_PRICEPERSHARE, SECURITY_TITLE, DIRECT_INDIRECT_OWNERSHIP) collapse to one; across accessions, rows identical on (ISSUERCIK, RPTOWNERCIK, TRANS_DATE, TRANS_SHARES, TRANS_PRICEPERSHARE) keep the earliest FILING_DATE only.

## 3. Issuer-to-ticker mapping

ISSUERTRADINGSYMBOL upper-cased, stripped, "." replaced by "-", suffixes ".OB"/".PK"/".OTC" removed. The mapped EODHD code must have an unadjusted close within the 5 trading days before TRANS_DATE; if the plain code is not priced at that time, the variants CODE_old, CODE_old1, CODE_old2 are tried; if none is priced, the SEC current mapping (company_tickers.json by ISSUERCIK) is tried; otherwise the row is UNMAPPED and excluded (counted by year in PHASE8_SEC_DATA_AUDIT.md). Filings with a blank symbol use the CIK route only.

## 4. Event = issuer-filing-day

All included rows of one issuer with the same FILING_DATE form one event with: number of distinct reporting owners, total purchase value (sum of shares x price), roles present (Officer, Director, TenPercentOwner, Other from RPTOWNER_RELATIONSHIP; a person listed as Director,Officer counts as both), earliest TRANS_DATE, maximum filing delay in business days (FILING_DATE minus TRANS_DATE), direct/indirect flag.

## 5. Preregistered event categories (five strategy cells)

| Cell | Definition (all causal at FILING_DATE) |
| --- | --- |
| C1 ANY | every event |
| C2 CLUSTER | at least two distinct reporting owners with included purchases of the same issuer filed within the 30 calendar days ending on FILING_DATE (this filing included) |
| C3 OPPORTUNISTIC | Cohen-Malloy-Pomorski adapted: the reporting owner has included purchases of this issuer in at least three distinct prior calendar years; ROUTINE if there is a purchase in the same calendar month as the current TRANS_DATE in each of the three preceding calendar years; OPPORTUNISTIC otherwise. Events with at least one opportunistic owner qualify; owners with fewer than three prior years are unclassified and do not qualify. Burn-in: 2006-2008 |
| C4 OFFICER | at least one purchasing owner whose relationship includes Officer |
| C5 DIRECTOR_ONLY | at least one purchasing owner whose relationship includes Director and no purchasing owner is an Officer |

Diagnostics on every cell (not cells): timely (max delay <= 2 business days) versus late; purchase value above/below the median of the trailing 12 months of events; direct versus indirect ownership.

## 6. Universe eligibility at entry

The mapped ticker must be eligible in the Phase 6 Tier 2 universe (LIQ1000: history >= 252 priced days, unadjusted close >= USD 5, 63-day median dollar volume >= USD 1m, top 1000 by that median, no missing close in 21 days, no zero-volume day in 5, integrity rules I1-I5) at the last month-end signal date on or before the entry day. Events on ineligible names are excluded and counted. Corroboration universe: PIT S&P 1500 membership at that month-end (2012-04 onward).

## 7. Development window and reporting

Entries from 2009-01-02 (three years of burn-in for C3; XBRL era) to 2017-12-28; returns through 2017-12-29 (development end). Reporting windows: 2009-2012 and 2013-2017 (the gate window), plus rolling 36-month windows.
