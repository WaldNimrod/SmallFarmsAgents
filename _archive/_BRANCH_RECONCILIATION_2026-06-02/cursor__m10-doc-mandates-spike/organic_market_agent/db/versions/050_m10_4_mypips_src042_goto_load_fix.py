"""050: M10.4 — SRC042: replace networkidle with load (networkidle hung Playwright)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "050"
down_revision = "049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.get_bind().execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile || '{"goto_wait_until": "load"}'::jsonb,
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )


def downgrade() -> None:
    op.get_bind().execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile || '{"goto_wait_until": "networkidle"}'::jsonb,
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )
