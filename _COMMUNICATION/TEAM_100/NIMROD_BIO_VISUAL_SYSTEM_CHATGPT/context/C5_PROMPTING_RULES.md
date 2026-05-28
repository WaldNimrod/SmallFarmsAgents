# C5 — Prompting Rules

## Reuse the locked prompts (don't reinvent)
- Worlds heroes → use `01-PROMPT-watercolor-backgrounds.md` (5 ready prompts with
  palette, quiet-zone, format specs).
- Logo family → use `02-PROMPT-logo-family.md`.
For SFA module heroes / icons / OG / favicon / textures / empty states, write new
prompts using the skeleton below — but the treatment + palette stay identical.

## Prompt skeleton (per asset)
1. Canvas: "Square 1024×1024" or "Landscape 1792×1024" (per target).
2. Subject: one loose subject/cluster (vary across siblings; partial/cropped is good).
3. Treatment (always): "real watercolor, washed stains, undefined feathered edges,
   visible transparent layers, pigment granulation, on cream paper #f5f3ec with
   visible paper texture — NOT digital, NOT flat, NOT glossy."
4. Composition: "off-center, ~30% quiet paper zone for text, calm, semi-abstract."
5. Match line (always): "Match the wash, palette, paper texture, and pencil/ink line
   of the attached Devora reference images — especially radishes.png. Same hand."
6. Negatives (always): "no text/numbers/logos; no photo; no 3D; no drop shadows; no
   bright red; not digital-clean; not symmetrical; no commercial watercolor-brush look."

## Palette in prompts
olive `#6a8a3a`, earth `#5b483a`, tan-orange `#c46a3e`, dusty teal `#2d8a8c`
(sparingly), on `#f5f3ec`. Never bright spark red in art.

## Process
- **Calibration set first** (see DECISIONS_APPLIED) → human approval → then families.
- Attach the Devora masters to every session.
- Export per C3; score against the QA rubric (`PKG/05_…/qa_rubric.md`) before approving.
- Versioned output (candidates/approved/rejected).
