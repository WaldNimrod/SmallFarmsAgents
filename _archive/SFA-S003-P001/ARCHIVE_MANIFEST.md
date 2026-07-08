# ARCHIVE_MANIFEST — SFA-S003-P001 (ספר גידולים)

| Field | Value |
|-------|-------|
| **program_id** | SFA-S003-P001 |
| **closure_type** | PROGRAM_COMPLETE (Phase 1 + Phase 2) |
| **roadmap status at archive** | All WPs COMPLETE / LOD500_LOCKED |
| **archived** | 2026-05-22 |
| **archived_by** | team_191 (Git, Archive & File Governance) |
| **trigger** | MANDATE_SFA-S003-P001-PHASE2-ARCHIVE_v1.0.0 (team_100) |
| **authority** | ADR042 / Iron Rule #15 |
| **branch** | claude/gallant-elbakyan-727a60 |

## Work packages archived

| WP | Teams | Archive path |
|----|-------|--------------|
| SFA-S003-P001-WP001 | TEAM_100 | `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP001/` |
| SFA-S003-P001-WP002 | TEAM_10, TEAM_100, TEAM_190 | `_archive/SFA-S003-P001/TEAM_10/SFA-S003-P001-WP002/`, `.../TEAM_100/...`, verdict at `.../TEAM_190/SFA-S003-P001-WP002-LGATEV-VERDICT_v1.0.0.md` |
| SFA-S003-P001-WP003 | TEAM_10, TEAM_100, TEAM_190 | `_archive/SFA-S003-P001/TEAM_10/SFA-S003-P001-WP003/`, `.../TEAM_100/...`, LGATEV + PATCH01 verdicts under `.../TEAM_190/` |
| SFA-S003-P001-WP004 | TEAM_10, TEAM_100, TEAM_190 | `_archive/SFA-S003-P001/TEAM_10/SFA-S003-P001-WP004/`, `.../TEAM_100/...`, `.../TEAM_190/SFA-S003-P001-WP004/` |

## Cross-WP artifacts

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_100/SFA-S003-P001/EXTERNAL_VALIDATION_BUNDLE/` | `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001/EXTERNAL_VALIDATION_BUNDLE/` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P001-LOD400-VERDICT_R2_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_190/SFA-S003-P001-LOD400-VERDICT_R2_v1.0.0.md` |

## Handled MSGs (under `{team}/archive/`)

| MSG | Archive path |
|-----|--------------|
| MSG-HUB-20260510-001 | `_archive/SFA-S003-P001/TEAM_10/archive/` |
| MSG-HUB-20260513-001 | `_archive/SFA-S003-P001/TEAM_190/archive/` |
| MSG-team100-to-team190-S003-WP004-LGATES-* | `_archive/SFA-S003-P001/TEAM_190/archive/` |
| MSG-team190-to-team100-S003-WP004-* | `_archive/SFA-S003-P001/TEAM_100/archive/` |

**file_count:** 39 (excluding this manifest)

## Path redirect (team_100 action required)

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` |

Update `SFA-S003-P001-WP001` `spec_ref` in `_aos/roadmap.yaml` to the archived path (or retire to `_aos/work_packages/` copy). Until updated, `validate_aos.sh` Check 4 will FAIL.

## Explicit exclusions (left in `_COMMUNICATION/`)

- `GCR_AOS_MESSAGING_INFRA_HARDENING_2026-05-10_v1.0.0.md` (live)
- `GCR_UPRESS_FTPS_PROTOCOL_2026-05-10_v1.0.0.md` (live)
- Phase handoffs / discovery summaries (not WP deliverables)
- `team_191/MANDATE_SFA-S003-P001-PHASE2-ARCHIVE_v1.0.0.md` (mandate record)

## Addendum — 2026-07-09 (Domain Doc & Archival Sweep, DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0)

`SFA-S003-P001-WP003-patch02` (`status: COMPLETE`, `lod_status: LOD500_LOCKED`) was found still fully live
under `_COMMUNICATION/` — never archived under this program. Archived now (leftover-artifact sweep):

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003-patch02/DISPATCH_sfa_build_2026-05-23_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP003-patch02/DISPATCH_sfa_build_2026-05-23_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003-patch02/EXTERNAL_VALIDATION_BUNDLE/*` (3 files) | `_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP003-patch02/EXTERNAL_VALIDATION_BUNDLE/*` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P001-WP003-patch02/LGATEV-VERDICT_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_190/SFA-S003-P001-WP003-patch02/LGATEV-VERDICT_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_190/SFA-S003-P001-WP003-patch02/LOD400-VERDICT_v1.0.0.md` |
| `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md` | `_archive/SFA-S003-P001/TEAM_10/SFA-S003-P001-WP003-patch02/BUILD_REPORT_v1.0.0.md` |

`spec_ref` (`_aos/work_packages/S003/SFA-S003-P001-WP003-patch02/LOD400_spec.md`) was not moved — per-domain
convention, `_aos/work_packages/` spec docs remain in place permanently (POST_GATE_ARCHIVE_PROCEDURE only
scopes `_COMMUNICATION/team_*/<WP-ID>/`); no dangling reference introduced. `roadmap.yaml` note at the
`L-GATE_B` gate (embedded `BUILD_REPORT:` path) repointed to the archived path same session.

**file_count (addendum):** 7 files across 3 teams. Executed by: sweep session (weak-engine, no team assigned —
see `_COMMUNICATION/team_120/SWEEP_REPORT_smallfarmsagents_2026-07-09_v1.0.0.md`). Not committed (left staged
per procedure — team_60 to review/commit).

---
*Archived 2026-05-22 by team_191 · addendum 2026-07-09 by domain-doc-archive-sweep*
