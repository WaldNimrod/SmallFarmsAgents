---
document_type: MANDATE
version: "1.0"
template: _COMMUNICATION/TEMPLATES/MANDATE.md
---

# Mandate — Team 10: Normalizer Quarantine Filter + CLI Metrics Flag
**Mandate ID:** MANDATE-20260330-NORM-FILTER-METRICS
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Development)
**Date:** 2026-03-30
**Priority:** HIGH
**Blocks:** M4 entry (Gate G4 QA cannot begin until this mandate is complete)

---

## Context

Architecture decision `ARCH-20260330-G3-DATA-QUALITY` and the specification
`docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` require:

1. The normalizer engine must skip rows flagged as `is_quarantined = true`
2. The `run_normalizer` CLI (and `run_ingestion --normalize`) must support a `--metrics` flag
   that prints the forward-metrics summary defined in the spec

**Dependency:** This mandate depends on Team 20's migration 009 (`source_tier` + `is_quarantined`
columns) being applied. If those columns do not yet exist, implement the code and add a graceful
fallback for the test environment (see notes in each task).

---

## Task 1 — Normalizer Engine: Skip Quarantined Rows

### File to modify
`organic_market_agent/normalizer/engine.py`

### Change

In `NormalizerEngine.run()`, add `is_quarantined = false` to the item query.

**Current query (lines 53–58):**
```python
stmt = (
    sa.select(RawExtractedItem)
    .join(SourceFetchRun, RawExtractedItem.source_fetch_run_id == SourceFetchRun.id)
    .where(RawExtractedItem.extraction_status == "extracted")
    .order_by(RawExtractedItem.id)
)
```

**Required change — add one `.where()` clause:**
```python
stmt = (
    sa.select(RawExtractedItem)
    .join(SourceFetchRun, RawExtractedItem.source_fetch_run_id == SourceFetchRun.id)
    .where(RawExtractedItem.extraction_status == "extracted")
    .where(RawExtractedItem.is_quarantined.is_(False))
    .order_by(RawExtractedItem.id)
)
```

This requires `is_quarantined` to exist on the `RawExtractedItem` model.

### Model update
Add `is_quarantined` to the `RawExtractedItem` SQLAlchemy model (if not already present):
```python
is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

> **Pre-009 fallback:** If migration 009 has not been applied yet (column does not exist),
> the model will raise on startup. Only apply this change after confirming the column exists,
> OR implement a try/except in the model that makes it optional — discuss with Team 100 if needed.
> Recommended: apply this mandate after Team 20 completes migration 009.

---

## Task 2 — `--metrics` Flag on `run_normalizer`

### File to modify
`organic_market_agent/normalizer/run_normalizer.py`

### Change

Add a `--metrics` flag that, when set, queries and prints the forward-metrics summary
after the normalizer run.

**Required output format:**
```
=== Cycle Metrics (run_id=<N>) ===
resolved           : 23
unresolvable       : 4
unresolvable_rate  : 14.8% (price_grid, non-quarantined)
distinct_products  : 8
community_sources  : 3 / 3 succeeded
thresholds         : resolved ✅  distinct_products ✅  unresolvable_rate ✅  community_sources ✅
```

**Pass/fail thresholds (from spec):**
| Metric | Threshold |
|--------|-----------|
| `resolved` | ≥ 10 |
| `distinct_products` | ≥ 3 |
| `unresolvable_rate` | ≤ 30% |
| `community_sources` | ≥ 2 |

**Implementation guidance:**

Add a helper function `print_cycle_metrics(session, ingestion_run_id)` that runs the
SQL template from `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` (section "SQL Template
for Forward Metrics").

The function should use `source_tier = 'price_grid'` for the unresolvable_rate filter
**if the column exists**, and fall back to `source_group = 'community'` if it does not
(pre-migration 009 environment).

Example skeleton:
```python
def _print_cycle_metrics(session: Session, ingestion_run_id: int | None) -> None:
    """Print forward-metrics summary for the given run_id (or all runs if None)."""
    from sqlalchemy import text

    run_filter = "sfr.ingestion_run_id = :run_id" if ingestion_run_id else "1=1"
    params: dict = {}
    if ingestion_run_id:
        params["run_id"] = ingestion_run_id

    # Check if source_tier column exists (post-009)
    has_tier = session.execute(text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_name='sources' AND column_name='source_tier'"
    )).scalar() > 0

    tier_filter = "s.source_tier = 'price_grid'" if has_tier else "s.source_group = 'community'"
    quarantine_filter = "AND r.is_quarantined = false" if has_tier else ""

    sql = text(f"""
        SELECT
            COUNT(*) FILTER (WHERE r.extraction_status = 'normalized') AS resolved,
            COUNT(*) FILTER (WHERE r.extraction_status = 'unresolvable') AS unresolvable,
            COUNT(*) AS total,
            COUNT(DISTINCT no_obs.product_id) AS distinct_products,
            COUNT(DISTINCT sfr.source_id) FILTER (
                WHERE r.extraction_status = 'normalized' AND s.market_scope = 'community'
            ) AS community_sources_succeeded,
            COUNT(DISTINCT sfr.source_id) FILTER (
                WHERE s.market_scope = 'community'
            ) AS community_sources_total
        FROM raw_extracted_items r
        JOIN source_fetch_runs sfr ON r.source_fetch_run_id = sfr.id
        JOIN sources s ON sfr.source_id = s.id
        LEFT JOIN normalized_observations no_obs ON no_obs.source_fetch_run_id = sfr.id
        WHERE {run_filter}
          AND {tier_filter}
          {quarantine_filter}
    """)

    row = session.execute(sql, params).mappings().one()
    resolved = row["resolved"] or 0
    unresolvable = row["unresolvable"] or 0
    total = row["total"] or 0
    distinct = row["distinct_products"] or 0
    comm_ok = row["community_sources_succeeded"] or 0
    comm_total = row["community_sources_total"] or 0

    rate = round(100 * unresolvable / total, 1) if total > 0 else 0.0

    def ok(cond: bool) -> str:
        return "✅" if cond else "❌"

    run_label = f"run_id={ingestion_run_id}" if ingestion_run_id else "all runs"
    print(f"\n=== Cycle Metrics ({run_label}) ===")
    print(f"resolved           : {resolved}")
    print(f"unresolvable       : {unresolvable}")
    print(f"unresolvable_rate  : {rate}% ({'price_grid, non-quarantined' if has_tier else 'community proxy'})")
    print(f"distinct_products  : {distinct}")
    print(f"community_sources  : {comm_ok} / {comm_total} succeeded")
    print(
        f"thresholds         : "
        f"resolved {ok(resolved >= 10)}  "
        f"distinct_products {ok(distinct >= 3)}  "
        f"unresolvable_rate {ok(rate <= 30.0)}  "
        f"community_sources {ok(comm_ok >= 2)}"
    )
```

Wire this into the Click command:
```python
@click.command()
@click.option("--source-id", default=None, type=int)
@click.option("--ingestion-run-id", default=None, type=int)
@click.option("--metrics", is_flag=True, default=False, help="Print forward-metrics summary after run")
def main(source_id, ingestion_run_id, metrics):
    """Normalize pending raw_extracted_items."""
    config.ensure_dirs()
    with SessionFactory() as session:
        engine = NormalizerEngine()
        counts = engine.run(session, ingestion_run_id=ingestion_run_id, source_id=source_id)
        click.echo(
            f"NormalizerEngine complete: resolved={counts['resolved']} "
            f"unresolvable={counts['unresolvable']} skipped={counts['skipped']}"
        )
        if metrics:
            _print_cycle_metrics(session, ingestion_run_id)
```

---

## Task 3 — Parsers Engine: Source Tier Warning Log

### File to modify
`organic_market_agent/parsers/engine.py`

### Change

After retrieving the source for a fetch job, log a warning if the source is `discovery` or `basket` tier.
This does NOT skip ingestion (parsers still run for discovery sources — data is collected but quarantined at migration time).
It is an informational signal for the operator.

**Implementation:**

Inside the parser engine's main run loop, after loading the source object, add:

```python
# Warn if source tier is not price_grid (requires migration 009)
try:
    if hasattr(source, "source_tier") and source.source_tier in ("discovery", "basket"):
        logger.warning(
            "Source %s has tier='%s' — extracted items will be quarantined and skipped by normalizer",
            source.code,
            source.source_tier,
        )
except Exception:
    pass  # source_tier not yet available (pre-migration 009)
```

> This uses `try/except` so the parser engine continues to work in pre-009 environments.

---

## Task 4 — Unit Tests

Add or update tests in `tests/test_normalizer.py`:

1. **`test_normalizer_skips_quarantined_items`** (unit test, no DB):
   Verify that if a `RawExtractedItem` has `is_quarantined = True`, it is not in the query
   result. This can be a mock/spy test that checks the `.where()` clause is applied.
   If a full DB integration test is preferable, use `db_session` fixture, insert one quarantined
   item, run the engine, and assert the item's `extraction_status` remains `'extracted'`.

2. **`test_print_cycle_metrics_no_crash`** (unit test):
   Mock the session to return a zero-row result and confirm `_print_cycle_metrics` does not
   raise an exception.

---

## Acceptance Criteria

| Criterion | Verification |
|-----------|-------------|
| `NormalizerEngine.run()` skips quarantined items | After migration 009, quarantined items remain `extracted` after normalizer run |
| `run_normalizer --metrics` prints forward-metrics summary | Output includes `resolved`, `distinct_products`, `unresolvable_rate`, `community_sources` |
| `--metrics` output shows threshold pass/fail symbols | ✅/❌ per threshold |
| Parser engine logs warning for discovery/basket sources | Warning present in output for SRC013 etc. |
| All existing tests pass | `pytest tests/ -q` → 0 failures |
| New tests pass | Both new test cases pass |

---

## Completion Report

Use the `COMPLETION_REPORT.md` template from `_COMMUNICATION/TEMPLATES/`.
Submit to: `_COMMUNICATION/TEAM_10/reports/`
Naming: `2026-03-30_NORM_FILTER_METRICS_COMPLETE_TEAM10.md`

Include:
- Code diff summary (files changed, lines added/removed)
- Sample `--metrics` output from a real DB run
- Test results (`pytest tests/ -q`)
- Any deviation from this mandate and rationale

---

## Reference Documents

- `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` — forward metrics definition, SQL template
- `_COMMUNICATION/TEAM_100/reports/2026-03-30_ARCH_DECISION_G3_DATA_QUALITY_TEAM100.md` — gate decision
- `_COMMUNICATION/TEAM_20/MANDATE_MIGRATION_009_SOURCE_TIER_TEAM20.md` — upstream column dependency
- `organic_market_agent/normalizer/engine.py` — file to modify (Task 1)
- `organic_market_agent/normalizer/run_normalizer.py` — file to modify (Task 2)
- `organic_market_agent/parsers/engine.py` — file to modify (Task 3)

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*Use template `_COMMUNICATION/TEMPLATES/COMPLETION_REPORT.md` for your completion report.*
