---
id: MANDATE_SFA-S003-P002-WP-C3_BUILDER_v1.0.0
from: team_00 (via team_10 spec-author session)
to: sfa_build (team_10 builder, separate fresh session)
date: "2026-05-26"
type: BUILDER_MANDATE
wp: "SFA-S003-P002-WP-C3"
project: smallfarmsagents
branch: main
gate: L-GATE_B
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD400_spec.md"
lod200_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD200_spec.md"
status: ACTIVE
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gate: "L-GATE_S PASS 2026-05-26 by team_10 (spec authoring under team_00 grant)"
expected_validator: "team_190 (non-Claude per IR#1) — L-GATE_V after BUILD complete"
parallel_with: "SFA-S003-P002-WP-C2 (active in separate session) — disjoint scopes, safe to run concurrently"
sibling_completions:
  - "WP-C1 LOD500_LOCKED at ccd14d2 (engine v1.1 inheritance shipped; Idan_2017 + Tend baseline)"
  - "WP-C4 LOD500_LOCKED at 27f6152 (web sources from multi-engine team_80)"
---

# Builder Mandate — SFA-S003-P002-WP-C3 (Wave 3: Curtis OCR + Backlog Sweep)

> **Activation gate**: L-GATE_B. team_190 validates post-build at L-GATE_V.
> **Parallel**: WP-C2 builder runs in separate session — disjoint scopes.

---

## §1 Mission (1-paragraph)

Ingest secondary sources requiring OCR or comparative analysis: Curtis
Stone (Urban Farmer) master chart XLSX + 34 scanned book pages OCR;
Idan's seedling succession patterns (L05a/L05b); FRANCHI Italian seed
catalog (L06 sheet 2). Resolve the Idan 2018 update vs L03/L04 (2017)
diff. Settle the Tend 2018 inclusion question (LOW row volume year).
**No new DB tables** — uses existing `crop_variety_source_values` and
`crop_knowledge_notes` tables. Smaller WP than C2; OCR pipeline is the
main technical risk.

## §2 Spec references (READ IN ORDER)

1. **`_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD400_spec.md`** — full build spec (PRIMARY)
2. `_aos/work_packages/S003/SFA-S003-P002-WP-C3/LOD200_spec.md` — scope context
3. `_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md` — sister WP, importer pattern
4. `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` — engine reference
5. `data/external_sources/INDEX.md` — source catalog
6. `data/external_sources/sample_extracts/urban_farmer__L40_curtis_crop_profiles.txt` — Curtis master chart preview
7. `data/external_sources/sample_extracts/israeli__L05a_IDAN_seedlings_winter_18-19.txt` — Idan succession winter
8. `data/external_sources/sample_extracts/israeli__L05b_IDAN_seedlings_summer_18-19.txt` — Idan succession summer
9. `data/external_sources/sample_extracts/israeli__L06_covers_and_tunnels.txt` — FRANCHI catalog in sheet 2
10. `data/external_sources/sample_extracts/israeli__L49_IDAN_market_gardening_tech.txt` — Idan 2018 update
11. `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md` — sister precedent + Idan_2017 baseline
12. `CLAUDE.md` — spoke conventions

## §3 Acceptance criteria (full matrix in LOD400 §5)

10 ACs targeting: L40 Curtis master chart ≥20 source_value rows; L41 OCR
≥30 cached JSONs (≥88% of 34 images); Curtis OCR narrative ≥10 crops in
`crop_knowledge_notes`; L05a+L05b succession intervals ≥8 crops; L06 FRANCHI
29 variety references; L49 diff report + non-duplicate upserts; Tend 2018
decision documented; reconciler blend stability (no regression in CALIBRATED
count); ≥12 tests; validate_aos.sh 29/19/0.

## §4 Build sequence (14 steps from LOD400 §6)

1. **No migrations** — all upserts hit existing tables
   (`crop_variety_source_values`, `crop_knowledge_notes`).
2. **OCR pipeline**: `scripts/ocr_curtis_images.py`. Decision per LOD400 §4.2:
   **Anthropic Vision API** (34 images × ~$0.05 = ~$1.70, well under $5 cap;
   quality > tesseract for scanned book pages).
   Tesseract fallback if Anthropic unavailable.
   Output: `data/external_sources/extracted/curtis_ocr/L41_curtis_chart_NN.json`
   per image, with structured fields {crop, planting_specs, varieties, dtm,
   avg_yield_per_bed, narrative_text}.
3. Run OCR for all 34 Curtis images. Validate ≥30 succeeded.
4. Build `organic_market_agent/crop_book/importer/urban_farmer/__init__.py` + `_shared.py`.
5. Build `urban_farmer/curtis_profiles_importer.py` (L40 XLSX → OP tier
   source_value rows with `source='OP:CurtisStone'`). 3 tests.
6. Build `urban_farmer/curtis_ocr_importer.py` (reads cached OCR JSON →
   NI tier `crop_knowledge_notes` rows with `source='NI:curtis_stone_book'`).
   2 tests.
7. Build `organic_market_agent/crop_book/importer/israeli/idan_seedlings_importer.py`
   — derive `succession_interval_weeks` from L05a/b bi-weekly tray-order
   patterns. 2 tests. **Verify `succession_interval_weeks` is a known field
   in crop_varieties** (check via `\d crop_varieties` or models.py); if NOT,
   downgrade scope + document in BUILD_REPORT (per LOD400 §3 risk note).
8. Build `israeli/franchi_catalog_importer.py` (L06 sheet 2 → variety
   provider references). 1 test.
9. Build `israeli/idan_2018_diff.py` — diff L49 vs L03/L04. Upsert only
   non-duplicate rows with `source='OP:Idan_2018'`. Output diff report to
   `_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/L49_DIFF_REPORT.md`. 1 test.
10. **Tend 2018 investigation**: pre-flight read of
    `data/external_sources/tend_multi_year/Tend_2018_*.csv` (these were
    NOT committed by WP-C1's gitignore exception since 2018 has 0 HARVESTS).
    Check own data path: `/Users/nimrod/Documents/old Mac BackUpp/מהגינה של נימרוד/Tend Data/Tend_2018/`.
    Decision: CROP_PLAN + SEED_LIST only (no HARVESTS/NOTES).
    Document at `_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/TEND_2018_INVESTIGATION.md`.
11. If Tend 2018 INGEST decision = yes: extend `tend_overlay.py` for 2018
    (CROP_PLAN + SEED_LIST only). Else: document SKIP + reason.
12. Wire into `seed.py`: add `--c3-only`, `--no-c3`, `_run_c3_ingestion()`.
    APPEND to existing CLI (don't overwrite C1/C2/C4 entries).
13. Full focused test pass (≥12 tests). Live ingestion. validate_aos.sh.
14. Write `_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/BUILD_REPORT_v1.0.0.md`
    + `L49_DIFF_REPORT.md` + `TEND_2018_INVESTIGATION.md` + `OCR_RUN_LOG.md`
    (Anthropic Vision API token cost).

## §5 Iron Rule compliance (CRITICAL)

| IR | What you must do |
|----|------------------|
| **IR#1** | BUILDER = Claude (you). team_190 (non-Claude, GPT-5+) validates. DO NOT self-validate. |
| **IR#4** | Do NOT edit `_aos/roadmap.yaml`. |
| **IR#6** | Inter-team artifacts via `_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/`. |
| **IR#7** | NO schema changes in C3 — uses existing tables only. |
| **IR#11** | Never touch `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. |
| **IR#12** | NEVER invoke `/AOS_gov-update` or `/AOS_gov-sync`. |
| **LOD500_LOCKED** | Never modify: `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py`, `db/versions/001..052_*.py`, `mu-plugin/`, `tend.py`, `models.py`, `reconciler.py` (engine v1.1 FINAL), `enrichment_runner.py` (FINAL). |

## §6 Engine v1.1 inheritance — already shipped (do NOT modify)

Sister WP-C1 R2 introduced `collect_source_values_with_inheritance` in
`reconciler.py`. It applies to ALL `crop_variety_source_values` insertions
via the existing `enrichment_runner`. Your C3 imports will benefit
automatically — no special handling needed in your code.

## §7 Completion criteria (BUILD_REPORT checklist)

- [ ] All 10 ACs from LOD400 §5 verified
- [ ] ≥12 new tests passing
- [ ] Existing tests: 0 new failures
- [ ] `validate_aos.sh` 29/19/0
- [ ] L40 Curtis master chart: ≥20 rows with `source='OP:CurtisStone'`
- [ ] L41 OCR: ≥30/34 images cached (≥88% success)
- [ ] Curtis OCR narrative ≥10 crops in `crop_knowledge_notes` (NI tier)
- [ ] L05a+L05b succession intervals derived for ≥8 crops
- [ ] L06 FRANCHI: 29 variety provider references
- [ ] L49 vs L03/L04 diff: report generated; no duplicate insertions
- [ ] Tend 2018 decision documented (INGEST partial OR SKIP with reason)
- [ ] OCR_RUN_LOG documents Anthropic Vision API cost (≤$5)
- [ ] BUILD_REPORT filed
- [ ] LOD500_LOCKED inventory check passes
- [ ] Commits on `main` with co-author trailer

## §8 Parallel-with-WP-C2 file-scope safety

WP-C2 builder runs concurrently. Disjoint scopes:

| Resource | WP-C2 owns | WP-C3 owns | Conflict? |
|----------|------------|------------|:---------:|
| Migrations | **053** (extend ckn enum) | NONE | ✅ No |
| Importer dirs | `importer/ni/aosnot_*`, `ni/sham_*`, `ni/zacks_*`, `ni/jmf_ft_*` | `importer/urban_farmer/`, `importer/israeli/idan_seedlings_*`, `importer/israeli/franchi_*`, `importer/israeli/idan_2018_diff.py` | ✅ No |
| External sources used | `data/external_sources/raw_text/*.txt` + `data/external_sources/extracted/aosnot/`, `extracted/sham_*/`, `extracted/zacks_*/`, `extracted/jmf_ft_*/` | `data/external_sources/urban_farmer/*.{xlsx,jpg}` + `data/external_sources/israeli/L05a*/L05b*/L49*` + `data/external_sources/extracted/curtis_ocr/` | ✅ No |
| Scripts | `scripts/extract_jmf_he.py` | `scripts/ocr_curtis_images.py` | ✅ No |
| `constants.py` | (likely no changes) | possibly `succession_interval_weeks` references | ⚠️ Read-only or append-only |
| `source_registry.py` | append 7 NI:* entries | append 4 entries (OP:CurtisStone, NI:curtis_stone_book, OP:Idan_seedlings, OP:FRANCHI_catalog, OP:Idan_2018) | ⚠️ Same file — **APPEND only** |
| `seed.py` CLI | append `--c2-only/--no-c2` | append `--c3-only/--no-c3` | ⚠️ Same file — **APPEND only** |
| `requirements.txt` | possibly `anthropic` SDK | possibly `pillow`/Anthropic Vision API client | ⚠️ Same file — **APPEND only** |

**Shared-file protocol** (same as C1/C4 parallel):
- `git pull --rebase origin main` before EVERY commit
- Conflicts in shared files: both ADDITIVE → keep BOTH sets
- Non-shared conflict → STOP and report

## §9 What you must NOT do

- Do NOT write to `_aos/`
- Do NOT edit `_aos/roadmap.yaml`
- Do NOT modify LOD500_LOCKED files (§5)
- Do NOT add new tables — C3 uses existing tables only
- Do NOT exceed $5 OCR budget — STOP and file INQUIRY
- Do NOT publish raw Curtis Stone book prose — OCR snippets ≤2000 chars per row
  (same fair-use bound as WP-B2/C2)
- Do NOT use tesseract if Anthropic Vision works (quality matters; per LOD400)
- Do NOT touch WP-C2 territory:
    `data/external_sources/raw_text/israeli__L02_*`,
    `raw_text/israeli__L09_*`, `raw_text/israeli__L10_*`,
    `raw_text/israeli__L11_*`,
    `raw_text/jmf_extension__L13_*`, `raw_text/jmf_extension__L14_*`,
    `raw_text/jmf_extension__L16_*`,
    `data/external_sources/extracted/aosnot/`, `extracted/sham_*/`,
    `extracted/zacks_*/`, `extracted/jmf_ft_*/`
- Do NOT issue your own L-GATE_V verdict (IR#1)
- Do NOT overwrite WP-C2 entries in shared files — APPEND only

## §10 Routing post-build

1. File BUILD_REPORT + L49_DIFF_REPORT + TEND_2018_INVESTIGATION + OCR_RUN_LOG
2. Report path to user (team_00)
3. team_00 (or follow-up team_10 session) files MANDATE_L-GATE_V to team_190
4. team_190 issues verdict
5. If PASS: roadmap transition to LOD500_LOCKED (team_00 authority)
6. If findings: remediation cycle

---

*Builder mandate issued 2026-05-26 by team_10 (spec-author session) on
behalf of team_00 program grant. Activation prompt at:
`_COMMUNICATION/team_10/SFA-S003-P002-WP-C3/ACTIVATION_PROMPT.md`*
