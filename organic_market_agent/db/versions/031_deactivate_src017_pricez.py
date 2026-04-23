"""031: Deactivate SRC017 (Pricez) — scheduled fetches return 403; pause until resolved."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None

SRC017 = "SRC017"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE sources SET is_active = false WHERE code = :code"),
        {"code": SRC017},
    )
    conn.execute(
        sa.text(
            "UPDATE source_fetch_profiles SET is_active = false "
            "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
        ),
        {"code": SRC017},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE sources SET is_active = true WHERE code = :code"),
        {"code": SRC017},
    )
    conn.execute(
        sa.text(
            "UPDATE source_fetch_profiles SET is_active = true "
            "WHERE source_id = (SELECT id FROM sources WHERE code = :code)"
        ),
        {"code": SRC017},
    )
