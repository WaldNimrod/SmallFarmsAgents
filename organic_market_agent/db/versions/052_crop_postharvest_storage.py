"""052: Postharvest storage conditions (WP-C4 / CW-08 — UC Davis Cantwell).

Revision ID: 052
Revises: 051
Create Date: 2026-05-27

SFA-S003-P002-WP-C4 LOD400 §3.3.
"""

from alembic import op
import sqlalchemy as sa

revision = "052"
down_revision = "051"
branch_labels = None
depends_on = None


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
        sa.Column("ethylene_production", sa.String(20), nullable=True),
        sa.Column("ethylene_sensitivity", sa.String(20), nullable=True),
        sa.Column("storage_life_days_min", sa.Integer, nullable=True),
        sa.Column("storage_life_days_max", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("crop_id", "source", name="uq_cps_crop_source"),
    )
    op.create_index("idx_cps_crop", "crop_postharvest_storage", ["crop_id"])


def downgrade() -> None:
    op.drop_index("idx_cps_crop", "crop_postharvest_storage")
    op.drop_table("crop_postharvest_storage")
