# ARCHIVE MANIFEST — SFA-S003-P004-WP-CB-UI-ALIGN (Class A)

**Archived:** 2026-06-02 · **By:** team_191 (executed by team_100 orchestration) · **Trigger:** ADR042 step-1 (WP closure)
**Closure:** L-GATE_V **Round 3 PASS** (team_190 / Cursor, non-Claude) · **Roadmap:** DONE / LOD500_LOCKED
**Live:** https://sfa.nimrod.bio @ `f66360d` (fix `b5ad8e5` cherry-picked to main) · **Mandate:** `team_191/ARCHIVE_MANDATE_2026-06-02_v1.0.0.md`

## What this WP delivered (Class A, LIVE)
White-green palette (cream killed, `--gj-paper #f8fbf8`) · team_35 `.sh`/`.sh__nav` app-shell site-wide (`#sfa-logo`) ·
`/calc` fixed (JS load, 14 calcs / 6 interactive, `/calc/print` + CSV export) · crop pages humanized (Hebrew
enums/labels). Build = team_10 (Sonnet) · internal QA = team_50 (Haiku) · gates = team_190 (Cursor, non-Claude, IR#1/#5).

## Gate trail
| Gate | Result | Engine |
|---|---|---|
| L-GATE_E | PASS | team_00 |
| L-GATE_S | PASS_WITH_FINDINGS (3 minor, actioned) | Cursor |
| L-GATE_V R1 | FAIL (PDF 404, crop-page raw keys, empty calc selector) | Cursor |
| L-GATE_V R2 | FAIL (residual `family:` leak) | Cursor |
| L-GATE_V R3 | **PASS** (final) | Cursor |

## Moved here (ADR042 — `_COMMUNICATION/` process trail; from → `_archive/SFA-S003-P004-WP-CB-UI-ALIGN/`)
- `TEAM_100/` ← `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-ALIGN/` — L-GATE_S + L-GATE_V validation mandates + verdict notifications.
- `TEAM_50/` ← `_COMMUNICATION/TEAM_50/SFA-S003-P004-WP-CB-UI-ALIGN/` — internal visual QA, live deploy QA, R2 re-QA.
- `TEAM_190/` ← `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-ALIGN/` — L-GATE_S + L-GATE_V R1/R2/R3 verdicts + evidence (R1/R2/R3 screenshot sets). *(R2/R3 verdicts were authored by the Cursor session and were uncommitted in the working tree; captured into the archive here so the closure proof is preserved.)*
- `team_99/` ← `_COMMUNICATION/team_99/SFA-S003-P004-WP-CB-UI-ALIGN/` — deploy mandates (initial + R3), deploy reports v1.0.0–v1.0.3, V01 PDF request.
- `team_191/` ← `_COMMUNICATION/team_191/SFA-S003-P004-WP-CB-UI-ALIGN/` — the archive mandate.

## Left in place (NOT archived)
- `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-ALIGN/` (LOD200 + LOD400_LOCKED spec) — discoverable spec record.
- `_aos/roadmap.yaml` — WP entry DONE / LOD500_LOCKED with full gate_history + CLOSURE.
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/` — design SSoT, referenced live by `documentation/09-design-system/`.
- `sfa_delivery/` code — live on main / sfa.nimrod.bio.
- Inbox `MSG-HUB-20260602-00X` messaging-log entries in team_99/team_100 inboxes (messaging audit trail).

## Open follow-ups (separate tracks — NOT closed by this archive)
- **WP-CB-DATA** — populate `crop_field_enrichment` in the uPress MySQL mirror → enables calc book-chip binding on crop-select.
- **WP-CB-UI-CLASSB** — Class B content design on the now-built `.sh` shell.
- **Hub team_100 actor-key** — `MSG-HUB-20260602-901` (DB-backed messaging; spoke currently file-fallback).
- **team_60 FTPS rotation-sync runbook** — DONE (merged to main): `documentation/05-admin-and-operations/FTPS_CRED_ROTATION_SYNC_RUNBOOK.md` + `scripts/sync_ftps_cred.sh`.
