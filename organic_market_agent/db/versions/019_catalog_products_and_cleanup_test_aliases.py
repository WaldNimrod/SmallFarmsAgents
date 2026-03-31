"""019: Remove M5 test alias litter; add PRD030–PRD032 + global aliases.

- DELETE product_aliases left by admin tests (m5-test-alias-*, m5-disable-*).
- INSERT products: PRD030 חסה זן מובחר, PRD031 פלפל סוויט בייט, PRD032 פלפל חריף.
- Seed product_aliases for cultivar / sweet bite / hot pepper strings.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


ALIASES = [
    # PRD030 — named lettuce cultivars (not generic חסה)
    ("PRD030", "חסה אייסברג", "1.0"),
    ("PRD030", "חסה חמאה", "1.0"),
    ("PRD030", "חסה לאליק", "1.0"),
    ("PRD030", "חסה סלאנובה", "1.0"),
    # PRD031 — sweet bite (not PRD003 red pepper)
    ("PRD031", "פלפל אדום בייבי", "1.0"),
    ("PRD031", "פלפל סוויט בייט", "1.0"),
    ("PRD031", "sweet bite", "0.9"),
    ("PRD031", "sweetbite", "0.85"),
    # PRD032 — hot pepper (not PRD004 sweet green)
    ("PRD032", "פלפל חריף ירוק", "1.0"),
    ("PRD032", "פלפל חריף", "1.0"),
    ("PRD032", "פלפל חריף אדום", "0.95"),
]


def upgrade() -> None:
    conn = op.get_bind()

    conn.execute(
        text(
            """
            DELETE FROM product_aliases
            WHERE alias_text_normalized LIKE 'm5-test-alias-%'
               OR alias_text LIKE 'm5-test-alias-%'
               OR alias_text_normalized LIKE 'm5-disable-%'
               OR alias_text LIKE 'm5-disable-%'
            """
        )
    )

    new_products = [
        ("PRD030", "חסה זן מובחר", "unit", "leafy_greens", "חורף-אביב", 30),
        ("PRD031", "פלפל סוויט בייט", "kg", "fruiting_vegetables", "אביב-סתיו", 31),
        ("PRD032", "פלפל חריף", "kg", "fruiting_vegetables", "אביב-סתיו", 32),
    ]
    for code, name_he, unit_code, category, season, disp in new_products:
        conn.execute(
            text(
                """
                INSERT INTO products (
                    code, canonical_name_he, category, default_measurement_unit_id,
                    is_organic_required, is_basket_product, seasonality_notes, display_order
                )
                SELECT
                    :code, :name_he, :category, mu.id,
                    true, false, :season, :disp
                FROM measurement_units mu
                WHERE mu.code = :unit_code
                  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.code = :code)
                """
            ),
            {
                "code": code,
                "name_he": name_he,
                "category": category,
                "season": season,
                "disp": disp,
                "unit_code": unit_code,
            },
        )

    for pcode, alias_text, conf in ALIASES:
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


def downgrade() -> None:
    conn = op.get_bind()
    for pcode in ("PRD030", "PRD031", "PRD032"):
        conn.execute(
            text("DELETE FROM product_aliases WHERE product_id = (SELECT id FROM products WHERE code = :c)"),
            {"c": pcode},
        )
    conn.execute(text("DELETE FROM products WHERE code IN ('PRD030', 'PRD031', 'PRD032')"))
