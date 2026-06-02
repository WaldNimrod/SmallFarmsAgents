"""052: M10.4 R2 — Playwright context (UA, locale, TZ, headers) for shell-prone mypips stores."""

from __future__ import annotations

import json

from alembic import op
from sqlalchemy import text

revision = "052"
down_revision = "051"
branch_labels = None
depends_on = None

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
_HEADERS = {"Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7"}

# Disable tab-merge for these handles: merged path was yielding empty card HTML; full page + UA is primary bet.
_BASE = {
    "user_agent": _UA,
    "locale": "he-IL",
    "timezone_id": "Asia/Jerusalem",
    "extra_http_headers": _HEADERS,
    "click_category_tabs": False,
    "goto_wait_until": "load",
    "post_load_delay_ms": 14000,
}


def _profile(code: str) -> dict:
    p = dict(_BASE)
    if code == "SRC042":
        p["post_load_delay_ms"] = 20000
        p["playwright_timeout_ms"] = 75000
    else:
        p["playwright_timeout_ms"] = 60000
    return p


_CODES = ("SRC042", "SRC055", "SRC062", "SRC069")


def upgrade() -> None:
    conn = op.get_bind()
    for code in _CODES:
        conn.execute(
            text(
                """
                UPDATE source_fetch_profiles fp
                SET selector_profile = fp.selector_profile || CAST(:patch AS jsonb),
                    updated_at = NOW()
                FROM sources s
                WHERE fp.source_id = s.id
                  AND s.code = :code
                  AND fp.platform_family = 'mypips'
                """
            ),
            {"code": code, "patch": json.dumps(_profile(code))},
        )


def downgrade() -> None:
    """Lossy: re-enable tab-merge for the four codes; remove R2 keys manually if needed."""
    conn = op.get_bind()
    conn.execute(
        text(
            """
            UPDATE source_fetch_profiles fp
            SET selector_profile = fp.selector_profile || '{"click_category_tabs": true}'::jsonb,
                updated_at = NOW()
            FROM sources s
            WHERE fp.source_id = s.id
              AND s.code IN ('SRC042', 'SRC055', 'SRC062', 'SRC069')
              AND fp.platform_family = 'mypips'
            """
        )
    )
