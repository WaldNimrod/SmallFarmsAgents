"""AC-02 / AC-07 — SQLAlchemy model smoke tests. No DB connection required."""

from __future__ import annotations


def test_all_six_models_importable() -> None:
    from organic_market_agent.crop_book.models import (
        Crop,
        CropConversionGroup,
        CropFamily,
        CropUnitConversion,
        CropVariety,
        CropVarietySourceValue,
    )

    assert CropFamily.__tablename__ == "crop_families"
    assert Crop.__tablename__ == "crops"
    assert CropVariety.__tablename__ == "crop_varieties"
    assert CropVarietySourceValue.__tablename__ == "crop_variety_source_values"
    assert CropConversionGroup.__tablename__ == "crop_conversion_groups"
    assert CropUnitConversion.__tablename__ == "crop_unit_conversions"


def test_crop_unit_conversion_has_mutual_exclusion_check() -> None:
    from organic_market_agent.crop_book.models import CropUnitConversion

    check_texts = [
        str(c.sqltext) if hasattr(c, "sqltext") else str(c)
        for c in CropUnitConversion.__table_args__
        if hasattr(c, "name") and "exclusion" in str(getattr(c, "name", ""))
    ]
    assert any("exclusion" in t for t in check_texts) or any(
        "chk_cuc_exclusion" in str(arg) or "conversion_group_id" in str(arg)
        for arg in CropUnitConversion.__table_args__
    ), "CropUnitConversion must have chk_cuc_exclusion CHECK constraint"


def test_crop_variety_check_constraints_defined() -> None:
    from organic_market_agent.crop_book.models import CropVariety

    constraint_names = {
        getattr(arg, "name", None) for arg in CropVariety.__table_args__
    }
    assert "chk_cv_planting_method" in constraint_names
    assert "chk_cv_harvest_stage" in constraint_names
    assert "chk_cv_harvest_unit" in constraint_names


def test_crops_check_constraints_defined() -> None:
    from organic_market_agent.crop_book.models import Crop

    constraint_names = {getattr(arg, "name", None) for arg in Crop.__table_args__}
    assert "chk_crops_category" in constraint_names
    assert "chk_crops_growth_cycle" in constraint_names
    assert "chk_crops_harvest_unit_default" in constraint_names


def test_relationships_defined_on_crop() -> None:
    from organic_market_agent.crop_book.models import Crop

    assert hasattr(Crop, "family")
    assert hasattr(Crop, "varieties")
    assert hasattr(Crop, "conversion_group")
    assert hasattr(Crop, "unit_conversions")


def test_relationships_defined_on_crop_variety() -> None:
    from organic_market_agent.crop_book.models import CropVariety

    assert hasattr(CropVariety, "crop")
    assert hasattr(CropVariety, "source_values")


def test_crop_family_repr() -> None:
    from organic_market_agent.crop_book.models import CropFamily

    fam = CropFamily(scientific_name="Brassicaceae", name_he="מצליבים")
    assert "Brassicaceae" in repr(fam)


def test_crop_unit_conversion_repr() -> None:
    from decimal import Decimal

    from organic_market_agent.crop_book.models import CropUnitConversion

    conv = CropUnitConversion(source_unit="bunch", target_unit="gram", conversion_factor=Decimal("150"), source="team_00")
    assert "bunch" in repr(conv)
    assert "gram" in repr(conv)
