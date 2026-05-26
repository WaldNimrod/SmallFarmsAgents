---
id: MANDATE_SFA-S003-P002-WP-B1-patch08_L-GATE_V_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B1-patch08
status: ACTIVE
verdict: PENDING
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190 — three distinct engines"
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md
spec_version: v1.0.1
build_commit: 7645860
report_commit: 083aadc
build_report_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch08/BUILD_REPORT_v1.0.0.md
prior_gate_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch08/LOD400-VERDICT_R2_v1.0.0.md
prior_gate_result: PASS clean
---

# L-GATE_V — patch08 (variety-parser cleanup)

## 1. Scope
Verify Sonnet build commit `7645860` against LOD400 v1.0.1 ACs.

## 2. Validation Criteria (10 VCs)

| # | Criterion | Check |
|---|-----------|-------|
| VC-V1 | IR#1 three-engine | Sonnet commit `7645860`; this verdict GPT-5.5 |
| VC-V2 | AC-01..AC-02 — filter integrated | `KNOWN_SECTION_HEADERS` frozenset present + `_is_valid_cultivar_name` function defined + invoked from `_extract_cultivar_names`. Blacklist checked FIRST. |
| VC-V3 | AC-03 — regression test PASSES | `pytest tests/integration/test_load_masterclass_sheets.py::test_extract_cultivar_filter_rejects_noise -v` returns 1 passed |
| VC-V4 | AC-04..AC-05 — cleanup script behavior | `scripts/patch08_cleanup_noise_varieties.py` exists; dry-run default; --apply idempotent (2nd run is no-op) — verifiable via test fixture |
| VC-V5 | AC-06..AC-07 — filter correctness | Real cultivars (Carmen, Ace, Sprinter, Escamillo) accepted by filter; noise patterns (URLs, bullets, Intensive Spacing) rejected |
| VC-V6 | AC-08 — integration suite | `pytest tests/integration/ -q` → **16 passed** (was 15 + 1 new) |
| VC-V7 | AC-09 — crop_book non-regression | `pytest tests/crop_book/ -q` → previous count maintained (350 passed + 1 OOS publisher), OR 327 passed + 23 skipped + 1 OOS if running in skip-aware env (acceptable variance) |
| VC-V8 | AC-10 — validate_aos.sh + diff scope | `validate_aos.sh` → 29/19/0 FAIL; `git show --name-only 7645860` lists exactly 4 files: `scripts/load_masterclass_sheets.py`, `scripts/patch08_cleanup_noise_varieties.py`, `tests/integration/test_load_masterclass_sheets.py`, `CHANGELOG.md` |
| VC-V9 | IR#4 builder discipline | Sonnet commit does NOT touch `_aos/roadmap.yaml` |
| VC-V10 | KNOWN_SECTION_HEADERS coverage | The 10 entries are present (Intensive Spacing, Cultivars, Cultivar Suggestions, Pests, Diseases, Harvest, Storage, Sowing, Transplanting, Yield). Both Python frozenset AND SQL tuple in cleanup script — kept in sync. |

## 3. Commands

```bash
git show --stat 7645860 | head -15
git log -1 --format='%an %s' 7645860

# KNOWN_SECTION_HEADERS in script
grep -A2 "KNOWN_SECTION_HEADERS:" scripts/load_masterclass_sheets.py | head -15
grep -A2 "KNOWN_SECTION_HEADERS =" scripts/patch08_cleanup_noise_varieties.py 2>&1 | head -15

# Filter function
grep -A2 "def _is_valid_cultivar_name" scripts/load_masterclass_sheets.py | head -5

# Tests
python3 -m pytest tests/integration/test_load_masterclass_sheets.py::test_extract_cultivar_filter_rejects_noise -v
python3 -m pytest tests/integration/ -q
python3 -m pytest tests/crop_book/ -q

# validate + diff scope
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
git show --name-only 7645860 | sort -u
git show --name-only 7645860 | grep "_aos/roadmap.yaml" && echo "VIOLATION" || echo "IR#4 CLEAN"
```

## 4. Output
`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch08/LGATEV-VERDICT_v1.0.0.md` (frontmatter: `build_commit: 7645860`, `criteria_total: 10`).

Commit: `gate(WP-B1-patch08/L-GATE_V): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 closes patch08.
FAIL → R2.

---
