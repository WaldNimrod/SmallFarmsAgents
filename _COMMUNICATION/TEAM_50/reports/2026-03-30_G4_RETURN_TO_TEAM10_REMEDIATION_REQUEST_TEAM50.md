# Team 50 → Team 10 — Gate G4 remediation request

**Date:** 2026-03-30  
**From:** Team 50 (QA)  
**To:** Team 10 (Feature Dev)  
**Subject:** **FAIL** on `QA-MANDATE-20260330-G4` — fixes required and **re-submission for re-test**

**Canonical QA report:** [_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G4_TEAM50.md](./2026-03-30_QA_G4_TEAM50.md)  
**Mandate:** [_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md](../QA_MANDATE_G4.md)

---

## 1. Outcome

**Gate G4:** **BLOCKED** until the items below are resolved and Team 50 re-runs the mandate.

Team 50 does **not** implement production fixes; this document lists **blocking defects** with evidence and the **expected re-verification** path.

---

## 2. Blocking defects (must fix)

### D1 — T05: `sample_size` vs mandate SQL join count (Critical)

**Symptom:** Second query under **T05** in `QA_MANDATE_G4.md` returns **1 row** (must be **0**).

**Evidence (Team 50 host):**

```text
mismatch rows: 1
(daily_aggregate id, sample_size, actual_count) = (78, 19, 24)
```

**SQL shape (from mandate):** join `daily_aggregates` to `normalized_observations` on `product_id` and `source_fetch_run_id IN (SELECT id FROM source_fetch_runs WHERE started_at::date = da.aggregate_date)`.

**Required:** Align **`DailyAggregate.sample_size`** definition with the mandate’s counting rule **or** amend the mandate with Team 100 if the stored `sample_size` is intentionally defined differently (then provide a **mandate-approved** validation query). Until then, **T05 FAIL** blocks the gate.

**Owner:** Team 10 (implementation) + Team 100 if spec change.

---

### D2 — T01 / full suite: skipped test (Critical per mandate wording)

**Symptom:** `pytest tests/test_aggregator.py tests/test_publisher_local.py` → **1 skipped** (`test_qa001_outlier_high_price`). Full suite: **62 passed, 1 skipped**.

**Mandate §3:** T01 requires all tests to pass; checklist also requires **48+ tests** with no regression — **skips** are not accepted under Team 50 onboarding unless **documented** with Team 100 approval.

**Required:** Implement the test, remove skip, or obtain **written Team 100 waiver** referenced in the completion report.

**Owner:** Team 10 (+ Team 100 if waiver).

---

### D3 — T02: CLI parity with `QA_MANDATE_G4.md` (Critical for auditable E2E)

**Symptom:** `python -m organic_market_agent` exposes **`run_ingestion`**, **`run_normalizer`**, **`run_viewer`**, **`run_admin`** only. The mandate lists **`run_aggregator`**, **`run_publisher`**, and **`run_normalizer --metrics`** — **not present**.

**Required (pick one, document in completion report):**

1. **Add** Click commands `run_aggregator` and `run_publisher` (and `--metrics` on normalizer if still required) that call the same code paths as production; **or**  
2. **Coordinate with Team 100** to update **`QA_MANDATE_G4.md`** to the **actual** supported commands and re-issue; Team 50 will then score against the updated text.

**Owner:** Team 10 + Team 100 (mandate text if option 2).

---

### D4 — T09: regression evidence package (Critical)

**Symptom:** Mandate requires **pre-M4** row counts for `sources`, `products`, `product_aliases` (active), `normalized_observations`, `raw_extracted_items` **before** the M4 pipeline action, then **after** — with **no unexplained drift** on M1–M3 tables (rules per mandate §2 T09).

**Required:** File a **dated snapshot** (SQL output or script) in `_COMMUNICATION/TEAM_10/reports/` taken on a **quiet DB** (no parallel ingestion), plus **post-run** snapshot. Team 50 will paste both into the next QA report.

**Owner:** Team 10 (evidence) + operator discipline; Team 50 re-executes comparison.

---

### D5 — Prerequisite §1 item 4 — `output/public/` before QA (High)

**Symptom:** `output/public/public_report.json` did **not** exist until Team 50 ran publish during QA.

**Required:** Team 10 completion handoff should include **evidence** that a standard pipeline run produces `output/public/*` **or** document that QA must generate it (then Team 100 updates prerequisite §1). Avoid ambiguity for the next cycle.

**Owner:** Team 10 (+ Team 100 if prerequisite change).

---

### D6 — T07 mandate example: `run_viewer` requires `--dir` (High / doc)

**Symptom:** Mandate shows `run_viewer --port 8082` without `--dir`; actual CLI **requires** `--dir <publish_output>`.

**Required:** Fix mandate text or CLI defaults; Team 50 used `--dir output/public` successfully.

**Owner:** Team 10 / Team 100 (docs).

---

## 3. Items that passed (no remediation)

For context, the following **passed** on the reported run: **T03**, **T04**, **T06**, **T07** (with `--dir`), **T08** (HTTP 200 on all five routes; shallow content review only). **Prerequisites** 1 and 3 passed (**014**, community/product counts in `normalized_observations`).

---

## 4. Re-submission checklist (Team 10)

When ready, file **all** of the following:

1. **Completion report** update or new dated report under `_COMMUNICATION/TEAM_10/reports/` referencing this remediation ID.  
2. **Verbatim** outputs: `pytest tests/test_aggregator.py tests/test_publisher_local.py -v` (**0 skipped** unless waived), `pytest tests/ -q`.  
3. **T05:** paste result of **both** mandate SQL queries (**0 rows** on the second).  
4. **T02:** paste CLI transcript using **documented** commands (post-CLI fix or post-mandate update).  
5. **T09:** paste **before/after** SQL snapshots per §2 D4.  
6. **Optional:** request line in `_COMMUNICATION/TEAM_50/reports/` (e.g. `YYYY-MM-DD_G4_REVIEW_REQUEST_RERUN_TEAM50.md`) pointing to the new Team 10 report.

---

## 5. Team 50 re-test

Upon receipt, Team 50 will re-execute **`QA_MANDATE_G4.md`** end-to-end and file a new **`_COMMUNICATION/TEAM_50/reports/<DATE>_QA_G4_TEAM50.md`** with **PASS / FAIL** and updated evidence.

---

## 6. References

| Document | Path |
|----------|------|
| QA report (this gate) | `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G4_TEAM50.md` |
| G4 mandate | `_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md` |
| CLI entry | `organic_market_agent/__main__.py` |

---

**[USER ACTION REQUIRED]:** None — routing to Team 10 for implementation and evidence.
