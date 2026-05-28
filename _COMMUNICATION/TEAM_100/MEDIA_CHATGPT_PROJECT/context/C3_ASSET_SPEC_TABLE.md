# C3 — Asset Spec Table + Export Recipe

The 12 assets this project produces. Filenames and paths are **exact** — the
website expects them. Priority: P0 = active break, P1 = wired slot, P2 = optional.

| Session | Asset | Final filename + path (under `sfa_delivery/public_assets/img/`) | Final dims | Aspect | Gen canvas | WebP budget | Priority |
|---------|-------|-----------------------------------------------------------------|-----------|--------|-----------|-------------|----------|
| 01 | OG share image | `og-default.webp` | 1200×630 | ~1.9:1 | 1792×1024 (landscape) → crop | ≤120 KB | **P0** |
| 02 | hero crop-book | `heroes/crop-book.webp` | 800×800 | 1:1 | 1024×1024 (square) | ≤90 KB | P1 |
| 03 | hero market | `heroes/market.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 04 | hero calc | `heroes/calc.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 05 | hero planner | `heroes/planner.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 06 | hero clients | `heroes/clients.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 07 | hero inventory | `heroes/inventory.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 08 | hero tend-bridge | `heroes/tend-bridge.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 09 | hero field-log | `heroes/field-log.webp` | 800×800 | 1:1 | 1024×1024 | ≤90 KB | P1 |
| 10 | hub hero | `hub-hero.webp` | 1600×900 | 16:9 | 1792×1024 (landscape) | ≤140 KB | P2 |
| 11 | contact illustration | `contact.webp` | 1600×900 | 16:9 | 1792×1024 | ≤140 KB | P2 |
| 12 | favicon set | `favicon.ico` + `favicon-32.png` + `apple-touch-icon.png` (180×180) | see prompt | 1:1 | 1024×1024 | ≤30 KB ea | P2 |

## Why a separate canvas vs final dims
ChatGPT's image generator outputs PNG at fixed canvases (1024×1024,
1792×1024, 1024×1792). It does **not** output WebP or arbitrary pixel sizes, and
won't hit exact hex colors. So: generate → download PNG → crop/resize → convert
to WebP **outside** ChatGPT.

## Export recipe (run locally after download)
Requires `cwebp` (`brew install webp`) and `sips` (built into macOS) or
ImageMagick `convert`.

**Square heroes (sessions 02–09): 1024×1024 PNG → 800×800 WebP**
```
sips -z 800 800 in.png --out tmp.png
cwebp -q 80 tmp.png -o heroes/<slug>.webp
```

**OG image (session 01): 1792×1024 PNG → crop to 1.9:1 → 1200×630 WebP**
```
# center-crop 1792×1024 to 1792×945 (≈1.9:1), then resize
sips -c 945 1792 in.png --out crop.png        # sips -c is height width
sips -z 630 1200 crop.png --out tmp.png
cwebp -q 80 tmp.png -o og-default.webp
```

**16:9 (sessions 10–11): 1792×1024 → 1600×900 WebP**
```
sips -c 1008 1792 in.png --out crop.png        # 1792×1008 = 16:9
sips -z 900 1600 crop.png --out tmp.png
cwebp -q 80 tmp.png -o <name>.webp
```

**Favicon (session 12): 1024×1024 mark PNG → sizes**
```
sips -z 180 180 mark.png --out apple-touch-icon.png
sips -z 32 32 mark.png --out favicon-32.png
# ICO (ImageMagick): convert mark.png -define icon:auto-resize=16,32,48 favicon.ico
```

Verify each WebP is under budget: `ls -l <file>.webp`. If over, drop `-q` to 75.

## Consistency check before finalizing
Lay sessions 01–09 side by side: same cream paper, same brush/ink feel, same
muted saturation. Regenerate any outlier.
