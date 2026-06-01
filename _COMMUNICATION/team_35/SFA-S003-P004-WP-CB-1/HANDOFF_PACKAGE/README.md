# Handoff: Crop Book v1 — calculator-driven (SFA-S003-P004-WP-CB-1)

> **From:** team_35 (Design Studio) · **To:** the implementing developer (Claude Code)
> **WP:** SFA-S003-P004-WP-CB-1 — Crop Book v1 · **LOD300 design package**
> **Live site being evolved:** `https://sfa.nimrod.bio/crop-book/` (currently a read-only book → becomes a planning tool)

---

## Overview

The SFA **Crop Book** is a Hebrew (RTL) agronomic reference for small market-gardeners and home growers. This WP turns the read-only book into a **planning tool** driven by **14 calculators**, with an **AssumptionField** component, honest **complete/partial** data states, a **multi-parameter filter**, a **calculator dashboard**, and a per-crop page at three depths organised by subject (down to JMF-MasterClass reference depth).

The product has four top-level surfaces (one nav): **ספר גידולים (Crop Book)** · **מחשבון (Calculator)** · **מחירון (Market/Pricelist)** · **חשבון (Account)**. This WP builds the **Crop Book** and **Calculator** surfaces; the others are stable nav hooks for future modules.

---

## About the design files

The files in `design/` are **design references created in HTML/CSS/JS** — a single pannable spec board that prototypes the intended look and behavior. **They are not production code to ship as-is.** Your task is to **recreate these designs in the target codebase's environment** using its established patterns.

**Target delivery tier (locked by the WP):** **Slim4 / PHP on uPress**, server-rendered templates (Twig/PHP) + **light vanilla JS** for the interactive calculators & filters. No SPA framework. `design/cropbook-v1.js` is written in plain ES5-ish vanilla JS precisely so it maps 1:1 to that tier — you can port it almost directly. If you are implementing in a different stack, treat the HTML/CSS as the visual contract and the JS as the behavior contract.

The whole UI is **Hebrew, RTL** (`dir="rtl"`). Brand: **Nimrod.bio AOS Design System v3.4** + watercolor crop masters + Carmela display font.

---

## Fidelity

**High-fidelity (hifi).** Final colors, typography, spacing, radii, shadows, and interactions are all specified here and in `design/tokens.css` + `design/cropbook-v1.css`. Recreate pixel-accurately. The one caveat: the board is a *spec canvas* — the device frames (`.frame`, `.board`, `.sec`, `.notes`, `.ab__label`) and the English annotations are **review chrome, NOT part of the product**. Build only what is *inside* the frames (the `.sh` app shells). Everything inside a `.sh` is real product UI.

---

## File map

```
design/
  LOD300 Crop Book v1.html   ← the spec board. Each product screen is a .sh block inside a .frame.
  tokens.css                 ← :root design tokens + base type. PORT THIS FIRST (verbatim values).
  cropbook-v1.css            ← every component style. Class prefixes: .cb-/.cv-/.af/.topic/.ref…
  cropbook-v1.js             ← behavior: calculators, AssumptionField, filters, pagination, depth tabs, tooltips
  assets/
    Carmela.ttf              ← brand display/wordmark font (licensing: confirm web-embed — OPEN_ISSUES Q3)
    wc-lettuce.png           ← watercolor master (חסה) — sits on near-white via mix-blend-mode: multiply
    wc-radish.png            ← watercolor master (צנונית)
    wc-parsley.png           ← watercolor master (פטרוזיליה)
    wc-dill.png              ← watercolor master (שמיר)
spec/
  COMPONENTS-delta.md        ← component contracts (AssumptionField, CalcPanel, topic taxonomy, filters, …)
  DESIGN_TOKENS-delta.md     ← token additions + the v2 white-green palette table + field-ordering rule
  TEMPLATES-delta.md         ← route map, Jinja/Twig macro list, page contracts, export endpoints
  OPEN_ISSUES.md             ← 8 open questions for team_100/team_00 + the JMF gap-analysis (7 new fields)
```

> **Note:** the SFA **system logo** is an inline SVG `<symbol id="sfa-logo">` defined once at the top of the HTML `<body>` (a sprout rising from three planting beds). It is **not** an image file. Do **not** use the old garden/radish logo — it was removed. Reuse the symbol via `<use href="#sfa-logo"/>`.

---

## Design tokens (port `tokens.css` verbatim)

### Palette — v2: white with a whisper of green
Neutrals (the page ground). **Do not** revert to the old cream/brown.
| token | value | use |
|---|---|---|
| `--gj-paper` | `#f8fbf8` | page background (near-white, faint green) |
| `--gj-paper-2` | `#eef4ee` | panels, table headers, inset blocks |
| `--gj-paper-3` | `#dde8dd` | deeper fills, track backgrounds |
| `--gj-ink` | `#1f2a22` | primary text + dark chrome ground (green-charcoal) |
| `--gj-ink-soft` | `#5d6b5e` | secondary text, labels |
| `--gj-line` | `#dce6dc` | borders, dividers |

### Accent "worlds" (unchanged from AOS v3.4)
| token | value | meaning |
|---|---|---|
| `--gj-leaf` / `--gj-leaf-deep` | `#6f8a45` / `#4d6a2c` | book / open / **validated** / primary actions |
| `--gj-leaf-soft` | `#9bb172` | viz fills (season bar, spacing dots) |
| `--gj-tomato` / `--gj-tomato-deep` | `#c24f2c` / `#8e3018` | market / attention / **missing** |
| `--gj-sun` / `--gj-sun-deep` | `#d39a32` / `#a4711a` | beta / calculator / warnings / **unvalidated** |
| `--gj-soil` / `--gj-soil-deep` | `#8b5d2f` / `#5a3c1a` | paid / earth / calculator result numerals |
| `--gj-code` / `--gj-code-deep` | `#2d8a8c` / `#1f5e60` | digital / **AssumptionField** accent |
| `--status-error` | `#c43a2e` | errors |
| `--cb-assume-wash` | `#e3eeee` | AssumptionField panel background |

### Topic colors (per-subject coding — see "Topic taxonomy")
`--t-nursery: var(--gj-code-deep)` · `--t-grow: var(--gj-leaf-deep)` · `--t-harvest: var(--gj-sun-deep)` · `--t-yield: var(--gj-tomato-deep)` · `--t-inputs: var(--gj-soil-deep)` · `--t-pest: #7a3b6b`

### Typography
| token | stack | use |
|---|---|---|
| `--gj-font-body` | `"Assistant", "Heebo", system-ui, sans-serif` | all body + UI text (incl. field micro-labels) |
| `--gj-font-head` | `"Frank Ruhl Libre", "David Libre", serif` | headings, numeric values, crop names |
| `--gj-font-mono` | `"JetBrains Mono", "SF Mono", Menlo, monospace` | code/keys/eyebrows (LTR technical only — never Hebrew labels) |
| `--gj-font-brand` | `"Carmela", "Frank Ruhl Libre", serif` | SFA wordmark + hero display only |

Type scale (px): h1 32/900, h2 24/700, h3 18/700, body 13–15/400–600, labels 11.5–12/600–700, mono eyebrow 10–11/700. Headings use negative letter-spacing (~-.01 to -.02em). **Hebrew labels must use the body face — never mono/uppercase** (mono uppercase is unreadable in Hebrew; this was an explicit correction).

Google Fonts import (in `tokens.css`): `Assistant 300–800`, `Frank Ruhl Libre 500/700/900`, `JetBrains Mono 400/500`. Carmela is `@font-face` from `assets/Carmela.ttf`.

### Radii / shadows / spacing
Radii: `--gj-r-s 8` · `-m 12` · `-l 14` · `-xl 18` · `-pill 99px`.
Shadows (green-neutral): `-s 0 1px 3px rgba(30,50,35,.05)` · `-m 0 4px 14px rgba(30,55,38,.07)` · `-l 0 8px 28px rgba(28,55,38,.11)`.
Spacing (4-pt): `--gj-sp-1..7` = 4 / 8 / 12 / 16 / 24 / 32 / 48px.

### Color-mix convention
Soft tint backgrounds use `color-mix(in oklch, var(--gj-X) N%, var(--gj-paper))`. Keep this — it auto-adapts tints to the paper tone.

---

## The screens / views

Each is a `.sh` (app shell) block inside a frame on the board. Shared shell: `.sh__bar` (logo + wordmark + `.sh__nav` + account + search) → optional breadcrumb → `.sh__body` → `.sh__foot` (status strip). Mobile shell adds a bottom tab bar `.sh__nav--mobile`.

### Global nav — `.sh__nav` (every screen)
Persistent top-level switch: **ספר גידולים** (book, active = leaf) · **מחשבון** (calc, active = sun) · **מחירון** (market, active = tomato) · account button (`.sh__acct`, soil avatar). Mobile = 4-item bottom tab bar (ספר/מחשבון/מחירון/חשבון). Account is a stable hook to a future module.

### 1 · Book list page (`/crop-book/`) — §2.1
- **Audience switch** (`.aud`, top of body): **כרטיסים (Cards)** = gardener/student (default) ⇄ **טבלה (Table)** = farmer. Same data, different density. Toggles `[data-aud-view="cards|table"]`; persist client-side; Cards is the cold-start default.
- **Filter bar on top** (`.ftop`, above results — NOT a sidebar):
  - Always-visible row (`.ftop__top`): free-text search + **"סינון מתקדם" toggle** (`.ftop__advbtn`, default **closed**) + live match count.
  - Collapsible panel (`.ftop__adv`, `#adv-filters`): filter groups — **משפחה** (family, multi) · **עונת גידול** (season chips multi *or* a specific date input) · **זריעה / שתילה** (sow-direct vs transplant, single) · **דורש הצללה בקיץ [ישראל]** (single) · **עמידות לקרה** (single) · **ימים להבשלה** (DTM range slider) · **מצב ספר** (completeness, single).
  - Panel footer (`.ftop__advfoot`): match count + **↺ איפוס פילטרים (reset, lives inside the panel)** + **החל סינון (apply)**.
  - **Defaults = search-all** (multi groups empty, single groups on "הכל"); reset restores `[data-default-on]` chips and clears text/date.
- **Cards grid** (`.cards-grid`, `repeat(auto-fill, minmax(168px,1fr))`): each `.ccard` = watercolor/emoji art (corner state dot ✓complete / !partial), crop name (he) + en, **graphics block** (`.cardviz`: a 12-cell **season timeline** `.seasonbar` with on/peak months + a **yield mini-bar** `.minibar`), and a meta row (calculator pips `.ccard__calcs` lit/dim + DTM `.ccard__dtm`).
- **Table** (`.ptable`): sortable columns גידול/משפחה/DTM/מרווח/יבול/מחיר + **calculator columns**, all normalized **per bed-meter** for unit consistency: זרעים/מ׳ (#1) · הכנסה/מ׳ (#9) · רווח/מ׳ (#13). `.calc-cell` amber tint; `*` propagates from unvalidated inputs; `—` for missing.
- **Pagination** (`.pager`, both views): default **25/page** with a rows-per-page select (25/50/100), prev/next, page numbers + ellipsis.

### 2 · Crop page (`/crop-book/<slug>/`) — §2.2 — three depths, organised by subject
Crop hero (`.crophero`: art, breadcrumb, name, scientific name, **state badge** complete/partial + field coverage). **Depth tabs** (`.depths`): פשוט (Simple) / מלא (Full) / העמקה (Drill-down) — toggles `[data-depth-view]`. **One route**; depth is a param, not navigation.

**All three depths are organised by a 13-topic taxonomy** (see below) so the page reads as a plan.
- **Simple (`simple`)**: 4 headline `.hv` values + a **per-topic summary grid** (`.tsum` of `.tcard`, 1–2 key numbers each) + one live calculator (yield) + rotation hint.
- **Full (`full`)**: every mandatory field in **collapsible topic sections** (`.topic`, click header to toggle `.is-collapsed`). 2-col field grid (`.fieldgrid`). New JMF-derived fields tagged **"מוצע" (proposed)**.
- **Drill-down (`drill`)**: (a) **variety-comparison table** (`.vtable`) with an averages `<tfoot>`; (b) **per-source reference sheet** (`.refsheet`) — source tabs EX/PR/WR (`.ref-srctab`) over topic rows (`.reftopic`) in canonical JMF order, each with per-topic provenance + key/values + step bullets; (c) **provenance hierarchy** (`.prov`) for the headline value (one winning value, EX/NI override > PR > WR).

### 3 · Calculator dashboard (`/calc/`) — §2.3b
Not a wizard — a **dashboard of connected modules**. Shared dark **context** strip (`.calc-context`: crop + #beds + target date) feeds every calculator. Each calculator = a **module card** (`.modcard`) in a grid (`.calc-dash`), grouped by `.dash-group` (זרעים וזריעה / לוח זמנים / יבול והכנסה / דישון). Modules are **wired** — outputs flow between cards (`.modcard__feed` "→ מזין מודול 3" / "← מ-מודול 1") and into a sticky **summary** (`.calc-summary`, each row tagged with its source module). One **export** block (`.calc-export` → PDF / CSV). **Architecture contract: one calculator = one module; `/calc/` = a dashboard that mounts modules + aggregates the summary; the same module embeds standalone inside crop pages.**

---

## Key components & their contracts

### AssumptionField — `.af` (NEW, first-class)
A planning assumption that is **never a silent constant**. Four mandatory parts: **(1)** default value (always visible in `.af__bar`), **(2)** inline override input (`[data-assume]` with `data-scale`), **(3)** an attractive when/why/how explainer (`.af__explain`), **(4)** a "read more →" link (`.af__more`) to a nimrod.bio post. Two states: collapsed (bar only) / expanded (`.is-open`). Reads default/unit/explainer/post_url from an `ASSUMPTIONS` registry. **Never disables a calculator** — always carries a default. Launch-blocking content: `germination_rate (90%)` + `bed_width (80 cm)` must have a live post URL. Teal accent (`--cb-assume`).

### Calculator panel — `.cv` (`data-calc="<kind>"`)
Header (number + title + audience badge) → **book-value chips** it reads (`.bv`, green, each with `↗ ספר` cross-link; editable variants `.bv.is-editable` show an override flagged `.is-overridden` "שונה מהספר" + restore) → optional inline AssumptionField → **user inputs** (`.ipt`) → **result** + formula. **Three operand languages:** green = book value, teal = assumption, neutral = user input. Disabled state `.cv.is-disabled` when a **required book field is MISSING** (names the field + "request info"; only MISSING disables — never unvalidated). Grouped sequence `.cv-seq` for #1→#3→#4.

**Surfacing (decided):** on the crop page the small calculators are **buttons** (`.calcbtn`, in-context) that **open the panel as a module overlay over the page** (`.calcmodal`, `[data-calc-open="<id>"]` → `.is-open`; close via `[data-calc-close]` or overlay click). The **full multi-calculator page is separate** (the dashboard, `/calc/`). **Every calculator is a self-contained module — the basis for the future system**; the same module renders inline (dashboard), in a crop-page modal, and as a table column.

### Provenance / confidence cues — §2.5
- **Validated** → plain value (EX/NI override or confidence ≥ τ=0.40).
- **Unvalidated** → `.ast` asterisk + hover/focus tooltip (`.tip__pop`); asterisk **propagates** to any calculator output that consumed it. (Validated = EX/NI override or confidence ≥ **τ = 0.50**.)
- **Missing** → `.val--missing` "—" + `.reqinfo` request-info CTA.
Complete vs Partial crop rollup = `all(field validated)`.

### Field info tooltip — `.finfo` (every field)
Every field carries `data-field="<key>"`; JS (`FIELD_INFO`) fills the **Hebrew label** (if empty) and appends an ⓘ affordance with a designed tooltip (Hebrew name + full explainer + the technical DB key in mono, dev-reference only). **No raw DB key is ever shown to the user as a label.**

### Topic taxonomy (the 13 subjects — canonical, from JMF MasterClass sheets)
`זנים · מרווח ופריסה · ציוד וכיוונון · קרקע ודישון · הכנת ערוגה · זריעה/שתילה · השקיה · טיפוח ועישוב · מזיקים ומחלות · קציר · שטיפה ואחסון · רצף וחברה` (+ יבול/הכנסה for calc-facing values). Used to organise all three depths and the reference sheet. Color-coded via `--t-*`. **Field ordering within a topic is critical: related fields must be adjacent** — `rows_per_bed`+`in_row_spacing_cm` pair; timing fields (`harvest_window`+`succession_interval`) pair; climate (`frost_tolerance`+`needs_summer_shade`) pair; water (`irrigation_type`+`root_depth_class`) pair. The 2-col grid renders each pair as one row.

### Rotation hint — `.rothint` (§2.6)
Informational chip from botanical family ("אל תעקבו אחרי {family} … 3 עונות"). Not a calculator; gap = `rotation_gap_seasons` assumption (default 3).

---

## Interactions & behavior (see `cropbook-v1.js`)
- **Calculators** recompute live on input. `CALC[kind]` holds pure formulas mirroring the approved catalog (seed/yield/revenue/pop/frost/fert). Book operands read from `[data-book][data-val]` (or the editable `.bv__in`); user inputs from `[data-k]`; assumptions from the `A` registry.
- **AssumptionField**: bar click toggles `.is-open`; `[data-assume]` writes the live value (× `data-scale`), echoes to `[data-assume-echo]`, and recomputes all dependents; `[data-reset]` restores default.
- **Editable book value** (`.bv__in`): on change, flag `.is-overridden`, update `data-val`, recompute; restore button reverts. Book SSoT is never mutated.
- **Filters**: chips toggle (`[data-single]` = radio within group); `[data-filter-toggle]` expands the advanced panel; `[data-filter-reset]` resets chips to `[data-default-on]` + clears inputs + resets counts.
- **Pagination** & **depth tabs** & **topic collapse** & **audience switch** are simple class-toggle handlers (see the named `wire*` functions).
- Tooltips open on hover AND `:focus-within` (keyboard accessible).
- **Motion budget:** hover lift on cards (`translateY(-2px)` + shadow), 140–180ms; AssumptionField ✎ rotates 45° on open; chevrons rotate. No large animations.

## State / data
- **SSoT:** both audience views and all depths read the same reconciled `value_best` per field; depth/audience/filters never change the query, only the template + density. **Validated when EX/NI override or confidence ≥ τ = 0.50.**
- **Decisions (resolved with Nimrod — see `spec/OPEN_ISSUES.md`):** override persistence = **per-session**; audience default = **always Cards**; Carmela = **licensed, self-host, enforce one consistent type system**; **τ = 0.50**; request-info = **one simple/basic community-CTA capture** (a marketing + feature-idea funnel, *not* an active community-management system — keep it lightweight); small calcs = **buttons → module overlay**, full calc = **its own page**, each module is a reusable base; price unit = **normalize in main UI, show all data in calculator + full depth**; `days_in_nursery_cell` duplication **removed** (single "ימים במשתלה"); `needs_summer_shade` = **3 levels 30/40/50%**.
- Calculator state is ephemeral client-side. AssumptionField overrides: ephemeral per-session in v1 (see OPEN_ISSUES Q1).
- Export endpoints (TEMPLATES-delta): `GET /calc/export.pdf?plan=…`, `GET /calc/export.csv?plan=…`. Request-info posts `{kind:"request-info", field_name, crop_slug}` to `/api/v1/contribute`. Assumptions served from `GET /api/v1/assumptions`.

## Assets
- **Watercolor crop masters** (`assets/wc-*.png`) — Devora's brand masters. They sit on near-white paper via `mix-blend-mode: multiply` (no transparent background needed). Available: lettuce, radish, parsley, dill. Crops without a master fall back to an emoji/SVG glyph (tomato 🍅, cucumber 🥒) until art exists.
- **Carmela.ttf** — wordmark/hero display only. Confirm web-embedding license (OPEN_ISSUES Q3); a wordmark SVG is the fallback.
- **System logo** — inline SVG `<symbol id="sfa-logo">` (in the HTML). Not a file.

## Out of scope / open questions
Calculator math semantics, data schema, and deploy are owned elsewhere. `spec/OPEN_ISSUES.md` has 8 open questions for team_100/team_00 **and a gap-analysis**: 7 field groups the JMF originals carry that the schema should add (seeder model/settings, irrigation type + root-depth class, pests & diseases, unit-of-sale/bunch size, labor productivity rates, #plantings/harvest-weeks). These are mocked as **"מוצע"** pending ratification — implement the UI slots but flag the data as proposed.

---

## Build order (suggested)
1. Port `tokens.css` (`:root` + base type + fonts) verbatim. Verify RTL + fonts load.
2. Build the **app shell** (`.sh` + `.sh__nav` + mobile tab bar) and the **system logo** symbol.
3. Book list: audience switch → cards (with `.cardviz` graphics) → table (per-meter columns) → top filter bar (collapsed advanced + in-panel reset) → pagination.
4. Crop page: depth tabs + the **topic taxonomy** scaffolding → Simple → Full (collapsible topics) → Drill-down (variety table + reference sheet + provenance).
5. **AssumptionField** + **Calculator panel** components (port `CALC` formulas) → Calculator dashboard.
6. Provenance cues, field tooltips (`FIELD_INFO`), rotation chip.
7. Wire export + request-info + assumptions endpoints.

Re-open `design/LOD300 Crop Book v1.html` in a browser at any point to compare pixel-for-pixel — it is the source of truth for spacing and color.
