---
id: SFA-S003-P004-WP-CB-UI-ALIGN-LOD200
wp: SFA-S003-P004-WP-CB-UI-ALIGN — Delivery-tier visual alignment to the team_35 LOD300
gate: L-GATE_E (pending team_00) → L-GATE_S
status: DRAFT (LOD200) — opened 2026-06-02 · AWAITING team_00 FINAL CHARACTERIZATION APPROVAL
author: team_100 (Chief System Architect)
date: 2026-06-02
design_ssot: _COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/
trigger: "team_00 — live UI does not match the team_35 design package"
---

# LOD200 — WP-CB-UI-ALIGN: align the live delivery tier to the team_35 LOD300

> **Status: DRAFT for team_00 approval (אפיון סופי).** No build until approved. team_100 authored this after
> team_00 flagged that the live site (`sfa.nimrod.bio`) does not look like the team_35 design package.

## 1. Problem (root-caused, evidence-backed)
The S003-P004 program delivered the crop-book **functionality** and passed functional QA (107/107) + two
L-GATE_V rounds — but it was accepted on **functional ACs only, never on pixel/visual fidelity to the
team_35 LOD300**. Result: the live UI is functionally correct but **visually does not match the design**.

Concrete, verified root causes (code + live screenshots + design-board render):
1. **Two competing palettes in `tokens.css`.** The design v2 mandates a **white-with-whisper-of-green** ground
   (`--gj-paper #f8fbf8`, explicitly *"do not revert to cream/brown"*). But `tokens.css` still defines the
   legacy **`--paper #f5f3ec` "Cool Stone" cream** AND sets `body { background: var(--paper) }` → the whole
   site renders cream, while crop-book-v1 components use `--gj-paper` white → a clash, not the design.
2. **The team_35 app-shell was never built.** No template uses the design's `.sh` / `.sh__nav` shell
   (top nav ספר גידולים · מחשבון · מחירון · חשבון + mobile 4-item tab bar). Every page (hub, market, all
   book pages, /calc) still renders inside the **legacy `.gj-shell` / `.dt-shell`** chrome from the prior WP-UI
   program. crop-book-v1 components sit inside old chrome.
3. **`/calc/` is inert + incomplete** (team_50 F-CALC-002/003): `_layout.php` only loads `crop-book-v1.js`
   for crop-book routes, so the calculator dashboard never gets `SFA_CALC` → panels don't recompute; and it
   shows 5 modcards vs the 14-calculator contract.
4. **`/calc/export.pdf` 404 on live** (team_50 F-EXPORT-001) — route/deploy gap.

## 2. Goal
Make every public delivery-tier surface **visually faithful to the team_35 LOD300** — one unified white-green
design system, the design app-shell + nav, and the interactive calculator surface working as designed.

## 3. Scope
1. **Unify the palette.** Remove the legacy cream `--paper*` ground; `body` background → `--gj-paper` (white).
   Reconcile any legacy `--ink`/`--paper` consumers to the `--gj-*` tokens. The design `tokens.css` is the SSoT
   (port verbatim where it diverges). Zero cream remaining anywhere.
2. **Build the design app-shell.** Implement `.sh` + `.sh__nav` (desktop horizontal nav: ספר/מחשבון/מחירון/
   חשבון, active-state per route) + `.sh__nav--mobile` (bottom tab bar) + the `#sfa-logo` symbol, per
   `spec/COMPONENTS-delta.md` §Main-Nav. Replace the legacy `.gj-shell`/`.dt-shell` chrome across all pages.
3. **Apply the design to every surface** (not only crop-book): home/hub, market list+detail, search,
   community, about — all on the unified shell + palette. crop-book-v1 components stay (they're already on
   the v2 tokens) but now render inside the correct shell.
4. **Fix /calc** (F-CALC-002/003): load `crop-book-v1.js` on `/calc/` (and any page with calculators); surface
   the **14 calculators** per the catalog (currently 5); wire export buttons.
5. **Fix /calc/export.pdf 404** (F-EXPORT-001) — confirm route on the deployed build (this may be deploy-only;
   verify locally first, then route a deploy mandate if the code is correct but undeployed).
6. **Hero + art** already shipped — verify they render on the unified shell (crop-book hero, 28 watercolors,
   3 module heroes).

## 3a. Design-coverage gap (team_00 directive: structure/style EXACT per team_35; content/fields from code)
team_35's LOD300 designed **only 2 surfaces** in v2 (crop-book + calculator) — their README says the others are
"stable nav hooks for future modules." The live hub/market/search/community/about are still in the **earlier
cream WP-UI style**. So this WP splits into two implementation classes:

- **Class A — IMPLEMENT (design exists):** crop-book + calculator + the `.sh` app-shell contract. Build exactly
  to the team_35 v2 templates we already hold.
- **Class B — AWAIT team_35 templates (design missing):** hub/home, market list+detail, search, community,
  about, account. We MUST NOT guess these (guessing is what caused the drift). A detailed design request was
  issued: `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-UI-CLASSB/DESIGN_MANDATE_team35_v2-surfaces_2026-06-02_v1.0.0.md`.
  Class B build is **blocked on team_35 delivery + team_00 approval**; the WP may proceed on Class A first.

Binding rule (team_00): **interface, style, page structure = EXACT to team_35; content + exact fields = from the
code.** Where a v2 template is missing, request it from team_35 — never improvise.

## 4. Out of scope
- New features / data-model changes (that's WP-CB-MIG2).
- The `/calc` revenue non-kg unit conversion (F-50-patch01-01) — separate, latent.
- Backend / Python / migrations — none touched. Delivery tier (`sfa_delivery/`) only.

## 5. Acceptance criteria (precision gate — VISUAL fidelity is mandatory, not optional)
- **AC-1** No legacy cream: grep shows zero `--paper:`/`#f5f3ec`/"Cool Stone" ground in served CSS; `body`
  background computes to `#f8fbf8`. Verified by `preview_inspect` on the live/local page (computed style),
  not just by screenshot.
- **AC-2** Design app-shell present on **every** route: `.sh__nav` desktop + `.sh__nav--mobile` bottom bar +
  `#sfa-logo`; active nav state correct per route; legacy `.gj-shell`/`.dt-shell` removed.
- **AC-3** **Pixel/visual fidelity:** each of the LOD300 frames (book-entry, crop-page simple/full/drill,
  calc-dash) compared side-by-side to the live render — palette, type (Assistant/Frank Ruhl Libre/Carmela),
  spacing, component look match. QA captures a design-vs-live screenshot pair per screen.
- **AC-4** `/calc/` interactive: `SFA_CALC` defined; the 6 interactive calcs recompute live; **14** calculators
  surfaced (not 5); export buttons functional (CSV downloads; PDF opens print view, no 404).
- **AC-5** No regressions: `composer test` green; `validate_aos.sh` 0 FAIL; no LOCKED Python backend/migration
  touched; existing routes still 200.
- **AC-6** RTL legibility preserved; no raw DB keys / "Array" / stray "—"; watercolor art + heroes render.

## 6. Process (per team_100 role — team_00 directive)
1. **team_00 FINAL approval of this characterization (אפיון) BEFORE build.** ← we are here.
2. team_100 authors LOD400 (precise: exact files, token map, shell markup, calc-load fix) → **team_190 L-GATE_S** (non-Claude, IR#1).
3. **Build = team_10** (Claude sub-agent). **QA = team_50** with a NEW mandatory standard: **design-vs-live
   visual comparison per screen** (the gap the prior 2 QA rounds missed — 200-OK/0-console-errors is NOT enough).
4. **L-GATE_V = team_190 NON-CLAUDE** (IR#1/#5) — includes a visual-fidelity check, not only functional ACs.
5. Closure per ADR042 (archive mandate to team_191).

## 7. Effort
LARGE — touches the shared shell + every page's chrome + the global palette. Higher blast radius than a patch;
hence a full WP with team_00 LOD200 sign-off and a stricter (visual) QA gate.
