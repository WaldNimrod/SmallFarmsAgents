---
id: SFA-S003-P002-WP-B1-patch06-LOD200
wp: SFA-S003-P002-WP-B1-patch06 — JMF_CROP_MAP cleanup (remove 27 cultivars+typos)
gate: L-GATE_S (LOD200)
status: PRE_LOD400
author: team_110
date: 2026-05-25
version: v1.0.0
parent_wp_chain:
  - SFA-S003-P002-WP-B1-patch03 (LOD500_LOCKED — last taxonomy)
  - SFA-S003-P002-WP-B1-patch04 (in-flight — populates crop_varieties first)
team_00_decision_ref: _COMMUNICATION/team_00/DECISION_WP-B1-patch04-patch06_INTEGRATION-CLEANUP_2026-05-25_v1.0.0.md
depends_on: [SFA-S003-P002-WP-B1-patch04]
validator: team_190 (GPT-5.5)
builder: team_10 (Sonnet sub-agent)
---

# LOD200 — patch06: JMF_CROP_MAP Cleanup

## 1. Mission

Apply the "baselines-only" policy (DECISION §1) to `JMF_CROP_MAP`: remove 22 cultivar entries + 5 typo entries. Net: 87 → **60 entries**. Update LOCKED tests to match the new shape: 24 duplicate-target groups → **6 groups** (all pure synonyms).

## 2. In-scope

### 2.1 JMF_CROP_MAP removals (27)
**22 cultivars (C):** Baby kale, Bell Pepper, Cauliflower / Romanesco, Fall Cabbage, Fresh Carrots, Greenhouse English Cucumber, Greenhouse Libanese Cucumber, Hakurei Turnip, Leek Storage, Leek Summer, Mesclun, Mini Celery Root, Mini Fennel, Roma Tomato, Salad Mix, Salanova Lettuce, Savoy Cabbage, Storage Onion, Sucrine, Summer Cabbage, Winter Radish, Zucchini.

**5 typos (D):** Brussel Sprouts, Eggplant  (Feld), Raddish, Spinach TR, Spinarch SD.

### 2.2 LOCKED test updates (LOD500_LOCKED scope exception)
- `test_jmf_crop_map.py::test_jmf_crop_map_count` — `expected_total: 87` → `60` (post-patch04 baseline)
- `test_jmf_crop_map.py::test_jmf_crop_map_duplicate_target_allowlist` — 24-group dict → **6-group dict** (just the 6 synonym pairs)
- `test_jmf_crop_map.py::test_ac03_duplicate_group_count` — assert `24` → `6`
- `test_jmf_crop_map_aliases.py::test_alias_spot_check_five_samples` — REMOVE the 4 spot-check entries that target removed keys (Brussel Sprouts, Pak Choi, Swiss Chard, Eggplant (Feld)) and the 5th (Greenhouse Cherry Tomato — still present as baseline, value `עגבניית שרי`) — repurpose the test to check 5 synonym aliases instead
- `test_jmf_crop_map_aliases.py::test_alias_entry_count_grew_by_34` — REMOVE this test entirely (the "34 aliases" concept no longer holds post-cleanup)
- `test_jmf_crop_map_aliases.py::test_hebrew_value_collision_set_has_24_groups` (renamed in patch03) — `24` → `6`; rename to `test_hebrew_value_collision_set_has_6_groups`

### 2.3 New regression tests (3-5)
- `test_no_cultivar_keys_in_map_post_patch06` — assert that no patch06-removed key is present
- `test_no_typo_keys_in_map_post_patch06` — same for typos
- `test_six_synonym_groups_exact` — explicit allowlist of the 6 remaining synonym groups

### 2.4 Cleanup of `crops` table orphans
`scripts/patch06_db_cleanup.py` (idempotent + dry-run):
- DELETE / MERGE any `crops` row whose `name_he` matches a value that's no longer reachable from the cleaned MAP
- Specifically the patch03 anomaly: row with `name_he = 'מלפפון חממה'` — if exists, MERGE its associations into `crops` row of `מלפפון`

### 2.5 CHANGELOG.md entry

## 3. Out-of-scope
- Modifications to `crops`/`crop_varieties` data — that was patch04's job
- Adding new entries to JMF_CROP_MAP — none
- Schema changes — none (Migration 047 already in patch04)
- Operational SQL fixes for end users — none (patch06_db_cleanup.py is the automated path)

## 4. Dependencies
- patch04 BUILD complete (cultivars must exist in `crop_varieties` before their keys can be removed from MAP). LOD200+LOD400 of patch06 can be authored + L-GATE_S validated in parallel with patch04's L-GATE_S.

## 5. LOD500_LOCKED scope exceptions
- `tests/crop_book/test_jmf_crop_map.py` — 3 LOCKED tests updated (count + allowlist + ac03_count)
- `tests/crop_book/test_jmf_crop_map_aliases.py` — 3 LOCKED tests updated (spot-check repurposed; growth_by_34 removed; collision rename) — extends the patch03 R3+R4 scope exception precedent
- `organic_market_agent/crop_book/constants.py` — 27-line removal block in `JMF_CROP_MAP` literal

Per DECISION §3.

## 6. AC + test count targets
- ACs: ~15 (1 per category removal + 6 per LOCKED test transition + 3 per cleanup script + 5 hygiene)
- Tests touched: ~6 LOCKED updated + 3 new regression = 9

## 7. Builder
team_10 (Sonnet sub-agent). MEDIUM scope but high LOCKED-touch surface — requires multi-round validation.

## 8. Sequencing
patch06 BUILD STRICTLY AFTER patch04 BUILD complete. Pre-build verification: run patch04's `load_masterclass_sheets.py` to confirm all 22 cultivars are in `crop_varieties` (so no data-loss when removed from MAP).

---

*LOD200 v1.0.0 — 2026-05-25.*
