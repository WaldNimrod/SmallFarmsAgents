# MOBILE DESIGN — SFA interface (375px) · v4

> **WP:** SFA-S003-P004-WP-CB-MOBILE · **From:** team_35 → **team_10** · **Date:** 2026-06-05 · **Version:** v4.0.0
> **Design SSoT:** `mobile_design_classb/SFA Mobile Design Board.html` (10 frames @375) · **CSS:** `mobile_design_classb/mobile-fixes.css` (v4) · **Verify:** team_50 @375 (§8)

## Changelog v3 → v4 (client review #3)
1. **Hub illustrations — corrected to the real ones.** Main tools use `public_assets/img/modules/module-{crop-book,market,calc}.png` (the hand-drawn module icons), **not** the `heroes/*.webp` washes. Coming tiles are icon-only (no placeholder art).
2. **Crop card** — illustration is a **small thumbnail** again (the faint-background wash was dropped — client found it not nice); the real space-saving comes from **tighter margins everywhere** (global density pass).
3. **In-season now** — crop list shows a clear **«עכשיו לזריעה / לשתילה»** badge (`.ccard__now`) + an "in-season" filter chip, so what to plant this month reads at a glance.
4. **CTAs on every surface** (`.cta`), in priority order: **(1) complete missing data** — primary, loud, filled leaf; **(2) suggestion/request — a FORM** (never WhatsApp), quiet; **(3) custom-for-your-farm — WhatsApp** (soil). No users yet → the everyday ask is contribute-data + suggest-form; WhatsApp is reserved for paid/custom work.
5. **Market** — disclaimer is now a **collapsible** title (`<details class="mkt-disc">`, closed by default); category chips are the **real product categories** (incl. **סלים**/baskets — 11 chips); the price column is **RTL-fixed** (number stacked over unit, `dir:ltr` isolate) so digits/units no longer reorder.
6. **Crop depths rebalanced:** **Simple** = minimal gardener view (essentials chips · planting calendar · one key value per topic — no full stat block); **Full** = topic overview **+ every field** (17) by topic; **Deep** = same structure as Full but each datum opens its **range across varieties + sources** (+ variety table).
7. **Calculator:** goal step = **6 main buttons + a dropdown** for the other 8 (14 total); the **session saves every calculation** (accumulated list) and **export = the whole session**; the **base assumptions are editable** from the result (entry point into the AssumptionField editor).
8. **Typography floor** (from v3) retained — desktop too.

---

## Components & rules
- Overrides `@media (max-width:480px)`; layout-agnostic new components: `.pcal`, `.cparam`, `.qb`, `.cta`, `.mkt-table`. `mobile-fixes.css` loads last, extends the three base stylesheets. No new palette.
- **Sanctioned desktop changes** (client-requested, flag for team_00): market **table-default**, **type-minimum floor**. Everything else desktop = 0 diff.

### Assets (copy from the repo, do not invent)
- Module icons: `public_assets/img/modules/module-crop-book.png`, `module-market.png`, `module-calc.png`.
- Crop watercolours: `public_assets/img/crops/wc-<slug>.png`. Calendar/region maps unchanged (§ below).

### CTA system `.cta`
`.cta--data` (primary, filled leaf — "complete missing data") · `.cta--suggest` (outlined, **inline form**, no WhatsApp) · `.cta--wa` (soil, WhatsApp — **custom-for-farm only**). Place a `.cta` block at the foot of hub, cards, crop pages, market, about.

### Icon language `.cparam` (unchanged) + `.ccard__now`
`.ccard__now` = in-season badge on the list: `🌱 עכשיו לזריעה` / `🪴 עכשיו לשתילה`, derived from `CropPlantingCalendar` for the current month + `activity_type`.

---

## FIX 1 · Crop cards
- Single column, compact **row** card: small thumb (66px / 88px featured), text-led, tight padding. **No background wash.**
- Body: name → English → `.ccard__now` (if in season) → `.cparams`. Featured first card adds `.ccard__feattag` + one-line `.ccard__desc`.
- A `.cta--data` foot invites completing partial crops.

## FIX 2 · Crop page — three depths (clear progression)
Header depth control `.sh__depths` (icons; active shows label). Calendar `.pcal` Hebrew maps (drive off `CropPlantingCalendar`, mig.049): `IL_general→כל הארץ · IL_north→צפון · IL_center→מרכז · IL_south→דרום · MED_general→אגן הים התיכון`; `seed→זריעה · transplant→שתילה · both→both`; `spring/summer/fall/winter/all→אביב/קיץ/סתיו/חורף/כל השנה`. **No raw keys in visible text.**
- **Simple** (gardener): essentials `.cparam` strip (spacing · DTM · water · method) → calendar → `.keylist` (one key value per topic). Nothing else.
- **Full**: `.tsum` overview **+** all 17 fields in `.topic`/`.fieldgrid` sections (single-column fields on mobile).
- **Deep**: same topic structure as Full, but each `.fg dd` carries a `.rng` (range across varieties) + an EX/PR/WR `.srcpill` row; plus the `.vtable` variety comparison. "Like Full, every datum opened."

## FIX 3 · Market
- **Collapsible disclaimer** `<details class="mkt-disc">` (title row + chevron; mandatory content still always present, just collapsed by default).
- **Real category chips:** הכל · עלים · פירות-ירק · שורש · מצליבים · בצליים · דלועיים · קטניות · **סלים** · פירות · ביצים (maps to `products.category` incl. `baskets`).
- **Default = table** (also desktop), cards via toggle.
- **RTL price fix:** `.t-price` is a column — `<span class="n" dir=ltr>12.40</span>` over `<small>₪ / ק״ג</small>`. Digits never reorder against the Hebrew unit.

## FIX 4 · About
- **Content first:** `.about-intro` (what SFA is) + `.about-points` (ידע פתוח · מחירי שוק · כלי תכנון · נבנה בשיתוף). The 5-tier ladder moves **below** as a secondary expansion (`.about-tiers-h` + the two `.tier-group`s). `.cta` block at the foot.

## FIX 5 · Hub
- `.modtile--row` launchers with the **correct module-*.png** (`object-fit:contain`, warm panel). Open tools (leaf/tomato/sun) above `.is-soon` icon-only coming tiles. `.cta` block at the foot.

## FIX 6 · Calculator — "define the question" + session
- **Goal step:** `.qb-goal--grid` of **6 primary** buttons (זרעים לקנות · תאריך זריעה · יבול צפוי · הכנסה צפויה · כמות שתילים · צפיפות) + `.qb-more` **select** for the remaining 8 (14 total → map to `CALC[kind]`).
- **Flexible basis/anchor:** `.qb-basis` (שטח / ערוגות / שתילים) and (תאריך יעד / תאריך זריעה / עכשיו) — not always area+target-date.
- **Result state:** `.qb-session` accumulates every calculation in the session (saved), current row highlighted; `.qb-answer` + `.qb-break` for the current; **`.qb-assum`** = editable base-assumptions entry (✎ ערוך הנחות → AssumptionField); **export = whole session** (PDF/CSV).
- **Assumptions editing entry points:** calc result (here) is the primary; also expose on the crop page's calculators and anywhere an assumption feeds a number (team_10 to wire the shared AssumptionField editor).

---

## 7 · Density (global mobile)
`.sh__body` 12px; reduced section margins, card gaps, hero/calendar/topic spacing — "don't take valuable space."

## 8 · QA checklist — team_50 @375
1. No clipping; tight margins throughout.
2. Hub shows **module-*.png** illustrations; coming tiles icon-only; CTA block present (data / form / WhatsApp).
3. Crop cards: small thumbnail (no wash); in-season badge on this-month crops; CTA foot.
4. Depths: **Simple is genuinely minimal** (essentials + calendar + one-key-per-topic); **Full has all fields + overview**; **Deep = Full + per-datum ranges/varieties/sources**.
5. Market: disclaimer collapsed→expands; 11 real categories incl. **סלים**; **price reads correctly RTL** (number then unit, no reorder); table default + cards toggle.
6. Calculator: 6 buttons + dropdown (14); session list accumulates + export-all; assumptions editable from result.
7. About: content first, tiers below; CTAs.
8. CTAs: suggestion path is a **form, not WhatsApp**; WhatsApp only on custom-for-farm. Type floor honored (desktop too).

## 9 · Open items (team_00 / data)
1. Two sanctioned desktop changes (market table-default, type floor) — ratify.
2. `peak` calendar source rule; region-overlay selector (reserved).
3. Calculator goal→`CALC[kind]` + basis→operand mapping — confirm with calculators.py owner; session persistence scope (per-device vs account).
4. AssumptionField editor — confirm all entry points (calc result, crop calculators, others).

```
— team_35 · WP-CB-MOBILE v4.0.0 · extends WP-CB-UI-CLASSB · 2026-06-05
```
