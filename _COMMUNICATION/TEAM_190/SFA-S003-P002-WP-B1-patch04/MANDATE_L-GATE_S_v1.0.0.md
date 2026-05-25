---
id: MANDATE_SFA-S003-P002-WP-B1-patch04_L-GATE_S_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch04
round: R1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04/LOD400_spec.md
spec_version: v1.0.0
engine_constraint: "Iron Rule #1 — non-Claude. GPT-5.5."
status: ACTIVE
verdict: PENDING
parallel_to: SFA-S003-P002-WP-B1-patch06 L-GATE_S R1
---

# L-GATE_S R1 — patch04 (Integration)

## 1. Scope
LARGE integration WP. New script (load_masterclass_sheets.py), new script (patch03_data_fix.py), new Migration 047 + junction model, +1 baseline (Ginger), CHANGELOG, ~10 new tests. ~600 LOC delta.

Authored in parallel with patch06 (cleanup). BUILD sequencing: patch04 → patch06 strictly (per DECISION §4).

## 2. Validation Criteria (16 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | IR#1 three-engine | LOD400 frontmatter: builder=team_10 Sonnet, validator=team_190 GPT-5.5, orchestrator=team_110 Opus 4.7 |
| VC-2 | DECISION exists + authorizes scope | `_COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md` exists; §2 lists OP-01..OP-04 + §2.5 Ginger |
| VC-3 | Single MAP addition (Ginger only) | LOD400 §3.1 shows exactly ONE new entry `"Ginger": "ג'ינג'ר"`. NO removals from MAP (deferred to patch06). |
| VC-4 | Migration 047 design correct | LOD400 §3.3 creates `crop_knowledge_notes_crops` table with FK to both parent tables + index + ON DELETE CASCADE. Backfill query handles existing rows. Downgrade reverses cleanly. |
| VC-5 | Junction ORM model correct | LOD400 §3.4 uses `Table()` pattern (not declarative class — appropriate for pure junction); secondary relationship added to `crop_knowledge_notes` model. |
| VC-6 | Loader script outline complete | LOD400 §3.5 has parse_md_sheet + md_to_cache_json + cli_main; body_text ≤ 2000 chars constraint explicit (R-02 captured); JSON schema matches WP-B2 cache. |
| VC-7 | Data-fix script safe | LOD400 §3.6: dry-run default; --apply required; idempotent (running twice yields 0 changes); logs every row. |
| VC-8 | Fair-use posture preserved | AC-14 requires `is_internal_farm_use_only=true` on all records (per DECISION §6). |
| VC-9 | LOCKED test discipline | LOD400 §3.2 adds 1 NEW regression test only (Ginger). 24-group allowlist UNCHANGED (AC-22 verifies). NO LOCKED test modified in patch04. |
| VC-10 | AC measurability | All 22 ACs are objective (size assertions, command exit codes, schema introspection, count checks). |
| VC-11 | AC-18 expected count | AC-18 says 355 passed (354 post-patch03 + 1 new Ginger). |
| VC-12 | AC-22 verifies non-touch of 24-group dict | Explicit AC that patch04 does NOT change the 24-group dict (cleanup is patch06's job). |
| VC-13 | File scope discipline (§2.1+§2.2) | 5 created + 5 modified files — total 10. NO other LOCKED file touched. |
| VC-14 | Sequencing constraint stated | LOD200 §11 + DECISION §4 explicitly say patch06 BUILD depends on patch04 LOD500_LOCKED. |
| VC-15 | Risk register completeness | R-01..R-05 cover: MD parser robustness, body_text truncation, migration backfill safety, lazy crops row creation, NotebookLM filename mangling. |
| VC-16 | validate_aos.sh + roadmap | `validate_aos.sh` returns 0 FAIL. roadmap.yaml parses; patch04 + patch06 entries present at `LOD200_LOCKED / L-GATE_E PASS`. |

## 3. Required commands
```bash
# 1. Frontmatter + version
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04/LOD400_spec.md
# Expected: version: v1.0.0

# 2. DECISION exists + cites patch04 scope
test -f _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md && echo PRESENT
grep -E "Ginger|ג'ינג'ר|Migration 047|crop_knowledge_notes_crops" \
  _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md | head -10

# 3. Current state (pre-build verification)
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
print(f'len: {len(JMF_CROP_MAP)} (expect 86)')
print(f'Ginger present? {\"Ginger\" in JMF_CROP_MAP} (expect False — built by patch04)')
"

# 4. Migration baseline
alembic current
# Expected: 046 (head pre-patch04)

# 5. NotebookLM source data
ls documentation/jmf_masterclass_crop_sheets/*.md | wc -l
# Expected: 39 (37 substantive + README + _index.json)

# 6. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 4. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch04/LOD400-VERDICT_v1.0.0.md`

Commit: `gate(WP-B1-patch04/L-GATE_S): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF (0 blockers) → team_110 dispatches Sonnet build for patch04.
FAIL → R2.

---
