---
id: MANDATE_SFA-S003-P002-WP-B1-patch01_L-GATE_B_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_10 (sfa_build — Builder — separate session per IR#1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-B1-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — builder engine MUST differ from team_190 (GPT-5.5). Recommended: Claude Code (Sonnet) in a SEPARATE session from team_110 (Claude Opus 4.7). team_110 MUST NOT run the build per ADR045 §8."
authorization_basis: "ADR045 R2 #2 — team_110 may independently mandate sfa_build during execution_authority: full mandate. Same mandate root as parent WP-B1."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md
spec_version: v1.0.3
spec_commit_lock: "TBD"   # the LOD400_LOCKED commit that bundles v1.0.3 cleanup + roadmap transition + this mandate; team_110 will rewrite this field in the BUILD_REPORT cross-reference.
parent_wp_lod500_commit: "6a85561"
lgate_s_r3_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD400-VERDICT_v1.0.2.md
---

# L-GATE_B Mandate — SFA-S003-P002-WP-B1-patch01

**ספר גידולים: JMF_CROP_MAP alias extension + Rutabaga Hebrew correction**
**Track:** A | **Profile:** L0 | **Effort:** SMALL | **Risk:** LOW

---

## 1. Gate History

| Gate | Result | Validator |
|------|--------|-----------|
| L-GATE_E | PASS | team_00 (2026-05-25 in-session) |
| L-GATE_S R1/R2/R3 | FAIL/FAIL/**PASS_WITH_FINDINGS** | team_190 (GPT-5.5). LOD400 v1.0.3 LOCKED. |
| L-GATE_B | (this mandate ↓) | team_10 |

---

## 2. Scope

Implement LOD400 v1.0.3 — a SMALL literal-map patch. Follow the 4-step build sequence at §6 of the spec exactly.

**Total estimated change footprint:**
- **1 file edit** (`organic_market_agent/crop_book/constants.py`):
  - `"Rutabaga"` value changed from `"ברוקקואר"` to `"רוטבגה"`
  - 34 alias entries appended after `OUTLIER_CROPS` section (verbatim from spec §3.2)
  - Result: `len(JMF_CROP_MAP) == 86`
- **2 file edits** (`tests/crop_book/test_jmf_crop_map.py` extend; `CHANGELOG.md` append)
- **3 new test files** (alias spot-checks, live-workbook coverage, seed dry-run smoke)

LOD400 spec is junior-dev-buildable. **If you find any ambiguity, STOP and file an inquiry MSG to team_110** at `_COMMUNICATION/team_110/SFA-S003-P002-WP-B1-patch01/`. Do NOT improvise on spec gaps.

---

## 3. Acceptance Criteria

Spec §4 defines **8 ACs** (AC-01..AC-08, with AC-04.1 as an integrated sub-AC). All must pass for L-GATE_B verdict.

Most critical:

- **AC-01** — `len(JMF_CROP_MAP) == 86` (NOT 85, NOT 87 — exactly 86)
- **AC-02** — `JMF_CROP_MAP["Rutabaga"] == "רוטבגה"` AND no `"ברוקקואר"` anywhere in `constants.py`
- **AC-03** — Counter assertion enumerates exactly the 25 by-design duplicate pairs/groups (spec §4 AC-03 has the literal Python `assert` block — copy-paste into the test)
- **AC-04** — Live-workbook coverage ≥ 42/50
- **AC-05** — All 56 prior WP-B1 tests still PASS (regression — no breakage)

---

## 4. LOD500_LOCKED files (DO NOT modify)

See spec §7 for the authoritative list. Headline items (anything outside this is OK to read; only constants.py + 2 test/changelog files are OK to edit):

- All B1 deliverables: `crop_task_templates.py`, `jmf_masterclass.py`, migration 044, `seed.py`
- WP-A engine SSoT: `source_registry.py`, `field_policy.py`, `reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`, `models.py`
- Raw material: `tend.py`
- WP-B1 LOD400 spec: `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`
- All prior migrations 001..043
- Publisher / views / mu-plugin

**Permitted edits — only 3 existing files:**
- `organic_market_agent/crop_book/constants.py` — JMF_CROP_MAP literal only
- `tests/crop_book/test_jmf_crop_map.py` — AC-03 assertion update + AC-01/AC-02 expected values updated
- `CHANGELOG.md` — `[Unreleased]` append

**Permitted new files:**
- `tests/crop_book/test_jmf_crop_map_aliases.py`
- `tests/crop_book/test_jmf_live_workbook_coverage.py`
- `tests/crop_book/test_jmf_seed_dry_run.py`
- `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md`

---

## 5. Required Files to Read FIRST

1. **This mandate** (you're reading it)
2. **LOD400 v1.0.3** (the spec): `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md`
3. **L-GATE_S R3 verdict** (1 MINOR carry — already addressed in v1.0.3 cleanup): `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD400-VERDICT_v1.0.2.md`
4. **Current `JMF_CROP_MAP` state** (post-WP-B1 build): `organic_market_agent/crop_book/constants.py`
5. **Existing tests** (pattern reference): `tests/crop_book/test_jmf_crop_map.py`

---

## 6. Iron Rule constraints

- **IR#1** — Your engine (Sonnet recommended) ≠ team_190 (GPT-5.5). team_110 (Opus 4.7) is the orchestrator — DO NOT run this build in team_110's session.
- **IR#4** — You MUST NOT touch `_aos/roadmap.yaml`. team_110 handles lifecycle in Phase 7.
- **IR#5** — L-GATE_V is team_190's; don't validate your own build.
- **IR#6** — BUILD_REPORT + any inquiries go in `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/`.
- **IR#11** — Never touch `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`.

---

## 7. Commit policy

Make separate commits per build step (Steps 2/3/4 per spec §6). Conventional prefix: `build(WP-B1-patch01/...)`. After each commit, run `validate_aos.sh` and confirm `29 PASS / 17 SKIP / 0 FAIL`. End every commit message with:

```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

(Adjust Sonnet version to match your actual model.)

---

## 8. Output — BUILD_REPORT

Write to: **`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md`**

Required sections (per the WP-B1 BUILD_REPORT pattern):
1. Verdict summary (BUILD_COMPLETE / BUILD_INCOMPLETE / BLOCKED)
2. Per-AC table (AC-01..AC-08 + AC-04.1) with PASS/FAIL + evidence
3. Test execution evidence (pytest tail; new ≥10 tests; ≥56 WP-B1 tests still PASS)
4. AOS validation evidence (validate_aos.sh tail — must be 29/17/0)
5. LOD500_LOCKED audit — `git diff <patch01-lock-commit>..HEAD -- <each locked path>` empty
6. Files touched — `git diff --name-only <patch01-lock-commit>..HEAD`
7. Live-workbook coverage — actual count of mapped crops from running the parser
8. Open questions / blockers (or "None — ready for L-GATE_V")

When done, your final agent response should be ≤ 200 words and include:
- BUILD_COMPLETE / not
- Commit hash range produced
- Test counts
- BUILD_REPORT path
- Any inquiries filed

---

## 9. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_100 NOT in routing chain.

---

*Mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Builder: sfa_build (Claude Sonnet sub-agent — separate session per IR#1).*
*Awaiting BUILD_REPORT at `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1-patch01/BUILD_REPORT_v1.0.0.md`.*
