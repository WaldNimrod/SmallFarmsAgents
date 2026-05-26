"""Tend overlay importer (SFA-S003-P002-WP-B3 LOD400 §7).

Reads Tend_<year>/ CSV exports and produces:

  1. CropTaskTemplate rows (source='Tend_<year>', trust_tier='OP',
     confidence_weight=0.55) for whitelisted recurring tasks — via the
     B1 crop_task_templates table.
  2. CropVarietySourceValue rows for `days_in_gh_total` and
     `days_to_first_potting` — via the WP-A enrichment engine.
  3. CropHarvestStat rows aggregated from HARVESTS.CSV — NEVER per-record.

Public entrypoints:

  parse_tasks_templates(csv_path, year)       -> list[dict]
  parse_greenhouse_plan(csv_path, year)       -> list[dict]
  parse_harvests_aggregate(csv_path, year)    -> list[dict]
  import_tend_overlay(session, tend_dir, *, year=2022, dry_run=False)
      -> TendOverlaySummary
"""

from __future__ import annotations

import csv
import logging
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from statistics import median
from typing import Optional

from sqlalchemy.orm import Session

from organic_market_agent.crop_book.constants import (
    TEND_CROP_MAP,
    TEND_TASK_BLACKLIST,
    TEND_TASK_TYPE_MAP,
    TEND_TASK_WHITELIST,
)
from organic_market_agent.crop_book.crop_task_templates import DAYS_OFFSET_PRESENCE_ONLY

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TendOverlaySummary:
    year: int
    task_template_rows_upserted: int
    source_value_rows_upserted: int
    harvest_stat_rows_upserted: int
    whitelist_filtered: int          # tasks excluded by whitelist (not blacklisted)
    method_disambiguation_misses: int  # Weed/RowCover with unclear Method
    crop_map_misses: list[str] = field(default_factory=list)  # Tend crops not in TEND_CROP_MAP
    harvests_aggregated: int = 0     # how many raw HARVESTS rows aggregated
    blacklist_filtered: int = 0      # tasks explicitly blacklisted


# ---------------------------------------------------------------------------
# Crop name lookup helpers
# ---------------------------------------------------------------------------

# Reverse map: Hebrew name_he → English (for lookup in models)
_HE_TO_EN: dict[str, str] = {v: k for k, v in TEND_CROP_MAP.items()}


def _parse_crop_name(plantings_assigned: str) -> str:
    """Extract the canonical Tend crop name from a 'Plantings Assigned' field.

    Format: '<Crop> <Cultivar> <Date>' e.g. 'Tomatoes Hyd. Whitny וייטני 13/07/2022'
    Strategy: try progressively shorter prefixes against TEND_CROP_MAP keys.
    """
    raw = plantings_assigned.strip()
    parts = raw.split()
    # Try from longest to shortest prefix
    for length in range(len(parts), 0, -1):
        candidate = " ".join(parts[:length])
        if candidate in TEND_CROP_MAP:
            return candidate
    # Fall back to first token
    return parts[0] if parts else raw


def _resolve_crop_id(session: Session, tend_crop_name: str) -> Optional[int]:
    """Return the crop.id for a Tend English crop name, or None on miss."""
    name_he = TEND_CROP_MAP.get(tend_crop_name)
    if name_he is None:
        return None
    from organic_market_agent.crop_book.models import Crop
    crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
    return crop.id if crop is not None else None


def _resolve_variety_id(session: Session, crop_id: int) -> int:
    """Get or create the default (name_en=None) variety for a crop."""
    from organic_market_agent.crop_book.models import CropVariety
    v = (session.query(CropVariety)
         .filter(CropVariety.crop_id == crop_id, CropVariety.name_en.is_(None))
         .order_by(CropVariety.id)
         .first())
    if v is None:
        v = CropVariety(crop_id=crop_id, name_en=None, name_he=None)
        session.add(v)
        session.flush()
    return v.id


# ---------------------------------------------------------------------------
# §7.3 parse_tasks_templates
# ---------------------------------------------------------------------------

def parse_tasks_templates(csv_path: Path, year: int) -> tuple[list[dict], dict]:
    """Parse TASKS CSV — return (task_dicts, summary_counts).

    summary_counts keys: whitelist_filtered, blacklist_filtered,
    method_disambiguation_misses, crop_map_misses (list of str).
    """
    source = f"Tend_{year}"
    results: list[dict] = []
    whitelist_filtered = 0
    blacklist_filtered = 0
    disambiguation_misses = 0
    crop_map_misses: list[str] = []

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            task_type_raw = row.get("Task Type", "").strip()
            if not task_type_raw:
                continue

            # Step 3: blacklist check first
            if task_type_raw in TEND_TASK_BLACKLIST:
                blacklist_filtered += 1
                continue

            # Step 4: whitelist check
            if task_type_raw not in TEND_TASK_WHITELIST:
                whitelist_filtered += 1
                logger.warning("Tend task not in whitelist: %r — skipping", task_type_raw)
                continue

            # Step 5: resolve JMF task_type
            method_raw = row.get("Method", "").strip()
            sub_method_raw = row.get("Sub-method", "").strip()

            if task_type_raw in TEND_TASK_TYPE_MAP:
                task_type = TEND_TASK_TYPE_MAP[task_type_raw]
                timing_anchor = _timing_anchor(task_type_raw)
            elif task_type_raw == "Weed":
                task_type, timing_anchor = _resolve_weed(method_raw)
                if not method_raw:
                    disambiguation_misses += 1
            elif task_type_raw == "Row Cover & Mulch":
                task_type, timing_anchor = _resolve_row_cover(sub_method_raw)
                if not sub_method_raw:
                    disambiguation_misses += 1
            else:
                logger.error("Whitelist/map mismatch for %r — skipping", task_type_raw)
                continue

            # Step 6: compute days_offset
            days_offset = _days_offset(task_type_raw)

            # Step 8: resolve crop_id
            plantings = row.get("Plantings Assigned", "").strip()
            if not plantings:
                whitelist_filtered += 1
                continue

            tend_crop_name = _parse_crop_name(plantings)
            if tend_crop_name not in TEND_CROP_MAP:
                crop_map_misses.append(tend_crop_name)
                logger.warning("Tend crop not in TEND_CROP_MAP: %r — skipping", tend_crop_name)
                continue

            # Note: crop_id is not resolved here (no session) — returns name_he
            name_he = TEND_CROP_MAP[tend_crop_name]

            results.append({
                "name_he":       name_he,          # resolved to crop_id at upsert time
                "source":        source,
                "trust_tier":    "OP",
                "task_type":     task_type,
                "timing_anchor": timing_anchor,
                "days_offset":   days_offset,
                "method":        method_raw or None,
                "input_material": row.get("Input", "").strip() or None,
                "notes":         row.get("Description", "").strip() or None,
            })

    summary_counts = {
        "whitelist_filtered": whitelist_filtered,
        "blacklist_filtered": blacklist_filtered,
        "method_disambiguation_misses": disambiguation_misses,
        "crop_map_misses": crop_map_misses,
    }
    return results, summary_counts


def _timing_anchor(task_type_raw: str) -> Optional[str]:
    """Compute timing_anchor from raw Tend task type label."""
    if task_type_raw == "Direct Sow":
        return "seeding"
    if task_type_raw == "Transplant":
        return "transplanting"
    if task_type_raw == "Stale Bed":
        return "field_prep"
    return None


def _days_offset(task_type_raw: str) -> int:
    """Compute days_offset for a Tend task row."""
    if task_type_raw in ("Direct Sow", "Transplant"):
        return 0
    return DAYS_OFFSET_PRESENCE_ONLY


def _resolve_weed(method: str) -> tuple[str, None]:
    """Resolve 'Weed' task to JMF task_type via Method column."""
    method_lower = method.lower() if method else ""
    if "flextine" in method_lower:
        return "flextine_harrow_1", None
    if method_lower in ("hand weed", "hand-weed", "") or not method:
        return "hand_weed", None
    # Unknown method → default + WARN
    logger.warning("Weed: unknown Method %r — defaulting to hand_weed", method)
    return "hand_weed", None


def _resolve_row_cover(sub_method: str) -> tuple[str, None]:
    """Resolve 'Row Cover & Mulch' task to JMF task_type via Sub-method column."""
    sm_lower = sub_method.lower() if sub_method else ""
    if any(kw in sm_lower for kw in ("straw", "mulch")):
        return "straw_mulch_topdress", None
    if sm_lower in ("tarp", "cover", "row cover", "") or not sub_method:
        return "net_row_cover", None
    # Unknown sub-method → default + WARN
    logger.warning("Row Cover & Mulch: unknown Sub-method %r — defaulting to net_row_cover", sub_method)
    return "net_row_cover", None


# ---------------------------------------------------------------------------
# §7.4 parse_greenhouse_plan
# ---------------------------------------------------------------------------

def parse_greenhouse_plan(csv_path: Path, year: int) -> list[dict]:
    """Parse GREENHOUSE_PLAN CSV — return source_value dicts for
    days_in_gh_total and days_to_first_potting."""
    source = f"Tend_{year}"
    results: list[dict] = []

    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []

        # Find relevant column names (case-insensitive substring match)
        gh_col = next(
            (h for h in headers if "days in greenhouse" in h.lower()), None)
        potting_col = next(
            (h for h in headers
             if "days to" in h.lower() and ("potting" in h.lower() or "1st" in h.lower())), None)

        if gh_col is None and potting_col is None:
            logger.warning("GREENHOUSE_PLAN: no recognizable Days columns in %s", csv_path)
            return results

        for row in reader:
            plantings = row.get("Plantings", "") or row.get("Crop", "") or ""
            plantings = plantings.strip()
            if not plantings:
                continue

            tend_crop_name = _parse_crop_name(plantings)
            if tend_crop_name not in TEND_CROP_MAP:
                logger.warning("Greenhouse plan crop not in TEND_CROP_MAP: %r", tend_crop_name)
                continue

            name_he = TEND_CROP_MAP[tend_crop_name]

            if gh_col:
                raw = row.get(gh_col, "").strip()
                try:
                    val = int(float(raw))
                    results.append({
                        "name_he": name_he,
                        "field_name": "days_in_gh_total",
                        "source": source,
                        "value_numeric": Decimal(val),
                        "value_text": str(val),
                        "unit": "days",
                        "trust_tier": "OP",
                        "confidence_weight": Decimal("0.55"),
                        "is_outlier_rejected": False,
                    })
                except (ValueError, TypeError):
                    pass

            if potting_col:
                raw = row.get(potting_col, "").strip()
                try:
                    val = int(float(raw))
                    results.append({
                        "name_he": name_he,
                        "field_name": "days_to_first_potting",
                        "source": source,
                        "value_numeric": Decimal(val),
                        "value_text": str(val),
                        "unit": "days",
                        "trust_tier": "OP",
                        "confidence_weight": Decimal("0.55"),
                        "is_outlier_rejected": False,
                    })
                except (ValueError, TypeError):
                    pass

    return results


# ---------------------------------------------------------------------------
# §7.5 parse_harvests_aggregate
# ---------------------------------------------------------------------------

def _month_to_season(month: int) -> str:
    if 3 <= month <= 5:
        return "spring"
    if 6 <= month <= 8:
        return "summer"
    if 9 <= month <= 11:
        return "fall"
    return "winter"  # 12, 1, 2


def _parse_date(date_str: str) -> Optional[date]:
    """Parse date from common formats like DD/MM/YYYY, YYYY-MM-DD, MM/DD/YYYY."""
    date_str = date_str.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def parse_harvests_aggregate(csv_path: Path, year: int) -> tuple[list[dict], int]:
    """Parse HARVESTS CSV — aggregate by (crop, season, year) — NEVER per-record.

    Returns (harvest_stat_dicts, raw_row_count).
    Hard assertion: len(emitted) <= distinct_crops × 4 seasons.
    """
    source = f"Tend_{year}"

    # Read all rows into memory for grouping
    raw_rows: list[dict] = []
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            raw_rows.append(dict(row))

    total_raw = len(raw_rows)

    # Group by (name_he, year, season)
    groups: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    crop_map_misses: set[str] = set()

    for row in raw_rows:
        # Resolve crop name
        plantings = row.get("Plantings", "") or row.get("Crop", "") or ""
        plantings = plantings.strip()
        if not plantings:
            continue

        tend_crop_name = _parse_crop_name(plantings)
        if tend_crop_name not in TEND_CROP_MAP:
            crop_map_misses.add(tend_crop_name)
            continue

        name_he = TEND_CROP_MAP[tend_crop_name]

        # Parse harvest date
        harvest_date_str = row.get("Harvest Date", "") or row.get("Date", "") or ""
        parsed_date = _parse_date(harvest_date_str)
        if parsed_date is None:
            continue

        row_year = parsed_date.year
        season = _month_to_season(parsed_date.month)

        groups[(name_he, row_year, season)].append(row)

    if crop_map_misses:
        logger.warning("HARVESTS: %d distinct crops not in TEND_CROP_MAP: %s",
                       len(crop_map_misses), list(crop_map_misses)[:10])

    # Aggregate each group
    results: list[dict] = []
    distinct_crops = len({name_he for name_he, _, _ in groups.keys()})

    for (name_he, row_year, season), rows in groups.items():
        # ISO week numbers
        week_nums: list[int] = []
        amounts: list[Decimal] = []
        amount_units: list[str] = []
        planters: set[str] = set()

        for row in rows:
            # Harvest date for week
            harvest_date_str = row.get("Harvest Date", "") or row.get("Date", "") or ""
            parsed_date = _parse_date(harvest_date_str)
            if parsed_date:
                week_nums.append(parsed_date.isocalendar()[1])

            # Amount
            amt_str = (row.get("Amount", "") or "").strip()
            try:
                amounts.append(Decimal(str(float(amt_str))))
            except (ValueError, TypeError):
                pass

            # Amount unit
            unit_str = (row.get("Amount Unit", "") or row.get("Unit", "") or "").strip()
            if unit_str:
                amount_units.append(unit_str)

            # Distinct planters/cycles
            planting_str = (row.get("Plantings Assigned", "") or row.get("Plantings", "") or "").strip()
            if planting_str:
                planters.add(planting_str)

        first_week = min(week_nums) if week_nums else None
        last_week = max(week_nums) if week_nums else None
        # Mode week (peak)
        peak_week = Counter(week_nums).most_common(1)[0][0] if week_nums else None

        yield_total = sum(amounts) if amounts else None
        yield_unit_mode = Counter(amount_units).most_common(1)[0][0] if amount_units else None

        results.append({
            "name_he":            name_he,
            "season":             season,
            "year":               row_year,
            "source":             source,
            "cycles_count":       len(planters),
            "first_harvest_week": first_week,
            "peak_harvest_week":  peak_week,
            "last_harvest_week":  last_week,
            "yield_total":        yield_total,
            "yield_unit":         yield_unit_mode,
            "yield_per_bed_min":  None,
            "yield_per_bed_max":  None,
            "yield_per_bed_median": None,
        })

    # Hard assertion: aggregation must be bounded
    max_allowed = distinct_crops * 4  # × 4 seasons × 1 year
    if len(results) > max(max_allowed, 1):
        raise AssertionError(
            f"HARVESTS aggregation produced {len(results)} rows > "
            f"max_allowed {max_allowed} (distinct_crops={distinct_crops} × 4 seasons). "
            "Programming bug in grouping logic."
        )

    return results, total_raw


# ---------------------------------------------------------------------------
# §7.7 Upsert helpers
# ---------------------------------------------------------------------------

def _upsert_task_template_tend(
    session: Session,
    crop_id: int,
    task_row: dict,
    source: str,
) -> bool:
    """Upsert on (crop_id, source, task_type, days_offset). Returns True if new.

    Matches B1's _upsert_task_template signature — same UNIQUE constraint
    enforces idempotency.
    """
    from organic_market_agent.crop_book.crop_task_templates import CropTaskTemplate

    days_off = task_row["days_offset"]
    task_type = task_row["task_type"]

    existing = (session.query(CropTaskTemplate)
                .filter_by(crop_id=crop_id, source=source,
                           task_type=task_type, days_offset=days_off)
                .one_or_none())
    if existing is None:
        obj = CropTaskTemplate(
            crop_id=crop_id,
            source=source,
            trust_tier="OP",
            task_type=task_type,
            timing_anchor=task_row.get("timing_anchor"),
            days_offset=days_off,
            method=task_row.get("method"),
            input_material=task_row.get("input_material"),
            notes=task_row.get("notes"),
        )
        session.add(obj)
        session.flush()
        return True
    else:
        existing.timing_anchor = task_row.get("timing_anchor")
        existing.notes = task_row.get("notes")
        session.flush()
        return False


def _upsert_source_value_tend(
    session: Session,
    variety_id: int,
    field_name: str,
    value_numeric: Decimal,
    source: str,
) -> None:
    """Upsert on (variety_id, field_name, source='Tend_<year>').

    trust_tier='OP', confidence_weight=0.55, is_outlier_rejected=False.
    Engine reuse: the next run_enrichment() call will pick these up.
    """
    from organic_market_agent.crop_book.models import CropVarietySourceValue

    row = (session.query(CropVarietySourceValue)
           .filter_by(variety_id=variety_id, field_name=field_name, source=source)
           .one_or_none())
    if row is None:
        row = CropVarietySourceValue(
            variety_id=variety_id, field_name=field_name, source=source,
        )
        session.add(row)
    row.value_numeric = value_numeric
    row.value_text = str(value_numeric)
    row.unit = "days"
    row.note = None
    row.trust_tier = "OP"
    row.confidence_weight = Decimal("0.55")
    row.is_outlier_rejected = False
    session.flush()


def _upsert_harvest_stat(
    session: Session,
    crop_id: int,
    row: dict,
) -> bool:
    """Upsert on (crop_id, season, year, source). Returns True if new.

    The crop_harvest_stats UNIQUE constraint enforces idempotency.
    """
    from organic_market_agent.crop_book.crop_harvest_stats import CropHarvestStat

    existing = (session.query(CropHarvestStat)
                .filter_by(crop_id=crop_id,
                           season=row["season"],
                           year=row["year"],
                           source=row["source"])
                .one_or_none())
    if existing is None:
        obj = CropHarvestStat(
            crop_id=crop_id,
            season=row["season"],
            year=row["year"],
            source=row["source"],
            cycles_count=row.get("cycles_count"),
            first_harvest_week=row.get("first_harvest_week"),
            peak_harvest_week=row.get("peak_harvest_week"),
            last_harvest_week=row.get("last_harvest_week"),
            yield_total=row.get("yield_total"),
            yield_unit=row.get("yield_unit"),
            yield_per_bed_min=row.get("yield_per_bed_min"),
            yield_per_bed_max=row.get("yield_per_bed_max"),
            yield_per_bed_median=row.get("yield_per_bed_median"),
            created_at=datetime.utcnow(),
        )
        session.add(obj)
        session.flush()
        return True
    else:
        # Update mutable aggregate fields
        existing.cycles_count = row.get("cycles_count")
        existing.first_harvest_week = row.get("first_harvest_week")
        existing.peak_harvest_week = row.get("peak_harvest_week")
        existing.last_harvest_week = row.get("last_harvest_week")
        existing.yield_total = row.get("yield_total")
        existing.yield_unit = row.get("yield_unit")
        session.flush()
        return False


# ---------------------------------------------------------------------------
# §7.6 Orchestrator
# ---------------------------------------------------------------------------

_TASKS_FILENAME = "TASKS (from macBook Air - nimrod).CSV"
_GH_PLAN_FILENAME = "GREENHOUSE_PLAN.CSV"
_HARVESTS_FILENAME = "HARVESTS.CSV"

# Fallbacks for fixture/test CSVs with simpler names
_TASKS_FALLBACKS = ["TASKS.CSV", "tasks.csv"]
_GH_FALLBACKS = ["greenhouse_plan.csv"]
_HARVESTS_FALLBACKS = ["harvests.csv"]


def _find_csv(directory: Path, primary: str, fallbacks: list[str]) -> Optional[Path]:
    """Return first matching CSV path, trying primary then fallbacks."""
    for name in [primary] + fallbacks:
        p = directory / name
        if p.exists():
            return p
    return None


def _find_csv_for_year(
    base_dir: Path,
    year: int,
    primary: str,
    fallbacks: list[str],
) -> Optional[Path]:
    """Resolve CSV for a Tend year — flat multi-year layout or legacy subdir."""
    flat_stems = [primary.split(".")[0].split(" ")[0]]
    for fb in fallbacks:
        stem = Path(fb).stem.upper()
        if stem not in flat_stems:
            flat_stems.append(stem)
    for stem in flat_stems:
        flat_name = f"Tend_{year}_{stem}.csv"
        flat_path = base_dir / flat_name
        if flat_path.exists():
            return flat_path
        flat_path_upper = base_dir / flat_name.upper()
        if flat_path_upper.exists():
            return flat_path_upper

    year_dir = base_dir / f"Tend_{year}"
    if year_dir.is_dir():
        found = _find_csv(year_dir, primary, fallbacks)
        if found is not None:
            return found

    return _find_csv(base_dir, primary, fallbacks)


def import_tend_overlay(
    session: Session,
    tend_dir: Path,
    *,
    year: int = 2022,
    dry_run: bool = False,
) -> TendOverlaySummary:
    """End-to-end orchestrator.

    Steps:
      1. Resolve CSV paths. Missing files → log WARN, skip that sub-parser.
      2. Call parse_tasks_templates() → emit task-template dicts.
      3. Call parse_greenhouse_plan() → emit source_value dicts.
      4. Call parse_harvests_aggregate() → emit harvest_stat dicts.
      5. For each task-template dict: _upsert_task_template_tend().
      6. For each source_value dict: _upsert_source_value_tend().
      7. For each harvest_stat dict: _upsert_harvest_stat().
      8. If dry_run: session.rollback(); else session.commit().
      9. Return TendOverlaySummary.
    """
    source = f"Tend_{year}"

    # 1. Resolve paths
    tasks_path = _find_csv_for_year(tend_dir, year, _TASKS_FILENAME, _TASKS_FALLBACKS)
    gh_plan_path = _find_csv_for_year(tend_dir, year, _GH_PLAN_FILENAME, _GH_FALLBACKS)
    harvests_path = _find_csv_for_year(tend_dir, year, _HARVESTS_FILENAME, _HARVESTS_FALLBACKS)

    if tasks_path is None:
        logger.warning("TASKS CSV not found in %s — skipping task templates", tend_dir)
    if gh_plan_path is None:
        logger.warning("GREENHOUSE_PLAN CSV not found in %s — skipping greenhouse plan", tend_dir)
    if harvests_path is None:
        logger.warning("HARVESTS CSV not found in %s — skipping harvest stats", tend_dir)

    # 2. Parse tasks
    task_dicts: list[dict] = []
    summary_counts: dict = {
        "whitelist_filtered": 0,
        "blacklist_filtered": 0,
        "method_disambiguation_misses": 0,
        "crop_map_misses": [],
    }
    if tasks_path is not None:
        task_dicts, summary_counts = parse_tasks_templates(tasks_path, year)

    # 3. Parse greenhouse plan
    gh_dicts: list[dict] = []
    if gh_plan_path is not None:
        gh_dicts = parse_greenhouse_plan(gh_plan_path, year)

    # 4. Parse harvests
    harvest_dicts: list[dict] = []
    harvests_raw_count = 0
    if harvests_path is not None:
        harvest_dicts, harvests_raw_count = parse_harvests_aggregate(harvests_path, year)

    # 5. Upsert task templates
    task_upserted = 0
    for task_dict in task_dicts:
        name_he = task_dict.pop("name_he")
        from organic_market_agent.crop_book.models import Crop
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("Tend overlay: crop not in DB: %r — skipping", name_he)
            continue
        is_new = _upsert_task_template_tend(session, crop.id, task_dict, source)
        if is_new:
            task_upserted += 1

    # 6. Upsert source values (greenhouse plan)
    sv_upserted = 0
    for sv_dict in gh_dicts:
        name_he = sv_dict.pop("name_he")
        from organic_market_agent.crop_book.models import Crop
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("Tend overlay: greenhouse crop not in DB: %r — skipping", name_he)
            continue
        variety_id = _resolve_variety_id(session, crop.id)
        _upsert_source_value_tend(
            session, variety_id,
            sv_dict["field_name"],
            sv_dict["value_numeric"],
            sv_dict["source"],
        )
        sv_upserted += 1

    # 7. Upsert harvest stats
    hs_upserted = 0
    for hs_dict in harvest_dicts:
        name_he = hs_dict.pop("name_he")
        from organic_market_agent.crop_book.models import Crop
        crop = session.query(Crop).filter_by(name_he=name_he).one_or_none()
        if crop is None:
            logger.warning("Tend overlay: harvest crop not in DB: %r — skipping", name_he)
            continue
        is_new = _upsert_harvest_stat(session, crop.id, hs_dict)
        if is_new:
            hs_upserted += 1

    # 8. Commit or rollback
    if dry_run:
        session.rollback()
    else:
        session.commit()

    return TendOverlaySummary(
        year=year,
        task_template_rows_upserted=task_upserted,
        source_value_rows_upserted=sv_upserted,
        harvest_stat_rows_upserted=hs_upserted,
        whitelist_filtered=summary_counts["whitelist_filtered"],
        method_disambiguation_misses=summary_counts["method_disambiguation_misses"],
        crop_map_misses=summary_counts["crop_map_misses"],
        harvests_aggregated=harvests_raw_count,
        blacklist_filtered=summary_counts["blacklist_filtered"],
    )
