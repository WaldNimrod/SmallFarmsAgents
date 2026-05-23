---
id: SFA-S003-P002-WP-A-LOD400
wp: SFA-S003-P002-WP-A — Data Enrichment Architecture
gate: L-GATE_S (LOD400 — implementation spec)
status: DRAFT — pending team_190 L-GATE_S
author: team_100 (Claude Sonnet 4.6, Chief Architect)
date: 2026-05-23
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md
decision_ref: _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md
builder: sfa_build (team_10)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-A: Data Enrichment Architecture

**Read before writing a single line of code:**
1. `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md` — architecture SSoT
2. `_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md` — decisions
3. `organic_market_agent/crop_book/models.py` — existing ORM (LOD500_LOCKED except GCR_1 fields)
4. `organic_market_agent/crop_book/importer/reconciler.py` — existing reconciler (to be replaced)
5. `organic_market_agent/crop_book/constants.py` — existing maps + TEAM00_DTM_OVERRIDES

---

## 1. Goal

Build the **data enrichment layer** for the ספר גידולים crop book:

1. **Migration 041** — new `crop_field_enrichment` table (min/max/best/confidence per field)
2. **Migration 042** — extend `crop_variety_source_values` with trust metadata (GCR_1 authorized)
3. **Source registry** — declarative 7-class registry replacing hardcoded source labels
4. **Field policy table** — declarative per-field trust order + blend strategy
5. **Reconciler engine** — pluggable weighted-mean + outlier gate; replaces reconciler.py
6. **Enrichment runner** — populates `crop_field_enrichment` from existing source_values
7. **NI importer skeleton** — design-registered; activates when Nimrod provides files
8. **Validation harness** — calibration script against team_00 EX overrides
9. **Enrichment SPA artifact** — new `sfagent-crop-book-enrichment.json` WP media file
10. **Tests** — ≥ 20 new tests; all existing tests continue to pass

On completion: `python -m organic_market_agent.crop_book.importer.seed --all` populates
enrichment data; `python scripts/validate_enrichment.py` prints calibration report.

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/crop_book/
├── source_registry.py          ← NEW: SourceSpec dataclass + SOURCE_REGISTRY dict
├── field_policy.py             ← NEW: FieldPolicy dataclass + FIELD_POLICY dict + outlier fns
├── enrichment_models.py        ← NEW: CropFieldEnrichment SQLAlchemy ORM class
├── models.py                   ← MODIFY: add 3 columns to CropVarietySourceValue (GCR_1)
└── importer/
    ├── reconciler.py           ← REWRITE: pluggable engine; old functions kept as wrappers
    ├── enrichment_runner.py    ← NEW: compute + upsert crop_field_enrichment rows
    ├── ni_importer.py          ← NEW: NI-class ingestion skeleton (no data files yet)
    └── seed.py                 ← MODIFY: add --enrich flag + call enrichment_runner

organic_market_agent/db/versions/
├── 041_crop_field_enrichment.py   ← NEW
└── 042_source_values_enrich.py    ← NEW (GCR_1 authorized)

scripts/
└── validate_enrichment.py         ← NEW: standalone calibration harness

tests/crop_book/
├── test_source_registry.py        ← NEW
├── test_field_policy.py           ← NEW
├── test_enrichment_reconciler.py  ← NEW (replaces + extends test_reconciler.py)
├── test_enrichment_runner.py      ← NEW
└── test_validate_enrichment.py    ← NEW
```

### 2.2 No changes to these files

- `organic_market_agent/crop_book/views.py` (LOD500_LOCKED — UI in WP-B)
- `organic_market_agent/publisher/` (LOD500_LOCKED — publisher in WP-B)
- `organic_market_agent/crop_book/importer/tend.py` (existing; called by reconciler)
- `organic_market_agent/crop_book/importer/jmf.py` (existing; called by reconciler)
- `organic_market_agent/crop_book/constants.py` (existing constants — read-only by new code)
- Any migration 001–040

---

## 3. Migration 041 — `crop_field_enrichment`

File: `organic_market_agent/db/versions/041_crop_field_enrichment.py`

```python
"""Migration 041: crop_field_enrichment table — per-field consensus + confidence."""
revision = "041"
down_revision = "040"

def upgrade():
    op.create_table(
        "crop_field_enrichment",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("variety_id", sa.BigInteger,
                  sa.ForeignKey("crop_varieties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.VARCHAR(100), nullable=False),
        sa.Column("value_min", sa.Numeric(14, 6), nullable=True),
        sa.Column("value_max", sa.Numeric(14, 6), nullable=True),
        sa.Column("value_best", sa.Numeric(14, 6), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("winning_source_class", sa.VARCHAR(20), nullable=True),
        sa.Column("computed_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("variety_id", "field_name", name="uq_cfe_variety_field"),
    )
    op.create_index("ix_cfe_variety_id", "crop_field_enrichment", ["variety_id"])

def downgrade():
    op.drop_table("crop_field_enrichment")
```

SQLite compatibility: use `BigInteger().with_variant(Integer(), "sqlite")` for id and variety_id
(same pattern as existing models). No JSON columns — fully SQLite-compatible.

---

## 4. Migration 042 — extend `crop_variety_source_values` (GCR_1)

File: `organic_market_agent/db/versions/042_source_values_enrich.py`

Authorization: GCR_1 pre-authorized by team_00 per
`_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md`

```python
"""Migration 042: add trust metadata to crop_variety_source_values. GCR_1 authorized."""
revision = "042"
down_revision = "041"

def upgrade():
    op.add_column("crop_variety_source_values",
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=True))
    op.add_column("crop_variety_source_values",
        sa.Column("confidence_weight", sa.Numeric(5, 4), nullable=True))
    op.add_column("crop_variety_source_values",
        sa.Column("is_outlier_rejected", sa.Boolean, nullable=False,
                  server_default=sa.text("false")))

    # Backfill trust_tier from existing source labels
    op.execute("""
        UPDATE crop_variety_source_values SET trust_tier = CASE
            WHEN source = 'team_00' THEN 'EX'
            WHEN source LIKE 'NI%'  THEN 'NI'
            WHEN source = 'JMF'     THEN 'PR'
            WHEN source LIKE 'Tend%' THEN 'OP'
            WHEN source LIKE 'OMA%' THEN 'MK'
            WHEN source LIKE 'WB%'  THEN 'WB'
            WHEN source LIKE 'UC%'  THEN 'UC'
            ELSE 'PR'
        END
    """)

    # Backfill confidence_weight from class defaults (EX/NI are NULL = hard override)
    op.execute("""
        UPDATE crop_variety_source_values SET confidence_weight = CASE
            WHEN trust_tier = 'EX' THEN NULL
            WHEN trust_tier = 'NI' THEN NULL
            WHEN trust_tier = 'PR' THEN 0.70
            WHEN trust_tier = 'OP' THEN 0.55
            WHEN trust_tier = 'MK' THEN 0.40
            WHEN trust_tier = 'WB' THEN 0.30
            WHEN trust_tier = 'UC' THEN NULL
            ELSE 0.50
        END
    """)

    # Backfill is_outlier_rejected from existing note field
    op.execute("""
        UPDATE crop_variety_source_values
        SET is_outlier_rejected = TRUE
        WHERE note LIKE '%OUTLIER_REJECTED%'
    """)

def downgrade():
    op.drop_column("crop_variety_source_values", "is_outlier_rejected")
    op.drop_column("crop_variety_source_values", "confidence_weight")
    op.drop_column("crop_variety_source_values", "trust_tier")
```

---

## 5. models.py — CropVarietySourceValue additions (GCR_1)

Add three mapped columns to the existing `CropVarietySourceValue` class in
`organic_market_agent/crop_book/models.py`:

```python
# ADD to CropVarietySourceValue (after existing 'note' column):
trust_tier: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
confidence_weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
is_outlier_rejected: Mapped[bool] = mapped_column(
    Boolean, nullable=False, server_default="false")
```

No other changes to models.py.

---

## 6. enrichment_models.py — CropFieldEnrichment ORM

File: `organic_market_agent/crop_book/enrichment_models.py` (NEW — separate from models.py)

```python
"""CropFieldEnrichment ORM — per-field consensus + confidence table (migration 041)."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

class CropFieldEnrichment(Base):
    __tablename__ = "crop_field_enrichment"

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    variety_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crop_varieties.id", ondelete="CASCADE"), nullable=False)
    field_name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    value_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    value_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    value_best: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 6), nullable=True)
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)
    source_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    winning_source_class: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False)

    variety: Mapped["CropVariety"] = relationship(  # noqa: F821
        "CropVariety", back_populates="enrichments")
```

Also add back-reference to `CropVariety` in models.py:
```python
# ADD to CropVariety class:
enrichments: Mapped[list["CropFieldEnrichment"]] = relationship(
    "CropFieldEnrichment", back_populates="variety", cascade="all, delete-orphan")
```

---

## 7. source_registry.py

File: `organic_market_agent/crop_book/source_registry.py` (NEW)

```python
"""Source registry — declarative 7-class taxonomy for crop-book data enrichment."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SourceSpec:
    label: str         # exact string as stored in source_values.source
    cls: str           # class code: EX/NI/PR/OP/MK/WB/UC
    weight: float      # default trust weight (None = hard override — EX/NI)
    is_hard_override: bool = False  # True → never enters blend; always wins
    requires_moderation: bool = False  # True → excluded from blend until weight set

SOURCE_REGISTRY: dict[str, SourceSpec] = {
    # EX — Expert overrides (hardcoded team_00)
    "team_00": SourceSpec("team_00", "EX", weight=1.0, is_hard_override=True),

    # NI — Nimrod-Input (files/links; label prefix "NI:")
    # NI sources are registered at import time: e.g. "NI:my_crop_data_2024.xlsx"
    # The registry keeps a sentinel for class detection:
    "_NI_CLASS_SENTINEL": SourceSpec("_NI_CLASS_SENTINEL", "NI", weight=0.85,
                                      is_hard_override=True),

    # PR — Prescriptive / MasterClass
    "JMF": SourceSpec("JMF", "PR", weight=0.70),

    # OP — Operational / Tend (one entry per year; builder adds new years as they appear)
    "Tend_2018": SourceSpec("Tend_2018", "OP", weight=0.55),
    "Tend_2019": SourceSpec("Tend_2019", "OP", weight=0.55),
    "Tend_2020": SourceSpec("Tend_2020", "OP", weight=0.55),
    "Tend_2021": SourceSpec("Tend_2021", "OP", weight=0.55),
    "Tend_2022": SourceSpec("Tend_2022", "OP", weight=0.55),
    # Legacy flat export (pre-year-folder layout)
    "Tend": SourceSpec("Tend", "OP", weight=0.55),

    # MK — Market index (OMA) — design-registered; no importer in WP-A
    "_MK_CLASS_SENTINEL": SourceSpec("_MK_CLASS_SENTINEL", "MK", weight=0.40),

    # WB — Web / third-party — design-registered; no importer in WP-A
    "_WB_CLASS_SENTINEL": SourceSpec("_WB_CLASS_SENTINEL", "WB", weight=0.30),

    # UC — User-Community — design-registered; moderation required
    "_UC_CLASS_SENTINEL": SourceSpec("_UC_CLASS_SENTINEL", "UC", weight=0.15,
                                      requires_moderation=True),
}

def get_source_spec(source_label: str) -> SourceSpec:
    """Look up spec by label; fall back to class detection for dynamic labels."""
    if source_label in SOURCE_REGISTRY:
        return SOURCE_REGISTRY[source_label]
    if source_label.startswith("NI:"):
        return SourceSpec(source_label, "NI", weight=0.85, is_hard_override=True)
    if source_label.startswith("OMA:"):
        return SourceSpec(source_label, "MK", weight=0.40)
    if source_label.startswith("WB:"):
        return SourceSpec(source_label, "WB", weight=0.30)
    if source_label.startswith("UC:"):
        return SourceSpec(source_label, "UC", weight=0.15, requires_moderation=True)
    # Unknown source: treat as lowest-trust WB
    return SourceSpec(source_label, "WB", weight=0.20)
```

---

## 8. field_policy.py

File: `organic_market_agent/crop_book/field_policy.py` (NEW)

```python
"""Field policy — trust order + blend strategy + outlier config per field."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional

@dataclass(frozen=True)
class OutlierConfig:
    domain_fn: Optional[Callable] = None   # e.g. _dtm_leaf_crop_check
    z_threshold: float = 3.5               # modified Z-score threshold (§7.6 LOD200)

@dataclass(frozen=True)
class FieldPolicy:
    trust_order: list[str]           # class priority: ["EX","NI","PR","OP"] etc.
    blend_strategy: str              # "weighted_mean" | "hard_winner" | "latest_op"
    outlier: OutlierConfig = field(default_factory=OutlierConfig)
    multi_year_op_mean: bool = False # True → average all OP values first


def _dtm_leaf_crop_check(name_he: str, value: float) -> bool:
    """Return True if this DTM value is a domain outlier (too low for leaf crop)."""
    from organic_market_agent.crop_book.constants import OUTLIER_CROPS
    return name_he in OUTLIER_CROPS and value < 20


FIELD_POLICY: dict[str, FieldPolicy] = {
    "days_to_maturity": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP"],
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(domain_fn=_dtm_leaf_crop_check, z_threshold=3.5),
    ),
    "avg_yield_per_bed_m": FieldPolicy(
        trust_order=["EX", "NI", "OP", "PR", "WB"],
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(z_threshold=3.0),
        multi_year_op_mean=True,
    ),
    "documented_price": FieldPolicy(
        trust_order=["EX", "NI", "OP", "MK", "WB"],
        blend_strategy="latest_op",     # most recent Tend year wins for OP
        outlier=OutlierConfig(z_threshold=3.0),
    ),
    "in_row_spacing_cm": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP", "WB"],
        blend_strategy="hard_winner",
        outlier=OutlierConfig(z_threshold=3.5),
    ),
    "rows_per_bed": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP"],
        blend_strategy="hard_winner",
    ),
    "planting_season": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP", "WB"],
        blend_strategy="hard_winner",
    ),
    "harvest_window_max_days": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP"],
        blend_strategy="hard_winner",
    ),
    "harvest_window_min_days": FieldPolicy(
        trust_order=["EX", "NI", "PR", "OP"],
        blend_strategy="hard_winner",
    ),
    "rootstock_variety": FieldPolicy(
        trust_order=["EX", "NI", "OP"],
        blend_strategy="hard_winner",
    ),
}
```

---

## 9. reconciler.py — rewrite

File: `organic_market_agent/crop_book/importer/reconciler.py` (REWRITE, existing file)

The existing public API (`reconcile_dtm`, `reconcile_variety`) is preserved as thin
wrappers that call the new engine. This preserves backward compat with any callers.

### 9.1 New engine: `reconcile_field()`

```python
def reconcile_field(
    field_name: str,
    source_rows: list[dict],   # dicts with: field_name, source, value_numeric, unit, note
    name_he: str = "",         # for domain outlier checks
) -> tuple[Decimal | None, dict]:
    """
    Returns (unified_value, enrichment_dict).

    enrichment_dict keys: value_min, value_max, value_best, confidence_score,
                          source_count, winning_source_class
    All source_rows for this field are also mutated:
      row["is_outlier_rejected"] = True/False
      row["trust_tier"] = class code
      row["confidence_weight"] = float or None
    """
```

### 9.2 Algorithm

```
1. Get policy = FIELD_POLICY.get(field_name) — if absent, use default hard_winner/3.5Z
2. For each row in source_rows where row.field_name == field_name:
   a. Look up spec = get_source_spec(row["source"])
   b. Set row["trust_tier"] = spec.cls
   c. Set row["confidence_weight"] = spec.weight (None for EX/NI)
   d. Apply domain outlier check (policy.outlier.domain_fn) if configured → set is_outlier_rejected
3. Collect candidate_rows = rows where NOT is_outlier_rejected
4. Apply statistical outlier gate (§7.6):
   a. Extract numeric values from candidate_rows
   b. If len >= 2: compute modified Z-scores (0.6745 × (x - median) / MAD)
   c. Mark rows where |Z| > policy.outlier.z_threshold as is_outlier_rejected,
      append note "STAT_OUTLIER_REJECTED (Z=X.X)"
5. Remaining non-outlier rows = blend_rows
6. value_min = min(all candidate numeric values, including stat-rejected)
   value_max = max(all candidate numeric values, including stat-rejected)
   (range includes raw data for audit; blend excludes outliers)
7. Check for EX/NI hard override (is_hard_override=True):
   a. If EX present → value_best = EX value; winning_class = "EX"; skip blend
   b. Elif NI present → value_best = NI value; winning_class = "NI"; skip blend
8. Else run blend on blend_rows per policy.blend_strategy:
   weighted_mean: value_best = Σ(weight_i × val_i) / Σ(weight_i)
   hard_winner:   value_best = value from highest-trust-order class present
   latest_op:     value_best = OP value with lexicographically latest source label
                               (Tend_2022 > Tend_2021 > ...) or hard_winner if no OP
9. Compute confidence_score:
   classes_present = len({spec.cls for r in blend_rows})
   classes_possible = len([c for c in policy.trust_order if c not in ("EX","NI")])
   if len(blend_rows) == 0: confidence_score = 0.0
   elif len(blend_rows) == 1: confidence_score = 0.15
   else:
     spread = std_dev(numeric vals) / mean(numeric vals) if mean != 0 else 1.0
     coverage = classes_present / max(classes_possible, 1)
     confidence_score = coverage * (1.0 - min(spread, 1.0) * 0.5)
     clamp to [0.0, 1.0]
10. Return (value_best, {value_min, value_max, value_best, confidence_score,
                         source_count=len(blend_rows), winning_source_class})
```

### 9.3 Backward-compat wrappers

```python
def reconcile_dtm(name_he, tend_values, jmf_value):
    """Legacy wrapper — delegates to reconcile_field."""
    rows = _build_dtm_rows(name_he, tend_values, jmf_value)
    value, enrich = reconcile_field("days_to_maturity", rows, name_he)
    source_rows = [r for r in rows if "value_numeric" in r]
    return value, source_rows

def reconcile_variety(source_rows):
    """Legacy wrapper — returns unified dict as before."""
    unified = {}
    for field_name in FIELD_POLICY:
        field_rows = [r for r in source_rows if r.get("field_name") == field_name]
        if not field_rows:
            continue
        value, _ = reconcile_field(field_name, field_rows)
        if value is not None:
            unified[field_name] = value
            if field_name == "avg_yield_per_bed_m":
                unified["yield_source"] = _winning_source(field_rows)
    # equipment fields (no enrichment, hard_winner only)
    for eq_field in ("seeder", "seeder_front_gear", "seeder_rear_gear", "seeder_roller_plate"):
        val = _best_from_pr_ni(source_rows, eq_field)
        if val:
            unified[eq_field] = val
    return unified
```

---

## 10. enrichment_runner.py

File: `organic_market_agent/crop_book/importer/enrichment_runner.py` (NEW)

```python
"""Compute and upsert crop_field_enrichment rows from existing source_values."""

ENRICHMENT_FIELDS = [
    "days_to_maturity",
    "avg_yield_per_bed_m",
    "documented_price",
    "in_row_spacing_cm",
    "rows_per_bed",
]

def run_enrichment(session, variety_ids: list[int] | None = None) -> int:
    """
    For each variety (optionally filtered), load its source_values for ENRICHMENT_FIELDS,
    call reconcile_field(), upsert into crop_field_enrichment.
    Returns count of upserted rows.
    """
```

Called by:
- `seed.py --enrich` after a full seed run
- `seed.py --all --enrich` (default: enrich after full import)
- Standalone: `python -m organic_market_agent.crop_book.importer.enrichment_runner`

Upsert key: `(variety_id, field_name)` — idempotent.

---

## 11. ni_importer.py — NI class skeleton

File: `organic_market_agent/crop_book/importer/ni_importer.py` (NEW)

Design-registered skeleton. No data files exist yet. Activates when Nimrod provides
files/links (CSV, XLSX, or URL). The class-level design contract:

```python
"""NI (Nimrod-Input) source importer skeleton.

When Nimrod provides a file or URL, add a new NiSource subclass and register it.
Each NI source produces rows formatted identically to Tend/JMF rows but with
source label "NI:<source_name>" and trust_tier="NI".
"""
from abc import ABC, abstractmethod

class NiSourceBase(ABC):
    source_label: str  # "NI:<name>"

    @abstractmethod
    def load(self) -> list[dict]:
        """Return source_value rows: [{"field_name", "source", "value_numeric", "unit"}]"""

# No concrete implementations yet — Nimrod provides files in WP-A build window.
# When files arrive, builder adds a subclass here and registers in SOURCE_REGISTRY.
```

---

## 12. validate_enrichment.py — calibration harness

File: `scripts/validate_enrichment.py` (NEW, standalone)

```
python scripts/validate_enrichment.py [--field FIELD] [--verbose]
```

Algorithm:
1. Connect to DB (reads DATABASE_URL from env)
2. For each variety with at least one EX source_value:
   a. Load all source_values for that variety + field
   b. Shadow run: exclude EX rows (`trust_tier='EX'`)
   c. Call `reconcile_field(field, non_ex_rows, name_he)`
   d. Compare `auto_value` vs `ex_value`
   e. Classify: CALIBRATED / MARGINAL / MISALIGNED (thresholds: ±20% / ±40%)
3. Print tabular report (ASCII table, no external deps)
4. Exit 0 always (misalignment is data quality signal, not failure)

---

## 13. seed.py additions

File: `organic_market_agent/crop_book/importer/seed.py` (MODIFY — add --enrich flag)

Add one CLI flag:
- `--enrich` — run enrichment_runner after seed (default: True for --all, False for --crops)

The `--all` path calls `enrichment_runner.run_enrichment(session)` automatically
unless `--no-enrich` is passed. No other changes to seed.py.

---

## 14. Enrichment SPA artifact

The enrichment JSON is a **new artifact** delivered to WordPress via the existing
`dispatch_upload` mechanism with a new profile `crop_book_enrichment`.

File generated: `output/sfagent-crop-book-enrichment.json`

Schema (top-level):
```json
{
  "generated_at": "2026-XX-XX",
  "schema_version": "1.0",
  "enriched_fields": ["days_to_maturity", "avg_yield_per_bed_m", "documented_price"],
  "varieties": {
    "<variety_id>": {
      "days_to_maturity": {
        "best": 52, "min": 45, "max": 60,
        "confidence": 0.72, "source_count": 3, "winning_class": "PR"
      }
    }
  }
}
```

Generation: new CLI command `python -m organic_market_agent.crop_book.publisher.enrichment_publisher`

This artifact does NOT modify `publisher/upload_dispatch.py` (LOD500_LOCKED).
Instead it uses a standalone script that calls `dispatch_upload` as an imported function
with `profile="crop_book_enrichment"` — this is additive (the profile doesn't exist yet;
if dispatch_upload raises UnknownProfile, the script catches and warns — not a failure).

**Note for builder**: If `dispatch_upload` cannot accept a new profile without code
changes, fall back to generating the JSON file only (no WP upload in WP-A). The JSON
file is the deliverable; upload is best-effort. Flag in BUILD_REPORT if upload skipped.

---

## 15. Acceptance Criteria

### AC-01 — Migrations 041 + 042 created and clean
- `041_crop_field_enrichment.py` creates table with correct DDL; `down_revision="040"`
- `042_source_values_enrich.py` adds 3 columns + backfill; `down_revision="041"`
- `alembic upgrade head` succeeds on clean DB; `alembic downgrade 040` reverses fully
- `alembic upgrade 041; alembic downgrade 040` also works (041 standalone)
- SQLite-compatible (no PostgreSQL-specific types in 041; 042 backfill skipped on SQLite
  via `op.get_bind().dialect.name == 'sqlite'` guard)

### AC-02 — CropFieldEnrichment ORM correct
- `from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment` succeeds
- All 9 columns mapped with correct types
- `CropVariety.enrichments` relationship resolves (back-ref added to models.py)

### AC-03 — Source registry complete
- `SOURCE_REGISTRY` has entries for all 7 source classes (including sentinel entries)
- `get_source_spec("team_00").cls == "EX"` and `is_hard_override == True`
- `get_source_spec("JMF").cls == "PR"`
- `get_source_spec("Tend_2022").cls == "OP"`
- `get_source_spec("NI:some_file.csv").cls == "NI"` (prefix detection)
- `get_source_spec("unknown_label").cls == "WB"` (fallback)

### AC-04 — Field policy covers all reconciled fields
- `FIELD_POLICY` has entries for all 9 fields listed in §8
- `FIELD_POLICY["days_to_maturity"].blend_strategy == "weighted_mean"`
- `FIELD_POLICY["documented_price"].blend_strategy == "latest_op"`
- `FIELD_POLICY["avg_yield_per_bed_m"].multi_year_op_mean == True`

### AC-05 — EX hard override always wins
- `reconcile_field("days_to_maturity", [EX_row(21), PR_row(60), OP_row(45)], "ארוגולה")`
  returns `value_best == 21`, `winning_source_class == "EX"`
- EX row is NOT in the weighted blend

### AC-06 — NI hard override wins over PR/OP
- `reconcile_field("days_to_maturity", [NI_row(50), PR_row(60), OP_row(45)])` returns 50
- `winning_source_class == "NI"`

### AC-07 — Weighted mean correct (no hard overrides)
- `reconcile_field("days_to_maturity", [PR_row(60, w=0.70), OP_row(45, w=0.55)])`
  returns `value_best ≈ 53.7` (= (0.70×60 + 0.55×45) / (0.70+0.55))
- Within 0.1 rounding tolerance

### AC-08 — Statistical outlier gate fires (§7.6)
- Given 4 OP rows: [45, 47, 46, 200] — the 200 is a clear outlier
- `reconcile_field("days_to_maturity", rows_with_200)` marks the 200 row
  `is_outlier_rejected=True` with note containing `STAT_OUTLIER_REJECTED`
- `value_best` computed without the 200 row
- `value_max == 200` (raw range preserved for audit)

### AC-09 — Domain outlier still fires (leaf crop DTM)
- ארוגולה with `tend_dtm=5` (near-harvest snapshot) → `is_outlier_rejected=True`
  with `OUTLIER_REJECTED` note (domain rule)
- Statistical gate and domain gate both independently recorded

### AC-10 — Multi-year OP mean for yield
- `avg_yield_per_bed_m` with OP rows from Tend_2020=8.0, Tend_2021=9.0, Tend_2022=10.0
- OP mean = 9.0 computed first; then blended with PR=11.0: `(0.55×9.0 + 0.70×11.0) / 1.25 ≈ 10.12`

### AC-11 — crop_field_enrichment rows populated
- `seed.py --all --enrich` produces at least one `crop_field_enrichment` row per variety
  that has source_values for at least one of the 5 ENRICHMENT_FIELDS
- `confidence_score` between 0.0 and 1.0 for all rows
- `source_count` ≥ 1 for all rows

### AC-12 — Confidence score formula (single-source edge case)
- Single source row → `confidence_score == 0.15`
- Zero source rows → no enrichment row created (not an error)

### AC-13 — Validation harness produces report
- `python scripts/validate_enrichment.py` exits 0
- Output contains `CALIBRATION REPORT` header
- At least one row for ארוגולה / days_to_maturity (the only current EX override)
- `status` column is CALIBRATED / MARGINAL / MISALIGNED

### AC-14 — NI skeleton importable
- `from organic_market_agent.crop_book.importer.ni_importer import NiSourceBase` succeeds
- `NiSourceBase` is abstract (cannot instantiate directly)

### AC-15 — Migration 042 backfill correct on existing data
- After `alembic upgrade 042` on the live DB:
  - All `source='team_00'` rows have `trust_tier='EX'`
  - All `source='JMF'` rows have `trust_tier='PR'` and `confidence_weight=0.70`
  - All `source LIKE 'Tend%'` rows have `trust_tier='OP'` and `confidence_weight=0.55`
  - Rows with `note LIKE '%OUTLIER_REJECTED%'` have `is_outlier_rejected=TRUE`

### AC-16 — UC rows excluded from blend by default
- A UC source_value row with `confidence_weight IS NULL` is not included in any
  weighted-mean computation (simulated test with SQLite in-memory)

### AC-17 — Enrichment JSON artifact generated
- `python -m organic_market_agent.crop_book.publisher.enrichment_publisher` creates
  `output/sfagent-crop-book-enrichment.json`
- JSON parses cleanly; contains `schema_version`, `enriched_fields`, `varieties` keys
- At least one variety entry with at least one enriched field

### AC-18 — No LOD500_LOCKED files modified beyond GCR_1 scope
- `git diff HEAD~N -- organic_market_agent/crop_book/views.py` is empty
- `git diff HEAD~N -- organic_market_agent/publisher/` is empty
- models.py diff is limited to: CropVarietySourceValue (3 new columns) +
  CropVariety.enrichments relationship — nothing else

### AC-19 — validate_aos.sh 0 FAIL
- `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL

### AC-20 — All existing tests pass
- `pytest tests/` shows all pre-existing crop_book tests PASS (≥ 115 from patch02 baseline)
- No regressions in reconciler backward-compat wrappers (`test_reconciler.py`)

---

## 16. Test requirements

**Minimum 20 new tests** across 5 new test files:

| File | Min tests | Key coverage |
|------|-----------|-------------|
| `test_source_registry.py` | 4 | all 7 classes; prefix detection; unknown fallback |
| `test_field_policy.py` | 4 | all 9 fields; outlier config; blend strategy values |
| `test_enrichment_reconciler.py` | 8 | AC-05..AC-12 above; edge cases |
| `test_enrichment_runner.py` | 3 | SQLite in-memory; upsert idempotency; AC-16 |
| `test_validate_enrichment.py` | 2 | calibration logic; shadow-run delta calculation |

All new tests use SQLite in-memory (or mock) — no PostgreSQL dependency.
Marker: `@pytest.mark.crop_book`

---

## 17. Build sequence (10 steps)

**Step 1** — Read this spec + LOD200 + decision record in full.

**Step 2** — Create `source_registry.py` and `field_policy.py`. Run Python import smoke.

**Step 3** — Create `enrichment_models.py`. Update `models.py` per §5 (GCR_1 scope only).
Verify `from organic_market_agent.crop_book.enrichment_models import CropFieldEnrichment`.

**Step 4** — Create migration 041 (`crop_field_enrichment`). Run `alembic upgrade 041`.
Create migration 042 (`source_values_enrich`). Run `alembic upgrade 042`.

**Step 5** — Rewrite `reconciler.py` with pluggable engine + backward-compat wrappers.
All existing `test_reconciler.py` tests must still pass after this step.

**Step 6** — Create `enrichment_runner.py`. Wire into `seed.py --enrich`.

**Step 7** — Create `ni_importer.py` skeleton. Verify ABC is abstract (cannot instantiate).

**Step 8** — Create `scripts/validate_enrichment.py`. Run against live DB or mock.

**Step 9** — Create `enrichment_publisher` module. Generate enrichment JSON artifact.

**Step 10** — Write all 20 new tests. Run `pytest tests/` → all pass.
Run `validate_aos.sh` → 0 FAIL.
Write `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-A/BUILD_REPORT_v1.0.0.md`.

---

## 18. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | Weighted-mean shifts DTM for ארוגולה away from EX override (21) | LOW | LOW | EX is hard override — no blend; cannot affect ארוגולה |
| R-02 | Statistical gate rejects valid multi-year Tend data as outliers | MEDIUM | MEDIUM | Z-threshold 3.5 is conservative; test against full 66-crop dataset; adjust per field if needed |
| R-03 | Migration 042 backfill slow on large source_values table | LOW | LOW | Backfill is one-time; can run with DB lock timeout; under 10k rows currently |
| R-04 | publisher/ locked — enrichment upload fails | MEDIUM | LOW | AC-17 says upload is best-effort; JSON file is the deliverable; flag in BUILD_REPORT |
| R-05 | NI files arrive during build window and disrupt scope | MEDIUM | LOW | NI skeleton handles this gracefully; new NiSource subclass = additive |
| R-06 | confidence_score formula produces counterintuitive values | LOW | MEDIUM | Tested in AC-12; calibration harness reveals if EX agrees with auto (AC-13) |

---

## 19. LOD500_LOCKED file inventory (do not touch)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/crop_book/views.py` | UI in WP-B |
| `organic_market_agent/publisher/upload_dispatch.py` | LIVE PRODUCTION |
| `organic_market_agent/publisher/*.py` (all existing) | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001–040_*.py` | All prior migrations |
| WordPress mu-plugin `sfagent-crop-book-shortcode.php` | Production deployed |
| `organic_market_agent/crop_book/importer/tend.py` | Existing; reading only |
| `organic_market_agent/crop_book/importer/jmf.py` | Existing; reading only |

**Exception — GCR_1 authorized (models.py):**
`organic_market_agent/crop_book/models.py` — allowed changes:
- Add 3 columns to `CropVarietySourceValue` class
- Add `enrichments` relationship to `CropVariety` class
- Nothing else

---

## 20. File-level deliverables summary

### CREATE (new files)
```
organic_market_agent/crop_book/source_registry.py
organic_market_agent/crop_book/field_policy.py
organic_market_agent/crop_book/enrichment_models.py
organic_market_agent/crop_book/importer/enrichment_runner.py
organic_market_agent/crop_book/importer/ni_importer.py
organic_market_agent/crop_book/publisher/enrichment_publisher.py
organic_market_agent/db/versions/041_crop_field_enrichment.py
organic_market_agent/db/versions/042_source_values_enrich.py
scripts/validate_enrichment.py
tests/crop_book/test_source_registry.py
tests/crop_book/test_field_policy.py
tests/crop_book/test_enrichment_reconciler.py
tests/crop_book/test_enrichment_runner.py
tests/crop_book/test_validate_enrichment.py
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-A/BUILD_REPORT_v1.0.0.md  ← builder writes after L-GATE_B
```

### MODIFY (existing files — GCR_1 scope only)
```
organic_market_agent/crop_book/models.py          ← +3 columns CropVarietySourceValue; +enrichments rel
organic_market_agent/crop_book/importer/reconciler.py  ← full rewrite; wrappers retained
organic_market_agent/crop_book/importer/seed.py   ← add --enrich flag only
CHANGELOG.md                                       ← add [Unreleased] entry
```

---

*LOD400 v1.0.0 — authored 2026-05-23 by team_100 (Claude Sonnet 4.6, Chief Architect)*
*Pending: team_190 L-GATE_S validation*
