---
id: MANDATE_SFA-S003-P002-WP-B1-patch01_L-GATE_V_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_V
wp: SFA-S003-P002-WP-B1-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7, orchestrator) AND team_10 (Claude Sonnet 4.6, builder sub-agent). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md
spec_version: v1.0.3
spec_lock_commit: "c1b14c5"
build_report_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md
build_head_commit: "048ce66"
prior_lgs_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD400-VERDICT_v1.0.2.md
---

# L-GATE_V Mandate — SFA-S003-P002-WP-B1-patch01

**ספר גידולים: JMF_CROP_MAP alias extension + Rutabaga Hebrew correction**
**Track:** A | **Profile:** L0 | **Effort:** SMALL | **Risk:** LOW

---

## 1. Gate History

| Gate | Result | Date | Validator |
|------|--------|------|-----------|
| L-GATE_E | PASS | 2026-05-25 | team_00 (Principal) |
| L-GATE_S R1 / R2 / R3 | FAIL / FAIL / **PASS_WITH_FINDINGS** | 2026-05-25 | team_190 (GPT-5.5). v1.0.3 LOCKED at `c1b14c5`. |
| L-GATE_B | **BUILD_COMPLETE** | 2026-05-25 | team_10 (Claude Sonnet 4.6 sub-agent). 3 build commits `929c30b..048ce66`. 10 new tests; 56 prior WP-B1 tests still PASS; 1 pre-existing publisher failure out-of-scope. |
| L-GATE_V | (this mandate ↓) | — | team_190 |

---

## 2. Scope

Constitutional validation of the team_10 build at HEAD `048ce66` against LOD400 v1.0.3 (commit `c1b14c5`). This is a SMALL literal-map patch — minimal change footprint, but verification is fully constitutional.

**In-scope commits for L-GATE_V:**
- `929c30b` — Step 2: constants.py edit (Rutabaga + 34 aliases)
- `d34e60c` — Step 3: tests (+10 new, AC-03 update)
- `048ce66` — Step 4: CHANGELOG + BUILD_REPORT

**Out-of-scope commits in the range (must be excluded from per-WP audits):**
- `417f3cc` — `governance(sync): propagate hub governance snapshot — 2026-05-25` (hub-driven AOS propagation per CLAUDE.md "_aos/ is READ-ONLY SNAPSHOT propagated from the hub via aos_sync_all.sh"; IR#11 allows source-to-snapshot flow)
- `7942166` — `gov(aos-sync): propagate hub b538182 → _aos/ (aos_sync_all.sh)` (same — second sync wave)

These two commits ONLY touched `_aos/governance/`, `_aos/lean-kit/`, and `_aos/last_gov_sync.yaml` — files explicitly excluded from team_110/team_10 mandate scope by IR#11 (governance flows source→snapshot only). They are constitutionally clean and do NOT touch any WP-B1, B1-patch01, or WP-A deliverable. The validate_aos.sh result moved from `29 PASS / 17 SKIP / 0 FAIL` to `29 PASS / 18 SKIP / 0 FAIL` due to one check reclassification from the governance update — not a regression.

---

## 3. Validation Criteria (20 VVs)

| # | Criterion | Check |
|---|-----------|-------|
| VV-1 | **IR#1 cross-engine** | Three distinct engines on chain: team_110 = Claude Opus 4.7, team_10 = Claude Sonnet 4.6 sub-agent, team_190 = GPT-5.5. Verify via `git log --format='%h %an %s%n%b---' c1b14c5..048ce66` showing builder commits ending `Claude Sonnet` and orchestrator commits ending `Claude Opus`. |
| VV-2 | **IR#4 single-writer roadmap** | `git diff c1b14c5..048ce66 -- _aos/roadmap.yaml` is EMPTY. |
| VV-3 | **IR#5 validator independence** | team_190 has not influenced the build. |
| VV-4 | **IR#6 _COMMUNICATION/ routing** | BUILD_REPORT exists at `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md`. No chat/inline communication. |
| VV-5 | **IR#11 governance scope** | Builder commits (`929c30b`, `d34e60c`, `048ce66`) MUST NOT have touched `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. (The other 2 in-range commits — `417f3cc`, `7942166` — are hub propagation per §2 above and are out-of-scope.) Verify via `git log --name-only 929c30b d34e60c 048ce66`. |
| VV-6 | **LOD500_LOCKED guard (15 paths)** | For each path in spec §7 (B1 + patch01 inherited list), `git diff c1b14c5..048ce66 -- <path>` is EMPTY. Critical: parent WP-B1 LOD400 spec MUST be CLEAN (`_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`). |
| VV-7 | **Additive-only scope** | Modified existing files limited to exactly 3: `organic_market_agent/crop_book/constants.py`, `tests/crop_book/test_jmf_crop_map.py`, `CHANGELOG.md`. No other existing file modified. (Out-of-scope governance sync commits may have touched other `_aos/` files; the per-WP audit excludes those.) |
| VV-8 | **`JMF_CROP_MAP` final state — Rutabaga fix** | `JMF_CROP_MAP["Rutabaga"] == "רוטבגה"`. Old value `"ברוקקואר"` is NOT present anywhere in `constants.py`. |
| VV-9 | **`JMF_CROP_MAP` final state — entry count** | `len(JMF_CROP_MAP) == 86`. |
| VV-10 | **`Eggplant  (Feld)` literal preserved** | `"Eggplant  (Feld)"` (with exactly 2 spaces and `(Feld)` qualifier) is a key in JMF_CROP_MAP. Verify byte-exactly. |
| VV-11 | **AC-03 Counter assertion enumerates exactly 25 pairs/groups** | Run Counter probe — must yield exactly the 25-entry dict from spec §4 AC-03 (Mesclun/Salad Mix, Summer Squash/Zucchini, Brussel Sprouts/Brussels Sprouts, etc.). |
| VV-12 | **AC functional coverage** | Run `pytest tests/crop_book/ -q`. Expected: ≥10 new patch01 tests PASS + 56 prior WP-B1 tests PASS = ≥66 WP-B1+patch01 tests. Total ≥251 with 1 pre-existing publisher failure acceptable. |
| VV-13 | **Test update preserves regression: AC-13 EX-override still PASSes** | `pytest tests/crop_book/test_jmf_ex_override_regression.py -v`. (The patch only edited JMF_CROP_MAP literal — should not affect EX-override behavior.) |
| VV-14 | **New tests cover all 8 patch01 ACs** | Test file inventory from BUILD_REPORT matches spec §5: extended `test_jmf_crop_map.py` (AC-01, AC-02, AC-03 update + AC-04.1) + 3 new files (`test_jmf_crop_map_aliases.py`, `test_jmf_live_workbook_coverage.py`, `test_jmf_seed_dry_run.py`). |
| VV-15 | **Live-workbook coverage threshold met** | AC-04 specified ≥42/50. BUILD_REPORT §7 reports actual count. Confirm it meets/exceeds 42. |
| VV-16 | **MINOR carry from L-GATE_S R3 closed** | The R3 MINOR (stale "~28" / "~6 pairs" prose) was addressed in v1.0.3 cleanup. Confirm via `grep -nE "~ *28 alias|~ *6 pair" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md` — must return zero matches (or matches only inside the v1.0.3 changelog block describing what was fixed, same by-design pattern as B1 V V-15). |
| VV-17 | **BUILD_REPORT completeness** | 8 required sections per mandate §8 (verdict, per-AC table, pytest, validate_aos.sh, LOD500_LOCKED audit, files touched, live-workbook coverage, open items). |
| VV-18 | **`validate_aos.sh` clean at HEAD** | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns `RESULT: 29 PASS / 18 SKIP / 0 FAIL`. (18 SKIP not 17 — explained in §2 above by hub governance sync; NOT a regression.) |
| VV-19 | **YAML / artifact integrity at HEAD** | `python3 -c "import yaml; yaml.safe_load(open('_aos/roadmap.yaml'))"` succeeds. WP-B1-patch01 entry: `status: BUILDING`, `lod_status: LOD400_LOCKED`, `current_lean_gate: L-GATE_B`. WP-B1 entry remains `DONE / LOD500_LOCKED` (untouched). WP-B2 + WP-B3 remain `PROPOSED` (no premature unblock). |
| VV-20 | **No untracked WP-scoped artifacts** | `git status --short` produces no `??` lines under `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/`, `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/`, `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/`, `organic_market_agent/crop_book/`, `tests/crop_book/`. (Pre-existing `??` drift elsewhere is not part of this WP scope.) |

**Total: 20 VVs.**

---

## 4. Required Commands

```bash
# 1. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. roadmap state
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
for wp_id in ['SFA-S003-P002-WP-B1', 'SFA-S003-P002-WP-B1-patch01', 'SFA-S003-P002-WP-B2']:
    wp = [w for w in d['work_packages'] if w['id']==wp_id][0]
    print(wp['id'], wp['status'], wp['lod_status'], wp['current_lean_gate'])
"

# 3. LOD500_LOCKED audit on builder commits ONLY (exclude hub-sync commits)
python3 - <<'PY'
import re, subprocess
pattern = re.compile(
    r'^organic_market_agent/(views|publisher|crop_book/(models|source_registry|field_policy|enrichment_models|importer/(reconciler|enrichment_runner|tend|jmf)|crop_task_templates)|crop_book/importer/(jmf_masterclass|seed))\.py'
    r'|^mu-plugin'
    r'|^organic_market_agent/db/versions/0(0[1-9]|[1-3][0-9]|4[0-3])_'
    r'|^_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec\.md'
)
for sha in ['929c30b', 'd34e60c', '048ce66']:
    out = subprocess.check_output(['git', 'show', '--name-only', '--format=', sha], text=True)
    hits = [line for line in out.splitlines() if pattern.search(line)]
    print(f'{sha}: {hits if hits else "CLEAN"}')
PY

# 4. JMF_CROP_MAP literal final state
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
from collections import Counter
print(f'entries={len(JMF_CROP_MAP)}')
print(f'Rutabaga={JMF_CROP_MAP[\"Rutabaga\"]!r}')
print(f'has_old_brokokoar: {\"ברוקקואר\" in JMF_CROP_MAP.values()}')
print(f'has_Eggplant_Feld: {\"Eggplant  (Feld)\" in JMF_CROP_MAP}')
c = Counter(JMF_CROP_MAP.values())
dups = {v: sorted([k for k, mv in JMF_CROP_MAP.items() if mv == v]) for v, cnt in c.items() if cnt > 1}
print(f'dup_count={len(dups)}')
"

# 5. Cross-engine attestation
git log --format='%h %an %s' c1b14c5..048ce66

# 6. AC-13 regression
pytest tests/crop_book/test_jmf_ex_override_regression.py -v

# 7. Full crop_book suite
pytest tests/crop_book/ -q
```

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD500-VERDICT_v1.0.0.md`**

(`LOD500-VERDICT` prefix because PASS transitions WP to `lod_status: LOD500_LOCKED`.)

Use the 7-section unified verdict template.

**Required dispositions in your §6:**
- VV-1..VV-20 per-criterion result
- 2 out-of-scope governance sync commits acknowledged as constitutionally clean and not affecting verdict
- Pre-existing publisher test failure acknowledged as out-of-scope (predates patch01; LOD500_LOCKED file)

**Decision criteria:**
- **PASS** → team_110 proceeds to Phase 7 (ADR042 closure → `status: DONE`, `lod_status: LOD500_LOCKED`, archive manifest) + Phase 8 (COMPLETION_REPORT).
- **PASS_WITH_FINDINGS (0 blockers)** → same as PASS.
- **FAIL (≥1 blocker)** → team_110 routes remediation back through team_10.

**Engine:** GPT-5.5 (non-Claude). **Independence:** do NOT read BUILD_REPORT or DISPOSITION until AFTER you've formed your own VV conclusions.

---

## 6. Authorization basis

ADR045 R2 #2; mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_100 NOT in routing chain (per ADR045 R2 #4 — team_100 receives only the final COMPLETION_REPORT for each WP upon LOD500_LOCKED).

---

*L-GATE_V mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Builder closed: team_10 (Claude Sonnet 4.6 sub-agent) — see BUILD_REPORT.*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD500-VERDICT_v1.0.0.md`.*
