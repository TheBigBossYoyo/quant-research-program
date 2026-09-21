# PHASE 9A — recommendation

Date: 2026-09-21. Audit only. No backtest, no locked data, no purchase.

## Verdict

# NO_AFFORDABLE_PIT_ANALYST_DATA

...with one qualification that keeps the branch alive at zero cost, set out in §3.

## 1. Why not PURCHASE_CANDIDATE_FOUND

The brief asked for the cheapest source supporting a causal historical backtest of analyst revisions.
The right dataset was found on the first priority provider and is not a near miss on price — it is
**not sold to individuals at any price**.

`ZACKS/EEH` on Nasdaq Data Link satisfies every structural requirement: `obs_date` is a separate,
filterable primary-key column from `per_end_date`; EPS mean/median/high/low, standard deviation,
analyst count and revision up/down counts; 1979 onwards; 23,000+ **listed and delisted** North American
issuers; daily updates for live continuity; `ZACKS/MT` supplies `comp_cik` for a clean join to the SEC
identifiers this repository already uses. `ZACKS/SEH` adds revenue consensus revisions on the same key.

Nasdaq's own FAQ then states that the Zacks agreement "restricts deeper history to institutions only"
and that "full history may only be licensed to institutions/businesses and not to individuals" — a
Personal account can buy roughly three years. Three years cannot support a 2010–2017 development window,
a 2018–2021 validation window, and a 2022–2026 holdout.

Recommending a Business account to get past this would be recommending a false representation about the
use of the data. That is not a research decision this programme should make on its own initiative, and
it is not recommended.

**No purchase is recommended. Nothing should be bought.**

## 2. Why not FREE_DATA_IS_SUFFICIENT

- **Alpha Vantage `EARNINGS_ESTIMATES`** is free and is genuinely class B — the freeze test (T3) shows
  past-period rows retain a snapshot rather than recomputing. But the snapshot's anchor date is absent
  from the schema, there is exactly one snapshot per fiscal period taken at the end of the estimation
  window, and history begins 2017-06. Per the brief's own rule, a source starting in 2017 is not
  backtested; here it is worse, because we could not timestamp the observations even if it went back
  further.
- **EODHD `/calendar/trends`** is class C by its own documentation and returned HTTP 403 on the current
  token in any case.
- **Open Source Asset Pricing** is free and high quality, but its firm-level panel is keyed on CRSP
  `permno`, which we cannot legitimately map to tickers, so it cannot produce a tradable long-only
  portfolio on our EODHD price panel.

None of these supports the primary analyst-revision strategy.

## 3. The qualification: one free thing is worth doing before this branch closes

The audit turned up an asset that costs nothing and answers the question that should be answered
*before* any money is ever discussed: **is the analyst-revision mechanism still alive in the modern
sample at all?**

Chen & Zimmermann's Open Source Asset Pricing publishes monthly long-short portfolio returns for 212
predictors, including the exact family Phase 9B would have tested — `AnalystRevision` (FY1 consensus
month-over-month), `REV6`, `ChNAnalyst`, `ForecastDispersion`, `EarningsForecastDisparity`, `FEPS`,
`sfe`. Those return series need **no identifier mapping**, so the CRSP blocker does not apply.

Restricted to the development window (≤ 2017-12), they give a free, decisive prior:

- these are **decile long-short, CRSP-universe, costless** portfolios — an **upper bound** on what a
  long-only, top-N, Trading-212-costed retail implementation could capture;
- if the upper bound has already decayed to nothing by 2010–2017, then no data purchase at any price
  could rescue the long-only retail version, and the branch closes on evidence rather than on budget;
- if the upper bound is still clearly positive, the finding is "the mechanism may be alive but the data
  is licence-blocked", which is a materially different and more useful conclusion to hand the user.

This is cheap, honest, and it is the difference between "we could not afford to look" and "we looked as
far as the free evidence allows". It is specified as Stage 0 in `PHASE9B_DRAFT.md` and is **not
executed** — Phase 9A is an audit.

## 4. What the user would have to do to change the answer

None of these are recommended; they are recorded so the decision is informed.

| option | what it gets | cost | why it is not recommended |
| --- | --- | --- | --- |
| Free Nasdaq Data Link **Personal** account | See real ZEEH pricing; pull the free 30-ticker sample; run the T5 immutability test | USD 0 | Worth doing *only* to confirm the licence finding and run T5. It will not unlock deep history. |
| Nasdaq Data Link **Business** account | Possibly a price for full ZEEH history | unknown, quote-based | Requires representing the use as business/institutional. Not a technical workaround. |
| **Intrinio Enterprise** | Same Zacks data, business licence | USD 1,250/mo + feed fees | 25× the ceiling. |
| **Finnhub All-In-One** | 20+ years of estimates, PIT semantics unverified | USD 3,500/mo, annual | 70× the ceiling. |
| **Estimize / ExtractAlpha** | Free historical test files on request | USD 0 to trial | Contributor-selected cross-section from ~2011; a corroborating dataset at best, and requires a human to make the request. |

## 5. Consequences for the programme

- The analyst-revision family is **not rejected on evidence** — it is **blocked on data licensing**,
  which is a different and weaker kind of closure. It should be recorded that way, not as a dead
  mechanism. The Phase 7B note that "analyst revisions [are] blocked by data" is now upgraded from an
  inference to a verified, citable licence restriction.
- **No strategy cells are added.** The cumulative ledger stays at **490**. No hypothesis was tested.
- **No multiplicity burden is incurred**, because nothing was evaluated against returns.
- Validation 2018–2021 and holdout 2022-01..2026-08 remain **completely unopened**.
- The EODHD cancellation recommendation from Phase 7A is **unchanged and reinforced**: the calendar
  package that would have been the cheap route to this family is class C, and our token cannot reach it.

## 6. Exact next action

**Decision required from the user.** Three options, in the order this audit would rank them:

1. **Run Phase 9B Stage 0 only** (free, no purchase, no locked data): download the OSAP long-short
   return series for the analyst-revision signals, evaluate on ≤ 2017-12 only, and let the result decide
   whether this family is worth any further discussion. Recommended.
2. **Open a free Nasdaq Data Link Personal account** and report back what the ZEEH pricing page actually
   shows (a price with a history selector, or "Contact Sales"), plus how many years of history a Personal
   account is offered. This is the one fact this audit could not obtain without creating an account,
   which is outside what the agent will do. Optional, and it will not change the licence finding.
3. **Accept that the analyst-revision family is licence-blocked** and either name the next distinct
   mechanism or close the equity programme at "no qualifying strategy on obtainable data".

Nothing is purchased under any option. Locked data stays locked under all three.
