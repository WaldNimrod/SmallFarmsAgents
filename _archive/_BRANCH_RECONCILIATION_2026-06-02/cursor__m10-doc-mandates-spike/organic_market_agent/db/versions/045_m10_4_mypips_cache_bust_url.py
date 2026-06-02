"""045: M10.4 — append cache-buster query on mypips product URLs (fresh Playwright fetch)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "045"
down_revision = "044"
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


def upgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET entry_url = CASE
                    WHEN fp.entry_url LIKE '%_oma=%' THEN fp.entry_url
                    ELSE fp.entry_url || '?_oma=m10_4'
                END,
                updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code AND fp.platform_family = 'mypips'
                """
            ),
            {"code": code},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles
            SET entry_url = REPLACE(entry_url, '?_oma=m10_4', ''),
                updated_at = NOW()
            WHERE platform_family = 'mypips'
              AND entry_url LIKE '%?_oma=m10_4'
            """
        )
    )
