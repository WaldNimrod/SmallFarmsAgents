# SFA UI Redesign — Step 2 Handoff (WP-CB-UI-REDESIGN)

**From:** team_35 (Design Studio / claude-design) → **To:** team_100 (spec) + team_200 (build)
**Date:** 2026-06-08 · **Stage:** LOD300 hi-fi, implementation-ready · **Lang:** Hebrew, RTL, mobile-first

This package is the refined hi-fi mockup set produced after the Step-1 REVIEW_RESPONSE was
discussed and the recommended defaults were approved. It is **design, not production code** —
standalone HTML, any backend mocked in-browser.

---

## Start here

1. **`00_DESIGN_BOARD.html`** — the entry point. All 7 screens, each shown at **desktop (1280px)**
   and in a **375px phone frame**, live and interactive. Open any screen full-screen from the board.
2. **`HANDOFF_NARRATIVE.html`** — screen-by-screen narrative, state notes, decisions log, tweak inventory.
3. This README — integration notes for the build.

Open the HTML files directly (`file://`) or serve the folder statically. Google Fonts load from CDN;
everything else is local. `mock.css` + `mock-v2.css` + `sfa-icons.js` + `wc/` must sit alongside the HTML.

---

## What's locked vs. what's new

| File | Status | Notes |
|---|---|---|
| `mock.css` | **LOCKED — unchanged** | Mirrors nimrod.bio Design System v3 tokens. Do not edit. |
| `mock-v2.css` | **NEW (refinement layer)** | Loads *after* each page's inline `<style>` so it wins on equal specificity. All Step-2 fixes live here. |
| `sfa-icons.js` | **NEW** | 26-glyph inline-SVG sprite, injected once into `<body>`. Replaces all emoji. |
| `*.html` (7) | refined | Emoji → icon markup; per-screen fixes applied. |
| `wc/` | unchanged | Watercolor crop + module illustrations — the visual identity. |

> The two-file approach (`mock.css` untouched + `mock-v2.css` overlay) is deliberate: it lets you
> fold the refinements into the real Design System gradually, or promote `mock-v2.css` rules into
> `tokens.css` wholesale. **Both changes are raised as formal DESIGN_SYSTEM_EXTENSION_REQUESTs** —
> see below.

---

## DESIGN_SYSTEM_EXTENSION_REQUESTs (to fold into the DS)

### DSX-1 — icon set
`mock.css` has color/type/radii/shadow tokens but **no icon system**, which is why the original
mockups fell back to OS emoji (breaking locked principle #6). Delivered as `sfa-icons.js`:

```html
<svg class="gi" aria-hidden="true"><use href="#i-sprout"></use></svg>
```

- 26 symbols, `viewBox 0 0 24 24`, monochrome, inherit `currentColor`.
- `fill="none" stroke="currentColor"` are baked as **attributes on each `<symbol>`** (not CSS) so
  they render as outlines in every engine — do not rely on CSS `fill` inheriting into `<use>`.
- `.gi` (in `mock-v2.css`) sets size `1.05em` + stroke; container font-size drives the glyph size,
  matching the emoji footprint it replaced.
- IDs: `i-sprout i-seedling i-drop i-shield i-companions i-box i-tractor i-bulb i-journal i-receipt
  i-scale i-leaf i-snow i-calendar i-repeat i-basket i-chart i-compost i-grid i-rows i-book i-cap
  i-gear i-download i-shekel i-info i-flame`.
- **For production:** swap the inline sprite for your build's icon pipeline if preferred, but keep
  the same IDs/semantics. Watercolors stay for crops & modules — icons are for UI affordances only.

### DSX-2 — named type scale (readability floor)
Encodes the answer to the founding "illegible sizing" complaint. In `mock-v2.css`:

```css
:root{ --fs-body:17px; --fs-data:18px; --fs-secondary:14px; --fs-micro:13px; }
@media(min-width:760px){ :root{ --fs-body:18px; --fs-data:19px; } }
```

Floor: nothing below **13px**, secondary text **≥14px**. Refactor surfaces to reference these tokens
instead of literal px (that drift is how secondary text fell to 11px originally).

---

## Key fixes & how they're implemented (for the build)

- **RTL number integrity** — every numeric/range/value run is LTR-isolated + `white-space:nowrap`
  (`.num`, and the value selectors in `mock-v2.css`). **Numbers, units, dates must never bidi-break.**
  When you template values, wrap them: `<span class="num">65–80</span>`.
- **Data-list de-crush** — crop drill-down `dl` is forced to 2 columns desktop / 1 mobile
  (`.stage .dl, .topic__body .dl`), values `nowrap`. Don't revert to `auto-fit minmax(220px)`.
- **Calc step badge** — `.step__h` is a 3-column grid (`auto 1fr auto`) reserving the badge column;
  the title wraps in its own cell. Goal-grid availability chips get top clearance via `.goals{margin-top}`.
- **Mobile header** — `≤680px`: search + account collapse, nav moves to a scrollable full-width row.
  Each surface already has its own in-page search, so the header search is hidden on mobile by design.
- **Knowledge ⓘ** — 44px touch target via `.qm::after`. On touch, tap opens the L2 "ידע SFA" modal
  directly (hover L1 tooltip is pointer-only). Ensure every ⓘ resolves to real L2 content.
- **Sandbox chrome** — the `.mockbar` caption bar is force-hidden for the handoff (`display:none`).

---

## States covered (verify in build)

- drill-down **closed** (key data) / **open** (depth) — crop stages, market cards
- knowledge **ⓘ L1** hover tooltip → **L2 "ידע SFA"** modal (definition + formula + source + contribute)
- calc: goal → result-shape switch (scalar / DATE / DATE-RANGE / DATE-LIST / RANKED-LIST + scalar+₪ + scalar+DATE)
- calc honest **no-data** (select בטטה + a date goal → "אין עדיין נתון … עזרו להשלים")
- market freshness: **fresh / aging / stale** (greyed, "אין מגמה")
- **mobile 375px** reflow of every screen (see the phone frames in the Design Board)

## Content dependency (not a UI gap)

The crop page's **story prose** (`description_md`) and **in-season treatments** (`care.{watering,
fertilizing,pests}_md`) are not yet published. The mockup's care section is populated from the real
phytoprotection fixture to show intent. The UI ships with honest empty-states until the content WP
authors + wires these. No server/schema work is implied by this UI WP.

---

## Out of scope (unchanged from brief)

Production code / LOD400 executable spec · new product features (calc engine is WP-CB-CALC) ·
dark mode (deferred) · inventing a new visual language (DS is locked).
