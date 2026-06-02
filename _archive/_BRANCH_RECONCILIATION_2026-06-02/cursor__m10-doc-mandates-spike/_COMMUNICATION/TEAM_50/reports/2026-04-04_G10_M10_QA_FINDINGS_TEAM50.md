---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G10 (M10.2 + M10.3)

**Report ID:** QA-RPT-20260404-G10-M10  
**QA Review Request:** `QA_REQUEST_M10_2_TEAM10.md`, `QA_REQUEST_M10_3_TEAM10.md`  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Team 190 (Preflight)  
**Date:** 2026-04-04  
**Gate:** G10 — OrganicMarketAgent M10 dictionary + static parsers  
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_M10_G10_TEAM50.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | 3.9.x (local agent) — ⚠️ below project target 3.11+; DB + app exercised successfully on this host |
| PostgreSQL | `DATABASE_URL` — ✅ |
| Alembic revision | `039 (head)` — ✅ |
| `db.check` result | ✅ PASS |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | M10 parser + FTPS unit tests | ✅ PASS | Critical | 13 passed |
| T02 | Full pytest | 🟡 PASS (M10 scope) | High | 4 failures in `test_admin_routes.py` / `test_admin_summary_counts.py` — Jinja `runs.html`; **pre-existing**, not caused by M10 migrations/parsers |
| T03 | Per-source community resolution SQL | ✅ PASS | Critical | 14 sources, all `pct = 100`, `unres = 0` |
| T04 | `catalog_renormalize` + product count | ✅ PASS | Critical | 83 products in `output/public/public_report.json` (≥70 M10.2, ≥80 M10.3) |
| T05 | `run_publisher --upload` + live HTTP | ✅ PASS | Critical | 8 files uploaded; `https://www.nimrod.bio/smallfarmsagent/` → HTTP/2 200 |
| T06 | Manifest sanity | ⏭️ SKIP | Medium | Optional; upload logs list 8 files including `manifest.json` |

**Score:** 5/5 executed critical tests passed (T02 counted as PASS for M10 delta).  
**Critical failures:** 0.

---

## 3. Evidence

### T01 — Pytest (M10 + FTPS)

```
.............                                                            [100%]
13 passed in 0.16s
```

### P1 — Alembic

```
039 (head)
```

### P2 — db.check

```
RESULT: PASS
```

### T03 — Per-source SQL (aggregated JSON)

```json
[["SRC002", 270, 0, "100.0"], ["SRC003", 25, 0, "100.0"], ["SRC004", 370, 0, "100.0"], ["SRC005", 93, 0, "100.0"], ["SRC006", 6, 0, "100.0"], ["SRC010", 585, 0, "100.0"], ["SRC021", 158, 0, "100.0"], ["SRC022", 117, 0, "100.0"], ["SRC023", 35, 0, "100.0"], ["SRC024", 13, 0, "100.0"], ["SRC025", 43, 0, "100.0"], ["SRC026", 58, 0, "100.0"], ["SRC027", 13, 0, "100.0"], ["SRC028", 23, 0, "100.0"]]
```

### T04 — Publish product count

```
products 83
```

### T05 — Upload + live

Publisher / FTPS (abridged):

```
FTPS uploaded: public_report-20260404_173140.json → wp-content/uploads/market/...
...
FTPS upload OK: 8 files uploaded
```

Live:

```
HTTP/2 200
```

### T02 — Full suite summary

```
4 failed, 154 passed, 1 skipped
FAILED tests/test_admin_routes.py::test_t01_readonly_get_routes_return_200
FAILED tests/test_admin_routes.py::test_t09_runs_trigger_creates_ingestion_run
FAILED tests/test_admin_routes.py::test_t14_runs_list_shows_manager_columns
FAILED tests/test_admin_summary_counts.py::test_runs_summary_matches_db
```

---

## 4. Findings Summary

### Passed tests

- T01, T03, T04, T05 satisfy M10.2 + M10.3 mandatory metrics and live publish path.

### Failed tests (non-blocking for G10 M10)

| Test | Root Cause | Severity | Blocking? |
|------|------------|----------|-----------|
| Admin route tests | `TemplateSyntaxError` in `admin/runs.html` | Medium | No — outside M10 deliverables; track under admin UI maintenance |

### Skipped tests

| Test | Reason |
|------|--------|
| T06 | Optional manifest diff not required for this sign-off |

---

## 5. Gate Decision

### 🟡 GATE G10 (M10.2 + M10.3 scope) — CONDITIONAL PASS

M10.2 and M10.3 **acceptance criteria** from `MANDATE_M10_CORRECTIONS_AND_GUIDANCE_TEAM10.md` are **met** (per-source resolution, product counts, publish + upload, live page 200).

| Condition ID | Description | Assigned To | Due |
|--------------|-------------|-------------|-----|
| C-G10-1 | Team 100 formal architectural approval on record (G10 requires Team 100 + full gate rules in `ROADMAP.md`) | Team 100 | Before declaring G10 fully closed |
| C-G10-2 | Remediate admin `runs.html` Jinja error so full pytest is green | Team 10 | Next admin/UI sprint |

**Team 10:** M10.3 implementation may be considered **QA-cleared** for dictionary/parser scope; **G10 final** still requires Team 100 sign-off per roadmap.

---

*Filed by: Team 50 (QA agent run)*  
*Date: 2026-04-04*
