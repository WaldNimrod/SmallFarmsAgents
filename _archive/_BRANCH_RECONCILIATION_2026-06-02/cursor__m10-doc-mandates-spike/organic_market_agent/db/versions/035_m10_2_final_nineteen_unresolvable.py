"""035: M10.2 — clear last community unresolvable rows (aliases + exact skips)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None

_EXACT_SKIP: list[tuple[int, str, str]] = [
    (2850, "נקודת איסוף(₪5 דמי משלוח)", "other"),
    (2851, "עדשים חומות", "dry_grocery"),
    (2852, "עדשים ירוקות", "dry_grocery"),
    (2853, "מחית 100% תמרים שקד הת", "grocery"),
    (2854, "אמרנט תבואות 500 גרם", "dry_grocery"),
    (2855, "שוקולתמר כדורי ביס פיס", "grocery"),
    (2856, "שוקותמר במילוי בוטנים", "grocery"),
    (2857, "שוקותמר קוקוס (בית השק", "grocery"),
    (2858, "שוקותמר שקדים (בית השק", "grocery"),
    (2859, "קפה מפולי תמר עם אגוזי", "grocery"),
    (2860, "תחליף קפה מפולי תמרים", "grocery"),
    (2861, "שיבולת שועל", "dry_grocery"),
    (2862, "שקדים", "dry_grocery"),
]

_ALIASES: list[tuple[str, str]] = [
    ("פומלית", "PRD051"),
    ("תפוח עץ אופל", "PRD042"),
    ("נבטים סיניים", "PRD033"),
    ("דלורית", "PRD041"),
    ("רבעי ארטישוק על הגריל", "PRD035"),
    ("עגבנייה", "PRD001"),
]


def upgrade() -> None:
    conn = op.get_bind()
    valid = {r[0] for r in conn.execute(text("SELECT code FROM products")).fetchall()}
    for d, pat, cat in _EXACT_SKIP:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (:d, :cat, 'exact', :p, 'M10.2 final nineteen', NULL, true)
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"d": d, "cat": cat, "p": pat[:500]},
        )
    for at, pcode in _ALIASES:
        if pcode not in valid:
            continue
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
                )
                SELECT p.id, :at,
                  lower(regexp_replace(trim(:at), '[[:space:]]+', ' ', 'g')),
                  0.95, true, NULL
                FROM products p WHERE p.code = :code
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa
                    WHERE pa.alias_text_normalized =
                      lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g'))
                      AND pa.source_id IS NULL
                  )
                """
            ),
            {"at": at, "at2": at, "code": pcode},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for d, _, _ in _EXACT_SKIP:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"), {"d": d}
        )
    valid = {r[0] for r in conn.execute(text("SELECT code FROM products")).fetchall()}
    for at, pcode in _ALIASES:
        if pcode not in valid:
            continue
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": at},
        )
