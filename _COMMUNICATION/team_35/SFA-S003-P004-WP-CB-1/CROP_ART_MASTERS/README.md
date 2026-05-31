# CROP_ART_MASTERS — watercolor crop illustrations (WP-CB-1)

**WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1) · **Owner:** team_100 · **Source:** nano-banana (Gemini) image gen
**Style SSoT:** the 4 original Devora masters in `../HANDOFF_PACKAGE/design/assets/` (wc-lettuce/radish/parsley/dill).

This is the canonical home for the *new* watercolor crop art (the original team_35 handoff under
`../HANDOFF_PACKAGE/` stays immutable). Art arrives in batches; this folder is built to keep growing.

## Layout
- `masters/` — **canonical full-res masters**, named `wc-<slug>.png` (slug = crop slug used by the delivery tier).
  These are the SSoT the 720px web derivatives are built from (`scripts/wc_derivatives.sh`).
- `incoming/` — **every raw drop, lossless**, named by content. Nothing is discarded — duplicates, alternates,
  ambiguous, and decorative pieces all kept here so a better pick can be promoted later.

## Naming convention
`incoming/`: `<crop>_<descriptor>.png` (e.g. `pepper_bell_green.png`); `_ALT` = duplicate of a crop we already
have a master for; `_AMBIGUOUS` = species unconfirmed; `DECOR_` = not a single-crop master (hero/ornament).
`masters/`: `wc-<slug>.png` only — one canonical master per crop.

## Batch 1 — 2026-06-01 (10 files from nano-banana)

| incoming file | content | disposition |
|---|---|---|
| `tomato_branch_2fruit.png` | עגבנייה — 2 fruit on a leafy branch | ✅ promoted → `masters/wc-tomato.png` (P0 gap filled) |
| `cucumber_single.png` | מלפפון — single fruit | ✅ promoted → `masters/wc-cucumber.png` (P0 gap filled) |
| `beet_single_red.png` | סלק — single burgundy root + tops | ✅ promoted → `masters/wc-beet.png` (P1 gap filled) |
| `pepper_red_on_stem.png` | פלפל — red fruit on stem | ✅ promoted → `masters/wc-pepper.png` (P1; chosen primary) |
| `pepper_chili_red_green_branch.png` | פלפל חריף — red+green on branch | ⏸ alternate (kept; not promoted) |
| `pepper_bell_green.png` | גמבה ירוקה | ⏸ alternate |
| `pepper_bell_green_2.png` | גמבה ירוקה (variant) | ⏸ duplicate alternate |
| `lettuce_head_ALT.png` | חסה — head | ⏸ ALT — `wc-lettuce.png` master already exists |
| `root_bunch_tan_AMBIGUOUS.png` | bunch of round tan/brown roots + green tops | ⚠ species unconfirmed (turnip/לפת? alt radish?) — **needs team_00 confirmation before promotion** |
| `DECOR_book_with_greens.png` | open book with lettuce + parsley sprig | 🎨 decorative hero/ornament — not a crop master |

### Open items for team_00
1. **Pepper primary:** `wc-pepper.png` = the red-on-stem pick. Confirm, or swap for a bell/chili alternate.
2. **Ambiguous root:** identify `root_bunch_tan_AMBIGUOUS.png` (turnip vs radish-alt) — promote to the right
   slug or discard.
3. **Decorative book:** keep as a crop-book landing/hero ornament? (could wire into the `/crop-book/` header).

## Downstream (deferred to the art-completion patch, NOT done yet)
When the art set is final, one tracked WP-CB-1 follow-up patch will:
1. `scripts/wc_derivatives.sh tomato cucumber beet pepper [...]` → 720px served derivatives in
   `sfa_delivery/public_assets/img/crops/`.
2. Extend `$wc_art_map` (`book_entry.php`) + the controller's crop-hero art map + `ICON_MAP` (add `beet`).
   The card grid (`book_entry.php`) and crop hero (`book_crop.php`) already consume the art — they light up
   automatically once the master + map entry exist.
Deferred deliberately: more art is incoming, and the current branch has a pending team_190 L-GATE_V R2 whose
delta is scoped to 3 presentation files — wiring is bundled into the follow-up to keep that clean.
