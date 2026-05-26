"""050: Cover crops chart (WP-C1) — JMF L12 + future cover crop sources.

Standalone table; cover crops are NOT in the `crops` table.

Revision ID: 050
Revises: 049
Create Date: 2026-05-27

SFA-S003-P002-WP-C1 LOD400 §3.2 (revision renumbered 050 per team_00).
"""

from alembic import op
import sqlalchemy as sa

revision = "050"
down_revision = "049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_cover_crops",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("name_en", sa.String(60), nullable=False),
        sa.Column("name_he", sa.String(60), nullable=True),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("total_days_garden", sa.Integer, nullable=True),
        sa.Column("germination_temp_c_min", sa.Numeric(4, 1), nullable=True),
        sa.Column("hardiness_zone", sa.Integer, nullable=True),
        sa.Column("sow_window", sa.Text, nullable=True),
        sa.Column("inoculum", sa.String(80), nullable=True),
        sa.Column("survives_winter", sa.Boolean, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "category IN ('legume','cereal','brassica','other')",
            name="ck_ccc_category",
        ),
        sa.UniqueConstraint("name_en", "source", name="uq_ccc_name_source"),
    )
    op.create_index("idx_ccc_category", "crop_cover_crops", ["category"])


def downgrade() -> None:
    op.drop_index("idx_ccc_category", "crop_cover_crops")
    op.drop_table("crop_cover_crops")
