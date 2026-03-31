"""028: Add `grocery` scope-skip category, broad retail patterns, mined exact unresolvable.

Nimrod decision: classify general grocery (מכולת) as V1 out-of-scope. Mined rows exclude
active product canonical names and global aliases so vegetable lines stay resolvable.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "028"
down_revision = "027"
branch_labels = None
depends_on = None

# display_order, pattern, notes_en (match_type=contains, category=grocery)
GROCERY_CONTAINS: list[tuple[int, str, str]] = [
    (14, "שמפו", "Shampoo / hair care retail"),
    (15, "דאודורנט", "Deodorant"),
    (16, "נוזל לניקוי", "Cleaning liquid (toilet/surface)"),
    (17, "נוזל כלים", "Dish liquid"),
    (18, "מלח", "Salt / packaged salt retail"),
    (19, "קמח", "Flour"),
    (20, "קוסקוס", "Couscous"),
    (21, "סמוצ", "Smoothie beverage / product line"),
    (22, "עוגיות", "Cookies"),
    (23, "משקה דגנים", "Grain drink"),
    (24, "שמן אתרי", "Essential oil"),
    (25, "ממרח", "Spreads"),
    (26, "חמאת בוטנים", "Nut butter"),
    (27, "חטיף", "Snack bar"),
    (28, "גרנולה", "Granola"),
    (29, "כדורי חלבה", "Confectionery"),
    (30, "זיתי", "Olives jarred"),
    (31, "תבואות -", "Dry goods grid prefix"),
    (32, "יין", "Wine"),
    (33, "סיידר", "Cider"),
    (34, "קארי טחון", "Ground curry spice retail"),
    (35, "פפריקה מתוקה", "Paprika spice"),
    (36, "פלפל שחור טחון", "Ground pepper spice"),
    (37, "פלפל שחור אורגני במטחנ", "Ground pepper retail"),
    (38, "פרג טחון", "Poppy spice"),
    (39, "קרקר", "Crackers"),
    (40, "חומץ תפוחים", "Apple cider vinegar retail"),
    (41, "דבש", "Honey jar retail"),
    (42, "מרלו - יין", "Wine line"),
    (43, "מיץ תפוח", "Juice carton"),
    (44, "פטריות פורטבלו", "Packaged mushrooms retail (not V1 fresh line)"),
    (45, "פטריות רעמת", "Lions mane product retail"),
    (46, "צנדריקה", "Footwear on mixed grid"),
    (47, "לוח שנה", "Non-food retail"),
    (48, "שמן זית אורגני", "Bottled olive oil retail line"),
    (49, "קלמנטינה", "Packaged citrus retail on mixed grid"),
    (50, "צמחי בר למאכל", "Foraging book/product retail"),
]


def upgrade() -> None:
    op.drop_constraint("chk_cssr_category", "catalog_scope_skip_rules", type_="check")
    op.create_check_constraint(
        "chk_cssr_category",
        "catalog_scope_skip_rules",
        "category_code IN ('donation','cleaning','dry_grocery','grocery','other')",
    )

    conn = op.get_bind()
    for display_order, pattern, notes in GROCERY_CONTAINS:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (
                    :display_order, 'grocery', 'contains', :pattern, :notes,
                    NULL, true
                )
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"display_order": display_order, "pattern": pattern, "notes": notes},
        )

    conn.execute(
        text(
            """
            INSERT INTO catalog_scope_skip_rules (
                display_order, category_code, match_type, pattern, notes,
                future_product_code, is_active
            )
            SELECT
                1000 + ROW_NUMBER() OVER (ORDER BY trimmed)::int,
                'grocery',
                'exact',
                LEFT(trimmed, 500),
                'Mined: unresolvable at migration; excluded catalog canonical + global aliases',
                NULL,
                true
            FROM (
                SELECT DISTINCT TRIM(rei.raw_product_name) AS trimmed
                FROM raw_extracted_items rei
                WHERE rei.extraction_status = 'unresolvable'
                  AND rei.is_quarantined IS NOT TRUE
                  AND TRIM(COALESCE(rei.raw_product_name, '')) <> ''
            ) d
            WHERE LENGTH(trimmed) <= 500
              AND NOT EXISTS (
                SELECT 1 FROM products p
                WHERE p.is_active IS TRUE
                  AND lower(regexp_replace(trim(p.canonical_name_he), '[[:space:]]+', ' ', 'g'))
                    = lower(regexp_replace(trim(d.trimmed), '[[:space:]]+', ' ', 'g'))
              )
              AND NOT EXISTS (
                SELECT 1 FROM product_aliases pa
                WHERE pa.is_active IS TRUE
                  AND pa.source_id IS NULL
                  AND pa.alias_text_normalized
                    = lower(regexp_replace(trim(d.trimmed), '[[:space:]]+', ' ', 'g'))
              )
            ON CONFLICT (display_order) DO NOTHING
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM catalog_scope_skip_rules WHERE category_code = 'grocery'"))
    op.drop_constraint("chk_cssr_category", "catalog_scope_skip_rules", type_="check")
    op.create_check_constraint(
        "chk_cssr_category",
        "catalog_scope_skip_rules",
        "category_code IN ('donation','cleaning','dry_grocery','other')",
    )
