# C5 — Prompting Rules (how to write each generation prompt)

## Prompt skeleton (per asset)
1. **Canvas:** "Square 1024×1024" OR "Landscape 1792×1024" (per the asset's target).
2. **Subject:** one loose subject or a small cluster (from C1 anchors). Be specific
   but not busy. Vary subjects across siblings — no repeated lineups.
3. **Treatment (always include):** "watercolor with fine warm-brown ink linework on
   warm cream paper (#f6f1e3), visible paper grain, loose washes, paper-showing
   highlights, muted earthy palette."
4. **Composition:** "off-center, generous breathing room, calm, hand-painted,
   slightly imperfect."
5. **The match line (always append):** the standing instruction from C4 (match the
   attached references, especially `ref_watercolor_radishes.jpg`).
6. **Negatives (always):** "no text, numbers, or logos; no photograph; no 3D; no
   drop shadows; no neon; no glossy gradients; not digital-clean; not symmetrical."

## Do / Don't
- DO attach the reference images to the session.
- DO keep each asset distinct from its siblings.
- DO generate the calibration set first; wait for approval.
- DON'T render any text/UI/letters.
- DON'T default to "seedling + tomato + carrot, centered."
- DON'T crank saturation or sharpness to look "polished" — calm beats crisp.

## Per-family tweaks
- **Icons:** "single centered glyph, line-first, minimal wash, legible at 24px."
- **Textures:** "abstract, edge-safe, near-flat, no recognizable objects, must sit
  quietly behind text."
- **Empty states:** "one small gentle object with lots of empty paper; friendly, calm."

## After generating
Export per C3 (sips/cwebp) to the target dims + WebP budget. Score against the QA
rubric before approving.
