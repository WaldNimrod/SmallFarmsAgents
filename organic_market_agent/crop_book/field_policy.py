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
    "avg_yield_per_bed_m": FieldPolicy(
        trust_order=("EX", "NI", "OP", "PR", "WB"),
        blend_strategy="weighted_mean",
        outlier=OutlierConfig(z_threshold=3.0),
        multi_year_op_mean=True,
    ),
    "documented_price": FieldPolicy(
        trust_order=("EX", "NI", "OP", "MK", "WB"),
        blend_strategy="latest_op",
        outlier=OutlierConfig(z_threshold=3.0),
    ),
    "in_row_spacing_cm": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP", "WB"),
        blend_strategy="hard_winner",
        outlier=OutlierConfig(z_threshold=3.5),
    ),
    "rows_per_bed": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP"),
        blend_strategy="hard_winner",
    ),
    "planting_season": FieldPolicy(
        trust_order=("EX", "NI", "PR", "OP", "WB"),
        blend_strategy="hard_winner",
    ),
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
}

# Default policy for fields not in the table
_DEFAULT_POLICY = FieldPolicy(
    trust_order=("EX", "NI", "PR", "OP", "MK", "WB", "UC"),
    blend_strategy="hard_winner",
)


def get_field_policy(field_name: str) -> FieldPolicy:
    """Return the policy for a field, falling back to default."""
    return FIELD_POLICY.get(field_name, _DEFAULT_POLICY)
