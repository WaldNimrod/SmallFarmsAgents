# Team 20 — G1 validation environment ready (Phase B / gate unblock)

**Date:** 2026-03-30  
**From:** Team 20 (Infrastructure)  
**To:** Team 50 (QA), Team 100 (Architecture), Project Lead  
**Mandate:** `_COMMUNICATION/TEAM_20/MANDATE_G1_GATE_UNBLOCK_TEAM20.md`

---

## Purpose

This report is the **§3.3 written completion** and **§3.1 handoff package** so Team 50 can run `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` (T01–T13) on a **stack-locked** host: **Python 3.11+**, **PostgreSQL 15+ direct install** (not Docker for the database used as G1 evidence).

---

## 3.1 Handoff package for Team 50

### 1) Exact interpreter and client versions (validation host)

Captured on the machine used for this verification (macOS, Apple Silicon):

```text
/opt/homebrew/bin/python3.11 --version
Python 3.11.15
```

```text
/opt/homebrew/opt/postgresql@15/bin/psql --version
psql (PostgreSQL) 15.17 (Homebrew)
```

**Team 50:** Use **Python 3.11.x or newer** for all G1 commands (`pytest`, `pip`, `python -m …`). A dedicated venv is recommended (see bootstrap below).

### 2) Confirmation — PostgreSQL is a direct local install

PostgreSQL **15.17** was installed with **Homebrew** (`postgresql@15` keg under `/opt/homebrew/Cellar/postgresql@15/15.17/…`) and started with **`brew services start postgresql@15`**. The `psql` binary used for evidence is **`/opt/homebrew/opt/postgresql@15/bin/psql`** — this is **not** a Docker image.

**Note for T01 / QA mandate:** Other unrelated containers on the same workstation may list `postgres` images in `docker ps`. **G1 evidence must use only** the database reached via **`DATABASE_URL` below** (Homebrew server on the host, typically TCP `127.0.0.1:5432`). Do not point `DATABASE_URL` at a Docker-mapped port for G1 sign-off.

### 3) `DATABASE_URL` format and setup

- **Format:** `postgresql://smallfarms_app@127.0.0.1/smallfarms_local` (or `@localhost` if peer/trust matches your install).  
- **Secrets:** Keep credentials in **`.env`** at the repo root (never commit). Copy from [`.env.example`](../../../.env.example) and adjust paths.  
- **Role/database:** On the validation host, Team 20 created role `smallfarms_app` and database `smallfarms_local` owned by that role, with grants on `public` per M1 mandate §0.2. **Team 50** should either reuse the same DB after a fresh `downgrade base` or recreate an empty DB and run `alembic upgrade head` per the bootstrap recipe.

### 4) `RAW_FILES_ROOT`

- **Recommended (repo-relative):** `/Users/nimrod/Documents/SmallFarmsAgents/raw_files` (as in `.env.example`).  
- Ensure the directory exists and is writable:

```bash
mkdir -p /Users/nimrod/Documents/SmallFarmsAgents/raw_files/artifacts
```

(Config loader will also create roots when `config.ensure_dirs()` is used; G1 tests do not require pre-filled raw files.)

### 5) Clean DB bootstrap recipe (repeatable)

From the repo root (`SmallFarmsAgents`), with **Homebrew PostgreSQL 15** running and **Python 3.11+**:

```bash
# 0) PATH for Homebrew PostgreSQL 15 (add to ~/.zshrc if needed)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# 1) One-time DB + role (if not already present) — see MANDATE_M1_INFRASTRUCTURE.md §0.2
#    Example: create role smallfarms_app LOGIN; create database smallfarms_local OWNER smallfarms_app; GRANTs on public.

# 2) Python venv (3.11+)
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 3) Environment
cp .env.example .env
# Edit .env: set DATABASE_URL and RAW_FILES_ROOT

export DATABASE_URL="postgresql://smallfarms_app@127.0.0.1/smallfarms_local"

# 4) Migrations + health
alembic upgrade head
python -m organic_market_agent.db.check
# Expect: RESULT: PASS

# 5) Unit tests (T01)
pytest tests/test_db_health.py -v
# Expect: 7 passed

# 6) Optional but recommended before G1 (T03 round-trip)
alembic downgrade base
alembic upgrade head
python -m organic_market_agent.db.check
```

**Team 20 verification (commands run + outcome):**

| Step | Result |
|------|--------|
| `alembic upgrade head` (clean DB) | OK |
| `python -m organic_market_agent.db.check` | `RESULT: PASS` |
| `alembic downgrade base` && `alembic upgrade head` | OK |
| `pytest tests/test_db_health.py -v` (Python 3.11.15) | **7 passed** |

---

## Codebase parity fix (Team 20)

- **`pip install -e .` failed** with `build-backend = setuptools.backends.legacy:build` (pip could not import `setuptools.backends.legacy`).  
- **Change:** [`pyproject.toml`](../../../pyproject.toml) now uses `build-backend = "setuptools.build_meta"` so editable installs work with current pip/setuptools.  
- **Note for Team 100:** If the written M1 mandate still requires the legacy backend string, reconcile spec vs tooling; `build_meta` is the supported path for `pip install -e .` here.

---

## 3.3 Completion checklist (mandate §3.3)

- [x] **Handoff package delivered to Team 50** — This file is the written handoff (path: `_COMMUNICATION/TEAM_20/reports/2026-03-30_G1_VALIDATION_ENV_READY_TEAM20.md`). **How/when:** filed in-repo on 2026-03-30; notify Team 50 / Project Lead to start **T01** of `QA_MANDATE_G1.md`.  
- [x] **Stack lock satisfied** on the validation host used above: Python **3.11.15**, PostgreSQL **15.17 (Homebrew)**, direct install.  
- [x] **Clean DB path verified by Team 20** — see table in §3.1 item 5.  
- [x] **No open Team 20 blockers** for Team 50 to start `QA_MANDATE_G1.md` on a host with the same stack — or: if another machine lacks Homebrew Postgres / Python 3.11, repeat §0 of M1 mandate and this bootstrap there.

---

## References

| Document | Path |
|----------|------|
| Gate unblock mandate | `_COMMUNICATION/TEAM_20/MANDATE_G1_GATE_UNBLOCK_TEAM20.md` |
| G1 QA procedure | `_COMMUNICATION/TEAM_50/QA_MANDATE_G1.md` |
| M1 implementation spec | `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md` |

---

## Acceptance note (mandate §6)

Item **(2)** (“Team 50 confirms they can start T01…”) requires **Team 50** acknowledgment after they read this handoff — out of Team 20’s control once this report is filed.
