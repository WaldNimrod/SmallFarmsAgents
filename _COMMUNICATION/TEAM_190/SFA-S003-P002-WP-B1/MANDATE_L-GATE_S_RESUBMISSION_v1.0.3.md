---
id: MANDATE_SFA-S003-P002-WP-B1_L-GATE_S_v1.0.3
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
spec_commit: 3c92a67
spec_version: v1.1.2
resubmission_round: 3
supersedes: MANDATE_SFA-S003-P002-WP-B1_L-GATE_S_v1.0.2
withdrawn: "MANDATE_..._v1.0.2 referenced LOD400 v1.1.1 (commit 6fe7d7d), which has been superseded by v1.1.2 (commit 3c92a67) following a team_00 botanical correction. Validate against v1.1.2 only."
prior_verdict: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.1.md
---

# L-GATE_S Mandate (Resubmission R3 — re-issued) — SFA-S003-P002-WP-B1

This mandate **supersedes and withdraws** `MANDATE_..._v1.0.2.md` (which
pointed at LOD400 v1.1.1). Validate against LOD400 **v1.1.2** at commit
`3c92a67`.

---

## 1. Why v1.0.2 is withdrawn

The v1.0.2 R3 mandate (commit `ebc47de`) asked you to re-validate
LOD400 v1.1.1, in which `Zucchini` was disambiguated from `Summer
Squash` to remove an "unintended duplicate Hebrew target." On post-issue
review by team_00, this was identified as a **botanical category error**:

- **קישוא** is the species (`Cucurbita pepo` in its market-garden sense).
- **זוקיני** is a *cultivar group* (zucchini-form) of קישוא, not a
  separate species.

In the spoke's schema, species-level identity lives in `crops.name_he`;
cultivar-level identity lives in `crop_varieties` (populated by the JMF
CULTIVARS sheet per LOD400 §6.7). Splitting Zucchini into its own
`crops.name_he` row would create an incorrect taxonomy where one
`Cucurbita pepo` species appears as two distinct `crops` rows.

Therefore the v1.1.1 split has been reverted, and v1.1.2 instead widens
AC-03's duplicate-target allow-list to include the legitimate
species-level pair `{Summer Squash, Zucchini} → "קישוא"`.

---

## 2. Resolved Findings from L-GATE_S R2 (final state in v1.1.2)

| # | Prior Finding | Sev. | Fix in v1.1.2 | Verification |
|---|---|------|----------------|---------------|
| F-S-002 | Nullable `days_offset` UNIQUE hole. | BLOCKER | RESOLVED in v1.1.0 (carried forward unchanged through v1.1.1, v1.1.2). | LOD400 §3 DDL, §4 ORM (`nullable=False` + sentinel), AC-15a/b/c, AC-16b. |
| F-S-001 (R2 residual) | AC-03 declared "duplicate Hebrew targets allowed ONLY for Mesclun/Salad Mix" but the literal also mapped Summer Squash AND Zucchini to "קישוא". | BLOCKER | RESOLVED via expansion (not via disambiguation). AC-03 allow-list now contains exactly **2** by-design pairs: `{Mesclun, Salad Mix} → "תערובת סלט"` AND `{Summer Squash, Zucchini} → "קישוא"`. The second pair is justified at §5 (species/cultivar reasoning) — Zucchini is a cultivar of the קישוא species, and cultivar-level identity belongs in `crop_varieties`, not `crops.name_he`. | LOD400 §5 literal (`"Zucchini": "קישוא"`), §5 botanical authoring-note, §9 AC-03 (Counter assertion now compares against both pairs). |

---

## 3. Scope

Validate LOD400 v1.1.2 at commit `3c92a67`. Diff from the v1.1.1 ↔ v1.1.2
transition:

```bash
git diff 6fe7d7d 3c92a67 -- _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
```

(+47 / −28 lines, scoped to: §5 Zucchini line revert + botanical note;
§9 AC-03 allow-list widened from 1 pair to 2 pairs; frontmatter
version/changelog.)

For convenience, the cumulative diff since the last PASS_WITH_FINDINGS-free
state (i.e., since v1.0.0 at commit `91972bc`):

```bash
git diff 91972bc 3c92a67 -- _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md
```

Re-run all 20 VCs from `MANDATE_..._v1.0.0.md` §3 + the 4 R2 sub-checks
from `MANDATE_..._v1.0.1.md` §4. Replace **VC-15.5 (R3)** from the
withdrawn v1.0.2 mandate with:

- **VC-15.5 (R3-revised)** — Hebrew-value duplicate set verification.
  Run:

  ```bash
  python3 - <<'PY'
  import re
  text = open('_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md').read()
  m = re.search(r'JMF_CROP_MAP: dict\[str, str\] = \{(.+?)^\}', text, re.S | re.M)
  entries = re.findall(r'^\s*"([^"]+)":\s+"([^"]+)"', m.group(1), re.M)
  from collections import Counter
  c = Counter(v for _, v in entries)
  dups = {v: sorted([k for k, mv in entries if mv == v]) for v, cnt in c.items() if cnt > 1}
  print(f'entries={len(entries)}')
  print(f'dups={dups}')
  PY
  ```

  Expected output (verbatim):

  ```text
  entries=52
  dups={'תערובת סלט': ['Mesclun', 'Salad Mix'], 'קישוא': ['Summer Squash', 'Zucchini']}
  ```

- **VC-15.6 (R3 botanical justification)** — Verify §5 contains a
  botanical note explaining the species/cultivar reasoning (keywords:
  "species", "cultivar", "crop_varieties"). The note exists so that a
  future reader cannot mistake the duplicate pair for an oversight.

Independence rule still applies. Do NOT read R1/R2/withdrawn-R3 verdicts
or mandates before deriving your own VC-15 conclusions.

---

## 4. Output Format

Write your verdict to:
**`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`**

(Use `v1.0.2` — the verdict version numbering is unchanged because the
withdrawn v1.0.2 mandate did not result in a verdict file.)

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

*Re-issued resubmission mandate 2026-05-24 by team_110 (Claude Opus 4.7).*
*Withdraws MANDATE_..._v1.0.2 (which referenced v1.1.1).*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1/LOD400-VERDICT_v1.0.2.md`.*
