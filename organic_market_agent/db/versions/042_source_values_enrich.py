"""042: ספר גידולים — crop_variety_source_values enrichment columns (GCR_1).

Additive columns on existing table, authorized by:
  _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md (Decision A-3 GCR_1)

Columns added:
  trust_tier         VARCHAR(20)   — source class code (EX/NI/PR/OP/MK/WB/UC) denormalized
  confidence_weight  NUMERIC(5,4)  — blending weight; NULL = hard-override or unmoderated UC
  is_outlier_rejected BOOLEAN      — True = excluded from weighted-mean by statistical outlier gate

Backfill (LOD400 AC-15):
  trust_tier backfilled from existing source labels.
  confidence_weight backfilled from class defaults.
  is_outlier_rejected backfilled from existing note field ('OUTLIER_REJECTED' marker).
  Backfill is skipped on SQLite (test dialect — no LIKE operator needed).
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "042"
down_revision = "041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "crop_variety_source_values",
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=True),
    )
    op.add_column(
        "crop_variety_source_values",
        sa.Column("confidence_weight", sa.Numeric(5, 4), nullable=True),
    )
    op.add_column(
        "crop_variety_source_values",
        sa.Column(
            "is_outlier_rejected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    # Backfill trust_tier + confidence_weight + is_outlier_rejected from existing data.
    # Skipped on SQLite — backfill only needed on production PostgreSQL.
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.execute("""
            UPDATE crop_variety_source_values SET trust_tier = CASE
                WHEN source = 'team_00'    THEN 'EX'
                WHEN source LIKE 'NI%'     THEN 'NI'
                WHEN source = 'JMF'        THEN 'PR'
                WHEN source LIKE 'Tend%'   THEN 'OP'
                WHEN source LIKE 'OMA%'    THEN 'MK'
                WHEN source LIKE 'WB%'     THEN 'WB'
                WHEN source LIKE 'UC%'     THEN 'UC'
                ELSE 'PR'
            END
        """)

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

        op.execute("""
            UPDATE crop_variety_source_values
            SET is_outlier_rejected = TRUE
            WHERE note LIKE '%OUTLIER_REJECTED%'
        """)


def downgrade() -> None:
    op.drop_column("crop_variety_source_values", "is_outlier_rejected")
    op.drop_column("crop_variety_source_values", "confidence_weight")
    op.drop_column("crop_variety_source_values", "trust_tier")
