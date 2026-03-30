# QA Report — Gate G4 — Re-run after Team 10 fixes

**Date:** 2026-03-31  
**From:** Team 50 (QA)  
**Mandate ID:** `QA-MANDATE-20260330-G4`  
**Source:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md`  
**Prior report:** `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G4_TEAM50.md`  
**Remediation reference:** `_COMMUNICATION/TEAM_50/reports/2026-03-30_G4_RETURN_TO_TEAM10_REMEDIATION_REQUEST_TEAM50.md`  
**Decision:** **FAIL**  
**Gate G4:** **BLOCKED**

---

## Summary

**Improvements verified:** `run_aggregator`, `run_publisher`, and `run_normalizer --metrics` are registered on `python -m organic_market_agent` (`organic_market_agent/__main__.py`). **T02** outcomes hold via CLI (`run_aggregator` + `run_publisher`). **T03**, **T04**, **T06** (unit coverage), **T07** (with mandatory `--dir`), and **T08** pass on this host.

**Still blocking:** **T05** — mandate **second** SQL returns **3** rows (`sample_size` ≠ join count). **T01** / full suite — **`test_qa001_outlier_high_price` remains SKIPPED** (environment has fewer than 11 active sources; Team 10 documents this in their completion report but the mandate still requires all T01 tests to pass without a Team 100 waiver on file). **T09** — no **G4-specific** before/after count package was found under Team 10 reports for this gate (G3 quiet-DB docs exist; they do not substitute for mandate §2 T09 evidence pasted into QA).

---

## Prerequisites (mandate §1)

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | `alembic current` → `014 (head)` | **PASS** | `014 (head)` |
| 2 | `pytest tests/ -q` all pass | **PARTIAL** | **62 passed, 1 skipped** (`test_qa001_outlier_high_price`) |
| 3 | ≥3 community sources, ≥15 products in `normalized_observations` | **PASS** | **6** distinct community sources, **24** distinct community products |
| 4 | `output/public/public_report.json` exists | **PASS** | Present after `run_publisher` (also existed before this run) |

**Environment:** macOS, `.venv/bin/python` (Python **3.9.6** in venv), `DATABASE_URL` from repo `.env` (value not logged).

---

## T01 — Unit tests

**Command:**

```bash
.venv/bin/python -m pytest tests/test_aggregator.py tests/test_publisher_local.py -v
```

**Result:** **14 passed, 1 skipped** — `tests/test_aggregator.py::test_qa001_outlier_high_price` **SKIPPED** (insufficient active sources for QA001 scenario).

**Gate criterion:** Mandate §3 requires all T01 tests to pass → **FAIL** (strict), unless Team 100 issues a written waiver referenced in QA.

---

## T02 — End-to-end CLI

**Commands executed:**

```bash
.venv/bin/python -m organic_market_agent run_aggregator
.venv/bin/python -m organic_market_agent run_publisher
.venv/bin/python -m organic_market_agent run_normalizer --metrics
```

**Aggregator (local date 2026-03-31):** `daily_groups=0 created=0 updated=0` (no observations keyed to that calendar day in UTC filter). **Publisher:** artifacts written to `output/public`.

**Post-checks:**

| Check | Result |
|--------|--------|
| `SELECT COUNT(*) FROM daily_aggregates` | **25** (> 0) |
| `SELECT COUNT(*) FROM weekly_snapshots` | **25** (> 0) |
| `output/public/public_report.json` | exists, valid JSON (**19** products) |
| `output/public/manifest.json` | exists |
| `output/public/public_report.html` | exists |

**Note:** Full `run_ingestion --normalize` was **not** re-executed in this cycle (would mutate operational data); CLI parity and publish path were validated directly.

**Result:** **PASS** on outcomes + **PASS** on mandated CLI surface (remediation D3 addressed).

---

## T03 — Publish threshold

- Latest community day in DB: products with `meets_publish_threshold = false` include **PRD003, PRD015, PRD016, PRD025, PRD027** (none appear in `public_report.json`).
- JSON contains **19** products, all with `meets_publish_threshold: true`.

**Result:** **PASS**

---

## T04 — JSON schema

Mandate Python assertion block executed — **no AssertionError**.

**Result:** **PASS**

---

## T05 — Aggregation consistency

**Query 1 (min ≤ median ≤ max):** `violations: 0` → **PASS**

**Query 2 (sample_size vs mandate join):**

```text
T05 q2 mismatch rows: 3
  (daily_aggregate id, sample_size, actual_count) = (134, 1, 5)
  (78, 27, 33)
  (135, 4, 5)
```

**Analysis:** `AggregatorEngine` aggregates on **`(no.observed_at AT TIME ZONE 'UTC')::date = aggregate_date`** (`organic_market_agent/aggregator/engine.py`). The mandate SQL counts observations whose **`source_fetch_run` started on `aggregate_date`**. When fetch calendar day and observation calendar day diverge, counts differ — **remediation D1 not resolved** for mandate-as-written.

**Result:** **FAIL**

---

## T06 — Staleness

Covered by `tests/test_publisher_local.py` (`test_manifest_staleness_*`); all **passed** in T01 publisher subset.

**Result:** **PASS**

---

## T07 — Local viewer

`run_viewer --port 18082 --dir output/public`; `GET /manifest.json` and `GET /public_report.json` returned **200** and valid JSON (verified via `urllib`).

**Result:** **PASS**

---

## T08 — Admin dashboard

`run_admin --port 18083`; routes `/`, `/sources`, `/sources/SRC002`, `/products`, `/unresolved` → **HTTP 200** (shallow check via `urllib`). Manual table content not re-audited in this pass.

**Result:** **PASS**

---

## T09 — Regression (M1–M3 tables)

Mandate requires **recorded baseline before** M4 pipeline action and **comparison after**. No dated **G4** before/after capture was supplied in `_COMMUNICATION/TEAM_10/reports/` for Team 50 to paste.

**Result:** **FAIL** (evidence gap; same class of finding as 2026-03-30 run)

---

## Full suite

```bash
.venv/bin/python -m pytest tests/ -q
```

**62 passed, 1 skipped** — satisfies “48+ tests” count but **not** zero-skip policy unless waived.

---

## Gate checklist (mandate §3)

| Item | Status |
|------|--------|
| T01 all PASS (≥14) | **FAIL** (1 skipped) |
| T02 pipeline + populated aggregates | **PASS** (CLI + DB counts) |
| T03 threshold + JSON | **PASS** |
| T04 schema | **PASS** |
| T05 consistency | **FAIL** |
| T06 staleness | **PASS** |
| T07 viewer | **PASS** |
| T08 admin 200 | **PASS** |
| T09 regression evidence | **FAIL** |
| 48+ tests, no regression | **PARTIAL** (skip remains) |

---

## Required actions (Team 10 / Team 100)

1. **T05:** Either change aggregation counting to match the mandate join (**`source_fetch_runs.started_at::date = aggregate_date`**, with the same product / observation filters as production intent), **or** obtain a **Team 100** update to `QA_MANDATE_G4.md` T05 SQL to match the **`observed_at`-date** definition and re-issue the mandate.
2. **T01:** Run QA001 in CI with ≥11 active sources, **or** file **Team 100** waiver + mandate amendment for conditional skip.
3. **T09:** File a **quiet-DB** before/after snapshot for the five tables in mandate §2 T09, referenced from a dated Team 10 completion addendum.

---

## Sign-off

**Gate G4:** **BLOCKED** — re-submit after the above; Team 50 will re-run `QA_MANDATE_G4.md`.

— Team 50 (QA)
