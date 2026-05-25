---
id: MANDATE_SFA-S003-P002-WP-B1-patch04_L-GATE_V_v1.0.0
from: team_110 (Claude Opus 4.7, orchestrator)
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B1-patch04
status: ACTIVE
verdict: PENDING
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator) ≠ team_10 Sonnet (builder) ≠ team_190 GPT-5.5 (validator) — three distinct engines"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04/LOD400_spec.md
spec_version: v1.0.1
build_commit: a0397cd
report_commit: 7d578ac
build_report_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch04/BUILD_REPORT_v1.0.0.md
prior_gate_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch04/LOD400-VERDICT_R2_v1.0.0.md
prior_gate_result: PASS (L-GATE_S R2, 16/16 VCs)
---

# L-GATE_V Mandate — patch04

## 1. Scope

Validate the Sonnet sub-agent build of patch04 (LARGE Integration WP) against LOD400 v1.0.1 ACs.

## 2. Pre-flight
Confirm GPT-5.5. Builder is team_10 Sonnet (commit `a0397cd`). Builder ≠ validator.

## 3. Validation Criteria (16 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-V1 | **IR#1 three-engine separation** | Build commit `a0397cd` authored under Sonnet co-author; report commit `7d578ac` likewise; this verdict by GPT-5.5. All three engines distinct. |
| VC-V2 | **AC-01..AC-03 Ginger baseline** | `JMF_CROP_MAP["Ginger"] == "ג'ינג'ר"`; `"ג'ינג'ר" in JMF_CROP_MAP.values()`; `len(JMF_CROP_MAP) == 87` |
| VC-V3 | **AC-04..AC-07 Migration 047** | `alembic current` shows `047`; table `crop_knowledge_notes_crops` exists with `(note_id, crop_id)` PK; index `ix_ckn_crops_crop_id` exists; downgrade to `046` clean |
| VC-V4 | **AC-08..AC-09 Junction ORM + cascade** | `crop_knowledge_notes.crops_linked` relationship returns list; cascading delete tested |
| VC-V5 | **AC-10..AC-14 Loader script** | `python scripts/load_masterclass_sheets.py --dry-run` parses without error; `--load-db` produces JSON files at `data/jmf/extracted/jmf_book/`; schema conforms (`schema_version: '1.0'`); every `body_text` ≤ 2000 chars; `is_internal_farm_use_only=true` |
| VC-V6 | **AC-15..AC-17 Data-fix script** | `python scripts/patch03_data_fix.py --dry-run` reports per-row impact; `--apply` idempotent (sample test); missing-row tolerance |
| VC-V7 | **AC-18 — 355 passed crop_book** | `pytest tests/crop_book/ -q` → 355 passed + 1 pre-existing publisher failure (OOS — do NOT flag) |
| VC-V8 | **AC-19 — integration tests pass** | `pytest tests/integration/ -q` → all new test_load_masterclass tests pass |
| VC-V9 | **AC-20 — validate_aos.sh 0 FAIL** | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 29 PASS / 19 SKIP / 0 FAIL |
| VC-V10 | **AC-21 — diff scope** | `git show --name-only a0397cd` shows changes ONLY in §2.1 + §2.2 file list (5 NEW + 6 MODIFIED = 11 source files + 24 data JSON files). No other LOCKED file. |
| VC-V11 | **AC-22 — 24-group dict UNCHANGED** | `test_jmf_crop_map_duplicate_target_allowlist` STILL asserts the same 24-group dict from post-patch03 (patch06 changes this; patch04 must NOT). |
| VC-V12 | **IR#4 builder discipline** | `_aos/roadmap.yaml` NOT touched in commit `a0397cd`. Lifecycle remains team_110-only. |
| VC-V13 | **Fair-use posture** | Every `body_text` field across all 24 JSON files ≤ 2000 chars; every record has `is_internal_farm_use_only: true`. Sample 5 JSONs. |
| VC-V14 | **24 JSON cache files acceptable** | LOD400 §2.3 anticipated "~37 files" but Sonnet processed 28 → 24 (after dedup on `crop_jmf_en` collisions). This is acceptable: the 13 non-emitted MDs fall in the "NEW/VARIANT" NotebookLM categories (per the README cross-reference) and were correctly skipped. Confirm BUILD_REPORT logs these skips with reasons. |
| VC-V15 | **Sheet 056 deferral acknowledged** | BUILD_REPORT §8 (or similar) documents that the M2M sheet 056 (storage/washing) was NOT loaded — junction infrastructure is built and tested, but the actual cross-crop link population is deferred (sheet has no `english_keys` in the index; full mapper requires additional logic). This is acceptable per LOD400 (the AC was about Migration 047, not sheet 056's data); flag as ADVISORY at most, not BLOCKER. |
| VC-V16 | **No regression of patch03 ACs** | `pytest tests/crop_book/test_jmf_crop_map.py::test_parsnips_value_post_patch02 tests/crop_book/test_jmf_crop_map.py::test_shallots_value_post_patch02 tests/crop_book/test_jmf_crop_map.py::test_mesclun_value_post_patch03` and similar all still pass. |

## 4. Commands

```bash
cd /Users/nimrod/Documents/SmallFarmsAgents

# 1. Engine + commit
git show --stat a0397cd | head -20
git log -1 --format='%an %ae %s' a0397cd

# 2. Ginger + size + 5 new baselines
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
print(f'Ginger: {JMF_CROP_MAP.get(\"Ginger\")!r}')
print(f'len: {len(JMF_CROP_MAP)} (expect 87)')
"

# 3. Migration + table
alembic current
psql or python3 sqlite probe — confirm crop_knowledge_notes_crops table exists with both FKs

# 4. Loader dry-run
python scripts/load_masterclass_sheets.py --dry-run | head -30

# 5. Data-fix dry-run
python scripts/patch03_data_fix.py --dry-run | head -20

# 6. Tests
python3 -m pytest tests/crop_book/ -q
python3 -m pytest tests/integration/ -q

# 7. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 8. Diff scope + IR#4
git show --name-only a0397cd | sort -u
git show --name-only a0397cd | grep "_aos/roadmap.yaml" && echo "IR#4 VIOLATION" || echo "IR#4 CLEAN"

# 9. JSON file sample
ls data/jmf/extracted/jmf_book/ | wc -l   # expect 24
cat data/jmf/extracted/jmf_book/Carrots.json | python3 -m json.tool | head -20

# 10. body_text length check
python3 -c "
import json, pathlib, glob
violations = []
for p in glob.glob('data/jmf/extracted/jmf_book/*.json'):
    d = json.load(open(p))
    for note_type, recs in d.get('notes', {}).items():
        for r in recs:
            if len(r.get('body_text','')) > 2000:
                violations.append((p, note_type, len(r['body_text'])))
print(f'body_text > 2000 violations: {len(violations)}')
for v in violations[:5]: print(v)
"

# 11. fair-use flag check
python3 -c "
import json, glob
bad = [p for p in glob.glob('data/jmf/extracted/jmf_book/*.json') if not json.load(open(p)).get('is_internal_farm_use_only')]
print(f'fair-use flag missing: {len(bad)}')
"
```

## 5. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch04/LGATEV-VERDICT_v1.0.0.md`

Frontmatter MUST include: `build_commit: a0397cd`, `spec_version: v1.0.1`, `engine: GPT-5.5`, `criteria_total: 16`, standard verdict fields.

Commit:
```
gate(WP-B1-patch04/L-GATE_V): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision:
- PASS / PASS_WITH_FINDINGS (0 blockers) → team_110 closes patch04 (Phase 7+8), then unblocks patch06 BUILD
- FAIL → R2

---

*L-GATE_V mandate 2026-05-25 by team_110.*
