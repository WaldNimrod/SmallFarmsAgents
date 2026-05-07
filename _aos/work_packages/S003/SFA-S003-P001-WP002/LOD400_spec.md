# LOD400 — SFA-S003-P001-WP002 — ספר גידולים: DB Migrations + Seed Importer

**Date:** 2026-05-07
**Author:** team_100 (Claude Sonnet 4.6)
**WP:** SFA-S003-P001-WP002 — seed נתונים ראשוני
**Type:** LOD400_SPEC
**Status:** L-GATE_S ROUND_2 — all Round 1 findings resolved in v2.0.0; awaiting re-submission to team_190
**L-GATE_S Round 1 verdict:** PASS_WITH_FINDINGS (team_190, 2026-05-07); F1 BigInteger PK + F2 field_name convention resolved. Verdict: `_COMMUNICATION/team_190/SFA-S003-P001-LOD400-VERDICT_v1.0.0.md`
**Builder:** sfa_build (Sonnet, Team 10)
**Validator:** team_190 (external — L-GATE_SPEC + L-GATE_VALIDATE)
**Depends on:** SFA-S003-P001-WP001 (LOD200 schema v1.4.0 APPROVED)

**Reference documents (read before writing a single line of code):**
1. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP001/LOD200_CROP_SCHEMA_2026-05-07_v1.0.0.md` — schema SSoT
2. `_COMMUNICATION/TEAM_100/SFA-S003-P001-WP002/LOD300_SAMPLE_DATA_2026-05-07_v1.0.0.md` — sample data targets
3. This LOD400 spec

---

## 1. Goal

Create the **ספר גידולים** (Crop Book) data layer:

1. **6 Alembic migrations** (035–040) — create all crop-book tables in PostgreSQL
2. **SQLAlchemy models** — ORM layer for all 6 tables
3. **Python seed importer** — reads Tend 5yr CSV data + JMF XLSX; populates DB
4. **Tests** — models + importer + reconciliation logic

On completion, `python -m organic_market_agent.crop_book.importer.seed --all` must populate all 6 tables with the 5 sample crops (LOD300 targets) and demonstrate structural correctness. Full 66-crop import is validated by the same command.

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/
└── crop_book/
    ├── __init__.py
    ├── models.py              ← all 6 SQLAlchemy ORM classes
    ├── importer/
    │   ├── __init__.py
    │   ├── tend.py            ← Tend CSV parser + loader
    │   ├── jmf.py             ← JMF XLSX parser + loader
    │   ├── reconciler.py      ← merges per-source values → unified זנים row
    │   └── seed.py            ← CLI entrypoint / orchestrator
    └── constants.py           ← shared enums + name-mapping tables
```

### 2.2 Source file paths (absolute, machine-local)

Builder must use these exact paths as defaults. Each path is wrapped in a `--source-dir` flag so they are overridable.

| Source | Path |
|--------|------|
| Tend CROP_PLAN (all years) | See §2.3 for per-year paths |
| Tend PRODUCT_SOLD (2022) | `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/PRODUCT_SOLD (from macBook Air - nimrod).CSV` |
| Tend HARVESTS (2022) | `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/HARVESTS (from macBook Air - nimrod).CSV` |
| JMF XLSX (primary) | `/Users/nimrod/Documents/Market Gardening/MasterClass/Crops Data/` |

### 2.3 Tend year folder layout

```
/Users/nimrod/Documents/israel Microgreens/crop data/
├── CROP_PLAN (from macBook Air - nimrod).CSV          ← flat export (oldest)
├── Tend_2022/
│   ├── CROP_PLAN (from macBook Air - nimrod).CSV
│   ├── PRODUCT_SOLD (from macBook Air - nimrod).CSV
│   └── HARVESTS (from macBook Air - nimrod).CSV
│   (+ 11 other CSVs — not needed for this WP)
```

Year folders for other years (2018–2021): builder must probe for them at the same parent path and import if present. If a year folder is missing → log `WARN: year {Y} not found, skipping`.

### 2.4 Table → Python class mapping

| DB table | SQLAlchemy class | LOD200 Hebrew name |
|----------|------------------|--------------------|
| `crop_families` | `CropFamily` | `משפחות_בוטניות` |
| `crops` | `Crop` | `גידולים` |
| `crop_varieties` | `CropVariety` | `זנים` |
| `crop_variety_source_values` | `CropVarietySourceValue` | `זן_ערכי_מקור` |
| `crop_conversion_groups` | `CropConversionGroup` | `קבוצות_המרה` |
| `crop_unit_conversions` | `CropUnitConversion` | `המרות_יחידות` |

### 2.5 Field name mapping (LOD200 Hebrew → DB English)

All 6 tables use **`BigInteger` (autoincrement)** PKs, consistent with the S002 project-wide pattern (migrations 001–034). This overrides the UUID notation in LOD200 v1.4.0. Rationale: autoincrement integers are simpler and align with all existing tables. Formally recorded in LOD200 v1.5.0 §4.9.

`crop_variety_source_values.field_name` stores **English DB column names** only — e.g. `documented_price`, `days_to_maturity`, `avg_yield_per_bed_m`. Never Hebrew logical names. This is the canonical convention for all source_values entries.

**`crop_families`**
```
id              → id (BigInteger PK, autoincrement)
שם_מדעי        → scientific_name (VARCHAR 200, UNIQUE NOT NULL)
שם_עברי        → name_he (VARCHAR 200, nullable)
```

**`crops`**
```
id                          → id (BigInteger PK)
שם_עברי                    → name_he (VARCHAR 200, UNIQUE NOT NULL)
שם_אנגלי                   → name_en (VARCHAR 200, nullable)
שם_מדעי                    → scientific_name (VARCHAR 200, nullable)
משפחה_id                   → family_id (FK → crop_families.id, NOT NULL)
קטגוריה                    → category (VARCHAR 50, NOT NULL)
מחזור_גידול                → growth_cycle (VARCHAR 30, nullable)
יחידת_קציר_ברירת_מחדל    → harvest_unit_default (VARCHAR 20, nullable)
שנת_פרי_ראשונה             → first_fruit_year (Integer, nullable)
קבוצת_המרה_id              → conversion_group_id (FK → crop_conversion_groups.id, nullable)
תיאור_כללי                 → description (Text, nullable)
מזהה_מוצר_oma              → oma_product_id (VARCHAR 20, nullable)
```

**`crop_varieties`**
```
id                          → id (BigInteger PK)
גידול_id                   → crop_id (FK → crops.id, NOT NULL)
שם_זן_אנגלי                → name_en (VARCHAR 200, nullable)
שם_זן_עברי                 → name_he (VARCHAR 200, nullable)
הוא_זן_ברירת_מחדל         → is_default (Boolean NOT NULL, default False)
מורכב                      → is_grafted (Boolean NOT NULL, default False)
זן_כנה                     → rootstock_variety (VARCHAR 200, nullable)
שיטת_שתילה                 → planting_method (VARCHAR 30, nullable)
ימים_לבשלות                → days_to_maturity (Integer, nullable)
חלון_קציר_מינ_ימים         → harvest_window_min_days (Integer, nullable)
חלון_קציר_מקס_ימים         → harvest_window_max_days (Integer, nullable)
ריווח_בשורה_סמ             → in_row_spacing_cm (Numeric 6,2, nullable)
שורות_לערוגה               → rows_per_bed (Integer, nullable)
עונת_שתילה                 → planting_season (VARCHAR 100, nullable)
מרווח_זריעת_רצף_שבועות    → succession_interval_weeks (Integer, nullable)
יחידת_קציר                 → harvest_unit (VARCHAR 20, nullable)
תשואה_ממוצעת_למ_ערוגה    → avg_yield_per_bed_m (Numeric 10,4, nullable)
תשואה_מקור                 → yield_source (VARCHAR 200, nullable)
מחיר_מתועד_שח              → documented_price (Numeric 10,2, nullable)
מחיר_מתועד_יחידה           → documented_price_unit (VARCHAR 50, nullable)
מחיר_מתועד_מקור            → documented_price_source (VARCHAR 200, nullable)
מחירון_מוצר_id             → pricebook_product_id (VARCHAR 100, nullable)
הכנסה_ממוצעת_למ_ערוגה_שח → avg_revenue_per_bed_m (Numeric 10,2, nullable)
ימים_לנביטה_בחממה          → days_to_germinate_gh (Integer, nullable)
ימים_בחממה_סה_כ            → days_in_gh_total (Integer, nullable)
מזרע                       → seeder (VARCHAR 100, nullable)
הגדר_קדמי                  → seeder_front_gear (VARCHAR 20, nullable)
הגדר_אחורי                 → seeder_rear_gear (VARCHAR 20, nullable)
לוח_גלגל                   → seeder_roller_plate (VARCHAR 20, nullable)
שלב_קציר                   → harvest_stage (VARCHAR 30, nullable)
הערות                      → notes (Text, nullable)
```

**`crop_variety_source_values`**

```
id             → id (BigInteger PK)
זן_id          → variety_id (FK → crop_varieties.id, NOT NULL)
שם_שדה         → field_name (VARCHAR 100, NOT NULL)  ← English DB col name only
מקור           → source (VARCHAR 100, NOT NULL)
ערך_טקסט      → value_text (Text, nullable)
ערך_מספרי     → value_numeric (Numeric 14,6, nullable)
יחידה          → unit (VARCHAR 50, nullable)
הערה           → note (Text, nullable)
```

**`crop_conversion_groups`**
```
id        → id (BigInteger PK)
שם        → name (VARCHAR 100, UNIQUE NOT NULL)
תיאור    → description (Text, nullable)
```

**`crop_unit_conversions`**
```
id                     → id (BigInteger PK)
קבוצת_המרה_id         → conversion_group_id (FK → crop_conversion_groups.id, nullable)
גידול_id              → crop_id (FK → crops.id, nullable)
יחידת_מקור            → source_unit (VARCHAR 50, NOT NULL)
יחידת_יעד             → target_unit (VARCHAR 50, NOT NULL, always 'gram')
ערך_המרה               → conversion_factor (Numeric 10,4, NOT NULL)
הקשר                  → context (VARCHAR 50, nullable)
מקור                  → source (VARCHAR 100, NOT NULL)
הערה                  → note (Text, nullable)
```

### 2.6 Constraint: `crop_unit_conversions`

Exactly one of `conversion_group_id` / `crop_id` must be non-null. Enforce via DB CHECK constraint:
```sql
CHECK (
  (conversion_group_id IS NOT NULL AND crop_id IS NULL) OR
  (conversion_group_id IS NULL AND crop_id IS NOT NULL)
)
```

### 2.7 Importer reconciliation rules

These rules govern how `tend.py` and `jmf.py` values are merged into the unified `crop_varieties` row:

| Field | Winning source | Rule |
|-------|---------------|------|
| `days_to_maturity` | `team_00` > JMF > Tend | DTM policy per §4.8 of LOD200. Outlier: Tend DTM < 20 for leaf crops → REJECT, log in source_values with flag `OUTLIER_REJECTED`. |
| `avg_yield_per_bed_m` | Tend (prefer multi-year average) > JMF | If multi-year Tend available, compute mean. JMF as fallback. |
| `documented_price` | Tend PRODUCT_SOLD (Net Sales / Total Qty Sold) | Computed field: `net_sales / total_qty_sold`. Per-year entry in source_values. Unified field = most recent year's value. |
| `in_row_spacing_cm` | JMF > Tend | JMF spacing is prescriptive; Tend is observed. |
| `rows_per_bed` | JMF > Tend | Same as spacing. |
| `seeder` / gear | JMF | Equipment data lives in JMF only. |
| `planting_season` | JMF > Tend | |
| `is_grafted` + `rootstock_variety` | Tend CROP_PLAN (`Rootstock` column) | |

**All raw source values** — regardless of which wins the unified field — must be stored in `crop_variety_source_values`. The importer populates source_values FIRST, then the reconciler populates the unified row.

### 2.8 Tend CROP_PLAN column mapping

Key columns from the 58-column CSV mapped to `crop_varieties` fields:

| CROP_PLAN column | crop_varieties field |
|-----------------|---------------------|
| `Crop` | crop match key (maps via `TEND_CROP_MAP` in `constants.py`) |
| `Variety` | `name_en` |
| `Planting Method` | `planting_method` |
| `Harvest Stage` | `harvest_stage` |
| `DTM` | `days_to_maturity` (source: Tend) |
| `Harvest Window` | `harvest_window_max_days` |
| `In-Row Spacing` | `in_row_spacing_cm` |
| `Rows Per Bed` | `rows_per_bed` |
| `Harvest Unit` | `harvest_unit` |
| `Avg Yield Rate` | `avg_yield_per_bed_m` (value_text) |
| `Avg. Sales Price` | `documented_price` |
| `Seeder` | `seeder` |
| `Front gear` | `seeder_front_gear` |
| `Rear gear` | `seeder_rear_gear` |
| `Roller plate` | `seeder_roller_plate` |
| `Growing Cycle` | `growth_cycle` (on parent `crops` row) |
| `Family Name` | `family_id` (lookup `crop_families` by scientific_name) |
| `Rootstock` | `rootstock_variety` (if non-blank → `is_grafted=True`) |
| `Growing Cycle` | `growth_cycle` |

---

## 3. Acceptance Criteria

### AC-01 — Migrations 035–040 created and clean

- All 6 migration files exist at `organic_market_agent/db/versions/035_*.py` – `040_*.py`.
- `down_revision` chain is correct: 035→034, 036→035, …, 040→039.
- `alembic upgrade head` succeeds on a clean DB (mock/skip if DB offline — see AC-01-OFFLINE below).
- `alembic downgrade 034` succeeds (full reversibility).
- All `CHECK` constraints (category enum, growth_cycle enum, harvest_unit enum, conversion exclusion) present in upgrade().

**AC-01-OFFLINE:** If DB is offline (`require_postgres` pattern), test `upgrade()` schema generation via `op.get_bind()` mock. Use `alembic_mock_upgrade()` helper (see existing test patterns).

Enum values for `category` CHECK:
`'vegetables','herbs','baby','legumes','fruits','fruit_trees','grains','cover_crops'`

Enum values for `growth_cycle` CHECK:
`'annual','biennial','perennial'`

Enum values for `harvest_unit` / `harvest_unit_default` CHECK:
`'kg','bunch','head','case','unit','seedling'`

Enum values for `planting_method` CHECK:
`'direct_sow','transplant','greenhouse_transplant','cutting','purchase'`

Enum values for `harvest_stage` CHECK:
`'full_size','baby_leaf','head','plant_sale','seed'`

### AC-02 — SQLAlchemy models correct

- `organic_market_agent/crop_book/models.py` defines all 6 classes.
- All relationships wired (`Crop.varieties`, `Crop.family`, `CropVariety.source_values`, etc.).
- `CropUnitConversion.__table_args__` includes the mutual-exclusion CHECK.
- `from organic_market_agent.crop_book.models import *` succeeds without DB.

### AC-03 — Constants / name-mapping tables

`organic_market_agent/crop_book/constants.py` defines:

```python
TEND_CROP_MAP: dict[str, str]   # Tend English crop name → name_he
# E.g. {'Arugula': 'ארוגולה', 'Broccoli': 'ברוקולי', ...}
# Must cover all 52 unique crops in HARVESTS 2022 (see discovery summary)

TEND_FAMILY_MAP: dict[str, str]  # Tend 'Family Name' → scientific_name
# E.g. {'Brassicaceae': 'Brassicaceae', 'Compositae': 'Asteraceae', ...}

CATEGORY_MAP: dict[str, str]  # Tend category → DB enum value
# E.g. {'Vegetables': 'vegetables', 'Herbs': 'herbs', ...}

HARVEST_UNIT_MAP: dict[str, str]  # Tend unit text → DB enum
# E.g. {'Kilograms': 'kg', 'kg': 'kg', 'Bunches': 'bunch', 'bn': 'bunch',
#        'Heads': 'head', 'hd': 'head', 'Cases': 'case', 'cs': 'case', ...}
```

### AC-04 — Seed importer populates 5 LOD300 target crops

Running:
```bash
python -m organic_market_agent.crop_book.importer.seed \
  --crops arugula broccoli tomato basil carrot
```

Must result in:
- 5 `crops` rows, 1 `crop_families` row minimum per crop, all `crop_varieties` rows per LOD300.
- For each variety: `documented_price` and `documented_price_unit` populated per LOD300 targets.
- `crop_variety_source_values` has at least 1 row per (variety × source) per measured field.
- `crop_conversion_groups` seeded with the 7 groups from LOD200 §4.6.
- `crop_unit_conversions` seeded with the 7 rows from LOD200 §4.7 + carrot override.

### AC-05 — Full 66-crop import

Running:
```bash
python -m organic_market_agent.crop_book.importer.seed --all
```

Must:
- Load all 66 crops from the LOD200 §5 list.
- Log a `WARN` for any crop in the list with no Tend data found (expected for OMA-only fruits).
- Log a `WARN` for any Tend outlier (DTM < 20 for leaf crops) with field `OUTLIER_REJECTED`.
- Exit 0 — partial data is allowed (crops with no Tend data get NULL fields, not errors).

### AC-06 — Importer is idempotent

Running the seed command twice does not create duplicate rows. Strategy: upsert on natural keys:
- `crop_families`: upsert on `scientific_name`
- `crops`: upsert on `name_he`
- `crop_varieties`: upsert on `(crop_id, name_en)` where `name_en` is NOT NULL; else upsert on `(crop_id, is_default=True)` for the default variety
- `crop_variety_source_values`: upsert on `(variety_id, field_name, source)`
- `crop_conversion_groups`: upsert on `name`
- `crop_unit_conversions`: upsert on `(conversion_group_id, crop_id, source_unit, context)` (NULLs treated as wildcards — use COALESCE in ON CONFLICT)

### AC-07 — Tests green

- `tests/crop_book/test_models.py` — import smoke + relationship traversal (no DB required)
- `tests/crop_book/test_tend_importer.py` — parse CROP_PLAN rows; mock CSV; verify field extraction per AC-04 targets
- `tests/crop_book/test_reconciler.py` — DTM reconciliation (team_00 wins, outlier rejection, JMF fallback)
- `tests/crop_book/test_seed_idempotency.py` — run seed twice on in-memory SQLite; assert row count stable
- All existing tests still pass (`pytest tests/`)

### AC-08 — No raw material modification

- Source CSV/XLSX files at their disk paths are NEVER written, moved, or deleted.
- The importer is read-only with respect to source data.
- `validate_aos.sh .` returns 0 FAIL.

### AC-09 — CLI entrypoint

`organic_market_agent/crop_book/importer/seed.py` is invokable via:
```bash
python -m organic_market_agent.crop_book.importer.seed --help
```

Flags:
- `--all` — import all 66 crops
- `--crops NAME [NAME ...]` — import named crops only (Tend English names)
- `--dry-run` — parse and log, do not write to DB
- `--year YEAR` — restrict Tend data to single year (default: all available)
- `--source-dir PATH` — override base path for Tend data (default: hardcoded path from §2.2)

---

## 4. File-level deliverables

### CREATE

```
organic_market_agent/db/versions/035_crop_book_families.py
organic_market_agent/db/versions/036_crop_book_crops.py
organic_market_agent/db/versions/037_crop_book_varieties.py
organic_market_agent/db/versions/038_crop_book_source_values.py
organic_market_agent/db/versions/039_crop_book_conversion_groups.py
organic_market_agent/db/versions/040_crop_book_unit_conversions.py

organic_market_agent/crop_book/__init__.py
organic_market_agent/crop_book/models.py
organic_market_agent/crop_book/constants.py
organic_market_agent/crop_book/importer/__init__.py
organic_market_agent/crop_book/importer/tend.py
organic_market_agent/crop_book/importer/jmf.py
organic_market_agent/crop_book/importer/reconciler.py
organic_market_agent/crop_book/importer/seed.py

tests/crop_book/__init__.py
tests/crop_book/test_models.py
tests/crop_book/test_tend_importer.py
tests/crop_book/test_reconciler.py
tests/crop_book/test_seed_idempotency.py
```

### UPDATE
- `CHANGELOG.md` — add `[Unreleased]` entry: "S003 ספר גידולים data layer — 6 tables, seed importer, 66 crops"
- `_COMMUNICATION/team_10/SFA-S003-P001-WP002/BUILD_REPORT_v1.0.0.md` — builder creates after L-GATE_B

---

## 5. Build notes

- All migrations use `BigInteger` PK (consistent with existing pattern, not UUID).
- Hebrew string columns: `Text` or `VARCHAR(n)` — PostgreSQL handles UTF-8 natively.
- `jmf.py` scope: read JMF XLSX files from §2.2 path using `openpyxl`. If JMF XLSX files have no parseable crop data (files may be templates only), log `INFO: JMF XLSX yielded 0 rows for {filename}` and continue — this is not a failure.
- Source `'JMF'` = JMF MasterClass XLSX. Source `'Tend_YEAR'` (e.g. `Tend_2022`) = Tend CSV for that year. Source `'team_00'` = manually provided values (hardcoded in `constants.py`).
- `team_00` DTM overrides for ארוגולה קיץ (21 days) are hardcoded in `constants.py` under `TEAM00_DTM_OVERRIDES: dict[str, int]`.

---

*LOD400 v2.0.0 — revised 2026-05-07 by team_100. Changes: F1 BigInteger PK canonical (§2.5 preamble); F2 field_name English convention (§2.5 preamble + blockquote removed); status ROUND_2 pending team_190 re-submission.*
