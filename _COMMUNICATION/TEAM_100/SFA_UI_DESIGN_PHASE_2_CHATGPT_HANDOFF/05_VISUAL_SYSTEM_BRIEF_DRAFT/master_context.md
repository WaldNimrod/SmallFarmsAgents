# Master Context — SFA Visual System (Phase 2 draft)

## What we are doing
Building a **large, coherent visual system** for SFA (חקלאות קטנה) — not a one-off
batch of 12 images. The system spans brand/OG art, module heroes, functional
icons, UI textures/backgrounds, empty states, and community illustrations.

## Two sources, two roles
- **Style source = nimrod.bio illustration line** ("מהגינה של נימרוד"). We
  **extend this existing line**; we do not invent a new style. Primary anchor:
  `ref_watercolor_radishes.jpg`. See `03_NIMROD_BIO_STYLE_ANCHORS/`.
- **Product source = live SFA at sfa.nimrod.bio** (`sfa_delivery/`). Defines
  what slots exist, sizes, RTL, palette tokens, and gaps. See `02_PRODUCT_UI_CONTEXT/`.

## The feeling (non-negotiable)
Delicate · pleasant · hinted/suggested (not literal-heavy) · calm · quiet ·
handmade. Warm cream paper, muted earthy palette, loose watercolor + warm
brown ink line, generous breathing room. A garden journal, not a brochure.

## Hard rules
- **No text, numbers, or logos inside any image** (HTML renders Hebrew over art).
- **No generic AI watercolor** (over-saturated, glossy, symmetrical, crisp-everywhere).
- **No repeated centered seedling/tomato/carrot lineups** — vary subjects, prefer
  loose single-subject or small clusters with empty space.
- Muted palette only (gj.css tokens). No neon, no high contrast, no 3D, no drop shadows.
- Match the paper tone + line quality + wash softness of the real references.

## Process (binding)
1. Collect/confirm references (style board).
2. **Generate the calibration set first (6–8)** and get Nimrod's approval on style.
3. Only then produce per-family at scale, in phases.
4. Approve PNG visually → scripted crop/resize/WebP per `C3` export recipe.
5. Version assets (candidates / approved / rejected).

## Scope (pending D01 — recommend full system, phased)
Phase 2a: brand/OG + 8 module heroes (the wired slots). Phase 2b: icon set +
favicon. Phase 2c: textures/backgrounds + empty states + community art.
