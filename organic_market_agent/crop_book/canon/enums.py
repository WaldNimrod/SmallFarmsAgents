"""Canon §6.3 / §6.3a — Canonical enum tokens + collapse map.

ENUM_TOKENS: {attribute_name → frozenset[str]}  — CLOSED-ENUM canonical token sets.
    Open-vocab attributes (variety_provider, rootstock_variety) are NOT in ENUM_TOKENS.

ENUM_COLLAPSE: {attribute_name → {raw_value → canonical_value}}
    Maps non-canonical strings to their canonical equivalents.

canonicalize_enum(field_name, raw_value) -> str | None
    For CLOSED-ENUM: map via ENUM_COLLAPSE then validate ∈ ENUM_TOKENS.
    For OPEN-VOCAB: normalize (trim/collapse whitespace/case-fold for dedup), return as-is.
    Returns None if raw_value is None/blank.

OPEN_VOCAB_ATTRS: set[str] — attributes that accept free text (normalize, not restrict).
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Closed-enum canonical token sets (Canon §6.3a)
# ---------------------------------------------------------------------------
ENUM_TOKENS: dict[str, frozenset[str]] = {
    "planting_method": frozenset({
        "direct_seed", "transplant", "seed_tuber", "slip", "cutting",
    }),
    "frost_tolerance_class": frozenset({
        "hardy", "half_hardy", "tender", "very_tender",
    }),
    "growth_cycle": frozenset({
        "annual", "biennial", "perennial",
    }),
    "category": frozenset({
        "vegetables", "herbs", "fruits", "fruit_trees",
    }),
    "harvest_unit": frozenset({
        "kg", "bunch", "head", "case", "unit", "seedling",
    }),
    "harvest_stage": frozenset({
        "full_size", "baby_leaf", "head", "plant_sale", "seed",
    }),
    "storage_ethylene_sensitivity": frozenset({
        "none", "low", "medium", "high",
    }),
    # Canon §16a — MIG2 additions (Amendment v1.3.0)
    "irrigation_type": frozenset({
        "drip", "sprinkler", "mixed",
    }),
    "root_depth_class": frozenset({
        "shallow", "medium", "deep",
    }),
    "needs_summer_shade": frozenset({
        "none", "shade_30", "shade_40", "shade_50",
    }),
    # sowing_months / transplant_months are LIST(int) — handled separately
}

# ---------------------------------------------------------------------------
# Collapse map: raw → canonical (Canon §6.3 + errata from R2/R3)
# ---------------------------------------------------------------------------
ENUM_COLLAPSE: dict[str, dict[str, str]] = {
    "planting_method": {
        "direct_sow":             "direct_seed",  # Canon §6.3 + F-190-MIG-xx
        "greenhouse_transplant":  "transplant",   # legacy alias
        "purchase":               "transplant",   # legacy alias (seedling purchase)
        # canonical → canonical (idempotent)
        "direct_seed":   "direct_seed",
        "transplant":    "transplant",
        "seed_tuber":    "seed_tuber",
        "slip":          "slip",
        "cutting":       "cutting",
    },
    "frost_tolerance_class": {
        "semi_hardy":  "half_hardy",   # Canon §6.3 + R2 errata
        "half-hardy":  "half_hardy",   # Canon §6.3 + R2 errata (hyphen)
        # canonical → canonical
        "hardy":       "hardy",
        "half_hardy":  "half_hardy",
        "tender":      "tender",
        "very_tender": "very_tender",
    },
    "storage_ethylene_sensitivity": {
        # Normalize free-text variants to closed set
        "none":     "none",
        "low":      "low",
        "medium":   "medium",
        "high":     "high",
        # common free-text variants
        "none/nil": "none",
        "minimal":  "low",
        "moderate": "medium",
        "very high": "high",
    },
    "harvest_unit": {
        # canonical → canonical
        "kg": "kg", "bunch": "bunch", "head": "head",
        "case": "case", "unit": "unit", "seedling": "seedling",
    },
    "harvest_stage": {
        # canonical → canonical
        "full_size": "full_size", "baby_leaf": "baby_leaf",
        "head": "head", "plant_sale": "plant_sale", "seed": "seed",
    },
    # Canon §16a — MIG2 closed enums
    "irrigation_type": {
        "drip": "drip", "sprinkler": "sprinkler", "mixed": "mixed",
        # common variant aliases
        "drip_irrigation": "drip",
        "sprinkler_irrigation": "sprinkler",
    },
    "root_depth_class": {
        "shallow": "shallow", "medium": "medium", "deep": "deep",
    },
    "needs_summer_shade": {
        "none": "none",
        "shade_30": "shade_30", "30%": "shade_30", "30": "shade_30",
        "shade_40": "shade_40", "40%": "shade_40", "40": "shade_40",
        "shade_50": "shade_50", "50%": "shade_50", "50": "shade_50",
    },
}

# ---------------------------------------------------------------------------
# Open-vocab attributes: free text, normalize but do NOT restrict to a set
# ---------------------------------------------------------------------------
OPEN_VOCAB_ATTRS: set[str] = {
    "variety_provider",
    "rootstock_variety",
    # Canon §16a — MIG2 additions (Amendment v1.3.0)
    "common_pests",
    "foliar_feeding_program",
    "unit_size",
}


def _normalize_open_vocab(value: str) -> str:
    """Trim + collapse whitespace + lower-case for dedup."""
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def canonicalize_enum(field_name: str, raw_value: str | None) -> str | None:
    """Return the canonical value for (field_name, raw_value).

    CLOSED-ENUM:
        1. Strip + lower.
        2. Map via ENUM_COLLAPSE[field_name].
        3. Validate ∈ ENUM_TOKENS[field_name]; if not, log DQ warning.
        4. Return canonical or original (not rejected — caller decides).

    OPEN-VOCAB (variety_provider, rootstock_variety):
        1. Trim + collapse whitespace + lower-case (for dedup).
        2. Return normalized value (no set restriction).

    month-lists (sowing_months, transplant_months):
        Call parse_month_list() instead — this function returns None for those.
    """
    if raw_value is None:
        return None
    stripped = raw_value.strip()
    if not stripped:
        return None

    # Open-vocab: normalize only
    if field_name in OPEN_VOCAB_ATTRS:
        return _normalize_open_vocab(stripped)

    # Month lists — not handled here
    if field_name in ("sowing_months", "transplant_months",
                      "seed_months_list", "transplant_months_list"):
        return None  # use parse_month_list() instead

    # Open-vocab list attrs (T3) — normalize each token
    if field_name == "common_pests":
        # common_pests: parse as comma-delimited list of open-vocab tokens
        return None  # use parse_list_attr() instead; canonicalize_enum returns None

    # Closed-enum
    collapse = ENUM_COLLAPSE.get(field_name, {})
    lower = stripped.lower()
    canonical = collapse.get(lower) or collapse.get(stripped)
    if canonical is None:
        # Try lower-cased stripped as direct token check
        tokens = ENUM_TOKENS.get(field_name)
        if tokens and lower in tokens:
            canonical = lower
        else:
            canonical = stripped  # pass through; log if not in token set

    # Validate
    tokens = ENUM_TOKENS.get(field_name)
    if tokens and canonical not in tokens:
        logger.warning(
            "DQ: %r value %r (→%r) not in canonical token set %s",
            field_name, raw_value, canonical, sorted(tokens),
        )

    return canonical


def parse_list_attr(csv_value: str | None, field_name: str) -> list[str] | None:
    """Parse a comma-delimited string of open-vocab tokens into a normalized list.

    Used for T3 open-vocab attributes like `common_pests`.
    Each token is trimmed, whitespace-collapsed, and lower-cased for dedup.
    Returns None if input is None or blank.
    Silently drops empty tokens.
    """
    if not csv_value:
        return None
    result: list[str] = []
    seen: set[str] = set()
    for part in csv_value.split(","):
        normalized = _normalize_open_vocab(part)
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result if result else None


def parse_month_list(csv_value: str | None) -> list[int] | None:
    """Parse a CSV month string ("2,3,5") into a sorted list of ints 1–12.

    Returns None if input is None or blank.
    Silently drops values outside 1–12.
    """
    if not csv_value:
        return None
    result: list[int] = []
    for part in csv_value.split(","):
        part = part.strip()
        if part.isdigit():
            month = int(part)
            if 1 <= month <= 12:
                result.append(month)
    return sorted(set(result)) if result else None
