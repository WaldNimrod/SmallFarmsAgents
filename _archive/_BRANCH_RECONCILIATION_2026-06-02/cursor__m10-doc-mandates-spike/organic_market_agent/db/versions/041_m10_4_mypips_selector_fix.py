"""041: M10.4 — mypips wait_for selector (pips-card-content + attached state)."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "041"
down_revision = "040"
branch_labels = None
depends_on = None

_CODES = (
    "SRC041",
    "SRC042",
    "SRC053",
    "SRC055",
    "SRC060",
    "SRC061",
    "SRC062",
    "SRC069",
    "SRC070",
)

_DEFAULT_SELECTOR = {
    "wait_for": "div.pips-card-content",
    "wait_for_state": "attached",
    "post_load_delay_ms": 8000,
    "dismiss_ok_button_name": "אוקיי",
    "click_category_tabs": False,
}

_LARGE_CATALOG_SELECTOR = {
    "wait_for": "div.pips-card-content",
    "wait_for_state": "attached",
    "post_load_delay_ms": 8000,
    "dismiss_ok_button_name": "אוקיי",
    "click_category_tabs": True,
}


def upgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        sel = _LARGE_CATALOG_SELECTOR if code == "SRC053" else _DEFAULT_SELECTOR
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET selector_profile = CAST(:sp AS jsonb), updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code AND fp.platform_family = 'mypips'
                """
            ),
            {"code": code, "sp": json.dumps(sel)},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        sel = {
            "wait_for": "h6",
            "post_load_delay_ms": 8000,
            "dismiss_ok_button_name": "אוקיי",
            "click_category_tabs": code == "SRC053",
        }
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET selector_profile = CAST(:sp AS jsonb), updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code
                """
            ),
            {"code": code, "sp": json.dumps(sel)},
        )
