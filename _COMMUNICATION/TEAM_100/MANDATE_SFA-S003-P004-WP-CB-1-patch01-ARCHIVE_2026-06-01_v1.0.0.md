---
id: MANDATE_SFA-S003-P004-WP-CB-1-patch01-ARCHIVE_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_191 (Git / Files)
date: 2026-06-01
type: ARCHIVE_MANDATE
wp: SFA-S003-P004-WP-CB-1-patch01
project: smallfarmsagents
status: ACTIVE
trigger: "patch01 LOD500_LOCKED (team_190 L-GATE_V PASS_WITH_FINDINGS, verdict c2dfa47)"
---

# Archive Mandate — SFA-S003-P004-WP-CB-1-patch01 (UI follow-ups + watercolor art)

patch01 reached **LOD500_LOCKED** on 2026-06-01 (team_190 L-GATE_V PASS_WITH_FINDINGS, verdict commit
`c2dfa47`). Archive the WP's **process trail** only — code/art stay in place on the branch.

## Archive → `_archive/SFA-S003-P004-WP-CB-1-patch01/` (ADR042, with ARCHIVE_MANIFEST.md)
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1-patch01/` — VALIDATION_MANDATE.
- `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1-patch01/` — BUILD_REPORT.
- `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1-patch01/` — LGATE-V_VERDICT (copy; keep canonical discoverable).

## Leave in place (do NOT archive)
- All `sfa_delivery/` code + `public_assets/` art (the shipped patch).
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/` (design SSoT) and
  `…/CROP_ART_MASTERS/` (active art library — may still receive batches).
- `_aos/roadmap.yaml`, `_aos/work_packages/…/SFA-S003-P004-WP-CB-1-patch01/LOD200_spec.md`,
  `documentation/`.

## Still open (do not close)
- `SFA-S003-P004-WP-CB-MIG2` (ELIGIBLE) — schema expansion (13-topic taxonomy + 7 JMF field groups).
  Tracks: F-CB1-UI-01 (field_policy canon-alignment), F-50-patch01-01 (non-kg revenue conversion — may
  fold into a future UI patch instead), season_window data gap.

## Output
- Create `_archive/SFA-S003-P004-WP-CB-1-patch01/ARCHIVE_MANIFEST.md`.
- Set `archive_ref` on the patch01 roadmap row (hand the one-line value to team_100, single-writer).
- Commit on `claude/wp-cb-1-ui-2026-05-31`; message: `archive(WP-CB-1-patch01): process artifacts → _archive (ADR042)`.

*Issued by team_100 · 2026-06-01.*
