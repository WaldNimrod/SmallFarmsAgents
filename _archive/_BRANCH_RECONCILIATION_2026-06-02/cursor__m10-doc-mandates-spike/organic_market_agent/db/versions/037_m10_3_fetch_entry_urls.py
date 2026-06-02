"""037: M10.3 — point SRC026/SRC027 fetch URLs at catalog pages with extractable grids."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None

_BENSFARM_CATEGORY = (
    "https://www.bensfarm.co.il/category/0/"
    "%D7%9E%D7%91%D7%A6%D7%A2%D7%99%D7%9D"
)
_ERANORGANI_TOMATO = "https://www.eranorgani.co.il/%D7%9E%D7%95%D7%A6%D7%A8%D7%99-%D7%A2%D7%92%D7%91%D7%A0%D7%99%D7%94"

_ERAN_SELECTOR = {
    "product_card": "div.product-box",
    "name": "h3, h4, .product-title",
    "price": ".price-box",
}


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = :u, updated_at = NOW()
            WHERE source_id = 26 AND is_active = true
            """
        ),
        {"u": _BENSFARM_CATEGORY},
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = :u,
                selector_profile = CAST(:sp AS jsonb),
                updated_at = NOW()
            WHERE source_id = 27 AND is_active = true
            """
        ),
        {"u": _ERANORGANI_TOMATO, "sp": json.dumps(_ERAN_SELECTOR)},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = 'https://www.bensfarm.co.il/',
                updated_at = NOW()
            WHERE source_id = 26 AND is_active = true
            """
        )
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = 'https://www.eranorgani.co.il/',
                selector_profile = '{}'::jsonb,
                updated_at = NOW()
            WHERE source_id = 27 AND is_active = true
            """
        )
    )
