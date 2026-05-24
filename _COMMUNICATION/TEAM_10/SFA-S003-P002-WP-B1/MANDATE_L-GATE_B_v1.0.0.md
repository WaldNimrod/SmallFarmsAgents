---
id: MANDATE_SFA-S003-P002-WP-B1_L-GATE_B_v1.0.0
from: team_110 (AOS Domain Architect — executing under ADR045 EXECUTION_MANDATE)
to: team_10 (sfa_build — Builder — separate session per IR#1)
date: 2026-05-24
type: GATE_MANDATE
gate: L-GATE_B
wp: SFA-S003-P002-WP-B1
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — builder engine MUST differ from team_190 (the validator). team_190 = GPT-5.5 (canonical). Builder = any non-GPT-5.5 engine. Recommended: Claude Code in a SEPARATE session from team_110 (the orchestrator). team_110 itself MUST NOT run the build per ADR045 §8 (orchestrator/builder separation)."
authorization_basis: "ADR045 R2 #2 — team_110 may independently issue mandates to team_10 during execution_authority: full mandate. Mandate root: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
spec_version: v1.1.3
spec_commit: "262d9a3"   # the LOCK commit (combines R3 PASS + v1.1.3 cleanup + roadmap transition)
lgate_s_verdict_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md
---

# L-GATE_B Mandate — SFA-S003-P002-WP-B1

**ספר גידולים: JMF Excel Base Layer — Multi-Source Knowledge Foundation**
**Track:** A | **Profile:** L0 | **Effort:** LARGE | **Risk:** MEDIUM

---

## 1. Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00 | Commit `f61c1da`. |
| L-GATE_PRE_HANDOFF R1/R2/R3 | PASS/FAIL/PASS | 2026-05-24 | team_190 (GPT-5.5) | Final PASS `7c3d7d6`. |
| L-GATE_S R1 / R2 / R3 | FAIL / FAIL / **PASS_WITH_FINDINGS** | 2026-05-24 | team_190 (GPT-5.5) | LOD400 v1.1.2 at commit `3c92a67`. 20/20 VCs PASS; 0 BLOCKER; 0 MAJOR; 2 MINOR (CARRY, addressed in v1.1.3 cleanup at commit `262d9a3`). Verdict: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`. |
| L-GATE_B | (this mandate ↓) | — | team_10 | LOD400 v1.1.3 LOCKED. Build now authorized. |

---

## 2. Scope

Implement LOD400 v1.1.3 in full. The spec is **detailed enough that you
should not need to make architectural judgement calls.** If you find an
implementation question the spec does not unambiguously answer, STOP and
file an inquiry MSG back to team_110 — do NOT improvise.

The spec specifies a 10-step build sequence at §11. Follow it exactly:

1. Read LOD400 + LOD200 + PROGRAM_BRIEF.
2. Create `crop_task_templates.py` ORM module.
3. Create migration 044.
4. Append `JMF_CROP_MAP` (52 entries) **verbatim** from spec §5.
5. Create `jmf_masterclass.py` parsers.
6. Add unit-conversion helpers.
7. Add `import_jmf_masterclass` orchestrator + upsert helpers.
8. Wire seed.py CLI flags.
9. Write `test_jmf_ex_override_regression.py` (the most critical
   regression test — AC-13 proves WP-A engine reuse is correctly wired).
10. Run pytest + validate_aos.sh + write BUILD_REPORT.

---

## 3. Acceptance Criteria

Spec §9 (LOD400 v1.1.3) defines **22 ACs** (AC-01 through AC-22, with
AC-15 split a/b/c and AC-16 split a/b). All must pass for L-GATE_B
verdict. The L-GATE_S verdict has identified them as objectively
measurable (VC-16 PASS).

The most critical ACs:

- **AC-13** — ARUGULA EX-override regression. After both WP-A `--all`
  and `import_jmf_masterclass`, `crop_field_enrichment` for
  ARUGULA / days_to_maturity MUST have `value_best == Decimal("21")` and
  `winning_source_class == "EX"`. This proves engine reuse end-to-end.
- **AC-15a/b/c** — UNIQUE constraint on `crop_task_templates` (real
  offset, presence-only sentinel, NULL rejection). AC-15b is the
  F-S-002 R1 regression assertion — non-negotiable.
- **AC-22** — No LOD500_LOCKED file modified (the inventory is at §14).

---

## 4. LOD500_LOCKED files (DO NOT modify)

See spec §14 for the authoritative list. Headline items:

- `organic_market_agent/views.py`
- `organic_market_agent/publisher/wp_upload.py`
- `organic_market_agent/publisher/upload_dispatch.py`
- `organic_market_agent/db/versions/001..043_*.py` (all prior migrations)
- `mu-plugin/`
- `organic_market_agent/crop_book/importer/tend.py` (raw-material guard)
- `organic_market_agent/crop_book/models.py` (no GCR for B1)
- All WP-A engine SSoT modules (`source_registry.py`, `field_policy.py`,
  `reconciler.py`, `enrichment_runner.py`, `enrichment_models.py`).

Permitted modifications (additive only): `constants.py` (append
`JMF_CROP_MAP` after `OUTLIER_CROPS`), `seed.py` (3 new CLI flags + 1
new call-site block), `CHANGELOG.md`.

---

## 5. Required Files to Read FIRST

1. Spec under build: `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` (v1.1.3 at commit `262d9a3`)
2. LOD200: `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD200_spec.md`
3. Program brief: `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md`
4. L-GATE_S R3 verdict (contains 2 MINOR CARRY notes you should
   acknowledge in BUILD_REPORT): `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`
5. WP-A LOD400 (structural reference for similar patterns):
   `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md`
6. WP-A locked engine SSoT (read-only):
   - `organic_market_agent/crop_book/source_registry.py`
   - `organic_market_agent/crop_book/field_policy.py`
   - `organic_market_agent/crop_book/importer/reconciler.py` (note
     `Candidate` / `FieldConsensus` dataclasses + `reconcile_field()`)
   - `organic_market_agent/crop_book/importer/enrichment_runner.py`
   - `organic_market_agent/crop_book/models.py` (`CropVarietySourceValue`)

---

## 6. Iron Rule constraints

- **IR#1 (cross-engine separation):** YOU (sfa_build, team_10) MUST run
  in a session whose engine differs from team_190 (GPT-5.5). Canonical
  builder engine: Claude Code (in a SEPARATE session from team_110 — do
  not piggyback on team_110's session). team_110 has been authoring
  specs as Claude Opus 4.7; you should run as Claude Code (Sonnet or
  Opus) in a fresh session. **Critical:** team_110 MUST NOT run this
  build itself per ADR045 §8.
- **IR#4 (roadmap):** You MUST NOT commit any change to
  `_aos/roadmap.yaml`. Lifecycle field updates are team_110's
  responsibility (Phase 7 closure).
- **IR#5 (validation):** L-GATE_V (the constitutional validation of
  your build) is team_190's responsibility, not yours.
- **IR#6 (communication):** Your BUILD_REPORT and any
  inquiry/remediation MSGs go in `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/`.
- **IR#11 (governance untouched):** Never write to `_aos/governance/`,
  `_aos/lean-kit/`, or `_aos/project_identity.yaml`.

---

## 7. Output Format — BUILD_REPORT

Write your report to:
**`_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/BUILD_REPORT_v1.0.0.md`**

Required contents:

1. **Verdict summary** — BUILD_COMPLETE / BUILD_INCOMPLETE / BLOCKED.
2. **Per-AC table** — AC-01 through AC-22 with PASS/FAIL + evidence
   (test output, count, command).
3. **Test execution evidence** — full `pytest tests/crop_book/ -q`
   output (post-build); total test count vs ≥ 140 expected (115 baseline + 25 new).
4. **AOS validation evidence** — full `validate_aos.sh` output; expect
   29 PASS / 17 SKIP / 0 FAIL.
5. **LOD500_LOCKED audit** — `git diff 262d9a3..HEAD -- <each locked path>`
   for every path in spec §14, with confirmation each diff is empty.
6. **Files touched** — `git diff --name-only 262d9a3..HEAD` with
   classification (CREATE / MODIFY / per spec §15).
7. **MINOR CARRY acknowledgments** — per the L-GATE_S verdict, two
   findings carry: F-S-002-MINOR-R3 (already addressed in v1.1.3
   spec cleanup) and F-S-003-MINOR-R3 (same). Confirm your build is
   consistent with the corrected wording in v1.1.3 (i.e., parser uses
   the sentinel, never NULL).
8. **Runtime stats from full import** — on the live JMF MasterClass
   workbook: crops_seen, source_value_rows_upserted,
   task_template_rows_upserted, map_misses, standalone_divergences,
   invalid_offsets. Include the `JmfImportSummary` repr.
9. **Open questions / blockers** — if any. Otherwise: "None — ready
   for L-GATE_V."

### Decision criteria

- **BUILD_COMPLETE** → all 22 ACs PASS; pytest green; validate_aos.sh
  green; LOD500_LOCKED audit empty. team_110 then files L-GATE_V to
  team_190.
- **BUILD_INCOMPLETE** → some ACs not yet PASS; team_10 continues work
  (no team_110 mandate cycle).
- **BLOCKED** → spec ambiguity, missing dependency, or other architectural
  question that needs team_110 intervention. File inquiry MSG to
  team_110 at `_COMMUNICATION/team_110/SFA-S003-P002-WP-B1/`.

### Engine constraint reminder

You are running in a session that MUST be distinct from team_110's. If
you find yourself BEING team_110 (i.e., the orchestrator session ran
this build), STOP immediately — that violates ADR045 §8.

---

## 8. Authorization basis

ADR045 R2 #2 — team_110 may independently mandate sfa_build during
`execution_authority: full` mandate. Mandate root:
`_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`
(R3 PASS at `7c3d7d6`).

team_100 is NOT in the routing chain for this mandate per ADR045 R2 #4.

---

*Mandate issued 2026-05-24 by team_110 (Claude Opus 4.7) under
EXECUTION_MANDATE SFA-S003-P002-WP-B.*
*Builder: sfa_build (team_10) — separate non-GPT-5.5 session.*
*Awaiting BUILD_REPORT at `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/BUILD_REPORT_v1.0.0.md`.*
