# Session Handoff — team_50 (QA & Functional Acceptance) | E2E BROWSER QA of the ENTIRE SFA delivery tier. Exercise every interface in a real browser: confirm every screen displays ACCURATE data, the UX is smooth and clear, and all data is rendered correctly + legibly (RTL Hebrew). This is a full-surface sweep, not a single-WP gate.

**Date:** 2026-06-01 · **Author:** team_100 (issuing the QA handoff) · **For:** team_50 · **Type:** SESSION_HANDOFF (QA mandate) · **Depth:** full

---

## 1. MISSION
Run a complete **end-to-end browser QA** over the whole SmallFarmsAgents public delivery tier (the Slim4/PHP app). For **every** route/interface: verify (a) it loads with **accurate data** (matches the DB / source of truth), (b) the **UX is smooth and clear**, (c) **all data renders correctly and legibly** — RTL Hebrew, no overflow, no raw DB keys, no literal "Array"/"—" where a value should appear, watercolor art loads (no broken `<img>`), no broken links/404s.

This is the system-wide acceptance sweep team_00 requested after the S003-P004 Crop Book v1 program merged to main (commit `8795b8a`). Not scoped to one WP — **all interfaces**.

## 2. IDENTITY SNAPSHOT
- **Team ID:** team_50 · **Role:** QA & Functional Acceptance · **Engine:** Cursor Composer (or any browser-capable engine) · **Domain scope:** universal.
- **Standard:** GCR-002 mandatory coverage for UI WPs — full UI interaction sweep + DB round-trip + scenario matrix 1–5 (happy / error / edge / duplicate / cancel). Happy-path-only is NOT a complete pass.
- **Governance:** `_aos/governance/team_50.md` (read first).

## 3. ENVIRONMENT (choose one; prefer LIVE for "real data")
- **LIVE (canonical):** `https://sfa.nimrod.bio` — Slim4/PHP on uPress + live MySQL. This is the real production data tier (PROJECT_CONTEXT.md §delivery). **Use this to validate data accuracy** against what users actually see. Read-only QA — do NOT submit real contribute/request-info spam (use one clearly-marked test submission max, or note it as untested-to-avoid-pollution).
- **LOCAL (for the merged code at HEAD):** from `sfa_delivery/`: `composer install` then `php -S localhost:8080 -t .` (see `sfa_delivery/README.md` §run). Local needs DB env vars (DB_HOST/DB_NAME/… per README) + a populated MySQL mirror; if no local DB, the pages render empty-states — fine for UX/markup checks, but **data-accuracy checks require LIVE or a seeded DB**.
- ⚠ The merged code on `main` (`8795b8a`) may not yet be **deployed** to `sfa.nimrod.bio`. **First step: detect drift** — compare a known new feature (e.g. the `/crop-book/` watercolor hero banner, 28 crop card images, server-side filter form, `/calc` export buttons) between LIVE and local HEAD. If LIVE lacks them, LIVE is running the pre-merge code → QA the new surfaces locally and flag "deploy pending" to team_00/team_99.

## 4. INTERFACES TO COVER (every one)
**Hub / global**
- `/` — home module grid (8 cards). Verify the 3 watercolor module heroes (calc / market / crop-book) load; other cards show sprite glyph; tier badges correct; disabled "בקרוב" cards non-navigable (no 404).
- `/about` — tier explainer (5 tiers). · `/search?q=…` — global search (crops + products), incl. empty query + no-match. · `/community` — contact + feed, mandatory disclaimer present.

**Crop Book**
- `/crop-book/` — **the big one.** Audience switch Cards⇄Table (`?view=`); **server-side filter form** (q / family dropdown / season / DTM-max / sow-method / frost) — test each filter narrows results; **0-result empty-state** keeps the filter bar (recoverable); pagination; crop cards show watercolor (28 crops) or graceful glyph fallback; **hero banner** (wc-cropbook-hero) renders.
- `/crop-book/questions`, `/crop-book/family`, `/crop-book/family/{slug}` (→ redirects, no 404), `/crop-book/table`, `/crop-book/search`, `/crop-book/cover-crops`.
- `/crop-book/{slug}/` — 3 depths `?depth=simple|full|drill`: depth tabs switch; **13-topic taxonomy** order; headline values; **prov_value cues** (validated plain / unvalidated `*`+tooltip / missing `—`+request-info) — confirm a COMPLETE crop shows real numbers and a PARTIAL crop shows `*`/`—`; **AssumptionField** (default + inline override + explainer + read-more link); **calculator panels** (enabled with correct numbers vs disabled-on-MISSING with Hebrew field label — NOT raw key, NOT "Array"); rotation hint; crop hero watercolor.
- `/crop-book/{slug}/variety/{vslug}/` — drill provenance / variety table.

**Calculator**
- `/calc/` — dashboard: context strip (crop / beds / target date); the 6 interactive calcs (#1,#7,#8,#9,#10,#12) **recompute live** on input + AssumptionField override; sticky summary; **export** ⬇PDF (opens print view) + ⬇CSV (downloads, Hebrew legible / UTF-8) — verify the plan params carry through.

**Market**
- `/market/` — price list cards; `/market/{slug}` — detail (big price, history table, stats, disclaimer). Verify prices match source.

## 5. WHAT "PASS" REQUIRES (per AC-style checklist)
For each interface report: **loads 200 · data accurate (vs DB/live) · RTL legible · interactive elements work · empty/error/edge states clean · no broken art/links · no raw keys / "Array" / stray "—".** Apply the scenario matrix 1–5 to the data-entry surfaces (filters, search, calculators, contribute/request-info). DB round-trip where data persists (contribute capture, if tested).

## 6. KNOWN CONTEXT / EXPECTED BEHAVIORS (don't flag as bugs)
- Crops **without** a watercolor master fall back to an emoji/sprite glyph — **intended** (28 crops have art; cauliflower/celery/etc. don't yet).
- `field_state` cues depend on the backend ingest delivering per-field state into the variety payload; if the live mirror predates that ingest, cues degrade to a neutral state (not "VALIDATED") — note it, but the **degrade must be honest** (never present missing/low-confidence data as validated).
- Proposed fields (needs_summer_shade, irrigation_type, root_depth_class, sale_unit) render as "מוצע" until WP-CB-MIG2 — **intended**.
- 2 pre-existing pytest failures exist server-side — not UI; out of QA browser scope.
- `/calc` PDF = a print-friendly auto-print HTML page (browser → Save as PDF), not a server-generated PDF binary — **intended** (no PDF engine on shared LAMP).

## 7. DELIVERABLE
Write `_COMMUNICATION/team_50/SFA-S003-P004/E2E_QA_REPORT_2026-06-01_v1.0.0.md`:
- Environment used (LIVE vs local + deploy-drift finding).
- Per-interface result table (route | loads | data-accurate | UX | rendering | findings).
- Findings list: severity (BLOCKER/MAJOR/MINOR/COSMETIC) + route + screenshot/observation + repro.
- Scenario-matrix coverage note per data surface.
- Overall verdict: PASS / PASS_WITH_FINDINGS / FAIL, with the top issues for team_100.
- Route findings that are real bugs → team_100 opens a remediation patch (WP-CB-1-patch02 or similar). Cosmetic/UX polish → batch for team_00 review.

## 8. MANDATORY READS
- `_aos/governance/team_50.md` (role + GCR-002 coverage standard + scenario matrix).
- `_aos/context/PROJECT_CONTEXT.md` (delivery tier canon — sfa.nimrod.bio is uPress, not home server).
- `sfa_delivery/README.md` (local run) · `sfa_delivery/app/routes.php` (authoritative route list).
- Design contract (expected look/behavior): `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/LOD300 Crop Book v1.html` + `documentation/09-design-system/`.

## 9. ACTIVATION PROMPT
```
HANDOFF_DEPTH: full
ACTIVATION_SCOPE: team_50 only

# Agent Onboarding — team_50 (QA & Functional Acceptance)

## TL;DR
- Identity: team_50 · QA & Functional Acceptance · browser-capable engine
- Mission: E2E BROWSER QA of the ENTIRE SFA delivery tier — every screen, accurate data, smooth UX, correct + legible RTL rendering.
- Environment: LIVE https://sfa.nimrod.bio (real data) AND/OR local sfa_delivery/ at main HEAD 8795b8a. FIRST detect deploy-drift (does LIVE have the new crop-book hero / 28 watercolors / filter form / /calc export?).
- Writes to: _COMMUNICATION/team_50/
- Deliverable: _COMMUNICATION/team_50/SFA-S003-P004/E2E_QA_REPORT_2026-06-01_v1.0.0.md

## Mandatory startup
1. Read _aos/governance/team_50.md (GCR-002 standard: full UI sweep + DB round-trip + scenario matrix 1–5).
2. Read _aos/context/PROJECT_CONTEXT.md (sfa.nimrod.bio = uPress live tier).
3. Read sfa_delivery/app/routes.php for the authoritative route list; sfa_delivery/README.md to run locally.
4. Open the design source of truth (LOD300 board + documentation/09-design-system/) to know expected look/behavior.

## What to do
Exercise EVERY route in §4 of the handoff in a real browser. For each: 200 load · data accuracy vs DB/live · RTL legibility · interactive elements (audience switch, filters, depth tabs, AssumptionField, calculators, export, search, pagination, tooltips) · empty/error/edge states · no broken art/links · no raw DB keys / "Array" / stray "—". Apply scenario matrix 1–5 to data surfaces. Report findings with severity + repro. Note any deploy-drift between LIVE and merged HEAD.

## First action
Confirm identity + environment, detect deploy-drift, then sweep the crop-book surface first (/crop-book/ + a crop page at all 3 depths) since it carries the most new functionality. Report the §7 deliverable.
```

## 10. NOTES FOR team_100 (on receipt of QA report)
- Real bugs → open a remediation patch (delivery-tier, chartered like patch01) → build/QA/team_190 non-Claude L-GATE_V.
- If deploy-drift confirmed (main merged but not on sfa.nimrod.bio) → route a deploy mandate to team_99 (uPress FTPS relay via waldhomeserver, per UI_DEPLOY_RUNBOOK) — that is OPS, not team_50.
