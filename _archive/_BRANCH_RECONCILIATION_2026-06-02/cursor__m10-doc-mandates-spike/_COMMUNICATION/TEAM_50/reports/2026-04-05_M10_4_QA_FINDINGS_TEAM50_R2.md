---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M10.4 Headless browser and mypips (Round-2 Re-review)
**Report ID:** QA-RPT-20260405-M10_4-R2
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
| P1 migration status | `python3 -m alembic upgrade head` completed (no pending revisions) |
| Alembic revision | `python3 -m alembic current` → `055 (head)` |
| `db.check` result | `python3 -m organic_market_agent.db.check` → `RESULT: PASS` |
| Playwright chromium | `python3 -m playwright install chromium` exit 0; headless launch smoke test PASS |
| UPRESS env (raw `.env` keys) | `{'UPRESS_FTPS_HOST': False, 'UPRESS_FTPS_USER': False, 'UPRESS_FTPS_PASSWORD': False}` |
| Upload runtime check | `run_publisher --upload` succeeded with FTPS upload (8 files) |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | AC1 Playwright install + launch | ✅ PASS | Critical | Chromium install + headless launch exits 0 |
| T02 | AC2 rendered HTML evidence | ✅ PASS | High | Non-shell rendered markers exist in latest assets (e.g. SRC041/SRC053/SRC060/SRC061/SRC070) |
| T03 | AC3 ≥7/9 priority with `raw_rows > 0` | ❌ FAIL | Critical | After coordinated 9-source ingestion, still 5/9 |
| T04 | AC4 per-source resolution ≥90% | ✅ PASS | Critical | All rows in mandate `HAVING` output are >=90% (SRC061=96.8, others 100.0) |
| T05 | AC5 published product count ≥90 | ❌ FAIL | Critical | `public_report.json` products count = 74 |
| T06 | AC6 full pytest green | ✅ PASS | Critical | `167 passed, 4 skipped` |
| T07 | AC7 mypips parser unit tests | ✅ PASS | Critical | `9 passed` |
| T08 | AC8 upload + live HTTP 200 | ✅ PASS | Critical | FTPS upload OK (8 files), both live URLs = 200 |
| T09 | Optional E2E marker | ❌ FAIL | Medium | `3 failed`; SRC061/SRC060/SRC070 duplicate-skip then 0 rows |

**Score:** 6/8 required tests passed (T01–T08).  
**Critical failures:** 2 (T03, T05).

---

## 3. Evidence

### P1 — Migration / Alembic
```text
python3 -m alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

python3 -m alembic current
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
055 (head)
```

### P2 — DB health
```text
python3 -m organic_market_agent.db.check
...
RESULT: PASS
```

### Coordinated ingestion before T03/T05 (per updated request)
```text
for code in SRC041 SRC042 SRC053 SRC055 SRC060 SRC061 SRC062 SRC069 SRC070; do
  python3 -m organic_market_agent run_ingestion --run-type manual --source-code "$code" --normalize
done

Observed highlights:
- SRC042: wait_for timeout; fetched 50710 bytes; parser wrote 0 items (IngestionRun #1808)
- SRC055: wait_for timeout; fetched 49254 bytes; parser wrote 0 items (IngestionRun #1810)
- SRC062: wait_for timeout; fetched 55959 bytes; parser wrote 0 items (IngestionRun #1813)
- SRC069: wait_for timeout; fetched 49107 bytes; parser wrote 0 items (IngestionRun #1814)
- SRC041/SRC053/SRC060/SRC061/SRC070: duplicate-asset skip runs in this cycle
```

### T01 — AC1 Playwright install + launch
```text
python3 -m playwright install chromium
(exit 0)

python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); b.close(); p.stop(); print('playwright_headless_launch=OK')"
playwright_headless_launch=OK
```

### T02 — AC2 rendered HTML (latest raw assets post-ingestion)
```text
latest_html_assets:
SRC041 {'raw_asset_id': 264, 'file_exists': True, 'bytes_size': 215846, 'marker': True, 'marker_token': 'pips-card-content'}
SRC042 {'raw_asset_id': 290, 'file_exists': True, 'bytes_size': 50710, 'marker': False, 'marker_token': None}
SRC053 {'raw_asset_id': 266, 'file_exists': True, 'bytes_size': 328110, 'marker': True, 'marker_token': 'pips-card-content'}
SRC055 {'raw_asset_id': 291, 'file_exists': True, 'bytes_size': 49254, 'marker': False, 'marker_token': None}
SRC060 {'raw_asset_id': 268, 'file_exists': True, 'bytes_size': 189307, 'marker': True, 'marker_token': 'pips-card-content'}
SRC061 {'raw_asset_id': 269, 'file_exists': True, 'bytes_size': 196837, 'marker': True, 'marker_token': 'pips-card-content'}
SRC062 {'raw_asset_id': 292, 'file_exists': True, 'bytes_size': 55959, 'marker': False, 'marker_token': None}
SRC069 {'raw_asset_id': 293, 'file_exists': True, 'bytes_size': 49107, 'marker': False, 'marker_token': None}
SRC070 {'raw_asset_id': 286, 'file_exists': True, 'bytes_size': 353739, 'marker': True, 'marker_token': 'pips-card-content'}
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
('SRC070', 227)
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
('SRC060', 56, 0, Decimal('100.0'))
('SRC061', 61, 2, Decimal('96.8'))
('SRC070', 116, 0, Decimal('100.0'))
all_pct_ge_90 = True
```

### T05 — AC5 command logs + count
```text
export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent catalog_renormalize
...
PublishEngine: wrote 74 products to output/public

export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent run_publisher
...
PublishEngine: wrote 74 products to output/public

python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))"
74
```

### T06 — AC6 full pytest
```text
python3 -m pytest tests/ -q
...............s........................................................ [ 42%]
.....sss................................................................ [ 84%]
...........................                                              [100%]
167 passed, 4 skipped in 17.61s
```

### T07 — AC7 parser tests
```text
python3 -m pytest tests/test_mypips_parser.py -q
.........                                                                [100%]
9 passed in 0.17s
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
FFF
...
FAILED tests/test_mypips_integration.py::test_mypips_e2e_src061
FAILED tests/test_mypips_integration.py::test_mypips_e2e_src060
FAILED tests/test_mypips_integration.py::test_mypips_e2e_src070
...
Source SRC061: duplicate asset, skipping (IngestionRun #1845)
Source SRC060: duplicate asset, skipping (IngestionRun #1846)
Source SRC070: duplicate asset, skipping (IngestionRun #1847)
3 failed in 132.89s
```

---

## 4. Findings Summary

### Passed Tests
- T01: Playwright environment is operational.
- T02: Non-shell rendered HTML exists for multiple priority sources.
- T04: Per-source resolution in current `HAVING` result set is >=90%.
- T06: Full regression suite passes on mandated `python3` path.
- T07: Mypips parser unit tests pass.
- T08: Upload and live HTTP checks pass.

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T03 | After coordinated ingestion, only 5/9 priority sources have `raw_rows > 0` | Critical | Yes |
| T05 | Published products remain 74 (<90 threshold) | Critical | Yes |
| T09 (optional) | E2E still fails due duplicate-skip/0-row assertions on SRC061/SRC060/SRC070 | Medium | No |

### Skipped Tests
None.

---

## 5. Gate Decision

### ❌ GATE M10.4 — FAIL
Gate remains BLOCKED. Critical failures in T03 and T05 prevent acceptance.

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F-M10.4-R3-1 | Raise extraction coverage from 5/9 to at least 7/9 priority sources | Team 10 |
| F-M10.4-R3-2 | Raise published product count from 74 to >=90, or obtain explicit Team 100 waiver per mandate note | Team 10 + Team 100 |

**Required actions:**
1. Team 10: resolve shell-store extraction gap for SRC042/SRC055/SRC062/SRC069 (or approved alternate ingestion strategy) and re-run coordinated ingestion.
2. Team 10 + Team 100: decide and document strict AC5 compliance vs waiver path if <90 persists after successful ingestion.
3. Team 50: re-execute full mandate after next remediation handoff.

Gate remains CLOSED until Team 100 issues a re-open decision.

---

## 6. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 10 | Fix T03/T05 blockers and submit next remediation package | CRITICAL |
| Team 100 | Decide waiver/threshold policy for AC5 if needed and publish binding decision | HIGH |
| Team 50 | Re-run full QA mandate after next handoff | MEDIUM |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-05*  
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
