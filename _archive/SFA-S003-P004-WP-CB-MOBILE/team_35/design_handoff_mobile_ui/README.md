# Handoff: SFA Mobile UI + sanctioned Desktop fixes (Crop-Book / Market / Calculator / About)

> **WP:** SFA-S003-P004-WP-CB-MOBILE · **From:** team_35 (UI/interface) → **Claude Code dev** · **Build owner:** team_10 · **Visual QA:** team_50 @375 · **Date:** 2026-06-05 · **Version:** v4.0.0
> **Live app:** sfa.nimrod.bio (Hebrew / RTL) · **Stack in repo:** PHP delivery (`sfa_delivery/`, Twig-ish templates + controllers) + Python crop-book/market models.

---

## Overview
SFA ("Small Farms Agents") is a free, open knowledge + planning app for small growers: a **crop-book** (68 crops — sowing calendars, spacing, yield, sources), a **market price-list**, and a **planning calculator** (14 calculators). The app is live and the **desktop** crop-book/market are launch-quality and **locked**.

This package fixes the **mobile (375px)** experience — which was the launch blocker — across four areas, **and** carries **two narrowly-scoped desktop changes** the client explicitly approved during review. It also folds in three rounds of client review (the full list of structural/layout decisions is in §"Exactly what we agreed", below).

The four mobile defects this resolves (original blocker report from team_00):
1. Crop-page **hero overlapped** its content.
2. **Planting calendar** was unreadable and **leaked raw `IL_general`-style keys** into the UI.
3. **Market** rendered **one card per row** → a ~12,500px scroll.
4. Entry cards let the **DTM number dominate the crop name**.
5. **/about** had too many tiers; active-vs-coming was unclear.

---

## About the design files
The files in `design_files/` are **design references authored in HTML/CSS** — prototypes that show the intended **look, structure, and behavior at 375px**. They are **not** production code to paste in.

Your task is to **recreate these designs inside the SFA codebase's existing environment** (the PHP `sfa_delivery` templates + the existing CSS layers), reusing its established patterns, class names, and data bindings. The prototypes deliberately reuse the **real production class names** (`.ccard`, `.pcal`, `.topic`, `.mkt-table`, `.modtile`, `.qb-*`, `.sh__*`) so most of this lands as **CSS + small template additions**, not a rewrite.

**The single most important artifact is `design_files/mobile-fixes.css`.** It is written as a **portable override layer** intended to load **last**, after the three existing stylesheets. Almost everything here is achievable by (a) shipping that override layer and (b) adding a handful of new DOM hooks in the templates (listed per-fix below).

> Hebrew/RTL note: the whole app is `dir="rtl"`. Use **logical properties** (`inset-inline-start`, `margin-inline-end`, `padding-inline`) — never hard left/right. The one place LTR is forced is **numbers/units** (prices, Latin names, month digits) via `dir="ltr"`/`unicode-bidi: isolate`.

---

## Fidelity
**High-fidelity.** Final colors, typography, spacing, iconography, copy, and interaction states. Recreate pixel-faithfully using the existing CSS variables in `tokens.css`. Do not introduce new colors or fonts — everything maps to existing tokens.

---

## The CSS layer model (read this first)
Four stylesheets, **load in this exact order**:
1. `tokens.css` — design tokens (colors, type, radii, shadows, topic colors). **Source of truth for all values.**
2. `cropbook-v1.css` — crop-book base components.
3. `classb.css` — the "Class-B" app-shell + market + calculator + tier components.
4. **`mobile-fixes.css`** — **this delivery.** Loads LAST. Overrides are `@media (max-width: 480px)` **except** the explicitly-flagged global pieces (see "Desktop-reaching changes").

`mobile-fixes.css` is organized into labelled banner sections — implement them in this order; each maps to a fix below:
`DENSITY` · `CROP CARD` · `IN-SEASON` · `CTA SYSTEM` · `CALENDAR .pcal` · `CROP DEPTHS` · `MARKET (table + disclaimer + RTL price)` · `TYPE MINIMUMS` · `CALC (goal grid + session + assumptions)` · `ABOUT`.

---

## ⚠️ Desktop-reaching changes (client-approved — must be ratified by team_00)
Everything else is mobile-only (≤480px) and **must not regress desktop**. These **two** are intentional global changes the client asked for in review:

### D1 · Market default view = **TABLE** (desktop + mobile)
The market keeps its existing **cards ⇄ table** toggle, but the **default flips to table**. Rationale: one-card-per-row was the mobile blocker, and the client wants the dense table as the landing view everywhere. `mobile-fixes.css` → section `FIX 3 · MARKET`. Implementation: server/initial render sets the market scope to `table`; the toggle still switches to cards and persists the user's choice.

### D2 · Type-minimum floor (desktop + mobile)
Client: "none of our fonts should be too small — desktop is too small." A **targeted** (not blanket) floor raises the smallest micro-text to a readable minimum: **~11px for mono micro-labels, ~12px for body-ish text** (`fg dt` 13 / `fg dd` 14). `mobile-fixes.css` → section `TYPE MINIMUMS` lists every selector + value. It is intentionally selector-targeted so layout holds; apply it globally (it sits outside the media query on purpose).

> Action for team_00: ratify D1 + D2 against the "desktop locked" rule before team_10 ships.

---

# Screens / Views

Eight mobile surfaces (all 375px, RTL). Each prototype is a standalone HTML file in `design_files/`, and all eight are tiled in `SFA Mobile Design Board.html` (the design SSoT — open this first to see them side-by-side).

All surfaces share the **app shell** (`.sh`): a top bar (`.sh__bar`: back/logo · contextual center · search) and a bottom tab bar (`.sh__nav--mobile`: ספר · מחשבון · מחירון · חשבון). Body padding is a tight **12px** (`.sh__body`) per the density pass.

---

## 1 · Hub / home — `surface-hub.html`
**Purpose:** Launch point; route to the three live tools, preview what's coming, and offer the CTAs.

**Layout:** vertical stack inside `.sh__body--wide`. Intro (`.hub-intro`) → group bar "הכלים שלך" → **row launchers** (`.hub-grid` of `.modtile--row`) → group bar "בקרוב" → coming tiles → `.cta` block → bottom nav.

**Tool launchers (`.modtile--row`):** horizontal card — illustration panel (warm `#f6f3ea`) on the inline-start, body (title + one-line desc + stat + "פתחו ›") filling the rest.
- **CRITICAL — use the REAL module illustrations from the repo**, not hero washes:
  - Crop-book → `public_assets/img/modules/module-crop-book.png`
  - Market → `public_assets/img/modules/module-market.png`
  - Calculator → `public_assets/img/modules/module-calc.png`
  - `object-fit: contain`, ~9px padding. (Copies are bundled in `design_files/assets/modules/`.)
- Tier badge per tool: crop-book/market = `tier--leaf` "פתוח"; calc = `tier--sun` "בטא".
- **Coming tiles** (`.is-soon`): icon-only (no placeholder art) — a single glyph in a muted panel + "בפיתוח"/"בקרוב". Two: "מתכנן עונה", "ניהול לקוחות ומלאי".

**CTA block** (see CTA system §): data-completion (loud) + suggestion form + WhatsApp.

---

## 2 · Crop-book entry cards — `surface-cards.html`  *(FIX of defect #4)*
**Purpose:** Browse/search crops; surface what to plant **now**.

**Layout:** search+filter row (`.mfilt`) → horizontally-scrolling **season chips** (`.seasonchips`, default "עכשיו בעונה" active) → result count → single-column `.cards-grid` of `.ccard` → CTA.

**`.ccard` (compact ROW card):**
- `flex-direction: row`. **Small thumbnail** (`.ccard__art`, **66px** wide; **88px** for featured) on the inline-start with a 1px divider; body fills the rest.
  - The watercolour is a **small thumbnail at full opacity** — *not* a faint background wash (an earlier wash idea was explicitly rejected). Image is `object-fit: contain` at 74% of the panel.
- Body order: `.ccard__now` (in-season badge, if applicable) → `.ccard__name` (17px; featured 20px) → `.ccard__en` (English, 11px) → `.cparams` (icon language). **The name dominates; the DTM is just one chip among the params** — never larger than the name.
- **Completeness dot** (`.ccard__state`): top-inline-start, `--complete` ✓ (leaf) or `--partial` ! (sun).
- **Featured first card** (`.ccard--feat`): bigger thumb + a one-line `.ccard__desc` + `.ccard__feattag`.

**`.ccard__now` in-season badge** (the new "what to plant now" signal): pill, leaf-tinted — `🌱 עכשיו לזריעה` or `🪴 עכשיו לשתילה`. Driven by `CropPlantingCalendar` for the current month + activity type.

**Icon language `.cparam`** (shared vocabulary — reused on crop pages too):
`--dtm` ⏳ days · `--yield` ⚖ kg/m · `--space` ⇲ spacing · `--water` 💧 · `--method` 🌱/🪴 sow/transplant. Each is `<span class="cparam cparam--x"><span class="g">icon</span>value<small>unit</small></span>`.

---

## 3 · Crop page — three depth views  *(FIX of defects #1, #2)*
Files: **Simple** `surface-crop.html` · **Full** `surface-crop-full.html` · **Deep** `surface-crop-deep.html`.

**Depth control** lives in the **header** (`.sh__depths`, a 3-way segmented control of icons; the active one shows its label) — this saves vertical space vs. an in-body control. Order: **פשוט (Simple) ◔ · מלא (Full) ▤ · העמקה (Deep) ⌖**.

**Hero (`.crophero`) — FIX of overlap defect:** a clean stacked block (no absolute-positioned overlap). Small art thumb + Latin/family breadcrumb (`.crophero__bc`, `dir=ltr`) + `<h1>` name (with `.gj-underline`) + scientific name + a `.statebadge` for completeness. Tight `padding-bottom` + bottom rule.

### Planting calendar `.pcal` — FIX of unreadable + raw-key leak (defect #2)
A compact 12-month grid with two tracks (sow / transplant). **NO raw keys may appear in visible text** — map everything to Hebrew:
- Region: `IL_general → כל הארץ` · `IL_north → צפון` · `IL_center → מרכז` · `IL_south → דרום` · `MED_general → אגן הים התיכון`.
- Activity: `seed → זריעה` · `transplant → שתילה` · `both → both`.
- Season: `spring/summer/fall/winter/all → אביב/קיץ/סתיו/חורף/כל השנה`.
- Cells: `.on` active month · `.peak` peak month · `.now` current month marker. Legend (`.pcal__legend`) + a plain-language note (`.pcal__note`) e.g. "היום יוני — מחוץ לעונה… החלון הקרוב: ספטמבר". Drives off `CropPlantingCalendar` (migration 049).

### Depth content — the rebalanced progression (client review #3)
The three depths must form a **clear Simple ⊂ Full ⊂ Deep progression**:

- **Simple (gardener-focused, genuinely minimal):** essentials chip strip `.ess` (spacing · DTM · water · method) → calendar → **one key value per topic** (`.keylist`/`.keyrow`: משתלה / גידול / קציר / יבול). **No full stat block, no per-field dump.** Aimed at a home gardener who needs spacing, seasons, and the headline per topic.
- **Full:** topic **overview** (`.tsum` of `.tcard`s) **+ every field (17)** organized into collapsible **`.topic`** sections with `.fieldgrid`/`.fg` dt-dd pairs (single-column on mobile). This is the "all the data, clearly organized" view.
- **Deep:** the **same topic structure as Full**, but **each datum opens up** — every `.fg dd` carries a `.rng` (range across varieties, e.g. "55 · טווח 40–58 · 8 זנים") and an **EX/PR/WR source pill row** (`.srcpill`), plus a **variety comparison table** (`.vtable`, horizontally scrollable) and a source-sheet topic. "Like Full, but every value expanded with comparisons + provenance."

> Source hierarchy shown in Deep: **EX** (expert) · **PR** (professional) · **WR** (web/network); the governing value is chosen by trust rank.

---

## 4 · Market price-list — `surface-market.html`  *(FIX of defect #3)*
**Purpose:** Scan current produce prices; filter by category; drill to a product.

**Layout:** header (title + freshness) → **collapsible disclaimer** → **category chips + view toggle** → table (default) / cards (toggle) → CTA.

**Collapsible disclaimer** (`<details class="mkt-disc">`, **closed by default**): the mandatory "what/where/why/why-not" note is a **summary title row + chevron** that expands on tap — it must not occupy the top of the screen by default (client: "the note is too big — title that opens on click"). Content (always present, just collapsed): מה (7-day rolling averages) · מאיפה (mezoo public scrapers + grower contributions) · למה (planning benchmark) · למה לא (not a local-market substitute).

**Category chips** (`.mchips`, horizontal scroll) — the **real product categories** from `products.category`, not invented ones:
`הכל · עלים · פירות-ירק · שורש · מצליבים · בצליים · דלועיים · קטניות · **סלים** · פירות · ביצים`
(**סלים** = baskets — was missing before; the underlying enum is `vegetables/herbs/baby/legumes/fruits/fruit_trees/grains/cover_crops` + `baskets`.) Single-select.

**View toggle** (`.aud[data-aud-switch]`): table ▤ / cards ▦. **Default = table** (also desktop — see D1).

**Table (`.mkt-table`) — default, dense:** 3 columns — מוצר (swatch + name + source count `dir=ltr`) · מחיר · מצב (freshness). Rows: `.is-stale` (aging), `.is-empty` (no data → "◐ תרמו" contribute link).

**RTL PRICE FIX (important):** prices/units were reordering under bidi. The fix: `.t-price` is a **column** — the LTR number stacked over the Hebrew unit:
```html
<span class="t-price"><span class="n">12.40</span><small>₪ / ק״ג</small></span>
```
`.t-price .n` is `direction: ltr; unicode-bidi: isolate`. This guarantees digits never reorder against the unit. Apply the same pattern anywhere a number meets a Hebrew unit.

**Cards (`.pcard`, toggle view):** retained for users who prefer them — swatch + name + price + range + 7-day sparkline + source count + freshness.

---

## 5 · Calculator — `surface-calc.html`  *(rebuilt: "define the question")*
**Purpose:** Pick a question, define its inputs flexibly, compute, and accumulate results across a session.

Two states in one scope (`#calc-scope[data-calc-state]`): **`ask`** and **`result`** (the prototype toggles via the compute/back buttons; `?state=result` deep-links the result state for review).

### ASK state — flexible question builder
Client direction: *don't assume area + target-date; let the user define the question, then compute.* Lead with an explainer (`.qb-intro`) + the builder (`.qb`):
- **Step 1 — what to calculate:** `.qb-goal--grid` = **6 primary calculator buttons** (זרעים לקנות · תאריך זריעה · יבול צפוי · הכנסה צפויה · כמות שתילים · צפיפות שתילה) **+ `.qb-more` `<select>`** holding the other **8** (14 calculators total). Map each to the existing `CALC[kind]` registry.
- **Step 2 — crop:** picker.
- **Step 3 — basis (flexible):** `.qb-basis` segmented — **לפי שטח / מס׳ ערוגות / מס׳ שתילים** (not always area). The relevant input field follows.
- **Step 4 — time anchor (optional):** `.qb-basis` — **תאריך יעד / תאריך זריעה / עכשיו** (not always target-date).
- **Natural-language echo** (`.qb__echo`): restates the assembled question. Then **"חשב ›"** (`.qb__go`).

### RESULT state
- **`.qb-session` — session memory:** every calculation in the session is **saved and accumulated** in a list (`.qb-session__row`, current one `.is-current`), with a "N חישובים · נשמר" badge. Confirm persistence scope with team_00 (per-device vs. account).
- **`.qb-answer`** big headline result + **`.qb-break`** breakdown rows, each tagged with its source (`קלט` input / `ספר` book / `הנחה` assumption).
- **`.qb-assum` — editable base assumptions:** a row that surfaces the assumptions in use (germination %, safety margin) + a **"✎ ערוך הנחות"** button that opens the shared **AssumptionField editor**. This is the **primary entry point** for editing assumptions; also expose it on the crop page's calculators and wherever an assumption feeds a number.
- **Export = the whole session** (`.calc-export`): PDF / CSV of **all** calculations done in the session, not just the current one.

---

## 6 · About — `surface-about.html`  *(FIX of defect #5)*
**Purpose:** Explain what SFA is; show what's open vs. coming; invite contribution.

**Content-first** (client: "lead with spread-out real content; the tiers are an expansion"):
- **`.about-intro`:** headline + lead paragraph (what SFA is) + **`.about-points`** — four points with icons: ידע פתוח · מחירי שוק שקופים · כלי תכנון · נבנה בשיתוף.
- **Tiers as a secondary expansion below** (`.about-tiers-h` divider, then two `.tier-group`s):
  - **פעיל עכשיו (2):** ספר + מחירון (OPEN CORE, leaf), מחשבון מלא (BETA, sun) — each `.tier-row` with a live status dot.
  - **בקרוב (3):** מתכנן עונה (COMING), ניהול לקוחות ומלאי (PAID, soil), פתרונות מותאמים (CUSTOM, tomato) — soon status dots.
- **CTA block** at the foot (all three CTAs).

---

## CTA system (`.cta`) — applies to hub, cards, crop pages, market, about
Client priority order, **strictly**:
1. **Complete missing data** — `.cta--data`: **loud**, filled `--gj-leaf-deep`, white text, primary button. The everyday primary ask (the book grows from contributions; there are no end-users yet to sell to).
2. **Suggestion / request** — `.cta--suggest`: quiet, outlined, an **inline FORM** (text input + send). **Never WhatsApp** for this — explicitly a form.
3. **Order something custom for your farm** — `.cta--wa`: soil-tinted, **WhatsApp**. WhatsApp is **reserved for paid/custom farm work only**.

Place a `.cta` block at the foot of each surface; pick the subset that fits (hub/about show all three; cards/crop/market typically show the data CTA).

---

# Interactions & behavior
- **Depth switch** (crop page): toggles Simple/Full/Deep; scroll resets to top. In the prototype the three are separate files; in the app it's one route with a view state.
- **Market view toggle**: table ⇄ cards; **persist the choice** (prototype reads `?view=cards`). Default table.
- **Market disclaimer**: native `<details>` expand/collapse; chevron rotates (`[open]`).
- **Calc compute/back**: `ask` → `result` and back; segmented groups (`.qb-goal`, `.qb-basis`) are single-select (active = `.is-on`); "more" `<select>` swaps the active calculator.
- **Topic sections** (`.topic`): collapsible; chevron rotates.
- **Variety table** (`.vtable`): horizontal scroll inside its rounded frame (`.vtable-wrap`).
- **Season chips** (cards) & **category chips** (market): horizontal scroll, single-select.
- **Reduced motion:** no decorative loops; any entrance animation must degrade to the visible end-state.

# State
- `cropDepth`: `simple | full | deep`.
- `marketView`: `table | cards` (persisted; default `table`).
- `marketCategory`: one of the 11 categories.
- `marketDisclaimerOpen`: bool (default false).
- `calcState`: `ask | result`; `calcGoal` (one of 14); `calcBasis` (area/beds/transplants); `calcAnchor` (target/sow/now); `calcInputs`.
- `calcSession`: ordered list of completed calculations (drives `.qb-session` + export-all).
- `assumptions`: editable set (germination %, safety margin, …) via AssumptionField.
- `seasonFilter` (cards): current-month in-season filter.

---

# Design tokens
**All values come from `tokens.css` — use the variables, do not hard-code.** Key families:
- **Color:** `--gj-paper` / `--gj-paper-2` / `--gj-paper-3` (warm whites), `--gj-ink` / `--gj-ink-soft` (text), `--gj-line` (hairlines). Brand greens: `--gj-leaf`, `--gj-leaf-deep`. Accents: `--gj-sun` (beta/amber), `--gj-soil` / `--gj-soil-deep` (WhatsApp/paid), `--gj-tomato` / `--gj-tomato-deep` (prices/custom), `--gj-code` / `--gj-code-deep` (calculator). Topic colors: `--t-nursery`, `--t-grow`, `--t-harvest`, `--t-yield`. Use `color-mix(in oklch, …)` for tints (as the override CSS does) — don't invent hexes.
- **Type:** `--gj-font-head` (display/headings), body sans, `--gj-font-mono` (micro-labels, Latin/codes). **Type floor (D2):** mono micro ≥ 11px, body-ish ≥ 12px, `.fg dt` 13 / `.fg dd` 14. Hebrew is RTL; Latin/numbers `dir=ltr`.
- **Radii:** `--gj-r-s/m/l`, `--gj-r-pill`.
- **Shadow:** `--gj-shadow-s/m`.
- **Spacing/density (mobile):** `.sh__body` padding 12px; reduced section margins, card gaps, hero/calendar/topic spacing (override CSS `DENSITY` section). The watercolour around-art margins were tightened specifically to reclaim space.

---

# Assets
Bundled in `design_files/assets/` (copies of repo assets — in the app, reference the originals under `public_assets/img/`):
- **Module illustrations (hub):** `assets/modules/module-crop-book.png`, `module-market.png`, `module-calc.png` — the **correct** hand-drawn tool icons (originals: `public_assets/img/modules/`). **Do not** use `heroes/*.webp` for the tool launchers.
- **Crop watercolours:** `assets/crops/wc-<slug>.png` and a few at `assets/wc-<slug>.png` (originals: `public_assets/img/crops/wc-<slug>.png`). ~70 exist; the controller maps unknown crops to a `leaf` fallback (see `CropBookViewController.php`).
- **Font:** `assets/Carmela.ttf` (Hebrew display) — already in the app's font stack.
- **Icons:** simple unicode glyphs / inline SVG logo symbol (`#sfa-logo`) — no icon-font dependency.

---

# Files in this bundle
```
design_handoff_mobile_ui/
├─ README.md                      ← this file (self-sufficient spec)
├─ MOBILE_DESIGN_v4.0.0.md        ← the formal team_35→team_10 spec (changelog + QA checklist §8)
└─ design_files/
   ├─ SFA Mobile Design Board.html   ← SSoT: all 8 surfaces tiled @375 (open first)
   ├─ surface-hub.html               ← §5 Hub
   ├─ surface-cards.html             ← §2 Crop entry cards
   ├─ surface-crop.html              ← §3 Crop page · Simple
   ├─ surface-crop-full.html         ← §3 Crop page · Full
   ├─ surface-crop-deep.html         ← §3 Crop page · Deep
   ├─ surface-market.html            ← §4 Market (table default + cards toggle)
   ├─ surface-calc.html              ← §5 Calculator (ask + result)
   ├─ surface-about.html             ← §6 About
   ├─ tokens.css                     ← design tokens (variable source of truth)
   ├─ cropbook-v1.css                ← crop-book base components
   ├─ classb.css                     ← app-shell / market / calc / tiers base
   ├─ mobile-fixes.css               ← ★ THE OVERRIDE LAYER — load LAST
   └─ assets/                        ← module icons, crop watercolours, font
```

---

# Implementation order (suggested)
1. Wire `mobile-fixes.css` to load **last** behind the three existing sheets.
2. **Density + type floor** (global selectors) — verify desktop holds; flag D1/D2 to team_00.
3. **Calendar key-mapping** (kill raw-key leaks) — server-side label maps for region/activity/season.
4. **Crop cards** row layout + `.cparam` + `.ccard__now` in-season badge (needs current-month calendar lookup).
5. **Crop hero** stacked layout (kill overlap) + **depth states** (Simple/Full/Deep content rules).
6. **Market** table-default + collapsible `<details>` disclaimer + real category chips (incl. `baskets`) + **`.t-price` stacked RTL number/unit**.
7. **Calculator** goal grid (6 + dropdown of 8) + flexible basis/anchor + **session accumulation + export-all** + **AssumptionField** entry point.
8. **About** content-first + tiers-as-expansion.
9. **CTAs** on every surface (data=loud, suggestion=form, WhatsApp=custom-only).
10. Hand to **team_50** for the 375 visual pass (QA checklist in `MOBILE_DESIGN_v4.0.0.md` §8).

# Open items (team_00 / data owners)
1. **Ratify D1 (market table-default) + D2 (type floor)** against the "desktop locked" rule.
2. Calculator **session persistence scope** (per-device vs. account).
3. `goal → CALC[kind]` and `basis → operand` mapping — confirm with the `calculators.py` owner.
4. **AssumptionField editor** — confirm all entry points (calc result, crop calculators, anywhere an assumption feeds a number).
5. Calendar `peak`-month source rule; region-overlay selector (reserved).

— team_35 · WP-CB-MOBILE v4.0.0 · 2026-06-05
