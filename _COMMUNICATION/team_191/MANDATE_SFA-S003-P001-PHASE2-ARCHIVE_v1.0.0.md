---
id: MANDATE_SFA-S003-P001-PHASE2-ARCHIVE_v1.0.0
from: team_100
to: team_191 (Git, Archive & File Governance)
date: 2026-05-13
type: ARCHIVE_MANDATE
project: SmallFarmsAgents (spoke)
status: OPEN
authority: ADR042 / Iron Rule #15
related_wp: SFA-S003-P001-WP004
next_step: "Move completed S003 Phase 1 + Phase 2 WP artifacts to _archive/SFA-S003-P001/ preserving directory structure."
handoff_to: team_191
handoff_context_pointer: _COMMUNICATION/team_191/MANDATE_SFA-S003-P001-PHASE2-ARCHIVE_v1.0.0.md
---

# Archive Mandate — SFA-S003-P001 Phase 1 + Phase 2 Complete

S003 (ספר גידולים) program is COMPLETE. All four WPs are LOD500_LOCKED.
Artifact archive required per Iron Rule #15 (ADR042). Same pattern as
SFA-S002-P001 archive (precedent: this directory's
`MANDATE_SFA-S002-P001-PHASE2-ARCHIVE_v1.0.0.md`).

## WPs to archive

| WP | Status | Artifacts source |
|----|--------|------------------|
| SFA-S003-P001-WP001 (Schema LOD200) | LOD500_LOCKED | `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/` |
| SFA-S003-P001-WP002 (DB + Seed) | LOD500_LOCKED | `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP002/`, `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP002/` |
| SFA-S003-P001-WP003 (Flask Blueprint) | LOD500_LOCKED | `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP003/`, `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP003/` |
| **SFA-S003-P001-WP004 (WordPress Integration)** | **LOD500_LOCKED** | `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP004/`, `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP004/`, `_COMMUNICATION/team_190/SFA-S003-P001-WP004/` |

Also archive cross-WP S003 communication artifacts:
- `_COMMUNICATION/TEAM_100/SFA-S003-P001/EXTERNAL_VALIDATION_BUNDLE/` (joint WP002+WP003 bundle from Phase 1)
- `_COMMUNICATION/team_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md` + `_R2_v1.0.0.md` (joint Phase 1 verdicts)
- `_COMMUNICATION/team_190/SFA-S003-P001-WP002-LGATEV-VERDICT_v1.0.0.md`
- `_COMMUNICATION/team_190/SFA-S003-P001-WP003-LGATEV-VERDICT_v1.0.0.md`
- `_COMMUNICATION/team_190/SFA-S003-P001-WP003-PATCH01-VERDICT_v1.0.0.md`

## Inbox MSGs to archive (post-handling)

Per ADR043 v1.2.0 §7 the canonical archive endpoint is
`POST /api/messaging/archive`. File-fallback (if API unavailable for team_191):
`git mv` to `_COMMUNICATION/{team}/archive/`.

WP004-related MSGs:
- `_COMMUNICATION/team_10/MSG-HUB-20260510-001.md` (DISPATCH MSG team_100→team_10)
- `_COMMUNICATION/team_100/MSG-HUB-20260511-001.md` (BUILD COMPLETE team_10→team_100, lives in hub but informational)
- `_COMMUNICATION/team_190/MSG-HUB-20260513-001.md` (L-GATE_V request team_100→team_190)
- `_COMMUNICATION/team_190/inbox/MSG-team100-to-team190-S003-WP004-LGATES-REQUEST-2026-05-09.md`
- `_COMMUNICATION/team_190/inbox/MSG-team100-to-team190-S003-WP004-LGATES-R2-REQUEST-2026-05-10.md`
- `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-2026-05-10.md`
- `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LOD400-VERDICT-R2-2026-05-10.md`
- `_COMMUNICATION/TEAM_100/MSG-team190-to-team100-S003-WP004-LGATEV-VERDICT-2026-05-13.md`

## Action

1. Move all completed WP artifacts to `_archive/SFA-S003-P001/` preserving directory structure (`team_10/SFA-S003-P001-WP00X/`, `team_100/SFA-S003-P001-WP00X/`, `team_190/SFA-S003-P001-WP00X/`).
2. Archive the cross-WP S003 communications listed above.
3. Move handled MSGs to their respective `archive/` subdirectories (via `POST /api/messaging/archive` per ADR043 §7, or file-fallback).
4. Commit: `archive(S003): Phase 1+2 WP artifacts → _archive/SFA-S003-P001/`

This should resolve `validate_aos.sh` Check 15 (stale artifacts for completed WPs in `_COMMUNICATION/`).

## Authority limits (per team_191 governance contract)

- MAY move (not delete) artifacts to `_archive/`
- MAY NOT modify `_aos/roadmap.yaml` or `_aos/governance/`
- MAY NOT touch application source code
- Branch-safe: write the archive commits on a feature branch; do not push to `main` without team_00 review (per recent workflow concerns about main hygiene)

## Cross-reference

- WP004 L-GATE_V verdict: `_COMMUNICATION/team_190/SFA-S003-P001-WP004/LGATEV-VERDICT_v1.0.0.md` (PASS_WITH_FINDINGS, 2026-05-13)
- WP004 BUILD_REPORT: `_COMMUNICATION/TEAM_10/SFA-S003-P001-WP004/BUILD_REPORT_v1.0.0.md`
- Production URL: `https://www.nimrod.bio/crop-book/` (live, no operational dependency on archive)

## Follow-up items NOT in archive scope (out of team_191 mandate)

These are flagged for team_00/team_100 decision; do NOT archive their tracking artifacts (yet):
- F-190-WP004-LV-01 (out-of-mandate prod deploy policy) — team_00 decision pending
- F-190-WP004-LV-02 (WP003 patch02 candidate for test-harness debt) — team_100 decision pending
- `GCR_AOS_MESSAGING_INFRA_HARDENING_2026-05-10_v1.0.0.md` (live GCR awaiting hub-side response) — keep in `_COMMUNICATION/TEAM_100/`
- `GCR_UPRESS_FTPS_PROTOCOL_2026-05-10_v1.0.0.md` (team_10's ancillary GCR) — keep in `_COMMUNICATION/TEAM_100/`

---

*Mandate issued 2026-05-13 by team_100.*
*Branch: `claude/gallant-elbakyan-727a60` · Commit: pending this session*
