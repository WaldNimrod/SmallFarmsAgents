# SFA Visual System — Phase 2 ChatGPT Handoff

Prepared by team_100, 2026-05-28. A complete source-and-context package so the
next ChatGPT design sessions can build a coherent **large-scale SFA visual
system** (icons, backgrounds, module heroes, OG, textures, empty states,
illustrations) — by **continuing the existing nimrod.bio illustration line**.

## What this folder contains
| Folder | Contents |
|--------|----------|
| `01_SOURCE_INVENTORY.md` | Every source file/folder inspected + where it landed here |
| `02_PRODUCT_UI_CONTEXT/` | The live SFA product source: modules, asset slots, Hebrew labels, **12 current UI screenshots** |
| `03_NIMROD_BIO_STYLE_ANCHORS/` | The style source: **4 real illustration images** + style-DNA analysis |
| `04_EXISTING_SFA_MEDIA_PACKAGE/` | The prior v1 media package (verbatim) + an audit of what to keep/rework |
| `05_VISUAL_SYSTEM_BRIEF_DRAFT/` | master context, asset families, calibration set, QA rubric |
| `06_DECISIONS_FOR_NIMROD/` | 10 decisions (table + Hebrew) with recommendations |
| `07_READY_TO_UPLOAD_TO_CHATGPT/` | Clean, final files to paste/upload into the ChatGPT Project |

## Source areas inspected
- `sfa_delivery/` (live SFA app): `_layout.php`, `templates/shell/*`, `macros/*`, `modules.php`, `public_assets/img/icons.svg`, `gj.css`/`hub.css`.
- nimrod.bio live site + WP media library (REST) — illustration hunt.
- The prior `_COMMUNICATION/TEAM_100/MEDIA_CHATGPT_PROJECT/` package.
- `visual_diff/` — reused current SFA UI screenshots from the WP-UI build.

## What is READY to upload to ChatGPT
The 8 files in `07_READY_TO_UPLOAD_TO_CHATGPT/` (description, instructions, C1–C5
context, upload-order) **+ the 4 images** in `03_.../images/`. Follow
`07/README_UPLOAD_ORDER.md`.

## What still needs Nimrod's decisions
The 10 decisions in `06_DECISIONS_FOR_NIMROD/` — most critical: **D02** (nimrod.bio
as primary style anchor) and **D03** (how many references; only ~4 genuine pieces exist).

## What should NOT be generated yet
Nothing should be mass-produced. **Generate the calibration set (6–8) first**,
get style approval, then produce family by family. No images were generated in
preparing this package.

## Key finding / risk
The genuine nimrod.bio illustration line is **small** (~4 real pieces; the rest of
the site is photos). Either anchor hard on these 4, or commission more before scale.
