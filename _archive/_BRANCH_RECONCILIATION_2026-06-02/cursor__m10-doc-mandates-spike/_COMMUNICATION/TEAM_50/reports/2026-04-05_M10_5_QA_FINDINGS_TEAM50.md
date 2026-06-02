---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — M10.5 CSA baskets & Teva Shuk (Sellio)
**Report ID:** QA-RPT-20260405-M10_5
**QA Review Request:** `_COMMUNICATION/TEAM_50/QA_REQUEST_M10_5_TEAM10.md`
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team 10 (Feature Dev), Team 190 (optional preflight)
**Date:** 2026-04-05
**Gate:** M10.5 — CSA baskets & Phase B retail (SRC033–SRC036)
**QA Mandate executed:** `_COMMUNICATION/TEAM_10/MANDATE_M10_5_CSA_RETAIL_TEAM10.md`

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `python3` = 3.9.6 |
| Alembic revision | `python3 -m alembic current` → `056 (head)` |
| Migration sync | `python3 -m alembic upgrade head` completed (no pending revisions) |
| `db.check` result | `python3 -m organic_market_agent.db.check` → `RESULT: PASS` |
| Playwright chromium | `python3 -m playwright install chromium` exit 0 |
| DATABASE_URL | Loaded from `.env` and used successfully for SQL + ingestion |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | AC1 CSA extraction coverage (SRC033–035) | ❌ FAIL | Critical | `csa_with_rows_gt0 = 1` (need >=2) |
| T02 | AC2 Teva organic-only extraction (SRC036) | ❌ FAIL | Critical | `12` organic-marked rows, `0` conventional (purity OK, threshold >=20 not met) |
| T03 | AC3 Organic filter documented + extensible | ✅ PASS | High | Documented Option A+C hybrid + `sellio_organic_only` in active `selector_profile` |
| T04 | AC4 Resolution >=85% per new source | ❌ FAIL | Critical | SRC033 `100.0`; SRC036 `0.0` (3 unresolvable, 0 normalized) |
| T05 | AC5 Published product count >=90 | ❌ FAIL | Critical | `public_report.json` count = `74` |
| T06 | AC6 "חנויות" filter shows Teva Shuk live | ❌ FAIL | Critical | Filter button exists, but no Teva/SRC036 evidence in live report and no normalized observations for SRC036 |
| T07 | AC7 Full regression suite | ✅ PASS | Critical | `176 passed, 4 skipped` |
| T08 | AC8 New unit tests (CSA+Sellio) | ✅ PASS | High | `9 passed` (`tests/test_csa_parsers.py` + `tests/test_sellio_parser.py`) |
| T09 | AC9 Live page updated | ✅ PASS | High | Upload succeeded (8 files), live HTTP codes 200 |

**Score:** 4/9 tests passed.  
**Critical failures:** 5 (T01, T02, T04, T05, T06).

---

## 3. Evidence

### Preconditions — migration and health
```text
python3 -m alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.

python3 -m alembic current
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
056 (head)

python3 -m organic_market_agent.db.check
...
RESULT: PASS
```

### Coordinated ingestion run (SRC033–SRC036)
```text
for code in SRC033 SRC034 SRC035 SRC036; do
  python3 -m organic_market_agent run_ingestion --run-type manual --source-code "$code" --normalize
done

SRC033: ParserEngine wrote 3 raw_extracted_items; Normalizer resolved=3
SRC034: ParserEngine wrote 0 raw_extracted_items
SRC035: ParserEngine wrote 0 raw_extracted_items (policy §4.5 path noted by parser)
SRC036: ParserEngine wrote 12 raw_extracted_items; Normalizer resolved=0 unresolvable=3 scope_skipped=9
```

### T01 — AC1 (CSA >=2/3 producing data)
```text
SELECT s.code, COUNT(rei.id) AS raw_rows
FROM sources s
LEFT JOIN source_fetch_runs sfr ON sfr.source_id = s.id
LEFT JOIN raw_extracted_items rei ON rei.source_fetch_run_id = sfr.id
WHERE s.code IN ('SRC033','SRC034','SRC035')
GROUP BY s.code
ORDER BY s.code;

('SRC033', 3)
('SRC034', 0)
('SRC035', 0)
csa_with_rows_gt0 = 1
```

### T02 — AC2 (SRC036 organic-only threshold)
```text
src036_latest_run_id = 2923
src036_rows = 12
src036_organic_marker_rows = 12
src036_non_organic_marker_rows = 0
```

Sample names from latest SRC036 run:
```text
פסטה כוסמין פוזילי אורגני – השדה
נודלס אורז מלא ואצות וואקמה ללא גלוטן אורגני – השדה
קוואקר עבה אורגני ללא גלוטן
קינואה רויאל אורגנית
חומוס אורגני
...
```

### T03 — AC3 (documented/extensible strategy)
```text
_COMMUNICATION/TEAM_10/reports/2026-03-30_M10_5_CSA_ANALYSIS_POLICY_TEAM10.md
line 76: "Option A + C hybrid ... documented as extensible ... via selector_profile"

DB profile:
code= SRC036
platform_family= sellio
selector_profile= {"wait_for":"span.main_price","goto_wait_until":"load","post_load_delay_ms":6000,"sellio_organic_only":true}

CSA payload evidence (SRC033 latest raw_payload_json):
{"parser":"csa_basket","csa_site":"havat_shorashim","csa_context":{...}}
```

### T04 — AC4 (resolution >=85%)
```text
SELECT s.code,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') AS norm,
  COUNT(*) FILTER (WHERE rei.extraction_status = 'unresolvable') AS unres,
  ROUND(100.0 * COUNT(*) FILTER (WHERE rei.extraction_status = 'normalized') /
    NULLIF(COUNT(*) FILTER (WHERE rei.extraction_status IN ('normalized','unresolvable')),0), 1) AS pct
...
('SRC033', 3, 0, Decimal('100.0'))
('SRC036', 0, 3, Decimal('0.0'))
```

### T05 — AC5 (published products count)
```text
export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent catalog_renormalize
... PublishEngine: wrote 76 products ...

export $(grep -v '^#' .env | xargs) 2>/dev/null || true; python3 -m organic_market_agent run_publisher
... PublishEngine: wrote 76 products ...

python3 -c "import json; d=json.load(open('output/public/public_report.json')); print(len(d.get('products',[])))"
74
```

### T06 — AC6 ("חנויות" filter + Teva visibility)
```text
Local UI artifact:
output/public/public_report_body.html: <button data-filter="store">🏪 חנויות</button>

Source configuration:
('SRC036', 'store', 'direct_price', 'farm_shop', True, 'active')

Normalized observations by source:
('SRC033', 3)
NO SRC036 normalized_observations

Live report probe:
live_products_count 76
live_products_with_store_source_type 45
contains_teva_literal False
contains_src036_literal False
```

### T07 — AC7 (full regression)
```text
python3 -m pytest tests/ -q
...
176 passed, 4 skipped in 17.27s
```

### T08 — AC8 (new parser tests)
```text
python3 -m pytest tests/test_csa_parsers.py tests/test_sellio_parser.py -q
.........                                                                [100%]
9 passed in 0.13s
```

### T09 — AC9 (live update)
```text
python3 -m organic_market_agent run_publisher --upload
FTPS upload OK: 8 files uploaded

curl -sL -o /dev/null -w "%{http_code}\n" "https://www.nimrod.bio/smallfarmsagent/"
200
curl -sL -o /dev/null -w "%{http_code}\n" "https://nimrod.bio/smallfarmsagent/"
200
```

---

## 4. Findings Summary

### Passed Tests
- T03: Organic filter strategy documented and profile-configurable.
- T07: Full regression suite is green.
- T08: New CSA/Sellio unit tests pass.
- T09: Upload and live HTTP checks pass.

### Failed Tests
| Test | Root Cause | Severity | Blocking? |
|------|-----------|----------|-----------|
| T01 | CSA extraction currently produced data for only 1/3 sources (SRC033 only) | Critical | Yes |
| T02 | Teva Shuk organic extraction count is 12, below AC2 threshold >=20 | Critical | Yes |
| T04 | SRC036 resolution is 0% (0 normalized, 3 unresolvable) | Critical | Yes |
| T05 | Published product count remains 74 (<90) | Critical | Yes |
| T06 | Store filter exists, but Teva/SRC036 data is not evidenced in live output | Critical | Yes |

### Skipped Tests
None.

---

## 5. Gate Decision

### ❌ GATE M10.5 — FAIL
Gate is BLOCKED due critical failures in AC1, AC2, AC4, AC5, AC6.

| Failure ID | Description | Assigned To |
|-----------|-------------|-------------|
| F-M10.5-1 | Raise CSA extraction coverage from 1/3 to >=2/3 (SRC034 and/or SRC035) | Team 10 |
| F-M10.5-2 | Raise SRC036 organic extraction from 12 to >=20 while keeping 0 conventional | Team 10 |
| F-M10.5-3 | Fix SRC036 normalization quality to >=85% | Team 10 |
| F-M10.5-4 | Raise published products from 74 to >=90 or receive explicit Team 100 waiver for AC5 | Team 10 + Team 100 |
| F-M10.5-5 | Ensure Teva Shuk data is actually visible via "חנויות" flow on live output | Team 10 |

**Required actions:**
1. Team 10: deliver remediation for SRC034/035 extraction and SRC036 extraction+normalization pipeline.
2. Team 100: issue explicit policy on AC2/AC5 threshold waivers (if requested) before next re-QA.
3. Team 50: re-run full M10.5 QA after remediation package is filed.

Gate remains CLOSED until Team 100 issues a re-open decision.

---

## 6. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 10 | Fix AC1/AC2/AC4/AC6 blockers and re-submit completion evidence | CRITICAL |
| Team 100 | Clarify waiver policy for AC2 and AC5 if thresholds remain unattainable in current scope | HIGH |
| Team 50 | Re-execute full QA after remediation handoff | MEDIUM |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-05*  
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
