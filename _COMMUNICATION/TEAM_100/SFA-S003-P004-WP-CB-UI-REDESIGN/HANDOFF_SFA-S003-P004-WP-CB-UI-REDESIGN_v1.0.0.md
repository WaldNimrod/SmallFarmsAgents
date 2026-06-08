# ACTIVATION — team_100 — SFA-S003-P004-WP-CB-UI-REDESIGN

**Role:** team_100 (Chief System Architect) · **Engine:** Claude Code · **Gate:** L-GATE_E → build · **Status:** READY
**Task (mandate):** execute the WORKPLAN — ship the full redesigned version of SFA to production.

## ▶ Your task = the WORKPLAN (read it, then drive it)
`_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-REDESIGN/WORKPLAN_full-version_2026-06-08_v1.0.0.md`
Run **WI-0 → WI-10**: DS fold (DSX-1 icons + DSX-2 type scale + mock-v2) → shell unify → build 6 public surfaces → calc **re-skin** → QA → deploy to `sfa.nimrod.bio` → cross-engine L-GATE_V → LOD500_LOCK → archive.

## Inputs (read first)
- **Design (LOD300, ready):** `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-REDESIGN/handoff_ui_redesign/` — `README.md` + `00_DESIGN_BOARD.html`; `mock-v2.css` + `sfa-icons.js` = the DSX deltas.
- **Principles/history:** `_COMMUNICATION/TEAM_100/UI_REDESIGN_2026-06/UX_DIRECTION_BRIEF_v0.1.md`.
- **Calc = WP-CB-CALC LOD500_LOCKED** → **WI-7 is RE-SKIN ONLY; never touch the engine** (`crop-book-v1.js` / goals / parity).

## State (done — not blockers)
WP registered (REGISTER / L-GATE_E) · FTP allowlist OPEN · calc locked · `validate_aos` 0 FAIL · committed `4b1470f`.

## Startup + cautions
Read `CLAUDE.md` → `_aos/governance/team_100.md` → the WORKPLAN. RICH route fixtures (avoid the `$notes` 500) · `qa_probe.mjs` for every RTL/overflow/mobile check (never curl-only) · commit defensively (explicit paths — AOS auto-syncer touches `_aos/`).

<!-- canonical short activation prompt; full server handoff intentionally omitted (the session reads team_100.md at startup). DB-inbox capture degraded → _COMMUNICATION/_log/messages.log (actor key unset on Mac, ADR043 §15.4). -->
