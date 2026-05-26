---
id: MANDATE_SFA-S003-P002-WP-B1-patch08_L-GATE_S_R2_v1.0.0
from: team_110
to: team_190
date: 2026-05-26
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch08
round: R2
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md
spec_version: v1.0.1
prior_round_ref: _COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch08/LOD400-VERDICT_v1.0.0.md
prior_round_result: FAIL (1 BLOCKER F-S-PATCH08-01)
orchestrator: team_110 (Claude Opus 4.7)
builder: team_10 (Claude Sonnet sub-agent)
validator: team_190 (GPT-5.5, non-Claude per IR#1)
engine_chain: "team_110 ≠ team_10 ≠ team_190"
status: ACTIVE
verdict: PENDING
---

# L-GATE_S R2 — patch08

## 1. R1 Disposition

R1 FAIL with 1 BLOCKER. F-S-PATCH08-01 correct: "Intensive Spacing" (17 chars, no colon, no period) slipped through both the Python filter and the SQL cleanup heuristics. Spec previously called this a "known limitation" — team_190 correctly rejected the limitation as inconsistent with DECISION §2.2's "delete the 11+ noise rows" requirement.

## 2. R2 Change (v1.0.0 → v1.0.1)

| Section | Change |
|---------|--------|
| **§3.1 Python filter** | NEW `KNOWN_SECTION_HEADERS: frozenset` constant (10 entries: 'Intensive Spacing', 'Cultivars', 'Cultivar Suggestions', 'Pests', 'Diseases', 'Harvest', 'Storage', 'Sowing', 'Transplanting', 'Yield'). `_is_valid_cultivar_name` checks the blacklist FIRST (before generic heuristics). |
| **§3.2 SQL cleanup** | Mirror tuple `KNOWN_SECTION_HEADERS = ('Intensive Spacing', ...)` + new SQL clause `OR name_en = ANY(:section_headers)`. Both Python and SQL cleanup catch the same explicit blacklist. |
| **§3.3 regression test** | Updated noise-list to assert 'Intensive Spacing' AND 'Cultivars' both REJECTED. Removed prior "spec note" that called this a known limitation. |
| **Footer** | v1.0.1 R2 changelog. |

No change to: filter heuristics for other patterns (URL, length, bullet, etc.), scope (3 modified + 1 new), builder identity (Sonnet).

## 3. Validation Criteria (R2 — focused)

| # | Criterion |
|---|-----------|
| VC-R2-1 | Version v1.0.1 |
| VC-R2-2 | §3.1 declares `KNOWN_SECTION_HEADERS` frozenset with ≥10 entries including 'Intensive Spacing'. Filter checks blacklist FIRST. |
| VC-R2-3 | §3.2 SQL has tuple `KNOWN_SECTION_HEADERS` + `OR name_en = ANY(:section_headers)` clause. Mirrors Python set. |
| VC-R2-4 | §3.3 regression test asserts both 'Intensive Spacing' and 'Cultivars' rejected. Prior "spec note" about Intensive Spacing limitation removed. |
| VC-R2-5 | No regression on R1 PASS sections (§3.4 CHANGELOG, §4 ACs structure, §5 build sequence, §7 LOCKED scope, §8 builder). |
| VC-R2-6 | validate_aos.sh 0 FAIL. |

## 4. Commands

```bash
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md

# §3.1 has KNOWN_SECTION_HEADERS frozenset
grep -A2 "KNOWN_SECTION_HEADERS: frozenset" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md

# §3.2 SQL has the same allowlist
grep -E "= ANY\(:section_headers\)|name_en LIKE.*Intensive" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md

# §3.3 regression test asserts Intensive Spacing rejected
grep -B1 -A1 "'Intensive Spacing'" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch08/LOD400_spec.md | head -10

bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 5. Output
`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch08/LOD400-VERDICT_R2_v1.0.0.md`. PASS/PWF → Sonnet build.

---
