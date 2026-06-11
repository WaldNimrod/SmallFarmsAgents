# VALIDATION_MANDATE — SFA-S003-P004-WP-CB-SRC-SWEEP (unified) — team_100 → team_190 — v2.0.0

**Date:** 2026-06-11
**From:** team_100 (Claude Code, builder)
**To:** team_190 (constitutional validator) — **MUST run on a non-Claude engine** (Cursor / Codex / Desktop) per Iron Rule #1/#5
**Gate:** L-GATE_VALIDATE
**Branch / HEAD:** `feat/wp-cb-src-sweep` @ **`dfea7e6`** (7 commits; supersedes the v1.0.0 mandate @ 0e0edbd)

## Why this mandate
team_100 (Claude Code) is the builder and CANNOT issue the constitutional L-GATE_VALIDATE verdict for its own
work. Build + deploy + integrity are complete; the only remaining canonical step is an independent cross-engine
PASS → then archive + roadmap `LOD500_LOCKED`.

## Scope — ONE unified verdict for the whole branch
The branch bundles two efforts (team_00 directed the second mid-flight); validate them together:
- **A) WP-CB-SRC-SWEEP** — source-data tail integration: L39 mesclun variety + L45 base-data cherry-pick;
  publisher `--crop-ids` scoping; post-seed derived-field strip.
- **B) Crop-taxonomy + data-integrity remediation** (team_00 2026-06-10) — dedup the crops the re-seed
  surfaced; prevent recurrence; fix the uc_davis postharvest misalignment.

## ⚠ History (two issues already found & fixed — context for the validator)
1. **R2 (AC-05):** the first validate FAILed `test_ac05_derived_fields` because `seed --all` reintroduced
   forbidden DERIVED fields (the canon `phase4` strip wasn't run). Fixed two ways: (a) stripped the live DB,
   (b) `seed --all` now auto-strips them (commit `20b8998`). **Validator: run against the CURRENT DB; do NOT
   `seed --all` first — if you do, the auto-strip handles it (or run `canon.migrate phase4`).**
2. **Postharvest misalignment:** `uc_davis_postharvest` paired a parallel `he_labels[]` list positionally with
   `samples[]` (misordered + broken padding) → 31 crops had wrong storage data. Fixed structurally
   (commit `dfea7e6`); local DB + production corrected.

Production was never exposed to the derived fields (not in the publish whitelist).

## Verification cases (re-execute independently at HEAD `dfea7e6`)

**Build / integrity**
1. **VC-1** `python -m pytest tests/crop_book -q` → **797 pass / 1 skip / 1 known-fail**
   (`test_wp_upload_crop_book::test_dispatch_upload_crop_book_profile` — PRE-EXISTING, retired www tier;
   identical on clean `main`). `test_ac05_derived_fields` (8 cases) PASSES.
2. **VC-2** `cd sfa_delivery && php vendor/bin/phpunit` (copied vendor) → 233 pass / 0 fail.
3. **VC-3** `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` → 0 FAIL.

**A — SRC-SWEEP content**
4. **VC-4** L39: crop #31 (`עלי בייבי`) has variety `חסה בייבי` (name_en set) + `cultivar_recommendation`
   source value (`NI:jmf_ft_mesclun_v1`) + 4 internal species notes.
5. **VC-5** L45: `OP:il_farm_2017_l45` source-values for days_to_maturity/spacing_in_row_cm/rows_per_bed
   (62 rows) + 22 internal notes / 22 crops; cannabis/price/budget/trees/calendar sheets NOT integrated
   (`scripts/extract_l45_basedata.py` documents the exclusion).
6. **VC-6** License firewall: `crop_knowledge_notes` is NOT in `sfa_ingest_push.py` `_AGRONOMY_FIELD_WHITELIST`;
   internal notes ("Salanova", L45 cultural text) absent from production HTML.
7. **VC-7** Publisher scoping: `--crop-ids` filters crop-keyed tables only; products/cover_crops excluded;
   ambiguous `--slugs` raises.

**B — Taxonomy / data-integrity**
8. **VC-8** Dedup (team_00 "different product = different crop"): name maps resolve the duplicates to canonical
   crops — `Basil→בזיל`, `Rutabaga→לפת`, `Salad Mix→עלי בייבי`, `Greenhouse Heirloom Tomato→עגבנייה`
   (`constants.py`); keep-crops (Celeriac/Chinese Cabbage/Hot Pepper/Brussels Sprouts) created with correct
   `name_en` + sibling family (`jmf_masterclass._KEEP_CROP_IDENTITY`). `tests/crop_book/test_seed_taxonomy_fix.py`
   proves no duplicate is minted. Live DB: **73 crops, 0 duplicate-name crops**; merged cultivars preserved
   (Aroma 2 F1 + Nufar on בזיל #4, Joan on לפת #51).
9. **VC-9** `seed --all` auto-strips the 5 forbidden DERIVED fields post-seed (`strip_derived_fields`,
   `--no-strip-derived` escape hatch) — a re-seed stays AC-05 clean.
10. **VC-10** `uc_davis_postharvest`: `name_he` bound intrinsically per sample row (no parallel `he_labels[]`,
    no padding loop); 31 crops carry CORRECT storage (peas 0–2°C/7–10d, cilantro 0–2/7–14d, broccoli 0–2/10–14d,
    basil 12–15/5–10d — not the prior tomato/potato/garlic mis-attributions).
11. **VC-11** `documentation/03-data-and-schema/DATA_INTEGRITY_CANON.md` present (the integrity runbook).

**Production (deployed, scoped)**
12. **VC-12** `https://sfa.nimrod.bio` healthy: `api/v1/crops` count = **70** (no stale/duplicate crops);
    salad-mix variety count 13; בזיל variety count 10 + לפת 3 (cultivars live); postharvest correction live
    (cilantro page no longer shows 90–180-day shelf life); `qa_probe.mjs` overflow=false mobile+desktop on
    salad-mix / basil / cilantro.

## Still deferred (NOT blockers for this verdict)
- 3 thin keep-crops (celeriac/chinese-cabbage/hot-pepper) held from production until enriched — local-only.
- `idan_planner.py` still EMITS `yield_per_m2_kg` (now neutralised by the auto-strip) — low-priority source cleanup.

## On PASS
team_100 closure protocol: archive mandate (team_191 `ARCHIVE_MANIFEST.md`) → roadmap `LOD500_LOCKED`.
