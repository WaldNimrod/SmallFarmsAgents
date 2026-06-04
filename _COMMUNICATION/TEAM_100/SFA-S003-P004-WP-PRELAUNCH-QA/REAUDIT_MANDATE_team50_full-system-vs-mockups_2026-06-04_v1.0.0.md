# RE-AUDIT MANDATE — Comprehensive full-system visual QA vs ALL mockups — team_100 → team_50 — v1.0.0

**Date:** 2026-06-04 · **From:** team_100 · **To:** team_50 (QA) · **Routed by:** team_00
**WP:** SFA-S003-P004-WP-PRELAUNCH-QA (re-audit — the original NO-GO was deploy-lag; everything is now live)
**Live:** https://sfa.nimrod.bio @ **`acca9b2`** (`?v=1780576560`) — FIDELITY + visual round + 70 crop icons all deployed.

## Why this re-audit (team_00 question)
team_00 asks: *"are you sure the interface is correct, precise, and beautiful per ALL the mockups we received?"* — team_100 will NOT certify that from structural passes alone. A **fresh, comprehensive, pixel-level design-vs-mockup sweep across EVERY surface has not been run on the complete live state.** This mandate is that sweep. It is the pre-launch GO/NO-GO assurance.

## Method (MANDATORY)
- Dependency-free CDP harness `_aos/lean-kit/modules/validation-quality/scripts/qa/qa_probe.mjs` (Node 18+) — **never curl for layout** (curl can't see the rendered box model). Production QA — **no cert-bypass flags**.
- **Cache-bust to the served `?v=`** so you compare the live `acca9b2` build, not a stale cache.
- **Design-vs-live screenshot PAIRS** at **1440 (desktop) + 768 (tablet) + 375 (mobile)** for every surface, placed beside the mockup region.

## Design SSoT (compare against BOTH boards)
- **Board-A** (crop-book + **calculator**) and **Board-B** (hub / market / search / community / about / account) — HTML paths in `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-FIDELITY/LOD400_spec.md` frontmatter `design_ssot`.

## Surfaces — every one, vs its mockup
1. **Hub `/`** (Board-B) — tiles, audience cards, eyebrows, hero, CTA, palette.
2. **Crop-book entry `/crop-book/`** (Board-A) — 168px cards, watercolor art on all crops, toggle, density, filters.
3. **Crop page `/crop-book/{slug}`** (Board-A) — single hero, centered column, headline values, topic cards, sections, varieties, depth tabs.
4. **Calculator `/calc/`** (Board-A) — **highest-priority / least re-verified.** 14 calc modules, inputs, results, book-chips, AssumptionField, the spacing/plant-count visualization, export. Compare layout + type scale + component shapes to Board-A precisely.
5. **Market list `/market/`** (Board-B) — cards, ₪ prices, freshness pills, Hebrew category chips, disclaimer, cards/table toggle.
6. **Market detail `/market/{slug}`** (Board-B) — graph + range buttons (7י/28י re-fetch), history.
7. **Search `/search?q=…`** (Board-B) · **Community `/community`** · **About `/about`** (Board-B).
8. **Account `/account`** if present (Board-B).

## Per surface, check
Layout/positioning vs mockup · spacing + type scale · icons + watercolor art · component shapes · color/palette (#f8fbf8, no cream) · RTL correctness · **no horizontal overflow at 375** · interactions function (toggles/tabs/graph/calc/search) · no raw English keys/units/numbers leaking · no console errors. List EVERY divergence with severity (BLOCKER/MAJOR/MINOR/COSMETIC) + a screenshot.

## Deliverable
`_COMMUNICATION/team_50/SFA-S003-P004-WP-PRELAUNCH-QA/REAUDIT_REPORT_live-acca9b2_v1.0.0.md` + a `design_pairs/` evidence folder. Bottom line: **GO / GO-WITH-FIXES / NO-GO** + a prioritized punch-list. Notify team_100 — team_100 dispatches any fixes (team_10) → re-deploy → re-verify. (This is the launch-readiness assurance; the constitutional crop-book L-GATE_V already PASSED, this confirms the *whole system* vs *all* mockups.)
