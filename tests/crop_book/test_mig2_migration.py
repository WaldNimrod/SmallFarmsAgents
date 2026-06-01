"""Migration 060 up/down test via SQLite (WI-4 / AC-01).

Uses SQLite in-memory via batch_alter_table (Alembic offline mode).
Tests:
  - 060 upgrade: seeder_settings column added
  - 060 downgrade: seeder_settings column removed
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, Text, inspect


def _load_m060():
    """Import the 060 migration module (leading-digit name → importlib)."""
    import importlib
    return importlib.import_module("organic_market_agent.db.versions.060_seeder_settings")


def _drive_migration(engine, direction: str) -> None:
    """Drive the REAL 060 upgrade()/downgrade() against `engine` via a live
    Alembic Operations context (F-190-MIG2-V-01: exercise the migration's own
    code, incl. batch_alter_table table-recreate on SQLite — not a hand-written
    DDL simulation)."""
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    m060 = _load_m060()
    with engine.connect() as conn:
        with conn.begin():
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            # Bind the module-level `op` proxy the migration uses, then run it.
            with Operations.context(ctx):
                if direction == "upgrade":
                    m060.upgrade()
                elif direction == "downgrade":
                    m060.downgrade()
                else:  # pragma: no cover
                    raise ValueError(direction)


def _run_migration_060_upgrade(engine) -> None:
    """Run the REAL 060 upgrade on the given engine."""
    _drive_migration(engine, "upgrade")


def _run_migration_060_downgrade(engine) -> None:
    """Run the REAL 060 downgrade on the given engine."""
    _drive_migration(engine, "downgrade")


def _create_minimal_schema(engine) -> None:
    """Create a minimal crop_varieties table for testing."""
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(sa.text("""
                CREATE TABLE IF NOT EXISTS crop_varieties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_id INTEGER NOT NULL,
                    name_en VARCHAR(200),
                    name_he VARCHAR(200),
                    is_default BOOLEAN NOT NULL DEFAULT 0,
                    is_grafted BOOLEAN NOT NULL DEFAULT 0,
                    seeder VARCHAR(100),
                    notes TEXT
                )
            """))


class TestMigration060:
    """AC-01: migration 060 adds seeder_settings nullable TEXT column."""

    def test_upgrade_adds_seeder_settings(self):
        """After 060 upgrade, seeder_settings column exists on crop_varieties."""
        engine = sa.create_engine("sqlite:///:memory:")
        _create_minimal_schema(engine)

        # Verify column doesn't exist before upgrade
        insp = sa.inspect(engine)
        cols_before = [c["name"] for c in insp.get_columns("crop_varieties")]
        assert "seeder_settings" not in cols_before

        # Run upgrade
        _run_migration_060_upgrade(engine)

        # Verify column exists after upgrade
        insp2 = sa.inspect(engine)
        cols_after = [c["name"] for c in insp2.get_columns("crop_varieties")]
        assert "seeder_settings" in cols_after, \
            "seeder_settings column must exist after upgrade"

    def test_seeder_settings_column_nullable(self):
        """seeder_settings must be nullable (Canon §16 T5)."""
        engine = sa.create_engine("sqlite:///:memory:")
        _create_minimal_schema(engine)
        _run_migration_060_upgrade(engine)

        insp = sa.inspect(engine)
        cols = {c["name"]: c for c in insp.get_columns("crop_varieties")}
        assert "seeder_settings" in cols

        # In SQLite, nullable is reflected as not having notnull constraint
        col = cols["seeder_settings"]
        assert col.get("nullable", True) is not False, \
            "seeder_settings must be nullable"

    def test_seeder_settings_accepts_text(self):
        """Can write and read text values for seeder_settings."""
        engine = sa.create_engine("sqlite:///:memory:")
        _create_minimal_schema(engine)
        _run_migration_060_upgrade(engine)

        test_value = "Front: A, Rear: B, Roller: C-24 plate"
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(sa.text(
                    "INSERT INTO crop_varieties (crop_id, seeder_settings) "
                    "VALUES (1, :val)"
                ), {"val": test_value})
            row = conn.execute(sa.text(
                "SELECT seeder_settings FROM crop_varieties WHERE crop_id = 1"
            )).fetchone()
        assert row is not None
        assert row[0] == test_value

    def test_seeder_settings_accepts_null(self):
        """seeder_settings accepts NULL."""
        engine = sa.create_engine("sqlite:///:memory:")
        _create_minimal_schema(engine)
        _run_migration_060_upgrade(engine)

        with engine.connect() as conn:
            with conn.begin():
                conn.execute(sa.text(
                    "INSERT INTO crop_varieties (crop_id, seeder_settings) "
                    "VALUES (2, NULL)"
                ))
            row = conn.execute(sa.text(
                "SELECT seeder_settings FROM crop_varieties WHERE crop_id = 2"
            )).fetchone()
        assert row is not None
        assert row[0] is None

    def test_downgrade_removes_seeder_settings(self):
        """AC-01 / F-190-MIG2-V-01: after the REAL 060 downgrade, the column is gone.

        Drives the migration's own downgrade() (batch_alter_table.drop_column),
        not a simulation — closing the prior stub-helper gap.
        """
        engine = sa.create_engine("sqlite:///:memory:")
        _create_minimal_schema(engine)

        _run_migration_060_upgrade(engine)
        cols_up = [c["name"] for c in sa.inspect(engine).get_columns("crop_varieties")]
        assert "seeder_settings" in cols_up, "column must exist after upgrade"

        _run_migration_060_downgrade(engine)
        cols_down = [c["name"] for c in sa.inspect(engine).get_columns("crop_varieties")]
        assert "seeder_settings" not in cols_down, \
            "seeder_settings must be removed after downgrade"

        # Pre-existing identity columns survive the batch table-recreate.
        for keep in ("id", "crop_id", "name_en", "seeder", "notes"):
            assert keep in cols_down, f"{keep} must survive downgrade"

    def test_migration_module_structure(self):
        """Migration file has correct revision IDs."""
        import importlib
        m060 = importlib.import_module("organic_market_agent.db.versions.060_seeder_settings")
        assert m060.revision == "060"
        assert m060.down_revision == "059"
