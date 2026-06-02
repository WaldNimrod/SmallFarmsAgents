# DISPATCH — SFA-S003-P004-WP-CB-UI-CLASSB → team_10 (build) — v1.0.0

**Date:** 2026-06-02 · **From:** team_100 · **To:** team_10 (sfa_build, Claude Sonnet) · **Gate:** L-GATE_B
**Branch:** `claude/wp-cb-ui-align-2026-06-02` · **Authority:** IR#1 — builder Sonnet ≠ team_100 Opus ≠ team_190 (non-Claude) L-GATE_V

## Authorization
team_190 L-GATE_S **PASS_WITH_FINDINGS** (verdict `45badf6`, 0 blockers / 0 major / 7 minor). LOD400 v1.0.0 LOCKED.
Build the team_35 Class B v2 design into the delivery tier — **delivery tier only; no backend/migration/schema.**

## Read first (binding)
1. LOD400: `_aos/work_packages/S003/SFA-S003-P004-WP-CB-UI-CLASSB/LOD400_spec.md` (§2 surface map, §3 data, §4
   honest-data rule, §5 ACs, §9 + §9a team_00 decisions).
2. Design SSoT: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/HANDOFF/design/` — `Board-B-*.html` (visual
   truth), `classb.css` (port verbatim → `public_assets/css/classb.css`), `classb.js` (→ `public_assets/js/classb.js`),
   `spec/B_COMPONENTS-TEMPLATES-classb-delta.md` (§30–42 contracts).
3. L-GATE_S verdict (the 7 minors below): `_COMMUNICATION/TEAM_190/SFA-S003-P004/WP-CB-UI-CLASSB/LOD400-VERDICT_v1.0.0.md`.

## Scope — 7 surfaces + shell refine (LOD400 §2)
Build each template to its Board-B frame, on the Class A app-shell (already built in WP-CB-UI-ALIGN):
hub `/` · market list `/market/` · market detail `/market/{slug}` · search `/search` · community `/community` ·
about `/about` · account `/account` (NEW `AccountController::index` + `account_landing.php`) + `_layout.php` shell refine.

## MUST fold in — the 7 team_190 minors (build them in, don't defer)
1. **Disclaimer class:** reskin to `.mkt-disc` (the board's class); **keep the LOCKED disclaimer copy verbatim**
   (the 4 bullets incl. "7 ימים אחרונים"). Don't invent new copy.
2. **Graph range label:** board says "30י" but spec/API use **28 days** → label and wire the control as **28י**
   (not 30). Live ranges = 7י + 28י; 90י + year = `.is-disabled` "בקרוב" (LOD400 §9 #3).
3. **`.reqchip` kinds:** the chips select a `kind` but `/api/v1/contribute` accepts **request-info only** in this
   WP — do NOT add new API kinds. Map all chips to the existing accepted payload; no new endpoint/contract.
4. **Search honesty (§4):** `HubController::search` must NOT show fake min/max/source counts on product rows.
   Show only real values; where absent, the designed empty/`—` state. No fabricated numbers.
5. **Disabled ranges:** explicitly mark 90י/year `.rangesel` buttons `.is-disabled` server-side in the template —
   `classb.js` alone does not disable them.
6. **Ignore the B-delta "community feed" line** — LOD400 §9 #1 feed-LESS wins (manifesto + `.reqcard` only).
7. **Asset loading:** extend `_layout.php` to load `classb.css` + (`cropbook-v1.js` THEN `classb.js`) on the Class
   B routes. Order matters (classb.js reuses cropbook-v1.js `wireFilters`/`wireAudience`).

## Note from the parallel Class A session (read — affects market export/print)
`routes.php` already moved the PDF print path to **`/calc/print`** (uPress/Apache doesn't route `.pdf` to Slim →
origin 404). If any Class B surface needs a print/PDF affordance, use an **extension-less route**, not `.pdf`.

## Acceptance (LOD400 §5) — VISUAL fidelity is mandatory
AC-1 classb.css/js ported + load order correct · AC-2 each surface matches its Board-B frame (team_50 will
capture design-vs-live pairs) · AC-3 market disclaimer always-on, cards⇄table, freshness 3-state per §9a,
graph 7/28 live + 90/year disabled, empty/stale on 0-report · AC-4 hub tiles+tiers+coming-soon+audience+manifest ·
AC-5 search grouped + `<mark>` + no-match CTA · AC-6 community feed-less, about 5-tier, account shell+"בקרוב" ·
AC-7 `composer test` green (+ new tests: account route, market detail, search grouping); `validate_aos` 0 FAIL;
no LOCKED Python/migration; routes 200; RTL legible; no raw keys/"Array"/stray "—".

## Authority limits
MAY write: `sfa_delivery/` (templates, public_assets, app/Controllers, tests), `_COMMUNICATION/TEAM_10/…CLASSB/`.
MAY NOT: edit `_aos/`, roadmap, LOCKED Python backend/migrations; add server-side features — if a server change
seems needed, STOP and append it to `_aos/work_packages/S003/SFA-S003-P004-WP-SRV-IDEAS/REGISTER.md` (PROPOSED +
provenance), render the honest degrade, continue. No deploy. No gate verdicts.

## Output
`_COMMUNICATION/TEAM_10/SFA-S003-P004-WP-CB-UI-CLASSB/BUILD_REPORT_v1.0.0.md` (§1 summary · §2 branch/commits ·
§3 AC table w/ evidence · §4 the 7 minors — how each was addressed · §5 validate_aos + composer test output ·
§6 any SRV-IDEAS entries filed · §7 next). Then team_100 → team_50 VISUAL QA → team_190 L-GATE_V.

*Dispatched by team_100 · 2026-06-02 · IR#1 cross-engine.*
