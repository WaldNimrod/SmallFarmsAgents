# COMPLETION REPORT — wc-tomato / wc-cucumber watercolor masters

> **WP:** SFA-S003-P004-WP-CB-1 (Crop Book v1) · **To:** team_00 (Principal)
> **From:** build session (Claude Code) · **Date:** 2026-06-01 · **Status:** `READY_PENDING_ART`

## Objective
Replace the emoji glyph fallback (עגבנייה 🍅 / מלפפון 🥒) on the two crops that lack a
watercolor master, by producing `wc-tomato.png` + `wc-cucumber.png` in the existing Devora
hand and wiring them into the crop-card and crop-hero render.

## Status summary
| Deliverable | State |
|---|---|
| ImagePrompt brief (style-locked, copy-paste) | ✅ DONE |
| 720px derivative pipeline (verified recipe) | ✅ DONE (staged) |
| Exact code wiring identified (2 lines, 2 files) | ✅ DONE (held) |
| `wc-tomato.png` / `wc-cucumber.png` masters | ⏳ WITH team_00 — pixel generation |
| Derivatives built + wiring applied + visual check | ⏳ BLOCKED on masters |

**Decision (team_00, this session):** art source = "I'll generate, you wire" — Principal
runs the two prompts in the image session; build side handles derivatives + wiring on drop.

## What was delivered
1. **ImagePrompt brief** — `…/HANDOFF_PACKAGE/design/assets/IMAGEPROMPT_wc-tomato-cucumber_v1.0.0.md`.
   Two prompts built from the binding style SSoT (`PROMPT_SERIES_v1.md` §Standing rules) and
   COMPONENTS.md §15. Enforces the brand rule **tomato = tan-red `#c46a3e`, no bright red**,
   cream paper `#f5f3ec`, loose semi-abstract single subject, PNG+alpha, ~2200px, plus a QA
   acceptance check (reads as same hand as `wc-radish.png`; composites cleanly under
   `mix-blend-mode: multiply`).
2. **Derivative pipeline** — `scripts/wc_derivatives.sh`. Recipe `sips -Z 720` (long-edge,
   alpha preserved) — verified to reproduce the shipped `wc-radish.png` derivative
   **byte-for-byte** (326,591 B). No magick/pngquant dependency. Run:
   `scripts/wc_derivatives.sh tomato cucumber`.
3. **Wiring (held, not yet applied — would 404 until masters exist):**
   - `sfa_delivery/app/Controllers/CropBookViewController.php:175` — `WC_ART` const (crop hero)
   - `sfa_delivery/templates/pages/book_entry.php:79` — `$wc_art_map` (crop cards grid)
   - Both: add `'tomato' => 'wc-tomato.png'` and `'cucumber' => 'wc-cucumber.png'`.
   Slugs `tomato` / `cucumber` are already resolved by the controller (`ICON_MAP`).

## Why not fully closed
Watercolor botanical art cannot be produced with code (only resize/encode tooling — `sips`,
`cwebp` — is present; no image-generation tool in this harness). This matches the WP's own
note that the masters require an image-generation pipeline or team_35/Devora. Per the team_00
decision above, pixel generation sits with the Principal; everything downstream is staged.

## Hand-back trigger (closes the WP slice)
1. team_00 saves `wc-tomato.png` + `wc-cucumber.png` (PNG+alpha, ~2200px) into
   `…/HANDOFF_PACKAGE/design/assets/`.
2. Build side runs `scripts/wc_derivatives.sh tomato cucumber`, applies the 2-line wiring,
   and visually confirms both crops drop the glyph and composite cleanly under multiply.
3. Mark this report `DONE`.

## Files touched
- `_COMMUNICATION/team_35/SFA-S003-P004-WP-CB-1/HANDOFF_PACKAGE/design/assets/IMAGEPROMPT_wc-tomato-cucumber_v1.0.0.md` (new)
- `scripts/wc_derivatives.sh` (new, +x)
- `_COMMUNICATION/TEAM_100/SFA-S003-P004-WP-CB-1/COMPLETION_REPORT_wc-tomato-cucumber_2026-06-01_v1.0.0.md` (this report)
