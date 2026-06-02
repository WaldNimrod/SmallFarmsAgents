"""057: M10.4 R3 — currency poll + welcome CTAs for shell-prone mypips; cache-bust m10_4e."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "057"
down_revision = "056"
branch_labels = None
depends_on = None

# Long poll + scroll helps Firestore-hydrated catalogs after wait_for timeout (T03).
_CURRENCY_POLL_MS = 120000

# SRC042: open welcome uses יאללה ממשיכים; closed overlay may use אוקיי.
_SRC042_EXTRA = {
    "extra_welcome_cta_names": ["יאללה ממשיכים!", "אוקיי"],
    "currency_poll_timeout_ms": _CURRENCY_POLL_MS,
    "post_load_delay_ms": 22000,
}

_SHELL_OTHERS = {
    "currency_poll_timeout_ms": _CURRENCY_POLL_MS,
    "post_load_delay_ms": 22000,
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
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        ),
        {"patch": json.dumps(_SRC042_EXTRA)},
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile || CAST(:patch AS jsonb),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        ),
        {"patch": json.dumps(_SHELL_OTHERS)},
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(
                  REPLACE(
                    REPLACE(fp.entry_url, '?_oma=m10_4b', '?_oma=m10_4e'),
                    '?_oma=m10_4c', '?_oma=m10_4e'),
                  '?_oma=m10_4d', '?_oma=m10_4e'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%_oma=m10_4%'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4e', '?_oma=m10_4d'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4e%'
            """
        )
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4e', '?_oma=m10_4d'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4e%'
            """
        )
    )
