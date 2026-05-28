# Current SFA Asset Slots (product source: sfa.nimrod.bio / sfa_delivery)

The functional/product source. Slots are derived from the live Slim/PHP app
(`sfa_delivery/`): `_layout.php`, `templates/shell/*`, `templates/macros/*`,
`modules.php`, `public_assets/`. Existing on disk: only `public_assets/img/icons.svg`.

| UI area | Current asset path / reference | Needed visual role | Current status | Priority | Notes |
|---------|-------------------------------|--------------------|----------------|----------|-------|
| OG / social share | `public_assets/img/og-default.webp` (referenced in `_layout.php`) | 1200×630 brand share image | **MISSING (break)** | P0 | og:image points to it; social previews broken |
| Module card heroes ×8 | `public_assets/img/heroes/{slug}.webp` (wired via `module_card.php` `hero_url`) | 800×800 per-module card art | MISSING (icon fallback active) | P1 | slugs: crop-book, market, calc, planner, clients, inventory, tend-bridge, field-log |
| Hub home hero | `public_assets/img/hub-hero.webp` (latent; `modules.php::thumb_prompts['module_hub']`) | 16:9 homepage hero illustration | LATENT (not wired/rendered) | P2 | "home research workshop" desk scene intent |
| Contact / community CTA | `public_assets/img/contact.webp` (latent; `thumb_prompts['contact']`; CSS `.contact-card__art` 16:9) | 16:9 warm people+greenhouse scene | LATENT | P2 | contact-card art slot exists in hub.css |
| Favicon set | none referenced | favicon.ico + 32 + apple-touch 180 | MISSING (gap) | P2 | derive from seedling mark |
| Functional icons | `public_assets/img/icons.svg` (inline sprite) | line icons: leaf, seedling, tomato, lettuce, cucumber, pepper, eggplant, carrot, onion, zucchini | PRESENT (line-art) | — | style anchor for new icons (D09) |
| Empty states | none | "no results", empty search, empty feed illustrations | MISSING (future) | P3 | not yet designed; future family |
| UI textures / backgrounds | CSS solid `--gj-paper` / washes only | subtle paper/wash textures for sections | MISSING (future) | P3 | currently flat color; potential paper-texture family |
| Community feed | text-only (CommunityFeed) | optional small contribution illustrations | MISSING (future) | P3 | read-only feed live; could gain small art |

## Page / section list (routes)
home (`/`), crop-book (`/crop-book/` + family/crop/variety/table/search/questions),
market (`/market/` + product), calc (`/calc`), community (`/community`),
search (`/search`), about. Shells: desktop (sidebar) + mobile.

## Layout facts that constrain art
- RTL Hebrew throughout; titles rendered in HTML (Frank Ruhl Libre) OVER art — **no text in images**.
- Module card art slot is `aspect-ratio: 1/1`; hero `<img>` is full-bleed `object-fit: cover`; icon reverts to corner badge when a hero image is present.
- Contact card art slot is `aspect-ratio: 16/9`.
- Calm brand: "no parallax, no hero-scroll-effects" (DESIGN_TOKENS).
