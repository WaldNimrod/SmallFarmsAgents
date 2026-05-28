# MEDIA PROMPT — Module Hero Images (8 mod-cards)

- **Author:** team_100 (Chief System Architect)
- **Date:** 2026-05-28
- **Item:** WP-UI follow-up Item D (COMPONENTS.md §3 + §15 hero slot)
- **team_100 does NOT generate media.** Prompt-only; team_00 runs these in an
  image-gen session and returns the 8 WebP files.

## Shared spec (all 8)

| Field | Value |
|-------|-------|
| Dimensions | **800 × 800** (1:1 mod-card art slot) |
| Format | WebP, sRGB, quality 80, target **≤90 KB each** |
| Text | **NONE in image** — the Hebrew title is rendered by HTML over the card |
| Style | calm-craft watercolor + hand-drawn ink linework, warm cream paper |
| Reference | team_35 design (`_archive/SFA-S003-P002-WP-UI/team_35/_handoff/design/index.html`) |
| No | photographs, 3D, neon, drop shadows, text/letters/numbers |

**Palette (from `gj.css`):** paper `#f6f1e3` / `#ece5d2`, ink `#2a2418`,
leaf `#6f8a45` (deep `#4d6a2c`), tomato `#c24f2c` (deep `#8e3018`),
sun `#d39a32`, soil `#8b5d2f` (deep `#5a3c1a`).

**Final paths (slug-exact — must match `modules.php` ids):**
`sfa_delivery/public_assets/img/heroes/{slug}.webp`

| # | slug | tier | palette | file |
|---|------|------|---------|------|
| 1 | crop-book | open | leaf | `heroes/crop-book.webp` |
| 2 | market | open | tomato | `heroes/market.webp` |
| 3 | calc | beta | sun | `heroes/calc.webp` |
| 4 | planner | coming | leaf | `heroes/planner.webp` |
| 5 | clients | paid | soil | `heroes/clients.webp` |
| 6 | inventory | paid | tomato | `heroes/inventory.webp` |
| 7 | tend-bridge | custom | soil | `heroes/tend-bridge.webp` |
| 8 | field-log | custom | leaf | `heroes/field-log.webp` |

---

### 1 — crop-book.webp (leaf)

```
Square 800x800 hand-illustrated card art, calm-craft watercolor with fine ink
linework on warm cream paper (#f6f1e3). Top-down view of a tidy raised vegetable
garden bed: neat rows of leafy greens — lettuce heads, chard, kale — in soft
leaf-green washes (#6f8a45, deep #4d6a2c) over brown soil (#8b5d2f). Calm, full-
bleed, balanced, muted earthy palette, visible paper grain. No text, no 3D, flat
editorial illustration, sRGB.
```

### 2 — market.webp (tomato)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). An open-air farmers market stall brimming with mixed vegetables —
ripe tomatoes (#c24f2c, deep #8e3018), peppers, cucumbers, leafy bunches — in
woven baskets, warm tomato-and-soil palette with sun #d39a32 highlights. Loose
brush texture, full-bleed, calm-craft style. No text, no 3D, flat illustration,
sRGB.
```

### 3 — calc.webp (sun)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). Abstract numeric/grid motif — a softly painted grid of squares
and simple ledger lines — overlaid with a delicate hand-drawn leaf and sprout
(leaf-green #6f8a45). Warm sun palette (#d39a32) with soil accents (#8b5d2f).
Calm, conceptual, balanced, paper texture. No legible text/numbers, no 3D, flat
editorial illustration, sRGB.
```

### 4 — planner.webp (leaf)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). A wall calendar / planting grid sketched by hand, its cells
holding tiny watercolor vegetable and seedling sketches (carrots, lettuce, basil)
in muted leaf-green (#6f8a45) and sun (#d39a32) on soft paper tones. Calm,
organized, airy composition. No legible text, no 3D, flat editorial illustration,
sRGB.
```

### 5 — clients.webp (soil)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). A handwritten farm ledger / notebook beside a small woven basket
of produce subscription veg (mixed greens and roots), warm soil palette (#8b5d2f,
deep #5a3c1a) with leaf-green (#6f8a45) accents. Cozy, crafted, calm composition,
visible paper grain. No legible text, no 3D, flat editorial illustration, sRGB.
```

### 6 — inventory.webp (tomato)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). A wooden harvest crate filled with mixed just-picked produce —
tomatoes (#c24f2c, deep #8e3018), strawberries, peppers, leafy bunches — warm
tomato-and-paper palette over soil tones (#8b5d2f). Loose brush texture, full-
bleed, calm-craft style. No text, no 3D, flat editorial illustration, sRGB.
```

### 7 — tend-bridge.webp (soil)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). An abstract connection/bridge motif — two softly painted nodes
linked by a flowing hand-drawn line — set over a calm farm field horizon with
rows of crops in muted soil palette (#8b5d2f, deep #5a3c1a) and leaf-green
(#6f8a45) accents. Conceptual, calm, balanced. No text/logos, no 3D, flat
editorial illustration, sRGB.
```

### 8 — field-log.webp (leaf)

```
Square 800x800 hand-illustrated card art, watercolor + ink linework on warm cream
paper (#f6f1e3). An open notebook lying on soil, its pages holding hand-drawn
crop sketches, weather marks (sun #d39a32, cloud), and small leaf studies in
leaf-green (#6f8a45, deep #4d6a2c). A pencil and a sprig of basil rest beside it.
Cozy, crafted, calm composition, paper grain. No legible text, no 3D, flat
editorial illustration, sRGB.
```

---

## Delivery back to team_100

Save all 8 renders as `sfa_delivery/public_assets/img/heroes/{slug}.webp`
(800×800, WebP q80, ≤90 KB) in the deploy worktree. Wiring is already in place:
`module_card.php` emits `<img class="mod-card__hero">` when `$module['hero_url']`
is set, and `hub.css` reverts the icon to a corner badge automatically. team_100
will add `hero_url` per module in `modules.php` and deploy once images land.
