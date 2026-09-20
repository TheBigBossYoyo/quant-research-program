# PHASE7B_DATA_SOURCE_SELECTION - verified facts for the new information source (retrieved 2026-09-12)

Every row states how the fact was obtained. VERIFIED = fetched from the primary source on 2026-09-12 (URL given); UNVERIFIED = not retrievable (page blocked or JavaScript-only) and must not support a promotion decision. No account was created and nothing was purchased.

## 1. SEC EDGAR (selected source)

| Item | Fact | Status | Source |
| --- | --- | --- | --- |
| Financial Statement Data Sets | numeric XBRL facts from the primary financial statements of all XBRL filers, with SIC codes; quarterly ZIPs from 2009 Q1 to 2026 Q2; reprocessed December 2024 to primary statements only; free; the SEC disclaims accuracy ("not a substitute for such filings") | VERIFIED | https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets |
| Insider Transactions Data Sets | Forms 3, 4 and 5 "as filed", structured, 2006 Q1 to 2026 Q2, quarterly ZIPs, free; filings after 17:30 ET on the last business day of a quarter fall into the next release | VERIFIED | https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets |
| EDGAR APIs | submissions, companyfacts, companyconcept, frames; no authentication; real-time with delays under one minute; nightly bulk ZIPs | VERIFIED | https://www.sec.gov/search-filings/edgar-application-programming-interfaces |
| Submissions API sample (Apple, CIK 320193) | fields include filingDate, reportDate, acceptanceDateTime (e.g. 8-K 2026-07-30T20:30:28Z with items "2.02,9.01"), form, items, isXBRL; 10-Q acceptance 2026-07-31T10:01:02Z for period 2026-06-27 | VERIFIED (fetched with a User-Agent header from Python) | https://data.sec.gov/submissions/CIK0000320193.json |
| Company facts sample | 503 us-gaap concepts; EarningsPerShareDiluted 338 facts with end, val, fy, fp, form, filed (earliest filed 2009-07-22) and calendar frame tags | VERIFIED | https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json |
| Frames sample | Revenues USD CY2019Q1: 2,715 entities in one call | VERIFIED | https://data.sec.gov/api/xbrl/frames/us-gaap/Revenues/USD/CY2019Q1.json |
| Full-text search | JSON results with form, file_date, ciks, display_names, items, sics; "share repurchase program" in 8-K, January 2015: 175 hits | VERIFIED | https://efts.sec.gov/LATEST/search-index?q=... |
| Access rules | SEC asks for a declared User-Agent and fair access (documented limit 10 requests per second); bulk datasets avoid the API for history | policy known from SEC developer pages; rate figure UNVERIFIED today | https://www.sec.gov/os/accessing-edgar-data |
| Licence | US government work, public domain; redistribution not an issue for personal research | VERIFIED by nature of source | - |

Why it qualifies: causal timestamps (acceptanceDateTime, filed), coverage across development (2009-2017), validation (2018-2021) and holdout (2022-2026), zero cost, structured bulk files, and it is exactly the information (insider trades, management signals, accounting facts) that the price-only program lacked.

## 2. Earnings and analyst data at retail vendors (not selected)

| Vendor / product | Relevant content | Point-in-time quality | Price | Status |
| --- | --- | --- | --- | --- |
| EODHD Fundamentals Data Feed | Earnings::History (reportDate, date, beforeAfterMarket, epsActual, epsEstimate, epsDifference, surprisePercent); Earnings::Trend (current consensus only: earningsEstimateAvg/Low/High, revenue, revision counts, quarterly and annual separated in v1.1); statements with per-report "filing_date"; 25+ years for about 11,000 tickers, 6 years for minor names | surprise at report date is causal; consensus history is NOT stored (Trend is a current snapshot) | USD 59.99/month (annual USD 599.90) | VERIFIED content; price from PHASE6_DATA_PROVIDER_AUDIT.md (2026-09-09) |
| Financial Modeling Prep | analyst estimates, price-target and upgrade/downgrade histories, earnings surprises, insider trades endpoints | consensus snapshots as-of dates UNVERIFIED | pricing page returned HTTP 403 on 2026-09-12; third-party summaries put Starter/Premium at USD 29-79/month | UNVERIFIED |
| Finnhub | EPS surprises, recommendation trends (monthly), price targets, insider transactions | history depth and as-of methodology UNVERIFIED | pricing page is JavaScript-only; a 2026 review states "from USD 50 per month per market" | UNVERIFIED |
| Alpha Vantage | Earnings History, Earnings Calendar, Earnings Estimates endpoints exist | fields not extractable from the documentation excerpt fetched | premium USD 49.99/month (from the Phase 6 audit) | UNVERIFIED |
| I/B/E/S (LSEG) via WRDS | the academic standard for point-in-time consensus | institutional access only | not available to an individual | not applicable |

Decision: no retail source documents a point-in-time consensus-estimate history within EUR 50/month; the analyst-revision family therefore stays blocked, and NEW_DATA_SOURCE_JUSTIFIED is not declared. If a vendor later documents as-of consensus snapshots (monthly, 2010 onward) at that price, the family reopens with its own preregistration.

## 3. Evidence sources cited in the audit (retrieved 2026-09-12)

- Martineau, "Rest in Peace Post-Earnings Announcement Drift", Critical Finance Review 11 (2022) 613-646: PEAD absent in large stocks since 2006, recently gone in microcaps. https://www.nowpublishers.com/article/Details/CFR-0122
- 2024 Form 4 filing-date event study (Finance Research Letters, "Insider filings as trading signals - Does it pay to be fast?"): SPY-adjusted CAR +0.534% next session, +1.009% over five sessions (t 6.5 / 5.1), intervals including zero at 21 and 63 sessions. https://www.sciencedirect.com/science/article/pii/S1544612324015435
- Brochet (2010): five-day abnormal return of insider purchases 1.0% pre- and 2.3% post-Sarbanes-Oxley (via the same search). Chen and Zimmermann; Jensen, Kelly and Pedersen: post-publication anomaly returns roughly halved, most characteristics still replicate in reduced form. https://onlinelibrary.wiley.com/doi/10.1111/jbfa.12491 (post-forecast-revision drift, Chen 2020)

## 4. Trading 212 and execution facts carried forward (verified 2026-09-09, PHASE6_COST_MODEL.md)

Long-only, unlevered, fractional orders, 0.15 percent FX each way on conversion, API executes in the primary currency only; US small and mid caps are available as USD instruments (per-instrument availability and minimum quantities UNVERIFIED until read from the instruments endpoint with a read-only key). The recommended program's base cost case therefore assumes a manually funded USD balance (3-5 bps per side) with the automated 20 bps case as the stress case, the reverse of Phase 6, and states so in every result.
