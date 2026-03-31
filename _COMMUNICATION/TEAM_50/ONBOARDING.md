# ONBOARDING — Team 50 (QA)
## Session Start Instructions

---

## Team Identity

**Name:** Team 50 — Quality Assurance  
**Role:** Validate every deliverable against spec and mandate before any gate opens.
Issue QA reports. Sign off on gates.  
**Does NOT** write production code. **Does** write QA test scripts and SQL validation queries.  
**Reports to:** Nimrod + Team 100.  
**Writes to:** `_COMMUNICATION/TEAM_50/reports/`

---

## First Actions — Every Session

1. Read this file in full
2. Read `_COMMUNICATION/ROADMAP.md` — identify active milestone and pending gates
3. Check for new completion reports from Team 10 and Team 20:
   - `_COMMUNICATION/TEAM_10/reports/`
   - `_COMMUNICATION/TEAM_20/reports/`
4. Check what you have already reviewed: `_COMMUNICATION/TEAM_50/reports/`
5. Read the QA Mandate for the gate under review before running any test
6. **Read the relevant spec documents** for the area under review (see Spec Documents table below)

**Do NOT run tests without first reading the spec that defines the expected behavior.**

---

## Canonical Templates — Mandatory

All reports filed by Team 50 **must** use the canonical templates:

```
_COMMUNICATION/TEMPLATES/
  README.md               ← Read this first for usage rules
  QA_FINDINGS_REPORT.md   ← ALWAYS use for gate results (the only valid gate decision format)
```

| Situation | Template to use | Where to file |
|-----------|----------------|---------------|
| Gate QA complete | `QA_FINDINGS_REPORT.md` | `_COMMUNICATION/TEAM_50/reports/` |
| Gate PASS | `QA_FINDINGS_REPORT.md` — section: ✅ GATE PASS | Team 50 reports |
| Gate CONDITIONAL | `QA_FINDINGS_REPORT.md` — section: 🟡 CONDITIONAL PASS | Team 50 reports |
| Gate FAIL | `QA_FINDINGS_REPORT.md` — section: ❌ GATE FAIL | Team 50 reports |

**A gate decision is ONLY binding when filed using `QA_FINDINGS_REPORT.md`.**
Verbal or informal gate decisions have no authority.

---

## QA Mandate Files (always read before testing)

| Gate | Mandate | Status |
|------|---------|--------|
| G1 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` | ✅ PASS |
| G2 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md` | ✅ PASS |
| G3 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G3_v2.md` (v2) | ✅ PASS |
| G4 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G4.md` | ✅ PASS |
| G5 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G5.md` | ✅ PASS |
| G6 | `_COMMUNICATION/TEAM_50/QA_MANDATE_G6.md` | ✅ PASS |
| G7 | To be issued after Nimrod approval | PENDING |

---

## Testing Philosophy

**Every gate has two layers of testing:**

1. **Unit tests** (written by Team 10/20, verified by Team 50)  
   Team 50 runs `pytest` and confirms all pass. Does not modify test files.

2. **QA tests** (designed and run by Team 50)  
   Integration, data quality, regression, and end-to-end tests that go beyond
   what unit tests can cover. These require a live DB and real data.

**The spec and mandate always win.**  
Code that works but deviates from spec is a FAIL until corrected or a formal
deviation is approved by Team 100.

---

## Test Types — Definitions and Tools

### Unit Tests
- **What:** Test individual functions/classes in isolation (mocked DB and HTTP)
- **Who writes:** Implementing team (Team 10/20)
- **Who verifies:** Team 50 (runs `pytest`, reads output)
- **Tool:** `pytest`
- **Pass criterion:** All tests pass, no skip, no xfail unless documented

### Integration Tests
- **What:** Components working together with a real DB (no mocks)
- **Who writes/runs:** Team 50
- **Tool:** `pytest` with live `DATABASE_URL` pointing to the real local DB
- **Pass criterion:** Data written to DB correctly; component interactions work as specified

### Data Quality Tests
- **What:** SQL queries that verify the content, types, and integrity of DB tables
- **Who writes/runs:** Team 50
- **Tool:** Direct `psql` queries or Python scripts with `psycopg2`
- **Pass criterion:** All SQL assertions return expected values

### Regression Tests
- **What:** Verify that a new milestone has not corrupted or modified data from previous milestones
- **Who writes/runs:** Team 50
- **Tool:** SQL row count snapshots before and after milestone run
- **Pass criterion:** All prior-milestone table row counts are unchanged; checksums match

### End-to-End Tests
- **What:** Full pipeline execution from ingestion to output artifact
- **Who writes/runs:** Team 50
- **Tool:** CLI run + output file inspection + DB verification
- **Pass criterion:** All pipeline stages complete; output matches spec format

### Functional/UI Tests
- **What:** Manual or automated walkthrough of all UI screens
- **Who writes/runs:** Team 50
- **Tool:** Manual (browser) + Flask test client for route-level checks
- **Pass criterion:** All screens render, all CRUD operations succeed, auth works

### Operational Tests
- **What:** Scheduled execution, email alerts, resilience under failure
- **Who writes/runs:** Team 50
- **Tool:** cron verification, mock or real SMTP, simulated failures
- **Pass criterion:** Automated behavior matches spec over observed period

---

## Gate-by-Gate QA Scope

### Gate G1 — Local Foundation (M1)
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md`

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_db_health.py` — all 7 tests PASS |
| 2 | Integration | `alembic downgrade base` + `alembic upgrade head` on clean DB |
| 3 | Schema | All 23 tables exist; all required indexes; all CHECK constraints active |
| 4 | Data Quality | 11 units, 29 products, ≥20 sources, aliases present (SQL queries) |
| 5 | Type Safety | No `FLOAT` columns anywhere; all `*_at` are `TIMESTAMPTZ`; prices `NUMERIC(12,4)` |
| 6 | Environment | Python 3.11+ (`python --version`); PostgreSQL via Docker (`docker ps` shows postgres container running; `DATABASE_URL` points to Docker port) |
| 7 | CLI | `python -m organic_market_agent.db.check` → output shows PASS for all 23 tables |

---

### Gate G2 — Collection Layer (M2)
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G2.md`

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_collectors.py tests/test_parsers.py` — all PASS |
| 2 | Integration | Live collection run (3+ sources); verify `ingestion_runs`, `source_fetch_runs`, `raw_assets` written |
| 3 | Data Quality | `raw_extracted_items` ≥50 rows; `raw_product_name` populated in majority of rows |
| 4 | Dedup | Run ingestion twice; second run: all `source_fetch_runs.status='skipped'`, zero new `raw_assets` |
| 5 | Error Handling | Simulate unreachable source (change `entry_url` to bad URL); verify retry count, `status='failed'`, `log_entries` row |
| 6 | File System | Raw asset files exist at `RAW_FILES_ROOT/{source_code}/{date}/` |
| 7 | Isolation | `normalized_observations` table must be empty (normalizer not yet run) |
| 8 | Regression | M1 tables (`measurement_units`, `products`, `sources`, `product_aliases`) row counts unchanged |

---

### Gate G3 — Normalizer Engine (M3)
*QA Mandate to be issued after G2 opens.*

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_normalizer.py` — all PASS |
| 2 | Integration | Normalizer run on M2 data; `normalized_observations` populated |
| 3 | Data Quality | All `confidence_score` in [0.0, 1.0]; all `flag_status` values valid; no FLOAT |
| 4 | DB-Driven | Insert new alias in DB, re-run normalizer for that source, verify `product_id` resolved correctly |
| 5 | Basket Policy | All basket products: `is_basket_product=true`, `normalized_price_value IS NULL` |
| 6 | Confidence | Items with missing unit: `confidence_score < 1.0`; direct match: `confidence_score = 1.0` |
| 7 | Regression | M2 tables (`raw_assets`, `raw_extracted_items`) row counts unchanged |

---

### Gate G4 — Aggregation + Local Viewer (M4)
*QA Mandate to be issued after G3 opens.*

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_aggregator.py tests/test_publisher_local.py` — all PASS |
| 2 | End-to-End | Full pipeline: ingest → normalize → aggregate → publish to local dir |
| 3 | Data Quality | `min_price ≤ median_price ≤ max_price` for all `daily_aggregates` rows |
| 4 | Threshold | Products with <2 obs or <2 sources: `meets_publish_threshold=false` and absent from `public_report.json` |
| 5 | JSON Schema | `public_report.json` has all required fields; all price values are numbers (not strings) |
| 6 | Staleness | Set `last_published_at = now() - 4 days`; verify `manifest.json staleness_level = 'warning'` |
| 7 | Staleness | Set `last_published_at = now() - 9 days`; verify `manifest.json staleness_level = 'irrelevant'` |
| 8 | Local Viewer | `localhost:8080` loads without error; at least 5 products displayed with prices |
| 9 | Regression | M2 + M3 tables row counts unchanged |

---

### Gate G5 — Admin UI (M5)
*QA Mandate to be issued after G4 opens.*

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_admin_routes.py` — all PASS |
| 2 | Functional/UI | All 7 screens load; each displays correct data from DB |
| 3 | CRUD | Create alias → verify in DB; edit alias → verify change; delete → verify removed |
| 4 | DB-Driven | Change alias in UI → run pipeline → verify normalization changed |
| 5 | Auth | Unauthenticated request → HTTP 302 redirect to login; wrong password → login page re-shown |
| 6 | Audit | Every admin write operation → `audit_log` row with correct `actor_name`, `action`, `entity_type` |
| 7 | Run Trigger | Click manual run in UI → verify `ingestion_runs` row created; status shown in UI |
| 8 | Team 100 | Architectural review completed and documented in `_COMMUNICATION/TEAM_100/reports/` |

---

### Gate G6 — Automation + Resilience (M6)
*QA Mandate to be issued after G5 opens.*

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/test_alerting.py tests/test_scheduler.py` — all PASS |
| 2 | Operational | `crontab -l` shows correct job; verify it runs at 06:00 |
| 3 | Resilience | Kill 1 source mid-run; verify partial run completes, other sources unaffected |
| 4 | Alert — Failure | Trigger ingestion failure; verify email received with correct subject + body |
| 5 | Alert — Staleness | Set `last_published_at = -4d`; verify warning email sent |
| 6 | Alert — Irrelevant | Set `last_published_at = -9d`; verify irrelevant email sent |
| 7 | Retry | Source returns HTTP 503 twice, then 200; verify `retry_count=2`, `status=success` |
| 8 | 7-Day Stability | Observe or review logs for 7 consecutive automatic runs without intervention |
| 9 | Log Cleanup | Insert synthetic `log_entries` with `created_at = now() - 91d`; run cleanup; verify removed |

---

### Gate G7 — Go-Live (M7)
*QA Mandate to be issued after G6 opens + Nimrod approval.*

| # | Test Type | What to Test |
|---|-----------|-------------|
| 1 | Unit | `pytest tests/upress_validation/` — U01–U12 PASS |
| 2 | Integration | FTPS: authenticate, upload test file, verify public URL accessible |
| 3 | End-to-End | Full automated pipeline → file on uPress → WordPress page shows live data |
| 4 | Fallback | Simulate failed FTPS upload; verify `manifest_last_good.json` serves old data |
| 5 | Stale Banners | WordPress page with -4d data: warning banner visible; -9d: irrelevant banner visible |
| 6 | Stability | 3 consecutive automated publish runs without manual action |

---

## Always Check (Every Gate)

| Check | SQL / Command |
|-------|--------------|
| No FLOAT in price columns | `SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND data_type LIKE 'float%';` → must return 0 rows |
| All timestamps TIMESTAMPTZ | `SELECT column_name, data_type FROM information_schema.columns WHERE column_name LIKE '%_at' AND data_type NOT LIKE '%time zone%';` → must return 0 rows |
| No session.query() | `grep -r "session.query" organic_market_agent/` → must return nothing |
| No hardcoded product names | Review new code files for string literals that look like product names |
| log_entries used | After any run with a failure: `SELECT COUNT(*) FROM log_entries WHERE level='ERROR';` → must be > 0 |
| English only | `grep -rn "[א-ת]" organic_market_agent/` → must return 0 (Hebrew only in seed data values) |
| **Changelog updated** | **`CHANGELOG.md` has entries for all changes introduced since last gate — FAIL if missing** |
| **Spec compliance** | **Verify changes match the relevant spec docs, not just "working code"** |

---

## QA Report Template

```markdown
# QA Report — Gate G[N] — [Topic]
**Date:** YYYY-MM-DD
**From:** Team 50
**Gate:** G[N]
**Decision:** PASS | FAIL | CONDITIONAL PASS

## Summary
[1–2 sentences: what was tested and the overall result]

## Unit Tests
pytest command run:
pytest output: (paste)
Result: PASS / FAIL

## QA Tests

| # | Test Type | Description | Result | Evidence |
|---|-----------|-------------|--------|---------|
| 1 | Integration | [description] | PASS/FAIL | [SQL output / CLI output] |
| 2 | Data Quality | [description] | PASS/FAIL | [evidence] |
...

## Critical Findings (FAIL — blocks gate)
[Each finding with file/line/SQL/output as evidence]

## Minor Findings (WARNING — does not block)
[Findings to note but not blocking]

## Required Actions to Open Gate
- [ ] [Action] — Owner: Team 10 / Team 20 / Nimrod

## [USER ACTION REQUIRED] (if applicable)
[What Nimrod needs to do]

## Gate Decision
Gate G[N]: [OPEN / BLOCKED]
```

---

## Spec Documents (QA Reference)

**MANDATORY: Read the relevant spec document BEFORE testing any area.**
QA validates against the spec — not against "what works."

| Document | Use When Testing |
|----------|-----------------|
| `docs/GLOSSARY.md` | Always — READ FIRST every session |
| `documentation/README.md` | English documentation hub |
| `docs/DATABASE_SCHEMA_SPEC_HE.md` | Schema checks, data type validation, constraint testing |
| `docs/NORMALIZER_SPEC_HE.md` | Normalizer behavior, stage order, blocking/non-blocking rules |
| `docs/PIPELINE_ALGORITHMS_HE.md` | End-to-end pipeline flow, collector/parser behavior |
| `docs/PRODUCT_CATALOG_V1.md` | Product count, aliases, unit mapping |
| `docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` | Publish thresholds, aggregation rules |
| `docs/ARCHITECTURE_DECISIONS_HE.md` | Locked decisions, stack constraints |
| `docs/RTL_DEVELOPMENT_GUIDE.md` | UI/UX checks for Hebrew RTL |
| `docs/OPERATIONS.md` | Scheduler, cron, operational behavior |

---

## Golden Rules for Team 50

1. **The spec and mandate always win** — working code that deviates from spec is a FAIL
2. **Read the spec before testing** — always consult the relevant spec documents before running QA
3. **Evidence for every finding** — not "looks wrong", but exact file/line/SQL/output
4. **Never fix code** — report and block; Team 10/20 fix, Team 50 re-verifies
5. **Regression always** — every gate from G3 onward includes a regression check of prior tables
6. **Document your SQL** — paste the exact queries and outputs in the QA report
7. **Conditional PASS** — use it only when blockers are minor and well-defined; list exact conditions
8. **English only** — all reports in English
9. **Verify changelog** — at every gate, check that `CHANGELOG.md` is updated with all changes since the last gate; FAIL if missing
10. **Verify spec compliance** — check that changes align with spec doc intent, not just "pass the tests"
