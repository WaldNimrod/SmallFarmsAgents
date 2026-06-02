"""032: M10.2 dictionary batch — scope-skip rules + selective aliases (Team 100 mandate).

Idempotent: ON CONFLICT / NOT EXISTS guards.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None

# (display_order, category_code, match_type, pattern, notes_en)
_SCOPE_RULES: list[tuple[int, str, str, str, str]] = [
    (1290, "donation", "contains", "תרומת ירקות", "M10.2 donation line"),
    (1291, "donation", "contains", "תרומה למנזר", "M10.2 donation"),
    (1292, "donation", "contains", "תרומה למשפחות", "M10.2 donation"),
    (1293, "donation", "contains", "תרומת ירקות לאתנחתא", "M10.2 donation"),
    (1294, "donation", "contains", "תרומה לאתנחתא", "M10.2 donation"),
    (1295, "grocery", "contains", "משחת שיניים", "M10.2 toothpaste"),
    (1296, "grocery", "contains", "מברשת שיניים", "M10.2 toothbrush"),
    (1297, "grocery", "contains", "דגני בוקר", "M10.2 cereal"),
    (1298, "grocery", "contains", "אטריות קונג", "M10.2 konjac noodles"),
    (1299, "grocery", "contains", "מבשם אוויר", "M10.2 air freshener"),
    (1300, "grocery", "contains", "תחבושות", "M10.2 pads"),
    (1301, "grocery", "contains", "מעדן שיבולת", "M10.2 oat dessert"),
    (1302, "grocery", "contains", "מארז 5 מברשות", "M10.2 toothbrush pack"),
    (1303, "grocery", "contains", "מארז חטיפי תמר", "M10.2 date snacks pack"),
    (1304, "grocery", "contains", "Botany-", "M10.2 hair care brand"),
    (1305, "grocery", "contains", "סירופ אגבה", "M10.2 agave syrup"),
    (1306, "grocery", "contains", "משקה שיבולת", "M10.2 oat drink"),
    (1307, "grocery", "contains", "ecolove", "M10.2 brand"),
    (1308, "grocery", "contains", "cotton -", "M10.2 cotton brand"),
    (1309, "cleaning", "contains", "ecover", "M10.2 cleaning brand"),
    (1310, "cleaning", "contains", "ecofriend", "M10.2 laundry"),
    (1311, "grocery", "contains", "אבקת מרק", "M10.2 soup powder"),
    (1312, "grocery", "contains", "סוכריות טופי", "M10.2 candy"),
    (1313, "grocery", "contains", "טופי על בסיס", "M10.2 candy base"),
    (1314, "grocery", "contains", "דובשניות כוסמין", "M10.2 pastry"),
    (1315, "grocery", "contains", "ארוחת פירות שיבולת", "M10.2 oat meal"),
    (1316, "grocery", "contains", "אריזת חיסכון תחבושות", "M10.2 pads pack"),
    (1317, "grocery", "contains", "מסיכת שיער", "M10.2 hair mask"),
    (1318, "grocery", "contains", "מרכך לשיער", "M10.2 conditioner"),
    (1319, "grocery", "contains", "טמפונים", "M10.2 tampons"),
    (1320, "grocery", "contains", "קמבוצ", "M10.2 kombucha"),
    (1321, "grocery", "contains", "רוטב סויה", "M10.2 soy sauce"),
    (1322, "grocery", "contains", "תערובת אבקת חלבון", "M10.2 protein powder"),
    (1323, "grocery", "contains", "אבקת חלבון אפונה", "M10.2 pea protein"),
    (1324, "grocery", "contains", "חרדל דיז", "M10.2 mustard"),
    (1325, "grocery", "contains", "צ'אטני", "M10.2 chutney"),
    (1326, "grocery", "contains", "נקטר אפרסקים", "M10.2 nectar"),
    (1327, "grocery", "contains", "מיץ ענבים", "M10.2 grape juice"),
    (1328, "grocery", "contains", "רסק תפוחים", "M10.2 apple puree retail"),
    (1329, "grocery", "contains", "שמן קוקוס אורגני כתית", "M10.2 bottled coconut oil line"),
    (1330, "grocery", "contains", "שקדים קלופים", "M10.2 packaged almonds retail"),
    (1331, "grocery", "contains", "תבלין פפריקה", "M10.2 spice jar"),
    (1332, "grocery", "contains", "סמוזי תפוח", "M10.2 smoothie drink"),
    (1333, "grocery", "contains", "תה רויבוס", "M10.2 tea retail"),
    (1334, "other", "contains", "נבטי אלפלפא על מצע", "M10.2 sprout kit retail"),
    (1335, "grocery", "contains", "נבטים סינים", "M10.2 sprout product retail"),
    (1336, "grocery", "contains", "קרם קוקוס אורגני", "M10.2 coconut cream can"),
    (1337, "grocery", "contains", "סילאן אורגני", "M10.2 silan"),
    (1338, "grocery", "contains", "חמוציות מיובשות", "M10.2 dried cranberry retail"),
    (1339, "grocery", "contains", "טחינה טבעית גדולה", "M10.2 tahini jar"),
    (1340, "grocery", "contains", "נוזל כביסה טבעי", "M10.2 laundry liquid"),
    (1341, "dry_grocery", "contains", "קינואה לבנה", "M10.2 quinoa retail"),
    (1342, "grocery", "contains", "שמן 750 מ", "M10.2 bottled oil SKU"),
    (1343, "grocery", "contains", "שמן ליטר 2", "M10.2 oil bottle"),
    (1344, "grocery", "contains", "תמר מהג", "M10.2 date product line"),
    (1345, "grocery", "contains", "חומוס", "M10.2 packaged hummus retail"),
    (1346, "other", "contains", "סל ירוקים - לחצו", "M10.2 UI placeholder basket"),
    (1347, "grocery", "contains", "מיץ תפוחים", "M10.2 juice"),
    (1348, "grocery", "contains", "תירוש טבעי", "M10.2 molasses drink"),
    (1349, "grocery", "contains", "קוקוס תאילנדי לשתיה", "M10.2 coconut drink"),
    (1350, "dry_grocery", "contains", "אורז אדום אורגני", "M10.2 rice pack"),
    (1351, "dry_grocery", "contains", "קילו אורז", "M10.2 rice pack"),
    (1352, "dry_grocery", "contains", "ספגטי מקמח", "M10.2 pasta"),
    (1353, "grocery", "contains", "מרכך כביסה", "M10.2 fabric softener"),
    (1354, "grocery", "contains", "לחם אגוזים", "M10.2 bread"),
    (1355, "grocery", "contains", "חטיף קוקוס", "M10.2 snack"),
    (1356, "grocery", "contains", "ממרח תמרים", "M10.2 spread"),
    (1357, "grocery", "contains", "סמוצ'י קיווי", "M10.2 smoothie"),
    (1358, "grocery", "contains", "הולי נאטס", "M10.2 brand"),
    (1359, "dry_grocery", "contains", "פיסטוק קלוי", "M10.2 nuts retail"),
    (1360, "grocery", "contains", "חמאת שיאה", "M10.2 shea butter product"),
    (1361, "grocery", "contains", "חליטת שקט", "M10.2 tea blend"),
    (1362, "dry_grocery", "contains", "קשיו טבעי", "M10.2 cashew retail"),
    (1363, "grocery", "contains", "מי קוקוס אורגני", "M10.2 coconut water bottle"),
    (1364, "dry_grocery", "contains", "צימוק טבעי", "M10.2 raisins"),
    (1365, "grocery", "contains", "פטריות רעמת האריה", "M10.2 lions mane product"),
    (1366, "grocery", "contains", "פפריקה מתוכה", "M10.2 paprika spice line"),
    (1367, "grocery", "contains", "מיץ ענבים שדה", "M10.2 juice bottle"),
    (1368, "grocery", "contains", "פטריות אויסטר", "M10.2 oyster mushroom retail pack"),
    (1369, "grocery", "contains", "פטריות שמפיניון", "M10.2 mushroom retail pack"),
    (1370, "grocery", "contains", "פלפל פלרמו", "M10.2 pepper retail pack"),
    (1371, "other", "exact", "חומעה", "M10.2 SRC024 herb name variant"),
    (1372, "other", "exact", "זוטה", "M10.2 SRC023 pending catalog"),
    (1373, "other", "exact", "פול", "M10.2 SRC023 ambiguous"),
    (1374, "other", "exact", "לבנדר רפואי", "M10.2 herb retail line"),
    (1375, "other", "exact", "תירס מתוק", "M10.2 corn retail line"),
    (1376, "other", "prefix", "ריג'לה", "M10.2 herb retail"),
]

# (alias_text, product_code) — existing PRD codes only
_ALIAS_ROWS: list[tuple[str, str]] = [
    ("מגש ירקות העונה", "PRD026"),
    ("מגש פירות העונה", "PRD027"),
    ('תפוח עץ "גרני סמית" אורגני', "PRD042"),
    ("תפוח עץ ברייבורן אורגני", "PRD042"),
    ("תפוח עץ חרמון אורגני", "PRD042"),
    ("תפוח עץ גאלה אורגני", "PRD042"),
    ("תפוח עץ ''גאלה''", "PRD042"),
    ("עגבניית ליקופן", "PRD001"),
    ("אפונת גינה", "PRD043"),
    ("סלרי", "PRD050"),
    ("תפוח אדום יבוא", "PRD056"),
    ("תפוח ירוק יבוא", "PRD042"),
    ("נבטים סיניים אורגנים", "PRD033"),
    ("נבטי אלפלפא אורגנים", "PRD033"),
    ("מיקס פלפלים לבישול", "PRD003"),
    ("עלי מיקרו חרדל אדום", "PRD010"),
    ("מארז למון גראס אורגני", "PRD084"),
    ("נענע אורגנית מארז", "PRD073"),
    ("מיקס נבטים אורגנים", "PRD033"),
    ("עשב חיטה אורגני", "PRD083"),
    ("שמיר אורגני שקית", "PRD074"),
    ("עלי מיקרו בזיל אדום", "PRD063"),
    ("פלפל פלרמו אדום אורגני", "PRD003"),
    ("מיקס עלי בייבי אורגניים", "PRD008"),
    ("מיקס עלי מיקרו", "PRD010"),
    ("מיקס פלפל צהוב כתום אורגני", "PRD047"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for display_order, cat, mtype, pattern, notes in _SCOPE_RULES:
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

    for alias_text, pcode in _ALIAS_ROWS:
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
            {"at": alias_text, "at2": alias_text, "code": pcode},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for display_order, *_ in _SCOPE_RULES:
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"),
            {"d": display_order},
        )
    for alias_text, _ in _ALIAS_ROWS:
        conn.execute(
            text("DELETE FROM product_aliases WHERE alias_text = :t AND source_id IS NULL"),
            {"t": alias_text},
        )
