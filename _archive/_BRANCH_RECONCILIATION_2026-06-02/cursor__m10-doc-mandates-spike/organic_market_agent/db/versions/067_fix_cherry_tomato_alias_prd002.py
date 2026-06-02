"""067: Cherry-tomato phrase must map to PRD002, not PRD001.

Removes wrong global alias from migration 023: \"עגבניות שרי אורגניות\" was tied to
regular tomato (PRD001). Re-inserts it for עגבנייה שרי (PRD002).
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "067"
down_revision = "066"
branch_labels = None
depends_on = None

_ALIAS_TEXT = "עגבניות שרי אורגניות"
_CONF = "0.95"


def _norm(s: str) -> str:
    return s.strip().lower()


def upgrade() -> None:
    conn = op.get_bind()
    n = _norm(_ALIAS_TEXT)
    conn.execute(
        text(
            """
            DELETE FROM product_aliases pa
            USING products p
            WHERE pa.product_id = p.id
              AND p.code = 'PRD001'
              AND pa.source_id IS NULL
              AND pa.alias_text_normalized = :n
            """
        ),
        {"n": n},
    )
    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized,
                source_id, confidence, is_active
            )
            SELECT id, :alias_text, :alias_norm, NULL,
                   CAST(:conf AS NUMERIC(3,2)), true
            FROM products WHERE code = 'PRD002'
            ON CONFLICT (alias_text_normalized, source_id)
            DO NOTHING
            """
        ),
        {"alias_text": _ALIAS_TEXT, "alias_norm": n, "conf": _CONF},
    )


def downgrade() -> None:
    conn = op.get_bind()
    n = _norm(_ALIAS_TEXT)
    conn.execute(
        text(
            """
            DELETE FROM product_aliases pa
            USING products p
            WHERE pa.product_id = p.id
              AND p.code = 'PRD002'
              AND pa.source_id IS NULL
              AND pa.alias_text_normalized = :n
            """
        ),
        {"n": n},
    )
    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized,
                source_id, confidence, is_active
            )
            SELECT id, :alias_text, :alias_norm, NULL,
                   CAST(:conf AS NUMERIC(3,2)), true
            FROM products WHERE code = 'PRD001'
            ON CONFLICT (alias_text_normalized, source_id)
            DO NOTHING
            """
        ),
        {"alias_text": _ALIAS_TEXT, "alias_norm": n, "conf": _CONF},
    )
