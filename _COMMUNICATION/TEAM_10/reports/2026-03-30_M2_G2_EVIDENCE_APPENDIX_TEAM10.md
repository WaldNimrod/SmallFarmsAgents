# Team 10 — G2 QA evidence appendix (verbatim captures)

**Date:** 2026-03-30  
**Purpose:** Supply `QA_MANDATE_G2.md` T01–T09 outputs for Team 50 re-validation after **G1** is formally open.  
**Canonical QA status:** [_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md](../../TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md) (FAIL / BLOCKED until G1 sign-off).  
**T06 mandate clarification:** [_COMMUNICATION/TEAM_100/reports/2026-03-30_T06_DEDUP_CRITERIA_CLARIFICATION_REQUEST_TEAM10.md](../../TEAM_100/reports/2026-03-30_T06_DEDUP_CRITERIA_CLARIFICATION_REQUEST_TEAM10.md)

---

## Environment (this capture)

| Item | Value |
|------|--------|
| Python | 3.11.15 (`python3.11`) |
| PostgreSQL | 15 (`postgres:15-alpine` Docker, `127.0.0.1:55436`) — **engineering evidence**; QA mandate prefers **direct install** for final sign-off |
| `DATABASE_URL` | `postgresql://oma:t@127.0.0.1:55436/organic` (ephemeral; container removable) |
| `RAW_FILES_ROOT` | `/tmp/oma_g2_appendix` |
| Alembic | `upgrade head` (001–005 seed) |

**Engineering shortcut (T02/T06 throughput):** Before run 1, all `source_fetch_profiles.retry_policy_json` set to `{"max_retries": 0, "backoff_seconds": 0}` (except **T07** segment below restores multi-retry for SRC002 only). This does **not** change application code.

---

## CLI semantics (T06 vs `sources_succeeded`)

- `succeeded` = count of sources with **`success`** fetch **and** a new `RawAsset` for that run (checksum dedup yields **`skipped`**, not `success`).
- `skipped` = duplicate checksum for that source (`skipped=N` printed on the summary line).
- Therefore a second live run can show **`succeeded=8` and `skipped=8`** simultaneously while T06 SQL shows **`new_assets > 0`** — any URL whose bytes **change** produces a new asset. See Team 100 note above.

---

## T01 — Unit tests

**Command:** `python3.11 -m pytest tests/test_collectors.py tests/test_parsers.py -v`

```text
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-8.4.2, pluggy-1.6.0 -- /opt/homebrew/opt/python@3.11/bin/python3.11
cachedir: .pytest_cache
rootdir: /Users/nimrod/Documents/SmallFarmsAgents
configfile: pyproject.toml
plugins: cov-5.0.0, anyio-4.13.0
collecting ... collected 20 items

tests/test_collectors.py::test_select_collector_easyfarm PASSED          [  5%]
tests/test_collectors.py::test_select_collector_json_endpoint PASSED     [ 10%]
tests/test_collectors.py::test_select_collector_html_default PASSED      [ 15%]
tests/test_collectors.py::test_select_collector_directory_page PASSED    [ 20%]
tests/test_collectors.py::test_easyfarm_fetch_html_success PASSED        [ 25%]
tests/test_collectors.py::test_easyfarm_fetch_raises_on_http_error PASSED [ 30%]
tests/test_collectors.py::test_html_collector_returns_html PASSED        [ 35%]
tests/test_collectors.py::test_govt_collector_returns_json PASSED        [ 40%]
tests/test_collectors.py::test_govt_collector_returns_text_for_non_json_mode PASSED [ 45%]
tests/test_collectors.py::test_collector_engine_duplicate_marks_skipped PASSED [ 50%]
tests/test_parsers.py::test_easyfarm_extracts_two_items PASSED           [ 55%]
tests/test_parsers.py::test_easyfarm_empty_page_returns_empty_list PASSED [ 60%]
tests/test_parsers.py::test_easyfarm_selector_override_merges_defaults PASSED [ 65%]
tests/test_parsers.py::test_simple_grid_table_extracts_items PASSED      [ 70%]
tests/test_parsers.py::test_simple_grid_no_prices_returns_empty PASSED   [ 75%]
tests/test_parsers.py::test_simple_grid_list_fallback_extracts PASSED    [ 80%]
tests/test_parsers.py::test_official_wholesale_parses_array PASSED       [ 85%]
tests/test_parsers.py::test_official_wholesale_unwraps_envelope PASSED   [ 90%]
tests/test_parsers.py::test_official_wholesale_raises_on_invalid_json PASSED [ 95%]
tests/test_parsers.py::test_official_wholesale_raises_on_non_list_payload PASSED [100%]

============================== 20 passed in 0.20s ==============================
```

---

## T02 — Live ingestion (run 1)

**Command:** `python3.11 -m organic_market_agent.scheduler.run_ingestion --run-type manual`

**Exit code:** 0  
**Pass note:** `sources_succeeded` (16) ≥ 3; `status=partial` (not `failed`).

```text
(full log — run 1)
```

```text
2026-03-30 03:00:33 WARNING  organic_market_agent.organic_market_agent.collectors.base — Fetch attempt 1/1 failed for source=SRC001: EasyFarm fetch failed: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1016)
2026-03-30 03:00:33 ERROR    organic_market_agent.organic_market_agent.collectors.base — Source SRC001 failed after 0 retries
2026-03-30 03:00:33 INFO     organic_market_agent.organic_market_agent.collectors.base — Source SRC002: fetched 69850 bytes, checksum=4b01d9843944
... (lines omitted identical to repo capture) ...
IngestionRun #1: status=partial succeeded=16 failed=4 skipped=0 community_ok=13
```

**T02 SQL** (`ingestion_runs` last 5):

```text
id	run_type	status	sources_total	sources_succeeded	sources_failed	community_sources_succeeded	finished_at
2	manual	partial	20	8	4	7	2026-03-30 00:01:11.507184+00:00
1	manual	partial	20	16	4	13	2026-03-30 00:00:50.553051+00:00
```

*(After T07, a third row `id=3` exists — use `ORDER BY id DESC` for latest two runs when re-scoring T02.)*

---

## T02 — Live ingestion (run 2, immediate, for T06)

```text
2026-03-30 03:00:54 WARNING  organic_market_agent.organic_market_agent.collectors.base — Fetch attempt 1/1 failed for source=SRC001: EasyFarm fetch failed: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1016)
...
IngestionRun #2: status=partial succeeded=8 failed=4 skipped=8 community_ok=7
```

---

## T03 — `raw_assets` sample + filesystem

**SQL** (mandate query, last 20 rows):

```text
source_code	file_type	bytes_size	checksum_len	storage_path	captured_at
SRC019	html	1166	64	/tmp/oma_g2_appendix/SRC019/2026-03-30/SRC019_000110.html	2026-03-30 00:00:54.567799+00:00
... (18 more rows) ...
SRC006	html	21141	64	/tmp/oma_g2_appendix/SRC006/2026-03-30/SRC006_000035.html	2026-03-30 00:00:32.953887+00:00
```

**`ls -la $RAW_FILES_ROOT` (first lines):**

```text
total 0
drwxr-xr-x  19 nimrod  wheel   608 Mar 30 03:00 .
drwxr-xr-x   3 nimrod  wheel    96 Mar 30 03:00 SRC002
drwxr-xr-x   3 nimrod  wheel    96 Mar 30 03:00 SRC003
... SRC004 … SRC020, artifacts ...
```

---

## T04 — `raw_extracted_items` volume

```text
total_items	fetch_runs_covered	named_items
3210	16	3210
```

---

## T05 — `source_fetch_runs` breakdown (cumulative over runs 1–2 before T07)

```text
status	cnt
failed	8
skipped	8
success	24
```

---

## T06 — Mandate SQL (second run = `MAX(id)` among runs 1–2 at query time)

**Query A — `new_assets`:**

```text
new_assets
8
```

**Query B — status histogram for `MAX(id)` ingestion run:**

```text
status	cnt
failed	4
skipped	8
success	8
```

**Assessment vs strict mandate text:** `new_assets ≠ 0` and not all rows are `skipped` because live pages changed bytes between runs. **Team 100 clarification requested** (see header link).

---

## T07 — Error handling + retry + `log_entries`

**Steps executed:** Saved original SRC002 URL; `UPDATE` bad URL + `retry_policy_json` = `max_retries=2`, `backoff_seconds=0` for SRC002 only;  
`python3.11 -m organic_market_agent.scheduler.run_ingestion --source-code SRC002`; then restored URL + default retry JSON.

**CLI:**

```text
2026-03-30 03:01:34 WARNING  organic_market_agent.organic_market_agent.collectors.base — Fetch attempt 1/3 failed for source=SRC002: EasyFarm fetch failed: [Errno 61] Connection refused
2026-03-30 03:01:34 WARNING  organic_market_agent.organic_market_agent.collectors.base — Fetch attempt 2/3 failed for source=SRC002: EasyFarm fetch failed: [Errno 61] Connection refused
2026-03-30 03:01:34 WARNING  organic_market_agent.organic_market_agent.collectors.base — Fetch attempt 3/3 failed for source=SRC002: EasyFarm fetch failed: [Errno 61] Connection refused
2026-03-30 03:01:34 ERROR    organic_market_agent.organic_market_agent.collectors.base — Source SRC002 failed after 2 retries
IngestionRun #3: status=failed succeeded=0 failed=1 skipped=0 community_ok=0
```

**SQL** (`source_fetch_runs` latest for SRC002):

```text
status	retry_count	error_message
failed	2	EasyFarm fetch failed: [Errno 61] Connection refused
```

**SQL** (`log_entries` ERROR, sample):

```text
level	module	message (trimmed)
ERROR	collectors.base	Collector failed for SRC002: EasyFarm fetch failed: [Errno 61] Connection refused
```

**Restore:** SRC002 `entry_url` and `retry_policy_json` reset to seed-like defaults after capture.

---

## T08 — Normalizer isolation

```text
obs_count
0
```

---

## T09 — M1 table counts (expected seed; G1 baseline pending formal QA)

```text
tbl	cnt
measurement_units	11
products	29
sources	20
product_aliases	44
unit_conversions	4
```

**Note:** Exact parity with **G1-confirmed** counts requires `_COMMUNICATION/TEAM_50/reports/*_QA_G1_TEAM50.md`.

---

## End of appendix

Team 50 may re-run the same SQL verbatim on a **direct PostgreSQL** environment per `QA_MANDATE_G2.md` environment reminder.
