"""047: M10.4 QA remediation — bump mypips cache-buster (force refetch + re-parse after collector fix)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "047"
down_revision = "046"
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
                SET entry_url = REPLACE(fp.entry_url, '?_oma=m10_4', '?_oma=m10_4b'),
                    updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id AND s.code = :code AND fp.platform_family = 'mypips'
                  AND fp.entry_url LIKE '%?_oma=m10_4%'
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
            SET entry_url = REPLACE(entry_url, '?_oma=m10_4b', '?_oma=m10_4'),
                updated_at = NOW()
            WHERE platform_family = 'mypips'
              AND entry_url LIKE '%?_oma=m10_4b%'
            """
        )
    )
