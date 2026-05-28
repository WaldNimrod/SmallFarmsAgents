# Prompt Set — canonical sources

The prompt set for this project is **assembled from existing locked prompts + new
application prompts**, not rewritten from scratch.

## Canonical (reuse as-is)
| Family | Prompt source (in repo) |
|--------|-------------------------|
| Worlds hero backgrounds (×5: Soil/Know/Code/Home/About) | `…/brand_system/nimrod_bio_AOS_design_system/01-PROMPT-watercolor-backgrounds.md` |
| Logo family (primary + 3 worlds + basket set) | `…/brand_system/nimrod_bio_AOS_design_system/02-PROMPT-logo-family.md` |
| SFA art catalog (per-module intent, Hebrew) | `…/brand_system/sfa_team35_handoff/design/art-prompts.jsx` + `…/02_PRODUCT_UI_CONTEXT/extracted_text/module_definitions.md` |

## New application prompts (write with the C5 skeleton)
- SFA module heroes ×8 (800×800) — subjects in `module_definitions.md`.
- OG/share (1200×630), favicon (from basket/seedling mark), icons (line+wash),
  textures, empty states.
- Draft stubs already exist (technical specs only, NOT art direction) at
  `…/04_EXISTING_SFA_MEDIA_PACKAGE/original_docs/prompts/SESSION_*.md` — use for
  sizes/paths; rewrite the art body per C2/C5 + the Devora anchors.

## Order = calibration first
Do not generate everything. Run the calibration set (DECISIONS_APPLIED) → approve →
then families in phase order: logo family → worlds heroes → SFA heroes → icons →
OG/favicon → textures/empty states.
