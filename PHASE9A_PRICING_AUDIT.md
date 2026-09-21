# PHASE 9A — pricing and licence audit

Retrieved 2026-09-21. **Nothing was purchased. No account was created. No form was submitted.**
Budget preference from the brief: free → ≤ USD 25/mo → ≤ USD 50/mo; > USD 50/mo needs strong
justification; > USD 300 upfront is out of scope at this stage.

---

## Verified prices

| provider / product | price | billing | licence | notes |
| --- | --- | --- | --- | --- |
| **Nasdaq Data Link — ZEEH / ZSEH (Zacks)** | **NOT PUBLIC** | per-feed, monthly / quarterly / annual terms exist | Personal / Academic / Business account types | Price visible only after free login; Personal accounts may see "Contact Sales" instead of a price. **Deep history is institution-only** (see below). |
| **Alpha Vantage — `EARNINGS_ESTIMATES`** | **USD 0** (free tier, 25 req/day) | — | personal | Listed as "Trending", not "Premium". Premium tiers exist for rate limits, USD 49.99/mo cited in the Phase 6 audit. |
| **EODHD — Fundamentals Data Feed** (contains the Calendar API) | **USD 59.99/mo** (USD 599.90/yr ≈ 49.99/mo) | monthly or annual, 1-month minimum | personal use | The route to `/calendar/trends` that is confirmed on the pricing page. |
| **EODHD — All-In-One** | **USD 99.99/mo** (USD 999.90/yr ≈ 83.33/mo) | monthly or annual | personal use | Also contains the Calendar API. |
| **EODHD — Corporate Events Calendar standalone add-on** | **UNVERIFIED** (~USD 19.99/mo per the brief) | — | — | The docs confirm a standalone package exists ("ships in the same standalone package as this calendar") but no price is shown on the public pricing table. |
| **Financial Modeling Prep** | ~USD 22–59/mo per third-party summaries | monthly / annual | — | Moot: rejected on data semantics, not price. |
| **Finnhub** | **USD 0** or **USD 3,500/mo** | All-In-One billed **annually** | "Personal Use. Terms apply" | No intermediate tier exists. Estimates are entirely in the paid tier. 70× the ceiling. |
| **Intrinio — Individual** | **USD 150/mo** | monthly | personal use, 1 seat, no redistribution | **Contains no estimate feed.** Free trial available. |
| **Intrinio — Startup** | **USD 333/mo** rising to 666 then 999 over 12 months | quarterly | commercial | Still no estimate feeds. |
| **Intrinio — Enterprise (only route to Zacks estimates)** | **USD 1,250/mo +** custom feed fees | custom | **Business Use** | Every Zacks estimate feed is tagged ENTERPRISE. |
| **Polygon.io / Benzinga analyst datasets** | **from USD 99/mo** per dataset (individual); 20% off annual | monthly / annual | individual or business | Ratings/price targets/insights, not consensus EPS snapshots. History from 2012. |
| **Zacks direct (zacksdata.com)** | **quote only** | — | institutional | Routes individuals to NasdaqData.com and Intrinio. |
| **Estimize / ExtractAlpha** | **quote only**; historical test files free on request to academics and fintech developers | — | institutional | Coverage ~2011+, contributor-selected cross-section. |
| **LSEG I/B/E/S Point in Time** | **institutional** | — | institutional | Daily snapshots from 2000-01-01. The academic standard. |
| **WRDS** | institutional affiliation required | — | academic | Not available to an individual. |
| **Open Source Asset Pricing (Chen & Zimmermann)** | **USD 0** | — | free, academic citation | 209 firm-level characteristics + 212 predictors' long-short portfolio returns, Oct 2025 release. |

## The decisive licence finding

Nasdaq Data Link FAQ, verbatim:

> **"Q: Why can't I subscribe to full history for Zacks data?**
> If you are viewing the Zacks data feeds and see that you may only subscribe to a limited amount of
> history (e.g. fewer than 3 years of history), even though the data documentation states the data feed
> has many more years of history, this is because our agreement with Zacks restricts deeper history to
> institutions only.
> As per our agreement with Zacks, deeper history or full history may only be licensed to
> institutions/businesses and not to individuals."

And on quote-gating generally:

> "Depending on your account type (Business, Academic or Personal), the pricing page for certain data
> feeds may only show a 'Contact Sales' button."

> "Sorry, Nasdaq Data Link and the publisher are only able to license this product for select use-cases…
> We show the above message for data feeds that are for institutional use only."

**Consequence.** Even at an acceptable monthly price, a Personal Nasdaq Data Link account cannot obtain
the 2010–2017 Zacks history this programme requires. A roughly 3-year window would support forward
paper trading and live signal generation, but not development or validation. Registering a Business
account to get around this is a legal representation about how the data will be used, not a technical
workaround, and is outside what this research programme should do on its own initiative.

## Terms that would matter if a purchase were ever authorised

Verified from the Nasdaq Data Link FAQ:

- **Free account**, no credit card, to see pricing and samples. Account types: Business / Academic /
  Personal; the type **cannot be changed later** (a new account with a different email is required).
  Okta activation plus MFA is mandatory.
- **Free samples** exist for almost all premium feeds. `ZACKS/EEH`'s sample is 30 large-cap tickers with
  `obs_date` in 2018.
- **Self-serve checkout** where offered: pick a history depth and a monthly / quarterly / annual term,
  accept the terms, enter name, address and card.
- **Cancellation**: any time via Account Settings → Subscriptions → Unsubscribe. Access continues to the
  end of the paid period, then simply does not renew.
- **Retention after cancellation**: **not stated in the FAQ.** The per-feed "View Full License" is the
  governing document and is visible only after login. This must be read before any purchase — a feed
  that forbids retaining extracted history after cancellation changes the economics of a one-month pull.
- **Rate limits**: premium subscribers get the highest API limits; bulk download, Tables API pagination,
  SQL interface and the Python client are all supported for export.

## Price/value verdict against the brief's ladder

| tier | what it buys in this family |
| --- | --- |
| **Free** | Alpha Vantage (class B, from 2017-06, unusable here) and OSAP portfolio returns (evidence, not a tradable panel). |
| **≤ USD 25/mo** | Nothing that passes the two-date test. |
| **≤ USD 50/mo** | Nothing that passes the two-date test. |
| **USD 50–100/mo** | EODHD Fundamentals (class C — buying it would be buying the wrong object); Polygon/Benzinga ratings (wrong family). |
| **> USD 1,000/mo or quote-only** | The only class-A sources: Zacks deep history, Intrinio Enterprise, LSEG I/B/E/S PIT. |

There is no price point between free and institutional at which point-in-time analyst consensus history
becomes purchasable by an individual. That is the finding, and it is a licence structure rather than a
gap in the search.
