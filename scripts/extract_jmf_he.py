"""One-time extraction runner for WP-C2 Hebrew + JMF extension sources.

Reads pre-extracted text files from data/external_sources/raw_text/,
calls Anthropic API to produce per-crop JSON cache, and logs token cost.

Usage:
    python3 scripts/extract_jmf_he.py --source aosnot --all
    python3 scripts/extract_jmf_he.py --source aosnot --dry-run
    python3 scripts/extract_jmf_he.py --source sham_variety_trials
    python3 scripts/extract_jmf_he.py --source all
    python3 scripts/extract_jmf_he.py --source all --dry-run

NOT runtime. NOT imported by the runtime import path.
Budget cap: $20 total. Cost logged to data/external_sources/extracted/_extraction_log.json.

SFA-S003-P002-WP-C2 LOD400 §5.
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

# ---------------------------------------------------------------------------
# Source catalogue
# ---------------------------------------------------------------------------

# Per-source raw text filename (in data/external_sources/raw_text/)
SOURCE_RAW_TEXT_MAP: dict[str, str] = {
    "aosnot":                    "israeli__L02_AOSNOT_variety_info.txt",
    "sham_variety_trials":       "israeli__L11_variety_trials_2021.txt",
    "sham_hydro_guide":          "israeli__L09_hydro_vegetable_guide.txt",
    "zacks_leafy_survey":        "israeli__L10_DR_ZACKS_leafy_hydro_survey.txt",
    "jmf_ft_nurseryseeding_ext": "jmf_extension__L14_FT_FINALE_NURSERYSEEDING.txt",
    "jmf_ft_seedingincellflats": "jmf_extension__L16_seeding_in_cell_flats.txt",
    "jmf_cover_crops_narrative": "jmf_extension__L13_cover_crops_guide.txt",
}

SOURCE_PROVENANCE_MAP: dict[str, str] = {
    "aosnot":                    "L02_AOSNOT_variety_info.docx",
    "sham_variety_trials":       "L11_variety_trials_2021.pdf",
    "sham_hydro_guide":          "L09_hydro_vegetable_guide.pdf",
    "zacks_leafy_survey":        "L10_DR_ZACKS_leafy_hydro_survey.pdf",
    "jmf_ft_nurseryseeding_ext": "FT_FINALE_NURSERYSEEDING.PDF",
    "jmf_ft_seedingincellflats": "L16_seeding_in_cell_flats.pdf",
    "jmf_cover_crops_narrative": "L13_cover_crops_guide.pdf",
}

# Note types extracted per source
SOURCE_NOTE_TYPES: dict[str, tuple[str, ...]] = {
    "aosnot": (
        "frost_tolerance", "flowering_date", "pollination_mechanism", "israeli_regions",
    ),
    "sham_variety_trials": ("variety_trial_score",),
    "sham_hydro_guide": ("hydro_suitability",),
    "zacks_leafy_survey": ("hydro_suitability",),
    "jmf_ft_nurseryseeding_ext": ("nursery_specific",),
    "jmf_ft_seedingincellflats": ("nursery_specific",),
    "jmf_cover_crops_narrative": ("growing_tip", "rotation_companion"),
}

# Hebrew sources: crop_he key; table format means single pass for all crops
HEBREW_PER_CROP_SOURCES = frozenset({"aosnot", "sham_hydro_guide", "zacks_leafy_survey"})
HEBREW_TABLE_SOURCES    = frozenset({"sham_variety_trials"})
# JMF FT extension sources: English crop names, _table.json format
JMF_FT_SOURCES          = frozenset({"jmf_ft_nurseryseeding_ext", "jmf_ft_seedingincellflats"})
# Cover crops: English per-crop or table
JMF_COVER_SOURCES       = frozenset({"jmf_cover_crops_narrative"})

SUPPORTED_SOURCES = tuple(SOURCE_RAW_TEXT_MAP.keys())

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_TEMPERATURE = 0.0
MAX_TOKENS = 4096
SCHEMA_VERSION = "1.0"

# Absolute cost cap (USD input tokens × $3/M + output tokens × $15/M for Sonnet)
BUDGET_CAP_USD = 20.0
# Approximate cost per 1K tokens (conservative upper bound for budgeting)
APPROX_COST_PER_1K_INPUT = 0.003   # $3 / 1M
APPROX_COST_PER_1K_OUTPUT = 0.015  # $15 / 1M

RAW_TEXT_BASE = pathlib.Path("data/external_sources/raw_text")
CACHE_BASE = pathlib.Path("data/external_sources/extracted")
EXTRACTION_LOG = CACHE_BASE / "_extraction_log.json"

# L02 AOSNOT is large (~1.3MB); chunk size for per-crop sections
L02_MAX_CHARS_PER_CALL = 8000  # characters fed to API per crop chunk


# ---------------------------------------------------------------------------
# Cost tracking
# ---------------------------------------------------------------------------

def _load_log() -> dict:
    if EXTRACTION_LOG.exists():
        try:
            return json.loads(EXTRACTION_LOG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"total_cost_usd": 0.0, "total_input_tokens": 0, "total_output_tokens": 0, "runs": []}


def _save_log(log: dict) -> None:
    EXTRACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    EXTRACTION_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def _estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * APPROX_COST_PER_1K_INPUT
        + output_tokens / 1000 * APPROX_COST_PER_1K_OUTPUT
    )


def _check_budget(log: dict) -> None:
    """Raise RuntimeError if budget cap already reached."""
    if log.get("total_cost_usd", 0.0) >= BUDGET_CAP_USD:
        raise RuntimeError(
            f"Budget cap ${BUDGET_CAP_USD} reached "
            f"(spent ${log['total_cost_usd']:.4f}). "
            "STOP — file INQUIRY to team_00 before proceeding."
        )


def _record_run(log: dict, source: str, crop: str, input_tokens: int, output_tokens: int) -> None:
    cost = _estimate_cost(input_tokens, output_tokens)
    log["total_cost_usd"] = log.get("total_cost_usd", 0.0) + cost
    log["total_input_tokens"] = log.get("total_input_tokens", 0) + input_tokens
    log["total_output_tokens"] = log.get("total_output_tokens", 0) + output_tokens
    log.setdefault("runs", []).append({
        "source": source,
        "crop": crop,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Stub extractors for --dry-run
# ---------------------------------------------------------------------------

def _stub_notes(crop_id: str, note_types: tuple[str, ...]) -> dict:
    return {nt: f"[STUB] {crop_id} / {nt} — dry-run placeholder" for nt in note_types}


_ALL_NOTE_TYPE_KEYS: tuple[str, ...] = (
    "pest_disease", "harvest_marker", "storage_handling", "rotation_companion",
    "cultivar_recommendation", "growing_tip", "irrigation", "nursery_specific",
    "flame_weed_timing", "biopesticide_spray",
    "phytoprotection_substance", "phytoprotection_application",
    "nursery_seeding_process",
    "frost_tolerance", "flowering_date", "pollination_mechanism",
    "israeli_regions", "variety_trial_score", "hydro_suitability",
)


def _validate_notes(notes: dict, note_types: tuple[str, ...]) -> dict:
    """Enforce ≤2000 chars, fill nulls for unused keys, include only valid note_type keys."""
    result = {k: None for k in _ALL_NOTE_TYPE_KEYS}
    for nt in note_types:
        val = notes.get(nt)
        if val is not None and val:
            if len(str(val)) > 2000:
                logger.warning("note_type=%r exceeds 2000 chars — truncating", nt)
                val = str(val)[:2000]
            result[nt] = str(val)
    return result


# ---------------------------------------------------------------------------
# Anthropic API helpers
# ---------------------------------------------------------------------------

def _call_api(client, prompt: str, model: str) -> tuple[str, int, int]:
    """Call API; return (raw_text, input_tokens, output_tokens)."""
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    return raw, response.usage.input_tokens, response.usage.output_tokens


def _parse_json_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ---------------------------------------------------------------------------
# Hebrew per-crop source (L02 aosnot, L09 sham_hydro_guide, L10 zacks)
# ---------------------------------------------------------------------------

def _detect_hebrew_crop_sections(client, text: str, model: str) -> list[str]:
    """Ask LLM to list all crop names found in the Hebrew text."""
    prompt = (
        "הטקסט הבא מכיל מידע על גידולים שונים בעברית. "
        "מה שמות הגידולים המופיעים בטקסט? "
        "החזר JSON בלבד: {\"crops\": [\"שם גידול\", ...]}\n\n"
        f"טקסט (ראשית):\n{text[:12000]}\n\n"
        "JSON בלבד:"
    )
    raw, _, _ = _call_api(client, prompt, model)
    data = _parse_json_response(raw)
    return data.get("crops", [])


def _detect_crop_sections_stub() -> list[str]:
    return ["אוסנה", "חסה", "עגבנייה"]


def _extract_crop_section(text: str, crop_he: str) -> str:
    """Heuristic: find the portion of text that discusses crop_he."""
    lines = text.split("\n")
    start = None
    end = None
    for i, line in enumerate(lines):
        if crop_he in line:
            start = max(0, i - 1)
            break
    if start is None:
        return ""
    # Find end: next line that looks like a new crop heading (≤60 chars, no punctuation)
    for j in range(start + 2, len(lines)):
        stripped = lines[j].strip()
        if (
            stripped
            and len(stripped) < 60
            and not stripped.endswith(":")
            and j > start + 5
            and lines[j - 1].strip() == ""
        ):
            end = j
            break
    if end is None:
        end = start + 400  # fallback: next 400 lines
    section = "\n".join(lines[start:end])
    return section[:L02_MAX_CHARS_PER_CALL]


def _build_hebrew_per_crop_prompt(crop_he: str, text_chunk: str, note_types: tuple[str, ...]) -> str:
    nt_list = ", ".join(note_types)
    template = "{" + ", ".join(f'"{nt}": "..." או null' for nt in note_types) + "}"
    return (
        f'אתה מחלץ ידע חקלאי מובנה מטקסט עברי על הגידול "{crop_he}".\n'
        f"חלץ הערות קצרות (≤2000 תווים כל אחת) לסוגים הבאים: {nt_list}.\n"
        f"החזר JSON בלבד עם המבנה הבא. השתמש ב-null לסוג שאינו מוזכר בטקסט.\n"
        f"שמור על טקסט עברי כפי שהוא — אין להמיר לאסקי.\n\n"
        f"טקסט:\n{text_chunk}\n\n"
        f"JSON בלבד:\n{template}"
    )


def process_hebrew_per_crop_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
    log: dict,
) -> int:
    """Process L02/L09/L10 style sources: one text file, extract per crop."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    raw_file = raw_text_base / SOURCE_RAW_TEXT_MAP[source_name]
    cache_dir = cache_base / source_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    provenance_pdf = SOURCE_PROVENANCE_MAP[source_name]

    if not raw_file.exists():
        logger.warning("Raw text file not found: %s — skipping source=%s", raw_file, source_name)
        return 0

    text = raw_file.read_text(encoding="utf-8")
    logger.info("Source=%s raw text size: %d chars", source_name, len(text))

    # Step 1: detect crop sections
    if dry_run:
        crops = _detect_crop_sections_stub()
        logger.info("[dry-run] Using stub crop list: %s", crops)
    else:
        _check_budget(log)
        try:
            crops = _detect_hebrew_crop_sections(client, text, model)
        except Exception as exc:
            logger.error("Crop section detection failed for %s: %s", source_name, exc)
            return 0
        logger.info("Detected %d crops in source=%s", len(crops), source_name)

    written = 0
    for crop_he in crops:
        out_path = cache_dir / f"{crop_he}.json"
        if out_path.exists() and not rebuild:
            logger.info("Cache exists, skipping %s/%s", source_name, crop_he)
            continue

        if not dry_run:
            _check_budget(log)

        text_chunk = _extract_crop_section(text, crop_he)
        if not text_chunk:
            logger.warning("Could not extract section for %r in %s — skipping", crop_he, source_name)
            continue

        if dry_run:
            notes = _validate_notes(_stub_notes(crop_he, note_types), note_types)
            in_tok, out_tok = 0, 0
        else:
            prompt = _build_hebrew_per_crop_prompt(crop_he, text_chunk, note_types)
            try:
                raw, in_tok, out_tok = _call_api(client, prompt, model)
                raw_notes = _parse_json_response(raw)
                notes = _validate_notes(raw_notes, note_types)
            except Exception as exc:
                logger.error("Extraction failed for %s/%s: %s", source_name, crop_he, exc)
                continue
            _record_run(log, source_name, crop_he, in_tok, out_tok)
            _save_log(log)
            logger.info(
                "Extracted %s/%s in=%d out=%d cumulative=$%.4f",
                source_name, crop_he, in_tok, out_tok, log["total_cost_usd"],
            )

        result = {
            "schema_version": SCHEMA_VERSION,
            "source": f"NI:{source_name}_v1",
            "crop_he": crop_he,
            "provenance": {
                "pdf": provenance_pdf,
                "extraction_model": model,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            },
            "notes": notes,
        }
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Written: %s", out_path)
        written += 1

    return written


# ---------------------------------------------------------------------------
# Hebrew table source (L11 sham_variety_trials)
# ---------------------------------------------------------------------------

def _build_hebrew_table_prompt(text: str, note_types: tuple[str, ...]) -> str:
    nt_list = ", ".join(note_types)
    return (
        "אתה מחלץ נתונים חקלאיים מובנים מטבלה עברית המכסה מספר גידולים.\n"
        f"לכל גידול המופיע בטבלה, חלץ הערות לסוגים: {nt_list}.\n"
        'החזר JSON בלבד: {"crops": {"שם גידול": {"variety_trial_score": "..." או null}, ...}}\n'
        "שמור על טקסט עברי כפי שהוא.\n\n"
        f"טקסט:\n{text[:12000]}\n\nJSON בלבד:"
    )


def process_hebrew_table_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
    log: dict,
) -> int:
    """Process L11 style sources: one text file, table format → _table.json."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    raw_file = raw_text_base / SOURCE_RAW_TEXT_MAP[source_name]
    cache_dir = cache_base / source_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    provenance_pdf = SOURCE_PROVENANCE_MAP[source_name]

    out_path = cache_dir / "_table.json"
    if out_path.exists() and not rebuild:
        logger.info("Cache exists, skipping %s (use --rebuild to overwrite)", source_name)
        return 0

    if not raw_file.exists():
        logger.warning("Raw text file not found: %s — skipping", raw_file)
        return 0

    text = raw_file.read_text(encoding="utf-8")

    if dry_run:
        crops_raw = {"חסה": {nt: f"[STUB] חסה / {nt}" for nt in note_types}}
        in_tok, out_tok = 0, 0
    else:
        _check_budget(log)
        prompt = _build_hebrew_table_prompt(text, note_types)
        try:
            raw, in_tok, out_tok = _call_api(client, prompt, model)
            data = _parse_json_response(raw)
            crops_raw = data.get("crops", data)  # tolerate {crops:{...}} or flat {crop: {}}
        except Exception as exc:
            logger.error("Table extraction failed for %s: %s", source_name, exc)
            return 0
        _record_run(log, source_name, "_table", in_tok, out_tok)
        _save_log(log)
        logger.info(
            "Extracted table %s: %d crops, in=%d out=%d cumulative=$%.4f",
            source_name, len(crops_raw), in_tok, out_tok, log["total_cost_usd"],
        )

    crops_validated = {
        crop_he: _validate_notes(notes_dict, note_types)
        for crop_he, notes_dict in crops_raw.items()
    }

    result = {
        "schema_version": SCHEMA_VERSION,
        "source": f"NI:{source_name}_v1",
        "provenance": {
            "pdf": provenance_pdf,
            "extraction_model": model,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        },
        "crops": crops_validated,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Written: %s (%d crops)", out_path, len(crops_validated))
    return 1


# ---------------------------------------------------------------------------
# JMF FT extension sources (L14, L16) — English crop names, _table.json
# ---------------------------------------------------------------------------

def _build_jmf_ft_prompt(source_name: str, text: str, note_types: tuple[str, ...]) -> str:
    nt_list = ", ".join(note_types)
    template_val = ", ".join(f'"{nt}": "..." or null' for nt in note_types)
    return (
        "You are extracting structured horticultural data from a farm technique document "
        f"covering multiple crops ({source_name}). The document text follows.\n"
        f"For each crop mentioned, extract notes (≤2000 chars each) for these types: {nt_list}.\n"
        f'Return ONLY valid JSON: {{"crops": {{"CropName": {{{template_val}}}, ...}}}}\n\n'
        f"Text:\n{text[:12000]}\n\nJSON ONLY:"
    )


def process_jmf_ft_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
    log: dict,
) -> int:
    """Process JMF FT extension sources (L14, L16): English names, _table.json."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    raw_file = raw_text_base / SOURCE_RAW_TEXT_MAP[source_name]
    cache_dir = cache_base / source_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    provenance_pdf = SOURCE_PROVENANCE_MAP[source_name]

    out_path = cache_dir / "_table.json"
    if out_path.exists() and not rebuild:
        logger.info("Cache exists, skipping %s (use --rebuild to overwrite)", source_name)
        return 0

    if not raw_file.exists():
        logger.warning("Raw text file not found: %s — skipping", raw_file)
        return 0

    text = raw_file.read_text(encoding="utf-8")

    if dry_run:
        crops_raw = {"Arugula": {nt: f"[STUB] Arugula / {nt}" for nt in note_types}}
        in_tok, out_tok = 0, 0
    else:
        _check_budget(log)
        prompt = _build_jmf_ft_prompt(source_name, text, note_types)
        try:
            raw, in_tok, out_tok = _call_api(client, prompt, model)
            data = _parse_json_response(raw)
            crops_raw = data.get("crops", data)
        except Exception as exc:
            logger.error("FT extraction failed for %s: %s", source_name, exc)
            return 0
        _record_run(log, source_name, "_table", in_tok, out_tok)
        _save_log(log)
        logger.info(
            "Extracted FT table %s: %d crops, in=%d out=%d cumulative=$%.4f",
            source_name, len(crops_raw), in_tok, out_tok, log["total_cost_usd"],
        )

    crops_validated = {
        crop: _validate_notes(notes_dict, note_types)
        for crop, notes_dict in crops_raw.items()
    }

    result = {
        "schema_version": SCHEMA_VERSION,
        "source": f"NI:{source_name}_v1",
        "provenance": {
            "pdf": provenance_pdf,
            "extraction_model": model,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        },
        "crops": crops_validated,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Written: %s (%d crops)", out_path, len(crops_validated))
    return 1


# ---------------------------------------------------------------------------
# Cover crops narrative (L13) — English per-crop or table
# ---------------------------------------------------------------------------

def _build_cover_crop_prompt(text: str, note_types: tuple[str, ...]) -> str:
    nt_list = ", ".join(note_types)
    return (
        "You are extracting structured horticultural knowledge from a cover crops guide.\n"
        f"For each crop mentioned, extract notes (≤2000 chars each) for: {nt_list}.\n"
        'Return ONLY valid JSON: {"crops": {"CropName": {"growing_tip": "..." or null, '
        '"rotation_companion": "..." or null}, ...}}\n\n'
        f"Text:\n{text[:12000]}\n\nJSON ONLY:"
    )


def process_cover_crops_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
    log: dict,
) -> int:
    """Process L13 cover crops narrative — English names, per-crop JSON files."""
    note_types = SOURCE_NOTE_TYPES[source_name]
    raw_file = raw_text_base / SOURCE_RAW_TEXT_MAP[source_name]
    cache_dir = cache_base / source_name
    cache_dir.mkdir(parents=True, exist_ok=True)
    provenance_pdf = SOURCE_PROVENANCE_MAP[source_name]

    out_path = cache_dir / "_table.json"
    if out_path.exists() and not rebuild:
        logger.info("Cache exists, skipping %s", source_name)
        return 0

    if not raw_file.exists():
        logger.warning("Raw text file not found: %s — skipping", raw_file)
        return 0

    text = raw_file.read_text(encoding="utf-8")

    if dry_run:
        crops_raw = {
            "Clover": {"growing_tip": "[STUB] clover tip", "rotation_companion": "[STUB] companion"},
            "Buckwheat": {"growing_tip": "[STUB] buckwheat tip", "rotation_companion": None},
        }
        in_tok, out_tok = 0, 0
    else:
        _check_budget(log)
        prompt = _build_cover_crop_prompt(text, note_types)
        try:
            raw, in_tok, out_tok = _call_api(client, prompt, model)
            data = _parse_json_response(raw)
            crops_raw = data.get("crops", data)
        except Exception as exc:
            logger.error("Cover crops extraction failed: %s", exc)
            return 0
        _record_run(log, source_name, "_table", in_tok, out_tok)
        _save_log(log)
        logger.info(
            "Extracted cover crops: %d crops, in=%d out=%d cumulative=$%.4f",
            len(crops_raw), in_tok, out_tok, log["total_cost_usd"],
        )

    crops_validated = {
        crop: _validate_notes(notes_dict, note_types)
        for crop, notes_dict in crops_raw.items()
    }

    result = {
        "schema_version": SCHEMA_VERSION,
        "source": f"NI:{source_name}_v1",
        "provenance": {
            "pdf": provenance_pdf,
            "extraction_model": model,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        },
        "crops": crops_validated,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Written: %s (%d crops)", out_path, len(crops_validated))
    return 1


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def process_source(
    source_name: str,
    raw_text_base: pathlib.Path,
    cache_base: pathlib.Path,
    rebuild: bool,
    dry_run: bool,
    model: str,
    client,
    log: dict,
) -> int:
    if source_name in HEBREW_PER_CROP_SOURCES:
        return process_hebrew_per_crop_source(
            source_name, raw_text_base, cache_base, rebuild, dry_run, model, client, log
        )
    elif source_name in HEBREW_TABLE_SOURCES:
        return process_hebrew_table_source(
            source_name, raw_text_base, cache_base, rebuild, dry_run, model, client, log
        )
    elif source_name in JMF_FT_SOURCES:
        return process_jmf_ft_source(
            source_name, raw_text_base, cache_base, rebuild, dry_run, model, client, log
        )
    elif source_name in JMF_COVER_SOURCES:
        return process_cover_crops_source(
            source_name, raw_text_base, cache_base, rebuild, dry_run, model, client, log
        )
    else:
        raise ValueError(f"Unknown source: {source_name!r}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "WP-C2 Hebrew + JMF extension extraction runner. "
            "Reads TEXT FILES and calls Anthropic API to produce JSON cache. "
            "Budget cap: $20. Q1: no PDFs; team_00 provides text files."
        )
    )
    parser.add_argument(
        "--source",
        choices=list(SUPPORTED_SOURCES) + ["all"],
        required=True,
        help="Source to process, or 'all' to process all sources in priority order",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Re-extract even if cache file already exists",
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
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level=level, stream=sys.stdout)

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

    log = _load_log()
    if not args.dry_run:
        _check_budget(log)

    sources_to_run = SUPPORTED_SOURCES if args.source == "all" else (args.source,)
    total_written = 0
    for src in sources_to_run:
        logger.info("Processing source: %s", src)
        written = process_source(
            src, args.raw_text_base, args.cache_base,
            args.rebuild, args.dry_run, args.model, client, log,
        )
        total_written += written
        logger.info("Source %s: %d files written", src, written)

    logger.info("Done. Total files written: %d", total_written)
    if not args.dry_run:
        logger.info(
            "Total cost estimate: $%.4f / $%.1f budget remaining: $%.4f",
            log.get("total_cost_usd", 0.0),
            BUDGET_CAP_USD,
            BUDGET_CAP_USD - log.get("total_cost_usd", 0.0),
        )


if __name__ == "__main__":
    main()
