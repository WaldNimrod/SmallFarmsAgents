"""048: M10.4 QA remediation — SRC042 (brodavkameshek) slower Firestore / variant DOM."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "048"
down_revision = "047"
branch_labels = None
depends_on = None

# Longer wait + timeout so catalog can render; parser has price-anchor fallback if cards differ.
_PATCH = text(
    """
    UPDATE source_fetch_profiles fp
    SET selector_profile = fp.selector_profile
        || '{"post_load_delay_ms": 16000, "playwright_timeout_ms": 60000}'::jsonb,
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
            SET selector_profile = fp.selector_profile
                - 'post_load_delay_ms'
                - 'playwright_timeout_ms',
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC042'
              AND fp.platform_family = 'mypips'
            """
        )
    )
