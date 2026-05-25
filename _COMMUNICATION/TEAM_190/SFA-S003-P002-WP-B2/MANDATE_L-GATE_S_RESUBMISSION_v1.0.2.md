---
id: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.2
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: RESUBMISSION
gate: L-GATE_S
wp: SFA-S003-P002-WP-B2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2."
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
spec_version: v1.1.1
resubmission_round: 3
supersedes: MANDATE_SFA-S003-P002-WP-B2_L-GATE_S_v1.0.1
prior_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.1.md
---

# L-GATE_S Mandate (R3) — SFA-S003-P002-WP-B2

Supersedes `MANDATE_..._v1.0.1`. Validate LOD400 **v1.1.1** — all 3 R2 BLOCKERS addressed.

---

## 1. Resolved Findings from R2

| # | Prior Finding | Sev. | Fix Applied in v1.1.1 |
|---|---|------|------------------------|
| **B1 / VC-6.R2** | Stale obsolete-class-name token still in spec body (lines 15/59/486) despite R2 probe expecting absence. | BLOCKER | All 3 mentions rewritten to avoid the literal token. Changelog § narrates the prior bug without naming the class. "Read before writing" item 4 and §7 intro affirm the correct class (`NIImporter`) without negating an alternate name. Probe `grep -c "NiSourceBase" ...` returns **0**. |
| **B2 / VC-15/17** | Architectural defect: B2 subclasses returned rows tagged `_resolution_crop_jmf_en` with no `variety_id`; `ni_registry.load_all()` calls `validate()` which drops such rows. End-to-end flow produces 0 NI rows. | BLOCKER | **Architectural fix:** B2 bypasses `ni_registry.load_all()`. §7.1 docstring explicitly documents the deviation rationale. B2 subclasses are NOT registered with `ni_registry`; seed.py iterates `NI_IMPORTER_CLASSES` directly with session. Subclass `load(self, session)` and `load_knowledge_notes(self, session)` accept session and return **fully-resolved rows** with `variety_id` / `crop_id` already populated. Resolution helpers (`_resolve_crop_id`, `_resolve_default_variety_id`) live in subclasses (mirrors B1 patterns). seed.py call-site simplified — no helper-functions-on-seed.py side. |
| **B3 / VC-16** | Publication prohibition was in advisory table only; no operative spec section actually banned public display. | BLOCKER | **NEW §3.1 "Display boundary — OPERATIVE LICENSING INVARIANT"** declares 4 binding prohibitions: no publisher read, no upload payload, no public WordPress view, admin/test-only DB access. §3.1.3 elevation rationale documented. NEW AC-21 (a/b/c) enforces via `git diff` audit + 2 publisher-isolation test assertions. New test file `test_ni_publisher_isolation.py` added to §10. |

---

## 2. Scope

Re-validate LOD400 v1.1.1. The diff from v1.1.0 is scoped to the 3 BLOCKER fixes above:

```bash
git diff fa11662 <new-head> -- _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
```

Q1 (text-file input) and Q5 (6 sources) scope changes from team_00 DECISION 2026-05-25 carry forward unchanged from v1.1.0.

Independence rule: do NOT read the R2 verdict before forming R3 conclusions. The R2 verdict is referenced in §1 above ONLY as fix-traceability evidence.

---

## 3. R3-specific evidence checks (4 probes — 1 per BLOCKER + 1 cumulative)

```bash
# 1. B1 fix — stale token absent
python3 -c "
content = open('_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md').read()
print('No NiSourceBase in spec:', 'NiSourceBase' not in content)
"
# Expected: No NiSourceBase in spec: True

# 2. B2 fix — bypass of ni_registry.load_all() documented
grep -nE "B2 bypasses|NOT registered with ni_registry|do(es)? NOT call ni_registry\.register" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md | head -5
# Expected: ≥3 hits in §7.1 + §8 indicating the architectural deviation.

# 3. B3 fix — operative licensing section + AC-21 enforcement present
grep -nE "## 3\.1 Display boundary|OPERATIVE LICENSING INVARIANT|AC-21" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md | head -10
# Expected: ≥4 hits: §3.1 header, "OPERATIVE LICENSING INVARIANT", AC-21a/b/c.

# 4. Cumulative — no regression on prior R2 evidence checks
grep -c "NIImporter" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
grep -c "data/jmf/raw_text" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
grep -c "jmf_book_alt\|jmf_ft_phytoprotection\|jmf_ft_nurseryseeding" _aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md
# Expected: NIImporter ≥15; data/jmf/raw_text ≥10; Q5 source identifiers ≥20.
```

---

## 4. Validation criteria

Re-run all 20 VCs from the original mandate. VC-3 (`_upsert_source_value` signature) + VC-6 (NIImporter correctness) + VC-15/17 (engine-reuse path) + VC-16 (licensing operative) should now PASS.

---

## 5. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.2.md`**

Commit with:
```
gate(WP-B2/L-GATE_S): team_190 R3 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

**Decision criteria:**
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 4 (roadmap transition) + Phase 5 (L-GATE_B mandate + spawn Sonnet builder)
- **FAIL (≥1 blocker)** → team_110 remediates + R4

---

## 6. Authorization basis

ADR045 R2 #2. Mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`. team_00 DECISION (Q1+Q5) at `_COMMUNICATION/team_00/DECISION_WP-B-OPEN-QUESTIONS_2026-05-25_v1.0.0.md`. team_100 NOT in routing chain.

---

*R3 resubmission mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B2/LOD400-VERDICT_v1.0.2.md`.*
