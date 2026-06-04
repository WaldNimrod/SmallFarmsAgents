# Request to the Gemini image session — hand back the crop-icon "recipe" for API continuation

**Purpose:** you (the Gemini session) painted our SFA crop-book watercolor masters (the "Devora" series — `wc-radish/lettuce/dill/parsley/tomato/cucumber/…`) from our brief. We're now generating the **next 43 crop icons via the Gemini API** (`gemini-2.5-flash-image`) and need your **exact working recipe** so the new batch reads as the **same hand**. Please reply with the structured spec below — verbatim, copy-pasteable, API-ready.

---

## Paste this into the Gemini session:

> You earlier generated our SFA crop-book watercolor icons (the Devora series) — washed watercolor crops on cream paper, e.g. `wc-radish`, `wc-lettuce`, `wc-dill`, `wc-parsley`, `wc-tomato`, `wc-cucumber`. We're continuing the **exact same series** for 43 more crops, but driving it through the **Gemini API** (`gemini-2.5-flash-image`) instead of an interactive chat. To keep every new icon the same hand, give me your **complete final recipe** in the structured form below. Be exact — I will hardcode this into API calls.
>
> **1. PROMPT TEMPLATE** — the exact, final prompt text you converged on, with a single `{SUBJECT}` slot where the crop description goes. Include every style phrase (paper, palette, edges, line, granulation, composition, "no bright red", negatives). The version that actually worked, not the first draft.
>
> **2. PER-CROP {SUBJECT} LINES** — one short botanical subject phrase per crop, in the series' voice (loose, off-center, hand-painted), for each of these 43 slugs. Keep them in the same descriptive register as your tomato/cucumber/radish subjects:
> `anise-hyssop, artichokes, arugula, bay, beans-default-pole-climbing, blackberry, cauliflower, celery, chickpea, chicory, chinese-lantern, chives, cilantro, cress, edamame, fava-bean, hibiscus, jerusalem-artichokes, jicama, kohlrabi, lemon-balm, lemon-verbena, lettuce-salad-mix, lovage, mint, new-zealand-spinach, okra, oranges, pac-choi-bok-choy, potato, sage, sesame, soybean, strawberry, sunflower, sweet-corn, sweet-potato, tarragon, thyme, turnips, watermelon, wheat, winter-squash`
>
> **3. STYLE BLOCK (verbatim)** — palette hexes (olive #6a8a3a, earth #5b483a, tan-orange #c46a3e, dusty teal #2d8a8c, cream #f5f3ec — confirm/correct), paper, edge treatment, pencil under-drawing, granulation, lighting, and the **NEGATIVE list** (no text/logos/3D/glossy/digital-flat/hard-vector/bright-red/symmetry/drop-shadow). Note any phrasing that *failed* and should be avoided.
>
> **4. REFERENCE IMAGES** — exactly which images you attach for style-matching, which is **primary** (radishes?), and how many you attach per generation. For the API I attach images as inline data — tell me the minimal set that reliably holds the style (e.g. radish + lettuce + dill).
>
> **5. GENERATION SETTINGS** — aspect ratio (square 1:1?), output resolution, any temperature / "be faithful to reference" guidance, and the **exact model id** you used. Anything I should set in `generationConfig`.
>
> **6. OUTPUT / FRAMING** — confirm: one off-center subject, quiet empty paper (the card crops to ~78%), PNG with **alpha** (or near-cream ground that composites under `mix-blend-mode: multiply` on near-white), ~2048–2200px long edge. Flag anything that breaks the multiply composite (grey box / hard rectangle).
>
> **7. ACCEPTANCE TEST** — your one-line "same hand" check (reads beside `wc-radish.png`: wash, line, paper grain; no bright red; composites clean).
>
> Return all 7 as plain text/markdown I can paste straight into code. If any crop needs a special note (e.g. show whole vs cut, fruit vs plant), include it inline in its {SUBJECT} line.

---

## What we already have on file (give this to the session if it asks for the basis)
- **Style SSoT:** `_COMMUNICATION/TEAM_100/NIMROD_BIO_VISUAL_SYSTEM_CHATGPT/prompts/PROMPT_SERIES_v1.md` (Standing rules + the radish prompt).
- **Crop-icon brief:** `…/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/assets/IMAGEPROMPT_wc-tomato-cucumber_v1.0.0.md`.
- **Reference masters (attach these):** `…/HANDOFF_PACKAGE/design/assets/wc-radish.png` (primary) + `wc-lettuce.png` + `wc-dill.png` + `wc-parsley.png`.
- **Known binding rules:** cream paper `#f5f3ec`; palette olive/earth/tan-orange/dusty-teal; **NO bright red** (tomato = tan-red `#c46a3e`); no text/logo/vector/glossy; off-center with quiet paper; PNG alpha; composites under `mix-blend-mode: multiply`.

## On receipt
team_100 folds the returned recipe into `scripts/gen_crop_icons.mjs` (the API generator) — prompt template + per-crop subjects + the radish-primary reference set — runs the batch, reviews each vs `wc-radish.png`, promotes to `masters/`, runs `wc_derivatives.sh`, wires the slugs, and CDP-verifies on the crop-book grid.
