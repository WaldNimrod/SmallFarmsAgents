---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_V_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7) AND team_10 (Claude Sonnet 4.6 sub-agent). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.1.3
spec_lock_commit: "d195b75"
build_report_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md
build_head_commit: "b6ecb6e"
prior_lgs_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.3.md
---

# L-GATE_V Mandate — SFA-S003-P002-WP-B2

**ספר גידולים: JMF NI Extraction Layer (AI-assisted, text-file input)**
**Track:** A | **Profile:** L0 | **Effort:** LARGE | **Risk:** MEDIUM

---

## 1. Gate History

| Gate | Result | Notes |
|------|--------|-------|
| L-GATE_E | PASS | team_00 (2026-05-24) |
| L-GATE_S R1/R2/R3/R4 | FAIL/FAIL/FAIL/**PASS_WITH_FINDINGS** | team_190 (GPT-5.5) — 4 rounds; spec evolved v1.0.0→v1.1.3 |
| L-GATE_B | **BUILD_COMPLETE** | team_10 (Sonnet sub-agent). 8 build commits `6e9d92d..b6ecb6e`. 37 new tests; 288 total; 1 pre-existing publisher failure out-of-scope |
| L-GATE_V | (this mandate ↓) | team_190 |

---

## 2. Scope

Constitutional validation of the team_10 build at HEAD `b6ecb6e` against LOD400 v1.1.3 (commit `d195b75`).

**In-scope (8 build commits):** `6e9d92d`, `808eb47`, `de38372`, `ae8a3c0`, `91f2081`, `f0ce180`, `e95dce4`, `b6ecb6e`.

**Out-of-scope** (3 hub-driven AOS propagation commits in range; IR#11 source→snapshot canonical flow): `92584ef`, `f2c6e5c`, `38a7371`. These touched ONLY `_aos/governance/`, `_aos/lean-kit/`, `_aos/last_gov_sync.yaml` — files explicitly excluded from team_110/team_10 mandate scope.

---

## 3. Validation Criteria (20 VVs)

| # | Criterion | Check |
|---|-----------|-------|
| VV-1 | **IR#1 cross-engine** | 3 distinct engines: Opus (team_110) ≠ Sonnet (team_10) ≠ GPT-5.5 (you). Verify via `git log --format='%h %an %s' d195b75..b6ecb6e`. |
| VV-2 | **IR#4 single-writer roadmap** | `git diff d195b75..b6ecb6e -- _aos/roadmap.yaml` is EMPTY. |
| VV-3 | **IR#5 validator independence** | team_190 not influenced by builder. |
| VV-4 | **IR#6 _COMMUNICATION/ routing** | BUILD_REPORT at canonical path. |
| VV-5 | **IR#11 governance untouched (B2 build commits ONLY)** | For each of the 8 build commits: `git show --name-only <sha>` returns no paths matching governance/lean-kit/project_identity. |
| VV-6 | **LOD500_LOCKED audit (16 paths)** | For each path in spec §2.2: `git diff d195b75..b6ecb6e -- <path>` empty. Includes models.py, source_registry.py, field_policy.py, reconciler.py, enrichment_runner.py, enrichment_models.py, crop_task_templates.py (B1), jmf_masterclass.py, constants.py, tend.py, jmf.py, views.py, publisher/**, mu-plugin/, migrations 001-044. |
| VV-7 | **`ni_importer.py` APPEND-ONLY** | `git diff d195b75..b6ecb6e -- organic_market_agent/crop_book/importer/ni_importer.py --stat` shows only insertions (+65, 0 deletions per team_110 independent check). Diff body = only the `_upsert_knowledge_note` function appended. NO class change. |
| VV-8 | **AC-03/AC-03b: NI_IMPORTER_CLASSES + bypass proof** | `len(NI_IMPORTER_CLASSES) == 6`; B2 source labels absent from `ni_registry.registered_labels` (proves `ni_registry.register()` was NOT called at module load). |
| VV-9 | **AC-04a body_text length CHECK at DB level** | `pytest tests/crop_book/test_migration_045.py` PASS; 2001-char insert raises IntegrityError. |
| VV-10 | **AC-04b note_type CHECK (13 values)** | 13 enum values accepted; non-enum value rejected. |
| VV-11 | **AC-05 licensing flag immutability** | `is_internal_farm_use_only=True` hardcoded in `_upsert_knowledge_note`; caller cannot set False. |
| VV-12 | **AC-10/AC-12 engine reuse via existing `_upsert_source_value(session, variety_id, sv)`** | `pytest tests/crop_book/test_ni_jmf_book.py` PASS. Cultivar_recommendation rows produced via the existing seed.py helper signature (NOT a new variant). |
| VV-13 | **AC-19 seed.py scope** | `git diff d195b75..b6ecb6e -- organic_market_agent/crop_book/importer/seed.py` = exactly 2 CLI flag additions + 1 call-site block. NO helper function additions. (Resolvers live in NIImporter subclasses per §7.2.) |
| VV-14 | **AC-20 _aos/governance + _aos/lean-kit CLEAN (B2 commits only)** | Same as VV-5 — re-confirms for the 8 build commits. |
| VV-15 | **AC-21a/b/c publisher/views.py CLEAN + isolation test PASS** | (a) `git diff d195b75..b6ecb6e -- organic_market_agent/publisher/ organic_market_agent/views.py` is EMPTY. (b) `pytest tests/crop_book/test_ni_publisher_isolation.py` PASS — no `crop_knowledge_notes` or `CropKnowledgeNote` references in publisher/ or views.py. |
| VV-16 | **AC functional coverage** | `pytest tests/crop_book/ -q` returns 288 passed + 1 pre-existing publisher failure. 37 NEW B2 tests. |
| VV-17 | **BUILD_REPORT completeness** | 8 required sections present (verdict, per-AC table, pytest, validate_aos.sh, LOD500_LOCKED audit, files touched, runtime stats placeholder, open items). |
| VV-18 | **validate_aos.sh exit code 0** | 0 FAIL. PASS/SKIP totals: 29/19 (drift acknowledged via F-S-B2-04 carry). |
| VV-19 | **YAML / artifact integrity** | `_aos/roadmap.yaml` parses; B2 entry shows `status: BUILDING`, `lod_status: LOD400_LOCKED`, `current_lean_gate: L-GATE_B`. |
| VV-20 | **Migration 045 present (sequencing — unblocks B3)** | `ls organic_market_agent/db/versions/045_*.py` returns `045_crop_knowledge_notes.py`. Confirms B3 builder may now be spawned (B3's `down_revision="045"` requirement satisfied). |

**Total: 20 VVs.**

---

## 4. Required Commands (excerpt — full list inline in §3)

```bash
# 1. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Cross-engine attestation
git log --format='%h %an %s' d195b75..b6ecb6e

# 3. AC-03b bypass proof
python3 -c "
import organic_market_agent.crop_book.importer.ni
from organic_market_agent.crop_book.importer.ni_importer import ni_registry
from organic_market_agent.crop_book.importer.ni import NI_IMPORTER_CLASSES
print(f'NI_IMPORTER_CLASSES: {len(NI_IMPORTER_CLASSES)}')
b2 = {cls().source_label for cls in NI_IMPORTER_CLASSES}
print(f'B2 labels: {sorted(b2)}')
print(f'registered: {ni_registry.registered_labels}')
print(f'overlap: {b2 & set(ni_registry.registered_labels)}')
"

# 4. ni_importer.py APPEND-only check
git diff d195b75..b6ecb6e --stat -- organic_market_agent/crop_book/importer/ni_importer.py

# 5. AC-21 publisher/views.py CLEAN
git diff d195b75..b6ecb6e --stat -- organic_market_agent/publisher/ organic_market_agent/views.py
pytest tests/crop_book/test_ni_publisher_isolation.py -v 2>&1 | tail -10

# 6. Migration 045 sequencing
ls organic_market_agent/db/versions/045_*.py

# 7. Focused regression
pytest tests/crop_book/test_ni_jmf_book.py tests/crop_book/test_migration_045.py -v 2>&1 | tail -20

# 8. Full suite
pytest tests/crop_book/ -q 2>&1 | tail -5
```

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD500-VERDICT_v1.0.0.md`**

Commit with:
```
gate(WP-B2/L-GATE_V): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision criteria:
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 7 (ADR042 closure) + Phase 8 (COMPLETION_REPORT)
- **FAIL (≥1 blocker)** → team_110 routes remediation through team_10

Independence rule: do NOT read BUILD_REPORT or DISPOSITION until AFTER your independent VV evaluation.

---

## 6. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_100 NOT in routing chain.

---

*L-GATE_V mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Builder closed: team_10 (Claude Sonnet 4.6 sub-agent). Migration 045 now committed — B3 builder unblocked.*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD500-VERDICT_v1.0.0.md`.*
