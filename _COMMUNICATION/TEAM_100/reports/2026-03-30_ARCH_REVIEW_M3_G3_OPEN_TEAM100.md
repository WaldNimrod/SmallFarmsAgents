# Architecture Review — M3 Normalizer Engine + Seed Patch M1.1
**From:** Team 100 (Architecture)
**Date:** 2026-03-30
**Subject:** M3 implementation review; Seed Patch M1.1 verified; Gate G3 opened
**Status:** ✅ M3 PASS | ✅ Seed Patch PASS | 🟢 G3 OPEN

---

## Summary

Both Team 10 (M3 Normalizer Engine) and Team 20 (Seed Patch M1.1) have delivered.
Team 100 has reviewed the code, applied and verified the migrations, and run the full
test suite. Gate G3 is hereby **opened as PASS** (no conditional items).

---

## 1. Team 10 — M3 Normalizer Engine

### Deliverables Verified

| Item | Status |
|------|--------|
| `organic_market_agent/normalizer/context.py` — `NormContext` dataclass | ✅ |
| `normalizer/alias_resolver.py` | ✅ |
| `normalizer/organic_flag.py` | ✅ |
| `normalizer/price_parser.py` | ✅ |
| `normalizer/unit_resolver.py` — uses `NormalizerRule.match_pattern` | ✅ |
| `normalizer/quantity_parser.py` | ✅ |
| `normalizer/price_normalizer.py` | ✅ |
| `normalizer/basket_handler.py` | ✅ |
| `normalizer/confidence.py` | ✅ |
| `normalizer/engine.py` — `NormalizerEngine` with blocking-failure safety | ✅ |
| `normalizer/run_normalizer.py` — CLI entry point | ✅ |
| `organic_market_agent/__main__.py` — `run_normalizer` subcommand | ✅ |
| `run_ingestion.py` — `--normalize` flag added | ✅ |
| `tests/test_normalizer.py` — 18 tests (14 pure unit, 4 DB integration) | ✅ |

### Architecture Observations

**Positive:**
- 7-stage pipeline is fully modular; each stage is an isolated function.
  Adding or reordering stages requires only a change to the engine's pipeline list.
- Blocking failure model is correct: missing `product_id`, `price_amount`, or
  `display_unit_id` after all stages → row is discarded (no partial writes).
- `unit_resolver` correctly consults `NormalizerRule` table first, then the built-in
  map, then the product default. DB-driven rules take precedence.
- No circular imports — `normalizer/__init__.py` uses relative imports only.
- 4 DB integration tests gracefully skip on `OperationalError` — correct pattern.

**One note (non-blocking):**
- `test_normalizer_engine_resolves_one_row` skips even with DB running. This is
  because the test requires a `raw_extracted_item` with a name that maps to a known
  alias; no such fixture row exists yet. Acceptable at this stage — the skip is safe.
  Team 50 will exercise end-to-end normalization in G3 T02.

### Test Results (2026-03-30)

```
Platform: macOS, Python 3.11.15, pytest 8.4.2
DB: Docker oma-g2-ev (postgres:15-alpine), Alembic v007

tests/test_normalizer.py      — 17 passed, 1 skipped
tests/test_parsers.py         — 10 passed
tests/test_collectors.py      — 7 passed
tests/test_db_health.py       — 7 passed
─────────────────────────────────────────────────────
TOTAL: 44 passed, 1 skipped
```

**Verdict: PASS**

---

## 2. Team 20 — Seed Patch M1.1 (Migrations 006 + 007)

### Migration 006 — Alias coverage

```
alembic upgrade 005 → 006: PASS
```

Adds aliases for 13 previously uncovered products:
PRD012, PRD014–016, PRD018–024, PRD027, PRD028.
47 new alias rows. Idempotent (`ON CONFLICT DO NOTHING`).

Alias completeness check:
```sql
SELECT COUNT(*) FROM products p
LEFT JOIN product_aliases pa ON pa.product_id = p.id AND pa.is_active = true
WHERE pa.id IS NULL AND p.is_active = true;
-- Result: 0 rows ✅
```

### Migration 007 — Source profile fixes

```
alembic upgrade 006 → 007: PASS
```

| Source | Change | Verified |
|--------|--------|---------|
| SRC018–SRC020 | `normalizer_type` → `simple_product_grid` | ✅ |
| SRC015–SRC016 | `is_active = false`, `status = 'candidate'` | ✅ |
| SRC002, 004, 005, 006 | `selector_profile` JSONB populated | ✅ |

Source profile verification:
```
('SRC015', 'official_wholesale', False, False)   ✅
('SRC016', 'official_wholesale', False, False)   ✅
('SRC018', 'simple_product_grid', True, True)    ✅
('SRC019', 'simple_product_grid', True, True)    ✅
('SRC020', 'simple_product_grid', True, True)    ✅
```

`db.check` after upgrade: **PASS** (all 23 tables; 29 products, 20 sources, 11 units)

**Verdict: PASS** — both conditional items from G1/G2 are resolved.

---

## 3. Docker Migration (Environment Change)

Stack change applied this session:

- Homebrew `postgresql@15` removed (port conflict with other projects).
- PostgreSQL now served via Docker only (consistent with all other projects).
- `docker-compose.yml` created at repo root (`oma-postgres`, port 5433).
- `.env` updated to `oma-g2-ev` container (port 55435, has all G2+ data).
- All active mandates and onboarding docs updated to remove "no Docker" language.
- `tests/conftest.py` updated: loads `.env` first, falls back to docker-compose URL.

No data loss. DB health check: PASS.

---

## 4. Gate G3 Decision

### Conditional items from G1 and G2 — resolved

| ID | Item | Resolution |
|----|------|-----------|
| P1 (G1) | 13 products without aliases | ✅ Migration 006 applied |
| P2 (G1) | SRC018–020 normalizer_type mismatch | ✅ Migration 007 applied |
| P3 (G1) | SRC015–016 HTTP 403 | ✅ Migration 007 — deactivated |
| EasyFarm selectors (G2) | 0-row extraction | ✅ Migration 007 — selector_profile JSONB |

### Gate G3 — OPEN

**G3 is hereby opened. No conditional items.**

Team 50 may proceed with `QA_MANDATE_G3.md` immediately.

---

## 5. Next Steps

| Team | Action | Priority |
|------|--------|----------|
| **Team 50** | Execute `QA_MANDATE_G3.md` — 10 tests | Immediate |
| **Team 10** | Stand by; address any G3 failures | On-call |
| **Team 20** | Stand by for any migration corrections | On-call |

Active milestone after G3: **M4 — Aggregation + Local Viewer**

---

*Team 100 (Architecture) — 2026-03-30*
