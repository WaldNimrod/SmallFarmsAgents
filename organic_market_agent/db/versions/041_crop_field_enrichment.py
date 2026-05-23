"""041: ספר גידולים — crop_field_enrichment table (per-field consensus rows).

New table, no GCR required (additive).  Built under SFA-S003-P002-WP-A LOD400 §17 Step 4.
Each row stores the reconciled consensus for a (variety_id, field_name) pair:
  value_min / value_max / value_best  — numeric range + best estimate
  confidence_score                    — 0.0000–1.0000 blended confidence
  source_count                        — number of non-outlier, non-moderation-excluded sources
  winning_source_class                — class code of the highest-trust source that contributed
  computed_at                         — UTC timestamp of last enrichment_runner run
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "041"
down_revision = "040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_field_enrichment",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("variety_id", sa.BigInteger(), nullable=False),
        sa.Column("field_name", sa.VARCHAR(100), nullable=False),
        sa.Column("value_min", sa.Numeric(14, 6), nullable=True),
        sa.Column("value_max", sa.Numeric(14, 6), nullable=True),
        sa.Column("value_best", sa.Numeric(14, 6), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("winning_source_class", sa.VARCHAR(20), nullable=True),
        sa.Column(
            "computed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.ForeignKeyConstraint(
            ["variety_id"],
            ["crop_varieties.id"],
            name="fk_cfe_variety_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("variety_id", "field_name", name="uq_cfe_variety_field"),
    )
    op.create_index("ix_cfe_variety_id", "crop_field_enrichment", ["variety_id"])
    op.create_index("ix_cfe_field_name", "crop_field_enrichment", ["field_name"])


def downgrade() -> None:
    op.drop_index("ix_cfe_field_name", table_name="crop_field_enrichment")
    op.drop_index("ix_cfe_variety_id", table_name="crop_field_enrichment")
    op.drop_table("crop_field_enrichment")
