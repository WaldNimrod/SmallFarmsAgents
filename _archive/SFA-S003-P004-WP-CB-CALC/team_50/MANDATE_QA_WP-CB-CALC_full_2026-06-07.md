---
id: SFA-S003-P004-WP-CB-CALC-QA-FULL
mandate_from: team_100 (Chief Architect — builder engine: Claude Opus)
mandate_to: team_50 (visual / functional QA — cross-engine, non-Claude per IR#1/#5)
re: FULL QA of the calculator — all 14/15 goals live (supersedes the B-now mandate)
supersedes: SFA-S003-P004-WP-CB-CALC-QA-BNOW (2026-06-07)
branch: claude/cb-calc-ui-2026-06-07 (pushed @ a3adfe5; not merged)
created: 2026-06-07
status: OPEN — team_50 action requested before merge-to-main + deploy
---

# MANDATE — team_50 FULL QA: WP-CB-CALC (14/15 live)

Supersedes the B-now mandate. All input-bearing goals are now wired; **14 of 15 goals are LIVE** (only water #0 is deferred to WP-CB-WATER). Builder = Claude (Opus); the verdict must be a **non-Claude** engine (IR#1/IR#5).

## 1. Scope — `/calc/`, all live goals
- **Re-verify the prior B-now pass** still holds (15-goal grid, "15 מטרות", #13 "השוואת גידולים", sow_date #4, harvest #5, honest states, no console errors).
- **F-01 (was the blocker) — re-verify FIXED:** #9 הכנסה now leads with **yield (ק״ג)** as the headline; **₪ is a secondary "שווי משוער · מדד השוק · להמחשה" line** (not the primary).
- **5 newly-live goals (primary focus):**
  | # | goal | check |
  |---|------|-------|
  | 6 | רצף גידולים | enter a sow date + "מספר מחזורים" → a LIST of N sowing dates (interval = round(harvest_window/7)) |
  | 14 | עלות זרעים | enter ₪/gram OR pack-price+grams/pack → ₪ cost (+ grams/packs secondary); no price → honest "הזינו מחיר" |
  | 11 | חלון קרה | pick a region → planting window (range); a **frost_free** region → honest "חלון פתוח" note (no fake date) |
  | 3 | ימי משתלה | enter "תאריך השתלה לשדה" (+ seedlings basis) → trays + tray-sow date |
  | 13 | השוואת גידולים | **basket**: add 2–6 crops (chips + ✕) → ranked list by **ק״ג/מ׳** (quantity-first), ₪/מ׳ secondary; single-crop select hidden in this mode |

## 2. Acceptance
1. Each live goal computes for an enriched crop; **honest state** (no fabricated number) when data/inputs absent.
2. **Quantity-first integrity** across #9 and #13 (₪ always secondary/illustrative).
3. Date math correct (already parity-verified vs `calculators.py`: sow/harvest/succession/frost/nursery).
4. Basket add/remove works; region picker populated from `frost_regions.json` (default coastal).
5. Session accumulates each shape; export still works; assumptions editor opens.
6. No JS console errors on load / goal switching / input changes. `qa_probe.mjs` PASS (no overflow/forbidden text).
7. 224/224 PHPUnit; validate_aos 0 FAIL (builder-side, already green).

## 3. ⚠ Scope caveats (unchanged)
- **Function over final styling.** The new result shapes render as **plain formatted text** — `mock.css` (`.r-date/.r-range/.r-list/.r-rank`) is NOT in production yet; the styled cards land with the UI-redesign CSS pass. **QA function; F-02 (nodata copy) + F-03 (plain render) are known-deferred — not new defects.**
- **water #0** intentionally shows "בפיתוח / מודל נפרד" — not a defect.

## 4. Build target & verdict
Branch `claude/cb-calc-ui-2026-06-07` (pushed, not deployed). QA locally against an enriched dev DB (lettuce/tomato + a bare crop + a `both`/transplant crop for nursery/sow transplant path), CDP harness + `qa_probe.mjs`. Return a non-Claude L-GATE QA verdict via `_COMMUNICATION/team_100/`. **On PASS → team_100 + team_00 merge to main + deploy** (F-02/F-03 ride the redesign CSS).
