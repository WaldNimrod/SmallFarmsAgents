"""make crop_knowledge_notes.crop_id nullable for M2M-only notes

Revision ID: 048
Revises: 047
Create Date: 2026-05-26

SFA-S003-P002-WP-B1-patch07 LOD400 §3.1.
Enables notes that apply to multiple crops via junction table (crop_knowledge_notes_crops)
without requiring a single crop_id. Dialect-aware per Migration 046 precedent.
"""
from alembic import op
import sqlalchemy as sa

revision = '048'
down_revision = '047'
branch_labels = None
depends_on = None


def upgrade():
    # Dialect-aware (per Migration 046 precedent in this repo)
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("crop_knowledge_notes", recreate="always") as batch_op:
            batch_op.alter_column("crop_id", existing_type=sa.BigInteger(), nullable=True)
    else:
        op.alter_column(
            "crop_knowledge_notes", "crop_id",
            existing_type=sa.BigInteger(),
            nullable=True,
        )


def downgrade():
    # Backfill from junction first (safe-only if junction has the data)
    op.execute(
        "UPDATE crop_knowledge_notes SET crop_id = "
        "(SELECT crop_id FROM crop_knowledge_notes_crops "
        " WHERE note_id = crop_knowledge_notes.id LIMIT 1) "
        "WHERE crop_id IS NULL"
    )
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("crop_knowledge_notes", recreate="always") as batch_op:
            batch_op.alter_column("crop_id", existing_type=sa.BigInteger(), nullable=False)
    else:
        op.alter_column(
            "crop_knowledge_notes", "crop_id",
            existing_type=sa.BigInteger(),
            nullable=False,
        )
