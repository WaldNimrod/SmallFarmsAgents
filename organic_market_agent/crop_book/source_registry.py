"""Source registry — declarative 8-class taxonomy for crop-book data enrichment.

Classes (trust order, highest first):
    EX  Expert override    — team_00 hardcoded overrides (hard override, always wins)
    NI  Nimrod-Input       — files/links supplied by team_00 (hard override over PR/OP)
    PR  Prescriptive       — JMF MasterClass / university extension (curated)
    WR  Web-Research       — AI-synthesized research (team_80 multi-engine scout)
    OP  Operational        — Tend / farm-records (actual observed data)
    MK  Market index       — OMA community price (design-registered)
    WB  Web / third-party  — external databases (design-registered)
    UC  User-Community     — user-submitted data (moderation gate required)

WP-C5 Phase A change (2026-05-28):
    SOURCE_REGISTRY is now the **default seed** (consumed by migration 056
    and used as the durable fallback when the DB is unavailable). The
    canonical runtime resolver is :func:`get_source_spec`, which delegates
    to :mod:`organic_market_agent.crop_book.source_weights_db` so weights
    can be re-tuned via a single SQL UPDATE per team_00 critical
    requirement in DECISION_RECORD_SFA-S003-P002-WP-C5_v1.0.0 §Decision 5.
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

    # --- WP-C1: Israeli structured + JMF cover crops ---
    "NI:groworganic": SourceSpec("NI:groworganic", "NI", weight=None, is_hard_override=True),
    "NI:bustan": SourceSpec("NI:bustan", "NI", weight=None, is_hard_override=True),
    "OP:Idan_2017": SourceSpec("OP:Idan_2017", "OP", weight=0.55),
    "PR:jmf_cover_crops": SourceSpec("PR:jmf_cover_crops", "PR", weight=0.70),

    # --- WP-C4: Web sources (team_80 multi-engine scout) ---
    "PR:uc_anr_germination": SourceSpec("PR:uc_anr_germination", "PR", weight=0.70),
    "PR:purdue_germination": SourceSpec("PR:purdue_germination", "PR", weight=0.70),
    "PR:osu_frost_tolerance": SourceSpec("PR:osu_frost_tolerance", "PR", weight=0.70),
    "PR:csu_planting_guide": SourceSpec("PR:csu_planting_guide", "PR", weight=0.70),
    "PR:umn_field_planning": SourceSpec("PR:umn_field_planning", "PR", weight=0.70),
    "PR:umd_soil_ph": SourceSpec("PR:umd_soil_ph", "PR", weight=0.70),
    "PR:ne_veg_guide": SourceSpec("PR:ne_veg_guide", "PR", weight=0.70),
    "PR:fao_fertilizer_use": SourceSpec("PR:fao_fertilizer_use", "PR", weight=0.70),
    "NI:il_moa_garden_guide": SourceSpec(
        "NI:il_moa_garden_guide", "NI", weight=None, is_hard_override=True,
    ),
    "NI:shaham_extension": SourceSpec(
        "NI:shaham_extension", "NI", weight=None, is_hard_override=True,
    ),
    "OP:vital_seeds_count": SourceSpec("OP:vital_seeds_count", "OP", weight=0.55),
    "OP:osborne_seed_count": SourceSpec("OP:osborne_seed_count", "OP", weight=0.55),
    "PR:uf_ifas_companion": SourceSpec("PR:uf_ifas_companion", "PR", weight=0.70),
    "PR:uc_davis_postharvest": SourceSpec("PR:uc_davis_postharvest", "PR", weight=0.70),

    # --- WP-C3: Curtis Stone + Idan seedlings + FRANCHI + Idan 2018 ---
    "OP:CurtisStone": SourceSpec("OP:CurtisStone", "OP", weight=0.55),
    "NI:curtis_stone_book": SourceSpec("NI:curtis_stone_book", "NI", weight=None, is_hard_override=True),
    "OP:Idan_seedlings": SourceSpec("OP:Idan_seedlings", "OP", weight=0.55),
    "OP:FRANCHI_catalog": SourceSpec("OP:FRANCHI_catalog", "OP", weight=0.55),
    "OP:Idan_2018": SourceSpec("OP:Idan_2018", "OP", weight=0.55),

    # --- WP-C5 Phase A: WR (Web-Research / AI-synthesized) class sentinel ---
    # team_00 Decision #5 — Option B (Moderate) weight 0.60.
    # Tunable via UPDATE crop_source_weights SET weight = ... WHERE source_label = 'WR:*'
    "_WR_CLASS_SENTINEL": SourceSpec(
        "_WR_CLASS_SENTINEL", "WR", weight=0.60
    ),

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
    """Look up SourceSpec by label.

    WP-C5 Phase A: delegates to :mod:`source_weights_db` (DB-backed) and
    falls back to the constants below if the DB row is missing OR the DB
    is unavailable.  Caller-facing signature is unchanged so existing
    reconciler / enrichment-runner code is not affected.

    Dynamic label conventions (in fallback):
        "NI:<name>"  → NI class  (Nimrod-provided file/link)
        "WR:<name>"  → WR class  (AI-synthesized research, weight 0.60)
        "OP:<name>"  → OP class  (operational farm data, weight 0.55)
        "PR:<name>"  → PR class  (published research, weight 0.70)
        "OMA:<name>" → MK class  (OMA market index product)
        "WB:<name>"  → WB class  (web / third-party)
        "UC:<id>"    → UC class  (user-community; moderation required)

    Unknown labels fall back to WB with reduced weight (0.20).
    """
    # Try DB-backed resolver first.  Returns a source_weights_db.SourceSpec
    # which is field-compatible with this module's SourceSpec.
    try:
        from organic_market_agent.crop_book import source_weights_db
        db_spec = source_weights_db.get_source_spec(source_label)
        # Convert to local SourceSpec for identity-preserving callers.
        return SourceSpec(
            label=db_spec.label,
            cls=db_spec.cls,
            weight=db_spec.weight,
            is_hard_override=db_spec.is_hard_override,
            requires_moderation=db_spec.requires_moderation,
        )
    except Exception:
        # Total-failure fallback: pure-Python resolution.
        pass

    return _resolve_constants(source_label)


def _resolve_constants(source_label: str) -> SourceSpec:
    """Pure-Python fallback resolver (no DB).  Also used by source_weights_db
    as its last-resort fallback."""
    if source_label in SOURCE_REGISTRY:
        return SOURCE_REGISTRY[source_label]
    if source_label.startswith("NI:"):
        return SourceSpec(source_label, "NI", weight=None, is_hard_override=True)
    if source_label.startswith("WR:"):
        return SourceSpec(source_label, "WR", weight=0.60)
    if source_label.startswith("OP:"):
        return SourceSpec(source_label, "OP", weight=0.55)
    if source_label.startswith("PR:"):
        return SourceSpec(source_label, "PR", weight=0.70)
    if source_label.startswith("OMA:"):
        return SourceSpec(source_label, "MK", weight=0.40)
    if source_label.startswith("MK:"):
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


# Trust-order rank: lower index = higher priority (for hard_winner selection).
# WP-C5 Phase A: WR slotted between PR and OP — Decision #5 rationale:
# WR > OP because it draws on multiple published sources; WR < PR because
# it is not first-party / peer-reviewed.
CLASS_RANK: dict[str, int] = {
    "EX": 0,
    "NI": 1,
    "PR": 2,
    "WR": 3,
    "OP": 4,
    "MK": 5,
    "WB": 6,
    "UC": 7,
}
