---
id: HANDOFF_SFA-S003-P004-CB-UI-TAILS+MARKET-DETAIL_v1.0.0
from: team_100 (this session — spec author)
to: team_100 (new build session)
date: 2026-06-12
type: session-handoff (build dispatch)
wps: SFA-S003-P004-WP-CB-UI-TAILS · SFA-S003-P004-WP-CB-MARKET-DETAIL
gate: L-GATE_SPEC (LOD400 authored) → external validation BY the build session → build → L-GATE_VALIDATE
engine: builder = team_10/Claude; validator MUST differ (non-Claude, IR#1/#5)
---

# HANDOFF — two LOD400-specced delivery-tier WPs, ready to validate + build

**Read first:** `CLAUDE.md` → `_aos/governance/team_100.md` → this handoff → the two SPECs below.

## What's handed off
Two delivery-tier (`sfa_delivery/`) WPs, each with a **full LOD400 spec authored**. Per team_00: **the build
session runs the external L-GATE_SPEC validation itself** (non-Claude), then builds, then external L-GATE_VALIDATE,
then deploy (FTPS `lftp` from the Mac) + closure.

| WP | LOD400 SPEC | Summary |
|----|------|---------|
| **WP-CB-UI-TAILS** | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-UI-TAILS/SPEC_2026-06-12_v1.0.0.md` | 3 UI tails: ₪ price-chip (live **+ estimated-from-book**), deep-provenance pills, calc precision-to-mockup |
| **WP-CB-MARKET-DETAIL** | `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-MARKET-DETAIL/SPEC_2026-06-12_v1.0.0.md` | `/market/{slug}` re-skin to the redesign DS + emoji-fold + watercolor hero |

## ⭐ Head start — the price-chip is already built
Branch **`feat/wp-cb-book-market-pricechip` @ `ab71d9f`** (pushed to origin) implements WP-CB-UI-TAILS item 1's core:
`CropBookViewController::entry()` resolves each crop's price by **slug OR `crops.hebrew_name = products.hebrew_name`**
(one `IN(...)` query, result keyed by crop slug, template unchanged) — fixes the production "0 chips" bug. phpunit
234/234, `:8095`-verified. **Adopt this commit**, then add only the **estimated-price** extension (AC-1.2: show
`crop.payload.market_link.price_current` labeled **`מחיר מוערך`** when no live price). The branch is a clean ff over
`main` — rebase it onto current `main` first (main advanced via the WI7 + tails closures).

## Build/validate flow (per WP)
1. **L-GATE_SPEC** — independently validate the LOD400 spec (non-Claude). On PASS → build.
2. **Build** — new feature branch off `main` (use a `git worktree` per WP; the worktree lacks the gitignored
   `_aos` cache + `.env`/vendor — run qa_probe & validate_aos from the MAIN checkout, `cp -RL` vendor for phpunit;
   see project memory `feedback_worktree_aos_cache_gap`).
3. **Verify** — phpunit 0 fail · `validate_aos` 0 FAIL (canonical checkout) · `qa_probe.mjs --shots` overflow=false +
   visual parity at 375+desktop (never validate layout with curl alone).
4. **Deploy** — `bash scripts/ftp_deploy_sfa_ui.sh` (ask team_00 to open the Mac's external IP on uPress — TCP :21
   timeout = closed) → production smoke.
5. **L-GATE_VALIDATE** — external, non-Claude → roadmap COMPLETE/LOD500_LOCKED + `POST_GATE_ARCHIVE_PROCEDURE`.

## Also in your queue (team_00 directed)
**Governance/roadmap hygiene — execute immediately (cosmetic/git-state-sensitive, held back from the spec session):**
1. **WP-CB-0** — stale `status: ACTIVE` (it's a LOD200_LOCKED canon, superseded by WP-CB-MIG/MIG2) → set to a
   completed/locked status.
2. **WP-CB-PRELAUNCH-QA** — dangling `status: ROUTED / NO-GO` never formally closed; it's superseded by the FIDELITY/
   MOCKUP-FIDELITY/MOBILE WPs that fixed its findings → close or supersede with a note.
3. **WP-CB-2/3/4/5 placeholders** (Planner/Tasks/Sales/Tend) — superseded by the S004 farmOS direction → reconcile/
   annotate (don't delete; mark superseded).
4. **Stale branches** — retire `rescue/wp-cb-content-56bc693` + any misplaced `feat/wp-cb-content`; confirm
   `feat/wp-cb-content-build` canonical. Also: `feat/wp-cb-ui-mockup-fidelity` + `feat/wp-cb-book-market-pricechip`
   + the `chore/`/`wi7-closure`/`docs/` branches from the prior session can be pruned once merged. **Caution:** the
   `/private/tmp/sfa-main` worktree holds **another team's uncommitted WIP** (`L49_DIFF_REPORT.md`, TEAM_10/WP-C3) —
   do NOT disturb it; coordinate with that owner before consolidating `main`'s worktrees.

## Context you'll want
- **Just closed (LOD500_LOCKED, on main):** WP-CB-UI-MOCKUP-FIDELITY (the big crop-book/market/home re-skin — root
  cause was a dropped `redesign.css :root` token block from a stray `*/` in a comment), WP-CB-UI-WI7.
- **Just registered (deferred future WPs):** WP-CB-ABOUT (LOD100), **WP-CB-DATA-API** (strategic — incremental
  validated code-preserved data API; **team_00: NO more `seed --all`**), WP-CB-DATA-CURRENCY (catch-up/keep-crops/
  beans-2-crop-model/hydro/JMF-FT, gated on DATA-API), plus existing WP-CB-WATER / WP-CB-CROPDATA-DATES / WP-CB-SEASON-VIZ.
- **Beans canon (memory):** exactly 2 bean crops — `שעועית מטפסת` (pole, **default**) + `שעועית שיח` (bush, explicit only).
- **Key project memories:** `reference_sfa_local_preview_harness` (:8095), `reference_sfa_deploy_topology` (uPress
  FTPS, dynamic IP), `feedback_worktree_aos_cache_gap`, `feedback_crossengine_validation` (Claude can't self-validate),
  the crop-taxonomy canon, `project_calculator_*` (8/14 calcs are Phase-B stubs awaiting Cropdata-Dates).

## Done criterion
Both WPs externally-validated, built, LIVE on sfa.nimrod.bio, LOD500_LOCKED + archived; governance hygiene executed;
verdicts/closure return to the team_100 origin.
