"""033: M10.2 follow-up — SRC021/SRC022 residual grocery patterns + produce aliases."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "033"
down_revision = "032"
branch_labels = None
depends_on = None

_SCOPE: list[tuple[int, str, str, str, str]] = [
    (1380, "grocery", "contains", "שוקולד", "M10.2 chocolate retail"),
    (1381, "grocery", "contains", "פופקורן", "M10.2 popcorn"),
    (1382, "grocery", "contains", "מעדן חלבון", "M10.2 protein dessert"),
    (1383, "grocery", "contains", "יוגורט", "M10.2 yogurt"),
    (1384, "grocery", "contains", "טופו", "M10.2 tofu"),
    (1385, "grocery", "contains", "פסטה", "M10.2 pasta"),
    (1386, "grocery", "contains", "מיץ שזיפים", "M10.2 juice"),
    (1387, "grocery", "contains", "תה ירוק", "M10.2 tea"),
    (1388, "grocery", "contains", "זוג כפפות", "M10.2 gloves"),
    (1389, "grocery", "contains", "קרחונים פינגווינים", "M10.2 ice pops"),
    (1390, "grocery", "contains", "אבקת אשווגנדה", "M10.2 supplement"),
    (1391, "grocery", "contains", "גוג'י ברי", "M10.2 goji"),
    (1392, "grocery", "contains", "גוג'י", "M10.2 goji"),
    (1393, "dry_grocery", "contains", "קינואה טריו", "M10.2 quinoa pack"),
    (1394, "grocery", "contains", "קטשופ השדה", "M10.2 ketchup"),
    (1395, "grocery", "contains", "מחית תפוח", "M10.2 puree spread"),
    (1396, "grocery", "contains", "רוטב מירין", "M10.2 mirin"),
    (1397, "grocery", "contains", "אריזת סנדוויץ", "M10.2 sandwich bags"),
    (1398, "grocery", "contains", "ברזל כמוסות", "M10.2 supplement"),
    (1399, "grocery", "contains", "נוביקס", "M10.2 cosmetic"),
    (1400, "grocery", "contains", "משקה עולש", "M10.2 drink"),
    (1401, "grocery", "contains", "שוקולנמר", "M10.2 confectionery"),
    (1402, "grocery", "contains", "אצות וואקמה", "M10.2 seaweed retail"),
    (1403, "grocery", "contains", "חמאת קוקוס 100%", "M10.2 coconut butter"),
    (1404, "grocery", "contains", "תמר ברהי", "M10.2 dates bulk"),
    (1405, "dry_grocery", "contains", "פנה מחיטה", "M10.2 pasta"),
    (1406, "grocery", "contains", "מגן תחתון", "M10.2 hygiene"),
    (1407, "grocery", "contains", "קרם פנים", "M10.2 face cream"),
    (1408, "cleaning", "contains", "מסיר אבנית", "M10.2 limescale"),
    (1409, "grocery", "contains", "מצות גלוטרי", "M10.2 matzo"),
    (1410, "grocery", "contains", "שימורי אפונה", "M10.2 canned peas"),
    (1411, "grocery", "contains", "פת פריכה", "M10.2 cracker"),
    (1412, "grocery", "contains", "לבאנה", "M10.2 labneh"),
    (1413, "grocery", "contains", "שקד עין חרוד", "M10.2 almond product"),
    (1414, "grocery", "contains", "אבקת פסיליום", "M10.2 psyllium"),
    (1415, "grocery", "contains", "דפי לזניה", "M10.2 lasagna sheets"),
    (1416, "grocery", "contains", "ביסקוטי", "M10.2 biscuit"),
    (1417, "grocery", "contains", "סירופ מייפל", "M10.2 maple syrup"),
    (1418, "grocery", "contains", "קפה נמס", "M10.2 instant coffee"),
    (1419, "grocery", "contains", "Red Giant", "M10.2 brand retail"),
    (1420, "grocery", "contains", "גבינה בולגרית", "M10.2 cheese"),
    (1421, "grocery", "contains", "אבקת קקאו נא", "M10.2 cocoa"),
    (1422, "dry_grocery", "contains", "אפונה יבשה", "M10.2 dry pea"),
    (1423, "dry_grocery", "contains", "עדשים שחורות", "M10.2 dry lentils"),
    (1424, "dry_grocery", "contains", "עדשים צהובות", "M10.2 dry lentils"),
    (1425, "dry_grocery", "contains", "עדשים אדומות", "M10.2 dry lentils"),
    (1426, "dry_grocery", "contains", "קינואה אדומה", "M10.2 quinoa"),
    (1427, "dry_grocery", "contains", "קינואה בתפזורת", "M10.2 quinoa"),
    (1428, "grocery", "contains", "גלילי קוקוס", "M10.2 coconut roll snack"),
    (1429, "grocery", "contains", "שמן חמניה", "M10.2 oil bottle"),
    (1430, "grocery", "contains", "שוקולד לבן", "M10.2 white chocolate"),
    (1431, "grocery", "contains", "מקלות קינמון", "M10.2 cinnamon sticks"),
    (1432, "grocery", "contains", "תבלין כמון", "M10.2 spice"),
    (1433, "grocery", "contains", "מיץ אננס", "M10.2 juice"),
    (1434, "grocery", "contains", "לאסי", "M10.2 lassi"),
    (1435, "grocery", "contains", "אגוזי מלך", "M10.2 walnuts pack"),
    (1436, "grocery", "contains", "אגוז ברזיל", "M10.2 brazil nuts"),
    (1437, "grocery", "contains", "אגוזי לוז", "M10.2 hazelnuts pack"),
    (1438, "grocery", "contains", "טחינה 500", "M10.2 tahini jar"),
    (1439, "grocery", "contains", "דוחן", "M10.2 millet retail"),
    (1440, "grocery", "contains", "נקטר תפוח", "M10.2 nectar"),
    (1441, "grocery", "contains", "קטשופ אורגני", "M10.2 ketchup"),
    (1442, "grocery", "contains", "שוקולד עם שבבי", "M10.2 chocolate snack"),
]

_ALIASES: list[tuple[str, str]] = [
    ("פומלית 5 ק\"ג", "PRD051"),
    ("סל רגיל", "PRD026"),
    ("סלסלת כ- 2 ק\"ג תפוח אד", "PRD056"),
    ('תפוח עץ "גרני סמיט" יר', "PRD042"),
    ("זוקיני", "PRD007"),
    ("קולרבי", "PRD036"),
    ("צרור אזוב", "PRD066"),
    ("נבטי אלפלפא", "PRD033"),
    ("נבטים מיקס גדול", "PRD033"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for d, cat, mt, pat, notes in _SCOPE:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (:d, :cat, :mt, :pat, :notes, NULL, true)
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {"d": d, "cat": cat, "mt": mt, "pat": pat, "notes": notes},
        )
    for at, pcode in _ALIASES:
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
    for d, *_ in _SCOPE:
        conn.execute(text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"), {"d": d})
    for at, _ in _ALIASES:
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": at},
        )
