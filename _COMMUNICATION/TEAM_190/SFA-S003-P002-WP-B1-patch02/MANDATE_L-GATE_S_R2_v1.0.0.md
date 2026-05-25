---
id: MANDATE_SFA-S003-P002-WP-B1-patch02_L-GATE_S_R2_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch02
round: R2
correction_cycle: R2
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch02/LOD400-VERDICT_v1.0.0.md
prior_round_result: FAIL (1 BLOCKER F-S-PATCH02-01)
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch02/LOD400_spec.md
spec_version: v1.0.1
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
---

# L-GATE_S R2 Mandate — SFA-S003-P002-WP-B1-patch02

## 1. R1 Disposition

R1 returned **FAIL** with 1 BLOCKER (F-S-PATCH02-01) on VC-9.

R1's finding was correct: LOD400 v1.0.0 §3.4 and §4 AC-04 incorrectly described the AC-03 duplicate-target assertion as the old 2-pair WP-B1 baseline (`תערובת סלט` + `קישוא` only), while the current LOD500_LOCKED post-patch01 state has 25 duplicate-target groups asserted across two tests (`test_jmf_crop_map_duplicate_target_allowlist` + `test_ac03_duplicate_group_count`).

All other 14 VCs PASSED in R1, including the single-engine builder rationale (VC-6) and the Hebrew value strings (VC-7, VC-8).

## 2. R2 Changes (LOD400 v1.0.0 → v1.0.1)

Exactly three localized edits — NO change to Hebrew values, builder rationale, scope, or any other AC:

1. **§3.4 rewritten** — now says: existing 25-group duplicate-target allowlist (per patch01 LOD400 v1.0.3 §4 AC-03) is preserved; cites the two existing test names (`test_jmf_crop_map_duplicate_target_allowlist` line ~37, `test_ac03_duplicate_group_count` line ~142); explicitly states neither Parsnips nor Shallots collides with any existing Hebrew value in either old or new map.
2. **AC-04 rewritten** — now asserts the 25-group baseline (membership + count) is unchanged, NOT a 2-pair dict.
3. **Footer changelog appended** — records v1.0.1 R2 correction provenance.

No edit to LOD200, mandate text outside this VC, or any other LOD400 section.

## 3. VC-9 (R2 — REVISED)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-9 | **AC-03 duplicate-target allowlist regression — 25 groups UNCHANGED** | LOD400 v1.0.1 §3.4 + §4 AC-04 must:<br/>(a) reference the **25-group** duplicate-target allowlist as the post-patch01 baseline (not 2 pairs)<br/>(b) cite the existing test names (`test_jmf_crop_map_duplicate_target_allowlist` + `test_ac03_duplicate_group_count`) as the unchanged regression coverage<br/>(c) confirm Parsnips and Shallots are OUTSIDE all duplicate groups in both pre- and post-patch02 maps<br/>Independent probe expected: `python3 -c "from organic_market_agent.crop_book.constants import JMF_CROP_MAP; from collections import Counter; print(len({v for v,c in Counter(JMF_CROP_MAP.values()).items() if c>1}))"` returns `25`. |

## 4. Carry-forward VCs (unchanged from R1; all PASSED)

VC-1, VC-2, VC-3, VC-4, VC-5, VC-6, VC-7, VC-8, VC-10, VC-11, VC-12, VC-13, VC-14, VC-15 — all PASSED in R1. Confirm by spot-check that nothing in v1.0.1 regressed them (only §3.4, AC-04, version-field, and footer changed).

**Total: 15 VCs** (same shape as R1).

## 5. Required Commands (R2 — minimal delta from R1)

```bash
# 1. Confirm spec version bumped
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch02/LOD400_spec.md
# Expected: version: v1.0.1

# 2. Confirm §3.4 cites 25 groups + the two test names
grep -E "25.group|test_jmf_crop_map_duplicate_target_allowlist|test_ac03_duplicate_group_count" \
  _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch02/LOD400_spec.md

# 3. Independent duplicate probe
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
from collections import Counter
c = Counter(JMF_CROP_MAP.values())
dups = {v: sorted(k for k,mv in JMF_CROP_MAP.items() if mv==v) for v,n in c.items() if n>1}
print(f'duplicate groups: {len(dups)}')
print(f'Parsnips in dups? {\"גזר לבן\" in dups or \"שורש פטרוזילה\" in dups}')
print(f'Shallots in dups? {\"שאלוט\" in dups or \"בצלצלי שאלוט\" in dups}')
"
# Expected: duplicate groups: 25 / Parsnips in dups? False / Shallots in dups? False

# 4. validate_aos.sh (carry-forward)
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 6. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch02/LOD400-VERDICT_R2_v1.0.0.md`**

Commit with:
```
gate(WP-B1-patch02/L-GATE_S R2): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision:
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 proceeds to Phase 4 + Phase 5 (single-engine build) + Phase 6 (L-GATE_V mandate)
- **FAIL (≥1 blocker)** → R3

## 7. Authorization basis

Same as R1 — ADR045 R2 #2; team_00 DECISION 2026-05-25 §Q4 + sequencing directive.

---

*L-GATE_S R2 mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch02/LOD400-VERDICT_R2_v1.0.0.md`.*
