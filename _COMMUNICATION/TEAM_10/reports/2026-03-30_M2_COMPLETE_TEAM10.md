# Team 10 — M2 Collection Layer Complete

**Date:** 2026-03-30  
**Milestone:** M2 — Collection Layer / Gate G2  
**Status:** COMPLETE (implementation + verification executed by Team 10)  
**Reference:** [_COMMUNICATION/TEAM_10/MANDATE_M2_COLLECTION_LAYER.md](../MANDATE_M2_COLLECTION_LAYER.md)

**Handoff:** Team 100 — acceptance review per architecture process.  
**QA request:** Team 50 — formal G2 sign-off (see `_COMMUNICATION/TEAM_50/reports/2026-03-30_G2_REVIEW_REQUEST_M2_TEAM50.md`).

---

## Environment (verification run)

- Python version: **3.11.15** (`python3.11`)
- PostgreSQL version: **15** (Alpine image `postgres:15-alpine`, ephemeral Docker container on `127.0.0.1:55433` — used only to produce reproducible evidence; production remains direct install per stack lock)
- Alembic: `alembic upgrade head` (revisions 001–005)
- Note: For faster verification, `retry_policy_json` was temporarily set to `max_retries: 0` on all `source_fetch_profiles` in the test database only (not a code change).

---

## Deliverables (code)

| Area | Location |
|------|----------|
| Exceptions | `organic_market_agent/utils/exceptions.py` |
| Log persistence (onboarding) | `organic_market_agent/utils/log_persist.py` |
| Collectors | `organic_market_agent/collectors/` |
| Parsers | `organic_market_agent/parsers/` |
| CLI | `organic_market_agent/scheduler/run_ingestion.py` |
| Tests | `tests/test_collectors.py`, `tests/test_parsers.py`, `tests/conftest.py` |

---

## Output: `python -m organic_market_agent.scheduler.run_ingestion --run-type manual`

**First run (representative tail):**

```text
IngestionRun #1: status=partial succeeded=16 failed=4 skipped=0 community_ok=13
```

Failures observed (live network, same run):

- **SRC001:** `SSL: CERTIFICATE_VERIFY_FAILED` (expired certificate on target host).
- **SRC015, SRC016, SRC017:** HTTP **403 Forbidden** (bot/WAF or access policy on target hosts).

**Second run (dedup):** duplicate checksums produced `skipped` statuses in logs (e.g. `Source SRC018: duplicate asset, skipping`). Final line:

```text
IngestionRun #2: status=partial succeeded=8 failed=4 skipped=8 community_ok=7
```

**G2 mandate evidence (verbatim T01–T09):** [_COMMUNICATION/TEAM_10/reports/2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md](./2026-03-30_M2_G2_EVIDENCE_APPENDIX_TEAM10.md)

(`succeeded` counts sources that fetched new bytes; skipped sources are not counted as succeeded per current CLI logic — dedup behavior is visible in `source_fetch_runs.status` and logs.)

---

## Output: `pytest` (full suite)

```text
python3.11 -m pytest tests/ -v
============================== 27 passed in 0.26s ==============================
```

Breakdown: `tests/test_collectors.py` (10), `tests/test_parsers.py` (10), `tests/test_db_health.py` (7). No live HTTP in unit tests.

---

## Output: `python -m organic_market_agent.db.check`

```text
RESULT: PASS
```

(All 23 tables reported OK against the verification database.)

---

## DB counts after two ingestion runs (verification database)

| Table | Rows |
|-------|------|
| ingestion_runs | 2 |
| source_fetch_runs | 40 |
| raw_assets | 24 |
| raw_extracted_items | **3210** |
| log_entries | 12 |

**source_fetch_runs by status:** success=24, skipped=8, failed=8 (cumulative over both runs).

Gate G2 threshold **raw_extracted_items ≥ 50** is satisfied.

---

## Dedup verification

- Re-running ingestion against the same sources produced **skipped** fetch runs when the SHA-256 checksum matched an existing `raw_assets` row for that source (see log lines `duplicate asset, skipping`).
- No duplicate `raw_assets` rows for the same `(source_id, checksum_sha256)` path in this verification run.

---

## Deviations / follow-ups (for Team 100 / Team 20 / sources)

1. **Onboarding compliance:** ERROR-level rows are written to **`log_entries`** for collector exhaustion failures, unexpected collector errors, and `ParserError` in `ParserEngine` (extends mandate snippets, which only showed stdout logging).

2. **Live EasyFarm HTML + `easyfarm_catalog`:** Several EasyFarm pages fetched successfully but the parser extracted **0** rows (selectors likely drift vs live DOM). **Mitigation:** use `source_fetch_profiles.selector_profile` in DB per source, or adjust parser defaults after Team 100 guidance — not a collector defect.

3. **Benchmark / verification sources (e.g. SRC018–SRC020):** Seed uses `fetch_mode='html_page'` while `normalizer_type` expects JSON parsers (`retail_benchmark` / `official_wholesale`). Fetches return HTML → parser errors (logged + `log_entries`). **Recommendation:** Team 20 / Team 100 align `source_fetch_profiles.fetch_mode` and `entry_url` with real endpoint shapes, or split HTML vs JSON sources in seed.

4. **External availability:** SSL expiry and HTTP 403 on some URLs are outside Team 10 code scope; ingestion correctly marks `failed`, continues other sources, and persists errors.

---

## Gate G2 request (Team 50)

Team 50 is requested to validate M2 against the mandate and `docs/PIPELINE_ALGORITHMS_HE.md`, using this report and the dedicated QA request file in `TEAM_50/reports/`.

---

## Process note (Team 10)

Team 10 executes builds, migrations, test runs, and ingestion evidence internally. Operator-only steps are not required from the project lead for routine verification; cross-team asks are filed in `TEAM_20` / `TEAM_50` / `TEAM_100` reports as appropriate.
