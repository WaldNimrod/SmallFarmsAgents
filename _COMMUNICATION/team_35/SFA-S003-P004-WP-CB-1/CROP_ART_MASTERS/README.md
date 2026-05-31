# CROP_ART_MASTERS — watercolor crop illustrations (WP-CB-1 / patch01)

**WP:** SFA-S003-P004-WP-CB-1 (+ WP-CB-1-patch01 wiring) · **Owner:** team_100 · **Source:** nano-banana (Gemini) image gen
**Style SSoT:** the 4 original Devora masters in `../HANDOFF_PACKAGE/design/assets/` (wc-lettuce/radish/parsley/dill).

Canonical home for the *new* watercolor crop art (the original team_35 handoff under `../HANDOFF_PACKAGE/` stays
immutable). Art arrives in batches; this folder keeps growing.

## Layout
- `masters/` — canonical full-res masters, `wc-<slug>.png` (slug = delivery-tier crop slug). SSoT the 720px web
  derivatives are built from (`scripts/wc_derivatives.sh`).
- `incoming/` — every raw drop, lossless, named by content. Nothing discarded (duplicates, alternates, ambiguous,
  decorative all kept so a better pick can be promoted later).

## Naming
`incoming/`: `<crop>_<descriptor>.png`; `_ALT`/`_ALT2…` = alternate of a crop already mastered; `_DUP` = byte-identical
duplicate; `_AMBIGUOUS_…` = species unconfirmed; `DECOR_` = not a single-crop master.
`masters/`: `wc-<slug>.png` (one canonical per crop) + `wc-cropbook-hero.png` (the book's central illustration).

## Coverage — 20 crop masters + 1 book hero (as of 2026-06-01)
wc-tomato · wc-cucumber · wc-beet · wc-pepper · wc-basil · wc-cabbage · wc-broccoli · wc-cauliflower · wc-eggplant ·
wc-carrot · wc-garlic · wc-onion · wc-scallion · wc-kale · wc-chard · wc-leek · wc-spinach · wc-pea · wc-melon ·
wc-fennel  + the original 4 (lettuce/radish/parsley/dill) = **24 crops** · **wc-cropbook-hero** (book logo).

## Batch 1 — 2026-06-01 (10 files)
tomato → wc-tomato · cucumber → wc-cucumber · beet → wc-beet · pepper(red-on-stem) → wc-pepper (primary).
Parked in `incoming/`: 3 pepper alternates, 1 lettuce ALT (master exists), 1 ambiguous tan-root bunch,
1 `DECOR_book_with_greens` → **promoted 2026-06-01 to `wc-cropbook-hero.png`** (book central logo, per team_00:
single style-consistent watercolor book image replacing the prior repo hero).

## Batch 2 — 2026-06-01 (20 files) — 16 new masters promoted
basil, cabbage, broccoli, cauliflower, eggplant, carrot, garlic (×2 identical drops → 1 master + 1 `_DUP`),
onion, scallion, kale, chard, leek, spinach, pea, melon, fennel.
Parked in `incoming/`: `pepper_bell_green_ALT3`, `pepper_bell_red_ALT` (have wc-pepper),
`bulb_pale_AMBIGUOUS_kohlrabi-turnip` (⚠ team_00 to identify → קולרבי/לפת).

## Wiring status — APPLIED (WP-CB-1-patch01, team_00-directed, 2026-06-01)
- 720px served derivatives built into `sfa_delivery/public_assets/img/crops/` (`scripts/wc_derivatives.sh`).
- `CropBookViewController::WC_ART` (crop hero) + `book_entry.php $wc_art_map` (crop cards) extended with all 20 new slugs.
- `wc-cropbook-hero.png` placed for the crop-book central logo.
- ICON_MAP intentionally NOT extended — watercolor (WC_ART/$wc_art_map) is preferred when present; the 10-glyph
  sprite stays the fallback for crops without a master (avoids broken `<use href="#icon-X">`).
- ⚠ This wiring touches WP-CB-1 LOD500_LOCKED files; it is the chartered scope of **WP-CB-1-patch01** and is flagged
  for team_190 patch01 L-GATE_V. Slug↔master match must be confirmed against the live MySQL mirror at QA (a slug that
  differs simply falls back to glyph — graceful).

### Open items for team_00
1. Identify `bulb_pale_AMBIGUOUS_kohlrabi-turnip.png` → promote to wc-kohlrabi / wc-turnip or discard.
2. Confirm `wc-pepper` primary (red-on-stem) vs the bell alternates.
3. Confirm `wc-cropbook-hero` placement (crop-book landing hero) — and whether to also replace the hub module-grid
   `heroes/crop-book.webp`.
