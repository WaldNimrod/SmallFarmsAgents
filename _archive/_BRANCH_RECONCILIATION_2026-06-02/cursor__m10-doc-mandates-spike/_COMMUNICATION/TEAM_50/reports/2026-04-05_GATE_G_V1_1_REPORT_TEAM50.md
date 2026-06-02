---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G-V1.1

**Report ID:** QA-RPT-20260405-G-V1-1  
**QA Review Request:** `QA-REQ-20260330-G-V1-1` — `_COMMUNICATION/TEAM_50/reports/2026-03-30_V1_1_QA_REQUEST_TEAM10.md` (status: **BLOCKED**; superseded completion pointer: `2026-04-08_V1_1_COMPLETION_TEAM10.md`)  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Team 190 (Constitutional preflight)  
**Date:** 2026-04-05  
**Gate:** G-V1.1 — Consolidated CQ + M10.x + M9C (v1.1.0)  
**QA Mandate executed:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` (v1.1)  
**Architectural / briefing references:**  
- ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 — `_COMMUNICATION/TEAM_100/reports/2026-04-08_TEAM50_CLARIFICATIONS_RESPONSE_TEAM100.md`  
- Team 50 briefing — `_COMMUNICATION/TEAM_50/reports/2026-04-08_V1_1_BRIEFING_TEAM100.md` (includes §0 test-impact table)

---

## 0. Preconditions (mandate §5 + briefing §8–9) — gate entry

| Precondition | Evidence | Met? |
|--------------|----------|------|
| Team 10 completion report filed | `_COMMUNICATION/TEAM_10/reports/2026-04-08_V1_1_COMPLETION_TEAM10.md` — **Mandate status: PARTIAL**; **Gate readiness: Not ready for G-V1.1** | **No** |
| Team 190 **PASS** on **v1.1.0 completion package** | `_COMMUNICATION/TEAM_190/PREFLIGHT_REQUEST_V1_1_TEAM10.md` states package **PARTIAL**. Team 190 reports on file include LOD400 **spec** validation PASS (`2026-04-08_PHASES_AB_LOD400_VALIDATION_TEAM190.md`, `2026-04-08_PHASES_AB_LOD400_REVALIDATION_V2_TEAM190.md`) — **not** a completion-package sign-off on the final Team 10 deliverable. | **No** |
| Team 10 `QA_REVIEW_REQUEST` with preload checklist | `2026-03-30_V1_1_QA_REQUEST_TEAM10.md` filed as **BLOCKED**; pre-conditions unchecked; points to `2026-04-08_V1_1_COMPLETION_TEAM10.md` (still partial). | **No** (formal unblock N/A) |

**Conclusion:** Formal G-V1.1 entry criteria were **not satisfied** before this execution. Team 50 proceeded per operator instruction to record **evidence and a binding FAIL** for the incomplete baseline.

---

## 1. Environment verified

| Check | Result |
|-------|--------|
| Python interpreter | `3.9.6` (`.venv/bin/python`) — **below** project policy 3.11+; pytest used this interpreter |
| Docker postgres | **Not verified** — `localhost:55435` **connection refused** |
| DATABASE_URL | Configured for `localhost:55435` — **not reachable** at execution time |
| Alembic revision (live DB) | **`alembic current` failed** (same connection error) |
| Repo migration head | `organic_market_agent/db/versions/073_src_wa_pending_manual.py` defines `revision = "073"` — **head ≥ 073 present in codebase** |
| `python -m organic_market_agent.db.check` | **Not executed to PASS** — connection refused |

**Environment verdict:** **INVALID for certified QA** — DB offline; `alembic current` / `db.check` could not complete.

---

## 2. Test results (T01–T16)

| Test ID | Name | Result | Weight | Notes |
|---------|------|--------|--------|-------|
| T01 | Full suite `not upress` | **FAIL** | CRITICAL | 8 failed (DB); 125 passed; 73 skipped; 12 deselected |
| T02 | Unresolvable count SQL | **SKIP** | CRITICAL | No DB |
| T03 | SRC021 unresolvable SQL | **SKIP** | HIGH | No DB |
| T04 | Published product count ≥ 77 | **FAIL** | CRITICAL | `public_report.json`: **49** products |
| T05 | PRD027 ≤ 1 | **PASS (with note)** | HIGH | **0** PRD027 rows (below publish threshold per mandate) |
| T06 | Cherry/tomato guard SQL | **SKIP** | CRITICAL | No DB |
| T07 | Inactive basket codes SQL | **SKIP** | CRITICAL | No DB |
| T08 | Eggs matrix (PRD067) | **FAIL** | HIGH | Completion report item 3 **Pending** |
| T09 | Passion fruit matrix (PRD072) | **FAIL** | HIGH | Completion report item 4 **Pending** |
| T10 | Blueberries table (PRD086) | **FAIL** | MEDIUM | Item 5 **PARTIAL** — shell only; TBD table |
| T11 | CSA basket tier | **PARTIAL** | HIGH | `pytest tests/test_basket_tier_resolver.py` **16 passed**; live tier SQL **not run** (no DB) |
| T12 | Pantry ADR / C3 path | **CONDITIONAL PASS** | MEDIUM | ADR file **missing** at `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md`; **C3 notification present:** `2026-04-08_C3_BLUEBERRY_FINDINGS_TEAM10.md` (mandate intermediate PASS) |
| T13 | WhatsApp protocol | **PASS** | HIGH | Protocol documents `pending_manual`, migration **073**, columns `raw_product_name` / `raw_price_text` / `raw_unit_text`, FK via `source_fetch_run_id` |
| T14 | Blog placeholder + vision link | **FAIL** | MEDIUM | `2026-04-08_V1_1_A4_BLOG_USER_ACTION_TEAM10.md` — **USER ACTION REQUIRED**; WP draft not confirmed |
| T15 | Privacy audit | **PASS (SRC / JSON)** | CRITICAL | `rg 'SRC[0-9]{3}'` on `output/public/*.{json,html}` → **no matches**. `public_report.json` → **no `http` URLs**. `*.html` contain template URLs (fonts, CDN, nimrod.bio, WhatsApp CTA) — **not** SRC tokens; **no farm/source scrape URLs observed** in JSON |
| T16 | E2E pipeline | **NOT EXECUTED** | CRITICAL | No witness log in session; precondition failure + operator scope |

**Score:** 4 clear PASS rows (T05 note, T11 unit tests, T12 intermediate, T13, T15 as scoped); multiple FAIL/SKIP/NOT RUN.  
**Critical failures:** **> 0** — **FAIL** per decision matrix.

---

## 3. Evidence (verbatim where captured)

### Gate entry — Team 10 completion (excerpt)

From `_COMMUNICATION/TEAM_10/reports/2026-04-08_V1_1_COMPLETION_TEAM10.md`:

```
**Mandate status:** **PARTIAL** — blocked on operator DB + Phase B/E + A2 export  
**Gate readiness:** **Not ready for G-V1.1**
```

### T01 — `pytest tests/ -m "not upress" -q`

```
=========================== short test summary info ============================
FAILED tests/test_admin_routes.py::test_t14_runs_list_shows_manager_columns
FAILED tests/test_db_health.py::test_all_required_tables_exist - sqlalchemy.e...
FAILED tests/test_db_health.py::test_seed_data_counts - sqlalchemy.exc.Operat...
FAILED tests/test_db_health.py::test_products_have_aliases - sqlalchemy.exc.O...
FAILED tests/test_db_health.py::test_all_products_have_valid_unit - sqlalchem...
FAILED tests/test_db_health.py::test_no_float_price_columns - sqlalchemy.exc....
FAILED tests/test_db_health.py::test_all_timestamp_columns_are_timestamptz - ...
FAILED tests/test_db_health.py::test_check_cli_passes - sqlalchemy.exc.Operat...
8 failed, 125 passed, 73 skipped, 12 deselected in 2.65s
```

Representative failure (connection):

```
E       sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 55435 failed: Connection refused
```

### Environment — `alembic current`

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (::1), port 55435 failed: Connection refused
```

### T04 / T05 — `public_report.json`

```
T04 product count: 49
T05 PRD027 entries: 0
```

(Command: `python -c` parsing `output/public/public_report.json`.)

### T11 — `pytest tests/test_basket_tier_resolver.py -v`

```
============================== 16 passed in 0.08s ==============================
```

### T13 — Protocol spot-check (columns + `pending_manual`)

From `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md`:

- §4: `extraction_status = 'pending_manual'` after migration **073**
- §5 ERRATA: `raw_product_name`, `raw_price_text`, `raw_unit_text`; links via `source_fetch_run_id` / `raw_assets`
- §5 SQL example: `INSERT INTO raw_extracted_items (... raw_product_name, raw_price_text, raw_unit_text, extraction_status) ... 'pending_manual'`

### T15 — SRC grep

`rg 'SRC[0-9]{3}' output/public/*.{json,html}` → **no matches** (tool: workspace grep).

---

## 4. Findings summary

### Passed (within scope executed)

- **T05:** PRD027 duplicate risk not present in current JSON (0 rows).
- **T11 (unit):** Resolver tests align with briefing API expectations.
- **T12 (intermediate):** C3 notification on file; Team 100 ADR still pending.
- **T13:** Protocol matches schema errata and `pending_manual` / 073 narrative.
- **T15:** No SRC token leakage in committed `public_report*.json/html`; JSON has no embedded URLs.

### Failed / blocked

| Test / area | Root cause | Severity | Blocking? |
|-------------|------------|----------|-----------|
| Preconditions | Completion **PARTIAL**; no Team 190 completion-package PASS; QA request **BLOCKED** | Critical | **Yes** |
| Environment | PostgreSQL not accepting connections on configured port | Critical | **Yes** |
| T01 | 8 tests require live DB | Critical | **Yes** |
| T02–T03, T06–T07, T11 SQL | No DB | Critical / High | **Yes** (where CRITICAL) |
| T04 | Product count 49 < 77 | Critical | **Yes** |
| T08–T10 | Completion report matrices/tables not delivered | High / Medium | **Yes** (HIGH aggregate) |
| T14 | WP blog placeholder not confirmed | Medium | Contributes to non-PASS |
| T16 | Pipeline not witnessed/re-run | Critical | **Yes** |

---

## 5. Gate decision

### GATE G-V1.1 — **FAIL**

**Rationale:** Mandate §3 — any **CRITICAL** failure yields **FAIL**. Multiple CRITICAL items failed or could not be executed (preconditions, environment, T01, T04, T16, SQL-backed CRITICAL tests). **T15** did not reveal SRC leakage in the artifacts checked; this does **not** offset other CRITICAL gaps.

**Next actions (for gate re-open):**

1. Bring PostgreSQL online; align `alembic current` to **≥ 073**; `python -m organic_market_agent.db.check` → **PASS**.
2. Team 10: complete LOD400 execution package; file completion report as **COMPLETE**.
3. Team 190: **PASS** on the **final** v1.1.0 completion package (per `HANDOFF` / preflight).
4. Team 10: file unblocked `QA_REVIEW_REQUEST` with preload paths per briefing.
5. Re-run T01–T16 on certified DB + fresh publish artifacts.

---

## 6. Sign-off

**Decision:** **FAIL**  
**Executed by:** Team 50 (QA) — automated/IDE session evidence capture, 2026-04-05  
**Binding format:** per `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`
