---
id: ARCHIVE_MANIFEST_SFA-S003-P004-WP-CB-0
wp: SFA-S003-P004-WP-CB-0
status: CLOSED
lod_status: LOD200_LOCKED
archived_by: team_60
archive_date: "2026-07-12"
mandate_ref: "CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md §3 A2-a"
roadmap_entry: "_aos/roadmap.yaml → id: SFA-S003-P004-WP-CB-0"
archive_root: "_archive/SFA-S003-P004-WP-CB-0/"
subtype: NO-DEDICATED-ARTIFACT-DIR
---

# Archive Manifest — SFA-S003-P004-WP-CB-0 (Crop Data Model Canon)

**ספר גידולים: Crop Data Model Canon (field taxonomy, attributes layer, units/enums, migration)**

Roadmap `status: DONE` normalized to `status: CLOSED` per the M11 fleet version-hygiene sweep A2-a ruling.

## Finding: no dedicated artifact directory exists for this WP-ID

A full search of `_COMMUNICATION/` (all TEAM_* and team_* directories, case-insensitive, filename + dirname) found
**zero files or folders named for `SFA-S003-P004-WP-CB-0`**. This WP is a design-only, no-build/no-L-GATE_V
canon-authoring effort (per its own roadmap `notes`: *"No build / no L-GATE_V of its own; terminal state = DONE /
LOD200_LOCKED"*). Its gate evidence (L-GATE_E, L-GATE_S R1-R3) lives entirely **inside the shared program-level**
`_COMMUNICATION/TEAM_100/SFA-S003-P004/` and `_COMMUNICATION/TEAM_190/SFA-S003-P004/` folders (e.g.
`TARGET_A_CANON_L-GATE_S_VERDICT_v1.0.0.md`, `VALIDATION_MANDATE_team190_*.md`), which are **shared with sibling
WPs** (WP-CB-MIG, WP-CB-MIG2, WP-CB-1, etc. all reference the same program folder) and are therefore **not
attributable exclusively to CB-0** — moving them would misattribute shared program history. Left in place, untouched.

Its LOD200 spec (`_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md`) also remains in
place, per the established sibling convention (WP-CB-1's own manifest: `_aos/work_packages/` specs are not moved by
Phase-3 archive in this domain — only `_COMMUNICATION/` artifacts are).

## Files MOVED

None — no dedicated WP-ID-tagged artifacts exist to move.

## Left In Place (intentionally not moved)

| Path | Reason |
|------|--------|
| `_aos/work_packages/S003/SFA-S003-P004-WP-CB-0/LOD200_CROP_DATA_MODEL_CANON.md` | Not moved by Phase-3 archive convention in this domain (spec_ref stays as-is) |
| `_COMMUNICATION/TEAM_100/SFA-S003-P004/*` and `_COMMUNICATION/TEAM_190/SFA-S003-P004/*` | Shared program-level folders referencing multiple sibling WPs (CB-MIG, CB-MIG2, CB-1, etc.) — not exclusively CB-0's; splitting would misattribute shared history |

*Manifest authored by team_60 · 2026-07-12 · M11 fleet version-hygiene sweep, A2-a execution (status-only backfill; no file action possible).*
