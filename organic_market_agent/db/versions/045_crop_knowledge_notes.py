"""Migration 045: crop_knowledge_notes table — per-crop NI narrative.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §3. Additive only.
Precondition for B3 migration 046.
"""
from alembic import op
import sqlalchemy as sa

revision = "045"
down_revision = "044"
branch_labels = None
depends_on = None

_NOTE_TYPE_ENUM = (
    # From JMF book (main + alt editions) — 8 baseline types
    "pest_disease",
    "harvest_marker",
    "storage_handling",
    "rotation_companion",
    "cultivar_recommendation",
    "growing_tip",
    "irrigation",
    "nursery_specific",
    # From FT PDFs — 2 baseline + 3 Q5 additions
    "flame_weed_timing",           # FT_FLAMEWEEDING
    "biopesticide_spray",          # FT_TABLEAUAPPLICATIONBIOPESTICIPE
    "phytoprotection_substance",   # FT_PHYTOPROTECTION (Q5)
    "phytoprotection_application", # FT_PHYTOPROTECTION (Q5)
    "nursery_seeding_process",     # FT_NURSERYSEEDING (Q5)
)
# Total: 13 enum values. Was 10 in v1.0.0; +3 from Q5.


def upgrade() -> None:
    op.create_table(
        "crop_knowledge_notes",
        sa.Column(
            "id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "crop_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            sa.ForeignKey("crops.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=False),
        sa.Column("note_type", sa.VARCHAR(40), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("provenance_pdf", sa.VARCHAR(200), nullable=True),
        sa.Column("provenance_pages", sa.VARCHAR(40), nullable=True),
        sa.Column(
            "is_internal_farm_use_only",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("extraction_model", sa.VARCHAR(50), nullable=True),
        sa.Column("extracted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint(
            "crop_id", "source", "note_type", name="uq_ckn_crop_source_type"
        ),
        sa.CheckConstraint(
            "note_type IN (" + ",".join(repr(v) for v in _NOTE_TYPE_ENUM) + ")",
            name="ck_ckn_note_type",
        ),
        sa.CheckConstraint(
            "length(body_text) <= 2000",
            name="ck_ckn_body_text_length",
        ),
    )
    op.create_index("idx_ckn_crop", "crop_knowledge_notes", ["crop_id"])
    op.create_index("idx_ckn_type", "crop_knowledge_notes", ["note_type"])


def downgrade() -> None:
    op.drop_index("idx_ckn_type", table_name="crop_knowledge_notes")
    op.drop_index("idx_ckn_crop", table_name="crop_knowledge_notes")
    op.drop_table("crop_knowledge_notes")
