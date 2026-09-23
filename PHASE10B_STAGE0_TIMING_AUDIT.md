# PHASE 10B STAGE 0 — causal-timing audit of the OSAP `ShortInterest` predictor

Date: 2026-09-23. **Code and documentation only. The `ret` column was never loaded.** Only
`signalname`, `port`, `date`, `Nlong` and `Nshort` were read from the portfolio file, and only to prove
the leg orientation (§2). No return, no statistic, no backtest.

Evidence: `reports/phase10b/raw/` (7 files, `SHA256SUMS.txt`) — OSAP source files, the Nasdaq short
interest report key, Asquith-Pathak-Ritter (JFE 2005), and the publication-date calendar computation.

---

## Verdict

# OSAP_SHORTINTEREST_TIMING_CAUSAL_FAIL

**Stage 0 is not executed. No preregistration is written.**

The failure is confined to the pre-September-2007 regime, and it contaminates **20.5% of the MODERN
2005-2017 decision window** and **100% of the EARLY 1990-2004 window**. The RECENT 2010-2017 window
would pass. §6 sets out what that leaves open.

---

## 1. The chain, traced end to end

### A. Which short-interest observation becomes signal month *t*

`DataDownloads/CompustatShortInterest.py` pulls `comp.sec_shortint_legacy` (1973-2024) and
`comp.sec_shortint` (2006+), where Compustat's `shortint` is *Shares Held Short as of Settlement Date*
and `datadate` is that settlement date. The month key is assigned by one line:

```python
df["time_avail_m"] = df["datadate"].dt.to_period("M").dt.to_timestamp()
```

`time_avail_m` is therefore **the calendar month containing the settlement date**. No lag of any kind
is applied — despite the field's name, it is an *observation* month, not an availability month.

The monthly collapse then takes the first non-missing record per `gvkey`-month after sorting by
`datadate`:

```python
df = df.sort_values(["gvkey", "time_avail_m", "datadate"])
... .agg(shortint=("shortint", first_non_missing), ...)
```

so where a month contains both a mid-month and a month-end settlement (from September 2007 onward),
the **mid-month** observation wins. That matches SignalDoc's note — "We use the mid-month observation
to make sure data would be available in real time" — and is the conservative choice. Before September
2007 only the mid-month settlement existed, so the selection is unambiguous.

`Predictors/ShortInterest.py` then computes `shortint / shrout` on the `permno`-`time_avail_m` key and
writes `[permno, yyyymm, ShortInterest]`, where `yyyymm` is `time_avail_m` verbatim.

**A: signal month *t* carries the short interest settled on the 15th of month *t*** (or the preceding
business day).

### B. What `yyyymm` means for this predictor

The calendar month of the settlement date. Nothing more. It is not lagged, not an availability month,
and not a portfolio-formation month.

### C. When the portfolio is formed

`SignalDoc.csv` gives `Portfolio Period = 1`, so `rebmonths` covers all twelve months and the sort is
refreshed every month; `Start Month = 6` is inert at monthly frequency. `LS Quantile = 0.2` → quintiles.

### D. What the published return at month *m* is

`Portfolios/Code/01_PortfolioFunction.R`, the decisive block:

```r
signallag = setDT(signal)[ , .(permno, yyyymm, signal, port) ][
  , yyyymm := yyyymm + 1                      # relabel to the NEXT month
][ , yyyymm := if_else(yyyymm %% 100 == 13, yyyymm+100-12, yyyymm) ]

crspret = crspret %>% left_join(signallag %>% select(permno,yyyymm,signallag,port),
                                by = c('permno','yyyymm'))
```

and `11_ProcessCRSP.R` keys CRSP returns by their own return month:

```r
ret = 100*ret , date = as.Date(date) , yyyymm = year(date) * 100 + month(date)
```

So the signal from month *m−1* is relabelled to month *m* and joined onto the return **earned during
month *m***; the output `date` is the last trading day of month *m*. (This also re-confirms Phase 9B
Amendment 1 D1: `ret` is in **percent**.)

**D: the published return at date *m* is the contemporaneous month-*m* return, formed on the signal
whose `yyyymm` is *m−1*.**

### E. Earliest date the observation could have been public

The signal for month *m−1* is the short interest settled ≈ the 15th of month *m−1*. The return period
begins on the **1st of month *m***. The causal question is whether that settlement figure was public
within roughly 16 days of settlement — and the answer depends entirely on which regime you are in.

## 2. Leg orientation — proved from counts, and the brief's assumption is inverted

The brief (§3) and my own Phase 10A write-up both assumed that `Sign = −1` puts the long leg at
**port 01**. That is wrong, and the mechanical proof catches it.

`import_signal()` applies the sign **before** sorting:

```r
signal$signal = signal$signal*Sign
```

so the sort is on *signed* short interest. Port 05 is then the highest signed value = the **lowest raw
short interest**. And the long/short names are assigned by port number, never by sign:

```r
if (longportname[1]  == 'max'){ longportname  = max(port$port) }   # -> port 05
if (shortportname[1] == 'min'){ shortportname = min(port$port) }   # -> port 01
```

Verified structurally on all 539 pre-2018 months (counts only, `ret` untouched):

| test | result |
| --- | --- |
| `LS.Nlong == port05.Nlong` | **539 / 539 months** |
| `LS.Nshort == port01.Nlong` | **539 / 539 months** |
| `LS.Nlong == port01.Nlong` | 218 / 539 (coincidental equal bin counts) |

**LS = port 05 − port 01. Port 05 is the long leg and holds the LOWEST short interest; port 01 is the
short leg and holds the highest.** The economic reading in Phase 10A was right — long = low short
interest — but the port label was wrong. The Phase 9B convention (port 05 = long) is universal in OSAP;
`Sign` never reverses it. `PHASE10B_DRAFT.md`, `STATUS.md`, `PLAN.md` and the project memory have been
corrected.

## 3. The publication regimes — and why today's rule cannot be run backwards

### Regime 3: from May 2008 — FINRA consolidated, uniform schedule

FINRA Notice 08-13: effective **15 May 2008**, firms report short interest in "all NASDAQ, Amex, NYSE,
ARCA and OTC equity securities" through one system, and FINRA provides the combined data to the
exchanges "on one uniform date at the end of each short interest reporting cycle". Nasdaq's own report
key states the rule:

> "NASDAQ member firms are required to report their short positions as of settlement on the 15th of each
> month, or the preceding business day if the 15th is not a business day, and as of settlement on the
> last business day of the month. The reports must be filed by the second business day after the
> reporting settlement date. **FINRA compiles the short interest data and provides it for publication on
> the 8th business day after the reporting settlement date.**"

### Regime 2: September 2007 to May 2008 — fixed schedule introduced

FINRA Notice 07-24 moved reporting from monthly to twice monthly effective **September 2007** and, in
Attachment A, published specific dates — the first fixed publication calendar. Notice 08-13 then notes
that consolidation "extended publication timelines for Amex, NYSE, and ARCA securities compared to
previous individual exchange schedules", i.e. the venues were not on a common clock until 2008.

### Regime 1: before September 2007 — no required release date

This is the finding that decides the audit. Asquith, Pathak and Ritter (*Journal of Financial
Economics* 78, 2005, 243-276), describing exactly this era, verbatim:

> "The exchanges then release these data to the news services. **Press release dates vary from month to
> month since exchanges have no required release date. The data are sometimes published as early as the
> 19th, and sometimes as late as the first of the next month.** Nasdaq has traditionally released the
> information a few days later than the NYSE and Amex."

Three things follow, and each is fatal on its own:

1. Publication "sometimes as late as the first of the next month" means that in an unknown subset of
   months the observation became public **on or after the day the OSAP return period begins**.
2. Nasdaq — a large share of the CRSP cross-section — was systematically **later still**, so for those
   names publication could fall several days into the return month.
3. There was **no required release date**, so the per-month release dates cannot be reconstructed from
   any rule. They would have to be recovered from archived press releases, which is not feasible here.

SignalDoc's stated assumption — "available bi-weekly with a four day lag" — does not match any regime.
The reporting *deadline* is two business days; publication is eight business days in the modern regime
and unscheduled before it. The four-day figure is the weakest link in the chain, exactly as suspected.

## 4. What the modern rule would have implied, month by month

Computed with the XNYS trading calendar (`reports/phase10b/raw/shortinterest_8bd_publication_check_19902017.csv`):
settlement = the 15th or the preceding session; publication = the 8th session after settlement; return
period = the 1st of the following month.

| window | months | publication precedes the return month | minimum margin | median margin |
| --- | ---: | ---: | ---: | ---: |
| EARLY 1990-2004 | 180 | 180 | **1 day** | 5 days |
| MODERN 2005-2017 | 156 | 156 | **1 day** | 5 days |
| RECENT 2010-2017 | 96 | 96 | **1 day** | 5 days |

Two readings, and both matter:

- **Where the 8-business-day rule actually applies (from 2008), the timing is causal** — but by a
  median of five days and, every February, by a single day (settlement 15 Feb, publication 28 Feb,
  return period starts 1 Mar). A ninth business day, or a holiday convention that differs by one
  session, breaks February.
- **Applying that rule to 1990-2007 is precisely the error the brief warned against.** The table shows
  what the modern schedule *would* have implied; it is not evidence about what happened. In that era
  the exchanges had no required release date and published as late as the first of the next month.

## 5. Verdict against the brief's condition

> THE SHORT-INTEREST OBSERVATION MUST HAVE BEEN PUBLIC BEFORE THE RETURN PERIOD STARTS.

| window | regime | condition holds? |
| --- | --- | --- |
| EARLY 1990-01 .. 2004-12 (180 m) | no required release date | **NO** — violated in an unidentifiable subset |
| **MODERN 2005-01 .. 2017-12 (156 m)** | 2005-01..2007-08 unscheduled (**32 m, 20.5%**); 2007-09.. fixed | **NO for the first 32 months** |
| RECENT 2010-01 .. 2017-12 (96 m) | consolidated, 8 business days | **YES**, margin 1-9 days |

The decision window is MODERN. One fifth of it sits in a regime where the return period demonstrably
could begin before the signal was public, and the affected months cannot be identified and dropped
because no release-date record exists. Under the brief's rule this is

**OSAP_SHORTINTEREST_TIMING_CAUSAL_FAIL → STOP.**

This is classified FAIL rather than UNRESOLVED deliberately. UNRESOLVED would mean the mapping could
not be established; it was established. There is positive documentary evidence, from a *Journal of
Financial Economics* paper covering the era, that publication sometimes fell on or after the first day
of the return month. The unknown is the frequency, not the existence.

## 6. What this does and does not say

- It says **nothing** about whether short interest predicts returns. No return was read.
- It is **not** a claim that Chen and Zimmermann made an error. Their four-day-lag assumption is a
  documented modelling choice that is reasonable for the post-2008 sample and generous for the earlier
  one. This programme's causal bar is simply stricter than theirs.
- It **does** mean the published `ShortInterest` long-short series cannot be used as a clean external
  screen over 1990-2017 without inheriting a look-ahead channel of unknown size in the older half.

## 7. The one option that survives, not executed

A redesigned Stage 0 restricted to **2008-01 .. 2017-12** — entirely inside the consolidated
8-business-day regime, where the timing is verifiably causal — would be legitimate. It would cost:

- the EARLY window, so no decay comparison is possible;
- the MODERN decision window as currently frozen, replaced by a 120-month window;
- statistical power, and a new preregistration written from scratch rather than an amendment.

It would also still carry the February one-day margin and the residual risk noted in §8.

That is a decision for the user. It is **not** taken here, and no preregistration is written.

## 8. Residual risks, recorded for any future attempt

1. **Missing mid-month observations.** `first_non_missing` takes the first record in the month. If a
   month's mid-month settlement is absent but the month-end one is present (possible from September
   2007), the signal becomes a month-end observation published ~10 days *into* the return month — a
   direct look-ahead. The frequency is unmeasurable without the underlying Compustat file.
2. **Retroactive split adjustment.** Nasdaq's report key states that split adjustments "will
   automatically be reflected in **all historical data available on the website**". The published
   archive is restated, not immutable, so a historical level is not necessarily the number that was
   public at the time.
3. **February margin.** One day in the modern regime, as computed in §4.
4. **`shrout` alignment.** The denominator comes from `monthlyCRSP` at the same `time_avail_m`; CRSP
   shares outstanding are themselves subject to a reporting lag, and APR note that "CRSP tends to lag
   actual shares outstanding when checked against SEC filings". Second-order here, but it is another
   quantity dated by observation rather than availability.
