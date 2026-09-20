# Phase 8B Amendment 4 — price-path data-integrity defect found in the first development run

Written 2026-09-20, **after** the first E062 development run and **before** any corrected run, by the agent, on its own
finding. The classifier is NOT touched by this amendment. No validation or holdout data is involved.

## The defect

The first development run (`reports/E062_20260920T213315`) reported a 2012 excess of **+737%** and a single monthly
return of **+635%** (2012-12). Both come from one position, `SFD_old` (Smithfield Foods), event
`E8B-0000091388-0000091388-12-000037`, entered 2012-09-04 and held to 2013-09-06.

Its adjusted-open series does not fall once and stay down. It **oscillates between two price levels**:

```
2012-11-16   -99.2%        2012-11-19   +13,143.8%
2012-12-11   -99.2%        2012-12-12   +12,538.9%
2012-12-18   -99.2%        2012-12-19   +12,194.4%
2012-12-20   -99.2%        2012-12-24   +12,044.4%
```

i.e. the vendor series alternates between roughly $0.17 and roughly $22 on adjacent sessions. (Smithfield Foods was
acquired at $34/share in September 2013; it did not trade at $0.24.) This is the EODHD delisted-series ticker-reuse /
split-adjustment pathology already documented in `PHASE6_EODHD_COVERAGE_AUDIT.md` ("5-7% ticker-reuse mismatches").

The hold-all portfolio re-equalises every position to 1/N on any session with an entry or an exit. Against an
oscillating series it therefore **buys at the corrupted low and trims at the corrupted high**, repeatedly, harvesting a
spurious return. That is how a position whose quoted price fell 98.6% over the holding period was booked as
`bought = 1.044, sold = 31.419, pnl = +30.37` — about thirty times the whole portfolio's starting equity.

## Why the existing guards did not catch it

Phase 6 already defines the right test (`phase6_stock_universe`: `EXTREME_DAY_UP = 2.0`, `EXTREME_DAY_DOWN = -0.75`,
I3) and Phase 8B does apply universe eligibility — but **eligibility is evaluated only at the signal date before
entry**. `SFD_old` was clean at its August 2012 signal date; the corruption begins in November 2012, inside the
252-session hold. Nothing in the Phase 8B return path re-examines the price path a position is actually traded on.

This is a general engineering gap, not a property of one stock.

## Scale (measured before the fix, on the development panel only)

Scanning the whole traded adjusted-open panel for the oscillation signature (a session with return > +300% adjacent to
a session with return < -75%):

- **1,163 of 19,944 codes (5.83%)** are affected, over **15,483** oscillation sessions.

The 5.8% figure matches the Phase 6 audit's independent estimate of vendor ticker-reuse damage, which is corroborating
evidence that this is the known vendor pathology rather than a new bug in Phase 8B's own code.

## Verdict on the first run

`reports/E062_20260920T213315` is marked **SUPERSEDED — DATA INTEGRITY DEFECT**. It is retained unmodified, as the
protocol requires, and **none of its return numbers are research results**. In particular the +6.09%/yr 2013-2017
excess it reported must not be quoted: an oscillating series anywhere in the book contaminates the equity path and
therefore every window.

## The correction (frozen before the corrected run)

A general screen, reusing the **existing Phase 6 I3 thresholds** rather than any new number chosen for this situation:

> A traded price path is **unclean** on any session where the adjusted-open return exceeds `EXTREME_DAY_UP` (+200%) or
> falls below `EXTREME_DAY_DOWN` (-75%). An event whose holding window `[entry_idx, exit_idx]` contains any unclean
> session for its own code is **excluded from the event list** as a data-integrity failure.

Properties this rule is required to have, and does:

- it is defined on the **price series only** and never looks at the event's return, sign or contribution;
- it uses thresholds already fixed by Phase 6 for a different purpose, so they were not chosen here;
- it excludes the whole event rather than truncating the hold, so no position gets a survivorship-flavoured early exit;
- exclusions are **counted and reported by year**, so the cost in sample size is visible.

Implementation: `research/phase8b_price_integrity.py`, applied in `research/phase8b_pipeline.py` when the event list is
built. **Every permanently frozen file — the classifier, the corpus builder, the display module, the lock, the timing
module, the events module, the portfolio engine and the backtest — stays byte-identical.** The corrected run is
verified against `PHASE8B_PIPELINE_FROZEN.json` before it starts.

## What this does not do

It does not change the classifier, any gate threshold, any cost case, the entry/exit timing, the universe definition
or the hypothesis. It removes filings whose price data is corrupt. If the corrected run still fails its gates, the
branch is rejected; a data repair is not permitted to rescue it, and the direction of the repair (removing a spuriously
profitable position) is against the hypothesis, not for it.
