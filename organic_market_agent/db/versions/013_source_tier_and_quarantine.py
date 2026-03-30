"""013: Add source_tier to sources and is_quarantined to raw_extracted_items.

Implements Phase 0 (source classification) and Phase 2 (noise quarantine) of
docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md, as specified in
MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md (renumbered from 009 to fit chain).

source_tier values:
  price_grid  — direct product + price listings (parseable, normalizable)
  basket      — CSA/subscription boxes (basket handler, no per-unit prices)
  discovery   — portals/NGOs that have no price data (deactivated)
  benchmark   — government/retail benchmarks and verification bodies

is_quarantined = true marks rows that should be permanently skipped by the
normalizer engine. Three noise categories are quarantined:
  1. All extractions from discovery-tier sources (portal page chrome)
  2. Unresolvable items from basket-tier sources (pre-basket-handler era)
  3. price_grid rows with null raw_price_text (pre-guard M2 selector mismatch)
"""

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Add source_tier (nullable first so existing rows don't immediately fail)
    op.add_column(
        "sources",
        sa.Column("source_tier", sa.String(20), nullable=True),
    )

    # 2. Seed tier for all 20 sources
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'price_grid' "
        "WHERE code IN ('SRC002','SRC004','SRC005','SRC006',"
        "               'SRC008','SRC009','SRC010','SRC011')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'basket' "
        "WHERE code IN ('SRC003','SRC007')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'discovery' "
        "WHERE code IN ('SRC001','SRC012','SRC013','SRC014')"
    ))
    conn.execute(sa.text(
        "UPDATE sources SET source_tier = 'benchmark' "
        "WHERE code IN ('SRC015','SRC016','SRC017','SRC018','SRC019','SRC020')"
    ))

    # 3. Tighten to NOT NULL + CHECK constraint
    op.alter_column("sources", "source_tier", nullable=False)
    op.create_check_constraint(
        "chk_source_tier",
        "sources",
        "source_tier IN ('price_grid','discovery','benchmark','basket')",
    )

    # 4. Add is_quarantined to raw_extracted_items
    op.add_column(
        "raw_extracted_items",
        sa.Column(
            "is_quarantined",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    # 5. Quarantine Category 1: all items from discovery-tier sources
    conn.execute(sa.text("""
        UPDATE raw_extracted_items rei
        SET is_quarantined = true
        FROM source_fetch_runs sfr
        JOIN sources s ON sfr.source_id = s.id
        WHERE rei.source_fetch_run_id = sfr.id
          AND s.source_tier = 'discovery'
    """))

    # 6. Quarantine Category 2: unresolvable items from basket-tier sources
    conn.execute(sa.text("""
        UPDATE raw_extracted_items rei
        SET is_quarantined = true
        FROM source_fetch_runs sfr
        JOIN sources s ON sfr.source_id = s.id
        WHERE rei.source_fetch_run_id = sfr.id
          AND s.source_tier = 'basket'
          AND rei.extraction_status = 'unresolvable'
    """))

    # 7. Quarantine Category 3: price_grid rows with null price text (pre-guard)
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
    op.drop_column("raw_extracted_items", "is_quarantined")
    op.drop_constraint("chk_source_tier", "sources", type_="check")
    op.drop_column("sources", "source_tier")
