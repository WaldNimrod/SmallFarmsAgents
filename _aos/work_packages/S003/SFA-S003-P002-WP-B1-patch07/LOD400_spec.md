---
id: SFA-S003-P002-WP-B1-patch07-LOD400
wp: SFA-S003-P002-WP-B1-patch07 — sheet 056 storage/washing M2M data load + Migration 048
gate: L-GATE_S (LOD400; LOD200 inlined)
status: PRE_LOD400_LOCK
author: team_110
date: 2026-05-26
version: v1.0.0
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch07-patch08_2026-05-26_v1.0.0.md
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190 — three distinct engines"
---

# LOD400 — patch07 (sheet 056 M2M load)

## 1. Goal
Load sheet 056 ("WASHING ITINERARY FOR CROPS IN THE MASTERCLASS") to `crop_knowledge_notes` via M2M junction. Requires Migration 048 to make `crop_id` nullable.

## 2. Architecture

### 2.1 Files CREATED (3)
```
organic_market_agent/db/versions/048_make_crop_knowledge_notes_crop_id_nullable.py  (~30 LOC)
scripts/load_sheet_056_storage.py                                                    (~150 LOC)
tests/integration/test_load_sheet_056.py                                             (~80 LOC)
```

### 2.2 Files MODIFIED (1)
```
CHANGELOG.md    ← [Unreleased] entry
```

### 2.3 Out-of-scope
- Re-architecting `crop_knowledge_notes` model
- Touching `load_masterclass_sheets.py` (patch08 is the sibling)
- Backfilling existing notes with junction rows (not required — they remain 1-to-1)

## 3. Implementation

### 3.1 Migration 048

```python
"""make crop_knowledge_notes.crop_id nullable for M2M-only notes

Revision ID: 048
Revises: 047
"""
from alembic import op
import sqlalchemy as sa

revision = '048'
down_revision = '047'

def upgrade():
    op.alter_column('crop_knowledge_notes', 'crop_id', nullable=True)

def downgrade():
    # Safe downgrade: only if all rows have non-null crop_id
    op.execute(
        "UPDATE crop_knowledge_notes SET crop_id = "
        "(SELECT crop_id FROM crop_knowledge_notes_crops WHERE note_id = crop_knowledge_notes.id LIMIT 1) "
        "WHERE crop_id IS NULL"
    )
    op.alter_column('crop_knowledge_notes', 'crop_id', nullable=False)
```

### 3.2 Sheet 056 parser

Source MD: `documentation/jmf_masterclass_crop_sheets/056-eouio-oyono.md`

Structure observed: section blocks each containing:
- 1+ crop names (lines starting with `→ `)
- Procedure text (multi-line, multiple `→` bullets)
- Storage params: drying time, temperature °C/°F, storage length

Parser extracts each block; for each block:
1. Resolve crop names to crop_ids via JMF_CROP_MAP / TEND_CROP_MAP / direct match
2. INSERT crop_knowledge_notes with crop_id=NULL, note_type='storage_handling', body_text=composed-procedure-text (≤2000 chars), is_internal_farm_use_only=TRUE
3. For each resolved crop_id: INSERT crop_knowledge_notes_crops(note_id, crop_id)

If a crop name is not resolvable → log WARN + skip that crop (but the note is still inserted with the resolved crops).

### 3.3 Script CLI

```bash
python scripts/load_sheet_056_storage.py --dry-run    # parse + report planned actions
python scripts/load_sheet_056_storage.py --apply --db-url ...  # mutate DB
```

Idempotent: ON CONFLICT (using a synthetic unique constraint on `(source, note_type, hash(body_text))` OR a "load_marker" pattern). For simplicity: check `WHERE source = 'NI:jmf_sheet_056' AND body_text = ?` before insert.

### 3.4 CHANGELOG entry

```markdown
### SFA-S003-P002-WP-B1-patch07 — Sheet 056 M2M data load + Migration 048 (2026-05-26)
- **Migration 048:** `crop_knowledge_notes.crop_id` now nullable (was NOT NULL). Enables M2M-only notes (storage/washing procedures applying to multiple crops via junction table from Migration 047).
- **`scripts/load_sheet_056_storage.py`:** new parser for sheet 056 ("WASHING ITINERARY FOR CROPS IN THE MASTERCLASS"). Inserts ~6-10 procedure notes (crop_id=NULL) + populates `crop_knowledge_notes_crops` junction with ~30-50 (note, crop) pairs.
- Per team_00 DECISION_WP-B1-patch07-patch08_2026-05-26 §1.
```

## 4. Acceptance Criteria (12 ACs)

- **AC-01** `alembic upgrade head` succeeds; `alembic current` shows `048`
- **AC-02** `crop_knowledge_notes.crop_id` is nullable (verified via `\d` or information_schema)
- **AC-03** `alembic downgrade 047` succeeds (with backfill from junction)
- **AC-04** `python scripts/load_sheet_056_storage.py --dry-run` exits 0 + reports planned actions
- **AC-05** `--apply` against test SQLite fixture: inserts ≥ 6 notes with `source='NI:jmf_sheet_056'` and `crop_id IS NULL`
- **AC-06** Same script also inserts ≥ 30 junction rows linking the notes to crops
- **AC-07** Idempotency: 2 consecutive `--apply` runs yield identical row counts (no duplicates)
- **AC-08** Every inserted note has `is_internal_farm_use_only=TRUE`
- **AC-09** Every inserted note has `body_text` ≤ 2000 chars
- **AC-10** Existing `crop_knowledge_notes` rows from patch04 (with `crop_id IS NOT NULL`) are UNCHANGED
- **AC-11** `pytest tests/integration/ -q` → N+5+ passing (was 15; +new test_load_sheet_056 tests). Exact N to be determined at build.
- **AC-12** `pytest tests/crop_book/ -q` → 350 + 1 OOS unchanged. `validate_aos.sh` 0 FAIL. Diff scope: 4 files (migration + script + test + CHANGELOG).

## 5. Build sequence
1. Read spec + DECISION + sheet 056 MD
2. Author Migration 048 + test upgrade/downgrade against SQLite fixture
3. Author parser + tests
4. Append CHANGELOG
5. Full test suite + validate_aos.sh
6. Single atomic commit
7. BUILD_REPORT

## 6. Risk register

| ID | Risk | Mitigation |
|----|------|-----------|
| R-01 | Sheet 056 structure unpredictable | Author parser defensively; skip-with-WARN on unparseable blocks; log everything in dry-run |
| R-02 | Some crop names in sheet 056 don't resolve (e.g., "Baby Asian Greens" not in JMF_CROP_MAP) | Log WARN + skip that crop reference for the note, but still insert the note with resolved crops. AC-06 ≥30 not all-or-nothing. |
| R-03 | Migration 048 downgrade fails if junction has multiple crops per note | Downgrade backfill picks FIRST junction row; documented limitation. Production environments shouldn't routinely downgrade. |
| R-04 | Idempotency check via `source+body_text` is fragile | If 2 different blocks produce identical body_text, treated as duplicate. Acceptable for v1; future improvement via content hash. |

## 7. LOCKED scope
4 files (3 NEW + 1 MODIFIED). All other LOCKED files untouched.

## 8. Builder
team_10 Sonnet sub-agent (MEDIUM scope: schema + parser + tests).

---

*LOD400 v1.0.0 — 2026-05-26. Pending team_190 L-GATE_S.*
