"""Seed product_aliases from PRODUCT_CATALOG_V1 alias section (+ extras for coverage)."""

from alembic import op
from sqlalchemy import text

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# (product_code, alias_text, confidence)
ALIASES = [
    ("PRD001", "עגבניה", "1.0"),
    ("PRD001", "עגבניות", "1.0"),
    ("PRD001", "עגבנייה לק\"ג", "0.95"),
    ("PRD001", "tomatoes", "0.9"),
    ("PRD001", "עגבניה בשלה", "0.85"),
    ("PRD002", "עגבניות שרי", "1.0"),
    ("PRD002", "שרי", "0.85"),
    ("PRD002", "cherry tomatoes", "0.9"),
    ("PRD005", "מלפפונים", "1.0"),
    ("PRD005", "מלפפון חממה", "0.9"),
    ("PRD005", "מלפפון שדה", "0.9"),
    ("PRD005", "cucumber", "0.9"),
    ("PRD008", "חסה ראש", "1.0"),
    ("PRD008", "חסה איסברג", "0.85"),
    ("PRD008", "חסה חמאה", "0.85"),
    ("PRD008", "חסה לייחידה", "0.9"),
    ("PRD008", "lettuce", "0.9"),
    ("PRD013", "גזרים", "1.0"),
    ("PRD013", "גזר ק\"ג", "0.95"),
    ("PRD013", "carrot", "0.9"),
    ("PRD013", "גזר שדה", "0.9"),
    ("PRD017", "בצל", "0.9"),
    ("PRD017", "בצל לבן", "0.85"),
    ("PRD017", "בצל ק\"ג", "0.95"),
    ("PRD017", "onion", "0.9"),
    ("PRD011", "כוסברה", "1.0"),
    ("PRD011", "כוסברה צרור", "1.0"),
    ("PRD011", "cilantro", "0.9"),
    ("PRD025", "סל קטן", "1.0"),
    ("PRD025", "סל אישי", "0.9"),
    ("PRD025", "ארגז קטן", "0.85"),
    ("PRD026", "סל בינוני", "1.0"),
    ("PRD026", "סל זוגי", "0.9"),
    ("PRD026", "ארגז בינוני", "0.85"),
    ("PRD029", "ארגז שבועי", "1.0"),
    ("PRD029", "מנוי שבועי", "0.9"),
    ("PRD029", "סל מנוי", "0.85"),
    ("PRD029", "קופסת ירקות", "0.8"),
    # extras so >=10 products with aliases (already satisfied); diversify
    ("PRD003", "פלפל אדום בייבי", "0.85"),
    ("PRD004", "פלפל חריף ירוק", "0.85"),
    ("PRD006", "חציל בלדי", "0.9"),
    ("PRD007", "קישואים", "1.0"),
    ("PRD009", "תרד", "0.9"),
    ("PRD010", "רוקטה", "0.95"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, conf in ALIASES:
        n = _norm(alias_text)
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, source_id, confidence, is_active
                )
                SELECT id, :alias_text, :alias_norm, NULL, CAST(:conf AS NUMERIC(3,2)), true
                FROM products WHERE code = :pcode
                """
            ),
            {"alias_text": alias_text, "alias_norm": n, "conf": conf, "pcode": pcode},
        )


def downgrade() -> None:
    op.execute("DELETE FROM product_aliases")
