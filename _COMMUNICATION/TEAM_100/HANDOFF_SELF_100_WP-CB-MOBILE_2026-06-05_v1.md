# HANDOFF (full) — team_100 → team_100 — SFA crop-book mobile remediation + program consolidation

**Date:** 2026-06-05 · **From:** team_100 (Opus, this session) · **To:** team_100 (next session) · **Depth:** full
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · **Branch:** `claude/ui-polish-hub-cropbook-2026-06-03` (SHARED — see §Git)
**Live:** https://sfa.nimrod.bio @ **`7fb3cf7`** (`?v=1780576560`) — uPress, deployed by team_99.

## SESSION TASK (next session)
**Receive the mobile DESIGN PACKAGE from team_35, then prepare + execute a FULL implementation work plan** for the crop-book/market **mobile** remediation (the current launch blocker). Flow: team_35 design → team_100 review + LOD → team_10 build → team_99 deploy → team_50 visual QA @375 → team_100 record. Mobile is what blocks publication; desktop is launch-quality.

## What is DONE + LOCKED (do not re-litigate / do not regress)
- **WP-CB-UI-FIDELITY** — LOD500_LOCKED. Blockers fixed (number formatting, Hebrew units, Hebrew market chips, single crop hero, working עונה/dtm filters), visual round (168px cards, centered crop page, toggle), **70/70 crop watercolor icons** (Nano Banana / gemini-2.5-flash-image, Devora style, transparent — pipeline `scripts/gen_crop_icons.mjs` + `scripts/wc_derivatives.sh` w/ `wc_knockout.py`). Archive: `_archive/SFA-S003-P004-WP-CB-UI-FIDELITY/ARCHIVE_MANIFEST.md`.
- **WP-CB-UI-patch01** — LOD500_LOCKED. `_archive/SFA-S003-P004-WP-CB-UI-patch01/`.
- **WP-CB-UI-WI7** — status VALIDATE (built+deployed+verified @7fb3cf7). team_00 Q2-Q5 via /AOS_decide (`_COMMUNICATION/team_00/DECISION_WI7_crop-book-design_2026-06-04_v1.0.0.md`): Q2 chips kept, Q3 kg_per_ha **÷10→ק״ג/דונם** (single choke point `FieldRegistry::fmtNumber`), Q4→future, Q5 hub eyebrows Hebraized. Plus the QA-reaudit fixes: **F-REA-001 basket unit→לסל** (team_50 caught it, team_100 missed it — dual-engine QA value), F-REA-002 search watercolor, legacy `table?category`→301. composer **205/205**. Open: `/about` tier badges left; team_50 spot-check pending → then LOD500.
- **Gates:** external L-GATE_S + L-GATE_V both PASS (team_190, non-Claude/GPT-5.x). team_50 + team_100 full-system visual QA both GO-WITH-FIXES (fixes shipped). All cross-engine (IR#1/#5) honored.

## THE BLOCKER — mobile (team_00, 2026-06-05)
*"גם הספר וגם המחירון עוד לא מספיק טובים — בעיקר במובייל. זה חוסם את הפרסום."* Desktop OK; **375px is not launch-ready.** team_100 mobile defects (CDP @375): (1) crop-page hero overlaps/crams; (2) planting calendar unreadable + leaks raw `IL_general` region token; (3) market list one-card-per-row → ~12,500px scroll, mostly empty cards; (4) entry-card DTM dominates the crop name, ~8,800px no pagination. **team_35 DESIGN MANDATE issued:** `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-MOBILE/DESIGN_MANDATE_team35_mobile-ui_2026-06-05_v1.0.0.md` (team_35 = Claude Design env; design only, NO screenshots — team_50 does visual QA). Also in scope: **/about simplification** (too many tiers; user must see active-vs-coming clearly). Roadmap WP: open **SFA-S003-P004-WP-CB-MOBILE** when you author the LOD (not yet in roadmap).
→ **Quick win you can do independently:** the `IL_general` raw-token leak in the crop-page calendar (render-layer).

## NEXT-SESSION STEPS
1. `/AOS_mail` — check for team_35's `MOBILE_DESIGN_v1.0.0.md` (`_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-MOBILE/`).
2. Review the design; author **LOD** for WP-CB-MOBILE + a **full implementation work plan** (per-surface: entry cards, crop page hero+calendar, market cards, /about) → roadmap entry.
3. Dispatch team_10 build (git-isolated; team_100 commits) → team_99 deploy → **team_50 visual QA @375** (CDP) → team_100 record → LOD500.
4. Close WP-CB-UI-WI7 to LOD500 once team_50 spot-checks `לסל` on /market/.

## Open threads / pending decisions
- **/about tier badges** (OPEN/BETA/COMING/PAID/CUSTOM) — team_00 wants clarity of active-vs-coming; folded into the team_35 mobile/UI design (simplify). team_10 left them pending.
- **WP-CB-SEASON-VIZ** (REGISTER, future) — 4-level graded seasonal-suitability + icon season interface; model + 45-crop matrix DECIDED: `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-SEASON-VIZ/REGISTER_seasonal-suitability_2026-06-04_v1.0.0.md`.
- **Calculator** — deferred Board-A pixel-polish; team_00 "נגיע לעיצוב במחשבון" later.

## ⚠ Git / branch entanglement (UNRESOLVED — needs coordination)
- The `ui-polish` branch is **SHARED** with a **parallel S004 session** actively committing to it. Current HEAD `550bc69` = *their* "plan(S004): WP003 COMPLETE … research deck"; my crop-book work (`92165f4` and below, 35 commits) is intact underneath. 6 S004-planning commits (vision/competitive-intel/CI-triangulation: `e3fe0b2 7485ff6 755330f 231c9c2 e51ba47 e12eb6d`) are on this branch — the parallel session's domain, NOT crop-book.
- **Merge ui-polish→main: pending.** Verified CLEAN (no file overlap with main's 4 team_99 deploy-report commits; conflict-free). team_00 chose **option 3 (wholesale merge)**, BUT the S004 session is live on the branch with an **uncommitted `.pptx`** — I did NOT force the merge over a live session / touch their work. **Resolve:** wait for the S004 session to reach a clean commit, then merge `ui-polish→main` (or coordinate with team_191). Do NOT stash/commit their uncommitted files.
- **Deploy is already current** (live = `7fb3cf7`, all crop-book code). "Full deployment" = done; only the git consolidation to main remains.

## MANDATORY READS (next session)
- This handoff · `_aos/roadmap.yaml` (WP-CB-UI-FIDELITY/patch01/WI7 + the new MOBILE WP you'll add) · `CLAUDE.md`
- `_COMMUNICATION/team_100/SFA-S003-P004-WP-CB-MOBILE/DESIGN_MANDATE_team35_mobile-ui_2026-06-05_v1.0.0.md`
- `_COMMUNICATION/team_00/DECISION_WI7_crop-book-design_2026-06-04_v1.0.0.md`
- team_50 re-audit `_COMMUNICATION/team_50/SFA-S003-P004-WP-CB-PRELAUNCH-QA/…` + team_100 sweep `…/SFA-S003-P004-WP-PRELAUNCH-QA/TEAM100_VISUAL_SWEEP_acca9b2_2026-06-04.md`
- memories: reference_prod_deploy_authorization · reference_sfa_deploy_topology · reference_aos_branch_autosyncer · feedback_crossengine_validation

## Operating reminders
IR#1/#5 cross-engine (team_190/team_50 external visual; team_100 never self-issues L-GATE_V). IR#4 single-writer roadmap. Deploys auth-gated on this Mac → route to team_99 (server). Commit defensively (explicit paths; verify ancestry — auto-syncer + the parallel S004 session both touch this branch). Pre-push runs validate_aos — keep 0 FAIL. Gemini image model needs **billing** (free tier = limit 0); key in `.env` (gitignored).
