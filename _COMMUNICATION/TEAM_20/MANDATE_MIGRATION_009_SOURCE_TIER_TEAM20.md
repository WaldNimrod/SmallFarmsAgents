---
document_type: MANDATE
version: "1.0"
template: _COMMUNICATION/TEMPLATES/MANDATE.md
---

# Mandate — Team 20: Migration 009 — source_tier + is_quarantined
**Mandate ID:** MANDATE-20260330-009-SOURCE-TIER
**From:** Team 100 (Architecture)
**To:** Team 20 (Infrastructure)
**Date:** 2026-03-30
**Priority:** HIGH
**Blocks:** M4 entry (Gate G4 QA cannot begin until this mandate is complete)

---

## Context

Architecture decision `ARCH-20260330-G3-DATA-QUALITY` and the specification
`docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` require two new columns and a data migration
to classify sources and quarantine M2-era noise rows.

This mandate implements **Phase 0** (source_tier) and **Phase 2** (is_quarantined) of that spec.

---

## Deliverables

1. **Alembic migration `009`** at:
   `organic_market_agent/db/versions/009_source_tier_and_quarantine.py`
   - `revision = "009"`, `down_revision = "008"`
   - Schema changes (see below)
   - Data migration (see below)

2. **Completion report** using the `COMPLETION_REPORT.md` template at:
   `_COMMUNICATION/TEAM_20/reports/2026-03-30_MIGRATION_009_COMPLETE_TEAM20.md`
   - Include Alembic output (`alembic upgrade head`)
   - Include before/after row counts (see verification queries below)
   - Must pass all acceptance criteria listed below

---

## Schema Changes

### 1. `sources` table — add `source_tier`

```sql
ALTER TABLE sources
  ADD COLUMN source_tier VARCHAR(20)
  CONSTRAINT chk_source_tier CHECK (source_tier IN ('price_grid', 'discovery', 'benchmark', 'basket'));
```

> Column is NOT NULL with a default of `'discovery'` to ensure existing rows don't violate constraint.
> The data migration below updates every row to its correct tier.

### 2. `raw_extracted_items` table — add `is_quarantined`

```sql
ALTER TABLE raw_extracted_items
  ADD COLUMN is_quarantined BOOLEAN NOT NULL DEFAULT false;
```

---

## Data Migration

### Step A — Classify all 20 sources

Set `source_tier` for every source. Reference: `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md`
"Classification of All 20 Sources" table.

```sql
-- price_grid sources (direct product + price listings)
UPDATE sources SET source_tier = 'price_grid'
WHERE code IN ('SRC002', 'SRC004', 'SRC005', 'SRC006', 'SRC008', 'SRC009', 'SRC010', 'SRC011');

-- basket sources (CSA/subscription, no per-unit prices)
UPDATE sources SET source_tier = 'basket'
WHERE code IN ('SRC003', 'SRC007');

-- discovery sources (portals / NGOs — no price data)
UPDATE sources SET source_tier = 'discovery'
WHERE code IN ('SRC001', 'SRC012', 'SRC013', 'SRC014');

-- benchmark sources (government + retail benchmarks + verification bodies)
UPDATE sources SET source_tier = 'benchmark'
WHERE code IN ('SRC015', 'SRC016', 'SRC017', 'SRC018', 'SRC019', 'SRC020');
```

After this block, run verification:
```sql
SELECT source_tier, COUNT(*) FROM sources GROUP BY source_tier;
```
Expected:
```
 price_grid | 8
 basket     | 2
 discovery  | 4
 benchmark  | 6
```
Any deviation must be reported and fixed before proceeding.

### Step B — Quarantine M2-era noise rows

Set `is_quarantined = true` for three categories of noise:

**Category 1 — Discovery-source extractions (portal page chrome)**
```sql
UPDATE raw_extracted_items rei
SET is_quarantined = true
FROM source_fetch_runs sfr
JOIN sources s ON sfr.source_id = s.id
WHERE rei.source_fetch_run_id = sfr.id
  AND s.source_tier = 'discovery';
```

**Category 2 — Basket-source extractions not from basket handler**
```sql
UPDATE raw_extracted_items rei
SET is_quarantined = true
FROM source_fetch_runs sfr
JOIN sources s ON sfr.source_id = s.id
WHERE rei.source_fetch_run_id = sfr.id
  AND s.source_tier = 'basket'
  AND rei.extraction_status = 'unresolvable';
```

**Category 3 — price_grid rows with null price text (pre-guard M2 selector mismatch)**
```sql
UPDATE raw_extracted_items rei
SET is_quarantined = true
FROM source_fetch_runs sfr
JOIN sources s ON sfr.source_id = s.id
WHERE rei.source_fetch_run_id = sfr.id
  AND s.source_tier = 'price_grid'
  AND rei.raw_price_text IS NULL
  AND rei.extraction_status = 'unresolvable';
```

After all three updates, record the total quarantined count:
```sql
SELECT COUNT(*) AS quarantined_total FROM raw_extracted_items WHERE is_quarantined = true;
```
Include this number in the completion report.

---

## Full Migration File

Create `organic_market_agent/db/versions/009_source_tier_and_quarantine.py` with this structure:

```python
"""Add source_tier to sources and is_quarantined to raw_extracted_items."""

import sqlalchemy as sa
from alembic import op

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Add source_tier column (nullable first, fill, then add constraint)
    op.add_column(
        "sources",
        sa.Column("source_tier", sa.String(20), nullable=True),
    )

    # 2. Classify all 20 sources
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'price_grid' "
        "WHERE code IN ('SRC002','SRC004','SRC005','SRC006','SRC008','SRC009','SRC010','SRC011')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'basket' WHERE code IN ('SRC003','SRC007')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'discovery' "
        "WHERE code IN ('SRC001','SRC012','SRC013','SRC014')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'benchmark' "
        "WHERE code IN ('SRC015','SRC016','SRC017','SRC018','SRC019','SRC020')"
    ))

    # 3. Tighten to NOT NULL + add CHECK constraint
    op.alter_column("sources", "source_tier", nullable=False)
    op.create_check_constraint(
        "chk_source_tier",
        "sources",
        "source_tier IN ('price_grid','discovery','benchmark','basket')",
    )

    # 4. Add is_quarantined column
    op.add_column(
        "raw_extracted_items",
        sa.Column("is_quarantined", sa.Boolean(), nullable=False, server_default="false"),
    )

    # 5. Quarantine Category 1: discovery-source extractions
    conn.execute(sa.text("""
        UPDATE raw_extracted_items rei
        SET is_quarantined = true
        FROM source_fetch_runs sfr
        JOIN sources s ON sfr.source_id = s.id
        WHERE rei.source_fetch_run_id = sfr.id
          AND s.source_tier = 'discovery'
    """))

    # 6. Quarantine Category 2: basket-source unresolvable items
    conn.execute(sa.text("""
        UPDATE raw_extracted_items rei
        SET is_quarantined = true
        FROM source_fetch_runs sfr
        JOIN sources s ON sfr.source_id = s.id
        WHERE rei.source_fetch_run_id = sfr.id
          AND s.source_tier = 'basket'
          AND rei.extraction_status = 'unresolvable'
    """))

    # 7. Quarantine Category 3: price_grid null-price pre-guard rows
    conn.execute(sa.text("""
        UPDATE raw_extracted_items rei
        SET is_quarantined = true
        FROM source_fetch_runs sfr
        JOIN sources s ON sfr.source_id = s.id
        WHERE rei.source_fetch_run_id = sfr.id
          AND s.source_tier = 'price_grid'
          AND rei.raw_price_text IS NULL
          AND rei.extraction_status = 'unresolvable'
    """))


def downgrade() -> None:
    op.drop_constraint("chk_source_tier", "sources", type_="check")
    op.drop_column("sources", "source_tier")
    op.drop_column("raw_extracted_items", "is_quarantined")
```

---

## Acceptance Criteria

All of the following must be satisfied and documented in the completion report:

| Check | Expected Result |
|-------|----------------|
| `alembic current` | shows `009 (head)` |
| `SELECT source_tier, COUNT(*) FROM sources GROUP BY source_tier` | `price_grid:8, basket:2, discovery:4, benchmark:6` |
| `SELECT COUNT(*) FROM sources WHERE source_tier IS NULL` | `0` |
| `SELECT COUNT(*) FROM raw_extracted_items WHERE is_quarantined = true` | Must be > 0 (expected ~1,500+) |
| `SELECT COUNT(*) FROM raw_extracted_items WHERE is_quarantined = false AND extraction_status = 'normalized'` | Must equal pre-migration normalized count |
| Schema check: `\d sources` shows `source_tier` column | Yes |
| Schema check: `\d raw_extracted_items` shows `is_quarantined` column | Yes |
| `python3.11 -m pytest tests/ -q` | All tests pass, 0 failures |

---

## What NOT to Do

- **Do NOT delete any rows.** Quarantine only.
- **Do NOT modify `extraction_status`** for quarantined rows. Leave as-is.
- **Do NOT add TTL or auto-delete logic.** That is Phase 1, out of scope for M3→M4 transition.
- **Do NOT change any parser or normalizer code.** That is Team 10's domain.

---

## Reference Documents

- `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` — phase spec and rationale
- `_COMMUNICATION/TEAM_100/reports/2026-03-30_ARCH_DECISION_G3_DATA_QUALITY_TEAM100.md` — gate decision
- `organic_market_agent/db/versions/008_fix_unresolvable_reason_text.py` — prior migration (down_revision)

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*Use template `_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md` for your completion report.*
