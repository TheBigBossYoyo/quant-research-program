# L2 web-capture index (Phase 11C, modern OOS/real-time literature sub-audit)

No successful HTML/web-page snapshot was captured this pass — both attempted paywalled-abstract
WebFetch calls returned HTTP 403 (SSRN/ScienceDirect anti-bot blocking) or navigation-chrome-only
content (Oxford Academic), with no citable abstract text retrieved. Per the audit's hard rules, these
failed fetches are recorded here rather than silently discarded, and no fabricated abstract text was
written in their place.

| URL attempted | Result | File | Retrieval date |
|---|---|---|---|
| https://www.sciencedirect.com/science/article/abs/pii/S0927539825000726 (Rebonato & Nyholm 2025 abstract) | HTTP 403, no content | (none) | 2026-09-27 |
| https://academic.oup.com/rfs/article-abstract/34/6/2773/5902842 (Andreasen/Engsted/Moller/Sander 2021 abstract) | Fetched only page navigation/JEL-code chrome, no abstract text | (none) | 2026-09-27 |

All substantive evidence for this sub-audit instead came from (a) downloaded working-paper/preprint PDFs
saved to `reports/phase11c/raw/literature/` (git-ignored; catalogued in `literature/SOURCES.txt`), extracted
to text and quoted with line-location citations in `L2_modern_oos_literature.md`, and (b) WebSearch result
synopses, which are explicitly tagged `[ABSTRACT]`/`[UNVERIFIED]` wherever used in that report and are not
to be treated as confirmed full-text findings.
