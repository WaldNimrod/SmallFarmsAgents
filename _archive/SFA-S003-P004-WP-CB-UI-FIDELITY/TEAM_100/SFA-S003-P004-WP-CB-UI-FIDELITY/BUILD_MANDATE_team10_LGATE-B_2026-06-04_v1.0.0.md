# BUILD MANDATE — SFA-S003-P004-WP-CB-UI-FIDELITY (L-GATE_B build) — team_100 → team_10 — v1.0.0

**Date:** 2026-06-04
**From:** team_100 (Chief System Architect, Claude Opus)
**To:** team_10 (Builder, Claude Sonnet)
**Repo:** `/Users/nimrod/Documents/SmallFarmsAgents` · branch `claude/ui-polish-hub-cropbook-2026-06-03` · base HEAD `40e2aa6`
**Gate cleared:** L-GATE_S **PASS_WITH_FINDINGS · authorize_build: true** (team_190 / GPT-5.x, non-Claude). Verdict: `_COMMUNICATION/team_190/SFA-S003-P004/WP-CB-UI-FIDELITY/WP-CB-UI-FIDELITY_LGATE-S_VERDICT_v1.0.0.md`
**Cross-engine:** builder = Sonnet (Claude), independent L-GATE_B = team_100 (Opus, CDP), constitutional L-GATE_V = team_190 (non-Claude). IR#1/#5 satisfied.

---

## 0. The spec is the LOD — build to it exactly
**Authoritative spec:** `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md` (v1.1.0, team_100-reviewed, L-GATE_S-passed). Every defect is pinned to `file:line` in §2 and detailed in §1. Build WI-1…WI-9 per §3. Do NOT re-derive root causes — they are confirmed against source. Do NOT weaken any AC (§5).

## 1. Hard constraints (read before touching anything)
- **GIT ISOLATION (CRITICAL):** You make **ZERO git operations.** No `commit`, `add`, `checkout`, `switch`, `branch`, `reset`, `rebase`, `merge`, `stash`, `tag`, `push`. Edit files in place only. **team_100 owns all commits** and verifies ancestry after. If you run any git state change you will orphan work and move the branch ref — forbidden.
- **Scope = delivery tier ONLY.** Touch only files under `sfa_delivery/`. **Never** edit `_aos/roadmap.yaml` or anything in `_aos/` (IR#4 — single-writer is team_100; AC-7 / finding F-190-FID-S-01). No DB/Python/migration (render-layer only).
- **No data mutation.** Mappings reconcile the render to existing data; they do not change data. If a fix appears to need a DB/data change (esp. D-4 season tokens — see §3), **STOP and report to team_100**; do not fold it silently (LOD §7).
- **No new defects.** Preserve the "WORKS" list (LOD §1) — hub, market list, search, market detail graph, palette, icon sprites.

## 2. Work items → build (full detail in LOD §1–§3; pinned files in §2 table)
1. **WI-1** Number-format helper (D-1) — shared `sfa_fmt_number()` / `FieldRegistry::fmtNumber()`; numeric-only; used by `book_crop.php` `$pv()`, `prov_value.php`, variety renders, calc dashboard.
2. **WI-2** Unit→Hebrew map (D-2) — new `FieldRegistry::unitLabel()`; renderer is the sole unit emitter; **remove the 3 hardcoded `<small>` units** at `book_crop.php:208/215/227` (D-1b single-unit rule). Cover all canon units (`organic_market_agent/crop_book/canon/field_registry.py`); unknown token → return as-is.
3. **WI-3** Category Hebrew labels (D-3) — `MarketViewController::fetchCategories()` → `enumLabel('category',$cat)`; extend `ENUM_LABELS['category']` with `legumes_fresh`/`eggs`/`baskets` (proposed wording in LOD Q2; if you ship a default, mark it for team_35 confirm). Keep `slug` raw (query param).
4. **WI-4 + D-5b** Hero dedup — collapse to the single `.crophero`; from legacy `.cb-crop-hero` remove duplicate breadcrumb + `<h1>` + `.cb-crop-hero__icon` box; **preserve** the description lede + family/dtm pills; **retarget `id="identity"`** to the surviving identity block so the section-nav link still resolves. Remove/repurpose `.cb-crop-hero__icon` CSS (`crop-book-deep.css:522-528`).
5. **WI-5** Filters (D-4a + D-4b) — (a) determine the real stored `crops.season` token format FIRST (query the canonical Postgres `oma-postgres` :5433 or trace the ingest payload; if you cannot determine it, STOP and ask team_100 — do NOT guess), then make the season filter consistent (prefer a `<select>` whose values match stored data, like `sow`/`frost`). (b) Re-route the 5 leading-questions so they hit the correct filter (`summer`/`winter`→season, `fast`→`dtm_max`); `beginner`/`small-space` → only if backing data exists, else flag for team_35 (Q4) — do not ship a 0-result link.
6. **WI-6** Interaction E2E (M-1) — fix the `_layout.php` per-route JS gate so each interaction's script loads where used; verify toggle / audience / depth-tabs / adv-filter / market-graph-range (`window.fetchHistory` binding; endpoint `MarketViewController::productHistoryApi` exists) / calc / search.
7. **WI-7** team_35 DESIGN_REQUEST (conditional) — file for Q2/Q3/Q4/Q5 (LOD §4). These BLOCK only their own items; everything else proceeds.
8. **WI-8** Fidelity sweep (M-3) — desktop 1440 + mobile 375; remediate BLOCKER/MAJOR divergences vs Board-A/B.
9. **WI-9** Re-verify patch01 mobile-overflow (`/crop-book/table` @375, already committed `7fbcf89`/`e798bc8`) survives your changes — it ships live in this WP's single deploy.

## 3. Verification you MUST run before handback
- `composer test` (from `sfa_delivery/`) — green; report counts.
- `php -l` on **every** edited PHP file — clean.
- A quick self-check of AC-1/AC-2 on your edited templates (grep your output for `\d+\.\d{3,}`, trailing-zero, and `cm|days|weeks|count` units beside Hebrew).
- You need NOT run the full CDP suite — team_100 does the independent CDP L-GATE_B vs Board-A/B. But list exactly which routes/ACs you self-verified and which you could not.

## 4. Handback → BUILD_REPORT
Write `_COMMUNICATION/team_10/SFA-S003-P004-WP-CB-UI-FIDELITY/BUILD_REPORT_v1.0.0.md` with:
- Files changed (path list — all must be under `sfa_delivery/`).
- Per-WI status (done / partial / blocked-on-team_35 / blocked-on-data).
- Test results (composer count, `php -l` clean).
- AC self-assessment (which you verified, which need team_100 CDP).
- Any item where you would have needed a git op, a data change, or a missing design — surfaced, NOT actioned.
- **Do NOT commit.** Leave the working tree dirty; team_100 reviews, commits with explicit `sfa_delivery/` paths, verifies ancestry, then runs CDP L-GATE_B.

---
*team_100 will independently verify with the CDP harness vs Board-A/B (not a low-tier QA pass). On L-GATE_B PASS → team_99 single deploy of branch HEAD (brings the 5 undeployed sfa_delivery commits + this build live) → team_50 re-audit + team_190 L-GATE_V.*
