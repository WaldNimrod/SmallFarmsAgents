# Module Definitions + Hebrew Labels (from sfa_delivery/modules.php)

The 8 modules rendered as cards on the SFA hub. `id` = slug = hero filename stem.
`color` drives the tier palette. `icon` references `icons.svg`. `thumb_prompt`
keys hold the original Hebrew design-intent prompts (watercolor, 1:1).

| # | id (slug) | name_he | tier | color | icon | stat_he | route |
|---|-----------|---------|------|-------|------|---------|-------|
| 1 | crop-book | ספר גידולים | open | leaf | lettuce | 66 גידולים · 242 זנים | /crop-book/ |
| 2 | market | מחירון | open | tomato | tomato | 30 מוצרים · 14 מקורות | /market/ |
| 3 | calc | מחשבון לחקלאי | beta | sun | carrot | גרסת בטא · בפיתוח | /calc/ |
| 4 | planner | תכנון עונה | coming | leaf | basil | בקרוב | /planner/ |
| 5 | clients | ניהול לקוחות | paid | soil | cucumber | כלים מתקדמים | /clients/ |
| 6 | inventory | מעקב יבול ומלאי | paid | tomato | strawberry | כלים מתקדמים | /inventory/ |
| 7 | tend-bridge | חיבור Tend / חשבונית-ירוקה | custom | soil | pepper | לפי הזמנה | /integrations/tend/ |
| 8 | field-log | יומן שדה | custom | leaf | onion | לפי הזמנה | /field-log/ |

## Original Hebrew design-intent prompts (modules.php::thumb_prompts)
These pre-existed in the codebase and describe the intended watercolor thumbnails.
They are consistent with the nimrod.bio line and should inform (not override) the
new visual DNA.

- **module_hub** (16:9): מבט מלמעלה על שולחן עבודה של חקלאי-מתכנן — מפת ערוגות צבועה ביד, סרגל, פרוסות תפוז, גזיר עיתון, צרור מרווה. אווירת "סדנת מחקר ביתית". פלטה: קרם דהוי, ירוק זית, חמרה-טראקוטה, צל-כחול. ללא טקסט.
- **contact** (16:9): שני אנשים על ספסל-עץ מול חממה קטנה, שיחה ידידותית. פלטה אדמה-ירוק-חמאה. ללא טקסט.
- **module_thumb_book/market/calc/plan/clients/inv/tend/field** (1:1): small watercolor studies per module (greens bunch / carrots on a crate / spiral notebook / planting calendar / coffee+ledger / harvest crate / hand-drawn ledger+pump / hoe+trowel on soil).

## Palette tokens (gj.css) — the product's live colors
paper `#f6f1e3` / `#ece5d2` / `#ddd2b2`; ink `#2a2418`, ink-soft `#776a4d`,
line `#d8ccae`; leaf `#6f8a45` (deep `#4d6a2c`, soft `#9bb172`); tomato `#c24f2c`
(deep `#8e3018`); sun `#d39a32`; soil `#8b5d2f` (deep `#5a3c1a`).
Fonts: Frank Ruhl Libre (head), Assistant/Heebo (body). RTL.
