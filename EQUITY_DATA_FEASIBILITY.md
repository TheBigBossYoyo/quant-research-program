# EQUITY_DATA_FEASIBILITY - desk assessment (2026-09-09), no purchase made

Scope: could a survivorship-safe, corporate-action-safe US equity history with point-in-time universe support be obtained within EUR 50/month, for a later cross-sectional or market-neutral research branch executable through Trading 212 Invest? This is a documentation-level assessment written from previously recorded knowledge; every vendor fact below is marked UNVERIFIED until fetched from the vendor's current page with a retrieval date, and none of it supports a go/no-go decision on its own. Nothing was downloaded or subscribed.

## Requirements (from the protocol)

1. Broad US coverage including delisted names (survivorship handling), ideally 20+ years.
2. Split/dividend/spin-off adjustment with unadjusted prices retained (corporate-action safety).
3. Point-in-time index or liquidity membership so a universe can be formed as of each rebalance date.
4. Checksum-grade reproducibility (files, versions, retrieval dates), an API within rate limits, and no clause preventing local storage for research.
5. Instrument mapping to Trading 212's tradeable list (UK/EU account; US stocks tradeable, but fractional and no shorting), which makes any market-neutral architecture RESEARCH-ONLY under current broker constraints.

## Candidate sources (all UNVERIFIED as of this note)

| Source | Expected cost | Delisted coverage | Corporate actions | Point-in-time universe | Notes |
| --- | --- | --- | --- | --- | --- |
| Free exchange/Yahoo-style feeds | 0 | No (survivors only) | Adjusted only, silently restated | No | Disqualified for this purpose: survivorship and adjustment leakage |
| Nasdaq Data Link WIKI/EOD (Quandl heritage) | discontinued or paid tiers | Partial | Adjusted + unadjusted historically | No | WIKI ended 2018; status of successors UNVERIFIED |
| EODHD (EOD Historical Data) | roughly EUR 20-80/month by tier | Claims delisted tickers | Adjusted and split/dividend files | No native PIT index membership | Nearest fit inside budget on paper; PIT membership would have to be rebuilt from historical index constituent files (also UNVERIFIED) |
| Norgate Data | roughly USD 30-60/month | Yes (delisted database is its selling point) | Yes | Yes (historical index constituents) | Windows desktop delivery; likely the best methodological fit; budget borderline; licence terms for local research storage UNVERIFIED |
| Sharadar (via Nasdaq Data Link) | above budget for full history | Yes | Yes | Partial | Typically > EUR 50/month |
| CRSP / Compustat | academic licence only | Yes | Yes | Yes | Not obtainable |
| Polygon / Tiingo | EUR 25-80/month tiers | Partial delisted coverage | Yes | No | API-first; delisted depth UNVERIFIED |

## Assessment

- Free data cannot satisfy requirements 1-3; using it would reintroduce exactly the survivorship and restatement leakage the protocol forbids.
- One paid source at the top of the budget (Norgate or EODHD) could plausibly satisfy 1-3 and, for Norgate, 4 and the point-in-time requirement; both need a written verification of coverage, licence and export rights before any subscription, and the decision is the user's.
- Even with adequate data, a market-neutral equity architecture is not executable in the current Trading 212 Invest account (no shorting, no margin), so the branch would be research-only until a different venue or a long-only formulation is specified.
- Recommendation: do not purchase now. If Phase 6 opens an equity branch, first obtain the vendor's current documentation with retrieval dates, verify delisted coverage on a known list of 2000-2010 delistings, and preregister the universe rule before any price file is opened.
