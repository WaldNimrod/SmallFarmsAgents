"""Sheet 056 storage/washing M2M data loader.

SFA-S003-P002-WP-B1-patch07 LOD400 §3.2–3.3.
Parses documentation/jmf_masterclass_crop_sheets/056-eouio-oyono.md and
loads per-procedure notes into crop_knowledge_notes (crop_id=NULL) with
M2M linkages in crop_knowledge_notes_crops.

Usage:
    python scripts/load_sheet_056_storage.py --dry-run
    python scripts/load_sheet_056_storage.py --apply [--db-url sqlite:///...] [--verbose]
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Local alias table — sheet-056-specific labels (not in JMF_CROP_MAP post-patch06)
# SCOPED to this script. DO NOT touch constants.py (LOCKED).
# ---------------------------------------------------------------------------
SHEET_056_ALIASES: dict[str, list[str]] = {
    # Aggregate labels — decomposed into multiple resolved crops
    "All Bunches (beets, carrots, radishes, turnips)": ["Beets", "Carrots", "Radishes", "Turnips"],
    # Workbook-local plural / variant labels
    # v1.0.2: "Mesclun Mix" + "Baby Asian Greens" target name_he directly (resolver extended).
    # The corresponding English baseline was removed post-patch06; resolver supports
    # "he:" prefix to look up by crops.name_he directly when no English key exists.
    "Mesclun Mix": ["he:עלי בייבי"],
    "Baby Asian Greens": ["he:עלי בייבי"],
    "Frisée": ["Endive"],               # Frisée is cultivar of Endive
    "Frisée Heads": ["Endive"],
    "Little Gem Mini Lettuce": ["Lettuce"],
    "Brocoli": ["Broccoli"],            # workbook typo
    "Mini Fennel": ["Fennel"],          # Mini Fennel is cultivar of Fennel (removed from MAP post-patch06)
    "Storage Carrots": ["Carrots"],
    "Storage Beets": ["Beets"],
    "Winter Radishes": ["Radishes"],
    "Bell Peppers": ["Peppers"],
    "Eggplants": ["Eggplant"],
    "Fresh Beans": ["Beans (Bush)"],    # default to bush if not specified
    "Sweet Peas": ["Peas"],
    "Zucchini": ["Summer Squash"],      # Zucchini is cultivar of Summer Squash per patch03
}

# All known crop labels from sheet 056 (used in parser to identify crop lines)
_ALL_SHEET_056_CROP_LABELS: frozenset[str] = frozenset({
    # Direct JMF/TEND map matches
    "Arugula", "Spinach", "Mesclun Mix", "Baby Asian Greens", "Frisée",
    "Kale", "Swiss Chard", "Frisée Heads", "Lettuce", "Little Gem Mini Lettuce",
    "Brocoli", "Cauliflower",
    # HIGH PRESSURE GUNNING section
    "All Bunches (beets, carrots, radishes, turnips)", "Green Onion", "Mini Fennel",
    "Leeks",
    # ROOT WASHER section
    "Storage Carrots", "Storage Beets", "Winter Radishes",
    # NO WASHING section
    "Basil", "Bell Peppers", "Cucumbers", "Eggplants", "Melons", "Tomatoes",
    "Cabbage", "Fresh Beans", "Sweet Peas", "Garlic", "Zucchini",
})

SOURCE = "NI:jmf_sheet_056"
NOTE_TYPE = "storage_handling"
TRUST_TIER = "NI"
PROVENANCE_PDF = "JARD0001_tableaux-itinéraire_lavage_EN"
PROVENANCE_PAGES = "1-3"
BODY_TEXT_MAX = 2000

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# Section headers that appear verbatim in the MD (stripped, uppercase)
_SECTION_HEADERS: frozenset[str] = frozenset({
    "WASH TUBS & BUBBLER",
    "HIGH PRESSURE GUNNING",
    "ROOT WASHER",
    "NO WASHING",
})

# Table metadata lines to skip
_METADATA_PATTERNS: tuple[re.Pattern, ...] = tuple(re.compile(p) for p in [
    r"^WASHING ITINERARY FOR CROPS",
    r"^VEGETABLES$",
    r"^CLEANING ITINERARY$",
    r"^DRYING$",
    r"^STORAGE TEMP\.",
    r"^STORAGE LENGTH$",
    r"^\d+/\d+$",
    r"^Table Washing itinerary",
    r"^!\[Image",
    r"^<!--",
    r"^#",
    # Section-header annotation lines (e.g., "→ Always use sanitizing..." preamble)
    r"^→ Always use sanitizing",
    r"^→ Use high gun pressure",
    r"→ Water should be changed",
])

_STORAGE_PARAM_PATTERNS: tuple[re.Pattern, ...] = tuple(re.compile(p) for p in [
    r"^\d+\s*°[CF]",
    r"^\d+\s*°[CF]\s*[-–]\s*\d+\s*°[CF]",
    r"^\d+\s+days?$",
    r"^\d+\s+weeks?",
    r"^A few weeks",
    r"^Many months",
    r"^–$",
    r"^\d+\s+minutes?$",
    r"^Spin-dry",
    r"^Drip-dry",
    r"^Shake out",
])


def _is_metadata(line: str) -> bool:
    s = line.strip()
    return any(p.match(s) for p in _METADATA_PATTERNS)


def _is_storage_param(line: str) -> bool:
    s = line.strip()
    return any(p.match(s) for p in _STORAGE_PARAM_PATTERNS)


def _is_section_header(line: str) -> bool:
    return line.strip() in _SECTION_HEADERS


def _strip_arrow(line: str) -> str:
    return re.sub(r"^\s*→\s*", "", line).strip()


def _is_crop_label(text: str) -> bool:
    """Return True if the stripped text is a known sheet-056 crop label."""
    return text in _ALL_SHEET_056_CROP_LABELS


def _parse_sheet(md_path: Path) -> list[dict]:
    """Parse sheet 056 MD into crop-group blocks.

    Strategy:
    1. Pre-join continuation lines (indented lines following a → line).
    2. Scan line by line, tracking current section header.
    3. A "block" starts when we see one or more known crop-label lines (→ CropName).
    4. Block ends when: (a) storage params appear after procedure lines, or
       (b) a new crop-label cluster begins.
    5. Procedure text = all non-crop, non-param, non-header content between crop labels
       and the end of the block.

    Returns list of dicts: {crop_labels, procedure, section}
    """
    raw_text = md_path.read_text(encoding="utf-8")

    # Pre-join continuation lines (PDF-to-MD wrapping artefact)
    raw_lines = raw_text.splitlines()
    joined: list[str] = []
    for line in raw_lines:
        # A continuation line is indented AND does NOT start with → or known keywords
        if (joined and line.startswith(" ")
                and not line.lstrip().startswith("→")
                and not _is_section_header(line.strip())
                and line.strip()):
            joined[-1] = joined[-1].rstrip() + " " + line.strip()
        else:
            joined.append(line)

    blocks: list[dict] = []
    current_section = "GENERAL"
    current_crops: list[str] = []
    current_proc_lines: list[str] = []

    def _flush():
        nonlocal current_crops, current_proc_lines
        if current_crops:
            proc = " ".join(l for l in current_proc_lines if l.strip())
            blocks.append({
                "crop_labels": list(current_crops),
                "procedure": proc.strip(),
                "section": current_section,
            })
        current_crops = []
        current_proc_lines = []

    for raw_line in joined:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            continue
        if _is_metadata(stripped):
            continue
        if _is_section_header(stripped):
            _flush()
            current_section = stripped
            continue
        if _is_storage_param(stripped):
            current_proc_lines.append(stripped)
            continue

        # Lines with → arrow
        if "→" in stripped:
            content = _strip_arrow(stripped)
            if _is_crop_label(content):
                # If we already have a crop cluster AND have procedure text,
                # flush the current block before starting the next.
                # If we have crops but no procedure yet, just accumulate crops.
                if current_crops and current_proc_lines:
                    _flush()
                current_crops.append(content)
            else:
                # It's a procedure instruction line
                if current_crops:
                    current_proc_lines.append(content)
                # else: skip pre-crop instructions (section preambles already filtered)
        else:
            # Non-arrow line that's not a header or param
            if current_crops:
                current_proc_lines.append(stripped)

    _flush()
    return blocks


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------

def _resolve_crop_label(label: str, session) -> list[int]:
    """Resolve a sheet-056 label to one or more crops.id values.

    Resolution chain (v1.0.2):
      1. SHEET_056_ALIASES — returns list of resolution targets. Each target may be:
         - An English JMF_CROP_MAP key (regular case)
         - A "he:<hebrew>" prefix indicating direct crops.name_he lookup
      2. For English keys: JMF_CROP_MAP → name_he → crops.id via SELECT
      3. For "he:" targets: direct SELECT id FROM crops WHERE name_he = <hebrew>
      4. If not found: TEND_CROP_MAP → name_he → crops.id
      5. If not found: direct DB name_en match
      6. If still not found: log WARN, return []
    """
    from sqlalchemy import text as sa_text

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP, TEND_CROP_MAP

    def _lookup_by_name_he(name_he: str) -> list[int]:
        row = session.execute(
            sa_text("SELECT id FROM crops WHERE name_he = :n"),
            {"n": name_he},
        ).fetchone()
        return [row[0]] if row else []

    def _lookup_by_name_en(name_en: str) -> list[int]:
        row = session.execute(
            sa_text("SELECT id FROM crops WHERE name_en = :n"),
            {"n": name_en},
        ).fetchone()
        return [row[0]] if row else []

    def _resolve_target(target: str) -> list[int]:
        if target.startswith("he:"):
            name_he = target[3:]
            ids = _lookup_by_name_he(name_he)
            if not ids:
                logger.warning("WARN: 'he:' target %r not found in crops.name_he", name_he)
            return ids

        if target in JMF_CROP_MAP:
            ids = _lookup_by_name_he(JMF_CROP_MAP[target])
            if ids:
                return ids
            logger.warning("WARN: JMF_CROP_MAP[%r]=%r not in DB", target, JMF_CROP_MAP[target])

        if target in TEND_CROP_MAP:
            ids = _lookup_by_name_he(TEND_CROP_MAP[target])
            if ids:
                return ids
            logger.warning("WARN: TEND_CROP_MAP[%r]=%r not in DB", target, TEND_CROP_MAP[target])

        ids = _lookup_by_name_en(target)
        if ids:
            return ids

        logger.warning("WARN: label %r unresolvable", label)
        return []

    # Step 1: expand via SHEET_056_ALIASES
    if label in SHEET_056_ALIASES:
        targets = SHEET_056_ALIASES[label]
        ids: list[int] = []
        seen: set[int] = set()
        for t in targets:
            for cid in _resolve_target(t):
                if cid not in seen:
                    seen.add(cid)
                    ids.append(cid)
        return ids

    # Direct resolution
    return _resolve_target(label)


# ---------------------------------------------------------------------------
# Body text composer
# ---------------------------------------------------------------------------

def _compose_body_text(block: dict) -> str:
    """Compose body_text from a block. Truncated to BODY_TEXT_MAX."""
    crops_str = ", ".join(block["crop_labels"])
    section = block["section"]
    procedure = block["procedure"]
    body = f"[{section}] Crops: {crops_str}. Procedure: {procedure}"
    if len(body) > BODY_TEXT_MAX:
        body = body[: BODY_TEXT_MAX - 3] + "..."
    return body


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def _dry_run(blocks: list[dict], session) -> int:
    """Print planned actions without mutations. Returns 0."""
    print(f"[DRY-RUN] Sheet 056 parser — {len(blocks)} block(s) parsed\n")
    total_notes = 0
    total_junction = 0
    for i, block in enumerate(blocks, 1):
        crop_ids: list[int] = []
        for label in block["crop_labels"]:
            crop_ids.extend(_resolve_crop_label(label, session))
        body = _compose_body_text(block)
        print(f"  [PLAN] Block {i}: crops={block['crop_labels']}")
        print(f"    resolved_ids={crop_ids}, body_len={len(body)}")
        print(f"    procedure_preview={block['procedure'][:80]!r}")
        total_notes += 1
        total_junction += len(crop_ids)
    print(f"\n[DRY-RUN] SUMMARY:")
    print(f"  Notes to insert:   {total_notes}")
    print(f"  Junction rows:     {total_junction}")
    print(f"  Source:            {SOURCE}")
    return 0


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def _apply(blocks: list[dict], session) -> tuple[int, int]:
    """Insert notes + junction rows. Idempotent. Returns (notes_inserted, junction_inserted)."""
    from sqlalchemy import text as sa_text

    now = datetime.now(timezone.utc).isoformat()
    notes_inserted = 0
    junction_inserted = 0

    for block in blocks:
        body = _compose_body_text(block)

        # Idempotency: skip if note with same source+body_text already exists
        existing = session.execute(
            sa_text(
                "SELECT id FROM crop_knowledge_notes "
                "WHERE source = :src AND body_text = :body"
            ),
            {"src": SOURCE, "body": body},
        ).fetchone()

        if existing:
            note_id = existing[0]
            logger.debug("SKIP note id=%d (idempotent)", note_id)
        else:
            session.execute(
                sa_text(
                    "INSERT INTO crop_knowledge_notes "
                    "(crop_id, source, trust_tier, note_type, body_text, "
                    " provenance_pdf, provenance_pages, "
                    " is_internal_farm_use_only, created_at) "
                    "VALUES (NULL, :src, :tier, :ntype, :body, "
                    "        :ppdf, :ppages, TRUE, :now)"
                ),
                {
                    "src": SOURCE, "tier": TRUST_TIER, "ntype": NOTE_TYPE,
                    "body": body, "ppdf": PROVENANCE_PDF,
                    "ppages": PROVENANCE_PAGES, "now": now,
                },
            )
            note_id = session.execute(
                sa_text(
                    "SELECT id FROM crop_knowledge_notes "
                    "WHERE source = :src AND body_text = :body"
                ),
                {"src": SOURCE, "body": body},
            ).fetchone()[0]
            notes_inserted += 1
            logger.info("INSERT note id=%d (block crops=%s)", note_id, block["crop_labels"])

        # Junction rows
        for label in block["crop_labels"]:
            for cid in _resolve_crop_label(label, session):
                exists_junc = session.execute(
                    sa_text(
                        "SELECT 1 FROM crop_knowledge_notes_crops "
                        "WHERE note_id = :nid AND crop_id = :cid"
                    ),
                    {"nid": note_id, "cid": cid},
                ).fetchone()
                if not exists_junc:
                    session.execute(
                        sa_text(
                            "INSERT INTO crop_knowledge_notes_crops (note_id, crop_id) "
                            "VALUES (:nid, :cid)"
                        ),
                        {"nid": note_id, "cid": cid},
                    )
                    junction_inserted += 1

    session.commit()
    return notes_inserted, junction_inserted


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cli_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Load sheet 056 storage/washing notes into crop_knowledge_notes."
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and report, no DB writes.")
    parser.add_argument("--apply", action="store_true", help="Insert notes into DB.")
    parser.add_argument(
        "--db-url",
        default="sqlite:///:memory:",
        help="SQLAlchemy DB URL (default: sqlite:///:memory:).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable DEBUG logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if not args.dry_run and not args.apply:
        parser.print_help()
        return 1

    md_path = REPO_ROOT / "documentation" / "jmf_masterclass_crop_sheets" / "056-eouio-oyono.md"
    if not md_path.exists():
        logger.error("Sheet 056 MD not found: %s", md_path)
        return 2

    blocks = _parse_sheet(md_path)
    if not blocks:
        logger.error("Parser returned 0 blocks — check MD structure.")
        return 3

    if args.dry_run:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        engine = create_engine(args.db_url)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            return _dry_run(blocks, session)

    # --apply
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(args.db_url)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        notes, junc = _apply(blocks, session)

    print(f"[APPLY] Done. notes_inserted={notes}, junction_inserted={junc}")
    return 0


if __name__ == "__main__":
    sys.exit(cli_main())
