"""011: Add missing core-vegetable aliases discovered via SRC002 product-name simulation.

Root cause: several common product name forms used by EasyFarm suppliers do not match
any existing alias because the current aliases were too specific (e.g. 'מלפפון שדה'
is not a substring of 'מלפפון אורגני'; 'חסה ראש' is not a substring of 'חסה ערבית').

Simulation of SRC002's 131 product names against the full alias table showed 14 distinct
products resolved. Adding these 6 short-form aliases raises the expected yield to 20.
"""

import sqlalchemy as sa
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None

# (alias_text, product_code, notes)
# All are global aliases (source_id = NULL)
NEW_ALIASES = [
    ("גזר",       "PRD013", "plain 'גזר' catches 'גזר אורגני' — shorter than 'גזר שדה'/'גזר ק\"ג'"),
    ("מלפפון",    "PRD005", "plain 'מלפפון' catches 'מלפפון אורגני' — 'מלפפון שדה' was too specific"),
    ("חציל",      "PRD006", "plain 'חציל' catches 'חציל אורגני' — 'חציל בלדי' was too specific"),
    ("חסה",       "PRD008", "plain 'חסה' catches 'חסה ערבית' — specific variety aliases missed it"),
    ("פלפל אדום", "PRD003", "catches 'פלפל אדום אורגני' — 'פלפל אדום בייבי' was too specific"),
    ("רוקט",      "PRD010", "catches 'רוקט אורגני' — 'רוקטה' is a different spelling, not a substring"),
]

# Normalise: lowercase, collapse whitespace (mirrors alias_resolver._normalize_text)
import re as _re
_WS = _re.compile(r"\s+")


def _norm(t: str) -> str:
    return _WS.sub(" ", t.strip().lower())


def upgrade() -> None:
    conn = op.get_bind()
    for alias_text, product_code, _note in NEW_ALIASES:
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
            {"alias_text": alias_text, "alias_norm": alias_norm, "product_code": product_code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for alias_text, _product_code, _note in NEW_ALIASES:
        alias_norm = _norm(alias_text)
        conn.execute(
            sa.text(
                "DELETE FROM product_aliases "
                "WHERE alias_text_normalized = :alias_norm AND source_id IS NULL"
            ),
            {"alias_norm": alias_norm},
        )
