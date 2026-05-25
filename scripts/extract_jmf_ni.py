"""One-time extraction runner — reads TEXT FILES (provided by team_00) and
calls Anthropic API to produce the JSON cache.

NOT runtime. NOT in tests. NOT imported by the runtime path. Run manually:

    python scripts/extract_jmf_ni.py --source jmf_book --crop Arugula
    python scripts/extract_jmf_ni.py --source jmf_book --all
    python scripts/extract_jmf_ni.py --source jmf_ft_phytoprotection
    python scripts/extract_jmf_ni.py --source jmf_book --rebuild --crop Arugula
    python scripts/extract_jmf_ni.py --source jmf_book --crop Arugula --dry-run

Requires:
    - ANTHROPIC_API_KEY env var (not needed for --dry-run)
    - Text files at data/jmf/raw_text/<source>/<crop>.txt (or _full.txt for FT)
      provided by team_00 post-merge (Q1 architectural decision — no PDFs).

NOTE per Q1: this script does NOT call pdftotext or read PDFs. Input is plain
text files. team_00 performs the PDF->text conversion themselves.

SFA-S003-P002-WP-B2 LOD400 v1.1.3 §6.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import sys
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SUPPORTED_SOURCES = (
    "jmf_book",
    "jmf_book_alt",
    "jmf_ft_flameweed",
    "jmf_ft_biopesticide",
    "jmf_ft_phytoprotection",
    "jmf_ft_nurseryseeding",
)

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_TEMPERATURE = 0.0
MAX_TOKENS = 4096

RAW_TEXT_BASE = pathlib.Path("data/jmf/raw_text")
CACHE_BASE = pathlib.Path("data/jmf/extracted")
SCHEMA_VERSION = "1.0"

# Per-source canonical PDF filename (for provenance)
SOURCE_PDF_MAP = {
    "jmf_book": "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF",
    "jmf_book_alt": "THE MARKET GARDENER_*.PDF",
    "jmf_ft_flameweed": "FT_FINALE_FLAMEWEEDING.PDF",
    "jmf_ft_biopesticide": "FT_FINALE_TABLEAUAPPLICATIONBIOPESTICIPE.PDF",
    "jmf_ft_phytoprotection": "FT_FINALE_PHYTOPROTECTION.PDF",
    "jmf_ft_nurseryseeding": "FT_FINALE_NURSERYSEEDING.PDF",
}

# Per-source note_type set (which keys are populated in the JSON `notes` dict)
SOURCE_NOTE_TYPES = {
    "jmf_book": (
        "pest_disease", "harvest_marker", "storage_handling",
        "rotation_companion", "cultivar_recommendation",
        "growing_tip", "irrigation", "nursery_specific",
    ),
    "jmf_book_alt": (
        "pest_disease", "harvest_marker", "storage_handling",
        "rotation_companion", "cultivar_recommendation",
        "growing_tip", "irrigation", "nursery_specific",
    ),
    "jmf_ft_flameweed": ("flame_weed_timing",),
    "jmf_ft_biopesticide": ("biopesticide_spray",),
    "jmf_ft_phytoprotection": ("phytoprotection_substance", "phytoprotection_application"),
    "jmf_ft_nurseryseeding": ("nursery_seeding_process",),
}

# FT sources use a single _full.txt file covering all crops
FT_SOURCES = frozenset(
    {"jmf_ft_flameweed", "jmf_ft_biopesticide", "jmf_ft_phytoprotection", "jmf_ft_nurseryseeding"}
)


# Full ordered list of all note_type keys (mirrors NOTE_TYPE_VALUES in crop_knowledge_notes.py)
_ALL_NOTE_TYPE_KEYS = (
    "pest_disease", "harvest_marker", "storage_handling", "rotation_companion",
    "cultivar_recommendation", "growing_tip", "irrigation", "nursery_specific",
    "flame_weed_timing", "biopesticide_spray",
    "phytoprotection_substance", "phytoprotection_application",
    "nursery_seeding_process",
)


def _validate_notes(notes: dict, note_types: tuple[str, ...]) -> dict:
    """Validate extracted notes dict — enforce length bounds, fill nulls."""
    all_keys = list(_ALL_NOTE_TYPE_KEYS)
    result = {k: None for k in all_keys}
    for nt in note_types:
        val = notes.get(nt)
        if val is not None:
            if len(val) > 2000:
                logger.warning("note_type=%r exceeds 2000 chars — truncating", nt)
                val = val[:2000]
            result[nt] = val
    return result


def _stub_extract_book_chapter(
    crop_jmf_en: str, note_types: tuple[str, ...]
) -> dict:
    """Stub extractor for --dry-run path (no API call)."""
    notes = {nt: f"[STUB] {crop_jmf_en} {nt} — dry-run placeholder" for nt in note_types}
    return _validate_notes(notes, note_types)


def _stub_extract_ft_table(source_name: str, note_types: tuple[str, ...]) -> dict[str, dict]:
    """Stub FT extractor for --dry-run path."""
    return {
        "Arugula": _validate_notes(
            {nt: f"[STUB] Arugula {nt} — dry-run" for nt in note_types}, note_types
        )
    }


def extract_book_chapter(
    client, text: str, crop_jmf_en: str, note_types: tuple[str, ...], model: str
) -> dict:
    """Call Anthropic API to extract book chapter notes.

    Returns a validated notes dict (all NOTE_TYPE_VALUES keys present, nulls for non-source types).
    """
    nt_list = ", ".join(note_types)
    template = "{" + ", ".join(f'"{nt}": "..." or null' for nt in note_types) + "}"
    prompt = (
        f'You are extracting structured horticultural knowledge from a book chapter about '
        f'the crop "{crop_jmf_en}". The chapter text follows.\n'
        f'Extract concise farm-relevant notes (<=2000 characters each) for these '
        f'note types: {nt_list}. Return ONLY valid JSON with the structure shown. '
        f'Use null for any note_type the chapter does not address.\n\n'
        f'Chapter text:\n"""\n{text}\n"""\n\n'
        f"Output JSON ONLY:\n{template}"
    )
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    notes = json.loads(raw.strip())
    return _validate_notes(notes, note_types)


def extract_ft_table(
    client, text: str, source_name: str, note_types: tuple[str, ...], model: str
) -> dict[str, dict]:
    """Call Anthropic API to extract FT table content.

    Returns a dict mapping crop_jmf_en -> validated notes dict.
    """
    nt_list = ", ".join(note_types)
    prompt = (
        f'You are extracting structured horticultural data from a farm technique table '
        f'covering multiple crops. The table text follows.\n'
        f'For each crop mentioned, extract notes (<=2000 chars each) for these types: {nt_list}.\n'
        f'Return ONLY valid JSON: {{"CropName": {{"{note_types[0]}": "..." or null, ...}}, ...}}\n\n'
        f'Table text:\n"""\n{text}\n"""\n\nOutput JSON ONLY:'
    )
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    crops_raw = json.loads(raw.strip())
    return {
        crop: _validate_notes(notes_dict, note_types)
        for crop, notes_dict in crops_raw.items()
    }


def _build_provenance(model: str, pages: str = "N/A") -> dict:
    return {
        "pdf": SOURCE_PDF_MAP.get("", "N/A"),  # filled by caller
        "pages": pages,
        "extraction_model": model,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }


def process_book_source(
    source_name: str,
    crop_filter: str | None,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
) -> int:
    """Process a jmf_book or jmf_book_alt source. Returns number of files written."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    source_text_dir = raw_text_base / source_name
    source_cache_dir = cache_base / source_name
    source_cache_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = SOURCE_PDF_MAP[source_name]

    if not source_text_dir.exists():
        logger.warning("Text dir not found: %s — skipping", source_text_dir)
        return 0

    text_files = sorted(source_text_dir.glob("*.txt"))
    if crop_filter:
        text_files = [f for f in text_files if f.stem.lower() == crop_filter.lower()]
    if not text_files:
        logger.warning("No text files found for source=%s crop_filter=%r", source_name, crop_filter)
        return 0

    written = 0
    for txt_path in text_files:
        crop_jmf_en = txt_path.stem
        out_path = source_cache_dir / f"{crop_jmf_en}.json"
        if out_path.exists() and not rebuild:
            logger.info("Cache exists, skipping %s (use --rebuild to overwrite)", out_path)
            continue

        text = txt_path.read_text(encoding="utf-8")
        logger.info("Extracting %s / %s ...", source_name, crop_jmf_en)

        if dry_run:
            notes = _stub_extract_book_chapter(crop_jmf_en, note_types)
        else:
            notes = extract_book_chapter(client, text, crop_jmf_en, note_types, model)

        result = {
            "schema_version": SCHEMA_VERSION,
            "source": f"NI:{source_name}_v1",
            "crop_jmf_en": crop_jmf_en,
            "provenance": {
                "pdf": pdf_name,
                "pages": "N/A",  # team_00 fills pages manually or from metadata
                "extraction_model": model,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            },
            "notes": notes,
        }
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Written: %s", out_path)
        written += 1
    return written


def process_ft_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
) -> int:
    """Process a jmf_ft_* source (single _full.txt input). Returns number of files written."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    source_text_dir = raw_text_base / source_name
    source_cache_dir = cache_base / source_name
    source_cache_dir.mkdir(parents=True, exist_ok=True)
    pdf_name = SOURCE_PDF_MAP[source_name]

    full_txt = source_text_dir / "_full.txt"
    if not full_txt.exists():
        logger.warning("Full text file not found: %s — skipping", full_txt)
        return 0

    # Write a single _table.json file
    out_path = source_cache_dir / "_table.json"
    if out_path.exists() and not rebuild:
        logger.info("Cache exists, skipping %s (use --rebuild to overwrite)", out_path)
        return 0

    text = full_txt.read_text(encoding="utf-8")
    logger.info("Extracting FT table: %s ...", source_name)

    if dry_run:
        crops_notes = _stub_extract_ft_table(source_name, note_types)
    else:
        crops_notes = extract_ft_table(client, text, source_name, note_types, model)

    result = {
        "schema_version": SCHEMA_VERSION,
        "source": f"NI:{source_name}_v1",
        "provenance": {
            "pdf": pdf_name,
            "pages": "1-end",
            "extraction_model": model,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        },
        "crops": crops_notes,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Written: %s (%d crops)", out_path, len(crops_notes))
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "JMF NI extraction runner — reads TEXT FILES and calls Anthropic API "
            "to produce JSON cache. Q1: no PDFs; team_00 provides text files."
        )
    )
    parser.add_argument(
        "--source",
        choices=SUPPORTED_SOURCES,
        required=True,
        help="JMF source to process",
    )
    parser.add_argument(
        "--crop",
        metavar="NAME",
        help="Restrict to single crop (English JMF name, e.g. Arugula). For book sources only.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all crops with text-file fixtures present (book sources only).",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Re-extract even if cache file already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stub Anthropic responses; no live API calls. Writes stub JSON to cache dir.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Anthropic model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--raw-text-base",
        type=pathlib.Path,
        default=RAW_TEXT_BASE,
        metavar="PATH",
        help=f"Base path for raw text files (default: {RAW_TEXT_BASE})",
    )
    parser.add_argument(
        "--cache-base",
        type=pathlib.Path,
        default=CACHE_BASE,
        metavar="PATH",
        help=f"Base path for output JSON cache (default: {CACHE_BASE})",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s %(name)s: %(message)s", level=level, stream=sys.stdout
    )

    # Book sources require --crop or --all
    if args.source not in FT_SOURCES and not args.crop and not args.all:
        parser.error(
            f"Source {args.source!r} is a book source — specify --crop NAME or --all"
        )

    # Get Anthropic client (or stub)
    client = None
    if not args.dry_run:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            parser.error("ANTHROPIC_API_KEY env var required (or use --dry-run)")
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            parser.error("anthropic package not installed — pip install anthropic")

    if args.source in FT_SOURCES:
        written = process_ft_source(
            source_name=args.source,
            raw_text_base=args.raw_text_base,
            cache_base=args.cache_base,
            rebuild=args.rebuild,
            dry_run=args.dry_run,
            model=args.model,
            client=client,
        )
    else:
        written = process_book_source(
            source_name=args.source,
            crop_filter=args.crop,
            raw_text_base=args.raw_text_base,
            cache_base=args.cache_base,
            rebuild=args.rebuild,
            dry_run=args.dry_run,
            model=args.model,
            client=client,
        )

    logger.info("Done. Files written: %d", written)


if __name__ == "__main__":
    main()
