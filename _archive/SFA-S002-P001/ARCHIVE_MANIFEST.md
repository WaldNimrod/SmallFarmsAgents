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

## SFA-S002-P001-WP005 — program-container archive mandate EXECUTED (2026-07-12)

`roadmap.yaml` records WP005 (`status: COMPLETE`, `lod_status: LOD500_LOCKED`) but no directory named
`SFA-S002-P001-WP005` ever existed (live or archived) under any team. Its actual artifacts lived inside the
**program-level container** `_COMMUNICATION/TEAM_100/SFA-S002-P001/` and `_COMMUNICATION/TEAM_190/SFA-S002-P001/`,
which held a standing, never-executed `ARCHIVE_MANDATE_v1.0.0.md` (issued 2026-05-07, team_100 → team_191).

**Disposition:** ESCALATE resolved. Per the M11 fleet version-hygiene centralized review (A2-c ruling —
`CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md` §3 A2-c: *"SFA — SFA-S002-P001-WP005
UNEXECUTED-ARCHIVE-MANDATE ... execute it (verify-and-move the program container)"*), team_60 executed the
standing mandate on 2026-07-12. The 5 archivable program-level items were moved **flat** into
`_archive/SFA-S002-P001/TEAM_100/` and `_archive/SFA-S002-P001/TEAM_190/` (program-level artifacts, not nested
under a `SFA-S002-P001-WP005/` subfolder — they document the whole program, not just WP005).

### Files MOVED (git mv)

| From | To |
|------|----|
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/ARCHIVE_MANDATE_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/ARCHIVE_MANDATE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/` (whole dir: VALIDATE_AOS_OUTPUT.txt, WP007, WP006, RISK_REGISTER.md, ROLLBACK_PLAN.md, PROGRAM_SUMMARY.md, MANIFEST.md, AOS_MAIL_PROMPT.md, WP003, WP004) | `_archive/SFA-S002-P001/TEAM_100/EXTERNAL_VALIDATION_BUNDLE/` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/L_GATE_S_VERDICTS_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/L_GATE_S_VERDICTS_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/PROGRAM_PACKAGE_LOD200_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_190/EXTERNAL_VERDICT_v1.0.0.md` |

### Path redirects

| Old path | New path |
|----------|----------|
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/ARCHIVE_MANDATE_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/ARCHIVE_MANDATE_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/EXTERNAL_VALIDATION_BUNDLE/` | `_archive/SFA-S002-P001/TEAM_100/EXTERNAL_VALIDATION_BUNDLE/` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/L_GATE_S_VERDICTS_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/L_GATE_S_VERDICTS_v1.0.0.md` |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/PROGRAM_PACKAGE_LOD200_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_100/PROGRAM_PACKAGE_LOD200_v1.0.0.md` |
| `_COMMUNICATION/TEAM_190/SFA-S002-P001/EXTERNAL_VERDICT_v1.0.0.md` | `_archive/SFA-S002-P001/TEAM_190/EXTERNAL_VERDICT_v1.0.0.md` |

### Left In Place (mandate §3 carry-forward carve-out — NOT archived)

| Path | Reason |
|------|--------|
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP001_M10_SPIKE.md` | `ARCHIVE_MANDATE_v1.0.0.md` §3 explicitly carries this forward to Phase 2 (reference for Phase 2 — keep accessible OUT of archive) |
| `_COMMUNICATION/TEAM_100/SFA-S002-P001/AUDIT_WP002_MYPIPS.md` | Same carve-out, WP002 |

**Note for team_100:** at mandate-issue time (2026-05-07) WP001/WP002 were expected to remain open into "Phase 2."
As of this pass (2026-07-12), `roadmap.yaml` shows both `SFA-S002-P001-WP001` and `SFA-S002-P001-WP002` at
`status: COMPLETE` / `lod_status: LOD500_LOCKED` — i.e. Phase 2 for these two has since closed. The mandate's
carry-forward carve-out was nonetheless honored as written (per the M11 sweep brief's explicit default), so these
2 audit files were left live rather than archived. team_100 may wish to re-evaluate whether they should now be
archived given WP001/WP002's closed status — flagged, not actioned.

---
*Manifest authored 2026-07-09 by domain-doc-archive-sweep (retroactive, for a program archived earlier by an
unattributed prior pass) — see `_COMMUNICATION/team_120/SWEEP_REPORT_smallfarmsagents_2026-07-09_v1.0.0.md`.
WP005 disposition completed 2026-07-12 by team_60 per A2-c of
`CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md`, executing the standing
`ARCHIVE_MANDATE_v1.0.0.md`.*
