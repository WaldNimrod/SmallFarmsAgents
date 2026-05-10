"""JMF XLSX parser — reads MasterClass crop data files.

If the directory is empty or files have no parseable crop rows,
logs INFO and returns an empty list (not a failure per LOD400 §5).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def parse_jmf_dir(path: Path) -> list[dict[str, Any]]:
    """Parse all XLSX files in path; return list of crop row dicts.

    Returns empty list if directory is missing, empty, or files have no data.
    """
    if not path.exists():
        logger.info("JMF XLSX directory not found: %s — skipping", path)
        return []

    xlsx_files = sorted(path.glob("*.xlsx"))
    if not xlsx_files:
        logger.info("JMF XLSX directory yielded 0 files, skipping: %s", path)
        return []

    rows: list[dict[str, Any]] = []
    try:
        import openpyxl  # noqa: PLC0415
    except ImportError:
        logger.warning("openpyxl not installed — JMF XLSX parsing skipped")
        return []

    for xlsx_path in xlsx_files:
        file_rows = _parse_xlsx(xlsx_path, openpyxl)
        if not file_rows:
            logger.info("JMF XLSX yielded 0 rows for %s", xlsx_path.name)
        else:
            rows.extend(file_rows)
            logger.info("JMF XLSX: parsed %d rows from %s", len(file_rows), xlsx_path.name)

    return rows


def _parse_xlsx(path: Path, openpyxl: Any) -> list[dict[str, Any]]:
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to open %s: %s", path, exc)
        return []

    rows: list[dict[str, Any]] = []
    for sheet in wb.worksheets:
        header_row = None
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i == 0:
                header_row = [str(c).strip() if c else "" for c in row]
                continue
            if header_row is None:
                break
            if not any(row):
                continue
            record = dict(zip(header_row, row))
            crop_name = record.get("Crop") or record.get("crop") or record.get("Name")
            if not crop_name:
                continue
            rows.append({"source": "JMF", "raw": record})

    wb.close()
    return rows
