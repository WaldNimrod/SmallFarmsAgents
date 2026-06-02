"""064: M13-PRE — SRC034 cache-bust entry_url (duplicate checksum skips left latest run with 0 rows)."""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "064"
down_revision = "063"
branch_labels = None
depends_on = None

_BASE = "https://www.meshekorgani.co.il/basket"
_BUST = f"{_BASE}?_oma=m13_pre"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = :bust,
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC034'
              AND fp.fetch_mode = 'html_page'
            """
        ),
        {"bust": _BUST},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET entry_url = :base,
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code = 'SRC034'
              AND fp.fetch_mode = 'html_page'
            """
        ),
        {"base": _BASE},
    )
