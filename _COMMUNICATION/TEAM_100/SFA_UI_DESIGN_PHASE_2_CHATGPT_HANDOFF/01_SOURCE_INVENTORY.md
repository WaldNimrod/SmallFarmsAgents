# Source Inventory

| Source path | Type | Relevance | Copied? | Handoff destination | Notes | Confidence |
|-------------|------|-----------|---------|---------------------|-------|------------|
| nimrod.bio `/uploads/2019/07/selejk.jpg` | JPG (watercolor) | **PRIMARY style anchor** | Yes | `03_.../images/ref_watercolor_radishes.jpg` | radishes/beets watercolor | High |
| nimrod.bio `/uploads/2019/07/logo.png` | PNG (illustration+text) | Brand basket + palette | Yes | `03_.../images/ref_brand_logo_basket.png` | wordmark present (ignore text) | High |
| nimrod.bio `/uploads/2019/07/bucket.png` | PNG (line-art) | Line/icon style | Yes | `03_.../images/ref_lineart_basket.png` | grey line basket | High |
| nimrod.bio `/uploads/2019/07/סל-…jpeg` | JPG (composite flyer) | Usage + greens study | Yes | `03_.../images/ref_usage_basket_flyer.jpg` | "מה בסל היום?"; has text | High |
| nimrod.bio `/uploads/2021/01/figure-blueberry.jpg` | JPG (photo) | Not illustration | No | — | photo — excluded | High |
| nimrod.bio `/uploads/2019/07/אינטרו-08.jpg` | JPG (photo) | Not illustration | No | — | photo of Nimrod w/ carrots | High |
| nimrod.bio `/uploads/2019/04/הסל-כולל.png` | PNG (text infographic) | Not illustration | No | — | text box, not art | High |
| nimrod.bio WP media library (REST) | mixed | Illustration hunt | Partial | — | mostly photos/articles; only the 4 above are line assets | Medium |
| `sfa_delivery/modules.php` | PHP | Module defs + Hebrew + thumb_prompts | Extracted | `02_.../extracted_text/module_definitions.md` | 8 modules + intent prompts | High |
| `sfa_delivery/public_assets/css/gj.css` | CSS | Palette + type tokens | Extracted | `02_.../extracted_text/` + C1/C2 | live design tokens | High |
| `sfa_delivery/public_assets/css/hub.css` | CSS | Card/art slot rules | Extracted | `02_.../current_asset_slots.md` | hero/icon/contact slots | High |
| `sfa_delivery/templates/_layout.php` | PHP | og:image + favicon refs | Extracted | `02_.../current_asset_slots.md` | og-default ref | High |
| `sfa_delivery/templates/shell|macros/*` | PHP | Slots, RTL, structure | Inspected | `02_.../current_asset_slots.md` | hero/feed/card macros | High |
| `sfa_delivery/public_assets/img/icons.svg` | SVG | Existing icon set | Referenced | `02_.../current_asset_slots.md` | icon style anchor | High |
| `visual_diff/{desktop,mobile}__*.png` | PNG | Current SFA UI screenshots | Yes (12) | `02_.../screenshots/` | reused WP-UI build captures | High |
| `_COMMUNICATION/TEAM_100/MEDIA_CHATGPT_PROJECT/**` | MD + imgs | Prior v1 media package | Yes (verbatim) | `04_.../original_docs/` | audited in `04/audit_notes.md` | High |

## Not copied (left in place, untouched)
Original `MEDIA_CHATGPT_PROJECT/` (source of truth for v1) — only **copied**, never
modified or deleted. nimrod.bio photos — referenced by URL only, not downloaded
into the handoff. No source materials were altered or removed.
