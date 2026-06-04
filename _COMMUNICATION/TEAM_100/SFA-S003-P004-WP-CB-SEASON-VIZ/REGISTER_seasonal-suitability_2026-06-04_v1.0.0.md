# REGISTER — Seasonal-suitability model + crop-page season interface (future WP)

**Date:** 2026-06-04 · **Author:** team_100 · **Status:** REGISTER (data model DECIDED by team_00; build deferred to a future WP)
**Origin:** WP-CB-UI-WI7 Q4 — team_00 elevated the season filter from binary to a 4-level graded model + a new visual interface.

## Data model (DECIDED — team_00)
Per crop × season, suitability = count of the season's 3 months present in the crop's **sow ∪ transplant** window:
| months in season | level | label (Hebrew) |
|---|---|---|
| 3/3 | ● | מועדף |
| 2/3 | ◐ | מתאים |
| 1/3 | ○ | אפשרי |
| 0/3 | — | לא מתאים |
Seasons: אביב [3,4,5] · קיץ [6,7,8] · סתיו [9,10,11] · חורף [12,1,2].
Semantics: "מתאים לקיץ" = **sown/transplanted in** the season's months (planting-window coverage = flexibility; NOT a separate agronomic optimal rating — a richer optimal-window dataset would be a future data WP). Coverage: 45/70 crops have month data; 25 have none → "אין נתוני עונה".
Full 45-crop graded matrix: see this session's transcript / regenerate via `sowing_months ∪ transplant_months` ∩ season-months (data in `crop_attribute`).

## Interface (DECIDED direction — team_00; build deferred)
- **Crop page — "Seasonal suitability" strip:** four season cells (אביב☘ · קיץ☀ · סתיו🍂 · חורף❄), each rendering the crop's **watercolor icon** at a fill matching its level (● full → ◐ ~60% → ○ ~30% → — greyed outline) + Hebrew level label. One glance = the whole year, in the brand's hand.
- **Entry cards — mini 4-dot season row** (`●◐○—`) for scannability.
- **Filter / leading-questions** reuse the levels (e.g. "מה מתאים לקיץ?" = level ≥ ◐).
- Alternatives noted: 12-month ring with planting months lit + season bands; horizontal year-bar.

## Build scope (future WP)
Render-layer + a small data-derivation helper (compute levels from months at render time, no DB change). New crop-page component + entry-card mini-indicator + filter wiring + the icon-fill treatment. team_00 design direction above is the spec basis; needs a proper LOD + team_50 visual QA on build.
