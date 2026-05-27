"""053: extend crop_knowledge_notes.note_type CHECK (WP-C2)

Adds 6 new note_type values to support Hebrew narrative NI extraction:
  frost_tolerance, flowering_date, pollination_mechanism,
  israeli_regions, variety_trial_score, hydro_suitability

SFA-S003-P002-WP-C2 LOD400 §3.
"""
from alembic import op

revision = "053"
down_revision = "052"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return  # SQLite re-creates table on schema change; skip live DB
    op.execute("""
        ALTER TABLE crop_knowledge_notes DROP CONSTRAINT IF EXISTS ck_ckn_note_type;
        ALTER TABLE crop_knowledge_notes ADD CONSTRAINT ck_ckn_note_type
          CHECK (note_type IN (
            'pest_disease','harvest_marker','storage_handling',
            'rotation_companion','cultivar_recommendation','growing_tip',
            'irrigation','nursery_specific','flame_weed_timing',
            'biopesticide_spray',
            'phytoprotection_substance','phytoprotection_application',
            'nursery_seeding_process',
            'frost_tolerance','flowering_date','pollination_mechanism',
            'israeli_regions','variety_trial_score','hydro_suitability'
          ));
    """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    op.execute("""
        ALTER TABLE crop_knowledge_notes DROP CONSTRAINT IF EXISTS ck_ckn_note_type;
        ALTER TABLE crop_knowledge_notes ADD CONSTRAINT ck_ckn_note_type
          CHECK (note_type IN (
            'pest_disease','harvest_marker','storage_handling',
            'rotation_companion','cultivar_recommendation','growing_tip',
            'irrigation','nursery_specific','flame_weed_timing','biopesticide_spray',
            'phytoprotection_substance','phytoprotection_application',
            'nursery_seeding_process'
          ));
    """)
