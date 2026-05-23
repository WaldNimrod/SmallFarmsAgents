---
id: SFA-S003-P002-WP-A-LOD200
wp: SFA-S003-P002-WP-A — Data Enrichment Architecture
gate: L-GATE_S (LOD200 — architecture design)
status: LOD200_LOCKED — team_00 advisory PASS 2026-05-23
author: team_110 (Claude Sonnet 4.6, Domain Architect)
authored_in_worktree: claude/gallant-elbakyan-727a60
date: 2026-05-23
version: v1.1.0
changelog: >
  v1.1.0 — team_00 advisory PASS 2026-05-23: (1) Added NI + UC source classes to
  taxonomy; (2) Added statistical outlier gate to reconciler (§7.6); (3) Updated
  trust-weight table; (4) UC moderation gate contract added (§5.4); (5) GCR_1
  pre-authorized; (6) Status LOD200_LOCKED.
  v1.0.0 — initial draft by team_110.
decision_ref: _COMMUNICATION/team_00/DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md
promotion_note: >
  Written to _aos/work_packages/ per team_110 onboarding mandate.
  team_100 must add WP-A entry to roadmap.yaml and route to L-GATE_S.
---

# LOD200 — SFA-S003-P002-WP-A: Data Enrichment Architecture

---

## §1  Purpose

This document is the **Phase 1 LOD200** for work package `SFA-S003-P002-WP-A`.

The ספר גידולים (Crop Book) shipped by S003-P001 is a production-grade, read-only
agronomic reference built from two sources: **Tend** (5-year farm operational records)
and **JMF** (MasterClass prescriptive curriculum). The reconciler that merges them uses
a hard-coded, per-field priority order with no confidence signal, no range representation,
and no extensibility contract for new sources.

This WP designs the **data enrichment layer** that turns the existing source-values
audit trail into an actionable multi-source confidence model, enabling:

1. Structured **source taxonomy** (formal classes + trust tiers per field)
2. **Schema extensions** for confidence metadata and per-field ranges
3. A **pluggable, weighted reconciler** that survives new source additions without
   code surgery
4. A **validation harness** that backtests the reconciler against known ground truth
   (team_00 expert overrides)
5. A **UI surfacing strategy** that shows confidence, not just presence

Phase 2 of this WP (post-GATE_1) will produce the LOD400 spec → LOD500 build.

---

## §2  Baseline — Production System (S003-P001)

| Item | Value |
|------|-------|
| Schema | 6 tables: `crop_families`, `crops`, `crop_varieties`, `crop_variety_source_values`, `crop_conversion_groups`, `crop_unit_conversions` |
| Migrations | 035–040 (Alembic, PostgreSQL 16.13, head=040) |
| ORM | 6 SQLAlchemy classes in `organic_market_agent/crop_book/models.py` |
| Seeded data | 52 crops / 242 varieties (as of production deploy 2026-05-10) |
| Reconciler | `importer/reconciler.py` — priority-based single-winner per field |
| Source values | `crop_variety_source_values` — per-(variety × field × source) audit trail |
| UI | Flask Blueprint `/crop-book/`, 8 tabs including מקורות (sources) |
| WP integration | WordPress SPA at https://www.nimrod.bio/crop-book/ |

### 2.1  Current source labels in source_values

| Label in `source` column | Meaning |
|--------------------------|---------|
| `Tend_2022` (and per-year variants) | Tend CSV data, that calendar year |
| `JMF` | JMF MasterClass XLSX |
| `team_00` | Manual expert override (hardcoded in `constants.TEAM00_DTM_OVERRIDES`) |

### 2.2  Current reconciler priority order (hardcoded in reconciler.py)

| Field | Priority |
|-------|----------|
| `days_to_maturity` | team_00 > JMF > Tend (latest) |
| `avg_yield_per_bed_m` | Tend multi-year mean > JMF |
| `documented_price` | Tend PRODUCT_SOLD (most recent year) |
| `in_row_spacing_cm` | JMF > Tend |
| `rows_per_bed` | JMF > Tend |
| `planting_season` | JMF > Tend |
| seeder / gear fields | JMF only |
| `rootstock_variety` | team_00 > Tend |

### 2.3  What is NOT in the current system

- No confidence score or trust-tier tag on source_values rows
- No range (min/max) for numeric fields on `crop_varieties`
- No market price from OMA (link exists via `crops.oma_product_id` FK but unused)
- No web source integration
- No backtesting / calibration harness
- No UI signal distinguishing "high confidence field" from "single-source guess"

---

## §3  Current Source Landscape

| Source | Label pattern | Type | Status | Fields contributed |
|--------|---------------|------|--------|-------------------|
| Tend (farm records) | `Tend_YYYY` | Operational | Live | DTM, yield, price, spacing, planting method |
| JMF (MasterClass) | `JMF` | Prescriptive | Live | DTM, spacing, rows/bed, seasons, seeder, price |
| team_00 overrides | `team_00` | Expert | Live | DTM overrides (ארוגולה); rootstock |
| OMA market index | — | Market | **FK linked, not yet imported** | Potential: current market price per product |
| Web sources | — | Web | **TBD — not yet defined** | Potential: Israeli extension service, agri databases |

The `crops.oma_product_id` column already creates a FK bridge to the OMA products
table. No importer or reconciler rule currently uses it.

---

## §4  The Data-Weight Problem

The current system has three interrelated gaps:

### Gap 1 — Hard-coded priority order with no confidence signal

The reconciler picks one winner per field per the hard-coded order. When JMF says
DTM=60 and Tend says DTM=45 across 5 years, the system silently returns 60 with no
indication of disagreement. The user and downstream consumers see only the winner.

**Impact**: Users cannot distinguish "all sources agree" (high confidence) from
"we picked JMF because it was in the list first" (low confidence).

### Gap 2 — No range representation for key numeric fields

Fields like `days_to_maturity`, `avg_yield_per_bed_m`, and `documented_price` are
single scalars on `crop_varieties`. When sources disagree, the range of reported
values carries agronomic meaning (e.g., "this crop matures in 45–60 days depending
on conditions") that is currently discarded.

**Impact**: The crop book gives false precision. A single DTM=60 is less useful to
a farmer than "45–60 days, typically 52 in Israel."

### Gap 3 — New source onboarding requires reconciler surgery

Adding a new source (OMA prices, web, future community sources) means:
- Modifying `reconciler.py` to add priority rules
- Modifying `constants.py` to add label mappings
- No declarative registry — each addition is a bespoke code change

**Impact**: WP-A's value multiplies with each new source. Without an extensibility
contract, each addition is a GCR-level change.

---

## §5  Source Taxonomy

### 5.1  Source classes (formal)

Seven classes in total — the first five are active in WP-A; the last two are
design-registered for future phases.

| Class | Code | Definition | Examples | WP-A status |
|-------|------|-----------|---------|------------|
| Expert | `EX` | Human expert override — domain authority judgment after source review | team_00 overrides in `constants.py` | Active |
| Nimrod-Input | `NI` | Files / links directly provided by team_00 — curated by Nimrod outside the formal Tend/JMF pipeline | CSV, XLSX, or URL sets Nimrod supplies during build | Active (design); importer in WP-A if files arrive |
| Prescriptive | `PR` | Reference / curriculum material — curated agronomic benchmarks | JMF MasterClass XLSX | Active |
| Operational | `OP` | Actual farm records — observed data from this specific farm's operations | Tend CROP_PLAN, PRODUCT_SOLD, HARVESTS (2018–2022) | Active |
| Market | `MK` | Community market index — crowd-sourced price benchmark | OMA products table (via `oma_product_id`) | Design-registered; importer in WP-B |
| Web | `WB` | External third-party databases — TBD scope | Israeli extension service, Agria, MASHAV | Design-registered; scope in WP-B |
| User-Community | `UC` | Future user-submitted data — crowd-sourced from platform users | In-app form submissions | Design-registered; moderation gate required (see §5.4) |

### 5.2  Trust tier per field

Trust tier = ordered list of source classes that win, highest first.
NI sits between EX and PR across all fields.

| Field | Trust order | Rationale |
|-------|------------|-----------|
| `days_to_maturity` | EX › NI › PR › OP | DTM is agronomically prescriptive; actual farm harvests early/late. Expert knows Israel-specific adaptation. |
| `avg_yield_per_bed_m` | EX › NI › OP_multi_yr › PR › WB | Five years of observed farm yield beats textbook. Web as supplementary fallback. |
| `documented_price` | EX › NI › OP_latest › MK › WB | Actual sale price from this farm. Market index as benchmark when no farm data. |
| `in_row_spacing_cm` | EX › NI › PR › OP › WB | Spacing is prescriptive; farm adapts but JMF is authority for teaching. |
| `rows_per_bed` | EX › NI › PR › OP | Same reasoning as spacing. |
| `planting_season` | EX › NI › PR › OP › WB | Israel climate context is expert domain; prescriptive before observed. |
| `harvest_window_*` | EX › NI › PR › OP | Prescriptive range defines the planning envelope. |
| `seeder` / gear fields | NI › PR | Equipment data: NI if Nimrod provides; JMF otherwise. |
| `rootstock_variety` | EX › NI › OP | Expert knows grafting practice; Tend records rootstock used. |

### 5.3  Trust weight defaults (for weighted numeric blend)

These weights apply to the weighted-mean calculation. EX and NI are both
treated as hard overrides when present (EX wins over NI if both present).

| Class | Weight | Notes |
|-------|--------|-------|
| EX | 1.0 | Hard override — not blended; always wins |
| NI | 0.85 | Hard override — wins over all non-EX sources; not blended |
| PR | 0.70 | Blended when EX + NI absent |
| OP | 0.55 | Bumped to 0.75 for multi-year mean with ≥ 3 non-outlier years |
| MK | 0.40 | Blended when available (WP-B) |
| WB | 0.30 | Default; source-specific calibration applied after validation harness §8 |
| UC | 0.15 | Only included in blend after moderation gate PASS (see §5.4) |

EX and NI override the weighted-mean entirely. The weights govern PR/OP/MK/WB/UC
blending when neither EX nor NI is present.

### 5.4  UC moderation gate (design contract — implementation WP-B+)

User-Community (UC) data must not enter the weighted-mean blend until it passes
a moderation gate. The design contract (schema must be compatible from WP-A):

- `crop_variety_source_values.source` label for UC entries: `UC:<user_id>` or `UC:aggregate`
- UC rows with `trust_tier='UC'` are stored in source_values but excluded from
  reconciler blend unless `confidence_weight IS NOT NULL AND confidence_weight > 0`
- A moderation action sets `confidence_weight = 0.15` (or 0.0 to permanently reject)
- The reconciler checks `confidence_weight IS NOT NULL` before including UC rows
- This design is backward-compatible: all existing rows have NULL confidence_weight
  for UC class → excluded → no behavior change

No UC importer is built in WP-A. The schema and reconciler must be compatible.

---

## §6  Schema Delta Analysis and Decision

### 6.1  Constraint: LOD500_LOCKED files

Per the iron rules for this WP:

| File / Path | Status | Implication |
|-------------|--------|-------------|
| `organic_market_agent/crop_book/models.py` | LOD500_LOCKED | Adding columns to existing ORM classes requires GCR + team_100 mandate |
| `organic_market_agent/crop_book/views.py` | LOD500_LOCKED | Modifying existing routes requires GCR (see §9) |
| `organic_market_agent/db/versions/035–040_*.py` | LOD500_LOCKED | Cannot modify; extend via 041+ |
| `publisher/` | LOD500_LOCKED | No changes |
| mu-plugin | LOD500_LOCKED | No changes |

### 6.2  Schema delta options

**Option A — Extend existing tables (minimal new tables)**
- Migration 041: Add `trust_tier VARCHAR(20)`, `confidence_weight NUMERIC(5,4)`,
  `is_outlier_rejected BOOLEAN` to `crop_variety_source_values`
- Migration 042: Add `dtm_min INTEGER`, `dtm_max INTEGER`, `yield_min NUMERIC(10,4)`,
  `yield_max NUMERIC(10,4)` to `crop_varieties`
- ⚠️ Both require modifying `models.py` (locked) → GCR required

**Option B — New `crop_field_enrichment` table (no models.py touch)**
- Migration 041: Create `crop_field_enrichment` — stores per-(variety, field) consensus:
  `variety_id`, `field_name`, `value_min`, `value_max`, `value_best`, `confidence_score`,
  `source_count`, `winning_source_class`, `computed_at`
- New model class in `organic_market_agent/crop_book/enrichment_models.py` — separate file,
  does not modify `models.py`
- Migration 042 (if needed): Add `trust_tier`, `confidence_weight` to `crop_variety_source_values`
  — requires models.py GCR

**Option C — Hybrid: new table for range/confidence + GCR-gated column additions**
- Migration 041: New `crop_field_enrichment` table (no GCR)
- Migration 042: Add `trust_tier`, `confidence_weight` to `crop_variety_source_values` (GCR for models.py)
- GCR issued as part of this WP's LOD400 planning before builder dispatch

### 6.3  Decision: Option C (Hybrid)

**Rationale**: The `crop_field_enrichment` table can ship without GCR and delivers
the range + confidence value immediately. The `trust_tier` + `confidence_weight` columns
on `crop_variety_source_values` are tightly coupled to the audit semantics of that table —
putting them in a join-required side table would fragment the audit trail. GCR for models.py
is accepted as a known dependency; team_100 issues it as part of WP-A LOD400 planning.

### 6.4  Migration 041 — `crop_field_enrichment` table

```sql
CREATE TABLE crop_field_enrichment (
    id             BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    variety_id     BIGINT NOT NULL REFERENCES crop_varieties(id) ON DELETE CASCADE,
    field_name     VARCHAR(100) NOT NULL,  -- English DB col name (e.g. 'days_to_maturity')
    value_min      NUMERIC(14,6),          -- lowest reliable source value
    value_max      NUMERIC(14,6),          -- highest reliable source value
    value_best     NUMERIC(14,6),          -- weighted-mean best estimate (see §7)
    confidence_score NUMERIC(5,4),         -- 0.0 (single-source guess) → 1.0 (all sources agree)
    source_count   INTEGER NOT NULL DEFAULT 0,  -- number of non-outlier sources
    winning_source_class VARCHAR(20),      -- class code of the EX/PR/OP/MK/WB winner
    computed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(variety_id, field_name)
);
```

Priority fields to populate in initial enrichment run:
- `days_to_maturity`
- `avg_yield_per_bed_m`
- `documented_price`

Additional fields (lower priority, best-effort):
- `in_row_spacing_cm`
- `rows_per_bed`

### 6.5  Migration 042 — extend `crop_variety_source_values` (GCR-gated)

```sql
ALTER TABLE crop_variety_source_values
    ADD COLUMN trust_tier          VARCHAR(20),     -- OP/PR/EX/MK/WB
    ADD COLUMN confidence_weight   NUMERIC(5,4),    -- 0.0–1.0 per-observation weight
    ADD COLUMN is_outlier_rejected BOOLEAN NOT NULL DEFAULT FALSE;
```

Backfill rule for existing rows:
- `trust_tier`: inferred from `source` label (`Tend_*` → OP; `JMF` → PR; `team_00` → EX)
- `confidence_weight`: set to class default per §5.3
- `is_outlier_rejected`: TRUE where `note LIKE '%OUTLIER_REJECTED%'`

The backfill is a one-time idempotent migration step (not part of the normal import flow).

**GCR requirement**: Before LOD400 build can start on migration 042, team_100 must
issue a formal GCR authorizing models.py modification to add these columns to
`CropVarietySourceValue`. The GCR is filed per the AOS governance template.

---

## §7  Reconciler Architecture

### 7.1  Current architecture (to be replaced)

```
importer/reconciler.py
  reconcile_dtm()       — DTM-specific, hard-coded team_00>JMF>Tend
  reconcile_variety()   — field-by-field with hard-coded priority lists
```

There is no registry — each new source requires direct code modification.

### 7.2  Target architecture: Pluggable Source Registry + Field Policy Table

The new reconciler is composed of three components:

**Component A — Source Registry**

A declarative registry mapping source labels to their class code and trust weight:

```python
# organic_market_agent/crop_book/source_registry.py

SOURCE_REGISTRY: dict[str, SourceSpec] = {
    "team_00":    SourceSpec(label="team_00", cls="EX", weight=1.0),
    "JMF":        SourceSpec(label="JMF",     cls="PR", weight=0.70),
    "Tend_2022":  SourceSpec(label="Tend_2022", cls="OP", weight=0.55),
    "Tend_2021":  SourceSpec(label="Tend_2021", cls="OP", weight=0.55),
    # ... one entry per Tend year; weight bumped at runtime if ≥3 OP years available
    # Adding a new source = one line here, no reconciler changes needed
}
```

New sources (OMA, web) register here. The reconciler reads class + weight from the
registry, never from hard-coded strings.

**Component B — Field Policy Table**

A declarative mapping from field name to its trust order (class priority list):

```python
FIELD_POLICY: dict[str, FieldPolicy] = {
    "days_to_maturity": FieldPolicy(
        trust_order=["EX", "PR", "OP"],
        blend_strategy="weighted_mean",    # or "hard_winner"
        outlier_check="leaf_crop_dtm",
    ),
    "avg_yield_per_bed_m": FieldPolicy(
        trust_order=["OP", "PR", "WB"],
        blend_strategy="weighted_mean",
        multi_year_mean=True,              # OP values averaged across years first
    ),
    "documented_price": FieldPolicy(
        trust_order=["OP", "MK", "WB"],
        blend_strategy="hard_winner",      # take the latest OP year, not a blend
    ),
    "in_row_spacing_cm": FieldPolicy(
        trust_order=["PR", "OP", "WB"],
        blend_strategy="hard_winner",
    ),
    # ... one entry per reconciled field
}
```

**Component C — Reconcile Engine**

A single `reconcile_field(field_name, source_rows)` function that:
1. Looks up `FIELD_POLICY[field_name]`
2. Groups `source_rows` by source class (from registry)
3. If EX class present → return EX value (hard override; log to enrichment)
4. Else: applies blend_strategy across non-EX classes per trust order
5. Computes: `value_best`, `value_min`, `value_max`, `confidence_score`, `source_count`
6. Returns `(unified_value, enrichment_row)` — unified for `crop_varieties`, enrichment
   for `crop_field_enrichment`

### 7.3  Blend strategies

| Strategy | Behavior | Used when |
|----------|----------|-----------|
| `hard_winner` | Take the highest-class, highest-priority non-outlier value | Categorical fields; price (use most recent) |
| `weighted_mean` | Weighted average across all non-outlier sources, weights from registry | Continuous numeric fields (DTM, yield) |

For `weighted_mean`:
```
value_best = Σ(weight_i × value_i) / Σ(weight_i)
```

For Tend multi-year mean (`multi_year_mean=True`): compute a single OP mean across
all Tend years first, then treat that mean as one OP observation in the blend.

### 7.4  Confidence score formula

```
source_class_spread = len(set(class for non-outlier sources))
agreement_ratio     = 1 - (std_dev / mean) for numeric values (0.0 if 1 source)
confidence_score    = (source_class_spread / len(FIELD_POLICY[field].trust_order))
                      × (1 - agreement_ratio * 0.5)
```

Bounds: clamp to [0.0, 1.0].

Simple interpretation:
- 1.0: all trust tiers present and values fully agree
- 0.5: values present from 2 of 3 trust tiers, moderate spread
- 0.1: single source, no calibration possible

### 7.5  Domain-specific outlier checks (retained from existing logic, moved to policy)

Existing DTM outlier check for leaf crops (`< 20 days`) is preserved but registered
under the `outlier_check="leaf_crop_dtm"` policy key rather than hardcoded in reconciler.

### 7.6  Statistical outlier gate (NEW — mandatory per team_00 decision)

Before any weighted-mean computation, a general statistical outlier gate is applied
to reject values that deviate excessively regardless of domain knowledge. This catches
data entry errors and pathological edge cases.

**Algorithm (per field, per variety, across all candidate source values):**

1. Collect all non-NaN, non-domain-outlier numeric values for the field
2. If n < 2: skip gate (single source cannot be an outlier statistically)
3. Compute modified Z-score: `Z_i = 0.6745 × (x_i - median) / MAD`
   where MAD = median absolute deviation. Robust to small samples.
4. If `|Z_i| > OUTLIER_Z_THRESHOLD` (default: 3.5): mark as statistical outlier
5. Statistical outliers: `is_outlier_rejected = TRUE`, `note` includes
   `STAT_OUTLIER_REJECTED (Z={Z_i:.1f})`; excluded from weighted-mean
6. If all values are rejected: fall back to median of original set + log WARNING

**Threshold defaults:**

| Field | OUTLIER_Z_THRESHOLD | Rationale |
|-------|--------------------|-----------| 
| `days_to_maturity` | 3.5 | Moderate — DTM has real variance across sources |
| `avg_yield_per_bed_m` | 3.0 | Tighter — yield errors are common in data entry |
| `documented_price` | 3.0 | Tighter — currency/unit mismatches are common |
| (all other numeric) | 3.5 | Default |

Thresholds are registered in `FIELD_POLICY` alongside blend_strategy — overridable
per field without touching reconciler code.

**Interaction with domain-specific outliers:**
Domain-specific rules (§7.5) run first. Statistical gate runs on the remaining
non-domain-rejected values. Both sets are stored in source_values with
`is_outlier_rejected=TRUE` but different `note` prefixes.

Outlier rows are stored in `source_values` with `is_outlier_rejected=TRUE` and
excluded from blend computation but included in `value_min`/`value_max` range
of `crop_field_enrichment` (so the full raw range is preserved for audit).

### 7.6  Backward compatibility

The existing `reconcile_variety()` function signature is retained as a thin wrapper
that calls the new engine. This avoids breaking any callers. The new engine is the
authoritative implementation; the wrapper delegates to it.

---

## §8  Validation Harness Design

### 8.1  Goal

Empirically calibrate the auto-reconciler: given the existing team_00 overrides as
ground truth, would the reconciler arrive at the same values without those overrides?

### 8.2  Approach

```
scripts/validate_enrichment.py  (standalone, reads from live DB)
```

For each field with at least one EX-class source_value in the DB:
1. Simulate reconciler WITHOUT EX rows (shadow run: set EX weight = 0)
2. Compute `auto_value` from the remaining sources
3. Compare with the `team_00` (EX) value
4. Compute `delta_pct = abs(auto_value - team_00_value) / team_00_value × 100`
5. Classify:
   - CALIBRATED: delta_pct ≤ 20% — reconciler aligns with expert
   - MARGINAL: 20% < delta_pct ≤ 40% — manual review recommended
   - MISALIGNED: delta_pct > 40% — reconciler and expert disagree; team_00 input needed

### 8.3  Output format

```
CALIBRATION REPORT — crop_field_enrichment validation harness
Generated: 2026-XX-XX
Scope: 1 crop × 1 field (ארוגולה / days_to_maturity — only current EX override)

| crop      | field             | team_00_val | auto_val | delta_pct | status     |
|-----------|-------------------|-------------|----------|-----------|------------|
| ארוגולה   | days_to_maturity  | 21          | 23       | 9.5%      | CALIBRATED |
```

### 8.4  Integration into seed import flow

Add `--validate` flag to `importer/seed.py`:
```
python -m organic_market_agent.crop_book.importer.seed --validate
```
This re-runs the validation harness after a seed run and logs the calibration report.
Non-blocking (exit 0 even if MISALIGNED — misalignment is a data quality signal,
not a failure).

### 8.5  Future use

When new sources are integrated (OMA prices, web), re-run the harness to measure
whether the new source shifts values toward or away from team_00 ground truth.
This provides evidence for tuning source trust weights.

---

## §9  UI Surfacing Strategy

### 9.1  What to surface

For each enriched field:
- **Range badge**: "45–60 days" instead of just "60 days" (uses `value_min`/`value_max` from
  `crop_field_enrichment`)
- **Confidence indicator**: one of three states shown as a colored dot/icon:
  - High (confidence_score ≥ 0.7): green
  - Medium (0.4–0.7): amber
  - Low (< 0.4): gray
- **Source class chips** in the מקורות tab: EX/PR/OP/MK/WB badge per source row

### 9.2  LOD500_LOCKED constraint handling

`views.py` is locked. Three options:

| Option | Approach | GCR needed |
|--------|----------|-----------|
| A | Modify `crop_detail()` in `views.py` to load enrichment data and pass to template | Yes — modifying views.py |
| B | New route `/crop-book/<id>/enrichment/` in a new `enrichment_views.py` registered on the same blueprint — template loaded via HTMX or JS fetch | No — new file |
| C | Enrichment data embedded in the WordPress SPA JSON (`data.json`) — JS renders confidence in the WP-hosted view only, Flask view unchanged | No — publisher extension only |

**Decision: Option A for Flask UI, Option C for WordPress SPA.**

Rationale: Option A requires a GCR for `views.py` but delivers confidence indicators
in the full Flask crop-book detail view (which is the richer UI). Option C is
achievable without GCR and enriches the public WordPress view. Both can be sequenced:
Option C in WP-A build, Option A in WP-B (UI phase) after the GCR is issued.

For WP-A LOD400 build scope:
- **In scope**: Option C (publisher extension — add enrichment JSON to SPA data.json)
  and Option B (new enrichment route, no GCR) for the Flask API endpoint
- **Deferred to WP-B**: Option A (Flask detail page template enhancement, requires GCR)

### 9.3  WordPress SPA enrichment (in WP-A scope)

Extend the `CropBookPublisher.generate_data()` method (in `publisher/` — also locked).
⚠️ `publisher/` is LOD500_LOCKED. Same GCR constraint applies.

**Revised approach**: Add enrichment JSON to a **new artifact** (`sfagent-crop-book-enrichment.json`)
uploaded as a separate WP REST media file. The SPA JavaScript fetches this on demand
(lazy-load). This does not modify any existing publisher file — it adds a new output
path through the existing `dispatch_upload` mechanism under a new `profile=crop_book_enrichment`.

This is fully additive — no locked files touched.

### 9.4  GCR dependency summary for UI

| GCR | Scope | When | Required for |
|-----|-------|------|-------------|
| GCR_1: models.py | Add 3 columns to CropVarietySourceValue | Before LOD400 build | Migration 042 |
| GCR_2: views.py | Modify crop_detail() route + template | WP-B planning | Option A Flask UI |
| GCR_3: publisher/ | Extend generate_data() | WP-B planning | Inline enrichment in existing data.json |

---

## §10  LOD500_LOCKED Constraint Matrix

| Component | Locked? | WP-A action | GCR needed |
|-----------|---------|------------|-----------|
| models.py (existing classes) | Yes | Add columns to CropVarietySourceValue | GCR_1 |
| models.py (new class) | N/A | New file enrichment_models.py | No |
| views.py | Yes | No change in WP-A | — |
| publisher/ | Yes | No change in WP-A (new artifact via dispatch_upload) | No |
| migrations 035–040 | Yes | No touch | — |
| migrations 041+ | New | Create 041, 042 | No (new files) |
| mu-plugin | Yes | No change | — |
| importer/ (existing) | No | Extend reconciler.py (new engine, wrapper retained) | No |
| constants.py | No | Add SourceSpec dataclass, extend TEAM00_DTM_OVERRIDES as needed | No |
| source_registry.py | New file | Create | No |
| enrichment_models.py | New file | Create | No |

---

## §11  Effort Estimate

### Phase 1 (WP-A) — Data Layer

| Task | Size | Notes |
|------|------|-------|
| Source registry (source_registry.py + FIELD_POLICY) | SMALL | Declarative data structures |
| Migration 041 (crop_field_enrichment) | SMALL | New table, new model class |
| Migration 042 (extend source_values) | SMALL | 3 columns + backfill — GCR_1 must precede |
| GCR_1 (models.py authorization) | SMALL | team_100 issues; not a builder task |
| Reconciler engine rewrite (reconciler.py) | NORMAL | Pluggable engine + blend strategies + confidence score |
| Updated importer (trust_tier + weight population) | NORMAL | Extend tend.py + jmf.py |
| Enrichment compute pass (populate crop_field_enrichment) | NORMAL | New enrichment_runner.py |
| Validation harness (scripts/validate_enrichment.py) | NORMAL | Shadow-run + calibration report |
| New enrichment SPA artifact (sfagent-crop-book-enrichment.json) | SMALL | New dispatch_upload profile |
| Tests | NORMAL | ≥20 new tests covering registry, engine, harness |
| **WP-A total** | **LARGE** | ~16–20h builder time |

### Phase 2 (WP-B) — UI + Source Expansion

| Task | Size | Notes |
|------|------|-------|
| OMA market price importer (Class MK) | NORMAL | Reads from OMA products table via oma_product_id |
| Web source integration (scope TBD) | NORMAL | Depends on sources confirmed by team_00 (Q5) |
| Flask UI enrichment (Option A) | NORMAL | GCR_2 for views.py; range badges + confidence dots |
| Publisher enrichment inline (GCR_3) | NORMAL | GCR_3 for publisher/; enrich existing data.json |
| **WP-B total** | **LARGE** | ~14–18h builder time |

---

## §12  Open Questions for team_00 (Advisory Review)

These questions require team_00 decisions before LOD400 can be finalized.

| # | Question | Default if no decision |
|---|----------|----------------------|
| Q1 | Is the **weighted-mean blend** (`value_best = weighted average`) the right approach for DTM, yield, price — or prefer simpler hard_winner with confidence annotation only? | Proceed with weighted_mean (richer, aligns with the enrichment goal) |
| Q2 | Should the **range (value_min / value_max)** be surfaced in the UI? Or just the confidence score? | Surface both — range is the most actionable signal for farmers |
| Q3 | Is **OMA market price integration** in WP-A scope (alongside the data layer), or deferred to WP-B? | Defer to WP-B — OMA integration adds complexity independent of the enrichment architecture |
| Q4 | What specific **web sources** are in scope for P002 overall? (Israeli Ministry of Agriculture? Agria? RHS? MyFarm?) Needed to define WB class importers in WP-B. | Defer — team_00 to specify in WP-B eligibility |
| Q5 | Should `confidence_score` be shown to end users in the public WordPress SPA, or only in the admin Flask UI? | Both — confidence is the core value proposition of the enrichment layer |
| Q6 | Pre-authorize **GCR_1** (models.py extension for migration 042) as part of this LOD200 approval, or require a separate GCR artifact? | Prefer pre-authorization here to unblock WP-A LOD400 build |
| Q7 | Is WP-A and WP-B the right split, or should both be a single WP with two phases? | Two WPs is cleaner (different gate owners: WP-A data layer, WP-B UI+sources) |

---

## §13  Acceptance Criteria for GATE_1 / LOD200 PASS

LOD200 is accepted when team_00 advisory review PASSES with all blocking Q1–Q7
answered and no material objections to the taxonomy, schema decisions, or reconciler
approach.

Specific GATE_1 acceptance criteria:

| AC | Criterion | Status |
|----|-----------|--------|
| AC-L200-01 | Source taxonomy (§5) accepted: 7 classes (EX/NI/PR/OP/MK/WB/UC) with trust tiers per field | ✓ LOCKED (team_00 2026-05-23) |
| AC-L200-02 | Schema delta decision accepted: Option C hybrid (migration 041 new table, migration 042 GCR-pre-authorized) | ✓ LOCKED |
| AC-L200-03 | Reconciler architecture accepted: pluggable registry + field policy + weighted-mean blend + statistical outlier gate | ✓ LOCKED |
| AC-L200-04 | Validation harness design accepted: shadow-run calibration against team_00 overrides | ✓ LOCKED |
| AC-L200-05 | UI surfacing approach accepted: WP-A = enrichment artifact + Flask API route; WP-B = full Flask template | ✓ LOCKED |
| AC-L200-06 | Effort estimate reviewed: WP-A LARGE (~16–20h) + WP-B LARGE (~14–18h) | ✓ LOCKED |
| AC-L200-07 | Q1–Q7 all resolved per DECISION_SFA-S003-P002-WP-A-LOD200_2026-05-23_v1.0.0.md | ✓ LOCKED |
| AC-L200-08 | GCR_1 (models.py) pre-authorized by team_00 — no separate artifact required | ✓ LOCKED |
| AC-L200-09 | NI + UC classes design-registered in taxonomy; UC moderation gate contract specified in §5.4 | ✓ LOCKED |
| AC-L200-10 | Statistical outlier gate (§7.6) mandatory for weighted-mean; Z-score method with per-field threshold | ✓ LOCKED |

---

## §14  Dependencies and Routing

### 14.1  Prerequisites (all SATISFIED)

- SFA-S003-P001 all 5 WPs LOD500_LOCKED — ✓ (as of 2026-05-23, commit d2a61a1)
- DB online (PostgreSQL 16.13, alembic head=040) — ✓
- Source data READ-ONLY (Tend CSVs, JMF XLSX) — ✓ (no modification permitted)

### 14.2  Routing after LOD200 PASS

```
team_110 → LOD200 DRAFT delivered to team_00 (advisory review)
  ↓
team_00 → advisory feedback + Q1–Q7 decisions → iteration with team_110
  ↓
team_00 → LOD200_LOCKED ACK
  ↓
team_100 → packages into L-GATE_S bundle (spec + constitutional checklist)
  → promotes LOD200 to _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md (formally)
  → adds WP-A entry to roadmap.yaml
  ↓
team_190 → L-GATE_S validation (non-Claude, cross-engine per IR#1)
  ↓
PASS → team_100 authors LOD400 spec (or delegates to team_110)
  ↓
team_10 (sfa_build) → LOD500 build
  ↓
team_190 → L-GATE_V → LOD500_LOCKED
  ↓
team_191 → archive
  ↓
canonical merge → main
```

### 14.3  GCR dependency chain

```
GCR_1 (models.py) — required before LOD400 build for migration 042
  → team_100 files GCR after LOD200_LOCKED
  → team_00 approves
  → team_100 issues builder mandate with GCR_1 authorization

GCR_2 (views.py) — required for WP-B UI phase
GCR_3 (publisher/) — required for WP-B publisher inline enrichment
  → Both deferred to WP-B LOD400 planning
```

---

*LOD200 v1.0.0 — authored 2026-05-23 by team_110 (Claude Sonnet 4.6, Domain Architect)*
*Branch: claude/gallant-elbakyan-727a60*
*Delivered to: _aos/work_packages/S003/SFA-S003-P002-WP-A/LOD200_spec.md*
*Advisory review requested from: team_00*
