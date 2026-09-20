# Venue feasibility — retrieved 2026-09-08 UTC

Documentation is distinct from measurements and account entitlements. The local timezone does not identify residency, regulatory entity, account currency or product eligibility. No authenticated endpoints or orders were used. Monetary research results in USDT are not EUR returns.

| Route | Verified evidence | Research decision / unresolved constraints |
|---|---|---|
| Binance cash spot | Public REST symbol rules and quotes obtained; monthly OHLCV archives with SHA256 checksums accessible | First-stage fixed BTCUSDT/ETHUSDT long/cash screen; no leverage, borrow, funding or short positions |
| Binance margin / derivatives | Separate product APIs and funding specifications exist; symbol spot margin flag is not account authorization | Deferred: eligibility, account fees, borrow inventory/rates, historical funding, maintenance-margin tiers and liquidation rules UNVERIFIED for this user |
| Trading 212 Invest / Stocks ISA | Public API beta documents stock/ETF instrument metadata, orders, account history and demo/live environments | Slower equity/ETF research possible in principle; candle/quote-history feed not established by API inventory. Need corporate-action-safe data and account instrument mapping |
| Trading 212 CFD | Public API scope is Invest/ISA | Reject automated CFD route under the documented public API; CFD app availability is not CFD API capability |

## Binance documented rules

Regular spot tier displays maker/taker 0.100%/0.100%; BNB discount exists but is not assumed. Exact account/symbol commissions and temporary promotions need later authenticated read-only verification. Screening uses current standard pricing over all historical dates, not a claim about historical charged fees. [Official fee table](https://www.binance.com/en/fee/trading).

REST docs direct public market data to data-api.binance.vision and require backoff for 429/418. Rules come from exchangeInfo, not hardcoded documentation examples. [REST documentation](https://developers.binance.com/en/docs/products/spot/rest-api). PRICE_FILTER, LOT_SIZE, MARKET_LOT_SIZE and NOTIONAL must be evaluated together; zero step in one filter does not disable other filters. [Official filter specification](https://github.com/binance/binance-spot-api-docs/blob/master/filters.md).

BTCUSDT live snapshot at 09:24 UTC: TRADING, spot allowed, price tick 0.01 USDT, quantity step/minimum 0.00001 BTC, minimum notional 5 USDT with minimum applied to market orders. Market quantity maximum 131.05893287 BTC. Snapshot rate limits: request weight 6000/minute, orders 100/10 seconds and 200000/day, raw requests 300000/5 minutes. These values expire and must be refreshed before any future order. Raw full filters and order-type inventory are saved in data/metadata/*exchangeInfo*.json. Spot supports market/limit/maker-only and listed contingent orders in that snapshot; none were submitted.

BTC top-of-book snapshot bid 78450.19 / ask 78450.20 USDT: approximately 0.00127 bps full spread. This is one present-time observation, not historical or stressed spread evidence; it does not calibrate the backtest. Historical depth, queue position and latency are absent. Extra 2 bps base or 4 bps stressed friction per side are explicitly assumptions, not measured slippage. Screening must not support promotion from these assumptions alone.

Public archive supplies daily/monthly files, OHLCV plus taker volume and checksums. Spot timestamp units change to microseconds from 2025-01-01; parser handles and tests date boundaries. Raw archives and acquisition manifest are retained with local SHA256. [Official public-data repository](https://github.com/binance/binance-public-data). Bars do not establish executable bid/ask or second-level opportunities.

## Trading 212 documented rules

API applies to Invest/Stocks ISA and uses the primary account currency; multi-currency API execution is unsupported. Limits are per account. [Scope](https://docs.trading212.com/api/section/general-information/api-limitations). Order reference lists market, limit, stop and stop-limit; help centre explicitly confirms live market orders. Treat live support for other types as unverified until reconciled. Market endpoint documents 50 requests/minute and is not idempotent: retrying may duplicate orders. [Order reference](https://docs.trading212.com/api/orders), [API key help](https://helpcentre.trading212.com/hc/en-us/articles/14584770928157-Trading-212-API-key).

Published Invest fees are zero trading commission/custody and 0.15% FX; taxes/levies depend on exchange/instrument. These are not equivalent to zero trading costs. The fee page's SEC-fee wording is ambiguous and will not be hardcoded; selected-equity tax/regulatory charges require separate verification. [Fee page](https://helpcentre.trading212.com/hc/en-us/articles/11471996799517-What-are-the-fees-in-the-Invest-ISAs-and-SIPP). Foreign-currency trades incur conversion on order value; repeated cross-currency API trades therefore face a material hurdle. [FX explanation](https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA).

Published fractional-investing page describes a one-currency-unit minimum, but instrument-specific quantity and price precision, fractional eligibility, exchange sessions/holidays and account execution constraints remain UNVERIFIED. [Fractional investing](https://www.trading212.com/learn/investing-101/fractional-investing). This is not a universal per-instrument executable minimum. Cash-investing route modeled long-only and unlevered; no financing/short capability assumed. Broker spread distributions, fills and slippage remain unmeasured. No trading212 credentials are required at this research stage.

## Capital and liquidity policy

EUR500 is experimental capital only. Snapshot Binance minimum 5 USDT is compatible with a single cash position in notional terms; that does not prove efficient capital or profitability. EUR/USDT conversion, transfer costs and residency/product access are unresolved. Reject seconds-level research relying on institutional latency; compare 5-minute through daily horizons empirically. For eventual sizing, each order must satisfy all filters, have a fee reserve, and remain below 0.1% of conservative observed interval quote volume and a conservative fraction of available book depth. Historical bars cannot certify the latter. Model both legs, dust, conversion and account-level risks before any promotion. No paid services needed so far (recurring research cost EUR0).
