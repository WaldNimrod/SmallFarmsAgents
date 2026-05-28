# MEDIA PROMPT — og-default.webp (Open Graph default share image)

- **Author:** team_100 (Chief System Architect)
- **Date:** 2026-05-28
- **Item:** WP-UI follow-up Item A (B1 from BUILD_REPORT)
- **team_100 does NOT generate media.** This artifact is prompt-only; team_00
  runs it in an image-gen session and returns the WebP.

## Target spec (all variants)

| Field | Value |
|-------|-------|
| Final filename | `og-default.webp` |
| Final path | `sfa_delivery/public_assets/img/og-default.webp` |
| Public URL | `https://sfa.nimrod.bio/public_assets/img/og-default.webp` |
| Dimensions | **1200 × 630** (canonical Open Graph) |
| Format | WebP, sRGB, quality 80, target **≤120 KB** |
| Safe zone | Keep title/logo within central 1100×560 (social crops edges) |

## Design system (from `public_assets/css/gj.css`)

- Background paper: `#f6f1e3` (warm cream); secondary `#ece5d2`
- Ink: `#2a2418`; soft ink `#776a4d`
- Accents: leaf `#6f8a45` (deep `#4d6a2c`), tomato `#c24f2c` (deep `#8e3018`),
  sun `#d39a32`, soil `#8b5d2f`
- Heading lockup font: **Frank Ruhl Libre** (serif), if any text is rendered
- Style: calm-craft watercolor + hand-drawn line work. **No photographs** —
  brand illustration only. Matches the team_35 design aesthetic
  (`_archive/SFA-S003-P002-WP-UI/team_35/_handoff/design/`).

---

## VARIANT 1 — Hero lockup (recommended)

```
Warm hand-illustrated brand banner, 1200x630, calm-craft watercolor with fine
hand-drawn ink linework on a warm cream paper background (#f6f1e3). Centered
composition: a small stylized seedling/sprout mark (two leaves, leaf-green
#6f8a45) growing from soil, flanked by 2-3 loosely painted vegetables — a ripe
red tomato (#c24f2c), a butterhead lettuce (leaf-green), and an orange carrot
(sun #d39a32). Above the produce, a clean serif Hebrew title lockup in dark ink
(#2a2418): "SFA · חקלאות קטנה" with a smaller tagline beneath. Soft watercolor
washes, visible paper texture, muted earthy palette (leaf, tomato, sun, soil
#8b5d2f). Generous margins, balanced negative space, editorial and friendly.
Flat illustration, no photorealism, no 3D, no drop shadows, sRGB.
```

## VARIANT 2 — Garden-bed band (text-light)

```
Hand-illustrated horizontal garden scene, 1200x630, watercolor + ink linework on
warm cream paper (#f6f1e3). A top-down/oblique view of a tidy raised vegetable
bed running across the lower third: rows of lettuce, carrots (sun #d39a32 tops),
and tomato plants (#c24f2c) in soft washes, soil tones (#8b5d2f). Upper area is
calm open cream space holding a compact serif Hebrew wordmark "SFA · חקלאות קטנה"
in dark ink (#2a2418) with a tiny two-leaf seedling glyph (leaf #6f8a45). Earthy,
muted, calm-craft style, visible brush texture, no photographs, no 3D, flat
editorial illustration, sRGB.
```

## VARIANT 3 — Emblem / crest (logo-forward)

```
Hand-drawn emblem composition, 1200x630, on warm cream paper (#f6f1e3). Centered
circular crest of loose ink linework + watercolor: a seedling with two leaves
(leaf-green #6f8a45) at center, encircled by small illustrated vegetables —
tomato (#c24f2c), carrot (sun #d39a32), lettuce, pepper — arranged like a wreath
in muted earthy tones (soil #8b5d2f). Below the crest, a serif Hebrew title
"SFA · חקלאות קטנה" in dark ink (#2a2418). Symmetric, calm, editorial,
craft-illustration aesthetic, visible paper grain, no photorealism, no 3D, no
neon, sRGB.
```

---

## Delivery back to team_100

Save the chosen render to `sfa_delivery/public_assets/img/og-default.webp`
(1200×630, WebP q80, ≤120 KB) in the deploy worktree, then notify team_100 →
team_100 commits + deploys via `scripts/ftp_deploy_sfa_ui.sh`.
