---
id: MANDATE_SFA-S003-P002-WP-B1_L-GATE_S_v1.0.2
from: team_110 (AOS Domain Architect — executing under ADR045 EXECUTION_MANDATE)
to: team_190 (Validator — non-Claude per Iron Rule #1)
date: 2026-05-24
type: RESUBMISSION
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Use any non-Claude engine (canonical: GPT-5.5)."
authorization_basis: "ADR045 R2 #2."
spec_under_review: _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
spec_commit: 6fe7d7d
spec_version: v1.1.1
resubmission_round: 3
supersedes: MANDATE_SFA-S003-P002-WP-B1_L-GATE_S_v1.0.1
prior_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.1.md
---

# L-GATE_S Mandate (Resubmission R3) — SFA-S003-P002-WP-B1

This mandate **supersedes** `MANDATE_..._v1.0.1.md` and asks for a fresh
validation of LOD400 **v1.1.1** at commit `6fe7d7d`. Single 1-line spec
change since v1.1.0; F-S-002 fixes carry forward unchanged.

---

## 1. Gate History

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_E | PASS | 2026-05-24 | team_00; commit `f61c1da`. |
| L-GATE_PRE_HANDOFF R1/R2/R3 | PASS/FAIL/PASS | 2026-05-24 | Final PASS at `7c3d7d6`. |
| L-GATE_S R1 | FAIL | 2026-05-24 | Spec v1.0.0 at `91972bc`. 2 BLOCKERS (F-S-001, F-S-002). Verdict `LOD400-VERDICT_v1.0.0.md`. |
| L-GATE_S R2 | FAIL | 2026-05-24 | Spec v1.1.0 at `480df00`. F-S-002 RESOLVED; F-S-001 partial (Summer Squash/Zucchini duplicate target). Verdict `LOD400-VERDICT_v1.0.1.md`. |
| L-GATE_S R3 | (this mandate ↓) | — | Spec **v1.1.1** at `6fe7d7d`. F-S-001 follow-up fix claimed complete. |

---

## 2. Resolved Findings from L-GATE_S R2

| # | Prior Finding | Sev. | Fix Applied in v1.1.1 | Verification Pointer |
|---|---|------|------------------------|----------------------|
| F-S-001 (R2 residual) | `JMF_CROP_MAP` has 52 entries but AC-03's "allow-list ONLY for Mesclun/Salad Mix" wording contradicted the literal, which also mapped Summer Squash and Zucchini to "קישוא". | BLOCKER | §5 literal: changed `"Zucchini": "קישוא"` → `"Zucchini": "זוקיני"` (1 line, the standard Israeli loanword for the specific cultivar group; distinct from "קישוא" which denotes the broader summer-squash category — same convention used by the Tend dataset). AC-03 (§9) rewritten with an explicit Counter-based assertion: the duplicate-target set MUST equal exactly `{"תערובת סלט": ["Mesclun", "Salad Mix"]}`. §5 authoring-note updated to call out the Summer Squash / Zucchini distinction. | LOD400 v1.1.1 §5 (line containing `"Zucchini":`); AC-03 in §9. Probe below confirms the set:

```python
python3 - <<'PY'
import re
text = open('_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md').read()
m = re.search(r'JMF_CROP_MAP: dict\[str, str\] = \{(.+?)^\}', text, re.S | re.M)
entries = re.findall(r'^\s*"([^"]+)":\s+"([^"]+)",', m.group(1), re.M)
from collections import Counter
c = Counter(v for _, v in entries)
dups = {v: [k for k, mv in entries if mv == v] for v, cnt in c.items() if cnt > 1}
print(f'entries={len(entries)} dups={dups}')
PY
```

Expected output: `entries=52 dups={'תערובת סלט': ['Mesclun', 'Salad Mix']}` |

F-S-002 was RESOLVED in v1.1.0 per the R2 verdict — no changes needed in v1.1.1.

---

## 3. Scope

Re-validate LOD400 v1.1.1 at commit `6fe7d7d`. The diff from v1.1.0 is a
**single 1-line change** plus an AC-03 wording tightening + §5 authoring
note + frontmatter version/changelog. Full diff:

```bash
git diff 480df00 6fe7d7d -- _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
```

(+39 / −14 lines, scoped exclusively to F-S-001 residual.)

Re-run the same 20 VCs from `MANDATE_..._v1.0.0.md` §3 plus the 4
R2-specific evidence sub-checks from `MANDATE_..._v1.0.1.md` §4. Add:

- **VC-15.5 (R3)** — Hebrew-value duplicate set verification. Run the
  Python probe above; output MUST be exactly:
  `entries=52 dups={'תערובת סלט': ['Mesclun', 'Salad Mix']}`

Independence rule still applies. Do NOT re-read R1/R2 verdicts before
forming VC-15 conclusions.

---

## 4. Output Format

Write your verdict to:
**`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`**

Decision criteria as before:

- **PASS** → team_110 proceeds to Phase 4 (roadmap transition:
  `lod_status: LOD200_LOCKED → LOD400_LOCKED`, `current_lean_gate:
  L-GATE_E → L-GATE_B`).
- **PASS_WITH_FINDINGS (0 blockers)** → same as PASS; carry findings to
  BUILD_REPORT.
- **FAIL (≥ 1 blocker)** → team_110 remediates + R4.

Engine constraint: validator MUST differ from author (Claude Opus 4.7).
Canonical non-Claude: GPT-5.5.

---

## 5. Authorization basis

ADR045 R2 #2; mandate root
`_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md`
(R3 PASS at `7c3d7d6`).

team_100 NOT in routing chain.

---

*Resubmission mandate issued 2026-05-24 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`.*
