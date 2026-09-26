# INTERRUPTED_UNVERIFIED_ARTIFACT — Phase 11A retail-product material

**Status of this whole directory: PARTIAL_TERMINATED_NON_DECISION_CRITICAL.**

* The product agent was interrupted before it produced a complete, verified inventory. The browser page-scripting
  permission was withdrawn mid-session, and the stage was stopped on 2026-09-26 after the mechanism gate failed.
* The 16 files in this directory are the partial metadata that was recovered. They are preserved exactly as produced.
* They contain **metadata only**: names, tickers, ISINs, venues, fees, hours and survivorship notes. No price, NAV,
  performance or return figure was recorded.
* They were **not** used to select instruments or to inspect returns. No final CFTC → ETP mapping was certified.

## `product_metadata.csv` — INTERRUPTED_UNVERIFIED_ARTIFACT

* **Malformed.** The header declares 21 columns, but 18 of the 47 data rows have 22–23 fields (unquoted commas) and one
  has 20. A strict CSV parser cannot read it, and positional parsing silently shifts columns.
* **Incomplete.** 31 of its 47 rows were never checked on Trading 212. Many ISINs, TERs and inception dates are
  `UNVERIFIED` or aggregator-sourced only.
* **Not repaired, and must not be used analytically.** SHA-256 at finalization:
  `4a793fd24def4f07a7f39ec4c151c926ffaef287f20aac88ffae557909d43714`.

Any reopening of Phase 11A must rebuild the product inventory from primary sources rather than start from this file.
See `research/phase11a/PHASE11A_STAGE0_AUDIT.md` §6–§10.
