---
id: SFA-S003-P002-WP-C4-LOD400
wp: SFA-S003-P002-WP-C4 — Web Sources (multi-engine team_80 consolidated)
gate: L-GATE_S (LOD400)
status: LOD400_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD200_spec.md
consolidated_findings_ref: _COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/CONSOLIDATED_FINDINGS_v1.0.0.md
input_findings:
  - team_80 OpenAI engine output (provided by team_00 2026-05-26)
  - team_80 Perplexity engine output (provided by team_00 2026-05-26)
  - team_80 Gemini engine output (provided by team_00 2026-05-26, partial)
---

# LOD400 — WP-C4: Web Sources Integration

## 1. Mission

Ingest 8 consolidated web sources (CW-01 through CW-08) identified by team_80's
multi-engine scout. Three sources address HIGH-priority gaps (germination
temperature, frost tolerance, soil pH); one addresses the CRITICAL gap of
Israeli planting calendar (CW-05); three address MEDIUM gaps; one addresses
LOW gap (postharvest storage). 3 INVESTIGATE_FURTHER sources (CW-09..CW-11)
deferred to future WP.

## 2. File-by-file delta

| Action | Path | Purpose |
|--------|------|---------|
| NEW | `organic_market_agent/db/versions/050_extend_planting_calendar_israeli.py` | extend region enum |
| NEW | `organic_market_agent/db/versions/051_crop_companion_matrix.py` | new table |
| NEW | `organic_market_agent/db/versions/052_crop_postharvest_storage.py` | new table |
| NEW | `organic_market_agent/crop_book/companion_matrix.py` | ORM for `crop_companion_matrix` |
| NEW | `organic_market_agent/crop_book/postharvest_storage.py` | ORM for `crop_postharvest_storage` |
| NEW | `organic_market_agent/crop_book/importer/web/__init__.py` | importer package |
| NEW | `organic_market_agent/crop_book/importer/web/uc_anr_germination.py` | CW-01 |
| NEW | `organic_market_agent/crop_book/importer/web/osu_frost_tolerance.py` | CW-02 |
| NEW | `organic_market_agent/crop_book/importer/web/umd_soil_ph.py` | CW-03 |
| NEW | `organic_market_agent/crop_book/importer/web/ne_veg_guide_nutrients.py` | CW-04 |
| NEW | `organic_market_agent/crop_book/importer/web/il_moa_calendar.py` | CW-05 (Israeli — CRITICAL) |
| NEW | `organic_market_agent/crop_book/importer/web/seeds_per_gram.py` | CW-06 |
| NEW | `organic_market_agent/crop_book/importer/web/uf_ifas_companion.py` | CW-07 |
| NEW | `organic_market_agent/crop_book/importer/web/uc_davis_postharvest.py` | CW-08 |
| NEW | `scripts/download_web_sources.py` | one-time download of all PDFs + HTML scrapes to `data/external_sources/web/` |
| MODIFY | `organic_market_agent/crop_book/importer/seed.py` | add `--c4-only`, `--no-c4` flags; integrate into `--all` |
| MODIFY | `organic_market_agent/crop_book/source_registry.py` | add 8 new `PR:*` + 2 `OP:*` + 2 `NI:*` source patterns |
| NEW | `data/external_sources/web/` | downloaded + cached source files (gitignored binaries, JSON extracts committed) |
| NEW | `tests/crop_book/test_c4_*.py` (one per importer + integration) | ≥20 tests |
| READ-ONLY | All LOD500_LOCKED files | builder must NOT touch |

## 3. Data model — full DDL

### 3.1 Migration 050 — extend `crop_planting_calendar.region`

The C1 table accepts free-text `region`. Add convention enum for IL regions
(documentation, not enforced):
- `IL_general` (default Israel)
- `IL_north` / `IL_center` / `IL_south` (zone-specific)
- `MED_general` (Mediterranean)

```python
"""050: document region conventions for crop_planting_calendar (additive comment only)"""
from alembic import op
revision = "050"
down_revision = "049"

def upgrade() -> None:
    # No DDL change — convention documented in comment + ORM docstring
    pass

def downgrade() -> None:
    pass
```

(Migration is a no-op placeholder for ordering; convention is documented in
`planting_calendar.py` ORM docstring.)

### 3.2 Migration 051 — `crop_companion_matrix`

```python
"""051: Crop companion planting matrix (WP-C4 / CW-07)"""
from alembic import op
import sqlalchemy as sa

revision = "051"
down_revision = "050"

def upgrade() -> None:
    op.create_table(
        "crop_companion_matrix",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_a_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("crop_b_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("compatibility", sa.String(20), nullable=False),  # beneficial|neutral|antagonistic
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("evidence_strength", sa.String(20), nullable=True),  # strong|weak|anecdotal
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint("compatibility IN ('beneficial','neutral','antagonistic')",
                           name="ck_ccm_compat"),
        sa.CheckConstraint("crop_a_id != crop_b_id", name="ck_ccm_no_self"),
        sa.UniqueConstraint("crop_a_id", "crop_b_id", "source", name="uq_ccm"),
    )
    op.create_index("idx_ccm_a", "crop_companion_matrix", ["crop_a_id"])
    op.create_index("idx_ccm_b", "crop_companion_matrix", ["crop_b_id"])

def downgrade() -> None:
    op.drop_index("idx_ccm_b", "crop_companion_matrix")
    op.drop_index("idx_ccm_a", "crop_companion_matrix")
    op.drop_table("crop_companion_matrix")
```

### 3.3 Migration 052 — `crop_postharvest_storage`

```python
"""052: Postharvest storage conditions (WP-C4 / CW-08 — UC Davis Cantwell)"""
from alembic import op
import sqlalchemy as sa

revision = "052"
down_revision = "051"

def upgrade() -> None:
    op.create_table(
        "crop_postharvest_storage",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("storage_temp_c_min", sa.Numeric(4, 1), nullable=True),
        sa.Column("storage_temp_c_max", sa.Numeric(4, 1), nullable=True),
        sa.Column("rh_pct_min", sa.Integer, nullable=True),
        sa.Column("rh_pct_max", sa.Integer, nullable=True),
        sa.Column("freezing_point_c", sa.Numeric(4, 1), nullable=True),
        sa.Column("ethylene_production", sa.String(20), nullable=True),   # VL/L/M/H/VH
        sa.Column("ethylene_sensitivity", sa.String(20), nullable=True),  # L/M/H
        sa.Column("storage_life_days_min", sa.Integer, nullable=True),
        sa.Column("storage_life_days_max", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("crop_id", "source", name="uq_cps_crop_source"),
    )
    op.create_index("idx_cps_crop", "crop_postharvest_storage", ["crop_id"])

def downgrade() -> None:
    op.drop_index("idx_cps_crop", "crop_postharvest_storage")
    op.drop_table("crop_postharvest_storage")
```

### 3.4 Source registry additions

```python
SOURCE_REGISTRY = {
    # ... existing C1/C2/C3 entries ...
    "PR:uc_anr_germination":      SourceSpec("PR:uc_anr_germination",      "PR", 0.70),
    "PR:purdue_germination":      SourceSpec("PR:purdue_germination",      "PR", 0.70),  # cross-val
    "PR:osu_frost_tolerance":     SourceSpec("PR:osu_frost_tolerance",     "PR", 0.70),
    "PR:csu_planting_guide":      SourceSpec("PR:csu_planting_guide",      "PR", 0.70),  # cross-val
    "PR:umn_field_planning":      SourceSpec("PR:umn_field_planning",      "PR", 0.70),  # cross-val
    "PR:umd_soil_ph":             SourceSpec("PR:umd_soil_ph",             "PR", 0.70),
    "PR:ne_veg_guide":            SourceSpec("PR:ne_veg_guide",            "PR", 0.70),
    "PR:fao_fertilizer_use":      SourceSpec("PR:fao_fertilizer_use",      "PR", 0.70),  # supplement
    "NI:il_moa_garden_guide":     SourceSpec("NI:il_moa_garden_guide",     "NI", None, is_hard_override=True),
    "NI:shaham_extension":        SourceSpec("NI:shaham_extension",        "NI", None, is_hard_override=True),
    "OP:vital_seeds_count":       SourceSpec("OP:vital_seeds_count",       "OP", 0.55),
    "OP:osborne_seed_count":      SourceSpec("OP:osborne_seed_count",      "OP", 0.55),
    "PR:uf_ifas_companion":       SourceSpec("PR:uf_ifas_companion",       "PR", 0.70),
    "PR:uc_davis_postharvest":    SourceSpec("PR:uc_davis_postharvest",    "PR", 0.70),
}
```

### 3.5 New `crop_variety_source_values.field_name` values

Add to FIELD_POLICY if blendable:
- `germination_temp_c_min`, `germination_temp_c_opt`, `germination_temp_c_max` (weighted_mean across sources)
- `frost_tolerance_class` (hard_winner — categorical, NOT blendable)
- `soil_ph_target`, `soil_ph_liming_threshold` (weighted_mean)
- `nutrient_removal_n_kg_ha`, `nutrient_removal_p_kg_ha`, `nutrient_removal_k_kg_ha`, `nutrient_removal_ca_kg_ha`, `nutrient_removal_mg_kg_ha` (weighted_mean with assumed_yield_t_ha context)
- `seeds_per_gram` (weighted_mean)

## 4. Importer architecture — per-source

Each web importer follows the same 4-step pattern:
1. **Pre-flight**: Verify `data/external_sources/web/<source>/<file>` exists. If not, instruct user to run `scripts/download_web_sources.py --source <name>`.
2. **Parse**: source-specific (HTML scrape via BeautifulSoup OR PDF table via pdfplumber)
3. **Normalize**: unit conversion (°F→°C, lbs/A→kg/ha, etc.), crop-name resolution via `IL_CROP_MAP` + new `EN_CROP_MAP`
4. **Upsert**: into `crop_variety_source_values` OR new tables, with source label + trust_tier

### 4.1 CW-01 UC ANR germination (`web/uc_anr_germination.py`)

```python
def parse_uc_anr_germination(pdf_path: Path) -> list[dict]:
    """Parse UC ANR Garden Notes 164220 PDF.
    Each row: Crop | Minimum °F | Optimum range °F | Maximum °F
    Convert °F → °C: c = (f - 32) * 5/9
    Output: list of dicts ready for upsert with field_names:
      germination_temp_c_min, germination_temp_c_opt, germination_temp_c_max
    """
```

### 4.2 CW-02 OSU frost tolerance (`web/osu_frost_tolerance.py`)

Parse OSU HTML chart. Map vegetable lists to `frost_tolerance_class` enum:
- "Hardy" → `hardy`
- "Semi-hardy" / "Half-hardy" → `semi_hardy`
- "Tender" → `tender`
- "Very tender" / "Cold-sensitive" → `very_tender`

Cross-validate with CSU + UMN (parse all 3 if scrapeable). For each crop:
- If 2/3 sources agree → use agreed class
- If all 3 disagree → log + use most-conservative (most-tender) class

### 4.3 CW-03 UMD soil pH (`web/umd_soil_ph.py`)

1-page PDF — pdfplumber table extraction. Per-crop fields: target pH + liming threshold.

### 4.4 CW-04 NE Veg Guide nutrients (`web/ne_veg_guide_nutrients.py`)

HTML scrape (BeautifulSoup). Tabular: crop | yield/A | N | P2O5 | K2O | Ca | Mg.
Unit conversion: lbs/A → kg/ha (factor 1.12085). P2O5 → P (× 0.4364), K2O → K (× 0.8301).

### 4.5 CW-05 IL MoA + Shaham (`web/il_moa_calendar.py`) — **CRITICAL**

This is the gap OpenAI couldn't fill. Implementation strategy:
1. Download Israeli MoA home vegetable garden guide PDF
2. Download Shaham extension PDFs (multiple, one per crop group)
3. Hebrew handling per WP-C2 pattern (UTF-8 raw, no escape)
4. Extract per crop: planting months, region (default `IL_general`)
5. Upsert to `crop_planting_calendar` with `source='NI:il_moa_garden_guide'` + `NI:shaham_extension`
6. NI tier (hard override over GROWORGANIC + Bustan from C1)

**Acceptance for this source specifically (AC-C4-05a/b)**: must produce ≥30
crop-month entries for Israeli planting calendar.

### 4.6 CW-06 Seeds per gram (`web/seeds_per_gram.py`)

Cross-validate Vital Seeds + Osborne. For each crop appearing in both:
- If diff < 20% → use mean
- If diff > 20% → log + flag for manual review

### 4.7 CW-07 UF/IFAS companion (`web/uf_ifas_companion.py`)

Parse companion matrix → insert pairs (crop_a, crop_b, compatibility) into
`crop_companion_matrix`. De-dup symmetric pairs (a,b) = (b,a).

**Evidence strength field**: mark all UF/IFAS rows as `weak` per academic
consensus on companion planting evidence.

### 4.8 CW-08 UC Davis postharvest (`web/uc_davis_postharvest.py`)

pdfplumber on Cantwell PDF. Per-row: crop scientific name + storage conditions.
Map scientific names to existing crops via Latin name lookup (introduce
`crops.scientific_name` index lookup).

## 5. Download harness — `scripts/download_web_sources.py`

```python
"""One-time download of all WP-C4 web sources to data/external_sources/web/<source>/.

Usage:
    python3 scripts/download_web_sources.py --source all
    python3 scripts/download_web_sources.py --source uc_anr_germination
"""

SOURCES = {
    "uc_anr_germination": "https://ucanr.edu/sites/default/files/2017-11/164220.pdf",
    "purdue_germination": "https://ag.purdue.edu/department/hla/extension/extension-publications-library/ext-pubs/ho-186-w.html",
    "osu_frost_tolerance": "<URL from Perplexity CS-02>",
    "csu_planting_guide": "https://extension.colostate.edu/resource/vegetable-planting-guide/",
    "umn_field_planning": "https://extension.umn.edu/vegetable-growing-guides-farmers/crop-and-field-planning-tools-vegetable-farmers",
    "umd_soil_ph": "https://extension.umd.edu/sites/extension.umd.edu/files/2021-03/B-1.pdf",
    "ne_veg_guide_nutrients": "https://nevegetable.org/cultural-practices/removal-nutrients-soil",
    "fao_fertilizer_use": "<URL from Perplexity CS-07>",
    "il_moa_garden_guide": "<URL from Perplexity CS-10 — confirm>",
    "shaham_extension": "<URL from Gemini CS-05 — confirm>",
    "vital_seeds_count": "<URL from Perplexity CS-04>",
    "osborne_seed_count": "<URL from Gemini CS-03>",
    "uf_ifas_companion": "<URL from Perplexity CS-05>",
    "uc_davis_postharvest": "https://extension.k-state.edu/foodsafety/produce/resources/docs/storage-guidelines-UCDavis.pdf",
}
```

Builder MUST verify each URL accessible during download; if any URL fails, fall
back: (a) try Wayback Machine snapshot; (b) document inaccessibility in
BUILD_REPORT and skip the source.

## 6. CLI integration

```python
parser.add_argument("--c4-only", action="store_true",
    help="Run WP-C4 web-source importers only")
parser.add_argument("--no-c4", action="store_true",
    help="Skip WP-C4 importers when --all is used")
```

`--all` flow (extend C1 pattern):
```python
if args.all and not args.no_c4:
    from organic_market_agent.crop_book.importer.web import (
        uc_anr_germination, osu_frost_tolerance, umd_soil_ph,
        ne_veg_guide_nutrients, il_moa_calendar, seeds_per_gram,
        uf_ifas_companion, uc_davis_postharvest,
    )
    logger.info("WP-C4: Web sources ingestion (8 importers)")
    for module in [uc_anr_germination, osu_frost_tolerance, umd_soil_ph,
                   ne_veg_guide_nutrients, il_moa_calendar, seeds_per_gram,
                   uf_ifas_companion, uc_davis_postharvest]:
        module.import_all(session)
    summary = run_enrichment(session, dry_run=False)
    session.commit()
```

## 7. Test plan (≥20 tests)

| File | Tests | What they verify |
|------|------:|------------------|
| `test_c4_uc_anr_germination.py` | 3 | parse PDF, °F→°C conversion, upsert |
| `test_c4_osu_frost_tolerance.py` | 3 | parse HTML, class mapping, cross-source reconciliation |
| `test_c4_umd_soil_ph.py` | 2 | parse PDF, target+liming fields |
| `test_c4_ne_veg_guide.py` | 3 | parse HTML, unit conversion (lbs/A→kg/ha, P2O5→P) |
| `test_c4_il_moa_calendar.py` | 4 | PDF parse, Hebrew preservation, calendar upsert, NI hard-override |
| `test_c4_seeds_per_gram.py` | 2 | cross-validation Vital vs Osborne, ±20% diff log |
| `test_c4_uf_ifas_companion.py` | 2 | matrix parse, symmetric de-dup |
| `test_c4_uc_davis_postharvest.py` | 2 | PDF parse, scientific name lookup, ethylene classification |
| `test_c4_migrations.py` | 3 | migrations 050/051/052 fwd+bwd |
| `test_c4_integration.py` | 2 | full --c4-only run + reconcile_field blends new sources |

## 8. Acceptance Criteria matrix

| AC | Description |
|----|-------------|
| AC-C4-01 | Migrations 050+051+052 apply cleanly fwd+bwd on PG + SQLite |
| AC-C4-02 | `download_web_sources.py --source all` succeeds for ≥10 of 14 source URLs (≥70%); inaccessible ones documented |
| AC-C4-03 | CW-01 UC ANR germination: ≥20 crops parsed; °F→°C conversion verified by hand-spot-check 3 crops |
| AC-C4-04 | CW-02 frost tolerance: 3-source cross-validation produces single class per crop for ≥15 crops |
| AC-C4-05 | CW-03 UMD pH: ≥30 crops have `soil_ph_target` populated |
| AC-C4-06 | CW-04 NPK removal: ≥15 crops have NPK in kg/ha with `assumed_yield_t_ha` context |
| AC-C4-07 | CW-05 IL MoA + Shaham: ≥30 crop-month entries in `crop_planting_calendar` with `source LIKE 'NI:il_%' OR source = 'NI:shaham_extension'` |
| AC-C4-08 | CW-05 Hebrew preservation: no `\uXXXX` escapes in resulting DB rows or JSON cache |
| AC-C4-09 | CW-06 seeds per gram: ≥10 crops have value; ≥3 cross-validated across Vital + Osborne |
| AC-C4-10 | CW-07 companion: ≥20 pair-rows in `crop_companion_matrix`; all marked `evidence_strength='weak'` |
| AC-C4-11 | CW-08 postharvest: ≥30 crops in `crop_postharvest_storage` |
| AC-C4-12 | Reconciler picks up new PR-tier sources; ≥5 (variety, field) pairs reach CALIBRATED in `validate_enrichment.py` shadow run |
| AC-C4-13 | NI:il_moa_garden_guide + NI:shaham_extension correctly hard-override GROWORGANIC/Bustan from C1 (verified by query) |
| AC-C4-14 | `seed.py --c4-only` + `--no-c4` + `--all` flow works |
| AC-C4-15 | Tests ≥20 passing; existing tests 0 regressions |
| AC-C4-16 | `validate_aos.sh` returns 29 PASS / 19 SKIP / 0 FAIL |
| AC-C4-17 | No LOD500_LOCKED file modified |
| AC-C4-18 | URL accessibility audit committed: `_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/URL_AUDIT_v1.0.0.md` |
| AC-C4-19 | License compliance audit: each source's TOS reviewed; flagged if any conflict |
| AC-C4-20 | BUILD_REPORT filed with per-source row counts + cross-validation reconciliation log |

## 9. Verification commands

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# Download web sources (one-time)
python3 scripts/download_web_sources.py --source all

# Migrations
alembic upgrade head
alembic downgrade 049 && alembic upgrade head

# Tests
python3 -m pytest tests/crop_book/test_c4_*.py

# Live ingestion
python3 -m organic_market_agent.crop_book.importer.seed --c4-only

# Validate
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# Israeli source sanity
python3 -c "
import sys; sys.path.insert(0,'.')
import sqlalchemy as sa
from organic_market_agent.db.session import SessionFactory
with SessionFactory() as s:
    n = s.execute(sa.text(\"SELECT COUNT(*) FROM crop_planting_calendar WHERE source LIKE 'NI:il_%'\")).scalar()
    print(f'IL MoA + Shaham rows: {n}')
    assert n >= 30, 'AC-C4-07 FAILED'
"
```

## 10. Build sequence
1. Migrations 050+051+052 + apply
2. ORM modules (companion_matrix.py, postharvest_storage.py)
3. Extend source_registry.py
4. Build download_web_sources.py + run with `--source all`
5. URL accessibility audit + write URL_AUDIT_v1.0.0.md
6. Build CW-05 IL MoA first (highest priority gap-fill) + tests
7. Build CW-01 germination + tests
8. Build CW-02 frost tolerance + cross-validation + tests
9. Build CW-03/04 soil pH + NPK + tests
10. Build CW-06/07 seeds + companion + tests
11. Build CW-08 postharvest + tests
12. Wire into seed.py
13. Full test pass; live ingestion; validate_aos.sh
14. BUILD_REPORT + URL_AUDIT + LICENSE_AUDIT

## 11. Risk register

| Risk | Probability | Impact | Mitigation |
|------|:---:|:---:|------------|
| Source URL goes dead between download and re-run | MED | LOW | Cache all downloads in `data/external_sources/web/<source>/`; never re-fetch at runtime |
| Hebrew encoding loss in Israeli source PDFs | LOW | HIGH | UTF-8 strict mode; test AC-C4-08 |
| Shaham PDFs are scanned (need OCR) | MED | MED | If pdfplumber returns empty → Anthropic Vision API one-time (~$5 budget) |
| License/TOS prohibits storage of full source | LOW | HIGH | Store DERIVED VALUES only (numbers); never store raw prose from sites with restrictive TOS |
| Cross-validation 3-engine frost tolerance disagrees | MED | LOW | Default to most-conservative (most-tender) class + log |
| FAO ECOCROP 403 errors (already seen in scout) | known | LOW | Skipped from this WP; defer to follow-up |

## 12. Constitutional rule traceability
| AC | IR enforced |
|----|-------------|
| AC-C4-01 | IR#7 (DB structural changes via migration) |
| AC-C4-08, 13 | IR#7 + Hebrew-encoding governance |
| AC-C4-17 | LOD500_LOCKED integrity |
| AC-C4-18, 19, 20 | IR#6 (canonical artifacts) |

---
*LOD400 authored by team_10 (Claude Sonnet 4.7) 2026-05-26 under team_00 grant.
Multi-engine team_80 input synthesized in CONSOLIDATED_FINDINGS_v1.0.0.md.
Ready for builder activation (separate WP-C4 builder mandate to follow).*
