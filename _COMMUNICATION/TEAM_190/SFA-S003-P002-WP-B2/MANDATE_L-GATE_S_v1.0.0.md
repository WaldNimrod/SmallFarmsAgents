---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2 — same EXECUTION_MANDATE as B1 + patch01 + B3 (covers full WP-B program)."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.0.0
parallel_with: SFA-S003-P002-WP-B3 (validate independently — no inter-dependency)
---

# L-GATE_S Mandate — SFA-S003-P002-WP-B2

**ספר גידולים: JMF PDF NI Extraction Layer (AI-assisted)**
**Track:** A | **Profile:** L0 | **Effort:** LARGE | **Risk:** MEDIUM (LLM extraction + licensing surface)

---

## 1. Gate History

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00; commit `f61c1da` (B-program-wide registration) |
| L-GATE_PRE_HANDOFF R1-R3 | PASS/FAIL/PASS | 2026-05-24 | Final PASS `7c3d7d6` (program-wide) |
| L-GATE_S | (this mandate ↓) | — | LOD400 v1.0.0 |

WP-B1 + WP-B1-patch01 are **LOD500_LOCKED** at `3e1f946` (extended JMF_CROP_MAP, 86 entries). WP-B3 is parallel-eligible with B2 (separate L-GATE_S running in parallel).

---

## 2. Scope

Validate the LOD400 spec for **WP-B2** (JMF PDF NI Extraction) as a spec-only constitutional review. This is a LARGE WP — LLM-assisted extraction harness + 3 NIImporter subclasses + new table + cache governance + licensing considerations.

Key novelties vs. B1 / patch01 / B3:
- LLM-assisted prepare step (NOT runtime; one-time per release)
- Committed JSON cache directory governance
- PDF licensing language enforcement at the DB schema layer (CHECK constraint on `body_text` length)
- NIImporter subclass framework materializing WP-A's `NiSourceBase` skeleton

---

## 3. Validation Criteria (20 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **IR#1 cross-engine** | LOD400 frontmatter assigns builder = `sfa_build` (Sonnet recommended, non-team_190) and validator = `team_190 (non-Claude)`. team_110 is Opus 4.7 (orchestrator). |
| VC-2 | **IR#4 single-writer roadmap** | LOD400 does not instruct builder to mutate `_aos/roadmap.yaml`. |
| VC-3 | **IR#6 _COMMUNICATION/ routing** | BUILD_REPORT path is `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md`. |
| VC-4 | **IR#11 governance untouched** | LOD400 §2.2 explicitly lists `_aos/governance/`, `_aos/lean-kit/` as untouchable. |
| VC-5 | **LOD500_LOCKED guard (16+ paths)** | §2.2 enumerates the locked inventory including all WP-A engine SSoT + B1 + patch01 deliverables + `constants.py` (LOD500_LOCKED via B1-patch01) + `ni_importer.py` (WP-A skeleton). §15 MODIFY list contains exactly 3 existing files: `ni_importer.py` (APPEND-only, single function), `seed.py` (additive flags), `CHANGELOG.md`. |
| VC-6 | **ni_importer.py append-only scope** | §7.5 declares the ONLY permitted modification to WP-A's `ni_importer.py`: APPEND `_upsert_knowledge_note` helper function at module level. NO change to `NiSourceBase` class. AC-18 enforces. |
| VC-7 | **Migration chain integrity** | LOD400 §3 declares `revision = "045"`, `down_revision = "044"`. Current head is `044_crop_task_templates.py` (B1). No conflicting 045 exists. Note: parallel-running B3 also produces 046 with `down_revision = "045"` — B2 045 must land first or B3 STOPs and inquires (documented in B3 spec). |
| VC-8 | **SQLite + Postgres compatibility** | §3 uses `BigInteger().with_variant(Integer(), "sqlite")`. `length(body_text)` CHECK is portable. `note_type IN (...)` CHECK is portable. |
| VC-9 | **note_type CHECK scope** | §3 CHECK constraint enumerates 10 enum values; §4 ORM tuple `NOTE_TYPE_VALUES` enumerates the same 10 (8 ebook + 2 FT). No B3-related task_type leakage. |
| VC-10 | **body_text length CHECK at DB level** | §3 CHECK `length(body_text) <= 2000`. §4 ORM declares same via `BODY_TEXT_MAX_LENGTH = 2000`. AC-04a regression-tests at DB insert level (not just runtime). |
| VC-11 | **Licensing flag schema-level** | §3 declares `is_internal_farm_use_only BOOLEAN NOT NULL DEFAULT TRUE`. §4 ORM mirrors. §5 cache schema does NOT include this field at extraction time — it's a DB-only default. AC-05 enforces the flag is never silently flipped by the importer. |
| VC-12 | **JSON cache schema completeness** | §5 specifies the JSON schema with all required keys: `schema_version`, `source`, `crop_jmf_en`, `provenance.{pdf,pages,extraction_model,extracted_at}`, `notes.<note_type>`. AC-08 enforces schema validation rejects files missing required keys or with bad `note_type`. |
| VC-13 | **Cache commit policy (advisory #2)** | §11 + §12 advisory #2 disposition: cache directory is COMMITTED (not gitignored) with `.gitattributes linguist-vendored` to suppress diff noise. §15 deliverables list `.gitkeep` files for each cache subdirectory. Reasoning documented (reproducibility, review, audit). |
| VC-14 | **Extraction runner is NOT in production code path** | §6 declares `scripts/extract_jmf_ni.py` (NOT under `organic_market_agent/`). §11 Step 10 nuance: builder does NOT run live API calls; only commits fixture JSONs + .gitkeep skeleton. Real extraction is team_00's manual post-merge step. |
| VC-15 | **Engine reuse: cultivar_recommendation via _upsert_source_value** | §7.2 + AC-12: when an ebook chapter contains `cultivar_recommendation`, the NI loader produces BOTH a `crop_knowledge_notes` row AND a `crop_variety_source_values` row with `field_name='cultivar_recommendation'`, `source='NI:jmf_book_v1'`, `trust_tier='NI'`, `confidence_weight=NULL`. This is hard-override per WP-A engine. |
| VC-16 | **PDF licensing advisory #1 disposition** | §12 advisory #1: schema enforces snippet bound (`body_text ≤ 2000` CHECK) + `is_internal_farm_use_only=TRUE` flag + `provenance_pdf` + `provenance_pages` for audit. Spec explicitly forbids publication: "Extracted narrative may be displayed to logged-in farm operators ONLY; never to public WordPress visitors. B2 does NOT push NI prose to WordPress." |
| VC-17 | **Transitive WP-A dependency (advisory #4)** | §2.2 + §8 (LOD200) name specific WP-A surfaces: `ni_importer.py::NiSourceBase`, `source_registry.py` (NI prefix-match), `_upsert_source_value` semantics. §2.1 names patch01 commit `3e1f946` for the JMF_CROP_MAP dependency. |
| VC-18 | **AC measurability** | All 18 ACs (§9) phrased as objective Python assertions, IntegrityError tests, file/path existence, or count checks. No subjective "should work" wording. |
| VC-19 | **Test coverage adequacy** | §10 lists 15+ tests across 9 new files. 4 fixture JSON files at `tests/crop_book/fixtures/ni/`. ALL tests use SQLite in-memory + fixture JSON; ZERO live Anthropic API calls. |
| VC-20 | **`validate_aos.sh` + YAML integrity** | (a) `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 29 PASS / 18 SKIP / 0 FAIL. (b) `python3 -c "import yaml; yaml.safe_load(open('_aos/roadmap.yaml'))"` succeeds; WP-B2 entry shows `lod_status: LOD200_LOCKED`, `current_lean_gate: L-GATE_E`, L-GATE_E PASS in gate_history. WP-B1 + patch01 entries remain `DONE / LOD500_LOCKED`. |

**Total: 20 criteria.**

---

## 4. Files to Review

### Spec documents (primary inputs)

- **LOD400 (under review):** `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md` (v1.0.0)
- **LOD200:** `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD200_spec.md` (v1.0.0)

### Context (for VC-5, VC-6, VC-15, VC-17)

- **WP-A `ni_importer.py`** (LOD500_LOCKED — verify NiSourceBase signature): `organic_market_agent/crop_book/importer/ni_importer.py`
- **WP-A `source_registry.py`** (verify NI prefix-match): `organic_market_agent/crop_book/source_registry.py`
- **B1-patch01 `JMF_CROP_MAP`** (verify ≥86 entries, used by B2's chapter mapping): `organic_market_agent/crop_book/constants.py`
- **Roadmap:** `_aos/roadmap.yaml` — confirm WP-B2 entry at `lod_status: LOD200_LOCKED`

### Required Commands

```bash
# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Roadmap parse
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
wp = [w for w in d['work_packages'] if w['id'] == 'SFA-S003-P002-WP-B2'][0]
print(wp['id'], wp['status'], wp['lod_status'], wp['current_lean_gate'])
"

# 3. WP-A NiSourceBase signature verification
python3 -c "
from organic_market_agent.crop_book.importer.ni_importer import NiSourceBase
import inspect
print('NiSourceBase is abstract:', inspect.isabstract(NiSourceBase))
print('load method present:', hasattr(NiSourceBase, 'load'))
"

# 4. JMF_CROP_MAP coverage (patch01 result, used by B2)
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
print(f'entries={len(JMF_CROP_MAP)}')
"
# Expected: entries=86

# 5. Migration head verification
ls organic_market_agent/db/versions/ | grep -E "^04[3-5]_" | sort
# Expected: only 043, 044 present (no 045 yet — B2 will create it)
```

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.0.md`**

7-section unified verdict template. **Commit the verdict** with:
```
gate(WP-B2/L-GATE_S): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

(team_190 commits — new canonical pattern established during patch01.)

**Decision criteria:**
- **PASS** / **PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 4 (roadmap transition) + Phase 5 (L-GATE_B mandate to builder sub-agent)
- **FAIL (≥1 blocker)** → team_110 remediates + R2

---

## 6. Authorization basis

ADR045 R2 #2; mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_100 NOT in routing chain.

---

*L-GATE_S R1 mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude). Parallel with B3 — independent validation.*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.0.md`.*
