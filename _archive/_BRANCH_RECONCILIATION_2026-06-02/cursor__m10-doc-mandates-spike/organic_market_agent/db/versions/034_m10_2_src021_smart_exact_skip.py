"""034: M10.2 — exact scope-skip for SRC021 unresolvables that do not contain a catalog product name."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None

# SRC022 residual: produce aliases + obvious grocery exact (display_order 2800-2999 reserved below bulk)
_SRC022_EXACT_SKIP: list[tuple[int, str]] = [
    (2800, "ג'ל כביסה 4 ליטר ''אקו"),
    (2801, 'גבינה צהובה "אדם" 100'),
    (2802, 'גבינה צהובה "גאודה" 10'),
    (2803, "גרעיני דלעת קלופים , ב"),
    (2804, "גרעיני חמניה קלופים ,"),
    (2805, "זרעי פשתן 400 גר"),
    (2806, "זרעי צ'יה 300 גר'"),
    (2807, 'טחינה 1 קילו "תבואות"'),
    (2808, "נקטר משמש 1 ליטר"),
    (2809, "נקטר שזיף 1 ליטר"),
    (2810, "סל של 110 ש\"ח מוצרים מ"),
    (2811, "סל של 190 ש\"ח שכולל יר"),
    (2812, "סמוזי מנגו אפרסק תפוח"),
    (2813, "סמוזי פירות אדומים"),
    (2814, "קינמון טחון"),
    (2815, 'שמן קנולה "תבואות"'),
    (2816, "תבלין קארי CANNAMELA"),
]

_SRC022_ALIASES: list[tuple[str, str]] = [
    ("דלעת", "PRD037"),
    ("אפונה סינית", "PRD043"),
    ("זוג חסות עלי אלון אדומ", "PRD008"),
    ("מארז 350 גר' פלפל swee", "PRD047"),
    ("סלסלת נבטוטים", "PRD033"),
    ("תערובת עלים לסלט - האר", "PRD008"),
    ("תערובת עלים לסלט - קטנ", "PRD008"),
    ("דלעת יפנית", "PRD037"),
]


def upgrade() -> None:
    conn = op.get_bind()
    # Drop non-existent product codes from aliases
    valid = {
        row[0]
        for row in conn.execute(text("SELECT code FROM products WHERE code LIKE 'PRD%'")).fetchall()
    }
    _aliases = [(a, c) for a, c in _SRC022_ALIASES if c in valid]

    for d, pat in _SRC022_EXACT_SKIP:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (:d, 'grocery', 'exact', :p, 'M10.2 SRC022 exact', NULL, true)
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"d": d, "p": pat[:500]},
        )

    for at, pcode in _aliases:
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

    # Bulk SRC021: exact skip per distinct unresolvable line unless raw contains an active product name
    conn.execute(
        text(
            """
            INSERT INTO catalog_scope_skip_rules (
                display_order, category_code, match_type, pattern, notes,
                future_product_code, is_active
            )
            SELECT
                3000 + ROW_NUMBER() OVER (ORDER BY trimmed),
                'grocery',
                'exact',
                LEFT(trimmed, 500),
                'M10.2 SRC021 smart exact (no embedded canonical product name)',
                NULL,
                true
            FROM (
                SELECT DISTINCT TRIM(rei.raw_product_name) AS trimmed
                FROM raw_extracted_items rei
                JOIN source_fetch_runs sfr ON sfr.id = rei.source_fetch_run_id
                JOIN sources s ON s.id = sfr.source_id
                WHERE s.code = 'SRC021'
                  AND rei.extraction_status = 'unresolvable'
                  AND TRIM(COALESCE(rei.raw_product_name, '')) <> ''
            ) d
            WHERE LENGTH(trimmed) <= 500
              AND NOT EXISTS (
                SELECT 1 FROM products p
                WHERE p.is_active IS TRUE
                  AND char_length(TRIM(p.canonical_name_he)) >= 3
                  AND strpos(
                    lower(regexp_replace(trimmed, '[[:space:]]+', ' ', 'g')),
                    lower(regexp_replace(TRIM(p.canonical_name_he), '[[:space:]]+', ' ', 'g'))
                  ) > 0
              )
            ON CONFLICT (display_order) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM catalog_scope_skip_rules WHERE notes LIKE 'M10.2 SRC021 smart exact%'")
    )
    conn.execute(text("DELETE FROM catalog_scope_skip_rules WHERE notes = 'M10.2 SRC022 exact'"))
    for d, _ in _SRC022_EXACT_SKIP:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"), {"d": d}
        )
    valid = {r[0] for r in conn.execute(text("SELECT code FROM products")).fetchall()}
    for at, pcode in _SRC022_ALIASES:
        if pcode not in valid:
            continue
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": at},
        )
