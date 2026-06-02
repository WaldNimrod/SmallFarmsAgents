"""055: M10.4 R2 — SRC060 typo alias (סמיט vs סמית) for Granny Smith apple."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "055"
down_revision = "054"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
            )
            SELECT p.id, :at,
              lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
              0.95, true, s.id
            FROM products p
            CROSS JOIN sources s
            WHERE p.code = 'PRD042' AND s.code = 'SRC060'
              AND NOT EXISTS (
                SELECT 1 FROM product_aliases pa
                WHERE pa.alias_text_normalized =
                  lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                  AND pa.source_id = s.id
              )
            """
        ),
        {"at": "תפוח עץ גרני סמיט", "at2": "תפוח עץ גרני סמיט", "at3": "תפוח עץ גרני סמיט"},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            DELETE FROM product_aliases pa
            USING sources s
            WHERE pa.source_id = s.id AND s.code = 'SRC060'
              AND pa.alias_text = 'תפוח עץ גרני סמיט'
            """
        )
    )
