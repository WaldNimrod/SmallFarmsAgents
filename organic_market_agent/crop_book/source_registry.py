"""Source registry — declarative 7-class taxonomy for crop-book data enrichment.

Classes (trust order, highest first):
    EX  Expert override    — team_00 hardcoded overrides (hard override, always wins)
    NI  Nimrod-Input       — files/links supplied by team_00 (hard override over PR/OP)
    PR  Prescriptive       — JMF MasterClass (curated agronomic benchmarks)
    OP  Operational        — Tend farm records (actual observed data)
    MK  Market index       — OMA community price (design-registered, importer in WP-B)
    WB  Web / third-party  — external databases (design-registered, importer in WP-B)
    UC  User-Community     — user-submitted data (moderation gate required)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpec:
    label: str
    cls: str                    # class code: EX/NI/PR/OP/MK/WB/UC
    weight: float | None        # None = hard override (EX/NI); not included in blend
    is_hard_override: bool = False   # True → always wins; never blended
    requires_moderation: bool = False  # True → excluded from blend until weight set


# ---------------------------------------------------------------------------
# Registry — extend here to add new sources.  No reconciler changes needed.
# ---------------------------------------------------------------------------
SOURCE_REGISTRY: dict[str, SourceSpec] = {
    # --- EX: Expert override (team_00 hardcoded) ---
    "team_00": SourceSpec("team_00", "EX", weight=None, is_hard_override=True),

    # --- NI: Nimrod-Input (files/links; label format "NI:<name>") ---
    # Registered on load by ni_importer; sentinel here for class detection:
    "_NI_CLASS_SENTINEL": SourceSpec(
        "_NI_CLASS_SENTINEL", "NI", weight=None, is_hard_override=True
    ),

    # --- PR: Prescriptive (JMF MasterClass) ---
    "JMF": SourceSpec("JMF", "PR", weight=0.70),

    # --- OP: Operational (Tend, one entry per year) ---
    "Tend_2018": SourceSpec("Tend_2018", "OP", weight=0.55),
    "Tend_2019": SourceSpec("Tend_2019", "OP", weight=0.55),
    "Tend_2020": SourceSpec("Tend_2020", "OP", weight=0.55),
    "Tend_2021": SourceSpec("Tend_2021", "OP", weight=0.55),
    "Tend_2022": SourceSpec("Tend_2022", "OP", weight=0.55),
    "Tend": SourceSpec("Tend", "OP", weight=0.55),          # legacy flat export

    # --- MK: Market index (design-registered; importer in WP-B) ---
    "_MK_CLASS_SENTINEL": SourceSpec("_MK_CLASS_SENTINEL", "MK", weight=0.40),

    # --- WB: Web / third-party (design-registered; importer in WP-B) ---
    "_WB_CLASS_SENTINEL": SourceSpec("_WB_CLASS_SENTINEL", "WB", weight=0.30),

    # --- UC: User-Community (design-registered; moderation gate required) ---
    "_UC_CLASS_SENTINEL": SourceSpec(
        "_UC_CLASS_SENTINEL", "UC", weight=0.15, requires_moderation=True
    ),
}


def get_source_spec(source_label: str) -> SourceSpec:
    """Look up SourceSpec by label; detect class from prefix for dynamic labels.

    Dynamic label conventions:
        "NI:<name>"  → NI class  (Nimrod-provided file/link)
        "OMA:<name>" → MK class  (OMA market index product)
        "WB:<name>"  → WB class  (web / third-party)
        "UC:<id>"    → UC class  (user-community; moderation required)

    Unknown labels fall back to WB with reduced weight (0.20).
    """
    if source_label in SOURCE_REGISTRY:
        return SOURCE_REGISTRY[source_label]
    if source_label.startswith("NI:"):
        return SourceSpec(source_label, "NI", weight=None, is_hard_override=True)
    if source_label.startswith("OMA:"):
        return SourceSpec(source_label, "MK", weight=0.40)
    if source_label.startswith("WB:"):
        return SourceSpec(source_label, "WB", weight=0.30)
    if source_label.startswith("UC:"):
        return SourceSpec(source_label, "UC", weight=0.15, requires_moderation=True)
    # Unknown source: treat as low-trust WB
    return SourceSpec(source_label, "WB", weight=0.20)


def is_hard_override(source_label: str) -> bool:
    """Return True if this source always wins (EX or NI class)."""
    return get_source_spec(source_label).is_hard_override


# Trust-order rank: lower index = higher priority (for hard_winner selection)
CLASS_RANK: dict[str, int] = {
    "EX": 0,
    "NI": 1,
    "PR": 2,
    "OP": 3,
    "MK": 4,
    "WB": 5,
    "UC": 6,
}
