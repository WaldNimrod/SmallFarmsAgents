"""Migration 047: crop_knowledge_notes_crops junction table (many-to-many).

SFA-S003-P002-WP-B1-patch04 LOD400 §3.3.
Creates junction table for cross-crop knowledge notes (e.g., storage/washing
guidance applicable to multiple crops — sheet 056).

Revision ID: 047
Revises: 046
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa

revision = '047'
down_revision = '046'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'crop_knowledge_notes_crops',
        sa.Column(
            'note_id',
            sa.Integer,
            sa.ForeignKey('crop_knowledge_notes.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            'crop_id',
            sa.Integer,
            sa.ForeignKey('crops.id', ondelete='CASCADE'),
            primary_key=True,
            nullable=False,
        ),
    )
    op.create_index('ix_ckn_crops_crop_id', 'crop_knowledge_notes_crops', ['crop_id'])
    # Backfill: for every existing crop_knowledge_notes row, link to its crop_id.
    # Risk R-03: current state is 0 rows in crop_knowledge_notes → backfill is a no-op.
    op.execute("""
        INSERT INTO crop_knowledge_notes_crops (note_id, crop_id)
        SELECT id, crop_id FROM crop_knowledge_notes WHERE crop_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)


def downgrade():
    op.drop_index('ix_ckn_crops_crop_id', table_name='crop_knowledge_notes_crops')
    op.drop_table('crop_knowledge_notes_crops')
