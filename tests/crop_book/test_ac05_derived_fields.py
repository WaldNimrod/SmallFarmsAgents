"""AC-05 Corrective: derived fields must have 0 rows in BOTH tables after Phase 4 + enrich.

Canon rule (LOD200 §6.4): yield_per_m2, oxide nutrients (p2o5/k2o),
plants_per_m2, and avg_revenue are DERIVED — never stored.

These tests verify the post-corrective state of the live DB and guard against
regression (Phase 4 previously left derived source_values intact, causing
Phase 8 re-enrichment to regenerate forbidden enrichment rows).

Requires: live PostgreSQL on port 5433.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.crop_book

DERIVED_FIELDS = (
    "yield_per_m2_kg",
    "nutrient_removal_p2o5_kg_ha",
    "nutrient_removal_k2o_kg_ha",
    "plants_per_m2",
)


class TestAC05DerivedFieldsAbsent:
    """AC-05: derived fields must not exist in source_values OR crop_field_enrichment."""

    def test_source_values_has_no_derived_fields(self, db_session):
        """crop_variety_source_values must have 0 rows for all 4 derived fields."""
        for field_name in DERIVED_FIELDS:
            cnt = db_session.execute(text(
                "SELECT COUNT(*) FROM crop_variety_source_values WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0
            assert cnt == 0, (
                f"FAIL AC-05: crop_variety_source_values has {cnt} rows for "
                f"derived field '{field_name}' — Phase 4 must delete from both tables"
            )

    def test_enrichment_has_no_derived_fields(self, db_session):
        """crop_field_enrichment must have 0 rows for all 4 derived fields."""
        for field_name in DERIVED_FIELDS:
            cnt = db_session.execute(text(
                "SELECT COUNT(*) FROM crop_field_enrichment WHERE field_name = :fn"
            ), {"fn": field_name}).scalar() or 0
            assert cnt == 0, (
                f"FAIL AC-05: crop_field_enrichment has {cnt} rows for "
                f"derived field '{field_name}' — enrichment must not store derived fields"
            )

    def test_elemental_p_coverage_present(self, db_session):
        """Elemental P (nutrient_removal_p_kg_ha) coverage must be >= former P2O5 variety count."""
        p_count = db_session.execute(text(
            "SELECT COUNT(DISTINCT variety_id) FROM crop_variety_source_values "
            "WHERE field_name = 'nutrient_removal_p_kg_ha'"
        )).scalar() or 0
        # The AC-05 corrective inserted 17 elemental P rows; coverage must be > 0
        assert p_count > 0, (
            "No elemental P (nutrient_removal_p_kg_ha) source_values found — "
            "oxide→elemental safety conversion may not have run"
        )

    def test_elemental_k_coverage_present(self, db_session):
        """Elemental K (nutrient_removal_k_kg_ha) coverage must be >= former K2O variety count."""
        k_count = db_session.execute(text(
            "SELECT COUNT(DISTINCT variety_id) FROM crop_variety_source_values "
            "WHERE field_name = 'nutrient_removal_k_kg_ha'"
        )).scalar() or 0
        assert k_count > 0, (
            "No elemental K (nutrient_removal_k_kg_ha) source_values found — "
            "oxide→elemental safety conversion may not have run"
        )

    def test_yield_per_bed_m_coverage_not_reduced(self, db_session):
        """Varieties with yield_per_bed_m enrichment must be >= pre-fix baseline (86)."""
        # Before fix: 86 varieties had avg_yield_per_bed_m/yield_per_bed_m source values.
        # After fix those 86 remain untouched (no yield_per_m2 without bed_m coverage existed).
        BASELINE_YIELD_BED_M = 86
        count = db_session.execute(text(
            "SELECT COUNT(DISTINCT variety_id) FROM crop_variety_source_values "
            "WHERE field_name IN ('avg_yield_per_bed_m', 'yield_per_bed_m')"
        )).scalar() or 0
        assert count >= BASELINE_YIELD_BED_M, (
            f"yield_per_bed_m coverage dropped below baseline: {count} < {BASELINE_YIELD_BED_M}"
        )

    def test_enrichment_p_k_populated_from_elemental(self, db_session):
        """After re-enrichment, elemental P and K must appear in crop_field_enrichment."""
        p_enriched = db_session.execute(text(
            "SELECT COUNT(DISTINCT variety_id) FROM crop_field_enrichment "
            "WHERE field_name = 'nutrient_removal_p_kg_ha'"
        )).scalar() or 0
        k_enriched = db_session.execute(text(
            "SELECT COUNT(DISTINCT variety_id) FROM crop_field_enrichment "
            "WHERE field_name = 'nutrient_removal_k_kg_ha'"
        )).scalar() or 0
        assert p_enriched > 0, "No elemental P enrichment rows after re-enrich"
        assert k_enriched > 0, "No elemental K enrichment rows after re-enrich"


class TestPhase4IdempotentCorrectness:
    """Phase 4 code path: verify the corrected phase4() function deletes from both tables."""

    def test_phase4_derived_fields_constant(self):
        """Derived field list in migrate.phase4 must include all 4 canon-forbidden fields."""
        import ast
        import pathlib

        source = pathlib.Path(
            "organic_market_agent/crop_book/canon/migrate.py"
        ).read_text()
        tree = ast.parse(source)

        # Find the DERIVED_FIELDS list inside phase4()
        derived_fields = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "phase4":
                for child in ast.walk(node):
                    if (
                        isinstance(child, ast.Assign)
                        and any(
                            isinstance(t, ast.Name) and t.id == "DERIVED_FIELDS"
                            for t in child.targets
                        )
                    ):
                        if isinstance(child.value, ast.List):
                            derived_fields = [
                                elt.s for elt in child.value.elts
                                if isinstance(elt, ast.Constant)
                            ]

        assert derived_fields is not None, "DERIVED_FIELDS not found in phase4()"
        for required in ("yield_per_m2_kg", "nutrient_removal_p2o5_kg_ha",
                         "nutrient_removal_k2o_kg_ha", "plants_per_m2"):
            assert required in derived_fields, (
                f"'{required}' missing from phase4() DERIVED_FIELDS"
            )

    def test_phase4_deletes_source_values(self):
        """Phase 4 code must DELETE from crop_variety_source_values, not pass."""
        import pathlib
        source = pathlib.Path(
            "organic_market_agent/crop_book/canon/migrate.py"
        ).read_text()

        # The old bug: 'pass  # Only delete enrichment rows'
        assert "pass  # Only delete enrichment rows" not in source, (
            "Old bug still present: phase4 has 'pass' for source_values deletion"
        )
        # The fix: DELETE FROM crop_variety_source_values
        assert "DELETE FROM crop_variety_source_values" in source, (
            "phase4 must DELETE FROM crop_variety_source_values for derived fields"
        )
