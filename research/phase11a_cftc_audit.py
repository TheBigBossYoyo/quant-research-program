"""Phase 11A Stage 0 - CFTC Commitments of Traders metadata, schema and release-calendar audit.

METADATA ONLY. This module never reads a position, open-interest, percentage, change,
trader-count or concentration value from any CFTC file. Every data read goes through
read_metadata(), whose column whitelist admits only market identity and report-date
fields, and which raises if anything else comes back. No price, return or performance
series of any kind is read, requested or computed here.

Subcommands (run from research/ with PYTHONUTF8=1):
  python phase11a_cftc_audit.py schedules   # fetch archived CFTC release schedules (Wayback), parse
  python phase11a_cftc_audit.py inventory   # schema + report-date + contract-identity inventory
  python phase11a_cftc_audit.py releasemap  # map every report date to its documented release date
  python phase11a_cftc_audit.py all

Inputs:  data/raw/phase11a/cftc/*.zip (official CFTC historical compressed files, hashed)
Outputs: reports/phase11a/cftc_audit/  (small CSV/JSON; no position values)
Evidence: reports/phase11a/raw/cftc/   (official pages, archived schedules)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import re
import sys
import time
import warnings
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "phase11a" / "cftc"
EVID = ROOT / "reports" / "phase11a" / "raw" / "cftc"
WAYBACK = EVID / "wayback"
OUT = ROOT / "reports" / "phase11a" / "cftc_audit"

UA = {"User-Agent": "Mozilla/5.0 (quant research metadata audit)"}

# ---------------------------------------------------------------------------
# 1. Metadata firewall
# ---------------------------------------------------------------------------
METADATA_COLUMNS = {
    "legacy": [
        "Market and Exchange Names",
        "As of Date in Form YYMMDD",
        "As of Date in Form YYYY-MM-DD",
        "CFTC Contract Market Code",
        "CFTC Market Code in Initials",
        "CFTC Region Code",
        "CFTC Commodity Code",
    ],
    "disagg": [
        "Market_and_Exchange_Names",
        "As_of_Date_In_Form_YYMMDD",
        "Report_Date_as_YYYY-MM-DD",
        "CFTC_Contract_Market_Code",
        "CFTC_Market_Code",
        "CFTC_Region_Code",
        "CFTC_Commodity_Code",
    ],
}
# Any column whose normalised name contains one of these WORDS carries a position-derived value.
_FORBIDDEN_RE = re.compile(r"\b(positions?|open interest|pct|oi|traders?|change|conc|spreading|spread|long|short|net)\b")


def _normalise(col: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", col.lower()).strip()


def is_forbidden(col: str) -> bool:
    """True if a CFTC column name denotes a position-derived quantity (never read by this audit)."""
    return bool(_FORBIDDEN_RE.search(_normalise(col)))


def _check_whitelist() -> None:
    for schema, cols in METADATA_COLUMNS.items():
        for c in cols:
            if is_forbidden(c):
                raise AssertionError(f"whitelist column {c!r} ({schema}) looks position-derived")


_check_whitelist()

DATE_COL = {"legacy": "As of Date in Form YYYY-MM-DD", "disagg": "Report_Date_as_YYYY-MM-DD"}
CODE_COL = {"legacy": "CFTC Contract Market Code", "disagg": "CFTC_Contract_Market_Code"}
NAME_COL = {"legacy": "Market and Exchange Names", "disagg": "Market_and_Exchange_Names"}

FILES = {
    "legacy": ["deacot1986_2016.zip"] + [f"deacot{y}.zip" for y in range(2017, 2027)],
    "disagg": ["fut_disagg_txt_hist_2006_2016.zip"] + [f"fut_disagg_txt_{y}.zip" for y in range(2017, 2027)],
}


def _member(zpath: Path) -> tuple[zipfile.ZipFile, str]:
    z = zipfile.ZipFile(zpath)
    names = [n for n in z.namelist() if n.lower().endswith(".txt")]
    if len(names) != 1:
        raise ValueError(f"{zpath.name}: expected exactly one .txt member, got {names}")
    return z, names[0]


def read_header(zpath: Path) -> list[str]:
    z, n = _member(zpath)
    with z.open(n) as fh:
        line = fh.readline().decode("latin-1").strip()
    return [c.strip().strip('"').strip() for c in line.split(",")]


def read_metadata(zpath: Path, schema: str) -> pd.DataFrame:
    """Read ONLY whitelisted identity/date columns. Raises if anything else is returned."""
    want = METADATA_COLUMNS[schema]
    z, n = _member(zpath)
    with z.open(n) as fh:
        df = pd.read_csv(fh, usecols=lambda c: c.strip() in want, dtype=str,
                         encoding="latin-1", skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    extra = set(df.columns) - set(want)
    if extra:
        raise AssertionError(f"metadata firewall breached: {sorted(extra)}")
    missing = set(want) - set(df.columns)
    if missing:
        raise KeyError(f"{zpath.name}: whitelisted columns missing: {sorted(missing)}")
    for c in df.columns:
        df[c] = df[c].str.strip()
    df["report_date"] = pd.to_datetime(df[DATE_COL[schema]], errors="raise")
    return df


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 2. Contract identity targets (codes as published by CFTC; names verified from files)
# ---------------------------------------------------------------------------
TARGETS = {
    # code: (commodity, group)
    "088691": ("Gold (COMEX)", "precious"),
    "084691": ("Silver (COMEX)", "precious"),
    "076651": ("Platinum (NYMEX)", "precious"),
    "075651": ("Palladium (NYMEX)", "precious"),
    "085692": ("Copper grade #1 (COMEX)", "industrial"),
    "067651": ("WTI crude oil (NYMEX)", "energy"),
    "06765T": ("Brent crude last day (NYMEX)", "energy"),
    "023651": ("Natural gas Henry Hub (NYMEX)", "energy"),
    "022651": ("Heating oil / NY Harbor ULSD (NYMEX)", "energy"),
    "111659": ("RBOB gasoline (NYMEX)", "energy"),
    "001602": ("Wheat SRW (CBOT)", "agriculture"),
    "001612": ("Wheat HRW (KC / CBOT)", "agriculture"),
    "002602": ("Corn (CBOT)", "agriculture"),
    "005602": ("Soybeans (CBOT)", "agriculture"),
    "007601": ("Soybean oil (CBOT)", "agriculture"),
    "026603": ("Soybean meal (CBOT)", "agriculture"),
    "080732": ("Sugar No. 11 (ICE US)", "softs"),
    "083731": ("Coffee C (ICE US)", "softs"),
    "073732": ("Cocoa (ICE US)", "softs"),
    "033661": ("Cotton No. 2 (ICE US)", "softs"),
    "057642": ("Live cattle (CME)", "livestock"),
    "054642": ("Lean hogs (CME)", "livestock"),
    "061641": ("Feeder cattle (CME)", "livestock"),
}
# Predecessor codes worth checking for identity continuity (name search, not assumed).
NAME_PATTERNS = {
    "copper": r"COPPER",
    "gasoline": r"GASOLINE|UNLEADED",
    "heating_oil": r"HEATING OIL|ULSD|USLD",
    "brent": r"BRENT",
    "natural_gas_nymex": r"NATURAL GAS.*NEW YORK MERCANTILE|NAT GAS NYME|NATURAL GAS - NEW YORK",
    "aluminium": r"ALUMINUM|ALUMINIUM",
    "nickel_zinc_lead_tin": r"NICKEL|ZINC|\bLEAD\b|\bTIN\b",
}


def inventory() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, headers, frames = [], {}, {"legacy": [], "disagg": []}
    for schema, files in FILES.items():
        for f in files:
            p = RAW / f
            manifest.append({"schema": schema, "file": f, "bytes": p.stat().st_size, "sha256": sha256(p)})
            headers[f] = read_header(p)
            md = read_metadata(p, schema)
            md["source_file"] = f
            frames[schema].append(md)
    pd.DataFrame(manifest).to_csv(OUT / "cftc_file_manifest.csv", index=False)

    # schema stability: compare every header to the first of its schema
    schema_rows = []
    for schema, files in FILES.items():
        ref = headers[files[0]]
        for f in files:
            h = headers[f]
            schema_rows.append({"schema": schema, "file": f, "n_columns": len(h),
                                "identical_to_first": h == ref,
                                "added": ";".join(sorted(set(h) - set(ref))),
                                "removed": ";".join(sorted(set(ref) - set(h)))})
    pd.DataFrame(schema_rows).to_csv(OUT / "cftc_schema_stability.csv", index=False)
    with open(OUT / "cftc_headers.json", "w") as fh:
        json.dump({f: h for f, h in headers.items() if f in (FILES["legacy"][0], FILES["disagg"][0])}, fh, indent=1)

    result = {}
    for schema in ("legacy", "disagg"):
        md = pd.concat(frames[schema], ignore_index=True)
        dup = md.duplicated(subset=[CODE_COL[schema], "report_date"]).sum()
        dates = pd.Series(sorted(md["report_date"].unique()))
        cal = pd.DataFrame({"report_date": dates})
        cal["year"] = cal.report_date.dt.year
        cal["weekday"] = cal.report_date.dt.day_name()
        cal["gap_days"] = cal.report_date.diff().dt.days
        cal.to_csv(OUT / f"{schema}_report_dates.csv", index=False)
        per_year = (cal.groupby("year")
                    .agg(n_report_dates=("report_date", "size"),
                         n_tuesday=("weekday", lambda s: int((s == "Tuesday").sum())),
                         non_tuesday=("weekday", lambda s: ";".join(sorted(set(s) - {"Tuesday"}))),
                         min_gap=("gap_days", "min"), median_gap=("gap_days", "median"),
                         max_gap=("gap_days", "max"))
                    .reset_index())
        per_year.to_csv(OUT / f"{schema}_report_dates_per_year.csv", index=False)
        non_tue = cal[cal.weekday != "Tuesday"][["report_date", "weekday"]]
        non_tue.to_csv(OUT / f"{schema}_non_tuesday_report_dates.csv", index=False)

        # target contracts: coverage and identity
        rows = []
        for code, (commodity, group) in TARGETS.items():
            sub = md[md[CODE_COL[schema]] == code]
            if sub.empty:
                rows.append({"code": code, "commodity": commodity, "group": group, "present": False})
                continue
            d = sub.report_date.sort_values()
            gaps = d.diff().dt.days
            post2000 = d[d >= "2000-10-01"]
            g2 = post2000.diff().dt.days
            names = sub.groupby(NAME_COL[schema]).report_date.agg(["min", "max", "size"]).reset_index()
            rows.append({
                "code": code, "commodity": commodity, "group": group, "present": True,
                "first_report": d.iloc[0].date().isoformat(), "last_report": d.iloc[-1].date().isoformat(),
                "n_reports": int(len(d)), "dup_rows": int(sub.duplicated("report_date").sum()),
                "n_gaps_gt_7d_after_2000_10": int((g2 > 7).sum()),
                "max_gap_after_2000_10": float(g2.max()) if len(g2) > 1 else None,
                "n_names": int(len(names)),
                "names": " || ".join(f"{r[NAME_COL[schema]]} [{r['min'].date()}..{r['max'].date()}, n={r['size']}]"
                                      for _, r in names.sort_values("min").iterrows()),
            })
        tgt = pd.DataFrame(rows)
        tgt.to_csv(OUT / f"{schema}_target_contracts.csv", index=False)

        # name-pattern search for predecessor / missing codes
        pat_rows = []
        for key, pat in NAME_PATTERNS.items():
            hit = md[md[NAME_COL[schema]].str.contains(pat, case=False, regex=True)]
            for (code, name), g in hit.groupby([CODE_COL[schema], NAME_COL[schema]]):
                pat_rows.append({"pattern": key, "code": code, "name": name,
                                 "first": g.report_date.min().date().isoformat(),
                                 "last": g.report_date.max().date().isoformat(), "n": int(len(g))})
        pd.DataFrame(pat_rows).sort_values(["pattern", "code", "first"]).to_csv(
            OUT / f"{schema}_name_pattern_search.csv", index=False)

        result[schema] = {
            "rows": int(len(md)), "distinct_contract_codes": int(md[CODE_COL[schema]].nunique()),
            "first_report_date": dates.iloc[0].date().isoformat(),
            "last_report_date": dates.iloc[-1].date().isoformat(),
            "n_report_dates": int(len(dates)), "duplicate_code_date_rows": int(dup),
            "non_tuesday_report_dates": int(len(non_tue)),
        }
    with open(OUT / "cftc_inventory_summary.json", "w") as fh:
        json.dump(result, fh, indent=1)
    return result


# ---------------------------------------------------------------------------
# 3. Release schedules (official CFTC pages as archived by the Internet Archive)
# ---------------------------------------------------------------------------
SCHEDULE_URLS = [
    "cftc.gov/dea/deacotcalendar.htm",                                     # 2004-2009 era page
    "cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm",  # 2010+ page
]
MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}


def _get(url: str, **kw):
    import socket

    import requests
    import urllib3.util.connection as uc
    uc.allowed_gai_family = lambda: socket.AF_INET  # this host's IPv6 route to archive.org is unreachable
    last = None
    for attempt in range(5):
        try:
            return requests.get(url, headers=UA, timeout=120, **kw)
        except requests.RequestException as e:  # transient network failures are retried, then surfaced
            last = e
            time.sleep(5 * (attempt + 1))
    raise last


def _cdx(url: str) -> list[str]:
    r = _get("https://web.archive.org/cdx/search/cdx",
             params={"url": url, "output": "json", "fl": "timestamp",
                     "filter": "statuscode:200", "collapse": "timestamp:6"})
    rows = r.json()
    return [x[0] for x in rows[1:]]


def _thin(timestamps: list[str]) -> list[str]:
    """Keep the first capture per (year, part-of-year): Jan-Apr, May-Sep, Oct-Dec. The archive throttles
    hard; three captures a year are enough to read each year's tentative schedule and its revisions."""
    keep, seen = [], set()
    for ts in sorted(timestamps):
        m = int(ts[4:6])
        key = (ts[:4], 0 if m <= 4 else 1 if m <= 9 else 2)
        if key not in seen:
            seen.add(key)
            keep.append(ts)
    return keep


def fetch_schedules(thin: bool = True) -> list[Path]:
    WAYBACK.mkdir(parents=True, exist_ok=True)
    saved = []
    for url in SCHEDULE_URLS:
        tag = "deacotcalendar" if "deacot" in url else "ReleaseSchedule"
        stamps = _cdx(url)
        for ts in (_thin(stamps) if thin else stamps):
            p = WAYBACK / f"{ts}_{tag}.html"
            if not p.exists():
                try:
                    r = _get(f"https://web.archive.org/web/{ts}id_/http://www.{url}")
                except Exception as e:  # archive rate-limits by refusing connections; record and move on
                    print("fetch failed", ts, type(e).__name__)
                    time.sleep(20)
                    continue
                if r.status_code != 200:
                    print("skip", ts, r.status_code)
                    continue
                p.write_bytes(r.content)
                time.sleep(2.0)
            saved.append(p)
    return saved


def _page_text(raw: bytes) -> str:
    from bs4 import BeautifulSoup
    warnings.filterwarnings("ignore")
    s = BeautifulSoup(raw, "lxml")
    for x in s(["script", "style"]):
        x.decompose()
    return re.sub(r"\s+", " ", s.get_text(" ", strip=True))


OLD_RE = re.compile(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+"
                    r"(January|February|March|April|May|June|July|August|September|October|November|December)"
                    r"\.?\s+(\d{1,2}),?\s+(\d{4})\s*(\*?)")


def parse_schedule_text(text: str) -> list[tuple[dt.date, bool]]:
    """Return (release_date, delayed_flag) pairs found in a CFTC schedule page's text.

    Two layouts exist: the 2004-2009 page lists 'Friday January 5, 2007' strings; the 2010+
    page lists a year heading, month names and day numbers with '*' for holiday delays."""
    found: list[tuple[dt.date, bool]] = []
    for m in OLD_RE.finditer(text):
        found.append((dt.date(int(m.group(3)), MONTHS[m.group(1)], int(m.group(2))), m.group(4) == "*"))
    if found:
        return found
    # new layout: restrict to the schedule block
    i = text.find("tentative schedule")
    j = text.find("Delayed release date", i)
    if i < 0:
        return found
    block = text[i: j if j > 0 else len(text)]
    tokens = block.replace("*", " * ").split()
    year = month = None
    k = 0
    while k < len(tokens):
        t = tokens[k]
        if re.fullmatch(r"20\d\d", t) and k + 1 < len(tokens) and tokens[k + 1] in ("Dates", "Release"):
            year, month = int(t), None
        elif t in MONTHS:
            month = MONTHS[t]
        elif re.fullmatch(r"\d{1,2}", t) and year and month:
            star = k + 1 < len(tokens) and tokens[k + 1] == "*"
            try:
                found.append((dt.date(year, month, int(t)), star))
            except ValueError:
                pass
        k += 1
    return found


def schedules() -> pd.DataFrame:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for p in sorted(WAYBACK.glob("*_deacotcalendar.html")) + sorted(WAYBACK.glob("*_ReleaseSchedule.html")):
        text = _page_text(p.read_bytes())
        for d, star in parse_schedule_text(text):
            rows.append({"release_date": d.isoformat(), "delayed_flag": star, "capture": p.name})
    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("no schedule dates parsed")
    agg = (df.groupby("release_date")
           .agg(delayed_flag=("delayed_flag", "max"), n_captures=("capture", "nunique"),
                first_capture=("capture", "min"), last_capture=("capture", "max"))
           .reset_index())
    agg["weekday"] = pd.to_datetime(agg.release_date).dt.day_name()
    agg.to_csv(OUT / "cftc_release_schedule_parsed.csv", index=False)
    return agg


# ---------------------------------------------------------------------------
# 4. Documented irregular publications (transcribed from official CFTC sources; each row cited)
# ---------------------------------------------------------------------------
# report_date -> actual (or announced) publication date, when it departs from the tentative schedule.
# Sources: reports/phase11a/raw/cftc/cot_historical_special_announcements.txt (HSA) and the press
# releases saved beside it. Rows are added only from those documents.
OVERRIDES = [
    # 2025 lapse in appropriations (HSA 2025-12-09 table; first catch-up on Wednesday 2025-11-19)
    ("2025-09-30", "2025-11-19", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-10-07", "2025-11-21", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-10-14", "2025-11-25", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-10-21", "2025-12-02", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-10-28", "2025-12-05", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-11-04", "2025-12-09", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-11-10", "2025-12-10", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-11-18", "2025-12-12", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-11-25", "2025-12-15", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-12-02", "2025-12-17", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-12-09", "2025-12-19", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-12-16", "2025-12-23", "HSA 2025-12-09 shutdown catch-up"),
    ("2025-12-23", "2025-12-29", "HSA 2025-12-09 shutdown catch-up (return to normal schedule)"),
    # 2025 National Day of Mourning (HSA 2025-01-07)
    ("2025-01-07", "2025-01-13", "HSA 2025-01-07 day of mourning"),
    # 2023 ION cyber incident (HSA 2023-02-02..2023-03-21): report originally due -> issued
    ("2023-01-31", "2023-02-24", "HSA 2023-02-24 ION"),
    ("2023-02-07", "2023-03-03", "HSA 2023-03-03 ION"),
    ("2023-02-14", "2023-03-08", "HSA 2023-03-08 ION"),
    ("2023-02-21", "2023-03-10", "HSA 2023-03-10 ION"),
    ("2023-02-28", "2023-03-14", "HSA 2023-03-14 ION"),
    ("2023-03-07", "2023-03-16", "HSA 2023-03-16 ION"),
    ("2023-03-14", "2023-03-21", "HSA 2023-03-21 ION"),
    # 2021 new federal holiday (HSA 2021-06-17)
    ("2021-06-15", "2021-06-21", "HSA 2021-06-17 Juneteenth"),
    # 2020 extra federal holiday (HSA 2020-12-28)
    ("2020-12-21", "2020-12-28", "HSA 2020-12-28 Dec-24 holiday"),
    # 2015 premature incomplete release on 2015-07-03; complete report 2015-07-06 (HSA 2015-07-06)
    ("2015-06-30", "2015-07-06", "HSA 2015-07-06 complete report; incomplete early release 07-03 ignored"),
    # 2014 holiday (HSA 2014-12-19)
    ("2014-12-23", "2014-12-30", "HSA 2014-12-19 Dec 25-26 holidays"),
    # 2012 updated reports for 11/27 published 12/05 (HSA 2012-12-04/05): the complete version
    ("2012-11-27", "2012-12-05", "HSA 2012-12-05 updated reports (original 11/30 incomplete)"),
]
# Conservative UPPER BOUNDS where the official source gives a rolling rather than exact catch-up
# schedule. Using the latest date consistent with the source can only delay a signal, never advance it.
UPPER_BOUNDS = [
    # 2013 lapse (press release 6745-13, 2013-10-23): first delayed report (due 10/04) published 10/25;
    # "two more ... during the week of October 28"; "at least two more ... during the week of
    # November 4"; previously announced schedule resumed "by the November 8, 2013 release date".
    ("2013-10-01", "2013-10-25", "PR 6745-13: first catch-up report 2013-10-25 (exact)"),
    ("2013-10-08", "2013-11-01", "PR 6745-13: week of Oct 28 (upper bound Fri 11-01)"),
    ("2013-10-15", "2013-11-01", "PR 6745-13: week of Oct 28 (upper bound Fri 11-01)"),
    ("2013-10-22", "2013-11-08", "PR 6745-13: week of Nov 4 / back on schedule by 11-08 (upper bound)"),
    ("2013-10-29", "2013-11-08", "PR 6745-13: week of Nov 4 / back on schedule by 11-08 (upper bound)"),
]
# Shutdown episodes: any report date inside a window that is not covered by OVERRIDES or
# UPPER_BOUNDS is marked UNRESOLVED and must not be used by a future experiment.
SHUTDOWN_WINDOWS = [
    ("2013-10-01", "2013-11-05", "2013 lapse in appropriations (PR 6745-13)"),
    ("2018-12-24", "2019-03-05", "2018-19 lapse in appropriations (HSA 2018-12-22, 2019-01-30; PR 7864-19 rolling Tue/Fri catch-up)"),
    ("2025-09-30", "2025-12-23", "2025 lapse in appropriations (HSA 2025-11-18, 2025-12-09; PR 9138-25, 9147-25)"),
]


def map_releases(report_dates, schedule_dates, overrides=OVERRIDES, bounds=UPPER_BOUNDS,
                 shutdown_windows=SHUTDOWN_WINDOWS, max_sched_lag_days: int = 8) -> pd.DataFrame:
    """Map each CFTC report (as-of) date to the release date a causal backtest may assume.

    Precedence: exact documented override > documented conservative upper bound > shutdown window
    (UNRESOLVED) > first archived scheduled release strictly after the report date and within
    max_sched_lag_days > UNRESOLVED."""
    rel = pd.Series(sorted(pd.to_datetime(pd.Series(list(schedule_dates))).unique()))
    ov = {pd.Timestamp(a): (pd.Timestamp(b), src, "documented_override") for a, b, src in overrides}
    ov.update({pd.Timestamp(a): (pd.Timestamp(b), src, "documented_upper_bound") for a, b, src in bounds
               if pd.Timestamp(a) not in ov})
    rows = []
    for d in pd.to_datetime(pd.Series(list(report_dates))):
        nxt = rel[rel > d]
        sched_rel = nxt.iloc[0] if len(nxt) else pd.NaT
        in_shutdown = [lbl for a, b, lbl in shutdown_windows if pd.Timestamp(a) <= d <= pd.Timestamp(b)]
        if d in ov:
            actual, src, status = ov[d]
        elif in_shutdown:
            actual, src, status = pd.NaT, in_shutdown[0], "UNRESOLVED_shutdown"
        elif pd.notna(sched_rel) and (sched_rel - d).days <= max_sched_lag_days:
            actual, src, status = sched_rel, "archived tentative schedule", "scheduled"
        else:
            actual, src, status = pd.NaT, f"no archived schedule within {max_sched_lag_days} days", "UNRESOLVED_no_schedule"
        rows.append({"report_date": d.date(), "scheduled_release": sched_rel.date() if pd.notna(sched_rel) else None,
                     "release_used": actual.date() if pd.notna(actual) else None,
                     "lag_days": (actual - d).days if pd.notna(actual) else None,
                     "release_weekday": actual.day_name() if pd.notna(actual) else None,
                     "status": status, "source": src})
    return pd.DataFrame(rows)


def release_map(first_year: int = 2004) -> pd.DataFrame:
    sched = pd.read_csv(OUT / "cftc_release_schedule_parsed.csv", parse_dates=["release_date"])
    cal = pd.read_csv(OUT / "legacy_report_dates.csv", parse_dates=["report_date"])
    cal = cal[cal.report_date.dt.year >= first_year].copy()
    df = map_releases(cal.report_date, sched.release_date)
    df.to_csv(OUT / "legacy_report_to_release_map.csv", index=False)
    df["year"] = pd.to_datetime(df.report_date).dt.year
    by_year = (df.groupby("year").status.value_counts().unstack(fill_value=0))
    by_year.to_csv(OUT / "legacy_release_map_status_by_year.csv")
    summ = {
        "years": f"{first_year}-{cal.report_date.dt.year.max()}",
        "n_report_dates": int(len(df)),
        "status_counts": df.status.value_counts().to_dict(),
        "lag_days_counts": df.lag_days.value_counts(dropna=False).sort_index().astype(int).to_dict(),
        "release_weekday_counts": df.release_weekday.value_counts(dropna=False).to_dict(),
    }
    with open(OUT / "legacy_release_map_summary.json", "w") as fh:
        json.dump(summ, fh, indent=1, default=str)
    return df


# ---------------------------------------------------------------------------
# 5. Execution-timing helper (used by tests and by the Stage 0 document)
# ---------------------------------------------------------------------------
def first_session_after(release_date: dt.date, sessions: list[dt.date]) -> dt.date:
    """First European trading session strictly AFTER the US release date.

    CFTC releases at 15:30 ET; every candidate European ETC venue (LSE 16:30 UK, Xetra /
    Borsa Italiana / Euronext 17:30 CET) has closed by 12:30 ET even in the spring and autumn
    daylight-saving mismatch weeks, so the release day itself is never tradeable."""
    for s in sorted(sessions):
        if s > release_date:
            return s
    raise ValueError("no session after release")


# ---------------------------------------------------------------------------
# 6. Sign-convention worked example (FAKE numbers only)
# ---------------------------------------------------------------------------
def hedging_pressure_short_share(pmpu_long: float, pmpu_short: float) -> float:
    """Canonical hedger hedging pressure used by this audit: share of hedger positions that are SHORT.

    HP = short / (long + short), in [0, 1]. HIGH HP = hedgers predominantly short = hedgers
    are paying speculators to carry long risk = Keynes-Hicks normal-backwardation premium
    predicts a HIGHER expected return for a LONG futures position."""
    tot = pmpu_long + pmpu_short
    if tot <= 0:
        raise ValueError("no hedger positions")
    return pmpu_short / tot


def hedging_pressure_net_short_oi(hedger_long: float, hedger_short: float, open_interest: float) -> float:
    """Kang-Rouwenhorst-Tang (2020) eq. (1): HP = (hedger SHORT - hedger LONG) / open interest.

    POSITIVE = hedgers net short = long futures expected to earn the insurance premium.
    NOTE the opposite convention in Gorton-Hayashi-Rouwenhorst (2013), who use the commercial
    net LONG position / OI and therefore expect a NEGATIVE slope; mixing the two inverts the signal."""
    if open_interest <= 0:
        raise ValueError("open interest must be positive")
    return (hedger_short - hedger_long) / open_interest


def smoothed_hedging_pressure(weekly_hp: list[float], window: int = 52) -> float:
    """KRT (2020) smoothed hedging pressure: trailing mean of the last `window` WEEKLY HP values.

    Requires a complete window (no partial averages); the caller must pass only reports whose
    documented release precedes the decision time."""
    if len(weekly_hp) < window:
        raise ValueError(f"need {window} weekly observations, got {len(weekly_hp)}")
    tail = weekly_hp[-window:]
    return sum(tail) / window


def main(argv: list[str]) -> None:
    cmd = argv[1] if len(argv) > 1 else "all"
    if cmd in ("schedules", "all"):
        fetch_schedules()
        s = schedules()
        print("schedule dates parsed:", len(s), s.release_date.min(), s.release_date.max())
    if cmd in ("inventory", "all"):
        print(json.dumps(inventory(), indent=1))
    if cmd in ("releasemap", "all"):
        df = release_map()
        print(df.status.value_counts())


if __name__ == "__main__":
    main(sys.argv)
