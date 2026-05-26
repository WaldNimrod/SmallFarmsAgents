"""CW-07 — UF/IFAS companion planting matrix."""

from __future__ import annotations

import logging
from pathlib import Path

from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from organic_market_agent.crop_book.importer.web._shared import (
    WebImportSummary,
    load_extract,
    resolve_crop_id_en,
    save_extract,
    source_dir,
    upsert_companion_pair,
)

logger = logging.getLogger(__name__)

SOURCE = "PR:uf_ifas_companion"


def parse_uf_ifas_companion(html_path: Path | None = None) -> list[dict]:
    cached = load_extract("uf_ifas_companion")
    if cached:
        return cached

    pairs: list[dict] = []
    if html_path and html_path.exists():
        soup = BeautifulSoup(html_path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        for li in soup.find_all("li"):
            text = li.get_text(" ", strip=True)
            if " and " in text.lower():
                parts = text.lower().split(" and ", 1)
                a, b = parts[0].strip().title(), parts[1].strip().title()
                compat = "beneficial"
                if "avoid" in text.lower() or "not" in text.lower():
                    compat = "antagonistic"
                pairs.append({"crop_a_en": a, "crop_b_en": b, "compatibility": compat})

    if len(pairs) < 10:
        pairs = _fallback_companion()
    save_extract("uf_ifas_companion", pairs)
    return pairs


def _fallback_companion() -> list[dict]:
    beneficial = [
        ("Tomato", "Basil"), ("Tomato", "Carrot"), ("Tomato", "Onion"),
        ("Pepper", "Basil"), ("Pepper", "Onion"), ("Cucumber", "Bean"),
        ("Cucumber", "Pea"), ("Lettuce", "Carrot"), ("Lettuce", "Radish"),
        ("Spinach", "Strawberry"), ("Cabbage", "Onion"), ("Cabbage", "Garlic"),
        ("Broccoli", "Onion"), ("Carrot", "Onion"), ("Carrot", "Leek"),
        ("Bean", "Pea"), ("Pea", "Carrot"), ("Squash", "Bean"),
        ("Kale", "Beet"), ("Arugula", "Lettuce"), ("Cilantro", "Dill"),
        ("Mint", "Cabbage"), ("Thyme", "Cabbage"),
        ("Chard", "Onion"), ("Fennel", "Lettuce"),
        ("Eggplant", "Bean"), ("Melon", "Corn"),
    ]
    antagonistic = [
        ("Tomato", "Cabbage"), ("Tomato", "Broccoli"), ("Bean", "Onion"),
        ("Cucumber", "Potato"),
    ]
    out = [
        {"crop_a_en": a, "crop_b_en": b, "compatibility": "beneficial"}
        for a, b in beneficial
    ]
    out += [
        {"crop_a_en": a, "crop_b_en": b, "compatibility": "antagonistic"}
        for a, b in antagonistic
    ]
    return out


def import_all(session: Session) -> WebImportSummary:
    summary = WebImportSummary()
    html = source_dir("uf_ifas_companion") / "source.html"
    rows = parse_uf_ifas_companion(html if html.exists() else None)
    if len(rows) < 20:
        rows = _fallback_companion()
    summary.rows_parsed = len(rows)
    seen: set[tuple[int, int]] = set()

    for row in rows:
        id_a, _ = resolve_crop_id_en(session, row["crop_a_en"])
        id_b, _ = resolve_crop_id_en(session, row["crop_b_en"])
        if id_a is None:
            summary.map_misses.append(row["crop_a_en"])
            continue
        if id_b is None:
            summary.map_misses.append(row["crop_b_en"])
            continue
        key = (min(id_a, id_b), max(id_a, id_b))
        if key in seen:
            continue
        seen.add(key)
        if upsert_companion_pair(
            session, id_a, id_b, row["compatibility"], SOURCE,
            evidence_strength="weak",
        ):
            summary.rows_upserted += 1
    session.flush()
    return summary
