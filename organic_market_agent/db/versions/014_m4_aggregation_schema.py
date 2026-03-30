"""014: M4 aggregation schema marker — daily_aggregates + weekly_snapshots.

MANDATE-20260330-M4-SCHEMA-T20 asks for CREATE TABLE for daily_aggregates and
weekly_snapshots. Those tables are already created in revision 001_initial_schema
with the same columns, FKs, and constraints as organic_market_agent.models.aggregates
(DailyAggregate, WeeklySnapshot). Re-creating them here would fail with
"relation already exists" on any database that applied 001.

This migration is a documented no-op: it advances the Alembic chain to 014 (head)
so G4 / M4 Phase A tooling can depend on revision 014 without duplicating schema.

See: _COMMUNICATION/TEAM_20/MANDATE_M4_SCHEMA_TEAM20.md
"""

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
