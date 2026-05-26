---
id: SFA-S003-P002-WP-C2-LOD400
wp: SFA-S003-P002-WP-C2
gate: L-GATE_S (LOD400 — build-precise spec, compact)
status: LOD400_LOCKED
author: team_10 (Claude Sonnet 4.7) under team_00 grant
date: 2026-05-26
version: v1.0.0
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-C2/LOD200_spec.md
pattern_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
---

# LOD400 — WP-C2: Hebrew Narrative NI Extraction

This LOD400 follows the WP-B2 extraction pattern exactly. Builder MUST read
WP-B2 LOD400 first as architectural reference.

## 1. Mission
(See LOD200 §1.) Bring 7 Hebrew/English authoritative sources into the existing
`crop_knowledge_notes` table via the same one-time-prepare → JSON cache → DB
upsert pipeline as WP-B2.

## 2. File-by-file delta

| Action | Path |
|--------|------|
| NEW | `organic_market_agent/db/versions/053_extend_ckn_note_type.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/aosnot_variety_info.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/sham_variety_trials.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/sham_hydro_guide.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/zacks_leafy_survey.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/jmf_ft_nurseryseeding.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/jmf_ft_seedingincellflats.py` |
| NEW (each) | `organic_market_agent/crop_book/importer/ni/jmf_cover_crops_narrative.py` |
| NEW | `scripts/extract_jmf_he.py` (multi-source dispatcher; calls Anthropic API once per crop chapter) |
| MODIFY | `organic_market_agent/crop_book/importer/seed.py` (add `--c2-only`, `--no-c2`) |
| NEW | `data/external_sources/extracted/` (cache root — gitignored binaries, committed JSONs) |
| NEW | `tests/crop_book/test_c2_*.py` (≥15 tests) |

## 3. Migration 053 DDL (renumbered from 049 — head is 052 after WP-C1+C4)

```python
"""049: extend crop_knowledge_notes.note_type CHECK (WP-C2)"""
from alembic import op
revision = "053"
down_revision = "052"

def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return  # SQLite re-creates table; skip live DB
    op.execute("""
        ALTER TABLE crop_knowledge_notes DROP CONSTRAINT IF EXISTS ck_ckn_note_type;
        ALTER TABLE crop_knowledge_notes ADD CONSTRAINT ck_ckn_note_type
          CHECK (note_type IN (
            'pest_disease','harvest_marker','storage_handling',
            'rotation_companion','cultivar_recommendation','growing_tip',
            'irrigation','nursery_specific','flame_weed_timing',
            'biopesticide_spray',
            'frost_tolerance','flowering_date','pollination_mechanism',
            'israeli_regions','variety_trial_score','hydro_suitability'
          ));
    """)

def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    op.execute("""
        ALTER TABLE crop_knowledge_notes DROP CONSTRAINT IF EXISTS ck_ckn_note_type;
        ALTER TABLE crop_knowledge_notes ADD CONSTRAINT ck_ckn_note_type
          CHECK (note_type IN (
            'pest_disease','harvest_marker','storage_handling',
            'rotation_companion','cultivar_recommendation','growing_tip',
            'irrigation','nursery_specific','flame_weed_timing','biopesticide_spray'
          ));
    """)
```

## 4. Importer pattern (one per source — all identical structure)

```python
"""ni/aosnot_variety_info.py — concrete NIImporter for L02 Hebrew encyclopedia"""
from pathlib import Path
import json
from organic_market_agent.crop_book.importer.ni_importer import NIImporter

class AosnotImporter(NIImporter):
    source_label = "NI:aosnot"
    cache_dir = Path("data/external_sources/extracted/aosnot")

    def load(self) -> list[dict]:
        """Read cached JSON per crop; return list of note dicts ready for upsert."""
        notes = []
        for fp in sorted(self.cache_dir.glob("*.json")):
            data = json.loads(fp.read_text(encoding="utf-8"))
            for n in data["notes"]:
                notes.append({
                    "crop_he": data["crop_he"],
                    "source": "NI:aosnot",
                    "trust_tier": "NI",
                    "note_type": n["note_type"],
                    "body_text": n["body"][:2000],  # bounded per WP-B2 §5.4
                    "provenance_pdf": "L02_AOSNOT_variety_info.docx",
                    "extraction_model": data.get("extraction_model", "claude-sonnet-4.7"),
                })
        return notes

    def validate(self, rows: list[dict]) -> tuple[int, list[str]]:
        """Return (valid_count, warnings)."""
        valid = sum(1 for r in rows if r["body_text"])
        warnings = [f"empty body: {r['crop_he']}/{r['note_type']}" for r in rows if not r["body_text"]]
        return valid, warnings
```

(Repeat pattern for each of 7 sources, varying `source_label`, `cache_dir`, and
`provenance_pdf`.)

## 5. Extraction harness `scripts/extract_jmf_he.py`

```python
"""One-time prepare: pdftotext → Anthropic API → JSON cache per crop.

Usage:
    python3 scripts/extract_jmf_he.py --source aosnot
    python3 scripts/extract_jmf_he.py --source all

Output: data/external_sources/extracted/<source>/<crop_he>.json
"""
```

**Per source, the harness:**
1. Reads pre-extracted text from `data/external_sources/raw_text/`
2. Chunks by per-crop section (heuristic: H1/H2 headers, or LLM section detector)
3. For each chunk, calls Anthropic API with a structured-extraction prompt
   (NOTE: this is a one-time prepare cost — NOT runtime; counts against
   user's Anthropic credits, NOT team_80's MCP)
4. Caches JSON output
5. Logs cost + token use to `data/external_sources/extracted/_extraction_log.json`

## 6. AC matrix (12 ACs)

| AC | Description |
|----|-------------|
| AC-C2-01 | Migration 049 applies cleanly on PG (SQLite-safe skip) |
| AC-C2-02 | L02 AOSNOT extraction produces ≥20 crop JSONs in `data/external_sources/extracted/aosnot/` |
| AC-C2-03 | L02 per-crop fields populated: frost_tolerance, israeli_regions, flowering_date present in ≥80% of cached JSONs |
| AC-C2-04 | L11 variety_trial_score rows: ≥5 lettuce varieties scored |
| AC-C2-05 | L09 hydro_suitability rows: ≥10 crops classified |
| AC-C2-06 | L10 Zacks survey: production benchmarks extracted where applicable (or documented as "no useful data" with reason) |
| AC-C2-07 | L14 + L16 + L13 JMF FT extractions populate `nursery_specific`, `growing_tip` per crop |
| AC-C2-08 | All extractions cached; runtime importer reads cache only (no API call at import) |
| AC-C2-09 | Hebrew text preserved: no `\uXXXX` escapes in JSON cache files (UTF-8 raw) |
| AC-C2-10 | NI hard-override semantics preserved: reconcile_field rejects blending NI rows |
| AC-C2-11 | Tests ≥15 (importer unit + cache schema + DB integration + Hebrew encoding) |
| AC-C2-12 | validate_aos.sh: 29/19/0 |

## 7. Verification commands

```bash
# Extraction (one-time)
python3 scripts/extract_jmf_he.py --source all

# Migration
alembic upgrade head

# Tests
python3 -m pytest tests/crop_book/test_c2_*.py

# Live ingestion
python3 -m organic_market_agent.crop_book.importer.seed --c2-only

# AOS validate
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# Hebrew encoding sanity
python3 -c "
from pathlib import Path
import json
for fp in Path('data/external_sources/extracted/aosnot').glob('*.json'):
    raw = fp.read_text(encoding='utf-8')
    assert '\\\\u05' not in raw, f'Escape detected in {fp.name}'
print('OK — Hebrew raw UTF-8 preserved')
"
```

## 8. Build sequence
1. Migration 049 + apply
2. Build extraction harness `scripts/extract_jmf_he.py`
3. Run extraction for L02 (highest-value); validate output
4. Build `ni/aosnot_variety_info.py` + tests
5. Run extraction + importers for L11, L09, L10 in sequence
6. Build JMF FT importers (L14, L16, L13)
7. Wire into `seed.py`; full focused test pass
8. Live ingestion; verify; BUILD_REPORT

## 9. Risk register

| Risk | Mitigation |
|------|------------|
| LLM hallucination on Hebrew encyclopedia | Cache + manual review pass before importer activation (per WP-B2 cache-review pattern) |
| Anthropic API cost overrun | Cap: $20 budget for full C2 extraction. Log token use. STOP if exceeded. |
| L10 Zacks survey low-yield | Acceptable per AC-C2-06 (document as "low-yield source"). |

---
*LOD400 authored by team_10 2026-05-26 under team_00 grant. Compact (~250 lines)
because pattern mirrors WP-B2 exactly. Detailed review at activation time.*
