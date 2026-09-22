# PHASE 10A — point-in-time audit

Date: 2026-09-22. Schema, timing and coverage tests only. No returns computed. Evidence in
`reports/phase10a/raw/`.

## The requirement

Every usable observation needs: issuer identifier, settlement/reference date, **public release date**,
short-interest quantity, and — if used — shares outstanding/float and the volume input behind days to
cover. A backtest may only enter **after public dissemination**.

A dataset that carries only the settlement date is still acceptable **if an official publication
calendar deterministically reconstructs the release timing**. That escape clause turns out to matter,
because none of the three primary sources embeds a release date in the data itself.

---

## T1 — Is it short interest or short-sale volume?

| source | verdict |
| --- | --- |
| NYSE `/NYSEGroupConsolidatedShortInterest/` | short interest, **aggregate only** |
| NYSE `/ShortData/*shvol/` | short-sale **volume** — excluded by definition, not used |
| NYSE Group Short Interest (paid) | short interest, issue level |
| Nasdaq query API / SFTP file | short interest, issue level |
| FINRA `consolidatedShortInterest` | short interest, issue level |
| FINRA `regShoDaily` | short-sale **volume** — excluded |
| ORTEX headline series | **modelled estimate** of short interest, not the reported print |

Only the middle four are the right object. ORTEX is disqualified on content: an intraday model output
is not "actual short interest", and its restatement behaviour is undocumented.

## T2 — Release date recoverable?

**NYSE (paid): YES, directly.** The NYSE Group Short Interest Calendar tabulates
`Settlement Date → NYSE Group Release Date` for every cycle, and the specification fixes the hour:

> "The NYSE Group Short Interest report is provided every two weeks on the day of the NYSE Group
> Release Date at 2:00pm ET."

Example rows (2026 schedule): settlement 15-Jan → release 27-Jan; 30-Jan → 10-Feb; 31-Mar → 10-Apr;
31-Dec → 12-Jan. The gap runs roughly 8–12 calendar days. The spec's revision history records calendars
added for 2016, 2017, 2018 and 2019, so historical release dates are recoverable, not inferred.

**NYSE (free aggregate): YES, incidentally.** The filename carries the publication date
(`..._20150811.xls`) while the sheet carries settlement date `07/31/2015`. Correct structure, no issuers.

**Nasdaq: PARTIALLY.** NasdaqTrader states data is "released after 4:00 p.m, ET, on the dissemination
date", but the *Report Overview & Publication Schedule* link **404s**, so the historical
settlement→dissemination mapping is not currently retrievable from Nasdaq.

**FINRA: YES, by rule, NOT by field.** The API carries `settlementDate` and no publication field. FINRA
states that compiled data is "provided for publication on the **7th business day** after the reporting
settlement date", and publishes settlement-to-publication deadline tables. That is a deterministic rule
plus an official calendar, so it satisfies the escape clause — **provided** the historical tables for
the target years are obtained and archived, not assumed from the current-year rule.

**Risk to carry forward:** a 7-business-day rule applied to the wrong holiday calendar silently
back-dates entry by a day or two. Any Phase 10B must use the archived per-year tables and assert that
every reconstructed release date is ≥ settlement + 7 business days.

## T3 — Do we get a full cross-section?

| source | cross-section |
| --- | --- |
| FINRA API | **yes** — 15,495 issues on 2017-12-29 (`record-total` header), venue-consolidated |
| NYSE paid file | yes, but **NYSE / American / Arca only** — no Nasdaq-listed issuers |
| Nasdaq paid SFTP | yes, Nasdaq-listed |
| Nasdaq public API | **no** — one symbol per call, 24 rows |
| NYSE free FTP | **no** — four aggregate rows per file |

A single-vendor US panel does not exist at the exchange level: NYSE and Nasdaq each sell their own
listings. Only FINRA consolidates — and only from 2017-12-29.

## T4 — Survivorship

**FINRA: PASS.** Historical files are snapshots, so issuers that later delisted are present. Verified
by symbol query on 2017-12-29:

| symbol | issuer | venue | later fate |
| --- | --- | --- | --- |
| `TWTR` | Twitter, Inc. | NYSE | delisted 2022 |
| `CELG` | Celgene Corporation | NNM | acquired 2019 |
| `RTN` | Raytheon Co | NYSE | merged 2020 |

All three return a populated row. This is the important distinction the brief asked for: the historical
**files** preserve dead tickers even where the current lookup page does not.

**Nasdaq public API: FAIL.** `TWTR` and `BSC` return `status 400`, no table. A panel built from it would
be conditioned on 2026 survival.

**NYSE paid file: expected PASS** (semi-monthly snapshots, and `CUSIP` is carried, which survives ticker
reuse — a defect this repository has already measured in its EODHD panel). Unverified, because the only
public samples are holdout-dated and were not opened.

## T5 — History depth against the requirement

Ideal 2004-2017; minimum useful 2010-2017.

| source | machine-readable history | verdict |
| --- | --- | --- |
| NYSE paid issue-level | **Jan 1988 →** (per product page) | meets the ideal, if licensable |
| Nasdaq paid SFTP | month-end available from **Sept 2007** | meets the minimum, if licensable |
| FINRA free API | **2017-12-29 →** | **fails** — one development-window date |
| NYSE free FTP (aggregate) | 2015-08 → | fails on both depth and content |
| Nasdaq public API | rolling 12 months | fails |
| ORTEX | est. 2016/2017 → , modelled | fails |

## T6 — Immutability and revisions

Not established for any source, and there is a specific reason to care here: short interest **is
revised**. Both the NYSE spec (`Revision_Indicator`, "R = the security's short interest for the previous
reporting period has been revised") and the FINRA schema (`revisionFlag`) carry explicit revision flags,
and the NYSE aggregate file's own column header reads `TOTAL PREVIOUS SHORT INTEREST (Revised)`.

Whether a historical file is rewritten in place when a revision lands, or the revision appears only in
the next cycle's `previous` column, is **undetermined**. It is the difference between a genuine
point-in-time archive and a restated one. Any Phase 10B must test it by pulling the same settlement date
twice, weeks apart, and diffing — the same immutability test specified for Zacks in Phase 9A (T5) and
for the same reason.

There is a second, related hazard: `Split_Indicator` / `stockSplitFlag`. Short-interest quantities are
share counts, so a split between two cycles changes the level mechanically. A change-in-short-interest
signal that ignores the split flag will read a 2-for-1 split as a 100% increase in bearish positioning.

## Summary

| test | FINRA free | NYSE paid | Nasdaq paid | Nasdaq public | NYSE free |
| --- | --- | --- | --- | --- | --- |
| true short interest | PASS | PASS | PASS | PASS | PASS (aggregate) |
| release date recoverable | PASS (by rule + calendar) | **PASS (by calendar)** | PARTIAL (link dead) | PARTIAL | PASS (filename) |
| full cross-section | PASS | PASS (NYSE only) | PASS (Nasdaq only) | FAIL | FAIL |
| delisted preserved | **PASS (verified)** | expected PASS | unknown | **FAIL** | n/a |
| history ≥ 2010-2017 | **FAIL (2017-12-29)** | PASS (1988) | PASS (2007) | FAIL | FAIL |
| price | free | not public | not public | free | free |
| immutability | **untested** | untested | untested | n/a | untested |

Every row that passes on history fails on price disclosure, and the row that passes on price fails on
history. That is the whole finding.
