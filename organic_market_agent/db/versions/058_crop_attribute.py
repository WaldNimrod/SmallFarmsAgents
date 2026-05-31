"""058: SFA-S003-P004-WP-CB-MIG Phase 3 — crop_attribute table.

Adds the crop_attribute table (Canon §4 — uniform attributes layer for T2/T3
categorical and list attributes).

Revision ID: 058
Revises: 057
Create Date: 2026-05-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "058"
down_revision = "057"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use JSONB on PostgreSQL, JSON on other backends (e.g. SQLite in tests)
    bind = op.get_bind()
    dialect = bind.dialect.name if bind is not None else "postgresql"

    if dialect == "postgresql":
        jsonb_type = postgresql.JSONB(astext_type=sa.Text())
    else:
        jsonb_type = sa.JSON()

    op.create_table(
        "crop_attribute",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "variety_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            sa.ForeignKey("crop_varieties.id", name="fk_ca_variety_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("attribute_name", sa.VARCHAR(100), nullable=False),
        sa.Column("value_canonical", sa.Text(), nullable=True),
        sa.Column("value_list", jsonb_type, nullable=True),
        sa.Column("winning_source_class", sa.VARCHAR(20), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("candidates", jsonb_type, nullable=True),
        sa.Column(
            "computed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint(
            "variety_id", "attribute_name", name="uq_ca_variety_attribute"
        ),
    )
    op.create_index(
        "ix_crop_attribute_variety_id",
        "crop_attribute",
        ["variety_id"],
    )
    op.create_index(
        "ix_crop_attribute_attribute_name",
        "crop_attribute",
        ["attribute_name"],
    )


def downgrade() -> None:
    op.drop_index("ix_crop_attribute_attribute_name", table_name="crop_attribute")
    op.drop_index("ix_crop_attribute_variety_id", table_name="crop_attribute")
    op.drop_table("crop_attribute")
