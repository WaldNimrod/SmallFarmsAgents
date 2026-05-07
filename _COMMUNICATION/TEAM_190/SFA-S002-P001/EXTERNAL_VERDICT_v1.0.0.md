# EXTERNAL_VERDICT — SFA-S002-P001 Phase 1 — team_190 — v1.0.0

**Date:** 2026-05-07  
**Author:** team_190  
**WP:** SFA-S002-P001-WP005  
**Gate:** L-GATE_VALIDATE (external constitutional)  
**Engine:** Cursor Composer (non-Opus; Iron Rule #1 satisfied)  
**Type:** EXTERNAL_VERDICT  
**Artifact path (canonical MANIFEST reference):** `_COMMUNICATION/team_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md`  
**Filesystem path (this repo):** `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md`

---

## Mandatory Identity Header

| Field | Value |
|-------|-------|
| **phase_owner** | team_190 |
| **correction_cycle** | n/a (initial external L-GATE_VALIDATE, not a revalidation package) |
| **scope** | SFA-S002-P001 Phase 1 — WP003, WP004, WP006, WP007 (WP001/WP002 explicitly Phase 2 per [`MANIFEST.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/MANIFEST.md)) |
| **bundle** | [`_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/) |

---

## §0 Verdict box

| Field | Value |
|-------|-------|
| **VERDICT** | **PASS_WITH_FINDINGS** |
| **WP / gate / round** | SFA-S002-P001-WP005 / L-GATE_VALIDATE / v1.0.0 |
| **One-line next step** | Team 100 shall wire **WP REST as primary** in [`organic_market_agent/scheduler/pipeline.py`](../../../organic_market_agent/scheduler/pipeline.py) and [`organic_market_agent/admin/routes/runs.py`](../../../organic_market_agent/admin/routes/runs.py) (or document an explicit ops-only upload path), reconcile [`_aos/roadmap.yaml`](../../../_aos/roadmap.yaml) WP004 status, and clear hub DB sync per ADR034 when online. |

---

## 1. Summary

Phase 1 removed the **F-01** public regression (stale index): production evidence in the bundle and in-repo ops reports support **fresh manifest** and **WP REST–based upload** as exercised in production. **Unit tests** for WP004/WP006/WP007 pass locally (81 tests). **`validate_aos.sh`** reports **29 PASS / 17 SKIP / 0 FAIL** (2026-05-07 rerun).

Independent review found **implementation and governance gaps** that do **not** re-open F-01 for the evidenced production path but **must** be tracked: automated pipeline and Admin “upload now” still call **FTPS-only** [`upload_artifacts`](../../../organic_market_agent/publisher/ftps_upload.py); [`run_publisher --upload`](../../../organic_market_agent/__main__.py) correctly prefers WP REST via [`_do_upload`](../../../organic_market_agent/__main__.py). **Roadmap** lists WP004 as `ELIGIBLE` despite delivered mobile parity work described in the bundle.

**LOD500:** No discrete `LOD500_*` files exist under `_aos/work_packages/S002/` for these WPs; **effective as-built** is documented by [`PROGRAM_SUMMARY.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/PROGRAM_SUMMARY.md), [`MANIFEST.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/MANIFEST.md), team_99 Pass-2 report, and risk register — acceptable for **L0 Phase 1** with findings below.

---

## 2. Constitutional criteria (Team 190 L-GATE_VALIDATE)

| # | Criterion | Result |
|---|-----------|--------|
| 1 | L-GATE_SPEC acceptance criteria met for delivered Phase 1 WPs | **PASS_WITH_FINDINGS** — WP004 AC-05/06 deferred per [`RISK_REGISTER.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/RISK_REGISTER.md); WP006 superseded per roadmap; scheduler/admin upload path gap vs WP007 wording (see §4) |
| 2 | `validate_aos.sh` — 0 FAIL | **PASS** — 29 PASS / 17 SKIP / 0 FAIL (§5); Check 25 `PENDING_DB_SYNC.yaml` present (ADR034 debt) |
| 3 | No new Iron Rule violations in scope reviewed | **PASS** |
| 4 | Governance artifacts consistent with delivery + ADR034 | **PASS_WITH_FINDINGS** — WP004 `status`/`current_lean_gate` in [`roadmap.yaml`](../../../_aos/roadmap.yaml) stale vs bundle; WP003 `status: BUILDING` vs notes “COMPLETE” |
| 5 | LOD500 as-built | **PASS_WITH_FINDINGS** — no formal LOD500 files; substituted by Phase 1 bundle + ops narratives (§1) |

---

## 3. AC matrix by WP (evidence-backed)

### WP003 — Server scraping verification

| AC | Lod ref | Result | evidence-by-path |
|----|---------|--------|------------------|
| AC-01..07 | [`LOD400_spec.md`](../../../_aos/work_packages/S002/SFA-S002-P001-WP003/LOD400_spec.md) §3 | **PASS** (with carried findings) | [`_COMMUNICATION/team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_PASS2_v1.0.0.md`](../../team_99/SFA-S002-P001-WP003/VERIFICATION_REPORT_PASS2_v1.0.0.md) — team_99 **PASS_WITH_FINDINGS** (CHP partial, historical errors documented); AC-04/05/06 **PASS**; [`_COMMUNICATION/TEAM_60/reports/2026-05-06_SCRAPING_VERIFICATION_PASS2_TEAM60.md`](../../TEAM_60/reports/2026-05-06_SCRAPING_VERIFICATION_PASS2_TEAM60.md) cross-file |

**route_recommendation:** Accept for Phase 1; continue CHP monitoring under normal ops.

### WP004 — Mobile UI parity

| AC | Result | evidence-by-path |
|----|--------|------------------|
| AC-01–04, AC-07 | **PASS** | [`tests/test_responsive_html.py`](../../../tests/test_responsive_html.py) — **47** tests; templates/CSS per [`LOD400_spec.md`](../../../_aos/work_packages/S002/SFA-S002-P001-WP004/LOD400_spec.md) §2 |
| AC-05 Lighthouse | **DEFERRED** (acknowledged) | [`RISK_REGISTER.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/RISK_REGISTER.md) R-01; [`WP004/QA_SCAFFOLD.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/WP004/QA_SCAFFOLD.md) |
| AC-06 cross-device smoke | **DEFERRED** (acknowledged) | R-01 |

**route_recommendation:** Team 50 runs live Lighthouse + device smoke when access available; not a Phase 1 constitutional blocker given explicit deferral and structural test coverage.

### WP006 — FTPS remediation

| AC | Result | evidence-by-path |
|----|--------|------------------|
| AC-01–03 (code + tests) | **PASS** | [`organic_market_agent/publisher/ftps_upload.py`](../../../organic_market_agent/publisher/ftps_upload.py) `ReusedSessionFTP_TLS`; [`tests/test_ftps_upload.py`](../../../tests/test_ftps_upload.py) — **14** tests |
| AC-04–07 (production FTPS fix) | **N/A / SUPERSEDED** | Roadmap `SUPERSEDED_BY_WP007`; network diagnosis in bundle [`PROGRAM_SUMMARY.md`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/PROGRAM_SUMMARY.md) |

### WP007 — HTTP upload (WP REST)

| AC | Result | evidence-by-path |
|----|--------|------------------|
| AC-01, AC-04–07 | **PASS** | [`organic_market_agent/publisher/wp_upload.py`](../../../organic_market_agent/publisher/wp_upload.py); [`_COMMUNICATION/TEAM_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md`](../../TEAM_10/SFA-S002-P001-WP007/SHORTCODE_INTEGRATION_DECISION.md); [`documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md`](../../../documentation/05-admin-and-operations/PUBLISH_CHECKLIST.md) §4 |
| AC-02 pipeline integration | **PARTIAL** | **Primary:** [`organic_market_agent/__main__.py`](../../../organic_market_agent/__main__.py) `_do_upload` → `upload_all_artifacts`. **Gap:** [`organic_market_agent/scheduler/pipeline.py`](../../../organic_market_agent/scheduler/pipeline.py) L285–338 still calls **FTPS-only** `upload_artifacts`; [`admin/routes/runs.py`](../../../organic_market_agent/admin/routes/runs.py) `runs_upload_now` still FTPS-only |
| AC-03 failure-mode / fallback | **PASS** (CLI path) | `_do_upload` + `UPRESS_FALLBACK_FTPS` in [`__main__.py`](../../../organic_market_agent/__main__.py) |
| AC-05 tests | **PASS** | [`tests/test_wp_upload.py`](../../../tests/test_wp_upload.py) — **20** tests |

**route_recommendation:** Treat **F-190-01** (below) as **follow-up before assuming cron/UI upload matches WP007** unless Team 99 documents an alternative production entrypoint.

### WP005 — Bundle (Phase 1)

| Item | Result | Notes |
|------|--------|------|
| Bundle usability | **PASS** | MANIFEST + per-WP folders + rollback + validator prompt |
| Original WP005 AC-02 (Lighthouse JSON, verbatim `SCRAPING_VERIFICATION.md` at bundle root, full WP001/WP002 folders) | **WAIVED / ADAPTED** | Phase 1 rescope per MANIFEST §Out of scope + roadmap `rescope_note`; [`LIGHTHOUSE_REPORT.json`](../../TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/) absent |
| WP005 AC-07 DB sync | **OPEN** | `PENDING_DB_SYNC.yaml` flagged by validator Check 25 |

---

## 4. Findings (non-blocking unless noted)

| id | Severity | Finding | route_recommendation |
|----|----------|---------|---------------------|
| F-190-01 | **MEDIUM** | Scheduler [`pipeline.py`](../../../organic_market_agent/scheduler/pipeline.py) and Admin [`runs_upload_now`](../../../organic_market_agent/admin/routes/runs.py) invoke **FTPS-only** upload; **`config.upress_configured()`** still keys off FTPS env only ([`config.py`](../../../organic_market_agent/utils/config.py)). WP007 production path evidenced via CLI/WP REST does not extend to these entrypoints in-repo. | Refactor upload phase to shared helper matching `_do_upload` (WP REST primary, gated FTPS fallback) or document and enforce ops procedure; add regression test or smoke for scheduler path if feasible. |
| F-190-02 | LOW | [`_aos/roadmap.yaml`](../../../_aos/roadmap.yaml): **WP004** `status: ELIGIBLE`, `current_lean_gate: L-GATE_S` vs delivered work and MANIFEST (“L-GATE_B PASS”). **WP003** `status: BUILDING` vs Pass-2 complete notes. | Team 100 normalizes roadmap rows after this verdict (API + `deploy_cascade` when DB online). |
| F-190-03 | LOW | Formal **LOD500** as-built files absent; WP005 bundle missing some original AC-02 artifacts (Lighthouse JSON, root `SCRAPING_VERIFICATION.md` filename). | File LOD500 summaries or accept L0 bundle as SSoT for Phase 1; add deferred QA artifacts when available. |
| F-190-04 | INFO | `validate_aos.sh` Check 21–22 **SKIP** (manual `validate_gates.sh` / `validate_lod.sh` advisories). | Optional mechanical follow-up; not a Phase 1 launch regression. |

---

## 5. Mechanical validation log

**Command:** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`  
**Date:** 2026-05-07  
**Result:** **29 PASS / 17 SKIP / 0 FAIL** — L-GATE_BUILD exit criterion satisfied.

**Pytest (spot):** `pytest tests/test_wp_upload.py tests/test_responsive_html.py tests/test_ftps_upload.py` → **81 passed**.

---

## 6. Cross-engine and routing

- **Validator engine:** Cursor Composer — **not** Anthropic Opus; satisfies bundle cross-engine constraint.
- **Writes:** This artifact only under `_COMMUNICATION/TEAM_190/`; **no** `_aos/` edits by team_190.
- **Downstream:** Team 00 / Team 100 own roadmap and gateHistory updates; Team 50 owns deferred Lighthouse/cross-device; hub DB sync per [`_aos/PENDING_DB_SYNC.yaml`](../../../_aos/PENDING_DB_SYNC.yaml) when ADR034 online.

---

## 7. Sign-off

**team_190 — L-GATE_VALIDATE — PASS_WITH_FINDINGS — 2026-05-07**
