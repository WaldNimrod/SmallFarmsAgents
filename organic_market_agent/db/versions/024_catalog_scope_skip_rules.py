"""024: catalog_scope_skip_rules + raw_extracted_items.ignore_reason_code."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "024"
down_revision = "023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "catalog_scope_skip_rules",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("category_code", sa.String(length=30), nullable=False),
        sa.Column("match_type", sa.String(length=20), nullable=False),
        sa.Column("pattern", sa.String(length=500), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("future_product_code", sa.String(length=32), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
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
        sa.CheckConstraint(
            "category_code IN ('donation','cleaning','dry_grocery','other')",
            name="chk_cssr_category",
        ),
        sa.CheckConstraint(
            "match_type IN ('exact','prefix','contains','regex')",
            name="chk_cssr_match_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("display_order", name="uq_catalog_scope_skip_rules_display_order"),
    )
    op.create_index("ix_catalog_scope_skip_rules_active", "catalog_scope_skip_rules", ["is_active"])

    op.add_column(
        "raw_extracted_items",
        sa.Column("ignore_reason_code", sa.String(length=80), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("raw_extracted_items", "ignore_reason_code")
    op.drop_index("ix_catalog_scope_skip_rules_active", table_name="catalog_scope_skip_rules")
    op.drop_table("catalog_scope_skip_rules")
