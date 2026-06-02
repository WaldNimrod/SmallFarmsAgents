"""065: M13-PRE — bump mypips ?_oma= for SRC042/055/062/069 (force fresh raw; duplicate checksum skips)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "065"
down_revision = "064"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4e', '?_oma=m13_pre'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4e%'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m13_pre', '?_oma=m10_4e'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        )
    )
