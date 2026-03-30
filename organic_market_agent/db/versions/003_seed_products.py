"""Seed 29 products (PRD001–PRD029)."""

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # default_measurement_unit_id resolved via subquery on measurement_units.code
    rows = [
        ("PRD001", "עגבנייה", "kg", "fruiting_vegetables", "כל השנה"),
        ("PRD002", "עגבנייה שרי", "kg", "fruiting_vegetables", "כל השנה"),
        ("PRD003", "פלפל אדום", "kg", "fruiting_vegetables", "אביב-סתיו"),
        ("PRD004", "פלפל ירוק", "kg", "fruiting_vegetables", "אביב-סתיו"),
        ("PRD005", "מלפפון", "kg", "fruiting_vegetables", "אביב-קיץ"),
        ("PRD006", "חציל", "kg", "fruiting_vegetables", "קיץ-סתיו"),
        ("PRD007", "קישוא", "kg", "fruiting_vegetables", "אביב-קיץ"),
        ("PRD008", "חסה", "unit", "leafy_greens", "חורף-אביב"),
        ("PRD009", "עלי תרד", "bunch", "leafy_greens", "חורף"),
        ("PRD010", "רוקט", "bunch", "leafy_greens", "חורף-אביב"),
        ("PRD011", "כוסברה", "bunch", "leafy_greens", "כל השנה"),
        ("PRD012", "פטרוזיליה", "bunch", "leafy_greens", "כל השנה"),
        ("PRD013", "גזר", "kg", "root_vegetables", "כל השנה"),
        ("PRD014", "סלק", "kg", "root_vegetables", "חורף-אביב"),
        ("PRD015", "לפת", "kg", "root_vegetables", "חורף"),
        ("PRD016", "צנון", "bunch", "root_vegetables", "חורף-אביב"),
        ("PRD017", "בצל יבש", "kg", "alliums", "כל השנה"),
        ("PRD018", "בצל ירוק", "bunch", "alliums", "חורף-אביב"),
        ("PRD019", "שום", "kg", "alliums", "אביב-קיץ"),
        ("PRD020", "כרישה", "unit", "alliums", "חורף"),
        ("PRD021", "כרוב לבן", "unit", "brassicas", "חורף"),
        ("PRD022", "כרובית", "unit", "brassicas", "חורף"),
        ("PRD023", "ברוקולי", "unit", "brassicas", "חורף"),
        ("PRD024", "שעועית ירוקה", "kg", "legumes_fresh", "אביב-קיץ"),
        ("PRD025", "סל ירקות קטן", "basket_small", "baskets", "כל השנה"),
        ("PRD026", "סל ירקות בינוני", "basket_medium", "baskets", "כל השנה"),
        ("PRD027", "סל ירקות גדול", "basket_large", "baskets", "כל השנה"),
        ("PRD028", "סל ירקות משפחתי", "basket_family", "baskets", "כל השנה"),
        ("PRD029", "ארגז CSA שבועי", "basket_medium", "baskets", "כל השנה"),
    ]
    for i, (code, name_he, unit_code, category, season) in enumerate(rows):
        op.execute(
            f"""
            INSERT INTO products (
                code, canonical_name_he, category, default_measurement_unit_id,
                is_organic_required, is_basket_product, seasonality_notes, display_order
            )
            SELECT
                '{code}', '{name_he}', '{category}', mu.id,
                true, {str(category == 'baskets').lower()}, '{season}', {i + 1}
            FROM measurement_units mu WHERE mu.code = '{unit_code}'
            """
        )


def downgrade() -> None:
    op.execute("DELETE FROM products")
