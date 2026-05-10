"""038: ספר גידולים — crop_variety_source_values table (per-source raw measurements).

field_name stores English DB column names only (e.g. 'days_to_maturity').
Unique constraint on (variety_id, field_name, source) enables idempotent upserts.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "038"
down_revision = "037"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_variety_source_values",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("variety_id", sa.BigInteger(), nullable=False),
        sa.Column("field_name", sa.VARCHAR(100), nullable=False),
        sa.Column("source", sa.VARCHAR(100), nullable=False),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_numeric", sa.Numeric(14, 6), nullable=True),
        sa.Column("unit", sa.VARCHAR(50), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["variety_id"], ["crop_varieties.id"], name="fk_cvsv_variety_id", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("variety_id", "field_name", "source", name="uq_cvsv_variety_field_source"),
    )
    op.create_index("ix_cvsv_variety_id", "crop_variety_source_values", ["variety_id"])
    op.create_index("ix_cvsv_variety_field", "crop_variety_source_values", ["variety_id", "field_name"])


def downgrade() -> None:
    op.drop_index("ix_cvsv_variety_field", table_name="crop_variety_source_values")
    op.drop_index("ix_cvsv_variety_id", table_name="crop_variety_source_values")
    op.drop_table("crop_variety_source_values")
