# Phase 11C / D1 — Web capture index

Retrieval date for all rows below: 2026-09-27 (WebFetch/WebSearch tool calls, this session).
Only one source returned a raw downloadable file (an archival PDF); all other sources were
read through WebFetch's HTML->markdown text extraction (no raw HTML saved locally) or WebSearch
result snippets. This index records URL -> local file (if any) -> retrieval date for every
source cited in `D1_h15_treasury_pit_audit.md`.

| # | URL | Local file | Retrieval date | Note |
|---|-----|-----------|-----------------|------|
| 1 | https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology | (text extract only, no file) | 2026-09-27 | Current par-yield-curve methodology, monotone convex, input maturities |
| 2 | https://www.federalreserve.gov/releases/h15/ | (text extract only) | 2026-09-27 | Current H.15 page, publication schedule text |
| 3 | https://alfred.stlouisfed.org/help/downloaddata | (text extract only) | 2026-09-27 | ALFRED vintage-date mechanics documentation |
| 4 | https://www.sifma.org/resources/guides-playbooks/holiday-schedule | (text extract only) | 2026-09-27 | 2026/2027 US bond-market full/early close schedule |
| 5 | https://fred.stlouisfed.org/series/DGS10 | (text extract only) | 2026-09-27 | Series metadata (title/units/frequency/source); no values recorded |
| 6 | https://fred.stlouisfed.org/series/DGS30 | (text extract only) | 2026-09-27 | Confirms 2002-02-18 to 2006-02-09 discontinuation gap |
| 7 | https://fred.stlouisfed.org/series/DGS20 | (text extract only) | 2026-09-27 | Metadata only; no explicit start date surfaced in rendered text |
| 8 | https://fred.stlouisfed.org/series/DGS1MO | (text extract only) | 2026-09-27 | Metadata only; no explicit start date surfaced in rendered text |
| 9 | https://fred.stlouisfed.org/series/DGS2MO | HTTP 404 | 2026-09-27 | Series does not exist on FRED |
| 10 | https://fred.stlouisfed.org/series/DGS4MO | HTTP 404 | 2026-09-27 | Series does not exist on FRED |
| 11 | https://fred.stlouisfed.org/release/tables?rid=18&eid=819 | HTTP 404 | 2026-09-27 | Attempted release-table metadata view; not reachable via WebFetch |
| 12 | https://www.federalreserve.gov/releases/h15/current/h15.pdf | `frb_h15_20161003_archival.pdf` (this folder) | 2026-09-27 | Actual PDF served was an archival Oct 3, 2016 H.15 PDF (current release is no longer distributed as PDF; see audit notes). Footnotes/methodology text used; numeric yield table in the file was NOT transcribed or used as a fact source. |
| 13 | https://www.cashmarket.deutsche-boerse.com/cash-en/Trading-calendar-and-trading-hours-22048 | (text extract only) | 2026-09-27 | Official Deutsche Börse Xetra/Frankfurt hours and 2026 non-trading dates |
| 14 | https://www.londonstockexchange.com/equities-trading/business-days | (JS-rendered, no content retrievable via WebFetch) | 2026-09-27 | Attempted official LSE holiday page; blocked by client-side rendering |
| 15 | WebSearch: "London Stock Exchange official trading hours" | (search snippets only) | 2026-09-27 | LSE FAQ text on trading hours 8:00-16:30 and closing auction 16:30-16:35, secondary aggregator confirmation |
| 16 | WebSearch: "UK bank holidays 2026 gov.uk" | (search snippets only) | 2026-09-27 | Official GOV.UK 2026 England & Wales bank holiday list (via GOV.UK's own X/social post, cross-referenced) |
| 17 | WebSearch: "Treasury Nominal Coupon-Issue TNC yield curve spot rates" | (search snippets only) | 2026-09-27 | Confirms TNC spot-rate curve exists, monthly/quarterly/EOM series, home.treasury.gov/data/treasury-coupon-issues-and-corporate-bond-yield-curves |
| 18 | WebSearch: "daily treasury par yield curve rates posted 3:30pm/4pm/6pm" | (search snippets only) | 2026-09-27 | Treasury posting-time claim (~6:00pm ET) — flagged UNVERIFIED, could not confirm on an official page directly |
| 19 | WebSearch: SIFMA press releases (Good Friday/Easter, Memorial Day 2026) | (search snippets only) | 2026-09-27 | Corroborating SIFMA recommendation press releases |
