"""042: M10.4 — enable tab-merge catalog collection for all 9 priority mypips sources."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "042"
down_revision = "041"
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


def _profile(click_tabs: bool) -> dict:
    return {
        "wait_for": "div.pips-card-content",
        "wait_for_state": "attached",
        "post_load_delay_ms": 8000,
        "dismiss_ok_button_name": "אוקיי",
        "click_category_tabs": click_tabs,
    }


def upgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET selector_profile = CAST(:sp AS jsonb), updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code AND fp.platform_family = 'mypips'
                """
            ),
            {"code": code, "sp": json.dumps(_profile(True))},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET selector_profile = CAST(:sp AS jsonb), updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code AND fp.platform_family = 'mypips'
                """
            ),
            {"code": code, "sp": json.dumps(_profile(code == "SRC053"))},
        )
