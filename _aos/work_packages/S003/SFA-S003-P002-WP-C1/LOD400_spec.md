---
id: SFA-S003-P002-WP-C1-LOD400
wp: SFA-S003-P002-WP-C1
gate: L-GATE_S (LOD400 — build-precise spec)
status: LOD400_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 canonical registration grant
date: 2026-05-26
version: v1.0.0
supersedes: LOD200_spec.md §10 AC count target
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD200_spec.md
sources_ref: data/external_sources/INDEX.md + WAVE_PLAN_v1.0.0.md
---

# LOD400 — WP-C1: Israeli Structured Data + Tend Multi-Year Backfill

**LOD400 precision standard:** any junior developer or fresh agent must
implement without inferring anything not explicitly stated.

---

## 1. Mission

(See LOD200 §1.) In one sentence: ingest 8 already-staged tabular sources from
`data/external_sources/` into the SFA crop book through the existing reconciler
engine, without inventing new infrastructure.

## 2. File-by-file delta

| Action | Path | Purpose |
|--------|------|---------|
| NEW | `organic_market_agent/db/versions/047_crop_planting_calendar.py` | migration 047 |
| NEW | `organic_market_agent/db/versions/048_crop_cover_crops.py` | migration 048 |
| NEW | `organic_market_agent/crop_book/planting_calendar.py` | ORM for `crop_planting_calendar` |
| NEW | `organic_market_agent/crop_book/cover_crops.py` | ORM for `crop_cover_crops` |
| NEW | `organic_market_agent/crop_book/importer/israeli/__init__.py` | empty |
| NEW | `organic_market_agent/crop_book/importer/israeli/groworganic_importer.py` | L01 |
| NEW | `organic_market_agent/crop_book/importer/israeli/bustan_importer.py` | L36 |
| NEW | `organic_market_agent/crop_book/importer/israeli/idan_planning_importer.py` | L03 + L04 |
| NEW | `organic_market_agent/crop_book/importer/jmf/__init__.py` | empty |
| NEW | `organic_market_agent/crop_book/importer/jmf/cover_crops_importer.py` | L12 |
| MODIFY | `organic_market_agent/crop_book/importer/tend_overlay.py` (WP-B3) | add `--year` loop for 2019/20/21 |
| MODIFY | `organic_market_agent/crop_book/constants.py` | add `IL_CROP_MAP` Hebrew→DB mapping |
| MODIFY | `organic_market_agent/crop_book/importer/seed.py` | add `--c1-only`, `--no-c1` flags; integrate into `--all` flow |
| MODIFY | `organic_market_agent/crop_book/source_registry.py` | add prefix patterns for `NI:groworganic`, `NI:bustan`, `OP:Idan_*`, `OP:Tend_2019/20/21` (Tend prefix already exists; verify) |
| NEW | `tests/crop_book/test_planting_calendar.py` | 5 tests |
| NEW | `tests/crop_book/test_cover_crops.py` | 4 tests |
| NEW | `tests/crop_book/test_groworganic_importer.py` | 3 tests |
| NEW | `tests/crop_book/test_bustan_importer.py` | 3 tests |
| NEW | `tests/crop_book/test_idan_planning_importer.py` | 4 tests |
| NEW | `tests/crop_book/test_cover_crops_importer.py` | 3 tests |
| NEW | `tests/crop_book/test_tend_multi_year.py` | 3 tests |
| READ-ONLY | All LOD500_LOCKED files (see LOD200 §8) | builder must NOT touch |

## 3. Data model — full DDL

### 3.1 Migration 047 — `crop_planting_calendar`

```python
"""047: Crop planting calendar (WP-C1) — Israeli monthly planting matrix.

Sources: GROWORGANIC.INFO (L01), BUSTAN (L36), and future per-region overlays.
Stores boolean month-columns + activity_type per (crop, source).
"""

from alembic import op
import sqlalchemy as sa

revision = "047"
down_revision = "046"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_planting_calendar",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("region", sa.String(40), nullable=True),
        sa.Column("activity_type", sa.String(20), nullable=False),  # 'seed'|'transplant'|'both'
        sa.Column("season", sa.String(20), nullable=True),
        # 12 monthly boolean columns
        sa.Column("month_jan", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_feb", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_mar", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_apr", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_may", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_jun", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_jul", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_aug", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_sep", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_oct", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_nov", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_dec", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "activity_type IN ('seed','transplant','both')",
            name="ck_cpc_activity_type",
        ),
        sa.CheckConstraint(
            "season IS NULL OR season IN ('spring','summer','fall','winter','all')",
            name="ck_cpc_season",
        ),
        sa.UniqueConstraint("crop_id", "source", "activity_type",
                            name="uq_cpc_crop_source_activity"),
    )
    op.create_index("idx_cpc_crop", "crop_planting_calendar", ["crop_id"])
    op.create_index("idx_cpc_source", "crop_planting_calendar", ["source"])


def downgrade() -> None:
    op.drop_index("idx_cpc_source", "crop_planting_calendar")
    op.drop_index("idx_cpc_crop", "crop_planting_calendar")
    op.drop_table("crop_planting_calendar")
```

### 3.2 Migration 048 — `crop_cover_crops`

```python
"""048: Cover crops chart (WP-C1) — JMF L12 + future cover crop sources.

Standalone table; cover crops are NOT in the `crops` table (they're not
market vegetables). Independent reference.
"""

from alembic import op
import sqlalchemy as sa

revision = "048"
down_revision = "047"


def upgrade() -> None:
    op.create_table(
        "crop_cover_crops",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("name_en", sa.String(60), nullable=False),
        sa.Column("name_he", sa.String(60), nullable=True),
        sa.Column("category", sa.String(40), nullable=False),  # legume|cereal|brassica|other
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("total_days_garden", sa.Integer, nullable=True),
        sa.Column("germination_temp_c_min", sa.Numeric(4, 1), nullable=True),
        sa.Column("hardiness_zone", sa.Integer, nullable=True),
        sa.Column("sow_window", sa.Text, nullable=True),
        sa.Column("inoculum", sa.String(80), nullable=True),
        sa.Column("survives_winter", sa.Boolean, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "category IN ('legume','cereal','brassica','other')",
            name="ck_ccc_category",
        ),
        sa.UniqueConstraint("name_en", "source", name="uq_ccc_name_source"),
    )
    op.create_index("idx_ccc_category", "crop_cover_crops", ["category"])


def downgrade() -> None:
    op.drop_index("idx_ccc_category", "crop_cover_crops")
    op.drop_table("crop_cover_crops")
```

## 4. Importer architecture

### 4.1 GROWORGANIC importer (L01) — `israeli/groworganic_importer.py`

**Source structure** (confirmed by `data/external_sources/sample_extracts/israeli__L01_*.txt`):
- Sheet `גיליון1`, 86 rows × 26 cols
- Row 11 header: `אביב | קיץ | סתיו | חורף` (season banners across columns)
- Row 12 sub-header: `Eqx | S22 | EFS | Eqx | S22 | ECS` (season markers)
- Legend (rows 4-5): `S=שתילים (transplant), X=זרעים (seed)`
- From row ~14: crop name in col A, activity codes per month

**Parsing strategy:**
```python
def parse_groworganic(xlsx_path: Path) -> list[PlantingCalendarRow]:
    """Read L01 GROWORGANIC.INFO and return a list of structured rows.

    Output dataclass:
        PlantingCalendarRow(
            crop_name_he: str,           # from col A of data row
            activity_type: str,           # 'seed'|'transplant'|'both'
            season: str,                  # 'spring'|'summer'|'fall'|'winter'
            month_jan..month_dec: bool,   # 12 booleans
            notes: str | None,
        )
    """
```

**Cell-to-month mapping** (assumed; verify against actual file):
Spring = mar/apr/may; Summer = jun/jul/aug; Fall = sep/oct/nov; Winter = dec/jan/feb.
For each crop row, parse the 4 seasonal subcolumns and explode to monthly booleans.
If cell contains `S` → activity=`transplant`. If `X` → `seed`. If both → split
into 2 rows (one per activity_type) per AC-C1-04.

**Crop name resolution:** use `IL_CROP_MAP` from `constants.py`. If a crop name
does not resolve, log warning + skip (do not insert). Resolution rate must be
≥80% (AC-C1-05).

### 4.2 BUSTAN importer (L36) — `israeli/bustan_importer.py`

**Source:** 1-page PDF with monthly planting matrix. Extract using `pdfplumber`:
```python
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    tables = pdf.pages[0].extract_tables()
```

Fall back: `pdftotext -layout` + regex if `pdfplumber` returns empty.

Legend: `ז=זריעה (seed), ש=שתילה (transplant), ש/ז=both, ז*=seed after germination`.
Each cell maps to its calendar month directly (column header = month name in Hebrew).

### 4.3 IDAN planning importer (L03, L04) — `israeli/idan_planning_importer.py`

Reads two XLSX files with same structure (`L03_IDAN_winter_planning.xlsx`,
`L04_IDAN_summer_planning.xlsx`). Both have sheet `תוכנית גידול`.

Per-row extraction:
- col 1: `גידול` (crop name HE) → resolve via IL_CROP_MAP
- col 2: `זן` (variety)
- col 4: `תאריך שתילה` (planting date — parse multiple formats)
- col 6: `תאריך התחלת אסיף` (harvest start month)
- col 7: `תאריך סיום אסיף` (harvest end month)
- col 10: `מספר שורות בערוגה` → field `rows_per_bed`
- col 11: `מרווח בשורה` → field `in_row_spacing_cm`
- col 12: `מספר צמחים למ"ר` → derived; skip unless explicit
- col 15: `כמות סה"כ` → if numeric+unit, derived `avg_yield_per_bed_m`

Output: rows for `crop_variety_source_values` with `source='OP:Idan_2017'`,
`trust_tier='OP'`, `confidence_weight=0.55`. Plus rows for
`crop_planting_calendar` derived from planting date + harvest window.

Idempotency: upsert by `(variety_id, field_name, source)`.

### 4.4 JMF cover crops importer (L12) — `jmf/cover_crops_importer.py`

1-page PDF — pdfplumber table extraction. Header row identifies columns:
`Cover crop | Total days | Min temp germ | Hardiness zone | When to sow | Inoculum | Survive winter | Note`.

Categories from row groupings: `Legumes (fabaceae)` and `Cereals (grasses)`.

Output: 1 row per cover crop into `crop_cover_crops` with `source='PR:jmf_cover_crops'`,
`trust_tier='PR'`. Hebrew names left NULL (English-only source).

### 4.5 Tend multi-year — extend `tend_overlay.py`

Existing `tend_overlay.py` already accepts `--year` (or year discovered via
`discover_tend_years`). The change is to point it at
`data/external_sources/tend_multi_year/` and pass each of 2019/20/21.

Required modification:
- Refactor `discover_tend_years()` to accept an alternate base path
- In `seed.py`, when `--all` or `--c1-only`, iterate over `[2019, 2020, 2021]`
  and call `tend_overlay.import_year(session, year, base_dir=external_tend_dir)`
- Each year sets `source='Tend_<year>'` (already in SOURCE_REGISTRY pattern)

### 4.6 `IL_CROP_MAP` — Hebrew → DB crop names

New constant in `constants.py`:
```python
IL_CROP_MAP: dict[str, str] = {
    # Hebrew name (as seen in L01/L03/L04/L36) → DB name_he (already in `crops` table)
    "ארוגולה": "ארוגולה",
    "אבטיח": "אבטיח",
    "אפונה": "אפונה",
    "בצל יבש": "בצל",
    "בצל ירוק": "בצל ירוק",
    "ברוקולי": "ברוקולי",
    "חסה ערבית": "חסה",
    "חסה אייסברג": "חסה",
    "חסה": "חסה",
    "כרוב אדום": "כרוב",
    "כרוב לבן": "כרוב",
    "כרובית": "כרובית",
    "כרישה": "כרישה",
    "סלק": "סלק",
    "עגבנית": "עגבניה",
    "עגבנית צ'רי": "עגבניה",
    "צנונית": "צנונית",
    "פלפל": "פלפל",
    "שומר": "שומר",
    "גזר": "גזר",
    "חציל": "חציל",
    "תפוז": "תפוז",
    # ... add ≥30 mappings; builder fills from L01/L03/L04 actual content
}
```

Builder MUST extend this map as needed by reading `data/external_sources/sample_extracts/`
and matching observed Hebrew names to the existing `crops.name_he` column.

## 5. Source-tier integration

Source label patterns are added to `source_registry.py`. Current
`get_source_spec()` already supports prefix-match for `NI:*`, `OP:*`, `PR:*`,
so the registry change is minimal — add explicit mappings if specific source
labels need overrides:

```python
SOURCE_REGISTRY = {
    # ... existing entries ...
    "NI:groworganic":      SourceSpec("NI:groworganic", "NI", weight=None, is_hard_override=True),
    "NI:bustan":           SourceSpec("NI:bustan",      "NI", weight=None, is_hard_override=True),
    "OP:Idan_2017":        SourceSpec("OP:Idan_2017",   "OP", weight=0.55),
    "Tend_2019":           SourceSpec("Tend_2019",      "OP", weight=0.55),
    "Tend_2020":           SourceSpec("Tend_2020",      "OP", weight=0.55),
    "Tend_2021":           SourceSpec("Tend_2021",      "OP", weight=0.55),
    "PR:jmf_cover_crops":  SourceSpec("PR:jmf_cover_crops", "PR", weight=0.70),
}
```

(Verify existing pattern doesn't already cover these via prefix match — if so,
explicit entries are optional but improve clarity.)

## 6. Crop-name mapping (Hebrew → DB)

**Strategy:** read all sample_extracts files, collect every distinct Hebrew crop
name, generate proposed `IL_CROP_MAP` entries. Builder presents the map to
team_00 for confirmation BEFORE first ingestion run (CALL OUT in BUILD_REPORT).

Failure mode: if any Hebrew crop name is unmappable → log + skip + record in
`_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/UNMAPPED_CROPS_v1.0.0.md`.

## 7. CLI integration

Modifications to `organic_market_agent/crop_book/importer/seed.py`:

```python
parser.add_argument("--c1-only", action="store_true",
    help="Run WP-C1 importers only (Israeli structured + Tend multi-year)")
parser.add_argument("--no-c1", action="store_true",
    help="Skip WP-C1 importers when --all is used")
```

`--all` flow extension (per LOD400 §13 of WP-B3 precedent):
```python
if args.all and not args.no_c1:
    from organic_market_agent.crop_book.importer.israeli import (
        groworganic_importer, bustan_importer, idan_planning_importer,
    )
    from organic_market_agent.crop_book.importer.jmf import cover_crops_importer
    from organic_market_agent.crop_book.importer import tend_overlay

    logger.info("WP-C1: Running Israeli structured data + Tend multi-year backfill")
    groworganic_importer.import_all(session, Path("data/external_sources/israeli/L01_GROWORGANIC_sowing_dates_base.xlsx"))
    bustan_importer.import_all(session, Path("data/external_sources/israeli/L36_BUSTAN_sowing_calendar.pdf"))
    idan_planning_importer.import_all(session,
        Path("data/external_sources/israeli/L03_IDAN_winter_planning.xlsx"),
        Path("data/external_sources/israeli/L04_IDAN_summer_planning.xlsx"))
    cover_crops_importer.import_all(session, Path("data/external_sources/jmf_extension/L12_cover_crop_chart.pdf"))
    for year in (2019, 2020, 2021):
        tend_overlay.import_year(session, year,
            base_dir=Path("data/external_sources/tend_multi_year"))
    summary = run_enrichment(session, dry_run=False)
    session.commit()
```

## 8. Test plan

| File | Tests | What they verify |
|------|------:|------------------|
| `test_planting_calendar.py` | 5 | migration 047 fwd/bwd, ORM round-trip, unique constraint, season+activity CHECK |
| `test_cover_crops.py` | 4 | migration 048 fwd/bwd, ORM round-trip, category CHECK |
| `test_groworganic_importer.py` | 3 | parse 86 rows, seasonal markers decoded, S/X activity mapping |
| `test_bustan_importer.py` | 3 | PDF table extract, Hebrew month resolution, legend handling |
| `test_idan_planning_importer.py` | 4 | L03 winter parse, L04 summer parse, summary-row skip, planting-date parsing |
| `test_cover_crops_importer.py` | 3 | parse 1-page PDF, category grouping, temp/zone numeric coercion |
| `test_tend_multi_year.py` | 3 | 2019/2020/2021 year-loop, idempotent re-import, harvest aggregation counts |

**Total: ≥25 tests.**

## 9. Acceptance Criteria matrix

| AC | Description | Status target |
|----|-------------|---------------|
| AC-C1-01 | Migration 047 (`crop_planting_calendar`) applies cleanly fwd/bwd on PG + SQLite | PASS |
| AC-C1-02 | Migration 048 (`crop_cover_crops`) applies cleanly fwd/bwd on PG + SQLite | PASS |
| AC-C1-03 | `groworganic_importer` parses L01 → ≥30 rows in `crop_planting_calendar` | PASS |
| AC-C1-04 | If `S` and `X` both present in same season cell, importer emits 2 rows (one seed, one transplant) | PASS |
| AC-C1-05 | `IL_CROP_MAP` resolves ≥80% of distinct Hebrew names found in L01+L03+L04+L36 | PASS |
| AC-C1-06 | `bustan_importer` extracts ≥20 crops with month booleans from 1-page PDF | PASS |
| AC-C1-07 | `idan_planning_importer` round-trips L03 (203 rows) + L04 (150 rows) into `crop_variety_source_values` with `source='OP:Idan_2017'` | PASS |
| AC-C1-08 | `cover_crops_importer` populates `crop_cover_crops` with ≥10 rows including germination temp + hardiness zone | PASS |
| AC-C1-09 | Tend 2019 ingestion: 442 CROP_PLAN rows parsed, 1,884 HARVESTS aggregated to `crop_harvest_stats` | PASS |
| AC-C1-10 | Tend 2020 ingestion: 724 CROP_PLAN parsed, 3,720 HARVESTS aggregated | PASS |
| AC-C1-11 | Tend 2021 ingestion: 552 CROP_PLAN parsed, 1,723 HARVESTS aggregated | PASS |
| AC-C1-12 | Reconciler picks up new sources without code change — `reconcile_field()` returns blended values where multiple sources cover same (variety, field) | PASS |
| AC-C1-13 | `validate_enrichment.py` shadow-run shows ≥3 new (variety, field) pairs reaching `CALIBRATED` status | PASS |
| AC-C1-14 | `seed.py --c1-only` runs all 5 new importers + Tend 3 years; `--no-c1` skips them all; `--all` includes them by default | PASS |
| AC-C1-15 | All importers idempotent (re-run produces no duplicate rows) | PASS |
| AC-C1-16 | `validate_aos.sh` returns 29 PASS / 19 SKIP / 0 FAIL | PASS |
| AC-C1-17 | Test suite ≥25 new tests; existing tests 0 regressions | PASS |
| AC-C1-18 | No LOD500_LOCKED file modified | PASS |
| AC-C1-19 | `UNMAPPED_CROPS_v1.0.0.md` filed if any Hebrew crop names unresolved | PASS |
| AC-C1-20 | Build report at `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md` | PASS |

## 10. Verification commands

```bash
# After build complete:
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. Migrations
alembic upgrade head
alembic downgrade 046 && alembic upgrade head  # smoke-test reversibility

# 2. Focused C1 tests
python3 -m pytest \
  tests/crop_book/test_planting_calendar.py \
  tests/crop_book/test_cover_crops.py \
  tests/crop_book/test_groworganic_importer.py \
  tests/crop_book/test_bustan_importer.py \
  tests/crop_book/test_idan_planning_importer.py \
  tests/crop_book/test_cover_crops_importer.py \
  tests/crop_book/test_tend_multi_year.py

# 3. Full suite
python3 -m pytest tests/

# 4. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 5. Live ingestion + enrichment
python3 -m organic_market_agent.crop_book.importer.seed --c1-only
python3 scripts/validate_enrichment.py  # expect more CALIBRATED rows than baseline

# 6. DB sanity
python3 -c "
import sys; sys.path.insert(0,'.')
import sqlalchemy as sa
from organic_market_agent.db.session import SessionFactory
import organic_market_agent.crop_book.planting_calendar
import organic_market_agent.crop_book.cover_crops
with SessionFactory() as s:
    print('crop_planting_calendar rows:', s.execute(sa.text('SELECT COUNT(*) FROM crop_planting_calendar')).scalar())
    print('crop_cover_crops rows:', s.execute(sa.text('SELECT COUNT(*) FROM crop_cover_crops')).scalar())
    print('crop_harvest_stats rows:', s.execute(sa.text('SELECT COUNT(*) FROM crop_harvest_stats')).scalar())
"
```

## 11. Build sequence (numbered)

1. Create 2 migration files (047, 048) + run `alembic upgrade head`
2. Create 2 ORM modules (`planting_calendar.py`, `cover_crops.py`)
3. Extend `constants.py` with `IL_CROP_MAP` (use sample_extracts as input)
4. Extend `source_registry.py` with new source patterns
5. Build `israeli/groworganic_importer.py` + tests
6. Build `israeli/bustan_importer.py` + tests
7. Build `israeli/idan_planning_importer.py` + tests
8. Build `jmf/cover_crops_importer.py` + tests
9. Extend `tend_overlay.py` for multi-year support
10. Wire into `seed.py` (`--c1-only`, `--no-c1`, `--all` flow)
11. Run full focused-test suite (expect ≥25 new tests passing)
12. Run live ingestion against PG; verify DB sanity counts
13. Run `validate_aos.sh` (expect 29/19/0)
14. Write BUILD_REPORT + UNMAPPED_CROPS (if any)

## 12. LOD500_LOCKED inventory check

Builder must verify before commit:
```bash
git status --short | grep -E '(views\.py|publisher/wp_upload|publisher/upload_dispatch|db/versions/00[1-9]_|db/versions/0[1-3][0-9]_|db/versions/04[0-6]_|mu-plugin|tend\.py$)' \
  && echo "VIOLATION" || echo "OK"
```

## 13. Risk register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|:---:|:---:|------------|
| R-C1-01 | `pdfplumber` table extraction fails on L36 / L12 1-page PDFs | MED | MED | Fall back to `pdftotext -layout` + regex; if still fails, manual JSON cache committed |
| R-C1-02 | `IL_CROP_MAP` resolution rate <80% (AC-C1-05 fail) | MED | HIGH | Pre-flight: parse all sample_extracts, build candidate map, surface ambiguities to team_00 BEFORE first run |
| R-C1-03 | Tend 2019/20/21 schema differs from 2022 (column rename) | LOW | MED | Parse header row per file; emit warning + skip incompatible columns |
| R-C1-04 | New `NI:groworganic` rows shadow existing JMF PR data → calibration regression | LOW | LOW | Expected: NI hard-override is by design. `validate_enrichment.py` will show the shift |
| R-C1-05 | `crop_harvest_stats` UNIQUE collision on multi-year re-import | LOW | LOW | Upsert by `(crop_id, season, year, source)` per WP-B3 contract |

## 14. Constitutional rule traceability

| AC | IR enforced |
|----|-------------|
| AC-C1-01..02 | IR#7 (DB structural mutations via migration, not direct SQL) |
| AC-C1-12, 13 | IR#5 (validator team_190 is the gate, this is just self-verification) |
| AC-C1-18 | LOD500_LOCKED integrity rule |
| AC-C1-19, 20 | IR#6 (canonical artifacts in `_COMMUNICATION/`) |

---

*LOD400 authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.
Ready for team_190 L-GATE_S validation OR direct builder activation per
team_00's preference.*
