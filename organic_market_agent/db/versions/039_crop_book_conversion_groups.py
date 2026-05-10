"""039: ספר גידולים — crop_conversion_groups table + deferred FK on crops.

Also adds the previously-deferred FK from crops.conversion_group_id → crop_conversion_groups.id.
This ordering avoids a circular dependency: crops (036) references this table (039).
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "039"
down_revision = "038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_conversion_groups",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_ccg_name"),
    )

    op.create_foreign_key(
        "fk_crops_conversion_group_id",
        "crops",
        "crop_conversion_groups",
        ["conversion_group_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_crops_conversion_group_id", "crops", type_="foreignkey")
    op.drop_table("crop_conversion_groups")
