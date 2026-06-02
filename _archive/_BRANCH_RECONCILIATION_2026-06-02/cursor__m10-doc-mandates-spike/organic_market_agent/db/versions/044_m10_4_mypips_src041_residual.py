"""044: M10.4 — SRC041 grocery scope-skip + produce aliases (mypips bestfruit)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "044"
down_revision = "043"
branch_labels = None
depends_on = None

_SCOPE: list[tuple[int, str, str, str, str]] = [
    (3381, "grocery", "contains", "קולה", "M10.4 SRC041 soda"),
    (3382, "grocery", "contains", "קוה ", "M10.4 SRC041 cola typo line"),
    (3383, "grocery", "contains", "קולי זירו", "M10.4 SRC041 soda typo"),
    (3384, "grocery", "contains", "שמן חמניות מזוכך", "M10.4 SRC041 bottled oil"),
    (3385, "grocery", "contains", "שמן קנולה", "M10.4 SRC041 canola bottle"),
    (3386, "grocery", "contains", "תבלין לשיפודים", "M10.4 SRC041 spice jar"),
    (3387, "grocery", "contains", "תבלין שווארמה", "M10.4 SRC041 spice jar"),
    (3388, "grocery", "contains", "שווארמה אסלי", "M10.4 SRC041 spice mix"),
    (3389, "grocery", "contains", "פפריקה", "M10.4 SRC041 spice jar"),
    (3390, "grocery", "contains", "גריל דג", "M10.4 SRC041 seasoning"),
    (3391, "grocery", "contains", "נבטי חמניות מהדרין", "M10.4 SRC041 sprout pack retail"),
    (3392, "other", "contains", "רוזמרי", "M10.4 SRC041 herb plant/pack ambiguity"),
    (3393, "other", "contains", "מלון", "M10.4 SRC041 melon line no V1"),
    (3394, "other", "contains", "אפרסמון", "M10.4 SRC041 persimmon retail no V1"),
    (3395, "other", "contains", "ענב לבן", "M10.4 SRC041 grapes line"),
    (3396, "other", "contains", "פלפל אנגלי", "M10.4 SRC041 pepper retail line"),
    (3397, "other", "contains", "פלפלונים אורגני", "M10.4 SRC041 small peppers pack"),
    (3399, "other", "contains", "רוגולה", "M10.4 SRC041 arugula pack line"),
    (3400, "other", "contains", "פטל אדום", "M10.4 SRC041 raspberry retail no V1"),
    (3401, "other", "contains", "רימון", "M10.4 SRC041 pomegranate retail no V1"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for display_order, cat, mtype, pattern, notes in _SCOPE:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (
                    :d, :cat, :mtype, :pat, :notes, NULL, true
                )
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"d": display_order, "cat": cat, "mtype": mtype, "pat": pattern, "notes": notes},
        )

    _aliases = [
        ("תפוח עץ סמיט", "PRD042"),
        ("תפוח עץ סמיט גדול", "PRD042"),
        ("כורכום", "PRD045"),
        ("עלי בייבי למהדרין חצי קילו", "PRD010"),
        ("פאקצוי מהדרין", "PRD062"),
    ]
    for alias_text, pcode in _aliases:
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
                )
                SELECT p.id, :at,
                  lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
                  0.95, true, NULL
                FROM products p WHERE p.code = :code
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa
                    WHERE pa.alias_text_normalized =
                      lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                      AND pa.source_id IS NULL
                  )
                """
            ),
            {"at": alias_text, "at2": alias_text, "at3": alias_text, "code": pcode},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for display_order, *_ in _SCOPE:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"),
            {"d": display_order},
        )
    for alias_text, _ in [
        ("תפוח עץ סמיט", "PRD042"),
        ("תפוח עץ סמיט גדול", "PRD042"),
        ("כורכום", "PRD045"),
        ("עלי בייבי למהדרין חצי קילו", "PRD010"),
        ("פאקצוי מהדרין", "PRD062"),
    ]:
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": alias_text},
        )
