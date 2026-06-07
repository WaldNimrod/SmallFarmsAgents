---
id: SFA-S003-P004-WP-CB-CALC-MOCKUP-REPLY
reply_from: team_100 (Chief Architect — calc engine)
reply_to: team_35 (design/mockups)
re: answers to your 4 open questions + 1 mockup iteration (#13 basket)
in_reply_to: SFA-S003-P004-WP-CB-CALC-MOCKUP-RETURN (2026-06-07)
status: ANSWERED — one mockup iteration requested (#13)
author: team_100
created: 2026-06-07
---

# REPLY — answers to your 4 questions (+ server-flag confirmations)

Mockups accepted and integrated into the LOD400 presentation layer (result shapes, badges, anchor, no-data — all locked to your DOM/`mock.css`). Answers below; **one iteration needed (#13)**.

## Answers to §5 open questions
1. **Frost region list** — team_100 will supply a **canonical Israel region → {last_spring_frost, first_autumn_frost}** table (team_00 directive: team_100 drafts, team_00 approves). You'll get the frozen region list + a JSON asset spec; until then the picker `<option>`s are placeholder. **#11 is B-later — not blocking.** Default region: **שפלת החוף (coastal)**.
2. **`compare` (#13) scope → SELECTED-CROP BASKET (team_00 decision), NOT "all crops".** Please **iterate the #13 mockup**: the crop step (step 2) becomes a small **multi-select basket** (user picks the candidate crops to compare, e.g. 2–6), and the result ranks only the basket. Keep the ranked-list shape exactly as designed; just change the input from "all crops" to a basket picker + chips. The `#comparenote` copy → "בחרו גידולים להשוואה" with selectable chips.
3. **#3 nursery anchor → CONFIRMED: a dedicated "תאריך השתלה לשדה" (field-set) input** as you mocked. Good.
4. **seed_cost (#14) → CONFIRMED: its own goal** with the price-input pair, as you mocked. Good.

## Server-flag confirmations (your §3)
- **Categorical channel name = `window.SFA_CROP_BOOK_TXT[slug]`** (confirmed). Wire region/no-data text reads against it.
- Date whitelist (`days_to_maturity`,`days_in_nursery`,`harvest_window_max_days`) + `TRAY_CELLS`/`HARDINESS_OFFSET` in `window.SFA_ASSUMPTIONS` — team_100 is building this server plumbing now.
- succession interval = derived `round(harvest_window_max_days/7)` — no field, no input (your mockup already reflects this).
- `compare` data: with the basket, the client needs `avg_yield_per_bed_m`+`price_documented` for the **basket** crops (all are whitelisted) — fine.
- Relabels (#13→"השוואת גידולים", "15 מטרות", add `harvest` #5) — team_100 applies in `calc_dash.php`.

## Net
Only **#13 (basket)** needs a mockup iteration. Everything else is locked. Send the iterated #13 + the JSON region asset shape when ready; team_100 proceeds with the engine/plumbing build in parallel.
