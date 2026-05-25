---
id: MANDATE_SFA-S003-P002-WP-B1-patch03_L-GATE_S_R4_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch03
round: R4
status: ACTIVE
verdict: PENDING
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch03/LOD400-VERDICT_R3_v1.0.0.md
prior_round_result: FAIL (1 BLOCKER F-S-PATCH03-R3-01 + 1 MINOR F-S-PATCH03-R3-02)
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md
spec_version: v1.0.3
engine_constraint: "Iron Rule #1 — non-Claude. GPT-5.5."
---

# L-GATE_S R4 Mandate — SFA-S003-P002-WP-B1-patch03

## 1. R3 Disposition

R3 verdict: **FAIL** with 1 BLOCKER + 1 MINOR. Both findings correct — pure spec-internal inconsistency between the R3-amended sections (§2.1/§2.2/§3.4b/§4 AC-18/§5/§6) and the un-amended §9/§10/AC-16/§3.5 CHANGELOG sections.

## 2. R4 Changes (v1.0.2 → v1.0.3) — mechanical cleanup only

| Section | Change |
|---------|--------|
| **§9 LOD500_LOCKED file inventory** | Updated from 2 functions in 1 file → 4 functions across 2 files. Explicitly lists all 4 functions + notes the 3rd alias-file function is NOT modified. |
| **§10 MODIFY list** | "3 existing files" → "4 existing files"; added `tests/crop_book/test_jmf_crop_map_aliases.py` row. |
| **§3.5 CHANGELOG template** | "2 test functions updated" → "4 test functions across 2 files updated (amended)". |
| **AC-16 parenthetical** | "2 LOCKED test updates absorb in place" → "4 LOCKED test updates across 2 files absorb in place — 2 in test_jmf_crop_map.py, 2 in test_jmf_crop_map_aliases.py". |
| **Footer changelog** | v1.0.3 R4 entry appended. |

No change to: architecture, Hebrew values, §3.2 24-group dict, 11 per-value ACs (AC-01..AC-11), AC-12..AC-15, AC-17, AC-18 file list, §3.4b alias-file edits, builder identity, risk register, or any other section.

## 3. Validation Criteria (R4 — focused on internal consistency)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-R4-1 | **Spec version bumped** | `version: v1.0.3` in frontmatter. |
| VC-R4-2 | **§9 fully reflects 4-function/2-file scope** | §9 lists all 4 functions (Cherry Tomato spot-check + 24-group rename in aliases file + duplicate_target_allowlist + ac03_duplicate_group_count). Explicitly notes the 3rd alias-file function is NOT modified. |
| VC-R4-3 | **§10 MODIFY list = 4 files** | §10 lists exactly 4 modified files: constants.py, test_jmf_crop_map.py, **test_jmf_crop_map_aliases.py**, CHANGELOG.md. Heading text says "4 existing files". |
| VC-R4-4 | **§3.5 CHANGELOG bullet updated** | "4 test functions across 2 files" appears in §3.5 (replacing "2 test functions"). |
| VC-R4-5 | **AC-16 parenthetical updated** | AC-16 mentions "4 LOCKED test updates across 2 files" — explicit "2 in test_jmf_crop_map.py, 2 in test_jmf_crop_map_aliases.py". |
| VC-R4-6 | **No regression in R3-passing sections** | §2.1 still lists 4 files; §2.2 still lists 4 functions; §3.4b unchanged; AC-18 still lists test_jmf_crop_map_aliases.py; §6 still has Step 3b. |
| VC-R4-7 | **No architecture/value drift** | §3.1 (11 value edits), §3.2 (24-group dict), §3.4 (11 new tests), §11 (builder identity = team_10 Sonnet) all unchanged from v1.0.2. |
| VC-R4-8 | **validate_aos.sh clean** | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL. |

## 4. Required Commands

```bash
# 1. Version bump
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md
# Expected: version: v1.0.3

# 2. §9 4-function listing
sed -n '/^## 9\. /,/^## 10\./p' _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md

# 3. §10 4-file MODIFY list
sed -n '/^## 10\. /,/^## 11\./p' _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md

# 4. §3.5 CHANGELOG bullet
grep -E "4 test functions across 2 files|2 test functions updated" \
  _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md

# 5. AC-16 update
grep -A1 "^- \*\*AC-16\*\*" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md

# 6. Carry-forward sanity
grep -c "test_jmf_crop_map_aliases.py" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md
# Expected: ≥ 5 occurrences (§2.1, §2.2, §3.4b, §4 AC-18, §9, §10)

# 7. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 5. Output

Write verdict to: `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch03/LOD400-VERDICT_R4_v1.0.0.md`

Commit: `gate(WP-B1-patch03/L-GATE_S R4): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 re-dispatches Sonnet
- **FAIL** → R5

## 6. Authorization basis

Same as R3 (ADR045 R2 #2; team_00 "יש לתקן את הממצאים ולהתקדם" in-session sequencing directive).

---

*L-GATE_S R4 mandate issued 2026-05-25 by team_110.*
