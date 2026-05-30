"""AssumptionField registry for Crop Book v1 — SFA-S003-P004-WP-CB-1.

Planning assumptions with sensible defaults the user can override inline.
These are NOT per-crop book data and never affect a crop's COMPLETE/PARTIAL
status.  They live here (not hard-coded in calculator logic) so both the
Python calculator layer and the UI/ingest payload share one SSOT.

Reference: LOD400 §4 / Mandatory Field Schema §3.3 / Calculator Catalog §3.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Assumption:
    key: str
    default: Union[float, dict]  # scalar OR table (e.g. hardiness_offset, tray_cells)
    unit: str
    explainer_he: str            # short inline explainer (Hebrew)
    post_url: str | None         # "read more" nimrod.bio link (None until published)


# ---------------------------------------------------------------------------
# Main ASSUMPTIONS registry (8 scalar/table keys per Schema §3.3)
# ---------------------------------------------------------------------------
ASSUMPTIONS: dict[str, Assumption] = {
    "germination_rate": Assumption(
        key="germination_rate",
        default=0.90,
        unit="fraction",
        explainer_he=(
            "כמה מהזרעים שאתה זורע צפויים לנבוט? ברירת המחדל 90% מתאימה לזרעים רעננים. "
            "זרעים ישנים או שנשמרו בתנאים לא אידיאליים עשויים לנבוט פחות — "
            "הגבה את כמות הזריעה בהתאם."
        ),
        post_url="https://nimrod.bio/blog/seed-germination-rate/",  # nimrod-bio post 1051 (slug permanent)
    ),
    "bed_width": Assumption(
        key="bed_width",
        default=0.80,
        unit="m",
        explainer_he=(
            "רוחב הערוגה בה אתה עובד. ברירת המחדל שלנו היא 80 ס\"מ — "
            "תקן JM Fortier מתורגם לסנטימטרים שלמים. "
            "שנה אם הערוגות שלך רחבות יותר או פחות."
        ),
        post_url="https://nimrod.bio/blog/garden-bed-width-80cm/",  # nimrod-bio post 1052 (slug permanent)
    ),
    "oversow": Assumption(
        key="oversow",
        default=1.10,
        unit="x",
        explainer_he=(
            "כמות הזרעים לזרות מעבר לצורך, כמרווח ביטחון. "
            "1.10 = 10% יותר. מפצה על נביטה חלקית, נזקי חרקים, ועוד."
        ),
        post_url=None,
    ),
    "std_bed_length_m": Assumption(
        key="std_bed_length_m",
        default=30.0,
        unit="m",
        explainer_he=(
            "אורך ערוגה סטנדרטי לחישובים. ברירת מחדל 30 מטר — "
            "בסיס תכנוני נוח לחוות קטנות."
        ),
        post_url=None,
    ),
    "compost_N_pct": Assumption(
        key="compost_N_pct",
        default=0.015,
        unit="fraction",
        explainer_he=(
            "אחוז חנקן (N) בקומפוסט — ברירת מחדל 1.5%. "
            "בדוק את ניתוח הקומפוסט שלך לערך מדויק."
        ),
        post_url=None,
    ),
    "application_efficiency": Assumption(
        key="application_efficiency",
        default=0.50,
        unit="fraction",
        explainer_he=(
            "כמה מהחנקן בקומפוסט זמין לצמח בעונה הראשונה. "
            "ברירת מחדל 50% — ממוצע קומפוסט בשל."
        ),
        post_url=None,
    ),
    "rotation_gap_seasons": Assumption(
        key="rotation_gap_seasons",
        default=3,
        unit="seasons",
        explainer_he=(
            "מספר העונות בין גידולים מאותה משפחה בוטנית באותה ערוגה. "
            "ברירת מחדל 3 עונות לצמצום מחלות ומזיקים."
        ),
        post_url=None,
    ),
}


# ---------------------------------------------------------------------------
# Lookup tables (config, not per-crop columns — Schema §3.4)
# ---------------------------------------------------------------------------

# tray_cells: nursery_tray_type text → cells per tray.
# Default 128 when nursery_tray_type is unknown or None.
TRAY_CELLS: dict[str, int] = {
    "72": 72,
    "128": 128,
    "200": 200,
    "242": 242,
    "288": 288,
    "50": 50,
    "104": 104,
}
_TRAY_CELLS_DEFAULT = 128

# hardiness_offset: frost_tolerance_class → offset days relative to last_frost.
# Positive = plant N days BEFORE last frost; negative = plant N days AFTER.
# Source: Calculator Catalog §4.
HARDINESS_OFFSET: dict[str | None, int] = {
    "very_hardy": 28,
    "hardy": 28,
    "semi_hardy": 14,
    "tender": 0,
    "very_tender": -14,
    "warm": -14,
    None: 0,  # conservative default for unknown class
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_assumption(key: str, override=None):
    """Return override if not None, else ASSUMPTIONS[key].default.

    For tray_cells and hardiness_offset use the dedicated helpers below.
    Raises KeyError if key is not in ASSUMPTIONS.
    """
    if override is not None:
        return override
    return ASSUMPTIONS[key].default


def get_tray_cells(nursery_tray_type: str | None, override: int | None = None) -> int:
    """Return cells per tray for the given nursery_tray_type.

    Falls back to _TRAY_CELLS_DEFAULT (128) for unknown types.
    Override takes precedence if provided.
    """
    if override is not None:
        return override
    if nursery_tray_type is None:
        return _TRAY_CELLS_DEFAULT
    return TRAY_CELLS.get(str(nursery_tray_type), _TRAY_CELLS_DEFAULT)


def get_hardiness_offset(frost_tolerance_class: str | None, override: int | None = None) -> int:
    """Return days offset vs last_frost for the given frost_tolerance_class.

    Positive = plant before last frost; negative = plant after.
    Falls back to 0 (conservative) for unknown classes.
    Override takes precedence if provided.
    """
    if override is not None:
        return override
    return HARDINESS_OFFSET.get(frost_tolerance_class, HARDINESS_OFFSET[None])
