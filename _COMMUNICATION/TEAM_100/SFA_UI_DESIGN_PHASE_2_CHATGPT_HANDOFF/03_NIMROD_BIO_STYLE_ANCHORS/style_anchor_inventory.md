# Style Anchor Inventory — nimrod.bio illustration line

The existing brand illustration line ("מהגינה של נימרוד" — From Nimrod's Garden).
This is the **style source** for the SFA visual system. We continue this line; we
do not invent a new one. **The actual image files in `images/` are essential —
verbal description alone is insufficient.**

| File | Source path / URL | Visual role | Why it matters | Use in future prompting |
|------|-------------------|-------------|----------------|-------------------------|
| `ref_watercolor_radishes.jpg` | nimrod.bio `/uploads/2019/07/selejk.jpg` | **PRIMARY anchor** — loose watercolor radishes/beets on cream paper, light pencil outline | The single clearest example of the painterly treatment to match: wash softness, restraint, paper grain | Attach to every session; "match this watercolor treatment" |
| `ref_brand_logo_basket.png` | nimrod.bio `/uploads/2019/07/logo.png` | Brand logo — woven basket of vegetables, soft fills + warm brown ink line | Defines the line-and-fill treatment + the vegetable palette + brand identity | Palette + ink-line reference (do NOT reproduce the Hebrew wordmark) |
| `ref_lineart_basket.png` | nimrod.bio `/uploads/2019/07/bucket.png` | Line-art basket (grey monochrome) | Shows the confident hand-drawn outline underneath the washes | Icon / line-work reference (feeds icon style D09) |
| `ref_usage_basket_flyer.jpg` | nimrod.bio `/uploads/2019/07/סל-e1562960018997.jpeg` | Real usage: "מה בסל היום?" flyer using the watercolor radishes + carrot-top greens + basket together | Shows how the elements compose in actual brand collateral; reveals a watercolor **greens/carrot-top** study not isolated elsewhere | Composition/style board (ignore its Hebrew text; study the painted elements) |

## ⭐ UPDATE 2026-05-28 — authentic source masters located (`source_masters/`)
The original designer (Devora) brand assets were found in local backups + Google
Drive and collected into `source_masters/`. This **largely resolves the thin-base
risk** below:
- **6 watercolor illustration masters** (PSD → flattened PNG): radishes, lettuce,
  dill, parsley ×2, bunch — high-res, transparent. These supersede the web JPGs.
- **Vector logos** (PDF) + transparent PNG logos + basket motif.
- **Carmela brand font** (the wordmark typeface).
See `source_masters/MANIFEST.md` for paths + raw-PSD locations. Anchor the style
board on `source_masters/watercolor_illustrations/radishes.png` (primary).

## Coverage finding (IMPORTANT — feeds decision D03)
The genuine standalone illustration assets are **few**: 3 clean assets + 1 usage
flyer. The rest of nimrod.bio is an old photo-based marketing site (Flatsome
theme) — produce photos, WhatsApp images, screenshots, aquaponics articles — NOT
part of the illustration line. So the reference base for "continue the line" is
thin. Before mass generation we should either (a) accept the 4 anchors as the
style board, or (b) commission/locate more pieces in this exact hand. See D03.
