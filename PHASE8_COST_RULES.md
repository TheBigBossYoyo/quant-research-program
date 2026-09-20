# PHASE8_COST_RULES - execution and cost cases (frozen 2026-09-12 before any event return was computed)

Basis: PHASE6_COST_MODEL.md (Trading 212 facts verified 2026-09-09). Costs are applied per side to traded notional at every entry and exit. Liquidity rank = the Tier 2 lagged 63-day median dollar-volume rank at the last month-end before the trade.

| Case | Description | Ranks 1-500 (buy / sell) | Ranks 501-1000 (buy / sell) | Role |
| --- | --- | --- | --- | --- |
| MANUAL_USD (primary) | orders placed by hand from a USD balance funded once (FX 15 bps on funding, not per trade); half-spread plus slippage | 5 / 5.3 bps | 10 / 10.3 bps | gate case |
| AUTOMATED | Trading 212 API in the primary currency: 15 bps FX each way plus 5 bps half-spread | 20 / 20.3 bps | 25 / 25.3 bps | must remain positive (G7) |
| STRESS | wider spreads, small/mid-cap slippage, FX | 30 / 31 bps | 45 / 46 bps | reported |

Why the primary case is MANUAL_USD: the strategy trades a handful of times a month at most; a human can place those orders from a USD sub-balance in the app (documented as FX-free per trade). The AUTOMATED case is the API path and is the stress on the same architecture. A zero-cost case is not computed.

Execution price: the open of the entry/exit day (adjusted open = open x adjusted_close / close). Integrity rule I5 (split-adjusted substitution) applies. Delisting inside the holding period: Phase 6 rule (last vendor price; Shumway haircut on distress proxies; sensitivities all100 and all30 reported).

Portfolio accounting (primary): 20 equal slots; a qualifying event opens one position sized at current equity / 20 at the entry open; if all slots are occupied the event is skipped and counted; a slot frees at the exit open; cash earns 0. Sensitivities: 10 and 40 slots. Turnover = traded notional / equity, one-way, annualised. Small-capital simulations at EUR 500 and EUR 1,000 (ECB 1.1652 USD/EUR): position = capital / 20; Trading 212 minimum order value EUR 1 (orders below are skipped and counted); fractional shares assumed available (UNVERIFIED per instrument); annual cost in EUR reported.
