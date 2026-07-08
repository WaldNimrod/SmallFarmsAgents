#!/usr/bin/env python3
"""Extract the agronomically-useful 'cherry-pick' from L45_2017_data_summary.xlsx.

SFA-S003-P004-WP-CB-SRC-SWEEP.

L45 is a real Israeli market-garden farm's 2017 operations workbook (10 sheets).
Per team_00 (2026-06-10) the WP integrates ONLY the interesting, non-duplicate
agronomic data — a deliberate cherry-pick, NOT a full importer:

  INCLUDED  : sheet 'נתוני בסיס' (base data) — per-crop empirical agronomy:
              rows/bed, in-row spacing (cm), transplant->harvest days (DTM),
              season, and rich cultural notes.
  EXCLUDED  : 'מפת חלקה' / 'תכנון ראשוני' / 'תכנית שתילה ומעקב' (one-farm planting
              calendar — duplicates the 197 calendar rows already in the DB from
              5 sources); 'מחירים' (market prices — belong to the price-index /
              מחירון domain, not the crop book); 'תקציב'/'השכרת גינות' (business
              economics — out of scope, cf. L43 DECISION); 'עצים' (perennial trees
              — out of the annual-vegetable crop-book scope); and crucially the
              'ירוק' sheet, which is CANNABIS cultivation data (strain names,
              indica/sativa ratios) — explicitly out of scope.

Output: data/external_sources/extracted/il_farm_2017_l45/_table.json
        (tracked artifact; the .xlsx itself stays gitignored, same pattern as Idan)

The il_farm_2017_l45 importer reads that JSON. Source: OP:il_farm_2017_l45,
trust tier OP (real operator records), confidence 0.80 — same class as Idan/Tend,
NOT a hard override.

Re-run: python scripts/extract_l45_basedata.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import openpyxl

XLSX = Path("data/external_sources/israeli/L45_2017_data_summary.xlsx")
OUT_DIR = Path("data/external_sources/extracted/il_farm_2017_l45")
SHEET = "נתוני בסיס"

# Column order in 'נתוני בסיס' (0-indexed), from the header row:
# מין | שורות לערוגה | מרווח שתילה | שתילים לערוגה | צנרת |
# זריעה לנביטה | זריעה לשתילה | שתילה לקטיף | עונה | קטיף | הערות
COL_CROP = 0
COL_ROWS_PER_BED = 1
COL_SPACING_CM = 2
COL_PLANTS_PER_BED = 3
COL_TRANSPLANT_TO_HARVEST = 7  # days_to_maturity
COL_SEASON = 8
COL_HARVEST = 9
COL_NOTES = 10

# Generic / non-crop rows to skip (handled also by idan SKIP_CROPS downstream)
SKIP_CROPS = {"תבלינים", "עשבי תבלין", "ירקות שורש", "עידן", "מין", ""}


def _num(val) -> float | None:
    """Parse an int/float cell to float, else None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    m = re.fullmatch(r"\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def _dtm(val) -> tuple[float | None, str | None]:
    """Parse 'שתילה לקטיף' (transplant->harvest days). Returns (numeric, raw_range).

    Ranges like '60-90' -> midpoint 75.0 with raw '60-90' preserved for the note.
    Single values like '150' -> 150.0. Non-numeric -> (None, None).
    """
    if val is None:
        return None, None
    s = str(val).strip()
    if not s:
        return None, None
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        return (lo + hi) / 2.0, s
    n = _num(s)
    return (n, s) if n is not None else (None, None)


def main() -> None:
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb[SHEET]

    crops: list[dict] = []
    seen: dict[str, dict] = {}
    for row in ws.iter_rows(values_only=True):
        cells = list(row)
        if len(cells) <= COL_NOTES:
            cells += [None] * (COL_NOTES + 1 - len(cells))
        crop_he = (str(cells[COL_CROP]).strip() if cells[COL_CROP] is not None else "")
        if crop_he in SKIP_CROPS:
            continue

        rows_per_bed = _num(cells[COL_ROWS_PER_BED])
        spacing_cm = _num(cells[COL_SPACING_CM])
        dtm_num, dtm_raw = _dtm(cells[COL_TRANSPLANT_TO_HARVEST])
        season = (str(cells[COL_SEASON]).strip() if cells[COL_SEASON] is not None else None) or None
        notes = (str(cells[COL_NOTES]).strip() if cells[COL_NOTES] is not None else None) or None

        # Need at least one usable agronomic field to be worth a row.
        if rows_per_bed is None and spacing_cm is None and dtm_num is None and not notes:
            continue

        rec = {
            "crop_he": crop_he,
            "rows_per_bed": rows_per_bed,
            "in_row_spacing_cm": spacing_cm,
            "days_to_maturity": dtm_num,
            "dtm_raw": dtm_raw,
            "season_he": season,
            "notes": notes,
        }
        # Merge duplicate crop rows (e.g. קייל appears twice): first non-null wins per field.
        if crop_he in seen:
            prev = seen[crop_he]
            for k in ("rows_per_bed", "in_row_spacing_cm", "days_to_maturity", "dtm_raw", "season_he", "notes"):
                if prev.get(k) in (None, "") and rec.get(k) not in (None, ""):
                    prev[k] = rec[k]
            continue
        seen[crop_he] = rec
        crops.append(rec)

    out = {
        "schema_version": "1.0",
        "source": "OP:il_farm_2017_l45",
        "provenance": {
            "xlsx": "L45_2017_data_summary.xlsx",
            "sheet": SHEET,
            "farm_year": 2017,
            "extraction_model": "claude-code-direct",
            "extracted_at": "2026-06-10T00:00:00+00:00",
            "note": "Cherry-pick of base-data sheet only (WP-CB-SRC-SWEEP). "
                    "Calendar/price/budget/trees/cannabis sheets intentionally excluded.",
        },
        "crops": crops,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "_table.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} — {len(crops)} crops")
    for c in crops:
        print(f"  {c['crop_he']}: dtm={c['days_to_maturity']} ({c['dtm_raw']}) "
              f"spacing={c['in_row_spacing_cm']} rows={c['rows_per_bed']} season={c['season_he']}")


if __name__ == "__main__":
    main()
