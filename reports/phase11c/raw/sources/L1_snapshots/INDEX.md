# L1 classic-literature audit — web capture index

No full-page HTML snapshots were saved for this sub-audit (WebFetch/WebSearch calls return
processed text, not raw HTML, so there was nothing to archive as a distinct capture file).
All decisive numeric claims are instead sourced from downloaded primary-source PDFs kept in
`reports/phase11c/raw/literature/` (git-ignored) and indexed in
`reports/phase11c/raw/literature/SOURCES.txt`. This file logs the secondary web lookups used
only for bibliographic triangulation or for papers whose full text could not be obtained.

| # | URL | Purpose | Tool | Retrieval date |
|---|-----|---------|------|----------------|
| 1 | https://www.nber.org/papers/w9178 | Confirm CP2005 NBER WP metadata | WebSearch | 2026-09-27 |
| 2 | https://academic.oup.com/rfs/article-abstract/25/10/3141/1573606 | Thornton-Valente (2012) RFS abstract page (full text paywalled; fetch returned only nav chrome, no body text) | WebFetch | 2026-09-27 |
| 3 | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1687953 | Thornton-Valente (2012) SSRN abstract (HTTP 403, blocked) | WebFetch | 2026-09-27 |
| 4 | https://repository.essex.ac.uk/5312/ | Attempted Essex repository mirror of Thornton-Valente (2012) (host unreachable: ECONNREFUSED) | WebFetch / curl | 2026-09-27 |
| 5 | https://fedinprint.org/item/fedlwp/10321/original | Attempted redirect resolution for Thornton-Valente (2010) St. Louis Fed WP version | WebFetch | 2026-09-27 |
| 6 | https://www.johnhcochrane.com/research-all/decomposing-the-yield-curve | Locate correct direct-PDF link for Cochrane-Piazzesi (2008) "Decomposing the Yield Curve" | WebFetch | 2026-09-27 |
| 7 | Various WebSearch queries (Cochrane-Piazzesi 2005/2008, Fama-Bliss 1987, Campbell-Shiller 1991, Thornton-Valente 2012, Duffee 2011, Adrian-Crump-Moench 2013, Bauer-Hamilton 2018, Sarno-Schneider-Wagner 2016, Ghysels-Horan-Moench, Liu-Wu 2021) | Locate publisher/working-paper URLs and PDF mirrors | WebSearch | 2026-09-27 |

Notes:
- Thornton & Valente (2012, RFS) full text was NOT obtained. Every claim about it in
  `L1_classic_literature.md` is marked `[ABSTRACT]` or `[UNVERIFIED]` and traceable only to the
  RFS abstract page, the SSRN abstract page, and WebSearch summaries of those pages — never to a
  read of the paper's tables.
- Fama & Bliss (1987) PDF was downloaded (see SOURCES.txt #19) but is a scanned image with no
  extractable text layer; OCR tooling (poppler/tesseract) is not installed in this environment.
  Its numbers are therefore reported only via (a) CP2005's own full-text replication of the
  Fama-Bliss regression (their Table 3, read in full text) and (b) a WebSearch secondary summary,
  both flagged accordingly in the report.
