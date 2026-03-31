"""026: Seed approved catalog_scope_skip_rules (Nimrod sign-off 2026-03-31).

Corrections vs draft: soap (סבון) → category cleaning; tea/infusion (חליט…) → dry_grocery.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None

# display_order, category_code, match_type, pattern, notes_en
RULE_ROWS: list[tuple[int, str, str, str, str]] = [
    (1, "donation", "prefix", "תרומת ירקות", "Donation vegetable lines; outside V1 price index"),
    (2, "donation", "prefix", "תרומה", "Donations to monastery / families; outside V1"),
    (3, "cleaning", "contains", "מרכך כביסה", "Laundry softener; cleaning / non-produce"),
    (4, "dry_grocery", "contains", "אורז", "Packaged rice on mixed retail grids"),
    (5, "dry_grocery", "contains", "ספגטי", "Pasta"),
    (6, "dry_grocery", "contains", "פיסטוק", "Nuts"),
    (7, "dry_grocery", "contains", "קשיו", "Nuts"),
    (8, "dry_grocery", "contains", "צימוק", "Dried fruit"),
    (9, "dry_grocery", "prefix", "מי קוקוס", "Coconut water beverage"),
    (10, "dry_grocery", "contains", "חמאת שיאה", "Packaged spread"),
    (11, "dry_grocery", "contains", "לחם", "Bread"),
    (12, "cleaning", "contains", "סבון", "Soap / cleaning products (Nimrod: cleaning)"),
    (13, "dry_grocery", "contains", "חליט", "Tea / infusion product lines (Nimrod: dry_grocery)"),
]


def upgrade() -> None:
    conn = op.get_bind()
    for display_order, category, mtype, pattern, notes in RULE_ROWS:
        conn.execute(
            text(
                """
                INSERT INTO catalog_scope_skip_rules (
                    display_order, category_code, match_type, pattern, notes,
                    future_product_code, is_active
                ) VALUES (
                    :display_order, :category_code, :match_type, :pattern, :notes,
                    NULL, true
                )
                ON CONFLICT (display_order) DO NOTHING
                """
            ),
            {
                "display_order": display_order,
                "category_code": category,
                "match_type": mtype,
                "pattern": pattern,
                "notes": notes,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()
    for display_order, _c, _m, _p, _n in reversed(RULE_ROWS):
        conn.execute(
            text("DELETE FROM catalog_scope_skip_rules WHERE display_order = :d"),
            {"d": display_order},
        )
