"""039: M10.3 — SRC025 residual unresolvable (galangal skip, chili alias)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "039"
down_revision = "038"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO catalog_scope_skip_rules (
                display_order, category_code, match_type, pattern, notes,
                future_product_code, is_active
            ) VALUES (
                3346, 'other', 'contains', 'זנגוויל', 'M10.3 SRC025 galangal root retail',
                NULL, true
            )
            ON CONFLICT (display_order) DO NOTHING
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
            )
            SELECT p.id, :at,
              lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
              0.95, true, NULL
            FROM products p WHERE p.code = 'PRD032'
              AND NOT EXISTS (
                SELECT 1 FROM product_aliases pa
                WHERE pa.alias_text_normalized =
                  lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                  AND pa.source_id IS NULL
              )
            """
        ),
        {
            "at": "פלפל צ'ילי חריף אורגני ( ארוז יח')",
            "at2": "פלפל צ'ילי חריף אורגני ( ארוז יח')",
            "at3": "פלפל צ'ילי חריף אורגני ( ארוז יח')",
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM catalog_scope_skip_rules WHERE display_order = 3346")
    )
    conn.execute(
        text(
            """
            DELETE FROM product_aliases
            WHERE alias_text = :t AND source_id IS NULL
            """
        ),
        {"t": "פלפל צ'ילי חריף אורגני ( ארוז יח')"},
    )
