# team_100 browser sweep — WP-CB-MOBILE (LIVE @ ?v=1780576560/1780691715) — 2026-06-06

**Type:** team_100 working sweep (advisory). Binding visual L-GATE_V verdict remains **team_50** (external/non-Claude, IR#1/#5).
**Method:** CDP (`qa_probe.mjs`) @ desktop 1280 + mobile 375, 8 surfaces × 2 viewports, + manual screenshot review + CDP DOM measurement. Live `https://sfa.nimrod.bio`.

## Automated (16/16 pass)
No horizontal overflow on any surface at desktop or 375; no raw region-token leak (`IL_general`/etc.); titles present. (Note: the overflow check does NOT catch vertical bloat — see the crop-page finding.)

## Verdict: **GO-WITH-FIXES** — one blocking defect on the crop page

### ❌ BLOCKER — Crop page renders the new depth IA ON TOP OF the entire legacy page (duplication, ~9,053px)
- `book_crop.php` renders the new Simple/Full/Deep depth panels (`#depth-content`, lines 241–~430) **and then also renders the full pre-Stage-2 page body below it** (lines ~558–690+): `cb-section-nav` + 7 `cb-section` blocks (identity-facts, calendar, agronomy, harvest, storage, companions, notes) + the `cb-vars` variety list.
- Measured live @375 (CDP): visible Simple panel = **627px** (correct, minimal), full/deep = `display:none`/0 (correct) — **but document height = 9,053px**, because the legacy `cb-vars` (4,995px) + `cb-section` blocks (~1,434px) are always-visible siblings outside the depth system.
- **Impact:** defeats the entire mobile remediation — the "genuinely minimal" Simple view is buried under ~8,400px of duplicated legacy content (the variety list + every legacy section). The crop page is still a giant cram.
- **Root cause:** Stage 2 *prepended* the depth IA instead of *replacing* the legacy crop-page body.
- **Fix:** remove the legacy body (section-nav + 7 cb-section blocks + cb-vars) — its content is now represented by the depth panels (calendar→Simple `.pcal`; all 17 fields→Full topics; varieties→Deep `.vtable`). **Care:** first verify each legacy section's content is covered by a depth panel and migrate any orphan (esp. the general `notes` section + any storage/companions prose) into the right depth before deleting. Re-test depth switching + heights, re-deploy.

## GO (verified)
- **Market @375:** dense `mkt-table` (D1 default), RTL stacked `t-price`, collapsed disclaimer, 11 chips, CTA — defect #3 (12,500px one-card-per-row) **fixed**. ✓
- **Crop entry cards @375:** compact single-column rows, small thumb (no wash), **name-dominant** + English subtitle, in-season `🌱/🪴` badges, season-chip filter, CTA — defect #4 **fixed**. (Full 70-crop list is long by nature; filter is the length strategy.) ✓
- **Hub / About / Calc @375 + all desktop:** automated pass (no overflow, no token leak); in-place Stage-1 edits, no layering issue. (Recommend team_50 eyeball.)

## Evidence
`screenshots/*.png` (16), `qa_probe_result.json`, `qa_config.json` in this dir.
