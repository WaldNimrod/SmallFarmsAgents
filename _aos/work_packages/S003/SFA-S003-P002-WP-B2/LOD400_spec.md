---
id: SFA-S003-P002-WP-B2-LOD400
wp: SFA-S003-P002-WP-B2 — JMF PDF NI Extraction Layer (AI-assisted)
gate: L-GATE_S (LOD400 — implementation spec)
status: PRE_LOD400_LOCK — awaiting team_190 L-GATE_S verdict
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD200_spec.md
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
wp_a_lod400_ref: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md
wp_b1_patch01_lock_commit: "3e1f946"   # extended JMF_CROP_MAP
builder: sfa_build (separate session per IR#1)
validator: team_190 (non-Claude, Iron Rule #1)
---

# LOD400 — SFA-S003-P002-WP-B2: JMF PDF NI Extraction Layer

**Read before writing a single line of code:**
1. LOD200 (this WP): `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD200_spec.md`
2. PROGRAM_BRIEF §3 (NI scope reference): `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`
3. WP-A `ni_importer.py` (LOD500_LOCKED — read-only): `organic_market_agent/crop_book/importer/ni_importer.py`. This is the `NiSourceBase` abstract class B2 subclasses.
4. WP-A `source_registry.py` (LOD500_LOCKED): verify `get_source_spec("NI:any")` returns class `"NI"` with `is_hard_override=True` (prefix-match path).
5. Extended `JMF_CROP_MAP` (86 entries; post-patch01): `organic_market_agent/crop_book/constants.py`. Used for ebook-to-crop_id resolution.

---

## 1. Goal

Build the **first concrete `NIImporter` subclasses** materializing the WP-A skeleton — extracting per-crop narrative knowledge from JMF MasterClass PDFs as NI-tier hard-override data:

1. **Migration 045** — new table `crop_knowledge_notes` (per-crop narrative, type-classified, with licensing + provenance fields)
2. **New ORM module** `organic_market_agent/crop_book/crop_knowledge_notes.py`
3. **3 concrete `NIImporter` subclasses:**
   - `ni/jmf_book.py` — Market Gardener 240-page ebook
   - `ni/jmf_ft_flameweed.py` — Fiche Technique flame-weeding PDF
   - `ni/jmf_ft_biopesticide.py` — Fiche Technique biopesticide table PDF
4. **Extraction runner script** `scripts/extract_jmf_ni.py` — one-time CLI that calls Anthropic API to produce the JSON cache (NOT production code, NOT runtime)
5. **JSON cache directory** `data/jmf/extracted/<source_name>/<crop_name_en>.json` — committed to repo per advisory #2 disposition
6. **`seed.py` CLI additions** — `--ni-only`, `--no-ni`
7. **≥ 15 tests** covering parser correctness, LLM stub handling, cache schema, DB integration, idempotency, FT PDF coverage, licensing flag enforcement
8. **WP-A engine reuse only** — every NI row uses the standard `_upsert_source_value` semantics (for `cultivar_recommendation` field) or the new `_upsert_knowledge_note` (for `crop_knowledge_notes` table). Source label format: `'NI:jmf_book_v1'` / `'NI:jmf_ft_flameweed_v1'` / `'NI:jmf_ft_biopesticide_v1'`.

On completion:
- `python -m organic_market_agent.crop_book.importer.seed --all` (with `--ni-only`) populates `crop_knowledge_notes` rows from cached JSON.
- `python scripts/extract_jmf_ni.py --source jmf_book --rebuild --crop arugula` regenerates the cache for a specific (source, crop) pair.

---

## 2. Architecture

### 2.1 Module structure

```
organic_market_agent/crop_book/
├── crop_knowledge_notes.py            ← NEW: CropKnowledgeNote SQLAlchemy ORM
└── importer/
    ├── ni/                            ← NEW directory
    │   ├── __init__.py                ← NEW: re-export the 3 subclasses + registry
    │   ├── jmf_book.py                ← NEW: 240-page ebook subclass
    │   ├── jmf_ft_flameweed.py        ← NEW: FT_FLAMEWEEDING PDF subclass
    │   └── jmf_ft_biopesticide.py     ← NEW: FT_TABLEAUAPPLICATION PDF subclass
    └── seed.py                        ← MODIFY: --ni-only, --no-ni flags + 1 call-site block

organic_market_agent/db/versions/
└── 045_crop_knowledge_notes.py        ← NEW

scripts/
└── extract_jmf_ni.py                  ← NEW: one-time CLI (NOT production code)

data/jmf/extracted/                    ← NEW directory tree (COMMITTED)
├── jmf_book/
│   ├── arugula.json
│   ├── basil.json
│   └── … (per-crop files, one per JMF chapter found)
├── jmf_ft_flameweed/
│   └── _table.json                   ← single structured table (not per-crop)
└── jmf_ft_biopesticide/
    └── _table.json                   ← single structured table

tests/crop_book/
├── test_crop_knowledge_notes_orm.py
├── test_migration_045.py
├── test_ni_jmf_book.py
├── test_ni_jmf_ft_flameweed.py
├── test_ni_jmf_ft_biopesticide.py
├── test_ni_cache_schema.py
├── test_ni_idempotency.py
├── test_ni_licensing_flag.py
└── test_seed_ni_cli.py

CHANGELOG.md                                ← MODIFY: [Unreleased] entry
```

### 2.2 No changes to these files (LOD500_LOCKED + raw-material)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/views.py`, `publisher/`, `mu-plugin/` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..044_*.py` | All prior migrations (045 reserved for B2) |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard |
| `organic_market_agent/crop_book/importer/jmf.py`, `jmf_masterclass.py` | B1 deliverables — LOD500_LOCKED |
| `organic_market_agent/crop_book/crop_task_templates.py` | B1 deliverable — LOD500_LOCKED |
| `organic_market_agent/db/versions/044_crop_task_templates.py` | B1 deliverable |
| `organic_market_agent/crop_book/models.py`, `source_registry.py`, `field_policy.py`, `enrichment_models.py`, `importer/reconciler.py`, `importer/enrichment_runner.py` | WP-A engine SSoT |
| `organic_market_agent/crop_book/importer/ni_importer.py` | WP-A skeleton — DO NOT MODIFY (B2 SUBCLASSES it without touching the base) |
| `organic_market_agent/crop_book/constants.py` | LOD500_LOCKED via B1-patch01 (extended JMF_CROP_MAP). B2 does NOT modify constants.py — uses JMF_CROP_MAP read-only. |

**Permitted modifications:**
- `organic_market_agent/crop_book/importer/seed.py` — add `--ni-only`, `--no-ni` flags + 1 new call-site block
- `CHANGELOG.md` — `[Unreleased]` entry

### 2.3 Engine + cache flow

```
                          ┌─── one-time prepare step ────┐
                          │   (NOT runtime; NOT in tests) │
                          │                                │
JMF PDFs (3 files)        │   pdftotext → text chunks     │
       │                  │       ↓                        │
       ▼                  │   scripts/extract_jmf_ni.py    │
   pdftotext              │       ↓                        │
       │                  │   Anthropic API (Claude Sonnet)│
       ▼                  │       ↓                        │
   raw text               │   structured JSON              │
                          │       ↓                        │
                          │   data/jmf/extracted/...json   │   ← COMMITTED
                          └────────────────────────────────┘
                                       │
                                       ▼  (committed cache, deterministic)
                          ┌─── runtime importer ───────────┐
                          │                                 │
                          │   ni/jmf_book.py.load()         │
                          │       reads JSON; emits rows    │
                          │       ↓                         │
                          │   _upsert_knowledge_note(...)   │
                          │       ↓                         │
                          │   crop_knowledge_notes (DB)     │
                          │   crop_variety_source_values    │
                          │       (cultivar_recommendation) │
                          └─────────────────────────────────┘
```

**Critical invariant:** the runtime path NEVER calls the Anthropic API and NEVER reads PDFs. Tests stub the cache directly with fixture JSON files.

---

## 3. Migration 045 — `crop_knowledge_notes`

File: `organic_market_agent/db/versions/045_crop_knowledge_notes.py`

```python
"""Migration 045: crop_knowledge_notes table — per-crop NI narrative.

SFA-S003-P002-WP-B2 LOD400 §3. Additive only.
"""
from alembic import op
import sqlalchemy as sa

revision = "045"
down_revision = "044"
branch_labels = None
depends_on = None

_NOTE_TYPE_ENUM = (
    "pest_disease", "harvest_marker", "storage_handling",
    "rotation_companion", "cultivar_recommendation", "growing_tip",
    "irrigation", "nursery_specific",
    "flame_weed_timing", "biopesticide_spray",
)

def upgrade():
    op.create_table(
        "crop_knowledge_notes",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  primary_key=True, autoincrement=True),
        sa.Column("crop_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                  sa.ForeignKey("crops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.VARCHAR(50), nullable=False),
        sa.Column("trust_tier", sa.VARCHAR(20), nullable=False),
        sa.Column("note_type", sa.VARCHAR(40), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("provenance_pdf", sa.VARCHAR(200), nullable=True),
        sa.Column("provenance_pages", sa.VARCHAR(40), nullable=True),
        sa.Column("is_internal_farm_use_only", sa.Boolean,
                  nullable=False, server_default=sa.text("true")),
        sa.Column("extraction_model", sa.VARCHAR(50), nullable=True),
        sa.Column("extracted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True),
                  nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("crop_id", "source", "note_type",
                            name="uq_ckn_crop_source_type"),
        sa.CheckConstraint(
            "note_type IN (" + ",".join(repr(v) for v in _NOTE_TYPE_ENUM) + ")",
            name="ck_ckn_note_type",
        ),
        sa.CheckConstraint(
            "length(body_text) <= 2000",
            name="ck_ckn_body_text_length",
        ),
    )
    op.create_index("idx_ckn_crop", "crop_knowledge_notes", ["crop_id"])
    op.create_index("idx_ckn_type", "crop_knowledge_notes", ["note_type"])

def downgrade():
    op.drop_index("idx_ckn_type", table_name="crop_knowledge_notes")
    op.drop_index("idx_ckn_crop", table_name="crop_knowledge_notes")
    op.drop_table("crop_knowledge_notes")
```

**SQLite compatibility:** `length(body_text) <= 2000` is portable (both Postgres and SQLite use `length()`). `now()` may need `CURRENT_TIMESTAMP` on SQLite via dialect branch — handle in same fashion as B1 §3 if `alembic upgrade 045` fails.

**Body-text length CHECK** is the schema-level enforcement of advisory #1's fair-use snippet bound. AC-04b regression-tests this constraint.

---

## 4. ORM — `crop_knowledge_notes.py`

File: `organic_market_agent/crop_book/crop_knowledge_notes.py` (NEW)

```python
"""CropKnowledgeNote ORM — per-crop NI narrative (migration 045).

SFA-S003-P002-WP-B2 LOD400 §4. Mirrors WP-A/B1 pattern.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, TIMESTAMP, Text,
    UniqueConstraint, VARCHAR,
)
from sqlalchemy.orm import Mapped, mapped_column

from organic_market_agent.db.base import Base

_PK_TYPE = BigInteger().with_variant(Integer(), "sqlite")

NOTE_TYPE_VALUES: tuple[str, ...] = (
    "pest_disease", "harvest_marker", "storage_handling",
    "rotation_companion", "cultivar_recommendation", "growing_tip",
    "irrigation", "nursery_specific",
    "flame_weed_timing", "biopesticide_spray",
)

# Body-text length cap — fair-use snippet bound (LOD400 §5.4)
BODY_TEXT_MAX_LENGTH: int = 2000


class CropKnowledgeNote(Base):
    __tablename__ = "crop_knowledge_notes"
    __table_args__ = (
        UniqueConstraint("crop_id", "source", "note_type",
                         name="uq_ckn_crop_source_type"),
        CheckConstraint(
            "note_type IN ({})".format(",".join(repr(v) for v in NOTE_TYPE_VALUES)),
            name="ck_ckn_note_type",
        ),
        CheckConstraint(
            f"length(body_text) <= {BODY_TEXT_MAX_LENGTH}",
            name="ck_ckn_body_text_length",
        ),
    )

    id: Mapped[int] = mapped_column(_PK_TYPE, primary_key=True, autoincrement=True)
    crop_id: Mapped[int] = mapped_column(
        _PK_TYPE, ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    trust_tier: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    note_type: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    provenance_pdf: Mapped[Optional[str]] = mapped_column(VARCHAR(200), nullable=True)
    provenance_pages: Mapped[Optional[str]] = mapped_column(VARCHAR(40), nullable=True)
    is_internal_farm_use_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    extraction_model: Mapped[Optional[str]] = mapped_column(VARCHAR(50), nullable=True)
    extracted_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (f"<CropKnowledgeNote crop_id={self.crop_id} type={self.note_type!r} "
                f"source={self.source!r} len(body)={len(self.body_text)}>")
```

---

## 5. JSON cache schema

Path: `data/jmf/extracted/<source_name>/<crop_name_en>.json`

Schema (top-level — same shape for jmf_book / jmf_ft_flameweed / jmf_ft_biopesticide):

```json
{
  "schema_version": "1.0",
  "source": "NI:jmf_book_v1",
  "crop_jmf_en": "Arugula",
  "provenance": {
    "pdf": "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF",
    "pages": "42-45",
    "extraction_model": "claude-sonnet-4.6",
    "extracted_at": "2026-05-25T14:23:00Z"
  },
  "notes": {
    "pest_disease":           "Flea beetles affect early-season plantings...",
    "harvest_marker":         "Harvest when leaves are 4–6 inches...",
    "storage_handling":       "Store at 1–4 °C, 95% humidity...",
    "rotation_companion":     "Rotate away from brassicas...",
    "cultivar_recommendation": "Astro is more bolt-resistant...",
    "growing_tip":            "Direct seed every 7–10 days for continuous harvest...",
    "irrigation":             "Light, frequent watering...",
    "nursery_specific":       null
  }
}
```

For `jmf_ft_flameweed` / `jmf_ft_biopesticide` cache files, only the FT-specific note types are present (`flame_weed_timing` / `biopesticide_spray`) and `nursery_specific` etc. are absent. Schema validators allow missing keys (null-equivalent).

**Field constraints (enforced at extraction time and re-verified at runtime upsert):**
- `body_text` for each note ≤ 2000 chars (matches DB CHECK constraint)
- `note_type` keys MUST be a subset of `NOTE_TYPE_VALUES` (ORM tuple from §4)
- `provenance.pdf` MUST match the filename of the source PDF
- `provenance.pages` MUST be a valid page range string (regex `^\d+(-\d+)?$`)

JSON files are committed to repo. `.gitattributes` adds `data/jmf/extracted/** linguist-vendored` to keep diff stats reasonable.

---

## 6. `extraction_runner` — `scripts/extract_jmf_ni.py`

File: `scripts/extract_jmf_ni.py` (NEW; CLI tool, NOT production code)

```python
"""One-time extraction runner — calls Anthropic API to produce the JSON cache.

NOT runtime. NOT in tests. NOT imported by the runtime path. Run manually:

    python scripts/extract_jmf_ni.py --source jmf_book --crop arugula
    python scripts/extract_jmf_ni.py --source jmf_book --all
    python scripts/extract_jmf_ni.py --source jmf_ft_flameweed
    python scripts/extract_jmf_ni.py --source jmf_book --rebuild --crop arugula

Requires: ANTHROPIC_API_KEY env var. Reads PDFs from JMF_PDF_DIR
(default: /Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass).
"""
import argparse, json, pathlib, sys
from datetime import datetime, timezone
import anthropic

# Constants
SUPPORTED_SOURCES = ("jmf_book", "jmf_ft_flameweed", "jmf_ft_biopesticide")
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_TEMPERATURE = 0.0     # deterministic structured extraction
CACHE_BASE = pathlib.Path("data/jmf/extracted")
SCHEMA_VERSION = "1.0"

# Per-source dispatch
def extract_jmf_book(client, pdf_text, crop_jmf_en, crop_chapter_pages):
    """Extract per-crop notes from a chapter slice. Returns dict matching §5 schema."""
    prompt = f"""You are extracting structured horticultural knowledge from a
book chapter about the crop "{crop_jmf_en}". The chapter text follows.
Extract concise farm-relevant notes (≤2000 characters each) for these
8 note types: pest_disease, harvest_marker, storage_handling,
rotation_companion, cultivar_recommendation, growing_tip, irrigation,
nursery_specific. Return ONLY valid JSON with the structure shown.
Use null for any note_type that the chapter does not address.

Chapter text:
\"\"\"
{pdf_text}
\"\"\"

Output JSON ONLY (no preamble, no markdown):
{{
  "pest_disease": "..." or null,
  "harvest_marker": "..." or null,
  ... (all 8 keys)
}}"""
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=4096,
        temperature=DEFAULT_TEMPERATURE,
        messages=[{"role": "user", "content": prompt}],
    )
    # Parse JSON from response; validate length; return.

def extract_jmf_ft_flameweed(client, pdf_text):
    """Extract flame-weed timing table → per-crop dict."""
    # ... similar pattern; produces dict mapping crop_jmf_en → flame_weed_timing string

def extract_jmf_ft_biopesticide(client, pdf_text):
    """Extract biopesticide application table → per-crop dict."""
    # ... similar pattern

def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("--source", choices=SUPPORTED_SOURCES, required=True)
    parser.add_argument("--crop", help="Restrict to single crop (English JMF name)")
    parser.add_argument("--all", action="store_true", help="Run all crops in JMF_CROP_MAP")
    parser.add_argument("--rebuild", action="store_true", help="Overwrite existing cache file")
    parser.add_argument("--pdf-dir", type=pathlib.Path, default=...)
    # ... arg parsing
    # Dispatch per --source. Call appropriate extract_* function. Write JSON. Done.

if __name__ == "__main__":
    main()
```

**Anthropic API contract:**
- Model: `claude-sonnet-4-6` (or current Sonnet); temperature `0.0` for determinism
- Max tokens: 4096 per call (chapter excerpts ≤ 3000 tokens; output ≤ 2000 chars × 8 = 16 KB ≪ 4096 tokens)
- Cost estimate: ~52 crops × 8 notes × 1 LLM call ≈ 416 calls @ Sonnet pricing. One-time cost; cached forever after.

---

## 7. NIImporter subclasses

### 7.1 `ni/__init__.py` (NEW — re-export + registry)

```python
"""NI importer subclasses (SFA-S003-P002-WP-B2).

Each subclass reads a committed JSON cache and produces DB rows via
the WP-A NiSourceBase abstract base.
"""
from organic_market_agent.crop_book.importer.ni.jmf_book import JmfBookSource
from organic_market_agent.crop_book.importer.ni.jmf_ft_flameweed import JmfFtFlameweedSource
from organic_market_agent.crop_book.importer.ni.jmf_ft_biopesticide import JmfFtBiopesticideSource

NI_SOURCES = (JmfBookSource, JmfFtFlameweedSource, JmfFtBiopesticideSource)
__all__ = ["JmfBookSource", "JmfFtFlameweedSource", "JmfFtBiopesticideSource", "NI_SOURCES"]
```

### 7.2 `ni/jmf_book.py` (NEW)

```python
"""JmfBookSource — Market Gardener 240-page ebook NI subclass.

Reads cached JSON from data/jmf/extracted/jmf_book/<crop>.json.
"""
from pathlib import Path
import json
from organic_market_agent.crop_book.importer.ni_importer import NiSourceBase

class JmfBookSource(NiSourceBase):
    source_label: str = "NI:jmf_book_v1"
    cache_dir: Path = Path("data/jmf/extracted/jmf_book")
    canonical_pdf_filename: str = "THEMARKETGARDENEREBOOK (from macBook Air - nimrod).PDF"

    def load(self) -> list[dict]:
        """Read all <crop>.json files in cache_dir; return upsert-ready row dicts.

        Each cache file produces:
          - 1 CropKnowledgeNote row per non-null `notes.<type>` key (up to 8)
          - 0-or-1 CropVarietySourceValue row for cultivar_recommendation
            (when present, mapped to the default-baseline variety; same
            pattern as B1 _default_variety_id).

        Rows returned with:
          source = "NI:jmf_book_v1"
          trust_tier = "NI"
          confidence_weight = None
          is_internal_farm_use_only = True
          provenance_pdf = canonical_pdf_filename
          provenance_pages = cache_file["provenance"]["pages"]
        """
```

### 7.3 `ni/jmf_ft_flameweed.py` (NEW)

```python
"""JmfFtFlameweedSource — FT_FLAMEWEEDING PDF NI subclass.

Reads cached JSON from data/jmf/extracted/jmf_ft_flameweed/_table.json.
The cache file is a single dict mapping crop_jmf_en → flame_weed_timing string.
Produces 1 CropKnowledgeNote row per crop with note_type='flame_weed_timing'.
"""
class JmfFtFlameweedSource(NiSourceBase):
    source_label = "NI:jmf_ft_flameweed_v1"
    cache_dir = Path("data/jmf/extracted/jmf_ft_flameweed")
    canonical_pdf_filename = "FT_FINALE_FLAMEWEEDING.PDF"
    ...
```

### 7.4 `ni/jmf_ft_biopesticide.py` (NEW)

Mirror pattern: `source_label = "NI:jmf_ft_biopesticide_v1"`; produces one `biopesticide_spray` note per crop covered in the table.

### 7.5 `_upsert_knowledge_note` helper (in `ni_importer.py` extension — additive only)

```python
def _upsert_knowledge_note(
    session,
    crop_id: int,
    source: str,
    note_type: str,
    body_text: str,
    *,
    provenance_pdf: str | None = None,
    provenance_pages: str | None = None,
    extraction_model: str | None = None,
    extracted_at: datetime | None = None,
) -> CropKnowledgeNote:
    """Upsert on (crop_id, source, note_type).

    trust_tier='NI', is_internal_farm_use_only=True hardcoded.
    """
```

**Where to put this helper:** add to `ni_importer.py` as a module-level helper function NEXT TO the existing `NiSourceBase` class (not inside). This is the ONLY permitted modification to the LOD500_LOCKED `ni_importer.py` — append-only, no class change, no base modification.

---

## 8. `seed.py` modifications

Add (after the existing B1 + patch01 + B3 flags):

```python
parser.add_argument(
    "--ni-only", action="store_true",
    help="Run only NI ingestion (skip JMF MasterClass / Tend / Tend overlay).",
)
parser.add_argument(
    "--no-ni", action="store_true",
    help="Skip NI ingestion.",
)
```

Mutual exclusion: `--ni-only ↔ --no-ni`.

Call site (inside `with SessionFactory() as session:` block, AFTER JMF MasterClass + Tend overlay + WP-A Tend imports — NI hard-override comes LAST so it wins precedence):

```python
if not args.no_ni:
    from organic_market_agent.crop_book.importer.ni import NI_SOURCES
    for src_class in NI_SOURCES:
        src = src_class()
        rows = src.load()
        for row in rows:
            # Each row is a dict tagged with target_table=
            #   "crop_knowledge_notes" → call _upsert_knowledge_note
            #   "crop_variety_source_values" → call _upsert_source_value (for cultivar_recommendation)
            if row["target_table"] == "crop_knowledge_notes":
                _upsert_knowledge_note(session, **row["payload"])
            else:
                _upsert_source_value(session, **row["payload"])
    session.flush()

if args.ni_only:
    if not args.dry_run:
        session.commit()
    return
```

---

## 9. Acceptance Criteria

**AC-01 — Migration 045 created and clean.**
`alembic upgrade head` creates `crop_knowledge_notes` with correct DDL; `alembic downgrade 044` drops it. CHECK constraints on `note_type` and `body_text` length active. Both Postgres and SQLite work.

**AC-02 — `CropKnowledgeNote` ORM correct.**
13 columns mapped with correct types; `NOTE_TYPE_VALUES` exported (10 entries); `BODY_TEXT_MAX_LENGTH == 2000`.

**AC-03 — NI subclasses importable + properly registered.**
`from organic_market_agent.crop_book.importer.ni import NI_SOURCES; assert len(NI_SOURCES) == 3`. Each subclass has `source_label` matching `'NI:<source>_v1'` pattern. Each subclass's `load()` method is callable.

**AC-04a — Body-text length CHECK enforced at DB level.**
Attempting to insert a row with `body_text` of 2001 characters raises `IntegrityError`. (Validates the fair-use snippet bound is at the schema layer, not just runtime.)

**AC-04b — `note_type` CHECK enforced.**
Inserting `note_type='nonsense_type'` raises `IntegrityError`. All 10 enum values accepted.

**AC-05 — Licensing flag default + enforcement.**
After importing any NI cache row, the resulting `crop_knowledge_notes` row has `is_internal_farm_use_only=True`. Test asserts this default cannot be silently flipped by the importer.

**AC-06 — UNIQUE constraint on (crop_id, source, note_type).**
Two inserts with identical `(crop_id, source='NI:jmf_book_v1', note_type='pest_disease')` raises `IntegrityError`. Re-import via `_upsert_knowledge_note` is idempotent (update path).

**AC-07 — `JmfBookSource.load()` reads fixture JSON correctly.**
Given a fixture file at `tests/crop_book/fixtures/ni/jmf_book/arugula.json` with 3 non-null note types, `JmfBookSource(cache_dir=fixture_dir).load()` returns 3 row dicts (one per non-null note_type), each carrying provenance + source + correct note_type.

**AC-08 — Cache schema validation.**
A fixture cache file missing the `schema_version` field is rejected with a clear error message. A file with `note_type` not in `NOTE_TYPE_VALUES` is rejected. A file with `body_text > 2000` chars in a note is rejected pre-DB.

**AC-09 — FT PDF subclasses work against fixture caches.**
`JmfFtFlameweedSource` + `JmfFtBiopesticideSource` each load their fixture cache and produce ≥ 1 row per crop in the cache. note_type matches the source.

**AC-10 — DB integration: end-to-end with fixture cache.**
On a SQLite in-memory DB seeded with 3 crops + all 3 NI cache fixtures populated: `import_ni()` (or the seed.py NI loop) produces ≥ 3 `crop_knowledge_notes` rows.

**AC-11 — Idempotency.**
Running the NI import twice in a row produces the same row count after second call as after first.

**AC-12 — Engine reuse: cultivar_recommendation via _upsert_source_value.**
When a JmfBook cache contains a `cultivar_recommendation` note, the NI loader ALSO produces a `crop_variety_source_values` row with `field_name='cultivar_recommendation'`, `source='NI:jmf_book_v1'`, `trust_tier='NI'`, `confidence_weight=NULL`, `is_outlier_rejected=False`. This row is hard-override per WP-A engine.

**AC-13 — CLI `--ni-only` + `--no-ni`.**
`seed.py --ni-only --dry-run` populates only NI rows. `seed.py --all --no-ni --dry-run` produces zero rows with `source LIKE 'NI:%'`. Mutual exclusion enforced.

**AC-14 — `extraction_runner` integration test (stubbed).**
With ANTHROPIC_API_KEY stubbed, `scripts/extract_jmf_ni.py --source jmf_book --crop arugula --dry-run` produces a valid JSON file matching the schema. (Real Anthropic calls are NOT run in tests; the dry-run path uses a fixture response.)

**AC-15 — Cache directory commit policy.**
`data/jmf/extracted/` directory exists in the repo (NOT gitignored). `.gitattributes` declares `data/jmf/extracted/** linguist-vendored`. At least 1 sample JSON file per source is committed (for repository reproducibility).

**AC-16 — All existing tests still PASS (regression).**
After the patch lands, full `pytest tests/crop_book/ -q` shows no regressions on the B1 + patch01 + B3 (if B3 has landed) tests.

**AC-17 — validate_aos.sh 0 FAIL.**
`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.

**AC-18 — No LOD500_LOCKED file modified beyond §2.2 scope.**
`git diff <patch01-lock-commit>..HEAD -- <each path in §2.2>` empty for all locked paths.
The only PERMITTED change to `ni_importer.py` is the APPEND of `_upsert_knowledge_note` helper at module level (§7.5). The `NiSourceBase` class itself MUST NOT be modified.

---

## 10. Test requirements

**Minimum 15 new tests** across 9 new test files:

| File | Tests | Coverage |
|------|-------|----------|
| `test_crop_knowledge_notes_orm.py` | 2 | AC-02 + AC-04b |
| `test_migration_045.py` | 2 | AC-01 + AC-04a (length CHECK enforcement) |
| `test_ni_jmf_book.py` | 3 | AC-03 + AC-07 + AC-12 (cultivar_recommendation engine reuse) |
| `test_ni_jmf_ft_flameweed.py` | 1 | AC-09 (FT cache load) |
| `test_ni_jmf_ft_biopesticide.py` | 1 | AC-09 (FT cache load) |
| `test_ni_cache_schema.py` | 2 | AC-08 (schema validation: missing version, bad note_type, oversize body) |
| `test_ni_idempotency.py` | 1 | AC-11 |
| `test_ni_licensing_flag.py` | 1 | AC-05 (flag default + immutability) |
| `test_seed_ni_cli.py` | 2 | AC-13 (--ni-only, --no-ni, mutual exclusion) |

**+1 fixture file** per source under `tests/crop_book/fixtures/ni/`:
- `jmf_book/arugula.json` (3 non-null note types)
- `jmf_book/basil.json` (different non-null set)
- `jmf_ft_flameweed/_table.json` (3 crops)
- `jmf_ft_biopesticide/_table.json` (3 crops)

All tests use SQLite in-memory + fixture JSON files. NO live Anthropic API calls in tests. Marker: `@pytest.mark.crop_book`.

---

## 11. Build sequence (10 steps)

**Step 1** — Read this LOD400 + LOD200 + PROGRAM_BRIEF §3 + WP-A `ni_importer.py` (verify NiSourceBase signature).

**Step 2** — Create `crop_knowledge_notes.py` (ORM). Smoke test: `from … import CropKnowledgeNote, NOTE_TYPE_VALUES, BODY_TEXT_MAX_LENGTH; assert len(NOTE_TYPE_VALUES) == 10; assert BODY_TEXT_MAX_LENGTH == 2000`.

**Step 3** — Create migration 045. Run `alembic upgrade 045` on a fresh SQLite DB and verify table + indices + CHECK constraints active. Run `downgrade 044` then `upgrade 045` again.

**Step 4** — Create the `ni/` subdirectory + `__init__.py` + 3 subclass files (§7). Each subclass currently raises `NotImplementedError` in `load()` — implementation in Step 6.

**Step 5** — Add `_upsert_knowledge_note` helper to `ni_importer.py` (APPEND ONLY — do NOT modify NiSourceBase). Verify `git diff ni_importer.py` shows ONLY the appended function.

**Step 6** — Implement `load()` for all 3 subclasses against fixture caches at `tests/crop_book/fixtures/ni/`. Builder generates the fixture files by hand (3 small JSON files per source).

**Step 7** — Create `scripts/extract_jmf_ni.py` (extraction runner). Implement the 3 `extract_*` dispatch functions. Test the `--dry-run` path with a stubbed Anthropic response. Do NOT make live API calls during the build — the runtime importer should work against existing fixture JSON.

**Step 8** — Wire `seed.py --ni-only` + `--no-ni` flags (§8). Write `test_seed_ni_cli.py`.

**Step 9** — Write remaining tests (§10). Achieve all 18 ACs.

**Step 10** — Run `pytest tests/crop_book/ -q` → all green (≥ 256 tests = 241 + 15 new patch01+B3 baseline). Run `validate_aos.sh` → 0 FAIL. Update `CHANGELOG.md`. Write BUILD_REPORT_v1.0.0.md per the canonical template (8 sections). **DO NOT commit any actual extracted PDF content to `data/jmf/extracted/`** — only commit the fixture JSON files in `tests/crop_book/fixtures/ni/` plus an EMPTY `data/jmf/extracted/<source>/` directory tree with a `.gitkeep` per directory + the `.gitattributes` entry. The real extraction (real Anthropic API calls against real PDFs) is a separate manual step team_00 will run post-merge.

**Note on Step 10's cache-commit-policy nuance:** the spec policy is "cache is committed", but the BUILDER doesn't run the real extraction (it requires ANTHROPIC_API_KEY + the actual PDFs which are on team_00's filesystem). The builder commits ONLY:
  (a) fixture JSONs (tests-scope)
  (b) `data/jmf/extracted/` directory structure with `.gitkeep` placeholders
  (c) `.gitattributes` entry
team_00 runs `scripts/extract_jmf_ni.py --all` post-merge to populate the real cache. This is documented in BUILD_REPORT §8 (open items).

---

## 12. PRE_HANDOFF advisory disposition

| # | Advisory | B2 disposition |
|---|---|---|
| 1 | **JMF PDF licensing — internal farm-use only** | **Addressed via schema + spec language.** §3 CHECK constraint enforces `body_text ≤ 2000 chars` (snippet length). §4 ORM declares `is_internal_farm_use_only=True` as default-not-null. §6 + §11 cache files carry `provenance.pdf` + `provenance.pages` for audit. AC-04a, AC-05 are the regression tests. Spec explicitly forbids publication: "Extracted narrative may be displayed to logged-in farm operators ONLY; never to public WordPress visitors. B2 does NOT push NI prose to WordPress." |
| 2 | **LLM extraction cache strategy** | **Resolved: cache is COMMITTED.** §5 + §6 + §11. Reasoning: (a) reproducibility — anyone running the project gets the same DB without LLM costs; (b) review — each extraction is a code-reviewable artifact; (c) cache invalidation explicit via `extract_jmf_ni.py --rebuild --crop <name>`. JSON files contain ONLY structured fields, never raw PDF text > 2000 chars per snippet. `.gitattributes` marks them `linguist-vendored` to suppress diff noise. *Alternatives considered:* gitignored (rejected — breaks reproducibility); redacted fixtures (rejected — B2 IS the canonical extraction). |
| 3 | Tend task whitelist | **N/A for B2** — Tend handling is WP-B3 (resolved by team_00 DECISION 2026-05-25 Option B). |
| 4 | Transitive WP-A dependency | **Addressed** explicitly. §2.2 lists WP-A `ni_importer.py` as LOD500_LOCKED; §7.5 declares the ONLY permitted modification (append `_upsert_knowledge_note` helper); §2.1 names the patch01 commit `3e1f946` for the `JMF_CROP_MAP` dependency; AC-18 enforces. |

---

## 13. Risk register

| ID | Risk | Likelihood | Severity | Mitigation |
|----|------|-----------|---------|-----------|
| R-01 | `pdftotext` not installed on builder's system | LOW | LOW | Extraction runner is NOT exercised by the build/test (per Step 10 nuance) — only by team_00 post-merge. Builder verifies presence via `which pdftotext` as documented step; missing → install or skip Step 7's live test. |
| R-02 | `crop_chapter` heuristic in `extract_jmf_book` misses a crop's chapter | MEDIUM | LOW | Builder writes the heuristic with a fallback regex; team_00 verifies per-crop coverage post-extraction; missed crops produce zero JSON files (graceful). Cache is per-crop, so a miss on one crop doesn't break others. |
| R-03 | Anthropic API model name changes (`claude-sonnet-4-6` deprecated) | LOW | LOW | `extraction_runner` accepts `--model` flag; team_00 can re-run with a current model post-deprecation; the cache JSON carries `provenance.extraction_model` for audit. |
| R-04 | LLM hallucinates content not in source PDF | MEDIUM | MEDIUM | Temperature `0.0` for determinism; prompt includes the verbatim chapter text and instructs to return null on uncertain extractions; team_00 reviews JSON files before approving for production. The 2000-char bound limits hallucination surface. |
| R-05 | `body_text` CHECK constraint syntax differs between Postgres and SQLite | LOW | LOW | `length(body_text) <= 2000` is portable. AC-04a tests on SQLite; production runs Postgres (same SQL). |
| R-06 | B3 migration 046 collides with B2 migration 045 if B3 runs first | LOW | LOW | The migration chain is linear (`044 → 045 → 046`). If B3 lands before B2, B3's `down_revision = "045"` will fail (no 045). Both WPs' specs explicitly say to verify the prior migration before running. Builder of whichever lands second STOPs and inquires if the prior is missing. |
| R-07 | NI hard-override semantics break PR/OP blending in `reconcile_field()` | LOW | LOW | WP-A engine already supports NI prefix-match (`get_source_spec("NI:any")` returns hard-override class). B2 just produces source labels matching that pattern. AC-12 verifies cultivar_recommendation engine reuse. |
| R-08 | Future ebook edition adds new chapters → cache stale | LOW | LOW | Cache invalidation explicit via `--rebuild`. New chapters require updating `JMF_CROP_MAP` (a B1-patch level concern). Out-of-scope for B2 itself. |

---

## 14. LOD500_LOCKED file inventory (must not be modified)

See §2.2 above. The ONLY permitted exception is `ni_importer.py` `_upsert_knowledge_note` helper append (§7.5). AC-18 enforces.

---

## 15. File-level deliverables summary

### CREATE

```
organic_market_agent/crop_book/crop_knowledge_notes.py
organic_market_agent/crop_book/importer/ni/__init__.py
organic_market_agent/crop_book/importer/ni/jmf_book.py
organic_market_agent/crop_book/importer/ni/jmf_ft_flameweed.py
organic_market_agent/crop_book/importer/ni/jmf_ft_biopesticide.py
organic_market_agent/db/versions/045_crop_knowledge_notes.py
scripts/extract_jmf_ni.py
data/jmf/extracted/jmf_book/.gitkeep
data/jmf/extracted/jmf_ft_flameweed/.gitkeep
data/jmf/extracted/jmf_ft_biopesticide/.gitkeep
.gitattributes                                  ← APPEND linguist-vendored rule (or CREATE if missing)
tests/crop_book/fixtures/ni/jmf_book/arugula.json
tests/crop_book/fixtures/ni/jmf_book/basil.json
tests/crop_book/fixtures/ni/jmf_ft_flameweed/_table.json
tests/crop_book/fixtures/ni/jmf_ft_biopesticide/_table.json
tests/crop_book/test_crop_knowledge_notes_orm.py
tests/crop_book/test_migration_045.py
tests/crop_book/test_ni_jmf_book.py
tests/crop_book/test_ni_jmf_ft_flameweed.py
tests/crop_book/test_ni_jmf_ft_biopesticide.py
tests/crop_book/test_ni_cache_schema.py
tests/crop_book/test_ni_idempotency.py
tests/crop_book/test_ni_licensing_flag.py
tests/crop_book/test_seed_ni_cli.py
_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md   (builder writes after L-GATE_B)
```

### MODIFY (existing files — additive scope only)

```
organic_market_agent/crop_book/importer/ni_importer.py    ← APPEND _upsert_knowledge_note() only
organic_market_agent/crop_book/importer/seed.py           ← +2 CLI flags + 1 call-site block
CHANGELOG.md                                                ← +[Unreleased] entry
```

### DO NOT TOUCH

See §2.2 LOD500_LOCKED inventory. Critical exclusions: `models.py`, `source_registry.py`, `field_policy.py`, `reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`, `tend.py`, `jmf.py`, `jmf_masterclass.py`, `crop_task_templates.py`, `constants.py`, all prior migrations.

---

*LOD400 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*Parallel-eligible with WP-B3 — no inter-dependency.*
*Pending: team_190 L-GATE_S validation (mandate next).*
