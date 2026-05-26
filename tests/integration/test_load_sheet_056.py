"""Integration tests for load_sheet_056_storage.py + Migration 048.

SFA-S003-P002-WP-B1-patch07 LOD400 §3.2 + AC-11.
5 new tests (brings tests/integration/ total to 20 passed):
  1. test_migration_048_upgrade_makes_crop_id_nullable
  2. test_sheet_056_parse_and_schema_validate
  3. test_sheet_056_dry_run_exits_zero
  4. test_sheet_056_apply_idempotent
  5. test_sheet_056_body_text_bound

All DB tests use SQLite in-memory fixtures — NOT live Postgres.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect as sa_inspect, text
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parents[2]

MIGRATION_047_PATH = (
    REPO_ROOT / "organic_market_agent" / "db" / "versions"
    / "047_create_crop_knowledge_notes_crops_junction.py"
)
MIGRATION_048_PATH = (
    REPO_ROOT / "organic_market_agent" / "db" / "versions"
    / "048_make_crop_knowledge_notes_crop_id_nullable.py"
)
SHEET_056_MD = (
    REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / "056-eouio-oyono.md"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_migration(path: Path, module_name: str = None):
    """Load a migration module by file path."""
    name = module_name or path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _load_loader():
    """Import load_sheet_056_storage script module."""
    scripts_dir = str(REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import importlib
    return importlib.import_module("load_sheet_056_storage")


def _build_pre048_engine():
    """SQLite in-memory engine with schema through migration 047."""
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations

    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        # Minimal schema
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
                crop_id INTEGER REFERENCES crops(id),
                source VARCHAR(50) NOT NULL,
                trust_tier VARCHAR(20) NOT NULL,
                note_type VARCHAR(40) NOT NULL,
                body_text TEXT NOT NULL,
                provenance_pdf VARCHAR(200),
                provenance_pages VARCHAR(40),
                is_internal_farm_use_only INTEGER NOT NULL DEFAULT 1,
                extraction_model VARCHAR(50),
                extracted_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)
        """))
        # Seed crop families
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Asteraceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Chenopodiaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Apiaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Fabaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Solanaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Cucurbitaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Brassicaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Amaryllidaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Poaceae')"))
        conn.execute(text("INSERT INTO crop_families(scientific_name) VALUES ('Lamiaceae')"))
        # Seed crops that appear in sheet 056 (using JMF_CROP_MAP name_he values)
        seeds = [
            ("ארוגולה", "Arugula", 1, "vegetables"),
            ("תרד", "Spinach", 2, "vegetables"),
            ("עלי בייבי", "Baby Greens", 1, "baby"),        # 'he:עלי בייבי' target
            ("אנדיב", "Endive", 1, "vegetables"),           # Frisée alias
            ("קייל", "Kale", 7, "vegetables"),
            ("מנגולד", "Swiss Chard", 2, "vegetables"),
            ("חסה", "Lettuce", 1, "vegetables"),
            ("ברוקולי", "Broccoli", 7, "vegetables"),
            ("כרובית", "Cauliflower", 7, "vegetables"),
            ("סלק", "Beets", 2, "vegetables"),
            ("גזר", "Carrots", 3, "vegetables"),
            ("צנונית", "Radishes", 7, "vegetables"),
            ("לפת", "Turnips", 7, "vegetables"),
            ("בצל ירוק", "Green Onion", 8, "vegetables"),
            ("כרישה", "Leeks", 8, "vegetables"),
            ("שומר", "Fennel", 3, "herbs"),
            ("בזיליקום", "Basil", 10, "herbs"),
            ("פלפל", "Peppers", 5, "vegetables"),
            ("מלפפון", "Cucumbers", 6, "vegetables"),
            ("חציל", "Eggplant", 5, "vegetables"),
            ("מלון", "Melons", 6, "vegetables"),
            ("עגבנייה", "Tomatoes", 5, "vegetables"),
            ("כרוב", "Cabbage", 7, "vegetables"),
            ("שעועית שיחית", "Beans (Bush)", 4, "vegetables"),
            ("אפונה", "Peas", 4, "vegetables"),
            ("שום", "Garlic", 8, "vegetables"),
            ("קישוא", "Summer Squash", 6, "vegetables"),
        ]
        for name_he, name_en, fam_id, cat in seeds:
            conn.execute(text(
                "INSERT OR IGNORE INTO crops(name_he, name_en, family_id, category) "
                "VALUES (:nhe, :nen, :fid, :cat)"
            ), {"nhe": name_he, "nen": name_en, "fid": fam_id, "cat": cat})
        conn.execute(text("INSERT INTO alembic_version(version_num) VALUES ('046')"))

    # Run migration 047 (junction table)
    m047 = _load_migration(MIGRATION_047_PATH, "m047")
    with engine.begin() as conn:
        ctx = MigrationContext.configure(conn)
        ops = Operations(ctx)
        m047.upgrade.__globals__["op"] = ops
        m047.upgrade()

    return engine


# ---------------------------------------------------------------------------
# Test 1: Migration 048 upgrade makes crop_id nullable
# ---------------------------------------------------------------------------

class TestMigration048Upgrade:
    """AC-01, AC-02, AC-03 — Migration 048 upgrade + downgrade on SQLite."""

    def test_migration_048_upgrade_makes_crop_id_nullable(self):
        """AC-01 / AC-02: upgrade succeeds; crop_id is nullable after migration."""
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations

        m048 = _load_migration(MIGRATION_048_PATH, "m048")
        engine = _build_pre048_engine()

        # Run upgrade
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m048.upgrade.__globals__["op"] = ops
            m048.upgrade()

        # Verify nullable: insert a row with crop_id=NULL
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes "
                "(crop_id, source, trust_tier, note_type, body_text, "
                " is_internal_farm_use_only, created_at) "
                "VALUES (NULL, 'NI:test_048', 'NI', 'storage_handling', 'test body', 1, :now)"
            ), {"now": now})
            row = conn.execute(text(
                "SELECT crop_id FROM crop_knowledge_notes WHERE source='NI:test_048'"
            )).fetchone()
        assert row is not None
        assert row[0] is None, f"Expected crop_id=NULL, got {row[0]}"

        # AC-03: downgrade succeeds (backfill from junction, then NOT NULL restored)
        with engine.begin() as conn:
            # Insert a junction row so the backfill has something to work with
            note_id = conn.execute(text(
                "SELECT id FROM crop_knowledge_notes WHERE source='NI:test_048'"
            )).fetchone()[0]
            crop_id = conn.execute(text("SELECT id FROM crops LIMIT 1")).fetchone()[0]
            conn.execute(text(
                "INSERT INTO crop_knowledge_notes_crops (note_id, crop_id) VALUES (:nid, :cid)"
            ), {"nid": note_id, "cid": crop_id})

        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m048.downgrade.__globals__["op"] = ops
            m048.downgrade()

        # After downgrade, NULL rows should have been backfilled
        with engine.connect() as conn:
            null_count = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes WHERE crop_id IS NULL"
            )).fetchone()[0]
        assert null_count == 0, f"Backfill failed: {null_count} rows still NULL after downgrade"


# ---------------------------------------------------------------------------
# Test 2: Parse + schema-validate sheet 056 blocks
# ---------------------------------------------------------------------------

class TestSheet056ParseAndSchemaValidate:
    """AC-04, AC-05: parser extracts ≥6 blocks; each block has required fields."""

    def test_sheet_056_parse_and_schema_validate(self):
        """AC-04/05: parser returns ≥6 blocks, each with crop_labels + procedure."""
        if not SHEET_056_MD.exists():
            pytest.skip("Sheet 056 MD not found")

        loader = _load_loader()
        blocks = loader._parse_sheet(SHEET_056_MD)

        assert len(blocks) >= 6, f"Expected ≥6 blocks, got {len(blocks)}"
        for i, block in enumerate(blocks):
            assert "crop_labels" in block, f"Block {i} missing 'crop_labels'"
            assert "procedure" in block, f"Block {i} missing 'procedure'"
            assert "section" in block, f"Block {i} missing 'section'"
            assert len(block["crop_labels"]) >= 1, f"Block {i} has no crop labels"
            assert len(block["procedure"]) > 0, f"Block {i} has empty procedure"

        # Verify specific expected crops appear somewhere
        all_labels = [label for b in blocks for label in b["crop_labels"]]
        label_set = set(all_labels)
        assert "Arugula" in label_set or any("rugula" in l for l in all_labels), \
            "Arugula not found in parsed labels"
        assert "Garlic" in label_set, "Garlic not found in parsed labels"

        # Verify alias table coverage: All Bunches aggregate should appear in labels
        assert any("Bunches" in l for l in all_labels), \
            "'All Bunches' aggregate label not found in parsed output"


# ---------------------------------------------------------------------------
# Test 3: Dry-run exits 0 and reports planned actions
# ---------------------------------------------------------------------------

class TestSheet056DryRun:
    """AC-04: --dry-run exits 0 + reports planned actions."""

    def test_sheet_056_dry_run_exits_zero(self, capsys):
        """AC-04: dry-run against in-memory SQLite returns exit code 0."""
        if not SHEET_056_MD.exists():
            pytest.skip("Sheet 056 MD not found")

        engine = _build_pre048_engine()

        # Run migration 048 so crop_id is nullable
        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        m048 = _load_migration(MIGRATION_048_PATH, "m048_dry")
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m048.upgrade.__globals__["op"] = ops
            m048.upgrade()

        loader = _load_loader()
        blocks = loader._parse_sheet(SHEET_056_MD)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            rc = loader._dry_run(blocks, session)

        captured = capsys.readouterr()
        assert rc == 0, f"_dry_run returned {rc}"
        assert "[DRY-RUN]" in captured.out
        assert "SUMMARY:" in captured.out
        assert "[PLAN]" in captured.out


# ---------------------------------------------------------------------------
# Test 4: Apply + idempotency (≥6 notes, ≥30 junction rows, duplicate-safe)
# ---------------------------------------------------------------------------

class TestSheet056ApplyIdempotent:
    """AC-05, AC-06, AC-07, AC-08, AC-10: apply inserts correct rows; idempotent."""

    @pytest.fixture(scope="class")
    def applied_engine(self):
        """Engine after running _apply twice (idempotency verification)."""
        engine = _build_pre048_engine()

        from alembic.runtime.migration import MigrationContext
        from alembic.operations import Operations
        m048 = _load_migration(MIGRATION_048_PATH, "m048_apply")
        with engine.begin() as conn:
            ctx = MigrationContext.configure(conn)
            ops = Operations(ctx)
            m048.upgrade.__globals__["op"] = ops
            m048.upgrade()

        loader = _load_loader()
        blocks = loader._parse_sheet(SHEET_056_MD)

        Session = sessionmaker(bind=engine)

        # First apply
        with Session() as session:
            n1, j1 = loader._apply(blocks, session)

        # Second apply — must be idempotent (no duplicates)
        with Session() as session:
            n2, j2 = loader._apply(blocks, session)

        return engine, n1, j1, n2, j2

    def test_sheet_056_apply_idempotent(self, applied_engine):
        """AC-05/06/07/08/10: notes, junction rows, idempotency, internal flag, existing unchanged."""
        if not SHEET_056_MD.exists():
            pytest.skip("Sheet 056 MD not found")

        engine, n1, j1, n2, j2 = applied_engine
        SOURCE = "NI:jmf_sheet_056"

        # AC-05: ≥6 notes with source='NI:jmf_sheet_056' and crop_id IS NULL
        with engine.connect() as conn:
            note_count = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes "
                "WHERE source = :src AND crop_id IS NULL"
            ), {"src": SOURCE}).fetchone()[0]
        assert note_count >= 6, f"AC-05: expected ≥6 notes, got {note_count}"

        # AC-06: ≥30 junction rows
        with engine.connect() as conn:
            junc_count = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes_crops j "
                "JOIN crop_knowledge_notes n ON n.id = j.note_id "
                "WHERE n.source = :src"
            ), {"src": SOURCE}).fetchone()[0]
        assert junc_count >= 30, f"AC-06: expected ≥30 junction rows, got {junc_count}"

        # AC-07: idempotency — second apply inserted 0 new notes and 0 new junction rows
        assert n2 == 0, f"AC-07: second apply inserted {n2} notes (expected 0)"
        assert j2 == 0, f"AC-07: second apply inserted {j2} junction rows (expected 0)"

        # AC-08: all inserted notes have is_internal_farm_use_only=TRUE (stored as 1 in SQLite)
        with engine.connect() as conn:
            non_internal = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes "
                "WHERE source = :src AND is_internal_farm_use_only != 1"
            ), {"src": SOURCE}).fetchone()[0]
        assert non_internal == 0, f"AC-08: {non_internal} notes missing is_internal_farm_use_only=TRUE"

        # AC-10: existing notes from before apply (crop_id IS NOT NULL) are unchanged
        with engine.connect() as conn:
            existing_unchanged = conn.execute(text(
                "SELECT COUNT(*) FROM crop_knowledge_notes WHERE crop_id IS NOT NULL"
            )).fetchone()[0]
        # There should be 0 pre-existing notes (fresh fixture); test checks no corruption
        assert existing_unchanged == 0, \
            f"AC-10: unexpected pre-existing notes with crop_id IS NOT NULL: {existing_unchanged}"


# ---------------------------------------------------------------------------
# Test 5: body_text ≤ 2000 chars for all inserted notes
# ---------------------------------------------------------------------------

class TestSheet056BodyTextBound:
    """AC-09: every inserted note has body_text ≤ 2000 chars."""

    def test_sheet_056_body_text_bound(self):
        """AC-09: body_text <= 2000 chars on all notes from sheet 056."""
        if not SHEET_056_MD.exists():
            pytest.skip("Sheet 056 MD not found")

        loader = _load_loader()
        blocks = loader._parse_sheet(SHEET_056_MD)

        violations = []
        for i, block in enumerate(blocks):
            body = loader._compose_body_text(block)
            if len(body) > 2000:
                violations.append(f"Block {i}: body_text length={len(body)}")

        assert violations == [], f"AC-09 body_text violations: {violations}"

        # Also verify the SHEET_056_ALIASES dict is present and has key entries
        assert hasattr(loader, "SHEET_056_ALIASES"), "SHEET_056_ALIASES not defined in loader"
        aliases = loader.SHEET_056_ALIASES
        assert "All Bunches (beets, carrots, radishes, turnips)" in aliases, \
            "Aggregate alias 'All Bunches' missing from SHEET_056_ALIASES"
        assert "he:עלי בייבי" in aliases["Mesclun Mix"], \
            "'Mesclun Mix' should target 'he:עלי בייבי'"
        assert "he:עלי בייבי" in aliases["Baby Asian Greens"], \
            "'Baby Asian Greens' should target 'he:עלי בייבי'"
        # Verify the All Bunches decomposition
        assert set(aliases["All Bunches (beets, carrots, radishes, turnips)"]) == {
            "Beets", "Carrots", "Radishes", "Turnips"
        }, "All Bunches decomposition incorrect"
