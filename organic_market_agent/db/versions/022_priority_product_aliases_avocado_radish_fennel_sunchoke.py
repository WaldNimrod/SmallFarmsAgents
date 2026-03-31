"""022: Global aliases for manager priority products (Nimrod 2026-03-31).

- PRD016 צנון: add צנונית / English radish variants (vegetable; not sprouts).
- PRD048 שומר, PRD057 ארטישוק ירושלמי, PRD059 אבוקדו: extra Hebrew + English.
- PRD035 ארטישוק: globe-artichoke English disambiguation vs Jerusalem type.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "022"
down_revision = "021"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# (product_code, alias_text, confidence)
ALIAS_ROWS: list[tuple[str, str, str]] = [
    # PRD016 — radish (צנון); צנונית is the common retail name for small pink radishes
    ("PRD016", "צנונית", "1.0"),
    ("PRD016", "צנונית אורגנית", "1.0"),
    ("PRD016", "צנוניות", "0.95"),
    ("PRD016", "צנוניות אורגניות", "0.95"),
    ("PRD016", "radishes", "0.9"),
    ("PRD016", "small radish", "0.9"),
    ("PRD016", "red radish", "0.9"),
    ("PRD016", "table radish", "0.85"),
    # PRD048 — fennel
    ("PRD048", "שומר צרור", "1.0"),
    ("PRD048", "שומר צרור אורגני", "1.0"),
    ("PRD048", "fennel", "0.95"),
    ("PRD048", "fennel bulb", "0.9"),
    ("PRD048", "sweet fennel", "0.85"),
    # PRD057 — Jerusalem artichoke / sunchoke
    ("PRD057", "sunchoke", "0.95"),
    ("PRD057", "sunchokes", "0.9"),
    ("PRD057", "topinambur", "0.9"),
    ("PRD057", "Jerusalem artichoke", "0.95"),
    ("PRD057", "jerusalem artichokes", "0.9"),
    ("PRD057", "גירסול", "0.9"),
    ("PRD057", "גירסול אורגני", "0.9"),
    # PRD059 — avocado
    ("PRD059", "avocado", "0.95"),
    ("PRD059", "avocados", "0.9"),
    ("PRD059", "hass avocado", "0.9"),
    ("PRD059", "avocado hass", "0.9"),
    ("PRD059", "אבוקדו האס", "0.95"),
    ("PRD059", "אבוקדו האס אורגני", "0.9"),
    # PRD035 — globe artichoke (distinct from PRD057)
    ("PRD035", "globe artichoke", "0.95"),
    ("PRD035", "artichoke globe", "0.9"),
    ("PRD035", "cynara", "0.75"),
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
