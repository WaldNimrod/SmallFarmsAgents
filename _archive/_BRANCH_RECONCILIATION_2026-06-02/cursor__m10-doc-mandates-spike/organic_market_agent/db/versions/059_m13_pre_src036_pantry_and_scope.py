"""059: M13-PRE — SRC036 normalization path: pantry_dry products, SRC036 aliases, scope rule fixes.

- Deactivate M10.5 058 rules 3501–3514 and 056 rule 3501 (השדה) so Teva lines reach alias resolution.
- Deactivate overly broad grocery scope rules that match Teva organic search titles (1311, 1337, 1345).
- Add category ``pantry_dry`` (Team 100 M13-PRE pre-approval).
- Insert PRD087–PRD100 pantry retail products + SRC036-scoped exact aliases for current Teva titles.
- Re-queue SRC036 rows that were ``ignored`` due to approved_scope_skip so ``catalog_renormalize`` can normalize them.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "059"
down_revision = "058"
branch_labels = None
depends_on = None

# display_order values to turn off (global rules that blocked Teva SKUs or M10.5 packaged skips)
_DEACTIVATE_SCOPE_DISPLAY_ORDERS = (
    3501,  # 056 – השדה
    3502,
    3503,
    3504,
    3505,
    3506,
    3507,
    3508,
    3509,
    3510,
    3511,
    3512,
    3513,
    3514,
    1311,  # אבקת מרק — matches Teva soup powder line
    1337,  # סילאן אורגני — matches Teva silan line
    1345,  # חומוס — matches Teva hummus line
)

# (code, canonical_name_he, unit_code, display_order)
_PANTRY_PRODUCTS: list[tuple[str, str, str, int]] = [
    ("PRD087", "קינואה אורגנית ארוזה", "unit", 187),
    ("PRD088", "חומוס אורגני ארוז", "unit", 188),
    ("PRD089", "שיבולת שועל אורגנית ארוזה", "unit", 189),
    ("PRD090", "מחית פירות אורגנית ארוזה", "unit", 190),
    ("PRD091", "משקה שקדים אורגני ארוז", "unit", 191),
    ("PRD092", "סילאן אורגני ארוז", "unit", 192),
    ("PRD093", "רסק תפוחים אורגני ארוז", "unit", 193),
    ("PRD094", "חמאת גהי אורגנית ארוזה", "unit", 194),
    ("PRD095", "זרעי צ׳יה אורגני ארוז", "unit", 195),
    ("PRD096", "פסטה אורגנית יבשה ארוזה", "unit", 196),
    ("PRD097", "נודלס אורגני ארוז", "unit", 197),
    ("PRD098", "אבקת מרק אורגנית ארוזה", "unit", 198),
    ("PRD099", "אטריות אורגניות ארוזות", "unit", 199),
    ("PRD100", "ערמונים אורגניים ארוזים", "unit", 200),
]

# (alias_text, product_code) — exact titles from SellioParser (price stripped)
_SRC036_ALIAS_ROWS: list[tuple[str, str]] = [
    ("קינואה רויאל אורגנית", "PRD087"),
    ("חומוס אורגני", "PRD088"),
    ("קוואקר דק אורגני", "PRD089"),
    ("קוואקר עבה אורגני ללא גלוטן", "PRD089"),
    ("מחית בננה ותפוח אורגנית", "PRD090"),
    ("חלב אורז עם שקדים אורגני", "PRD091"),
    ("חלב שקדים אורגני 0% סוכר", "PRD091"),
    ("חלב שקדים אורגני", "PRD091"),
    ("סילאן לחיץ אורגני 350גרם", "PRD092"),
    ("רסק תפוחי עץ אורגני", "PRD093"),
    ("חמאת גהי אורגנית", "PRD094"),
    ("זרעי צ'יה אורגני", "PRD095"),
    ("זרעי צ׳יה אורגני", "PRD095"),
    ("פסטה כוסמין פוזילי אורגני – השדה", "PRD096"),
    ("פסטה כוסמין אורגנית עם ספירולינה פטוצ'יני – השדה", "PRD096"),
    ("פסטה כוסמין פטוצ'יני תרד – השדה", "PRD096"),
    ("נודלס אורז מלא ואצות וואקמה ללא גלוטן אורגני – השדה", "PRD097"),
    ("נודלס אורז מלא ללא גלוטן אורגני – השדה", "PRD097"),
    ("נודלס אורז שחור ללא גלוטן אורגני – השדה", "PRD097"),
    ("נודלס סובה מכוסמת ללא גלוטן אורגני – השדה", "PRD097"),
    ("אבקת מרק ירקות אורגנית – השדה", "PRD098"),
    ("אטריות אורגניות מאורז תאילנדי – ללא גלוטן – השדה", "PRD099"),
    ("ערמונים אורגניים קלווים כרם", "PRD100"),
]


def upgrade() -> None:
    conn = op.get_bind()

    op.drop_constraint("chk_p_category", "products", type_="check")
    op.create_check_constraint(
        "chk_p_category",
        "products",
        "category IN ("
        "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
        "'alliums','cucurbits','legumes_fresh','baskets','fruits','eggs','pantry_dry'"
        ")",
    )

    for d in _DEACTIVATE_SCOPE_DISPLAY_ORDERS:
        conn.execute(
            text(
                "UPDATE catalog_scope_skip_rules SET is_active = false, "
                "notes = COALESCE(notes,'') || ' [deactivated 059 M13-PRE]' WHERE display_order = :d"
            ),
            {"d": d},
        )

    for code, name_he, unit_code, disp in _PANTRY_PRODUCTS:
        conn.execute(
            text(
                """
                INSERT INTO products (
                    code, canonical_name_he, category, default_measurement_unit_id,
                    is_organic_required, is_basket_product, seasonality_notes, display_order
                )
                SELECT
                    :code, :name_he, 'pantry_dry', mu.id,
                    true, false, 'M13-PRE retail organic', :disp
                FROM measurement_units mu
                WHERE mu.code = :unit_code
                  AND NOT EXISTS (SELECT 1 FROM products p WHERE p.code = :code2)
                """
            ),
            {
                "code": code,
                "code2": code,
                "name_he": name_he,
                "unit_code": unit_code,
                "disp": disp,
            },
        )

    for alias_text, pcode in _SRC036_ALIAS_ROWS:
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
                )
                SELECT p.id, :at,
                  lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
                  0.97, true, s.id
                FROM products p
                CROSS JOIN sources s
                WHERE p.code = :pcode AND s.code = 'SRC036'
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa
                    WHERE pa.alias_text_normalized =
                      lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                      AND pa.source_id = s.id
                  )
                """
            ),
            {"at": alias_text, "at2": alias_text, "at3": alias_text, "pcode": pcode},
        )

    conn.execute(
        text(
            """
            UPDATE raw_extracted_items rei
            SET extraction_status = 'extracted',
                unresolvable_reason = NULL,
                ignore_reason_code = NULL
            FROM source_fetch_runs sfr
            JOIN sources s ON s.id = sfr.source_id
            WHERE rei.source_fetch_run_id = sfr.id
              AND s.code = 'SRC036'
              AND rei.extraction_status = 'ignored'
              AND rei.ignore_reason_code = 'approved_scope_skip'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()

    for alias_text, _ in _SRC036_ALIAS_ROWS:
        conn.execute(
            text(
                """
                DELETE FROM product_aliases pa
                USING sources s
                WHERE pa.source_id = s.id AND s.code = 'SRC036' AND pa.alias_text = :t
                """
            ),
            {"t": alias_text},
        )

    for code, _, _, _ in _PANTRY_PRODUCTS:
        conn.execute(
            text("DELETE FROM product_aliases WHERE product_id = (SELECT id FROM products WHERE code = :c)"),
            {"c": code},
        )
        conn.execute(text("DELETE FROM products WHERE code = :c"), {"c": code})

    for d in _DEACTIVATE_SCOPE_DISPLAY_ORDERS:
        conn.execute(
            text(
                "UPDATE catalog_scope_skip_rules SET is_active = true, "
                "notes = regexp_replace(COALESCE(notes,''), ' \\[deactivated 059 M13-PRE\\]', '') "
                "WHERE display_order = :d"
            ),
            {"d": d},
        )

    op.drop_constraint("chk_p_category", "products", type_="check")
    op.create_check_constraint(
        "chk_p_category",
        "products",
        "category IN ("
        "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
        "'alliums','cucurbits','legumes_fresh','baskets','fruits','eggs'"
        ")",
    )
