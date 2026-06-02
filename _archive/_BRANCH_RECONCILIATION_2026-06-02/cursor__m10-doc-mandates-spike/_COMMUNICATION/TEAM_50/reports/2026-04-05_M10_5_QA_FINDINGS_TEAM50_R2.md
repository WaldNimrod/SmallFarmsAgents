---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M10.5 CSA baskets & Teva Shuk (R2 Re-review)
**Report ID:** QA-RPT-20260405-M10_5-R2  
**QA Review Request:** `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_5_TEAM10.md`  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Team 190 (optional preflight)  
**Date:** 2026-04-05  
**Gate:** M10.5 — CSA baskets & Teva Shuk (SRC033–SRC036)  
**QA Mandate executed:** `_COMMUNICATION/TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md`  
**Previous baseline for comparison:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_M10_5_QA_FINDINGS_TEAM50.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `python3` = 3.9.6 |
| Migration sync | `python3 -m alembic upgrade head` completed |
| Alembic revision | `python3 -m alembic current` → `058 (head)` |
| `db.check` result | `python3 -m organic_market_agent.db.check` → `RESULT: PASS` |
| Playwright chromium | `python3 -m playwright install chromium` exit 0 |
| DATABASE_URL | Loaded from `.env`; SQL + ingestion executed successfully |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | AC1 CSA extraction coverage (SRC033–035) | ❌ FAIL | Critical | `csa_with_rows_gt0 = 1` (need >=2) |
| T02 | AC2 Teva organic-only extraction (SRC036) | ✅ PASS | Critical | `src036_rows=21`, organic=21, conventional=0 |
| T03 | AC3 Organic filter documented + extensible | ✅ PASS | High | Policy + active profile evidence captured (`sellio_organic_only=true`) |
| T04 | AC4 Resolution >=85% per new source | ❌ FAIL | Critical | SRC033=100%; SRC036 has 0 normalized observations and cumulative `pct=0.0` |
| T05 | AC5 Published product count >=90 | ❌ FAIL | Critical | `public_report.json` count = `76` |
| T06 | AC6 "חנויות" filter shows Teva data live | ❌ FAIL | Critical | No Teva/SRC036 evidence in local/live published JSON; SRC036 normalized obs = 0 |
| T07 | AC7 Full regression suite | ✅ PASS | Critical | `177 passed, 4 skipped` |
| T08 | AC8 New unit tests (CSA+Sellio) | ✅ PASS | High | `10 passed` |
| T09 | AC9 Live page updated | ✅ PASS | High | FTPS upload OK (8 files), live HTTP 200 for both URLs |

**Score:** 5/9 tests passed.  
**Critical failures:** 4 (T01, T04, T05, T06).

---

## 3. Evidence

### Preconditions
```text
python3 -m alembic upgrade head
INFO ... PostgresqlImpl ...

python3 -m alembic current
...
058 (head)

python3 -m organic_market_agent.db.check
...
RESULT: PASS
```

### Ingestion run (SRC033–SRC036)
```text
for code in SRC033 SRC034 SRC035 SRC036; do
  python3 -m organic_market_agent run_ingestion --run-type manual --source-code "$code" --normalize
done

SRC033: wrote 3 raw_extracted_items; normalizer resolved=3
SRC034: duplicate asset, skipping
SRC035: duplicate asset, skipping
SRC036: wrote 21 raw_extracted_items; normalizer resolved=0 unresolvable=0 scope_skipped=21
```

### T01 — AC1 (CSA >=2/3)
```text
('SRC033', 6)
('SRC034', 0)
('SRC035', 0)
csa_with_rows_gt0 = 1
```

### T02 — AC2 (SRC036 organic-only)
```text
src036_latest_run_id = 3031
src036_rows = 21
src036_organic_marker_rows = 21
src036_non_organic_marker_rows = 0
```

### T03 — AC3 (documented + extensible)
```text
Policy doc evidence:
_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md
Option A + C hybrid, extensible via selector_profile.

DB profile evidence:
SRC036_PROFILE (..., 'sellio', '{"wait_for":"span.main_price","goto_wait_until":"load","post_load_delay_ms":6000,"sellio_organic_only":true,"headless_scroll_passes":4,"headless_scroll_pause_ms":1500}')
SRC036_entry_url (..., 'https://www.teva-shuk.co.il/search?q=%D7%90%D7%95%D7%A8%D7%92%D7%A0%D7%99')
```

### T04 — AC4 (resolution >=85%)
```text
('SRC033', 6, 0, 0, Decimal('100.0'))
('SRC036', 0, 3, 0, Decimal('0.0'))

latest SRC036 run statuses:
src036_latest_run_id 3031
('ignored', 21)
```

### T05 — AC5 (published count)
```text
python3 -m organic_market_agent catalog_renormalize
... PublishEngine: wrote 76 products ...

python3 -m organic_market_agent run_publisher
... PublishEngine: wrote 76 products ...

python3 -c "import json; ... len(products)"
76
```

### T06 — AC6 (store filter + Teva visibility)
```text
normalized_observations by source:
('SRC033', 6)
('SRC034', 0)
('SRC035', 0)
('SRC036', 0)

local published JSON:
local_products_count 76
local_products_with_store_source_type 45
local_contains_teva_literal False
local_contains_src036_literal False

live published JSON:
live_products_count 76
live_products_with_store_source_type 45
live_contains_teva_literal False
live_contains_src036_literal False
```

### T07 — AC7 (full regression)
```text
python3 -m pytest tests/ -q
177 passed, 4 skipped in 16.68s
```

### T08 — AC8 (new tests)
```text
python3 -m pytest tests/test_csa_parsers.py tests/test_sellio_parser.py -q
..........                                                               [100%]
10 passed in 0.19s
```

### T09 — AC9 (live publish)
```text
python3 -m organic_market_agent run_publisher --upload
FTPS upload OK: 8 files uploaded

curl ... https://www.nimrod.bio/smallfarmsagent/ -> 200
curl ... https://nimrod.bio/smallfarmsagent/ -> 200
```

---

## 4. Findings Summary

### Passed Tests
- T02: AC2 now meets threshold and purity.
- T03: Strategy remains documented and extensible.
- T07: Full suite passes.
- T08: New parser tests pass (expanded to 10).
- T09: Live publish and availability checks pass.

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T01 | CSA coverage remains 1/3 (SRC034, SRC035 still 0 rows) | Critical | Yes |
| T04 | SRC036 has no normalized observations; cumulative resolution metric still fails | Critical | Yes |
| T05 | Published count remains below threshold (76 < 90) | Critical | Yes |
| T06 | No explicit Teva/SRC036 evidence in published live payload; store filter criterion unresolved | Critical | Yes |

### Skipped Tests
None.

---

## 5. Gate Decision

### ❌ GATE M10.5 — FAIL
Gate remains BLOCKED due unresolved critical failures in AC1, AC4, AC5, AC6.

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F-M10.5-R2-1 | Raise CSA extraction coverage from 1/3 to >=2/3 | Team 10 |
| F-M10.5-R2-2 | Resolve AC4 rule for SRC036 (zero normalized due ignored/scope policy) with implementable acceptance path | Team 10 + Team 100 |
| F-M10.5-R2-3 | Raise published product count from 76 to >=90 or issue explicit waiver | Team 10 + Team 100 |
| F-M10.5-R2-4 | Provide explicit Teva/SRC036 visibility evidence in live/published output for AC6 | Team 10 |

**Required actions:**
1. Team 10: remediate AC1/AC6 data-path issues and resubmit evidence package.
2. Team 100: issue binding interpretation/waiver policy for AC4+AC5 under retail packaged-scope behavior.
3. Team 50: execute next re-review after remediation + architecture ruling.

---

## 6. Improvement Delta vs Previous Round

| Metric | Previous (QA-RPT-20260405-M10_5) | Current (R2) | Delta |
|--------|-----------------------------------|--------------|-------|
| AC1 CSA sources with rows | 1/3 | 1/3 | No change |
| AC2 SRC036 organic rows | 12 (0 conventional) | 21 (0 conventional) | **+9 rows** |
| AC5 published products count | 74 | 76 | **+2** |
| AC7 full pytest | 176 passed, 4 skipped | 177 passed, 4 skipped | **+1 passing test** |
| AC8 new parser tests | 9 passed | 10 passed | **+1 test** |
| AC6 Teva/SRC036 explicit visibility | Not evidenced | Not evidenced | No change |

Verdict feedback: remediation improved extraction purity/volume for SRC036 and test coverage, but gate blockers remain on CSA coverage, resolution/publish thresholds, and live evidence of Teva contribution.

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-05*  
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
