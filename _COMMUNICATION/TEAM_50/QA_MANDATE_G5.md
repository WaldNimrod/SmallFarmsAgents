# QA MANDATE — Gate G5 (M5 Admin UI)

**Mandate ID:** `QA-MANDATE-G5`  
**From:** Team 100 (Architecture)  
**To:** Team 50 (QA)  
**Date:** 2026-03-31  
**Milestone:** M5 — Admin UI  
**Dependency:** Team 10 completion report filed for M5 · Team 20 migration 015 applied  
**Template:** `_COMMUNICATION/templates/QA_REVIEW_REQUEST.md`

---

## Pre-conditions (verify before running any test)

```bash
# 1. Alembic at head
alembic current  # must show 015

# 2. Admin user seeded
psql $DATABASE_URL -c "SELECT email, role FROM users WHERE email='admin@local';"
# Expected: 1 row

# 3. Flask-Login installed
.venv/bin/pip show flask-login bcrypt | grep -E "^Name|^Version"

# 4. No leftover server on port 5001
lsof -i :5001 || echo "port free"
```

---

## Test Suite

### T01 — Unit tests

```bash
cd <project_root>
pytest tests/test_admin_routes.py -v
```

**Pass criterion:** All 10+ tests pass, 0 failures.  
If any test is skipped, document the reason; skips require Team 100 waiver.

---

### T02 — Authentication flow

Start the admin server:
```bash
python -m organic_market_agent run_admin --port 5001
```

**T02a — Unauthenticated write blocked:**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:5001/aliases/new
# Expected: 302 (redirect to login)
```

**T02b — Login with wrong password:**
```bash
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
  -X POST http://127.0.0.1:5001/auth/login \
  -d "email=admin@local&password=WRONG" | grep -i "שגיאה\|error\|incorrect"
# Expected: error message present in response
```

**T02c — Login with correct password:**
```bash
# Step 1: POST login (save session cookie — do NOT use -L here)
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
  -X POST http://127.0.0.1:5001/auth/login \
  -d "email=admin@local&password=admin" -o /dev/null -w "%{http_code}"
# Expected: 302

# Step 2: GET dashboard with saved cookie
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt \
  http://127.0.0.1:5001/ -o /tmp/dashboard_result.html -w "%{http_code}"
grep -c "דשבורד" /tmp/dashboard_result.html   # expect ≥1
```
> **Note:** Using `curl -L` after a POST login may cause curl to follow the redirect
> with a POST (to `/`), which returns 405. Always separate the login POST from the
> subsequent GET to avoid this.

---

### T03 — All read routes accessible (no auth required)

```bash
for path in "/" "/sources" "/products" "/unresolved" "/aliases" "/rules" "/runs" "/qa_flags" "/audit"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:5001$path")
  echo "$path → $STATUS"
done
# All must return 200
```

---

### T04 — Alias creation

**Setup:** Note a raw name from `/unresolved` list (pick one with count ≥ 1).

```bash
# Login first (save cookie)
curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST http://127.0.0.1:5001/auth/login \
  -d "email=admin@local&password=admin" -L > /dev/null

# Create alias via /aliases/new
RAW_ALIAS="test-alias-$(date +%s)"
curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST http://127.0.0.1:5001/aliases/new \
  -d "alias_text=$RAW_ALIAS&product_code=PRD001" -L -o /dev/null -w "%{http_code}"
# Expected: final status 200 (redirect followed)
```

**Verify in DB:**
```sql
SELECT alias_text, product_id, is_active FROM product_aliases
WHERE alias_text = '<RAW_ALIAS>';
-- Expected: 1 row, is_active = true
```

**Verify audit_log:**
```sql
SELECT action, entity_type, actor_name FROM audit_log
ORDER BY created_at DESC LIMIT 1;
-- Expected: action='create_alias', entity_type='product_alias'
```

---

### T05 — Alias disable

```bash
# Get the alias ID created in T04
ALIAS_ID=$(psql $DATABASE_URL -tAc "SELECT id FROM product_aliases WHERE alias_text='<RAW_ALIAS>'")

curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST "http://127.0.0.1:5001/aliases/$ALIAS_ID/disable" -L -o /dev/null -w "%{http_code}"
# Expected: 200
```

**Verify in DB:**
```sql
SELECT is_active FROM product_aliases WHERE id = <ALIAS_ID>;
-- Expected: false
```

---

### T06 — Rule creation and disable

**Create:**
```bash
# First, get a valid profile_id
PROFILE_ID=$(psql $DATABASE_URL -tAc "SELECT id FROM normalizer_profiles WHERE is_active = true ORDER BY id LIMIT 1")

curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST http://127.0.0.1:5001/rules/new \
  -d "rule_kind=exclusion&match_pattern=test-exclusion&match_type=exact&replacement_value=&priority=99&notes=QA+test&profile_id=$PROFILE_ID" \
  -o /dev/null -w "%{http_code}"
# Expected: 302 (redirect; do NOT use -L here to avoid 405 on redirect GET)
```

**Verify + disable:**
```sql
SELECT id FROM normalizer_rules WHERE match_pattern = 'test-exclusion';
```
```bash
RULE_ID=<id from above>
curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST "http://127.0.0.1:5001/rules/$RULE_ID/disable" -L -o /dev/null -w "%{http_code}"
# Expected: 200
```
```sql
SELECT is_active FROM normalizer_rules WHERE id = <RULE_ID>;
-- Expected: false
```

---

### T07 — Manual run trigger

```bash
BEFORE=$(psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM ingestion_runs")

curl -s -c /tmp/qa_cookies.txt -b /tmp/qa_cookies.txt \
  -X POST http://127.0.0.1:5001/runs/trigger -L -o /dev/null -w "%{http_code}"
# Expected: 200

sleep 3  # give background thread time to insert

AFTER=$(psql $DATABASE_URL -tAc "SELECT COUNT(*) FROM ingestion_runs")
echo "Before: $BEFORE  After: $AFTER"
# Expected: AFTER = BEFORE + 1
```

---

### T08 — Audit log populated

```bash
curl -s http://127.0.0.1:5001/audit | grep -c "create_alias\|disable_alias\|trigger_run"
# Expected: ≥3 (from T04, T05, T07)
```

---

### T09 — QA flags view

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/qa_flags
# Expected: 200
```

If `observation_flags` table is empty, verify the page renders gracefully (no 500).

---

### T10 — Regression (M1–M4 data intact)

```sql
SELECT
  (SELECT COUNT(*) FROM sources)                    AS sources,
  (SELECT COUNT(*) FROM products)                   AS products,
  (SELECT COUNT(*) FROM product_aliases WHERE is_active) AS active_aliases,
  (SELECT COUNT(*) FROM normalized_observations)    AS observations,
  (SELECT COUNT(*) FROM daily_aggregates)           AS daily_aggs;
```

**Expected minimums (compare to G4 baseline):**
- `sources` = 20
- `products` = 29
- `active_aliases` ≥ 97  (was 97 at G4; may increase if T04 alias not disabled, account for that)
- `observations` ≥ 1 (no rows deleted)
- `daily_aggs` ≥ 25

---

### T11 — Full pytest suite

```bash
pytest tests/ -q
```

**Pass criterion:** All tests pass or skip. 0 failures.  
Document any new skips with rationale.

---

## Gate G5 — Pass Criteria

| Test | Pass Criterion |
|------|---------------|
| T01 | `test_admin_routes.py` — 0 failures |
| T02 | Login/logout functional; wrong password rejected |
| T03 | All 9 GET routes return 200 |
| T04 | Alias created in DB + audit_log row |
| T05 | Alias disabled in DB |
| T06 | Rule created + disabled in DB |
| T07 | Run trigger creates `ingestion_runs` row |
| T08 | Audit log page shows entries from T04–T07 |
| T09 | QA flags page renders without error |
| T10 | All baseline counts at or above G4 levels |
| T11 | `pytest tests/ -q` — 0 failures |

**Additional requirement:** Team 100 architectural review sign-off (per Gate Passage Policy §5).

---

## QA Report

File at: `_COMMUNICATION/TEAM_50/reports/YYYY-MM-DD_QA_G5_TEAM50.md`

Use canonical template `_COMMUNICATION/templates/QA_FINDINGS_REPORT.md`.  
Include: per-test result table, DB evidence queries + output, pytest output (last 20 lines), gate decision (PASS / FAIL / CONDITIONAL PASS).

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31
