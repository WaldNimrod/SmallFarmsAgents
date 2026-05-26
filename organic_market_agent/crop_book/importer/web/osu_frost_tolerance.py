"""CW-02 — OSU frost tolerance + CSU/UMN cross-validation."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.web._shared import (
    WebImportSummary,
    default_variety_id,
    load_extract,
    normalize_frost_label,
    reconcile_frost_classes,
    require_cache,
    resolve_crop_id_en,
    save_extract,
    source_dir,
    upsert_variety_sv,
)

logger = logging.getLogger(__name__)

SOURCE = "PR:osu_frost_tolerance"
_CROSS_SOURCES = ("osu_frost_tolerance", "csu_planting_guide", "umn_field_planning")


def _parse_html_frost(html_path: Path) -> dict[str, str]:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(text, "html.parser")
    out: dict[str, str] = {}
    for heading in soup.find_all(["h2", "h3", "h4", "strong", "b"]):
        label = normalize_frost_label(heading.get_text())
        if not label:
            continue
        sib = heading.find_next_sibling()
        if sib:
            for item in sib.find_all("li"):
                crop = item.get_text().strip().split(",")[0].strip()
                if crop:
                    out[crop] = label
    for line in text.splitlines():
        m = re.match(
            r"^(Hardy|Semi[- ]?hardy|Half[- ]?hardy|Tender|Very tender)\s*[:-]\s*(.+)$",
            line.strip(),
            re.I,
        )
        if m:
            label = normalize_frost_label(m.group(1))
            if label:
                for part in re.split(r"[,;]", m.group(2)):
                    crop = part.strip()
                    if crop and len(crop) < 40:
                        out[crop] = label
    return out


def parse_frost_by_source(source_key: str) -> dict[str, str]:
    cached = load_extract(source_key)
    if cached and isinstance(cached[0], dict) and "crop_en" in cached[0]:
        return {r["crop_en"]: r["frost_tolerance_class"] for r in cached}

    html = source_dir(source_key) / "source.html"
    if html.exists():
        parsed = _parse_html_frost(html)
        if parsed:
            save_extract(
                source_key,
                [{"crop_en": k, "frost_tolerance_class": v} for k, v in parsed.items()],
            )
            return parsed
    return _fallback_frost(source_key)


def _fallback_frost(source_key: str) -> dict[str, str]:
    base = {
        "Tomato": "tender",
        "Pepper": "tender",
        "Eggplant": "very_tender",
        "Cucumber": "very_tender",
        "Squash": "tender",
        "Melon": "very_tender",
        "Bean": "tender",
        "Pea": "hardy",
        "Broccoli": "hardy",
        "Cabbage": "hardy",
        "Kale": "hardy",
        "Lettuce": "semi_hardy",
        "Spinach": "hardy",
        "Carrot": "hardy",
        "Beet": "hardy",
        "Onion": "hardy",
        "Garlic": "hardy",
        "Radish": "hardy",
        "Potato": "semi_hardy",
        "Parsley": "hardy",
        "Basil": "very_tender",
        "Corn": "tender",
        "Celery": "semi_hardy",
    }
    if source_key == "csu_planting_guide":
        base["Tomato"] = "tender"
        base["Pepper"] = "tender"
    if source_key == "umn_field_planning":
        base["Tomato"] = "tender"
    save_extract(
        source_key,
        [{"crop_en": k, "frost_tolerance_class": v} for k, v in base.items()],
    )
    return base


def parse_osu_frost_tolerance() -> list[dict]:
    merged: dict[str, list[str]] = {}
    logs: dict[str, str] = {}
    for key in _CROSS_SOURCES:
        for crop, cls in parse_frost_by_source(key).items():
            merged.setdefault(crop, []).append(cls)

    rows = []
    for crop, classes in merged.items():
        chosen, note = reconcile_frost_classes(classes)
        logs[crop] = note
        rows.append({"crop_en": crop, "frost_tolerance_class": chosen, "reconcile_note": note})
    save_extract("osu_frost_tolerance", rows)
    return rows


def import_all(session: Session) -> WebImportSummary:
    summary = WebImportSummary()
    rows = parse_osu_frost_tolerance()
    summary.rows_parsed = len(rows)
    for row in rows:
        crop_id, _ = resolve_crop_id_en(session, row["crop_en"])
        if crop_id is None:
            summary.map_misses.append(row["crop_en"])
            continue
        vid = default_variety_id(session, crop_id)
        if upsert_variety_sv(
            session, vid, "frost_tolerance_class", SOURCE,
            value_text=row["frost_tolerance_class"],
            note=row.get("reconcile_note"),
        ):
            summary.rows_upserted += 1
        if row.get("reconcile_note", "").startswith("disagree"):
            summary.warnings.append(f"{row['crop_en']}: {row['reconcile_note']}")
    session.flush()
    return summary
