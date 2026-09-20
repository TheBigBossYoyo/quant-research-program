# Research conclusion — 8 September 2026

## Verdict

**No strategy currently passes.** After 243 counted hypotheses across fourteen economic families on two asset classes, tested under preregistration, chronological locks, three cost cases, multiplicity accounting and adversarial audits, no candidate qualifies for the 2025 validation set. The program stops under condition B of the continuation contract: the executable research space for the data and venues available has been responsibly exhausted, and further search on the same data would be duplicative or a disguised parameter sweep. This is a research result, not a failure of process, and it is explicitly preferable to a false positive.

The 2025 validation data were never analysed. The 2026 final holdout was never downloaded. No live trading, paper trading or capital exposure occurred. No credentials were used.

## What was tested

| Family | Experiments | Data | Best development result | Why it fails |
|---|---|---|---|---|
| Spot time-series momentum/reversal, 5m–daily | E001–E003 | BTC/ETH spot 5m 2022–24 | Daily 48-bar momentum, positive but uncertain | Intervals include zero; 30–60% drawdown risk; delay-sensitive |
| Delta-neutral funding carry (monthly, continuous, capped) | E004–E009 | Perp hourly, funding | ETH capped carry 2.1% CAGR | Below 4.3% short-rate reference; GBP translation risk; maintenance unverified |
| Perpetual momentum/reversal, signed | E010–E011 | Perp hourly 2022–24 | Daily ETH momentum 8.4% stressed | Fails uncertainty; 39% drawdown; loses almost all return with one extra day of delay |
| Taker-flow reversal, single asset | E012 | Perp hourly + spot | Hourly reversal IC -0.02 to -0.03, robust | About 1 bp of edge against 14 bps round trip; fee-only ledgers lose 41–57%/yr |
| Funding/basis positioning, single asset | E013 | Perp 8h/daily | Contrarian sign in all 16 cells | Under-powered; faded to zero in 2024 |
| Cross-sectional momentum/reversal, funding carry, relative flow | E014, E016 | 396-symbol perp universe 2020–24 | 7-day flow continuation: 34.6% CAGR, Sharpe 1.31 stressed | Fails 207-trial bound; hostile audit: 2020-driven, top-ten names > all P&L, short leg loses, post-2020 excess ≈ 0 |
| Slower flow variants (14/28-day) | E017 | same | 14-day: 47% CAGR, Sharpe 1.58 | Fails adjusted bound at 7-day blocks; same 2020 concentration |
| Low volatility, abnormal volume, illiquidity | E018 | same | vol30 rank IC -0.07 (t -4.5) | Spread portfolio loses 14%/yr: short high-vol leg eats the lottery tail |
| Market-wide funding/breadth timing of BTC | E019 | same, weekly | IC 0.00 / 0.04 | Intervals include zero |
| ETF trend and momentum, long-only monthly | E020 | 12 GBP UCITS ETFs 2009–19 | Trend12 Sharpe 0.56, 6.1% CAGR | Below equal weight (0.74) and 60/40 (0.96) on Sharpe and drawdown |
| Session / funding-hour seasonality | E021 | Spot 5m | all negative | One round trip per day at 24 bps destroys the account |
| BTC/ETH lead-lag | E022 | Perp hourly | IC -0.023 both directions | Same cost-dominated hourly reversal as E012 |
| 90-day cross-sectional momentum | E023 | perp universe | IC -0.017, t -1.2 | Insignificant |

Cost cases used: spot 10/12/24 bps per side; perpetual 5/7/14 bps per executed notional (alts 7/14/28); ETFs 10/20/40 bps; funding charged with sign; opportunity cost against lagged US or UK short rates where relevant.

## What the evidence says

Three effects are statistically robust on Binance data: reversal after aggressive taker flow at the one-hour horizon (both within an asset and across BTC/ETH), the cross-sectional rank of relative taker flow, and the cross-sectional rank of realised volatility. None is a strategy for this account. The hourly reversal is the compensation earned by passive liquidity providers; a retail taker pays it rather than collects it, and the measurable edge is an order of magnitude below the round trip. The flow rank carries genuine information (0 of 200 within-week placebos match it) but its payoff came from illiquid names in 2020 and vanishes after costs and outside that year. The volatility rank is real in medians and negative in means because the short leg is short the coins that occasionally multiply.

The slow, executable mechanisms are real but not attractive: funding carry earned about 2% a year against a 4% risk-free reference; ETF trend and momentum lagged a plain equal-weight allocation over the development decade.

## Reopening conditions

The search should reopen only when one of these changes the information set, and each new branch must be preregistered and counted on top of 243:

1. **Order-book or trade-level data** for BTC/ETH perpetuals (the public bookTicker/bookDepth archives, or a paid feed inside the EUR50/month budget after a written justification of what free data cannot answer) to test whether the hourly flow reversal can be captured with passive orders, including fill probability and adverse selection. Caveat already measured in E012: the aggregate hourly reversal edge is about one basis point, below even a fee-only maker round trip of four basis points, so book data would only be worth acquiring to test book-conditioned signals (a different information set), not maker execution of the OHLCV signal.
2. **More perpetual history and regimes** for the cross-sectional flow effect, so that its 2020 dependence can be judged against years not yet seen; the 2025 set must not be used for this.
3. **Read-only account facts** (fees, maintenance tiers) only if a candidate reaches a promotion gate that depends on them.
4. **A checksum-grade ETF data source** with a longer development window if the ETF branch is revisited; the current development decade is structurally hostile to trend rules and the 2020–2024 split must remain untouched until a development candidate passes.

## Integrity notes

Defects found and fixed during this session, with regression tests: none in the ledgers; one archive data defect (seven daily rows with taker volume above total volume, quarantined at the field level). Test count at close: 62. Every experiment directory contains results.json with the code hash, sources, cost cases, seeds and the full set of rejected configurations. Raw archives are checksum-verified except the yfinance ETF files, which are hashed at retrieval.
