# RESEARCH — SFA Data-Layer Inventory for new UI

**Author:** team_100 research sub-agent
**Date:** 2026-05-27
**Mandate ref:** `_COMMUNICATION/TEAM_100/MANDATE_WP-UI-RE-BUILD_v1.0.0.md` §1 deliverable 2 + §5.4 AC-DB-1
**Read-only research artifact.** No schema mutations performed.

---

## 0. Executive summary — what's on the wire NOW vs. what's queued

| Layer | What exists | UI must handle |
|---|---|---|
| Canonical Postgres (waldhomeserver) | 14 crop-book tables (035–052), 6 task/note/calendar/etc. + field-enrichment | All fields from Section A/B — many not yet pushed |
| `sfa_ingest_push.py` (PG → MySQL mirror) | **Only** crops, varieties, products | Top-level + `payload_json` keys per Section C |
| MySQL mirror @ sfa.nimrod.bio | crops, crop_varieties, products | API exposed today (Section C) |
| Live REST API (https://sfa.nimrod.bio/api/v1) | `/health`, `/modules`, `/crops`, `/crops/{slug}`, `/products`, `/products/{slug}` | Endpoints for tasks/notes/harvest/calendar do **NOT** exist yet — UI should degrade gracefully |

**Forward-looking risk:** the canonical Postgres has 6 additional tables (`crop_task_templates`, `crop_knowledge_notes`, `crop_harvest_stats`, `crop_planting_calendar`, `crop_cover_crops`, `crop_companion_matrix`, `crop_postharvest_storage`, `crop_field_enrichment`) that the publisher does NOT yet push. When the parallel session expands `sfa_ingest_push.py`, the UI must already accept these payloads — implement unknown-field fallback per AC-DB-1.

---

## A. Migration inventory (041 → 053)

| ID  | File | Tables touched | Op | New cols / enum vals | WP |
|-----|------|----------------|-----|----------------------|-----|
| 041 | `041_crop_field_enrichment.py` | `crop_field_enrichment` (new) | CREATE TABLE | `id, variety_id, field_name, value_min, value_max, value_best, confidence_score, source_count, winning_source_class, computed_at` | WP-A |
| 042 | `042_source_values_enrich.py` | `crop_variety_source_values` | ADD COLUMN | `trust_tier VARCHAR(20)`, `confidence_weight NUMERIC(5,4)`, `is_outlier_rejected BOOLEAN` + backfill from `source` label | WP-A (GCR_1) |
| 043 | `043_backfill_source_values_trust.py` | `crop_variety_source_values` | DATA backfill | (re-runs 042 backfill on live DB; idempotent) | WP-A (LV-01 remediation) |
| 044 | `044_crop_task_templates.py` | `crop_task_templates` (new) | CREATE TABLE | `id, crop_id, source, trust_tier, task_type, timing_anchor, days_offset (sentinel -32768), method, input_material, notes, display_order, is_active, created_at` + CHECK for task_type (14 enum), timing_anchor (4 enum) | WP-B1 |
| 045 | `045_crop_knowledge_notes.py` | `crop_knowledge_notes` (new) | CREATE TABLE | `id, crop_id, source, trust_tier, note_type, body_text (≤2000), provenance_pdf, provenance_pages, is_internal_farm_use_only, extraction_model, extracted_at, created_at` + CHECK note_type (13 enum) | WP-B2 |
| 046 | `046_tend_overlay.py` | `crop_harvest_stats` (new) + ALTER `crop_task_templates` | CREATE TABLE + ALTER CHECK | crop_harvest_stats: `id, crop_id, season, year, source, cycles_count, first_harvest_week, peak_harvest_week, last_harvest_week, yield_total, yield_unit, yield_per_bed_min, yield_per_bed_max, yield_per_bed_median, created_at`. Adds 6 task_type enum values: `nursery_seed, pest_spray, potting_up, thinning, trellis, fertilize` | WP-B3 (GCR-B3-1) |
| 047 | `047_create_crop_knowledge_notes_crops_junction.py` | `crop_knowledge_notes_crops` (new) | CREATE TABLE | M2M junction: `note_id, crop_id` | WP-B1-patch04 |
| 048 | `048_make_crop_knowledge_notes_crop_id_nullable.py` | `crop_knowledge_notes` | ALTER COLUMN | `crop_id` → NULLABLE (M2M-only notes) | WP-B1-patch07 |
| 049 | `049_crop_planting_calendar.py` | `crop_planting_calendar` (new) | CREATE TABLE | `id, crop_id, source, trust_tier, region, activity_type, season, month_jan…month_dec (12 booleans), notes, created_at` + CHECK activity_type (`seed/transplant/both`), season (`spring/summer/fall/winter/all`) | WP-C1 |
| 050 | `050_crop_cover_crops.py` | `crop_cover_crops` (new) | CREATE TABLE | `id, name_en, name_he, category, source, trust_tier, total_days_garden, germination_temp_c_min, hardiness_zone, sow_window, inoculum, survives_winter, notes, created_at` + CHECK category (`legume/cereal/brassica/other`) | WP-C1 |
| 051 | `051_crop_companion_matrix.py` | `crop_companion_matrix` (new) | CREATE TABLE | `id, crop_a_id, crop_b_id, compatibility (beneficial/neutral/antagonistic), source, trust_tier, evidence_strength (strong/weak/anecdotal), notes, created_at` | WP-C4 |
| 052 | `052_crop_postharvest_storage.py` | `crop_postharvest_storage` (new) | CREATE TABLE | `id, crop_id, source, trust_tier, storage_temp_c_min, storage_temp_c_max, rh_pct_min, rh_pct_max, freezing_point_c, ethylene_production, ethylene_sensitivity, storage_life_days_min, storage_life_days_max, notes, created_at` | WP-C4 |
| 053 | `053_extend_ckn_note_type.py` | `crop_knowledge_notes` | ALTER CHECK | Adds 6 note_type enum: `frost_tolerance, flowering_date, pollination_mechanism, israeli_regions, variety_trial_score, hydro_suitability` (total now 19) | WP-C2 |

---

## B. ORM model inventory (post WP-A)

| Class | Table | File | Source WP |
|---|---|---|---|
| `CropFieldEnrichment` | `crop_field_enrichment` | `crop_book/enrichment_models.py` | WP-A |
| `CropVarietySourceValue` (extended) | `crop_variety_source_values` | `crop_book/models.py` | WP-A (042) |
| `CropTaskTemplate` | `crop_task_templates` | `crop_book/crop_task_templates.py` | WP-B1 |
| `CropKnowledgeNote` | `crop_knowledge_notes` | `crop_book/crop_knowledge_notes.py` | WP-B2 |
| `CropHarvestStat` | `crop_harvest_stats` | `crop_book/crop_harvest_stats.py` | WP-B3 |
| (junction Table) | `crop_knowledge_notes_crops` | `crop_book/crop_knowledge_notes_crops.py` | WP-B1-patch04 |
| `CropPlantingCalendar` | `crop_planting_calendar` | `crop_book/planting_calendar.py` | WP-C1 |
| `CropCoverCrop` | `crop_cover_crops` | `crop_book/cover_crops.py` | WP-C1 |
| `CropCompanionMatrix` | `crop_companion_matrix` | `crop_book/companion_matrix.py` | WP-C4 |
| `CropPostharvestStorage` | `crop_postharvest_storage` | `crop_book/postharvest_storage.py` | WP-C4 |

### Enum vocabularies (ORM source-of-truth)

| Enum | Values | Defined in |
|---|---|---|
| `TASK_TYPE_VALUES` (20) | stale_seed_bed, flame_weeder, flextine_harrow_1, flextine_harrow_2, biodisc, hoe, hand_weed, boron_seaweed_1, boron_seaweed_2, straw_mulch_topdress, head_pinch_chop, mow_and_tarp, at_seeding_transplanting, net_row_cover, nursery_seed, pest_spray, potting_up, thinning, trellis, fertilize | `crop_task_templates.py` |
| `TIMING_ANCHOR_VALUES` (4) | seeding, transplanting, harvest, field_prep | `crop_task_templates.py` |
| `NOTE_TYPE_VALUES` (19) | pest_disease, harvest_marker, storage_handling, rotation_companion, cultivar_recommendation, growing_tip, irrigation, nursery_specific, flame_weed_timing, biopesticide_spray, phytoprotection_substance, phytoprotection_application, nursery_seeding_process, frost_tolerance, flowering_date, pollination_mechanism, israeli_regions, variety_trial_score, hydro_suitability | `crop_knowledge_notes.py` |
| `SEASON_VALUES` (4 in harvest_stats, 5 in calendar) | spring, summer, fall, winter (+ `all` in calendar) | `crop_harvest_stats.py`, `planting_calendar.py` |
| `ACTIVITY_TYPES` (3) | seed, transplant, both | `planting_calendar.py` |
| `MONTH_COLUMNS` (12) | month_jan…month_dec | `planting_calendar.py` |
| `CATEGORY_VALUES` (cover crops, 4) | legume, cereal, brassica, other | `cover_crops.py` |
| `COMPATIBILITY_VALUES` (3) | beneficial, neutral, antagonistic | `companion_matrix.py` |
| `EVIDENCE_VALUES` (3) | strong, weak, anecdotal | `companion_matrix.py` |
| Crops `category` (8) | vegetables, herbs, baby, legumes, fruits, fruit_trees, grains, cover_crops | `models.py` |
| Crops `growth_cycle` (3) | annual, biennial, perennial | `models.py` |
| Crops `harvest_unit_default` (6) | kg, bunch, head, case, unit, seedling | `models.py` |
| Variety `planting_method` (5) | direct_sow, transplant, greenhouse_transplant, cutting, purchase | `models.py` |
| Variety `harvest_stage` (5) | full_size, baby_leaf, head, plant_sale, seed | `models.py` |
| Trust tiers (7) | EX, NI, PR, OP, MK, WB, UC | `source_registry.py` |

### Region conventions (free-text `region` column — calendar)

`IL_general`, `IL_north`, `IL_center`, `IL_south`, `MED_general`.

---

## C. API shape probe (live, 2026-05-27)

### `GET /api/v1/health`
```
{ "status": "ok", "php_version": "8.5.5", "db": "ok", "ts": "2026-05-27T16:44:56+00:00" }
```

### `GET /api/v1/modules`
Returns `{version, updated, tiers{open,beta,coming,paid,custom}, modules[], pages[], contact{}, ai_prompts{}}`. Each module: `id, name_he, name_en, sub, tier, icon, thumb_prompt, stat, stat_count, color, route, shortcode, status, route_runtime`.
Tier classes: `open|beta|coming|paid|custom`. 8 modules registered (crop-book, market, calc, planner, clients, inventory, tend-bridge, field-log).

### `GET /api/v1/crops` → `{ count: 52, items: [...] }`
Item keys (10): `id, slug, hebrew_name, scientific_name, family_id, family_name_he, category, season, dtm_min, dtm_max`.

### `GET /api/v1/crops/{slug}` (e.g. `basil`)
Keys (16): `id, slug, hebrew_name, scientific_name, family_id, family_name_he, category, season, dtm_min, dtm_max, last_pushed_at, schema_version, name_en, growth_cycle, harvest_unit_default, first_fruit_year, description_md, oma_product_id, variety_count, varieties[]`.

`varieties[]` element keys (14): `id, name, schema_version, name_en, is_default, days_to_maturity, harvest_window_min_days, harvest_window_max_days, in_row_spacing_cm, planting_method, planting_season, harvest_unit, documented_price, documented_price_unit, documented_price_source, notes`.

### `GET /api/v1/products` → `{ count: 65, items: [...] }` (also accepts `?category=…`)
Item keys (8): `id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days`.

### `GET /api/v1/products/{slug}` (e.g. `prd017`)
Keys (12): `id, slug, hebrew_name, category, unit, last_price, last_price_date, freshness_days, last_pushed_at, schema_version, code, is_organic_required, is_basket_product, seasonality_notes, price_history_30d`.

### NOT EXPOSED (404)
`/varieties/{id}`, `/sources`, `/crops/{slug}/tasks`, `/crops/{slug}/notes`, `/crops/{slug}/harvest`, `/crops/{slug}/calendar`. These tables exist server-side but are not pushed/exposed yet.

---

## D. `payload_json` keys written by `sfa_ingest_push.py`

The current push pipeline embeds a `payload_json` dict on each row (crops/varieties/products). The MySQL mirror surfaces these alongside top-level columns.

| Endpoint | `payload_json` keys |
|---|---|
| `crops` | `schema_version, name_en, growth_cycle, harvest_unit_default, first_fruit_year, description_md, oma_product_id, variety_count` |
| `crop_varieties` (nested under crop) | `schema_version, name_en, is_default, days_to_maturity, harvest_window_min_days, harvest_window_max_days, in_row_spacing_cm, planting_method, planting_season, harvest_unit, documented_price, documented_price_unit, documented_price_source, notes` |
| `products` | `schema_version, code, is_organic_required, is_basket_product, seasonality_notes` |

The MySQL ingest API merges `payload_json` keys into the row response (visible in the live API probe). UI should treat the union of (top-level columns ∪ payload_json keys) as the rendering surface.

**Forward expansion (not yet in push):** when the parallel session extends the push, anticipate these additional payload_json keys per `crop_varieties`:
- enrichment summary: `enrichment[].field_name, value_best, value_min, value_max, confidence_score, source_count, winning_source_class, computed_at` (from `crop_field_enrichment`)
- per-variety source values: `source_values[].source, trust_tier, confidence_weight, is_outlier_rejected, value_text, value_numeric, unit, note`

And on `crops`:
- `tasks[]` (from `crop_task_templates`)
- `knowledge_notes[]` (from `crop_knowledge_notes`)
- `harvest_stats[]` (from `crop_harvest_stats`)
- `planting_calendar[]` (from `crop_planting_calendar`)
- `companion_pairs[]` (from `crop_companion_matrix`)
- `postharvest[]` (from `crop_postharvest_storage`)

---

## E. Field set the UI must handle (canonical, exhaustive)

### E.1 Crop detail (top-level + extensions)

| Field | Type | Hebrew label | Source WP | UI treatment |
|---|---|---|---|---|
| `id` | int | — | core | (hidden) |
| `slug` | text | — | core | URL handle |
| `hebrew_name` | text | שם בעברית | core | h1 |
| `name_en` | text | שם באנגלית | core | sub-title |
| `scientific_name` | text | שם מדעי | core | italic badge |
| `family_id` / `family_name_he` | int/text | משפחה | core | breadcrumb |
| `category` | enum(8) | קטגוריה | core | badge |
| `season` | text | עונה | core | badge |
| `growth_cycle` | enum(3) | מחזור צמיחה | core | badge |
| `harvest_unit_default` | enum(6) | יחידת קציר ברירת מחדל | core | inline |
| `first_fruit_year` | int | שנת פרי ראשון | core | row (perennial only) |
| `dtm_min` / `dtm_max` | int | ימים לבגרות (טווח) | core | range badge |
| `description_md` | markdown | תיאור | core | prose block |
| `oma_product_id` | text | מזהה מחירון | core | link to /products |
| `variety_count` | int | מספר זנים | core | numeric chip |
| `last_pushed_at` | timestamp | עודכן | core | footer micro |
| `schema_version` | int | — | core | (hidden) |
| **tasks[]** (future) | array | משימות גידול | WP-B1/B3 | timeline track (anchor + days_offset) |
| **knowledge_notes[]** (future) | array | פנקס ידע | WP-B2/C2 | accordion sections by note_type |
| **harvest_stats[]** (future) | array | סטטיסטיקת קציר | WP-B3 | summary card with yield_per_bed_median |
| **planting_calendar[]** (future) | array | לוח שתילה ישראלי | WP-C1 | 12-month grid (region overlay) |
| **companion_pairs[]** (future) | array | שתילה משותפת | WP-C4 | matrix mini-card |
| **postharvest[]** (future) | array | אחסון לאחר קציר | WP-C4 | spec table |
| **cover_crops** (chart) | array | צמחי כיסוי | WP-C1 | separate page (not crop-detail) |

### E.2 Variety detail

| Field | Type | Hebrew label | Source WP | UI treatment |
|---|---|---|---|---|
| `id` | int | — | core | hidden |
| `name` / `name_en` | text | שם זן | core | h2 |
| `is_default` | bool | זן ברירת מחדל | core | star icon |
| `days_to_maturity` | int | ימים לבגרות | core | table row |
| `harvest_window_min_days` / `_max_days` | int | חלון קציר (ימים) | core | range row |
| `in_row_spacing_cm` | numeric | מרווח בשורה (ס"מ) | core | row + ruler icon |
| `planting_method` | enum(5) | שיטת שתילה | core | badge |
| `planting_season` | text | עונת שתילה | core | badge |
| `harvest_unit` | enum(6) | יחידת קציר | core | inline |
| `documented_price` / `_unit` / `_source` | numeric+text | מחיר תיעודי + מקור | core | inline group |
| `notes` | text | הערות | core | small italic |
| `is_grafted` / `rootstock_variety` (PG only) | bool/text | מורכב / כנה | core | conditional row |
| `rows_per_bed` (PG only) | int | שורות לערוגה | core | row |
| `succession_interval_weeks` (PG only) | int | מרווח רצף (שבועות) | core | row |
| `avg_yield_per_bed_m` (PG only) | numeric | יבול ממוצע לערוגה למטר | core | row |
| `yield_source` (PG only) | text | מקור יבול | core | tooltip |
| `pricebook_product_id` (PG only) | text | קישור למחירון | core | link |
| `avg_revenue_per_bed_m` (PG only) | numeric | הכנסה ממוצעת לערוגה למטר | core | row |
| `days_to_germinate_gh` (PG only) | int | ימים לנביטה בחממה | core | row |
| `days_in_gh_total` (PG only) | int | סה"כ ימים בחממה | core | row |
| `seeder` / `seeder_front_gear` / `_rear_gear` / `_roller_plate` (PG only) | text | הגדרות זרעית | core | nested group |
| `harvest_stage` (enum 5, PG only) | enum | שלב קציר | core | badge |
| **enrichment[].value_best/min/max** | numeric | ערך מוסכם (טווח) | WP-A | dual-track gauge per field |
| **enrichment[].confidence_score** | numeric 0–1 | רמת ביטחון | WP-A | progress dot |
| **enrichment[].source_count** | int | מספר מקורות | WP-A | chip "n מקורות" |
| **enrichment[].winning_source_class** | enum(7) | מקור מנצח | WP-A | tier badge |
| **source_values[]** (per variety) | array | פירוט מקורות | WP-A | expandable accordion |
| └ `source` | text | מקור | WP-A | label |
| └ `trust_tier` | enum(7) | סיווג אמינות | WP-A | color badge |
| └ `confidence_weight` | numeric | משקל | WP-A | numeric |
| └ `value_text` / `value_numeric` / `unit` | mixed | ערך + יחידה | WP-A | inline |
| └ `is_outlier_rejected` | bool | נדחה כחריג | WP-A | strikethrough |
| └ `note` | text | הערה | WP-A | italic |

### E.3 Task templates (`tasks[]`)

| Field | Hebrew label | UI treatment |
|---|---|---|
| `task_type` (enum 20) | סוג משימה | icon + label |
| `timing_anchor` (enum 4) | עוגן זמן | badge |
| `days_offset` (int; -32768 = presence-only) | היסט בימים | numeric — render "X" sentinel as "מבוצע" without offset |
| `method` | שיטה | tooltip |
| `input_material` | חומר תשומה | tooltip |
| `notes` | הערות | tooltip |
| `source` / `trust_tier` | מקור | tier badge |
| `display_order` | — | sort key (hidden) |
| `is_active` | פעיל | hide row when false |

### E.4 Knowledge notes (`knowledge_notes[]`) — internal-use-only by default

| Field | Hebrew label | UI treatment |
|---|---|---|
| `note_type` (enum 19) | סוג רשומה | section header |
| `body_text` (≤2000) | תוכן | prose block |
| `provenance_pdf` / `provenance_pages` | מקור (PDF + עמודים) | footer micro |
| `is_internal_farm_use_only` | פנימי בלבד | **HARD GATE** — do NOT render to public sfa.nimrod.bio unless false |
| `extraction_model` / `extracted_at` | מודל חילוץ | tooltip |
| `source` / `trust_tier` | מקור | tier badge |

### E.5 Harvest stats (`harvest_stats[]`)

| Field | Hebrew label | UI treatment |
|---|---|---|
| `season` (enum 4) + `year` | עונה / שנה | header |
| `cycles_count` | מספר מחזורים | numeric |
| `first_harvest_week` / `peak_harvest_week` / `last_harvest_week` | שבועות קציר (ראשון/שיא/אחרון) | strip chart |
| `yield_total` / `yield_unit` | יבול כולל | numeric |
| `yield_per_bed_min/max/median` | יבול לערוגה (מינ/מקס/חציון) | range + median dot |

### E.6 Planting calendar (`planting_calendar[]`)

| Field | Hebrew label | UI treatment |
|---|---|---|
| `region` (`IL_general`/`IL_north`/`IL_center`/`IL_south`/`MED_general`) | אזור | filter chips |
| `activity_type` (seed/transplant/both) | פעולה | tabs |
| `season` (enum 5 inc. `all`) | עונה | badge |
| `month_jan…month_dec` (12 bool) | ינואר…דצמבר | 12-cell strip |
| `notes` | הערות | tooltip |
| `source` / `trust_tier` | מקור | tier badge |

### E.7 Cover crops (`crop_cover_crops`) — standalone page

| Field | Hebrew label | UI |
|---|---|---|
| `name_en` / `name_he` | שם | h2 |
| `category` (legume/cereal/brassica/other) | קטגוריה | filter |
| `total_days_garden` | ימים בגינה | row |
| `germination_temp_c_min` | טמפ' מינ' לנביטה | row |
| `hardiness_zone` | אזור עמידות | row |
| `sow_window` | חלון זריעה | row |
| `inoculum` | אינוקולנט | row |
| `survives_winter` | שורד חורף | bool icon |
| `notes` | הערות | small |

### E.8 Companion matrix (`companion_pairs[]`)

| Field | Hebrew label | UI |
|---|---|---|
| `crop_a_id`/`crop_b_id` | זוג גידולים | linked pills |
| `compatibility` (beneficial/neutral/antagonistic) | תאימות | colored badge (green/gray/red) |
| `evidence_strength` (strong/weak/anecdotal) | חוזק ראיה | dot scale |
| `notes` | הערות | tooltip |
| `source`/`trust_tier` | מקור | tier badge |

### E.9 Postharvest storage (`postharvest[]`)

| Field | Hebrew label | UI |
|---|---|---|
| `storage_temp_c_min/max` | טווח טמפ' אחסון | range row |
| `rh_pct_min/max` | טווח לחות יחסית | range row |
| `freezing_point_c` | נקודת קיפאון | row |
| `ethylene_production` | ייצור אתילן | badge |
| `ethylene_sensitivity` | רגישות לאתילן | badge |
| `storage_life_days_min/max` | חיי מדף (ימים) | range row |
| `notes` | הערות | small |

### E.10 Products (mirror — public market index)

| Field | Hebrew label | UI |
|---|---|---|
| `hebrew_name` | שם | h2 |
| `category` | קטגוריה | breadcrumb |
| `unit` | יחידה | inline |
| `last_price` / `last_price_date` | מחיר אחרון / תאריך | header |
| `freshness_days` | טריות (ימים) | freshness pill |
| `code` | קוד | small mono |
| `is_organic_required` | אורגני נדרש | bool icon |
| `is_basket_product` | מוצר סל | bool icon |
| `seasonality_notes` | עונתיות | text |
| `price_history_30d` | היסטוריית מחיר 30 ימים | sparkline |

### E.11 Unknown-field fallback (AC-DB-1)

For any key NOT in the tables above, the UI must:
1. Render under a collapsed `<details>` block labeled "מידע נוסף".
2. Show as `<dt>field_name</dt><dd>JSON.stringify(value)</dd>`.
3. Never crash on unexpected types (array/object/null).

---

## F. Source-tier vocabulary (rendering canon)

| Code | Class name | Hebrew label | Weight | Color cue | Badge | Tooltip |
|---|---|---|---|---|---|---|
| `EX` | Expert override | מקור מומחה (team_00) | hard override | gold/amber | "מקור מומחה" | "ערך שנקבע ידנית על-ידי team_00 — תמיד גובר" |
| `NI` | Nimrod-Input | קלט נמרוד | hard override | royal blue | "מקור פנימי" | "קובץ/קישור שסופק על-ידי team_00 (קצין הידע) — גובר על PR/OP" |
| `PR` | Prescriptive | מקור הוראתי | 0.70 | leaf green | "מקור הוראתי" | "ספרי הוראה אגרונומיים — JMF MasterClass / אוניברסיטאות" |
| `OP` | Operational | מקור תפעולי | 0.55 | terracotta | "נתוני שדה" | "תיעוד שדה ממשי (Tend, Idan)" |
| `MK` | Market index | מדד שוק | 0.40 | sun yellow | "מדד שוק" | "מחירון קהילתי OMA — נתונים מצרפיים" |
| `WB` | Web / 3rd-party | מקור רשת | 0.30 | paper gray | "מקור רשת" | "מסדי נתונים חיצוניים — אמינות מופחתת" |
| `UC` | User-Community | קהילה | NULL until moderated | tomato (muted) | "קהילה" | "תרומת משתמש — ממתין לאישור מודרציה" |

Render order (highest → lowest trust): EX, NI, PR, OP, MK, WB, UC.
`is_outlier_rejected=TRUE` → strike-through + tooltip "נדחה כחריג סטטיסטי".
`confidence_weight IS NULL` on non-EX/NI → "ממתין לאישור" pill.

Color palette ties: leaf / tomato / sun / paper / soil — matches existing nimrod.bio tier palette (`/api/v1/modules` tiers).

Class detection from dynamic source labels:
- `NI:<name>` → NI
- `OMA:<name>` → MK
- `WB:<name>` → WB
- `UC:<id>` → UC
- Unknown → WB @ 0.20

---

## G. Five highest-impact new fields the UI must surface

1. **`crop_harvest_stats.yield_per_bed_median` + `yield_per_bed_min/max`** (WP-B3) — new actionable economic data per crop per season; needs a dedicated "יבול בפועל" card in crop detail with median dot + range bar.
2. **`crop_field_enrichment.value_best` + `confidence_score` + `winning_source_class`** (WP-A) — *every* numeric variety field gets a trust-weighted consensus row; UI must replace flat numeric cells with `[value_best ± range] · confidence · tier-badge` micro-component.
3. **`crop_planting_calendar.month_jan…month_dec` (× `activity_type` × `region`)** (WP-C1) — Israeli monthly seed/transplant grid; needs a 12-cell strip view in crop detail with `region` filter chips (`IL_general`/`IL_north`/`IL_center`/`IL_south`).
4. **`crop_task_templates` timeline** (WP-B1/B3) — 20 task types anchored to (`seeding`/`transplanting`/`harvest`/`field_prep`) ± `days_offset`; needs a horizontal timeline track in crop detail with the **-32768 sentinel** rendered as "מבוצע" without offset (do NOT render the literal -32768).
5. **`crop_knowledge_notes.is_internal_farm_use_only`** (WP-B2/C2) — **HARD GATE for licensing compliance**: 19 note types but most carry `is_internal_farm_use_only=TRUE`. Public sfa.nimrod.bio must filter on this flag before any render; failure = licensing violation.

---

**File path:** `/Users/nimrod/Documents/SmallFarmsAgents/_COMMUNICATION/team_100/RESEARCH_data_layer_inventory_2026-05-27_v1.0.0.md`
**Source-of-truth refs:**
- Migrations: `organic_market_agent/db/versions/041_…053_…py`
- ORM: `organic_market_agent/crop_book/{models.py, enrichment_models.py, crop_task_templates.py, crop_knowledge_notes.py, crop_harvest_stats.py, planting_calendar.py, cover_crops.py, companion_matrix.py, postharvest_storage.py, source_registry.py, field_policy.py}`
- Push: `.claude/worktrees/*/organic_market_agent/publisher/sfa_ingest_push.py` (375 lines, crops/varieties/products only)
- Live API: https://sfa.nimrod.bio/api/v1/{health,modules,crops,crops/{slug},products,products/{slug}}
