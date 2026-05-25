---
id: SFA-S003-P002-WP-B3-LOD400
wp: SFA-S003-P002-WP-B3 — Tend Israel Adaptation Overlay
gate: L-GATE_S (LOD400 — implementation spec)
status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S verdict
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD200_spec.md
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
wp_a_lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md
wp_b1_lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
team_00_whitelist_decision_date: 2026-05-25
team_00_whitelist_decision: "Option B (extended): 9 original + Trellis + Fertilize & Amend = 11 categories whitelisted; 6 new task_type enum values"
builder: sfa_build (separate session per IR#1)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B3: Tend Israel Adaptation Overlay

**Read before writing a single line of code:**
1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD200_spec.md`
2. PROGRAM_BRIEF §4 (Tend scope reference): `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`
3. WP-B1 LOD400 (parent — LOD500_LOCKED — read-only): `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`. §3+§4 define `crop_task_templates` schema + ORM that this patch extends.
4. WP-A engine SSoT (read-only):
   - `organic_market_agent/crop_book/source_registry.py` — `Tend_<year>` OP-class entries
   - `organic_market_agent/crop_book/importer/reconciler.py` — `Candidate` / `FieldConsensus` / `reconcile_field()` API
   - `organic_market_agent/crop_book/importer/enrichment_runner.py` — `run_enrichment(session)` entry point
   - `organic_market_agent/crop_book/models.py` — `CropVarietySourceValue` columns
5. **Existing raw-material guard** (DO NOT MODIFY): `organic_market_agent/crop_book/importer/tend.py`. B3 introduces a separate `tend_overlay.py` for clarity.

---

## 1. Goal

Build the **Tend Israel adaptation overlay** that layers Israeli local farm-operations data (OP tier, weight `0.55`) on top of the JMF PR baseline. Implementation:

1. **Migration 046** — new table `crop_harvest_stats` + ALTER `crop_task_templates` CHECK constraint adding 6 new `task_type` values
2. **New ORM module** `organic_market_agent/crop_book/crop_harvest_stats.py`
3. **GCR-B3-1** (REQUIRES team_00 sign-off): extend the LOD500_LOCKED `TASK_TYPE_VALUES` tuple in `crop_task_templates.py` by appending exactly 6 entries
4. **New importer** `organic_market_agent/crop_book/importer/tend_overlay.py` with 3 sub-parsers + orchestrator + upsert helpers
5. **`TEND_TASK_TYPE_MAP` constant** appended to `constants.py` (Tend label → JMF `task_type` mapping)
6. **`seed.py` CLI additions** — `--tend-overlay-only`, `--no-tend-overlay`
7. **≥ 20 tests** covering whitelist enforcement, task-type mapping, aggregation correctness, DB integration, idempotency, no-per-record assertion for HARVESTS
8. **WP-A engine reuse only** — 2 blendable scalar fields (`days_in_gh_total`, `days_to_first_potting`) go through `_upsert_source_value` → `reconcile_field()`. Task-template rows go directly into `crop_task_templates` (extension of B1's table). Harvest stats go into the NEW `crop_harvest_stats` table (terminal — no engine integration).

team_00 confirmed whitelist on 2026-05-25 (Option B — see §6).

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/crop_book/
├── constants.py                     ← MODIFY: append TEND_TASK_TYPE_MAP (11 entries)
├── crop_task_templates.py           ← MODIFY (GCR-B3-1): append 6 entries to TASK_TYPE_VALUES tuple
├── crop_harvest_stats.py            ← NEW: CropHarvestStat SQLAlchemy ORM class
└── importer/
    ├── tend_overlay.py              ← NEW: 3 parsers + orchestrator + upsert helpers
    └── seed.py                      ← MODIFY: --tend-overlay-only, --no-tend-overlay flags + 1 new call-site block

organic_market_agent/db/versions/
└── 046_tend_overlay.py              ← NEW: crop_harvest_stats + ALTER CHECK constraint

tests/crop_book/
├── test_tend_overlay_parsers.py            ← NEW
├── test_tend_task_whitelist.py             ← NEW
├── test_tend_task_type_mapping.py          ← NEW
├── test_tend_overlay_aggregation.py        ← NEW
├── test_tend_overlay_integration.py        ← NEW
├── test_tend_idempotency.py                ← NEW
├── test_crop_harvest_stats_orm.py          ← NEW
├── test_migration_046.py                   ← NEW
└── test_seed_tend_overlay_cli.py           ← NEW

CHANGELOG.md                                ← MODIFY: [Unreleased] entry
```

### 2.2 No changes to these files (LOD500_LOCKED beyond GCR-B3-1)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/views.py`, `publisher/`, `mu-plugin/` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..045_*.py` | All prior migrations (045 reserved for B2; check at build time that B2's 045 is committed before B3 runs `alembic upgrade 046` — if B2 hasn't landed, builder files inquiry) |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard (CLAUDE.md) — B3 uses a NEW module `tend_overlay.py` |
| `organic_market_agent/crop_book/importer/jmf.py`, `jmf_masterclass.py` | B1 deliverables LOD500_LOCKED |
| `organic_market_agent/crop_book/models.py`, `source_registry.py`, `field_policy.py`, `enrichment_models.py`, `importer/reconciler.py`, `importer/enrichment_runner.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/ni_importer.py` | WP-A skeleton; B2 may extend; B3 doesn't touch |

**Permitted modifications:**
- `constants.py` — APPEND `TEND_TASK_TYPE_MAP` after `JMF_CROP_MAP` block
- `crop_task_templates.py` — APPEND 6 entries to `TASK_TYPE_VALUES` tuple (GCR-B3-1)
- `seed.py` — add 2 CLI flags + 1 new call-site block
- `CHANGELOG.md`

### 2.3 GCR-B3-1 — explicit scope

**Authorization required from team_00 BEFORE LOD400 LOCK.** Scope:

| File | Allowed change |
|------|----------------|
| `organic_market_agent/crop_book/crop_task_templates.py` | Append exactly 6 string entries to the existing `TASK_TYPE_VALUES` tuple: `"nursery_seed"`, `"pest_spray"`, `"potting_up"`, `"thinning"`, `"trellis"`, `"fertilize"`. The tuple grows from 14 → 20 entries. No other change — no new column, no new method, no class change. |

Rationale: the migration 046 CHECK constraint extension must be mirrored by the ORM-level `TASK_TYPE_VALUES` tuple to keep validation symmetric (ORM and DB must agree). Without this, B1's existing tests + B3's new tests + the SQLite/Postgres validators all diverge.

The L-GATE_S R1 mandate to team_190 explicitly references this GCR. If team_00 has not signed off by then, L-GATE_S cannot progress.

---

## 3. Migration 046 — `crop_harvest_stats` + ALTER `crop_task_templates`

File: `organic_market_agent/db/versions/046_tend_overlay.py`

```python
"""Migration 046: crop_harvest_stats + extend crop_task_templates task_type enum.

SFA-S003-P002-WP-B3 LOD400 §3. ALTER on B1's table is authorized by
GCR-B3-1 (team_00 sign-off recorded in L-GATE_S R1 mandate).
"""
from alembic import op
import sqlalchemy as sa

revision = "046"
down_revision = "045"   # B2's migration; builder verifies B2 LOD500_LOCKED before running
branch_labels = None
depends_on = None

_NEW_TASK_TYPES = ("nursery_seed", "pest_spray", "potting_up", "thinning",
                   "trellis", "fertilize")
_B1_TASK_TYPES = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)
_FULL_TASK_TYPES = _B1_TASK_TYPES + _NEW_TASK_TYPES   # 20 total

_SEASON_VALUES = ("spring", "summer", "fall", "winter")

def upgrade():
    # 1. Create crop_harvest_stats
    op.create_table(
        "crop_harvest_stats",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season", sa.VARCHAR(20), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("cycles_count", sa.Integer, nullable=True),
        sa.Column("first_harvest_week", sa.Integer, nullable=True),
        sa.Column("peak_harvest_week", sa.Integer, nullable=True),
        sa.Column("last_harvest_week", sa.Integer, nullable=True),
        sa.Column("yield_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("yield_unit", sa.VARCHAR(20), nullable=True),
        sa.Column("yield_per_bed_min", sa.Numeric(10, 3), nullable=True),
        sa.Column("yield_per_bed_max", sa.Numeric(10, 3), nullable=True),
        sa.Column("yield_per_bed_median", sa.Numeric(10, 3), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("crop_id", "season", "year", "source",
                            name="uq_chs_crop_season_year_source"),
        sa.CheckConstraint(
            "season IN ({})".format(",".join(repr(v) for v in _SEASON_VALUES)),
            name="ck_chs_season",
        ),
    )
    op.create_index("idx_chs_crop", "crop_harvest_stats", ["crop_id"])
    op.create_index("idx_chs_crop_year", "crop_harvest_stats", ["crop_id", "year"])

    # 2. ALTER crop_task_templates CHECK constraint
    # SQLite cannot ALTER CHECK constraints in place. Use dialect branch:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE crop_task_templates DROP CONSTRAINT ck_cct_task_type")
        op.create_check_constraint(
            "ck_cct_task_type", "crop_task_templates",
            "task_type IN ({})".format(",".join(repr(v) for v in _FULL_TASK_TYPES)),
        )
    elif bind.dialect.name == "sqlite":
        # SQLite path: drop+rebuild table with new constraint via batch_alter_table.
        # Preserve all data + indices + UNIQUE constraint + the days_offset NOT NULL.
        with op.batch_alter_table("crop_task_templates",
                                  recreate="always") as batch_op:
            batch_op.create_check_constraint(
                "ck_cct_task_type",
                "task_type IN ({})".format(",".join(repr(v) for v in _FULL_TASK_TYPES)),
            )
    else:
        raise RuntimeError(f"Unsupported dialect: {bind.dialect.name}")


def downgrade():
    # Reverse order
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE crop_task_templates DROP CONSTRAINT ck_cct_task_type")
        op.create_check_constraint(
            "ck_cct_task_type", "crop_task_templates",
            "task_type IN ({})".format(",".join(repr(v) for v in _B1_TASK_TYPES)),
        )
    elif bind.dialect.name == "sqlite":
        with op.batch_alter_table("crop_task_templates",
                                  recreate="always") as batch_op:
            batch_op.create_check_constraint(
                "ck_cct_task_type",
                "task_type IN ({})".format(",".join(repr(v) for v in _B1_TASK_TYPES)),
            )
    else:
        raise RuntimeError(f"Unsupported dialect: {bind.dialect.name}")

    op.drop_index("idx_chs_crop_year", table_name="crop_harvest_stats")
    op.drop_index("idx_chs_crop", table_name="crop_harvest_stats")
    op.drop_table("crop_harvest_stats")
```

**Downgrade caveat:** if any `crop_task_templates` row contains a task_type value introduced by migration 046 (one of the 6 new values), the downgrade will fail when the CHECK constraint is re-tightened. AC-01b enforces this: downgrade test runs on a DB that has only B1 rows.

**B2/B3 sequencing note:** `down_revision = "045"`. If B2 has not yet landed migration 045 at build time, the builder STOPs and files an inquiry MSG to team_110 — does NOT improvise (e.g., does NOT set `down_revision = "044"`).

---

## 4. ORM — `crop_harvest_stats.py`

File: `organic_market_agent/crop_book/crop_harvest_stats.py` (NEW)

```python
"""CropHarvestStat ORM — per-(crop, season, year, source) aggregates.

SFA-S003-P002-WP-B3 LOD400 §4. Mirrors the WP-A/B1 pattern of putting
new tables in their own module rather than touching LOD500_LOCKED models.py.
"""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger, CheckConstraint, ForeignKey, Integer, Numeric, TIMESTAMP,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

SEASON_VALUES: tuple[str, ...] = ("spring", "summer", "fall", "winter")

class CropHarvestStat(Base):
    __tablename__ = "crop_harvest_stats"
    __table_args__ = (
        UniqueConstraint("crop_id", "season", "year", "source",
                         name="uq_chs_crop_season_year_source"),
        CheckConstraint(
            "season IN ({})".format(",".join(repr(v) for v in SEASON_VALUES)),
            name="ck_chs_season",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    season: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    cycles_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    first_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    peak_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_harvest_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    yield_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    yield_unit: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    yield_per_bed_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    yield_per_bed_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    yield_per_bed_median: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (f"<CropHarvestStat crop_id={self.crop_id} {self.season} {self.year} "
                f"cycles={self.cycles_count} source={self.source!r}>")
```

---

## 5. `crop_task_templates.py` modification (GCR-B3-1 scope)

File: `organic_market_agent/crop_book/crop_task_templates.py` (MODIFY — GCR-B3-1 only)

Locate the existing `TASK_TYPE_VALUES` tuple (B1 LOD400 §4 — 14 entries). Append exactly 6 new entries. NO other change.

```python
# BEFORE (B1):
TASK_TYPE_VALUES: tuple[str, ...] = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)

# AFTER (B3 GCR-B3-1):
TASK_TYPE_VALUES: tuple[str, ...] = (
    # ── B1 baseline (14) ──
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
    # ── B3 extensions (6 — added under GCR-B3-1, team_00 approved 2026-05-25) ──
    "nursery_seed", "pest_spray", "potting_up", "thinning",
    "trellis", "fertilize",
)
```

Total: 20 entries.

---

## 6. `constants.py` modification — Tend task-type mapping + whitelist

File: `organic_market_agent/crop_book/constants.py` (MODIFY — append only)

Append AFTER the existing `JMF_CROP_MAP` block (added by B1-patch01). Do NOT modify anything above.

```python
# ---------------------------------------------------------------------------
# Tend overlay — task-type mapping + whitelist (SFA-S003-P002-WP-B3 LOD400 §6)
# ---------------------------------------------------------------------------
# team_00 confirmed whitelist on 2026-05-25 (Option B — 11 categories =
# 9 baseline + Trellis + Fertilize & Amend = 758/798 rows = 95.0% coverage).
# Source-of-truth analysis: TASKS.CSV row distribution captured in
# _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25.md
# (filed alongside the L-GATE_S R1 mandate per advisory #3 protocol).

TEND_TASK_WHITELIST: frozenset[str] = frozenset({
    # ── Original 9 (PROGRAM_BRIEF §4) ──
    "Transplant",            # 234 rows
    "Greenhouse Sow",        # 143 rows
    "Direct Sow",            # 124 rows
    "Weed",                  #  78 rows
    "Row Cover & Mulch",     #  55 rows
    "Stale Bed",             #  42 rows
    "Pest & Disease",        #  27 rows
    "Potting up",            #  16 rows
    "Thin",                  #   7 rows
    # ── Added by team_00 Option-B decision (2026-05-25) ──
    "Trellis",               #  13 rows
    "Fertilize & Amend",     #  13 rows
})

TEND_TASK_BLACKLIST: frozenset[str] = frozenset({
    "Maintenance",            #  6 rows — non-template
    "Irrigate",               #  3 rows — non-template (per-event)
    "Seed Cleaning",          #  2 rows — back-office
    "Drill Sow",              #  1 row  — single occurrence
    "השלמות שתילה",            #  4 rows — gap-fill (not template)
    "ריכוז שעות",              #  1 row  — labor-tracking artifact
    "הידרופוניקה",             #  1 row  — single occurrence
    "Cultivation & Tillage",  #  6 rows — single-crop (Carrots only); 0.75% coverage value
    "Prune",                  #  6 rows — low volume; overlaps `hand_weed` semantically
    "Greenhouse Activity",    # 16 rows — mixed content (mostly השלמות gap-fills)
})

# Tend label → JMF task_type enum value mapping.
# Some Tend rows require Method/Sub-method inspection to disambiguate
# (e.g., Weed → hand_weed vs flextine; Row Cover & Mulch → net_row_cover
# vs straw_mulch_topdress). See parse_tasks_templates() in tend_overlay.py.
TEND_TASK_TYPE_MAP: dict[str, str] = {
    # ── Direct 1-to-1 mappings ──
    "Direct Sow":          "at_seeding_transplanting",   # timing_anchor=seeding
    "Transplant":          "at_seeding_transplanting",   # timing_anchor=transplanting
    "Greenhouse Sow":      "nursery_seed",               # NEW B3
    "Stale Bed":           "stale_seed_bed",
    "Pest & Disease":      "pest_spray",                 # NEW B3
    "Potting up":          "potting_up",                 # NEW B3
    "Thin":                "thinning",                   # NEW B3
    "Trellis":             "trellis",                    # NEW B3
    "Fertilize & Amend":   "fertilize",                  # NEW B3
    # ── Method-disambiguated mappings (importer §7.4 logic) ──
    # "Weed"               → "hand_weed" (default; reclassify if Method=Flextine)
    # "Row Cover & Mulch"  → "net_row_cover" (default; reclassify if Sub-method=Mulch/Straw)
}
# Note: "Weed" and "Row Cover & Mulch" are NOT direct keys in this dict —
# their mapping happens in tend_overlay.py with Method/Sub-method inspection.
# Whitelist controls inclusion; this map controls task_type assignment.
```

**Total whitelisted rows (Tend_2022 baseline):** 758/798 = 95.0% coverage. The remaining 40 rows are blacklisted (31) or covered-by-blacklist (9 — Greenhouse Activity, Cultivation & Tillage, Prune partials).

---

## 7. `tend_overlay.py` — importer module

File: `organic_market_agent/crop_book/importer/tend_overlay.py` (NEW)

### 7.1 Module header

```python
"""Tend overlay importer (SFA-S003-P002-WP-B3 LOD400 §7).

Reads Tend_<year>/ CSV exports and produces:

  1. CropTaskTemplate rows (source='Tend_<year>', trust_tier='OP',
     confidence_weight=0.55) for whitelisted recurring tasks — via the
     B1 crop_task_templates table.
  2. CropVarietySourceValue rows for `days_in_gh_total` and
     `days_to_first_potting` — via the WP-A enrichment engine.
  3. CropHarvestStat rows aggregated from HARVESTS.CSV — NEVER per-record.

Public entrypoints:

  parse_tasks_templates(csv_path, year)       -> list[CropTaskTemplateDict]
  parse_greenhouse_plan(csv_path)             -> list[CropSourceValueDict]
  parse_harvests_aggregate(csv_path, year)    -> list[CropHarvestStatDict]
  import_tend_overlay(session, tend_dir, *, year=2022, dry_run=False)
      -> TendOverlaySummary
"""
```

### 7.2 Data classes

```python
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Optional

@dataclass
class TendOverlaySummary:
    year: int
    task_template_rows_upserted: int
    source_value_rows_upserted: int
    harvest_stat_rows_upserted: int
    whitelist_filtered: int          # tasks excluded by whitelist
    method_disambiguation_misses: int  # Weed/RowCover with unclear Method
    crop_map_misses: list[str]       # Tend crops not in TEND_CROP_MAP
    harvests_aggregated: int         # how many raw HARVESTS rows aggregated
    blacklist_filtered: int          # tasks explicitly blacklisted
```

### 7.3 `parse_tasks_templates(csv_path, year)`

Algorithm:

1. Open CSV with `csv.DictReader`.
2. For each row, extract `task_type_raw = row["Task Type"].strip()`.
3. If `task_type_raw` is in `TEND_TASK_BLACKLIST`: increment `blacklist_filtered`, skip.
4. If `task_type_raw` is NOT in `TEND_TASK_WHITELIST`: increment `whitelist_filtered`, skip (this catches new unforeseen task types — log WARN with the raw value).
5. Resolve JMF `task_type`:
   - If `task_type_raw` in `TEND_TASK_TYPE_MAP`: use the mapped value.
   - Else if `task_type_raw == "Weed"`: inspect `row["Method"]`:
     - `"Hand weed"` / empty → `"hand_weed"`
     - `"Flextine"` → `"flextine_harrow_1"` (best-effort)
     - Other → `"hand_weed"` (default) + WARN
   - Else if `task_type_raw == "Row Cover & Mulch"`: inspect `row["Sub-method"]`:
     - `"Tarp"` / `"Cover"` / `"Row cover"` → `"net_row_cover"`
     - `"Straw"` / `"Mulch"` → `"straw_mulch_topdress"`
     - Other → `"net_row_cover"` (default) + WARN
   - Else: this shouldn't happen (whitelist + map agree); log ERROR + skip.
6. Compute `timing_anchor`:
   - `"at_seeding_transplanting"` from `"Direct Sow"` → `"seeding"`
   - `"at_seeding_transplanting"` from `"Transplant"` → `"transplanting"`
   - `"stale_seed_bed"` → `"field_prep"`
   - All others → `None` (no anchor; days_offset is presence-only)
7. Compute `days_offset`:
   - For tasks with a plant date (Direct Sow / Transplant): `0` (task IS the seeding/transplant event).
   - For other tasks: use `DAYS_OFFSET_PRESENCE_ONLY` from `crop_task_templates.py` (matches B1 contract). Reason: Tend rows are individual events with absolute dates, not relative offsets from a plant date. Computing the offset requires joining to the plant-date task, which is a separate aggregation pass — out of scope for this iteration (file follow-up if needed).
8. Resolve `crop_id` via `TEND_CROP_MAP[parse_crop_name(row["Plantings Assigned"])]`:
   - The `Plantings Assigned` field has format `"<Crop> <Cultivar> <Date>"` (e.g., `"Tomatoes Hyd. Whitny וייטני 13/07/2022"`).
   - `parse_crop_name()` returns the first token until a known cultivar boundary. Use the existing TEND_CROP_MAP keys as the first-pass match set.
   - On miss: append to `summary.crop_map_misses`, skip the row, log WARN.
9. Emit one dict per row with:
   ```python
   {
     "crop_id":       <int>,
     "source":        f"Tend_{year}",
     "trust_tier":    "OP",
     "task_type":     <JMF enum value>,
     "timing_anchor": <str or None>,
     "days_offset":   <int>,        # DAYS_OFFSET_PRESENCE_ONLY for non-anchor rows
     "method":        row["Method"].strip() or None,
     "input_material": row["Input"].strip() or None,
     "notes":         row["Description"].strip() or None,
   }
   ```

### 7.4 `parse_greenhouse_plan(csv_path)`

Reads `GREENHOUSE_PLAN.CSV` (287 rows). For each row, emit one or two `CropVarietySourceValue` dicts:

| CSV column substring (case-insensitive) | Returned `field_name` | Unit handling |
|-----------------------------------------|------------------------|----------------|
| `Days In Greenhouse` | `days_in_gh_total` | integer days |
| `Days to 1st potting up` / `Days to first potting` | `days_to_first_potting` | integer days |

Crop resolution: same `TEND_CROP_MAP` pattern as §7.3. Variety: matches `(crop_id, name_en)` if cultivar present in row, else default-baseline variety (same as B1 §6.9 pattern).

### 7.5 `parse_harvests_aggregate(csv_path, year)`

Reads `HARVESTS.CSV` (939 rows). **NEVER emits per-record rows.**

Algorithm:

1. Read all rows. Group by `(crop_name, year, season)`:
   - `season` derived from row's `Harvest Date` month:
     - month 3-5 → `"spring"`
     - month 6-8 → `"summer"`
     - month 9-11 → `"fall"`
     - month 12, 1, 2 → `"winter"`
2. For each group, compute:
   - `cycles_count` = number of distinct planting rows that contributed to this group's harvest (heuristic — count distinct `Plantings Assigned` values)
   - `first_harvest_week` / `peak_harvest_week` / `last_harvest_week` = min / mode-week / max ISO week numbers
   - `yield_total` = sum of `Amount` column (numeric)
   - `yield_unit` = mode of `Amount Unit` column (e.g., `"kg"`)
   - `yield_per_bed_min` / `_max` / `_median` = computed from per-record `Amount / bed_count` (when bed_count is available; else NULL)
3. Emit one dict per group:
   ```python
   {
     "crop_id":            <int>,
     "season":             <str>,
     "year":               <int>,
     "source":             f"Tend_{year}",
     "cycles_count":       <int>,
     "first_harvest_week": <int>,
     "peak_harvest_week":  <int>,
     "last_harvest_week":  <int>,
     "yield_total":        <Decimal>,
     "yield_unit":         <str>,
     "yield_per_bed_min":  <Decimal or None>,
     "yield_per_bed_max":  <Decimal or None>,
     "yield_per_bed_median": <Decimal or None>,
   }
   ```
4. Hard assertion: `len(emitted) <= crops_count × 4 seasons × 1 year`. If exceeded, abort (programming bug in grouping).

### 7.6 `import_tend_overlay(session, tend_dir, *, year=2022, dry_run=False)`

```python
def import_tend_overlay(
    session: Session,
    tend_dir: Path,
    *,
    year: int = 2022,
    dry_run: bool = False,
) -> TendOverlaySummary:
    """End-to-end orchestrator.

    Steps:
      1. Resolve CSV paths (tend_dir / "TASKS (from macBook Air - nimrod).CSV"
         + GREENHOUSE_PLAN + HARVESTS). Missing files → log WARN, skip that
         sub-parser (graceful degradation).
      2. Call parse_tasks_templates() → emit task-template dicts.
      3. Call parse_greenhouse_plan() → emit source_value dicts.
      4. Call parse_harvests_aggregate() → emit harvest_stat dicts.
      5. For each task-template dict: _upsert_task_template_tend(session, dict).
      6. For each source_value dict: _upsert_source_value_tend(session, dict).
      7. For each harvest_stat dict: _upsert_harvest_stat(session, dict).
      8. If dry_run: session.rollback(); else session.commit().
      9. Return TendOverlaySummary.
    """
```

### 7.7 Upsert helpers

```python
def _upsert_task_template_tend(session, row: dict) -> CropTaskTemplate:
    """Upsert on (crop_id, source, task_type, days_offset).

    Matches B1's _upsert_task_template signature for crop_task_templates.
    The B1 UNIQUE constraint enforces idempotency.
    """
    # Implementation identical to B1's _upsert_task_template (jmf_masterclass.py §6.10)
    # but with source='Tend_<year>', trust_tier='OP'.

def _upsert_source_value_tend(
    session, variety_id: int, field_name: str, value_numeric: Decimal, year: int,
) -> CropVarietySourceValue:
    """Upsert on (variety_id, field_name, source='Tend_<year>').

    trust_tier='OP', confidence_weight=0.55, is_outlier_rejected=False.
    Engine reuse: the next run_enrichment() call will pick these up.
    """

def _upsert_harvest_stat(session, row: dict) -> CropHarvestStat:
    """Upsert on (crop_id, season, year, source).

    The crop_harvest_stats UNIQUE constraint enforces idempotency.
    """
```

---

## 8. `seed.py` modifications

Add after the existing flags (post-B1 / patch01):

```python
parser.add_argument(
    "--tend-overlay-dir", type=Path,
    default=Path("/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022"),
    metavar="PATH",
    help="Tend overlay CSV directory (default: %(default)s; year inferred from dirname suffix)",
)
parser.add_argument(
    "--tend-overlay-year", type=int, default=2022, metavar="YEAR",
    help="Year for source label and HARVESTS aggregation (default: %(default)s)",
)
parser.add_argument(
    "--tend-overlay-only", action="store_true",
    help="Run only Tend overlay ingestion (skip JMF / NI / WP-A Tend).",
)
parser.add_argument(
    "--no-tend-overlay", action="store_true",
    help="Skip Tend overlay ingestion.",
)
```

Mutual exclusion: `--tend-overlay-only` ↔ `--no-tend-overlay` (parser.error).

Call site (inside `with SessionFactory() as session:` block, AFTER JMF MasterClass import from B1 and BEFORE WP-A Tend raw-material import):

```python
if not args.no_tend_overlay:
    from organic_market_agent.crop_book.importer.tend_overlay import import_tend_overlay
    tend_summary = import_tend_overlay(
        session, args.tend_overlay_dir, year=args.tend_overlay_year,
        dry_run=args.dry_run,
    )
    logger.info("Tend overlay: %s", tend_summary)
    if tend_summary.crop_map_misses:
        logger.warning("Tend overlay crop_map misses (%d): %s",
                       len(tend_summary.crop_map_misses),
                       ", ".join(tend_summary.crop_map_misses[:10]))
    session.flush()

if args.tend_overlay_only:
    # Early return — skip remaining importers
    if not args.dry_run:
        session.commit()
    return
```

---

## 9. Acceptance Criteria

**AC-01a — Migration 046 creates `crop_harvest_stats` cleanly.**
`alembic upgrade head` creates the table with correct DDL; `alembic downgrade 045` drops it. Works on both Postgres and SQLite (the SQLite branch in §3 handles the batch_alter pattern).

**AC-01b — Migration 046 extends `crop_task_templates` CHECK constraint cleanly.**
After `alembic upgrade 046`, `crop_task_templates.task_type` accepts all 20 enum values (14 from B1 + 6 from B3). On a fresh DB with no rows: `alembic downgrade 045` succeeds (reverts to 14-value CHECK). With B3 rows present: downgrade fails — documented behavior.

**AC-02 — `CropHarvestStat` ORM correct.**
13 columns mapped with correct types; `SEASON_VALUES` exported; CHECK + UNIQUE constraints active.

**AC-03 — `TASK_TYPE_VALUES` ORM tuple extended (GCR-B3-1).**
`from organic_market_agent.crop_book.crop_task_templates import TASK_TYPE_VALUES`; `len(TASK_TYPE_VALUES) == 20`; new 6 values present; B1 baseline 14 preserved.

**AC-04 — `TEND_TASK_WHITELIST` + `TEND_TASK_BLACKLIST` + `TEND_TASK_TYPE_MAP` importable.**
`from organic_market_agent.crop_book.constants import TEND_TASK_WHITELIST, TEND_TASK_BLACKLIST, TEND_TASK_TYPE_MAP`. Counts: whitelist has 11 entries; blacklist has 10 entries; type_map has 9 direct entries.

**AC-05 — Whitelist + blacklist coverage on live `TASKS.CSV`.**
Running `parse_tasks_templates(<live TASKS.CSV>, year=2022)`:
- Returns ≥ 690 rows (758/798 expected; some may drop due to crop_map misses)
- `summary.whitelist_filtered + summary.blacklist_filtered ≥ 40` (the 40 non-whitelisted rows: 10 categories × ~40 average)

**AC-06 — `Weed` Method disambiguation.**
A Tend row with `Task Type="Weed"` and `Method="Hand weed"` maps to `task_type="hand_weed"`. A row with `Method="Flextine"` maps to `"flextine_harrow_1"`. A row with unknown Method maps to `"hand_weed"` (default) with a WARN log.

**AC-07 — `Row Cover & Mulch` Sub-method disambiguation.**
A Tend row with `Sub-method="Tarp"` maps to `task_type="net_row_cover"`. `Sub-method="Straw"` maps to `"straw_mulch_topdress"`. Unknown Sub-method maps to `"net_row_cover"` (default) + WARN.

**AC-08 — `GREENHOUSE_PLAN.CSV` populates 2 source_value fields.**
After `import_tend_overlay`, at least one `crop_variety_source_values` row exists with `field_name='days_in_gh_total'` AND `source='Tend_2022'`. Same for `'days_to_first_potting'`.

**AC-09 — `HARVESTS.CSV` aggregates — NO per-record rows.**
After `import_tend_overlay` against the live HARVESTS.CSV (939 rows), `SELECT COUNT(*) FROM crop_harvest_stats WHERE source='Tend_2022'` is ≤ `(distinct crops) × 4 seasons` = max ~200 rows. Per-record count (939) is NEVER reached. The summary's `harvests_aggregated == 939` (input count) but emitted rows are aggregated.

**AC-10 — `crop_harvest_stats` UNIQUE constraint.**
Two inserts with identical `(crop_id, season, year, source)` raises `IntegrityError`.

**AC-11 — CHECK constraint regression — old B1 task_types still accepted.**
Inserting `task_type='hand_weed'` (B1 baseline) after migration 046 still succeeds. Inserting `task_type='nonsense_value'` raises IntegrityError.

**AC-12 — Idempotent re-import.**
Running `import_tend_overlay(session, ...)` twice in a row produces the same row count in all 3 target tables after the second call as after the first.

**AC-13 — `Trellis` and `Fertilize & Amend` (Option-B additions) actually flow through.**
After live import:
- `SELECT COUNT(*) FROM crop_task_templates WHERE task_type='trellis' AND source='Tend_2022'` ≥ 1 (expect ~13)
- Same for `task_type='fertilize'` (expect ~13)

**AC-14 — CLI `--tend-overlay-only` skips JMF + NI.**
`seed.py --tend-overlay-only --dry-run` produces no rows with `source='JMF'` and no `source LIKE 'NI:%'` rows.

**AC-15 — CLI `--no-tend-overlay` skips Tend overlay.**
`seed.py --all --no-tend-overlay --dry-run` produces zero rows with `source='Tend_2022'`.

**AC-16 — Mutual exclusion enforced.**
`seed.py --tend-overlay-only --no-tend-overlay` exits with non-zero status + argparse error.

**AC-17 — Existing B1 + patch01 tests still PASS (regression).**
`pytest tests/crop_book/ -q` shows zero regressions on the 56 patch01 + 56 B1 tests after this build. (The patch01 tests asserted `TASK_TYPE_VALUES` shape — they should still pass because the tuple was only EXTENDED, not modified.)

**AC-18 — `validate_aos.sh` 0 FAIL.**
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.

**AC-19 — No LOD500_LOCKED file modified beyond GCR-B3-1 scope.**
`git diff <patch01-lock-commit>..HEAD -- <each path in §2.2>` empty for all non-GCR-B3-1 paths.
For `crop_task_templates.py`: diff scoped to ONLY the `TASK_TYPE_VALUES` tuple extension (6 new entries) + a section comment. No other line touched.

**AC-20 — Engine integration: scalar field blending works.**
After `import_tend_overlay` + `run_enrichment(session)`, `crop_field_enrichment` rows exist for `days_in_gh_total` and `days_to_first_potting` with `source_count >= 1` and `winning_source_class IN ('OP', 'EX', 'NI')` (depending on whether team_00 or JMF overrides are present).

---

## 10. Test requirements

**Minimum 20 new tests** across 9 new test files:

| File | Tests | Key coverage |
|------|-------|--------------|
| `test_tend_overlay_parsers.py` | 4 | AC-05, AC-09 (parse_tasks; parse_greenhouse_plan; parse_harvests_aggregate; empty CSV edge case) |
| `test_tend_task_whitelist.py` | 3 | AC-05 (whitelist included; blacklist excluded; non-listed dropped with WARN) |
| `test_tend_task_type_mapping.py` | 4 | AC-06, AC-07 (Weed Method; Row Cover Sub-method; Trellis/Fertilize Option-B additions resolve correctly) |
| `test_tend_overlay_aggregation.py` | 2 | AC-09 (harvest aggregation correctness; no-per-record assertion) |
| `test_tend_overlay_integration.py` | 2 | AC-08, AC-12, AC-13, AC-20 (SQLite in-memory; full flow; engine integration) |
| `test_tend_idempotency.py` | 1 | AC-12 (twice-import = same row count) |
| `test_crop_harvest_stats_orm.py` | 2 | AC-02 (column/constraint coverage; SEASON enum) |
| `test_migration_046.py` | 2 | AC-01a + AC-01b (upgrade + downgrade + CHECK on both new + B1 values) |
| `test_seed_tend_overlay_cli.py` | 2 | AC-14, AC-15, AC-16 |

All tests use SQLite in-memory or fixture CSVs at `tests/crop_book/fixtures/tend_2022/` (builder creates ≥ 1 minimal fixture per CSV — 3 crops, 5 rows each). Marker: `@pytest.mark.crop_book`.

---

## 11. Build sequence (10 steps)

**Step 1** — Read this LOD400 + LOD200 + PROGRAM_BRIEF §4 + parent WP-B1 LOD400 §3-§4.

**Step 2** — Verify GCR-B3-1 sign-off is in the team_00 DECISION record at `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25.md` (team_110 will produce this file alongside the L-GATE_S R1 mandate; if missing, STOP and inquire). Verify migration 045 (B2) is committed before running step 4 — if not, STOP and inquire.

**Step 3** — Create `crop_harvest_stats.py` (ORM). Verify import smoke: `from ... import CropHarvestStat, SEASON_VALUES; assert len(SEASON_VALUES) == 4`.

**Step 4** — Create migration 046. Run `alembic upgrade 046` against a fresh SQLite DB. Verify `crop_task_templates` accepts all 20 enum values via a constraint probe. Run `alembic downgrade 045` (on empty DB) and `alembic upgrade 046` again.

**Step 5** — Apply GCR-B3-1 edit to `crop_task_templates.py` (extend `TASK_TYPE_VALUES` to 20 entries). Run `python3 -c "from organic_market_agent.crop_book.crop_task_templates import TASK_TYPE_VALUES; print(len(TASK_TYPE_VALUES))"` → MUST print `20`.

**Step 6** — Append `TEND_TASK_WHITELIST` + `TEND_TASK_BLACKLIST` + `TEND_TASK_TYPE_MAP` to `constants.py` per spec §6. Smoke-test imports.

**Step 7** — Create `tend_overlay.py` with the 3 parsers + orchestrator + upsert helpers (§7). Write `test_tend_overlay_parsers.py` against minimal fixture CSVs. Achieve AC-05, AC-06, AC-07.

**Step 8** — Wire seed.py CLI flags (§8). Write `test_seed_tend_overlay_cli.py`. Achieve AC-14, AC-15, AC-16.

**Step 9** — Write remaining tests (`test_tend_overlay_aggregation`, `test_tend_overlay_integration`, `test_tend_idempotency`, `test_crop_harvest_stats_orm`, `test_migration_046`, `test_tend_task_whitelist`, `test_tend_task_type_mapping`). Achieve AC-08 through AC-13, AC-17, AC-20.

**Step 10** — Run full `pytest tests/crop_book/ -q` → all green (≥ 261 tests = 241 + 20 new; allow the 1 pre-existing publisher failure). Run `validate_aos.sh` → 0 FAIL. Update `CHANGELOG.md`. Write BUILD_REPORT_v1.0.0.md.

---

## 12. PRE_HANDOFF advisory disposition

| # | Advisory | B3 disposition |
|---|---|---|
| 1 | JMF PDF licensing | **N/A for B3** (Tend CSV data, not PDF) |
| 2 | LLM extraction cache | **N/A for B3** (no LLM) |
| 3 | **Tend task whitelist — team_00 confirmation REQUIRED before LOD400 LOCK** | **RESOLVED 2026-05-25** — team_00 confirmed Option B: 11 categories whitelisted, 10 blacklisted, 95.0% coverage. Decision record filed at `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25.md` (to be produced alongside L-GATE_S R1 mandate). |
| 4 | Transitive WP-A dependency | **Addressed** in §2.1 (named WP-A files); §3 (engine reuse via `reconcile_field()` for scalar fields); §7.6 (upsert helpers reuse B1 patterns); AC-20 (engine regression). |

---

## 13. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | SQLite `batch_alter_table` for CHECK rename doesn't preserve all column defaults | MEDIUM | MEDIUM | AC-11 explicitly tests B1 baseline values still accepted post-migration. If failure: builder verifies via direct DDL inspection (`PRAGMA table_info(crop_task_templates)`); files inquiry if behavior diverges. |
| R-02 | `Plantings Assigned` crop-name parsing is heuristic | MEDIUM | LOW | `summary.crop_map_misses` surfaces unmapped names cleanly. The 86-entry `JMF_CROP_MAP` and existing TEND_CROP_MAP cover the canonical set; misses are logged with WARN, never crash the import. |
| R-03 | HARVESTS season-boundary calculation differs from operational expectations | LOW | LOW | Use ISO week + month → season convention documented in §7.5. AC-09 confirms aggregation is bounded; absolute season assignment can be tuned later. |
| R-04 | `Days In Greenhouse` / `Days to first potting` columns vary across editions | LOW | LOW | Case-insensitive substring match; missing column → emit zero source_values for that field; log WARN with file. |
| R-05 | New enum values pollute B1-only consumers downstream | LOW | LOW | B1's ORM tests already verify `TASK_TYPE_VALUES` shape — they should pass after the extension because the tuple is APPENDED-only (B1's 14 baseline still at indices 0..13). AC-17 enforces. |
| R-06 | GCR-B3-1 approval delay blocks L-GATE_S | MEDIUM | HIGH | LOD400 §10 says GCR sign-off is a hard prerequisite. The L-GATE_S R1 mandate to team_190 includes the `DECISION` file path so team_190 can verify the sign-off chain. Without it, mandate is invalid. |
| R-07 | B2 migration 045 not yet landed when B3 tries to upgrade | MEDIUM | LOW | Step 2 verifies B2 LOD500_LOCKED before step 4. If B2 hasn't landed, builder STOPs and inquires. Both WPs run in parallel — sequencing at migration time is a real concern. |

---

## 14. LOD500_LOCKED file inventory (must not be modified)

See §2.2 above. The ONLY GCR-permitted exception is `crop_task_templates.py` `TASK_TYPE_VALUES` extension (§5).

---

## 15. File-level deliverables summary

### CREATE (new files)

```
organic_market_agent/crop_book/crop_harvest_stats.py
organic_market_agent/crop_book/importer/tend_overlay.py
organic_market_agent/db/versions/046_tend_overlay.py
tests/crop_book/test_tend_overlay_parsers.py
tests/crop_book/test_tend_task_whitelist.py
tests/crop_book/test_tend_task_type_mapping.py
tests/crop_book/test_tend_overlay_aggregation.py
tests/crop_book/test_tend_overlay_integration.py
tests/crop_book/test_tend_idempotency.py
tests/crop_book/test_crop_harvest_stats_orm.py
tests/crop_book/test_migration_046.py
tests/crop_book/test_seed_tend_overlay_cli.py
tests/crop_book/fixtures/tend_2022/<minimal CSVs>      (builder generates ≥ 3 small CSVs)
_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25.md   (team_110 produces alongside L-GATE_S R1 mandate)
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B3/BUILD_REPORT_v1.0.0.md             (builder writes after L-GATE_B)
```

### MODIFY (existing files — additive scope only)

```
organic_market_agent/crop_book/constants.py              ← +TEND_TASK_WHITELIST + TEND_TASK_BLACKLIST + TEND_TASK_TYPE_MAP
organic_market_agent/crop_book/crop_task_templates.py    ← +6 entries to TASK_TYPE_VALUES (GCR-B3-1)
organic_market_agent/crop_book/importer/seed.py          ← +4 CLI flags + 1 call-site block
CHANGELOG.md                                              ← +[Unreleased] entry
```

### DO NOT TOUCH

See §2.2 LOD500_LOCKED inventory.

---

*LOD400 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*team_00 whitelist confirmation 2026-05-25 (Option B). team_00 GCR-B3-1 sign-off requested via DECISION file alongside L-GATE_S R1 mandate.*
*Pending: team_190 L-GATE_S validation (mandate next).*
