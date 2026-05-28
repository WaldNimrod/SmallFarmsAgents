# C3 — Asset System (brand-wide families + formats)

All families share the C2 watercolor DNA. Produced in phases (D01=C).

## Families
1. **Logo family** (T-04) — primary logo, 3 world variations (אדמה/ידע/דיגיטל),
   commercial basket set. Must work at favicon 16px, print/mono, round avatar.
   Source: `02-PROMPT-logo-family.md` + `source_masters/logos_*`.
2. **Worlds hero backgrounds** (T-03) — 5 semi-abstract watercolor heroes (Soil,
   Know, Code, Home, About). 16:9; 30% quiet zone for text. Source:
   `01-PROMPT-watercolor-backgrounds.md`.
3. **SFA module heroes** (×8) — crop-book, market, calc, planner, clients,
   inventory, tend-bridge, field-log. 800×800 (1:1). One loose subject/cluster each.
4. **Functional icons** — line-art + minimal wash (D09). Legible at 24px. Extends SFA `icons.svg`.
5. **OG / share** — 1200×630. 6. **Favicon set** — from the basket/seedling mark.
7. **UI textures / backgrounds** — near-flat paper/wash, edge-safe, non-distracting.
8. **Empty states** — one gentle object + space.

## Formats (per the locked watercolor brief)
- **Vector preferred (SVG)** where possible.
- Raster: **PNG on transparency + JPG on paper-bg**; 1× = 1920×1080, 2× = 3840×2160.
- Hero ratio 16:9 (worlds) / 4:3 (blog) / 1:1 (SFA module heroes) / 1200×630 (OG).
- Deliver 4 variants per hero where applicable: SVG, PNG@1x, PNG@2x, JPG@2x.

## SFA web slots (final paths under `sfa_delivery/public_assets/img/`)
`og-default.webp` (1200×630, ≤120KB) · `heroes/{slug}.webp` ×8 (800×800, ≤90KB) ·
`hub-hero.webp`/`contact.webp` (1600×900, ≤140KB) · `favicon.*`. See
`…/02_PRODUCT_UI_CONTEXT/current_asset_slots.md`.

## Generate → export
Engine outputs PNG at fixed canvases (1024² / 1792×1024) and won't hit exact hex/WebP.
Export locally (sips + cwebp) to target dims/budget; full recipe in
`…/SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF/07_READY_TO_UPLOAD_TO_CHATGPT/CONTEXT_C3_ASSET_SYSTEM.md`.

## Versioned workflow (D08)
`candidates/` → reviewed → `approved/` / `rejected/`. Never overwrite approved; version up.
