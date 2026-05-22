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

---
*Archived 2026-05-22 by team_191*
