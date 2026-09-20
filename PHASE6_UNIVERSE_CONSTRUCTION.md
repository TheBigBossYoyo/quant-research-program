# PHASE6_UNIVERSE_CONSTRUCTION - point-in-time US equity universe (preregistered 2026-09-09, before any stock-level data exists in the repository)

Applies to the stock-level track on Norgate Data (recommended provider) or, with the documented degradations in section 7, on EODHD. Nothing here may be changed after stock-level results are inspected except through a versioned amendment recorded in EXPERIMENTS.md that counts as an additional trial.

## 1. Principle

At rebalance date t the strategy may only use securities and fields observable at the close of t-1 (signals) and may only trade at prices from t onward. Membership, liquidity, price, history and classification are all evaluated from data dated at or before t-1. The universe is rebuilt at every rebalance date from the full security master, including securities that were later delisted, acquired or bankrupt.

## 2. Security master (mechanical inclusions)

Included: US-listed common stocks (NYSE, NYSE American/AMEX, NASDAQ, and their predecessors) as classified by the vendor's security type, currently listed or delisted.
Excluded mechanically: ETFs, ETNs, closed-end funds, unit investment trusts, preferred shares, warrants, rights, units, SPAC units, limited partnership units where the vendor flags them, ADRs and other foreign-domiciled depositary instruments, OTC/pink-sheet listings (Norgate's "formerly major exchange listed" OTC continuation is used only to record post-delisting prices for the delisting-return rule, never for new positions), and securities without a GICS sector classification. Multiple share classes of one issuer: keep the class with the higher lagged 63-day median dollar volume.

## 3. Eligibility filters at rebalance date t (all lagged, all mechanical)

| Filter | Rule (base) | Sensitivity band (counted as neighbourhood, not free parameters) |
| --- | --- | --- |
| History | at least 252 daily prices before t | 189, 378 |
| Membership | member of the Russell 3000 on t-1 per vendor historical constituents (from 1990-07-01); before Russell availability no stock-level test is run | S&P 1500 membership as alternative reference |
| Price | unadjusted close on t-1 >= USD 5 | USD 3, USD 10 |
| Liquidity | median daily dollar volume over the 63 trading days ending t-1 >= USD 1 million (1990 dollars are not rescaled; the rank filter below dominates in later years) | USD 0.5m, 2m |
| Rank cap | top N by that lagged 63-day median dollar volume, N = 1000 | N = 500, 1500 |
| Data quality | no missing close in the last 21 trading days; no zero-volume day in the last 5 | - |

Market capitalisation is not used as an eligibility filter because point-in-time shares outstanding must first pass an integrity check against known splits; it may be used later as a control variable in Fama-MacBeth regressions once that check passes.

## 4. IPO and new-listing handling

A security enters the eligible set only once every feature it needs is computable from real history (252 days for momentum 12-1; 252 days for volatility measures; industry classification present). No back-filled prices, no pro-forma histories. Spin-offs start their own history on the first trading day.

## 5. Delistings, acquisitions and bankruptcies

Norgate does not provide delisting reasons or delisting returns. Rule, applied to any held security whose vendor series ends:
1. The position is closed on the last vendor price date at the last close (or, for the total-return mode, the last total-return value).
2. Distress proxy: if the return from 126 trading days before the last date to the last close is <= -50 percent, or the last unadjusted close is below USD 1, the delisting is treated as performance-related and an additional delisting return is applied: -30 percent for NYSE/AMEX listings, -55 percent for NASDAQ listings (Shumway 1997; Shumway and Warther 1999). Otherwise the delisting is treated as an exchange/acquisition event and no additional return is applied.
3. Sensitivity (mandatory, reported with every stock-level result): (a) -100 percent on all distress-proxy delistings; (b) -30 percent on all delistings regardless of proxy.
4. Delisted securities never disappear from the universe history: the delisting month's return is booked in the strategy and in the benchmark (equal-weight eligible universe) alike.
5. Post-purchase reconciliation test: a fixed list of known failures must be present with an end date in the correct month (Enron 2001-12/2002-01, WorldCom 2002-07, Bear Stearns 2008-05, Lehman Brothers 2008-09, Washington Mutual 2008-09, Circuit City 2009-01, General Motors old 2009-06, Blockbuster 2010-07, Eastman Kodak 2012-01, Radioshack 2015-02, SunEdison 2016-04) and a fixed list of acquisitions (Compaq 2002-05, Gillette 2005-10, Anheuser-Busch 2008-11, Wyeth 2009-10, Burlington Northern 2010-02, Heinz 2013-06). Failure of this test blocks all stock-level results.

## 6. Ticker and exchange changes

Continuous vendor series are used (Norgate merges history across symbol changes). Exchange transfers do not trigger any trade. Reverse splits are handled by the vendor adjustment; the unadjusted price filter uses the unadjusted close so that a reverse-split penny stock cannot re-enter the universe through adjustment.

## 7. If EODHD is used instead of Norgate

Membership filter unavailable before 2012: replace with liquidity rank only; record "NO_PIT_MEMBERSHIP" in every result. Symbol continuity undocumented: every ticker whose history starts after 2000 with a large first-day volume must be checked for a predecessor symbol; unresolved cases are excluded from that date (counted and reported). Delisting dates from the delisted-tickers list end date. Historical market cap unavailable: no size controls.

## 8. Sector classification

GICS sector (11) and industry group (24) from the vendor as of the current snapshot. This is not point-in-time: reclassifications are rare but exist; the sector-neutral tests will be repeated on the 49-industry French SIC mapping (which is point-in-time by construction of the French portfolios) as a cross-check at the family level.

## 9. Benchmarks derived from the same universe

Equal-weight eligible universe (rebalanced with the strategy), lagged-dollar-volume-weighted eligible universe, and the CRSP-based market factor from the French library (external, total return). All benchmarks book delisting returns identically.

## 10. Rebalance calendar

Primary: monthly, signals at the last trading day's close of month m, orders executed at the open of the first trading day of month m+1 (next-day open after the signal). Alternatives counted as a neighbourhood: weekly (Friday close -> Monday open) and biweekly. Weekday choice is never tuned after seeing results; if a weekday sensitivity is run, it is one preregistered table with all five weekdays reported.
