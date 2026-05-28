# C3 — Asset System (families, sizes, paths, export)

## Families (intensity high→low)
1. **Brand/OG/wide** — OG 1200×630, heroes 1600×900. Richest, scene-based, airy.
2. **Module heroes ×8** — 800×800 (1:1, full-bleed). One loose subject/cluster, varied per card.
3. **Functional icons** — design 96–256px → simplify to ~24px. Line-art + minimal wash.
4. **UI textures/backgrounds** — tileable/large. Near-flat, paper/wash only, must not distract.
5. **Empty states** — ~600–800px. One gentle object + space; friendly not sad.
6. **Community art** — small/medium. Loose figures sharing/contributing.

## Final paths (under `sfa_delivery/public_assets/img/`)
- `og-default.webp` (1200×630, ≤120 KB)
- `heroes/{crop-book,market,calc,planner,clients,inventory,tend-bridge,field-log}.webp` (800×800, ≤90 KB)
- `hub-hero.webp`, `contact.webp` (1600×900, ≤140 KB)
- `favicon.ico` + `favicon-32.png` + `apple-touch-icon.png` (180×180)
- icons extend `icons.svg`; textures/empty-states TBD on approval

## Generation → export (the generator won't output WebP/exact dims)
Generate PNG at the nearest canvas (1024×1024 square / 1792×1024 landscape), then
locally:
```
# square hero: 1024² → 800²
sips -z 800 800 in.png --out tmp.png && cwebp -q 80 tmp.png -o heroes/<slug>.webp
# OG: 1792×1024 → crop ~1.9:1 → 1200×630
sips -c 945 1792 in.png --out c.png && sips -z 630 1200 c.png --out t.png && cwebp -q 80 t.png -o og-default.webp
# 16:9: 1792×1024 → 1600×900
sips -c 1008 1792 in.png --out c.png && sips -z 900 1600 c.png --out t.png && cwebp -q 80 t.png -o <name>.webp
```
Verify each WebP is under budget; if over, drop `-q` to 75.

## Versioned workflow (recommended)
`candidates/` → reviewed → `approved/` (or `rejected/`). Never overwrite an
approved asset; bump a version instead.
