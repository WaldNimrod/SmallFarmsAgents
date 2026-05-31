"""Canon §6.1 — Unit registry + variant normalization map.

UNIT_REGISTRY: canonical unit string per dimension.
UNIT_VARIANT_MAP: {field_name → {raw_unit → canonical_unit}} — exhaustive per-field map
    constructed from the live DB sweep (Canon §6.1 + errata F-190-CB0-03).

normalize_unit(field_name, raw_unit) -> str  — idempotent, returns canonical unit.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Canonical unit strings (one per dimension)
# ---------------------------------------------------------------------------
UNIT_REGISTRY: dict[str, str] = {
    "temperature":     "°C",
    "duration_days":   "days",
    "duration_weeks":  "weeks",
    "length":          "cm",
    "yield_per_bed_m": "kg_per_bed_m",
    "yield_per_m2":    "kg_per_m2",       # derived only — not stored
    "nutrient_load":   "kg_per_ha",
    "price_ils_kg":    "ILS_per_kg",
    "price_ils_bunch": "ILS_per_bunch",
    "price_ils_unit":  "ILS_per_unit",
    "ratio_pct":       "pct",
    "acidity":         "pH",
    "seed_density":    "seeds_per_g",
    "count":           "count",
}

# ---------------------------------------------------------------------------
# Per-field unit variant map (field_name → {raw_variant → canonical})
# ---------------------------------------------------------------------------
# Each field key maps all observed live variants (incl. NULL/blank) to the
# canonical string.  Fields not listed here have no known unit-chaos and pass
# through their existing unit unchanged (already canonical).
#
# Special sentinel: None → canonical (handles NULL DB values)
# ---------------------------------------------------------------------------

_TEMP_MAP: dict[str | None, str] = {
    "°C": "°C",
    "celsius": "°C",
    "C": "°C",
    None: "°C",
    "": "°C",
}

UNIT_VARIANT_MAP: dict[str, dict[str | None, str]] = {
    # Temperature fields
    "germination_temp_c_min": _TEMP_MAP,
    "germination_temp_c_opt": _TEMP_MAP,
    "germination_temp_c_max": _TEMP_MAP,
    "storage_temp_c_min":     _TEMP_MAP,
    "storage_temp_c_max":     _TEMP_MAP,

    # yield_per_bed_m: bare "kg" is a sloppy unit for already-per-bed-m values
    # (Canon §6.1 errata F-190-CB0-03 — 63 rows; value stays unchanged)
    "avg_yield_per_bed_m": {
        "kg":          "kg_per_bed_m",
        "kg/m":        "kg_per_bed_m",
        "kg_per_bed_m": "kg_per_bed_m",
        None:          "kg_per_bed_m",
        "":            "kg_per_bed_m",
    },
    # After rename, the field key changes — include both for idempotency
    "yield_per_bed_m": {
        "kg":          "kg_per_bed_m",
        "kg/m":        "kg_per_bed_m",
        "kg_per_bed_m": "kg_per_bed_m",
        None:          "kg_per_bed_m",
        "":            "kg_per_bed_m",
    },

    # yield_per_m2 — derived/drop; only matters for conversion before drop
    "yield_per_m2_kg": {
        "kg/m2":  "kg_per_m2",
        "kg/m²":  "kg_per_m2",
        "kg_per_m2": "kg_per_m2",
        None:     "kg_per_m2",
        "":       "kg_per_m2",
    },

    # rows_per_bed: "rows" and blank → "count"
    "rows_per_bed": {
        "count": "count",
        "rows":  "count",
        None:    "count",
        "":      "count",
    },

    # soil_ph: blank → "pH"
    "soil_ph_target": {
        "pH": "pH",
        None: "pH",
        "":   "pH",
    },
    "soil_ph_liming_threshold": {
        "pH": "pH",
        None: "pH",
        "":   "pH",
    },

    # nutrients
    "nutrient_removal_n_kg_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_p_kg_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_k_kg_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_ca_kg_ha":   {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_mg_kg_ha":   {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_p2o5_kg_ha": {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_k2o_kg_ha":  {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    # After rename: _kg_per_ha suffix
    "nutrient_removal_n_kg_per_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_p_kg_per_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_k_kg_per_ha":    {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_ca_kg_per_ha":   {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},
    "nutrient_removal_mg_kg_per_ha":   {"kg/ha": "kg_per_ha", "kg_per_ha": "kg_per_ha", None: "kg_per_ha", "": "kg_per_ha"},

    # seeds_per_g
    "seeds_per_gram": {"seeds/g": "seeds_per_g", "seeds_per_g": "seeds_per_g", None: "seeds_per_g", "": "seeds_per_g"},
    "seeds_per_g":    {"seeds/g": "seeds_per_g", "seeds_per_g": "seeds_per_g", None: "seeds_per_g", "": "seeds_per_g"},

    # price — qualifier is preserved (ILS/kg → ILS_per_kg, etc.)
    "documented_price": {
        "ILS/kg":    "ILS_per_kg",
        "ILS/bunch": "ILS_per_bunch",
        "ILS/unit":  "ILS_per_unit",
        "ILS_per_kg":    "ILS_per_kg",
        "ILS_per_bunch": "ILS_per_bunch",
        "ILS_per_unit":  "ILS_per_unit",
        None: "ILS_per_kg",   # default fallback
        "":   "ILS_per_kg",
    },
    "price_documented": {
        "ILS/kg":    "ILS_per_kg",
        "ILS/bunch": "ILS_per_bunch",
        "ILS/unit":  "ILS_per_unit",
        "ILS_per_kg":    "ILS_per_kg",
        "ILS_per_bunch": "ILS_per_bunch",
        "ILS_per_unit":  "ILS_per_unit",
        None: "ILS_per_kg",
        "":   "ILS_per_kg",
    },

    # ratio / storage_rh_pct
    "storage_rh_pct_min": {"%": "pct", "pct": "pct", None: "pct", "": "pct"},
    "storage_rh_pct_max": {"%": "pct", "pct": "pct", None: "pct", "": "pct"},
}

# All canonical unit strings — used for AC-02 post-check
ALL_CANONICAL_UNITS: set[str] = {
    "°C", "days", "weeks", "cm", "kg_per_bed_m", "kg_per_m2",
    "kg_per_ha", "ILS_per_kg", "ILS_per_bunch", "ILS_per_unit",
    "pct", "pH", "seeds_per_g", "count",
}


def normalize_unit(field_name: str, raw_unit: str | None) -> str:
    """Return the canonical unit for (field_name, raw_unit).

    If a field-specific map exists, look up raw_unit (handling None/blank).
    Otherwise return raw_unit as-is (already canonical or unknown field).

    Idempotent: canonical units pass through unchanged.
    """
    field_map = UNIT_VARIANT_MAP.get(field_name)
    if field_map is None:
        return raw_unit or ""
    key = raw_unit if raw_unit else None
    # Try exact key first; then try empty string if None not in map
    if key in field_map:
        return field_map[key]
    if raw_unit == "" and None in field_map:
        return field_map[None]
    # Unknown variant — return as-is (will be caught by AC-02 check)
    return raw_unit or ""
