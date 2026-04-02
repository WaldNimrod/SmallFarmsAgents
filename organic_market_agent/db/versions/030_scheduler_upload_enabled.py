"""030: Add upload_enabled flag to scheduler_config (M7 Go-Live)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "030"
down_revision = "029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "scheduler_config",
        sa.Column(
            "upload_enabled",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("scheduler_config", "upload_enabled")
