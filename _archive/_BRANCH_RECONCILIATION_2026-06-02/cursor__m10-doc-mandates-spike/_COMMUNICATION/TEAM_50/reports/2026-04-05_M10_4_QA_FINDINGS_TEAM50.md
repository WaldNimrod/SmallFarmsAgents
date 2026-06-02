---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M10.4 Headless browser and mypips (Re-review)
**Report ID:** QA-RPT-20260405-M10_4-RERUN
**QA Review Request:** `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_4_TEAM10.md`
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team 10 (Feature Dev), Team 190 (optional preflight)
**Date:** 2026-04-05
**Gate:** M10.4 — Headless browser and mypips
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_M10_4_TEAM50.md` (v1.1)

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `python3` = 3.9.6 |
| Alembic revision | `051 (head)` — PASS (meets P1: 051+) |
| `db.check` result | PASS |
| Playwright chromium | `python3 -m playwright install chromium` exit 0; headless launch smoke test PASS |
| UPRESS env for upload | `.env` direct key probe returned false for `UPRESS_*`, but `run_publisher --upload` completed FTPS upload successfully (effective credentials available at runtime) |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | AC1 Playwright install + launch | ✅ PASS | Critical | Chromium install + headless launch exits 0 |
| T02 | AC2 rendered HTML evidence | ✅ PASS | High | Non-shell rendered markers exist for priority sources (e.g., SRC041/SRC053/SRC060/SRC061/SRC070) |
| T03 | AC3 ≥7/9 priority with `raw_rows > 0` | ❌ FAIL | Critical | Query returns only 5/9 sources with rows |
| T04 | AC4 per-source resolution ≥90% | ❌ FAIL | Critical | SRC060 = 82.8%, SRC070 = 79.3% |
| T05 | AC5 published product count ≥90 | ❌ FAIL | Critical | `public_report.json` products count = 76 |
| T06 | AC6 full pytest green | ✅ PASS | Critical | `167 passed, 4 skipped` |
| T07 | AC7 mypips parser unit tests | ✅ PASS | Critical | `9 passed` |
| T08 | AC8 upload + live HTTP 200 | ✅ PASS | Critical | FTPS upload OK (8 files), both live URL checks = 200 |
| T09 | Optional E2E marker | ❌ FAIL | Medium | `2 failed, 1 passed`; duplicate-asset ingestion produced 0 rows for SRC061/SRC060 |

**Score:** 5/8 required tests passed (T01–T08).  
**Critical failures:** 3 (T03, T04, T05).

Note on ingestion coordination before T03/T05: no full coordinated 9-source `run_ingestion` execution was run in this QA session; optional T09 executed targeted ingestion for SRC061/SRC060 and both runs were duplicate-skipped.

---

## 3. Evidence

### P1 — Alembic head
```text
python3 -m alembic current
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
051 (head)
```

### P2 — DB health
```text
python3 -m organic_market_agent.db.check
...
RESULT: PASS
```

### T01 — AC1 Playwright install + launch
```text
python3 -m playwright install chromium
(exit 0, no stderr)

python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('playwright_headless_launch=OK')"
playwright_headless_launch=OK
```

### T02 — AC2 rendered HTML (stored assets)
```text
latest_html_assets:
SRC041 {'raw_asset_id': 264, 'file_exists': True, 'bytes_size': 215846, 'marker': True, 'marker_token': 'pips-card-content'}
SRC042 {'raw_asset_id': 275, 'file_exists': True, 'bytes_size': 43929, 'marker': False, 'marker_token': None}
SRC053 {'raw_asset_id': 266, 'file_exists': True, 'bytes_size': 328110, 'marker': True, 'marker_token': 'pips-card-content'}
SRC055 {'raw_asset_id': 267, 'file_exists': True, 'bytes_size': 42473, 'marker': False, 'marker_token': None}
SRC060 {'raw_asset_id': 268, 'file_exists': True, 'bytes_size': 189307, 'marker': True, 'marker_token': 'pips-card-content'}
SRC061 {'raw_asset_id': 269, 'file_exists': True, 'bytes_size': 196837, 'marker': True, 'marker_token': 'pips-card-content'}
SRC062 {'raw_asset_id': 276, 'file_exists': True, 'bytes_size': 49174, 'marker': False, 'marker_token': None}
SRC069 {'raw_asset_id': 270, 'file_exists': True, 'bytes_size': 41944, 'marker': False, 'marker_token': None}
SRC070 {'raw_asset_id': 271, 'file_exists': True, 'bytes_size': 363269, 'marker': True, 'marker_token': 'pips-card-content'}
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
('SRC041', 187)
('SRC053', 270)
('SRC060', 75)
('SRC061', 72)
('SRC070', 122)
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
('SRC041', 124, 0, Decimal('100.0'))
('SRC053', 113, 0, Decimal('100.0'))
('SRC060', 53, 11, Decimal('82.8'))
('SRC061', 60, 3, Decimal('95.2'))
('SRC070', 65, 17, Decimal('79.3'))
all_pct_ge_90 = False
```

### T05 — AC5 command logs + count
```text
export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent catalog_renormalize
...
PublishEngine: wrote 76 products to output/public

export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent run_publisher
...
PublishEngine: wrote 76 products to output/public

python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))"
76
```

### T06 — AC6 full pytest
```text
python3 -m pytest tests/ -q
...............s........................................................ [ 42%]
.....sss................................................................ [ 84%]
...........................                                              [100%]
167 passed, 4 skipped in 16.99s
```

### T07 — AC7 parser tests
```text
python3 -m pytest tests/test_mypips_parser.py -q
.........                                                                [100%]
9 passed in 0.13s
```

### T08 — AC8 upload + live HTTP
```text
export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent run_publisher --upload
...
FTPS upload OK: 8 files uploaded

curl -sL -o /dev/null -w "%{http_code}\n" "https://www.nimrod.bio/smallfarmsagent/"
200

curl -sL -o /dev/null -w "%{http_code}\n" "https://nimrod.bio/smallfarmsagent/"
200
```

### T09 — Optional E2E marker
```text
RUN_MYPIPS_E2E=1 python3 -m pytest tests/test_mypips_integration.py -m integration -q
...
FAILED tests/test_mypips_integration.py::test_mypips_e2e_src061 - AssertionError: SRC061 expected raw rows after ingestion
FAILED tests/test_mypips_integration.py::test_mypips_e2e_src060 - AssertionError: SRC060 expected raw rows after ingestion
...
IngestionRun #1775: status=completed succeeded=0 failed=0 community_ok=0
IngestionRun #1776: status=completed succeeded=0 failed=0 community_ok=0
2 failed, 1 passed in 132.93s (0:02:12)
```

---

## 4. Findings Summary

### Passed Tests
- T01: Playwright/Chromium installed and headless launch succeeds.
- T02: Rendered/non-shell HTML evidence exists for multiple priority sources.
- T06: Full regression suite now passes under mandated `python3` path.
- T07: Mypips parser unit tests pass (`9/9`).
- T08: Upload and live endpoint checks are successful (HTTP 200).

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T03 | Only 5/9 priority codes have `raw_rows > 0` in mandate SQL window | Critical | Yes |
| T04 | Per-source resolution below threshold for SRC060 (82.8) and SRC070 (79.3) | Critical | Yes |
| T05 | Published products count is 76 (<90 threshold) | Critical | Yes |
| T09 (optional) | E2E ingestion for SRC061/SRC060 duplicate-skipped and produced 0 rows | Medium | No |

### Skipped Tests
None.

---

## 5. Gate Decision

### ❌ GATE M10.4 — FAIL
Gate remains BLOCKED. Critical failures in T03, T04, and T05 prevent acceptance.

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F-M10.4-R2-1 | Increase extraction coverage from 5/9 to at least 7/9 priority sources | Team 10 |
| F-M10.4-R2-2 | Raise per-source resolution to >=90% for all qualifying rows (currently SRC060/SRC070 fail) | Team 10 |
| F-M10.4-R2-3 | Raise published product count from 76 to >=90 (or obtain Team 100 waiver) | Team 10 + Team 100 |

**Required actions:**
1. Team 10: remediate extraction/resolution gaps for SRC060/SRC070 and missing priority-source rows.
2. Team 10 + Team 100: decide strict fix vs documented waiver path for AC5 if catalog reality remains below threshold.
3. Team 50: re-execute full mandate after remediation handoff.

Gate remains CLOSED until Team 100 issues a re-open decision.

---

## 6. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 10 | Fix T03/T04/T05 blockers and file renewed remediation handoff | CRITICAL |
| Team 100 | Decide waiver policy (if any) for AC5 and confirm acceptance thresholds | HIGH |
| Team 50 | Re-run mandate after next remediation package | MEDIUM |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-05*  
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
