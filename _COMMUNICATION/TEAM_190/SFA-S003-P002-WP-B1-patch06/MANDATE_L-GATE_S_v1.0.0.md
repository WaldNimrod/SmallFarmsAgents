---
id: MANDATE_SFA-S003-P002-WP-B1-patch06_L-GATE_S_v1.0.0
from: team_110
to: team_190
date: 2026-05-25
type: GATE_MANDATE
gate: L-GATE_S
wp: SFA-S003-P002-WP-B1-patch06
round: R1
spec_ref: _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
spec_version: v1.0.0
engine_constraint: "Iron Rule #1 — non-Claude. GPT-5.5."
status: ACTIVE
verdict: PENDING
parallel_to: SFA-S003-P002-WP-B1-patch04 L-GATE_S R1
---

# L-GATE_S R1 — patch06 (Cleanup)

## 1. Scope
MEDIUM cleanup WP. Remove 27 entries from `JMF_CROP_MAP` (22 cultivars + 5 typos). Update 6 LOCKED test functions across 2 files. New cleanup script. Net MAP: 87 → 60 entries; duplicate groups 24 → 6.

Authored in parallel with patch04 (integration). BUILD sequenced AFTER patch04.

## 2. Validation Criteria (15 VCs)

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 | IR#1 three-engine | LOD400 frontmatter: builder=team_10 Sonnet, validator=team_190 GPT-5.5, orchestrator=team_110 Opus 4.7 |
| VC-2 | DECISION exists + authorizes scope | DECISION §3 explicitly lists 22+5 = 27 removals and the LOCKED scope exception covering 6 test functions across 2 files |
| VC-3 | 27 removals listed byte-exactly (§3.1) | LOD400 §3.1 has all 22 cultivar + 5 typo key strings matching current source. Builder-safety warning about value-collision present. |
| VC-4 | Post-state arithmetic correct | §4 AC-01 says `len == 60`. Computed: 87 (post-patch04) − 27 = 60 ✓. AC-07 says sum of group sizes = 12. Computed: 6 groups × 2 keys = 12 ✓. |
| VC-5 | 6-group allowlist exact (§3.3) | The 6-group dict in §3.3 is `{פאק צ'וי: [Bok Choy, Pak Choi], מנגולד: [Chard, Swiss Chard], בצל ירוק: [Green Onion, Scallions], תפוח אדמה: [Potato, Potatoes], אבטיח: [Watermelon, Watermelons], כוסברה: [Cilantro, Coriander]}`. Verifiable post-build via Counter probe. |
| VC-6 | LOCKED scope exception narrow + authorized | §2.3 / §8 list exactly 6 LOCKED test functions across 2 files. DECISION §3.3 authorizes. NO other LOCKED file modifiable. |
| VC-7 | test_alias_entry_count_grew_by_34 removal explicit | §3.6 explicitly says "REMOVE this test entirely" — not modify. AC-11 verifies absence. |
| VC-8 | 3 new regression tests defined byte-exact (§3.5) | LOD400 §3.5 contains complete function bodies (not pseudocode) for `test_no_cultivar_keys_*`, `test_no_typo_keys_*`, `test_six_synonym_groups_exact`. |
| VC-9 | Cleanup script safe | §3.7 dry-run default; --apply required; idempotent. Targets explicit orphan name_he set, not heuristics. |
| VC-10 | Implicit patch03 §1.3 revert acknowledged | §3.1 comment + CHANGELOG §3.8 acknowledge that Greenhouse Libanese Cucumber removal implicitly reverts patch03 §1.3's `מלפפון חממה` baseline. |
| VC-11 | Dependency stated | LOD200 §4 + LOD400 §6 Step 1 + DECISION §4 + roadmap.yaml `depends_on` all say patch06 BUILD strictly after patch04 LOD500_LOCKED. |
| VC-12 | AC measurability | All 15 ACs objective (membership, count, equality, command exit codes). |
| VC-13 | Risk register completeness | R-01..R-04 cover: importer downstream impact (mitigated by patch04), value-collision in `replace_all`, function-removal semantics (delete vs modify), cleanup script safety. |
| VC-14 | File scope discipline | 4 MODIFIED files (constants.py, 2 test files, CHANGELOG) + 1 CREATED (cleanup script). NO other files touched. |
| VC-15 | validate_aos.sh + roadmap | `validate_aos.sh` 0 FAIL. roadmap.yaml parses; patch06 entry at LOD200_LOCKED / L-GATE_E PASS; depends_on patch04. |

## 3. Required commands
```bash
# 1. Frontmatter
grep -E "^version:" _aos/work_packages/S003/SFA-S003-P002-WP-B1-patch06/LOD400_spec.md
# Expected: version: v1.0.0

# 2. Current pre-build state — confirm the 27 keys still present
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
removals = [
    # Cultivars (22)
    'Baby kale','Bell Pepper','Cauliflower / Romanesco','Fall Cabbage',
    'Fresh Carrots','Greenhouse English Cucumber','Greenhouse Libanese Cucumber',
    'Hakurei Turnip','Leek Storage','Leek Summer','Mesclun','Mini Celery Root',
    'Mini Fennel','Roma Tomato','Salad Mix','Salanova Lettuce','Savoy Cabbage',
    'Storage Onion','Sucrine','Summer Cabbage','Winter Radish','Zucchini',
    # Typos (5)
    'Brussel Sprouts','Eggplant  (Feld)','Raddish','Spinach TR','Spinarch SD',
]
missing = [k for k in removals if k not in JMF_CROP_MAP]
print(f'27 keys all present? {len(missing)==0} (missing: {missing})')
print(f'len: {len(JMF_CROP_MAP)}')
"

# 3. Post-removal arithmetic check (simulate what build will produce)
python3 -c "
from organic_market_agent.crop_book.constants import JMF_CROP_MAP
from collections import Counter
REMOVE = set([... 27 keys ...])  # populate
# Simulate Ginger from patch04
sim = {k:v for k,v in JMF_CROP_MAP.items() if k not in REMOVE}
sim['Ginger'] = \"ג'ינג'ר\"
c = Counter(sim.values())
print(f'simulated len: {len(sim)} (expect 60)')
print(f'simulated dup groups: {sum(1 for n in c.values() if n>1)} (expect 6)')
print(f'simulated dup key refs: {sum(n for n in c.values() if n>1)} (expect 12)')
"

# 4. DECISION authorizes 4-test scope exception extension to alias file
grep -E "test_alias_entry_count_grew_by_34|test_hebrew_value_collision|test_alias_spot_check" \
  _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md | head -5

# 5. validate_aos.sh
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## 4. Output

`_COMMUNICATION/TEAM_190/SFA-S003-P002-WP-B1-patch06/LOD400-VERDICT_v1.0.0.md`

Commit: `gate(WP-B1-patch06/L-GATE_S): team_190 verdict — <RESULT>` Co-Authored-By GPT-5.5.

PASS/PWF → team_110 holds patch06 build until patch04 LOD500_LOCKED. Then dispatches Sonnet.
FAIL → R2.

---
