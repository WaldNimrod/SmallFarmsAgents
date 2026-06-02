"""060: M13-PRE / M10.4 — shell-prone mypips stores: relax wait_for + scroll nudges."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "060"
down_revision = "059"
branch_labels = None
depends_on = None

_PATCH = {
    "wait_for": "body",
    "wait_for_state": "attached",
    "headless_scroll_passes": 8,
    "headless_scroll_pause_ms": 2000,
}


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile || CAST(:patch AS jsonb),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        ),
        {"patch": json.dumps(_PATCH)},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile::jsonb
                - 'wait_for'
                - 'wait_for_state'
                - 'headless_scroll_passes'
                - 'headless_scroll_pause_ms',
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        )
    )
