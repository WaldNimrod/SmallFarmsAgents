"""071: Resolve SRC061 residual unresolvable lines — baby leaf mix + sprout blend strings."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "071"
down_revision = "070"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# (product_code, alias_text, confidence)
_ROWS: list[tuple[str, str, str]] = [
    ("PRD008", "מיקס בייבי", "0.9"),
    ("PRD033", "נבטים , תערובת", "0.95"),
]


def _insert_alias(conn, pcode: str, alias_text: str, conf: str) -> None:
    n = _norm(alias_text)
    conn.execute(
        text(
            """
            INSERT INTO product_aliases (
                product_id, alias_text, alias_text_normalized,
                source_id, confidence, is_active
            )
            SELECT id, :alias_text, :alias_norm, NULL,
                   CAST(:conf AS NUMERIC(3,2)), true
            FROM products WHERE code = :pcode
            ON CONFLICT (alias_text_normalized, source_id)
            DO NOTHING
            """
        ),
        {"alias_text": alias_text, "alias_norm": n, "conf": conf, "pcode": pcode},
    )


def upgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, conf in _ROWS:
        _insert_alias(conn, pcode, alias_text, conf)


def downgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, _conf in reversed(_ROWS):
        n = _norm(alias_text)
        conn.execute(
            text(
                """
                DELETE FROM product_aliases pa
                USING products p
                WHERE pa.product_id = p.id AND p.code = :pcode
                  AND pa.alias_text_normalized = :n AND pa.source_id IS NULL
                """
            ),
            {"pcode": pcode, "n": n},
        )
