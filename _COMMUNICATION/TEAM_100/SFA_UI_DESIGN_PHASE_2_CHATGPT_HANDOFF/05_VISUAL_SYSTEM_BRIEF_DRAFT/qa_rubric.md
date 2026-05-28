# QA Rubric — every SFA asset must pass before approval

Score each asset against all criteria. Any FAIL on a hard rule = reject + regenerate.

## Hard rules (binary — any fail = reject)
- [ ] **No text / numbers / logos** rendered inside the image.
- [ ] **No generic AI watercolor** (over-saturated, glossy, perfectly symmetrical, every edge crisp).
- [ ] **No 3D, no drop shadows, no neon, no high-gloss gradients.**
- [ ] **Palette** within the muted gj.css range (paper/leaf/tomato/sun/soil/ink). No off-brand colors.
- [ ] **Safe crop:** key subject inside the safe margin for the target aspect (no critical detail at edges).
- [ ] **Export-ready:** generatable to the target dims + WebP budget per `C3` without quality loss.

## Quality scales (rate 1–5; ≥4 to approve)
- **Brand continuity:** looks like the same hand/paper as `ref_watercolor_radishes.jpg` (1=alien, 5=seamless).
- **UI usefulness:** works in its slot (legible at size, doesn't fight HTML text over it).
- **Cohesion:** belongs to the same set as the other approved assets.
- **Distinctiveness:** not a repeat of another asset's composition (avoid same-y lineups).
- **Calm/handmade feel:** delicate, hinted, quiet, imperfect — not loud or stocky.

## Per-family extra checks
- **Icons:** legible + recognizable at 24px and 16px; line-first.
- **Textures:** invisible behind content; no recognizable objects; edge-safe.
- **Heroes:** subject varies from sibling cards; one loose subject/cluster, not a lineup.
- **Empty states:** gentle/friendly, not sad; lots of space.

## Recording
For each asset log: filename, family, scores, pass/fail on hard rules, decision
(approved / candidate / rejected), and which anchor it was matched against.
