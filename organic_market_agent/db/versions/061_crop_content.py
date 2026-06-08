"""061: SFA-S003-P004-WP-CB-CONTENT — crop_content + crop_content_source tables.

Multi-source narrative prose with provenance: a canonical parent (crop_content) and a
per-source variant child (crop_content_source). Mirrors the crop_attribute provenance
shape (migration 058) applied to prose. Content is crop-level (FK → crops.id).

Revision ID: 061
Revises: 060
Create Date: 2026-06-09
"""
from alembic import op
import sqlalchemy as sa

revision = "061"
down_revision = "060"
branch_labels = None
depends_on = None

# Keep in sync with content_models.CONTENT_TYPE_VALUES.
_CONTENT_TYPES = ("story", "care_watering", "care_fertilizing", "care_pests")


def upgrade() -> None:
    _bigint = sa.BigInteger().with_variant(sa.Integer(), "sqlite")
    _content_type_check = "content_type IN ({})".format(
        ",".join("'{}'".format(v) for v in _CONTENT_TYPES)
    )

    op.create_table(
        "crop_content",
        sa.Column("id", _bigint, primary_key=True, autoincrement=True),
        sa.Column(
            "crop_id",
            _bigint,
            sa.ForeignKey("crops.id", name="fk_cc_crop_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content_type", sa.VARCHAR(40), nullable=False),
        sa.Column("text_md", sa.Text(), nullable=True),
        sa.Column("winning_source_class", sa.VARCHAR(20), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=True),
        sa.Column("source_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "computed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("crop_id", "content_type", name="uq_cc_crop_content_type"),
        sa.CheckConstraint(_content_type_check, name="ck_cc_content_type"),
    )
    op.create_index("ix_crop_content_crop_id", "crop_content", ["crop_id"])

    op.create_table(
        "crop_content_source",
        sa.Column("id", _bigint, primary_key=True, autoincrement=True),
        sa.Column(
            "content_id",
            _bigint,
            sa.ForeignKey("crop_content.id", name="fk_ccs_content_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source_label", sa.VARCHAR(100), nullable=False),
        sa.Column("source_class", sa.VARCHAR(20), nullable=False),
        sa.Column("raw_text_md", sa.Text(), nullable=False),
        sa.Column("source_url", sa.VARCHAR(500), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("content_id", "source_label", name="uq_ccs_content_source"),
    )
    op.create_index(
        "ix_crop_content_source_content_id", "crop_content_source", ["content_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_crop_content_source_content_id", table_name="crop_content_source")
    op.drop_table("crop_content_source")
    op.drop_index("ix_crop_content_crop_id", table_name="crop_content")
    op.drop_table("crop_content")
