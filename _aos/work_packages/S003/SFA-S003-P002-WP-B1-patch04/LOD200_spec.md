---
id: SFA-S003-P002-WP-B1-patch04-LOD200
wp: SFA-S003-P002-WP-B1-patch04 — JMF MasterClass Integration (NotebookLM → DB)
gate: L-GATE_S (LOD200)
status: PRE_LOD400
author: team_110
date: 2026-05-25
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-B2 (LOD500_LOCKED — NIImporter framework)
  - SFA-S003-P002-WP-B1-patch03 (LOD500_LOCKED — last taxonomy)
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md
depends_on: [SFA-S003-P002-WP-B1-patch03]
blocks: [SFA-S003-P002-WP-B1-patch06]
validator: team_190 (GPT-5.5)
builder: team_10 (Sonnet sub-agent)
---

# LOD200 — patch04: JMF MasterClass Integration

## 1. Mission

Operationalize the 37 NotebookLM-extracted MasterClass crop sheets into the live `crop_knowledge_notes` + `crop_varieties` tables. Add Ginger as a new baseline. Introduce many-to-many notes↔crops via Migration 047. Automate patch03 data-fix.

## 2. In-scope

### 2.1 New code
- `scripts/load_masterclass_sheets.py` — MD → JSON cache → DB loader
- `scripts/patch03_data_fix.py` — idempotent UPDATEs for the 11 patch03 keys
- Alembic migration **047_create_crop_knowledge_notes_crops_junction** — junction table + FKs
- `organic_market_agent/db/models/crop_knowledge_notes_crops.py` — new ORM model
- Update `crop_knowledge_notes` model to add `crops: relationship(secondary='crop_knowledge_notes_crops')`

### 2.2 Data deliverables
- ~37 JSON files at `data/jmf/extracted/jmf_book/<crop>.json` (per WP-B2 cache schema)
- ~200-400 `crop_knowledge_notes` rows
- ~150-200 `crop_varieties` rows from MasterClass CULTIVARS sections
- ~1 junction-loaded sheet (056 storage/washing) linked to all relevant crops

### 2.3 Single JMF_CROP_MAP addition
- `"Ginger": "ג'ינג'ר"` (per DECISION §2.5)
- +1 regression test asserting the new value
- +1 lazy crops row will be created at next `seed.py --ni-only` run

### 2.4 CHANGELOG.md `[Unreleased]` entry

## 3. Out-of-scope (deferred to patch06)
- Removal of 22 cultivar entries from JMF_CROP_MAP
- Removal of 5 typo entries
- LOCKED test updates for the 24-group → 3-group transition
- Revert of patch03 `Greenhouse Libanese Cucumber → מלפפון חממה`

## 4. Data sources
- 37 MDs at `documentation/jmf_masterclass_crop_sheets/*.md` (already committed)
- `_index.json` (Hebrew↔English mapping)

## 5. Trust-layer placement
JMF tier (PR). NIImporter framework from WP-B2. New notes inherit fair-use posture (§3.1 invariant): `is_internal_farm_use_only=true`, `body_text` ≤ 2000 chars per row.

## 6. Schema change (Migration 047)

```python
# 047_create_crop_knowledge_notes_crops_junction.py
op.create_table(
    'crop_knowledge_notes_crops',
    sa.Column('note_id', sa.Integer, sa.ForeignKey('crop_knowledge_notes.id', ondelete='CASCADE'), primary_key=True),
    sa.Column('crop_id', sa.Integer, sa.ForeignKey('crops.id', ondelete='CASCADE'), primary_key=True),
)
op.create_index('ix_ckn_crops_crop_id', 'crop_knowledge_notes_crops', ['crop_id'])
```

Backfill: for every existing `crop_knowledge_notes` row, insert `(note.id, note.crop_id)` into junction (preserves the current 1-to-many semantics during transition).

## 7. Dependencies
- patch03 LOD500_LOCKED (`bbed...` commit, post-COMPLETION_REPORT)
- WP-B2 NIImporter framework (`_upsert_knowledge_note` helper)

## 8. LOD500_LOCKED scope exceptions
- `tests/crop_book/test_jmf_crop_map.py` — APPEND 1 new test (`test_ginger_baseline_post_patch04`)
- All other LOCKED tests UNCHANGED (24-group allowlist preserved — patch06 handles that)

## 9. AC + test count targets
- ACs: ~22 (1 per Ginger + ~5 per script + 4 per migration + 6 per data integrity + 6 hygiene)
- New tests: ~10 (Ginger, script parsing, migration up/down, junction model, data-fix script unit tests)

## 10. Builder
team_10 (Sonnet sub-agent). NOT single-engine — LARGE scope + new schema + ~400 DB rows.

## 11. Sequencing
patch04 BUILD must complete before patch06 BUILD (per DECISION §4). LOD200 + LOD400 + L-GATE_S can run in parallel with patch06's equivalents.

---

*LOD200 v1.0.0 — 2026-05-25, team_110.*
