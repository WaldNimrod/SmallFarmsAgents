---
document_type: QA_FINDINGS_REPORT
version: "1.0"
---

# QA Findings Report — Gate G-V1.1 (re-run)

**Report ID:** QA-RPT-20260409-G-V1-1  
**QA Review Request:** `QA-REQ-20260330-G-V1-1` — `_COMMUNICATION/TEAM_50/reports/2026-03-30_V1_1_QA_REQUEST_TEAM10.md` (**BLOCKED**)  
**From:** Team 50 (QA)  
**To:** Team 100 (Architecture)  
**CC:** Team 10 (Feature Dev), Team 190 (Constitutional preflight)  
**Date:** 2026-04-09  
**Gate:** G-V1.1 — Consolidated CQ + M10.x + M9C (v1.1.0)  
**QA Mandate:** `_COMMUNICATION/TEAM_50/QA_MANDATE_G_V1_1.md` (v1.1)  
**References:**  
- ARCH-20260408-TEAM50-CLARIFICATIONS-V1-1 — `_COMMUNICATION/TEAM_100/reports/2026-04-08_TEAM50_CLARIFICATIONS_RESPONSE_TEAM100.md`  
- Team 50 briefing — `_COMMUNICATION/TEAM_50/reports/2026-04-08_V1_1_BRIEFING_TEAM100.md` (§0 T01–T16 table)

---

## 0. Preconditions (mandate §5 + briefing §8–9)

| Precondition | Evidence | Met? |
|--------------|----------|------|
| Team 10 completion report **COMPLETE** | `_COMMUNICATION/TEAM_10/reports/2026-04-08_V1_1_COMPLETION_TEAM10.md` — **PARTIAL**; **Not ready for G-V1.1** | **No** |
| Team 190 **PASS** on final v1.1.0 completion package | `_COMMUNICATION/TEAM_190/PREFLIGHT_REQUEST_V1_1_TEAM10.md` — **HOLD**; package **PARTIAL**; full preflight not executed | **No** |
| Team 10 **QA_REVIEW_REQUEST** unblocked + preload checklist | `2026-03-30_V1_1_QA_REQUEST_TEAM10.md` — **BLOCKED** | **No** |

Formal gate entry: **not satisfied**. Execution below records evidence for Team 100 after remediation work (pytest skip behavior when DB absent).

---

## 1. Environment

| Check | Result |
|-------|--------|
| Python (`.venv`) | `3.9.6` — below repo policy **3.11+** (see `.python-version` / `pyproject.toml`); noted for certified runs |
| `DATABASE_URL` for run | `postgresql://oma:oma@127.0.0.1:5433/organic_market_agent` (canonical per `.env.example` / `DOCKER_SHARED_WORKSTATION.md`) |
| TCP `127.0.0.1:5433` | **Connection refused** — no PostgreSQL listener on canonical port at execution time |
| `alembic current` | **Not run to success** — requires live DB |
| `python -m organic_market_agent.db.check` | **Not run to PASS** — requires live DB |
| Repo migration **073** | Present in codebase: `organic_market_agent/db/versions/073_src_wa_pending_manual.py` |

---

## 2. Test matrix (T01–T16)

| ID | Result | Notes |
|----|--------|------|
| **T01** | **PASS** | `pytest tests/ -m "not upress" -q` — **0 failures** (see §3) |
| **T02** | **SKIP** | SQL needs DB — port closed |
| **T03** | **SKIP** | SQL needs DB |
| **T04** | **FAIL** | `public_report.json` → **49** products (mandate ≥ **77**) |
| **T05** | **PASS (note)** | **0** rows `product_id == PRD027` (below publish threshold — mandate allows PASS with note) |
| **T06** | **SKIP** | SQL needs DB |
| **T07** | **SKIP** | SQL needs DB |
| **T08** | **FAIL** | Completion report item 3 — C1 egg matrix **Pending** |
| **T09** | **FAIL** | Item 4 — C2 passion fruit **Pending** |
| **T10** | **FAIL** | Item 5 — C3 blueberries **PARTIAL** |
| **T11** | **PARTIAL** | `pytest tests/test_basket_tier_resolver.py` — **16 passed**; tier distribution SQL not run (no DB) |
| **T12** | **CONDITIONAL PASS** | Team 100 ADR `_COMMUNICATION/TEAM_100/reports/2026-04-08_ADR_PACK_WEIGHT_COMPARISON_TEAM100.md` **not present**; C3 notification exists: `2026-04-08_C3_BLUEBERRY_FINDINGS_TEAM10.md` (mandate intermediate path) |
| **T13** | **PASS** | `documentation/05-admin-and-operations/WHATSAPP_DATA_SUBMISSION_PROTOCOL.md` — `pending_manual`, migration **073**, columns `raw_product_name` / `raw_price_text` / `raw_unit_text`, FK via `source_fetch_run_id` |
| **T14** | **PASS** | Publisher template `organic_market_agent/publisher/templates/public_report_body.html` — vision block links to `https://nimrod.bio/blog/farm-not-profitable/` (M9C placeholder) |
| **T15** | **PASS** | No `SRC[0-9]{3}` in `output/public/public_report.json` (grep); no SRC tokens in committed JSON body for privacy spot-check |
| **T16** | **NOT EXECUTED** | Full pipeline not re-run / no Phase B/E witness log in this session |

**Privacy override (T15):** No SRC-code leak observed in checked JSON.

---

## 3. Evidence (verbatim)

### T01 — `pytest tests/ -m "not upress" -q`

Environment: `DATABASE_URL=postgresql://oma:oma@127.0.0.1:5433/organic_market_agent`

```
125 passed, 75 skipped, 12 deselected in 1.33s
```

(Includes module-level skip of `tests/test_db_health.py` when PostgreSQL is unreachable.)

### T04 / T05 — `output/public/public_report.json`

```
T04 products: 49
T05 PRD027: 0
```

### T11 — `pytest tests/test_basket_tier_resolver.py -q`

```
................                                                         [100%]
16 passed in 0.07s
```

### T15 — SRC pattern in `public_report.json`

Workspace search: `SRC[0-9]{3}` → **no matches** in `output/public/public_report.json`.

### TCP check — canonical Postgres port

```
PORT_FAIL [Errno 61] Connection refused
```

(host `127.0.0.1`, port `5433`)

---

## 4. Gate decision

### GATE G-V1.1 — **FAIL**

**Reasons (mandate §3):**  
- **CRITICAL:** T04 fails (49 < 77).  
- **CRITICAL:** T02, T06, T07 not executed on a live certified DB (environment).  
- **CRITICAL:** Preconditions not met (completion **PARTIAL**, Team 190 preflight **HOLD**, QA request **BLOCKED**).  
- **CRITICAL:** T16 not verified.

T01 regression suite reported **zero failures**; skipped tests must be understood as **non-certification** of DB-backed criteria until PostgreSQL is reachable at canonical **5433** and `db.check` / mandate SQL pass.

---

## 5. Feedback to Team 100 (canonical)

1. **Unblock formally:** completion report → **COMPLETE** (or **COMPLETE WITH DEVIATIONS** with Team 100 sign-off), Team 190 preflight **PASS** on that package, refreshed **QA_REVIEW_REQUEST** with preload checklist.  
2. **Environment:** Ensure certified QA can bind to **`127.0.0.1:5433`** per `documentation/08-troubleshooting/DOCKER_SHARED_WORKSTATION.md` (no conflicting stack; `oma-postgres` running).  
3. **Publish threshold:** Re-run Phase B/E so `public_report.json` meets **T04 ≥ 77** products and document PRD027 per **T05**.  
4. **Python:** Align operator/CI interpreter to **3.11+** for parity with `requires-python`.  
5. **T12:** Team 100 may still file Pantry ADR when C3 evidence is sufficient; until then **CONDITIONAL PASS** on C3 notification remains valid per mandate.

---

**Binding format:** `_COMMUNICATION/TEMPLATES/QA_FINDINGS_REPORT.md`
