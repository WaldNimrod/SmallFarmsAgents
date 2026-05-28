# STYLE UPDATE — message to the media-generation team/session

> Hand this to whoever runs the ChatGPT Media Studio sessions. It updates the
> brief: the new SFA assets must **continue the existing nimrod.bio illustration
> line**, not invent a fresh style. Three real reference files are now in the
> project (`context/reference_existing/`).

---

**Update — anchor every image to the existing nimrod.bio illustrations.**

We are NOT designing a new look. We are extending the illustration line that
already accompanies the nimrod.bio brand ("מהגינה של נימרוד"). Before generating,
open the three reference files added to the project:

1. `ref_watercolor_radishes.jpg` — **the primary anchor.** Soft watercolor
   radishes/beets on cream paper with a light pencil/ink outline. Match this
   exact treatment: loose pigment washes, visible paper grain, muted beet-red +
   olive-green, gentle imperfect edges.
2. `ref_brand_logo_basket.png` — the brand's vegetable basket: soft color fills
   with warm brown ink linework. Use it for the palette + the line-and-fill feel.
3. `ref_lineart_basket.png` — the confident hand-drawn outline underneath.

**Apply to every session prompt:** keep your existing per-session subject + canvas
+ export spec, but append this line to the prompt before generating —

> "Match the watercolor treatment, muted earthy palette, cream-paper texture, and
> hand-drawn pencil/ink line quality of the attached reference images — especially
> ref_watercolor_radishes.jpg. Same hand, same paper, same restraint. Hand-painted
> and slightly imperfect, never digital-clean, never glossy, no text."

**Consistency bar:** lay each new asset next to `ref_watercolor_radishes.jpg`. If
it looks more polished/digital/saturated than the reference, regenerate softer.
The brand is calm and handmade.

**Unchanged:** filenames, dimensions, byte budgets, and the export recipe in
`context/C3_ASSET_SPEC_TABLE.md`. Session order unchanged (01 og-default is still
the in-set style anchor; the nimrod.bio references are the *brand* anchor above it).
