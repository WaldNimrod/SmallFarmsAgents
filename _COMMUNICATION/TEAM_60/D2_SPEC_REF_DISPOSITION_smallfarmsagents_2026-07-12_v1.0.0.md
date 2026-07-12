---
id: D2_SPEC_REF_DISPOSITION_smallfarmsagents_2026-07-12_v1.0.0
type: DISPOSITION RECORD
from: team_60 (DevOps/Platform)
to: team_120 (Ambassador — custodian), team_100 (Chief System Architect)
date: 2026-07-12
domain: smallfarmsagents (SFA)
wp: AOS-V5-M11-WP-FLEET-VERSION-HYGIENE-SWEEP (hub-native, file-canonical — ADR034 R10)
re: CENTRALIZED_SWEEP_REVIEW_team_120_M11_FLEET_HYGIENE_2026-07-10_v1.0.0.md §6 (D2 masked Check-4 spec_ref)
---

# D2 spec_ref fix-or-waive — SFA — disposition record

Executes §6 of the centralized sweep review for SFA's 2 broken `spec_ref` items.

## 1. `SFA-S003-P004-WP-CB-CONTENT` — WAIVED

**Broken ref:** `spec_ref: "_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CONTENT/SPEC_2026-06-09_v1.0.0.md"`

**Verification:** fleet-wide `find . -iname "SPEC_2026-06-09*"` from the domain root returns zero results. The file
does not exist live or archived anywhere in the tree, despite the WP's own `_archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md`
citing it as an evidence artifact at line 32.

**Disposition:** WAIVE (not FIX) — the review's own rule is *"FIX (repoint) where the real artifact exists; formal
per-domain WAIVER where it is genuinely gone/never produced."* No real artifact exists to repoint to; nothing was
invented.

**team_100 sign-off: APPROVED 2026-07-12** (coordinator message: *"CB-CONTENT spec_ref WAIVER: APPROVED (SPEC file
confirmed gone fleet-wide; OPS/content WP, no as-built). Proceed."*). This clears the §10-item-3 pending condition.

**Actions taken (updated 2026-07-12 after team_100 sign-off + Check-5 constraint discovered):**
- `_aos/roadmap.yaml`, `SFA-S003-P004-WP-CB-CONTENT` row — the dead `spec_ref` path was **removed**. team_100
  directed "null/remove the field," but a literal YAML `null` breaks `validate_aos.sh` **Check 5** (required-fields:
  every WP must carry a non-empty `spec_ref`; Check 5 has no placeholder exception). The value was therefore set to
  the **recognized `"TBD"` waiver placeholder** — the exact token in Check 4's skip-list (`TBD`/`null`/`None`/`''`)
  AND the established fleet waiver marker (review §6 uses `spec_ref: TBD` for the parallel no-as-built nimrod-bio
  `NB-S001-P001-WP001` waiver). `"TBD"` satisfies BOTH Check 4 (skipped, not resolved) and Check 5 (present,
  non-empty). A `spec_ref_waiver:` field was added on the row recording the gone-artifact fact + the team_100
  sign-off + this disposition ref.
- `_archive/SFA-S003-P004-WP-CB-CONTENT/ARCHIVE_MANIFEST.md` — "2026-07-12 disposition (team_60)" addendum added
  after the existing pre-existing-gap note, cross-referencing the roadmap waiver.
- No document content invented; no as-built reconstructed.

**Result:** `validate_aos.sh` **Check 4 now PASSES** (all spec_refs resolve or are recognized placeholders) and
**Check 5 still PASSES**.

## 2. `SFA-S003-P001-WP001` — already fixed, no action

**Current ref:** `spec_ref: "_archive/SFA-S003-P001/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md"`

**Verification (re-run this pass):** the file exists at that exact path (confirmed via `ls -la`, 27927 bytes,
dated 2026-05-23). The review listed this as *"spec_ref repoint outstanding since 2026-05-22"* — that repoint has
since been completed (by an earlier, unattributed pass) and the current `roadmap.yaml` state already reflects the
fix.

**Disposition:** already fixed, no action needed.

## 3. `SFA-S003-P004-WP-CB-DSX1-SWEEP` — FIXED (repoint; team_100 authorized 2026-07-12)

Surfaced by `validate_aos.sh` Check 4 during this pass — a second broken `spec_ref` NOT listed in the review's §6
table. team_100 authorized the fix (coordinator message: *"DSX1-SWEEP spec_ref: AUTHORIZED to fix (it's a clean
correct repoint, not a guess)."*).

- **Was:** `spec_ref: "_COMMUNICATION/team_110/SFA-S003-P004-WP-CB-DSX1-SWEEP/HANDOFF_SFA-S003-P004-WP-CB-DSX1-SWEEP_v1.0.0.md"` (pre-archive path; the artifact was moved to `_archive/` by an earlier closure pass, leaving the ref dangling).
- **Now:** `spec_ref: "_archive/SFA-S003-P004-WP-CB-DSX1-SWEEP/team_110/HANDOFF_SFA-S003-P004-WP-CB-DSX1-SWEEP_v1.0.0.md"` — the real archived location (file confirmed present, 3679 bytes). Clean mechanical repoint, redirect exists.

## Check 65 (C-MB5 governance-cache count) — delta identified for team_100 re-stamp

Not a team_60 fix (gov-cache re-stamp is team_100/120 authority, IR#12) — reported here for team_100 to re-stamp.

- **Symptom:** `AOS_GOVERNANCE_VERSION.yaml` `cache_file_count: 294`; on-disk `find -type f` over `_aos/{governance,methodology,lean-kit}` = **295** (+1).
- **The exact delta file:** `_aos/methodology/SPEC_CONVENTIONS_KERNEL_v1.0.0.md` — the **only** file in the three
  cache dirs with a birth time (2026-07-10T00:54:18) **after** the stamp's `synced_at` (2026-07-08T22:22:10Z).
  (mtime was useless — a 07-10 00:54 bulk re-sync reset every methodology file's mtime; birth time isolated it.)
- **Provenance:** legitimate hub-originated file — **byte-identical** to hub source
  `agents-os/methodology/SPEC_CONVENTIONS_KERNEL_v1.0.0.md`, tracked in hub git (added @ `ec23003`, created in hub
  2026-07-08 20:41). It reached the spoke via the 07-10 partial re-sync that propagated the file but did not
  re-write the stamp count.
- **Recommended action (team_100/120):** re-stamp only — bump `cache_file_count` 294 → 295 via
  `aos_sync_all.sh` / `aos_gov_stamp.sh`. **Do NOT delete** — it is canonical governance content, not stray.
  team_60 took no action on the cache or the stamp (IR#12).

---
*team_60 · 2026-07-12 · M11 fleet version-hygiene sweep, SFA domain, D2 execution (updated post team_100 sign-off + DSX1 authorization + Check-65 delta report).*
