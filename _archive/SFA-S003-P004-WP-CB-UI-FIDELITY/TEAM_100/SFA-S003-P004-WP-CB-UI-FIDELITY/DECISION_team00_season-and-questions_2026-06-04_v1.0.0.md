# DECISION — SFA-S003-P004-WP-CB-UI-FIDELITY — team_00 (recorded by team_100) — v1.0.0

**Date:** 2026-06-04 · **Decider:** team_00 (Nimrod), in-session · **Scope:** D-4 filters (Decisions A & B)

## Context
L-GATE_B surfaced that the delivery mirror's `crops.season` column stores **growth-cycle** tokens (annual/year-round/biennial), not planting season — so the original "season" filter was unbacked. team_10's build relabeled it honestly to "מחזור גידול" and deferred a real season filter to a data WP.

## Decision A — Season filter: derive season FROM months (NO data WP)
team_00 ruling: **"יש לנו חודשים לכל גידול — מה הבעיה לתרגם עונה לחודשים?"** We already store planting months per crop, so derive the season from them.

**Confirmed against canonical Postgres (organic_market_agent):**
- `sowing_months` = `int[]` arrays (e.g. `[2,3,4,10,11,12]`), mirrored into `crops.payload_json` (agronomy block; same place `planting_method` is read).
- Coverage: **39/70 crops** with `sowing_months`; **+`transplant_months`** brings it to ~44/70. `season_window` is unpopulated (do not use).

**Implementation (render/query-layer, existing data — supersedes the "data WP" path):**
- Restore a real **"עונה"** season filter as a `<select>`: קיץ / חורף / אביב / סתיו (+ "הכל").
- Season→months map (meteorological, Israel): summer `[6,7,8]`, autumn `[9,10,11]`, winter `[12,1,2]`, spring `[3,4,5]`.
- A crop matches season X iff its `sowing_months` **∪** `transplant_months` intersect months(X). Crops lacking month data simply don't match (honest partial coverage — document it).
- Drop the "מחזור גידול" relabel; the growth-cycle `crops.season` column is no longer the season-filter backing.

## Decision B — Leading questions: team_35 designs the backable set
team_00 ruling: **team_35 designs a data-backed question set.** With Decision A, summer/winter are now backable (via months) and `fast` via `dtm_max` — so the feature need not be gutted.

**Interim (ship now, team_35 refines/expands):** restore `summer`/`winter` (→ `?season=…`) and `fast` (→ `?dtm_max=60`) leading-questions; **fix the entry-card "12 שאלות" count** to reflect the actual number. team_35 owns the final set + the exact "מתאים לקיץ" semantics (sow-in-season vs grow-in-season) via the existing `DESIGN_REQUEST_team35_v1.0.0.md` (Q4).

## Deploy
team_00: **HOLD deploy** until A is implemented and B routed — then one clean deploy (still subsumes the team_50 deploy-lag NO-GO).
