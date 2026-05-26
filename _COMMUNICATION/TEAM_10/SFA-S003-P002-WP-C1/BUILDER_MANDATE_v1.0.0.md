---
id: MANDATE_SFA-S003-P002-WP-C1_BUILDER_v1.0.0
from: team_00 (via team_10 spec-author session)
to: sfa_build (team_10 builder, separate fresh session)
date: "2026-05-26"
type: BUILDER_MANDATE
wp: "SFA-S003-P002-WP-C1"
project: smallfarmsagents
branch: main
gate: L-GATE_B
spec_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md"
lod200_ref: "_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD200_spec.md"
status: ACTIVE
authorization_basis: "team_00 in-session grant 2026-05-26 (program-level for WP-C)"
prior_gate: "L-GATE_S PASS by team_10 spec-authoring session 2026-05-26"
expected_validator: "team_190 (non-Claude per IR#1) — L-GATE_V after BUILD complete"
---

# Builder Mandate — SFA-S003-P002-WP-C1 (Wave 1: Israeli Structured + Tend Multi-Year)

> **Activation gate:** L-GATE_B (Builder). sfa_build (team_10 in a fresh Claude
> Code session) builds per `LOD400_spec.md`. team_190 validates post-build at
> L-GATE_V.

---

## §1 Mission (1-paragraph summary)

Ingest 8 already-staged tabular sources from `data/external_sources/` (Israeli
sowing calendars, Idan Eliakim 2017 planning, JMF cover crop chart, Tend
2019/2020/2021 multi-year backfill) into the SFA crop book through the existing
WP-A reconciler engine. No LLM, no OCR, no PDF narrative parsing — pure
structured tabular work. Adds 2 new migrations (047 planting_calendar, 048
cover_crops), 5 new importer modules, ~14k new harvest aggregates, ≥3 new
Israeli sources to the trust-tier blender.

## §2 Spec references (read in order)

1. **`_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD400_spec.md`** — full build spec (PRIMARY)
2. `_aos/work_packages/S003/SFA-S003-P002-WP-C1/LOD200_spec.md` — scope context
3. `data/external_sources/INDEX.md` — source file catalog with quality scores
4. `data/external_sources/WAVE_PLAN_v1.0.0.md` — overall 4-wave program plan
5. `data/external_sources/sample_extracts/` — pre-extracted samples of every source (read before building each importer)
6. `_aos/work_packages/S003/SFA-S003-P002-WP-B3/LOD400_spec.md` — Tend overlay pattern reference
7. `_aos/work_packages/S003/SFA-S003-P002-WP-A/LOD400_spec.md` — engine + reconciler reference
8. `_aos/governance/team_10.md` (if present) or treat team_10 as the standard sfa_build role
9. `CLAUDE.md` — spoke conventions (port canon, LOD500_LOCKED list, raw-material guard)

## §3 Acceptance criteria (summary — full matrix in LOD400 §9)

20 ACs targeting: 2 migrations clean fwd/bwd; 5 importer modules each
extracting target row count; IL_CROP_MAP ≥80% resolution; reconciler
integration; idempotency; CLI integration; ≥25 tests; `validate_aos.sh` 29/19/0;
no LOD500_LOCKED touched; BUILD_REPORT filed.

## §4 Build sequence (numbered, from LOD400 §11)

1. Migrations 047 + 048 → `alembic upgrade head`
2. ORM modules: `planting_calendar.py` + `cover_crops.py`
3. Extend `constants.py` with `IL_CROP_MAP` Hebrew→DB mapping (use
   `data/external_sources/sample_extracts/` as input)
4. Extend `source_registry.py` with new source patterns
5. Build `israeli/groworganic_importer.py` (L01) + 3 tests
6. Build `israeli/bustan_importer.py` (L36 PDF table) + 3 tests
7. Build `israeli/idan_planning_importer.py` (L03+L04) + 4 tests
8. Build `jmf/cover_crops_importer.py` (L12 PDF table) + 3 tests
9. Extend `tend_overlay.py` for years 2019/2020/2021
10. Wire all into `seed.py` (`--c1-only`, `--no-c1`, `--all` flow)
11. Full focused-test suite ≥25 new tests passing
12. Live ingestion against PG; DB sanity counts
13. `validate_aos.sh` (expect 29/19/0)
14. Write `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/BUILD_REPORT_v1.0.0.md` + `UNMAPPED_CROPS_v1.0.0.md` (if any)
15. Commit on `main` (per project precedent; no offline branch needed — DB online verified)

## §5 Iron Rule compliance (CRITICAL — must preserve)

| IR | What you must do |
|----|------------------|
| **IR#1** | You are the BUILDER (sfa_build, Claude). team_190 (non-Claude) validates post-build. DO NOT self-validate. |
| **IR#4** | Do NOT edit `_aos/roadmap.yaml` (team_100 authority; team_00 grant covers spec-author, not builder). |
| **IR#6** | Inter-team artifacts via `_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/`. |
| **IR#7** | DB schema changes ONLY via alembic migrations. No direct DDL. |
| **IR#11** | Never touch `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml`. |
| **IR#12** | NEVER invoke `/AOS_gov-update` or `/AOS_gov-sync`. |
| **LOD500_LOCKED** | Never modify `views.py`, `publisher/wp_upload.py`, `publisher/upload_dispatch.py`, `db/versions/001..046_*.py`, `mu-plugin/`, `tend.py` (the raw-material guard). All these are explicitly listed in LOD200 §8. |

## §6 Completion criteria (checklist for BUILD_REPORT)

- [ ] All 20 ACs verified (per LOD400 §9)
- [ ] ≥25 new tests passing
- [ ] Full suite 0 new failures (existing pre-existing failures from WP-B unchanged)
- [ ] `validate_aos.sh` 29/19/0
- [ ] `crop_planting_calendar` populated ≥30 rows
- [ ] `crop_cover_crops` populated ≥10 rows
- [ ] `crop_variety_source_values` gains rows with `source LIKE 'OP:Idan_%' OR LIKE 'NI:groworganic' OR LIKE 'NI:bustan' OR LIKE 'Tend_2019' OR LIKE 'Tend_2020' OR LIKE 'Tend_2021'`
- [ ] `crop_harvest_stats` gains ≥3 new year aggregates (2019, 2020, 2021)
- [ ] `validate_enrichment.py` shadow run shows ≥3 new CALIBRATED (variety, field) pairs
- [ ] BUILD_REPORT filed
- [ ] UNMAPPED_CROPS_v1.0.0.md filed (if any Hebrew names unresolved)
- [ ] LOD500_LOCKED inventory check passes (LOD400 §12 command)
- [ ] Commit(s) on `main` with co-author trailer

## §7 Routing post-build

When BUILD complete:
1. File BUILD_REPORT (see §6)
2. Report path of BUILD_REPORT to user (team_00)
3. team_00 (or follow-up team_10 session) files `MANDATE_L-GATE_V` to team_190
   (separate non-Claude session) for cross-engine validation
4. team_190 issues verdict (PASS / PASS_WITH_FINDINGS / FAIL)
5. If PASS: roadmap transition to `LOD500_LOCKED, status: DONE` (team_00 authority)
6. If findings: remediation cycle

## §8 What you must NOT do

- Do NOT write to `_aos/` (any subdir — that's spec-author/orchestrator territory)
- Do NOT modify roadmap.yaml
- Do NOT use Anthropic API in importers (LLM is for WP-C2, not C1)
- Do NOT introduce OCR (WP-C3 territory)
- Do NOT make schema changes outside migrations 047 + 048
- Do NOT commit incomplete work — finish a coherent slice + tests + report before commit
- Do NOT issue your own L-GATE_V verdict (IR#1)

---

*Builder mandate issued 2026-05-26 by team_10 (spec-author session) on behalf
of team_00 program grant. Activation prompt at:
`_COMMUNICATION/team_10/SFA-S003-P002-WP-C1/ACTIVATION_PROMPT.md`*
