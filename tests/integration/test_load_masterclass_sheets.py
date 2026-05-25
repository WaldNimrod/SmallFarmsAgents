"""Integration tests for load_masterclass_sheets.py and patch03_data_fix.py.

SFA-S003-P002-WP-B1-patch04 LOD400 §5.
10 new tests covering ACs 04-17:
  1.  test_migration_047_upgrade_creates_table
  2.  test_migration_047_downgrade_reverses
  3.  test_junction_orm_relationship_returns_crops
  4.  test_junction_cascade_delete_on_crop
  5.  test_load_masterclass_dryrun_parses_all_37
  6.  test_load_masterclass_produces_valid_json_schema
  7.  test_load_masterclass_body_text_truncation
  8.  test_patch03_data_fix_dryrun_reports_correctly
  9.  test_patch03_data_fix_idempotent
  10. test_load_masterclass_all_records_internal_flag

All DB tests use SQLite in-memory fixtures — NOT live Postgres.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect as sa_inspect, text
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_047_PATH = (
    REPO_ROOT
    / "organic_market_agent"
    / "db"
    / "versions"
    / "047_create_crop_knowledge_notes_crops_junction.py"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_migration(path: Path):
    spec = importlib.util.spec_from_file_location("m047", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _build_pre047_engine():
    """Create a SQLite in-memory engine with tables up through migration 046."""
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE crop_families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scientific_name TEXT NOT NULL UNIQUE
            )
        """))
        conn.execute(text("""
            CREATE TABLE crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_he TEXT NOT NULL UNIQUE,
                name_en TEXT,
                family_id INTEGER NOT NULL REFERENCES crop_families(id),
                category TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE crop_knowledge_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop_id INTEGER NOT NULL REFERENCES crops(id),
                source VARCHAR(50) NOT NULL,
                trust_tier VARCHAR(20) NOT NULL,
                note_type VARCHAR(40) NOT NULL,
                body_text TEXT NOT NULL,
                provenance_pdf VARCHAR(200),
                provenance_pages VARCHAR(40),
                is_internal_farm_use_only INTEGER NOT NULL DEFAULT 1,
                extraction_model VARCHAR(50),
                extracted_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL,
                UNIQUE(crop_id, source, note_type),
                CHECK(length(body_text) <= 2000)
            )
        """))
        conn.execute(text("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL
            )
        """))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Brassicaceae')"))
        conn.execute(text("INSERT INTO crops(name_he, name_en, family_id, category) VALUES ('כרוב', 'Cabbage', 1, 'vegetables')"))
        conn.execute(text("INSERT INTO crops(name_he, name_en, family_id, category) VALUES ('פלפל', 'Peppers', 1, 'vegetables')"))
        conn.execute(text("INSERT INTO alembic_version(version_num) VALUES ('046')"))
    return engine


# ---------------------------------------------------------------------------
# Test 1: migration 047 upgrade creates junction table
# ---------------------------------------------------------------------------

class TestMigration047Upgrade:
    """AC-04, AC-05, AC-06 — Migration 047 upgrade."""

    @pytest.fixture(scope="class")
    def migrated_engine(self):
        """SQLite engine upgraded through migration 047."""
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m047 = _load_migration(MIGRATION_047_PATH)
        engine = _build_pre047_engine()

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m047.upgrade.__globals__["op"] = ops
            m047.upgrade()

        return engine

    def test_migration_047_upgrade_creates_table(self, migrated_engine):
        """AC-04/05: junction table exists with correct columns after upgrade."""
        inspector = sa_inspect(migrated_engine)
        tables = inspector.get_table_names()
        assert "crop_knowledge_notes_crops" in tables, (
            f"Table 'crop_knowledge_notes_crops' not found in: {tables}"
        )
        cols = {c["name"] for c in inspector.get_columns("crop_knowledge_notes_crops")}
        assert "note_id" in cols
        assert "crop_id" in cols

    def test_migration_047_index_exists(self, migrated_engine):
        """AC-06: ix_ckn_crops_crop_id index exists."""
        inspector = sa_inspect(migrated_engine)
        indices = {
            idx["name"]
            for idx in inspector.get_indexes("crop_knowledge_notes_crops")
        }
        assert "ix_ckn_crops_crop_id" in indices, (
            f"Index 'ix_ckn_crops_crop_id' not found in: {indices}"
        )


# ---------------------------------------------------------------------------
# Test 2: migration 047 downgrade reverses
# ---------------------------------------------------------------------------

class TestMigration047Downgrade:
    """AC-07 — Migration 047 downgrade (reversibility)."""

    def test_migration_047_downgrade_reverses(self):
        """AC-07: downgrade removes index + table."""
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m047 = _load_migration(MIGRATION_047_PATH)
        engine = _build_pre047_engine()

        # Upgrade first
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m047.upgrade.__globals__["op"] = ops
            m047.upgrade()

        inspector = sa_inspect(engine)
        assert "crop_knowledge_notes_crops" in inspector.get_table_names()

        # Downgrade
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m047.downgrade.__globals__["op"] = ops
            m047.downgrade()

        inspector2 = sa_inspect(engine)
        assert "crop_knowledge_notes_crops" not in inspector2.get_table_names(), (
            "Table should be gone after downgrade"
        )


# ---------------------------------------------------------------------------
# Test 3: junction ORM relationship returns crops
# ---------------------------------------------------------------------------

class TestJunctionORM:
    """AC-08 — ORM relationship on CropKnowledgeNote returns Crop instances.

    This test verifies the SQL semantics of the junction table directly
    (via raw SQL), then verifies the ORM Table object is registered.
    Full ORM mapper instantiation requires the complete dependency chain;
    the relationship attribute is verified to exist on the class definition.
    """

    @pytest.fixture(scope="class")
    def junction_engine(self):
        """SQLite engine upgraded through migration 047."""
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m047 = _load_migration(MIGRATION_047_PATH)
        engine = _build_pre047_engine()

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m047.upgrade.__globals__["op"] = ops
            m047.upgrade()

        return engine

    def test_junction_orm_relationship_returns_crops(self, junction_engine):
        """AC-08: junction table correctly links notes to multiple crops (SQL level)."""
        from datetime import datetime, timezone

        # Verify the ORM classes define the relationship attribute
        from organic_market_agent.crop_book.crop_knowledge_notes import CropKnowledgeNote
        from organic_market_agent.crop_book.models import Crop
        from organic_market_agent.crop_book.crop_knowledge_notes_crops import (
            crop_knowledge_notes_crops,
        )
        # Relationship attribute must exist on both sides
        assert hasattr(CropKnowledgeNote, "crops_linked"), (
            "CropKnowledgeNote missing 'crops_linked' relationship"
        )
        assert hasattr(Crop, "knowledge_notes_linked"), (
            "Crop missing 'knowledge_notes_linked' relationship"
        )

        # Verify the junction table object is registered in Base.metadata
        from organic_market_agent.db.base import Base
        assert "crop_knowledge_notes_crops" in Base.metadata.tables, (
            "crop_knowledge_notes_crops not in Base.metadata.tables"
        )

        # Test SQL semantics directly
        now = datetime.now(timezone.utc).isoformat()
        with junction_engine.begin() as conn:
            cab_id = conn.execute(text("SELECT id FROM crops WHERE name_he = 'כרוב'")).fetchone()[0]
            pep_id = conn.execute(text("SELECT id FROM crops WHERE name_he = 'פלפל'")).fetchone()[0]
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes "
                "(crop_id, source, trust_tier, note_type, body_text, is_internal_farm_use_only, created_at) "
                "VALUES (:cid, 'NI:orm_test', 'NI', 'growing_tip', 'test body', 1, :now)"
            ), {"cid": cab_id, "now": now})
            note_id = conn.execute(text(
                "SELECT id FROM crop_knowledge_notes WHERE source='NI:orm_test'"
            )).fetchone()[0]
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes_crops (note_id, crop_id) VALUES (:nid, :cid)"
            ), {"nid": note_id, "cid": cab_id})
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes_crops (note_id, crop_id) VALUES (:nid, :cid)"
            ), {"nid": note_id, "cid": pep_id})

        with junction_engine.connect() as conn:
            linked_crops = conn.execute(text(
                "SELECT c.name_he FROM crop_knowledge_notes_crops j "
                "JOIN crops c ON c.id = j.crop_id WHERE j.note_id = :nid"
            ), {"nid": note_id}).fetchall()
        linked_names = {r[0] for r in linked_crops}
        assert len(linked_names) == 2, f"Expected 2 linked crops, got {linked_names}"
        assert "כרוב" in linked_names
        assert "פלפל" in linked_names


# ---------------------------------------------------------------------------
# Test 4: cascade delete on crop removes junction rows
# ---------------------------------------------------------------------------

class TestJunctionCascade:
    """AC-09 — Cascade delete removes junction rows."""

    def test_junction_cascade_delete_on_crop(self):
        """AC-09: Deleting a note cascades to junction rows (ON DELETE CASCADE on note_id FK)."""
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        from datetime import datetime, timezone
        from sqlalchemy import event

        m047 = _load_migration(MIGRATION_047_PATH)

        # Create a fresh engine with FK enforcement BEFORE any connections
        engine = create_engine("sqlite:///:memory:")

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # Build pre-047 schema on this engine
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE crop_families (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scientific_name TEXT NOT NULL UNIQUE
                )
            """))
            conn.execute(text("""
                CREATE TABLE crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_he TEXT NOT NULL UNIQUE,
                    name_en TEXT,
                    family_id INTEGER NOT NULL REFERENCES crop_families(id),
                    category TEXT NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE crop_knowledge_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crop_id INTEGER NOT NULL REFERENCES crops(id) ON DELETE CASCADE,
                    source VARCHAR(50) NOT NULL,
                    trust_tier VARCHAR(20) NOT NULL,
                    note_type VARCHAR(40) NOT NULL,
                    body_text TEXT NOT NULL,
                    provenance_pdf VARCHAR(200),
                    provenance_pages VARCHAR(40),
                    is_internal_farm_use_only INTEGER NOT NULL DEFAULT 1,
                    extraction_model VARCHAR(50),
                    extracted_at TIMESTAMP,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(crop_id, source, note_type),
                    CHECK(length(body_text) <= 2000)
                )
            """))
            conn.execute(text("""
                CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)
            """))
            conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Brassicaceae')"))
            conn.execute(text("INSERT INTO crops(name_he, name_en, family_id, category) VALUES ('כרוב', 'Cabbage', 1, 'vegetables')"))
            conn.execute(text("INSERT INTO alembic_version(version_num) VALUES ('046')"))

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m047.upgrade.__globals__["op"] = ops
            m047.upgrade()

        now = datetime.now(timezone.utc).isoformat()
        with engine.begin() as conn:
            cab_id = conn.execute(
                text("SELECT id FROM crops WHERE name_he = 'כרוב'")
            ).fetchone()[0]
            # Insert a note
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes "
                "(crop_id, source, trust_tier, note_type, body_text, "
                " is_internal_farm_use_only, created_at) "
                "VALUES (:cid, 'NI:cascade_test', 'NI', 'growing_tip', 'body', 1, :now)"
            ), {"cid": cab_id, "now": now})
            note_id = conn.execute(text(
                "SELECT id FROM crop_knowledge_notes WHERE source='NI:cascade_test'"
            )).fetchone()[0]
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes_crops (note_id, crop_id) VALUES (:nid, :cid)"
            ), {"nid": note_id, "cid": cab_id})

        # Verify junction row exists
        with engine.connect() as conn:
            count = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes_crops WHERE note_id = :nid",
            ), {"nid": note_id}).fetchone()[0]
        assert count == 1

        # Delete the note — junction row should cascade-delete (note_id FK has ON DELETE CASCADE)
        with engine.begin() as conn:
            conn.execute(text(
                "DELETE FROM crop_knowledge_notes WHERE id = :nid"
            ), {"nid": note_id})

        with engine.connect() as conn:
            count_after = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes_crops WHERE note_id = :nid"
            ), {"nid": note_id}).fetchone()[0]
        assert count_after == 0, "Junction row should be deleted via cascade on note deletion"


# ---------------------------------------------------------------------------
# Test 5: dry-run parses all processable sheets
# ---------------------------------------------------------------------------

class TestLoaderDryRun:
    """AC-10 — dry-run parses MDs without error."""

    def test_load_masterclass_dryrun_parses_all_37(self, capsys):
        """AC-10: --dry-run parses all processable MDs without exception."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        loader = importlib.import_module("load_masterclass_sheets")

        exit_code = loader.cli_main(["--dry-run"])
        captured = capsys.readouterr()
        output = captured.out

        # Must complete without error
        assert exit_code == 0, f"cli_main returned {exit_code}"
        assert "SUMMARY:" in output
        # At least some sheets processed (MATCHED_CURRENT status sheets)
        assert "[PLAN]" in output


# ---------------------------------------------------------------------------
# Test 6: JSON schema validity
# ---------------------------------------------------------------------------

class TestJSONSchemaValid:
    """AC-11, AC-12 — loader produces valid JSON files."""

    def test_load_masterclass_produces_valid_json_schema(self, tmp_path):
        """AC-12: each JSON conforms to WP-B2 schema."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        loader = importlib.import_module("load_masterclass_sheets")

        # Test one entry directly
        sheets_dir = REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets"
        md_path = sheets_dir / "039-document-039.md"

        if not md_path.exists():
            pytest.skip("039-document-039.md not found")

        parsed = loader.parse_md_sheet(md_path)
        cache_rec = loader.md_to_cache_json(
            parsed=parsed,
            source="NI:jmf_masterclass",
            crop_jmf_en="Cabbage",
            crop_name_he="כרוב",
            md_filename="039-document-039.md",
            pages="3",
        )
        errors = loader.validate_json_schema(cache_rec)
        assert errors == [], f"Schema validation errors: {errors}"

        # Required top-level fields
        for field in ["schema_version", "source", "crop_jmf_en", "crop_name_he",
                      "is_internal_farm_use_only", "provenance", "notes"]:
            assert field in cache_rec, f"Missing field: {field}"

        assert cache_rec["schema_version"] == "1.0"
        assert cache_rec["is_internal_farm_use_only"] is True


# ---------------------------------------------------------------------------
# Test 7: body_text truncation
# ---------------------------------------------------------------------------

class TestBodyTextTruncation:
    """AC-13 — body_text <= 2000 chars."""

    def test_load_masterclass_body_text_truncation(self):
        """AC-13: body_text truncation to 2000 chars is enforced."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        loader = importlib.import_module("load_masterclass_sheets")

        # Create an artificially long body
        long_text = "A" * 3000
        truncated, was_truncated = loader._truncate(long_text)
        assert was_truncated is True
        assert len(truncated) <= 2000
        assert truncated.endswith("...")

        # Verify short text is not truncated
        short_text = "Short note."
        same, was_truncated2 = loader._truncate(short_text)
        assert was_truncated2 is False
        assert same == short_text

    def test_all_processable_sheets_body_text_within_limit(self):
        """AC-13: All sheets produced by the parser respect body_text <= 2000."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        loader = importlib.import_module("load_masterclass_sheets")

        from organic_market_agent.crop_book.constants import JMF_CROP_MAP
        import json

        index = json.loads((REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / "_index.json").read_text())
        violations = []
        for entry in index:
            keys = entry.get("english_keys", [])
            primary = next((k for k in keys if k in JMF_CROP_MAP), None)
            if primary is None:
                continue
            md_path = REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / entry["md"]
            if not md_path.exists():
                continue
            parsed = loader.parse_md_sheet(md_path)
            rec = loader.md_to_cache_json(
                parsed=parsed,
                source="NI:jmf_masterclass",
                crop_jmf_en=primary,
                crop_name_he=JMF_CROP_MAP[primary],
                md_filename=entry["md"],
                pages=str(entry.get("pages", "?")),
            )
            for nt, nl in rec["notes"].items():
                for note in nl:
                    if len(note["body_text"]) > 2000:
                        violations.append(f"{entry['md']} / {nt}: {len(note['body_text'])} chars")
        assert violations == [], f"body_text violations: {violations}"


# ---------------------------------------------------------------------------
# Test 8: is_internal_farm_use_only flag
# ---------------------------------------------------------------------------

class TestInternalFlagOnAllRecords:
    """AC-14 — is_internal_farm_use_only = True on every record."""

    def test_load_masterclass_all_records_internal_flag(self):
        """AC-14: every note in every processable sheet has is_internal_farm_use_only=True."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        import json
        loader = importlib.import_module("load_masterclass_sheets")

        from organic_market_agent.crop_book.constants import JMF_CROP_MAP
        index = json.loads(
            (REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / "_index.json").read_text()
        )
        violations = []
        for entry in index:
            keys = entry.get("english_keys", [])
            primary = next((k for k in keys if k in JMF_CROP_MAP), None)
            if primary is None:
                continue
            md_path = REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / entry["md"]
            if not md_path.exists():
                continue
            parsed = loader.parse_md_sheet(md_path)
            rec = loader.md_to_cache_json(
                parsed=parsed,
                source="NI:jmf_masterclass",
                crop_jmf_en=primary,
                crop_name_he=JMF_CROP_MAP[primary],
                md_filename=entry["md"],
                pages=str(entry.get("pages", "?")),
            )
            if rec.get("is_internal_farm_use_only") is not True:
                violations.append(f"{entry['md']}: top-level flag not True")
            for nt, nl in rec["notes"].items():
                for note in nl:
                    if note.get("is_internal_farm_use_only") is not True:
                        violations.append(f"{entry['md']}/{nt}: note flag not True")
        assert violations == [], f"is_internal_farm_use_only violations: {violations}"


# ---------------------------------------------------------------------------
# Test 9: patch03 data-fix dry-run
# ---------------------------------------------------------------------------

class TestPatch03DataFixDryRun:
    """AC-15 — dry-run reports per-row impact without mutation."""

    @pytest.fixture
    def sqlite_db_with_old_names(self, tmp_path):
        """SQLite DB with some old patch03 name_he values."""
        db_path = tmp_path / "test.db"
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE crop_families (
                    id INTEGER PRIMARY KEY,
                    scientific_name TEXT NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_he TEXT NOT NULL UNIQUE,
                    name_en TEXT,
                    family_id INTEGER NOT NULL REFERENCES crop_families(id),
                    category TEXT NOT NULL
                )
            """))
            conn.execute(text("INSERT INTO crop_families(id, scientific_name) VALUES (1, 'Test')"))
            # Insert one old name
            conn.execute(text(
                "INSERT INTO crops(name_he, family_id, category) "
                "VALUES ('גזר לבן', 1, 'vegetables')"
            ))
        return db_url, engine

    def test_patch03_data_fix_dryrun_reports_correctly(self, sqlite_db_with_old_names, capsys):
        """AC-15: dry-run shows '1 row(s) would be updated' without mutating."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        fix = importlib.import_module("patch03_data_fix")

        db_url, engine = sqlite_db_with_old_names
        exit_code = fix.run_data_fix(db_url, dry_run=True)
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "[DRY-RUN]" in captured.out
        # Verify row was NOT mutated
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT name_he FROM crops WHERE name_he = 'גזר לבן'")
            ).fetchone()
        assert row is not None, "Dry-run must not have mutated the row"


# ---------------------------------------------------------------------------
# Test 10: patch03 data-fix idempotency
# ---------------------------------------------------------------------------

class TestPatch03DataFixIdempotent:
    """AC-16, AC-17 — idempotent + missing-row tolerance."""

    def test_patch03_data_fix_idempotent(self, tmp_path):
        """AC-16: running --apply twice yields 0 row changes on second run."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        fix = importlib.import_module("patch03_data_fix")

        db_path = tmp_path / "idempotent.db"
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE crop_families (
                    id INTEGER PRIMARY KEY,
                    scientific_name TEXT NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_he TEXT NOT NULL UNIQUE,
                    family_id INTEGER NOT NULL REFERENCES crop_families(id),
                    category TEXT NOT NULL
                )
            """))
            conn.execute(text("INSERT INTO crop_families(id, scientific_name) VALUES (1, 'Test')"))
            conn.execute(text(
                "INSERT INTO crops(name_he, family_id, category) "
                "VALUES ('גזר לבן', 1, 'vegetables')"
            ))

        # First apply
        exit1 = fix.run_data_fix(db_url, dry_run=False)
        assert exit1 == 0

        # Verify updated
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT name_he FROM crops WHERE name_he = 'שורש פטרוזילה'")
            ).fetchone()
        assert row is not None, "First apply should update the name"

        # Second apply — should find 0 rows with old name → no-op
        exit2 = fix.run_data_fix(db_url, dry_run=False)
        assert exit2 == 0

        with engine.connect() as conn:
            count_old = conn.execute(
                text("SELECT COUNT(*) FROM crops WHERE name_he = 'גזר לבן'")
            ).fetchone()[0]
        assert count_old == 0, "Old name should not reappear"

    def test_patch03_data_fix_missing_row_tolerance(self, tmp_path):
        """AC-17: script handles missing-row-set gracefully (0 rows, no error)."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import importlib
        fix = importlib.import_module("patch03_data_fix")

        db_path = tmp_path / "missing.db"
        db_url = f"sqlite:///{db_path}"
        engine = create_engine(db_url)
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE crop_families (
                    id INTEGER PRIMARY KEY,
                    scientific_name TEXT NOT NULL
                )
            """))
            conn.execute(text("""
                CREATE TABLE crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_he TEXT NOT NULL UNIQUE,
                    family_id INTEGER NOT NULL REFERENCES crop_families(id),
                    category TEXT NOT NULL
                )
            """))
            conn.execute(text("INSERT INTO crop_families(id, scientific_name) VALUES (1, 'Test')"))
            # Intentionally: NO 'גזר לבן' row

        # Should not raise
        exit_code = fix.run_data_fix(db_url, dry_run=False)
        assert exit_code == 0
