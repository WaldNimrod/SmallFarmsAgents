"""066: CSA expansion — shekel-line parser template source (SRC075) + forward-looking basket aliases."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "066"
down_revision = "065"
branch_labels = None
depends_on = None

_SEL = {"csa_site": "shekel_line_baskets", "shekel_require_organic": True}

# Inactive placeholder: operator replaces entry_url with a validated distinct farm before go-live.
_PLACEHOLDER_ENTRY = "https://www.meshekorgani.co.il/basket?_oma=csa_tpl=066"

_GLOBAL_ALIASES: list[tuple[str, str]] = [
    ("סל ירקות אורגני שבועי", "PRD025"),
    ("סל משפחתי אורגני", "PRD027"),
    ("ארגז ירקות שבועי אורגני", "PRD025"),
]


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO sources (
                code, name, base_url, source_group, market_scope, sales_channel,
                status, priority, legal_review_required, is_active, notes, source_tier,
                display_bucket
            ) VALUES (
                'SRC075',
                'CSA template (shekel-line)',
                'https://www.meshekorgani.co.il/basket',
                'basket_csa',
                'community',
                'csa_basket',
                'candidate',
                5,
                false,
                false,
                'Replace entry_url/base_url with a validated distinct organic farm before activation; duplicate Meshek Organi URL is intentional inactive placeholder only (066).',
                'basket',
                'grower'
            )
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO source_fetch_profiles (
                source_id, platform_family, fetch_mode, entry_url, http_method,
                is_active, selector_profile, timeout_seconds
            )
            SELECT s.id, NULL, 'html_page', :entry, 'GET', false, CAST(:sp AS jsonb), 45
            FROM sources s WHERE s.code = 'SRC075'
            """
        ),
        {"entry": _PLACEHOLDER_ENTRY, "sp": json.dumps(_SEL)},
    )
    conn.execute(
        text(
            """
            INSERT INTO normalizer_profiles (source_id, normalizer_type, version, is_active, notes)
            SELECT s.id, 'csa_basket', '1.0', true, '066 shekel_line_baskets'
            FROM sources s WHERE s.code = 'SRC075'
            """
        )
    )

    for alias_text, pcode in _GLOBAL_ALIASES:
        conn.execute(
            text(
                """
                INSERT INTO product_aliases (
                    product_id, alias_text, alias_text_normalized, confidence, is_active, source_id
                )
                SELECT p.id, :at,
                  lower(regexp_replace(trim(:at2), '[[:space:]]+', ' ', 'g')),
                  0.92, true, NULL
                FROM products p
                WHERE p.code = :pcode
                  AND NOT EXISTS (
                    SELECT 1 FROM product_aliases pa
                    WHERE pa.alias_text_normalized =
                      lower(regexp_replace(trim(:at3), '[[:space:]]+', ' ', 'g'))
                      AND pa.source_id IS NULL
                  )
                """
            ),
            {"at": alias_text, "at2": alias_text, "at3": alias_text, "pcode": pcode},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for alias_text, _ in _GLOBAL_ALIASES:
        conn.execute(
            text(
                """
                DELETE FROM product_aliases
                WHERE source_id IS NULL AND alias_text = :at
                """
            ),
            {"at": alias_text},
        )
    conn.execute(
        text(
            """
            DELETE FROM normalizer_profiles
            WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC075')
            """
        )
    )
    conn.execute(
        text(
            """
            DELETE FROM source_fetch_profiles
            WHERE source_id = (SELECT id FROM sources WHERE code = 'SRC075')
            """
        )
    )
    conn.execute(text("DELETE FROM sources WHERE code = 'SRC075'"))
