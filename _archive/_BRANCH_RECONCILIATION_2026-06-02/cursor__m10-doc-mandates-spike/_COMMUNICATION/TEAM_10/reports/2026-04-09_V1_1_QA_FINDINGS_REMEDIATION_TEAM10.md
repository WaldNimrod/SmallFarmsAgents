# QA findings remediation — G-V1.1 (Team 50 report QA-RPT-20260405-G-V1-1)

**Date:** 2026-04-09  
**From:** Team 10  
**To:** Team 50 / Team 100 / Team 190  
**Source:** `_COMMUNICATION/TEAM_50/reports/2026-04-05_GATE_G_V1_1_REPORT_TEAM50.md`

This document maps **each finding** to root cause, **remediation** (code/docs/ops), and **re-validation** command.  
**Status:** Code remediation applied in repo (2026-04-09): see [`CHANGELOG.md`](../../../CHANGELOG.md) and [`2026-04-09_V1_1_QA_REMEDIATION_VERIFICATION_TEAM10.md`](2026-04-09_V1_1_QA_REMEDIATION_VERIFICATION_TEAM10.md).

---

## 1. Preconditions / gate entry (report §0)

| Finding | Root cause | Remediation |
|---------|------------|-------------|
| Completion **PARTIAL** | Phase B/E + A2 export not run without DB | Operator: Postgres + `alembic upgrade head` → 073; run Phase B; refresh completion to **COMPLETE** |
| No Team 190 **completion-package** PASS | Preflight on HOLD while partial | After completion COMPLETE + evidence, update `PREFLIGHT_REQUEST_V1_1_TEAM10.md` and obtain Team 190 PASS |
| QA request **BLOCKED** | Intentional until package ready | File new **unblocked** re-review request (see `_COMMUNICATION/TEAM_50/reports/2026-04-09_V1_1_QA_REREVIEW_REQUEST_TEAM10.md`) **only** when preconditions met |

---

## 2. Environment (report §1) — Python 3.11+

| Finding | Remediation |
|---------|-------------|
| `.venv` Python **3.9.6** < policy **3.11+** | Recreate venv: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'` (or project install instructions) |
| `requires-python` | Already `>=3.11` in [`pyproject.toml`](../../pyproject.toml) — enforce with correct interpreter |
| **Repo pin** | Add **`.python-version`** with content `3.11` (pyenv / asdf) at repo root |

---

## 3. T01 — Full suite without DB

| Finding | Root cause | Remediation |
|---------|------------|-------------|
| **8 failed** (connection refused) | `test_db_health.py` + `test_t14` hit DB while Postgres down | **A.** Module-level skip in `tests/test_db_health.py` when `OperationalError` on `SELECT 1` (same pattern as `db_session` in `conftest.py`). **B.** `test_t14_runs_list_shows_manager_columns`: add `require_postgres` fixture or inline skip. **C.** Add `postgres_reachable()` + `@pytest.fixture require_postgres` in [`tests/conftest.py`](../../tests/conftest.py). |

**Re-validation:** With DB **down**: `pytest tests/ -m "not upress" -q` → 0 failures (health module skipped; T14 skipped).  
**Certified QA:** With DB **up**: no skip — full T01 must pass for gate.

---

## 4. T02–T03, T06–T07, T11 SQL — no DB

| Finding | Remediation |
|---------|-------------|
| SQL not run | Run spec SQL on operator DB; paste into completion report |

**Artifacts to add** (not created while session was Plan-only — add in Agent mode):

- `scripts/sql/g_v1_1_t02_distinct_unresolvable.sql` — verbatim §A2.3 first query
- `scripts/sql/g_v1_1_t03_src021_unresolvable.sql` — verbatim §A2.3 second query
- `scripts/sql/g_v1_1_t06_cherry_guard.sql` — bundle §A1.2 queries (CQ-P08)
- `scripts/sql/g_v1_1_t07_basket_inactive_aliases.sql` — §A1.3 + CSA basket target check
- `scripts/sql/g_v1_1_t11_basket_tier_distribution.sql` — from LOD400 §C4.5 / QA mandate T11 (tier distribution)

---

## 5. T04 — Published products < 77

| Finding | Remediation |
|---------|-------------|
| **49** products | Phase B full ingestion + aggregate + publish on live DB — not a code defect |

---

## 6. T08–T10 — matrices missing

| Finding | Remediation |
|---------|-------------|
| Completion items 3–5 **Pending** | File runnable SQL (LOD400 §C1–C3); use `s.name` not `s.name_he` (ORM column is `name`) |

**Artifacts** (same: add in Agent mode; replace `s.name_he` with `s.name AS source_name`):

- `scripts/sql/g_v1_1_c1_eggs_matrix.sql` — §C1.1 + `GROUP BY` uses `s.name`
- `scripts/sql/g_v1_1_c2_passion_fruit_audit.sql` — §C2.1
- `scripts/sql/g_v1_1_c3_blueberries_audit.sql` — §C3.1

Embed `psql` output tables in completion report addendum after Phase B.

---

## 7. T14 — Blog + vision link

| Finding | Remediation |
|---------|-------------|
| WP draft not confirmed | Nimrod: WP REST or admin (see A4 curl in LOD400) |
| Vision block must **link** to placeholder | Add in [`organic_market_agent/publisher/templates/public_report_body.html`](../../organic_market_agent/publisher/templates/public_report_body.html) inside `.vision-block` a line linking to `https://nimrod.bio/blog/farm-not-profitable/` (slug per spec §A4.4) with accessible label (e.g. draft article title) |

Update `2026-04-08_V1_1_A4_BLOG_USER_ACTION_TEAM10.md` after WP draft exists.

---

## 8. T16 — E2E pipeline

| Finding | Remediation |
|---------|-------------|
| Not witnessed | Operator runs Phase B/E block; attach log snippet to completion report |

---

## 9. Point test run checklist (post-remediation)

```bash
python3.11 -m pytest tests/ -m "not upress" -q
python3.11 -m pytest tests/test_basket_tier_resolver.py -v
python3.11 -m organic_market_agent.db.check
alembic current
```

---

## 10. Filed requests (this wave)

- Re-review QA: `_COMMUNICATION/TEAM_50/reports/2026-04-09_V1_1_QA_REREVIEW_REQUEST_TEAM10.md`
- Constitutional preflight re-request: `_COMMUNICATION/TEAM_190/2026-04-09_PREFLIGHT_REREVIEW_V1_1_TEAM10.md`
