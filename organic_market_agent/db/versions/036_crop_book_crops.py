"""036: ספר גידולים — crops table (core crop entities).

Note: conversion_group_id FK to crop_conversion_groups is added in migration 039
after that table exists. The column is created nullable here without a FK constraint.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crops",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name_he", sa.VARCHAR(200), nullable=False),
        sa.Column("name_en", sa.VARCHAR(200), nullable=True),
        sa.Column("scientific_name", sa.VARCHAR(200), nullable=True),
        sa.Column("family_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.VARCHAR(50), nullable=False),
        sa.Column("growth_cycle", sa.VARCHAR(30), nullable=True),
        sa.Column("harvest_unit_default", sa.VARCHAR(20), nullable=True),
        sa.Column("first_fruit_year", sa.Integer(), nullable=True),
        sa.Column("conversion_group_id", sa.BigInteger(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("oma_product_id", sa.VARCHAR(20), nullable=True),
        sa.CheckConstraint(
            "category IN ('vegetables','herbs','baby','legumes','fruits','fruit_trees','grains','cover_crops')",
            name="chk_crops_category",
        ),
        sa.CheckConstraint(
            "growth_cycle IS NULL OR growth_cycle IN ('annual','biennial','perennial')",
            name="chk_crops_growth_cycle",
        ),
        sa.CheckConstraint(
            "harvest_unit_default IS NULL OR harvest_unit_default IN ('kg','bunch','head','case','unit','seedling')",
            name="chk_crops_harvest_unit_default",
        ),
        sa.ForeignKeyConstraint(["family_id"], ["crop_families.id"], name="fk_crops_family_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name_he", name="uq_crops_name_he"),
    )
    op.create_index("ix_crops_family_id", "crops", ["family_id"])
    op.create_index("ix_crops_category", "crops", ["category"])


def downgrade() -> None:
    op.drop_index("ix_crops_category", table_name="crops")
    op.drop_index("ix_crops_family_id", table_name="crops")
    op.drop_table("crops")
