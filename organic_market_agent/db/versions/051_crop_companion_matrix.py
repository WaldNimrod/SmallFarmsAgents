"""051: Crop companion planting matrix (WP-C4 / CW-07).

Revision ID: 051
Revises: 050
Create Date: 2026-05-27

SFA-S003-P002-WP-C4 LOD400 §3.2 (revision 051 — WP-C1 owns 050).
"""

from alembic import op
import sqlalchemy as sa

revision = "051"
down_revision = "050"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crop_companion_matrix",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_a_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("crop_b_id", sa.BigInteger,
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("compatibility", sa.String(20), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("trust_tier", sa.String(20), nullable=False),
        sa.Column("evidence_strength", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.CheckConstraint(
            "compatibility IN ('beneficial','neutral','antagonistic')",
            name="ck_ccm_compat",
        ),
        sa.CheckConstraint("crop_a_id != crop_b_id", name="ck_ccm_no_self"),
        sa.UniqueConstraint("crop_a_id", "crop_b_id", "source", name="uq_ccm"),
    )
    op.create_index("idx_ccm_a", "crop_companion_matrix", ["crop_a_id"])
    op.create_index("idx_ccm_b", "crop_companion_matrix", ["crop_b_id"])


def downgrade() -> None:
    op.drop_index("idx_ccm_b", "crop_companion_matrix")
    op.drop_index("idx_ccm_a", "crop_companion_matrix")
    op.drop_table("crop_companion_matrix")
