---
id: MANDATE_SFA-S003-P002-WP-B1-patch01_L-GATE_S_v1.0.0
from: team_110 (AOS Domain Architect — ADR045 execution_authority: full)
to: team_190 (Constitutional Validator — non-Claude per Iron Rule #1)
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch01
project: smallfarmsagents
status: ACTIVE
verdict: PENDING
engine_constraint: "Iron Rule #1 — validator engine MUST differ from team_110 (Claude Opus 4.7). Canonical non-Claude: GPT-5.5."
authorization_basis: "ADR045 R2 #2 — team_110 may issue mandates to team_190 directly during execution_authority: full mandate. Same mandate root as WP-B1: SFA-S003-P002-WP-B EXECUTION_MANDATE_v1.0.0 (R3 PASS at 7c3d7d6)."
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md
spec_version: v1.0.0
spec_commit: "55c5b6c"
parent_wp: SFA-S003-P002-WP-B1
parent_lod500_commit: "6a85561"
---

# L-GATE_S Mandate — SFA-S003-P002-WP-B1-patch01

**ספר גידולים: JMF_CROP_MAP alias extension + Rutabaga Hebrew correction**
**Track:** A | **Profile:** L0 | **Effort:** SMALL | **Risk:** LOW

---

## 1. Gate History

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_E | PASS | 2026-05-25 | team_00 in-session authorization. Sequencing directive: patch01 MUST close before WP-B2. Hebrew correction directive: phonetic transliteration `Rutabaga → רוטבגה`. Commit `5c181bc`. |
| L-GATE_S | (this mandate ↓) | — | team_190 |

Parent WP-B1 reached LOD500_LOCKED at commit `6a85561` on 2026-05-25 with PASS_WITH_FINDINGS verdicts at all 4 lifecycle gates. WP-B1-patch01 is a **sibling** WP — WP-B1 stays LOCKED.

---

## 2. Scope

Validate the LOD400 spec for **WP-B1-patch01** as a spec-only constitutional review. The patch is minimal — `constants.py` JMF_CROP_MAP literal edits only (no schema, ORM, importer, migration, CLI, or model changes).

Spec under review: LOD400 v1.0.0 at commit `55c5b6c`.

---

## 3. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | **IR#1 cross-engine** | LOD400 frontmatter assigns builder `sfa_build` and validator `team_190 (non-Claude)`. Author (team_110) is Claude Opus 4.7. You (validator) are GPT-5.5. |
| VC-2 | **IR#4 lifecycle-only roadmap** | LOD400 does not instruct builder to mutate `_aos/roadmap.yaml`. Lifecycle transitions remain team_110's responsibility. |
| VC-3 | **IR#6 artifact communication** | All inter-team artifacts route via `_COMMUNICATION/<team>/`. |
| VC-4 | **IR#11 governance untouched** | LOD400 §2.2/§7 list governance/lean-kit as untouched; §10 deliverables don't write under `_aos/governance/`. |
| VC-5 | **Parent WP-B1 LOD500_LOCKED preserved** | LOD400 §1, §2.2, §7 all explicitly state that WP-B1 is NOT reopened. The B1 LOD400 spec (commit `6a85561`) MUST NOT be modified by this patch. Verify §7 lists `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md` as "DO NOT TOUCH". |
| VC-6 | **LOD500_LOCKED inventory complete** | §7 LOD500_LOCKED inventory includes ALL the post-B1 locked files: `crop_task_templates.py`, `jmf_masterclass.py`, migration 044, `seed.py` (now LOD500_LOCKED via B1 closure), and the B1 LOD400 spec. Plus the WP-A and WP-B1 inherited lock list. |
| VC-7 | **Modified files = exactly 3** | §10 MODIFY list is exactly: `constants.py`, `test_jmf_crop_map.py`, `CHANGELOG.md`. No other existing file is in §10 MODIFY. |
| VC-8 | **Rutabaga fix is unambiguous** | §3.1 specifies the exact before/after literal: `"ברוקקואר" → "רוטבגה"`. AC-02 enforces both the new value AND the absence of the old value. |
| VC-9 | **Alias enumeration is exact** | §3.2 lists 33 alias entries categorized by reason (typo, synonym, storage qualifier, etc.). §4 AC-04.1 adds 1 more (`Eggplant  (Feld)`). Total: 34 alias additions. §3.2 entry-count math sums to 33 explicitly; §4 AC-01 expects total post-patch = 86 (52 baseline + 34 aliases). Verify arithmetic and that AC-01 + AC-04.1 are mutually consistent. |
| VC-10 | **AC-03 Counter assertion enumerates 13 by-design pairs/groups** | §4 AC-03 lists exactly 13 entries in the expected `duplicates` dict. Each entry is a `Hebrew → sorted-list-of-English-keys` mapping. Verify the 13 entries by inspecting the literal block; verify every Hebrew target appearing in §3.2 alias block IS represented (no orphans). |
| VC-11 | **`Eggplant  (Feld)` literal handling explicit** | §4 AC-04.1 specifies the design choice: add the exact-string `"Eggplant  (Feld)"` (with double space + parenthetical) as a literal alias mapping to `"חציל"`. This preserves the WP-B1 parser contract (no whitespace normalization at the parser layer). AC-04.1 explicitly raises AC-01 expected count from 85 to 86. |
| VC-12 | **All 22 WP-B1 ACs preserved (no regression)** | §4 AC-05 mandates regression: running the full `tests/crop_book/` suite after the patch must show all 56 prior WP-B1 tests PASS. The patch does NOT modify B1 deliverables. |
| VC-13 | **Test count target** | §5 sets a target of ≥10 new tests across 1 EXTEND + 3 NEW test files. AC-03 update mandates updating the existing `test_ac03_*` (not duplicating it). |
| VC-14 | **No GCR required** | §LOD200-§9 + §LOD400 implicit: pure data extension; no schema/model/migration. |
| VC-15 | **LOD400 precision standard (junior-dev buildable)** | §3.1 has the exact before/after string. §3.2 has the literal Python dict block with comments. §4 ACs are testable. §5 tests are file-allocated. §6 build sequence is 4 steps. A junior dev can implement Step 2 (constants edit) by literal copy-paste. |
| VC-16 | **`validate_aos.sh` clean at HEAD** | Run `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` — expect `29 PASS / 17 SKIP / 0 FAIL`. |
| VC-17 | **YAML / artifact integrity** | `python3 -c "import yaml; yaml.safe_load(open('_aos/roadmap.yaml'))"` succeeds. WP-B1-patch01 entry shows `lod_status: LOD200_LOCKED`, `current_lean_gate: L-GATE_E`, L-GATE_E PASS in gate_history, depends_on: ["SFA-S003-P002-WP-B1"]. |
| VC-18 | **Sequencing claim verifiable** | LOD200 §1 + §12 state patch01 must close before WP-B2. Roadmap shows WP-B2 still `PROPOSED`. Verify nothing in this patch creates an unintended unblock of B2 (no shared file modifications, no lifecycle field touches on B2). |
| VC-19 | **Hebrew correctness of new values** | Best-effort verification (you can't read Hebrew correctness for every entry, but you can sanity-check): each new alias value is a non-empty Hebrew string, and the Counter assertion's left-hand keys are all non-empty Hebrew strings. Specifically verify `"Rutabaga"` value contains the Hebrew letters resh-vav-tet-bet-gimel-heh (`ר`+`ו`+`ט`+`ב`+`ג`+`ה`) and is exactly `"רוטבגה"`. |
| VC-20 | **Operational gate semantics** | LOD400 §1 + LOD200 §1 explicitly state that after patch lands, the operational pause on `seed.py --all` against the live workbook (from `DISPOSITION_FINDING-01_v1.0.0.md` §3.4) is lifted. This is a docs-only semantic — there is no `gate` flag in code; the pause was a process control. Verify the spec articulates this clearly. |

**Total: 20 criteria.**

---

## 4. Files to Review

### Spec documents

- **LOD400 (under review):** `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD400_spec.md` (commit `55c5b6c`)
- **LOD200:** `_aos/work_packages/S003/SFA-S003-P002-WP-B1-patch01/LOD200_spec.md` (commit `5c181bc`)

### Context (for verifying VC-5, VC-6, VC-12, VC-18)

- **Parent WP-B1 LOD400** (LOD500_LOCKED at `6a85561` — read-only): `_aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md`
- **WP-B1 completion report:** `_COMMUNICATION/team_110/SFA-S003-P002-WP-B1/COMPLETION_REPORT_SFA-S003-P002-WP-B1_v1.0.0.md`
- **WP-B1 disposition:** `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B1/DISPOSITION_FINDING-01_v1.0.0.md`
- **WP-B1 inquiry (live workbook crop inventory):** `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B1/INQUIRY_AC04_CROP_CHART_MISMATCH_v1.0.0.md`
- **Existing JMF_CROP_MAP** (post-B1 build): `organic_market_agent/crop_book/constants.py`

### Roadmap

- `_aos/roadmap.yaml` — confirm WP-B1-patch01 entry exists at `lod_status: LOD200_LOCKED` and WP-B1 entry remains at `LOD500_LOCKED / DONE`.

---

## 5. Required Commands

```bash
# 1. AOS validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .

# 2. Roadmap parse + WP-B1-patch01 state
python3 -c "
import yaml
d = yaml.safe_load(open('_aos/roadmap.yaml'))
for wp_id in ['SFA-S003-P002-WP-B1', 'SFA-S003-P002-WP-B1-patch01', 'SFA-S003-P002-WP-B2']:
    wp = [w for w in d['work_packages'] if w['id']==wp_id][0]
    print(wp['id'], wp['status'], wp['lod_status'], wp['current_lean_gate'])
"

# 3. Parent WP-B1 LOD400 untouched (must be empty)
git diff 6a85561..55c5b6c -- _aos/work_packages/S003/SFA-S003-P002-WP-B1/LOD400_spec.md

# 4. Existing JMF_CROP_MAP Rutabaga value (pre-patch state — should still be "ברוקקואר")
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
print(f'Rutabaga={JMF_CROP_MAP[\"Rutabaga\"]!r}')
print(f'entries={len(JMF_CROP_MAP)}')
"
# Expected: Rutabaga='ברוקקואר'  entries=52 (the patch HASN'T been built yet; this confirms the baseline.)

# 5. Cross-engine attestation for patch01 commits
git log --format='%h %an %s' 6a85561..55c5b6c
```

---

## 6. Output Format

Write your verdict to:
**`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD400-VERDICT_v1.0.0.md`**

Use the unified verdict template (7 sections).

### Decision criteria

- **PASS** — all 20 VCs PASS; team_110 proceeds to Phase 4 (roadmap transition `lod_status: LOD200_LOCKED → LOD400_LOCKED`, `current_lean_gate: L-GATE_E → L-GATE_B`) and Phase 5 (build mandate to sfa_build).
- **PASS_WITH_FINDINGS (0 blockers)** — same as PASS; carry MAJOR/MINOR forward.
- **FAIL (≥1 blocker)** — team_110 remediates + R2.

### Engine constraint

Validator MUST be non-Claude (GPT-5.5 canonical). Author is Claude Opus 4.7.

### Independence rule

Do NOT read prior WP-B1 verdicts (R1/R2/R3 + L-GATE_V) to short-circuit your own pass on this patch. Each VC must be independently derived from the LOD400 v1.0.0 content.

---

## 7. Authorization basis

ADR045 R2 #2; mandate root `_COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md` (R3 PASS at `7c3d7d6`). Same mandate that authorized WP-B1; covers patch01 as a follow-up to a WP within the mandate's program scope.

team_100 NOT in routing chain.

---

*Mandate issued 2026-05-25 by team_110 (Claude Opus 4.7) under EXECUTION_MANDATE SFA-S003-P002-WP-B.*
*Validator: team_190 (non-Claude per IR#1).*
*Awaiting verdict at `_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch01/LOD400-VERDICT_v1.0.0.md`.*
