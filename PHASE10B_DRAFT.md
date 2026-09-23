# PHASE 10B — DRAFT ONLY, NOT EXECUTED, NOT PREREGISTERED

> **Superseded in part, 2026-09-23.** The causal-timing audit (`PHASE10B_STAGE0_TIMING_AUDIT.md`) returned **OSAP_SHORTINTEREST_TIMING_CAUSAL_FAIL**: before
> September 2007 the exchanges had no required short-interest release date and published as late as the
> first of the following month, which is on or after the day OSAP's return period begins. Stage 0 as
> specified below is **not executed**. The only surviving variant is a 2008-2017 window, which needs its
> own preregistration. The leg-orientation claim below has also been corrected.

Status: **draft**. Nothing here is frozen or hashed. No experiment ID. No cell added to the 490-cell
ledger. Running any stage below requires a separate preregistration, hashed and committed **before any
return is read**, exactly as Phase 9B Stage 0 was.

Written because Phase 10A found the family **partially available**: a free, correctly structured panel
that starts 2017-12-29, and historical panels with no published price.

---

## The mechanism

Short interest is the outstanding reported short position — the accumulated view of informed sellers,
disclosed publicly twice a month with a ~7-12 day lag. Two readings:

- **high short interest → subsequent underperformance** (Dechow et al. 2001; Asquith, Pathak and
  Ritter 2005, strongest where borrow supply is constrained);
- **low short interest → subsequent outperformance** (Boehmer, Huszar and Jordan 2010), with the
  positive long-side effect *larger in absolute value* than the negative short side.

The second is why this family was worth auditing. Almost every anomaly this programme has examined is a
short-side story that dies under a long-only mandate; this one is documented as the opposite shape.

**Correction to the brief, made before any test.** The brief nominated *change in short interest over
the latest 1-2 reports* as PRIMARY. The literature does not support that ordering: evidence for the
change is confined to distressed firms, a one-month change has been found to carry no marginal
predictive power once the demeaned short-interest ratio is controlled for, and the open-source
replication corpus contains three short-interest **level** predictors and **no change predictor at all**.
This draft therefore makes the **level primary and the change corroborating**. If that inversion is not
accepted, Phase 10B should not run, because it would be leading with the weaker and unreplicated form.

## Stage 0 — free external mechanism screen (the only executable stage)

**Purpose.** Decide, with no purchase, no new download and no locked data, whether short-interest
sorting still separated returns in the development era — and specifically whether the **low-SI long
leg** beats a *value-weighted* market rather than merely an equal-weighted universe.

**Data.** `data/raw/phase9b/PredictorPortsFull_202510.csv`, already on disk, sha256
`6cdaf0ff051222b813e6f8404d7a30b94e146b421625f202bd04473fe97a1817`. Open Source Asset Pricing,
October 2025 release, free under academic citation.

**Signals — fixed, three, no sweep:**

| role | signal | source |
| --- | --- | --- |
| **PRIMARY** | `ShortInterest` | Dechow et al. 2001; short interest / shares outstanding; `Sign = −1`; EW; monthly |
| corroboration | `IO_ShortInterest` | Asquith, Pathak, Ritter 2005; institutional ownership among the top 1% of short interest |
| corroboration | `Recomm_ShortInterest` | Drake, Rees, Swanson 2011 |

Nothing else may be loaded. No other OSAP predictor may be scanned after these results are seen.

**Structural facts already established** (names, ports and dates only; `ret` never read —
`reports/phase10a/raw/osap_short_interest_portfolio_structure_20260922.json`): `ShortInterest` has ports
`01`-`05` plus `LS`, 1973-02 → 2024-12, **539 pre-2018 months**. `IO_ShortInterest` has `01`-`03` + `LS`;
`Recomm_ShortInterest` has `01`-`02` + `LS`.

**Which port is the long leg — RESOLVED 2026-09-23, and this draft's original claim was wrong.**
This draft first asserted that `Sign = −1` puts the long side at port 01. It does not. OSAP applies the
sign **before** sorting (`signal$signal = signal$signal*Sign`) and names the legs by port number
(`longportname = max(port$port)`), so **port 05 is always the long leg**; for `ShortInterest` it holds
the *lowest raw short interest*, which is the long-only reading we want. Proved mechanically on all 539
pre-2018 months from counts alone: `LS.Nlong == port05.Nlong` and `LS.Nshort == port01.Nlong` in 539/539.
See `PHASE10B_STAGE0_TIMING_AUDIT.md` §2.

**Windows** — identical to Phase 9B so the two screens are comparable:

| window | range | role |
| --- | --- | --- |
| EARLY | 1990-01 .. 2004-12 | decay reference |
| **MODERN** | **2005-01 .. 2017-12** | **decision window** |
| RECENT | 2010-01 .. 2017-12 | recent-era robustness |

Everything dated 2018-01-01 or later is rejected in code immediately after the date column is parsed and
before `ret` is used, then re-checked by `research/phase6_lock.enforce(..., segment='development')`.

**Statistics** — as frozen in Phase 9B: n, mean monthly, annualized mean (12×), annualized volatility
(√12 × sample sd), Sharpe, Newey-West t under the fixed rule `L = floor(4·(T/100)^(2/9))`, and cumulative
return as descriptive output only.

**Benchmarks** — both frozen before execution, as in Phase 9B:

- **B1 (gate)** — `EWCOV`, the `Nlong`-weighted average of the populated quantile ports from the same
  file: same source, same universe, same equal weighting.
- **B2 (reported, and this time it should arguably gate)** — CRSP value-weighted market, `Mkt-RF + RF`
  from the Phase 6 French library already on disk.

**Note for the preregistration author:** in Phase 9B, B2 was deliberately non-gating and the
`beats_b1_but_not_b2` warning fired. Given that Asquith-Pathak-Ritter *measure* this family's effect
collapsing from 215 bp EW to an insignificant 39 bp VW, there is a strong case for making B2 a gate here
rather than a footnote. That choice must be made **in the preregistration, before any return is read**,
and argued on the literature rather than on the result.

**Indicative gate** (to be finalised and frozen in the preregistration, not here):

1. `ShortInterest` 2005-2017 long-short mean > 0 **and** NW t ≥ 2.0;
2. `ShortInterest` 2010-2017 long-short mean > 0;
3. at least one corroborating signal positive in 2005-2017;
4. **low-SI long leg excess over B1 > 0 in both windows**;
5. **low-SI long leg excess over B2 > 0 in both windows** — the condition the last three candidates failed.

Failing (1) → `REJECT_SHORT_INTEREST_MECHANISM`. Passing (1) but failing (5) →
`MECHANISM_SURVIVES_BUT_NOT_LONG_ONLY_AT_LARGE_CAP`, which is a rejection for *this* programme even
though it is not a rejection of the anomaly.

**Limitations to state in the output.** Third-party decile/quintile portfolios, gross, costless,
equal-weighted, monthly rebalanced, full CRSP cross-section including microcaps we could not trade,
built from Compustat short interest we cannot license. An upper bound on nothing — the Phase 9B lesson
holds: long-short = long leg − short leg, and the spread bounds the long side in neither direction.

**Cells added: 0.**

## Stage 1 onwards — BLOCKED, sketched so it cannot be retrofitted later

Runs only if Stage 0 is encouraging **and** a data route opens.

**Data.** NYSE Group Short Interest (1988→, CUSIP, `Free_Float`, `Change_In_Short_Interest_Position`,
`Revision_Indicator`, `Split_Indicator`) **plus** Nasdaq Short Interest bulk SFTP (month-end from
2007-09). Both are required: NYSE alone omits every Nasdaq-listed issuer. Both are quote-priced.

**Preconditions, all three, before any purchase:**

1. **Immutability test** — pull one settlement date twice, ≥ 14 days apart, diff. Any change to a
   historical row demotes the source from point-in-time. Both schemas carry revision flags, so this is a
   live risk, not a formality.
2. **Publication-date archive** — obtain and store the per-year settlement→release calendars (NYSE
   Group Short Interest Calendar; FINRA reporting deadline tables). Assert every reconstructed release
   date is ≥ settlement + 7 business days. Signal date is the **release** date, never the settlement date.
3. **Split handling** — short interest is a share count, so a split between cycles changes the level
   mechanically. Any change signal must read `Split_Indicator` / `stockSplitFlag` and drop or adjust the
   affected observation. A 2-for-1 split read naively is a +100% "increase in bearish positioning".

**Architecture** — small, low-turnover, and the same shape the last three phases used so results stay
comparable: liquid US universe with PIT membership and delisted issuers retained; **semi-monthly or
monthly** ranking, never event-driven on each report; **long-only**, top 20/30/50, equal weight, no
leverage; Trading 212 base and 20 bp stress cost cases; **SPY/value-weighted market as the primary
benchmark** with a CAPM and FF5+MOM alpha gate; development ≤ 2017-12, validation only on a development
pass, holdout only after architecture freeze; feasible at EUR 500-1,000 or explicitly capital-limited.

**Trial budget.** Primary (level) + 2 variants (change over 1-2 reports; SI/float) × 3 portfolio sizes
= **9 cells maximum**, declared in advance, added to the cumulative 490 and carried into the deflated
Sharpe.

**If only FINRA data is ever available** (i.e. 2018 onward), the existing chronological split cannot be
stretched. A new split would have to be preregistered from scratch, with the reduced sample and its
consequences for power stated before any result is seen — and the whole of it would sit inside what is
currently validation and holdout, which is a separate and much larger decision.

## What voids this draft

- Stage 0 rejects the mechanism → family closed on evidence, no purchase discussion.
- Stage 0 shows the effect surviving only equal-weighted → closed for *this* programme, and recorded as
  such rather than as a general rejection.
- No quote is obtained, or the quotes are enterprise-scale → family stays recorded as partially
  available and dormant.
- The immutability test fails → the data is not point-in-time and no purchase is justified.
