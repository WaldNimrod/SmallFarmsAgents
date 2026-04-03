---
document_type: QA_MANDATE
version: "1.0"
---

# QA Mandate — Gate G7

**Mandate ID:** `QA-MANDATE-G7`  
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**CC:** Team 10 (Feature Dev), Team 20 (Infrastructure)  
**Date:** 2026-04-02  
**Milestone:** M7 — Public Publishing / Go-Live  
**Gate:** G7  

---

## Pre-conditions (verify before starting)

```bash
# 1. Alembic at 030
alembic current
# Expected: 030 (head)

# 2. upload_enabled column exists in scheduler_config
psql $DATABASE_URL -tAc "SELECT upload_enabled FROM scheduler_config WHERE id=1;"
# Expected: f (default false)

# 3. .env has UPRESS_* credentials
grep -c "UPRESS_SFTP_HOST" .env
# Expected: 1

# 4. Local publish artifacts exist
ls output/public/manifest.json
# Expected: file exists

# 5. Admin server running on port 5001
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/
# Expected: 200
```

---

## Test Suite

### T01 — Full pytest suite (local, non-upress)

```bash
pytest tests/ -q -m "not upress"
```

**Pass criterion:** 0 failures. Document any skips with rationale.  
**Weight:** Critical

---

### T02 — FTPS upload unit tests (mocked)

```bash
pytest tests/test_ftps_upload.py -v
```

**Pass criterion:** All 8 tests pass.  
**Weight:** Critical

---

### T03 — Publisher M7 artifact tests

```bash
pytest tests/test_publisher_local.py -v
```

**Pass criterion:** All 11 tests pass, including:
- `test_publish_body_fragment_generated` — body fragment without `<html>` wrapper
- `test_publish_versioned_filenames` — versioned + fixed-name copies exist
- `test_manifest_last_good_created` — second publish creates `manifest_last_good.json`
- `test_publish_manifest_includes_expected_keys` — manifest v2 schema with `schema_version`, `artifacts`, `fixed_names`, `upload_base`

**Weight:** Critical

---

### T04 — Pipeline upload integration tests (mocked)

```bash
pytest tests/test_pipeline_upload.py -v
```

**Pass criterion:** Both tests pass:
- `test_upload_called_when_enabled` — upload phase triggers when `upload_enabled=True`
- `test_upload_skipped_when_disabled` — upload phase skipped when `skip_upload=True`

**Weight:** Critical

---

### T05 — CLI commands exist

```bash
python -m organic_market_agent --help
```

**Pass criterion:** Output includes `run_upload` and `run_publisher` (with `--upload` option).

```bash
python -m organic_market_agent run_publisher --help
python -m organic_market_agent run_upload --help
```

**Pass criterion:** Help text shows expected options.  
**Weight:** High

---

### T06 — Local publish produces all M7 artifacts

```bash
python -m organic_market_agent run_publisher --output-dir output/public
ls -la output/public/
```

**Pass criterion:** Output contains:
- `public_report.json` and `public_report-<version>.json`
- `public_report.html` and `public_report-<version>.html`
- `public_report_body.html` and `public_report_body-<version>.html`
- `manifest.json` with `schema_version: "2.0"`

**Weight:** Critical

---

### T07 — Body fragment structure

> **Amendment (2026-04-02):** M8 CSS architecture refactor changed root class from
> `sfagent-market-report` to `sfagent`. Updated grep target accordingly.

```bash
grep -c 'class="sfagent"' output/public/public_report_body.html
grep -c "<html" output/public/public_report_body.html
```

**Pass criterion:**
- `class="sfagent"` count >= 1
- `<html` count = 0 (no full HTML wrapper)

**Weight:** High

---

### T08 — Manifest v2 schema validation

```bash
python3 -c "
import json
m = json.load(open('output/public/manifest.json'))
required = ['schema_version','artifact_version','staleness_days','artifacts','fixed_names','upload_base']
missing = [k for k in required if k not in m]
print('PASS' if not missing else f'FAIL: missing {missing}')
assert m['schema_version'] == '2.0'
print(f'artifact_version: {m[\"artifact_version\"]}')
"
```

**Pass criterion:** PASS, schema_version is "2.0".  
**Weight:** Critical

---

## Live Server Tests (require FTPS credentials)

### T09 — U01-U12 uPress validation suite

```bash
pytest tests/test_upress_validation.py -v -m upress
```

**Pass criterion:** All 12 tests pass:

| Test | Description |
|------|-------------|
| U01  | FTPS login with ReusedSessionFTP_TLS |
| U02  | TLS encrypted channel |
| U03  | Write to market/ directory |
| U04  | Overwrite existing file |
| U05  | Versioned filename upload |
| U06  | Artifacts before manifest upload order |
| U07  | Public HTTP access to uploaded file |
| U08  | Cache TTL measurement (informational) |
| U09  | WordPress page renders at /SmallFarmsAgent |
| U10  | JSON endpoint accessible and valid |
| U11  | manifest_last_good.json survives |
| U12  | Full unattended upload cycle |

**Weight:** Critical

---

### T10 — WordPress shortcode installation

```bash
python scripts/wp_shortcode_install.py
```

**Pass criterion:** Output shows `[OK]` for both shortcode install and page creation.  
**Weight:** Critical

---

### T11 — End-to-end: publish + upload + verify

```bash
# 1. Publish locally
python -m organic_market_agent run_publisher --output-dir output/public

# 2. Upload to uPress
python -m organic_market_agent run_upload --output-dir output/public

# 3. Verify public access
curl -s -o /dev/null -w "%{http_code}" https://nimrod.bio/wp-content/uploads/market/public_report.json
# Expected: 200

curl -s -o /dev/null -w "%{http_code}" https://nimrod.bio/wp-content/uploads/market/manifest.json
# Expected: 200

# 4. Verify WordPress page
curl -s -o /dev/null -w "%{http_code}" https://nimrod.bio/SmallFarmsAgent
# Expected: 200

# 5. Verify body fragment in page
curl -s https://nimrod.bio/SmallFarmsAgent | grep -c 'class="sfagent"'
# Expected: >= 1
```

> **Amendment (2026-04-02):** Updated grep target from `sfagent-market-report` to
> `class="sfagent"` per M8 CSS architecture refactor.

**Pass criterion:** All HTTP requests return 200, page contains market report.  
**Weight:** Critical

---

### T12 — Stale data banner (simulated)

After 3+ days without fresh data, the body fragment should include the stale warning banner.

**Verification:** Manual inspection of generated HTML when `reference_now` exceeds `generated_at` by >3 days. Already covered by `test_manifest_staleness_warning` and `test_manifest_staleness_irrelevant` in `test_publisher_local.py`.

**Weight:** Medium

---

## Gate Pass Criteria

| # | Criterion | Weight |
|---|-----------|--------|
| 1 | All T01-T04 local pytest suites pass (0 failures) | Critical |
| 2 | CLI commands `run_publisher --upload` and `run_upload` functional | High |
| 3 | Local publish produces all M7 artifacts (T06-T08) | Critical |
| 4 | U01-U12 live server tests pass (T09) | Critical |
| 5 | WordPress shortcode installed, page created (T10) | Critical |
| 6 | End-to-end publish→upload→verify works (T11) | Critical |
| 7 | manifest_last_good.json fallback works | High |
| 8 | Stale data banner appears after 3 days (T12) | Medium |

**Gate G7 PASS** requires all Critical criteria met. High criteria failures require documented remediation plan. Medium criteria failures are logged as known issues.

---

## Reporting

File your gate report at: `_COMMUNICATION/TEAM_50/reports/2026-04-XX_GATE_G7_REPORT_TEAM50.md`  
Follow the format from G6 report.
