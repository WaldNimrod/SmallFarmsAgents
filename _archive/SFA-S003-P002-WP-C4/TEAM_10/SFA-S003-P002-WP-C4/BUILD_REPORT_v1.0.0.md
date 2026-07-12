---
id: BUILD_REPORT_SFA-S003-P002-WP-C4_v1.0.0
from: team_10 (sfa_build)
to: team_00, team_190
date: 2026-05-27
wp: SFA-S003-P002-WP-C4
gate: L-GATE_B complete — ready for team_190 L-GATE_V
---

# BUILD_REPORT — WP-C4 Web Sources Integration

## Migration renumbering note

LOD400 specified migrations **050–052**. WP-C1 already owns **049** (`crop_planting_calendar`) and **050** (`crop_cover_crops`). C4 implemented:

| Revision | File | Purpose |
|----------|------|---------|
| — (skipped) | — | LOD400 §3.1 no-op region doc → `planting_calendar.py` docstring only |
| **051** | `051_crop_companion_matrix.py` | `crop_companion_matrix` |
| **052** | `052_crop_postharvest_storage.py` | `crop_postharvest_storage` |

## Deliverables

| Artifact | Path |
|----------|------|
| Download harness | `scripts/download_web_sources.py` |
| Web importers (×8) | `organic_market_agent/crop_book/importer/web/` |
| ORM | `companion_matrix.py`, `postharvest_storage.py` |
| Tests (27) | `tests/crop_book/test_c4_*.py` |
| URL audit | `URL_AUDIT_v1.0.0.md` |
| License audit | `LICENSE_AUDIT_v1.0.0.md` |
| JSON extracts | `data/external_sources/web/*/extract.json` |

## Live ingestion summary (`seed --c4-only`, 2026-05-27)

| Source | Rows parsed | Upserted | Target |
|--------|------------:|---------:|--------|
| il_moa_calendar | 60 | 56 | `crop_planting_calendar` (NI) |
| uc_anr_germination | 20+ | 57 | `crop_variety_source_values` |
| osu_frost_tolerance | 21 | 21 | SV `frost_tolerance_class` |
| umd_soil_ph | 32 | 36 | SV pH fields |
| ne_veg_guide_nutrients | 15 | 65 | SV NPK kg/ha |
| seeds_per_gram | 62 | 26 | SV `seeds_per_gram` |
| uf_ifas_companion | 31 | 29 | `crop_companion_matrix` |
| uc_davis_postharvest | 45 | 32 | `crop_postharvest_storage` |

**DB counts after run:** IL calendar NI rows **56**; companion pairs **29**; postharvest **32**.

## Cross-validation log (frost / seeds)

- **Frost:** OSU + CSU + UMN extracts merged; 2/3 consensus or most-tender default (see `osu_frost_tolerance` reconcile notes in source values).
- **Seeds/gram:** Vital + Osborne; >20% diff logged (e.g. Carrot, Lettuce, Tomato).

## Acceptance criteria matrix

| AC | Status | Evidence |
|----|--------|----------|
| AC-C4-01 | PASS | Migrations 051–052 applied; `test_c4_migrations.py` |
| AC-C4-02 | PASS | 10/14 URLs cached (71%) — `URL_AUDIT_v1.0.0.md` |
| AC-C4-03 | PASS | ≥20 germination crops; °F→°C spot test in `test_c4_uc_anr_germination.py` |
| AC-C4-04 | PASS | ≥15 frost classes; `test_c4_osu_frost_tolerance.py` |
| AC-C4-05 | PASS | ≥30 soil pH rows |
| AC-C4-06 | PASS | ≥15 NPK crops |
| AC-C4-07 | PASS | 56 IL NI calendar rows (≥30) |
| AC-C4-08 | PASS | Hebrew in `extract.json` without `\\u` escapes — `test_c4_il_moa_calendar.py` |
| AC-C4-09 | PASS | ≥10 seeds/gram; cross-val notes present |
| AC-C4-10 | PASS | 29 companion pairs; all `evidence_strength=weak` |
| AC-C4-11 | PASS | 32 postharvest rows (≥30) |
| AC-C4-12 | PASS | `crop_field_enrichment` populated for new fields (germination, pH, NPK, seeds) |
| AC-C4-13 | PASS | NI sources override C1 on same `(crop_id, activity_type)` upsert keys |
| AC-C4-14 | PASS | `--c4-only` / `--no-c4` wired; `test_seed_cli.py` patched |
| AC-C4-15 | PASS | 27 new tests; 403 crop_book tests pass (0 regressions) |
| AC-C4-16 | PASS | `validate_aos.sh` 29 PASS / 19 SKIP / 0 FAIL |
| AC-C4-17 | PASS | No LOD500_LOCKED files modified |
| AC-C4-18 | PASS | `URL_AUDIT_v1.0.0.md` filed |
| AC-C4-19 | PASS | `LICENSE_AUDIT_v1.0.0.md` filed |
| AC-C4-20 | PASS | This report |

## Validation commands

```bash
alembic current   # 052 (head)
python3 -m pytest tests/crop_book/test_c4_*.py -q
python3 -m organic_market_agent.crop_book.importer.seed --c4-only
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

## Routing

Builder complete (IR#1). **team_190** (non-Claude) → L-GATE_V. Do not self-validate.
