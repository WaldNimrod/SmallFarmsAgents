"""046: M10.4 — scope-skip alternate Hebrew apostrophe for goji berry line."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "046"
down_revision = "045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(
        text(
            """
            INSERT INTO catalog_scope_skip_rules (
                display_order, category_code, match_type, pattern, notes,
                future_product_code, is_active
            ) VALUES (
                3402, 'grocery', 'contains', 'גוג׳י ברי', 'M10.4 goji alternate apostrophe (Hebrew ׳)',
                NULL, true
            )
            ON CONFLICT (display_order) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    op.get_bind().execute(
        text("DELETE FROM catalog_scope_skip_rules WHERE display_order = 3402")
    )
