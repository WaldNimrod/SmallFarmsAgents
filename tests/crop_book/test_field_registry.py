"""Tests for crop_book.canon.field_registry — FIELD_REGISTRY + RENAME_MAP + get_canonical()."""
import pytest

from organic_market_agent.crop_book.canon.field_registry import (
    FIELD_REGISTRY,
    RENAME_MAP,
    ALIAS_MAP,
    DERIVE_DROP_FIELDS,
    get_canonical,
)


class TestFieldRegistry:
    """AC-01: FIELD_REGISTRY implements Canon §7 exactly."""

    def test_rename_entries_present(self):
        """All §7.1 renames are in FIELD_REGISTRY."""
        expected_renames = {
            "in_row_spacing_cm": "spacing_in_row_cm",
            "avg_yield_per_bed_m": "yield_per_bed_m",
            "documented_price": "price_documented",
            "seeds_per_gram": "seeds_per_g",
            "nutrient_removal_n_kg_ha": "nutrient_removal_n_kg_per_ha",
            "nutrient_removal_p_kg_ha": "nutrient_removal_p_kg_per_ha",
            "nutrient_removal_k_kg_ha": "nutrient_removal_k_kg_per_ha",
            "nutrient_removal_ca_kg_ha": "nutrient_removal_ca_kg_per_ha",
            "nutrient_removal_mg_kg_ha": "nutrient_removal_mg_kg_per_ha",
            "days_in_gh_total": "days_in_nursery",
            "days_to_first_potting": "nursery_days_to_potting",
            "days_to_germinate_gh": "nursery_days_to_germinate",
        }
        for old, canonical in expected_renames.items():
            assert old in RENAME_MAP, f"{old!r} not in RENAME_MAP"
            assert RENAME_MAP[old] == canonical, f"RENAME_MAP[{old!r}] = {RENAME_MAP[old]!r}, expected {canonical!r}"

    def test_derive_drop_fields(self):
        """Derived/dropped fields are in DERIVE_DROP_FIELDS."""
        expected_derive = {
            "yield_per_m2_kg",
            "nutrient_removal_p2o5_kg_ha",
            "nutrient_removal_k2o_kg_ha",
            "plants_per_m2",
            "avg_revenue_per_bed_m",
            "storage_life_text",
        }
        assert expected_derive <= DERIVE_DROP_FIELDS

    def test_attr_layer_fields(self):
        """T2/T3 §7.2 attrs all map to crop_attribute layer."""
        attr_fields = [
            "planting_method", "frost_tolerance_class", "season_window",
            "sowing_months", "transplant_months", "storage_ethylene_sensitivity",
            "variety_provider", "rootstock_variety", "harvest_unit", "harvest_stage",
        ]
        for f in attr_fields:
            meta = FIELD_REGISTRY.get(f)
            assert meta is not None, f"{f!r} not in FIELD_REGISTRY"
            assert meta.layer == "crop_attribute", f"{f!r} layer={meta.layer!r}"

    def test_get_canonical_rename(self):
        """get_canonical maps old→canonical."""
        assert get_canonical("avg_yield_per_bed_m") == "yield_per_bed_m"
        assert get_canonical("in_row_spacing_cm") == "spacing_in_row_cm"
        assert get_canonical("days_in_gh_total") == "days_in_nursery"
        assert get_canonical("days_to_germinate_gh") == "nursery_days_to_germinate"
        assert get_canonical("days_to_first_potting") == "nursery_days_to_potting"

    def test_get_canonical_identity(self):
        """get_canonical returns same for already-canonical names."""
        assert get_canonical("yield_per_bed_m") == "yield_per_bed_m"
        assert get_canonical("days_to_maturity") == "days_to_maturity"
        assert get_canonical("days_in_nursery") == "days_in_nursery"

    def test_get_canonical_unknown(self):
        """Unknown fields return themselves (passthrough)."""
        assert get_canonical("nonexistent_field_xyz") == "nonexistent_field_xyz"

    def test_nursery_trio_f190_mig03(self):
        """F-190-MIG-03: nursery companion renames present."""
        assert get_canonical("days_to_first_potting") == "nursery_days_to_potting"
        assert get_canonical("days_to_germinate_gh") == "nursery_days_to_germinate"
        # The canonical names are KEEP (not drop)
        assert FIELD_REGISTRY["nursery_days_to_potting"].disposition == "KEEP"
        assert FIELD_REGISTRY["nursery_days_to_germinate"].disposition == "KEEP"
        assert FIELD_REGISTRY["days_in_nursery"].disposition == "KEEP"
