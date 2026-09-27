# V1 Sub-Audit — Source Index (Treasury UCITS ETF Deployment Metadata)

Sub-audit: V1 (vehicle/instrument metadata). Retrieval date for all rows below: 2026-09-27.
No performance, price, NAV, return, or yield-history data was saved anywhere in this index or its
target files. Where a source page embeds a performance chart/table, only metadata fields were
extracted via a scoped prompt; no raw page capture was saved to disk (WebFetch processes remotely
and returns text — no local HTML/PDF snapshot files were written into the repository by this
sub-audit). Three official factsheet PDFs were fetched but returned as unparseable binary/compressed
data by the fetch tool; no data was extracted from them and nothing was saved to this repository
(noted below for audit-trail completeness; the tool's own transient cache, if any, is outside this
repository and outside this audit's control).

| # | URL | File (or 'quarantine' or 'no data extracted') | Retrieval date | Tag |
|---|-----|------------------------------------------------|-----------------|-----|
| 1 | https://www.ishares.com/uk/individual/en/products/251715/ishares-treasury-bond-13yr-ucits-etf | no data extracted (product page JS content not fully rendered; only partial fields returned) | 2026-09-27 | [ISSUER] |
| 2 | https://www.ishares.com/uk/individual/en/products/251716/ishares-treasury-bond-710yr-ucits-etf | no data extracted (partial) | 2026-09-27 | [ISSUER] |
| 3 | https://www.ishares.com/uk/individual/en/products/272124/ishares-usd-treasury-bond-20-yr-ucits-etf | no data extracted (partial) | 2026-09-27 | [ISSUER] |
| 4 | https://www.ishares.com/uk/individual/en/products/307243/ishares-treasury-bond-0-1yr-ucits-etf | no data extracted (partial) | 2026-09-27 | [ISSUER] |
| 5 | https://www.ishares.com/uk/individual/en/literature/fact-sheet/ibtm-ishares-treasury-bond-7-10yr-ucits-etf-fund-fact-sheet-en-gb.pdf | no data extracted (binary/unparseable PDF; not saved to repo) | 2026-09-27 | [ISSUER] |
| 6 | https://www.ishares.com/uk/individual/en/literature/fact-sheet/ib01-ishares-treasury-bond-0-1yr-ucits-etf-fund-fact-sheet-en-gb.pdf | no data extracted (binary/unparseable PDF; not saved to repo) | 2026-09-27 | [ISSUER] |
| 7 | https://www.ishares.com/ch/individual/en/literature/fact-sheet/idtl-ishares-treasury-bond-20yr-ucits-etf-fund-fact-sheet-en-ch.pdf | no data extracted (binary/unparseable PDF; not saved to repo) | 2026-09-27 | [ISSUER] |
| 8 | https://www.justetf.com/en/etf-profile.html?isin=IE00B14X4S71 | no data extracted / metadata-only (see V1_treasury_ucits_metadata.md) | 2026-09-27 | [SECONDARY] |
| 9 | https://www.justetf.com/en/etf-profile.html?isin=IE00B3VWN518 | metadata-only | 2026-09-27 | [SECONDARY] |
| 10 | https://www.justetf.com/en/etf-profile.html?isin=IE00BSKRJZ44 | metadata-only | 2026-09-27 | [SECONDARY] |
| 11 | https://www.justetf.com/en/etf-profile.html?isin=IE00BGSF1X88 | metadata-only | 2026-09-27 | [SECONDARY] |
| 12 | https://www.justetf.com/en/etf-profile.html?isin=IE00BDFK1573 | metadata-only | 2026-09-27 | [SECONDARY] |
| 13 | https://www.justetf.com/en/etf-profile.html?isin=IE00BD8PGZ49 | metadata-only | 2026-09-27 | [SECONDARY] |
| 14 | https://www.justetf.com/en/etf-profile.html?isin=IE00BGPP6697 | metadata-only | 2026-09-27 | [SECONDARY] |
| 15 | https://www.trading212.com/trading-instruments/invest/IBTS.GB | metadata-only (title/URL only; full page fetch returned 403) | 2026-09-27 | [T212] |
| 16 | https://www.trading212.com/trading-instruments/invest/IBTA.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 17 | https://www.trading212.com/trading-instruments/invest/IBTG.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 18 | https://www.trading212.com/trading-instruments/invest/IBTU.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 19 | https://www.trading212.com/trading-instruments/invest/IDTL.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 20 | https://www.trading212.com/trading-instruments/invest/IBTL.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 21 | https://www.trading212.com/trading-instruments/invest/DTLE.GB | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 22 | https://www.trading212.com/trading-instruments/invest/IBB1.DE | metadata-only (title/URL only; 403 on direct fetch) | 2026-09-27 | [T212] |
| 23 | https://www.trading212.com/trading-instruments/invest/IB01.GB | UNVERIFIED (generic page title only, could not confirm instrument-specific content; 403 on direct fetch) | 2026-09-27 | [T212]/[UNVERIFIED] |
| 24 | https://community.trading212.com/t/ishares-usd-treasury-bond-1-3yr-ucits-etf-eur-hedged-acc/60080 | metadata-only (forum thread; ambiguous whether a fulfilled or pending feature request) | 2026-09-27 | [T212]/[UNVERIFIED] |
| 25 | https://community.trading212.com/t/request-usd-treasury-bond-20-years-ishares-etf/18324 | metadata-only (older forum request thread; superseded by confirmed live IDTL.GB/DTLE.GB/IBTL.GB pages) | 2026-09-27 | [T212]/[SECONDARY] |
| 26 | (WebSearch aggregation, no single URL) SPDR Bloomberg 1-3 Year U.S. Treasury Bond UCITS ETF | metadata-only | 2026-09-27 | [SECONDARY] |
| 27 | https://www.justetf.com/en/etf-profile.html?isin=LU0429458895 (Xtrackers II US Treasuries 1-3 UCITS ETF 1D) | metadata-only (ISIN/ticker only, not deep-profiled) | 2026-09-27 | [SECONDARY] |
| 28 | https://www.justetf.com/en/etf-profile.html?isin=LU2662649685 (Xtrackers II US Treasuries 7-10 UCITS ETF 1D) | metadata-only (ISIN/ticker only, not deep-profiled) | 2026-09-27 | [SECONDARY] |
| 29 | https://www.justetf.com/en/etf-profile.html?isin=LU1407888053 (Amundi US Treasury Bond 7-10Y UCITS ETF Dist) | metadata-only (ISIN/ticker/TER only) | 2026-09-27 | [SECONDARY] |
| 30 | https://www.justetf.com/en/etf-profile.html?isin=LU1407890620 (Amundi US Treasury Bond Long Dated UCITS ETF Dist) | metadata-only (ISIN/ticker/TER only; NOTE: tracks 10+yr min maturity, not a strict 20+yr match) | 2026-09-27 | [SECONDARY] |
| 31 | https://www.amundietf.co.uk/en/professional/products/fixed-income/amundi-us-treasury-bond-01y-ucits-etf-acc/lu2182388665 | metadata-only (ISIN only) | 2026-09-27 | [SECONDARY] |
| 32 | https://www.amundietf.co.uk/en/professional/products/fixed-income/amundi-us-treasury-bond-01y-ucits-etf-eur-hedged-acc/lu2182388749 | metadata-only (ISIN only) | 2026-09-27 | [SECONDARY] |
| 33 | https://www.ishares.com/us/literature/brochure/ishares-currency-hedged-product-brief.pdf | metadata-only (general hedging methodology description, US-market brochure, used only as a generic description of monthly-rolling-forward mechanics — not a UCITS-specific prospectus) | 2026-09-27 | [ISSUER]/[SECONDARY] |

Note on quarantine folder: `V1_snapshots/QUARANTINE_UNREAD_MAY_CONTAIN_PRICE_DATA/` is present per protocol but
no files were placed in it — this sub-audit did not save any raw page/PDF captures locally. All
extraction was done through prompt-scoped fetches with explicit performance-data exclusion instructions,
and any performance/price/yield figures that appeared incidentally in tool output (e.g. a bid/ask quote,
a dividend-yield percentage, a weighted-average-YTM figure) were discarded and are NOT recorded in
V1_treasury_ucits_metadata.md/.csv or anywhere else in this repository.
