---
document_type: QA_FINDINGS_REPORT
version: "1.0"
scope: ops_parity
---

# QA Findings Report — Production publish path parity (post-M7 ops)

**Report ID:** QA-RPT-20260421-OPS-PARITY  
**QA Review Request:** `QA-REQ-20260421-OPS-PARITY` — [`2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md`](2026-04-21_QA_REVIEW_REQUEST_PRODUCTION_DATA_PARITY_TEAM10.md)  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature / Operations)  
**Date:** 2026-04-21  
**Scope:** Operational / regression verification — **not** a re-open of closed gates G1–G9; FTPS target vs WordPress shortcode, scheduler path, public HTTP vs FTP behaviour.

---

## 1. Environment verified (local / repo)

| Check | Result |
|-------|--------|
| Python | `3.11` (command: `python3.11 -m pytest`) — meets 3.11+ |
| `pytest tests/ -q` | **152 passed, 1 failed, 2 skipped** (see §2) — failure is **out of scope** for publish-path parity (`tests/test_admin_routes.py::test_t09_runs_trigger_creates_ingestion_run`) |
| `validate_aos.sh .` | **26 PASS / 9 SKIP / 0 FAIL** — L-GATE_BUILD exit criterion satisfied (request text cited 17/2; lean-kit version on this spoke reports different pass/skip counts; **0 FAIL** holds) |
| Production DB / wald / Alembic 031 | **Deferred to Team 10 ops evidence** — not re-run in this workspace; see [`../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md) and [`../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) |

---

## 2. Test results (request §3)

| ID | Test | Result | Notes |
|----|------|--------|-------|
| T01 | FTP vs local `manifest.json` / `public_report_body.html` after publish | **PASS (evidence-backed)** | Team 10: FTP `wp-content/uploads/market` matches host `output/public` (e.g. `artifact_version` `20260421_060007`, 34 products) — [sign-off §2026-04-21 check](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md) |
| T02 | HTTPS `curl` — `artifact_version`, `product_count`, `report_date` vs post-publish | **PASS with conditions** | If HTTPS lags FTP / host body or `Last-Modified`, classify as **HTTPS cache (CDN/ezCache)**, not FTPS failure — [sign-off](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md); owner: **uPress site cache purge** (not code) |
| T03 | WordPress themed page | **PASS (spot-check / prior evidence)** | Per runbook; Team 10 sign-off and Team 30 public UI notes; not re-executed here |
| T04 | Scheduler / FTPS path vs `UPRESS_UPLOAD_PATH` (no `sfa/` for new uploads) | **PASS (ops narrative)** | Aligned in checklist/runbook; wald not verified live in this session |
| T05 | DB sanity (no impossible dates) | **PASS** | [Sign-off: DB audit](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md) — no ≥2099 rows in scoped tables |
| T06 | Full `pytest` suite | **FAIL (1 test)** | `test_t09_runs_trigger_creates_ingestion_run` — IngestionRun count unchanged after POST `/runs/trigger` with patched pipeline; **does not** invalidate FTPS path parity; track under general QA / admin routes |

**Score (parity-focused):** T01–T05 as scoped in request — **PASS with conditions** on T02.  
**Suite health:** 1 non-blocking failure for this ops track (T06).

---

## 3. Evidence

### 3.1 `validate_aos.sh` (excerpt)

```
RESULT: 26 PASS / 9 SKIP / 0 FAIL
L-GATE_BUILD EXIT CRITERION: SATISFIED
```

### 3.2 `pytest` (excerpt)

```
1 failed, 152 passed, 2 skipped
FAILED tests/test_admin_routes.py::test_t09_runs_trigger_creates_ingestion_run
```

### 3.3 Parity and cache (authoritative)

See [`../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md`](../../TEAM_10/reports/2026-04-18_PRODUCTION_DATA_PARITY_SIGNOFF_TEAM10.md) (FTP match, optional verify/purge env vars, HTTPS cache behaviour).

---

## 4. Findings summary

**Passed (parity):** FTPS target `wp-content/uploads/market`, manifest alignment Team 10–FTP, documented guardrails, DB audit narrative.  
**Conditions (public read):** HTTPS may trail FTP until uPress/CDN cache refresh — not classified as upload-path failure.  
**Open (general QA):** `test_t09_runs_trigger_creates_ingestion_run` failure — out of band for M7/parity closure unless Team 100 broadens scope.

---

## 5. Ops decision (not a numbered G* gate)

### PASS (path + pipeline) — with open item on public HTTPS

- **PASS** — path parity, scheduler/UPRESS story, SRC017/ops as documented.  
- **Open item:** When HTTPS JSON lags verified FTP or host `output/public`, **purge uPress cache** (or use documented optional ezCache automation); do not change publish gates or index window in repo for this.

---

## 6. Required actions

| Team | Action | Priority |
|------|--------|----------|
| Owner / ops | If `curl` HTTPS is stale vs FTP, **uPress cache purge** | HIGH (when observed) |
| Team 10 | None blocking parity close-out from this report | — |
| Team 100 / QA | Optional: triage `test_t09` admin route test / fixture | LOW |

---

*Filed by: Team 50 (QA)*  
*Date: 2026-04-21*
