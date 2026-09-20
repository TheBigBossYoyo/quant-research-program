# PHASE6_SMALL_CAPITAL_FEASIBILITY

Status 2026-09-09: NOT STARTED. Mandate section 58: small-capital execution simulation begins only after a statistically credible long-only candidate exists at stock level. None exists (see PHASE6_CANDIDATES.csv).

Preregistered simulation design (fixed now so it cannot be tuned to a candidate later):
- Capital cases EUR 500, 1,000, 2,500, 5,000 converted at the ECB rate of the simulation date (2026-09-09: 1.1652 USD, 0.85898 GBP per EUR).
- Instrument constraints from the Trading 212 instruments endpoint (minTradeQuantity, currency) read once with a read-only key; until read, fractional quantity step assumed UNVERIFIED and reported as such.
- Minimum order value one currency unit; orders below it are skipped and counted.
- Cost cases from PHASE6_COST_MODEL.md; FX architecture A (automated, 15 bps each way) as base, B (USD balance, 0 bps per trade) as the non-automated comparison.
- Outputs: tracking error vs the unconstrained portfolio, skipped orders, number of positions whose expected monthly edge exceeds their round-trip cost, total cost as percent of capital per year, Sharpe retention.
- No leverage, no shorting, no CFD.
