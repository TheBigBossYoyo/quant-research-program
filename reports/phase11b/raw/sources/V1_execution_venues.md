# Phase 11B Stage 0 — Execution Venue & Cost Audit (V1)

**Sub-question:** Is an eventual low-turnover (weekly or monthly), unlevered, long-only spot BTC/ETH strategy with EUR 500–1,000 capital executable at reasonable cost for a European retail investor holding a Trading 212 Invest account?

**Scope note:** This is not a backtest. No price, return, or OHLCV series were downloaded, read, or recorded at any point in this audit. Only fee schedules, minimum order sizes, product lists, TERs, and regulatory-status facts were collected. This document does not recommend any venue; it documents costs and constraints only. Not financial advice.

Today's date: 2026-09-26. All facts below are timestamped with retrieval date; several figures (crypto exchange fee tiers, ETP fee waivers) are known to change frequently and should be re-verified before any real decision.

Raw page snapshots (where the source was reachable without a bot-detection wall) are saved under `reports/phase11b/raw/sources/V1_snapshots/`. Where a primary page was bot-protected, an Internet Archive capture or a corroborating secondary source was used instead, as noted.

---

## 1. Headline finding (read this first)

**Binance does not currently serve EU/EEA retail residents for new spot business.** Binance failed to secure a MiCA (Markets in Crypto-Assets) licence before the 1 July 2026 end of the EU transitional period. Per Binance's own blog post (16 June 2026) and multiple independent reports (Coindesk, Euronews, 26 June 2026), Binance halted new spot orders, deposits, sign-ups, and Earn/staking products for EU/EEA users from 1 July 2026; withdrawals remained open. As of the most recent reporting found (early-to-mid September 2026), Binance had withdrawn a Greek MiCA application and was pursuing authorisation via France's AMF, with no confirmation of a granted licence. **This means the "previous phases used Binance public data and assumed Binance spot 0.10% maker/taker" assumption is not currently executable for an EU/EEA resident** — Binance's 0.10%/0.10% fee is real (VERIFIED_DOC) but the venue itself is presently closed to new EU/EEA retail business. This is a material, current-facts change relative to any prior phase assumption and should be treated as a standing blocker for any Binance-routed candidate until credibly resolved.

By contrast, **Kraken, Coinbase, Bitstamp, and Bitvavo all hold MiCA CASP authorisation** (Kraken: Central Bank of Ireland, 25 Jun 2025; Coinbase: CSSF Luxembourg, 20 Jun 2025; Bitstamp: CSSF Luxembourg, 16 May 2025; Bitvavo: AFM Netherlands, 26 Jun 2025), passporting across the EEA, and are therefore live options for an EU retail resident today. (A UK resident is outside MiCA/EEA scope and subject to FCA rules instead — see §3.)

---

## 2. Fact tables — crypto spot exchanges

### 2.1 Binance

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| Regular (VIP0) spot maker/taker fee | 0.100% / 0.100% | VERIFIED_DOC | https://www.binance.com/en/fee/schedule | 2026-09-26 |
| BNB fee-discount rate | 25% off (→0.075%/0.075%) | VERIFIED_DOC | https://www.binance.com/en/fee/schedule | 2026-09-26 |
| Minimum notional filter (typical) | 5 USDT-equivalent (`MIN_NOTIONAL`/`NOTIONAL` filter; varies per symbol, must be checked via `exchangeInfo`) | VERIFIED_DOC | https://github.com/binance/binance-spot-api-docs/blob/master/filters.md | 2026-09-26 |
| EUR SEPA deposit fee | Historically ~1 EUR flat / instant SEPA; "zero processing fee" promos also seen; varies by promo | SECONDARY | https://www.binance.com/en/support/faq/detail/9bc72093183046b394a7a738abc21e7b | 2026-09-26 |
| **EU/EEA MiCA licence status** | **Not granted.** Withdrew Greek (HCMC) application 24 Jun 2026, 6 days before the deadline; new spot orders/deposits/sign-ups for EU/EEA users suspended from 1 Jul 2026; withdrawals remain open; now pursuing licence via France's AMF; no grant confirmed as of the most recent reports found (Sept 2026) | VERIFIED_DOC (Binance's own blog) + SECONDARY (Coindesk, Euronews) | https://www.binance.com/en/blog/regulation/5369321191341949883 ; https://www.coindesk.com/policy/2026/06/26/binance-tells-eu-users-it-will-no-longer-provide-services-after-failing-to-secure-mica-license | 2026-09-26 |

Direct machine fetch of `binance.com/en/fee/schedule` for the archival snapshot returned HTTP 202 with an empty body (bot/JS-challenge behaviour); the fee figures above were confirmed via an independent fetch pass that successfully rendered the page content. No usable raw snapshot could be archived for this page; the blog MiCA-status page snapshot did archive successfully (also 202/empty on raw `requests` fetch — see `V1_snapshots/_index.md`); figures were cross-confirmed by rendered fetch and by secondary reporting.

### 2.2 Kraken (Kraken Pro)

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| Lowest tier (<$10k 30-day volume, or equivalent Assets-on-Platform) spot maker/taker fee | 0.40% / 0.80% | VERIFIED_DOC | https://www.kraken.com/features/fee-schedule | 2026-09-26 |
| Fee tier basis (post 9 Jul 2026 restructure) | Best-of: 30-day spot volume, futures volume, or assets-on-platform (AoP) | VERIFIED_DOC | https://www.kraken.com/features/fee-schedule ; https://blog.kraken.com/product/pro/new-kraken-pro-fee-tiers | 2026-09-26 |
| EUR SEPA deposit fee | Free | VERIFIED_DOC | https://support.kraken.com/articles/360000381846-cash-deposit-options-fees-minimums-and-processing-times- | 2026-09-26 |
| EUR SEPA withdrawal fee | 1 EUR (standard SEPA), minimum withdrawal 2 EUR, up to 5 banking days | VERIFIED_DOC | https://support.kraken.com/articles/360000423043-cash-withdrawal-options-fees-minimums-and-processing-times- | 2026-09-26 |
| Minimum order size (Trade form, EUR pairs) | 5 EUR | VERIFIED_DOC | https://support.kraken.com/hc/en-us/articles/205893708-What-is-the-minimum-order-size | 2026-09-26 |
| EU MiCA licence | Payward Europe Solutions Ltd, authorised by Central Bank of Ireland, 25 Jun 2025; EU-wide passport | VERIFIED_DOC (ESMA CASP register cited) | https://www.kraken.com/europe-switch | 2026-09-26 |

Note: earlier-vintage secondary sources (pre-restructure) cited a 0.25%/0.40% starter tier; the fee schedule was restructured on 9 Jul 2026 to the cross-platform (volume-or-AoP) model shown above, which is what the official page currently shows.

### 2.3 Coinbase Advanced (Advanced Trade)

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| Entry-tier spot maker/taker fee, EU/UK | 0.25% / 0.50% | SECONDARY (multiple independent trade-press pickups of a 16 Sep 2026 Coinbase announcement; official blog post returned HTTP 403 to automated fetch) | https://www.coinbase.com/blog/were-lowering-fees-for-many-active-traders-on-coinbase-advanced (blocked); corroborated by https://www.securities.io/coinbase-lowers-advanced-trading-fees-with-tiers-starting-at-10-000/ and https://cryptodaily.co.uk/2026/09/coinbase-advanced-fees-usdc-vip-tiers | 2026-09-26 |
| Entry-tier spot maker/taker fee, US (for reference/contrast) | 0.50% / 0.90% | SECONDARY | same as above | 2026-09-26 |
| Qualifying-volume threshold for next tier | Lowered from $25,000 to $10,000 (30-day, or eligible derivatives volume, or USDC balance) | SECONDARY | same as above | 2026-09-26 |
| EUR SEPA deposit fee | Free (1–3 business days) | VERIFIED_DOC | https://help.coinbase.com/en/exchange/funding/depositing-with-sepa-transfers | 2026-09-26 |
| Minimum order size | Asset-dependent per official "Product Specifications"; no single flat EUR figure published; commonly sub-EUR-1 notional minimums for BTC/ETH pairs | UNVERIFIED (exact figure not located; official page directs to per-asset spec sheet) | https://help.coinbase.com/en/international-exchange/order-management/what-is-the-minimum-trade-size | 2026-09-26 |
| EU MiCA licence | Coinbase Luxembourg S.A., CASP authorisation from CSSF, 20 Jun 2025; EU-wide passport | VERIFIED_DOC (CSSF/ESMA register cited) | https://help.coinbase.com/en-gb/coinbase/other-topics/other/mica-cblu | 2026-09-26 |

### 2.4 Bitstamp

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| Lowest tier (<$10,000 30-day volume) spot maker/taker fee | 0.30% / 0.40% (a $0–$1,000 micro-tier at 0%/0% is also cited by some sources) | SECONDARY (official `bitstamp.net/fee-schedule/` is behind an Incapsula bot-challenge; confirmed unreachable both via direct fetch — 202/empty body — and via an Internet Archive capture from 19 Sep 2026, which also returned an empty Incapsula-challenge shell) | https://www.bitstamp.net/fee-schedule/ (bot-protected; archive: http://web.archive.org/web/20260919173518/https://www.bitstamp.net/fee-schedule/) | 2026-09-26 |
| EUR SEPA deposit fee | Free | SECONDARY | multiple review aggregators | 2026-09-26 |
| EUR SEPA withdrawal fee | 3 EUR | SECONDARY | multiple review aggregators | 2026-09-26 |
| Minimum order size | 25 EUR/USD (or 0.001 BTC for BTC-denominated pairs) | SECONDARY | multiple review aggregators | 2026-09-26 |
| EU MiCA licence | Bitstamp Europe S.A., CASP authorisation from CSSF Luxembourg, 16 May 2025; EEA passport | VERIFIED_DOC | https://blog.bitstamp.net/post/bitstamp-secures-casp-license-under-mica/ | 2026-09-26 |

### 2.5 Bitvavo

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| Fee-tier basis | 9-tier maker/taker schedule on trailing 30-day volume | VERIFIED_DOC (Internet Archive capture, since live `bitvavo.com/en/fees` returned HTTP 403 to automated fetch) | archive: http://web.archive.org/web/20251113103313/https://bitvavo.com/en/fees | Archived 2025-11-13; re-confirmed by independent secondary sources on 2026-09-26 |
| Lowest tier (<€100,000 30-day volume) maker/taker fee | 0.15% / 0.25% | VERIFIED_DOC + SECONDARY corroboration | same as above | 2026-09-26 |
| EUR deposit (SEPA / iDEAL) fee | Free, €5 minimum | SECONDARY | multiple review aggregators | 2026-09-26 |
| Minimum transaction amount | €5 (below this, only whole-balance "dust" sells are permitted) | VERIFIED_DOC (official Zendesk help article reached) | https://support.bitvavo.com/hc/en-us/articles/4405175127825-What-is-the-minimum-transaction-amount | 2026-09-26 |
| EU MiCA licence | CASP authorisation from Dutch AFM, 26 Jun 2025; covers custody/administration, trading-platform operation, transfer services; passports across EEA (incl. Norway/Iceland/Liechtenstein) | VERIFIED_DOC | https://bitvavo.com/en/news/bitvavo-obtains-mica-licence | 2026-09-26 |

### 2.6 Stablecoin / cash-holding note (all venues)

Under MiCA, e-money-token (EMT) issuers must hold ≥60% of reserves in EU bank deposits and publish an approved white paper. Circle's **USDC/EURC are MiCA-compliant** and remain available on EU-licensed venues. **Tether (USDT) has not sought MiCA authorisation and has been delisted from MiCA-licensed EU exchanges since 1 July 2026.** Practical implication for holding cash between signals: on a MiCA-licensed venue, "cash" would realistically be held as fiat EUR balance or a MiCA-compliant EUR/USD e-money token (e.g., EURC), not USDT; this carries issuer/reserve counterparty risk distinct from (generally lower than) bank deposit protection, and is unrelated to any exchange-specific custody risk. — SECONDARY, general regulatory synthesis, no single primary URL; see https://www.scorechain.com/blog/eu-stablecoin-regulation-mica and https://bingx.com/en/learn/article/the-impact-of-eu-mica-regulations-on-tether-usdt-and-usd-coin-usdc (retrieved 2026-09-26).

---

## 3. Trading 212

Trading 212 is not a single product; crypto-adjacent access differs by **legal entity** and **account type**. Facts below are from Trading 212's own help-centre (official, Zendesk-hosted, reachable without bot-blocking).

| Fact | Value | Status | URL | Retrieval date |
|---|---|---|---|---|
| (a) Spot crypto | Yes — a distinct **"Trading 212 Crypto"** account exists, offered by **Trading 212 Markets Ltd** (Cyprus, CySEC), which also holds a **MiCA CASP authorisation** for crypto exchange/custody services (CySEC register, effective ~22 Sep 2025; crypto trading on this CASP authorisation went live Oct 2025) | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/30717768082461-What-is-the-Trading-212-Crypto-account | 2026-09-26 |
| Spot crypto — settlement model | Off-chain: "Trades are settled off-chain, so nothing moves to or from personal wallets"; no wallet transfers in/out of the platform; fiat deposit/withdrawal only, in EUR or USD | VERIFIED_DOC | same as above | 2026-09-26 |
| Spot crypto — fees | "No wallets, no commissions"; explicit "Trading commission: Free", "Custody Fee: Free"; cost is a **variable spread built into price** (no percentage disclosed in the fee article itself) | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/30752021087005-What-fees-does-Trading-212-charge-for-crypto-trading | 2026-09-26 |
| Spot crypto — typical spread (external estimate) | ~0.30% on major coins (BTC/ETH) | SECONDARY (not disclosed by T212 itself as a number) | https://www.datawallet.com/crypto/buy-crypto-trading-212 | 2026-09-26 |
| Spot crypto — minimum order | €2 or $2 | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/30752021087005-What-fees-does-Trading-212-charge-for-crypto-trading | 2026-09-26 |
| (b) Crypto ETNs/ETPs | Yes, but **only via Trading 212 UK Ltd** (FCA-regulated, firm ref. 609146) — i.e., only for accounts under that specific (UK) legal entity, not the EU entities | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/30591328588573-How-to-obtain-approval-to-invest-in-Crypto-ETNs | 2026-09-26 |
| Crypto ETN — exchange restriction | "Only ETNs that reference Bitcoin or Ethereum **and are listed on a UK Recognised Investment Exchange** are available to trade" — i.e., **LSE-listed ETNs, not Xetra-listed ones**, at least for the UK-entity offering | VERIFIED_DOC | same as above | 2026-09-26 |
| Crypto ETN — access gate | Requires classification as a "Restricted Investor" (self-certify ≤10% of net assets in high-risk investments) + a knowledge/experience test + a mandatory 24-hour reflection period + final confirmation, consistent with the FCA's Restricted Mass Market Investment regime | VERIFIED_DOC | same as above | 2026-09-26 |
| Crypto ETN — specific product names/tickers | **Not disclosed** in the help-centre articles reached; only the RIE/BTC-or-ETH-reference criterion is stated. (Community/press sources separately mention BlackRock/iShares, 21Shares, WisdomTree, Bitwise as issuers with UK-listed products, but this was not confirmed on an official T212 product list.) | UNVERIFIED (product list) | — | 2026-09-26 |
| Crypto ETN — ISA eligibility change | Until 5 Apr 2026: "buy, hold, and sell Crypto ETNs within your ISA as usual." From 6 Apr 2026: Buy button disabled for ISA — existing holdings may still be held/sold, but **no new ISA purchases**; stated to be an HMRC-driven ISA-eligibility rule, applicable to all UK platforms | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/31007919710365-Crypto-ETNs-in-ISA-accounts | 2026-09-26 |
| Crypto ETN — GIA (non-ISA) status after 6 Apr 2026 | Not addressed in the ISA-specific article; the restriction is described as ISA-eligibility-specific (HMRC), so a General Investment Account is inferred (not confirmed) to be unaffected | UNVERIFIED (inference) | same as above | 2026-09-26 |
| (c) Crypto CFDs | Yes — "CFDs on cryptocurrencies are only available for accounts with Trading 212 Markets Ltd. and Trading 212 EU GmbH", i.e., the Cyprus and Germany CFD entities, not the UK Invest/ISA/Crypto entities described above | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/11717160183197-What-trading-instruments-does-Trading-212-offer | 2026-09-26 |
| FX fee | 0.15% applied "when executing an order with an instrument in a different currency [than the account/cash] balance," using spot rate + 0.15%; applies each time (buy and sell) when instrument currency ≠ balance currency; avoidable via T212's multi-currency account (hold balances natively in up to 13 currencies incl. EUR/GBP/USD/CHF) | VERIFIED_DOC | https://helpcentre.trading212.com/hc/en-us/articles/360018909758-What-is-the-FX-fee-Invest-Stocks-ISA | 2026-09-26 |
| Cash interest on uninvested EUR | Currently ~2.80% standard variable rate (new clients onboarded under Trading 212 EU GmbH/BaFin get a temporary 4.2% promo for 4 months); paid daily, no min/max balance; held either in qualifying money-market funds/banks (if interest enabled) or banks only | SECONDARY (rate levels; the existence/mechanism of interest-on-cash is on T212's own help-centre) | https://helpcentre.trading212.com/hc/en-us/articles/15475153380637-What-is-interest-on-cash ; rate figures per https://www.eupersonalfinance.eu/articles/trading-212-eur-interest | 2026-09-26 |

**Interpretation for the sub-question:** for an EU-resident T212 user, the closest match to "spot BTC/ETH" is the **Trading 212 Crypto** product (Cyprus entity, MiCA CASP-licensed, off-chain settlement, no commission, ~0.30% estimated spread, €2 minimum). The **physical ETP route (iShares/WisdomTree/CoinShares/21Shares)** is not directly tradeable as "Trading 212 Crypto" but as ordinary **stocks/ETPs** — and per the ETN-specific help-centre pages, appears gated to the **UK entity + LSE listings + FCA Restricted-Investor approval flow**, i.e., not obviously available to an EU-entity (non-UK) T212 account at all as an ETN; an EU account would instead reach BTC exposure via T212 Crypto (spot-like) or via crypto CFDs (leveraged/derivative, generally unsuitable for an "unlevered" mandate and carries the CFD retail-loss-rate disclosure T212 itself displays, 77% of retail CFD accounts lose money).

---

## 4. Physical Bitcoin/Ethereum ETP total expense ratios (issuer pages)

| Product | ISIN | TER | Status | URL | Retrieval date |
|---|---|---|---|---|---|
| iShares Bitcoin ETP (IB1T) | XS2940466316 | **0.15%** p.a. (fee partially waived) through 31 Dec 2026; **0.25%** p.a. from 1 Jan 2027 | VERIFIED_DOC | https://www.ishares.com/uk/professionals/en/products/337088 | 2026-09-26 |
| WisdomTree Physical Bitcoin (BTCW) | GB00BJYDH287 | **0.25%** p.a. (cut from 0.35% in Feb 2025; originally cut from 0.95% to 0.35% in Jan 2024) | SECONDARY (official wisdomtree.com page returned HTTP 403 to automated fetch; Internet Archive capture from 2 May 2026 obtained instead) | archive: http://web.archive.org/web/20260502045344/https://www.wisdomtree.com/investments/etfs/crypto/btcw ; corroborated by https://www.justetf.com/en/etf-profile.html?isin=GB00BJYDH287 | 2026-09-26 |
| WisdomTree Physical Ethereum | GB00BJYDH394 | **0.35%** p.a. | SECONDARY | https://www.justetf.com/en/etf-profile.html?isin=GB00BJYDH394 | 2026-09-26 |
| CoinShares Physical Bitcoin (BITC) | GB00BLD4ZL17 | **0.15%** p.a., effective 23 Feb 2026 (permanent reduction; prior steps: 0.95%→0.35% Feb 2024, →0.25% Jan 2025) | VERIFIED_DOC | https://coinshares.com/news/coinshares-reduces-management-fee-on-europe-s-largest-physically-backed-bitcoin-etp-to-0-15-/ | 2026-09-26 |
| 21Shares Bitcoin Core ETP (CBTC) | CH1199067674 | **0.10%** p.a., effective 1 Oct 2025, described as a **12-month fee waiver** (i.e., due to expire around **1 Oct 2026** — days after this audit's retrieval date; underlying fee before the waiver was 0.21%) | VERIFIED_DOC | https://www.21shares.com/en-eu/product/cbtc | 2026-09-26 |

**Time-sensitive flag:** the 21Shares Bitcoin Core waived TER (0.10%) is scheduled to expire around 1 October 2026 — essentially immediately after this audit. If this candidate route were ever pursued for real, the TER must be re-checked at execution time; it could plausibly revert toward its pre-waiver 0.21% level. Likewise iShares IB1T's 0.15% waived rate is locked only through 31 Dec 2026, stepping to 0.25% on 1 Jan 2027.

These TERs are an ongoing drag distinct from any trading/switching cost, and they apply continuously regardless of turnover (i.e., even a buy-and-hold ETP position pays ~0.10–0.35%/year in TER, on top of any brokerage spread/commission and, if the ETP's listing currency differs from the account's base currency, T212's 0.15% FX fee each way).

---

## 5. Cost model for a binary BTC-or-cash strategy

All figures below are **illustrative cost models built entirely from the fee percentages above**, not from any observed price or spread data (none was collected, per the hard rules). Spread/slippage figures are explicitly labelled **ASSUMPTION** — a generic, unverified estimate, not a measurement — because collecting real spread data would require live market/price data, which this audit was barred from doing.

**Assumptions:**
- ASSUMPTION: effective one-way execution slippage (spread cost) of **0.05%** per trade on liquid BTC/EUR or ETH/EUR pairs on Kraken/Coinbase/Bitstamp/Bitvavo, for a EUR 500–1,000 market order. This is a generic placeholder, not measured; real spreads vary by pair, time of day, and venue and could be materially higher for ETH or in stressed conditions.
- "Switch" = one directional trade (enter or exit the BTC/ETH position), consistent with the brief's "52 switches max" (weekly) / "12" (monthly) framing, i.e., worst case is a trade at every single rebalance point (maximum reversal frequency). A real strategy with genuine persistence would very likely switch far less often; these are upper-bound, not expected, costs.
- Taker (market order) fee used throughout, since a small discretionary retail rebalance cannot reliably rely on maker (limit, resting-order) fills.
- No FX fee is added for the pure-crypto-exchange routes because trading is assumed to occur EUR-balance-to-EUR-pair (no currency conversion). For the Trading 212 Crypto route, no separate taker fee exists; the ~0.30% estimated spread (SECONDARY) is used as the full one-way cost.
- For the ETN/ETP route, this table shows only the **annual TER drag** (Section 4), since (i) no live bid/ask spread was collected (hard rule), (ii) T212 charges no separate commission on stocks/ETFs, and (iii) if the ETP's listing currency differs from account currency, add T212's 0.15% FX fee per leg (ASSUMPTION-flagged as "if applicable" — not quantified here because it depends on the specific ISIN/listing currency vs. the user's account currency, which was not established).

### 5.1 One-way cost per switch (%, of notional)

| Venue | Taker fee | + assumed spread | = one-way cost |
|---|---|---|---|
| Kraken (lowest tier) | 0.80% | 0.05% | **0.85%** |
| Coinbase Advanced (EU/UK entry tier) | 0.50% | 0.05% | **0.55%** |
| Bitstamp (lowest tier) | 0.40% | 0.05% | **0.45%** |
| Bitvavo (lowest tier) | 0.25% | 0.05% | **0.30%** |
| Binance (0.10%; **currently blocked for EU/EEA — reference only**) | 0.10% | 0.05% | **0.15%** |
| Trading 212 Crypto (spread-only, no separate commission) | — | ~0.30% (SECONDARY) | **~0.30%** |

### 5.2 Annualized worst-case cost, weekly (52 switches) vs. monthly (12 switches), on notional

| Venue | Weekly (52×) | Monthly (12×) |
|---|---|---|
| Kraken | **44.2%** | **10.2%** |
| Coinbase Advanced (EU) | **28.6%** | **6.6%** |
| Bitstamp | **23.4%** | **5.4%** |
| Bitvavo | **15.6%** | **3.6%** |
| Binance (blocked for EU/EEA) | 7.8% | 1.8% |
| Trading 212 Crypto | **~15.6%** | **~3.6%** |

### 5.3 EUR 500 vs EUR 1,000

The percentage costs in §5.1–5.2 are **notional-independent** (they are pure percentages of trade value), so they apply identically at EUR 500 and EUR 1,000, **except** where a venue's minimum order size or a fixed (non-percentage) fee starts to bind:

- Bitvavo: €5 minimum — non-binding at EUR 500 or 1,000 (a single switch of the full balance is far above the minimum).
- Kraken: €5 minimum (Trade form) — non-binding.
- Bitstamp: €25 minimum — non-binding, but worth noting it is 5% of a EUR 500 balance if ever partial-sized.
- T212 Crypto: €2 minimum — non-binding.
- Fixed EUR withdrawal fees (e.g., Kraken's 1 EUR SEPA withdrawal, Bitstamp's 3 EUR SEPA withdrawal) are **not** part of the per-rebalance switching cost (they apply only if fiat is moved off-exchange), but if the strategy design required periodically pulling cash back to a bank/T212 account, a 1–3 EUR fixed fee is proportionally larger on EUR 500 (0.2–0.6%) than on EUR 1,000 (0.1–0.3%) — a real, if secondary, small-capital penalty.

### 5.4 Interpretation

At worst-case (every-period reversal) turnover, **weekly rebalancing is not cost-viable at retail/lowest-tier fees on any audited venue** — costs of 15–44%/year on notional would overwhelm any plausible crypto BTC/ETH long-only edge documented so far in this research programme. **Monthly rebalancing is far more plausible** (3.6–10.2%/year worst case across venues), and on the cheaper venues (Bitvavo, Trading 212 Crypto) a monthly-turnover strategy with a real, moderate hit rate/edge could plausibly clear costs — but only if the true switching frequency is well below the worst-case 12/year ceiling, and only after real (not assumed) spread and slippage are measured, which is out of scope for this document. These are cost-feasibility bounds, not a claim that any specific strategy survives them; that requires the actual signal's realized turnover and edge, tested separately under the existing chronological validation protocol.

At EUR 500–1,000, **fee-tier structure is a structural, not incidental, headwind**: a user trading only EUR 500–1,000 will not realistically accumulate the 30-day volume (e.g., Kraken $10k+, Coinbase $10k+) needed to reach better-than-entry-tier pricing — they will sit at the worst tier indefinitely, unlike a backtest that might implicitly assume improving fee tiers with scale.

---

## 6. Constraints (non-cost)

- **Cash-holding counterparty/venue risk between signals:** on a MiCA-licensed exchange, EUR fiat balances and MiCA-compliant EMTs (e.g., EURC) are the realistic "cash" leg; USDT is delisted from MiCA venues since 1 Jul 2026 (§2.6). Exchange insolvency/custody risk still exists distinct from bank deposit protection; this was not further quantified (out of scope: this is a qualitative constraint, not a fact requiring price data).
- **Trading 212 cash interest:** ~2.8% standard variable EUR rate is available on uninvested cash held at T212 (SECONDARY for the exact current rate), which is a genuine, if small, benefit of holding the "cash" leg inside T212 rather than idle on a crypto exchange — but T212 does not custody spot crypto positions itself in the same account wrapper as its interest-bearing cash sleeve (Crypto account vs Invest/CFD cash), so combining "cash leg = T212 interest-bearing EUR" with "risk leg = spot BTC on an exchange" would mean moving fiat between T212 and the exchange at each switch, incurring transfer time/fees not modelled here.
- **Tax/reporting complexity** (capital gains treatment of frequent crypto switches, ETN vs spot crypto tax treatment, T212 GIA vs ISA wrapper effects) is explicitly out of scope per the audit brief; flagged only, not analyzed.
- **Binance blocker is a standing fact, not a one-off:** any future candidate design that assumes Binance access for an EU/EEA resident must treat this as `UNVERIFIED`/blocked until a MiCA licence is confirmed granted, not merely applied for.

---

## 7. Source list / snapshot index

A machine-readable index of every URL fetched, HTTP status, and byte count is at `reports/phase11b/raw/sources/V1_snapshots/_index.md`. Individual raw snapshots (where retrievable) are one `.txt` file per source in the same directory, each prefixed with its URL and retrieval timestamp. Bot-protected sources (Binance fee pages, Bitstamp fee-schedule page, Bitvavo live fee page, WisdomTree product page) are noted above with the Internet-Archive or secondary-source fallback actually used, per the audit's hard rules.

---

## 8. Short conclusions

1. **Binance is currently not usable** by an EU/EEA retail resident for this strategy (MiCA licence not secured as of the most recent facts found, Sept 2026); any prior-phase cost assumption built on Binance's 0.10%/0.10% fee needs a live, licensed alternative venue substituted before being treated as executable.
2. **Kraken, Coinbase, Bitstamp, and Bitvavo are MiCA-licensed and open to EU residents today.** Of these, **Bitvavo has the lowest documented lowest-tier taker fee (0.25%)**, giving it the cheapest worst-case annualized cost among the exchange-based routes.
3. **Trading 212 does offer a genuine spot-like BTC/ETH product** ("Trading 212 Crypto," Cyprus-entity, MiCA-licensed, off-chain settlement, no explicit commission, ~0.30% estimated spread, €2 minimum) — this is a real answer to sub-question (a), distinct from T212's CFD and ETN offerings.
4. **T212 crypto ETNs are gated to the UK entity, LSE-listed products only, and require an FCA Restricted-Investor approval flow**; from 6 Apr 2026 new ISA purchases of these ETNs are disallowed (existing holdings unaffected) per an HMRC ISA-eligibility rule. This route looks materially less relevant for an EU-entity T212 account than the Cyprus spot-crypto product.
5. **Physical ETPs (iShares IB1T, WisdomTree BTCW/ETHW, CoinShares BITC, 21Shares CBTC)** carry ongoing TERs of 0.10–0.35% p.a., several under temporary fee waivers that are due to step up within the next 3–15 months (21Shares CBTC waiver ends ~1 Oct 2026; iShares IB1T waiver ends 31 Dec 2026) — this is a fixed annual drag independent of turnover, on top of any brokerage spread and (if currency mismatched) T212's 0.15% FX fee per leg.
6. **Weekly rebalancing looks cost-prohibitive everywhere audited** (15–44%/year worst case); **monthly rebalancing is the only turnover regime with a plausible chance of clearing costs**, and only on the cheaper venues (Bitvavo, Trading 212 Crypto), and only if realized turnover is well under the worst-case ceiling and realized spreads are close to (not materially above) the ASSUMPTION used here. This audit does not establish that any strategy actually clears these costs — that is a separate, still-open empirical question outside this document's scope.
