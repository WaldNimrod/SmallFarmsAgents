---
document_type: QA_REVIEW_REQUEST
version: "1.0"
---

# QA Review Request — Production publish path parity and public static consistency

**Request ID:** QA-REQ-20260421-OPS-PARITY  
**From:** Team 10 (Feature / Operations)  
**To:** Team 50 (QA)  
**Date:** 2026-04-21  
**Scope:** Post-M7 operational fix — not a re-open of a closed numbered gate (G1–G9); **operational / regression verification** of FTPS target directory vs WordPress shortcode, scheduler upload flag, and observed public-HTTP vs FTP parity.  
**Priority:** HIGH  

**Context:** [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md), [`documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md`](../../documentation/05-admin-and-operations/WORDPRESS_PUBLIC_PUBLISH_RUNBOOK.md), Team 10 sign-off note [`../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md).

---

## 1. What was completed (evidence in repo / server)

| Area | Summary |
|------|---------|
| **Config (waldhomeserver)** | `UPRESS_PUBLIC_BASE=https://www.nimrod.bio`, `UPRESS_UPLOAD_PATH=wp-content/uploads/market` (aligned with WordPress `uploads/.../market/public_report_body.html`). |
| **Code** | [`organic_market_agent/publisher/ftps_upload.py`](../../organic_market_agent/publisher/ftps_upload.py) — optional public manifest verify (`UPRESS_VERIFY_PUBLIC_MANIFEST`), optional ezCache purge after upload (`UPRESS_EZCACHE_PURGE_AFTER_UPLOAD` + WP Application Password env vars in [`organic_market_agent/utils/config.py`](../../organic_market_agent/utils/config.py)). |
| **Data migration** | Alembic `031` — SRC017 (Pricez) deactivated; production DB was aligned (see prior ops). |
| **Ops** | Legacy duplicate market files removed from FTP `sfa/`; FTPS now targets `wp-content/uploads/market/`. |
| **Docs** | Checklist, runbook, [`.env.example`](../../.env.example), `CHANGELOG.md` updated. |

---

## 2. Pre-conditions (for your independent re-check)

Execute or spot-check as applicable on the **current** `main` and **waldhomeserver** (or use Nimrod-staged access):

- [ ] `alembic current` on production DB **031 (head)** (or document if intentionally behind pending `git pull`).
- [ ] `pytest` on a clean checkout: `python3.11 -m pytest tests/ -q` — expect all passing except known skips (per project state).
- [ ] `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect **17 PASS / 2 SKIP / 0 FAIL** before any AOS-level gate language is used in reporting.
- [ ] On **wald**, `scheduler_config`: `upload_enabled=true`, `is_enabled=true`, SRC017 inactive (sources + `source_fetch_profiles`).

---

## 3. QA test plan (suggested)

1. **FTP vs local:** `manifest.json` and `public_report_body.html` under FTP `wp-content/uploads/market/` **byte- or hash-match** the pipeline host’s `output/public/` after a successful `run_publisher --upload` (or last daily run).
2. **HTTPS (nimrod.bio):** `curl` [`https://www.nimrod.bio/wp-content/uploads/market/manifest.json`](https://www.nimrod.bio/wp-content/uploads/market/manifest.json) and [`public_report.json`](https://www.nimrod.bio/wp-content/uploads/market/public_report.json) — `artifact_version`, `product_count`, `report_date` **match** post-publish expectations; **if stale** vs FTP, classify as **CDN/ezCache** (not FTPS failure) and record whether purging the site cache resolves.
3. **WordPress page:** Themed page (e.g. [`/smallfarmsagent/`](https://www.nimrod.bio/smallfarmsagent/)) — table renders, metadata line, RTL/mobile spot-check.
4. **Scheduler log:** `sfa-scheduler.log` (or equivalent) shows FTPS to path consistent with `UPRESS_UPLOAD_PATH` in `.env` (no `sfa/` for new uploads).
5. **DB sanity:** No impossible dates in `normalized_observations` / `daily_aggregates` (e.g. year 2099) — or **PASS** with “0 rows” if audit was already run.

---

## 4. Known issues (non-blocking for filing)

| Issue | Impact | How to classify |
|--------|--------|-----------------|
| Public HTTPS can lag behind FTP for `manifest.json` after upload (CDN / ezCache) | **MEDIUM** (operator confusion) | If FTP matches `output/public` but HTTPS is stale, **do not** fail the FTPS path fix; file as **“HTTPS cache”**; recommend uPress purge or `UPRESS_EZCACHE_PURGE_AFTER_UPLOAD` with Application Password. |
| REST `POST .../ezcache/v1/cache` may return **403** from some client networks | **LOW** (automation) | Document; manual uPress panel purge is fallback. |

If none: **None**.

---

## 5. Request to Team 50

Please run the **suggested test plan (§3)** and file findings using the canonical template:

- Template: [`_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`](../TEMPLATES/QA_FINDINGS_REPORT.md)  
- Save as: `_COMMUNICATION/TEAM_50/reports/2026-04-21_ProductionParity_QA_FINDINGS_TEAM50.md` (or next available dated filename you use).

**Pass criteria (proposed):**  
- **PASS — path parity & pipeline:** FTPS → `wp-content/uploads/market`, local manifest matches FTP after publish, scheduler and SRC017 per spec.  
- **PASS with conditions — public read:** If HTTPS lags, **PASS (path + data)** with **open item** “purge CDN or enable automated ezCache purge on pipeline host” until `curl` matches.

---

*Issued by: Team 10*  
*Date: 2026-04-21*
