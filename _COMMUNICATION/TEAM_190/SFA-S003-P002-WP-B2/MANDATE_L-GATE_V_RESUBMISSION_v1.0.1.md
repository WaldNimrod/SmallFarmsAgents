---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_V_v1.0.1
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: RESUBMISSION
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
build_head_commit: "69966be"
prior_lgv_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD500-VERDICT_v1.0.0.md
resubmission_round: 2
supersedes: MANDATE_SFA-S003-P002-WP-B2_L-GATE_V_v1.0.0
---

# L-GATE_V Mandate (R2) — SFA-S003-P002-WP-B2

Supersedes `MANDATE_..._v1.0.0`. Validate at new HEAD `69966be`. Both R1 findings closed.

---

## 1. Resolved Findings from R1

| # | Prior Finding | Sev. | Fix Applied |
|---|---|------|-------------|
| **F-LV-B2-01** | `--ni-only` ran JMF/Tend/Tend-overlay before returning; seed.py had TWO NI call-site blocks (one in dry-run branch, one in SessionFactory branch). Violated AC-13 + AC-19 + LOD400 §8 (1 call-site only). | BLOCKER | Commit `18f8671` (team_10 Sonnet sub-agent) — `build(WP-B2/fix-LV-B2-01): make --ni-only actually NI-only + dedup NI call-site`. Added module-level `_run_ni_ingestion(session)` helper (single NI call-site block, reused). Moved `--ni-only` to a fast-path early-return BEFORE any JMF/Tend code path. Added regression test `test_ac13_ni_only_dry_run_suppresses_jmf_and_tend` capturing stdout/stderr and asserting zero `JMF MasterClass:` / `Seeding crop_families` / `Parsed` lines. Verified by team_110: `python3 -m organic_market_agent.crop_book.importer.seed --all --ni-only --dry-run` output now contains ONLY `INFO __main__: DRY RUN — no DB writes` (zero JMF/Tend output). |
| **F-LV-B2-02** | BUILD_REPORT §3.3 test-file inventory cited nonexistent names (test_ni_migration.py, test_ni_orm.py, etc.). | MINOR | Commit `69966be` (team_10 Sonnet) — `build(WP-B2/fix-LV-B2-02): correct BUILD_REPORT test-file inventory`. §3.3 now lists actual filenames (test_migration_045.py, test_crop_knowledge_notes_orm.py, test_seed_ni_cli.py, etc.). |

---

## 2. Scope

Re-validate the build at new HEAD `69966be` against LOD400 v1.1.3 (commit `d195b75`).

**In-scope (10 build commits cumulative — 8 original + 2 remediation):**
- Original 8: `6e9d92d`, `808eb47`, `de38372`, `ae8a3c0`, `91f2081`, `f0ce180`, `e95dce4`, `b6ecb6e`
- R1 remediation: `18f8671` (BLOCKER fix), `69966be` (MINOR fix)

**Out-of-scope (interleaved non-B2 commits in range):**
- B3 closure commits between B2 remediation steps: `10d419e` (B3 ADR042 closure), `c7e0d9e` (B3 COMPLETION_REPORT). These touched `_aos/roadmap.yaml`, `_archive/SFA-S003-P002-WP-B3/`, `_COMMUNICATION/team_110/SFA-S003-P002-WP-B3/` — explicitly out of B2 scope.
- Hub-sync commits if any (`gov(aos-sync)`, `governance(sync)`) — IR#11 canonical source→snapshot flow.

Independence rule: do NOT read R1 verdict before forming R2 conclusions. The R1 verdict is referenced in §1 ONLY as fix-traceability evidence.

---

## 3. R2-specific evidence checks (3 probes)

```bash
# 1. F-LV-B2-01 BLOCKER fix — --ni-only suppresses JMF/Tend
python3 -m organic_market_agent.crop_book.importer.seed --all --ni-only --dry-run 2>&1 | \
  grep -cE "JMF MasterClass:|Seeding crop_families|Parsed.*Tend"
# Expected: 0

# 2. seed.py has exactly one NI call-site (the _run_ni_ingestion helper)
grep -cE "^def _run_ni_ingestion" organic_market_agent/crop_book/importer/seed.py
# Expected: 1

grep -cE "_run_ni_ingestion\(session\)" organic_market_agent/crop_book/importer/seed.py
# Expected: 2 (one call from dry-run branch, one from SessionFactory branch — both
# inside the --ni-only fast-path, OR factored differently. The KEY check is that
# the JMF/Tend ingestion code does NOT execute when --ni-only is set. Verified
# functionally by probe #1.)

# 3. AC-13 regression test exists
grep -nE "test_ac13_ni_only_dry_run_suppresses_jmf_and_tend|test_ni_only_dry_run|--ni-only --dry-run" tests/crop_book/test_seed_ni_cli.py
# Expected: ≥1 hit (the new regression test definition)

# 4. seed.py scope still disciplined (additive only — no new files; resolution helpers still NOT in seed.py)
git diff d195b75..69966be --stat -- organic_market_agent/crop_book/importer/seed.py
# Expected: modest net additions (the sub-agent reported 64 insertions + 50 deletions = +14 net,
# representing the helper extraction + early-return). NO _resolve_default_variety_for_jmf_crop
# or _resolve_crop_id_for_jmf_crop functions (those live in NIImporter subclasses per §7.2).
grep -nE "_resolve_default_variety_for_jmf_crop|_resolve_crop_id_for_jmf_crop" organic_market_agent/crop_book/importer/seed.py
# Expected: 0 hits (no forbidden helpers in seed.py)

# 5. BUILD_REPORT §3.3 inventory now matches actual files
grep -E "test_ni_migration\.py|test_ni_orm\.py|test_ni_seed_flags\.py" _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B2/BUILD_REPORT_v1.0.0.md
# Expected: 0 hits (the hallucinated names are gone)

ls tests/crop_book/test_migration_045.py tests/crop_book/test_crop_knowledge_notes_orm.py tests/crop_book/test_seed_ni_cli.py 2>&1
# Expected: all 3 exist

# 6. LOD500_LOCKED audit unchanged from R1
python3 - <<'PY'
import subprocess
build_shas = ["6e9d92d", "808eb47", "de38372", "ae8a3c0", "91f2081",
              "f0ce180", "e95dce4", "b6ecb6e", "18f8671", "69966be"]
locked_paths = [
    "organic_market_agent/views.py",
    "organic_market_agent/publisher/wp_upload.py",
    "organic_market_agent/publisher/upload_dispatch.py",
    "organic_market_agent/crop_book/importer/tend.py",
    "organic_market_agent/crop_book/importer/jmf.py",
    "organic_market_agent/crop_book/importer/jmf_masterclass.py",
    "organic_market_agent/crop_book/source_registry.py",
    "organic_market_agent/crop_book/field_policy.py",
    "organic_market_agent/crop_book/models.py",
    "organic_market_agent/crop_book/importer/reconciler.py",
    "organic_market_agent/crop_book/importer/enrichment_runner.py",
    "organic_market_agent/crop_book/enrichment_models.py",
    "organic_market_agent/crop_book/crop_task_templates.py",
    "organic_market_agent/crop_book/crop_knowledge_notes.py",
    "organic_market_agent/crop_book/constants.py",
    "organic_market_agent/db/versions/044_crop_task_templates.py",
    "organic_market_agent/db/versions/045_crop_knowledge_notes.py",
]
import re
for path in locked_paths:
    diff = subprocess.check_output(["git", "diff", "d195b75..69966be", "--", path], text=True)
    status = "CLEAN" if not diff else "CHANGED"
    print(f"{status}  {path}")
PY
# Expected: ALL CLEAN

# 7. Full test suite
pytest tests/crop_book/ -q 2>&1 | tail -5
# Expected: ≥340 passed, 1 pre-existing publisher failure

# 8. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expected: 0 FAIL
```

---

## 4. Validation criteria

Re-run all 20 VVs from `MANDATE_..._v1.0.0.md`. The F-LV-B2-01 fix touches VV-12/13/16 (AC-13 + AC-19 + functional coverage); F-LV-B2-02 touches VV-17 (BUILD_REPORT completeness). All other VVs unchanged from R1.

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD500-VERDICT_v1.0.1.md`**

Commit with:
```
gate(WP-B2/L-GATE_V): team_190 R2 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision criteria:
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 7 ADR042 closure + Phase 8 COMPLETION_REPORT
- **FAIL (≥1 blocker)** → R3

---

## 6. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_100 NOT in routing chain.

---

*R2 resubmission mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Builder: team_10 (Sonnet sub-agent) — both R1 remediation commits delivered.*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD500-VERDICT_v1.0.1.md`.*
