# PHASE6_EODHD_COVERAGE_AUDIT - what the purchased EODHD subscriptions actually cover (2026-09-11)

Status: section 1 (facts verified before any bulk download) and section 2 (audit rules) were written before
the audit script ran; section 3 is filled from reports/PHASE6_EODHD_AUDIT_<stamp>/audit.json afterwards and
records the numbers without changing the rules. No strategy return was computed before section 3 was complete.

## 1. Subscriptions verified through the API (2026-09-11, token from the user environment, never persisted)

| Item | Verified fact | Evidence |
| --- | --- | --- |
| Account | /api/user: subscriptionMode paid, subscriptionType monthly, dailyRateLimit 100,000, extraLimit 500 | research/phase6_eodhd.py `verify_subscription` (personal fields dropped) |
| EOD Historical Data - All World | /api/eod/{ticker}.US returns full history from 1985-01-01 for active and delisted tickers (AAPL 10,504 rows from 1985-01-02; ENRNQ 1,731 rows 1997-12-31..2004-11-17); fields Date, Open, High, Low, Close, Adjusted_close, Volume; 1 API call per ticker | data/metadata/phase6_eodhd_acquisition_*.jsonl |
| Exchange symbol lists | active US 51,090 tickers (17,882 Common Stock); delisted US 60,075 (32,984 Common Stock); no code appears in both; 2,712 delisted codes carry `_old`/`_old1` suffixes for reused symbols; "US" pseudo-venue holds notes/units/warrants | data/raw/phase6/eodhd/symbols/{active,delisted}_US.json |
| Indices Historical Constituents Data API (marketplace, unicornbay/spglobal) | /api/mp/unicornbay/spglobal/list (110 indices, 85 in USD) and /comp/{ID} (path parameter; the query form `?id=` returns HTTP 500) with Components (current, with Sector/Industry/Weight) and HistoricalTickerComponents (Code, Name, StartDate, EndDate, IsActiveNow, IsDelisted); 10 API calls per request | data/raw/phase6/eodhd/constituents/{list,comp_GSPC,comp_MID,comp_SML}.json |
| Not included | /api/fundamentals (index HistoricalTickerComponents, sector, market cap) and /api/symbol-change-history return HTTP 403 | acquisition log |

### Measured constituent coverage (raw counts from the saved JSON, before any price download)

| Index | Historical rows | Earliest StartDate | Earliest EndDate | EndDates before 2012-04 | Reading |
| --- | ---: | --- | --- | ---: | --- |
| S&P 500 (GSPC.INDX) | 822 | 1957-03-04 | 2008-09-16 (Lehman, single row) | 1 | Start dates of members alive in April 2012 are known back to 1957, but removals before April 2012 are absent: every pre-2012 reconstruction is conditioned on surviving to April 2012. Point-in-time from 2012-04-04 only |
| S&P 400 (MID.INDX) | 1,018 | 2012-04-04 | 2012-04-10 | 0 | Point-in-time from 2012-04-04 |
| S&P 600 (SML.INDX) | 1,502 | 2012-04-04 | 2012-04-04 | 0 | Point-in-time from 2012-04-04 |

Marketing states "up to 12 years"; the vendor landing page states "12 years" for the four S&P indices. The measured record is consistent with that: continuous membership changes begin 2012-04-04. The development segment (< 2018-01-01) therefore contains 69 months (2012-04..2017-12) of point-in-time S&P 1500 membership. That is the whole point-in-time development sample this product can supply.

Consequences fixed now:
1. Tier 1 universe (PIT_SP1500): members of the S&P 500, 400 or 600 on t-1 per HistoricalTickerComponents, rebalance months 2012-04-30..2017-11-30 (signals) with returns to 2017-12-31. Sector labels exist only for current members (Components.Sector) and are therefore NOT point-in-time and NOT available for departed members; any sector-neutral stock ranking on Tier 1 is a degraded diagnostic and will be labelled SECTOR_NOT_PIT.
2. Tier 2 universe (LIQ1000_NO_PIT_MEMBERSHIP): the preregistered EODHD fallback of PHASE6_UNIVERSE_CONSTRUCTION.md section 7: all US common stocks (active and delisted, every venue, because a failed company's last venue is often OTC), eligibility by lagged liquidity rank only, labelled NO_PIT_MEMBERSHIP in every result. Its start year is set by the survivorship rule in section 2, not by hand.
3. Industry momentum at stock level is replaced by the deployable sector-ETF version (nine SPDR sector ETFs from 1998-12-22, XLRE from 2015-10 excluded for history) because EODHD supplies no historical sector for stocks; ETF histories were downloaded (data/metadata/phase6_eodhd_etf_manifest.json) together with SPY/IVV/VTI/IWM/MDY/IJR/IJH/RSP as deployable benchmarks.

## 2. Audit rules (fixed before the audit script ran)

| Test | Rule | Consequence of failure |
| --- | --- | --- |
| A1 constituent price coverage | share of member-months (2012-04..2017-12) with >= 15 priced days per index >= 0.97; delisted members' coverage reported separately | < 0.97: Tier 1 results carry the flag PIT_COVERAGE_GAP and the gate document treats Tier 1 as unusable if < 0.90 |
| A2 delisted-history depth | delisted share of the yearly top-1000 approximate-dollar-volume universe; survivorship-safe start year = first year whose delisted share >= 0.75 x the 2003-2007 mean share (older years must show at least as many delisted names as 2003-2007, because more time has elapsed for them to delist; a lower share can only mean missing histories) | Tier 2 starts at that year; earlier years are never used for any result; if the start year is after 2005 the pre-2005 eras are recorded as NOT TESTABLE on EODHD |
| A3 reconciliation | 17 known failures/acquisitions: present with last price date within one month of the expected month | any absent failure blocks Tier 2 results until explained; truncation before the final trading days (Bear Stearns type) is recorded as a limitation of the delisting-return rule |
| A4 ticker reuse | constituent spells whose EOD series does not cover the spell (first date > spell start + 30 days or last date < spell end - 30 days) | share > 0.05 in any index: the affected spells are excluded and counted; if excluded spells are disproportionately IsDelisted, Tier 1 carries SURVIVORSHIP_RESIDUAL |
| A5 splits | nine well-known splits: unadjusted close ratio within 15 percent of the split ratio and adjusted_close continuous | any failure: adjusted_close is not used for returns until the cause is understood |
| A6 integrity | no non-positive closes; zero-volume days counted; duplicate dates removed by the loader | descriptive |

The delisting-return rule of PHASE6_UNIVERSE_CONSTRUCTION.md section 5 applies unchanged (Shumway haircuts on distress-proxy delistings; sensitivities -100 percent and -30 percent-on-all).

## 3. Audit results

(filled after reports/PHASE6_EODHD_AUDIT_<stamp>/audit.json exists)

### 3.0 Source: reports/PHASE6_EODHD_AUDIT_20260911T223343/audit.json

### 3.1 A1 constituent price coverage (2012-04..2017-12)

| Index | Spells | Member-months | Covered | Coverage | Spells without any price file | Delisted spells | Delisted coverage | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GSPC | 633 | 33722 | 32592 | 0.9665 | 2 | 156 | 0.9033 | PIT_COVERAGE_GAP |
| MID | 608 | 26438 | 25029 | 0.9467 | 3 | 247 | 0.9238 | PIT_COVERAGE_GAP |
| SML | 869 | 38805 | 37167 | 0.9578 | 6 | 422 | 0.9528 | PIT_COVERAGE_GAP |

### 3.2 A2 delisted-history depth

Delisted common stocks with at least one row: 32978.
First-date year of delisted histories: 1985: 306, 1986: 43, 1987: 48, 1988: 28, 1989: 27, 1990: 35, 1991: 45, 1992: 77, 1993: 85, 1994: 189, 1995: 194, 1996: 187, 1997: 3887, 1998: 434, 1999: 2421, 2000: 719, 2001: 1143, 2002: 480, 2003: 639, 2004: 661, 2005: 656, 2006: 666, 2007: 1055, 2008: 604, 2009: 636, 2010: 740, 2011: 638, 2012: 665, 2013: 825, 2014: 1009, 2015: 852, 2016: 1071, 2017: 1654, 2018: 1153, 2019: 1217, 2020: 1792, 2021: 2860, 2022: 1020, 2023: 604, 2024: 404, 2025: 824, 2026: 385

Last-date year of delisted histories: 1998: 220, 1999: 791, 2000: 789, 2001: 730, 2002: 453, 2003: 344, 2004: 342, 2005: 355, 2006: 364, 2007: 403, 2008: 322, 2009: 262, 2010: 318, 2011: 312, 2012: 346, 2013: 314, 2014: 326, 2015: 483, 2016: 610, 2017: 1527, 2018: 2225, 2019: 1954, 2020: 1957, 2021: 3533, 2022: 3053, 2023: 2792, 2024: 2358, 2025: 2786, 2026: 2709

| Year | Names with >= 120 priced days | Delisted share of top-1000 by approximate dollar volume | Min dollar volume in top 1000 |
| --- | ---: | ---: | ---: |
| 1985 | 883 | 0.260 | 0 |
| 1986 | 959 | 0.265 | 0 |
| 1987 | 1056 | 0.269 | 499 |
| 1988 | 1106 | 0.272 | 1,351 |
| 1989 | 1163 | 0.276 | 2,810 |
| 1990 | 1207 | 0.284 | 3,081 |
| 1991 | 1257 | 0.284 | 5,756 |
| 1992 | 1401 | 0.295 | 22,503 |
| 1993 | 1566 | 0.308 | 62,948 |
| 1994 | 1777 | 0.315 | 93,938 |
| 1995 | 1926 | 0.326 | 146,390 |
| 1996 | 2190 | 0.339 | 303,316 |
| 1997 | 2430 | 0.334 | 514,499 |
| 1998 | 5140 | 0.694 | 5,043,503 |
| 1999 | 6425 | 0.719 | 7,916,469 |
| 2000 | 6683 | 0.716 | 13,334,070 |
| 2001 | 6570 | 0.664 | 10,285,328 |
| 2002 | 6501 | 0.620 | 8,960,940 |
| 2003 | 6470 | 0.615 | 10,213,305 |
| 2004 | 6904 | 0.634 | 16,249,164 |
| 2005 | 7144 | 0.607 | 19,216,795 |
| 2006 | 7383 | 0.604 | 25,692,702 |
| 2007 | 7592 | 0.584 | 36,225,047 |
| 2008 | 7589 | 0.543 | 33,754,506 |
| 2009 | 7505 | 0.514 | 26,263,307 |
| 2010 | 7736 | 0.532 | 31,532,293 |
| 2011 | 7820 | 0.530 | 34,065,556 |
| 2012 | 7814 | 0.517 | 30,795,263 |
| 2013 | 7992 | 0.507 | 36,691,676 |
| 2014 | 8415 | 0.521 | 46,062,038 |
| 2015 | 8553 | 0.485 | 45,445,217 |
| 2016 | 8602 | 0.473 | 47,143,594 |
| 2017 | 8694 | 0.455 | 48,307,112 |

Reference 2003-2007 mean delisted share 0.609; rule: first year with share >= 0.75 x reference -> **survivorship-safe Tier 2 start year = 1998**.

### 3.3 A3 reconciliation of known failures and acquisitions

| Code | Event | Expected month | EODHD first | EODHD last | Within one month |
| --- | --- | --- | --- | --- | --- |
| ENRNQ | failure Enron (NYSE delisting 2002-01; OTC trading continued) | 2002-01 | 1997-12-31 | 2004-11-17 | NO |
| MCWEQ | failure WorldCom | 2002-07 | 2001-06-08 | 2004-04-20 | NO |
| BSC_old | failure Bear Stearns | 2008-05 | 1999-01-04 | 2008-03-14 | NO |
| LEH | failure Lehman Brothers | 2008-09 | 1997-12-31 | 2008-09-17 | yes |
| WAMUQ | failure Washington Mutual | 2008-09 | 1997-12-31 | 2012-03-20 | NO |
| CCTYQ | failure Circuit City | 2009-01 | 1997-12-31 | 2011-09-26 | NO |
| GM_old | failure General Motors (old) | 2009-06 | 1997-12-31 | 2011-03-31 | NO |
| BLIAQ | failure Blockbuster (BB Liquidating) | 2010-07 | 2019-11-11 | 2026-09-10 | NO |
| EKDKQ | failure Eastman Kodak (old) | 2012-01 | 1997-12-31 | 2013-09-03 | NO |
| RSH | failure RadioShack | 2015-02 | 2003-09-10 | 2015-02-02 | yes |
| SUNEQ | failure SunEdison | 2016-04 | 2016-01-04 | 2017-12-29 | NO |
| CPQ | acquisition Compaq | 2002-05 | 1999-01-04 | 2002-05-03 | yes |
| G_old | acquisition Gillette | 2005-10 | 1997-12-31 | 2005-09-30 | yes |
| BUD_old | acquisition Anheuser-Busch | 2008-11 | 1997-12-31 | 2008-11-17 | yes |
| WYE | acquisition Wyeth | 2009-10 | 1997-12-31 | 2009-10-15 | yes |
| BNI | acquisition Burlington Northern | 2010-02 | 1997-12-31 | 2010-02-12 | yes |
| HNZ | acquisition Heinz | 2013-06 | 2003-09-10 | 2013-06-07 | yes |

Present 17/17; within one month 8/17.

### 3.4 A4 ticker-reuse / spell coverage mismatches

| Index | Spells | Mismatches | Share |
| --- | ---: | ---: | ---: |
| GSPC | 633 | 28 | 0.044 |
| MID | 608 | 40 | 0.066 |
| SML | 869 | 52 | 0.060 |

Examples: ADT (ADT Inc, series does not cover spell, spell 2012-10-01..2016-05-03, series 2018-01-19..2026-09-11); ALTR (Altair Engineering Inc, series does not cover spell, spell 2012-04-04..2015-12-29, series 2017-11-01..2025-03-25); BEAM (Beam Therapeutics Inc, series does not cover spell, spell 2012-04-04..2014-05-01, series 2020-02-06..2026-09-11); BTU (Peabody Energy Corp, series does not cover spell, spell 2012-04-04..2014-09-22, series 2017-04-03..2026-09-11); COV (Covidien plc, series does not cover spell, spell 2012-04-04..2015-01-27, series 2007-06-14..2012-06-15); DEN (Denbury Resources Inc, series does not cover spell, spell 2012-04-04..2015-03-23, series 2020-09-21..2023-11-03); DNB (Dun & Bradstreet Holdings Inc., series does not cover spell, spell 2012-04-04..2017-04-05, series 2020-07-01..2025-08-25); DO (Diamond Offshore Drilling Inc, series does not cover spell, spell 2012-04-04..2016-10-03, series 2022-03-30..2024-09-04); DTV (DTE Energy Co, series does not cover spell, spell 2012-04-04..2015-07-29, series 2016-10-11..2019-09-30); EMC (Global X Emerging Markets Great Consumer ETF, series does not cover spell, spell 2012-04-04..2016-09-08, series 2023-05-15..2026-09-11); FRX (Forest Road Acquisition Corp., series does not cover spell, spell 2012-04-04..2014-07-01, series 2021-01-15..2021-06-25); HSH (Hillshire Brands Company, series does not cover spell, spell 2012-04-04..2012-06-29, series 2012-06-29..2020-07-21)

### 3.5 A5 split reconciliation

| Code | Date | Expected ratio | Unadjusted close ratio | Adjusted close ratio | Consistent |
| --- | --- | ---: | ---: | ---: | --- |
| AAPL | 2014-06-09 | 7.0 | 6.890 | 0.984 | True |
| AAPL | 2005-02-28 | 2.0 | 1.984 | 0.992 | True |
| MSFT | 2003-02-18 | 2.0 | 1.935 | 0.968 | True |
| NVDA | 2007-09-11 | 1.5 | 1.469 | 0.979 | True |
| GOOGL | 2014-04-03 | 2.0 | 1.986 | 0.994 | True |
| AMZN | 1999-09-02 | 2.0 | 1.982 | 0.991 | True |
| WMT | 1999-04-20 | 2.0 | 1.880 | 0.940 | True |
| CSCO | 2000-03-23 | 2.0 | 1.855 | 0.928 | True |
| C | 2011-05-09 | 0.1 | 0.102 | 1.024 | True |

Consistent 9/9.

### 3.6 A6 integrity

Files with rows 50874; empty 16; request errors 1; files with a non-positive close 3979; zero-volume days in total 22150370.

### 3.7 Interpretation and consequences (written before E051)

- A1: coverage 0.947-0.966 in all three indices: above the 0.90 usability floor, below the 0.97 target -> Tier 1 results carry PIT_COVERAGE_GAP. Delisted members' coverage 0.90-0.95: departed names are mostly, not entirely, priced.
- A2: delisted histories start overwhelmingly in 1997-1999 (3,887 begin in 1997, 2,421 in 1999); the delisted share of the top-1000 jumps from 0.33 (1997) to 0.69 (1998). Rule A2 -> **Tier 2 survivorship-safe start year 1998**. Years 1990-1997 are NOT TESTABLE on EODHD; the stock-level eras are E2b 1998-1999 (24 months), E3 2000-2009, E4 2010-2017.
- A3: 17 of 17 names present; under the literal rule only 8 of 17 end within one month of the exchange event because six failures continue trading OTC in EODHD (more complete than the rule assumed) and SunEdison was pointed at the wrong code. Gate Amendment 1 (PHASE6_NORGATE_PURCHASE_GATE.md section 8) re-reads the rule; amended count 15 of 17 captured, 16 of 17 present. Genuine defects: Bear Stearns ends 2008-03-14 (before the collapse week; the -85 percent is not in the data), Blockbuster's 2010 failure is absent (BLIAQ is another company).
- A4: mismatch shares 4.4 / 6.6 / 6.0 percent (GSPC / MID / SML). The universe builder remaps a mismatched spell to the delisted `_old` variant when that series covers the spell (61 of 2,110 point-in-time spells remapped, 59 dropped). Dropped spells are counted in E051 meta; Tier 1 carries SURVIVORSHIP_RESIDUAL because the dropped spells are predominantly companies whose ticker was reused after a failure or acquisition.
- A5: 9 of 9 splits consistent; adjusted_close is used for total returns; unadjusted close for the price filter; split factors from the splits endpoint for dollar volume.
- A6: 3,979 files contain a non-positive close (vendor errors); the panel reader treats non-positive prices as missing (rule fixed before any result).

### 3.8 Data-integrity rules I1-I5 (fixed 2026-09-12 after the aborted first E051 attempt, before any valid stock-level result)

The aborted attempt (reports/E051_aborted_20260912T0010_data_integrity) showed vendor errors passing the eligibility filters:
placeholder prices of exactly 1,000,000, split factors of zero, one-day jumps of 6,000x in the unadjusted close, adjusted closes
inconsistent with the unadjusted series. The following mechanical rules are applied identically to every strategy and every
benchmark; none uses a return to decide anything about a strategy.

| Rule | Definition | Where |
| --- | --- | --- |
| I1 split sanity | split ratios outside [1/50, 50] are ignored (vendor error) | panel build |
| I2 price sanity | open/close/adjusted close <= 0 or >= 500,000 treated as missing (BRK-A peaks below 300,000 in development) | panel reader |
| I3 extreme day | a split-adjusted daily close return > +200 percent or < -75 percent marks the name unclean for the next 252 trading days (ineligible at any signal date in that window) | universe features |
| I4 adjusted/unadjusted consistency | at month-ends, a month whose adjusted-close return differs from the split-adjusted-close return by more than 10 percent (abs((1+r_adj)/(1+r_split) - 1) > 0.10) is inconsistent; a name is ineligible at t if any of the 12 month-ends t-11..t is inconsistent (the momentum window) | universe features |
| I5 holding-month substitution | if a held name's open-to-open adjusted return differs from its split-adjusted open-to-open return by more than 10 percent, the split-adjusted return is booked (dividend omitted for that month); substitutions are counted | holding returns |

Consequence: the eligible universe shrinks by the unclean names each month (counted in E051 meta); genuine multi-hundred-percent
single-day moves in liquid names are excluded for a year as a side effect, symmetrically for strategy and benchmark.
