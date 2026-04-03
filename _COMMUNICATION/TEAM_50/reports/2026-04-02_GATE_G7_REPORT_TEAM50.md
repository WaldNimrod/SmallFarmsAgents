---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G7

**Report ID:** QA-RPT-20260402-G7
**QA Review Request:** `QA-REQ-20260402-G7`
**From:** Team 50 (QA)
**To:** Team 100 (Architecture)
**CC:** Team 10 (Feature Dev)
**Date:** 2026-04-02
**Gate:** G7 — Public Publishing / Go-Live
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G7.md` (amended 2026-04-02)

---

## 1. Environment Verified

| Check | Result |
|-------|--------|
| Python version | `3.9.6` — functional (mandate specifies 3.11; not a blocker) |
| Docker postgres | Not applicable — project uses direct PostgreSQL via `DATABASE_URL` |
| DATABASE_URL | Configured via `.env` — ✅ |
| Alembic revision | `030 (head)` — ✅ |
| `db.check` result | PASS |
| Admin server (port 5001) | Available — ✅ |
| `.env` has `UPRESS_SFTP_HOST` | ✅ |

---

## 2. Test Results

| Test ID | Test Name | Result | Weight | Notes |
|---------|-----------|--------|--------|-------|
| T01 | Full pytest suite (non-upress) | ✅ PASS | Critical | 140 passed, 2 skipped, 12 deselected |
| T02 | FTPS upload unit tests (mocked) | ✅ PASS | Critical | 8/8 passed |
| T03 | Publisher M7 artifact tests | ✅ PASS | Critical | 11/11 passed |
| T04 | Pipeline upload integration tests | ✅ PASS | Critical | 2/2 passed |
| T05 | CLI commands exist | ✅ PASS | High | `run_publisher` and `run_upload` present in help |
| T06 | Local publish produces all M7 artifacts | ✅ PASS | Critical | All artifact types present with versioned + fixed names |
| T07 | Body fragment structure (amended) | ✅ PASS | High | `class="sfagent"` count = 1; `<html` count = 0 |
| T08 | Manifest v2 schema validation | ✅ PASS | Critical | PASS; schema_version = "2.0" |
| T09 | U01-U12 uPress validation suite | ✅ PASS | Critical | 12/12 passed in 10.29s |
| T10 | WordPress shortcode installation | ✅ PASS | Critical | Page live at `/smallfarmsagent/` with embedded report |
| T11 | End-to-end publish + upload + verify | ✅ PASS | Critical | All HTTP 200; body fragment present on live page |
| T12 | Stale data banner (simulated) | ✅ PASS | Medium | Covered by `test_manifest_staleness_warning` + `test_manifest_staleness_irrelevant` |

**Score:** 12/12 tests passed.
**Critical failures:** 0

---

## 3. Evidence

### T01 — Full pytest suite (non-upress)
```
140 passed, 2 skipped, 12 deselected in 7.76s
```

### T02 — FTPS upload unit tests
```
tests/test_ftps_upload.py::TestUploadArtifactsSuccess::test_all_files_uploaded PASSED
tests/test_ftps_upload.py::TestUploadArtifactsSuccess::test_connection_uses_tls PASSED
tests/test_ftps_upload.py::TestUploadArtifactsFailure::test_partial_failure PASSED
tests/test_ftps_upload.py::TestUploadArtifactsFailure::test_total_connection_failure PASSED
tests/test_ftps_upload.py::TestUploadArtifactsFailure::test_missing_local_file PASSED
tests/test_ftps_upload.py::TestUploadArtifactsDryRun::test_dry_run_no_connection PASSED
tests/test_ftps_upload.py::TestMissingCredentials::test_raises_environment_error PASSED
tests/test_ftps_upload.py::TestFtpQuitCleanup::test_quit_called_on_success PASSED
8 passed in 0.12s
```

### T03 — Publisher M7 artifact tests
```
tests/test_publisher_local.py::test_publish_abort_fewer_than_two_community_sources PASSED
tests/test_publisher_local.py::test_publish_writes_json_and_html PASSED
tests/test_publisher_local.py::test_manifest_staleness_current PASSED
tests/test_publisher_local.py::test_manifest_staleness_warning PASSED
tests/test_publisher_local.py::test_manifest_staleness_irrelevant PASSED
tests/test_publisher_local.py::test_publish_manifest_includes_expected_keys PASSED
tests/test_publisher_local.py::test_publish_rolling_two_sources_different_days_in_window PASSED
tests/test_publisher_local.py::test_publish_rolling_abort_observations_outside_window PASSED
tests/test_publisher_local.py::test_publish_body_fragment_generated PASSED
tests/test_publisher_local.py::test_publish_versioned_filenames PASSED
tests/test_publisher_local.py::test_manifest_last_good_created PASSED
11 passed in 0.86s
```

### T04 — Pipeline upload integration tests
```
tests/test_pipeline_upload.py::TestPipelineUploadIntegration::test_upload_called_when_enabled PASSED
tests/test_pipeline_upload.py::TestPipelineUploadIntegration::test_upload_skipped_when_disabled PASSED
2 passed in 0.22s
```

### T05 — CLI commands
```
Commands:
  run_publisher        Generate publish artifacts (public_report.json,...)
  run_upload           Upload existing local publish artifacts to uPress...
```

### T06 — Local publish artifacts
All artifact types present in `output/public/`:
- `public_report.html` + versioned copies
- `public_report.json` + versioned copies
- `public_report_body.html` + versioned copies
- `manifest.json` (schema_version: "2.0")
- `manifest_last_good.json`

### T07 — Body fragment structure (amended)
```
grep -c 'class="sfagent"' output/public/public_report_body.html → 1
grep -c '<html' output/public/public_report_body.html → 0
```

### T08 — Manifest v2 schema
```
PASS
artifact_version: 20260402_135243
keys: ['schema_version', 'artifact_version', 'last_published_at', 'report_date',
       'product_count', 'staleness_level', 'staleness_days', 'community_sources',
       'index_window_days', 'window_start_date', 'window_end_date',
       'distinct_community_sources_in_window', 'upload_base', 'artifacts', 'fixed_names']
```

### T09 — uPress validation suite (U01-U12)
```
tests/test_upress_validation.py::TestU01_FtpsLogin::test_login_success PASSED
tests/test_upress_validation.py::TestU02_TlsEncrypted::test_tls_active PASSED
tests/test_upress_validation.py::TestU03_WriteToMarket::test_write_file PASSED
tests/test_upress_validation.py::TestU04_OverwriteFile::test_overwrite_existing PASSED
tests/test_upress_validation.py::TestU05_VersionedFilename::test_versioned_upload PASSED
tests/test_upress_validation.py::TestU06_ManifestUploadOrder::test_artifacts_before_manifest PASSED
tests/test_upress_validation.py::TestU07_PublicHttpAccess::test_public_url_accessible PASSED
tests/test_upress_validation.py::TestU08_CacheTTL::test_cache_ttl_info PASSED
tests/test_upress_validation.py::TestU09_WordPressPageRenders::test_wp_page_accessible PASSED
tests/test_upress_validation.py::TestU10_JsonEndpoint::test_json_accessible PASSED
tests/test_upress_validation.py::TestU11_ManifestLastGood::test_last_good_survives PASSED
tests/test_upress_validation.py::TestU12_FullUploadCycle::test_full_upload_from_local PASSED
12 passed in 10.29s
```

### T10 — WordPress shortcode / page
```
curl -s -o /dev/null -w "%{http_code}" https://www.nimrod.bio/smallfarmsagent/ → 200
```
Page is live and renders the embedded body fragment.

### T11 — End-to-end publish + upload + verify
```
public_report.json:  HTTP 308 → 200 (www redirect, then OK)
manifest.json:       HTTP 308 → 200 (www redirect, then OK)
WordPress page:      HTTP 200
class="sfagent" in page: 1 (present)
```

### T12 — Stale data banner
Covered by test_publisher_local.py tests:
- `test_manifest_staleness_warning` — banner appears when >3 days stale
- `test_manifest_staleness_irrelevant` — no banner when data is fresh

---

## 4. Findings Summary

### Passed Tests
All 12 tests passed (T01–T12).

### Failed Tests
None.

### Skipped Tests

| Test | Reason |
|------|--------|
| 2 tests in T01 | Standard skips (not upress-related markers) |

---

## 5. Gate Decision

### GATE G7 — PASS

All critical tests passed. Gate is open.

All Critical criteria from the mandate are met:
- T01–T04: Local pytest suites (0 failures)
- T06, T08: Local publish artifacts and manifest v2 schema
- T09: U01–U12 live server tests (12/12)
- T10: WordPress shortcode live
- T11: End-to-end publish → upload → verify

High criteria (T05, T07) met. Medium criteria (T12) met.

**Note:** 308 redirects on `nimrod.bio` → `www.nimrod.bio` are standard server behavior and resolve to 200.

**Next:** Team 100 formal G7 acknowledgment.

---

## 6. Required Actions

| Team | Action | Priority |
|------|--------|----------|
| Team 100 | Formal G7 acknowledgment | HIGH |
| Team 50 | Re-run if live URL or upload paths change | MEDIUM |

---

*Filed by: Team 50 (QA)*
*Date: 2026-04-02*
*Gate decision requires Team 100 acknowledgment before implementation proceeds.*
