"""040: ספר גידולים — crop_unit_conversions table.

Each row converts a source_unit → gram (pivot) for a conversion group OR
a specific crop. Exactly one of (conversion_group_id, crop_id) must be non-null.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "040"
down_revision = "039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_unit_conversions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("conversion_group_id", sa.BigInteger(), nullable=True),
        sa.Column("crop_id", sa.BigInteger(), nullable=True),
        sa.Column("source_unit", sa.VARCHAR(50), nullable=False),
        sa.Column("target_unit", sa.VARCHAR(50), nullable=False),
        sa.Column("conversion_factor", sa.Numeric(10, 4), nullable=False),
        sa.Column("context", sa.VARCHAR(50), nullable=True),
        sa.Column("source", sa.VARCHAR(100), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "(conversion_group_id IS NOT NULL AND crop_id IS NULL) OR "
            "(conversion_group_id IS NULL AND crop_id IS NOT NULL)",
            name="chk_cuc_exclusion",
        ),
        sa.ForeignKeyConstraint(
            ["conversion_group_id"],
            ["crop_conversion_groups.id"],
            name="fk_cuc_conversion_group_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["crop_id"], ["crops.id"], name="fk_cuc_crop_id", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cuc_conversion_group_id", "crop_unit_conversions", ["conversion_group_id"]
    )
    op.create_index("ix_cuc_crop_id", "crop_unit_conversions", ["crop_id"])


def downgrade() -> None:
    op.drop_index("ix_cuc_crop_id", table_name="crop_unit_conversions")
    op.drop_index("ix_cuc_conversion_group_id", table_name="crop_unit_conversions")
    op.drop_table("crop_unit_conversions")
