---
id: MANDATE_SFA-S003-P002-WP-B1-patch04-hotfix01_L-GATE_S_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch04-hotfix01
round: R1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04-hotfix01/LOD400_spec.md
spec_version: v1.0.0
orchestrator: team_110 (Claude Opus 4.7)
builder: team_110 (Claude Opus 4.7 — single-engine, SMALL scope per patch02 precedent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator + single-engine builder) ≠ team_190 GPT-5.5 (validator) — IR#1 preserved via distinct validator engine"
status: ACTIVE
verdict: PENDING
---

# L-GATE_S R1 — patch04-hotfix01 (Postgres int↔bool fix)

## 1. Scope

SMALL hotfix: 3 line edits in `scripts/load_masterclass_sheets.py` + 1 regression test. Defect surfaced operationally — production Postgres rejects int literals (`0`/`1`) for boolean columns; SQLite was tolerant. patch04 tests ran SQLite-only.

## 2. Validation Criteria (10 VCs)

| # | Criterion | Check |
|---|-----------|-------|
| VC-1 | Engine chain | frontmatter has orchestrator + builder (both team_110) + validator (team_190 GPT-5.5) + engine_chain summary |
| VC-2 | Single-engine builder rationale | DECISION §4 + LOD400 §8 invoke patch02 precedent. SMALL scope (3 LOC + 1 test), no architectural decisions, no schema. IR#1 preserved via team_190 distinct validator. |
| VC-3 | DECISION authorization | DECISION_WP-B1-patch04-hotfix01_2026-05-26 §§1-3 explicit. LOCKED scope exception narrow (3 files). |
| VC-4 | Defect description accurate | DECISION §1 + LOD400 §1 correctly identify root cause: int literals in INSERT VALUES for boolean columns; SQLite tolerant, Postgres strict. Operational evidence cited (24 JSONs written, 0 DB rows inserted). |
| VC-5 | §3.1 + §3.2 edits byte-exact | OLD lines match current `scripts/load_masterclass_sheets.py` source. NEW lines use `FALSE, FALSE` and `TRUE`. |
| VC-6 | §3.3 regression test correct | Test scans source for forbidden int-literal patterns + asserts corrected patterns present. Tight matching to avoid false positives. |
| VC-7 | AC measurability | All 7 ACs objective (string presence/absence + pytest count + validate_aos exit code + diff scope) |
| VC-8 | Out-of-scope items explicit | DECISION §5 + LOD400 §6 R-02 explicitly state that `patch03_data_fix.py` is NOT in scope (uses parameterized text, separate audit if needed) |
| VC-9 | LOCKED scope discipline | §7 lists 3 files only. NO other LOCKED file modifiable. |
| VC-10 | validate_aos.sh + roadmap | `validate_aos.sh` 0 FAIL; roadmap.yaml parses; hotfix01 entry will be at LOD200_LOCKED/L-GATE_E PASS after Phase 4. |

## 3. Required Commands

```bash
# 1. Spec version
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04-hotfix01/LOD400_spec.md

# 2. Current source has the buggy patterns (pre-build verification)
grep -nE "VALUES \(:crop_id, :name_en, 0, 0\)|, 1, :model, :now" scripts/load_masterclass_sheets.py
# Expected: both lines present (confirms defect exists pre-fix)

# 3. DECISION exists + authorizes
test -f _COMMUNICATION/team_00/DECISION_WP-B1-patch04-hotfix01_2026-05-26_v1.0.0.md && echo PRESENT
grep -E "int↔bool|FALSE, FALSE|int.bool defect" \
  _COMMUNICATION/team_00/DECISION_WP-B1-patch04-hotfix01_2026-05-26_v1.0.0.md | head -5

# 4. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 4. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch04-hotfix01/LOD400-VERDICT_v1.0.0.md`

Commit: `gate(WP-B1-patch04-hotfix01/L-GATE_S): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 single-engine build.
FAIL → R2.

---
