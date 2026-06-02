"""043: M10.4 — scope-skip + aliases for mypips nursery/grocery noise and a few produce lines."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "043"
down_revision = "042"
branch_labels = None
depends_on = None

_SCOPE: list[tuple[int, str, str, str, str]] = [
    (3347, "other", "contains", "רקפות פרח", "M10.4 SRC053 flower flats retail"),
    (3348, "grocery", "contains", "גוג'י ברי", "M10.4 packaged berries retail"),
    (3349, "other", "contains", "דשן", "M10.4 fertilizer/nursery"),
    (3350, "other", "contains", "תערובת שתילה", "M10.4 potting mix"),
    (3351, "other", "contains", "כלי שתילה", "M10.4 kids planting kit"),
    (3352, "other", "contains", "מקלות במבוק", "M10.4 bamboo stakes"),
    (3353, "other", "contains", "פחם איכותי", "M10.4 charcoal bag"),
    (3354, "grocery", "contains", "משחת קלנדולה", "M10.4 cosmetic salve"),
    (3355, "dry_grocery", "contains", "מקדמיה", "M10.4 macadamia pack"),
    (3356, "dry_grocery", "contains", "פקאן", "M10.4 pecan pack"),
    (3357, "grocery", "contains", "שמן קוקוס אורגני", "M10.4 coconut oil bottle"),
    (3358, "dry_grocery", "contains", "שקדים טבעיים", "M10.4 packaged almonds"),
    (3359, "other", "contains", "סוקולנטים", "M10.4 succulents retail"),
    (3360, "other", "contains", "זיגו קקטוס", "M10.4 cactus retail"),
    (3361, "other", "contains", "גרניום", "M10.4 geranium plant"),
    (3362, "other", "contains", "לוונדר", "M10.4 lavender plant"),
    (3363, "other", "contains", "כוסית רב שנתית", "M10.4 perennial retail"),
    (3364, "other", "contains", "נץ חלב", "M10.4 plant retail"),
    (3365, "other", "contains", "סנסיוורה", "M10.4 snake plant"),
    (3366, "other", "contains", "לאושטיאן", "M10.4 herb plant pot"),
    (3367, "other", "contains", "עציץ שעווה", "M10.4 wax planter"),
    (3368, "other", "contains", "אגלונמה", "M10.4 houseplant"),
    (3369, "grocery", "contains", "מיץ רימונים קפוא", "M10.4 frozen juice"),
    (3370, "other", "contains", "שתילי ירקות - סטרטרים", "M10.4 starter plants not priced produce"),
    (3371, "other", "contains", "ציפורן", "M10.4 nursery/clove ambiguity — skip retail plant line"),
    (3372, "other", "contains", "קרעה", "M10.4 herb plant retail"),
    (3373, "other", "contains", "לואיזה", "M10.4 herb plant"),
    (3374, "grocery", "contains", "אננס", "M10.4 pineapple retail no V1 code"),
    (3375, "other", "contains", "מלון כתום", "M10.4 melon retail line"),
    (3376, "other", "contains", "אבטיח", "M10.4 watermelon retail no V1 code"),
    (3377, "other", "contains", "במיה", "M10.4 okra retail no V1 code"),
    (3378, "other", "contains", "סברס", "M10.4 cactus fruit line"),
    (3379, "other", "contains", "לוביה", "M10.4 beans retail pack"),
    (3380, "grocery", "contains", "אפרסמון טריומף", "M10.4 persimmon retail pack line"),
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
        ("בננות", "PRD046"),
        ("מבצע בוקצ'וי- מארז 3 יח'", "PRD062"),
        ("מארז ארטישוק ננסי | מארז 6 יח'", "PRD035"),
        ("עלי בייבי אורגני", "PRD010"),
        ("פטרוזילה עציץ תבלין", "PRD012"),
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
        ("בננות", "PRD046"),
        ("מבצע בוקצ'וי- מארז 3 יח'", "PRD062"),
        ("מארז ארטישוק ננסי | מארז 6 יח'", "PRD035"),
        ("עלי בייבי אורגני", "PRD010"),
        ("פטרוזילה עציץ תבלין", "PRD012"),
    ]:
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": alias_text},
        )
