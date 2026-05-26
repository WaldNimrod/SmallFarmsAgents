---
id: MANDATE_SFA-S003-P002-WP-C2_BUILDER_v1.0.0
from: team_00 (via team_10 spec-author session)
to: sfa_build (team_10 builder, separate fresh session)
date: "2026-05-26"
type: BUILDER_MANDATE
wp: "SFA-S003-P002-WP-C2"
project: smallfarmsagents
branch: main
gate: L-GATE_B
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C2/LOD400_spec.md"
lod200_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C2/LOD200_spec.md"
pattern_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md"
status: ACTIVE
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gate: "L-GATE_S PASS 2026-05-26 by team_10 (spec authoring under team_00 grant)"
expected_validator: "team_190 (non-Claude per IR#1) — L-GATE_V after BUILD complete"
parallel_with: "SFA-S003-P002-WP-C3 (active in separate session) — disjoint scopes, safe to run concurrently"
sibling_completions:
  - "WP-C1 LOD500_LOCKED at ccd14d2 (engine v1.1 inheritance shipped)"
  - "WP-C4 LOD500_LOCKED at 27f6152 (web sources from multi-engine team_80)"
---

# Builder Mandate — SFA-S003-P002-WP-C2 (Wave 2: Hebrew Narrative NI Extraction)

> **Activation gate**: L-GATE_B. team_190 validates post-build at L-GATE_V.
> **Parallel**: WP-C3 builder runs in separate session — disjoint scopes.

---

## §1 Mission (1-paragraph)

Apply the WP-B2 NIImporter pattern to 7 Hebrew + JMF authoritative sources.
LLM-assisted extraction (Anthropic API, one-time prepare with caching)
of per-crop narrative knowledge into the existing `crop_knowledge_notes`
table + extended `note_type` enum. **CRITICAL Hebrew source**: L02 AOSNOT
(1.3MB Hebrew per-crop encyclopedia with ~30-50 crops) — closes the
biggest narrative gap (currently 23/57 crops covered → target 50+/57).
Plus official שה"ם variety trials, Dr. Zacks hydro survey, JMF FT extensions.

## §2 Spec references (READ IN ORDER)

1. **`_aos/work_packages/S003/SFA-S003-P002-WP-C2/LOD400_spec.md`** — full build spec (PRIMARY)
2. `_aos/work_packages/S003/SFA-S003-P002-WP-C2/LOD200_spec.md` — scope context
3. **`_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md`** — NIImporter pattern reference (MUST mirror)
4. `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` — engine reference
5. `_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md` — sister WP pattern (for CLI / source_registry style)
6. `data/external_sources/INDEX.md` — source catalog
7. `data/external_sources/raw_text/israeli__L02_AOSNOT_variety_info.txt` — pre-extracted Hebrew text sample
8. `data/external_sources/raw_text/israeli__L11_variety_trials_2021.txt` — שה"ם official
9. `data/external_sources/raw_text/israeli__L09_hydro_vegetable_guide.txt` — Hebrew hydro
10. `data/external_sources/raw_text/israeli__L10_DR_ZACKS_leafy_hydro_survey.txt` — Hebrew survey
11. `data/external_sources/raw_text/jmf_extension__L14_FT_FINALE_NURSERYSEEDING.txt`
12. `data/external_sources/raw_text/jmf_extension__L16_seeding_in_cell_flats.txt`
13. `data/external_sources/raw_text/jmf_extension__L13_cover_crops_guide.txt`
14. `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md` — sister build precedent
15. `CLAUDE.md` — spoke conventions

## §3 Acceptance criteria (full matrix in LOD400 §6)

12 ACs targeting: migration 053 clean fwd/bwd; L02 AOSNOT ≥20 crop JSONs;
per-crop field coverage ≥80% of cached JSONs for frost_tolerance,
israeli_regions, flowering_date; L11 ≥5 lettuce variety trial scores;
L09 ≥10 crops classified for hydro suitability; L10 production benchmarks;
L14+L16+L13 JMF FT extracted per crop; all extractions cached; Hebrew
preserved (no `\uXXXX` escapes); NI hard-override semantics preserved;
≥15 tests; validate_aos.sh 29/19/0.

## §4 Build sequence (8 steps from LOD400 §8)

1. **Migration 053** (`053_extend_ckn_note_type.py`) — extend
   `crop_knowledge_notes.note_type` CHECK constraint with 6 new enum values:
   `frost_tolerance`, `flowering_date`, `pollination_mechanism`,
   `israeli_regions`, `variety_trial_score`, `hydro_suitability`.
   NOTE: head is currently 052 (WP-C4's last). Use `down_revision = "052"`.
   See LOD400 §3 for the exact DDL.
2. Build `scripts/extract_jmf_he.py` (multi-source dispatcher).
   Calls Anthropic API for per-crop chunked extraction → JSON cache.
   Budget cap: $20 (log token cost to `data/external_sources/extracted/_extraction_log.json`).
3. Run extraction for L02 (HIGHEST priority — largest source). Validate output.
4. Build `organic_market_agent/crop_book/importer/ni/aosnot_variety_info.py`
   + 5 tests (mirrors WP-B2 pattern; see LOD400 §4 for exact code skeleton).
5. Run extraction + build importers for L11, L09, L10, L14, L16, L13.
6. Wire into `seed.py`: add `--c2-only`, `--no-c2`, `_run_c2_ingestion()`.
   APPEND to existing CLI (don't overwrite C1/C4 entries).
7. Full focused test pass (≥15 tests). Live ingestion. validate_aos.sh.
8. Write `_COMMUNICATION/team_10/SFA-S003-P002-WP-C2/BUILD_REPORT_v1.0.0.md`
   + `EXTRACTION_LOG_v1.0.0.md` (token cost + per-source row counts).

## §5 Iron Rule compliance (CRITICAL)

| IR | What you must do |
|----|------------------|
| **IR#1** | BUILDER = Claude (you). team_190 (non-Claude, GPT-5+) validates. DO NOT self-validate. |
| **IR#4** | Do NOT edit `_aos/roadmap.yaml`. |
| **IR#6** | Inter-team artifacts via `_COMMUNICATION/team_10/SFA-S003-P002-WP-C2/`. |
| **IR#7** | DB schema changes ONLY via alembic migration 053. |
| **IR#11** | Never touch `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. |
| **IR#12** | NEVER invoke `/AOS_gov-update` or `/AOS_gov-sync`. |
| **LOD500_LOCKED** | Never modify: `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py`, `db/versions/001..052_*.py`, `mu-plugin/`, `tend.py`, `models.py`, `reconciler.py` (engine v1.1 is FINAL), `enrichment_runner.py` (uses inheritance helper — FINAL). |

## §6 Engine v1.1 inheritance — already shipped (do NOT modify)

**Sister WP-C1 R2 introduced** `collect_source_values_with_inheritance` in
`reconciler.py`. This is the variety→species inheritance helper. It applies
to BOTH production reconciliation AND calibration shadow run.

For WP-C2:
- Your NIImporters add rows to `crop_knowledge_notes` (not `crop_variety_source_values`)
- `crop_knowledge_notes` is queried directly (no reconciliation logic)
- Therefore inheritance is NOT relevant to your C2 build
- BUT: when you also write to `crop_variety_source_values` (for the
  `cultivar_recommendation` exception per WP-B2 §6), the existing engine
  will apply inheritance automatically — no special handling needed

## §7 Completion criteria (BUILD_REPORT checklist)

- [ ] All 12 ACs from LOD400 §6 verified
- [ ] ≥15 new tests passing
- [ ] Existing tests: 0 new failures (47 reconciler/enrichment + 31 WP-C1 + 27 WP-C4 = 105 baseline)
- [ ] `validate_aos.sh` 29/19/0
- [ ] L02 AOSNOT cached JSONs: ≥20 in `data/external_sources/extracted/aosnot/`
- [ ] Per-crop field coverage ≥80% for: frost_tolerance, israeli_regions, flowering_date
- [ ] L11 variety_trial_score ≥5 lettuce varieties
- [ ] L09 hydro_suitability ≥10 crops
- [ ] L14+L16+L13 JMF FT extracted (nursery_specific, growing_tip per crop)
- [ ] Hebrew preservation verified (no `\uXXXX` escapes in JSON cache or DB)
- [ ] NI hard-override semantics preserved (verify in DB query)
- [ ] `crop_knowledge_notes` total grows from 54 → 200+ (target)
- [ ] EXTRACTION_LOG documents Anthropic API token cost (cap $20)
- [ ] BUILD_REPORT filed with per-source counts + Hebrew encoding verification
- [ ] LOD500_LOCKED inventory check passes
- [ ] Commits on `main` with co-author trailer

## §8 Parallel-with-WP-C3 file-scope safety

WP-C3 builder runs concurrently in another session. Disjoint scopes:

| Resource | WP-C2 owns | WP-C3 owns | Conflict? |
|----------|------------|------------|:---------:|
| Migrations | **053** (extend ckn enum) | NONE (uses existing tables) | ✅ No |
| Importer dirs | `importer/ni/aosnot_*`, `ni/sham_*`, `ni/zacks_*`, `ni/jmf_ft_*` | `importer/urban_farmer/`, `importer/israeli/idan_seedlings_*`, `importer/israeli/franchi_*` | ✅ No |
| External sources used | `data/external_sources/raw_text/*.txt` + `data/external_sources/extracted/*` (NEW JSON cache) | `data/external_sources/urban_farmer/*.{xlsx,jpg}` + `data/external_sources/israeli/L05a/b/49.xlsx` | ✅ No |
| Scripts | `scripts/extract_jmf_he.py` | `scripts/ocr_curtis_images.py` | ✅ No |
| `constants.py` | (no changes expected) | `succession_interval_weeks` references | ⚠️ Read-only |
| `source_registry.py` | append 7 NI:* entries | append 4-5 OP:* entries | ⚠️ Same file — **APPEND only** |
| `seed.py` CLI | append `--c2-only/--no-c2` + `_run_c2_ingestion()` | append `--c3-only/--no-c3` + `_run_c3_ingestion()` | ⚠️ Same file — **APPEND only** |
| `requirements.txt` | possibly `anthropic` SDK (if not present) | possibly `tesseract`/`pillow` (if OCR uses local) | ⚠️ Same file — **APPEND only** |

**Shared-file protocol** (same as C1/C4 parallel):
- `git pull --rebase origin main` before EVERY commit
- If shared-file conflict in constants.py / source_registry.py / seed.py /
  requirements.txt: both edits are ADDITIVE → keep BOTH sets, re-run focused tests
- If non-shared file conflict → unexpected → STOP and file INQUIRY

## §9 What you must NOT do

- Do NOT write to `_aos/`
- Do NOT edit `_aos/roadmap.yaml`
- Do NOT modify LOD500_LOCKED files (see §5 — list INCLUDES reconciler.py and enrichment_runner.py post-engine-v1.1)
- Do NOT skip the L02 AOSNOT extraction (it's the CRITICAL Hebrew encyclopedia)
- Do NOT publish raw prose from L02 (DOCX) — extract narrative SNIPPETS only,
  bounded to 2000 chars per row per WP-B2 §5.4. AOSNOT is Hebrew web content;
  fair-use snippets only.
- Do NOT exceed $20 Anthropic API budget without team_00 approval — STOP and
  file INQUIRY before continuing
- Do NOT issue your own L-GATE_V verdict (IR#1)
- Do NOT overwrite WP-C3 entries in shared files (constants.py,
  source_registry.py, seed.py, requirements.txt) — APPEND only
- Do NOT touch files in `data/external_sources/urban_farmer/` or
  `data/external_sources/israeli/L05a*/L05b*/L49*` (WP-C3 territory)

## §10 Routing post-build

1. File BUILD_REPORT + EXTRACTION_LOG
2. Report path to user (team_00)
3. team_00 (or follow-up team_10 session) files MANDATE_L-GATE_V to team_190
4. team_190 issues verdict (PASS / FAIL / PASS_WITH_FINDINGS)
5. If PASS: roadmap transition to LOD500_LOCKED (team_00 authority)
6. If findings: remediation cycle

---

*Builder mandate issued 2026-05-26 by team_10 (spec-author session) on
behalf of team_00 program grant. Activation prompt at:
`_COMMUNICATION/team_10/SFA-S003-P002-WP-C2/ACTIVATION_PROMPT.md`*
