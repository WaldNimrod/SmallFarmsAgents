---
id: SFA-S003-P002-WP-B3-LOD200
wp: SFA-S003-P002-WP-B3 — Tend Israel Adaptation Overlay
gate: L-GATE_S (LOD200 — architecture spec)
status: PRE_LOD400
author: team_110 (execution mandate per ADR045)
date: 2026-05-25
version: v1.0.0
lod200_supersedes: PLACEHOLDER_PENDING_TEAM_110 (committed in f61c1da)
program_brief_ref: _COMMUNICATION/TEAM_10/SFA-S003-P002-WP-B/PROGRAM_BRIEF_v1.0.0.md
execution_mandate_ref: _COMMUNICATION/TEAM_110/SFA-S003-P002-WP-B/EXECUTION_MANDATE_v1.0.0.md
parent_wp_chain:
  - SFA-S003-P002-WP-A (engine SSoT — LOD500_LOCKED at 594cbc8)
  - SFA-S003-P002-WP-B1 (crop_task_templates schema — LOD500_LOCKED at 6a85561)
  - SFA-S003-P002-WP-B1-patch01 (extended JMF_CROP_MAP — LOD500_LOCKED at 3e1f946)
depends_on: [SFA-S003-P002-WP-B1-patch01, SFA-S003-P002-WP-B1, SFA-S003-P002-WP-A]
validator: team_190 (non-Claude, Iron Rule #1)
builder: sfa_build (separate session per IR#1)
parallel_eligible_with: SFA-S003-P002-WP-B2
---

# LOD200 — SFA-S003-P002-WP-B3: Tend Israel Adaptation Overlay

## 1. Mission

Layer Israeli local adaptation on top of the JMF PR-tier baseline. **Only recurring template patterns**, NOT individual one-off records — Tend captures Nimrod's farm operations as patterns extractable from CSV exports. Tier: **OP (Operational, weight 0.55)**.

Sources processed (all under `/Users/nimrod/Documents/israel Microgreens/crop data/Tend_2022/`):

- **`TASKS (from macBook Air - nimrod).CSV`** (798 rows) — extract recurring template patterns ONLY (whitelist applied)
- **`GREENHOUSE_PLAN (from macBook Air - nimrod).CSV`** (287 rows) — populate `days_in_gh_total`, `days_to_germinate_gh`
- **`HARVESTS (from macBook Air - nimrod).CSV`** (939 rows) — aggregate to statistics; NEVER insert individual records

Out-of-scope inputs (per PROGRAM_BRIEF §1):
- `NOTES.CSV` (27 rows; site-specific observations, not templates)
- `LOCATIONS`, `ORDERS_*`, `PACK`, `PICK`, `SEED_LIST` (not relevant per team_00 directive)

## 2. In-scope

- **Migration 046** — new table `crop_harvest_stats` (per-crop / season / year aggregates) AND `ALTER TABLE crop_task_templates DROP+ADD CHECK constraint` to extend the `task_type` enum with 4 new values (`nursery_seed`, `pest_spray`, `potting_up`, `thinning`)
- **New ORM module** `organic_market_agent/crop_book/crop_harvest_stats.py`
- **New importer** `organic_market_agent/crop_book/importer/tend_overlay.py` (NOT to be confused with the LOD500_LOCKED `tend.py`)
- **Task-type mapping table** (Tend label → JMF `task_type`) added to `constants.py`
- **Tend task whitelist** explicit in `tend_overlay.py` (advisory #3 disposition; see §11)
- **CLI integration:** `seed.py --tend-overlay-only`, `--no-tend-overlay`
- **Tests** ≥20 (parser tests + whitelist enforcement + aggregation correctness + DB integration + idempotency)
- **WP-A engine reuse only** — all blendable scalar fields (e.g., `days_in_gh_total`) flow through `_upsert_source_value` → `reconcile_field()` via the standard upsert. Task-template rows go directly into `crop_task_templates` (extension of B1's table; same path).

## 3. Out-of-scope

- **Modifying `organic_market_agent/crop_book/importer/tend.py`** — raw-material guard per CLAUDE.md. B3 uses a NEW module `tend_overlay.py` for clarity.
- **Individual harvest records** — explicitly forbidden. Only aggregates to `crop_harvest_stats`.
- **Non-template tasks** — explicitly excluded via whitelist (see §11 advisory #3 disposition).
- **NOTES.CSV ingestion** — site-specific observations, not templates.
- **No edits to LOD500_LOCKED files** (see §9).

## 4. Data sources

| File | Rows | B3 usage |
|------|------|----------|
| `TASKS.CSV` | 798 | Whitelist-filter → extract `(crop_id, task_type, days_offset_from_sow)` patterns → aggregate timing → upsert to `crop_task_templates` with `source='Tend_2022'`, `trust_tier='OP'` |
| `GREENHOUSE_PLAN.CSV` | 287 | Extract `Days In Greenhouse`, `Days to 1st potting up` → upsert to `crop_variety_source_values` (fields: `days_in_gh_total`, `days_to_first_potting`) |
| `HARVESTS.CSV` | 939 | Aggregate by (crop, year, season) → cycles_count, peak_week, yield range, yield median → upsert to `crop_harvest_stats`. NEVER insert per-record rows. |

## 5. Data model summary

### 5.1 New table — `crop_harvest_stats` (migration 046)

| Column | Type | Notes |
|--------|------|-------|
| `id` | `BIGSERIAL` PK | autoincrement; SQLite variant `Integer` |
| `crop_id` | `BIGINT` FK → `crops.id` ON DELETE CASCADE | not null |
| `season` | `VARCHAR(20)` | enum: `spring`/`summer`/`fall`/`winter` (CHECK) |
| `year` | `INTEGER` | e.g., 2022 |
| `source` | `VARCHAR(50)` | e.g., `'Tend_2022'` |
| `cycles_count` | `INTEGER` | number of planting cycles in (crop, season, year) |
| `first_harvest_week` | `INTEGER` | week-of-year of first harvest |
| `peak_harvest_week` | `INTEGER` | week-of-year of peak harvest volume |
| `last_harvest_week` | `INTEGER` | week-of-year of last harvest |
| `yield_total` | `NUMERIC(12,2)` | total harvest (in `yield_unit`) |
| `yield_unit` | `VARCHAR(20)` | e.g., `'kg'`, `'bunch'` |
| `yield_per_bed_min` | `NUMERIC(10,3)` | minimum across cycles |
| `yield_per_bed_max` | `NUMERIC(10,3)` | maximum across cycles |
| `yield_per_bed_median` | `NUMERIC(10,3)` | median across cycles |
| `created_at` | `TIMESTAMP` default `now()` | audit |
| `UNIQUE(crop_id, season, year, source)` | idempotency key |

### 5.2 ALTER `crop_task_templates` CHECK constraint (extension)

B1 created `crop_task_templates` with 14 `task_type` enum values (spec §3 of B1 LOD400). B3 extends to 18 via:

```sql
ALTER TABLE crop_task_templates DROP CONSTRAINT ck_cct_task_type;
ALTER TABLE crop_task_templates ADD CONSTRAINT ck_cct_task_type
  CHECK (task_type IN (
    -- original 14 from B1
    'stale_seed_bed', 'flame_weeder', 'flextine_harrow_1', 'flextine_harrow_2',
    'biodisc', 'hoe', 'hand_weed', 'boron_seaweed_1', 'boron_seaweed_2',
    'straw_mulch_topdress', 'head_pinch_chop', 'mow_and_tarp',
    'at_seeding_transplanting', 'net_row_cover',
    -- NEW 4 from B3
    'nursery_seed', 'pest_spray', 'potting_up', 'thinning'
  ));
```

`TASK_TYPE_VALUES` tuple in `crop_task_templates.py` ORM is also extended in the same migration (sync via post-migration sanity test). Per IR rules, the ORM file IS LOD500_LOCKED post-B1; B3 needs explicit GCR to modify it (see §10).

### 5.3 New source_value fields populated

| field_name | from sheet | unit |
|------------|------------|------|
| `days_in_gh_total` | GREENHOUSE_PLAN | days |
| `days_to_first_potting` | GREENHOUSE_PLAN | days |

Both with `source='Tend_<year>'`, `trust_tier='OP'`, `confidence_weight=0.55`.

## 6. Trust-layer placement

| Field | Value |
|-------|-------|
| `source` | `'Tend_<year>'` (e.g., `'Tend_2022'`) — already registered in `SOURCE_REGISTRY` per WP-A |
| `trust_tier` | `'OP'` |
| `confidence_weight` | `0.55` |
| Hard override? | No |
| Blend behavior | OP enters the standard `reconcile_field()` engine; loses to EX/NI hard overrides; competes with PR (JMF B1) per field policy |

For `documented_price`: B3 OP entries lose to canonical Tend already in WP-A; B3's contribution is mostly historical aggregation (via `crop_harvest_stats`) which is NOT in `crop_variety_source_values`.

## 7. Engine + flow diagram

```
Tend_2022 CSVs (3 files: TASKS, GREENHOUSE_PLAN, HARVESTS)
   │
   ▼
tend_overlay.py
   ├── parse_tasks_templates  → whitelist filter → timing aggregation
   │      └─▶ crop_task_templates (source='Tend_2022', trust_tier='OP')
   │
   ├── parse_greenhouse_plan  → 2 scalar fields per variety
   │      └─▶ crop_variety_source_values → reconcile_field() → crop_field_enrichment
   │
   └── parse_harvests_aggregate  → (crop, season, year) statistics
          └─▶ crop_harvest_stats (NEW table; NOT scalar fields)
```

The `parse_harvests_aggregate` path is **terminal** — no engine integration; it's read directly by future UI surfaces for "this season vs prior years" comparison.

## 8. Dependencies

### 8.1 Direct

- **WP-B1** (LOD500_LOCKED at `6a85561`) — supplies `crop_task_templates` schema (B3 ALTER constraint + insert with `source='Tend_<year>'`). Also supplies the importer pattern (`_default_variety_id`, `_upsert_source_value`).
- **WP-B1-patch01** (LOD500_LOCKED at `3e1f946`) — supplies extended `JMF_CROP_MAP` (86 entries) — though B3 uses `TEND_CROP_MAP` from `constants.py` (already-existing, not modified).
- **WP-A** (LOD500_LOCKED at `594cbc8`) — supplies `SOURCE_REGISTRY` (`Tend_<year>` already registered as OP class) + `reconcile_field()` for the 2 scalar fields.

### 8.2 External

- Python: `csv` (stdlib), `statistics` (stdlib for median calculations).
- Filesystem: read-only access to `Tend_2022/` directory.

### 8.3 Tooling

- Builder: any non-team_190 (sfa_build Sonnet sub-agent recommended)
- Validator: team_190 (GPT-5.5, non-Claude)

## 9. LOD500_LOCKED inventory (unchanged in B3)

All WP-A + WP-B1 + patch01 deliverables remain locked. Headline items:

- All WP-A engine SSoT modules
- `organic_market_agent/crop_book/importer/tend.py` (raw-material guard — NOT to be replaced; B3 adds `tend_overlay.py` alongside)
- All B1 + patch01 deliverables (`crop_task_templates.py` — see §10 GCR; `jmf_masterclass.py`; migration 044; B1 `constants.py` lines; B1 `seed.py` lines)
- `views.py`, `publisher/`, `mu-plugin/`
- Migrations 001..044 (045 is reserved for B2)

**Permitted modifications:**
- `organic_market_agent/crop_book/constants.py` — APPEND a new `TEND_TASK_TYPE_MAP` dict (Tend label → JMF `task_type` enum value). NOT modify TEND_CROP_MAP or JMF_CROP_MAP.
- `organic_market_agent/crop_book/importer/seed.py` — add `--tend-overlay-only`, `--no-tend-overlay` flags + 1 new call-site block.
- `organic_market_agent/crop_book/crop_task_templates.py` — extend `TASK_TYPE_VALUES` tuple by appending 4 new entries (GCR-B3-1 required; see §10).
- `CHANGELOG.md`.

## 10. GCR requirements

**GCR-B3-1 IS REQUIRED** for B3 to modify the LOD500_LOCKED ORM:

- **File:** `organic_market_agent/crop_book/crop_task_templates.py`
- **Scope:** append exactly 4 new values to the `TASK_TYPE_VALUES` tuple (`nursery_seed`, `pest_spray`, `potting_up`, `thinning`). No other change.
- **Rationale:** the CHECK constraint extension in migration 046 must be mirrored by the ORM-level `TASK_TYPE_VALUES` tuple to keep validation symmetric. Without this, the ORM and the DB schema disagree, causing test fixtures and the `Migration 044 → 046` upgrade path to break.
- **Authorization required:** team_00 sign-off before LOD400 LOCK.

**This GCR will be requested in the L-GATE_S R1 mandate to team_190**, with a parallel request to team_00 for approval. Without GCR approval, B3 LOD400 cannot lock.

(All other modifications are pure-additive — no further GCRs needed.)

## 11. PRE_HANDOFF advisory disposition

| # | Advisory | B3 disposition |
|---|---|---|
| 1 | JMF PDF licensing | **N/A for B3** — Tend CSV data, not JMF PDF. |
| 2 | LLM extraction cache strategy | **N/A for B3** — no LLM in B3. |
| 3 | **Tend task whitelist — confirm final list with team_00 BEFORE LOD400 LOCK** | **PROPOSAL pending team_00 confirmation (this LOD200 → carries into LOD400).** Proposed whitelist (per PROGRAM_BRIEF §4):<br/>`Transplant`, `Direct Sow`, `Greenhouse Sow`, `Weed`, `Row Cover & Mulch`, `Stale Bed`, `Pest & Disease`, `Potting up`, `Thin`.<br/>Proposed blacklist:<br/>`Maintenance`, `Irrigate`, `Trellis (when planting=blank)`, `Seed Cleaning`, `Drill Sow`, `השלמות שתילה`, `ריכוז שעות`, `הידרופוניקה`.<br/>**team_00 sign-off requested in the L-GATE_S mandate to team_190.** Both lists fixed in LOD400 §6. |
| 4 | Transitive WP-A dependency | **Addressed** in §8.1 (named WP-A commit + specific surfaces: `SOURCE_REGISTRY` Tend_<year> entries, `reconcile_field()`, `_upsert_source_value`). |

## 12. AC and test count targets

- **Acceptance Criteria target:** ≥ 12 ACs in LOD400 (PROGRAM_BRIEF §4.4)
- **Test count target:** ≥ 20 tests, preliminary breakdown:
  - 5× whitelist enforcement (each whitelist + blacklist class verified)
  - 4× task-type mapping correctness (Tend label → JMF `task_type`)
  - 3× aggregation (median timing; yield min/max/median; cycle counting)
  - 3× DB integration on SQLite in-memory (upsert; UNIQUE; idempotent re-import)
  - 2× `crop_harvest_stats` no-per-record assertion (table count after import ≤ #crops × 4 seasons × 1 year)
  - 1× crop-name mapping spot-check (Tend → DB Hebrew via existing TEND_CROP_MAP)
  - 1× CHECK constraint regression on ALTER (the 4 new enum values accepted; B1's 14 still accepted; rogue value rejected)
  - 1× CLI behavior (`--tend-overlay-only`)

Final inventory fixed in LOD400 §10.

## 13. Open questions (resolved in LOD400)

1. **Tend task whitelist — final list** — propose in §11; awaiting team_00 confirmation.
2. **Season enum** — propose: `spring`/`summer`/`fall`/`winter`. LOD400 confirms (Israel-specific seasonal boundaries documented in module comment).
3. **Year boundary** — propose: calendar year matches Tend folder name (`Tend_2022` → year=2022). LOD400 confirms.
4. **Task-type mapping** — proposed in PROGRAM_BRIEF §4 table. LOD400 §6 nails down the exact dict literal.
5. **Multi-year handling** — B3 ingests Tend_2022 only. Tend_2023+ will be a follow-up patch (re-run with `--year 2023`). LOD400 confirms.

## 14. Sequencing

```
WP-B1 + patch01 (LOD500_LOCKED) ──┐
                                    ├──▶ WP-B3 (this WP)
WP-A (LOD500_LOCKED) ──────────────┘     and WP-B2 (parallel)
```

B3 and B2 are **parallel-eligible** — no inter-dependency. B3 writes to `crop_task_templates` (extension), `crop_variety_source_values` (additive), and `crop_harvest_stats` (NEW). B2 writes to `crop_knowledge_notes` (NEW). No write conflicts.

---

*LOD200 v1.0.0 — authored 2026-05-25 by team_110 under EXECUTION_MANDATE SFA-S003-P002-WP-B (same mandate covers B1, B1-patch01, B2, B3).*
*Next phase: LOD400 spec. **Blocking question for team_00:** confirm the §11 advisory #3 whitelist before LOD400 lock.*
