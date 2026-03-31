"""016: M6 — scheduler_config + pipeline_alerts.

MANDATE-M6-SCHEMA-TEAM20

Mandate seed used ON CONFLICT DO NOTHING without a UNIQUE constraint; PostgreSQL
would not dedupe. We seed with INSERT ... SELECT ... WHERE NOT EXISTS instead.

ingestion_runs.id is BigInteger; pipeline_alerts.ingestion_run_id matches it.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision = "016"
down_revision = "015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scheduler_config",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("run_hour", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("run_minute", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("retry_attempts", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("cleanup_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("cleanup_after_days", sa.Integer(), nullable=False, server_default="90"),
        sa.Column("cleanup_last_run", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("run_hour >= 0 AND run_hour <= 23", name="chk_sc_run_hour"),
        sa.CheckConstraint("run_minute >= 0 AND run_minute <= 59", name="chk_sc_run_minute"),
        sa.CheckConstraint(
            "retry_attempts >= 0 AND retry_attempts <= 10",
            name="chk_sc_retry_attempts",
        ),
        sa.CheckConstraint("cleanup_after_days >= 7", name="chk_sc_cleanup_after_days"),
    )

    conn = op.get_bind()
    conn.execute(
        text(
            """
            INSERT INTO scheduler_config (
                is_enabled, run_hour, run_minute, retry_attempts,
                cleanup_enabled, cleanup_after_days
            )
            SELECT true, 6, 0, 2, true, 90
            WHERE NOT EXISTS (SELECT 1 FROM scheduler_config)
            """
        )
    )

    op.create_table(
        "pipeline_alerts",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), primary_key=True),
        sa.Column("ingestion_run_id", sa.BigInteger(), nullable=True),
        sa.Column("level", sa.VARCHAR(20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["ingestion_run_id"],
            ["ingestion_runs.id"],
            ondelete="SET NULL",
        ),
        sa.CheckConstraint(
            "level IN ('info', 'warning', 'error')",
            name="chk_pa_level",
        ),
    )
    op.create_index("ix_pipeline_alerts_is_read", "pipeline_alerts", ["is_read"])
    op.execute(
        "CREATE INDEX ix_pipeline_alerts_created_at ON pipeline_alerts (created_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_pipeline_alerts_created_at")
    op.drop_index("ix_pipeline_alerts_is_read", table_name="pipeline_alerts")
    op.drop_table("pipeline_alerts")
    op.drop_table("scheduler_config")
