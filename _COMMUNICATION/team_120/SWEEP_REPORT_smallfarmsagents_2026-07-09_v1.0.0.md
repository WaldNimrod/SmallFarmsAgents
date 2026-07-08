---
id: SWEEP_REPORT_smallfarmsagents_2026-07-09_v1.0.0
type: DOMAIN_DOC_ARCHIVE_SWEEP_REPORT
from: sweep-session@smallfarmsagents
to: team_120
date: 2026-07-09
procedure: DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0
run_status: COMPLETE
---

## Baseline (Phase 0)

domain_id: smallfarmsagents | branch: main | sha: 90ed1e0fae2a75a345cc71fed4c028ad9955e07d | domain_version_flag: **V5**

version_markers:
```
governance:   _aos/AOS_GOVERNANCE_VERSION.yaml → hub_sha 2176f3072d76, synced 2026-06-10, synced_by team_100
lean_kit:     _aos/lean-kit/LEAN_KIT_VERSION.md → NOT FOUND; canonical value read instead from
              _aos/metadata.yaml → lean_kit_version: 3.3.0 (current hub Lean Kit release — V5)
              (NOTE: _aos/roadmap.yaml project.lean_kit_version: "3.1.7+c546ed4" is a stale project-creation-time
              field, never updated since 2026-03-01 onboarding — informational only, superseded by metadata.yaml)
active_milestone: "S003" (roadmap.yaml project header — see ESCALATE/systemic note: looks stale vs. S004 activity)
```

before (as literally produced by the procedure's own Phase-0 command text):
```
unarchived_comm_files: 245   open_wps: 4   archive_dirs: 34
```
**IMPORTANT — see systemic finding E-1 below.** The literal command `find _COMMUNICATION/team_* -type f ...`
uses a case-sensitive shell glob. This domain's team directories are a **mix of `TEAM_NN` (uppercase) and
`team_nn` (lowercase)** — the literal command only ever sees the lowercase ones. The **true** before-state,
walking all team dirs regardless of case:
```
unarchived_comm_files (true): 1366   open_wp_dirs (true, _aos/work_packages 2 levels deep — this domain nests
  WPs under stage dirs S001/S002/S003, so the literal maxdepth-1 "4" is really 3 stage containers + 1 parent):
  58   archive_dirs: 34 (unchanged basis — 33 real subdirs + parent)
```
All Phase 2/3 decisions below were made against the **true** counts, not the undercounted literal ones.

---

## Phase 1 — documentation

- **D-1 DOC_CANON:** `N/A-spoke` — no `core/` directory in this domain (spoke, not hub).
- **D-2 as-built records:** `PASS (convention-adjusted) · gaps=2`. This domain's convention is
  `ARCHIVE_MANIFEST.md` (program/WP-level) + `LOD500-VERDICT_*.md` files (both present in most closed WPs) in
  place of a single `LOD500_asbuilt.md` file type — accepted as satisfying D-2. Two real gaps found:
  (1) `SFA-S002-P001-WP005` (`status: COMPLETE`) has **no artifact trail at all** — no dedicated dir, no
  manifest entry, only mentions inside an un-archived program container (see ESCALATE below);
  (2) `SFA-S003-P004-WP-CB-CONTENT`'s own `ARCHIVE_MANIFEST.md` cites a `SPEC_2026-06-09_v1.0.0.md` file as
  evidence that **does not exist anywhere** in the tree (live or archived) — pre-existing gap, not authored by
  this sweep (no document content invented, per Phase 1 rule).
- **D-3 module/directory indexes:** `PASS` — only one `INDEX.md` in the whole tree (`data/external_sources/INDEX.md`,
  unrelated to WP archival) and no `MODULE.md`; no dangling index references found. Two **pre-existing** dangling
  `roadmap.yaml` references to WP artifacts that this sweep's own Phase-3 moves would otherwise have
  orphaned were mechanically repointed (see Phase 3 below — this is the "mechanical fix (repoint)" case D-3
  explicitly allows since the `_archive` redirect exists).
- **D-4 CS-cite advisory:** not run — `validate_aos.sh` unavailable in this worktree (see Phase 5 V-3).

---

## Phase 2 — classification counts

**WP-level** (all 70 entries in `_aos/roadmap.yaml` `work_packages:`, the file-SSoT per RULE-C for this spoke):

```
ARCHIVE: 4 · KEEP(v5): 29 · QUARANTINE-V4: 0 · ESCALATE: 37
```
(4 + 29 + 0 + 37 = 70 ✓)

- **ARCHIVE (4)** — `status: COMPLETE` (exact enum match), leftover un-archived `_COMMUNICATION` artifacts found
  and moved this session: `SFA-S002-P001-WP001`, `SFA-S002-P001-WP002`, `SFA-S003-P001-WP003-patch02`,
  `SFA-S003-P004-WP-CB-CONTENT` (partial — see notes).
- **KEEP (29)** = 15 already-fully-archived (comm-side clean, nothing left to move) + 14 open v5-current WPs
  under non-standard-but-unambiguously-open status tokens (`ACTIVE`, `ROUTED`, `VALIDATE`, `REGISTER`,
  `DEFERRED`, `OPEN`, `PLACEHOLDER` — all `milestone_ref: S003`, the domain's own active/open milestone per
  RULE-B; none resemble a terminal/complete state, so none risk mis-archival).
- **QUARANTINE-V4 (0)** — no open v4-legacy WP-ID found anywhere in this domain (see Phase 5 V-1).
- **ESCALATE (37)** = **32 × MALFORMED-STATUS ("DONE"-vocabulary class)** + **5 × other WP-level anomaly**
  (`SFA-S002-P001-WP005`, `SFA-S004-P001-WP001..004`) — full lists in the ESCALATE section below.

**Non-WP artifacts** (loose `_COMMUNICATION` content, container dirs with no roadmap.yaml row) — a second,
separate enumeration axis per §5's own two-part enumerate step:
```
ESCALATE (non-WP): 3 container-dirs (no roadmap entry) + 1 bucketed loose-file tail
  (≈868 files across ~25 named folders + ~104 team-root files, spanning 12 of 14 team dirs)
```
None of these were archived, quarantined, or otherwise touched — see ESCALATE section.

---

## Phase 3 — archive

```
archived_wps: [ SFA-S002-P001-WP001, SFA-S002-P001-WP002, SFA-S003-P001-WP003-patch02, SFA-S003-P004-WP-CB-CONTENT (partial) ]
manifests_written: 3  (1 new: _archive/SFA-S002-P001/ARCHIVE_MANIFEST.md — none existed before, despite most of
  that program already being archived by an earlier, unattributed pass; 2 updated with addenda:
  _archive/SFA-S003-P001/ARCHIVE_MANIFEST.md, _archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md)
archive_failures(->ESCALATE): [ none — 0 bad WPs ]
files_moved: 12 (via git mv; all confirmed non-duplicate before moving)
```

Detail:
- **SFA-S002-P001-WP001 / WP002** — one `MANDATE_v1.0.0.md` each, found still live under `_COMMUNICATION/TEAM_100/`
  even though sibling teams' artifacts for the same WPs were archived long ago. Moved into the existing
  `_archive/SFA-S002-P001/TEAM_100/<WP-ID>/`.
- **SFA-S003-P001-WP003-patch02** — never archived at all (7 files across TEAM_100/TEAM_190/TEAM_10, including
  an `EXTERNAL_VALIDATION_BUNDLE/` of 4 files). Moved into new `_archive/SFA-S003-P001/<TEAM>/SFA-S003-P001-WP003-patch02/`
  subdirs, matching the program's existing per-team layout. `roadmap.yaml`'s embedded `BUILD_REPORT:` path note
  (line 710) repointed to the archived location (mandatory M.1.3).
- **SFA-S003-P004-WP-CB-CONTENT** — 2 of 3 live files were genuinely new (never archived): `COMPLETION_REPORT_2026-06-09_v1.0.0.md`
  (TEAM_100) and `VALIDATION_MANDATE_2026-06-09_v1.0.0.md` (TEAM_190). Moved into the existing
  `_archive/SFA-S003-P004-WP-CB-CONTENT/{team_100 (new),team_190}/`. The **3rd live file**,
  `VERDICT_SFA-S003-P004-WP-CB-CONTENT_L-GATE_VALIDATE_v1.0.0.md`, is a **byte-identical duplicate** of a file
  already archived there since 2026-06-09 — confirmed via `diff` (identical) — left in place untouched per
  INV-3 (never delete); reported, not silently overwritten. `roadmap.yaml`'s gate_history `L-GATE_VALIDATE`
  embedded verdict path (line 4838) was a **pre-existing dangling reference** (points at the un-archived path
  even though the file has been archived since 2026-06-09) — mechanically repointed to the archived copy per
  D-3 (redirect exists → mechanical fix allowed).
- **SFA-S003-P004-WP-CB-DSX1-SWEEP** — checked, **not archived, no action needed**: its one live leftover
  directory (`TEAM_110`, 2 files) is **100% byte-identical duplicate** of content already archived in 2026-06-09
  — nothing new to move. Reported as a stray duplicate for team_60's discretion (not deleted).

`_aos/work_packages/<STAGE>/<WP-ID>/LOD400_spec.md` files were **never** moved for any WP, archived or not —
confirmed via `POST_GATE_ARCHIVE_PROCEDURE.md` v1.2.0 (Steps 1-10), which scopes only `_COMMUNICATION/team_*/<WP-ID>/`;
this domain's spec docs are a permanent fixture of `_aos/work_packages/`, by design, not a dangling reference.

**Nothing was committed.** All 12 moves + 3 manifest edits/creates + 1 roadmap.yaml edit are staged/present in
the working tree, uncommitted, per instruction (team_60 to review and commit).

---

## Phase 4 — quarantine

```
quarantined: [ ]  · index_file: _aos/V4_QUARANTINE_INDEX.md — NOT CREATED (0 candidates, none needed)
```
Zero `QUARANTINE-V4` artifacts found. This domain is fully on the v5 line (RULE-B: its `S###-P###-WP###` /
`SFA-S###-P###-WP...` IDs are the v5 framework, not v4). See Phase 5 V-1 for the full grep evidence — every hit
of "AOS-V4" / "agents_os_v3" in this domain is either already inside `_archive/`, or a prose citation of the
**hub's own** historical WP-IDs / module path (RULE-A: prose mention ≠ this domain's v4-legacy artifact).

---

## Phase 5 — anti-drift verify

- **V-1 residual_v4_active_hits: 0** (adjusted). Raw grep for `AOS-V4|AOS_V4|agents_os_v3|AOS-V4.5-WP`
  outside `_archive/` returns 11 file hits; all 11 inspected:
  - 2 are **false positives** of the procedure's own exclusion regex: `_archive/_BRANCH_RECONCILIATION_2026-06-02/...`
    — these files are already safely inside `_archive/`, but the path has no *leading* slash before `_archive`
    (it's the tree root), so the literal exclusion pattern `/_archive/` doesn't match. Not real drift.
  - 9 are prose citations of the **hub's** (agents-os) own historical WP-IDs (`AOS-V4.1-WP-ACTOR-KEY-PROCEDURE`,
    `AOS-V4.2-WP-MSG-*`, `AOS-V4-WP-CHARTER`, `AOS-V4.5-WP-CI-LOCAL-MINIMAL`) or its `agents_os_v3` Python
    module path, appearing in handoff/GCR/debt docs and one hook comment — RULE-A: prose mention in an active
    doc/config file ≠ this domain's own v4-legacy artifact (exact match to the procedure's own worked example
    for `pytest.ini` / `AOS-V4.5-WP-CI-LOCAL-MINIMAL`). KEEP, no action.
- **V-2 markers_v5: yes** (see Phase 0 — `_aos/metadata.yaml lean_kit_version: 3.3.0`; hub sync SHA current).
- **V-3 validate_aos.sh: script unavailable in this worktree.** Checked both
  `_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh` (this domain has **no** `_aos/lean-kit/`
  directory at all) and the top-level `lean-kit/modules/validation-quality/scripts/` (directory exists, script
  file itself absent). Not run — noted per instruction, not treated as a failure.
- **V-4 doc_canon: N/A** (spoke, no `core/`).

---

## ESCALATE (team_120 decides — DO NOT guess)

### A. MALFORMED-STATUS — "DONE"-vocabulary class (32 WPs)

**Do not auto-archive.** Every WP below has `roadmap.yaml status: DONE` — not the `COMPLETE` enum literal the
classification table's ARCHIVE row requires — while `lod_status: LOD500_LOCKED`. Per RULE-A (classify by
structured fields, never prose) and the table's own row 3 (status not a valid enum value → `ESCALATE
MALFORMED-STATUS`), these do not cleanly match the ARCHIVE row. All are `milestone_ref: S003` (the domain's
current active milestone).

1. `SFA-S002-P001-WP003` *(already fully archived by a prior, undated pass — see Phase 3 program manifest;
   flagged for the status-field data-hygiene fix only, no file action needed)*
2. `SFA-S003-P002-WP-A`
3. `SFA-S003-P002-WP-B1`
4. `SFA-S003-P002-WP-B1-patch01`
5. `SFA-S003-P002-WP-B1-patch02`
6. `SFA-S003-P002-WP-B1-patch03`
7. `SFA-S003-P002-WP-B1-patch04`
8. `SFA-S003-P002-WP-B1-patch04-hotfix01`
9. `SFA-S003-P002-WP-B1-patch04-hotfix02`
10. `SFA-S003-P002-WP-B1-patch06`
11. `SFA-S003-P002-WP-B1-patch07`
12. `SFA-S003-P002-WP-B1-patch08`
13. `SFA-S003-P002-WP-B2`
14. `SFA-S003-P002-WP-B3`
15. `SFA-S003-P002-WP-C1`
16. `SFA-S003-P002-WP-C2`
17. `SFA-S003-P002-WP-C3`
18. `SFA-S003-P002-WP-C4`
19. `SFA-S003-P002-WP-C5`
20. `SFA-S003-P002-WP-C6`
21. `SFA-S003-P002-WP-UI`
22. `SFA-S003-P002-WP-UI-patch01`
23. `SFA-S003-P002-WP-UI-patch02`
24. `SFA-S003-P002-WP-UI-patch03`
25. `SFA-S003-P002-WP-UI-patch04`
26. `SFA-S003-P004-WP-CB-MIG`
27. `SFA-S003-P004-WP-CB-1`
28. `SFA-S003-P004-WP-CB-MIG2`
29. `SFA-S003-P004-WP-CB-1-patch01`
30. `SFA-S003-P004-WP-CB-UI-ALIGN`
31. `SFA-S003-P004-WP-CB-UI-CLASSB`
32. `SFA-S003-P004-WP-CB-DATA`

Of these 32: **10 already have their `_COMMUNICATION` artifacts fully archived already** (WP-B1 + its 8
patches, WP-B2, WP-B3, WP-UI + patches 02-04, WP-CB-1, WP-CB-1-patch01, WP-CB-UI-ALIGN, WP-CB-UI-CLASSB,
WP-CB-DATA, WP003 — a prior, unattributed pass evidently treated `DONE` as equivalent to `COMPLETE` for
archival purposes). **The remainder (WP-A, WP-C1..C6, WP-UI-patch01, WP-CB-MIG, WP-CB-MIG2) still have live,
un-archived `_COMMUNICATION` artifacts.** Per this sweep's explicit brief, **none were archived or further
touched this session** — the file-move question is downstream of team_120's ruling on the status field itself.
Recommend: team_120 rules once on the whole class (either "DONE == COMPLETE, backfill the status field fleet-wide
and let the remaining un-archived ones through Phase 3" or "leave as-is, DONE is intentionally distinct") —
this is exactly the kind of repeat pattern §11 R-4 asks to fold into the classification table.

### B. Other WP-level anomalies (7 items)

- **`SFA-S002-P001-WP005`** (`status: COMPLETE`, `lod_status: LOD500_LOCKED`) — **no dedicated artifact
  directory exists anywhere** (live or archived) under this exact WP-ID. Its actual content lives inside the
  **program-level container** `_COMMUNICATION/TEAM_100/SFA-S002-P001/` and `TEAM_190/SFA-S002-P001/` (23 + 1
  files: `PROGRAM_PACKAGE_LOD200_v1.0.0.md`, `ARCHIVE_MANDATE_v1.0.0.md`, `L_GATE_S_VERDICTS_v1.0.0.md`,
  `EXTERNAL_VALIDATION_BUNDLE/`, `EXTERNAL_VERDICT_v1.0.0.md`) — both container dirs are themselves still fully
  live, and contain a standing `ARCHIVE_MANDATE_v1.0.0.md` that was evidently never (or only partially)
  executed. Subtype `NO-DEDICATED-ARTIFACT-DIR` / `UNEXECUTED-ARCHIVE-MANDATE`. No file touched — team_120 to
  rule on completing that mandate for the whole program container.
- **`SFA-S004-P001-WP001`, `WP002`, `WP003`, `WP004`** (all `status: COMPLETE`) — a small, newly-opened
  (2026-06-04/05) RESEARCH-track cluster ("Vision Re-Lock & Platform Selection"). Their `spec_ref` fields form a
  **forward-chain across siblings** (WP002's `spec_ref` → WP001's brief; WP003's `spec_ref` → WP002's own
  synthesis output; WP004's `spec_ref` → WP002's triangulation doc) and their true deliverables are
  **un-suffixed root-level files** at `_COMMUNICATION/TEAM_100/` (e.g. `BRIEF_SFA_VISION_RELOCK_AND_PLATFORM_DIRECTION_*.md`,
  `CI_SYNTHESIS_8COMPETITORS_SFA-S004-P001-WP002_*.md`) rather than per-WP subdirectories — WP001 in particular
  has **zero** files that even mention its own WP-ID by name (only linked via the structured `spec_ref` field).
  Archiving 3 of 4 chain-linked files while a 4th (WP001's) has no WP-ID-taggable file at all would be an
  inconsistent partial action, and moving research memory that appears intended to stay live/referenced for
  ongoing platform decisions is a judgment call, not a mechanical one. Subtype `RESEARCH-TRACK-CHAINED-ARTIFACTS`.
  No file touched — team_120 to rule on archive granularity (e.g. archive the whole `SFA-S004-P001` program at
  once, once/if it fully closes, rather than per-WP).
- **`SFA-S003-P004-WP-CB-CONTENT`** — `MISSING-SPEC-ARTIFACT`: see Phase 1 D-2 gap above (pre-existing,
  not authored by this sweep).
- **`SFA-S003-P004-WP-CB-CONTENT`** — `DUPLICATE-ARTIFACT-LEFTOVER`: see Phase 3 detail above (1 identical
  duplicate file left in place, not deleted).
- **`SFA-S003-P004-WP-CB-DSX1-SWEEP`** — `DUPLICATE-ARTIFACT-LEFTOVER`: 2 identical duplicate files left in
  place (see Phase 3 detail above).
- **`SFA-S003-P001-WP001`** — its own `_archive/SFA-S003-P001/ARCHIVE_MANIFEST.md` has flagged, since
  2026-05-22, an unresolved `spec_ref` repoint (`LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md`) as "team_100 action
  required" — still outstanding as of this sweep. Pre-existing, not touched (not this sweep's WP to fix
  unilaterally).

### C. Container/family dirs with no `roadmap.yaml` WP entry (3)

RULE-C requires reading status from `roadmap.yaml`; these have no row there at all, so no deciding field can be
read — the table's own catch-all ("cannot read the deciding field → ESCALATE") applies.

- `_aos/work_packages/S003/SFA-S003-P002-WP-B/` (spec-only) + live `_COMMUNICATION/{TEAM_10,TEAM_110,TEAM_190,team_35}/SFA-S003-P002-WP-B/`
  (14 files) — reads as a family-level container for the (separately DONE-flagged) B1/B2/B3 sub-WPs.
- `_aos/work_packages/S003/SFA-S003-P002-WP-C/` (spec-only, `LOD400_spec.md`, no live comm dir) — same pattern
  for the C1-C6 family.
- `_aos/work_packages/S003/SFA-S003-P004` (bare, no suffix) + live `_COMMUNICATION/{TEAM_100,TEAM_190,TEAM_50}/SFA-S003-P004/`
  (84 files: 6+25+53) — reads as the **whole program-level container** for the WP-CB-* family.

No file touched. Recommend team_120 confirm these are pure organizational containers (safe to leave alone / fold
into their children's future archives) rather than requiring their own `roadmap.yaml` registration.

### D. Large loose non-WP tail — bucketed, not individually archived (≈868 files + ~104 team-root files)

None of these match a WP-ID pattern; RULE-D ("retired, no active reader") could not be mechanically confirmed
for any of them without a deep individual read (a shallow `DEPRECATED|SUPERSEDED|RETIRED` grep found scattered
substring hits that are not authoritative status headers — false-positive risk too high to act on). Bucketed by
folder (file counts as of this sweep):

| Team | Folder | Files |
|------|--------|-------|
| TEAM_100 | `SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF` | 132 |
| TEAM_100 | (team-root loose files) | 104 |
| TEAM_50 | `SFA-PRELAUNCH-QA` | 103 |
| TEAM_100 | `NIMROD_BIO_VISUAL_SYSTEM_CHATGPT` | 42 |
| TEAM_10 | `reports/` | 29 |
| TEAM_100 | `reports/` | 27 |
| TEAM_50 | `reports/` | 26 |
| team_99 | (team-root loose files) | 29 |
| team_00 | (team-root loose files) | 25 |
| TEAM_100 | `MEDIA_CHATGPT_PROJECT` | 24 |
| TEAM_100 | `SFA-PRODUCT-INFO-PACK` | 22 |
| TEAM_100 | `UI_REDESIGN_2026-06` | 22 |
| TEAM_190 | (team-root loose files) | 17 |
| TEAM_100 | `sfa notebooklm 2026-04-23` | 16 |
| TEAM_50 | (team-root loose files) | 16 |
| TEAM_20 | `reports/` | 8 |
| TEAM_80 | `smallfarms_agent_handoff` | 8 |
| TEAM_20 | (team-root loose files) | 10 |
| team_191 | (team-root loose files) | 10 |
| TEAM_80 | `sfa_handoff_v2` | 6 |
| TEMPLATES | (all files — active reference templates, not WP artifacts) | 6 |
| TEAM_80 | `SFA-CROP-DATA-SCOUT-2026-05-26` | 5 |
| TEAM_190 | `inbox/` | 5 |
| TEAM_100 | `SFA-S004-CI-EXTERNAL` | 4 |
| TEAM_80 | (team-root loose files) | 6 |
| TEAM_100 | `SFA-S004-RESEARCH-SUMMARY` | 3 |
| TEAM_190 | `reports/` | 2 |
| TEAM_60 | `reports/` | 2 |
| team_30 | `screenshots/` + root | 4 |
| TEAM_100 | `SFA-S003-CROPBOOK-PROD-DATA-GAP` | 1 |
| TEAM_100 | `outbox_templates` | 1 |
| TEAM_100 | `SFA-S003-P004-WP-CB-FROST-DATA` (WP-ID-shaped but **no roadmap.yaml row** — likely an abandoned/renamed idea) | 1 |
| TEAM_100 | `specs/` | 1 |
| TEAM_190 | `archive/` (a **per-team** local "archive" subfolder, distinct from the top-level `_archive/`) | 1 |
| team_191 | `archive/` (same pattern) | 1 |
| team_35 | (team-root + `SFA-S003-P002-WP-B`) | 2 |
| TEAM_60 | (team-root, none) | 0 |
| (root) | `_COMMUNICATION/{README,LEAN_KIT_INTEGRATION,ROADMAP}.md` | 3 — active infra docs, **not** WP artifacts, KEEP, no ambiguity |

`ESCALATE` (ruling needed): every row above except the explicit `TEMPLATES/` and `(root)` infra-doc rows, which
are unambiguous KEEP (active reference material, no version tag needed, no closed-WP association). team_120 to
triage by folder — recommend prioritizing `SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF` (132), `SFA-PRELAUNCH-QA`
(103), and the TEAM_100 team-root pile (104) as the highest-value next passes given size.

### E. Systemic findings (process-level, not per-item)

- **E-1 — Case-sensitivity blind spot in the procedure's own literal commands.** Both the Phase-0 baseline
  formula and the Phase-2 enumerate command (`_COMMUNICATION/team_*`) use a case-sensitive glob. This domain
  mixes `TEAM_NN` (uppercase, 8 dirs) and `team_nn` (lowercase, 6 dirs) — the literal commands only ever see
  the lowercase half, undercounting the true backlog by **~5.5x** (245 reported vs. 1366 true). The context
  brief for this sweep noted a prior "~34 ARCHIVE candidates" estimate was unverified/possibly stale — this is
  almost certainly why: it was very likely derived from the same case-blind query. Recommend team_120 patch the
  procedure's enumerate commands to `find _COMMUNICATION -maxdepth 1 -type d -iname 'team_*'` (case-insensitive)
  fleet-wide, since any other domain with mixed-case team dirs will hit the same undercount.
- **E-2 — Informal status vocabulary, undocumented.** This domain's `roadmap.yaml` uses `DONE` (32×) plus
  `ACTIVE`, `ROUTED`, `VALIDATE`, `REGISTER`, `OPEN`, `PLACEHOLDER` (14× combined) as `status` field values —
  none are in the classification table's documented enum (`COMPLETE/CLOSED/COMPLETE_SUPERSEDED/SUPERSEDED/ARCHIVED/DRAFT/PLANNED/DEFERRED`).
  A prior archival pass evidently already treated `DONE` as archival-equivalent to `COMPLETE` for 10 of the 32
  WPs (see ESCALATE §A) — i.e. local practice already diverged from the documented enum before this procedure
  existed. Recommend team_120 either ratify `DONE` as a documented `COMPLETE`-equivalent synonym (with a
  backfill of the `status` field fleet-wide) or explicitly reject it and require normalization — either way,
  this removes the ambiguity for the next weak-engine run.
- **E-3 — `active_milestone: "S003"` may be stale.** `SFA-S004-P001-WP001..004` (dated 2026-06-04/05) and the
  `SFA-S003-P004-WP-CB-*` backlog (`REGISTER`/`PLACEHOLDER` items, undated) both postdate typical S003 closure
  activity, yet the project header still names S003 as active. Not blocking (no STALE-MILESTONE-WP row was
  triggered — no DRAFT/PLANNED/DEFERRED WP pointed at a *closed* milestone), but worth a domain-owner check.
- **E-4 — 2 false-positive V-1 hits** inside `_archive/_BRANCH_RECONCILIATION_2026-06-02/...` — the procedure's
  own exclusion regex (`/_archive/`) assumes a leading slash that isn't present for root-relative paths. Not
  real drift; flagged so the same regex gap doesn't cause a false alarm in another domain's report.

---

## After (metrics)

```
after (literal, same undercounting formula as baseline): { unarchived_comm_files: 245, open_wps: 4, archive_dirs: 34 }
after (true):     { unarchived_comm_files: 1354, open_wp_dirs: 58, archive_dirs: 34, quarantined: 0 }
```
delta: `{ archived: 12 files across 4 WPs, quarantined: 0, comm_files_cleared: 12 (true count only — the
literal/undercounted metric cannot see this delta, since all 12 moved files lived under uppercase TEAM_* dirs) }`

---

## Session notes

- Executed in isolated worktree `/Users/nimrod/Documents/AOS_V5/SmallFarmsAgents-sweep` (branch `main`), per
  instruction — the primary checkout at `/Users/nimrod/Documents/AOS_V5/SmallFarmsAgents` (branch
  `chore/classb-dead-block-retire`) was never touched.
- **Nothing committed or pushed.** `git status --porcelain` shows: 1 new file (`_archive/SFA-S002-P001/ARCHIVE_MANIFEST.md`),
  3 modified files (`_aos/roadmap.yaml`, 2 other manifests), 12 renamed/moved files (git-detected as `R`). All
  staged/present in the working tree for team_60 to review and commit.
- Application source code was never touched — all actions confined to `_COMMUNICATION/`, `_archive/`, and
  `_aos/roadmap.yaml` per instruction.
