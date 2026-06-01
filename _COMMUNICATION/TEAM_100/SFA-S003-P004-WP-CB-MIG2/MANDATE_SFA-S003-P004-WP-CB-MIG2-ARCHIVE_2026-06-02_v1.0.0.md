---
id: MANDATE_SFA-S003-P004-WP-CB-MIG2-ARCHIVE
from: team_100
to: team_191
cc: [team_00]
date: 2026-06-02
type: archive_mandate
adr: ADR042 (WP closure protocol)
wp: SFA-S003-P004-WP-CB-MIG2
---

# Archive Mandate — SFA-S003-P004-WP-CB-MIG2 (ADR042)

WP-CB-MIG2 (Crop Data Model Expansion) is **LOD500_LOCKED** (L-GATE_V PASS_WITH_FINDINGS, team_190
non-Claude, 2026-06-02; verdict `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/WP-CB-MIG2_LGATE-V_VERDICT_v1.0.0.md`).
Per ADR042, archive the WP process artifacts.

## Scope — archive (move → `_archive/SFA-S003-P004-WP-CB-MIG2/`)
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MIG2/` (mandates, MSGs, this mandate)
- `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-MIG2/` (BUILD_REPORT)
- `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-MIG2/` (QA_REPORT)
- `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-MIG2/` (L-GATE_S + L-GATE_V verdicts)

## Keep in place (live, NOT archived)
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-MIG2/LOD400_spec.md` (v1.0.1 — locked spec)
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` (Canon v1.3.0 — live SSoT)
- All shipped code: migration 060, `canon/` (topics/enums/units/field_registry), `attribute_resolver`,
  `field_policy`, `sfa_ingest_push`, `FieldRegistry.php`, `book_crop.php`, `load_masterclass_sheets`,
  `scripts/build_crop_gap_console.py`, `scripts/ingest_nimrod_validation.py`, and the MIG2 tests.

## On completion
Set `archive_ref` on the WP-CB-MIG2 roadmap row to the archive manifest path and notify team_100.

## Notes
- All MIG2 work is on branch `claude/wp-cb-mig2-2026-06-01` (not merged to main — merge is a team_00 call).
  Archive on that branch.
- Operational follow-on (NOT part of this archive): live `alembic upgrade 060`, PR backfill, and the
  manual-validation console → NI ingest cycle (team_00 / team_99).

-- team_100 (Chief System Architect)
