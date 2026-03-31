"""020: Apply unresolved_change_requests_v1 batch (Nimrod 2026-03-31).

- Extend products.category CHECK with fruits, eggs (organic box scope).
- Global aliases onto existing PRD003, PRD007, PRD026, PRD032.
- Insert PRD033–PRD067 + aliases from static review export (excludes
  donation rows marked not relevant).
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "020"
down_revision = "019"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# Map raw strings from admin/unresolved onto existing catalog codes.
EXISTING_PRODUCT_ALIASES: list[tuple[str, str, str]] = [
    ("PRD026", "סל אורגני משפחתי ליום", "1.0"),
    ("PRD026", "סל אורגני רגיל ליום ב'", "1.0"),
    ("PRD026", "סל אורגני רגיל ליום ה'", "1.0"),
    ("PRD032", "פלפל חריף אורגני", "1.0"),
    ("PRD007", "קישוא כהה אורגני", "1.0"),
    ("PRD003", "גמבה", "1.0"),
]

# (code, canonical_name_he, unit_code, category, seasonality_notes, display_order)
NEW_PRODUCTS: list[tuple[str, str, str, str, str, int]] = [
    ("PRD033", "נבטים", "unit", "leafy_greens", "כל השנה", 33),
    ("PRD034", "תערובת לחליטה", "bunch", "leafy_greens", "כל השנה", 34),
    ("PRD035", "ארטישוק", "unit", "fruiting_vegetables", "אביב-סתיו", 35),
    ("PRD036", "קולורבי", "kg", "brassicas", "כל השנה", 36),
    ("PRD037", "דלעת", "kg", "cucurbits", "קיץ-סתיו", 37),
    ("PRD038", "לימון", "kg", "fruits", "כל השנה", 38),
    ("PRD039", "סלרי שורש", "bunch", "root_vegetables", "כל השנה", 39),
    ("PRD040", "מנגולד", "bunch", "leafy_greens", "חורף-אביב", 40),
    ("PRD041", "דלורית", "kg", "cucurbits", "קיץ", 41),
    ("PRD042", "תפוח עץ", "kg", "fruits", "סתיו-חורף", 42),
    ("PRD043", "אפונה טריה", "kg", "legumes_fresh", "אביב-קיץ", 43),
    ("PRD044", "קייל", "bunch", "leafy_greens", "חורף-אביב", 44),
    ("PRD045", "כורכום טרי", "kg", "root_vegetables", "כל השנה", 45),
    ("PRD046", "בננה", "kg", "fruits", "כל השנה", 46),
    ("PRD047", "פלפל צהוב / כתום", "kg", "fruiting_vegetables", "אביב-סתיו", 47),
    ("PRD048", "שומר", "kg", "root_vegetables", "חורף", 48),
    ("PRD049", "תמר", "kg", "fruits", "כל השנה", 49),
    ("PRD050", "סלרי עלים", "bunch", "leafy_greens", "כל השנה", 50),
    ("PRD051", "פומלית", "kg", "fruits", "חורף-אביב", 51),
    ("PRD052", "אמרנט", "bunch", "leafy_greens", "אביב-קיץ", 52),
    ("PRD053", "פלפל רמירו", "kg", "fruiting_vegetables", "אביב-סתיו", 53),
    ("PRD054", "פפאיה", "kg", "fruits", "כל השנה", 54),
    ("PRD055", "קלמנטינה", "kg", "fruits", "חורף", 55),
    ("PRD056", "תפוח אדמה", "kg", "root_vegetables", "כל השנה", 56),
    ("PRD057", "ארטישוק ירושלמי", "kg", "root_vegetables", "סתיו-חורף", 57),
    ("PRD058", "אשכולית אדומה", "kg", "fruits", "חורף-אביב", 58),
    ("PRD059", "אבוקדו", "kg", "fruits", "כל השנה", 59),
    ("PRD060", "בטטה", "kg", "root_vegetables", "כל השנה", 60),
    ("PRD061", "תפוז", "kg", "fruits", "חורף", 61),
    ("PRD062", "בוקצ'וי", "bunch", "leafy_greens", "אביב-סתיו", 62),
    ("PRD063", "בזיליקום", "bunch", "leafy_greens", "אביב-קיץ", 63),
    ("PRD064", "מרווה", "bunch", "leafy_greens", "אביב-קיץ", 64),
    ("PRD065", "אשכולית", "kg", "fruits", "חורף-אביב", 65),
    ("PRD066", "אזוב", "bunch", "leafy_greens", "אביב-קיץ", 66),
    ("PRD067", "ביצים", "unit", "eggs", "כל השנה", 67),
]

# (product_code, alias_text, confidence)
NEW_ALIAS_ROWS: list[tuple[str, str, str]] = [
    ("PRD033", "מיקס נבטים לסלט אורגני", "1.0"),
    ("PRD033", "נבטוטי עדשים אורגניים", "1.0"),
    ("PRD033", "נבטים סיניים אורגניים", "1.0"),
    ("PRD033", "נבטי אלפלפא אורגניים", "1.0"),
    ("PRD033", "נבטי אפונה", "1.0"),
    ("PRD033", "נבטי צנונית", "1.0"),
    ("PRD033", "נבטי קייל", "1.0"),
    ("PRD033", "נבטי אמרנטוס", "1.0"),
    ("PRD034", "בדיוק - תערובת לחליטה", "1.0"),
    ("PRD035", "ארטישוק אורגני", "1.0"),
    ("PRD036", "קולורבי אורגני", "1.0"),
    ("PRD037", "דלעת אורגנית", "1.0"),
    ("PRD037", "דלעת ערמונים אורגנית", "1.0"),
    ("PRD037", "דלעת יפנית אורגנית", "1.0"),
    ("PRD038", "לימון אורגני", "1.0"),
    ("PRD039", "סלרי שורש אורגני", "1.0"),
    ("PRD039", "2 חב' שורש סלרי אורגני", "1.0"),
    ("PRD039", "שורש סלרי", "0.95"),
    ("PRD040", "מנגולד אורגני", "1.0"),
    ("PRD040", "2 חב' מנגולד אורגני ב-", "1.0"),
    ("PRD041", "דלורית אורגנית", "1.0"),
    ("PRD042", "תפוח עץ אורגני", "1.0"),
    ("PRD042", "תפוח עץ גרני סמיט אורג", "1.0"),
    ("PRD043", "אפונת שלג אורגנית", "1.0"),
    ("PRD044", "2 חב' קייל אדום אורגני", "1.0"),
    ("PRD044", "קייל אדום אורגני", "1.0"),
    ("PRD044", "קייל", "0.95"),
    ("PRD044", "קייל ירוק", "0.95"),
    ("PRD045", "כורכום טרי אורגני", "1.0"),
    ("PRD046", "בננה אורגנית", "1.0"),
    ("PRD046", "בננה", "0.95"),
    ("PRD047", "פלפל כתום / צהוב אורגנ", "1.0"),
    ("PRD047", "פלפל כתום", "0.95"),
    ("PRD047", "פלפל צהוב", "0.95"),
    ("PRD048", "שומר אורגני", "1.0"),
    ("PRD049", "תמר מג'הול אורגני 1 ק\"", "1.0"),
    ("PRD050", "2 חב' סלרי עלים אורגני", "1.0"),
    ("PRD050", "סלרי עלים אורגני", "1.0"),
    ("PRD051", "פומלית אורגנית", "1.0"),
    ("PRD052", "אמרנט אורגני", "1.0"),
    ("PRD053", "פלפל רמירו אורגני", "1.0"),
    ("PRD053", "פלפל שושקה", "0.95"),
    ("PRD053", "פלפל ארוך", "0.95"),
    ("PRD054", "פפאיה אורגנית", "1.0"),
    ("PRD055", "קלמנטינה אורגנית", "1.0"),
    ("PRD056", "תפוח אדמה אורגני", "1.0"),
    ("PRD056", "תפוח אדמה אדום אורגני", "1.0"),
    ("PRD057", "ארטישוק ירושלמי אורגני", "1.0"),
    ("PRD058", "אשכולית אדומה אורגני", "1.0"),
    ("PRD059", "אבוקדו אורגני", "1.0"),
    ("PRD060", "בטטה אורגנית", "1.0"),
    ("PRD060", "בטטה", "0.95"),
    ("PRD061", "תפוז אורגני", "1.0"),
    ("PRD062", "בקצ'וי", "1.0"),
    ("PRD062", "פאקצ'וי", "0.95"),
    ("PRD062", "בקצוי", "0.9"),
    ("PRD063", "בזיליקום", "1.0"),
    ("PRD064", "מרווה", "1.0"),
    ("PRD065", "אשכולית", "1.0"),
    ("PRD066", "זעתר", "1.0"),
    ("PRD067", "ביצי חופש אורגניות", "1.0"),
    ("PRD067", "ביצים", "0.95"),
]


def _insert_product(conn, code: str, name_he: str, unit_code: str, category: str, season: str, disp: int) -> None:
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

    op.drop_constraint("chk_p_category", "products", type_="check")
    op.create_check_constraint(
        "chk_p_category",
        "products",
        "category IN ("
        "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
        "'alliums','cucurbits','legumes_fresh','baskets','fruits','eggs')",
    )

    for code, name_he, unit_code, category, season, disp in NEW_PRODUCTS:
        _insert_product(conn, code, name_he, unit_code, category, season, disp)

    for pcode, alias_text, conf in EXISTING_PRODUCT_ALIASES:
        _insert_alias(conn, pcode, alias_text, conf)

    for pcode, alias_text, conf in NEW_ALIAS_ROWS:
        _insert_alias(conn, pcode, alias_text, conf)


def downgrade() -> None:
    conn = op.get_bind()
    codes_new = [r[0] for r in NEW_PRODUCTS]
    for pcode in reversed(codes_new):
        conn.execute(
            text("DELETE FROM product_aliases WHERE product_id = (SELECT id FROM products WHERE code = :c)"),
            {"c": pcode},
        )
        conn.execute(text("DELETE FROM products WHERE code = :c"), {"c": pcode})

    for pcode, alias_text, _conf in reversed(EXISTING_PRODUCT_ALIASES):
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

    op.drop_constraint("chk_p_category", "products", type_="check")
    op.create_check_constraint(
        "chk_p_category",
        "products",
        "category IN ("
        "'root_vegetables','fruiting_vegetables','leafy_greens','brassicas',"
        "'alliums','cucurbits','legumes_fresh','baskets')",
    )
