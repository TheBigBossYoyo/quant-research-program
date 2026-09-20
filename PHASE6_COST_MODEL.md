# PHASE6_COST_MODEL - Trading 212 Invest execution economics for US equities (documented facts retrieved 2026-09-09; preregistered cost cases)

## 1. Verified from official Trading 212 pages (retrieval date 2026-09-09)

| Item | Documented rule | Source |
| --- | --- | --- |
| Commission, custody | "The only fee Trading 212 can charge your Invest, ISAs, and SIPP is the FX Fee"; trading commission free, custody free | helpcentre.trading212.com/hc/en-us/articles/11471996799517 |
| FX fee | 0.15 percent applied as a mark-up on the spot rate on every conversion, on buys and on sells; not applied to dividends | helpcentre.trading212.com/hc/en-us/articles/360018909758 |
| Multi-currency | "only the Invest and SIPP accounts support multi-currency"; supported balances include USD; "Pay no FX fees on your trades by selecting the asset's currency"; manual conversion available; available currencies may differ by country of residence | helpcentre.trading212.com/hc/en-us/articles/11669719976093 |
| Primary currency | "Once you create an account, its base currency cannot be changed" | helpcentre.trading212.com/hc/en-us/articles/360007308078 |
| API scope | Invest and Stocks ISA only; "Orders can be executed only in the primary account currency"; multi-currency accounts lack API support | docs.trading212.com/api/section/general-information/api-limitations |
| API orders | market (50 req/min), limit, stop, stop-limit (1 req/2 s); "not idempotent" in beta (duplicates possible); stop triggers on last traded price; extended hours for market orders | docs.trading212.com/api/orders |
| API instruments | fields ticker, isin, currencyCode, minTradeQuantity, maxOpenQuantity, workingScheduleId, type, shortName, addedOn; 1 req/50 s; sell example "-10.5" implies decimal quantities | docs.trading212.com/api/instruments-metadata |
| Fractional shares | "Most instruments available on the Invest accounts and ISAs can be traded fractionally"; "Fractional Market, Limit, Stop and Stop Limit orders are all supported"; pending fractional orders by number of shares only; minimum order value one unit of currency (learn page 403 on retrieval; community/help snippets: UNVERIFIED as an official per-instrument rule) | helpcentre.trading212.com/hc/en-us/articles/9511997937437 |
| Short selling, leverage | "Short selling ... is available only with a CFD account"; leverage "available only in CFD accounts" | helpcentre.trading212.com/hc/en-us/articles/360009036118 |
| US regulatory sell charges | SEC transaction fee and FINRA trading activity fee on sells (help page quotes "$0.00206 per dollar" and "$0.000195 x quantity sold" as extracted; the SEC rate wording is inconsistent with the published SEC fee schedule and is treated as UNVERIFIED in magnitude) | helpcentre.trading212.com/hc/en-us/articles/11471996799517 |
| Historical market data | the public API has no candle/quote-history endpoint in the documented inventory | docs.trading212.com (inventory) |

Not documented and therefore modelled, not asserted: bid/ask spreads, slippage, fill quality of fractional market orders, US price-improvement, minTradeQuantity values per instrument (to be read from the instruments endpoint in a later phase with a read-only key), whether this user's account has the multi-currency feature enabled, and whether a USD sub-balance can be used from the API (documentation says no).

## 2. FX architectures (mandate section 35)

| Architecture | Mechanism | Cost per trade | Automation |
| --- | --- | --- | --- |
| A. Trade-by-trade conversion | GBP primary account, USD stock, conversion on each buy and each sell | 15 bps each way = 30 bps round trip in addition to spread/slippage | Available through the API today (primary currency only) |
| B. USD sub-balance | fund a USD balance once, trade USD stocks from it; FX only on deposits/withdrawals | 0 bps per trade; 15 bps once on funding | App/web only; the API cannot use multi-currency balances (documented) |
| C. API restriction | the API executes in the primary currency only | forces architecture A for any automated workflow | - |

Consequence: an automated monthly strategy with one-way turnover T per month pays 2 x 0.15 percent x T of FX per month under A. At T = 30 percent per month (typical for top-N momentum) that is 0.09 percent per month, about 1.1 percent per year, before spreads. Weekly rebalancing at similar signal decay would multiply this. This is the main reason the deployable track prioritises monthly schedules and low-turnover signals, and why architecture B (manual execution from a USD balance following the system's orders) is recorded as the cheaper but non-automated path.

## 3. Preregistered cost cases for stock-level backtests (per side, applied to traded notional)

| Case | Half-spread + slippage (top-1000 liquidity, lagged dollar-volume rank 1-1000) | FX | US sell fees | Total buy / sell |
| --- | --- | --- | --- | --- |
| Optimistic | 3 bps | 0 (architecture B) | 0.3 bps on sells | 3 / 3.3 bps |
| Base (automated, architecture A) | 5 bps | 15 bps | 0.3 bps on sells | 20 / 20.3 bps |
| Stress | 15 bps, doubled for ranks 501-1000 (30 bps) | 15 bps | 1 bp on sells | 30-45 / 31-46 bps |
| Ranks 1001-1500 (if a sensitivity universe is used) | base 10 bps, stress 40 bps | as above | as above | - |

Spread figures are assumptions from the documented absence of data, to be replaced by measured spreads once an instrument snapshot with quotes exists; until then every stock-level result reports all three cases and no promotion may rest on the optimistic case. Market impact: orders are capped at 0.5 percent of the lagged 21-day average dollar volume per name; at EUR 500-5,000 this never binds, but the cap is kept so that capacity estimates use the same code path.

## 4. Taxes and levies

US-listed instruments carry no stamp duty or FTT; only the regulatory sell fees above. UK-listed instruments would incur 0.5 percent stamp duty and are therefore excluded from Phase 6 unless a UK-specific mechanism is preregistered. Personal taxation is out of scope.

## 5. Small-capital realism (mandate section 36) - to be simulated only after a candidate exists

Capital cases EUR 500 / 1,000 / 2,500 / 5,000 converted at the ECB rate of the simulation date; fractional quantities rounded to the instrument's minTradeQuantity (UNVERIFIED until read from the API); minimum order value one currency unit; positions whose expected monthly edge in currency is below the round-trip cost are counted as "uneconomic" and reported; tracking error against the unconstrained portfolio; skipped orders; number of meaningful positions.
