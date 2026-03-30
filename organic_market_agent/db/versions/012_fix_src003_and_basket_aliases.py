"""012: Fix SRC003 selector profile, deactivate SRC007, add basket product aliases.

SRC003 (ח'ביזה / chubeza.com): HTML inspection shows the subscription form uses
.box_card rows with h3 titles and .product_price spans. Migration 007's generic
selector did not match this structure, yielding 0 items. Correct selectors:
  product_row → .box_card
  name        → h3
  price       → .product_price

SRC007 (סלסילה): The stored HTML is a JS-rendered product modal — #product_title
and #product_price are empty placeholders in the static snapshot. Static HTTP
scraping cannot recover useful data. Deactivated.

Basket aliases: SRC003 produces "ארגז ירקות גדול" and "ארגז ירקות קטן". The
existing aliases "ארגז גדול" / "ארגז קטן" are not substrings of those names because
"ירקות" sits between the two words. Three new global aliases bridge this gap.
"""

import json
import re as _re

import sqlalchemy as sa
from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None

_WS = _re.compile(r"\s+")


def _norm(t: str) -> str:
    return _WS.sub(" ", t.strip().lower())


SRC003_SELECTOR = {
    "product_row": ".box_card",
    "name": "h3",
    "price": ".product_price",
    "unit": None,
    "quantity": None,
}

NEW_ALIASES = [
    ("ארגז ירקות גדול",   "PRD027"),  # סל ירקות גדול
    ("ארגז ירקות קטן",    "PRD025"),  # סל ירקות קטן
    ("ארגז ירקות בינוני", "PRD026"),  # סל ירקות בינוני (preventive)
]


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Fix SRC003 selector profile
    conn.execute(
        sa.text(
            "UPDATE source_fetch_profiles "
            "SET selector_profile = CAST(:sel AS jsonb) "
            "WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC003')"
        ),
        {"sel": json.dumps(SRC003_SELECTOR)},
    )

    # 2. Deactivate SRC007 (JS-rendered modal — cannot be scraped statically)
    for table_sql in (
        "UPDATE sources SET is_active = false WHERE code = 'SRC007'",
        "UPDATE source_fetch_profiles SET is_active = false "
        "WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC007')",
    ):
        conn.execute(sa.text(table_sql))

    # 3. Add basket product aliases (global, source_id = NULL)
    for alias_text, product_code in NEW_ALIASES:
        alias_norm = _norm(alias_text)
        conn.execute(
            sa.text(
                """
                INSERT INTO product_aliases (
                    product_id, source_id, alias_text, alias_text_normalized, is_active
                )
                SELECT p.id, NULL, :alias_text, :alias_norm, true
                FROM products p
                WHERE p.code = :product_code
                ON CONFLICT (alias_text_normalized, source_id) DO NOTHING
                """
            ),
            {
                "alias_text": alias_text,
                "alias_norm": alias_norm,
                "product_code": product_code,
            },
        )


def downgrade() -> None:
    conn = op.get_bind()

    # Restore SRC007 active state
    for table_sql in (
        "UPDATE sources SET is_active = true WHERE code = 'SRC007'",
        "UPDATE source_fetch_profiles SET is_active = true "
        "WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC007')",
    ):
        conn.execute(sa.text(table_sql))

    # Remove basket aliases added by this migration
    for alias_text, _prd in NEW_ALIASES:
        conn.execute(
            sa.text(
                "DELETE FROM product_aliases "
                "WHERE alias_text_normalized = :norm AND source_id IS NULL"
            ),
            {"norm": _norm(alias_text)},
        )

    # Restore old generic selector for SRC003 (migration 010 value)
    old_sel = json.dumps(
        {
            "product_row": "div.prod_row",
            "name": ".form-prod-title",
            "price": ".price",
            "unit": None,
            "quantity": None,
        }
    )
    conn.execute(
        sa.text(
            "UPDATE source_fetch_profiles "
            "SET selector_profile = CAST(:sel AS jsonb) "
            "WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC003')"
        ),
        {"sel": old_sel},
    )
