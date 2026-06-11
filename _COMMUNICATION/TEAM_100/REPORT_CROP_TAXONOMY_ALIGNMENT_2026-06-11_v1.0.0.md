# REPORT — Crop Taxonomy Alignment + Recurrence Prevention — team_100 — v1.0.0

**Date:** 2026-06-11
**Author:** team_100
**Type:** REPORT (data-integrity remediation; follow-up to SFA-S003-P004-WP-CB-SRC-SWEEP findings)
**Trigger:** team_00 directive 2026-06-10 — fix the duplicate crops surfaced by the re-seed; align both DBs;
prevent recurrence; document the integrity discipline.

## 1. Root cause

A full `seed --all` (run during WP-CB-SRC-SWEEP) minted duplicate crops from **non-canonical name maps**
(`JMF_CROP_MAP`/`TEND_CROP_MAP` mapping a crop to a Hebrew name that doesn't match the canonical crop) and
left forbidden DERIVED fields (no canon strip). Production was never affected (it had only the clean 70 crops;
duplicates were local-only re-seed artifacts).

## 2. Taxonomy decisions (team_00)

Rule: **"different agricultural product = different crop"**, even if the same botanical species.

| Crop | Ruling | Action |
|------|--------|--------|
| סלרי שורש (Celeriac) | separate crop | keep — name_en=Celeriac, family=Apiaceae |
| כרוב סיני (Chinese Cabbage) | separate crop | keep — name_en, family=Brassicaceae |
| פלפל חריף (Hot Pepper) | separate crop | keep — name_en, family=Solanaceae |
| כרוב ניצנים (Brussels Sprouts) | separate crop | mapping already correct; no data yet (non-issue) |
| רוטבגה (Rutabaga) | = לפת (Turnips) | merge → לפת #51 |
| בזיליקום (Basil) | = בזיל | merge → בזיל #4 |
| תערובת סלט (Salad Mix) | = עלי בייבי | merge → עלי בייבי #31 |
| עגבניות מורשת (Heirloom Tomato) | variety-type, NOT a crop | merge → עגבנייה #49 (reversed patch03 split) |

## 3. What was done

**Recurrence prevention (code — committed `20b8998`, `9d33099`):**
- `constants.py`: `JMF_CROP_MAP` Basil→בזיל, Rutabaga→לפת, Heirloom→עגבנייה; `TEND_CROP_MAP` Salad Mix→עלי בייבי;
  IL/OpenAI basil aliases→בזיל. The 4 duplicates now resolve to canonical crops (no minting).
- `jmf_masterclass.py`: keep-crops created with correct name_en + sibling family (`_KEEP_CROP_IDENTITY`),
  not the 'Unknown' placeholder.
- `seed.py`: `strip_derived_fields()` auto-runs on `--all` (deletes the 5 canon-forbidden DERIVED fields from
  both tables) with a `--no-strip-derived` escape hatch — closes the AC-05 gap.
- Tests: `test_seed_taxonomy_fix.py` (resolution + keep-crop identity + derived strip) + updated crop-map
  synonym-group tests. Suite **797 pass / 1 skip / 1 pre-existing** (`wp_upload`, retired tier).

**Local DB aligned (single-writer, me): 77 → 73 crops.**
- Merged 4 duplicates, **preserving real cultivars** by re-parenting their varieties to canonical: Aroma 2 F1
  + Nufar → בזיל #4; Joan → לפת #51; heirloom variety → עגבנייה #49; תערובת סלט #95 (redundant copy of #31) removed.
- Keep-crops #90/#91/#93 given correct name_en + sibling family.
- AC-05 clean; 0 leftover duplicates.

**Production (team_00 chose "canonical fixes only"):**
- Pushed בזיל #4 + לפת #51 (scoped `--crop-ids`, HTTP 200, 0 rejected). Smoke PASS: basil variety count 8→10,
  turnips 2→3, qa_probe overflow=false mobile+desktop, prod crop count still **70** (dup-free).
- **HELD** the 3 thin keep-crops (celeriac/chinese-cabbage/hot-pepper) from production until they have adequate
  data — publishing near-empty crop pages would degrade the live product. They exist in local (73 crops).

**Documentation:** `documentation/03-data-and-schema/DATA_INTEGRITY_CANON.md` (runbook) + project memory
(`project_crop_taxonomy_rule`, `feedback_sfa_seed_deploy_baseline_drift`).

## 4. Open / follow-up
- 3 thin keep-crops are local-only, pending data enrichment before they're published to prod.
- `idan_planner.py` still EMITS the derived `yield_per_m2_kg` (the post-seed strip now guards it); a cleaner
  fix is to stop emitting it. Low priority.
- This effort was executed under team_00 direct directive; it can be formalized as its own WP if desired.
