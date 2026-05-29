"""057: WP-UI-patch02 Phase 1 — add icon_url column to crops table.

Adds a nullable VARCHAR(255) column `icon_url` to `crops` to store
per-crop watercolor art URLs (Phase 1 of per-crop watercolor icon system).
When NULL the UI falls back to the existing SVG sprite / icon-leaf.

Revision ID: 057
Revises: 056
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = "057"
down_revision = "056"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crops", sa.Column("icon_url", sa.VARCHAR(255), nullable=True))


def downgrade() -> None:
    op.drop_column("crops", "icon_url")
