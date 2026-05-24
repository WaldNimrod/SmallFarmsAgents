---
id: SFA-S003-P002-WP-B1-LOD400
wp: SFA-S003-P002-WP-B1 — JMF MasterClass Excel Base Layer
gate: L-GATE_S (LOD400 — implementation spec)
status: LOD400_LOCKED — L-GATE_S PASS_WITH_FINDINGS at v1.1.2 (R3); v1.1.3 cleans MINOR carries per verdict §5
author: team_110 (execution mandate per ADR045)
date: 2026-05-24
version: v1.1.3
changelog: >
  v1.1.3 — LOCK CLEANUP per L-GATE_S R3 verdict §5 carry-forward.
  F-S-002-MINOR-R3: §6.4 example + AC-06 wording updated from
  `int | None` / `<int or None>` to non-null sentinel terminology
  (the governing rules in §3/§4/§6.4 cell rules / AC-15 / AC-16 were
  already correct; this just removes residual prose drift).
  F-S-003-MINOR-R3: frontmatter `status` updated from "awaiting
  team_190 L-GATE_S verdict" to "LOD400_LOCKED"; AC-03 parenthetical
  corrected (allow-list widened in R3 v1.1.2, not "tightened in R2
  v1.1.1"); footer updated to point at the R3 verdict path. No
  substantive content change; spec_commit at L-GATE_S PASS was
  `3c92a67` (v1.1.2).
  v1.1.2 — Botanical correction (team_00 review note): `Zucchini` ↔
  `Summer Squash` are NOT separate species at the `crops.name_he`
  level. קישוא is the species; זוקיני is a cultivar of קישוא. The
  species/cultivar distinction belongs in `crop_varieties`, not
  `crops`. v1.1.2 reverts the v1.1.1 mis-split: both English labels
  map to `"קישוא"`. AC-03's allow-list is widened from 1 pair to 2
  by-design pairs: `{Mesclun, Salad Mix} → "תערובת סלט"` AND
  `{Summer Squash, Zucchini} → "קישוא"`. §5 authoring-note rewritten
  with the species/cultivar reasoning.
  v1.1.1 — F-S-001 R2 follow-up fix (now superseded by v1.1.2):
  attempted to disambiguate Zucchini → "זוקיני". This was botanically
  incorrect — see v1.1.2.
  v1.1.0 — F-S-001 fix: §5 now lists the complete 52-entry JMF_CROP_MAP
  contract (no builder-side inference). F-S-002 fix: §3 / §4 / §6.4
  redefine `days_offset` as INTEGER NOT NULL with sentinel constant
  DAYS_OFFSET_PRESENCE_ONLY = -32768 for presence-only `X` cells; UNIQUE
  constraint is now null-safe on both Postgres and SQLite. AC-15 + AC-16
  + §13 R-04 updated accordingly.
  L-GATE_S R1 verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.0.md (FAIL — 2 BLOCKERS).
  L-GATE_S R2 verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.1.md (FAIL — F-S-002 RESOLVED; F-S-001 not fully resolved due to Summer Squash/Zucchini duplicate, fixed in v1.1.1).
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD200_spec.md
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
pre_handoff_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md
wp_a_lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md   # structural template
wp_a_locked_commit: 594cbc8    # WP-A LOD500_LOCKED — engine SSoT
builder: sfa_build (separate session per IR#1)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B1: JMF MasterClass Excel Base Layer

**Read before writing a single line of code:**
1. `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD200_spec.md` — architecture SSoT
2. `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md` — asset paths + row counts
3. `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md` — 4 advisories
4. `organic_market_agent/crop_book/models.py` — existing ORM (LOD500_LOCKED — read-only here)
5. `organic_market_agent/crop_book/source_registry.py` — `SOURCE_REGISTRY["JMF"]` (LOD500_LOCKED)
6. `organic_market_agent/crop_book/field_policy.py` — `FIELD_POLICY` blend strategies
7. `organic_market_agent/crop_book/importer/reconciler.py` — `reconcile_field()` / `Candidate` / `FieldConsensus`
8. `organic_market_agent/crop_book/importer/enrichment_runner.py` — `run_enrichment(session, variety_ids=None, dry_run=False)`
9. `organic_market_agent/crop_book/constants.py` — `TEND_CROP_MAP` (mapping convention to mirror)
10. `organic_market_agent/crop_book/importer/seed.py` — existing CLI surface

---

## 1. Goal

Build the **JMF MasterClass Excel ingestion layer** that supplies the WP-A
enrichment engine with PR-tier (weight `0.70`) baseline values for 11
crop-knowledge fields, and that introduces a new `crop_task_templates`
table (migration 044) for discrete growing-task templates extracted from
the JMF `CROP ASSOCIATED TASKS` sheet.

1. **Migration 044** — `crop_task_templates` table (additive; FK to `crops`).
2. **Migration 045** — backfill / no-op placeholder is **NOT** introduced
   by B1; the next migration slot (045) is reserved for WP-B2.
3. **New importer module** — `organic_market_agent/crop_book/importer/jmf_masterclass.py`
   with 5 sheet parsers + 1 orchestrator, all returning `Candidate` lists
   keyed to existing crop_id / variety_id rows.
4. **New ORM module** — `organic_market_agent/crop_book/crop_task_templates.py`
   (separate from `models.py` per the WP-A precedent for new tables).
5. **`JMF_CROP_MAP` constant** in `constants.py` — English JMF crop name
   → Hebrew `crops.name_he`.
6. **`seed.py` CLI additions** — `--jmf-only`, `--no-jmf` flags;
   `--all` invokes JMF ingestion before existing Tend ingestion.
7. **≥ 25 new tests** covering parsers, mapping, unit conversion, DB
   integration, idempotency, CLI behavior, and one regression assertion
   that EX overrides still win.
8. **WP-A engine reuse only** — every blendable scalar field flows
   through `reconcile_field()`; nothing bypasses it.

On completion:
- `python -m organic_market_agent.crop_book.importer.seed --all` populates
  JMF values via `CropVarietySourceValue(source='JMF', trust_tier='PR',
  confidence_weight=0.70)` AND populates `crop_task_templates` rows for
  every crop that appears in `JMF_CROP_MAP`.
- `python -m organic_market_agent.crop_book.importer.seed --jmf-only`
  runs JMF without Tend.
- `python -m organic_market_agent.crop_book.importer.seed --all --no-jmf`
  reproduces the pre-B1 behavior (Tend-only).

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/crop_book/
├── constants.py                     ← MODIFY: append JMF_CROP_MAP (52 entries)
├── crop_task_templates.py           ← NEW: CropTaskTemplate SQLAlchemy ORM class
└── importer/
    ├── jmf_masterclass.py           ← NEW: 5 parsers + 1 orchestrator
    └── seed.py                      ← MODIFY: --jmf-only, --no-jmf flags + call site

organic_market_agent/db/versions/
└── 044_crop_task_templates.py       ← NEW

tests/crop_book/
├── test_jmf_masterclass_parsers.py        ← NEW
├── test_jmf_crop_map.py                   ← NEW
├── test_jmf_unit_conversions.py           ← NEW
├── test_jmf_masterclass_integration.py    ← NEW (DB integration)
├── test_jmf_idempotency.py                ← NEW
├── test_crop_task_templates_orm.py        ← NEW
├── test_migration_044.py                  ← NEW
├── test_seed_jmf_cli.py                   ← NEW
└── test_jmf_ex_override_regression.py     ← NEW

CHANGELOG.md                                ← MODIFY: [Unreleased] entry
```

### 2.2 No changes to these files (LOD500_LOCKED + WP-A engine SSoT)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/views.py` | LIVE PRODUCTION (admin UI) |
| `organic_market_agent/publisher/wp_upload.py` | LIVE PRODUCTION |
| `organic_market_agent/publisher/upload_dispatch.py` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..043_*.py` | All prior migrations |
| `mu-plugin/` | Deployed WP plugin |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard (CLAUDE.md) |
| `organic_market_agent/crop_book/models.py` | LOD500_LOCKED — B1 needs no new column |
| `organic_market_agent/crop_book/source_registry.py` | WP-A engine SSoT — `SOURCE_REGISTRY["JMF"]` already present |
| `organic_market_agent/crop_book/field_policy.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/reconciler.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/enrichment_runner.py` | WP-A engine SSoT (called by seed.py post-import) |
| `organic_market_agent/crop_book/importer/jmf.py` | Existing empty stub — left untouched; B1 puts all new code in `jmf_masterclass.py` |

---

## 3. Migration 044 — `crop_task_templates`

File: `organic_market_agent/db/versions/044_crop_task_templates.py`

```python
"""Migration 044: crop_task_templates table — per-crop discrete growing tasks.

SFA-S003-P002-WP-B1 LOD400 §3. Additive only; no modification of prior tables.
"""
from alembic import op
import sqlalchemy as sa

revision = "044"
down_revision = "043"
branch_labels = None
depends_on = None

_TASK_TYPE_ENUM = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)
_TIMING_ANCHOR_ENUM = ("seeding", "transplanting", "harvest", "field_prep")

def upgrade():
    op.create_table(
        "crop_task_templates",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=False),
        sa.Column("task_type", sa.VARCHAR(40), nullable=False),
        sa.Column("timing_anchor", sa.VARCHAR(20), nullable=True),
        # F-S-002 (R1): days_offset is NOT NULL with a sentinel value for
        # presence-only ("X") cells. SQL UNIQUE constraints permit multiple
        # NULL tuples on both Postgres and SQLite — nullability here would
        # break idempotent re-import. Sentinel chosen so it is impossible
        # to confuse with a real offset (no agricultural task is scheduled
        # -32768 days from any anchor).
        sa.Column("days_offset", sa.Integer, nullable=False,
                  server_default=sa.text("-32768")),
        sa.Column("method", sa.Text, nullable=True),
        sa.Column("input_material", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        # F-S-002 (R1): all 4 columns are NOT NULL → UNIQUE behaves
        # deterministically on both Postgres and SQLite (no NULL-tuple
        # idempotency hole). Presence-only rows collide via the
        # DAYS_OFFSET_PRESENCE_ONLY sentinel (-32768).
        sa.UniqueConstraint("crop_id", "source", "task_type", "days_offset",
                            name="uq_cct_crop_source_type_offset"),
        sa.CheckConstraint(
            "task_type IN (" + ",".join(repr(v) for v in _TASK_TYPE_ENUM) + ")",
            name="ck_cct_task_type",
        ),
        sa.CheckConstraint(
            "timing_anchor IS NULL OR timing_anchor IN ("
            + ",".join(repr(v) for v in _TIMING_ANCHOR_ENUM) + ")",
            name="ck_cct_timing_anchor",
        ),
    )
    op.create_index("idx_cct_crop", "crop_task_templates", ["crop_id"])
    op.create_index("idx_cct_type", "crop_task_templates", ["task_type"])

def downgrade():
    op.drop_index("idx_cct_type", table_name="crop_task_templates")
    op.drop_index("idx_cct_crop", table_name="crop_task_templates")
    op.drop_table("crop_task_templates")
```

**SQLite compatibility:** `BigInteger().with_variant(Integer(), "sqlite")` matches
the existing WP-A pattern (`enrichment_models.py` line 19). The `server_default=
sa.text("now()")` may need `sa.text("CURRENT_TIMESTAMP")` on SQLite — handle via
`op.get_bind().dialect.name == "sqlite"` branch if `alembic upgrade 044` fails on
SQLite test fixtures.

**CHECK constraint scope (B1 only):** the 14 `task_type` values listed above are
the B1 baseline. WP-B3 will introduce additional values (`nursery_seed`,
`pest_spray`, `potting_up`, `thinning`) via migration 046 by `ALTER TABLE … DROP
CONSTRAINT ck_cct_task_type; ADD CONSTRAINT ck_cct_task_type CHECK …`. B1 must
NOT pre-add B3's values — keep the contract tight to its own scope.

**`days_offset` sentinel (F-S-002 R1 fix):** the column is `INTEGER NOT NULL`
with server-default `-32768`. The Python constant
`DAYS_OFFSET_PRESENCE_ONLY: int = -32768` is exported from
`crop_task_templates.py` (§4) and used by the importer (§6.4) for `X`
(presence-only) cells. Range note: PostgreSQL `INTEGER` is `int32`
(`-2147483648 .. 2147483647`); SQLite stores any signed 64-bit integer. The
sentinel value `-32768` is far outside any plausible real offset (no
agricultural task schedules −90 years from a transplant date), so a future
real-world value cannot collide with it. **Query helper contract:** any view
or downstream module that reads `days_offset` MUST treat
`days_offset == DAYS_OFFSET_PRESENCE_ONLY` as "no specific offset" (display
"—" or "presence only"); arithmetic on the raw value is forbidden.

---

## 4. ORM — `crop_task_templates.py`

File: `organic_market_agent/crop_book/crop_task_templates.py` (NEW)

```python
"""CropTaskTemplate ORM — discrete growing-task rows per crop (migration 044).

SFA-S003-P002-WP-B1 LOD400 §4. Mirrors the WP-A pattern of putting new tables in
their own module rather than touching the LOD500_LOCKED models.py.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, TIMESTAMP, Text,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

# Sentinel value for the `days_offset` column when the source data records
# only task presence (e.g., JMF "X" cells with no integer). NOT NULL on the
# column ensures the (crop_id, source, task_type, days_offset) UNIQUE
# constraint is deterministic on both Postgres and SQLite — see F-S-002 R1.
DAYS_OFFSET_PRESENCE_ONLY: int = -32768


def is_presence_only(days_offset: int) -> bool:
    """Return True if `days_offset` is the presence-only sentinel."""
    return days_offset == DAYS_OFFSET_PRESENCE_ONLY


TASK_TYPE_VALUES: tuple[str, ...] = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)

TIMING_ANCHOR_VALUES: tuple[str, ...] = (
    "seeding", "transplanting", "harvest", "field_prep",
)

class CropTaskTemplate(Base):
    __tablename__ = "crop_task_templates"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", "task_type", "days_offset",
                         name="uq_cct_crop_source_type_offset"),
        CheckConstraint(
            "task_type IN ({})".format(",".join(repr(v) for v in TASK_TYPE_VALUES)),
            name="ck_cct_task_type",
        ),
        CheckConstraint(
            "timing_anchor IS NULL OR timing_anchor IN ({})".format(
                ",".join(repr(v) for v in TIMING_ANCHOR_VALUES)),
            name="ck_cct_timing_anchor",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    task_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    timing_anchor: Mapped[Optional[str]] = mapped_column(VARCHAR(20), nullable=True)
    # F-S-002 (R1): NOT NULL + sentinel default. Use `is_presence_only(row.days_offset)`
    # to detect presence-only rows in callers — never compare against -32768 inline.
    days_offset: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DAYS_OFFSET_PRESENCE_ONLY,
        server_default=str(DAYS_OFFSET_PRESENCE_ONLY),
    )
    method: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_material: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (f"<CropTaskTemplate crop_id={self.crop_id} task_type={self.task_type!r} "
                f"days_offset={self.days_offset} source={self.source!r}>")
```

**No relationship added to `Crop`** — this would require a `models.py` edit
beyond GCR scope. Tests and views use explicit queries
(`session.query(CropTaskTemplate).filter_by(crop_id=…)`). If a back-ref is
ever needed, file GCR-B1-1 first.

---

## 5. `constants.py` modification — `JMF_CROP_MAP`

File: `organic_market_agent/crop_book/constants.py` (MODIFY — append block only)

Append AFTER `OUTLIER_CROPS` (the current tail at line 173). Do NOT modify
anything above this point.

```python
# ---------------------------------------------------------------------------
# JMF MasterClass crop-name map (SFA-S003-P002-WP-B1 LOD400 §5)
# ---------------------------------------------------------------------------
# Maps the English crop-name strings used in JMF CROP CHART / CROP ASSOCIATED
# TASKS / DIRECT SEEDING / NURSERY / CULTIVARS sheets to the canonical
# Hebrew `crops.name_he` values already populated by WP-A.
# On miss (importer encounters a JMF crop not in this map): log WARN and skip
# the row — same convention as TEND_CROP_MAP miss handling in tend.py.
#
# Maintenance: when a new JMF crop appears, append here; do NOT branch on it
# elsewhere. The 52 entries below cover all 52 CROP CHART rows in the
# 2018-edition MasterClass workbook (PROGRAM_BRIEF §1). Spot-check the count
# at test time (test_jmf_crop_map.py — AC-04).

JMF_CROP_MAP: dict[str, str] = {
    # ---- Brassicas ----
    "Arugula":            "ארוגולה",
    "Bok Choy":           "פאק צ'וי",
    "Broccoli":           "ברוקולי",
    "Brussels Sprouts":   "כרוב ניצנים",
    "Cabbage":            "כרוב",
    "Cauliflower":        "כרובית",
    "Kale":               "קייל",
    "Kohlrabi":           "קולורבי",
    "Radishes":           "צנונית",
    "Turnips":            "לפת",
    # ---- Greens / Salads ----
    "Chard":              "מנגולד",
    "Cress":              "גרגר נחלים",
    "Endive":             "אנדיב",
    "Lettuce":            "חסה",
    "Mesclun":            "תערובת סלט",
    "New Zealand Spinach": "תרד ניו-זילנד",
    "Salad Mix":          "תערובת סלט",
    "Spinach":            "תרד",
    # ---- Alliums ----
    "Garlic":             "שום",
    "Leeks":              "כרישה",
    "Onions":             "בצל",
    "Scallions":          "בצל ירוק",
    "Shallots":           "שאלוט",
    # ---- Roots / Tubers ----
    "Beets":              "סלק",
    "Carrots":            "גזר",
    "Celery Root":        "סלרי שורש",
    "Jerusalem Artichokes": "ארטישוק ירושלמי",
    "Parsnips":           "גזר לבן",
    "Potatoes":           "תפוח אדמה",
    "Rutabaga":           "ברוקקואר",
    "Sweet Potatoes":     "בטטה",
    # ---- Solanaceae ----
    "Eggplant":           "חציל",
    "Peppers":            "פלפל",
    "Tomatillos":         "תומאטיו",
    "Tomatoes":           "עגבנייה",
    # ---- Cucurbits ----
    "Cucumbers":          "מלפפון",
    "Melons":             "מלון",
    "Summer Squash":      "קישוא",
    "Watermelons":        "אבטיח",
    "Winter Squash":      "דלעת",
    "Zucchini":           "קישוא",   # cultivar of קישוא; cultivar-level distinction lives in crop_varieties
    # ---- Legumes ----
    "Beans (Bush)":       "שעועית",
    "Beans (Pole)":       "שעועית מטפסת",
    "Fava Beans":         "פול",
    "Peas":               "אפונה",
    "Snow Peas":          "אפונת שלגים",
    # ---- Herbs ----
    "Basil":              "בזיל",
    "Celery":             "סלרי",
    "Cilantro":           "כוסברה",
    "Dill":               "שמיר",
    "Fennel":             "שומר",
    "Parsley":            "פטרוזיליה",
}
# Total: 52 entries. Maintenance rule: when a new JMF MasterClass edition
# adds or renames a crop, append/edit an entry here only — never branch on
# JMF names elsewhere in the codebase. On runtime miss (JMF row whose
# English label is not a key), the importer logs WARN with the unmapped
# label and skips that row (same convention as TEND_CROP_MAP miss handling
# in tend.py). Test AC-03 enforces `len(JMF_CROP_MAP) == 52`.
```

**Authoring note (F-S-001 R1 fix):** the 52 entries above resolve the
PROGRAM_BRIEF "52-row CROP CHART" inventory. Hebrew values are sourced
preferentially from the existing `TEND_CROP_MAP` (where the English label
matches semantically) so JMF and Tend share the same `crops.name_he` —
this is what makes the WP-A enrichment engine able to blend PR (JMF) and
OP (Tend) values for the same crop. JMF-only crops (no Tend counterpart —
e.g., Cauliflower, Endive, Fava Beans, Parsnips, Potatoes, Rutabaga,
Shallots, Snow Peas, Sweet Potatoes, Tomatillos, Watermelons) use Hebrew
names spelled per standard Israeli horticultural usage and will seed
brand-new `crops.name_he` rows on first JMF import.

**Botanical note on Zucchini vs Summer Squash (v1.1.2 correction):**
both English labels resolve to the same `crops.name_he = "קישוא"`
because קישוא is the *species* and זוקיני is a *cultivar group* of
קישוא, not a separate species. The species/cultivar distinction lives
in the `crop_varieties` table (variety-level, populated from JMF
CULTIVARS sheet — see §6.7). A v1.1.1 patch incorrectly separated them
into distinct `crops.name_he` rows; v1.1.2 restores the correct
species-level mapping and adds the pair to the AC-03 allow-list (see
§9 AC-03). AC-03 verifies
the count; the builder must NOT add or remove entries during Step 4 of §11
— if a JMF MasterClass edition encountered at build time has fewer/more
crop rows than this contract specifies, the builder files an inquiry MSG
back to team_110 rather than improvising.

---

## 6. `jmf_masterclass.py` — five parsers + orchestrator

File: `organic_market_agent/crop_book/importer/jmf_masterclass.py` (NEW)

### 6.1 Module header

```python
"""JMF MasterClass XLSX importer (SFA-S003-P002-WP-B1 LOD400 §6).

Reads the JMF MasterClass workbook (5 sheets) and an optional pair of
standalone direct-seeding / nursery copies, producing:

  1. CropVarietySourceValue rows  (source='JMF', trust_tier='PR',
     confidence_weight=0.70) for 11 field names — fed to the WP-A
     enrichment engine via the standard upsert path.
  2. CropTaskTemplate rows (migration 044) for discrete growing tasks.

Public entrypoints:

  parse_crop_chart(xlsx_path)            -> list[dict]
  parse_associated_tasks(xlsx_path)      -> list[CropTaskTemplate]
  parse_direct_seeding_chart(xlsx_path)  -> list[dict]
  parse_nursery_chart(xlsx_path)         -> list[dict]
  parse_cultivars(xlsx_path)             -> list[dict]
  import_jmf_masterclass(session, jmf_dir, *, dry_run=False) -> JmfImportSummary

All parsers return Python primitives only (no DB writes). The orchestrator
opens a transaction, calls upsert helpers, and commits.
"""
```

### 6.2 Data classes

```python
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Optional

@dataclass
class JmfImportSummary:
    crops_seen: int
    source_value_rows_upserted: int
    task_template_rows_upserted: int
    map_misses: list[str]    # JMF crop names with no JMF_CROP_MAP entry
    standalone_divergences: list[tuple[str, str, str, str]]
    # (sheet, crop_he, field_name, "<master>!=<standalone>")
    invalid_offsets: int = 0
    # F-S-002 (R1): count of CROP ASSOCIATED TASKS cells whose integer
    # value collided with DAYS_OFFSET_PRESENCE_ONLY (= -32768) and were
    # therefore skipped with ERROR. Expected: 0 in practice; this counter
    # exists to catch upstream data corruption early.
```

### 6.3 `parse_crop_chart(xlsx_path)`

Sheet: `CROP CHART` (52 rows). Headers (zero-indexed): row 0 = sheet title,
row 1 = column headers. Column-name fragments (case-insensitive substring
match — column order varies by edition):

| Column matched | Returned key (DB field name) | Unit handling |
|----------------|------------------------------|----------------|
| `Crop` | `crop_jmf_en` (raw English label) | — |
| `DTM` or `Days to Maturity` | `days_to_maturity` | integer days |
| `Harvest Window` (max) | `harvest_window_max_days` | integer days |
| `Yield` or `Yield per Bed` | `avg_yield_per_bed_m` | convert per-100-bed → per-meter (see §7.1) |
| `Price` | `documented_price` | strip currency symbol; Decimal |
| `Unit` (paired with Price) | `documented_price_unit` | text passthrough |

Returns `list[dict]` with one dict per non-empty row. Missing values are
omitted from the dict (do NOT emit keys with `None` — the upsert layer
treats absent keys as "no observation").

### 6.4 `parse_associated_tasks(xlsx_path)`

Sheet: `CROP ASSOCIATED TASKS` (30 rows × 14 task-type columns). Each cell
contains either a blank, an integer (days offset), or an `X` (presence
flag). The parser emits one `CropTaskTemplate`-shaped dict per non-blank
cell:

```python
{
    "crop_jmf_en": <row label>,
    "task_type":   <one of TASK_TYPE_VALUES — derived from column header
                    via _TASK_COLUMN_MAP (defined below)>,
    "timing_anchor": "seeding",  # default for JMF (override via _TASK_TIMING_MAP)
    "days_offset":   <int — DAYS_OFFSET_PRESENCE_ONLY for X cells>,
    "method":        None,
    "input_material": None,
    "notes":         None,
}
```

`_TASK_COLUMN_MAP` (column-header substring → `task_type`):

```python
_TASK_COLUMN_MAP: dict[str, str] = {
    "Stale Seed Bed":         "stale_seed_bed",
    "Flame":                  "flame_weeder",
    "Flextine 1":             "flextine_harrow_1",
    "Flextine 2":             "flextine_harrow_2",
    "Biodisc":                "biodisc",
    "Hoe":                    "hoe",
    "Hand Weed":              "hand_weed",
    "Boron Seaweed 1":        "boron_seaweed_1",
    "Boron Seaweed 2":        "boron_seaweed_2",
    "Straw Mulch":            "straw_mulch_topdress",
    "Head Pinch":             "head_pinch_chop",
    "Mow and Tarp":           "mow_and_tarp",
    "At Seeding":             "at_seeding_transplanting",
    "Row Cover":              "net_row_cover",
}
_TASK_TIMING_MAP: dict[str, str] = {
    "stale_seed_bed":  "field_prep",
    "flame_weeder":    "field_prep",
    "at_seeding_transplanting": "seeding",
    # All others default to "seeding".
}
```

**Cell parsing rules** (F-S-002 R1 fix — `days_offset` is NOT NULL):
- Empty / whitespace → skip (no row emitted; the absence of a row IS the
  "no observation" signal — do NOT emit a sentinel row).
- `X` (case-insensitive) → `days_offset = DAYS_OFFSET_PRESENCE_ONLY`
  (imported from `crop_task_templates`). The row is emitted and the
  `(crop_id, source='JMF', task_type, -32768)` UNIQUE constraint
  collapses duplicate `X` observations from re-imports — idempotency
  guarantee for AC-07a, AC-15.
- Integer → `days_offset = int(value)`. The parser must reject any value
  equal to `DAYS_OFFSET_PRESENCE_ONLY` from the upstream sheet (an actual
  −32768 day offset is implausible and would corrupt the sentinel
  contract). If encountered, log ERROR with `crop_jmf_en` + `task_type`,
  skip the cell, increment a `summary.invalid_offsets` counter. (Add this
  field to `JmfImportSummary` in §6.2.)
- Negative integers are allowed (pre-planting tasks like
  `stale_seed_bed`) provided they are **not** equal to the sentinel.
- Anything else (e.g. "5-7 days") → log WARN, store raw text in `notes`,
  set `days_offset = DAYS_OFFSET_PRESENCE_ONLY` (so the row is still
  represented but UNIQUE behavior remains deterministic).

### 6.5 `parse_direct_seeding_chart(xlsx_path)`

Sheet: `DIRECT SEEDING CHART` (21 rows). Column-name fragments:

| Column matched | Returned key | Unit handling |
|----------------|---------------|----------------|
| `Crop` | `crop_jmf_en` | — |
| `In-Row Spacing` | `in_row_spacing_cm` | **inch → cm** via `* Decimal("2.54")` (see §7.2) |
| `Rows per Bed` | `rows_per_bed` | integer |
| `Seed Density` | `direct_seed_density_g` | grams per bed, Decimal |
| `Seeder` | `seeder` (stored as `value_text`) | string |

### 6.6 `parse_nursery_chart(xlsx_path)`

Sheet: `NURSERY & TRANSPLANT CHART` (45 rows). Columns:

| Column matched | Returned key | Unit handling |
|----------------|---------------|----------------|
| `Crop` | `crop_jmf_en` | — |
| `Days in Cell` (min/max) | `days_in_nursery_cell` | midpoint stored (`(min+max)/2` rounded to int); range appended to `note` as `"range:<min>-<max>"` |
| `Tray Type` | `nursery_tray_type` | string |
| `In-Row Spacing` | `in_row_spacing_cm` | **inch → cm** (same as §6.5) |
| `Rows per Bed` | `rows_per_bed` | integer |

### 6.7 `parse_cultivars(xlsx_path)`

Sheet: `CULTIVARS` (136 rows). Columns:

| Column matched | Returned key | Unit handling |
|----------------|---------------|----------------|
| `Crop` | `crop_jmf_en` | — |
| `Cultivar` | `variety_name_en` (target join key on `crop_varieties.name_en`) | — |
| `Provider` or `Supplier` | `cultivar_provider` | string |
| `DTM` | `days_to_maturity` (variety-scoped) | integer days |
| `Description` | `cultivar_description` | string |
| `Comments` | `cultivar_description` (append; `' / '`-joined) | string |

### 6.8 `import_jmf_masterclass(session, jmf_dir, *, dry_run=False)`

```python
def import_jmf_masterclass(
    session: Session,
    jmf_dir: Path,
    *,
    dry_run: bool = False,
) -> JmfImportSummary:
    """End-to-end orchestrator.

    Steps:
      1. Resolve the master workbook  (jmf_dir / "CROPPLANNINGTOOLMASTERCLASS-*.XLSX")
         and the two standalone files (jmf_dir / "תבלאות נתונים" / ...).
         Missing master → log WARN, return zero-summary. (No exception.)
      2. Call the 5 parsers (master) + 2 standalone parsers.
      3. Cross-check standalone vs master for direct-seeding + nursery sheets;
         master wins, divergences appended to summary.standalone_divergences.
      4. For each row, resolve crop_id via JMF_CROP_MAP[crop_jmf_en] →
         crops.name_he. Miss → append to summary.map_misses, skip.
      5. For each numeric scalar field, build a Candidate and call
         _upsert_source_value(session, variety_id, field_name, value, ...)
         which performs the (variety_id, field_name, source='JMF') upsert
         on crop_variety_source_values. (See §6.9 for variety resolution.)
      6. For each task-template dict from parse_associated_tasks, call
         _upsert_task_template(session, crop_id, row) which upserts on the
         (crop_id, source='JMF', task_type, days_offset) unique key.
      7. If dry_run: session.rollback(); else session.commit().
      8. Return JmfImportSummary.
    """
```

### 6.9 Variety resolution policy

JMF CROP CHART / DIRECT SEEDING / NURSERY rows are crop-scoped (no
cultivar). For these, attach the `source_value` to the **default
"baseline" variety** for that crop — i.e. the synthetic variety created by
the existing WP-A Tend importer when no cultivar text is supplied. The
selector:

```python
def _default_variety_id(session, crop_id: int) -> int:
    v = (session.query(CropVariety)
         .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
         .one_or_none())
    if v is None:
        v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
        session.add(v); session.flush()
    return v.id
```

CULTIVARS rows ARE variety-scoped. Match `(crop_id, name_en=cultivar)`;
create on miss with the cultivar name.

### 6.10 Source-value upsert helper

```python
def _upsert_source_value(
    session,
    variety_id: int,
    field_name: str,
    value_numeric: Optional[Decimal] = None,
    value_text:    Optional[str]     = None,
    unit:          Optional[str]     = None,
    note:          Optional[str]     = None,
) -> CropVarietySourceValue:
    """Upsert on (variety_id, field_name, source='JMF').

    trust_tier='PR', confidence_weight=0.70, is_outlier_rejected=False
    are hardcoded here (not read from SOURCE_REGISTRY — they are the
    contract this importer exists to provide).
    """
    SOURCE = "JMF"
    row = (session.query(CropVarietySourceValue)
           .filter_by(variety_id=variety_id, field_name=field_name, source=SOURCE)
           .one_or_none())
    if row is None:
        row = CropVarietySourceValue(
            variety_id=variety_id, field_name=field_name, source=SOURCE,
        )
        session.add(row)
    row.value_numeric = value_numeric
    row.value_text    = value_text
    row.unit          = unit
    row.note          = note
    row.trust_tier         = "PR"
    row.confidence_weight  = Decimal("0.70")
    row.is_outlier_rejected = False
    session.flush()
    return row
```

Idempotency: re-running the importer over the same XLSX with no data
changes produces zero row mutations beyond `updated_at` semantics (none
present — there is no `updated_at` column on `crop_variety_source_values`).
Counter-test AC-07.

---

## 7. Unit conversions

### 7.1 Yield: per-100-bed → per-meter

JMF reports yield as "lbs per 100ft bed" or "kg per 100m bed". The DB
stores `avg_yield_per_bed_m` as **kg per 1 meter of bed**.

Conversion table:

| JMF unit string | Multiplier to kg/m |
|------------------|--------------------|
| `lbs/100ft` | `Decimal("0.453592") / Decimal("30.48")` = ≈ `0.014882` |
| `kg/100m`   | `Decimal("0.01")` |
| `kg/100ft`  | `Decimal("1") / Decimal("30.48")` = ≈ `0.032808` |
| `lbs/100m`  | `Decimal("0.453592") / Decimal("100")` = ≈ `0.004536` |

Worked examples (must produce these values in `test_jmf_unit_conversions.py`):
- Input: `200 lbs/100ft` → `200 * 0.014882` = `2.9764` kg/m
- Input: `500 kg/100m`   → `5.00` kg/m
- Input: `300 kg/100ft`  → `300 * 0.032808` = `9.8424` kg/m

Round to 4 decimal places using `Decimal.quantize(Decimal("0.0001"))`.

### 7.2 Spacing: inch → cm

`in_row_spacing_cm = inches * Decimal("2.54")`. Worked examples:
- `2"` → `5.08 cm`
- `4"` → `10.16 cm`
- `12"` → `30.48 cm`

Round to 2 decimal places.

### 7.3 NULL handling

Any of the above conversions on a NULL / blank cell returns `None` and the
upsert skips that field for that row (do not write `NULL` into `value_numeric`
— omit the call entirely).

---

## 8. `seed.py` modifications

File: `organic_market_agent/crop_book/importer/seed.py` (MODIFY — additive)

### 8.1 New CLI flags

Add after the existing `--jmf-dir` flag (line ~473):

```python
parser.add_argument(
    "--jmf-masterclass-dir", type=Path,
    default=Path("/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning"),
    metavar="PATH",
    help="JMF MasterClass XLSX directory (default: %(default)s)",
)
parser.add_argument(
    "--jmf-only", action="store_true",
    help="Run only JMF MasterClass ingestion (skip Tend).",
)
parser.add_argument(
    "--no-jmf", action="store_true",
    help="Skip JMF MasterClass ingestion (Tend only).",
)
```

`--jmf-only` and `--no-jmf` are mutually exclusive — enforce with
`parser.add_mutually_exclusive_group()`.

### 8.2 New call site

Inside the existing `with SessionFactory() as session:` block, BEFORE the
existing Tend seed call:

```python
if not args.no_jmf:
    from organic_market_agent.crop_book.importer.jmf_masterclass import import_jmf_masterclass
    jmf_summary = import_jmf_masterclass(
        session, args.jmf_masterclass_dir, dry_run=args.dry_run,
    )
    logger.info("JMF MasterClass: %s", jmf_summary)
    if jmf_summary.map_misses:
        logger.warning("JMF map misses (%d): %s",
                       len(jmf_summary.map_misses),
                       ", ".join(jmf_summary.map_misses[:10]))
    if jmf_summary.standalone_divergences:
        logger.warning("JMF standalone divergences (%d) — master wins",
                       len(jmf_summary.standalone_divergences))
    session.flush()

if args.jmf_only:
    if args.all and not args.no_enrich:
        from organic_market_agent.crop_book.importer.enrichment_runner import run_enrichment
        summary = run_enrichment(session, dry_run=args.dry_run)
        logger.info("Enrichment: %s", summary)
    if not args.dry_run:
        session.commit()
    return

# (existing Tend seed call remains here, unchanged)
```

### 8.3 Mutual-exclusion validation

Add after `args = parser.parse_args()`:

```python
if args.jmf_only and args.no_jmf:
    parser.error("--jmf-only and --no-jmf are mutually exclusive")
if args.jmf_only and args.crops:
    parser.error("--jmf-only cannot be combined with --crops")
```

---

## 9. Acceptance Criteria

**AC-01 — Migration 044 created and clean.**
`alembic upgrade head` on an empty DB creates `crop_task_templates` with
the exact DDL in §3; `alembic downgrade 043` drops the table and both
indices; `alembic upgrade 044` standalone (after `downgrade 043`) also
succeeds. SQLite and PostgreSQL both work.

**AC-02 — `CropTaskTemplate` ORM correct.**
`from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate`
succeeds; all 13 columns map to the correct types; `TASK_TYPE_VALUES` and
`TIMING_ANCHOR_VALUES` tuples are exported and match the migration enums.

**AC-03 — `JMF_CROP_MAP` is exactly 52 entries.**
*(F-S-001 R1 fix; allow-list widened to 2 by-design pairs in R3 v1.1.2 — species-level mapping per team_00 botanical review.)*
`from organic_market_agent.crop_book.constants import JMF_CROP_MAP`
succeeds; `len(JMF_CROP_MAP) == 52`; every key is a unique non-empty
ASCII English string; every value is a non-empty Hebrew string.

**Duplicate-target allow-list (exhaustive — 2 pairs by botanical design):**

| English keys (JMF) | Hebrew target | Reason |
|---|---|---|
| `Mesclun`, `Salad Mix` | `"תערובת סלט"` | Both denote the same Israeli salad-greens mix; one `crops.name_he` row serves both English labels. |
| `Summer Squash`, `Zucchini` | `"קישוא"` | קישוא is the **species** (*Cucurbita pepo* in its market-garden sense); זוקיני is a **cultivar** of קישוא. The species/cultivar distinction lives in the `crop_varieties` table (variety-level — populated from JMF CULTIVARS sheet per §6.7), not in `crops.name_he`. Both JMF English labels therefore correctly resolve to the same `crops.name_he`. |

Implementation assertion:

```python
from collections import Counter
counts = Counter(JMF_CROP_MAP.values())
duplicates = {v: sorted([k for k, mv in JMF_CROP_MAP.items() if mv == v])
              for v, c in counts.items() if c > 1}
assert duplicates == {
    "תערובת סלט": ["Mesclun", "Salad Mix"],
    "קישוא":       ["Summer Squash", "Zucchini"],
}, f"unexpected Hebrew-value duplicates: {duplicates}"
```

Any future addition of a duplicate target requires a LOD400 patch +
L-GATE_S re-run; this is NOT a builder-side judgement.

**AC-04 — Map coverage vs. live JMF CROP CHART.**
After `parse_crop_chart(<master XLSX>)`, the set of distinct
`crop_jmf_en` values returned by the parser equals the keys of
`JMF_CROP_MAP` minus the deliberate duplicate `Mesclun` (which doesn't
appear in CROP CHART; it's a Tend-side synonym preserved in the map for
convenience). If the JMF MasterClass workbook on disk has a Crop value
that is NOT in `JMF_CROP_MAP`, the test FAILs with the missing key listed
— team_110 then issues a follow-up patch and re-runs L-GATE_S R3 (NOT a
builder-side improvisation).

**AC-05 — `parse_crop_chart` returns 52 rows with required keys.**
Length ≥ 50 (allowing for empty trailing rows). Every row has
`crop_jmf_en`; at least 90% have `days_to_maturity`.

**AC-06 — `parse_associated_tasks` emits typed rows per non-blank cell.**
For the master XLSX, ≥ 100 rows emitted (30 crops × ~4 tasks each on
average); every row's `task_type` is in `TASK_TYPE_VALUES`; days_offset is
`int` (NOT NULL; `DAYS_OFFSET_PRESENCE_ONLY` for X cells per F-S-002 fix); `notes` populated only when the raw cell is non-numeric and
non-`X`.

**AC-07 — Idempotent re-import.**
Running `import_jmf_masterclass(session, jmf_dir)` twice in a row produces
the same row count in `crop_variety_source_values` and
`crop_task_templates` after the second call as after the first. No
`IntegrityError`. Test AC-07a counts; AC-07b inspects mutation count via
SQL `pg_stat_user_tables` (PG) or `sqlite_stat1` (SQLite) — for SQLite,
use a row-modified counter assertion via `session.dirty` after `flush()`.

**AC-08 — Unit conversion: yield (per §7.1).**
Three worked examples from §7.1 produce the documented kg/m values to
4-decimal precision.

**AC-09 — Unit conversion: spacing (per §7.2).**
Three worked examples from §7.2 produce the documented cm values to
2-decimal precision.

**AC-10 — NULL pass-through.**
Empty cells produce NO `source_value` row (not a NULL `value_numeric`
row). Asserted by counting rows for a crop where the input cell is blank.

**AC-11 — JMF crop appears in `crop_variety_source_values` with correct trust.**
After `import_jmf_masterclass`, at least one row exists with
`source='JMF'`, `trust_tier='PR'`, `confidence_weight=Decimal("0.70")`,
`is_outlier_rejected=False`.

**AC-12 — Enrichment runner integrates with JMF rows.**
After `import_jmf_masterclass` + `run_enrichment(session)`, at least one
`crop_field_enrichment` row exists with `source_count >= 2` (JMF + Tend
together) for `days_to_maturity` on a crop that has both.

**AC-13 — EX override regression.**
ARUGULA (`name_he='ארוגולה'`): after WP-A `--all` (TEAM00_DTM_OVERRIDES
inserts EX value 21) AND `import_jmf_masterclass` (JMF DTM ≈ 60), the
`crop_field_enrichment` row for `days_to_maturity` on the ARUGULA variety
has `value_best == Decimal("21")` and `winning_source_class == "EX"`.
EX hard override **must** continue to win — proves WP-A engine reuse is
correctly wired.

**AC-14 — `crop_task_templates` populated for at least 20 crops.**
After full `seed.py --all`, `SELECT COUNT(DISTINCT crop_id) FROM
crop_task_templates WHERE source = 'JMF'` is ≥ 20.

**AC-15 — UNIQUE constraint enforced on `crop_task_templates` (incl. presence-only).**
*(F-S-002 R1 fix — split into 3 sub-assertions.)*
- **AC-15a** — Inserting two rows with identical
  `(crop_id, source, task_type, days_offset)` where `days_offset` is a
  real integer raises `IntegrityError` on both Postgres and SQLite.
- **AC-15b** — Inserting two rows with identical
  `(crop_id, source, task_type, DAYS_OFFSET_PRESENCE_ONLY)` (i.e., two
  presence-only `X` observations of the same task on the same crop)
  ALSO raises `IntegrityError`. This was the F-S-002 idempotency hole and
  is the regression assertion for the fix.
- **AC-15c** — Inserting a row with `days_offset = None` is rejected at
  ORM-level (raises `IntegrityError` from the `NOT NULL` constraint).
  Re-import via `_upsert_task_template` is idempotent because the upsert
  matches on the full 4-column key (no NULL involvement).

**AC-16 — CHECK constraint enforced on `task_type` + `days_offset` NOT NULL.**
- **AC-16a** — Inserting a row with `task_type='nursery_seed'` (reserved
  for WP-B3) raises `IntegrityError`. Confirms B1 does NOT pre-add B3
  enum values.
- **AC-16b** — Inserting a row that explicitly sets `days_offset=None`
  raises `IntegrityError` (`NOT NULL` violation). This complements
  AC-15c — proves the column nullability discipline holds at the
  database level, not just the ORM level.

**AC-17 — CLI `--jmf-only` skips Tend.**
`seed.py --jmf-only --dry-run` does NOT import Tend rows
(`crops` table count comes only from JMF crops + WP-A baseline).

**AC-18 — CLI `--no-jmf` skips JMF.**
`seed.py --all --no-jmf --dry-run` produces zero rows with
`source='JMF'`.

**AC-19 — Mutual exclusion enforced.**
`seed.py --jmf-only --no-jmf` exits with non-zero status and prints an
argparse error.

**AC-20 — `validate_aos.sh` 0 FAIL.**
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
returns `RESULT: 29 PASS / 17 SKIP / 0 FAIL`.

**AC-21 — Existing crop_book tests pass.**
`pytest tests/crop_book/ -q` shows zero regressions vs the pre-B1
baseline (WP-A LOD500_LOCKED at `594cbc8` had ≥ 115 passing tests).

**AC-22 — No LOD500_LOCKED file modified beyond §2.1 scope.**
`git diff 594cbc8..HEAD -- <each locked path in §2.2>` is empty.
`git diff 594cbc8..HEAD -- organic_market_agent/crop_book/models.py` is
empty (B1 introduces no GCR).

---

## 10. Test requirements

**Minimum 25 new tests** across 9 new test files:

| File | Min tests | Key coverage (AC linkage) |
|------|-----------|----------------------------|
| `test_jmf_masterclass_parsers.py` | 6 | AC-05, AC-06; one test per sheet (crop_chart, associated_tasks, direct_seeding, nursery, cultivars) + 1 edge case (empty workbook) |
| `test_jmf_crop_map.py` | 3 | AC-03, AC-04; coverage assertion + miss-handling + Hebrew encoding round-trip |
| `test_jmf_unit_conversions.py` | 4 | AC-08, AC-09, AC-10; yield × 3 inputs + spacing × 3 inputs + NULL pass-through |
| `test_jmf_masterclass_integration.py` | 4 | AC-11, AC-12, AC-14; SQLite in-memory; variety resolution; enrichment runner integration |
| `test_jmf_idempotency.py` | 2 | AC-07a, AC-07b |
| `test_crop_task_templates_orm.py` | 3 | AC-02 (column / enum tuple coverage) + AC-16b (`days_offset = None` rejected at ORM-level) + `is_presence_only(DAYS_OFFSET_PRESENCE_ONLY) is True` |
| `test_migration_044.py` | 4 | AC-01 forward + AC-15a (real-offset duplicate) + AC-15b (presence-only duplicate; F-S-002 R1 regression) + AC-16a (`task_type='nursery_seed'` rejected) |
| `test_seed_jmf_cli.py` | 3 | AC-17, AC-18, AC-19 |
| `test_jmf_ex_override_regression.py` | 1 | AC-13 (the most important regression assertion) |

All tests use SQLite in-memory or a real fixture XLSX file under
`tests/crop_book/fixtures/jmf/` (builder creates ≥ 1 minimal fixture
workbook with 3 crops covering each of the 5 sheets — required for
parser tests). Marker: `@pytest.mark.crop_book`.

---

## 11. Build sequence (10 steps)

**Step 1** — Read this LOD400 + LOD200 + PROGRAM_BRIEF in full.

**Step 2** — Create `crop_task_templates.py` (ORM). Verify import smoke:
`python -c "from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate, TASK_TYPE_VALUES; print(len(TASK_TYPE_VALUES))"` → `14`.

**Step 3** — Create migration 044. Run `alembic upgrade 044` against a
fresh SQLite DB and verify table + indices. Run `alembic downgrade 043`,
then `alembic upgrade 044` again.

**Step 4** — Append `JMF_CROP_MAP` to `constants.py` **verbatim from §5
of this spec** (all 52 entries — do NOT derive, infer, or shorten). The
spec is the contract; do not consult `crops.name_en` or the live XLSX
for the mapping. After paste, run AC-03 (`len(JMF_CROP_MAP) == 52` and
key/value uniqueness rules) and AC-04 (live XLSX coverage check). If
AC-04 reports a missing key, STOP and file an inquiry MSG back to
team_110 per the F-S-001 R1 contract — do NOT improvise.

**Step 5** — Create `jmf_masterclass.py` with the 5 parser functions
(no DB writes yet). Write `test_jmf_masterclass_parsers.py` against a
minimal fixture workbook (3 crops). Achieve AC-05, AC-06.

**Step 6** — Add unit conversion helpers (`_yield_to_per_meter`,
`_inches_to_cm`). Write `test_jmf_unit_conversions.py`. Achieve AC-08, AC-09, AC-10.

**Step 7** — Add `import_jmf_masterclass` orchestrator + the two upsert
helpers. Write `test_jmf_masterclass_integration.py` and
`test_jmf_idempotency.py`. Achieve AC-07, AC-11, AC-14.

**Step 8** — Wire seed.py CLI flags (`--jmf-only`, `--no-jmf`,
`--jmf-masterclass-dir`) and call site. Write `test_seed_jmf_cli.py`.
Achieve AC-17, AC-18, AC-19.

**Step 9** — Write `test_jmf_ex_override_regression.py`. This is the
single most important test — it proves the WP-A engine integration is
correct end-to-end and that B1 has not regressed any prior calibration.
Achieve AC-13.

**Step 10** — Run `pytest tests/crop_book/ -q` → all green (≥ 140 tests
total: 115 baseline + 25 new). Run
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
→ 0 FAIL. Update `CHANGELOG.md` `[Unreleased]` section. Write
`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/BUILD_REPORT_v1.0.0.md` per
the canonical template, including: per-AC pass/fail, test counts,
unmodified-LOD500_LOCKED audit, runtime stats for the full import on the
live workbook (varieties touched, source_value rows upserted, task
templates inserted).

---

## 12. PRE_HANDOFF advisory disposition

Per `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B/PRE_HANDOFF_VERDICT_v1.0.0.md`
§4 (4 advisory items):

| # | Advisory | WP-B1 disposition |
|---|---|---|
| 1 | JMF PDF licensing — extracted prose for internal farm-use only | **N/A** for B1 (Excel only; no narrative prose extracted). Carried to WP-B2 LOD400. |
| 2 | LLM extraction cache strategy (`data/jmf/extracted/`) | **N/A** for B1 (no LLM step). Carried to WP-B2 LOD400. |
| 3 | Tend task whitelist — confirm with team_00 before lock | **N/A** for B1 (B1 does not parse Tend). Carried to WP-B3 LOD400. |
| 4 | Transitive WP-A dependency made explicit | **Addressed** explicitly in §1 (commit `594cbc8`), §2.2 (every WP-A file listed as "no changes"), §6.10 (engine-reuse upsert contract), and AC-13 (regression test that proves engine reuse is correct). |

---

## 13. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | JMF CROP CHART column-header drift across MasterClass editions | MEDIUM | MEDIUM | Parsers use case-insensitive substring match (§6.3); fallback log WARN on missing column; AC-05 catches gross structural change. |
| R-02 | Hebrew encoding issues writing `JMF_CROP_MAP` values into Python source | LOW | LOW | Python 3.11 source is UTF-8 by default; `test_jmf_crop_map.py` round-trips a sample Hebrew value through `repr()` / `eval()`. |
| R-03 | Yield-unit string varies ("lbs/100ft" vs "lb/100'") | MEDIUM | LOW | Conversion table in §7.1 is keyed on exact strings; unknown unit → log WARN, skip the value. AC-08 covers the documented strings only; uncommon variants surface in the importer's `map_misses` channel. |
| R-04 | CHECK constraint syntax differs on SQLite vs Postgres | LOW | MEDIUM | Both support `CHECK (col IN (...))` form. Tested by AC-01 + AC-16a on SQLite; integration env runs Postgres. |
| R-08 | `days_offset` sentinel (-32768) collides with a real future offset | NEGLIGIBLE | LOW | No agricultural task is scheduled −32768 days from any anchor. Parser rejects any input cell equal to the sentinel (logs ERROR + increments `summary.invalid_offsets`). AC-15b regression-tests UNIQUE for presence-only rows. F-S-002 R1 fix. |
| R-09 | `JMF_CROP_MAP` Hebrew value drifts from MasterClass edition | LOW | LOW | Hebrew values are the contract for `crops.name_he` — they MUST be stable across editions. New JMF MasterClass editions that add crops require a team_110 LOD400 patch (NOT a builder improvisation per §11 Step 4). F-S-001 R1 fix. |
| R-05 | Existing `parse_jmf_dir` in `jmf.py` still wired into seed.py | LOW | LOW | Confirmed by reading seed.py line 471 — the existing `--jmf-dir` flag points to a different default path. B1 adds an independent `--jmf-masterclass-dir` flag. Old call site can stay (returns 0 rows; harmless). Builder verifies in Step 8. |
| R-06 | `_default_variety_id` collides with WP-A's variety creation | LOW | MEDIUM | Same selector predicate (`name_en IS NULL`) as WP-A; concurrent inserts in the same session are serialized by SQLAlchemy. Tested in AC-07. |
| R-07 | Migration 044 conflicts with WP-A migration 043 if 043's down_revision shifts | LOW | LOW | Confirmed at spec time: `043` is the current head (43 files in `db/versions/`). Builder verifies by reading `043_backfill_source_values_trust.py` for the `revision = "043"` line. |

---

## 14. LOD500_LOCKED file inventory (must not be modified)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/views.py` | UI |
| `organic_market_agent/publisher/wp_upload.py` | LIVE PRODUCTION |
| `organic_market_agent/publisher/upload_dispatch.py` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..043_*.py` | All prior migrations |
| `mu-plugin/` | Deployed WP plugin |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard |
| `organic_market_agent/crop_book/models.py` | LOD500_LOCKED (B1 = no GCR) |
| `organic_market_agent/crop_book/source_registry.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/field_policy.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/enrichment_models.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/reconciler.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/enrichment_runner.py` | WP-A engine SSoT |

**Permitted modifications (additive only):**

| File / path | Scope of change |
|-------------|-----------------|
| `organic_market_agent/crop_book/constants.py` | Append `JMF_CROP_MAP` after `OUTLIER_CROPS`; nothing else. |
| `organic_market_agent/crop_book/importer/seed.py` | Add 3 CLI flags + 1 new call-site block (per §8). Existing logic untouched. |
| `CHANGELOG.md` | Append `[Unreleased]` entry. |

---

## 15. File-level deliverables summary

### CREATE (new files)

```
organic_market_agent/crop_book/crop_task_templates.py
organic_market_agent/crop_book/importer/jmf_masterclass.py
organic_market_agent/db/versions/044_crop_task_templates.py
tests/crop_book/test_jmf_masterclass_parsers.py
tests/crop_book/test_jmf_crop_map.py
tests/crop_book/test_jmf_unit_conversions.py
tests/crop_book/test_jmf_masterclass_integration.py
tests/crop_book/test_jmf_idempotency.py
tests/crop_book/test_crop_task_templates_orm.py
tests/crop_book/test_migration_044.py
tests/crop_book/test_seed_jmf_cli.py
tests/crop_book/test_jmf_ex_override_regression.py
tests/crop_book/fixtures/jmf/minimal_masterclass.xlsx     (binary fixture — 3 crops)
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/BUILD_REPORT_v1.0.0.md  (builder writes after L-GATE_B)
```

### MODIFY (existing files — additive scope only)

```
organic_market_agent/crop_book/constants.py             ← +JMF_CROP_MAP block (52 entries)
organic_market_agent/crop_book/importer/seed.py         ← +3 CLI flags, +1 call-site block
CHANGELOG.md                                              ← +[Unreleased] entry
```

### DO NOT TOUCH

See §14 LOD500_LOCKED inventory.

---

*LOD400 v1.1.3 — LOCKED 2026-05-24 by team_110 under EXECUTION_MANDATE
SFA-S003-P002-WP-B (ADR045, `execution_authority: full`). L-GATE_S
PASS_WITH_FINDINGS at v1.1.2 (commit `3c92a67`); v1.1.3 is the MINOR
cleanup commit per verdict §5 carry-forward instructions.*
*Lifecycle: v1.0.0 → v1.1.0 (F-S-001 + F-S-002 fixes) → v1.1.1
(botanically incorrect Zucchini split) → v1.1.2 (team_00 botanical
correction: species/cultivar; AC-03 widened to 2 by-design pairs) →
v1.1.3 (R3 MINOR carry-forward cleanup, LOCKED).*
*L-GATE_S R3 verdict: PASS_WITH_FINDINGS (20/20 VCs PASS; 2 MINOR CARRY, addressed in v1.1.3 cleanup). Verdict: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`. Next: L-GATE_B mandate to sfa_build.*
