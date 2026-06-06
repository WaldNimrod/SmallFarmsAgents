# HANDOFF (full) — team_100 → team_100 — crop-book follow-ups: RESEARCH-FIRST on an isolated branch

**Date:** 2026-06-07 · **From:** team_100 (this session) · **To:** team_100 (next session) · **Depth:** full
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · **Base:** `main` @ **`f3e693c`** (origin == local at handoff time)
**Live:** https://sfa.nimrod.bio (assets `?v=1780691715`) — WP-CB-MOBILE is COMPLETE/LOD500_LOCKED/archived.

## SESSION TASK (next session)
Pick up the **two carried-forward follow-ups** from WP-CB-MOBILE and **begin with RESEARCH** (design/LOD phase — do NOT jump to build). The full code-grounded scope is already written — treat it as your directive/spec:

➡ **`_COMMUNICATION/team_100/REPORT_WP-CB-MOBILE_FOLLOWUPS_calc-and-deep-provenance_2026-06-07.md`**

Two candidate WPs in that report:
1. **WP-CB-CALC** — wire the calculator's 8 stub goals (6/14 currently live). All 14 are implemented in Python; the work is a Python→JS port (cheap for 3 non-date stubs) + a **JS date engine that consumes the already-built-but-dead time-anchor** (the 4–5 date calcs) + a product decision on `water` (no model exists).
2. **WP-CB-DEEP-PROVENANCE** — REASSESSED as small: Deep source pills **already render in production** (lettuce: 32). The real gap = crop **data-coverage** (crops without `crop_field_enrichment` rows fall to a fallback that strips provenance) + a **stale/false comment** at `CropBookViewController.php:693-696`. Mostly data + doc cleanup, not a pipeline rebuild.

## ⚠ BRANCH DISCIPLINE — work on a NEW ISOLATED BRANCH (mandatory)
A **parallel session is live on `main`** working on the **UI/interfaces redesign** (`UI_REDESIGN_2026-06` — untracked `_COMMUNICATION/TEAM_100/UI_REDESIGN_2026-06/mockups/` + a `.claude/launch.json` entry). To avoid collisions:
- **Step 0:** branch off current main, do NOT commit follow-up work to `main`:
  ```
  git fetch origin && git checkout main && git pull --ff-only origin main
  git checkout -b claude/cb-followups-2026-06-07
  ```
- Work the calc/deep-provenance follow-ups ONLY on `claude/cb-followups-2026-06-07`.
- **Do NOT touch** the parallel session's WIP (`UI_REDESIGN_2026-06/`, the `.claude/launch.json` entry) — leave them untouched even though they show in `git status`.
- The calculator surface (`calc_dash.php`, `crop-book-v1.js`) and the UI-redesign effort may eventually overlap — **coordinate with the UI_REDESIGN session via Nimrod before merging to main**, and rebase your branch on main before any merge.

## RESEARCH-FIRST steps (next session)
1. Read the report (above) + this handoff + `_aos/roadmap.yaml`.
2. Create the isolated branch (Step 0 above).
3. **Research / design phase (no build yet):**
   - **Calc:** confirm the Python↔JS parity plan for the 3 cheap ports; design the **JS date engine** + how `runEngine()` will consume `state.anchor` + date inputs (today ignored — `crop-book-v1.js:624-662`); list the book-fields to plumb through `QB_BOOK_ALIAS` + engine chips; decide date-aware result/session rendering.
   - **Deep-provenance:** verify live-mirror coverage — `SELECT COUNT(*) FROM crop_field_enrichment` on uPress (ask Nimrod / via an authorized path), survey which crops lack enrichment rows; confirm the stale comment fix.
   - **Open decisions for team_00:** (a) `water` calculator — define a model or drop the goal; (b) account-scoped session persistence (currently per-device `sessionStorage`); (c) surface `harvest_window` (#5) as a 15th goal; (d) is the crop-enrichment data-coverage work in scope here or a separate data WP.
4. **Author the LOD** for WP-CB-CALC (phased: A=cheap ports, B=date engine, C=water decision) + the disposition for WP-CB-DEEP-PROVENANCE; add roadmap REGISTER/OPEN entries (team_00 prioritization). THEN proceed to build (git-isolated; team_100 commits) only after the LOD + team_00 go.

## Current product/repo state (verified at handoff)
- WP-CB-MOBILE: **COMPLETE / LOD500_LOCKED**, archived to `_archive/SFA-S003-P004-WP-CB-MOBILE/` (manifest + CLOSURE_RECORD). Live, validated GO by team_50.
- `validate_aos` **0 FAIL** (30 PASS). origin == local @ `f3e693c`. Suite 217/217 (PHP delivery).
- Deploy: **direct from the Mac** works once Nimrod opens the current external IP on uPress (dynamic allowlist — `curl https://api.ipify.org`, ask, then `bash scripts/ftp_deploy_sfa_ui.sh`). Closed-IP symptom = TCP `ftp.s1240.upress.link:21` timeout.

## MANDATORY READS (next session)
- The report (the task spec) · this handoff · `_aos/roadmap.yaml` · `CLAUDE.md`
- Prior session-close handoff: `_COMMUNICATION/team_100/HANDOFF_SELF_100_WP-CB-MOBILE-CLOSED_2026-06-06.md`
- Memories: `project_calculator_client_math_gap` · `feedback_shared_include_scope_var_clobber` · `feedback_worktree_vendor_autoload_trap` · `reference_sfa_deploy_topology`
- Key code: `organic_market_agent/crop_book/calculators.py` (14 calcs), `sfa_delivery/public_assets/js/crop-book-v1.js` (`CALC` L31-129, `wireQuestionBuilder` L552+), `sfa_delivery/templates/pages/calc_dash.php`, `sfa_delivery/app/Controllers/CropBookViewController.php` (`buildSourceClasses` L1010, fallback L835-962).

## Operating reminders
IR#1/#5 cross-engine (team_50/team_190 external visual/constitutional; team_100 never self-issues the binding verdict). IR#4 single-writer roadmap. Deploys auth-gated → deploy from Mac after IP open, or route to team_99. Commit defensively (explicit paths; verify ancestry — governance auto-syncer (Model B/ADR054) + the parallel UI session both touch the tree). Pre-push runs validate_aos — keep 0 FAIL. **Route tests must seed RICH payload** (the WP-CB-MOBILE 500 lesson — empty fixtures hide real-data crashes); **smoke the LIVE page after any deploy**.
