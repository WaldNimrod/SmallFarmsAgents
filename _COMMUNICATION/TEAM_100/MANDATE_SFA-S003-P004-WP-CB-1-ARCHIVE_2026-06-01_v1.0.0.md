---
id: MANDATE_SFA-S003-P004-WP-CB-1-ARCHIVE_v1.0.0
from: team_100 (Chief System Architect — smallfarmsagents spoke)
to: team_191 (Git / Files)
date: 2026-06-01
type: ARCHIVE_MANDATE
wp: SFA-S003-P004-WP-CB-1
project: smallfarmsagents
status: ACTIVE
trigger: "WP-CB-1 UI slice LOD500_LOCKED (team_190 L-GATE_V R3 PASS_WITH_FINDINGS, verdict 8018df6)"
---

# Archive Mandate — SFA-S003-P004-WP-CB-1 (Crop Book v1 UI slice)

WP-CB-1 reached **LOD500_LOCKED** on 2026-06-01 (team_190 L-GATE_V R3 PASS_WITH_FINDINGS, verdict commit
`8018df6`). Per the WP-closure protocol, archive the WP's process artifacts. The **code stays in place** on
the branch (`sfa_delivery/`, `public_assets/`) — only the `_COMMUNICATION/` process trail is archived.

## Scope to archive → `_archive/SFA-S003-P004-WP-CB-1/`
Move (with an `ARCHIVE_MANIFEST.md` index, ADR042 step-1):
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/` — DISPATCH (UI), FIELD_INTERFACE_MAP, the three
  VALIDATION_MANDATEs (LGATE-V + R2 + R3), the wc completion report.
- `_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-1/` — BUILD_REPORT_UI.
- `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-1/` — the three verdicts (R1, R2, R3).

## Do NOT archive / leave in place
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/` — the design SSoT (referenced live by
  `documentation/09-design-system/`); keep in place.
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/CROP_ART_MASTERS/` — **active**, still receiving art batches
  (feeds WP-CB-1-patch01); keep in place.
- The R3 verdict file should be **copied** (not moved) into the archive if you prefer a self-contained bundle,
  but the canonical one stays discoverable until patch01 closes.
- `_aos/roadmap.yaml`, `documentation/`, all `sfa_delivery/` code — untouched.

## Open follow-up (do not close these)
`SFA-S003-P004-WP-CB-1-patch01` (ELIGIBLE) carries the L-GATE_V findings + watercolor art wiring — leave its
artifacts active. `SFA-S003-P004-WP-CB-MIG2` (ELIGIBLE) likewise.

## Output
- Create `_archive/SFA-S003-P004-WP-CB-1/ARCHIVE_MANIFEST.md` (what moved, from→to, commit).
- Set `archive_ref` on the WP-CB-1 roadmap row (single-writer: hand the one-line value back to team_100, or
  team_191 under its `_aos/` bootstrap mandate per the Directory Authority table).
- Commit on `claude/wp-cb-1-ui-2026-05-31`; message: `archive(WP-CB-1): process artifacts → _archive (ADR042)`.

*Issued by team_100 · 2026-06-01.*
