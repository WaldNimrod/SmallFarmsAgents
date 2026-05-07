"""037: ספר גידולים — crop_varieties table (variety-level agronomic parameters)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_varieties",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("crop_id", sa.BigInteger(), nullable=False),
        sa.Column("name_en", sa.VARCHAR(200), nullable=True),
        sa.Column("name_he", sa.VARCHAR(200), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_grafted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("rootstock_variety", sa.VARCHAR(200), nullable=True),
        sa.Column("planting_method", sa.VARCHAR(30), nullable=True),
        sa.Column("days_to_maturity", sa.Integer(), nullable=True),
        sa.Column("harvest_window_min_days", sa.Integer(), nullable=True),
        sa.Column("harvest_window_max_days", sa.Integer(), nullable=True),
        sa.Column("in_row_spacing_cm", sa.Numeric(6, 2), nullable=True),
        sa.Column("rows_per_bed", sa.Integer(), nullable=True),
        sa.Column("planting_season", sa.VARCHAR(100), nullable=True),
        sa.Column("succession_interval_weeks", sa.Integer(), nullable=True),
        sa.Column("harvest_unit", sa.VARCHAR(20), nullable=True),
        sa.Column("avg_yield_per_bed_m", sa.Numeric(10, 4), nullable=True),
        sa.Column("yield_source", sa.VARCHAR(200), nullable=True),
        sa.Column("documented_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("documented_price_unit", sa.VARCHAR(50), nullable=True),
        sa.Column("documented_price_source", sa.VARCHAR(200), nullable=True),
        sa.Column("pricebook_product_id", sa.VARCHAR(100), nullable=True),
        sa.Column("avg_revenue_per_bed_m", sa.Numeric(10, 2), nullable=True),
        sa.Column("days_to_germinate_gh", sa.Integer(), nullable=True),
        sa.Column("days_in_gh_total", sa.Integer(), nullable=True),
        sa.Column("seeder", sa.VARCHAR(100), nullable=True),
        sa.Column("seeder_front_gear", sa.VARCHAR(20), nullable=True),
        sa.Column("seeder_rear_gear", sa.VARCHAR(20), nullable=True),
        sa.Column("seeder_roller_plate", sa.VARCHAR(20), nullable=True),
        sa.Column("harvest_stage", sa.VARCHAR(30), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "planting_method IS NULL OR planting_method IN ('direct_sow','transplant','greenhouse_transplant','cutting','purchase')",
            name="chk_cv_planting_method",
        ),
        sa.CheckConstraint(
            "harvest_stage IS NULL OR harvest_stage IN ('full_size','baby_leaf','head','plant_sale','seed')",
            name="chk_cv_harvest_stage",
        ),
        sa.CheckConstraint(
            "harvest_unit IS NULL OR harvest_unit IN ('kg','bunch','head','case','unit','seedling')",
            name="chk_cv_harvest_unit",
        ),
        sa.ForeignKeyConstraint(["crop_id"], ["crops.id"], name="fk_cv_crop_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("crop_id", "name_en", name="uq_cv_crop_name_en"),
    )
    op.create_index("ix_cv_crop_id", "crop_varieties", ["crop_id"])
    op.create_index("ix_cv_crop_id_is_default", "crop_varieties", ["crop_id", "is_default"])


def downgrade() -> None:
    op.drop_index("ix_cv_crop_id_is_default", table_name="crop_varieties")
    op.drop_index("ix_cv_crop_id", table_name="crop_varieties")
    op.drop_table("crop_varieties")
