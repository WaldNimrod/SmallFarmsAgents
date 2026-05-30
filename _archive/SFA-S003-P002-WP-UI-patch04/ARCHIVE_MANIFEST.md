# ARCHIVE_MANIFEST — SFA-S003-P002-WP-UI-patch04 — team_191 — v1.0.0

**Date:** 2026-05-30
**Author:** team_191 (Git/Files / Archive Steward)
**WP:** SFA-S003-P002-WP-UI-patch04
**Type:** ARCHIVE_MANIFEST
**archive_date:** 2026-05-30
**archived_by:** team_191 (Archive Steward) — executed in team_100 session under archive mandate
**mandate:** `_archive/SFA-S003-P002-WP-UI-patch04/MANDATE_SFA-S003-P002-WP-UI-patch04-ARCHIVE_v1.0.0.md`
**procedure:** `_aos/lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.1.0
**file_count:** 7 (6 artifacts + this manifest)
**iron_rule:** IR#15 (Archive)

---

## 1. WP Identity

| Field | Value |
|-------|-------|
| **id** | SFA-S003-P002-WP-UI-patch04 |
| **label** | Crop-book completeness (all crop data) + global nav + broken-link + layout/ordering |
| **status** | DONE |
| **lod_status** | LOD500_LOCKED |
| **closed_at** | 2026-05-30 |
| **production_url** | https://sfa.nimrod.bio/crop-book/ |
| **milestone / program** | S003 / SFA-S003-P002 |
| **phase / track / effort / profile** | 2_followup / A / LARGE / L0 |
| **build_commit** | a7a787a |
| **builder** | team_10 (Claude Sonnet A∥B→C) + team_100 integration |
| **qa** | team_50 (Claude Haiku) |
| **validator** | team_190 (non-Claude) per IR#1 |

---

## 2. Gate Ledger

| Gate | Round | Result | Commit | Artifact |
|------|-------|--------|--------|----------|
| L-GATE_E | — | PASS | — | team_00 live review (6 defects) |
| L-GATE_S | — | PASS | — | team_100 LOD400 v1.0.0 |
| L-GATE_B | — | PASS | 70dc728 | `team_10/BUILD_REPORT_v1.0.0.md` |
| QA | — | QA_PASS_WITH_FINDINGS | 70dc728 | `team_50/QA_REPORT_v1.0.0.md` |
| DEPLOY | — | LIVE | c7dc779 | roadmap DEPLOY entry (re-push + uPress deploy + broken-links 72→0) |
| L-GATE_V | R1 | **FAIL** | c7dc779 | `team_190/L-GATE_V_VERDICT_v1.0.0.md` (AC-U4-06 nav clobber) |
| — | remediation | FIXED | a7a787a | `$active`→`$month_active` + re-assert guard |
| L-GATE_V | R2 | **PASS** | a7a787a | `team_190/L-GATE_V_VERDICT_R2_v1.0.0.md` |

**Cross-engine (IR#1):** builder Claude Sonnet ≠ QA Claude Haiku ≠ validator non-Claude. Satisfied.

---

## 3. Inventory

All paths relative to `_archive/SFA-S003-P002-WP-UI-patch04/`.

| Archive path | SHA | Size | Origin | Summary |
|-------------|-----|------|--------|---------|
| `MANDATE_SFA-S003-P002-WP-UI-patch04-ARCHIVE_v1.0.0.md` | a25fca09 | 1584 | authored at closure | archive mandate |
| `team_10/BUILD_REPORT_v1.0.0.md` | 3ca1e566 | 2298 | authored at closure from Workflow record | build report (A∥B→C + integration + fixes) |
| `team_50/QA_REPORT_v1.0.0.md` | 250f6ba9 | 1696 | authored at closure from Workflow QA record | QA report |
| `team_190/L-GATE_V_MANDATE_v1.0.0.md` | 9394a808 | 3482 | `_COMMUNICATION/TEAM_190/…/` | R1 validation mandate |
| `team_190/L-GATE_V_VERDICT_v1.0.0.md` | 1fc9cf24 | 5927 | `_COMMUNICATION/TEAM_190/…/` | R1 verdict (FAIL — AC-U4-06) |
| `team_190/L-GATE_V_R2_MANDATE_v1.0.0.md` | df676d45 | 2058 | `_COMMUNICATION/TEAM_190/…/` | R2 narrow re-check mandate |
| `team_190/L-GATE_V_VERDICT_R2_v1.0.0.md` | c3913095 | 4127 | `_COMMUNICATION/TEAM_190/…/` | R2 verdict (PASS) |

---

## 4. Preserved in Place (NOT archived)

| Path | Reason |
|------|--------|
| `sfa_delivery/` (_layout, nav.php, book_crop.php, book_cover_crops.php, crop_* macros, CropBook/Market controllers, routes, hub.css, tests) | LIVE PRODUCTION |
| `organic_market_agent/publisher/sfa_ingest_push.py` (rich crops embed + cover_crops) | LIVE pipeline code |
| `_aos/work_packages/S003/SFA-S003-P002-WP-UI-patch04/LOD400_spec.md` | LOD500 reference — immutable per ADR042 |
| `_aos/roadmap.yaml` WP-UI-patch04 row | Gate history — IR#4 single writer (team_100) |

---

## 5. Closure Trail

| Event | Commit | Date |
|-------|--------|------|
| activation (E+S) + LOD400 | 1f1d5ab | 2026-05-29 |
| build (B + QA) | 70dc728 | 2026-05-29 |
| link fix (prdNNN) | eef88b4 | 2026-05-29 |
| planned-module/methodology fix → 0 broken links | c7dc779 | 2026-05-29 |
| roadmap DEPLOY LIVE + L-GATE_V mandate | 8177b08 / 67b515f | 2026-05-29 |
| L-GATE_V R1 FAIL + remediation (nav clobber) | a7a787a | 2026-05-30 |
| R1 verdict + R2 mandate recorded | 6e2c654 | 2026-05-30 |
| archive + LOD500_LOCKED (this op) | (this commit) | 2026-05-30 |

---

## 6. Path Redirects (POST_GATE_ARCHIVE_PROCEDURE v1.1.0 M.2)

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_MANDATE_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI-patch04/team_190/L-GATE_V_MANDATE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_VERDICT_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI-patch04/team_190/L-GATE_V_VERDICT_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_R2_MANDATE_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI-patch04/team_190/L-GATE_V_R2_MANDATE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-UI-patch04/L-GATE_V_VERDICT_R2_v1.0.0.md` | `_archive/SFA-S003-P002-WP-UI-patch04/team_190/L-GATE_V_VERDICT_R2_v1.0.0.md` |

---

## 7. Step 3 (multi-engine propagation) — verification

ADR042 Step 3 applies only if `core/governance/` (hub) was modified during the WP. **It was not**
— spoke application code + spoke docs only. **Step 3 SKIPPED (verified exempt).**

---

## 8. Validation

```
validate_aos.sh — post-archive (2026-05-30): patch04 files clean.
```
**Note:** a concurrent, unrelated WP (`SFA-S003-P004-WP-CB-1`) has uncommitted files in the
working tree (owned by a separate session) which trip Check 32; that is outside this WP's scope
and was deliberately not committed by this team_100 session.

---

*Archive manifest generated by team_191 (Archive Steward) | 2026-05-30 | IR#15 | POST_GATE_ARCHIVE_PROCEDURE v1.1.0*
