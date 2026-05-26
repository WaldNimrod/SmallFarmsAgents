"""049: Crop planting calendar (WP-C1) — Israeli monthly planting matrix.

Sources: GROWORGANIC.INFO (L01), BUSTAN (L36), and future per-region overlays.
Stores boolean month-columns + activity_type per (crop, source).

Revision ID: 049
Revises: 048
Create Date: 2026-05-27

SFA-S003-P002-WP-C1 LOD400 §3.1 (revision renumbered 049 per team_00 — 047/048 taken).
"""

from alembic import op
import sqlalchemy as sa

revision = "049"
down_revision = "048"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_planting_calendar",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("region", sa.String(40), nullable=True),
        sa.Column("activity_type", sa.String(20), nullable=False),
        sa.Column("season", sa.String(20), nullable=True),
        sa.Column("month_jan", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_feb", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_mar", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_apr", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_may", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_jun", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_jul", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_aug", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_sep", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_oct", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_nov", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("month_dec", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "activity_type IN ('seed','transplant','both')",
            name="ck_cpc_activity_type",
        ),
        sa.CheckConstraint(
            "season IS NULL OR season IN ('spring','summer','fall','winter','all')",
            name="ck_cpc_season",
        ),
        sa.UniqueConstraint("crop_id", "source", "activity_type",
                            name="uq_cpc_crop_source_activity"),
    )
    op.create_index("idx_cpc_crop", "crop_planting_calendar", ["crop_id"])
    op.create_index("idx_cpc_source", "crop_planting_calendar", ["source"])


def downgrade() -> None:
    op.drop_index("idx_cpc_source", "crop_planting_calendar")
    op.drop_index("idx_cpc_crop", "crop_planting_calendar")
    op.drop_table("crop_planting_calendar")
