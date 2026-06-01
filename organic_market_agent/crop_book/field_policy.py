"""Field policy — trust order, blend strategy, and outlier config per field.

Each entry in FIELD_POLICY determines how reconcile_field() handles that field:
  trust_order:        class priority list (highest first)
  blend_strategy:     "weighted_mean" | "hard_winner" | "latest_op"
  outlier:            OutlierConfig (domain_fn + z_threshold)
  multi_year_op_mean: True → average all OP values first before blending
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass(frozen=True)
class OutlierConfig:
    domain_fn: Optional[Callable[[str, float], bool]] = None
    """Optional domain-specific outlier check: (name_he, value) -> bool (True = outlier)."""
    z_threshold: float = 3.5
    """Modified Z-score threshold for statistical outlier gate."""


@dataclass(frozen=True)
class FieldPolicy:
    trust_order: tuple[str, ...]
    """Source class priority: first = highest trust."""
    blend_strategy: str
    """
    weighted_mean : weighted average across non-override, non-outlier sources
    hard_winner   : take value from highest-class source present
    latest_op     : OP value with lexicographically latest source label wins;
                    hard_winner for non-OP sources if no OP present
    """
    outlier: OutlierConfig = field(default_factory=OutlierConfig)
    multi_year_op_mean: bool = False
    """If True, average all OP-class values first, then treat as one OP observation."""


# ---------------------------------------------------------------------------
# Domain outlier check for leaf-crop DTM
# ---------------------------------------------------------------------------
def _dtm_leaf_crop_check(name_he: str, value: float) -> bool:
    """Return True if this DTM value is a domain outlier (near-harvest snapshot)."""
    from organic_market_agent.crop_book.constants import OUTLIER_CROPS
    return name_he in OUTLIER_CROPS and value < 20


# ---------------------------------------------------------------------------
# Field policy table — one entry per reconciled field
# ---------------------------------------------------------------------------
FIELD_POLICY: dict[str, FieldPolicy] = {
    "days_to_maturity": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(domain_fn=_dtm_leaf_crop_check, z_threshold=3.5),
    ),
    # WI-6 / AC-07 / F-CB1-UI-01: renamed avg_yield_per_bed_m → yield_per_bed_m
    "yield_per_bed_m": FieldPolicy(
        trust_order=("EX", "NI", "OP", "PR", "WB"),
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(z_threshold=3.0),
        multi_year_op_mean=True,
    ),
    # WI-6 / AC-07 / F-CB1-UI-01: renamed documented_price → price_documented
    "price_documented": FieldPolicy(
        trust_order=("EX", "NI", "OP", "MK", "WB"),
        blend_strategy="latest_op",
        outlier=OutlierConfig(z_threshold=3.0),
    ),
    # WI-6 / AC-07 / F-CB1-UI-01: renamed in_row_spacing_cm → spacing_in_row_cm
    "spacing_in_row_cm": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP", "WB"),
        blend_strategy="hard_winner",
        outlier=OutlierConfig(z_threshold=3.5),
    ),
    "rows_per_bed": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    # WI-6 / AC-07: planting_season REMOVED from FIELD_POLICY.
    # season_window is a T2 attribute (resolved by attribute_resolver via
    # _COLUMN_ORIGIN_ATTRS: season_window→planting_season → crop_attribute).
    # It must NOT exist in the enrichment policy dict (layer-ownership violation).
    "harvest_window_max_days": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    "harvest_window_min_days": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    "rootstock_variety": FieldPolicy(
        trust_order=("EX", "NI", "OP"),
        blend_strategy="hard_winner",
    ),
    # --- WP-C4 web-source fields ---
    "germination_temp_c_min": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "germination_temp_c_opt": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "germination_temp_c_max": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "frost_tolerance_class": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    "soil_ph_target": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "soil_ph_liming_threshold": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "nutrient_removal_n_kg_ha": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "nutrient_removal_p_kg_ha": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "nutrient_removal_k_kg_ha": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "nutrient_removal_ca_kg_ha": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "nutrient_removal_mg_kg_ha": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
    "seeds_per_gram": FieldPolicy(
        trust_order=("EX", "NI", "OP", "PR"),
        blend_strategy="weighted_mean",
    ),
    # --- WP-CB-1 calculator fields ---
    "days_in_nursery_cell": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(z_threshold=3.5),
    ),
    "succession_interval_weeks": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    # --- WP-CB-MIG2 T1 facts (Canon §16, Amendment v1.3.0) ---
    # Irrigation
    "drip_lines_per_bed": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",  # discrete count, hard winner appropriate
    ),
    # Harvest labor rates (units_per_hr)
    "labor_rate_harvest": FieldPolicy(
        trust_order=("EX", "NI", "OP", "PR"),
        blend_strategy="weighted_mean",  # rate — average multi-source
        multi_year_op_mean=True,
    ),
    "labor_rate_wash": FieldPolicy(
        trust_order=("EX", "NI", "OP", "PR"),
        blend_strategy="weighted_mean",
        multi_year_op_mean=True,
    ),
    # Succession
    "plantings_per_season": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",  # discrete count
    ),
    "harvest_weeks_span": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="weighted_mean",
    ),
}

# Default policy for fields not in the table
_DEFAULT_POLICY = FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP", "MK", "WB", "UC"),
    blend_strategy="hard_winner",
)


# Backward-compat aliases for locked consumers (reconciler.py, legacy importers).
# These old keys still appear in source_values and reconcile_variety() but are
# remapped to their canonical name's policy so behavior stays consistent.
# The *FIELD_POLICY dict itself* does NOT contain the old names (WI-6 / AC-07).
_FIELD_POLICY_ALIASES: dict[str, str] = {
    "avg_yield_per_bed_m":  "yield_per_bed_m",
    "documented_price":     "price_documented",
    "in_row_spacing_cm":    "spacing_in_row_cm",
    # planting_season is intentionally NOT aliased — it is T2/attribute; if old code
    # looks it up it gets the _DEFAULT_POLICY (hard_winner), which is safe.
}


def get_field_policy(field_name: str) -> FieldPolicy:
    """Return the policy for a field, falling back to default.

    WI-6 / AC-07: the canonical names are the primary keys. Old names are resolved
    via _FIELD_POLICY_ALIASES to keep locked consumer code (reconciler.py) consistent.
    """
    policy = FIELD_POLICY.get(field_name)
    if policy is not None:
        return policy
    # Try canonical alias
    canonical = _FIELD_POLICY_ALIASES.get(field_name)
    if canonical is not None:
        return FIELD_POLICY.get(canonical, _DEFAULT_POLICY)
    return _DEFAULT_POLICY
