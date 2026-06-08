---
id: SFA-S003-P004-WP-CB-CALC-MOCKUP-RETURN
return_from: team_35 (design/mockups — UI-redesign session)
return_to: team_100 (Chief Architect — calculator engine session)
re: WP-CB-CALC calculator — mockups + goal→shape mapping + UI-driven server flags
in_reply_to: SFA-S003-P004-WP-CB-CALC-MANDATE-MOCKUPS (2026-06-07)
gate: L-GATE_D (design input for the LOD400 presentation layer)
status: DELIVERED — mockups complete; awaiting engine-team integration
author: team_35
created: 2026-06-07
mockups:
  - _COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/calc.html       # builder + 5 result shapes + no-data + region picker
  - _COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/cropdata_entry.html  # §5 guided-entry tool
  - _COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/assumptions.html     # assumptions editor (already delivered)
  - _COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/mock.css             # shared shell + LOCKED design tokens
---

# RETURN — Calculator (WP-CB-CALC) mockups + mapping + UI-driven flags

**To:** team_100 (calc engine) · **From:** team_35 (design) · **Date:** 2026-06-07

> ## ⚠ ACTION REQUIRED — team_100 (calc engine), before the LOD400 presentation layer locks
> **A. Answer the 4 design-blocking questions (full detail in §5):**
> 1. **Frost region list** — send the canonical Israel region set for the picker (mockup uses placeholders); default region?
> 2. **`compare` (#13) scope** — rank **all crops** (as mocked) or a user-picked shortlist/basket? *(team_00 flagged this as a product call — may come from Nimrod.)*
> 3. **`nursery` (#3) anchor** — dedicated "תאריך השתלה לשדה" input (as mocked) or reuse "תאריך יעד"?
> 4. **`seed_cost` (#14)** — its own goal flow (as mocked) or a sub-line on the `seed` (#1) result?
>
> **B. Fold the 6 UI-driven server/data flags (§3) into the spec** — incl. the live-builder relabel ("רווח גולמי"→"השוואת גידולים", "14"→"15 מטרות", add #5) and the frost-region JSON asset.
>
> Reply via `_COMMUNICATION/team_35/` (or through Nimrod, per your LOD_DESIGN §6 cross-session coordination). team_35 will iterate the mockups on your answers.

Mockups are standalone HTML on the **LOCKED design tokens** (`tokens.css` → `mock.css`), RTL, mobile-first, and consistent with the parallel UI-redesign (same shell/container, real watercolor illustrations, the universal "closed = key, open = depth" drill-down, and the two-level ⓘ knowledge model). They drop into the LOD400 presentation layer.

All §1 product framing honored: **quantity is the hero metric; ₪ is a smaller secondary line; no fabricated numbers (honest no-data state); RTL mobile-first; existing tokens.**

---

## 1. What's in the mockups (per §6.1)

**`calc.html` — the calculator** (interactive: click any goal, the result + inputs change):
- **ASK builder, 4 steps:** (1) 15-goal grid with **honest availability badges** (זמין / בקרוב / — מודל נפרד); (2) crop select (+ "all crops" mode for #13); (3) basis chips + number + **goal-specific inputs** (יעד יבול, seed-cost price pair, succession count/season-end); (4) **time anchor — now LIVE** (the chip + date input drive date goals; greys out for non-date goals) + the **frost region picker** (appears only for #11).
- **RESULT** that renders the correct **shape per goal** + **session** (accumulates, per-device) + **export** (PDF/CSV) + assumptions link.
- **A reference gallery of all 5 result shapes + the no-data state**, each tagged with the goals that use it — this is the visual spec for your render layer.

**`cropdata_entry.html` — the §5 guided-entry tool** (internal/owner-only): one crop at a time, **keyboard-driven (1–5 + Enter)**, progress bar (33/70), `planting_method` (incl. the new **"גם וגם"** value) + `frost_tolerance_class`, conditional `days_in_nursery` (shows only for שתיל/גם-וגם), classification queue. Lower polish by design.

---

## 2. Mapping doc (per §6.2) — 15 goals → result shape + inputs

| # | key | goal (he) | result SHAPE | inputs beyond {crop, basis} | anchor | phase |
|---|-----|-----------|--------------|------------------------------|--------|-------|
| 1 | seed | זרעים לקנות | **scalar** (גרם) | — | — | live |
| 8 | yield | יבול צפוי | **scalar** (ק״ג) | — | — | live |
| 9 | revenue | הכנסה צפויה | **scalar + ₪ secondary** | — | — | live |
| 10 | pop | צפיפות שתילה | **scalar + grid** (צמ׳/מ״ר) | — | — | live |
| 12 | fert | כמות דישון | **scalar** (ק״ג קומפוסט) | — | — | live |
| 7 | beds | ערוגות ליעד | **scalar** (ערוגות) | **יעד יבול** (ק״ג) | — | live |
| 2 | transplants | כמות שתילים | **scalar** (שתילים) | — | — | A |
| 14 | seed_cost | עלות זרעים | **scalar + ₪** | **₪/גרם** OR **pack ₪ + גרם/חבילה** | — | A |
| 13 | compare | השוואת גידולים | **RANKED LIST** (ק״ג/מ׳ primary, ₪/מ׳ secondary) | **none — iterates ALL crops** (crop step → "all") | — | A |
| 5 | harvest | חלון קטיף | **DATE RANGE** | — | sow | B-now |
| 6 | succession | רצף גידולים | **DATE LIST** | **# successions** OR **season-end date** (interval is derived, not asked) | sow | B-now |
| 4 | sow_date | תאריך זריעה | **DATE** | — | target | B-now |
| 3 | nursery | ימי משתלה | **scalar + DATE** (מגשים + tray-sow date) | **field-set date**; plants chained from #2 | field-set | B-later |
| 11 | frost | חלון קרה | **DATE RANGE** | **region picker** (no free-text dates) | region | B-later |
| 0 | water | צריכת מים | **— (no-data / בפיתוח)** | — | — | deferred (WP-CB-WATER) |

**5 shapes to build in the render layer:** `scalar` (+ secondary ₪ variant, + grid variant), `DATE`, `DATE RANGE`, `DATE LIST`, `RANKED LIST`, `scalar+DATE`. The mockup gallery shows each.

**Session-row string per shape** (the scalar-only `pushSession` assumption you flagged at `crop-book-v1.js:719-760` must generalize):
- scalar → `"כמות שתילים · עגבנייה → ~97 שתילים"`
- DATE → `"תאריך זריעה · עגבנייה → 16/06/2026"`
- DATE RANGE → `"חלון קרה · עגבנייה → 15/03–15/11"`
- DATE LIST → `"רצף · עגבנייה → 5 זריעות מ-16/06"`
- RANKED LIST → `"השוואה · 8 גידולים → עגבנייה #1"`

---

## 3. UI-driven flags that imply SERVER / data changes (per §6.3)

These are **logged, not assumed** — fold into the LOD400 as you see fit. Most confirm gaps you already found in the LOD_DESIGN §3:

1. **Categorical delivery channel (confirms §3.2).** The region picker and the no-data state both depend on `planting_method` + `frost_tolerance_class` reaching the client as **text**, surviving the `parseFloat` flatten. The UI needs a `window.SFA_CROP_BOOK_TXT[slug]` (or equivalent) — please confirm the channel name so the mockup→engine wiring is exact.
2. **Date book-fields whitelist (confirms §3.1).** `days_to_maturity`, `days_in_nursery`, `harvest_window_max_days` must reach the client for the DATE/RANGE/LIST shapes. (succession interval = derived `round(harvest_window_max_days/7)` — no new field.)
3. **Frost region table = a static asset the UI loads.** The region picker needs `region → {last_spring_frost, first_autumn_frost}`. Please expose it as a JSON asset (e.g. `/public_assets/data/frost_regions.json`) with the region list **frozen** so the picker's `<option>`s match the engine keys. **Region list is currently placeholder in the mockup — send the canonical list.**
4. **`compare` (#13) breaks the single-crop request.** The result iterates all crops → the client needs the full `avg_yield_per_bed_m` (+ `price_documented`) map for every crop in one payload (already whitelisted per §4.1, but confirm it ships for the **list**, not just the selected crop).
5. **`TRAY_CELLS` (128) + `HARDINESS_OFFSET` must reach JS** (confirms §2.4/§4 B0.3) — the `scalar+DATE` nursery card and the frost offset both display values derived from them; surface in `window.SFA_ASSUMPTIONS`.
6. **Goal relabel:** the live builder still says **"רווח גולמי" (#13)** and **"14 מחשבונים"** (`calc_dash.php:69,115`). Per decision #2 + #4 → rename to **"השוואת גידולים"** and **"15 מטרות"**, add the **`harvest` (#5)** goal entry. (Design uses these labels already.)

No other UI need implies a server change. Everything else (seed-cost inputs, succession count, the assumptions editor, export, session) is client-side.

---

## 4. Design guidance / notes for the build

- **Reuse `mock.css` tokens verbatim** — do not re-pick colors/spacing; it mirrors the LOCKED `tokens.css`. The calculator must look identical to the rest of the redesigned app (same header/shell/footer, `--gj-*`).
- **Honest availability is a first-class UI state**, not an afterthought: every goal button carries its phase badge; a goal enabled for some crops but not the selected one shows the **no-data card** (gallery, last cell). Never a 0 or a guess.
- **Quantity-first everywhere:** in #9 and #13 the ₪ figure is visually smaller and explicitly labeled "להמחשה / לפי מדד השוק". Keep it subordinate.
- **The anchor is the date-engine's input surface** — the mockup greys it when the goal is non-date and relabels it ("חי — מזין מטרה זו" / "לא רלוונטי"). Wire `state.anchor` + date input + (new) date book-fields exactly as the LOD_DESIGN §B0.4 describes.
- **`succession` interval is computed, not asked** — the only user input is # cycles or a season-end date (per decision #5). Mockup reflects this.
- **Guided-entry tool is internal** — keep it behind owner auth; speed > polish; the "גם וגם" value must be a real canonical `planting_method` enum (decision #7).

---

## 5. Open questions back to the engine team

1. **Frost region list** — send the canonical regions (and whether the picker should default to a "general / coastal" region).
2. **`compare` scope** — rank ALL crops, or a shortlist (e.g. top-N / a user-picked basket)? The mockup shows all; confirm.
3. **#3 nursery anchor** — is a dedicated **"תאריך השתלה לשדה"** (field-set) input the right 4th-step extension, or should it reuse "תאריך יעד"? Mockup assumes a dedicated field-set date.
4. **seed_cost (#14)** — its own goal flow (as mocked) or a sub-line on the `seed` (#1) result? Mockup treats it as its own goal with a price-input pair.

Route any reply via `_COMMUNICATION/team_35/` or ping through Nimrod. team_35 can iterate the mockups on your answers before the LOD400 locks.
