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

## Coverage — 17 crop masters + 1 book hero (verified, 2026-06-01)
**Served (have wc-*.png + 720px derivative):**
tomato · cucumber · beet · pepper · broccoli · cabbage · chard · eggplant · fennel · garlic · kale · scallion ·
melon  + original lettuce · radish · parsley · dill = **17 crops** · plus **wc-cropbook-hero**.

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

> **Correction note:** an interim commit (`ada847d`) was authored from mis-identified filenames and listed crops
> with no actual master (basil/cauliflower/carrot/onion/leek/spinach/pea). It was corrected the same session — the
> maps now list **only the 17 slugs that have a real served PNG** (every WC_ART/$wc_art_map ref verified to resolve).

## Wiring status — APPLIED (WP-CB-1-patch01, team_00-directed, 2026-06-01)
- 720px served derivatives in `sfa_delivery/public_assets/img/crops/` for all 17 crops + hero (`scripts/wc_derivatives.sh`).
- `CropBookViewController::WC_ART` (crop hero) + `book_entry.php $wc_art_map` (crop cards) list exactly the 17 served slugs.
- `wc-cropbook-hero.png` placed for the crop-book central logo.
- ICON_MAP unchanged — watercolor preferred when present; the 10-glyph sprite stays the fallback (no broken `<use>`).
- ⚠ Touches WP-CB-1 LOD500_LOCKED files (WC_ART/$wc_art_map) — chartered **WP-CB-1-patch01** scope, flagged for
  team_190 patch01 L-GATE_V. Slug↔master match to confirm vs the live MySQL mirror at QA (mismatch → glyph fallback).

### Open items for team_00
1. Identify `root_bunch_tan_AMBIGUOUS.png` (batch1) → promote to a slug or discard.
2. Confirm `wc-pepper` primary (red-on-stem) vs the bell/chili alternates parked in incoming/.
3. `DECOR_module_icons_calc_price_book.png` — use for the hub module grid? (separate from crop art.)
4. Still missing masters (fall back to glyph): basil, carrot, cauliflower, onion, leek, spinach, pea, zucchini, etc.
