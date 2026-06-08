---
id: SFA-S003-P004-WP-CB-CALC-QA-BNOW
mandate_from: team_100 (Chief Architect — builder engine: Claude Opus)
mandate_to: team_50 (visual / functional QA — cross-engine, non-Claude per IR#1/#5)
re: visual + functional QA of the live calculator (Phase A + B-now date goals)
branch: claude/cb-calc-ui-2026-06-07 (pushed; not merged to main)
created: 2026-06-07
status: OPEN — team_50 action requested (L-GATE_D deferred this QA to "after typed showResult + B-now wiring land" — it has landed)
---

# MANDATE — team_50 QA: WP-CB-CALC (Phase A + B-now)

The L-GATE_D verdict (PASS_WITH_FINDINGS) explicitly deferred full visual QA "until typed `showResult` + B-now goal wiring land." **They have landed** (branch `claude/cb-calc-ui-2026-06-07`). Builder = Claude (Opus); per IR#1/IR#5 the **visual/functional verdict must be a non-Claude engine** — that's you.

## 1. What to QA — `/calc/` ("מחשבון התכנון")
**9 of 15 goals are now LIVE** (the rest show honest "בקרוב"):
- **7 scalar (regression):** זרעים(#1) · יבול(#8) · הכנסה(#9) · צפיפות(#10) · דישון(#12) · ערוגות(#7) · **שתילים(#2, new Phase A)**.
- **2 date goals (NEW B-now — primary focus):** **תאריך זריעה(#4 → a single date)** · **חלון קטיף(#5 → a date range)**, the surfaced 15th goal.

## 2. Acceptance checks
1. **Page loads, 15-goal grid** renders; header reads **"15 מטרות"**; #13 reads **"השוואת גידולים"** (NOT "רווח גולמי").
2. **Date goals compute** for a crop with date data (use an enriched crop — e.g. lettuce/tomato): pick תאריך-זריעה → a date appears (dd/mm/yyyy, LTR) derived from the תאריך-יעד anchor − days-to-maturity; pick חלון-קטיף → a start–end range from the תאריך-זריעה anchor. Anchor dates are pre-filled by default.
3. **Honest states (no fabricated numbers):** a crop WITHOUT date data → date goal shows the honest "אין נתון לגידול זה" message (not a 0/guess); a goal not yet built → "בפיתוח".
4. **Quantity-first integrity:** #9 revenue shows ₪ as a SECONDARY line.
5. **Session + export** still accumulate/work; assumptions editor opens.
6. No JS console errors on load or on goal switching.

## 3. ⚠ Scope caveats (so you QA the right thing)
- **Function over final polish.** The date result shapes use the team_35 mockup class names, but `mock.css` is NOT in production yet — so date/range results currently render as **plain formatted text** (functional, not yet the styled `.r-date`/`.r-range` cards). **QA the FUNCTION** (correct dates, honest states, no crashes); the visual restyle lands with the UI-redesign CSS in a later slice. Flag function bugs, not the known-pending styling.
- **6 goals intentionally still "בקרוב"** (seed_cost/succession/compare/frost/nursery need new inputs — next slices; water is deferred to WP-CB-WATER). Not defects.
- **Date math is already parity-verified** against the real `calculators.py` (sow 16/06/2026; harvest 15/09→27/10) — your job is the in-browser integration, not the math.

## 4. Build target
Branch `claude/cb-calc-ui-2026-06-07` is pushed but **not deployed**. To QA in-browser, either: (a) run locally against an enriched dev DB, or (b) request a staging deploy of the branch via team_00/team_99 (deploy is auth-gated). Use the dependency-free CDP runner (`_aos/lean-kit/.../qa/qa_probe.mjs`) per the browser-QA canon — **curl alone won't catch render bugs.**

## 5. Verdict
Return a non-Claude L-GATE QA verdict (PASS / PASS_WITH_FINDINGS / CHANGES) via `_COMMUNICATION/team_100/`. On PASS → team_100 proceeds to the remaining input-bearing goals + (with team_00) merge to main + deploy.
