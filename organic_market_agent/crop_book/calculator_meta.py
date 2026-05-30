"""Calculator metadata registry for Crop Book v1 — SFA-S003-P004-WP-CB-1.

Maps each calculator id (1..14) to its audience, required book fields,
assumption keys used, and user inputs.  This drives the enabled/disabled
state per crop without coupling to the calculator implementations.

Reference: Calculator Catalog §6 (field → calculator dependency map), LOD400 §5.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Metadata registry
# ---------------------------------------------------------------------------
# Structure per calc:
#   audience:              "G" | "F" | "B"  (gardener / farmer / both)
#   required_book_fields:  list[str]  — BOOK values whose absence disables the calc
#   assumption_keys:       list[str]  — AssumptionFields used (always have defaults)
#   user_inputs:           list[str]  — direct user-typed values (never disable)

CALCULATOR_META: dict[int, dict] = {
    1: {
        "audience": "B",
        "required_book_fields": ["rows_per_bed", "in_row_spacing_cm", "seeds_per_gram"],
        "assumption_keys": ["germination_rate", "oversow"],
        "user_inputs": ["bed_length_m", "seeds_per_hole"],
    },
    2: {
        "audience": "B",
        "required_book_fields": ["rows_per_bed", "in_row_spacing_cm"],
        "assumption_keys": [],
        "user_inputs": ["bed_length_m"],
    },
    3: {
        "audience": "F",
        "required_book_fields": ["days_in_nursery_cell"],
        "assumption_keys": ["tray_cells", "oversow"],
        "user_inputs": ["plants", "field_set_date"],
    },
    4: {
        "audience": "B",
        "required_book_fields": ["days_to_maturity", "planting_method"],
        "assumption_keys": [],
        "user_inputs": ["target_harvest_date"],
        # days_in_nursery_cell is conditionally required (transplant only);
        # included for completeness — UI checks planting_method first
    },
    5: {
        "audience": "B",
        "required_book_fields": [
            "days_to_maturity",
            "harvest_window_max_days",
            "planting_method",
        ],
        "assumption_keys": [],
        "user_inputs": ["sow_date"],
    },
    6: {
        "audience": "F",
        "required_book_fields": ["succession_interval_weeks"],
        "assumption_keys": [],
        "user_inputs": ["first_sow_date", "num_successions_or_season_end"],
    },
    7: {
        "audience": "F",
        "required_book_fields": ["avg_yield_per_bed_m"],
        "assumption_keys": ["std_bed_length_m"],
        "user_inputs": ["target_kg"],
    },
    8: {
        "audience": "B",
        "required_book_fields": ["avg_yield_per_bed_m"],
        "assumption_keys": [],
        "user_inputs": ["bed_length_m"],
    },
    9: {
        "audience": "F",
        "required_book_fields": [
            "avg_yield_per_bed_m",
            "documented_price",
            "documented_price_unit",
        ],
        "assumption_keys": [],
        "user_inputs": ["bed_length_m"],
    },
    10: {
        "audience": "B",
        "required_book_fields": ["rows_per_bed", "in_row_spacing_cm"],
        "assumption_keys": ["bed_width"],
        "user_inputs": [],
    },
    11: {
        "audience": "B",
        "required_book_fields": ["days_to_maturity", "frost_tolerance_class"],
        "assumption_keys": ["hardiness_offset"],
        "user_inputs": ["last_frost_date", "first_frost_date"],
    },
    12: {
        "audience": "F",
        "required_book_fields": ["nutrient_removal_n_kg_ha"],
        "assumption_keys": ["compost_N_pct", "application_efficiency"],
        "user_inputs": ["area_m2"],
    },
    13: {
        "audience": "F",
        "required_book_fields": ["avg_yield_per_bed_m", "documented_price"],
        "assumption_keys": [],
        "user_inputs": ["bed_meters"],
    },
    14: {
        "audience": "F",
        "required_book_fields": [],  # uses grams from #1 (user input chain)
        "assumption_keys": [],
        "user_inputs": ["grams_needed", "seed_price_per_g_or_pack_price"],
    },
}

# Sentinel for field states — mirrors Gap-Fill Plan §2
_FIELD_MISSING = "MISSING"
_FIELD_VALIDATED = "VALIDATED"
_FIELD_UNVALIDATED = "UNVALIDATED"


def calc_enabled(calc_id: int, field_state: dict[str, str]) -> bool:
    """Return True if the calculator can run for a crop with the given field_state.

    A calculator is DISABLED iff any required_book_field has state "MISSING".
    UNVALIDATED fields allow the calculator to run (result shown with asterisk).
    AssumptionFields and user inputs never cause a disabled state.

    Args:
        calc_id:     1..14
        field_state: dict mapping field_name -> "VALIDATED" | "UNVALIDATED" | "MISSING"
                     Fields absent from the dict are treated as MISSING.

    Returns:
        True if enabled, False if disabled.
    """
    meta = CALCULATOR_META[calc_id]
    for field in meta["required_book_fields"]:
        state = field_state.get(field, _FIELD_MISSING)
        if state == _FIELD_MISSING:
            return False
    return True
