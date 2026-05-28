---
id: SFA-S003-P002-WP-C6-LOD400
wp: SFA-S003-P002-WP-C6 — Sparse Crops Expansion (execution)
gate: L-GATE_B (LOD400)
status: READY_FOR_BUILD
author: team_100 (Chief Architect)
date: 2026-05-28
version: v1.0.0
supersedes_planning: LOD200_spec.md (PROPOSED)
depends_on: [SFA-S003-P002-WP-C5]   # LOD500_LOCKED ✅ 2026-05-28
activation: team_00 prioritization grant 2026-05-28 ("מאשר")
orchestration:
  build: "team_10 (Claude Sonnet)"
  qa: "team_50 (Claude Haiku)"
  validation: "team_190 (non-Claude — IR#1 cross-engine)"
---

# LOD400 — WP-C6: Sparse Crops Expansion

## 0. Premise correction (vs LOD200)
LOD200 assumed WR synthesis needs an **external** LLM API (team_80 multi-engine
scout / OpenAI / Gemini / Perplexity). **This is not required.** The existing
WR packs (`data/external_sources/web/gemini_il_research/`,
`.../openai_tier1_research/`) are just **structured agronomic JSON** ingested by
`importer/ni/gemini_il_research.py` / `openai_tier1_research.py`. A Claude
in-session agent IS an LLM and produces the same artifact at **$0** — exactly the
method used for WP-C2 deepening (in-session, no separate API spend). The WR
trust tier (weight 0.60, added in WP-C5) exists precisely for AI-synthesized
research on crops lacking IL/PR sources.

## 1. Mission
Bring the **19 sparse crops** (≤2 enriched fields, per
`_COMMUNICATION/team_100/SFA-S003-P002-WP-C6/COVERAGE_SNAPSHOT_v1.0.0.md`) up to
**≥6 enriched fields each** by generating WR research-pack data in-session,
importing it as `WR:` source values, and re-running enrichment.

## 2. Scope — the 19 crops (DB crop_id : name_he : name_en)
herbs (10): 1 אזוב מצוי/Anise Hyssop, 28 לימון בלם/Lemon Balm, 34 נענע/Mint,
43 מרווה/Sage, 47 טרגון/Tarragon, 48 טימין/Thyme, 22 היביסקוס/Hibiscus,
29 לימון ורבנה/Lemon Verbena, 32 לובסטייה/Lovage, 50 כורכום/Turmeric.
vegetables (7): 57 ג'ינג'ר/Ginger (0 fields!), 13 פנס סיני/Chinese Lantern,
16 גרגר נחלים/Cress, 23 ארטישוק ירושלמי/Jerusalem Artichoke, 24 ג'יקמה/Jicama,
31 עלי בייבי/Salad Mix, 38 פאק צ'וי/Pac Choi.
fruit_trees (2): 5 דפנה/Bay, 37 תפוז/Oranges.

## 3. Per-crop field target (≥6 of the canonical vocabulary)
Populate at least 6, prefer 8–10, of these `field_name`s (existing schema — NO
new fields): `days_to_maturity`, `germination_temp_c_min`,
`germination_temp_c_opt`, `germination_temp_c_max`, `in_row_spacing_cm`,
`rows_per_bed`, `soil_ph_target`, `soil_ph_liming_threshold`, `seeds_per_gram`,
`storage_temp_c_min`, `storage_temp_c_max`, `storage_rh_pct_min`,
`storage_rh_pct_max`, `storage_life_days`, `nutrient_removal_n_kg_ha`,
`nutrient_removal_p_kg_ha`, `nutrient_removal_k_kg_ha`,
`harvest_window_max_days`, `days_in_gh_total`, `frost_tolerance_class`,
`plants_per_m2`, `yield_per_m2_kg`, `succession_interval_weeks`.
- Perennial herbs/roots (Turmeric, Ginger, Bay, Oranges, Lovage, Sage, Thyme,
  Mint): germination/DTM may be N/A — substitute propagation/establishment-
  appropriate fields (spacing, soil pH, storage, nutrient removal, days_in_gh_total).
  ≥6 valid fields is the bar regardless of which 6.

## 4. Data quality method (binding)
- Each value generated from the builder's agronomic knowledge **and grounded via
  WebSearch/WebFetch** against a reputable extension/horticulture source where
  possible (USDA/UC ANR/RHS/university extension/Israeli MoA). $0 — no paid API.
- Realistic ranges only; min ≤ best ≤ max. No fabricated precision. When a value
  is genuinely uncertain, omit the field rather than guess (better 6 solid than
  10 shaky).
- Hebrew names must match the DB `crops.name_he` exactly (see §2 ids) for lookup.

## 5. Deliverables
1. `data/external_sources/web/claude_sparse_crops_research/sfa_sparse_crops_2026-05-28.json`
   — pack matching the gemini schema: `{dataset_id, generated_at, note, crops:[{crop_id, name_he, name_en, <fields...>, _sources:[urls]}]}`.
2. `organic_market_agent/crop_book/importer/ni/claude_sparse_crops_research.py`
   — mirror of `gemini_il_research.py`: `SOURCE="WR:claude_sparse_crops_v1"`,
   `TRUST="WR"`, `CONFIDENCE=0.60`, crop_id→name_he map for the 19 crops, writes
   `crop_variety_source_values` for the default variety, idempotent (upsert).
3. Wire the importer into the seed/import entrypoint used for the other WR packs.
4. Run import + `enrichment_runner.run_enrichment(session, dry_run=False)`.
5. `tests/crop_book/test_c6_sparse_crops.py` — asserts each of the 19 crops has
   ≥6 `crop_field_enrichment` rows after enrichment; WR rows present; no change
   to previously well-covered crops' counts.

## 6. Acceptance Criteria
| AC | Check | Pass |
|----|-------|------|
| AC-C6-01 | Each of 19 crops ≥6 distinct enriched fields (SQL coverage query) | all 19 pass |
| AC-C6-02 | New source values carry `source_label='WR:claude_sparse_crops_v1'`, tier WR | SQL filter |
| AC-C6-03 | No regression: every crop that had ≥3 fields pre-C6 still has ≥ its prior count | diff vs COVERAGE_SNAPSHOT |
| AC-C6-04 | importer idempotent (re-run → no dup source_values) | run twice, count stable |
| AC-C6-05 | `name_he` lookups all resolve (0 "crop not in DB — skipped" for the 19) | importer log |
| AC-C6-06 | values web-grounded — `_sources` URLs present per crop in the JSON | inspect pack |
| AC-C6-07 | `test_c6_sparse_crops.py` 100% pass | pytest |
| AC-C6-08 | no engine/schema/migration change (data-only) | git diff scope |
| AC-C6-09 | `validate_aos.sh .` = 0 FAIL | run |
| AC-C6-10 | enrichment global stable/up: variety/field/high-conf counts ≥ pre-C6 | run_enrichment summary |

## 7. Out of scope
Engine v1.1, reconciler, trust-tier ladder, new field_names, new migrations,
UI. Data ingestion only (new WR rows).

## 8. Build phases
1. B.0 — read `gemini_il_research.py` + a sample pack; confirm schema + entrypoint.
2. B.1 — generate the WR pack JSON for all 19 crops (web-grounded, ≥6 fields each).
3. B.2 — author `claude_sparse_crops_research.py` importer (mirror gemini).
4. B.3 — run importer + `run_enrichment`; verify coverage query shows all 19 ≥6.
5. B.4 — tests (AC-C6-07) + AC-C6-01..10 locally.
6. B.5 — `validate_aos.sh`; BUILD_REPORT to `_COMMUNICATION/TEAM_10/SFA-S003-P002-WP-C6/`; commit on builder branch; flag QA.

## 9. QA + validation
team_50 (Haiku) independent coverage verification (AC matrix) → QA_PASS.
team_190 (non-Claude) L-GATE_V (IR#1: builder Sonnet ≠ validator non-Claude) →
on PASS team_100 ADR042 closure → LOD500_LOCKED.

## 10. GCR
NONE — `crop_source_weights` already has `WR:*`@0.60 (WP-C5). C6 only adds rows.
