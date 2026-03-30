# M5 Admin UI — implementation complete (Team 10)

**Date:** 2026-03-31  
**Mandate:** `MANDATE-M5-ADMIN-UI-TEAM10`  
**Status:** Delivered for QA.

## Summary

- **Authentication:** Flask-Login + `bcrypt.checkpw` against `users.password_hash` (compatible with migration `015` seed `admin@local` / `admin`). `ADMIN_SECRET_KEY` env overrides default dev secret.
- **Audit:** `organic_market_agent/admin/audit.py` — `audit_write()` on all write paths; `AuditLog` from `models.users`.
- **Alias CRUD:** `/aliases`, `/aliases/new`, `POST /aliases/<id>/disable`; unresolved detail `POST .../add_alias`; product detail `POST /products/<code>/disable_alias/<id>`.
- **Rules CRUD:** `/rules`, `/rules/new`, `POST /rules/<id>/disable`. UI rule kinds map to DB CHECK: `price_multiplier` → `price_correction`, `exclusion` → `ignore_pattern` (plus direct keys `unit_map`, `organic_flag`, `product_alias`, etc.).
- **Runs:** `/runs`, `/runs/<id>`, `POST /runs/trigger` starts `threading.Thread(daemon=True)` → `organic_market_agent.scheduler.pipeline.run_pipeline(ingestion_run_id)` (collect/parse refactor `execute_ingestion_for_run` in `run_ingestion.py`, then normalizer, `AggregatorEngine` for UTC today, `PublishEngine` → `output/public`; `PublishAbortError` logged).
- **Read-only:** `/qa_flags`, `/audit`.
- **Templates:** RTL Bootstrap, nav per mandate; flashes in `base.html`.

## Dependencies

- `requirements.txt`: added explicit `bcrypt>=4.1.0` (alongside existing `flask-login`, `passlib[bcrypt]`).

## Tests

```bash
pip install -r requirements.txt   # ensures flask-login + bcrypt
python3 -m pytest tests/test_admin_routes.py -v
python3 -m pytest tests/ -q
```

- `tests/conftest.py`: `db_session`, `admin_app`, `client`, `logged_in_client`, `admin_login()`.
- `tests/test_admin_routes.py`: T01–T11 per mandate (T09 mocks `run_pipeline`).

## Security note

POST forms do **not** use Flask-WTF CSRF in this iteration; protection relies on session cookie + `@login_required`. Escalate to Team 100 if CSRF is required for production.

## Files touched (high level)

- New: `admin/auth.py`, `admin/audit.py`, `admin/routes/auth.py`, `aliases.py`, `rules.py`, `runs.py`, `qa_flags.py`, `audit_pages.py`, `scheduler/pipeline.py`, templates under `admin/templates/admin/`, `tests/test_admin_routes.py`.
- Edited: `admin/__init__.py`, `routes/products.py`, `routes/unresolved.py`, `scheduler/run_ingestion.py`, `requirements.txt`, `tests/conftest.py`.
