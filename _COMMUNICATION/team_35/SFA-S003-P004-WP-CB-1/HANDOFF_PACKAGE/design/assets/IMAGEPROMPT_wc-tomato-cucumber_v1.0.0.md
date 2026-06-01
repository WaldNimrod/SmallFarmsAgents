# ImagePrompt brief — wc-tomato · wc-cucumber (Crop Book v1)

> **WP:** SFA-S003-P004-WP-CB-1 · **For:** the two crop masters still on glyph fallback
> (עגבנייה 🍅 / מלפפון 🥒). Produces `wc-tomato.png` + `wc-cucumber.png` to sit
> beside the existing four (`wc-lettuce/radish/parsley/dill`).
> **Style SSoT:** `_COMMUNICATION/TEAM_100/NIMROD_BIO_VISUAL_SYSTEM_CHATGPT/prompts/PROMPT_SERIES_v1.md`
> **Slot contract:** COMPONENTS.md §15 (ImagePrompt) — placeholder → real `<img>` once sourced.

## Standing rules (apply to BOTH — from PROMPT_SERIES_v1 §Standing rules)
- **Attach the Devora reference images** to the session — **radishes.png primary**, plus
  lettuce / dill / parsley. The two new masters MUST read as the same hand.
- **Real watercolor only:** washed stains, feathered/undefined edges, visible transparent
  layers, pigment granulation, faint pencil under-drawing, on cream paper `#f5f3ec` with
  paper grain. NOT digital, NOT flat, NOT glossy, NOT symmetrical, no clean vector outline.
- **Palette:** olive `#6a8a3a`, earth `#5b483a`, **tan-orange `#c46a3e`**, dusty teal
  `#2d8a8c` (sparingly), cream `#f5f3ec`. **⚠ No bright red** — the tomato is **tan-red
  `#c46a3e`**, never a saturated red. This is a binding brand rule.
- **No text, numbers, logos** in the image. One loose subject/cluster, off-center, quiet
  empty paper around it (the card crops to ~78%, the hero to a 96px box).
- Ground: the existing four masters ship **PNG with alpha** on near-cream; they display via
  `mix-blend-mode: multiply` on near-white. Paint on cream `#f5f3ec` — a transparent OR
  near-cream ground both composite correctly under multiply.

---

## Prompt — wc-tomato (עגבנייה) · ~2048×2048, export PNG
```
Real watercolor study of a small cluster of two or three ripe garden tomatoes on the
vine with a leafy green stem and a star calyx, on cream paper (#f5f3ec). Washed
tan-red / tan-orange pigment (#c46a3e) for the fruit and olive-green (#6a8a3a) for
the leaves and stem, warm brown (#5b483a) faint hand-drawn line, undefined feathered
edges, visible paper texture and pigment pooling, a faint pencil under-drawing showing.
Loose, gentle, semi-abstract, off-center with quiet empty paper around it. Hand-painted,
slightly imperfect. NO text, no outline-clean vector, no digital gradient, no glossy
look, NO BRIGHT RED — keep the tomatoes tan-red #c46a3e. Match the wash, palette, paper
texture and pencil/ink line of the attached reference images — especially radishes.png.
Same hand, same paper.
```

## Prompt — wc-cucumber (מלפפון) · ~2048×2048, export PNG
```
Real watercolor study of one or two slender garden cucumbers with a curling vine
tendril, a broad lobed leaf and a small yellow blossom, on cream paper (#f5f3ec).
Washed olive and deeper green pigment (#6a8a3a) with cool shadow, a touch of dusty
teal (#2d8a8c) sparingly, warm brown (#5b483a) faint hand-drawn line, undefined
feathered edges, visible paper texture and pigment pooling, a faint pencil
under-drawing showing. Loose, gentle, semi-abstract, off-center with quiet empty
paper around it. Hand-painted, slightly imperfect. NO text, no outline-clean vector,
no digital gradient, no glossy look. Match the wash, palette, paper texture and
pencil/ink line of the attached reference images — especially radishes.png and the
leafy lettuce/dill masters. Same hand, same paper.
```

---

## Export spec (match the existing four)
- **Master:** PNG, **alpha preserved**, **~2200px long edge** (existing masters range
  1476–2200px). Save full-res to **this folder**:
  `…/HANDOFF_PACKAGE/design/assets/wc-tomato.png` and `…/wc-cucumber.png`.
- **720px derivative + wiring:** handled by the build side — run
  `scripts/wc_derivatives.sh` (added with this brief), then the two-line code wiring lands.

## QA acceptance (before handing back to build)
1. Reads as the **same hand** as `wc-radish.png` side-by-side (wash, line, paper grain).
2. Tomato is **tan-red `#c46a3e`**, not saturated red.
3. No text / logo / hard vector edge / glossy sheen.
4. One off-center subject with quiet paper — composites cleanly under `mix-blend-mode: multiply`
   on `#fbfaf7` (drop it on a near-white div to check — no grey box, no hard rectangle).
