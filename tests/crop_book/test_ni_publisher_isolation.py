"""Publisher isolation tests — AC-21b + AC-21c.

Verifies that publisher/ and views.py do NOT reference crop_knowledge_notes
or CropKnowledgeNote. Enforces §3.1 OPERATIVE LICENSING INVARIANT.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §3.1.2 / §9.
"""
import pathlib
import pytest

pytestmark = pytest.mark.crop_book

PUB_DIR = pathlib.Path("organic_market_agent/publisher")
VIEWS_PY = pathlib.Path("organic_market_agent/crop_book/views.py")

FORBIDDEN_STRINGS = ("crop_knowledge_notes", "CropKnowledgeNote")


class TestNiPublisherIsolation:
    """AC-21b: publisher/ does not reference crop_knowledge_notes."""

    def test_ac21b_publisher_dir_clean(self):
        assert PUB_DIR.exists(), f"Publisher dir not found: {PUB_DIR}"
        violations = []
        for py_file in PUB_DIR.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN_STRINGS:
                if forbidden in content:
                    violations.append(f"{py_file.name}: contains '{forbidden}'")
        assert violations == [], (
            "§3.1 violation — publisher files reference crop_knowledge_notes:\n"
            + "\n".join(violations)
        )

    def test_ac21c_views_py_clean(self):
        """AC-21c: views.py does not reference crop_knowledge_notes."""
        assert VIEWS_PY.exists(), f"views.py not found: {VIEWS_PY}"
        content = VIEWS_PY.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in content, (
                f"§3.1 violation — views.py references '{forbidden}'"
            )
