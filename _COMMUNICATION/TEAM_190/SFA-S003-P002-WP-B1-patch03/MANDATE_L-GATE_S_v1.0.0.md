---
id: MANDATE_SFA-S003-P002-WP-B1-patch03_L-GATE_S_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch03
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7) AND team_10 (Sonnet, future builder). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2; team_00 DECISION_WP-B1-patch03_TAXONOMY_2026-05-25 §§1-4."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md
spec_version: v1.0.0
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md
---

# L-GATE_S Mandate — SFA-S003-P002-WP-B1-patch03

**ספר גידולים: JMF_CROP_MAP taxonomic expansion (11 value changes)**
**Track A | Profile L0 | Effort MEDIUM | Risk LOW-MEDIUM**

## 1. Scope

Validate LOD400 v1.0.0 spec for WP-B1-patch03 as a spec-only constitutional review. patch02 closed Q4 (Parsnips + Shallots); patch03 amends that DECISION with 11 additional taxonomy changes per a new DECISION file dated 2026-05-25.

Total scope: 11 value edits + 2 LOCKED test updates (narrow scope-exception) + 11 new regression tests + CHANGELOG. ~70-100 effective LOC. Sub-agent build (NOT single-engine like patch02).

## 2. Why MEDIUM (not SMALL)

| Dimension | patch02 (SMALL) | patch03 (MEDIUM) |
|-----------|-----------------|------------------|
| Value edits | 2 | 11 |
| New tests | 2 | 11 |
| LOCKED files modified | 0 (all additive) | 2 test functions (narrow exception per DECISION §4) |
| New baseline `crops.name_he` | 0 | 5 |
| Architectural decisions | 0 | 3 (עלי בייבי baseline, Cherry/Heirloom split, cultivar-vs-baseline distinction) |
| Build pattern | Single-engine team_110 | Sonnet sub-agent (team_10) |

## 3. Gate History

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_E | PASS | 2026-05-25 | team_00 in-session authorization via new DECISION file |
| L-GATE_S | (this mandate ↓) | — | LOD400 v1.0.0 |

## 4. Validation Criteria (18 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **IR#1 cross-engine** | LOD400 frontmatter assigns builder=`team_10 (Sonnet)`, validator=`team_190 (non-Claude GPT-5.5)`, orchestrator=`team_110 (Opus 4.7)`. All 3 distinct. **NOT** single-engine like patch02 — LOD200 §10 + LOD400 §11 explicitly invoke sub-agent pattern because scope exceeds the threshold. |
| VC-2 | **IR#4 single-writer roadmap** | LOD400 deliverables don't include roadmap mods by the builder. team_110 transitions lifecycle fields in Phase 4 outside build scope. |
| VC-3 | **IR#6 `_COMMUNICATION/` routing** | All inter-team artifacts in `_COMMUNICATION/<team>/<WP>/`. |
| VC-4 | **IR#11 governance untouched** | `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` explicitly listed in §10 DO NOT TOUCH. |
| VC-5 | **LOD500_LOCKED scope exception is narrow + authorized** | DECISION §4 authorizes ONLY the 2 named test functions for modification. LOD400 §2.2 + §9 explicitly limit scope. NO other LOCKED file modifiable. |
| VC-6 | **DECISION file exists + cites all 11 values verbatim** | `_COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md` exists. §§1.1-1.4 list all 11 (key → new_value) pairs. §2 lists 6 status-quo confirmations. §3 specifies the 24-group post-state. |
| VC-7 | **§3.1 11-edit table is internally consistent** | The 11 "Old" column values match current post-patch02 state of `JMF_CROP_MAP` (verifiable via probe). The 11 "New" column values match DECISION §§1.1-1.4 byte-exactly. |
| VC-8 | **§3.2 24-group dict literal — group count + membership** | Independent probe over the §3.2 dict literal returns exactly **24** groups. Total key count across groups = sum of group sizes (count manually). Each "shrunk" group (פלפל, עגבנייה, מלפפון, כרוב) has the correct REMAINING members (not the original). Each "new"/"unchanged" group (עלי בייבי, etc.) is correct. NO group is duplicated. |
| VC-9 | **Disappeared groups not in §3.2** | `"תערובת סלט"` and `"קייל"` keys must NOT appear in the §3.2 dict literal (both groups disappeared). |
| VC-10 | **AC measurability** | All 18 ACs phrased as objective `assert JMF_CROP_MAP[K] == V`, `len(JMF_CROP_MAP) == 86`, `dup_count == 24`, command/test outcomes, or diff scope. |
| VC-11 | **AC-15 new-baseline assertion present** | AC-15 explicitly enumerates the 5 new `name_he` strings (עלי בייבי, עגבניית שרי, עגבניות מורשת, מלפפון חממה, כרוב סיני). |
| VC-12 | **Builder safety guidance** | §3.1 explicitly warns about `replace_all` collision (the value `"תערובת סלט"` appears in 2 lines; the value `"עגבנייה"` appears in 4 lines pre-patch). §6 step 2 mandates unique-substring matching. R-03 captured. |
| VC-13 | **24-group dict pre-validation step** | §6 Step 6 mandates running `pytest tests/crop_book/test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist -v` BEFORE commit. R-04 captured. |
| VC-14 | **Test count consistency** | §11 (LOD200) says 13 tests touched (2 LOCKED updates + 11 new); §5 (LOD400) repeats; §4.3 AC-16 says 354 passed (343 baseline + 11 new). Numbers align. |
| VC-15 | **Risk register completeness** | §8 covers: prod DB drift (R-01, deferred per DECISION §8), lazy baseline creation (R-02, mitigated by existing importer pattern), replace_all collision (R-03), 24-group dict typo (R-04), Hebrew encoding (R-05). |
| VC-16 | **CHANGELOG entry comprehensive** | §3.5 enumerates: 5 new baselines + 3 remappings + 5 splits + 3 refinements + duplicate-allowlist transition + LOCKED scope exception citation. |
| VC-17 | **Builder identity: NOT single-engine** | §11 explicitly contrasts patch02 (single-engine, 4 LOC) vs patch03 (Sonnet sub-agent, ~70 LOC + LOCKED edits). Builder field in frontmatter = `team_10` (Sonnet). IR#1 orchestrator-vs-builder separation RESTORED. |
| VC-18 | **validate_aos.sh + roadmap integrity** | `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL. `_aos/roadmap.yaml` parses; patch03 entry present at `lod_status: LOD200_LOCKED, current_lean_gate: L-GATE_E` (or LOD400_LOCKED if Phase 4 already ran). All 6 prior WPs (WP-A + B1 + patch01 + B3 + B2 + patch02) remain `DONE / LOD500_LOCKED`. |

**Total: 18 VCs.**

## 5. Files to Review

- **LOD400 (under review):** `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md` (v1.0.0)
- **LOD200:** `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD200_spec.md` (v1.0.0)
- **DECISION (authorization):** `_COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md`
- **Current `constants.py` state** (post-patch02 LOCK; reference for §3.1 "Old" column): `organic_market_agent/crop_book/constants.py`
- **Current LOCKED tests** (reference for §3.2 + §3.3 starting state): `tests/crop_book/test_jmf_crop_map.py`
- **Roadmap:** `_aos/roadmap.yaml`

## 6. Required Commands

```bash
# 1. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Current pre-build state of the 11 affected keys
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
keys = ['Mesclun', 'Salad Mix', 'Baby kale',
        'Greenhouse Cherry Tomato', 'Greenhouse Heirloom Tomato',
        'Greenhouse Libanese Cucumber', 'Chinese Cabbage',
        'Hot Pepper', 'Beans (Bush)', 'Snow Peas', 'Basil']
for k in keys:
    print(f'{k:35} → {JMF_CROP_MAP[k]!r}')
print(f'len: {len(JMF_CROP_MAP)}')
"
# Expected: each line shows the OLD value from LOD400 §3.1 'Old line' column.
# (Spec is locked but build has NOT run yet.)

# 3. DECISION exists + cites all 5 new baseline name_he values
test -f _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md && echo "DECISION present"
grep -E "עלי בייבי|עגבניית שרי|עגבניות מורשת|מלפפון חממה|כרוב סיני" \
  _COMMUNICATION/team_00/DECISION_WP-B1-patch03_TAXONOMY_2026-05-25_v1.0.0.md | head -10

# 4. LOD400 cites the same values
grep -E "עלי בייבי|עגבניית שרי|עגבניות מורשת|מלפפון חממה|כרוב סיני" \
  _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch03/LOD400_spec.md | head -10

# 5. Roadmap state — patch03 + parent WPs
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
for wp_id in ['SFA-S003-P002-WP-B1', 'SFA-S003-P002-WP-B1-patch01',
              'SFA-S003-P002-WP-B2', 'SFA-S003-P002-WP-B3',
              'SFA-S003-P002-WP-B1-patch02', 'SFA-S003-P002-WP-B1-patch03']:
    wp = [w for w in d['work_packages'] if w['id']==wp_id]
    if wp:
        print(wp[0]['id'], wp[0]['status'], wp[0]['lod_status'], wp[0]['current_lean_gate'])
    else:
        print(f'{wp_id}: MISSING')
"

# 6. Manual count of the 24-group dict in §3.2 (independent verification)
# Count: lines starting with '"' inside the assert duplicates == { ... } block, sum group sizes.
# Expected: 24 keys (Hebrew strings) total in the dict; sum of group sizes = 38 keys-with-duplicates.
```

## 7. Output Format

Write verdict to: **`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch03/LOD400-VERDICT_v1.0.0.md`**

Commit with:
```
gate(WP-B1-patch03/L-GATE_S): team_190 verdict — <RESULT>
Co-Authored-By: GPT-5.5 <noreply@anthropic.com>
```

Decision:
- **PASS / PASS_WITH_FINDINGS (0 blockers)** → team_110 dispatches build to Sonnet sub-agent (team_10) via standard pattern
- **FAIL (≥1 blocker)** → R2

Independence rule: derive VC conclusions from spec content + commands. The DECISION file is authorization evidence; it is NOT a substitute for spec-internal-consistency checks (e.g., the 24-group dict must be validated structurally, not just compared verbatim to a DECISION listing).

## 8. Authorization basis

ADR045 R2 #2 — team_110 independently mandates team_190. team_00 DECISION_WP-B1-patch03_TAXONOMY_2026-05-25 §§1-4 authorizes the scope including the narrow LOD500_LOCKED test exception.

---

*L-GATE_S R1 mandate issued 2026-05-25 by team_110 (Claude Opus 4.7).*
*Validator: team_190 (non-Claude per IR#1).*
*Future builder: team_10 (Sonnet sub-agent — spawned post-PASS).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch03/LOD400-VERDICT_v1.0.0.md`.*
