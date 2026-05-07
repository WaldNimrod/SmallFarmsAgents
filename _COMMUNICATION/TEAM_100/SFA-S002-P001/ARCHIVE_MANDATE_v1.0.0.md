# ARCHIVE MANDATE — SFA-S002-P001 Phase 1 — TEAM_100 → TEAM_191

**Date:** 2026-05-07
**From:** team_100 (sfa_arch / Claude Opus 4.7)
**To:** team_191 (Git/Files custodian)
**Type:** ARCHIVE_MANDATE (per ADR042 Step 1 — WP Closure Protocol)
**Trigger:** L-GATE_VALIDATE PASS achieved for SFA-S002-P001 Phase 1 (effective PASS after F-190-01 remediation 2026-05-07).

---

## 1. Scope — 5 WPs to archive

| WP | Final state | Closure verdict |
|----|-------------|-----------------|
| **SFA-S002-P001-WP003** | Server Scraping Verification (Pass-1 + Pass-2) | L-GATE_B PASS Pass-2 (team_99 self-attest, OPS) — F-01 closed |
| **SFA-S002-P001-WP004** | Mobile UI Parity | L-GATE_B PASS (sfa_build Sonnet) — AC-05/06 deferred to Team 50 with live site (R-01) |
| **SFA-S002-P001-WP006** | FTPS Upload Remediation (TLS hypothesis) | L-GATE_B PASS_CODE_CORRECT — SUPERSEDED_BY_WP007 |
| **SFA-S002-P001-WP007** | HTTP Upload Migration via WP REST API | L-GATE_B PASS production-verified (team_99 deploy) — F-01 root cause fix |
| **SFA-S002-P001-WP008** | Wire WP REST primary into scheduler + admin | L-GATE_B PASS production-verified (team_99 deploy 5b80c60) — F-190-01 remediation |
| **SFA-S002-P001-WP005** | Public Launch Package (bundle) | L-GATE_V PASS effective (team_190 PASS_WITH_FINDINGS + same-day F-190-01 fix) |

**NOT archived this round (carry forward to Phase 2 — SFA-S003 in next session):**
- WP001 (M10 thaw) — DEFERRED_PHASE2, mandate intact at L-GATE_S PASS / LOD400_LOCKED
- WP002 (MyPIPS sources) — DEFERRED_PHASE2, same state

---

## 2. Archive instructions

Per ADR042 + lean-kit POST_GATE_ARCHIVE_PROCEDURE.md v1.1.0:

1. Create directory: `_archive/SFA-S002-P001-Phase1/`
2. Move (or copy + reference) the following artifacts into it, preserving repo paths:
   - `_aos/work_packages/S002/SFA-S002-P001-WP003/LOD400_spec.md`
   - `_aos/work_packages/S002/SFA-S002-P001-WP004/LOD400_spec.md`
   - `_aos/work_packages/S002/SFA-S002-P001-WP005/LOD400_spec.md`
   - `_aos/work_packages/S002/SFA-S002-P001-WP006/LOD400_spec.md`
   - `_aos/work_packages/S002/SFA-S002-P001-WP007/LOD400_spec.md`
   - `_aos/work_packages/S002/SFA-S002-P001-WP008/LOD400_spec.md`
   - `_COMMUNICATION/team_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md`
   - `_COMMUNICATION/team_100/SFA-S002-P001/L_GATE_S_VERDICTS_v1.0.0.md`
   - `_COMMUNICATION/team_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md` *(reference for Phase 2 — keep accessible OUT of archive)*
   - `_COMMUNICATION/team_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md` *(reference for Phase 2 — keep accessible OUT of archive)*
   - All MANDATE files under `_COMMUNICATION/team_100/SFA-S002-P001-WP{003,004,005,006,007,008}/`
   - All DEPLOY/REPORT files under `_COMMUNICATION/team_99/SFA-S002-P001-WP{003,006,007,008}/`
   - All cross-team REPORT files under `_COMMUNICATION/TEAM_60/reports/2026-05-0?_SCRAPING_VERIFICATION_*`
   - All MSG-HUB files under `_COMMUNICATION/team_99/MSG-HUB-20260507-*.md`
   - The full bundle directory `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/`
   - The external verdict `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md`
3. Create `_archive/SFA-S002-P001-Phase1/ARCHIVE_MANIFEST.md` cataloguing each archived artifact with:
   - Original path (pre-archive)
   - Archive path (post-archive)
   - File hash (sha256) for integrity
   - Ownership team
   - Final gate verdict
4. Verify `validate_aos.sh` Check 15 passes (no stale Phase 1 artifacts in active `_COMMUNICATION/`).
5. Commit + push.

---

## 3. Carry-forward (do NOT archive)

These remain in active `_aos/` and `_COMMUNICATION/` for Phase 2:
- `_aos/work_packages/S002/SFA-S002-P001-WP001/LOD400_spec.md` (Phase 2)
- `_aos/work_packages/S002/SFA-S002-P001-WP002/LOD400_spec.md` (Phase 2)
- `_COMMUNICATION/team_100/SFA-S002-P001-WP001/MANDATE_v1.0.0.md` (Phase 2)
- `_COMMUNICATION/team_100/SFA-S002-P001-WP002/MANDATE_v1.0.0.md` (Phase 2)
- `_COMMUNICATION/team_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md` (Phase 2 input)
- `_COMMUNICATION/team_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md` (Phase 2 input)
- `documentation/05-admin-and-operations/UPRESS_WP_REST_API_PUBLISH_RUNBOOK.md` (operational, evergreen)
- The PROGRAM_PACKAGE_LOD200 stays accessible — its decisions D1–D7 still bind Phase 2.

---

## 4. After archival

Once team_191 confirms `ARCHIVE_MANIFEST.md` is written and committed, team_100 will:
- Update `_aos/roadmap.yaml` Phase 1 WP `lod_status: LOD500_LOCKED` (already done in same session)
- Update `_aos/PENDING_DB_SYNC.yaml` to record the archival mutations
- Notify team_00 of Phase 1 closure complete

This mandate completes ADR042 Step 1. Step 2 (DB state transition) is file-based per ADR034 R9 (spoke-native, DB still offline). Step 3 (multi-engine propagation) is exempt — no `core/governance/` modifications during this program.

---

*Archive mandate issued 2026-05-07. Awaiting team_191 acknowledgement.*
