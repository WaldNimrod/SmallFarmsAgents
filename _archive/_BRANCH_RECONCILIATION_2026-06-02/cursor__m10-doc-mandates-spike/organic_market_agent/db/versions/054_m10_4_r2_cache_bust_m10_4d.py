"""054: M10.4 R2 — cache-buster m10_4d for four shell-prone sources (fresh fetch after profile change)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "054"
down_revision = "053"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4b', '?_oma=m10_4d'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4b%'
            """
        )
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4c', '?_oma=m10_4d'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4c%'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4d', '?_oma=m10_4b'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        )
    )
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4d', '?_oma=m10_4c'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )
