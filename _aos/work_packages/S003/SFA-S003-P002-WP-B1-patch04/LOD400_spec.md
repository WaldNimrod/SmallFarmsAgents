---
id: SFA-S003-P002-WP-B1-patch04-LOD400
wp: SFA-S003-P002-WP-B1-patch04 — JMF MasterClass Integration
gate: L-GATE_S
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-25
version: v1.0.1
lod200_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04/LOD200_spec.md
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator) ≠ team_10 Sonnet (builder) ≠ team_190 GPT-5.5 (validator) — three distinct engines"
---

# LOD400 — patch04 Integration

## 1. Goal

Operational integration of NotebookLM MasterClass deliverable + 1 new baseline (Ginger) + many-to-many schema for cross-crop notes + automated patch03 data-fix.

## 2. Architecture

### 2.1 Files CREATED (5)
```
scripts/load_masterclass_sheets.py                                    (~250 LOC)
scripts/patch03_data_fix.py                                            (~80 LOC)
organic_market_agent/db/migrations/versions/047_*.py                  (~60 LOC — Migration 047)
organic_market_agent/db/models/crop_knowledge_notes_crops.py          (~30 LOC — junction ORM)
tests/integration/test_load_masterclass_sheets.py                     (~120 LOC)
```

### 2.2 Files MODIFIED (5)
```
organic_market_agent/crop_book/constants.py            ← +1 Ginger entry
tests/crop_book/test_jmf_crop_map.py                   ← +1 regression test (Ginger)
organic_market_agent/db/models/crop_knowledge_notes.py ← + relationship(secondary='crop_knowledge_notes_crops')
organic_market_agent/db/models/__init__.py             ← + export of junction model
CHANGELOG.md                                            ← [Unreleased] entry
```

### 2.3 Data files PRODUCED at runtime (not committed pre-build; out of LOC budget)
```
data/jmf/extracted/jmf_book/<crop>.json   × ~37 files
```

## 3. Implementation — exact code paths

### 3.1 `constants.py` — Ginger addition

Locate the Herbs section in `JMF_CROP_MAP` (just before the `"Parsley":...` line). Add (preserving the patch01 alias section structure):

```python
    # ─── BEGIN patch04 single-baseline addition (2026-05-25) ───
    "Ginger":             "ג'ינג'ר",   # team_00 DECISION_WP-B1-patch04-patch06 §2.5: Baby Ginger from MasterClass sheet 050. Cultivars (Baby variant) → crop_varieties.
```

### 3.2 `test_jmf_crop_map.py` — APPEND 1 regression test

```python
def test_ginger_baseline_post_patch04():
    """patch04 (DECISION §2.5): Ginger Hebrew is 'ג'ינג'ר'."""
    from organic_market_agent.crop_book.constants import JMF_CROP_MAP
    assert JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"
    assert "ג'ינג'ר" in JMF_CROP_MAP.values()
```

LOCKED tests (duplicate_target_allowlist + ac03_duplicate_group_count) UNCHANGED — Ginger creates a new unique value, doesn't change 24-group dict.

### 3.3 Migration 047 — junction table

```python
"""create_crop_knowledge_notes_crops_junction

Revision ID: 047
Revises: 046
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa

revision = '047'
down_revision = '046'

def upgrade():
    op.create_table(
        'crop_knowledge_notes_crops',
        sa.Column('note_id', sa.Integer, sa.ForeignKey('crop_knowledge_notes.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('crop_id', sa.Integer, sa.ForeignKey('crops.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_index('ix_ckn_crops_crop_id', 'crop_knowledge_notes_crops', ['crop_id'])
    # Backfill: for every existing crop_knowledge_notes row, link to its crop_id
    op.execute("""
        INSERT INTO crop_knowledge_notes_crops (note_id, crop_id)
        SELECT id, crop_id FROM crop_knowledge_notes WHERE crop_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)

def downgrade():
    op.drop_index('ix_ckn_crops_crop_id', 'crop_knowledge_notes_crops')
    op.drop_table('crop_knowledge_notes_crops')
```

### 3.4 Junction ORM model (`crop_knowledge_notes_crops.py`)

```python
from sqlalchemy import Column, ForeignKey, Integer, Table
from organic_market_agent.db.base import Base

crop_knowledge_notes_crops = Table(
    'crop_knowledge_notes_crops',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('crop_knowledge_notes.id', ondelete='CASCADE'), primary_key=True),
    Column('crop_id', Integer, ForeignKey('crops.id', ondelete='CASCADE'), primary_key=True),
)
```

Add to `crop_knowledge_notes.py` model:
```python
crops_linked = relationship('Crop', secondary='crop_knowledge_notes_crops', back_populates='knowledge_notes_linked')
```

### 3.5 `scripts/load_masterclass_sheets.py` — MD → JSON → DB

Pseudo-structure:
```python
def parse_md_sheet(md_path) -> dict:
    """Extract sections: CULTIVARS, INTENSIVE SPACING, PESTS, DISEASES, HARVEST, ..."""
    # Returns: {'cultivars': [...], 'pests': '<text>', 'diseases': '<text>', ...}

def md_to_cache_json(parsed: dict, source: str, crop_jmf_en: str, crop_name_he: str) -> dict:
    """WP-B2 cache schema:
    {
      'schema_version': '1.0',
      'source': source,
      'crop_jmf_en': crop_jmf_en,
      'crop_name_he': crop_name_he,
      'is_internal_farm_use_only': True,
      'provenance': {...},
      'notes': {
        'pest_pressure': [{'body_text': ..., 'page_ref': null, 'confidence': 'high'}],
        ...
      }
    }
    """
    # body_text strictly ≤ 2000 chars (truncate/summarize if longer)

def cli_main():
    """For each MD in documentation/jmf_masterclass_crop_sheets/:
       1. Map filename → JMF_CROP_MAP key via _index.json
       2. Parse + convert
       3. Write to data/jmf/extracted/jmf_book/<crop>.json
       4. If --load-db: call _upsert_knowledge_note + crop_varieties insert via session
    """
```

### 3.6 `scripts/patch03_data_fix.py` — automated DB UPDATE

```python
"""Idempotent UPDATEs for patch03's 11 Hebrew terminology corrections.

Per DECISION_WP-B1-patch04-patch06 §2.2.
"""
PATCH03_UPDATES = [
    # (old_name_he, new_name_he)
    ('גזר לבן',     'שורש פטרוזילה'),  # Parsnips
    ('שאלוט',       'בצלצלי שאלוט'),    # Shallots
    ('תערובת סלט',  'עלי בייבי'),       # Mesclun + Salad Mix collapse
    ('קייל',        'עלי בייבי'),        # Baby kale ONLY (NOT all Kale!) — handled by crops.id filter
    # ... etc per patch03 §1.1-1.4
]

def main(dry_run: bool):
    for old, new in PATCH03_UPDATES:
        # SELECT count(*) FROM crops WHERE name_he = :old
        # If dry_run: print count
        # Else: UPDATE crops SET name_he = :new WHERE name_he = :old
        # Print: "{old} → {new}: {n} rows {'updated' if not dry_run else 'would be updated'}"
```

**Safety:** dry-run by default. Requires `--apply` flag to mutate. Logs every row touched.

### 3.7 CHANGELOG.md

```markdown
### SFA-S003-P002-WP-B1-patch04 — JMF MasterClass Integration (2026-05-25)
- **NEW baseline:** `Ginger → ג'ינג'ר` (37th of NotebookLM crop sheets — "Baby Ginger")
- **NEW infrastructure:** Migration 047 creates `crop_knowledge_notes_crops` junction (many-to-many)
- **NEW data:** ~200-400 `crop_knowledge_notes` rows + ~150-200 `crop_varieties` rows populated from 37 NotebookLM MasterClass MDs
- **NEW scripts:** `scripts/load_masterclass_sheets.py` (MD → JSON cache → DB) + `scripts/patch03_data_fix.py` (automated production data-fix for patch03)
- Per team_00 DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25 §§2-3
```

## 4. Acceptance Criteria (22 ACs)

### 4.1 Ginger baseline (AC-01..AC-03)
- **AC-01** `JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"`
- **AC-02** `"ג'ינג'ר" in JMF_CROP_MAP.values()`
- **AC-03** `len(JMF_CROP_MAP) == 87` (was 86; +1)

### 4.2 Migration 047 (AC-04..AC-07)
- **AC-04** `alembic upgrade head` returns success; `alembic current` shows `047`
- **AC-05** Table `crop_knowledge_notes_crops` exists with columns `(note_id, crop_id)` both NOT NULL PK
- **AC-06** Index `ix_ckn_crops_crop_id` exists
- **AC-07** `alembic downgrade 046` cleanly removes both index + table (reversibility)

### 4.3 Junction ORM (AC-08..AC-09)
- **AC-08** ORM relationship `crop_knowledge_notes.crops_linked` returns list of `Crop` instances
- **AC-09** Cascading delete: deleting a `Crop` row cascades to junction rows (verified via test)

### 4.4 Loader script (AC-10..AC-14)
- **AC-10** `python scripts/load_masterclass_sheets.py --dry-run` parses all 37 MDs without error, prints planned actions
- **AC-11** `python scripts/load_masterclass_sheets.py --load-db` (against test SQLite) produces 37 JSON files at `data/jmf/extracted/jmf_book/`
- **AC-12** Each JSON conforms to WP-B2 schema (`schema_version: '1.0'`, all required fields present)
- **AC-13** Every `body_text` ≤ 2000 chars (fair-use posture)
- **AC-14** `is_internal_farm_use_only` = `true` on every record

### 4.5 Data-fix script (AC-15..AC-17)
- **AC-15** `python scripts/patch03_data_fix.py --dry-run` reports per-row impact without mutation
- **AC-16** `python scripts/patch03_data_fix.py --apply` is idempotent (running twice yields 0 row changes on the second run)
- **AC-17** Script handles missing-row-set gracefully (e.g., if `name_he='גזר לבן'` doesn't exist in DB, reports "0 rows", no error)

### 4.6 Hygiene (AC-18..AC-22)
- **AC-18** `pytest tests/crop_book/ -q` returns **355 passed** (354 baseline + 1 new Ginger test) + 1 pre-existing publisher failure (OOS)
- **AC-19** `pytest tests/integration/ -q` returns passing (the new test_load_masterclass_sheets.py tests pass on SQLite fixture)
- **AC-20** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL
- **AC-21** `git diff <patch03-lock>..HEAD` shows changes ONLY in §2.1 + §2.2 file lists (no other LOCKED files modified)
- **AC-22** 24-group duplicate-target allowlist UNCHANGED (`test_jmf_crop_map_duplicate_target_allowlist` still PASSES with the SAME 24-group dict — patch06 handles cleanup)

## 5. Test requirements

10 new tests minimum:
1. `test_ginger_baseline_post_patch04` (constants.py regression)
2. `test_migration_047_upgrade_creates_table` (integration)
3. `test_migration_047_downgrade_reverses` (integration)
4. `test_junction_orm_relationship_returns_crops` (integration)
5. `test_junction_cascade_delete_on_crop` (integration)
6. `test_load_masterclass_dryrun_parses_all_37` (integration)
7. `test_load_masterclass_produces_valid_json_schema` (unit)
8. `test_load_masterclass_body_text_truncation` (unit, 2000-char limit)
9. `test_patch03_data_fix_dryrun_reports_correctly` (unit)
10. `test_patch03_data_fix_idempotent` (integration)

## 6. Build sequence

1. Read LOD400 + LOD200 + DECISION + verify current state (`alembic current` should show `046`; `JMF_CROP_MAP` size 86)
2. Apply §3.1 Ginger edit in `constants.py`
3. Append §3.2 regression test
4. Author Migration 047 (§3.3) + junction model (§3.4) + update `crop_knowledge_notes` model + `__init__.py`
5. Run `alembic upgrade head` against SQLite test fixture; confirm 047 applied
6. Author `scripts/load_masterclass_sheets.py` (§3.5) + integration tests
7. Author `scripts/patch03_data_fix.py` (§3.6) + unit tests
8. Append CHANGELOG (§3.7)
9. Run `pytest tests/crop_book/ tests/integration/ -q` — must show 355 + N new passing
10. Run `python scripts/load_masterclass_sheets.py --dry-run` — must parse all 37 MDs
11. Run `python scripts/patch03_data_fix.py --dry-run` against test DB — must report planned changes
12. Run `validate_aos.sh` — 0 FAIL
13. Commit as single atomic commit:
```
build(WP-B1-patch04): MasterClass integration + Migration 047 + Ginger baseline

[summary]

Co-Authored-By: Claude Sonnet <noreply@anthropic.com>
```

**Builder safety:**
- DO NOT actually `--apply` the data-fix script during build (production DB mutation — out of build scope).
- DO NOT actually upgrade live Postgres in CI; SQLite fixture only for migration tests.
- The 37 JSON files at `data/jmf/extracted/jmf_book/` may be committed if user wants persistent cache (default: yes, commit them — they're small text files).

## 7. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | MD parser handles 37 diverse formats unevenly | Per-MD test fixture; parser tolerant of missing sections |
| R-02 | `body_text` > 2000 chars on long sheets (e.g., 22-page Tomatoes) | Truncate with `…` + log warning; AC-13 enforces |
| R-03 | Migration 047 backfill assumes existing `crop_knowledge_notes.crop_id` not null | Current state: 0 rows in table (verified §pre-flight); backfill is no-op |
| R-04 | Ginger's `crops` row doesn't exist; importer fails on `--ni-only` | Lazy creation via `_upsert_knowledge_note` (B2 pattern) handles this |
| R-05 | NotebookLM filename Hebrew-mangling breaks `_index.json` lookup | Pre-resolved during NotebookLM intake (commit `7e1...`); index is committed |

## 8. LOD500_LOCKED inventory

Same as post-patch03 + cumulative. Permitted modifications:
- `constants.py` — +1 line (Ginger)
- `test_jmf_crop_map.py` — +1 test function (Ginger regression)
- `crop_knowledge_notes.py` model — +1 `relationship` line
- `db/models/__init__.py` — +1 export

All other LOCKED files untouched.

## 9. Out-of-scope (deferred to patch06)
Per DECISION §3 — cleanup of 27 entries from JMF_CROP_MAP + LOCKED test updates.

## 10. Builder identity
team_10 (Sonnet sub-agent). NOT single-engine. IR#1 standard pattern.

---

*LOD400 v1.0.0 — 2026-05-25 by team_110.*
*v1.0.1 (2026-05-25) — R2 correction per team_190 L-GATE_S R1 VC-1 BLOCKER: frontmatter now explicitly records the full three-engine chain (orchestrator + builder + validator + engine_chain summary). No other change.*
*Pending: team_190 L-GATE_S R2.*
