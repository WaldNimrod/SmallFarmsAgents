"""MD → JSON cache → DB loader for JMF MasterClass crop sheets.

SFA-S003-P002-WP-B1-patch04 LOD400 §3.5.

Usage:
    python scripts/load_masterclass_sheets.py --dry-run       # parse + validate only
    python scripts/load_masterclass_sheets.py --load-db       # parse + write JSON + insert DB
    python scripts/load_masterclass_sheets.py --load-db --db-url sqlite:///test.db

LICENSING INVARIANT:
    All records produced by this script carry is_internal_farm_use_only=True
    and body_text <= 2000 chars (WP-B2 §3.1 / DECISION §6 fair-use posture).
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
SHEETS_DIR = REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets"
INDEX_PATH = SHEETS_DIR / "_index.json"
OUTPUT_DIR = REPO_ROOT / "data" / "jmf" / "extracted" / "jmf_book"

SCHEMA_VERSION = "1.0"
SOURCE_LABEL = "NI:jmf_masterclass"
TRUST_TIER = "NI"
BODY_TEXT_MAX = 2000  # chars — fair-use bound (WP-B2 §3.1)

# ---------------------------------------------------------------------------
# Section keywords → note_type mapping
# ---------------------------------------------------------------------------
SECTION_NOTE_TYPE_MAP: dict[str, str] = {
    "cultivar": "cultivar_recommendation",
    "pest": "pest_disease",
    "disease": "pest_disease",
    "harvest": "harvest_marker",
    "storage": "storage_handling",
    "washing": "storage_handling",
    "rotation": "rotation_companion",
    "companion": "rotation_companion",
    "irrigation": "irrigation",
    "nursery": "nursery_specific",
    "growing": "growing_tip",
    "crop planning": "growing_tip",
    "crop specifics": "growing_tip",
    "spacing": "growing_tip",
    "transplant": "growing_tip",
    "fertiliz": "growing_tip",
    "soil": "growing_tip",
}

# Sections we extract cultivar names from
CULTIVAR_HEADERS = {"cultivar", "cultivars", "variety", "varieties"}

# ---------------------------------------------------------------------------
# MD parser
# ---------------------------------------------------------------------------

def _truncate(text: str, max_len: int = BODY_TEXT_MAX) -> tuple[str, bool]:
    """Truncate text to max_len chars. Returns (text, was_truncated)."""
    text = text.strip()
    if len(text) <= max_len:
        return text, False
    truncated = text[:max_len - 3] + "..."
    return truncated, True


def _extract_sections(md_text: str) -> dict[str, list[str]]:
    """Split MD into labelled sections by scanning for heading-like lines.

    Returns dict mapping lowercase section title → list of paragraph strings.
    """
    sections: dict[str, list[str]] = {}
    current_key: str | None = "intro"
    current_lines: list[str] = []

    # Strip HTML comments and image references
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)
    md_text = re.sub(r"!\[.*?\]\(.*?\)", "", md_text)

    for line in md_text.splitlines():
        stripped = line.strip()
        # Detect section headers — lines in ALL CAPS or ## heading or known keywords
        if _is_section_header(stripped):
            if current_lines:
                key = current_key or "intro"
                sections.setdefault(key, []).extend(current_lines)
            current_key = stripped.lower().rstrip(":")
            current_lines = []
        elif stripped:
            current_lines.append(stripped)

    # flush
    if current_lines:
        key = current_key or "intro"
        sections.setdefault(key, []).extend(current_lines)

    return sections


def _is_section_header(line: str) -> bool:
    """Heuristic: a line is a section header if it is short (< 60 chars),
    non-empty, and either ALL-CAPS or starts with a Markdown heading marker."""
    if not line:
        return False
    if line.startswith("#"):
        return True
    if len(line) < 60 and line == line.upper() and any(c.isalpha() for c in line):
        return True
    # Known section keywords (case-insensitive, short line)
    lower = line.lower().rstrip(":")
    known = {
        "cultivars", "cultivar", "crop planning", "crop specifics",
        "starting seeds", "irrigation type", "irrigation management",
        "transplanting", "harvest", "harvesting", "storage",
        "pests", "diseases", "pest management", "disease management",
        "rotation", "companion planting", "nursery", "growing tips",
        "spacing", "fertilization", "amendments",
    }
    return lower in known and len(line) < 60


def _resolve_note_type(section_key: str) -> str:
    """Map a section key to a note_type enum value."""
    sk = section_key.lower()
    for keyword, note_type in SECTION_NOTE_TYPE_MAP.items():
        if keyword in sk:
            return note_type
    return "growing_tip"


def _extract_cultivar_names(sections: dict[str, list[str]]) -> list[str]:
    """Pull cultivar names from the cultivar section lines."""
    cultivar_names: list[str] = []
    for key, lines in sections.items():
        if any(kw in key for kw in CULTIVAR_HEADERS):
            for line in lines:
                # Remove bullet markers and arrows
                clean = re.sub(r"^[→•\-\*]+\s*", "", line).strip()
                # Skip lines that look like instructions / sentences
                if clean and len(clean) < 80 and not clean.lower().startswith(("use ", "any ", "those ", "plant ")):
                    cultivar_names.append(clean)
    return cultivar_names


def parse_md_sheet(md_path: Path) -> dict:
    """Parse a single MD sheet and return structured data.

    Returns:
        {
          'cultivars': [str, ...],
          'notes': {note_type: body_text, ...}  # at most 1 per type
          'warnings': [str, ...]
        }
    """
    text = md_path.read_text(encoding="utf-8", errors="replace")
    sections = _extract_sections(text)

    cultivars = _extract_cultivar_names(sections)
    notes: dict[str, str] = {}
    parse_warnings: list[str] = []

    for section_key, lines in sections.items():
        if not lines:
            continue
        note_type = _resolve_note_type(section_key)
        body = " ".join(lines)
        body, was_truncated = _truncate(body)
        if was_truncated:
            msg = f"{md_path.name}: section '{section_key}' body truncated to {BODY_TEXT_MAX} chars"
            logger.warning(msg)
            parse_warnings.append(msg)
        # Merge multiple sections of same note_type with separator
        if note_type in notes:
            combined = notes[note_type] + " | " + body
            combined, was_truncated = _truncate(combined)
            if was_truncated:
                parse_warnings.append(
                    f"{md_path.name}: merged section '{note_type}' truncated"
                )
            notes[note_type] = combined
        else:
            notes[note_type] = body

    return {
        "cultivars": cultivars,
        "notes": notes,
        "warnings": parse_warnings,
    }


# ---------------------------------------------------------------------------
# JSON cache schema (WP-B2)
# ---------------------------------------------------------------------------

def md_to_cache_json(
    parsed: dict,
    source: str,
    crop_jmf_en: str,
    crop_name_he: str,
    md_filename: str,
    pages: str,
) -> dict:
    """Convert parsed MD data to WP-B2 cache schema JSON dict.

    All note records carry:
      - body_text strictly <= 2000 chars (fair-use bound)
      - is_internal_farm_use_only: True
    """
    notes_structured: dict[str, list[dict]] = {}
    for note_type, body_text in parsed["notes"].items():
        # Safety guard — double-check truncation
        assert len(body_text) <= BODY_TEXT_MAX, (
            f"body_text for {crop_jmf_en}/{note_type} exceeds {BODY_TEXT_MAX}: {len(body_text)}"
        )
        notes_structured[note_type] = [
            {
                "body_text": body_text,
                "page_ref": None,
                "confidence": "high",
                "is_internal_farm_use_only": True,
            }
        ]

    return {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "crop_jmf_en": crop_jmf_en,
        "crop_name_he": crop_name_he,
        "is_internal_farm_use_only": True,
        "provenance": {
            "md_filename": md_filename,
            "pages": pages,
            "extraction_model": "load_masterclass_sheets.py/v1.0",
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        },
        "cultivars": parsed["cultivars"],
        "notes": notes_structured,
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_json_schema(cache_record: dict) -> list[str]:
    """Validate a cache record against WP-B2 schema requirements.

    Returns list of violation strings (empty = valid).
    """
    errors: list[str] = []
    required_top = ["schema_version", "source", "crop_jmf_en", "crop_name_he",
                    "is_internal_farm_use_only", "provenance", "notes"]
    for field in required_top:
        if field not in cache_record:
            errors.append(f"Missing required field: {field}")

    if cache_record.get("is_internal_farm_use_only") is not True:
        errors.append("is_internal_farm_use_only must be True")

    for note_type, note_list in cache_record.get("notes", {}).items():
        for i, note in enumerate(note_list):
            if "body_text" not in note:
                errors.append(f"notes.{note_type}[{i}] missing body_text")
            elif len(note["body_text"]) > BODY_TEXT_MAX:
                errors.append(
                    f"notes.{note_type}[{i}].body_text exceeds {BODY_TEXT_MAX} chars "
                    f"({len(note['body_text'])})"
                )
            if note.get("is_internal_farm_use_only") is not True:
                errors.append(f"notes.{note_type}[{i}].is_internal_farm_use_only must be True")

    return errors


# ---------------------------------------------------------------------------
# DB insertion (uses SQLAlchemy session — only called with --load-db)
# ---------------------------------------------------------------------------

def _get_or_create_crop(session, name_he: str, name_en: str):
    """Get or lazily create a crops row (pattern from B2 NIImporter)."""
    from sqlalchemy import text
    result = session.execute(
        text("SELECT id FROM crops WHERE name_he = :name_he"),
        {"name_he": name_he},
    ).fetchone()
    if result:
        return result[0]

    # Lazy creation — minimal row with a placeholder family
    fam_result = session.execute(
        text("SELECT id FROM crop_families LIMIT 1")
    ).fetchone()
    if not fam_result:
        session.execute(
            text("INSERT INTO crop_families (scientific_name) VALUES ('Unknown')")
        )
        fam_result = session.execute(
            text("SELECT id FROM crop_families LIMIT 1")
        ).fetchone()
    fam_id = fam_result[0]

    session.execute(
        text(
            "INSERT INTO crops (name_he, name_en, family_id, category) "
            "VALUES (:name_he, :name_en, :fam_id, 'vegetables')"
        ),
        {"name_he": name_he, "name_en": name_en, "fam_id": fam_id},
    )
    result = session.execute(
        text("SELECT id FROM crops WHERE name_he = :name_he"),
        {"name_he": name_he},
    ).fetchone()
    return result[0]


def _upsert_knowledge_note(session, crop_id: int, note_type: str, body_text: str):
    """Insert or skip a crop_knowledge_notes row (ON CONFLICT DO NOTHING pattern)."""
    from sqlalchemy import text
    now = datetime.now(timezone.utc).isoformat()
    session.execute(
        text(
            "INSERT INTO crop_knowledge_notes "
            "(crop_id, source, trust_tier, note_type, body_text, "
            " is_internal_farm_use_only, extraction_model, created_at) "
            "VALUES (:crop_id, :source, :tier, :nt, :body, 1, :model, :now) "
            "ON CONFLICT (crop_id, source, note_type) DO NOTHING"
        ),
        {
            "crop_id": crop_id,
            "source": SOURCE_LABEL,
            "tier": TRUST_TIER,
            "nt": note_type,
            "body": body_text,
            "model": "load_masterclass_sheets.py/v1.0",
            "now": now,
        },
    )


def _upsert_variety(session, crop_id: int, variety_name: str):
    """Insert a crop_varieties row if not exists."""
    from sqlalchemy import text
    try:
        session.execute(
            text(
                "INSERT INTO crop_varieties (crop_id, name_en, is_default, is_grafted) "
                "VALUES (:crop_id, :name_en, 0, 0)"
            ),
            {"crop_id": crop_id, "name_en": variety_name},
        )
    except Exception:
        pass  # UNIQUE conflict — variety already exists


def load_to_db(cache_records: list[dict], db_url: str) -> dict[str, int]:
    """Insert all cache records into the database.

    Returns summary: {'notes_inserted': N, 'varieties_inserted': N, 'crops_created': N}
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    Session = sessionmaker(engine)
    notes_inserted = 0
    varieties_inserted = 0
    crops_created = 0

    with Session() as session:
        for rec in cache_records:
            name_he = rec["crop_name_he"]
            name_en = rec["crop_jmf_en"]

            # Check if crop existed before
            from sqlalchemy import text
            existing = session.execute(
                text("SELECT id FROM crops WHERE name_he = :nh"), {"nh": name_he}
            ).fetchone()
            crop_id = _get_or_create_crop(session, name_he, name_en)
            if not existing:
                crops_created += 1

            # Insert knowledge notes
            for note_type, note_list in rec["notes"].items():
                for note in note_list:
                    _upsert_knowledge_note(session, crop_id, note_type, note["body_text"])
                    notes_inserted += 1

            # Insert varieties
            for variety_name in rec["cultivars"]:
                _upsert_variety(session, crop_id, variety_name)
                varieties_inserted += 1

        session.commit()

    return {
        "notes_inserted": notes_inserted,
        "varieties_inserted": varieties_inserted,
        "crops_created": crops_created,
    }


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def _build_index_map() -> list[dict]:
    """Load _index.json and return list of processable sheet entries."""
    index_data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return index_data


def cli_main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Returns 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Load JMF MasterClass crop sheets into JSON cache and/or DB."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse all MDs and report planned actions without writing.")
    parser.add_argument("--load-db", action="store_true",
                        help="Write JSON cache files and load into DB.")
    parser.add_argument("--db-url", default="sqlite:///dev.db",
                        help="SQLAlchemy DB URL (default: sqlite:///dev.db).")
    parser.add_argument("--sheets-dir", default=str(SHEETS_DIR),
                        help="Path to the crop sheets directory.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR),
                        help="Path for JSON output files.")
    args = parser.parse_args(argv)

    if not args.dry_run and not args.load_db:
        print("ERROR: specify --dry-run or --load-db (or both).", file=sys.stderr)
        return 1

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(name)s: %(message)s")

    sheets_dir = Path(args.sheets_dir)
    output_dir = Path(args.output_dir)
    index_entries = _build_index_map()

    # Import JMF_CROP_MAP for validation
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP

    processed = 0
    skipped = 0
    skip_log: list[dict] = []
    cache_records: list[dict] = []
    all_warnings: list[str] = []

    for entry in index_entries:
        md_filename = entry["md"]
        english_keys = entry.get("english_keys", [])
        status = entry.get("status", "")
        hebrew_name = entry.get("hebrew_name", "")
        pages = entry.get("pages", "?")

        md_path = sheets_dir / md_filename

        if not md_path.exists():
            reason = f"MD file not found: {md_filename}"
            logger.warning(reason)
            skip_log.append({"md": md_filename, "reason": reason})
            skipped += 1
            continue

        # Determine primary english key → must be in JMF_CROP_MAP
        primary_key: str | None = None
        for ek in english_keys:
            if ek in JMF_CROP_MAP:
                primary_key = ek
                break

        if primary_key is None:
            reason = (
                f"No english_keys map to JMF_CROP_MAP (status={status}, "
                f"keys={english_keys!r}, hebrew={hebrew_name!r})"
            )
            logger.info("SKIP %s: %s", md_filename, reason)
            skip_log.append({"md": md_filename, "reason": reason})
            skipped += 1
            continue

        crop_name_he = JMF_CROP_MAP[primary_key]

        # Parse
        parsed = parse_md_sheet(md_path)
        all_warnings.extend(parsed["warnings"])

        cache_rec = md_to_cache_json(
            parsed=parsed,
            source=SOURCE_LABEL,
            crop_jmf_en=primary_key,
            crop_name_he=crop_name_he,
            md_filename=md_filename,
            pages=pages,
        )

        # Validate
        errors = validate_json_schema(cache_rec)
        if errors:
            logger.error("SCHEMA ERROR in %s: %s", md_filename, errors)
            skipped += 1
            skip_log.append({"md": md_filename, "reason": f"schema errors: {errors}"})
            continue

        cache_records.append(cache_rec)

        notes_count = sum(len(v) for v in cache_rec["notes"].values())
        cultivar_count = len(cache_rec["cultivars"])
        print(
            f"  [PLAN] {md_filename} → crop='{primary_key}' (he='{crop_name_he}') "
            f"| {notes_count} notes | {cultivar_count} cultivars"
        )
        processed += 1

    print(f"\nSUMMARY: {processed} processable, {skipped} skipped")
    if all_warnings:
        print(f"  {len(all_warnings)} truncation warning(s)")
    for sk in skip_log:
        print(f"  SKIP: {sk['md']} — {sk['reason']}")

    if args.dry_run and not args.load_db:
        print("\nDry-run complete — no files written.")
        return 0

    # Write JSON files
    if args.load_db:
        output_dir.mkdir(parents=True, exist_ok=True)
        for rec in cache_records:
            safe_name = re.sub(r"[^\w\-]", "_", rec["crop_jmf_en"])
            out_path = output_dir / f"{safe_name}.json"
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(rec, fh, ensure_ascii=False, indent=2)
            logger.info("Wrote %s", out_path)

        print(f"\nJSON files written to {output_dir}")

        # Load DB
        try:
            summary = load_to_db(cache_records, args.db_url)
            print(
                f"DB loaded: {summary['notes_inserted']} notes, "
                f"{summary['varieties_inserted']} varieties, "
                f"{summary['crops_created']} crops created."
            )
        except Exception as exc:
            logger.error("DB load failed: %s", exc)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
