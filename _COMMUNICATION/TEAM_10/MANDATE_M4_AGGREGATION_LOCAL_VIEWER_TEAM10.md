---
document_type: MANDATE
version: "1.0"
template: _COMMUNICATION/TEMPLATES/MANDATE.md
---

# Mandate — Team 10: M4 Aggregation + Local Viewer + Admin Monitoring Dashboard
**Mandate ID:** MANDATE-20260330-M4-AGG-VIEWER-T10
**From:** Team 100 (Architecture)
**To:** Team 10 (Feature Development)
**Date:** 2026-03-30
**Priority:** HIGH
**Gate dependency:** Blocks Gate G4
**Status:** ACTIVE

---

## 1. Context

M3 and all M3→M4 boundary work are complete:
- Gate G3: PASS
- Migration 013 applied: `source_tier` on `sources`, `is_quarantined` on `raw_extracted_items`
- `NormalizerEngine` skips quarantined rows
- `run_normalizer --metrics` implemented and working
- Pipeline delivers 22 distinct products from 3 reliable sources per run

M4 Phase A requires Team 10 to build three engines and one management interface:

1. **`AggregatorEngine`** — rolls `normalized_observations` into `daily_aggregates`
   and `weekly_snapshots`
2. **`QAEngine`** — detects outliers, missing-source alerts, duplicate observations
3. **`PublishEngine`** (local only) — generates `public_report.json`,
   `public_report.html`, and `manifest.json`; serves them via a local HTTP server
4. **Admin Monitoring Dashboard** — a read-only Flask web interface showing the
   operational state of the data pipeline (source health, product coverage, alias
   gaps). This is a **new M4 deliverable** added by Team 100 to make the pipeline
   observable before M5's full admin UI is built.

**Dependency:** Team 20 must apply migration 014 (daily_aggregates + weekly_snapshots
tables) before `AggregatorEngine` tests can run against a live DB. Implement and
mock-test locally first; request migration 014 from Team 20 in parallel.

**Triggered by:** M4 milestone activation per `_COMMUNICATION/ROADMAP.md`

**Related documents:**
- `_COMMUNICATION/ROADMAP.md` — M4 specification (reference)
- `_COMMUNICATION/TEAM_20/MANDATE_M4_SCHEMA_TEAM20.md` — upstream DB schema dependency
- `organic_market_agent/models/aggregates.py` — `DailyAggregate`, `WeeklySnapshot` models
- `organic_market_agent/models/publishing.py` — `PublishedReport` model (if present)
- `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md` — forward metrics thresholds

---

## 2. Requirements

### Task 1 — AggregatorEngine

**File:** `organic_market_agent/aggregator/engine.py`

The `AggregatorEngine` reads `normalized_observations` for a date range and
computes per-product, per-market-scope aggregates.

**Key logic:**

```python
class AggregatorEngine:
    def run(self, session: Session, aggregate_date: date) -> dict[str, int]:
        """Compute daily_aggregates for aggregate_date.
        Returns {"created": N, "updated": N}.
        """
        # 1. GROUP normalized_observations by (product_id, market_scope, sales_channel)
        #    WHERE observed_at::date = aggregate_date
        # 2. For each group compute:
        #    - sample_size = COUNT(*)
        #    - distinct_sources = COUNT(DISTINCT source_id)
        #    - min_price, max_price, avg_price, median_price, stddev_price
        # 3. meets_publish_threshold = (sample_size >= 2 AND distinct_sources >= 2)
        # 4. UPSERT into daily_aggregates (ON CONFLICT DO UPDATE)
        # 5. Roll up to weekly_snapshots for the week containing aggregate_date
```

**Publish threshold (binding rule):**
`meets_publish_threshold = true` if and only if:
- `sample_size >= 2` (at least 2 individual price observations)
- `distinct_sources >= 2` (from at least 2 different sources)

Both conditions must hold. Products with only 1 source (even with many observations)
must be marked `false`.

**Weekly rollup:** After computing `daily_aggregates`, aggregate all days in the
containing ISO week into `weekly_snapshots`. Use `UPSERT` (ON CONFLICT DO UPDATE).

**Acceptance criterion:** After running `AggregatorEngine().run(session, date.today())`,
`SELECT COUNT(*) FROM daily_aggregates WHERE meets_publish_threshold = true` returns
a positive number when the pipeline has data from ≥2 sources for any product.

---

### Task 2 — QAEngine

**File:** `organic_market_agent/aggregator/qa_engine.py`

The `QAEngine` reads `normalized_observations` and flags quality issues.

**Rules to implement:**

| Rule ID | Trigger | Action |
|---------|---------|--------|
| QA001 | Price is > 3σ above the product's daily mean | Log warning with source, product, price |
| QA002 | A source that was active last run is missing from current run | Log warning with source code |
| QA003 | Duplicate `(source_id, product_id, observed_at::date)` pairs | Log warning with count |

QA output is **log-only** in M4. No separate DB table is required (that is M5 scope).

```python
class QAEngine:
    def run(self, session: Session, run_id: int) -> list[str]:
        """Return list of QA warning strings for the given ingestion run."""
```

**Acceptance criterion:** `QAEngine().run(session, last_run_id)` returns a list
(possibly empty) without raising. For a run with known outlier data, at least
one QA001 warning is generated.

---

### Task 3 — PublishEngine (local only)

**File:** `organic_market_agent/publisher/engine.py`

Generates three output files in a configurable local directory
(default: `output/public/`):

**`public_report.json`** — schema:
```json
{
  "generated_at": "<ISO-8601 timestamp>",
  "report_date": "<YYYY-MM-DD>",
  "products": [
    {
      "product_id": "<code e.g. PRD001>",
      "canonical_name_he": "עגבנייה",
      "market_scope": "community",
      "meets_publish_threshold": true,
      "sample_size": 4,
      "distinct_sources": 3,
      "min_price": 14.0,
      "max_price": 22.0,
      "avg_price": 17.5,
      "median_price": 17.0,
      "normalized_unit": "ק\"ג",
      "last_observed_at": "<ISO-8601>"
    }
  ]
}
```

Products with `meets_publish_threshold = false` **must not appear** in this list.
The publish run must abort (raise `PublishAbortError`) if fewer than 2 community
sources contributed data in the latest ingestion run.

**`public_report.html`** — Jinja2 template rendering the same data as a simple
Hebrew-friendly HTML table (RTL layout, Bootstrap 5 CDN). Must include:
- Report date and generation timestamp
- Per-product row: name, avg price, unit, range, sample size, sources count
- Staleness banner if `last_observed_at` > 3 days ago

**`manifest.json`** — schema:
```json
{
  "last_published_at": "<ISO-8601>",
  "report_date": "<YYYY-MM-DD>",
  "product_count": 10,
  "staleness_level": "current | warning | irrelevant",
  "community_sources": 3
}
```

Staleness rules (from `docs/M3_DATA_QUALITY_AND_COHORT_GATE_SPEC.md`):
- `current`: last_published_at ≤ 3 days ago
- `warning`: 4–7 days ago
- `irrelevant`: > 7 days ago (was specified as 8 in older docs — use 8)

**Acceptance criterion:** `PublishEngine().run(session, output_dir)` creates all
three files in `output_dir`. `public_report.json` passes JSON schema validation.
Products below threshold are absent from the JSON.

---

### Task 4 — Local Viewer (HTTP server)

**File:** `organic_market_agent/publisher/viewer.py`

Serve the `output/public/` directory on `localhost:8080` using Python's built-in
`http.server`. Add a CLI command:

```bash
python -m organic_market_agent run_viewer [--port 8080] [--dir output/public/]
```

This command blocks and serves files statically. No Flask required for the viewer —
`http.server` is sufficient.

**Acceptance criterion:** After `run_viewer`, `curl http://localhost:8080/manifest.json`
returns valid JSON with the expected fields.

---

### Task 5 — Admin Monitoring Dashboard (new M4 deliverable)

**Purpose:** A read-only Flask web interface giving the operator a real-time view
of pipeline health. This enables the operator to identify missing aliases, broken
sources, and coverage gaps without running SQL queries manually.

**Package:** `organic_market_agent/admin/`

**Dependency:** Add `flask` to `pyproject.toml` (or `requirements.txt`).

**Package structure:**
```
organic_market_agent/admin/
    __init__.py         — create_app() Flask application factory
    routes/
        __init__.py
        dashboard.py    — GET /
        sources.py      — GET /sources, GET /sources/<code>
        products.py     — GET /products
        unresolved.py   — GET /unresolved
    templates/admin/
        base.html       — Bootstrap 5 CDN layout, Hebrew RTL meta, navbar
        dashboard.html  — KPI summary cards
        sources.html    — source status table
        source_detail.html — per-source unresolved items
        products.html   — product coverage table
        unresolved.html — alias gap view
```

**CLI entry point** — add to `organic_market_agent/__main__.py`:
```python
@cli.command()
@click.option("--port", default=8080, show_default=True)
@click.option("--host", default="127.0.0.1", show_default=True)
def run_admin(port: int, host: str) -> None:
    """Start the admin monitoring dashboard."""
    from organic_market_agent.admin import create_app
    create_app().run(host=host, port=port, debug=False)
```

**Routes and their SQL queries:**

| Route | Page | Key data |
|-------|------|----------|
| `GET /` | Dashboard | Active sources count, products covered (of 29), total observations, last run timestamp, overall resolution % |
| `GET /sources` | Source list | Per-source: code, name, tier, is_active, last_run_date, items_extracted, resolved, unresolved, resolution_% |
| `GET /sources/<code>` | Source detail | Top 50 unresolved items for this source grouped by `raw_product_name` with occurrence count — sorted by count DESC |
| `GET /products` | Product coverage | Per product (canonical_name_he, code), # distinct sources with observations, total observations, avg_price, last_observed_at |
| `GET /unresolved` | Alias gap view | All unresolved `raw_product_name` strings grouped by name, with total occurrence count and distinct source count. Sorted by count DESC. This is the primary tool for identifying missing aliases. |

**Template requirements:**
- RTL layout (`<html dir="rtl" lang="he">`)
- Bootstrap 5 loaded from CDN (no build tools)
- Navbar with links to all 4 pages
- Tables are sortable by column header (Bootstrap table styling sufficient — no JS sorting required in M4)
- Source status table: color-code rows — `is_active=false` rows in muted grey

**Data freshness note:** All queries read directly from the DB at request time.
No caching required in M4.

**Acceptance criterion:** `python -m organic_market_agent run_admin` starts without
error. All 5 routes (`/`, `/sources`, `/sources/SRC002`, `/products`, `/unresolved`)
return HTTP 200 and render valid HTML with the correct data.

---

### Task 6 — Unit Tests

**`tests/test_aggregator.py`** — minimum 8 tests:
- Publish threshold: 2 obs from 2 distinct sources → `meets_publish_threshold=true`
- Publish threshold: 2 obs from 1 source → `meets_publish_threshold=false`
- Publish threshold: 1 obs from 2 sources → `meets_publish_threshold=false`
- Outlier detection: price > 3σ → QA001 warning generated
- Weekly snapshot built correctly from 7 daily aggregates
- AggregatorEngine with empty observations → 0 rows created, no error
- UPSERT: running aggregator twice on same date updates, not duplicates
- `stddev_price` is NULL when `sample_size = 1`

**`tests/test_publisher_local.py`** — minimum 6 tests:
- `public_report.json` contains only products with `meets_publish_threshold=true`
- `public_report.json` JSON schema validates (all required fields present, correct types)
- `manifest.json` staleness: `last_published_at = today` → `current`
- `manifest.json` staleness: `last_published_at = today - 4d` → `warning`
- `manifest.json` staleness: `last_published_at = today - 9d` → `irrelevant`
- `PublishEngine.run()` raises `PublishAbortError` when community sources < 2

---

## 3. Out of Scope

- FTPS upload — deferred to M6
- Admin authentication / login — deferred to M5
- Alias CRUD in the admin UI — deferred to M5 (M4 dashboard is read-only)
- `qa_flags` DB table — deferred to M5
- CSS custom styling beyond Bootstrap 5 defaults — not required in M4
- Admin dashboard pagination — not required in M4 (LIMIT 200 rows is acceptable)

---

## 4. Verification Checklist

```bash
.venv/bin/python -m pytest tests/test_aggregator.py tests/test_publisher_local.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m organic_market_agent run_admin --port 8081 &
curl -s http://localhost:8081/ | grep -c "<html"   # must return 1
```

- [ ] `pytest tests/test_aggregator.py` — ≥8 tests, all PASS
- [ ] `pytest tests/test_publisher_local.py` — ≥6 tests, all PASS
- [ ] All existing tests still pass (48+ tests)
- [ ] `public_report.json` present and valid after `PublishEngine.run()`
- [ ] `manifest.json` staleness levels correct
- [ ] `localhost:<port>/` returns HTTP 200 with valid HTML
- [ ] `/sources/SRC002` shows unresolved items with counts
- [ ] `/unresolved` shows top unresolved product names

---

## 5. Completion Report

File at: `_COMMUNICATION/TEAM_10/reports/2026-03-30_M4_IMPLEMENTATION_COMPLETE_TEAM10.md`

Include Mandate ID `MANDATE-20260330-M4-AGG-VIEWER-T10`, test results, sample output
files (truncated), and any deviations from this mandate.

Upon completion, file a **QA Review Request** using the canonical template:
`_COMMUNICATION/TEAM_50/reports/<DATE>_G4_REVIEW_REQUEST_TEAM50.md`

---

## 6. Escalation

If migration 014 is not yet applied when you begin Task 1, use mock DB sessions for
unit tests and defer DB integration tests. Flag the blocker in
`_COMMUNICATION/TEAM_10/reports/BLOCKED_M4_SCHEMA_TEAM10.md`.

---

*Issued by: Team 100 (Architecture)*
*Date: 2026-03-30*
*Authorized by: Team 100 (Architecture)*
