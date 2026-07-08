# ARCHIVE_MANIFEST — SFA-S002-P001 (Public Index Launch Readiness Program)

| Field | Value |
|-------|-------|
| **program_id** | SFA-S002-P001 |
| **closure_type** | PROGRAM_COMPLETE (Phase 1 + Phase 2, per `roadmap.yaml` project notes: "S002 PROGRAM: COMPLETE — no open items") |
| **roadmap status at archive** | WP001/002/004/006/007/008 `status: COMPLETE`; WP003 `status: DONE` (non-standard token — see note); WP005 `status: COMPLETE` (see note) |
| **authority** | ADR042 / Iron Rule #15 |

> **Note:** no manifest existed for this program prior to 2026-07-09 despite most of its WP artifacts already
> having been moved into this directory by an earlier (undated, unattributed) archive pass. This manifest was
> authored retroactively during the Domain Doc & Archival Sweep (`DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0`,
> 2026-07-09) to bring the directory to compliance (mandatory Path-redirects table) and to record two
> additional leftover moves made in that same session (WP001/WP002 TEAM_100 dirs, below).

## Work packages archived (state as of 2026-07-09)

| WP | Teams present | Archive path |
|----|----------------|--------------|
| SFA-S002-P001-WP001 | TEAM_10, TEAM_100 | `_archive/SFA-S002-P001/TEAM_10/SFA-S002-P001-WP001/`, `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP001/` |
| SFA-S002-P001-WP002 | TEAM_10, TEAM_100 | `_archive/SFA-S002-P001/TEAM_10/SFA-S002-P001-WP002/`, `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP002/` |
| SFA-S002-P001-WP003 | TEAM_100, team_99 | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP003/`, `_archive/SFA-S002-P001/team_99/SFA-S002-P001-WP003/` — **flag:** `roadmap.yaml` `status: DONE` (not the `COMPLETE` enum literal); already fully archived by a prior pass despite this; data-hygiene ESCALATE only (no file action) |
| SFA-S002-P001-WP004 | TEAM_100 | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP004/` |
| SFA-S002-P001-WP006 | TEAM_100, team_99 | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP006/`, `_archive/SFA-S002-P001/team_99/SFA-S002-P001-WP006/` |
| SFA-S002-P001-WP007 | TEAM_10, TEAM_100, team_99 | `_archive/SFA-S002-P001/TEAM_10/SFA-S002-P001-WP007/`, `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP007/`, `_archive/SFA-S002-P001/team_99/SFA-S002-P001-WP007/` |
| SFA-S002-P001-WP008 | TEAM_100, team_99 | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP008/`, `_archive/SFA-S002-P001/team_99/SFA-S002-P001-WP008/` |
| SFA-S002-P001-WP005 | — none found — | **not archived — see note below** |

## 2026-07-09 sweep additions (leftover, never-archived artifacts found still live)

| Former path | Archived path |
|-------------|---------------|
| `_COMMUNICATION/TEAM_100/SFA-S002-P001-WP001/MANDATE_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP001/MANDATE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001-WP002/MANDATE_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/SFA-S002-P001-WP002/MANDATE_v1.0.0.md` |

`spec_ref` for both (`_aos/work_packages/S002/SFA-S002-P001-WP00{1,2}/LOD400_spec.md`) was not moved — per-domain
convention, `_aos/work_packages/` spec docs remain in place permanently; no dangling reference introduced.

## SFA-S002-P001-WP005 — not archived, ESCALATE

`roadmap.yaml` records WP005 (`status: COMPLETE`, `lod_status: LOD500_LOCKED`) but **no directory named
`SFA-S002-P001-WP005` exists anywhere** (live or archived) under any team. Its actual artifacts (per grep)
live inside the **program-level container** `_COMMUNICATION/TEAM_100/SFA-S002-P001/` and
`_COMMUNICATION/TEAM_190/SFA-S002-P001/` (e.g. `PROGRAM_PACKAGE_LOD200_v1.0.0.md`, `ARCHIVE_MANDATE_v1.0.0.md`,
`L_GATE_S_VERDICTS_v1.0.0.md`, `EXTERNAL_VALIDATION_BUNDLE/`, `EXTERNAL_VERDICT_v1.0.0.md`) — both container
directories are themselves still fully live, un-archived, and contain an explicit `ARCHIVE_MANDATE_v1.0.0.md`
that was evidently never (or only partially) executed. This is a program-level container, not a single WP-ID
artifact dir — the mechanical Step-2 scan (`find _COMMUNICATION/team_* -maxdepth 1 -type d -name "<WP-ID>"`)
returns zero hits for `SFA-S002-P001-WP005` and does not cover container-level dirs. **ESCALATE** (subtype
`NO-DEDICATED-ARTIFACT-DIR` / `UNEXECUTED-ARCHIVE-MANDATE`) — team_120 to rule on completing the standing
`ARCHIVE_MANDATE_v1.0.0.md` for the whole `SFA-S002-P001` program container. No file touched.

---
*Manifest authored 2026-07-09 by domain-doc-archive-sweep (retroactive, for a program archived earlier by an
unattributed prior pass) — see `_COMMUNICATION/team_120/SWEEP_REPORT_smallfarmsagents_2026-07-09_v1.0.0.md`.
Not committed (left staged per procedure — team_60 to review/commit).*
