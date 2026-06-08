---
id: SFA-S003-P004-WP-CB-CALC-MOCKUP-ITERATION
from: team_35 (design)
to: team_100 (calc engine)
re: iteration on FROST_REGIONS_AND_SPEC_LOCK — #13 basket + region picker wired
in_reply_to: SFA-S003-P004-WP-CB-CALC-FROST-REGIONS
created: 2026-06-07
status: DONE — both residuals addressed; one team_00 approval outstanding (frost dates)
---

# ITERATION — #13 basket + region picker (reply to your spec-lock)

**To:** team_100 (calc engine) · **From:** team_35 · **Date:** 2026-06-07

Both items from your `FROST_REGIONS_AND_SPEC_LOCK` are done in `calc.html` (verified rendered):

## 1. #13 `compare` → SELECTED-CROP BASKET (your residual)
- Step-2 now switches to a **multi-select basket** when `compare` is chosen: copy **"בחרו גידולים להשוואה (2–6)"**, crop **chips with ✕ remove** + a **"+ הוסף גידול"** control. The single crop `<select>` is hidden in this mode.
- Result ranks **only the basket** — `RANKED LIST · סל נבחר · כמות מובילה`; ₪/מ׳ stays the secondary column.
- Echo + session string updated → "סל של N גידולים". The "all crops" version is removed.
- **Engine note:** payload for #13 now needs `avg_yield_per_bed_m` + `price_documented` for **the basket crops only** (2–6), not the full book — lighter than the earlier "all crops" assumption.

## 2. Region picker → wired to your frozen keys
- Picker options use your canonical keys/labels: `coastal`⭐(default) · `judean_hills` · `jordan_valley` · `northern_negev` · `upper_galilee`.
- Copy references `frost_regions.json`; **frost_free region → honest "open window"** message (no fake date), per your note.
- `<option value>` = the frozen key; the picker shows `label_he`. Ready to read your `frost_regions.json` as-is (`default` + `regions[]`, `DD-MM` dates).

## 3. Outstanding — team_00 only
Your frost **dates are DRAFT pending team_00 approval**. That gates the live `frost_regions.json` ship (frost #11 is B-later, non-blocking for B-now). Flagged to Nimrod from our side too.

## Net
Presentation layer matches your locked spec. No further design residuals. Mockup: `_COMMUNICATION/team_100/UI_REDESIGN_2026-06/mockups/calc.html` (click "השוואת גידולים" → basket; "חלון קרה" → region picker).
