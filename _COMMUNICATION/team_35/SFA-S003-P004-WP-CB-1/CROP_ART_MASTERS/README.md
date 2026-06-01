# CROP_ART_MASTERS — watercolor crop illustrations (WP-CB-1 / patch01)

**WP:** SFA-S003-P004-WP-CB-1 (+ WP-CB-1-patch01 wiring) · **Owner:** team_100 · **Source:** nano-banana (Gemini) image gen
**Style SSoT:** the 4 original Devora masters in `../HANDOFF_PACKAGE/design/assets/` (wc-lettuce/radish/parsley/dill).

Canonical home for the *new* watercolor crop art (the original team_35 handoff under `../HANDOFF_PACKAGE/` stays
immutable). Art arrives in batches; this folder keeps growing.

## Layout
- `masters/` — canonical full-res masters, `wc-<slug>.png` (slug = delivery-tier crop slug). SSoT the 720px web
  derivatives are built from (`scripts/wc_derivatives.sh`, sources masters/ then the original-4 handoff).
- `incoming/` — every raw drop, lossless, named by content. Nothing discarded.

## Naming
`incoming/`: `<crop>_<descriptor>[_b2].png`; `_ALT` = alternate of a crop already mastered; `_DUP` = byte-identical
duplicate; `_AMBIGUOUS_…` = species unconfirmed; `DECOR_` = not a single-crop master.
`masters/`: `wc-<slug>.png` (one canonical per crop) + `wc-cropbook-hero.png` (the book's central illustration).

## Coverage — 28 crop masters + 1 book hero (verified, 2026-06-01)
**Served (have wc-*.png + 720px derivative) — every one wired in WC_ART + $wc_art_map (exact 28=28 match):**
basil · beet · broccoli · bush-bean · cabbage · carrot · chard · cucumber · dill · eggplant · fennel · garlic ·
ginger · kale · leek · lettuce · melon · onion · parsley · pea · pepper · pole-bean · radish · scallion · spinach ·
tomato · turmeric · zucchini = **28 crops** · plus **wc-cropbook-hero**.

Any crop NOT in this list falls back to the icon-sprite glyph (graceful) until its master is created.

## Batch 1 — 2026-06-01 (10 files) → 4 crop masters
tomato → wc-tomato · cucumber → wc-cucumber · beet → wc-beet · pepper(red-on-stem) → wc-pepper.
Parked in `incoming/`: 3 pepper alternates, 1 lettuce ALT (master exists), 1 ambiguous tan-root bunch,
1 `DECOR_book_with_greens` → **promoted to `wc-cropbook-hero.png`** (book central watercolor logo, per team_00).

## Batch 2 — 2026-06-01 (12 files) → 9 new crop masters
broccoli, cabbage, chard, eggplant, fennel, garlic, kale, scallion, melon.
Parked in `incoming/`: `beet_ALT_b2` + `cucumber_ALT_b2` (masters already exist),
`DECOR_module_icons_calc_price_book` (3-icon module graphic — Calculator / Price-List / Crops-Book; candidate for
the hub module grid, not a crop master).

## Batch 3 — 2026-06-01 (5 files) → 4 new crop masters
onion (969g1k) → wc-onion · leek (n8ahgv (1)) → wc-leek · basil (Gemini_Generated_Image_.png) → wc-basil ·
carrot ((1)) → wc-carrot. Parked in `incoming/`: `melon_cantaloupe_ALT_b3` (sn0n49 — have wc-melon),
`cabbage_ALT_b3` ((2) — have wc-cabbage; removed as exact dup).

## Batch 4 — 2026-06-01 (8 files) → 7 new crop masters
turmeric (wpvj6h) → wc-turmeric · ginger (pisxgc) → wc-ginger · spinach (7lypiy) → wc-spinach ·
pea (9yjuzf) → wc-pea · bush-bean (v6tcf0) → wc-bush-bean · pole-bean (5rqv0b) → wc-pole-bean ·
zucchini (aiyp75) → wc-zucchini. Parked: `spinach_ALT_b4` (4nvzgk — have wc-spinach).
This completes the full JMF MasterClass set (24/24) + turmeric/zucchini extras.

> **Correction note:** interim commits `ada847d` (mis-identified filenames; nonexistent masters) and a later
> attempt where the **PHP map edits silently failed** (stale Edit match → maps stayed at the original 4 even though
> PNGs were served) were both corrected by an authoritative Python rewrite of both maps. The maps now contain
> EXACTLY the 21 served crop slugs — verified `served == mapped` with zero dangling refs and zero unmapped PNGs.

## Wiring status — APPLIED (WP-CB-1-patch01, team_00-directed, 2026-06-01)
- 720px served derivatives in `sfa_delivery/public_assets/img/crops/` for all 21 crops + hero (`scripts/wc_derivatives.sh`).
- `CropBookViewController::WC_ART` (crop hero) + `book_entry.php $wc_art_map` (crop cards) list exactly the 21 served slugs.
- `wc-cropbook-hero.png` placed for the crop-book central logo.
- ICON_MAP unchanged — watercolor preferred when present; the 10-glyph sprite stays the fallback (no broken `<use>`).
- ⚠ Touches WP-CB-1 LOD500_LOCKED files (WC_ART/$wc_art_map) — chartered **WP-CB-1-patch01** scope, flagged for
  team_190 patch01 L-GATE_V. Slug↔master match to confirm vs the live MySQL mirror at QA (mismatch → glyph fallback).

### Open items for team_00
1. Identify `root_bunch_tan_AMBIGUOUS.png` (batch1) → promote to a slug or discard.
2. Confirm `wc-pepper` primary (red-on-stem) vs the bell/chili alternates parked in incoming/.
3. `DECOR_module_icons_calc_price_book.png` — use for the hub module grid? (separate from crop art.)
4. Still missing masters (fall back to glyph): basil, carrot, cauliflower, onion, leek, spinach, pea, zucchini, etc.
