"""035: ספר גידולים — crop_families table (botanical families)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_families",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("scientific_name", sa.VARCHAR(200), nullable=False),
        sa.Column("name_he", sa.VARCHAR(200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scientific_name", name="uq_crop_families_scientific_name"),
    )
    op.create_index("ix_crop_families_scientific_name", "crop_families", ["scientific_name"])


def downgrade() -> None:
    op.drop_index("ix_crop_families_scientific_name", table_name="crop_families")
    op.drop_table("crop_families")
