"""023: Global product_aliases batch for normalizer hit-rate (plan B).

Common Hebrew retail / CSA strings → existing catalog codes. ON CONFLICT DO NOTHING.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# (product_code, alias_text, confidence)
ALIAS_ROWS: list[tuple[str, str, str]] = [
    ("PRD001", "עגבניות שרי אורגניות", "0.95"),
    ("PRD001", "עגבניה בשלה אורגנית", "0.9"),
    ("PRD005", "מלפפון בייבי אורגני", "0.9"),
    ("PRD005", "מלפפונים אורגניים", "0.9"),
    ("PRD008", "חסה ערבית אורגנית", "0.9"),
    ("PRD008", "חסה לאליק אורגנית", "0.9"),
    ("PRD013", "גזר אורגני", "0.95"),
    ("PRD013", "גזר שורש אורגני", "0.9"),
    ("PRD006", "חציל בלדי אורגני", "0.9"),
    ("PRD007", "קישואים אורגניים", "0.95"),
    ("PRD011", "כוסברה אורגנית", "0.95"),
    ("PRD010", "רוקט אורגני", "0.95"),
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
    for pcode, alias_text, conf in ALIAS_ROWS:
        _insert_alias(conn, pcode, alias_text, conf)


def downgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, _conf in reversed(ALIAS_ROWS):
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
