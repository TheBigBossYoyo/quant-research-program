# E044_20260909T092223 - FIRST REPLICATION PASS (SUPERSEDED, RETAINED)

Status: SUPERSEDED for a data-integrity reason, not for a strategy reason. Nothing in this folder has been modified or deleted; this note is the only addition (2026-09-09).

## Why it is superseded

The E043 data-integrity audit that gated this run disclosed 120 missing hourly observations in each of four monthly kline histories: SOLUSDT, XRPUSDT, FTMUSDT and LTCUSDT, on 2022-02-26, 2022-02-27, 2022-02-28, 2022-04-01 and 2022-04-02 (thirty incomplete 4h bars per asset). The frozen engine treated those bars as incomplete (prior intent retained, no signal update, marks carried), which is causally safe but is not the best available record: Binance publishes official daily archives for exactly those days. Those twenty daily archives were downloaded and checksum-verified (data/metadata/phase4_daily_gap_supplement_acquisition.json) after this run finished.

The supplemented rerun uses the identical frozen configuration (config SHA256 aeb65b74..., FROZEN_E040_HASH 9928aa46...), identical universe hash, identical signal, sizing, exit, cost, funding and execution rules. The only change is that the four affected inputs contain the official rows for those five days. Monthly mark-price archives were already complete for those days, so no mark-price supplement was required.

## What this first pass showed (stress cost case, equal E040, 2022-2024)

Positive net: SOL, DOT, DOGE, ADA, AVAX, AXS, MATIC, FTM. Negative net: XRP, BNB, LTC, LINK. These observations are part of the research history and are preserved here in full (metrics.csv, daily_panel.csv, per-asset paths and trades). No universe change, parameter change, weighting change or strategy change was made in response to them.

## Rule

Do not cite these numbers as the Phase 4 result. The Phase 4 result is the supplemented rerun named in reports/PHASE4_ACTIVE_REPLICATION.txt and PHASE4_CONCLUSION.md; the first-pass versus supplemented comparison is reported in PHASE4_DATA_SUPPLEMENTATION_AUDIT.md.

## Mechanism of the difference (added after diagnosis)

With the gap bars absent, the full-window SMAs of the trend ensemble were NaN for up to 250 bars after each gap; all seven votes were NaN for 238 four-hour bars per affected asset, which the engine treated as a flat target. The breakout component was unaffected. See PHASE4_DATA_SUPPLEMENTATION_AUDIT.md.
