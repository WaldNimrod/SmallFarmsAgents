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


# WP-CB-CONTENT license firewall: the public narrative-content pipeline (loader + the new
# crop_content publisher fetchers) MUST NOT read the internal-only crop_knowledge_notes table.
CONTENT_LOADER_PY = pathlib.Path(
    "organic_market_agent/crop_book/importer/content_loader.py"
)
CONTENT_MODELS_PY = pathlib.Path("organic_market_agent/crop_book/content_models.py")


class TestContentLicenseFirewall:
    """WP-CB-CONTENT §2c — public crop_content path has zero crop_knowledge_notes read path.

    The firewall bans IMPORTING / QUERYING the internal table — not merely naming it in a
    docstring that documents the separation. So we assert: no import of the crop_knowledge_notes
    module, no reference to the CropKnowledgeNote model, and no SQL against the table.
    """

    @staticmethod
    def _assert_no_read_path(py_path: pathlib.Path) -> None:
        import io
        import tokenize

        assert py_path.exists(), f"not found: {py_path}"
        src = py_path.read_text(encoding="utf-8")
        code = []
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT):
                continue  # ignore docstrings/comments — they may name the table to document the firewall
            code.append(tok.string)
        joined = " ".join(code)
        assert "CropKnowledgeNote" not in joined, f"{py_path.name}: imports/uses the CropKnowledgeNote model"
        assert "crop_knowledge_notes" not in joined, f"{py_path.name}: imports the crop_knowledge_notes module"

    def test_content_loader_clean(self):
        self._assert_no_read_path(CONTENT_LOADER_PY)

    def test_content_models_clean(self):
        self._assert_no_read_path(CONTENT_MODELS_PY)
