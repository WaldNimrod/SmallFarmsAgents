"""042: ספר גידולים — crop_variety_source_values enrichment columns (GCR_1).

Additive columns on existing table, authorized by:
  _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md (Decision A-3 GCR_1)

Columns added:
  trust_tier         VARCHAR(20)   — source class code (EX/NI/PR/OP/MK/WB/UC) denormalized
  confidence_weight  NUMERIC(5,4)  — blending weight; NULL = hard-override or unmoderated UC
  is_outlier_rejected BOOLEAN      — True = excluded from weighted-mean by statistical outlier gate
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
            server_default="false",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("crop_variety_source_values", "is_outlier_rejected")
    op.drop_column("crop_variety_source_values", "confidence_weight")
    op.drop_column("crop_variety_source_values", "trust_tier")
