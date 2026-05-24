"""Migration 044: crop_task_templates table — per-crop discrete growing tasks.

SFA-S003-P002-WP-B1 LOD400 §3. Additive only; no modification of prior tables.
"""
from alembic import op
import sqlalchemy as sa

revision = "044"
down_revision = "043"
branch_labels = None
depends_on = None

_TASK_TYPE_ENUM = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)
_TIMING_ANCHOR_ENUM = ("seeding", "transplanting", "harvest", "field_prep")


def upgrade():
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    created_at_default = sa.text("CURRENT_TIMESTAMP") if is_sqlite else sa.text("now()")
    is_active_default = sa.text("1") if is_sqlite else sa.text("true")

    op.create_table(
        "crop_task_templates",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=False),
        sa.Column("task_type", sa.VARCHAR(40), nullable=False),
        sa.Column("timing_anchor", sa.VARCHAR(20), nullable=True),
        # F-S-002 (R1): days_offset is NOT NULL with a sentinel value for
        # presence-only ("X") cells. SQL UNIQUE constraints permit multiple
        # NULL tuples on both Postgres and SQLite — nullability here would
        # break idempotent re-import. Sentinel chosen so it is impossible
        # to confuse with a real offset (no agricultural task is scheduled
        # -32768 days from any anchor).
        sa.Column("days_offset", sa.Integer, nullable=False,
                  server_default=sa.text("-32768")),
        sa.Column("method", sa.Text, nullable=True),
        sa.Column("input_material", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=is_active_default),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=created_at_default),
        # F-S-002 (R1): all 4 columns are NOT NULL → UNIQUE behaves
        # deterministically on both Postgres and SQLite (no NULL-tuple
        # idempotency hole). Presence-only rows collide via the
        # DAYS_OFFSET_PRESENCE_ONLY sentinel (-32768).
        sa.UniqueConstraint("crop_id", "source", "task_type", "days_offset",
                            name="uq_cct_crop_source_type_offset"),
        sa.CheckConstraint(
            "task_type IN (" + ",".join(repr(v) for v in _TASK_TYPE_ENUM) + ")",
            name="ck_cct_task_type",
        ),
        sa.CheckConstraint(
            "timing_anchor IS NULL OR timing_anchor IN ("
            + ",".join(repr(v) for v in _TIMING_ANCHOR_ENUM) + ")",
            name="ck_cct_timing_anchor",
        ),
    )
    op.create_index("idx_cct_crop", "crop_task_templates", ["crop_id"])
    op.create_index("idx_cct_type", "crop_task_templates", ["task_type"])


def downgrade():
    op.drop_index("idx_cct_type", table_name="crop_task_templates")
    op.drop_index("idx_cct_crop", table_name="crop_task_templates")
    op.drop_table("crop_task_templates")
