---
id: MANDATE_SFA-S003-P002-WP-B1-patch04-hotfix02_L-GATE_S_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch04-hotfix02
round: R1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04-hotfix02/LOD400_spec.md
spec_version: v1.0.0
orchestrator: team_110 (Claude Opus 4.7)
builder: team_110 (Claude Opus 4.7 — single-engine, SMALL scope per hotfix01/patch02 precedent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 Opus 4.7 (orchestrator + builder) ≠ team_190 GPT-5.5 (validator) — IR#1 preserved via distinct validator engine"
status: ACTIVE
verdict: PENDING
---

# L-GATE_S R1 — patch04-hotfix02 (Postgres transaction-poisoning fix)

## 1. Scope

SMALL hotfix: 1 function (`_upsert_variety`, ~10 LOC) rewritten to use `ON CONFLICT (crop_id, name_en) DO NOTHING` instead of `try/except: pass` (which poisoned Postgres transaction). + 1 regression test. Sibling of hotfix01 (`a7493a4`, int↔bool).

## 2. Validation Criteria (9 VCs)

| # | Criterion | Check |
|---|-----------|-------|
| VC-1 | Engine chain | frontmatter has orchestrator + builder (both team_110) + validator (team_190 GPT-5.5) + engine_chain summary |
| VC-2 | Single-engine builder rationale | DECISION §4 + LOD400 §8 invoke patch02 + hotfix01 precedent. SMALL scope. IR#1 preserved via team_190 validator. |
| VC-3 | DECISION authorization | DECISION_WP-B1-patch04-hotfix02_2026-05-26 §§1-3 explicit |
| VC-4 | Defect description accurate | DECISION §1 + LOD400 §1 correctly identify root cause: Python try/except catches Python exception but Postgres transaction stays poisoned. `_upsert_knowledge_note` already uses correct ON CONFLICT pattern. Operational evidence cited: OP-2 re-run post-hotfix01 (2026-05-26) failed with `InFailedSqlTransaction`. |
| VC-5 | §3.1 rewrite byte-exact | OLD function body matches current source (post-hotfix01 state with FALSE, FALSE). NEW uses `ON CONFLICT (crop_id, name_en) DO NOTHING`. Targets correct UNIQUE constraint name (`uq_cv_crop_name_en`). |
| VC-6 | §3.2 regression test correct | Asserts presence of `ON CONFLICT (crop_id, name_en) DO NOTHING` + absence of `except Exception:\n        pass  # UNIQUE conflict` snippet. Tight matching to avoid false positives. |
| VC-7 | AC measurability | All 7 ACs objective (string presence/absence + pytest count + validate_aos exit code + diff scope) |
| VC-8 | LOCKED scope discipline | §7 lists 3 files only. NO other LOCKED file modifiable. |
| VC-9 | validate_aos.sh + roadmap | `validate_aos.sh` 0 FAIL; roadmap entry post-commit at LOD400_LOCKED. |

## 3. Required Commands

```bash
# 1. Spec version
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch04-hotfix02/LOD400_spec.md

# 2. Current source has the buggy try/except pattern (pre-build verification)
grep -A2 "except Exception:" scripts/load_masterclass_sheets.py | head -5
# Expected: shows the `pass  # UNIQUE conflict` line

# 3. Current source has the FALSE, FALSE post-hotfix01 patch
grep "VALUES (:crop_id, :name_en, FALSE, FALSE)" scripts/load_masterclass_sheets.py
# Expected: 1 match

# 4. Confirm UNIQUE constraint name in Postgres schema (cited in spec)
# (Validator may skip; the constraint name is in patch04 ARCHIVE_MANIFEST + spec §3.1)

# 5. DECISION exists
test -f _COMMUNICATION/team_00/DECISION_WP-B1-patch04-hotfix02_2026-05-26_v1.0.0.md && echo PRESENT

# 6. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 4. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch04-hotfix02/LOD400-VERDICT_v1.0.0.md`

Commit: `gate(WP-B1-patch04-hotfix02/L-GATE_S): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 single-engine build.
FAIL → R2.

---
