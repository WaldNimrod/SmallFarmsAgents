"""034: Add display_bucket column to sources table.

Supports the public filter bar (grower / store / chain) added in WP002.
CHECK constraint mirrors Source.display_bucket model mapping.
Existing rows default to 'store' (safe, widest category).

down_revision: 033 (src_wa_pending_manual)
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column(
            "display_bucket",
            sa.VARCHAR(20),
            nullable=True,  # nullable during backfill
        ),
    )

    # Backfill existing rows
    op.execute(
        sa.text("UPDATE sources SET display_bucket = 'store' WHERE display_bucket IS NULL")
    )

    # Apply NOT NULL constraint after backfill
    op.alter_column("sources", "display_bucket", nullable=False)

    # Apply CHECK constraint
    op.create_check_constraint(
        "chk_src_display_bucket",
        "sources",
        "display_bucket IN ('grower','store','chain','discovery','benchmark','verification')",
    )


def downgrade() -> None:
    op.drop_constraint("chk_src_display_bucket", "sources", type_="check")
    op.drop_column("sources", "display_bucket")
