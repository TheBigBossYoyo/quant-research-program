# PHASE4_PREVALIDATION_DECISION

# **DO_NOT_OPEN_2025**

Classification: **CROSS_ASSET_WEAK_SIGNAL**

Basis: the preregistered gate in phase4_e040_frozen_config.yaml (section `gate`, SHA256 aeb65b7447f0e5d923d254688d2e319695792557ec577fe69c64c5916bba0b89, frozen 2026-09-09 before any replication performance), applied exactly as written to the supplemented replication E044_20260909T135755 and its analysis E045_20260909T140237 (reports/E045_20260909T140237/results.json). No threshold was added, loosened or tightened. The stress cost case (9.05 bps per side plus actual funding) is the preregistered primary case; equal 50/50 component weighting and equal asset weighting are the preregistered primary portfolio.

## Gate conditions, one by one

| # | Condition (frozen) | Threshold | Observed | Result |
| --- | --- | --- | --- | --- |
| 1 | Assets evaluated | >= 8 | 12 (all preregistered names, including MATIC to its mandated exit and the two losing majors) | PASS |
| 2 | Positive net fraction (total net return > 0, stress case, equal E040) | >= 2/3 | 8 of 12 = 0.6667 (SOL, DOT, DOGE, ADA, AVAX, AXS, MATIC, FTM positive; XRP, BNB, LTC, LINK negative) | PASS at the boundary: one more losing asset fails it |
| 3 | Positive factor-alpha fraction (daily regression intercept > 0; underlying, BTC, replication market, lagged BTC volatility, lagged BTC trend; HAC 14) | >= 2/3 | 9 of 12 = 0.75 (negative: XRP, DOT, ADA) | PASS |
| 4 | Median net Sharpe | >= 0.3 | 0.702 | PASS |
| 5 | Median factor alpha | > 0 | 0.536 per year (conditional intercept, see red-team item 4) | PASS |
| 6 | Common-time-block bootstrap: 95% lower bound of the cross-asset median factor alpha, all preregistered block lengths | > 0 | 14-day [-0.261, 1.365]; 30-day [-0.249, 1.389]; 60-day [-0.241, 1.306]; every lower bound below zero | **FAIL** |
| 7 | Primary portfolio maximum drawdown | > -40% | -24.1% (equal assets, equal components, net of allocation-transfer cost estimates) | PASS |
| 8 | Top-5 trade share of positive portfolio P&L (conservative denominator) | < 50% | 13.2% (2,633 component episodes; top trade 3.3%, top 10 20.2%) | PASS |
| 9 | Top calendar-year share of positive portfolio P&L | < 60% | 56.4% (2024) | PASS, close to the limit |
| 10 | Asset-conservative cost case (14 bps per side plus funding) portfolio net return | > 0 | +62.2% total (CAGR 17.5%, Sharpe 0.740, DD -27.2%) | PASS |
| 11 | Remove best calendar year, portfolio net return | > 0 | +34.7% over 2022-2023 (Sharpe 0.694) | PASS |
| 12 | No unresolved accounting or data defects | required | Trade-contribution reconciliation error 3e-11 USDT; all fourteen histories complete after official-archive supplementation; frozen hashes verified before every run; first pass retained as superseded | PASS |

Eleven of twelve conditions pass. Condition 6 fails: with dates resampled jointly across all twelve names (so that the common crypto regime is not treated as twelve independent samples), the median factor alpha's 95% interval spans roughly -25% to +135% per year. The evidence is directionally consistent but statistically unresolved on a three-year, single-regime sample.

## Classification under the frozen rules

- REPLICATION_FAILURE requires median net effect <= 0 and positive fraction <= 0.5: not met (median total net return +89%, positive fraction 0.667).
- MIXED_REPLICATION requires positive fraction < 2/3: not met (exactly 2/3).
- VALIDATION_ELIGIBLE requires every gate: not met (condition 6).
- CROSS_ASSET_RESEARCH_PROMISING requires the directional, factor, common-block and cost criteria to pass with only concentration/risk failing: not met, because the failing condition is the common-block uncertainty criterion itself.
- Therefore: **CROSS_ASSET_WEAK_SIGNAL** (positive majority, gate not passed).

## Consequences

- 2025 validation data remain LOCKED. No file, query or summary of 2025 has been read; the loader firewall (guard_dates/guard_path, tests test_2025_firewall and test_protected_access_fails_before_open) is unchanged.
- 2026 remains UNTOUCHED: never downloaded, never queried.
- E040 is not modified, retuned, re-weighted or pruned in response to this result. No losing asset is excluded. Any future variant must be registered separately and cannot use this replication as its development sample without counting the multiplicity.
- No PRE_2025_FINAL_FREEZE.md is created, because the gate did not pass.
- Cumulative economic hypotheses remain 385 (E044 counted once; the supplemented rerun is a data-integrity correction of the same hypothesis, and the seven cost/delay/funding cases are diagnostics).

## Sensitivity disclosed without changing the gate

- Under base costs (7.05 bps) or the secondary inverse-volatility weighting the positive fraction is unchanged (8 of 12); the median Sharpe ranges 0.58 (adverse funding) to 0.74 (base) across the seven cost cases.
- The underlying-only regression (the interpretable, unconditional intercept) gives a median alpha of 28.5% per year with 9 of 12 positive; its per-asset 95% intervals also include zero for every name.
- Condition 2 passes only by equality and condition 9 passes by 3.6 points; the pass set is fragile in both directions and this is reported, not acted on.
