# D2 snapshots index — Phase 11C GSW/ACM/Fama-Bliss/Liu-Wu PIT audit

Retrieval date for all rows: 2026-09-27. No yield/term-premium/return VALUE files were downloaded or read (hard rule). Only documentation/metadata was captured.

| URL | Local file | Content type | Retrieval date | Notes |
|---|---|---|---|---|
| https://web.archive.org/cdx/search/cdx?url=federalreserve.gov/data/yield-curve-tables/feds200628.csv&output=json&fl=timestamp,digest,length | cdx_feds200628_raw.json | Wayback CDX API response (metadata, not data values) | 2026-09-27 | Service unavailable: HTTP 503 "Internet Archive: Temporarily Offline" on repeated attempts (see log below). This is API metadata (timestamps/digests), not yield data, and is explicitly permitted by the hard rules — capture attempt failed for infrastructure reasons, not a rule violation. |
| https://web.archive.org/cdx/search/cdx?url=federalreserve.gov/econresdata/researchdata/feds200628.csv&output=json&fl=timestamp,digest,length | cdx_feds200628_econresdata.json | Wayback CDX API response (metadata) | 2026-09-27 | Same outage; HTTP 503. |
| https://web.archive.org/cdx/search/cdx?url=federalreserve.gov*&matchType=domain&limit=5&output=json | (not saved, transient) | Wayback CDX API response (metadata) | 2026-09-27 | One anomalous HTTP 200 returned `[]` (empty) — not usable as evidence of zero captures; matchType=domain query syntax likely malformed, and the surrounding attempts on the correct query all 503'd. Treated as inconclusive, not as a real result. |

## CDX outage log (raw HTTP status codes, no content read)
9 attempts total across ~6 minutes, spaced with delays:
1. HTTP 503 (http://)
2. HTTP 503 (https://)
3. HTTP 503
4. HTTP 000 (connection failure)
5. HTTP 503
6. HTTP 200 but empty `[]` for a differently-shaped query (matchType=domain) — inconclusive
7. HTTP 503
8. HTTP 503
9. HTTP 503 (final attempt)

Conclusion: the Wayback Machine CDX API was not reachable in a usable state during this audit window (2026-09-27, US afternoon). This is consistent with well-documented extended Internet Archive service instability since the October 2024 DDoS/security incident, with intermittent recurrences into 2025-2026. archive.org's own homepage returned HTTP 200 at the same time, indicating the outage is specific to backend services (CDX/wayback machine) rather than total site downtime.

**Action for a future session**: retry the identical CDX queries listed above (feds200628.csv current path, feds200628.csv legacy econresdata path, and the ACM/Kim-Wright data file URLs) when the service is confirmed up (check `https://web.archive.org/cdx/search/cdx?url=example.com&output=json&limit=1` returns real JSON first). Do not conclude PIT_BLOCKED for archivability from this outage alone — re-test before finalizing that classification element.

## Documentation pages read (WebFetch — HTML/text, not data files)
| URL | Retrieval date | Tag |
|---|---|---|
| https://www.federalreserve.gov/data/nominal-yield-curve.htm | 2026-09-27 | OFFICIAL |
| https://www.federalreserve.gov/data/yield-curve-tables/feds200628_1.html | 2026-09-27 | OFFICIAL (legacy/pre-Nov-2019 vintage page, still live) |
| https://www.federalreserve.gov/pubs/feds/2006/200628/200628abs.html | 2026-09-27 | OFFICIAL |
| https://www.federalreserve.gov/econres/feds/the-us-treasury-yield-curve-1961-to-the-present.htm | 2026-09-27 | OFFICIAL |
| https://www.federalreserve.gov/data/yield-curve-models.htm | 2026-09-27 | OFFICIAL |
| https://www.federalreserve.gov/pubs/feds/2006/200628/200628pap.pdf | 2026-09-27 | OFFICIAL (fetched but not machine-readable via WebFetch; binary PDF, not opened/read as data — this is the methodology PAPER, not a yield-value data file, and permitted, but extraction failed) |
| https://www.newyorkfed.org/research/data_indicators/term-premia-tabs | 2026-09-27 | OFFICIAL (thin content via fetch) |
| https://sites.google.com/view/jingcynthiawu/yield-data | 2026-09-27 | OFFICIAL (author's site) |
| https://ionmihai.github.io/finsets/02_papers/gurkaynak_etal_2007.html | 2026-09-27 | SECONDARY |
| https://www.federalreserve.gov/econresdata/researchdata/feds200628.html | 2026-09-27 | OFFICIAL — HTTP 404 (page retired) |

WebSearch queries used for corroboration are listed in the bibliography of D2_gsw_acm_fb_vintage_audit.md.
