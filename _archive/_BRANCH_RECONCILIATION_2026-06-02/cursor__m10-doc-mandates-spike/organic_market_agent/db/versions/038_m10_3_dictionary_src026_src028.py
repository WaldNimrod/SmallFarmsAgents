"""038: M10.3 — scope-skip + aliases for SRC026/SRC028 residuals; SRC027 pizza sauce line."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "038"
down_revision = "037"
branch_labels = None
depends_on = None

_SCOPE: list[tuple[int, str, str, str, str]] = [
    (3325, "other", "contains", "מלון melon", "M10.3 SRC026 fruit line / no V1 code"),
    (3326, "other", "contains", "כף אווז", "M10.3 SRC026 lambs quarter herb"),
    (3327, "grocery", "contains", "אזומייט", "M10.3 SRC026 soil amendment"),
    (3328, "other", "contains", "קומפוסט compost", "M10.3 SRC026 compost SKU"),
    (3329, "grocery", "contains", "CANNAMELA", "M10.3 SRC028 spice brand jars"),
    (3330, "grocery", "contains", "גבינה מלוחה", "M10.3 SRC028 cheese"),
    (3331, "grocery", "contains", "גבינת ", "M10.3 SRC028 cheese SKUs"),
    (3332, "other", "contains", "האופציה האקולוגית", "M10.3 SRC028 bagging UI line"),
    (3333, "grocery", "contains", "אטריות טליאטלה", "M10.3 SRC028 pasta"),
    (3334, "grocery", "contains", "חומץ בלסמי", "M10.3 SRC028 vinegar"),
    (3335, "dry_grocery", "contains", "בורגול עבה", "M10.3 SRC028 bulgur"),
    (3336, "dry_grocery", "contains", "זרעי פשתן", "M10.3 SRC028 flax seed"),
    (3337, "dry_grocery", "contains", "גרעיני חמניות", "M10.3 SRC028 sunflower kernels"),
    (3338, "dry_grocery", "contains", "גרעיני תירס", "M10.3 SRC028 corn kernels"),
    (3339, "grocery", "contains", "אבקת קקאו", "M10.3 SRC028 cocoa powder"),
    (3340, "dry_grocery", "contains", "אגוז פקאן", "M10.3 SRC028 pecans"),
    (3341, "dry_grocery", "contains", "אגוזי ברזיל", "M10.3 SRC028 brazil nuts"),
    (3342, "dry_grocery", "contains", "גריסי פנינה", "M10.3 SRC028 pearled grains"),
    (3343, "grocery", "contains", "אננס בינוני", "M10.3 SRC028 pineapple retail / no V1 code"),
    (3344, "other", "contains", "ג'ינג'ר", "M10.3 SRC028 ginger retail / no V1 code"),
    (3345, "grocery", "contains", "MUTTI", "M10.3 SRC027 imported sauce jar"),
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

    _alias_rows = [
        ("קיוו Kiwi", "PRD068"),
        ("ביצי חופש eggs free range", "PRD067"),
        ("כורכום turmeric", "PRD045"),
        ("אפונה ירוקה אורגנית", "PRD043"),
    ]
    for alias_text, pcode in _alias_rows:
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
        ("קיוו Kiwi", "PRD068"),
        ("ביצי חופש eggs free range", "PRD067"),
        ("כורכום turmeric", "PRD045"),
        ("אפונה ירוקה אורגנית", "PRD043"),
    ]:
        conn.execute(
            text(
                """
                DELETE FROM product_aliases
                WHERE alias_text = :t AND source_id IS NULL
                """
            ),
            {"t": alias_text},
        )
