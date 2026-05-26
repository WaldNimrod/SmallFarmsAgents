---
id: MANDATE_SFA-S003-P002-WP-B1-patch08_L-GATE_S_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch08
round: R1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md
spec_version: v1.0.0
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190"
parallel_to: SFA-S003-P002-WP-B1-patch07 L-GATE_S R1
status: ACTIVE
verdict: PENDING
---

# L-GATE_S R1 — patch08 (variety-parser cleanup)

## 1. Scope
MEDIUM: filter logic in `_extract_cultivar_names` + DELETE ~11 noise rows + regression tests. Targets defect surfaced in OP-2 prod load (15 new varieties, ~11 noise + ~4 real).

## 2. Validation Criteria (10 VCs)

| # | Criterion | Check |
|---|-----------|-------|
| VC-1 | Engine chain | 3 distinct engines in frontmatter |
| VC-2 | DECISION | DECISION_WP-B1-patch07-patch08 §2 authorizes scope |
| VC-3 | Filter heuristic completeness | §3.1 `_is_valid_cultivar_name` covers: URLs, bullets, single chars, sentence-endings, section headers (colon), comma-lists, length > 40, pure-numeric |
| VC-4 | Test coverage of filter | §3.3 test asserts both ACCEPT cases (Carmen, Marnero) and REJECT cases (URLs, bullets, sentences) |
| VC-5 | DELETE script idempotency | §3.2 + AC-05: 2 consecutive `--apply` runs yield no changes on second |
| VC-6 | DELETE heuristics correct | §3.2: SQL filter matches the same noise patterns the Python filter rejects. NO whitelist of real cultivars accidentally caught. |
| VC-7 | Acknowledged limitation | §5 note + R-04: "Intensive Spacing" type values (no colon, short) require parser-level section-header skip, not filter — DECISION-approved limitation |
| VC-8 | Out-of-scope explicit | §5 Step 7: re-running OP-2 against PRODUCTION is operational, NOT part of build. The build verifies fix correctness on test fixture. |
| VC-9 | LOCKED scope | §7: 3 modified + 1 created. No other LOCKED touched. |
| VC-10 | validate_aos.sh | clean |

## 3. Required Commands

```bash
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md

# Verify current production state has the noise (pre-fix)
docker exec oma-postgres psql -U oma -d organic_market_agent -c "
SELECT count(*) FROM crop_varieties
WHERE name_en ~ '://' OR name_en IN ('●', '○', '-', '*', '1')
   OR length(name_en) > 40 OR name_en LIKE '%: %'
   OR (length(name_en) > 6 AND name_en LIKE '%.');"
# Expected: ~11 (the noise from OP-2)

bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 4. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch08/LOD400-VERDICT_v1.0.0.md`

Commit: `gate(WP-B1-patch08/L-GATE_S): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

---
