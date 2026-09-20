# PHASE6_DATA_PURCHASE_RECOMMENDATION (2026-09-09) — requires explicit user action; nothing has been purchased

## Exact product

**Norgate Data — US Stock Market package, Platinum level, 12-month term.**
Order page: https://norgatedata.com/subscribe/subscribe.php (package list: https://norgatedata.com/stockmarketpackages.php).

## Current price (vendor page, retrieved 2026-09-09)

| Term | USD | EUR at ECB 1.1652 | Monthly equivalent |
| --- | ---: | ---: | ---: |
| 12 months (recommended) | 630.00 | 540.69 | EUR 45.06 |
| 6 months (fallback if the up-front amount is the constraint) | 346.50 | 297.38 | EUR 49.56 |

Both are inside the EUR 50/month ceiling on a monthly-equivalent basis; the vendor bills the whole term up front and offers no monthly term. Payment by card, PayPal or transfer; no automatic renewal ("We do not perform any automatic renewals. It must be initiated by you."). Refund policy page exists but was not retrieved (UNVERIFIED). Card FX mark-ups are not included in the EUR figures.

## Required duration

12 months. Phase 6 needs one acquisition/snapshot window plus reruns for validation and the final holdout, which the protocol staggers over months. A 6-month term is workable but risks the holdout stage falling outside the licence.

## Datasets needed (all included in Platinum)

1. Daily OHLCV, unadjusted and total-return modes, for all currently listed and delisted US common stocks and ETFs from 1990-01-01.
2. Delisted-securities database (symbol "-YYYYMM" suffix, last trade date).
3. Historical index constituents: Russell 3000 / 1000 / 2000 (from July 1990), S&P 500 / 400 / 600 / 100, Nasdaq-100, used as the vendor-maintained point-in-time eligibility reference.
4. Turnover, shares outstanding, float, market capitalisation, GICS sector/industry classification.
5. Capital-event and dividend fields (for corporate-action reconciliation tests).

## Why free alternatives are insufficient

- Yahoo/Stooq-style downloads contain survivors only, restate adjusted prices silently, carry no delistings, and their terms do not permit this use. Using them for a cross-sectional factor study would overstate momentum and low-volatility returns by construction (failed firms vanish from the losers/high-vol buckets).
- Tiingo (USD 30) was measured on 2026-09-09: its inactive-ticker coverage is negligible before 2013-2015, so 2000-2012 would be survivorship-biased.
- EODHD (USD 19.99) carries delisted names but no point-in-time index membership before April 2012 (and only on the USD 59.99 plan), no historical market cap, no documented symbol-change continuity and an undocumented pre-2018 delisting depth.
- The Kenneth French library is survivorship-free but portfolio-level only: it cannot build a top-N long-only portfolio, count positions, model Trading 212 costs, or estimate capacity.

## Survivorship implications

Norgate's delisted database (25,222 securities counted to Sep 2022, growing) plus historical Russell 3000 membership lets the universe at date t be defined from securities genuinely in the index or above lagged-liquidity thresholds on t, including those that later went bankrupt or were acquired. Norgate does not supply a delisting return; PHASE6_UNIVERSE_CONSTRUCTION.md preregisters a conservative treatment (Shumway-style haircut for distress delistings, full-loss sensitivity) so that no failed company disappears without its loss being booked.

## Expected volume

Local database delivered by the Norgate Data Updater (Windows application; vendor states up to 63 GB disk for full entitlement). Python package `norgatedata` 1.0.77 reads it while NDU runs. Our exporter will write hashed Parquet snapshots under data/raw/phase6/norgate with a manifest, so every experiment cites immutable files.

## Cancellation / licence terms

No auto-renewal; the subscription simply lapses. EULA: personal, non-commercial use; two computers; no redistribution; on expiry all vendor content must be deleted, but "Derived Data" (backtests, statistics) may be retained. Exported price snapshots are vendor content and would have to be deleted at expiry; experiment outputs and hashes are derived data and stay.

## Fallback if the user declines Norgate

EODHD "EOD Historical Data — All World", USD 19.99/month (EUR 17.16), cancel-any-time monthly billing. Accept the documented limitations (universe rebuilt from lagged liquidity only, delisted depth reconciliation post-purchase). This is a materially weaker basis for the point-in-time requirement and would be recorded as such in every Phase 6 classification.

## What the user must do

Nothing has been bought. If approved, the user subscribes on the Norgate order form, installs the Norgate Data Updater on this PC, completes the initial download, and confirms. No credentials need to be shared with the agent: the Python package reads the local database. The agent will then run the acquisition/export script, the integrity tests, and the preregistered universe construction before any factor result is inspected.
