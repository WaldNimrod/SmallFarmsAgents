"""Canon §7 — Field registry: current → canonical name + metadata.

FIELD_REGISTRY: {current_name → FieldMeta}
    Authoritative transform map used by Phase 5 (rename) and consumers.

RENAME_MAP: {old_name → canonical_name}  — all rename entries (flat lookup).
ALIAS_MAP:  {old_name → canonical_name}  — same as RENAME_MAP; used by consumers
    for one-cycle read-compatibility (resolve old OR new name → canonical).

get_canonical(field_name) -> str
    Returns the canonical name for field_name (identity if already canonical).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldMeta:
    canonical: str
    """Canonical field name (Canon §6.2 naming convention)."""
    field_type: str
    """T1 | T2 | T3 | T4 | T5 | T6"""
    layer: str
    """enrichment | crop_attribute | column | none (derived)"""
    disposition: str
    """KEEP | RENAME | DERIVE | ATTR | DEPRECATE-COL | DQ | DROP"""
    unit: str | None = None
    """Canonical unit string (from units.py) — None for text/categoricals."""


# ---------------------------------------------------------------------------
# Field registry — Canon §7 (complete)
# ---------------------------------------------------------------------------
FIELD_REGISTRY: dict[str, FieldMeta] = {
    # -------------------------------------------------------------------------
    # §7.1 Reconciled-numeric facts (T1 → enrichment)
    # -------------------------------------------------------------------------
    "days_to_maturity": FieldMeta(
        canonical="days_to_maturity",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    "harvest_window_max_days": FieldMeta(
        canonical="harvest_window_max_days",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    "harvest_window_min_days": FieldMeta(
        canonical="harvest_window_min_days",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    # RENAME: in_row_spacing_cm → spacing_in_row_cm
    "in_row_spacing_cm": FieldMeta(
        canonical="spacing_in_row_cm",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="cm",
    ),
    "spacing_in_row_cm": FieldMeta(
        canonical="spacing_in_row_cm",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="cm",
    ),
    "rows_per_bed": FieldMeta(
        canonical="rows_per_bed",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="count",
    ),
    # RENAME: avg_yield_per_bed_m → yield_per_bed_m
    "avg_yield_per_bed_m": FieldMeta(
        canonical="yield_per_bed_m",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_bed_m",
    ),
    "yield_per_bed_m": FieldMeta(
        canonical="yield_per_bed_m",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_bed_m",
    ),
    # DERIVE: yield_per_m2_kg → computed (drop stored)
    "yield_per_m2_kg": FieldMeta(
        canonical="yield_per_m2_kg",
        field_type="T4", layer="none", disposition="DERIVE", unit="kg_per_m2",
    ),
    # RENAME: documented_price → price_documented
    "documented_price": FieldMeta(
        canonical="price_documented",
        field_type="T1", layer="enrichment", disposition="RENAME", unit=None,
    ),
    "price_documented": FieldMeta(
        canonical="price_documented",
        field_type="T1", layer="enrichment", disposition="KEEP", unit=None,
    ),
    # RENAME: seeds_per_gram → seeds_per_g
    "seeds_per_gram": FieldMeta(
        canonical="seeds_per_g",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="seeds_per_g",
    ),
    "seeds_per_g": FieldMeta(
        canonical="seeds_per_g",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="seeds_per_g",
    ),
    # RENAME: nutrient_removal_*_kg_ha → *_kg_per_ha
    "nutrient_removal_n_kg_ha": FieldMeta(
        canonical="nutrient_removal_n_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_ha",
    ),
    "nutrient_removal_n_kg_per_ha": FieldMeta(
        canonical="nutrient_removal_n_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_ha",
    ),
    "nutrient_removal_p_kg_ha": FieldMeta(
        canonical="nutrient_removal_p_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_ha",
    ),
    "nutrient_removal_p_kg_per_ha": FieldMeta(
        canonical="nutrient_removal_p_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_ha",
    ),
    "nutrient_removal_k_kg_ha": FieldMeta(
        canonical="nutrient_removal_k_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_ha",
    ),
    "nutrient_removal_k_kg_per_ha": FieldMeta(
        canonical="nutrient_removal_k_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_ha",
    ),
    "nutrient_removal_ca_kg_ha": FieldMeta(
        canonical="nutrient_removal_ca_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_ha",
    ),
    "nutrient_removal_ca_kg_per_ha": FieldMeta(
        canonical="nutrient_removal_ca_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_ha",
    ),
    "nutrient_removal_mg_kg_ha": FieldMeta(
        canonical="nutrient_removal_mg_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="kg_per_ha",
    ),
    "nutrient_removal_mg_kg_per_ha": FieldMeta(
        canonical="nutrient_removal_mg_kg_per_ha",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="kg_per_ha",
    ),
    # DERIVE: oxide nutrients (drop stored)
    "nutrient_removal_p2o5_kg_ha": FieldMeta(
        canonical="nutrient_removal_p2o5_kg_ha",
        field_type="T4", layer="none", disposition="DERIVE", unit="kg_per_ha",
    ),
    "nutrient_removal_k2o_kg_ha": FieldMeta(
        canonical="nutrient_removal_k2o_kg_ha",
        field_type="T4", layer="none", disposition="DERIVE", unit="kg_per_ha",
    ),
    # KEEP: germination temps
    "germination_temp_c_min": FieldMeta(
        canonical="germination_temp_c_min",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="°C",
    ),
    "germination_temp_c_opt": FieldMeta(
        canonical="germination_temp_c_opt",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="°C",
    ),
    "germination_temp_c_max": FieldMeta(
        canonical="germination_temp_c_max",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="°C",
    ),
    # KEEP: soil pH
    "soil_ph_target": FieldMeta(
        canonical="soil_ph_target",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="pH",
    ),
    "soil_ph_liming_threshold": FieldMeta(
        canonical="soil_ph_liming_threshold",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="pH",
    ),
    # KEEP: storage numerics
    "storage_temp_c_min": FieldMeta(
        canonical="storage_temp_c_min",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="°C",
    ),
    "storage_temp_c_max": FieldMeta(
        canonical="storage_temp_c_max",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="°C",
    ),
    "storage_rh_pct_min": FieldMeta(
        canonical="storage_rh_pct_min",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="pct",
    ),
    "storage_rh_pct_max": FieldMeta(
        canonical="storage_rh_pct_max",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="pct",
    ),
    "storage_life_days": FieldMeta(
        canonical="storage_life_days",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    # RENAME: days_in_gh_total → days_in_nursery (Canon §7.1)
    "days_in_gh_total": FieldMeta(
        canonical="days_in_nursery",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="days",
    ),
    "days_in_nursery": FieldMeta(
        canonical="days_in_nursery",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    # RENAME: days_to_first_potting → nursery_days_to_potting (F-190-MIG-03)
    "days_to_first_potting": FieldMeta(
        canonical="nursery_days_to_potting",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="days",
    ),
    "nursery_days_to_potting": FieldMeta(
        canonical="nursery_days_to_potting",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    # RENAME: days_to_germinate_gh → nursery_days_to_germinate (F-190-MIG-03)
    "days_to_germinate_gh": FieldMeta(
        canonical="nursery_days_to_germinate",
        field_type="T1", layer="enrichment", disposition="RENAME", unit="days",
    ),
    "nursery_days_to_germinate": FieldMeta(
        canonical="nursery_days_to_germinate",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),
    # KEEP: succession_interval_weeks
    "succession_interval_weeks": FieldMeta(
        canonical="succession_interval_weeks",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="weeks",
    ),
    # DERIVE: plants_per_m2, avg_revenue_per_bed_m (drop stored)
    "plants_per_m2": FieldMeta(
        canonical="plants_per_m2",
        field_type="T4", layer="none", disposition="DERIVE", unit="count",
    ),
    "avg_revenue_per_bed_m": FieldMeta(
        canonical="avg_revenue_per_bed_m",
        field_type="T4", layer="none", disposition="DERIVE", unit=None,
    ),
    # days_in_nursery_cell (WP-CB-1 legacy — keep for now; not in Canon §7 as rename)
    "days_in_nursery_cell": FieldMeta(
        canonical="days_in_nursery_cell",
        field_type="T1", layer="enrichment", disposition="KEEP", unit="days",
    ),

    # -------------------------------------------------------------------------
    # §7.2 Categorical / list attributes (T2/T3 → crop_attribute)
    # -------------------------------------------------------------------------
    "planting_method": FieldMeta(
        canonical="planting_method",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "frost_tolerance_class": FieldMeta(
        canonical="frost_tolerance_class",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "planting_season": FieldMeta(
        canonical="season_window",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "season_window": FieldMeta(
        canonical="season_window",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "seed_months_list": FieldMeta(
        canonical="sowing_months",
        field_type="T3", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "sowing_months": FieldMeta(
        canonical="sowing_months",
        field_type="T3", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "transplant_months_list": FieldMeta(
        canonical="transplant_months",
        field_type="T3", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "transplant_months": FieldMeta(
        canonical="transplant_months",
        field_type="T3", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "storage_ethylene_sensitivity": FieldMeta(
        canonical="storage_ethylene_sensitivity",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    # DERIVE/DROP (use numeric storage_life_days)
    "storage_life_text": FieldMeta(
        canonical="storage_life_text",
        field_type="T4", layer="none", disposition="DERIVE", unit=None,
    ),
    "variety_provider": FieldMeta(
        canonical="variety_provider",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "rootstock_variety": FieldMeta(
        canonical="rootstock_variety",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "harvest_unit": FieldMeta(
        canonical="harvest_unit",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "harvest_stage": FieldMeta(
        canonical="harvest_stage",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),

    # -------------------------------------------------------------------------
    # §16 — Canon Amendment v1.3.0 (WP-CB-MIG2 new fields)
    # -------------------------------------------------------------------------

    # T5 identity/ops columns
    "seeder_model": FieldMeta(
        canonical="seeder",
        field_type="T5", layer="column", disposition="ALIAS", unit=None,
    ),
    "seeder": FieldMeta(
        canonical="seeder",
        field_type="T5", layer="column", disposition="KEEP", unit=None,
    ),
    "seeder_settings": FieldMeta(
        canonical="seeder_settings",
        field_type="T5", layer="column", disposition="KEEP", unit=None,
    ),

    # T1 enrichment facts (irrigation / harvest / succession)
    "drip_lines_per_bed": FieldMeta(
        canonical="drip_lines_per_bed",
        field_type="T1", layer="enrichment", disposition="NEW", unit="count",
    ),
    "labor_rate_harvest": FieldMeta(
        canonical="labor_rate_harvest",
        field_type="T1", layer="enrichment", disposition="NEW", unit="units_per_hr",
    ),
    "labor_rate_wash": FieldMeta(
        canonical="labor_rate_wash",
        field_type="T1", layer="enrichment", disposition="NEW", unit="units_per_hr",
    ),
    "plantings_per_season": FieldMeta(
        canonical="plantings_per_season",
        field_type="T1", layer="enrichment", disposition="NEW", unit="count",
    ),
    "harvest_weeks_span": FieldMeta(
        canonical="harvest_weeks_span",
        field_type="T1", layer="enrichment", disposition="NEW", unit="weeks",
    ),

    # T2/T3 crop_attribute attributes (CLOSED-ENUM or OPEN-VOCAB)
    "irrigation_type": FieldMeta(
        canonical="irrigation_type",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "root_depth_class": FieldMeta(
        canonical="root_depth_class",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "needs_summer_shade": FieldMeta(
        canonical="needs_summer_shade",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "unit_size": FieldMeta(
        canonical="unit_size",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "common_pests": FieldMeta(
        canonical="common_pests",
        field_type="T3", layer="crop_attribute", disposition="ATTR", unit=None,
    ),
    "foliar_feeding_program": FieldMeta(
        canonical="foliar_feeding_program",
        field_type="T2", layer="crop_attribute", disposition="ATTR", unit=None,
    ),

    # Aliases: sale_unit → harvest_unit (D-MIG2-1); no duplicate storage
    "sale_unit": FieldMeta(
        canonical="harvest_unit",
        field_type="T2", layer="crop_attribute", disposition="ALIAS", unit=None,
    ),
}

# ---------------------------------------------------------------------------
# Derived lookup maps
# ---------------------------------------------------------------------------

# Rename map: old_name → canonical_name (only RENAME entries)
RENAME_MAP: dict[str, str] = {
    old: meta.canonical
    for old, meta in FIELD_REGISTRY.items()
    if meta.disposition == "RENAME"
}

# Alias map: ANY old name (incl. RENAME entries) → canonical name
# Used for one-cycle consumer read-compatibility
ALIAS_MAP: dict[str, str] = {
    old: meta.canonical
    for old, meta in FIELD_REGISTRY.items()
}

# Derived / drop fields (T4 — stored rows to delete)
DERIVE_DROP_FIELDS: frozenset[str] = frozenset({
    "yield_per_m2_kg",
    "nutrient_removal_p2o5_kg_ha",
    "nutrient_removal_k2o_kg_ha",
    "plants_per_m2",
    "avg_revenue_per_bed_m",
    "storage_life_text",
})


def get_canonical(field_name: str) -> str:
    """Return canonical name for field_name (identity if already canonical or unknown)."""
    meta = FIELD_REGISTRY.get(field_name)
    if meta is None:
        return field_name
    return meta.canonical
