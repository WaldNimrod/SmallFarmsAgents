---
id: SFA-S003-P002-WP-B1-LOD200
wp: SFA-S003-P002-WP-B1 — JMF MasterClass Excel Base Layer
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045)
date: 2026-05-24
version: v1.0.0
lod200_supersedes: PLACEHOLDER_PENDING_TEAM_110 (committed in f61c1da)
parent_phase: S003-P002
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
depends_on: [SFA-S003-P002-WP-A]
depends_on_commit: 594cbc8        # WP-A LOD500_LOCKED
validator: team_190 (non-Claude, Iron Rule #1)
builder: sfa_build (separate session per IR#1)
---

# LOD200 — SFA-S003-P002-WP-B1: JMF MasterClass Excel Base Layer

## 1. Mission

Ingest the JMF (Jean-Martin Fortier) MasterClass Excel files as the
**PR-tier (Prescriptive, weight 0.70) baseline** for the multi-source crop
knowledge base built on the WP-A enrichment engine (LOD500_LOCKED at
`594cbc8`).

JMF Excel populates 11 source-value fields and a new `crop_task_templates`
table (migration 044) that B3 (Tend overlay) and B2 (JMF PDF NI) will
subsequently layer on top of. Successful B1 completion is the prerequisite
for B2 and B3 (data-model dependency).

## 2. In-scope

- **Migration 044** — new table `crop_task_templates` (additive; no
  modification of existing schema).
- **New importer module** `organic_market_agent/crop_book/importer/jmf_masterclass.py`
  with 5 parser functions (one per JMF sheet) and 1 orchestrator
  `import_jmf_masterclass(session, xlsx_path)`.
- **Crop-name mapping constant** `JMF_CROP_MAP` (English JMF → Hebrew
  `crops.name_he`) added to `organic_market_agent/crop_book/constants.py`.
- **11 source-value fields** populated via the WP-A engine
  (`crop_variety_source_values` with `source='JMF'`, `trust_tier='PR'`,
  `confidence_weight=0.70`):
  `days_to_maturity`, `harvest_window_max_days`, `days_in_nursery_cell`,
  `avg_yield_per_bed_m`, `documented_price`, `in_row_spacing_cm`,
  `rows_per_bed`, `direct_seed_density_g`, `nursery_tray_type`,
  `cultivar_provider`, `cultivar_description`.
- **Task-template rows** for 14 `task_type` enum values across CROP
  ASSOCIATED TASKS columns.
- **CLI flags** on `seed.py`: `--jmf-only`, `--no-jmf`; default `--all`
  invokes the JMF importer after WP-A and before existing Tend importer.
- **Tests** ≥25 (parser + integration + idempotency + crop-map coverage).
- **WP-A engine reuse only** — all blendable fields go through
  `reconcile_field()`; nothing bypasses the reconciler.

## 3. Out-of-scope

- **No LLM extraction** — that is WP-B2 (`NIImporter` subclass for the JMF
  book PDF + Fiche Technique PDFs).
- **No Tend overlay** — that is WP-B3 (`tend_overlay.py` over the existing
  `tend.py` raw-material guard).
- **No edits to LOD500_LOCKED files** (see §9).
- **No `models.py` GCR** — `crop_task_templates` is additive ORM in a new
  module; no schema change to existing tables.
- **No publisher / WordPress work** — JSON artifacts and uploads are
  WP-B2/B3 scope or follow-up WPs.

## 4. Data sources

All paths confirmed on disk by team_190 PRE_HANDOFF_VERDICT R1.

| File | Sheets read | Rows |
|------|-------------|------|
| `/Users/nimrod/Documents/old Mac BackUpp/Market Gardening/MasterClass/Crop Planning/CROPPLANNINGTOOLMASTERCLASS-1515735991193 (from macBook Air - nimrod).XLSX` | `CROP CHART`, `CROP ASSOCIATED TASKS`, `DIRECT SEEDING CHART`, `NURSERY & TRANSPLANT CHART`, `CULTIVARS` | 52 / 30 / 21 / 45 / 136 |
| `…/Crop Planning/תבלאות נתונים/DIRECTSEEDINGCHART-*.XLSX` | standalone direct-seeding | 21 |
| `…/Crop Planning/תבלאות נתונים/NURSERYTRANSPLANTCHART-*.XLSX` | standalone nursery | 45 |

Standalone files act as confirmation copies; if values diverge from the
master, the master wins and the divergence is logged at WARN level.

## 5. Data model summary

### 5.1 New table — `crop_task_templates` (migration 044)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `BIGSERIAL` PK | autoincrement; SQLite variant `Integer` |
| `crop_id` | `BIGINT` FK → `crops.id` ON DELETE CASCADE | not null |
| `source` | `VARCHAR(50)` | e.g. `'JMF'` (B1), `'Tend_2022'` (B3) |
| `trust_tier` | `VARCHAR(20)` | `'PR'` for JMF, `'OP'` for Tend |
| `task_type` | `VARCHAR(40)` | enum, CHECK constraint |
| `timing_anchor` | `VARCHAR(20)` NULL | `seeding`/`transplanting`/`harvest`/`field_prep` |
| `days_offset` | `INTEGER` NULL | signed; pre-planting = negative |
| `method` | `TEXT` NULL | free-form (e.g. "flame-weeder pass 1") |
| `input_material` | `TEXT` NULL | e.g. "Bio-Boron + Seaweed" |
| `notes` | `TEXT` NULL | free-form |
| `display_order` | `INTEGER` default `100` | UI ordering |
| `is_active` | `BOOLEAN` default `TRUE` | soft-disable |
| `created_at` | `TIMESTAMP` default `now()` | audit |
| `UNIQUE(crop_id, source, task_type, days_offset)` | idempotency key |
| index `idx_cct_crop(crop_id)`, `idx_cct_type(task_type)` |

### 5.2 `task_type` enum (CHECK constraint values)

`stale_seed_bed`, `flame_weeder`, `flextine_harrow_1`, `flextine_harrow_2`,
`biodisc`, `hoe`, `hand_weed`, `boron_seaweed_1`, `boron_seaweed_2`,
`straw_mulch_topdress`, `head_pinch_chop`, `mow_and_tarp`,
`at_seeding_transplanting`, `net_row_cover`.

B3 (Tend overlay) will additionally introduce `nursery_seed`, `pest_spray`,
`potting_up`, `thinning` — those are NOT introduced by B1 and the CHECK
constraint will be expanded in WP-B3's migration 046.

### 5.3 New source_value field-name catalog

11 entries listed in §2; each row added via the existing WP-A
`crop_variety_source_values` table with `source='JMF'`, `trust_tier='PR'`,
`confidence_weight=0.70`, `is_outlier_rejected=FALSE` (the
`reconcile_field()` engine in WP-A may later flip the outlier flag).

Variety attribution: when the JMF row carries cultivar text (CULTIVARS
sheet), it attaches to the `crop_varieties` row matched by
`(crop_id, name_en)`; otherwise it attaches to the default
"baseline" variety synthesized per crop (the same default variety used by
the existing WP-A Tend path).

## 6. Trust-layer placement

| Field | Value |
|-------|-------|
| `source` | `'JMF'` (single label; matches `SOURCE_REGISTRY["JMF"]` from WP-A) |
| `trust_tier` | `'PR'` |
| `confidence_weight` | `0.70` |
| Hard override? | No |
| Blend strategy per field | inherited from `FIELD_POLICY` (`weighted_mean`, `hard_winner`, or `latest_op` as already defined in `field_policy.py`) |

Behavior expectations:

- For `days_to_maturity`: JMF enters the `weighted_mean` blend with Tend
  (OP, 0.55); EX (team_00) or NI overrides still win when present.
- For `documented_price`: JMF (PR) loses to the most-recent Tend year
  (`latest_op` strategy) when both are present.
- For `in_row_spacing_cm`, `rows_per_bed`, `planting_season`,
  `harvest_window_*`: JMF wins via `hard_winner` only when no EX/NI is
  present (PR > OP in trust order).

The `JMF_CROP_MAP` ensures that JMF English crop names resolve to the same
`crop_id` already populated by WP-A so blending occurs against the correct
row.

## 7. Trust-layer / engine placement diagram

```
JMF XLSX files
   │
   ▼
jmf_masterclass.py (5 parsers + orchestrator)
   │
   ▼
crops.name_he ◀── JMF_CROP_MAP ── JMF "Arugula" / "Beets" / ...
   │
   ├─▶ crop_variety_source_values  (11 fields × matched variety/crop)
   │       │
   │       ▼
   │   enrichment_runner.run_enrichment(...)   ◀── WP-A engine
   │       │
   │       ▼
   │   crop_field_enrichment (per-field consensus)
   │
   └─▶ crop_task_templates (new table; not part of reconcile_field)
```

Task templates do NOT flow through `reconcile_field()` because they are
not blendable scalar fields — they are discrete row sets keyed by
`(crop_id, source, task_type, days_offset)`. WP-B3 layers Tend templates
into the same table with `source='Tend_<year>'`; the UI later filters/merges
at read time, NOT at import time.

## 8. Dependencies

### 8.1 Direct

- **WP-A** (`SFA-S003-P002-WP-A`) — LOD500_LOCKED at commit `594cbc8`.
  Specifically depends on:
  - `organic_market_agent/crop_book/source_registry.py` — `SOURCE_REGISTRY["JMF"]`
    must remain a `PR`-class entry with `weight=0.70`.
  - `organic_market_agent/crop_book/field_policy.py` — `FIELD_POLICY` entries
    for the 5 blendable fields (`days_to_maturity`, `avg_yield_per_bed_m`,
    `documented_price`, `in_row_spacing_cm`, `rows_per_bed`).
  - `organic_market_agent/crop_book/importer/reconciler.py` —
    `reconcile_field()` public signature.
  - `organic_market_agent/crop_book/importer/enrichment_runner.py` —
    `run_enrichment(session, variety_ids=None)` entrypoint.
  - Migration 042 — `trust_tier` / `confidence_weight` columns on
    `crop_variety_source_values` (B1 inserts with those columns populated).

  **Transitive note (PRE_HANDOFF Advisory #4):** WP-B2 and WP-B3 also
  depend on WP-A; each downstream LOD400 will state this explicitly.

### 8.2 External

- Python: `openpyxl ≥ 3.1` (already a project dep; used by current `jmf.py`).
- Filesystem: read-only access to the JMF MasterClass directory listed in §4.

### 8.3 Tooling

- Builder engine: any non-team_190 engine (sfa_build session, likely Claude
  Code) per IR#1.
- Validator (L-GATE_S and L-GATE_V): team_190 (GPT-5.5, non-Claude).

## 9. LOD500_LOCKED inventory (unchanged in WP-B1)

| File / path | Reason |
|-------------|--------|
| `organic_market_agent/views.py` | LIVE PRODUCTION (admin) |
| `organic_market_agent/publisher/wp_upload.py` | LIVE PRODUCTION |
| `organic_market_agent/publisher/upload_dispatch.py` | LIVE PRODUCTION |
| `organic_market_agent/db/versions/001..043_*.py` | Prior migrations |
| `mu-plugin/` | Deployed WP plugin |
| `organic_market_agent/crop_book/importer/tend.py` | Raw-material guard (per CLAUDE.md) |

The existing `organic_market_agent/crop_book/importer/jmf.py` (an empty
stub from WP-A) is NOT LOD500_LOCKED. WP-B1 may extend or replace it;
LOD400 will pick one option explicitly (current plan: leave it untouched
and put all new code in `jmf_masterclass.py`).

## 10. GCR requirements

**None.** WP-B1 is fully additive:

- Migration 044 creates a brand-new table; existing tables untouched.
- ORM is a new module `crop_task_models.py` (separate from `models.py`,
  same pattern as `enrichment_models.py` in WP-A).
- No changes to `views.py`, `publisher/`, `tend.py`, or any prior migration.

If LOD400 review surfaces a hidden need to add a back-reference relationship
on `Crop` (mirroring WP-A's `CropVariety.enrichments`), team_110 will file
**GCR-B1-1** to team_00 BEFORE locking LOD400. Default plan: avoid the
back-ref; access via explicit query in views/tests.

## 11. AC and test count targets

- **Acceptance Criteria target:** ≥ 15 ACs in LOD400 (PROGRAM_BRIEF §2.5).
- **Test count target:** ≥ 25 tests, broken down (preliminary):
  - 5× `test_jmf_masterclass_parsers.py` — one per sheet (chart / tasks /
    direct-seed / nursery / cultivars)
  - 4× crop-name mapping (`JMF_CROP_MAP` round-trip; miss → WARN+skip;
    Hebrew non-ASCII safety; 52-crop coverage assertion)
  - 4× unit conversions (inches→cm; yield/100bed → yield/m; rounding;
    NULL handling)
  - 6× DB integration on SQLite in-memory
    (`crop_task_templates` upsert; idempotent re-import; FK cascade;
    CHECK constraint enforcement; `source_value` insert path; enrichment
    runner integration)
  - 3× migration round-trip (`alembic upgrade 044` / `downgrade 043` /
    `upgrade 044` again)
  - 2× CLI behavior (`--jmf-only` skips Tend; `--no-jmf` skips JMF)
  - 1× regression: ARUGULA `days_to_maturity` EX override (21) still wins
    after JMF (60) is added to the blend (proves WP-A engine reuse).

Final inventory is fixed in LOD400 §16.

## 12. Open questions (resolved in LOD400)

1. **`JMF_CROP_MAP` location** — proposal: append constant to existing
   `organic_market_agent/crop_book/constants.py` next to `TEND_CROP_MAP`.
   Behavior on miss: WARN + skip (matches Tend importer convention).
   *Decision: confirm in LOD400.*
2. **Idempotency window for upsert** — proposal: use
   `(crop_id, source, task_type, days_offset)` UNIQUE constraint as the
   merge key for `crop_task_templates`; for `crop_variety_source_values`,
   reuse the existing WP-A upsert key `(variety_id, field_name, source)`.
   *Decision: confirm in LOD400.*
3. **`days_in_nursery_cell` storage** — proposal: as a `source_value`
   field (numeric) per crop. Some JMF rows give a single number, some a
   range; LOD400 will specify "midpoint stored, range note appended."
4. **JMF row → `variety_id` resolution** — proposal: synthesize a
   "baseline" variety per crop (same convention as Tend) when CULTIVARS
   sheet has no per-cultivar value; otherwise match
   `(crop_id, name_en)` from the CULTIVARS row.
5. **Standalone-vs-master divergence policy** — proposal: master wins;
   divergence logged at WARN with both values. *Decision: confirm in LOD400.*

## 13. PRE_HANDOFF advisories — disposition for WP-B1

| # | Advisory | WP-B1 disposition |
|---|---|---|
| 1 | JMF PDF licensing | **N/A** (B1 is Excel-only). Deferred to WP-B2 LOD400. |
| 2 | LLM extraction cache strategy | **N/A** (no LLM in B1). Deferred to WP-B2 LOD400. |
| 3 | Tend task whitelist | **N/A** (B1 does not touch Tend). Deferred to WP-B3 LOD400. |
| 4 | Transitive WP-A dependency must be explicit in each spec | **Addressed** in §8.1 above and will be re-stated in WP-B1 LOD400 §1/§2. |

## 14. Sequencing into the program

```
WP-B1 (this spec)  ──▶ LOD500_LOCKED ──▶ WP-B2 + WP-B3 (sequential)
```

B2 and B3 cannot begin LOD400 authoring until B1's `crop_task_templates`
table and `JMF_CROP_MAP` constant are LOD500_LOCKED, because:
- B3 inserts into the **same** `crop_task_templates` table (`source='Tend_<year>'`)
  and its task-type mapping table (PROGRAM_BRIEF §4) depends on the B1
  enum baseline.
- B2 (`NIImporter` subclass for the JMF book) reuses the JMF crop-name
  mapping resolved in B1.

---

*LOD200 v1.0.0 — authored 2026-05-24 by team_110 under EXECUTION_MANDATE
SFA-S003-P002-WP-B (ADR045, `execution_authority: full`).*
*Next phase: LOD400 spec (15 sections, mirroring WP-A v1.1.0).*
