# Execution Mandate — Team 20: Unblock Gate G1 (M1 Phase B)

**From:** Project Lead (Nimrod)  
**To:** Team 20 (Infrastructure)  
**Date:** 2026-03-30  
**Priority:** Critical — **Gate G2 and all downstream work are blocked** until Team 50 files formal G1 sign-off.

---

## 1. Objective

Provide a **compliant, reproducible validation environment** and coordination so **Team 50** can execute `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` in full and file:

`_COMMUNICATION/TEAM_50/reports/{date}_QA_G1_TEAM50.md` with **PASS** or an approved **CONDITIONAL PASS** (per that mandate’s scoring rules).

This mandate does **not** replace `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md`; it **narrows** Team 20’s current obligation to what is blocking the process **now**.

---

## 2. Mandatory environment (stack lock)

Team 50 **must** validate against:

| Requirement | Criterion |
|-------------|-----------|
| Python | **3.11.x or higher** on the validation host |
| PostgreSQL | **15.x or higher**, **direct install** on the validation host |
| Docker | **Not** used for the database Team 50 uses to record G1 evidence |

If Team 20 cannot meet direct install on a given machine, **document the blocker** in `_COMMUNICATION/TEAM_20/reports/` and coordinate an alternate **physical or VM host** where the stack lock is satisfied. “Docker-only Postgres” is **not** acceptable for G1 gate evidence per `_COMMUNICATION/ROADMAP.md` and `QA_MANDATE_G1.md`.

---

## 3. Deliverables (all required)

### 3.1 Handoff package for Team 50

Provide Team 50 (in writing — email, ticket, or a short report section) with:

1. **Exact** `python --version` and `psql --version` from the validation host.  
2. **Confirmation** that PostgreSQL is direct install (one sentence stating how verified, e.g. `brew list`, `apt`, service name — not a `postgres` Docker image).  
3. **`DATABASE_URL`** format and how Team 50 should set it (no secrets committed to git; use `.env` or secret store as per project norms).  
4. **`RAW_FILES_ROOT`** path Team 50 should use for any downstream G2 runs on the same machine (directory exists and is writable).  
5. **Clean DB bootstrap recipe** Team 50 can repeat: create empty database → `alembic upgrade head` → `python -m organic_market_agent.db.check` → **RESULT: PASS**.

### 3.2 Codebase parity

- Confirm **M1 Phase A** artifacts remain valid: migrations through head, `tests/test_db_health.py`, `python -m organic_market_agent.db.check`.  
- If anything in the repo **prevents** a clean `upgrade head` on a fresh database, **fix** it under Team 20’s scope (migrations, env template, docs) and reference the change in your report.

### 3.3 Written completion

File **one** dated report under `_COMMUNICATION/TEAM_20/reports/`:

`2026-03-30_or_later_G1_VALIDATION_ENV_READY_TEAM20.md` (or a later date in the filename)

The report **must** state explicitly:

- [ ] Handoff package delivered to Team 50 (how / when).  
- [ ] Stack lock satisfied (Python 3.11+, PostgreSQL 15+ direct).  
- [ ] Clean DB path verified by Team 20 (commands run + outcome).  
- [ ] No open Team 20 blockers for Team 50 to start `QA_MANDATE_G1.md` — or list blockers with owner and next step.

---

## 4. Out of scope (do not expand)

- **No** M2 feature work (collectors, parsers, `run_ingestion` logic).  
- **No** QA test execution for G1/G2 — that is **Team 50** only.  
- **No** rewriting of `QA_MANDATE_G1.md` / `QA_MANDATE_G2.md` — escalate to Team 100 if the mandate itself is wrong.

---

## 5. References

| Document | Purpose |
|----------|---------|
| `_COMMUNICATION/ROADMAP.md` | M1 / G1 acceptance criteria |
| `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md` | Full M1 implementation spec |
| `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` | Tests T01–T13 Team 50 will run |
| `_COMMUNICATION/TEAM_50/reports/2026-03-30_QA_G2_TEAM50.md` | Why G2 is blocked (no G1 sign-off) |
| `_COMMUNICATION/TEAM_20/reports/2026-03-30_G1_PHASEB_SUPPORT_REQUEST_TEAM10.md` | Prior Team 10 → Team 20 request (context) |

---

## 6. Acceptance (Project Lead)

This mandate is **done** when:

1. The Team 20 report in §3.3 is on file and checkboxes are satisfied or blockers are owned.  
2. Team 50 confirms they can start **T01** of `QA_MANDATE_G1.md` on the provided host without further Team 20 dependency (except bugfixes).
