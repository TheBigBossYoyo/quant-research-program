# PHASE 10A — recommendation

Date: 2026-09-22. Audit only. No backtest, no purchase, no locked data. Ledger unchanged at 490.

## Verdict

# SHORT_INTEREST_DATA_PARTIAL

Not `NO_AFFORDABLE_CAUSAL_SHORT_INTEREST_DATA`, because a free, correctly structured, venue-consolidated,
survivorship-safe issue-level panel demonstrably exists and is queryable today without a key. Not
`FREE_SHORT_INTEREST_DATA_SUFFICIENT` or `AFFORDABLE_..._FOUND`, because that panel begins on
**2017-12-29** — one settlement date before the development window closes — and everything with a real
history is priced by quote under an enterprise licence.

## 1. The shape of the finding

| | free | paid |
| --- | --- | --- |
| **has 2010-2017 history** | — | NYSE (1988), Nasdaq (2007), Compustat/WRDS |
| **issue-level & consolidated** | FINRA (2017-12-29 →) | — |
| **price published** | yes ($0) | **no, for every single one** |

The free source and the historical sources are disjoint, and the split falls almost exactly on our
development boundary. FINRA's free consolidated API has better structure than anything we have audited
in three phases — 15,495 issues on a single settlement date, venue-consolidated across NYSE/NNM/ARCA/
SC/AMEX/BZX/OTC, revision and split flags, days to cover, previous-period level for a change signal,
and delisted issuers verifiably preserved (TWTR, CELG and RTN all return rows on 2017-12-29). It is
simply eight years too young.

## 2. Why no purchase is recommended

Three reasons, in descending order of importance.

**(a) The mechanism screen is discouraging where it matters most.** Asquith, Pathak and Ritter measure
the effect at **215 bp/month equally weighted and 39 bp/month value-weighted, insignificant**. Chen and
Welch put the post-2005 median large-cap anomaly at **7 bp/month**. Every short-interest portfolio in the
open-source corpus is equal-weighted. This programme has already produced three candidates that beat an
equal-weighted universe and lost to the value-weighted index a retail account can buy — Phase 8's
insider cell, Phase 8B's E062, and Phase 9B Stage 0's analyst-revision long leg. A fourth is the
default expectation here, and spending money to discover it again would be poor judgement.

**(b) The brief's PRIMARY signal is the weaker documented form.** The literature supports the **level**;
evidence for the **change** is confined to distressed firms, and a one-month change has been found to
carry no marginal predictive power once the demeaned short-interest ratio is controlled for. The free
replication corpus contains `ShortInterest`, `IO_ShortInterest` and `Recomm_ShortInterest` — all levels
— and **no change-in-short-interest predictor at all**. Buying data to test change-first would be
buying the wrong test.

**(c) No price is public anywhere.** NYSE's issue-level product does not appear in either of its public
pricing guides; the governing rule is "a flat fee per NYSE Market Data product per organization … on an
enterprise-wide basis". Nasdaq's bulk file is "subscribe for SFTP" with no figure, and its own
*Publication Schedule* and *Data Fields & Definitions* links **404**. We cannot evaluate against the
USD 25 / 50 ladder because there is nothing to evaluate. And NYSE alone would not be enough — it
excludes every Nasdaq-listed issuer.

The one genuinely encouraging result — Boehmer, Huszar and Jordan's finding that the **low**-short-interest
long side is the *larger* half of the effect, unusual for an anomaly and the reason this family fits a
long-only mandate at all — comes from a 1988-2005 sample that predates its own publication.

## 3. What is worth doing, and it is free

The same move that worked in Phase 9B. `data/raw/phase9b/PredictorPortsFull_202510.csv` is **already on
disk and already hashed**, and it contains published quintile and long-short portfolio returns for
`ShortInterest` (Dechow et al. 2001) with **539 pre-2018 monthly observations**, span 1973-02 onward,
`Sign = −1` so the long leg is the low-short-interest side — exactly the long-only interpretation.

That answers, for zero cost and with no new data, the question that decides whether any purchase could
ever be justified: **did short-interest sorting still separate returns in 2005-2017, and did the low-SI
long leg beat a value-weighted market rather than just an equal-weighted universe?**

If it did not, the family closes on evidence and no price would have mattered. If it did, we would at
least know what we were being asked to pay for. `PHASE10B_DRAFT.md` specifies this as Stage 0 and it is
**not executed** — Phase 10A computes no returns.

## 4. If the family ever cleared Stage 0

Two acquisitions would be needed together, not one:

1. **NYSE Group Short Interest** — 1988 onward, CUSIP, `Free_Float`, `Change_In_Short_Interest_Position`,
   `Revision_Indicator`, `Split_Indicator`, and an official settlement→release calendar. Best-structured
   source audited. Price by quote; NYSE/American/Arca only.
2. **Nasdaq Short Interest bulk SFTP** — month-end from September 2007, to cover the Nasdaq-listed half
   of the universe. Price by quote; documentation links currently broken.

Both would need the immutability test (pull one settlement date twice, weeks apart, diff) before any
research use, for the same reason it was specified for Zacks in Phase 9A: revision flags exist in both
schemas, so restatement is a real possibility and a silently restated archive is not point-in-time.

Neither should be requested now.

## 5. Consequences for the programme

- The short-interest family is **not rejected and not adopted**. It is **partially available**: free
  data with the right structure and the wrong start date; historical data with the right start date and
  no published price.
- **0 cells added. Cumulative ledger 490.** No hypothesis was tested.
- Validation 2018-2021 and holdout 2022-01..2026-08 remain **unopened**. The NYSE issue-level sample
  files on the public FTP were deliberately **not downloaded** because both sample dates fall in the
  holdout.
- Daily short-sale volume is recorded as a **separate, untested information family**. It is abundant and
  free at both NYSE and FINRA, and nothing in this audit says anything about it.

## 6. Exact next action

**Decision required from the user.** In the order this audit would rank them:

1. **Run Phase 10B Stage 0** (free, no purchase, no locked data, no new download): screen the
   `ShortInterest` published portfolios on ≤ 2017-12 against both an equal-weighted covered-universe
   benchmark and the value-weighted market, with the level as the primary signal. This is the cheapest
   way to find out whether the family survives the large-cap/value-weighted test that has killed the
   last three candidates. Recommended.
2. **Ask NYSE and Nasdaq for a quote** on the two short-interest products (an email to `datasales@nyse.com`
   and the Nasdaq subscription contact). This requires a human; the agent does not open vendor sales
   conversations. Only worth doing after Stage 0, and only if Stage 0 is encouraging.
3. **Accept the family as partially available and dormant**, and either name the next distinct mechanism
   or close the equity programme at "no qualifying strategy on obtainable data".

Nothing is purchased under any option. Locked data stays locked under all three.
