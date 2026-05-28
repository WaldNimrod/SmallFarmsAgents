---
id: SFA-S003-P002-WP-C5-LOD200
wp: SFA-S003-P002-WP-C5 — Cleanup & Refinement (Phase A code+data, Phase B team_00 manual)
gate: L-GATE_S (LOD200)
status: PROPOSED
author: team_10 (Claude Sonnet 4.7) under team_00 grant 2026-05-26 (Phase A approved 2026-05-28)
date: 2026-05-26 (v1.0.0) / 2026-05-28 (v1.1.0 — Phase A added)
version: v1.1.0
parent_wp_chain:
  - SFA-S003-P002-WP-A (engine SSoT + engine v1.1 inheritance)
  - SFA-S003-P002-WP-B (LOD500_LOCKED)
  - SFA-S003-P002-WP-C1 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C4 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C3 (LOD500_LOCKED) ✅
  - SFA-S003-P002-WP-C2 (partial — Hebrew narrative NI build complete, awaiting closure)
depends_on: [SFA-S003-P002-WP-C2]
activation_condition: "C2 closes OR team_00 explicitly authorizes Phase A early"
mode: "two-phase WP: Phase A = builder code+data cleanup; Phase B = team_00 manual refinement"
decision_record: "_COMMUNICATION/team_10/SFA-S003-P002-WP-C5/DECISION_RECORD_v1.0.0.md"
---

# LOD200 — WP-C5: Cleanup & Refinement (two-phase)

## 1. Mission

After ingestion waves C1+C2+C3+C4 complete, the catalog contains:
- Crop-name duplications (basil, tomato, beans)
- Anonymous variety orphans accumulating source-values per crop
- A new WR (web-research / AI-synthesized) trust tier without governance integration
- ~20 sparse crops needing follow-up (deferred to WP-C6)

WP-C5 cleans this in two phases:

**Phase A — Builder (code+data, this team_10 mandate)**
1. Consolidate crop duplicates per DECISION_RECORD §1-§3
2. Integrate WR trust tier with DB-backed weights table (architectural,
   per DECISION_RECORD §5 — team_00 critical requirement)
3. Refactor `source_registry.py` to a thin facade over the new DB table

**Phase B — team_00 manual refinement** (original v1.0.0 scope, retained)
4. EX overrides for confident-knowledge fields
5. UNMAPPED_CROPS resolution
6. Outlier marking, knowledge note QA, gap-fill

---

## 2. Phase A — In-scope (BUILDER mandate, this WP)

### 2.1 Schema changes (NEW migrations)

| Migration | Purpose | Reversible? |
|-----------|---------|-------------|
| **054** | Create `crop_source_weights` table | Yes (drop_table) |
| **055** | Data cleanup: basil + tomato + beans consolidation | **NO** (data merge) — downgrade is no-op with comment |
| **056** | Seed `crop_source_weights` with current weights + WR=0.60 | Yes (delete rows) |

**`crop_source_weights` schema (migration 054):**

```sql
CREATE TABLE crop_source_weights (
  id              BIGSERIAL PRIMARY KEY,
  source_label    VARCHAR(100) NOT NULL UNIQUE,  -- exact OR prefix pattern like 'WR:*'
  trust_tier      VARCHAR(20)  NOT NULL,         -- EX/NI/PR/OP/MK/WB/UC/WR
  weight          NUMERIC(5,4) NULL,             -- NULL = hard override
  is_hard_override BOOLEAN     NOT NULL DEFAULT FALSE,
  requires_moderation BOOLEAN  NOT NULL DEFAULT FALSE,
  notes           TEXT         NULL,
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK (trust_tier IN ('EX','NI','PR','OP','MK','WB','UC','WR')),
  CHECK (
    (is_hard_override = TRUE AND weight IS NULL)
    OR
    (is_hard_override = FALSE AND (weight IS NOT NULL OR requires_moderation = TRUE))
  )
);
CREATE INDEX idx_csw_tier ON crop_source_weights(trust_tier);
```

### 2.2 Data cleanup (migration 055)

Per DECISION_RECORD §1-§3 (verbatim merges below). All
`source_values` use `INSERT ... ON CONFLICT DO NOTHING` to respect
`UNIQUE(variety_id, field_name, source)`; conflicting rows are kept on
the target (default) variety. After merges, source variety rows are
deleted; source crop rows are deleted.

**Basil (Decision #1):** crop 58 → crop 4
- variety 461 → crop 4 (becomes non-default variant)
- DELETE crop 58

**Tomato (Decision #2, Option A):** keep crops 49 + 73 separated; merge orphans
- crop 49 merges: vid 222, 403, 404, 405, 406 → vid 233; vid 227 → vid 225;
  vid 229 → vid 226
- crop 73 merges: vid 443, 444, 445, 477 → vid 460 (verify 477 source-value
  count before merge — DECISION_RECORD calls this out)

**Beans (Decision #3):** primary = crop 6 (default = מטפסת / Pole/Climbing)
- Rename crop 6.name_en: `'Beans: Bush & Pole'` → `'Beans (default: Pole/Climbing)'`
- Move vid 479 (crop 60 default, 1 sv) → crop 6 default
- Move vid 476 (crop 59 default, 0 sv) → crop 6 as `is_default=False`,
  `name_en='Bush variant'`
- DELETE nonsense varieties in crop 60 (names: `'●'`, `'1'`,
  `'marketgardenerinstitute.com'`, `'Intensive Spacing'`) where sv_count = 0
- DELETE crops 59, 60

### 2.3 Code changes (LOD500_LOCKED-respecting)

| File | Change |
|------|--------|
| `organic_market_agent/crop_book/source_registry.py` | Refactor to thin facade calling `source_weights_db`. Constants retained as **default seed only** (still readable for migration 056 + emergency fallback). Add `WR` to `CLASS_RANK`. |
| `organic_market_agent/crop_book/source_weights_db.py` | **NEW.** `get_source_spec(label) → SourceSpec` reads DB with in-process LRU cache. Fallback chain: exact match → prefix pattern (`WR:*` etc.) → unknown-source default. |
| `tests/crop_book/test_source_weights_db.py` | **NEW.** Coverage: exact lookup, prefix fallback, hard-override semantics, WR tier=0.60, cache reset, fallback when DB row missing. |

**LOD500_LOCKED untouched**: `reconciler.py`, `enrichment_runner.py`,
`validate_enrichment.py` — DB-backed weights are transparent to the
reconciler because `source_registry.get_source_spec()` keeps its
signature.

### 2.4 Verification

1. `alembic upgrade head` clean
2. Static AST check: migrations 054/056 have non-trivial downgrades; 055
   documents the irreversible nature
3. Row-count snapshot before/after migration 055 archived to
   `_COMMUNICATION/team_10/SFA-S003-P002-WP-C5/CLEANUP_AUDIT_v1.0.0.md`
4. `python -m pytest tests/crop_book/test_source_weights_db.py -v` 100% pass
5. `python -m pytest tests/crop_book/ -k "reconciler or source_registry"`
   no regressions (engine v1.1 inheritance still produces CALIBRATED=5/5)
6. `python scripts/run_enrichment.py` re-runs end-to-end with new DB weights;
   enrichment row counts within ±5% of pre-cleanup baseline (gain expected
   from merge consolidation, not loss)
7. `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
   = 29 PASS / 19 SKIP / 0 FAIL

---

## 3. Phase A — Out-of-scope

- New crops or new ingestion (those went into C1-C4; sparse-crop expansion
  is WP-C6)
- Engine v1.1 changes (final since WP-C1 R1 remediation)
- UI work
- Sparse-crop research (deferred to WP-C6)

---

## 4. Phase B — Manual refinement (team_00, original v1.0.0 scope)

After Phase A LOD500_LOCKED, team_00 performs (no builder mandate):

1. **EX overrides** for fields where team_00 has confident knowledge that the
   auto reconciliation produced wrong value
2. **Crop name mapping fixes** — Resolve remaining UNMAPPED_CROPS from C1+C2
3. **Outlier marking** via `is_outlier_rejected=TRUE` flag
4. **Cultivar disambiguation** for varieties with conflicting OP data
5. **Knowledge note review** — Spot-check LLM-extracted NI narrative
6. **Field-level decisions** on remaining MARGINAL/MISALIGNED pairs
7. **Gap-fill** via team_00 domain expertise (NI rows for IL microclimate)

Decision artifacts under `_COMMUNICATION/team_00/SFA-S003-P002-WP-C5/`:
- `EX_OVERRIDES_v1.0.0.md`
- `OUTLIER_DECISIONS_v1.0.0.md`
- `KNOWLEDGE_NOTE_REVIEW_v1.0.0.md`
- `UNMAPPED_RESOLUTIONS_v1.0.0.md`
- `DATA_FROZEN_v1.0.0.md` (closure marker)

Phase B uses helper scripts (team_00 directory authority only):
- `scripts/team_00/add_ex_override.py`
- `scripts/team_00/mark_outlier.py`
- `scripts/team_00/review_calibration.py`

Re-run `enrichment_runner` after each batch of team_00 changes. Final
`validate_enrichment.py` snapshot + `crop_field_enrichment` JSON archive.

---

## 5. Data-model summary (combined)

- **New table**: `crop_source_weights` (migration 054)
- **Data merges**: crops + variety consolidations (migration 055)
- **New rows**: `crop_source_weights` seeds (migration 056); plus Phase B's
  EX/NI manual rows in `crop_variety_source_values` and `crop_knowledge_notes`
- **No new ingestion-table schemas** beyond C4

## 6. Trust-layer placement

| Tier | Weight | Notes |
|------|--------|-------|
| EX | NULL (hard) | team_00 — principal authority |
| NI | NULL (hard) | Nimrod-curated files/links |
| PR | 0.70 | Published research (JMF, university extension) |
| **WR** | **0.60 ★** | **NEW — AI-synthesized research via team_80 multi-engine scout** |
| OP | 0.55 | Operational farm data (Tend, Idan, Curtis, FRANCHI) |
| MK | 0.40 | Market data (placeholder) |
| WB | 0.30 | Web blog (placeholder) |
| UC | NULL (moderation) | User-contributed (moderation gate) |

★ WR weight = 0.60 per DECISION_RECORD §5 Option B (team_00-approved).
**Tunable later via DB UPDATE — single SQL statement, system-wide effect.**
See `_COMMUNICATION/team_10/SFA-S003-P002-WP-C5/DECISION_RECORD_v1.0.0.md`
for the verbatim team_00 requirement.

---

## 7. Dependencies

- Hard (Phase A): WP-C1, WP-C3, WP-C4 LOD500_LOCKED ✅; WP-C2 build complete
  (closure pending — Phase A can start under team_00 explicit authorization
  granted 2026-05-28 in DECISION_RECORD §intro)
- Hard (Phase B): Phase A LOD500_LOCKED

## 8. LOD500_LOCKED untouched

- Same protected list as C1/C4
- ALSO: `reconciler.py`, `enrichment_runner.py`, `validate_enrichment.py`
  are post-engine-v1.1 frozen. No engine changes in C5.
- Earlier migrations (001-053) frozen; only forward migrations 054/055/056.

## 9. GCR requirements

**NONE.** New table `crop_source_weights` is internal infrastructure;
no governance schema change. Engine surface unchanged.

## 10. Success criteria

### Phase A (Builder — this mandate)
- Migrations 054/055/056 applied; alembic head = "056"
- `crop_source_weights` row count: 8 tiers × seed labels (≥20 rows)
- Cleanup audit shows: crops dropped 58/59/60 (and the orphan-variety
  count reduces by ≥9 in crop 49 + ≥4 in crop 73)
- All Phase A tests green; engine v1.1 enrichment regenerated without
  CALIBRATED regressions
- validate_aos.sh: 29 PASS / 19 SKIP / 0 FAIL

### Phase B (team_00 — separate closure)
- All UNMAPPED_CROPS from C1/C2 resolved
- All CALIBRATION MISALIGNED pairs decided
- `DATA_FROZEN_v1.0.0.md` filed by team_00

## 11. Open questions (Phase A — RESOLVED 2026-05-28)

All 5 open questions resolved by team_00 in DECISION_RECORD v1.0.0:
1. Basil consolidation → MERGE crop 58 → 4
2. Tomato consolidation → Option A (keep both, merge orphans)
3. Bean consolidation → MERGE under crop 6, default = מטפסת
4. Sparse crops future → register WP-C6 (LOD200 placeholder authored)
5. WR tier weight → 0.60 ★ WITH critical DB-driven weights architecture

Open questions Phase B retains (for team_00 during manual execution):
- Which crops most urgently need EX overrides beyond ארוגולה DTM?
- Threshold for "acceptable divergence" between auto and team_00 knowledge?
- Should team_00 override JMF cultivar recommendations with Israeli-adapted
  choices?

---

*v1.0.0 authored by team_10 (Claude Sonnet 4.7) 2026-05-26.
v1.1.0 amendment 2026-05-28 adds Phase A (code+data cleanup) per team_00
in-session approval; see DECISION_RECORD for the 5 verbatim decisions.*
