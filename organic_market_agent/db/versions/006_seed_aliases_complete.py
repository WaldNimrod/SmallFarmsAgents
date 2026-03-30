"""006: Complete product alias coverage — 13 products missing from revision 005."""

from alembic import op
from sqlalchemy import text

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def _norm(s: str) -> str:
    return s.strip().lower()


# Products without aliases after revision 005:
# PRD012 פטרוזיליה, PRD014 סלק, PRD015 לפת, PRD016 צנון,
# PRD018 בצל ירוק, PRD019 שום, PRD020 כרישה,
# PRD021 כרוב לבן, PRD022 כרובית, PRD023 ברוקולי,
# PRD024 שעועית ירוקה, PRD027 סל גדול, PRD028 סל משפחתי
ALIASES = [
    ("PRD012", "פטרוזיליה", "1.0"),
    ("PRD012", "פטרוזיליה צרור", "1.0"),
    ("PRD012", "parsley", "0.9"),
    ("PRD014", "סלק", "1.0"),
    ("PRD014", 'סלק ק"ג', "0.95"),
    ("PRD014", "beet", "0.9"),
    ("PRD014", "beetroot", "0.9"),
    ("PRD015", "לפת", "1.0"),
    ("PRD015", 'לפת ק"ג', "0.95"),
    ("PRD015", "turnip", "0.9"),
    ("PRD016", "צנון", "1.0"),
    ("PRD016", "צנון צרור", "1.0"),
    ("PRD016", "radish", "0.9"),
    ("PRD018", "בצל ירוק", "1.0"),
    ("PRD018", "בצל ירוק צרור", "1.0"),
    ("PRD018", "spring onion", "0.9"),
    ("PRD018", "scallion", "0.9"),
    ("PRD019", "שום", "1.0"),
    ("PRD019", 'שום ק"ג', "0.95"),
    ("PRD019", "שום שן", "0.85"),
    ("PRD019", "garlic", "0.9"),
    ("PRD020", "כרישה", "1.0"),
    ("PRD020", "כרישה ליחידה", "0.95"),
    ("PRD020", "leek", "0.9"),
    ("PRD021", "כרוב לבן", "1.0"),
    ("PRD021", "כרוב", "0.85"),
    ("PRD021", "white cabbage", "0.9"),
    ("PRD021", "cabbage", "0.85"),
    ("PRD022", "כרובית", "1.0"),
    ("PRD022", "כרובית ליחידה", "0.95"),
    ("PRD022", "cauliflower", "0.9"),
    ("PRD023", "ברוקולי", "1.0"),
    ("PRD023", "ברוקולי ליחידה", "0.95"),
    ("PRD023", "broccoli", "0.9"),
    ("PRD024", "שעועית ירוקה", "1.0"),
    ("PRD024", "שעועית", "0.85"),
    ("PRD024", "green beans", "0.9"),
    ("PRD024", 'שעועית ק"ג', "0.95"),
    ("PRD027", "סל גדול", "1.0"),
    ("PRD027", "סל ירקות גדול", "1.0"),
    ("PRD027", "ארגז גדול", "0.85"),
    ("PRD028", "סל משפחתי", "1.0"),
    ("PRD028", "סל ירקות משפחתי", "1.0"),
    ("PRD028", "ארגז משפחתי", "0.85"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for pcode, alias_text, conf in ALIASES:
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


def downgrade() -> None:
    conn = op.get_bind()
    codes = [row[0] for row in ALIASES]
    for pcode in set(codes):
        conn.execute(
            text(
                "DELETE FROM product_aliases WHERE product_id = "
                "(SELECT id FROM products WHERE code = :pcode) "
                "AND source_id IS NULL"
            ),
            {"pcode": pcode},
        )
