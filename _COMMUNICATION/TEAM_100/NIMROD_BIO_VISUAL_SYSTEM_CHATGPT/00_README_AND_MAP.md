# nimrod.bio Visual System — unified ChatGPT Project (Stage 6)

Prepared by team_100, 2026-05-28. A **new, consolidated** ChatGPT design project that
supersedes the earlier SFA-only media package. It is anchored on the **locked
nimrod.bio AOS Design System (v3.4)** and covers the brand's **Stage 6** visual art:
logo family + watercolor illustration system — across the whole brand, with **SFA as
one application** (the דיגיטל world's flagship, P-07).

## Why new (not patch the old)
The old `MEDIA_CHATGPT_PROJECT` was built only from SFA's `gj.css` + 4 web images.
We then found the **authoritative master brand system** (locked v3.4: taxonomy,
voice, palette, typography, system.css + ready watercolor/logo prompts) AND the
**original designer (Devora) source masters** (6 watercolor PSDs + vector logos +
Carmela font). A unified project anchored on those is the correct foundation; the
old SFA media set becomes a scoped subset inside it.

## What nimrod.bio is (one paragraph)
נימרוד ולד — one root, three worlds: **אדמה** (Soil — produce, hydroponic
greenhouse, BCS, nursery) · **ידע / "ייעוץ והוראה"** (Know — consulting + teaching)
· **דיגיטל / מיזו** (Code — **SFA** free community AI for small farming, tiktrack,
greenhouse co-op). The brand's uniqueness is **the bridges between worlds.** Moto:
"שורש אחד, שלוש זרועות" · tagline "העולם הוא כזה — אלא אם כן (Unless)."

## Folder map
| Path | Purpose |
|------|---------|
| `01_PROJECT_DESCRIPTION.md` | ChatGPT Project "Description" |
| `02_PROJECT_INSTRUCTIONS.md` | ChatGPT Project "Instructions" |
| `03_UPLOAD_ORDER.md` | exact upload sequence (which files + images) |
| `context/C1_BRAND_MASTER.md` | brand, 3 worlds, SFA's place, master palette, voice |
| `context/C2_VISUAL_DNA.md` | watercolor+ink line, Devora masters, do/don't |
| `context/C3_ASSET_SYSTEM.md` | brand-wide asset families + formats |
| `context/C4_SOURCE_INDEX.md` | pointer map to every authoritative source file in the repo |
| `context/C5_PROMPTING_RULES.md` | how to prompt; reuse the locked prompts; calibration-first |
| `prompts/README_PROMPTS.md` | the canonical prompt set (locked brand prompts + SFA application) |
| `DECISIONS_APPLIED.md` | D01–D10 rulings + revised sequence + calibration + QA |

## Authoritative sources already in the repo (do not duplicate — reference)
- **Master brand system (LOCKED):** `…/SFA_UI_DESIGN_PHASE_2_CHATGPT_HANDOFF/03_NIMROD_BIO_STYLE_ANCHORS/brand_system/nimrod_bio_AOS_design_system/` — `brand/voice.md`, `brand/TAXONOMY-v3.4-LOCKED.md`, `brand/typography.md`, `brand/system.css`, `01-PROMPT-watercolor-backgrounds.md`, `02-PROMPT-logo-family.md`.
- **SFA team_35 design:** `…/brand_system/sfa_team35_handoff/` (COMPONENTS/DESIGN_TOKENS/TEMPLATES + design CSS/JSX + art-prompts.jsx + MODULES_REGISTRY.yaml).
- **Devora source masters:** `…/03_NIMROD_BIO_STYLE_ANCHORS/source_masters/` (6 watercolor PSD→PNG, vector logos, Carmela font, MANIFEST).
- **SFA application context + screenshots:** `…/02_PRODUCT_UI_CONTEXT/`.
- **Decisions:** `_COMMUNICATION/team_00/DECISION_SFA_VISUAL_SYSTEM_2026-05-28_v1.md`.

## Process (binding)
Calibration-first (D04). Build the reference style board (D03=C) from the Devora
masters + the locked prompts, run a 6-image calibration set, get approval, then
produce families in phases. No mass generation before approval.
