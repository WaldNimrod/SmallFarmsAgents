# ARCHIVAL MANDATE — WP-CB-MOBILE (LOD500_LOCKED) — team_100 → team_191 — v1.0.0

**Date:** 2026-06-06 · **From:** team_100 · **To:** team_191 (Git/Files) · **WP:** SFA-S003-P004-WP-CB-MOBILE
**Trigger:** WP reached **LOD500_LOCKED** (team_50 binding L-GATE_V = GO, 2026-06-06). Iron Rule #15 requires completed-WP artifacts be archived out of `_COMMUNICATION/`. The roadmap entry stays (status flips `VALIDATE → COMPLETE` once archived).

## Archive these WP artifact dirs → `_archive/SFA-S003-P004-WP-CB-MOBILE/`
- `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-MOBILE/` (LOD400 build spec, design mandate, team_100 sweep + screenshots)
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-MOBILE/` (the v4 design package: MOBILE_DESIGN, README, prototypes, mobile-fixes.css)
- `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-MOBILE/` (QA mandate, activation prompt, QA_REPORT_2026-06-06, qa_run evidence, MSG)
- `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-MOBILE/` + the team_99 deploy MSGs (DEPLOY_AUTHORIZED / DEPLOY_UNBLOCK / DEPLOYED-STANDDOWN)

Write an `ARCHIVE_MANIFEST.md` (mirror the prior WP-CB-UI-FIDELITY manifest format) listing moved paths + the closing verdict (team_50 GO, live `?v=1780691715`, commit `a18816c`).

## Do NOT archive / leave in place
- `_aos/roadmap.yaml` (SSOT — team_100/100 lane), `CLAUDE.md`, `documentation/` (deploy runbook + sfa-delivery-tier doc corrections), and the live `sfa_delivery/` source.

## After archival
1. Flip the roadmap WP-CB-MOBILE `status: VALIDATE → COMPLETE` (or notify team_100 to).
2. `validate_aos.sh .` → expect **0 FAIL** (Check 15 clears once `_COMMUNICATION/` is free of the completed-WP artifacts).
3. Verify ancestry + commit on the active branch (`main`) with explicit paths; push.

Context: launch blocker CLEARED — site live + validated GO. This is housekeeping closure only.
