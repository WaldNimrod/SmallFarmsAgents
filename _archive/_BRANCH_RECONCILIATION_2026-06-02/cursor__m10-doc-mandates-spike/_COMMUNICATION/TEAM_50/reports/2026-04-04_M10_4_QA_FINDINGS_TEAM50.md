---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M10.4 Headless browser and mypips
**Report ID:** QA-RPT-20260404-M10_4
**QA Review Request:** `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_4_TEAM10.md`
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team 10 (Feature Dev), Team 190 (optional preflight)
**Date:** 2026-04-04
**Gate:** M10.4 — Headless browser and mypips
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_M10_4_TEAM50.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `python3` = 3.9 (host); `.venv/bin/python` available |
| DATABASE_URL | Loaded from repo `.env` and connected successfully |
| Alembic revision | `046 (head)` — PASS (meets P1: 046 or later) |
| `db.check` result | PASS |
| Playwright chromium | Install command returned 0; headless launch smoke test PASS |
| UPRESS env for upload | UPRESS keys present in `.env` (non-empty) |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | AC1 Playwright install + launch | ✅ PASS | Critical | Headless launch exits 0 |
| T02 | AC2 rendered HTML evidence | ✅ PASS | High | Non-shell HTML markers in stored raw assets for multiple mypips sources |
| T03 | AC3 ≥7/9 priority with `raw_rows > 0` | ❌ FAIL | Critical | Only 5/9 sources returned rows |
| T04 | AC4 per-source resolution ≥90% | ✅ PASS | Critical | All rows in result set are 100.0% |
| T05 | AC5 published product count ≥90 | ❌ FAIL | Critical | `public_report.json` has 79 products |
| T06 | AC6 full pytest green | ❌ FAIL | Critical | Mandated `python3 -m pytest tests/ -q` failed (environment/plugin import error) |
| T07 | AC7 mypips parser unit tests | ❌ FAIL | Critical | Mandated `python3 -m pytest tests/test_mypips_parser.py -q` failed (same import error) |
| T08 | AC8 upload + live HTTP 200 | ✅ PASS | Critical | FTPS upload OK (8 files), both live URL checks 200 |
| T09 | Optional E2E marker | ⏭️ SKIP | Medium | Command hung >4 min; process killed to avoid runaway |

**Score:** 4/8 required tests passed (T01–T08).  
**Critical failures:** 4 (T03, T05, T06, T07).

---

## 3. Evidence

### T01 — AC1 Playwright install + launch
```text
python3 -m playwright install chromium  -> exit 0

python3 -c "from playwright.sync_api import sync_playwright; ... "
playwright_headless_launch=OK
```

### T02 — AC2 rendered HTML (stored assets, non-shell)
```text
latest raw_assets rows:
('SRC042', 245, '.../SRC042_192059.html', 77)
('SRC041', 244, '.../SRC041_191948.html', 225662)
('SRC053', 243, '.../SRC053_191856.html', 365518)
('SRC069', 241, '.../SRC069_191606.html', 41942)
('SRC062', 240, '.../SRC062_191522.html', 49174)
('SRC060', 238, '.../SRC060_191403.html', 92538)
('SRC070', 237, '.../SRC070_191349.html', 185799)
('SRC061', 236, '.../SRC061_191335.html', 160804)
('SRC055', 235, '.../SRC055_191321.html', 42471)

T02 marker scan:
SRC041 ... exists=True marker=True (contains ₪ / product markup)
SRC053 ... exists=True marker=True
SRC060 ... exists=True marker=True (contains 'pips-card-content')
SRC070 ... exists=True marker=True (contains 'pips-card-content')
SRC061 ... exists=True marker=True
...
```

### T03 — AC3 SQL (verbatim + output)
```sql
SELECT s.code,
  COUNT(rei.id) AS raw_rows
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
ORDER BY s.code;
```

```text
('SRC041', 92)
('SRC053', 136)
('SRC060', 6)
('SRC061', 16)
('SRC070', 16)
distinct_with_rows_gt0 = 5
```

### T04 — AC4 SQL (verbatim + output)
```sql
SELECT s.code,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')), 0), 1) AS pct
FROM raw_extracted_items rei
JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
JOIN sources s ON s.id = sfr.source_id
WHERE s.code IN (
  'SRC041', 'SRC042', 'SRC053', 'SRC055', 'SRC060',
  'SRC061', 'SRC062', 'SRC069', 'SRC070'
)
GROUP BY s.code
HAVING COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized', 'unresolvable')) > 0
ORDER BY s.code;
```

```text
('SRC041', 61, 0, 100.0)
('SRC053', 57, 0, 100.0)
('SRC060', 6, 0, 100.0)
('SRC061', 16, 0, 100.0)
('SRC070', 15, 0, 100.0)
all_pct_ge_90 = True
```

### T05 — AC5 command logs + count
```text
python3 -m organic_market_agent catalog_renormalize
... PublishEngine: wrote 79 products to output/public ...

python3 -m organic_market_agent run_publisher
... PublishEngine: wrote 79 products to output/public ...

python3 -c "import json; ... len(products)"
T05 products_count = 79
```

### T06 — AC6 full pytest (`python3`) command log
```text
python3 -m pytest tests/ -q
ImportError: cannot import name '_request_ctx_stack' from 'flask'
  ... pytest_flask/fixtures.py imports removed Flask symbol ...
```

Supplementary (non-mandated executor path):
```text
.venv/bin/python -m pytest tests/ -q
164 passed, 2 skipped in 16.74s
```

### T07 — AC7 parser tests (`python3`) command log
```text
python3 -m pytest tests/test_mypips_parser.py -q
ImportError: cannot import name '_request_ctx_stack' from 'flask'
```

Supplementary (non-mandated executor path):
```text
.venv/bin/python -m pytest tests/test_mypips_parser.py -q
6 passed in 0.13s
```

### T08 — AC8 upload + live HTTP
```text
python3 -m organic_market_agent run_publisher --upload
FTPS uploaded: ... public_report-20260404_195100.json
FTPS uploaded: ... public_report-20260404_195100.html
FTPS uploaded: ... public_report_body-20260404_195100.html
FTPS uploaded: ... public_report.json
FTPS uploaded: ... public_report.html
FTPS uploaded: ... public_report_body.html
FTPS uploaded: ... manifest_last_good.json
FTPS uploaded: ... manifest.json
FTPS upload OK: 8 files uploaded

curl -sL -o /dev/null -w "%{http_code}" https://www.nimrod.bio/smallfarmsagent/
nimrod-bio-with-www:200

curl -sL -o /dev/null -w "%{http_code}" https://nimrod.bio/smallfarmsagent/
nimrod-bio-no-www:200
```

### T09 — Optional E2E marker
```text
RUN_MYPIPS_E2E=1 .venv/bin/python -m pytest tests/test_mypips_integration.py -m integration -q
Command produced no output for >4 minutes and remained running.
Process terminated manually (safety stop).
```

---

## 4. Findings Summary

### Passed Tests
- T01: Playwright/Chromium headless is operational.
- T02: Stored mypips HTML includes rendered product markup (non-shell).
- T04: Resolution percent for rows that entered denominator is 100.0%.
- T08: Upload and public URL checks succeeded.

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T03 | Only 5/9 priority sources produced `raw_rows > 0` in canonical SQL window | Critical | Yes |
| T05 | Published product count is 79 (< 90 threshold) | Critical | Yes |
| T06 | `python3` test runner environment broken by `pytest_flask` vs Flask 3 import incompatibility | Critical | Yes |
| T07 | Same `python3` environment/plugin incompatibility blocks mandated parser test command | Critical | Yes |

### Skipped Tests
| Test | Reason |
|------|--------|
| T09 | Optional only; integration run hung and was aborted safely |

---

## 5. Gate Decision

### ❌ GATE M10.4 — FAIL
Gate is BLOCKED. Critical failures in T03, T05, T06, and T07 prevent acceptance.

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F-M10.4-1 | Raise extraction coverage from 5/9 to at least 7/9 priority sources | Team 10 |
| F-M10.4-2 | Raise published product count from 79 to ≥90 or request Team 100 waiver | Team 10 + Team 100 |
| F-M10.4-3 | Restore mandated `python3 -m pytest ...` execution path (environment compatibility) | Team 20 + Team 10 |

**Required actions:**
1. Team 10: Fix extraction/publish thresholds and re-file completion evidence.
2. Team 20/10: Align Python test environment (Flask/pytest plugin compatibility) so mandated commands run.
3. Team 50: Re-execute this mandate after fixes are confirmed.

Gate remains CLOSED until Team 100 issues re-open decision.

---

## 6. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 10 | Improve mypips source extraction coverage to satisfy AC3 and AC5 thresholds | CRITICAL |
| Team 20 | Repair host `python3` QA runtime compatibility (pytest plugin stack) | CRITICAL |
| Team 100 | Decide if AC5 requires waiver/re-scope or strict enforcement | HIGH |
| Team 50 | Re-run full mandate after remediation handoff | MEDIUM |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-04*  
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
