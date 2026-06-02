"""049: M10.4 — SRC042 use ``load`` navigation (stronger than domcontentloaded; avoids networkidle hang)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "049"
down_revision = "048"
branch_labels = None
depends_on = None

_PATCH = text(
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


def upgrade() -> None:
    op.get_bind().execute(_PATCH)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile - 'goto_wait_until',
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )
