"""060: WP-CB-MIG2 — add seeder_settings TEXT column to crop_varieties.

Canon §16 (Amendment v1.3.0): seeder_settings is a T5 identity/ops column
that holds a free-text summary of front/rear gear + roller plate settings
(structured as prose, per D-MIG2-2). Only this column is new DDL — all other
MIG2 changes are Python config + data.

Revision ID: 060
Revises: 059
Create Date: 2026-06-01
"""
from alembic import op
import sqlalchemy as sa

revision = "060"
down_revision = "059"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add nullable seeder_settings TEXT column to crop_varieties."""
    with op.batch_alter_table("crop_varieties") as batch_op:
        batch_op.add_column(
            sa.Column(
                "seeder_settings",
                sa.Text(),
                nullable=True,
                comment="Free-text seeder settings summary (front/rear gear + roller plate). Canon §16 T5.",
            )
        )


def downgrade() -> None:
    """Drop seeder_settings column (data is lost — irreversible)."""
    with op.batch_alter_table("crop_varieties") as batch_op:
        batch_op.drop_column("seeder_settings")
