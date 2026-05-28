# SFA Media Studio — ChatGPT Project Package · MAPPING

Everything needed to stand up a ChatGPT **Project** and generate the 12 SFA media
assets, one chat session per asset. Prepared by team_100, 2026-05-28.

## How to use (3 steps)
1. **Create the Project** in ChatGPT. Set its **Description** from `00_PROJECT_DESCRIPTION.md`
   and its **Instructions** from `01_PROJECT_INSTRUCTIONS.md`.
2. **Upload the 4 context files** (`context/C1…C4`) to the Project's files/knowledge.
3. **Open one new chat per asset.** Paste the matching numbered prompt from
   `prompts/SESSION_NN_*.md`. Generate → export per `C3` → save to the named path.

## Folder map
```
MEDIA_CHATGPT_PROJECT/
├── README_MAPPING.md            ← this file (the מיפוי)
├── 00_PROJECT_DESCRIPTION.md    ← ChatGPT Project "Description"
├── 01_PROJECT_INSTRUCTIONS.md   ← ChatGPT Project "Instructions" (applies to all chats)
├── context/                     ← upload all 4 to Project knowledge
│   ├── C1_BRAND_AND_PRODUCT.md  ← what SFA is, audience, modules, personality
│   ├── C2_DESIGN_SYSTEM.md      ← palette (hex), type, style language, don'ts
│   ├── C3_ASSET_SPEC_TABLE.md   ← 12 assets: paths, dims, budgets + export recipe
│   └── C4_ICON_VOCABULARY.md    ← subject anchors per module + brand mark
└── prompts/                     ← one numbered prompt per session
    ├── SESSION_01_og-default.md       (P0 · STYLE ANCHOR — do first)
    ├── SESSION_02_hero_crop-book.md   (P1)
    ├── SESSION_03_hero_market.md      (P1)
    ├── SESSION_04_hero_calc.md        (P1)
    ├── SESSION_05_hero_planner.md     (P1)
    ├── SESSION_06_hero_clients.md     (P1)
    ├── SESSION_07_hero_inventory.md   (P1)
    ├── SESSION_08_hero_tend-bridge.md (P1)
    ├── SESSION_09_hero_field-log.md   (P1)
    ├── SESSION_10_hub-hero.md         (P2 · optional)
    ├── SESSION_11_contact.md          (P2 · optional)
    └── SESSION_12_favicon.md          (P2 · optional)
```

## Session → output map
| # | Session | Output file (under `sfa_delivery/public_assets/img/`) | Dims | Priority |
|---|---------|------------------------------------------------------|------|----------|
| 01 | og-default | `og-default.webp` | 1200×630 | **P0** |
| 02 | hero crop-book | `heroes/crop-book.webp` | 800×800 | P1 |
| 03 | hero market | `heroes/market.webp` | 800×800 | P1 |
| 04 | hero calc | `heroes/calc.webp` | 800×800 | P1 |
| 05 | hero planner | `heroes/planner.webp` | 800×800 | P1 |
| 06 | hero clients | `heroes/clients.webp` | 800×800 | P1 |
| 07 | hero inventory | `heroes/inventory.webp` | 800×800 | P1 |
| 08 | hero tend-bridge | `heroes/tend-bridge.webp` | 800×800 | P1 |
| 09 | hero field-log | `heroes/field-log.webp` | 800×800 | P1 |
| 10 | hub hero | `hub-hero.webp` | 1600×900 | P2 |
| 11 | contact | `contact.webp` | 1600×900 | P2 |
| 12 | favicon | `favicon.ico` + `favicon-32.png` + `apple-touch-icon.png` | — | P2 |

## Recommended order
01 (anchor) → 02–09 (the card set, generate back-to-back for consistency) →
10–12 (optional). After P0/P1 land: notify team_100 → wire `modules.php hero_url`
+ bundled deploy + L-GATE_V re-validation (WP-UI-patch01 deferred sub-items).

## Notes
- ChatGPT image gen outputs PNG at fixed canvases and won't hit exact hex or WebP —
  the **export recipe in C3** (sips + cwebp) converts to the final spec. This is a
  manual post-step outside ChatGPT.
- Keeping all 12 in one Project (shared Instructions + knowledge) is what holds the
  set visually consistent. Treat SESSION_01 as the look to match.
