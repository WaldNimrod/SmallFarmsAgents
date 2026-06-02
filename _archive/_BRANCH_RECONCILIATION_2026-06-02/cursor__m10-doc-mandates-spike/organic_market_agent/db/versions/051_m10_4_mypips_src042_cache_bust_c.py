"""051: M10.4 — SRC042 cache-buster m10_4c (force new raw after identical shell checksum)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "051"
down_revision = "050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4b', '?_oma=m10_4c'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
              AND fp.entry_url LIKE '%?_oma=m10_4b%'
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4c', '?_oma=m10_4b'),
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )
