---
id: MEDIA_COMPLETION_MAP_SFA-S003-P002-WP-UI-patch02_v1.0.0
from: team_100 (Chief Architect)
date: 2026-05-29
type: gap_analysis
wp: SFA-S003-P002-WP-UI-patch02 (Media Integration Completion)
source: oma-postgres crops (70 rows) + sfa_delivery/public_assets/img/icons.svg + design handoff dirs
---

# Media Completion Map — what exists, what's deployed, what's missing

## 1. Brand / module media
| Asset | Generated? | Wired on main? | Deployed? | Gap |
|-------|-----------|----------------|-----------|-----|
| 8 module heroes (crop-book, market, calc, planner, clients, inventory, tend-bridge, field-log) | ✅ watercolor candidates (branch claude/sfa-ui-patch01) | ❌ modules.php has 0 hero_url refs on main | ❌ | merge branch → main, wire modules.php, deploy |
| hub-home hero | ✅ candidate (hub-hero) | ❌ | ❌ | wire + deploy |
| og-default (1200×630) | ✅ candidate | ❌ (placeholder ref in _layout) | ❌ | place webp + deploy |
| favicon (favicon-180) | ✅ candidate | ❌ | ❌ | place + deploy |
| pending team_190 L-GATE_V R2 (media re-check) | mandate filed on branch | — | — | run non-Claude R2 after merge |

## 2. Per-crop icons — the big gap (70 crops)
**Current SVG sprite (`icons.svg`) = 10 symbols**: generic `icon-leaf`, `icon-seedling`
+ 8 dedicated: tomato, lettuce, cucumber, pepper, eggplant, carrot, onion, zucchini.

**Decision: watercolor raster per crop (all 70).** SVG sprite stays as fallback
when `crops.icon_url` is null.

| category | crops | have dedicated SVG today | need watercolor art |
|----------|------:|-------------------------:|--------------------:|
| vegetables | 48 | 8 (tomato, lettuce, cucumber, pepper, eggplant, carrot, onion, zucchini) | 48 |
| herbs | 16 | 0 | 16 |
| fruits | 4 | 0 (cherry-tomato can reuse icon-tomato as fallback) | 4 |
| fruit_trees | 2 | 0 | 2 |
| **total** | **70** | **8** | **70** |

### Dedicated-SVG crops (8) — get a watercolor upgrade for consistency
Tomatoes(49), Lettuce(30), Cucumbers(17), Peppers(41), Eggplant(19), Carrots(10),
Onions(56), Summer Squash(46). (Cherry Tomato 73, Salad Mix 31, Scallions 36 currently share via fallback.)

### Crops with NO dedicated icon today (62) — fallback to generic leaf/seedling
herbs(16): Anise Hyssop, Basil, Chives, Cilantro, Dill, Hibiscus, Lemon Balm,
Lemon Verbena, Lovage, Mint, Parsley, Sage, Sesame, Tarragon, Thyme, Turmeric.
fruits(4): Blackberry, Cherry Tomato, Strawberry, Watermelon.
fruit_trees(2): Bay, Oranges.
vegetables(40): Artichokes, Arugula, Beans, Beets, Broccoli, Cabbage, Cauliflower,
Celery, Chard, Chickpea, Chicory, Chinese Lantern, Cress, Edamame, Fava Bean,
Fennel, Garlic, Ginger, Jerusalem Artichokes, Jicama, Kale, Kohlrabi, Leeks,
Salad Mix, Melons, NZ Spinach, Okra, Scallions, Pac Choi, Peas, Potato, Radishes,
Soybean, Spinach, Sunflower, Sweet Corn, Sweet Potato, Turnips, Wheat, Winter Squash.

## 3. Required completions (work breakdown)
1. **Data model**: add nullable `crops.icon_url` (Alembic migration; SSOT for per-crop art). [in-session]
2. **UI render**: crop-card/module_card show `icon_url` watercolor, fallback to SVG sprite when null. [in-session]
3. **Brand media**: merge branch watercolor heroes/og/favicon → main, wire `modules.php`, update deploy. [in-session]
4. **Generation prompts**: 70 slug-exact watercolor crop-art prompts. [in-session authoring]
5. **Art generation**: 70 watercolor rasters via external image-gen (team_00 / ChatGPT-Devora pipeline). [EXTERNAL — the only non-in-session step]
6. **Backfill + deploy**: populate `icon_url` per crop as art lands → deploy to sfa.nimrod.bio → validate.
7. **Cross-engine validation**: team_190 non-Claude L-GATE_V on the system + brand-media R2.

## 4. Coverage targets
- Phase 1 (now): system complete — 70/70 crops render SOMETHING (watercolor if present, else SVG/leaf fallback); brand media deployed.
- Phase 2 (as art lands): 70/70 `icon_url` populated → 100% watercolor coverage.
