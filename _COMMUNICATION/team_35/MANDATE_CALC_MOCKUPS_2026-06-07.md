---
id: SFA-S003-P004-WP-CB-CALC-MANDATE-MOCKUPS
mandate_from: team_100 (Chief Architect)
mandate_to: team_35 (design / mockups) — UI-redesign effort
re: WP-CB-CALC calculator — mockups + spec integration
gate: L-GATE_D (design input feeding the LOD400 presentation layer)
status: OPEN — team_35 action required (team_100 is waiting on these mockups to complete the אפיון)
author: team_100
created: 2026-06-07
related:
  - _COMMUNICATION/team_100/SFA-S003-P004-WP-CB-CALC/LOD_DESIGN_2026-06-07_v1.0.0.md
  - _aos/work_packages/S003/SFA-S003-P004-WP-CB-CALC/LOD400_spec.md
  - sfa_delivery/templates/pages/calc_dash.php (current builder)
  - sfa_delivery/public_assets/js/crop-book-v1.js (current engine)
---

# MANDATE — Calculator (WP-CB-CALC) mockups + spec integration

**To:** team_35 (design/mockups), coordinating with the parallel UI-redesign (team_100 UI session)
**From:** team_100 · **Date:** 2026-06-07

> **Boundary (per team_00):** the calculator's **engine, data, derivations, server plumbing, and parity tests are owned by team_100** and fully specced in the LOD400. The **visual + interaction design of the calculator is owned by team_35** (this mandate). team_100 is **waiting on your mockups** to complete the presentation layer of the אפיון. This mandate gives you everything you need so the mockups are functionally complete and drop straight into the LOD400.

---

## 1. Product framing — LOCKED (team_00, 2026-06-07). Read first.
1. **The hero metric is QUANTITY (yield/כמות), not money.** The calculator is a *planning* tool, not a financial projection.
2. **Price/value is SECONDARY and illustrative** ("gimmick" from our own price-list). Never the headline; always a smaller, secondary line.
3. **No fabricated numbers.** A goal with no data for the chosen crop must show an honest "no data / coming" state — never a made-up result.
4. RTL Hebrew, **mobile-first** (this surface shipped under WP-CB-MOBILE). Reuse the existing design tokens (`--gj-*` in the current CSS).

## 2. The flow to design (current builder, evolved)
The current builder (`calc_dash.php`) is a single scope with two states — **ASK** (question builder) → **RESULT** (answer + session + export). Keep that spine; redesign the look/interaction. The ASK builder has 4 steps:
1. **מה לחשב** — goal picker (6 primary buttons + a "עוד… (8)" dropdown). **Now 15 goals** (see §3).
2. **עבור איזה גידול** — crop `<select>`.
3. **לפי מה** — basis chips (שטח / מס׳ ערוגות / מס׳ שתילים) + a basis number input; some goals force a "יעד יבול" input.
4. **עוגן זמן** — date anchor (תאריך יעד / תאריך זריעה / עכשיו). **This step becomes LIVE** (today it's inert) — it drives the date calculators.
→ **«חשב»** → RESULT: big answer + breakdown rows + **session** (accumulates every calc, per-device) + **export** (PDF/CSV of the whole session) + an **assumptions editor** (נביטה/ביטחון…).

**New interaction needs your design must add:**
- A **region picker** (Step 4) for the frost calculator — user selects an Israeli region → frost dates (no free-text dates).
- A few **goal-specific inputs**: succession (number of cycles **or** season-end date); seed-cost (price/gram **or** pack price + grams/pack); nursery (field-set date).

## 3. The 15 goals — final list, result TYPE, and what each shows
The **result TYPE** is the critical design driver — today every result is a single scalar; **5 new result shapes** need design:

| # | Goal (he) | Result TYPE | Shows (primary → secondary) | Phase |
|---|---|---|---|---|
| 1 | זרעים לקנות | scalar | גרם (+ זרעים · צמחים) | live |
| 8 | יבול צפוי | scalar | ק״ג | live |
| 9 | הכנסה צפויה | scalar | ₪ (secondary line) | live |
| 10 | צפיפות שתילה | scalar + grid | צמ׳/מ״ר (+ visual grid) | live |
| 12 | כמות דישון | scalar | ק״ג קומפוסט | live |
| 7 | ערוגות ליעד | scalar | ערוגות | live |
| 2 | כמות שתילים | scalar | שתילים | Phase A |
| 14 | עלות זרעים | scalar | ₪ (+ packs) — **needs price inputs** | Phase A |
| 13 | **השוואת גידולים** (ex-"רווח") | **RANKED LIST** | crops ranked by **כמות (יבול/מ׳)**; **₪/מ׳ as a secondary line** | Phase A |
| 5 | חלון קטיף | **DATE RANGE** | start → end dates | Phase B-now |
| 6 | רצף גידולים | **DATE LIST** | N sowing dates (a schedule) | Phase B-now |
| 4 | תאריך זריעה | **DATE** | one date (dd/mm/yyyy) | Phase B-now |
| 3 | ימי משתלה | scalar + **DATE** | trays (מגשים) + tray-sow date | Phase B-later |
| 11 | חלון קרה | **DATE RANGE** | earliest → latest safe planting | Phase B-later |
| 0 | צריכת מים | — **DEFERRED** | keep the "בפיתוח" honest state | deferred |

> #13 is a **comparison**, not "profit" — no "רווח"/"margin" wording. Lead with quantity; show ₪/מ׳ small. It is the only **multi-crop** goal (ranks across crops, not one selected crop) — design how the crop step adapts (e.g. "all crops" / a shortlist).

### Design these 5 result shapes (the heart of the ask):
- **DATE** (#4): one prominent date, Hebrew dd/mm/yyyy, with the anchor it was computed from.
- **DATE RANGE** (#5, #11): two dates as a window/bar (e.g. "מ-… עד-…"), ideally a small timeline.
- **DATE LIST** (#6): a schedule of N sowing dates (list or calendar strip).
- **RANKED LIST** (#13): a ranked table of crops — quantity primary, ₪ secondary, clear #1.
- **scalar+date** (#3): a count (trays) plus a date.

## 4. Honest data-state design (important)
Coverage is uneven across crops (we measured it). Mockups must include the **"this crop has no data for this goal"** state — a clean, honest empty/disabled state (like the existing "מחשבון זה בפיתוח" card), NOT a zero or a guess. Goals roll out in waves (live → Phase A → B-now → B-later); design must gracefully show a goal that's enabled for some crops and not others.

## 5. Secondary surface — the guided-entry tool (WP-CB-CROPDATA-DATES)
A **separate, internal (owner-only) UI** — a per-crop **question-sequence** for Nimrod to classify crops fast:
- `planting_method`: זריעה ישירה / שתיל / **גם וגם** / פקעת / ייחור (note the new "גם וגם" value).
- `frost_tolerance_class`: a pick from a small set (very_hardy … very_tender).
- (conditionally) `days_in_nursery` for transplant/both crops.
Design priority: **speed of data entry** (one crop at a time, keyboard-friendly, progress indicator). Lower visual polish than the public calculator. Mock it, but it's secondary to §3.

## 6. What to return to team_100 (so it integrates into the LOD400)
1. Mockups (the surface-calc design files, your usual format) for: the ASK builder (4 steps incl. region picker + the goal-specific inputs), the RESULT state, and **each of the 5 result shapes in §3**, plus the honest no-data state (§4), and the guided-entry tool (§5).
2. A short **mapping doc**: each of the 15 goals → which result shape + which inputs it needs. This is what lets us wire mockups to the engine in the LOD400.
3. Flag any UI need that implies a **server-side change** → log it (do not assume it); team_100 folds it into the spec.

## 7. Reference (engine truth — for accurate mockups)
- Goals/labels/units: `calc_dash.php:57-74` (`$CALC_GOALS`).
- Engine + result wiring: `crop-book-v1.js` (`CALC` L31-129; `wireQuestionBuilder` L552+; `runEngine` L624-662; result render L719-760; session L695-717).
- Product + data decisions + result-type rationale: the LOD_DESIGN (linked in frontmatter) §0, §3, §4, Phase A/B.

**team_100 awaits your mockups + mapping doc to lock the LOD400 presentation layer.** Route the return via `_COMMUNICATION/team_100/` (canonical artifact, IR#6).
