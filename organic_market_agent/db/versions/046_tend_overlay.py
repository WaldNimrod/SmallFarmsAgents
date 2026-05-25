"""Migration 046: crop_harvest_stats + extend crop_task_templates task_type enum.

SFA-S003-P002-WP-B3 LOD400 §3. ALTER on B1's table is authorized by
GCR-B3-1 (team_00 sign-off recorded in
_COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-B3-WHITELIST_2026-05-25_v1.0.0.md).
"""
from alembic import op
import sqlalchemy as sa

revision = "046"
down_revision = "045"   # B2's migration; builder verified B2 LOD500_LOCKED before running
branch_labels = None
depends_on = None

_NEW_TASK_TYPES = ("nursery_seed", "pest_spray", "potting_up", "thinning",
                   "trellis", "fertilize")
_B1_TASK_TYPES = (
    "stale_seed_bed", "flame_weeder", "flextine_harrow_1", "flextine_harrow_2",
    "biodisc", "hoe", "hand_weed", "boron_seaweed_1", "boron_seaweed_2",
    "straw_mulch_topdress", "head_pinch_chop", "mow_and_tarp",
    "at_seeding_transplanting", "net_row_cover",
)
_FULL_TASK_TYPES = _B1_TASK_TYPES + _NEW_TASK_TYPES   # 20 total

_SEASON_VALUES = ("spring", "summer", "fall", "winter")


def upgrade():
    # 1. Create crop_harvest_stats
    op.create_table(
        "crop_harvest_stats",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("season", sa.VARCHAR(20), nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("cycles_count", sa.Integer, nullable=True),
        sa.Column("first_harvest_week", sa.Integer, nullable=True),
        sa.Column("peak_harvest_week", sa.Integer, nullable=True),
        sa.Column("last_harvest_week", sa.Integer, nullable=True),
        sa.Column("yield_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("yield_unit", sa.VARCHAR(20), nullable=True),
        sa.Column("yield_per_bed_min", sa.Numeric(10, 3), nullable=True),
        sa.Column("yield_per_bed_max", sa.Numeric(10, 3), nullable=True),
        sa.Column("yield_per_bed_median", sa.Numeric(10, 3), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("crop_id", "season", "year", "source",
                            name="uq_chs_crop_season_year_source"),
        sa.CheckConstraint(
            "season IN ({})".format(",".join(repr(v) for v in _SEASON_VALUES)),
            name="ck_chs_season",
        ),
    )
    op.create_index("idx_chs_crop", "crop_harvest_stats", ["crop_id"])
    op.create_index("idx_chs_crop_year", "crop_harvest_stats", ["crop_id", "year"])

    # 2. ALTER crop_task_templates CHECK constraint
    # SQLite cannot ALTER CHECK constraints in place. Use dialect branch:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE crop_task_templates DROP CONSTRAINT ck_cct_task_type")
        op.create_check_constraint(
            "ck_cct_task_type", "crop_task_templates",
            "task_type IN ({})".format(",".join(repr(v) for v in _FULL_TASK_TYPES)),
        )
    elif bind.dialect.name == "sqlite":
        # SQLite path: drop+rebuild table with new constraint via batch_alter_table.
        # Preserve all data + indices + UNIQUE constraint + the days_offset NOT NULL.
        with op.batch_alter_table("crop_task_templates",
                                  recreate="always") as batch_op:
            batch_op.create_check_constraint(
                "ck_cct_task_type",
                "task_type IN ({})".format(",".join(repr(v) for v in _FULL_TASK_TYPES)),
            )
    else:
        raise RuntimeError(f"Unsupported dialect: {bind.dialect.name}")


def downgrade():
    # Reverse order
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE crop_task_templates DROP CONSTRAINT ck_cct_task_type")
        op.create_check_constraint(
            "ck_cct_task_type", "crop_task_templates",
            "task_type IN ({})".format(",".join(repr(v) for v in _B1_TASK_TYPES)),
        )
    elif bind.dialect.name == "sqlite":
        with op.batch_alter_table("crop_task_templates",
                                  recreate="always") as batch_op:
            batch_op.create_check_constraint(
                "ck_cct_task_type",
                "task_type IN ({})".format(",".join(repr(v) for v in _B1_TASK_TYPES)),
            )
    else:
        raise RuntimeError(f"Unsupported dialect: {bind.dialect.name}")

    op.drop_index("idx_chs_crop_year", table_name="crop_harvest_stats")
    op.drop_index("idx_chs_crop", table_name="crop_harvest_stats")
    op.drop_table("crop_harvest_stats")
