# PHASE 10A — mechanism / literature screen

Date: 2026-09-22. **No returns were computed.** This is a reading of published evidence to decide
whether the family deserves data spending, not a test of it.

The six questions the brief posed, answered as directly as the literature allows.

---

## Q1. Is the LEVEL of short interest associated with future returns?

Yes, and it is one of the older documented effects. Dechow et al. (2001) is the reference
implementation in the open-source replication corpus (`ShortInterest`, short interest scaled by shares
outstanding, `Sign = −1`: high short interest predicts low returns), original sample 1976-1993.
Asquith, Pathak and Ritter (2005) sharpen it to constrained stocks — high short-interest demand
against low institutional-ownership supply.

Short interest is also, separately, an unusually strong **aggregate** market-timing predictor
(Rapach, Ringgenberg and Zhou, JFE 2016), with in-sample and out-of-sample annual R² near 13%. That is
a different use of the same raw data — one that the free NYSE aggregate file could actually support —
and it is not the cross-sectional family drafted for Phase 10B.

## Q2. Is the CHANGE in short interest more informative than the level?

**The evidence does not support that as a general claim, which matters because the brief nominated
change as the PRIMARY signal.**

- Changes appear more informative specifically for **financially distressed** firms, where they proxy
  for shifts in short-sellers' beliefs.
- Outside that, results favour the level. Work on short-interest surprise reports that a one-month
  change has **no marginal predictive power** once the demeaned short-interest ratio is controlled for;
  cross-country work finds the ratio predicts while the change does not.
- The open-source replication corpus is telling by omission: it carries `ShortInterest`,
  `IO_ShortInterest` and `Recomm_ShortInterest` — all **levels or level interactions** — and **no
  change-in-short-interest predictor at all**.

So a Phase 10B that made "change over the latest 1-2 reports" primary would be leading with the weaker
of the two documented forms, and with the one that has no free replication to screen against. If this
family is ever preregistered, **the level should be primary and the change corroborating** — the
reverse of the draft brief. That is the single most consequential finding in this screen.

## Q3. Are results primarily on the short side?

**No — and this is the one genuinely encouraging thing here.** Boehmer, Huszar and Jordan, "The Good
News in Short Interest" (JFE 96(1), 2010, NYSE/AMEX/NASDAQ 1988-2005): relatively heavily traded
stocks with **low** short interest earn statistically and economically significant **positive**
abnormal returns, and those positive returns are "often larger (in absolute value) than the negative
returns observed for heavily shorted stocks". Their interpretation is that the good news in low short
interest is publicly available and only slowly impounded.

The heavily-shorted short side is weaker and, in their words, "can be transient and of debatable
economic significance".

Most anomalies this programme has examined are short-side stories that collapse under a long-only
constraint. This one is the opposite shape, which is why it was worth auditing at all.

## Q4. Has the effect materially decayed post-publication?

Yes, and the programme should assume so.

- McLean and Pontiff (2016): roughly a **50% decline** in anomaly returns after publication, broadly.
- Chen and Welch, "What Useful Alphas?" (2026), across about 200 published long-short anomaly
  portfolios: median **48 bp/month through 2005**, falling to **19 bp post-2005**, and to **7 bp**
  when restricted to post-2005 years **and** the top 90% of market capitalisation by stock count.

The short-interest papers above are 1988-2005 and 1976-1993 samples — entirely pre-publication. Nothing
in this screen establishes what survives in 2010-2017, which is exactly the window we cannot buy data
for.

## Q5. Does the economically useful side survive in large / liquid stocks?

**This is where the family looks most fragile.**

Asquith, Pathak and Ritter report constrained stocks underperforming by **215 bp/month equally
weighted** but only **39 bp/month value-weighted, and insignificant**. The effect is concentrated in
small, illiquid, hard-to-borrow names.

That is the same object this programme has now produced three times: Phase 8's insider-purchase cell,
Phase 8B's repurchase cell (E062), and Phase 9B Stage 0's analyst-revision long leg all beat an
equal-weighted universe and lost to the value-weighted index a retail account can buy. Every
short-interest portfolio in the open-source corpus is likewise `Stock Weight = EW`.

Chen and Welch's 7 bp/month for large caps post-2005 points the same way. A Trading 212 book at
EUR 500-1,000, long-only, without microcaps, is on the wrong side of this split.

## Q6. Is the signal plausibly usable LONG-ONLY?

**Plausible in principle, unproven in the modern era, and probably small.**

The long-only reading is "hold low short interest" — Quantpedia lists exactly this as a strategy:
"Stocks are sorted based on their short interest ratio, and the first percentile is held. The portfolio
is equally weighted and rebalanced monthly", citing Boehmer-Huszar-Jordan and reporting 26.8% CAGR with
-33.3% maximum drawdown on the 1988-2005 sample. Two caveats are attached in the same source: the
strategy is highly correlated with the broad market, and equal-weighting materially outperforms
value-weighting.

A 26.8% CAGR from a pre-publication sample, equal-weighted, at the first-percentile extreme, is not
evidence about a 30-stock liquid long-only book in 2010-2017. It is the upper end of the most
favourable published configuration.

## What this screen implies

| question | answer | consequence |
| --- | --- | --- |
| level predictive? | yes, documented since the 1970s-90s samples | keep |
| change better? | **no, weaker and unreplicated free** | **invert the draft: level primary** |
| short-side only? | **no — the long side is the larger half** | the one reason this family fits us |
| decayed? | yes, assume ~50%+ and more in large caps | expect small |
| survives in large caps? | **doubtful — 215 bp EW vs 39 bp VW insignificant** | the likely killer |
| long-only usable? | plausible, unproven post-2005 | needs a modern test we cannot run |

The mechanism is the right *shape* for this programme and the wrong *size*. And the only window that
would settle it — 2010-2017, large-cap, value-weighted-benchmarked — is the window with no affordable
data.

## Sources

- Boehmer, Huszar, Jordan, "The good news in short interest", *Journal of Financial Economics* 96(1), 2010, 80-97.
- Asquith, Pathak, Ritter, "Short interest, institutional ownership, and stock returns", *JFE* 78(2), 2005, 243-276.
- Dechow, Hutton, Meulbroek, Sloan (2001), as implemented in the Open Source Asset Pricing `ShortInterest` predictor.
- Drake, Rees, Swanson (2011), OSAP `Recomm_ShortInterest`.
- Rapach, Ringgenberg, Zhou, "Short interest and aggregate stock returns", *JFE*, 2016.
- McLean and Pontiff (2016), post-publication decay.
- Chen and Welch, "What Useful Alphas?", arXiv 2607.06502, 2026.
- Quantpedia, "Short Interest Effect — Long Only version".
