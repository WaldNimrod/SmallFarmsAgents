---
id: MANDATE_SFA-S003-P002-WP-C4_BUILDER_v1.0.0
from: team_00 (via team_10 spec-author session)
to: sfa_build (team_10 builder, separate fresh session)
date: "2026-05-26"
type: BUILDER_MANDATE
wp: "SFA-S003-P002-WP-C4"
project: smallfarmsagents
branch: main
gate: L-GATE_B
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD400_spec.md"
lod200_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD200_spec.md"
consolidated_findings_ref: "_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/CONSOLIDATED_FINDINGS_v1.0.0.md"
status: ACTIVE
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gate: "L-GATE_S R2 PASS by team_10 spec-authoring session 2026-05-26 (post multi-engine team_80 consolidation)"
expected_validator: "team_190 (non-Claude per IR#1) — L-GATE_V after BUILD complete"
parallel_with: "SFA-S003-P002-WP-C1 (currently in BUILD in separate session) — disjoint file scopes, safe to run concurrently"
---

# Builder Mandate — SFA-S003-P002-WP-C4 (Wave 4: Web Sources, multi-engine team_80 consolidated)

> **Activation gate:** L-GATE_B (Builder). sfa_build (team_10 in a fresh
> Claude Code session) builds per `LOD400_spec.md`. team_190 validates
> post-build at L-GATE_V. May run in PARALLEL with the active WP-C1 session
> (disjoint file scopes — see §9 below).

---

## §1 Mission (1-paragraph summary)

Ingest 8 consolidated web sources identified by team_80's multi-engine scout
(OpenAI ChatGPT + Perplexity + Gemini). 4 sources fill HIGH-priority gaps:
germination temperature (UC ANR), frost tolerance (OSU + cross-validation),
soil pH (UMD), and — **CRITICAL** — the Israeli planting calendar via IL MoA
and Shaham/שה"ם sources (which OpenAI specifically failed to find but
Perplexity + Gemini did — the multi-engine win). 3 sources fill MEDIUM gaps
(NPK removal, seeds/gram, companion planting); 1 LOW gap (postharvest
storage). Adds 3 new migrations (050 region docs, 051 `crop_companion_matrix`,
052 `crop_postharvest_storage`), 8 new web importer modules, and 1 download
harness.

## §2 Spec references (read in order)

1. **`_aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD400_spec.md`** — full build spec (PRIMARY)
2. `_aos/work_packages/S003/SFA-S003-P002-WP-C4/LOD200_spec.md` — scope context
3. **`_COMMUNICATION/team_80/SFA-CROP-DATA-SCOUT-2026-05-26/CONSOLIDATED_FINDINGS_v1.0.0.md`** — source-by-source detail + URLs + cross-engine consensus matrix
4. `data/external_sources/INDEX.md` — local files index (NOT this WP's scope but useful context)
5. `_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md` — sister WP, similar importer pattern
6. `_aos/work_packages/S003/SFA-S003-P002-WP-B2/LOD400_spec.md` — Hebrew-handling pattern (for IL MoA/Shaham)
7. `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` — engine + reconciler reference
8. `CLAUDE.md` — spoke conventions

## §3 Acceptance criteria (summary — full matrix in LOD400 §8)

20 ACs targeting: 3 migrations clean fwd/bwd; URL accessibility audit;
8 importers each producing target row counts; 3-source frost tolerance
cross-validation; Hebrew preservation for IL sources; companion-matrix
symmetric de-dup; postharvest scientific-name lookup; reconciler integration;
≥20 tests; `validate_aos.sh` 29/19/0; no LOD500_LOCKED touched; URL_AUDIT +
LICENSE_AUDIT + BUILD_REPORT filed.

## §4 Build sequence (14 steps from LOD400 §10)

1. Migrations 050+051+052 → `alembic upgrade head`
2. ORM modules: `companion_matrix.py` + `postharvest_storage.py`
3. Extend `source_registry.py` with 14 new patterns (8 PR + 2 OP + 2 NI + 2 cross-val)
4. Build `scripts/download_web_sources.py`; run `--source all`; file URL_AUDIT_v1.0.0.md
5. **Build CW-05 IL MoA + Shaham importer first** (HIGHEST priority gap-fill) — `web/il_moa_calendar.py` + 4 tests
6. Build CW-01 UC ANR germination + 3 tests
7. Build CW-02 OSU frost tolerance + cross-validation logic + 3 tests
8. Build CW-03 UMD soil pH + 2 tests
9. Build CW-04 NE Veg Guide NPK + unit conversion + 3 tests
10. Build CW-06 seeds-per-gram cross-validation + 2 tests
11. Build CW-07 UF/IFAS companion matrix + symmetric de-dup + 2 tests
12. Build CW-08 UC Davis postharvest + scientific-name lookup + 2 tests
13. Wire all into `seed.py` (`--c4-only`, `--no-c4`, `--all` flow)
14. Live ingestion; `validate_aos.sh`; BUILD_REPORT + URL_AUDIT + LICENSE_AUDIT

## §5 Iron Rule compliance (CRITICAL — must preserve)

| IR | What you must do |
|----|------------------|
| **IR#1** | You are the BUILDER (sfa_build, Claude). team_190 (non-Claude, GPT-5+) validates post-build. DO NOT self-validate. |
| **IR#4** | Do NOT edit `_aos/roadmap.yaml` (team_100 authority; team_00 grant covers spec-author, not builder). |
| **IR#6** | Inter-team artifacts via `_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/`. |
| **IR#7** | DB schema changes ONLY via alembic migrations. No direct DDL. |
| **IR#11** | Never touch `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. |
| **IR#12** | NEVER invoke `/AOS_gov-update` or `/AOS_gov-sync`. |
| **LOD500_LOCKED** | Never modify `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py`, `db/versions/001..049_*.py`, `mu-plugin/`, `tend.py` (raw-material guard), `models.py`. |

## §6 Completion criteria (checklist for BUILD_REPORT)

- [ ] All 20 ACs verified (per LOD400 §8)
- [ ] ≥20 new tests passing; existing tests 0 new failures
- [ ] `validate_aos.sh` 29/19/0
- [ ] `crop_companion_matrix` populated ≥20 pair-rows
- [ ] `crop_postharvest_storage` populated ≥30 crops
- [ ] **CRITICAL AC-C4-07**: `crop_planting_calendar` has ≥30 rows with
      `source LIKE 'NI:il_%' OR source = 'NI:shaham_extension'`
- [ ] `crop_variety_source_values` has new rows with sources: `PR:uc_anr_germination`,
      `PR:osu_frost_tolerance`, `PR:umd_soil_ph`, `PR:ne_veg_guide`,
      `OP:vital_seeds_count`, `OP:osborne_seed_count`
- [ ] Hebrew preservation verified for IL MoA + Shaham (AC-C4-08 — no `\uXXXX` escapes)
- [ ] `validate_enrichment.py` shadow run shows ≥5 new CALIBRATED (variety, field) pairs
- [ ] BUILD_REPORT, URL_AUDIT, LICENSE_AUDIT all filed
- [ ] LOD500_LOCKED inventory check passes
- [ ] Commits on `main` with co-author trailer

## §7 Routing post-build

Same as WP-C1: BUILD_REPORT → file path to team_00 → team_190 L-GATE_V mandate
→ verdict → (if PASS) roadmap transition by team_00 / spec-author session.

## §8 What you must NOT do

- Do NOT write to `_aos/`
- Do NOT edit roadmap.yaml
- Do NOT modify LOD500_LOCKED files
- Do NOT skip the URL download pre-flight — without `data/external_sources/web/<source>/`
  the importers will fail
- Do NOT skip the URL_AUDIT step (AC-C4-18 will fail)
- Do NOT publish raw prose from sources with restrictive TOS — store DERIVED
  VALUES (numbers, classifications) only
- Do NOT use sources with unclear license; flag in LICENSE_AUDIT and skip
- Do NOT issue your own L-GATE_V verdict (IR#1)
- Do NOT touch files in `data/external_sources/israeli/`, `jmf_extension/`,
  `tend_multi_year/`, `urban_farmer/`, `misc_investigate/` — those belong to
  WP-C1/C2/C3 and may be in active use by the parallel WP-C1 session

## §9 Parallel-with-WP-C1 file-scope safety

WP-C1 is being built concurrently in a separate session. The two scopes are
**disjoint** — verify before you start:

| Resource | WP-C1 owns | WP-C4 owns | Conflict? |
|----------|------------|------------|:---------:|
| Migrations | 047, 048 | 050, 051, 052 | ✅ No (049 is for WP-C2) |
| ORM modules | `planting_calendar.py`, `cover_crops.py` | `companion_matrix.py`, `postharvest_storage.py` | ✅ No |
| Importer dirs | `importer/israeli/`, `importer/jmf/cover_crops_importer.py` | `importer/web/` | ✅ No |
| External sources used | `data/external_sources/israeli/`, `tend_multi_year/`, `jmf_extension/L12_*` | `data/external_sources/web/` (NEW) | ✅ No |
| `constants.py` | `IL_CROP_MAP` | `EN_CROP_MAP` (new) | ⚠️ Same file, different keys — **append, do not overwrite** |
| `source_registry.py` | 7 new entries (PR:jmf_cover, NI:groworganic, etc.) | 14 new entries (PR:uc_anr_*, NI:il_moa_*, etc.) | ⚠️ Same file, different keys — **append, do not overwrite** |
| `seed.py` CLI | `--c1-only`, `--no-c1` | `--c4-only`, `--no-c4` | ⚠️ Same file — **append, do not overwrite** |

**Shared-file protocol:**
- Pull latest `main` before each commit
- If shared-file conflict arises (`constants.py`, `source_registry.py`,
  `seed.py`), prefer rebase + manual merge (both sessions are additive,
  conflicts should be trivial)
- If file is locked by uncommitted work in the other session, file an INQUIRY
  and wait briefly

---

*Builder mandate issued 2026-05-26 by team_10 (spec-author session) on behalf
of team_00 program grant. Activation prompt at:
`_COMMUNICATION/team_10/SFA-S003-P002-WP-C4/ACTIVATION_PROMPT.md`*
