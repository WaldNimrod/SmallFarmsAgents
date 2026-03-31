"""029: Admin queues — product catalog suggestions + pending product aliases (Nimrod UX)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "029"
down_revision = "028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_catalog_suggestions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canonical_name_he", sa.String(length=200), nullable=False),
        sa.Column("proposed_code", sa.String(length=32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="chk_pcs_status",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_catalog_suggestions_status", "product_catalog_suggestions", ["status"])

    op.create_table(
        "pending_product_aliases",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("alias_text", sa.String(length=200), nullable=False),
        sa.Column("alias_text_normalized", sa.String(length=200), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="chk_ppa_status",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pending_product_aliases_status", "pending_product_aliases", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pending_product_aliases_status", table_name="pending_product_aliases")
    op.drop_table("pending_product_aliases")
    op.drop_index("ix_product_catalog_suggestions_status", table_name="product_catalog_suggestions")
    op.drop_table("product_catalog_suggestions")
