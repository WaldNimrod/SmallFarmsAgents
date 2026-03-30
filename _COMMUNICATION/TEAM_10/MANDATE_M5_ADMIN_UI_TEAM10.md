# MANDATE — M5 Admin UI Feature Dev (Team 10)

**Mandate ID:** `MANDATE-M5-ADMIN-UI-TEAM10`  
**From:** Team 100 (Architecture)  
**To:** Team 10 (Feature Dev)  
**Date:** 2026-03-31  
**Milestone:** M5 — Admin UI  
**Dependency:** Gate G4 ✅ PASS · Team 20 migration 015 applied  
**Template:** `_COMMUNICATION/templates/MANDATE.md`

---

## Context

M4 delivered a **read-only** admin dashboard (sources, products, unresolved, public report). M5 upgrades it to a **fully operational** management tool:

1. **Authentication** — local password login (bcrypt, session cookie). Every write route is protected.
2. **Alias CRUD** — create, edit, disable aliases directly from the UI.
3. **Rule CRUD** — manage normalizer rules (unit maps, price multipliers, organic flags).
4. **Manual run trigger** — start an ingestion+normalize+aggregate+publish cycle from the UI.
5. **QA flags view** — read-only list of flagged observations with flag details.
6. **Audit log view** — read-only trail of all write actions.
7. **Test suite** — `tests/test_admin_routes.py` (10+ tests).

### What is already complete (do NOT re-implement)

| Feature | Status |
|---------|--------|
| Flask app factory, blueprints registration | ✅ Done |
| Dashboard (KPIs) | ✅ Done |
| Sources list + detail | ✅ Done |
| Products list + detail | ✅ Done |
| Unresolved list + detail | ✅ Done |
| Bootstrap 5 RTL, Heebo font, Hebrew labels | ✅ Done |
| Public report redesign | ✅ Done |
| `docs/RTL_DEVELOPMENT_GUIDE.md` | ✅ Done |

---

## RTL Rule (mandatory for all new templates)

Read and follow `docs/RTL_DEVELOPMENT_GUIDE.md` before writing any HTML.  
Key rules: `bootstrap.rtl.min.css`, `dir="rtl" lang="he"`, CSS logical properties, `<span dir="ltr">` for numbers/codes.

---

## Task 1 — Authentication

### 1a — Dependencies

Add to `requirements.txt` if not present:
```
Flask-Login>=0.6.3
bcrypt>=4.1.0
```

### 1b — `organic_market_agent/admin/auth.py`

```python
from flask_login import LoginManager, UserMixin
from organic_market_agent.models.users import User as UserModel

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "יש להתחבר כדי לגשת לעמוד זה."

class AdminUser(UserMixin):
    def __init__(self, db_user):
        self.id = str(db_user.id)
        self.email = db_user.email
        self.display_name = db_user.display_name

@login_manager.user_loader
def load_user(user_id):
    # load from DB, return AdminUser or None
    ...
```

### 1c — `organic_market_agent/admin/routes/auth.py`

Blueprint `auth`, prefix `/auth`:

| Route | Method | Description |
|-------|--------|-------------|
| `/auth/login` | GET | Render Hebrew login form |
| `/auth/login` | POST | Verify password (bcrypt), set session, redirect to `/` |
| `/auth/logout` | GET | Clear session, redirect to login |

Login form fields: `email` (default `admin@local`), `password`. Show error in Hebrew on failure.

### 1d — Protect all write routes

- Import `login_required` from `flask_login`.
- Apply `@login_required` to every POST/PUT/DELETE route added in this mandate.
- Read-only GET routes (dashboard, sources, products, unresolved, product detail, source detail) **remain public** for now (M5 scope: only writes protected).

### 1e — Update `create_app()` in `organic_market_agent/admin/__init__.py`

```python
from organic_market_agent.admin.auth import login_manager
# inside create_app():
app.secret_key = os.environ.get("ADMIN_SECRET_KEY", "dev-secret-change-me")
login_manager.init_app(app)
app.register_blueprint(auth_bp)
```

### 1f — Login template `admin/login.html`

Full Hebrew, RTL. Show the brand header. Simple email+password form, submit button "כניסה". Error message block in red.

---

## Task 2 — Alias CRUD

### 2a — Enrich unresolved detail with "הוסף אליאס" action

In `organic_market_agent/admin/routes/unresolved.py`, add:

**`POST /unresolved/<raw_name>/add_alias`**

Request body (form): `product_code` (selected from a dropdown of all active products).

Logic:
```python
# 1. Look up product by code
# 2. Insert into product_aliases:
#    alias_text = raw_name
#    alias_text_normalized = raw_name.strip().lower()
#    product_id = product.id
#    source_id = NULL (global)
#    is_active = True
# 3. Write audit_log row: action='create_alias', entity_type='product_alias', entity_id=new_alias.id
# 4. Redirect to /unresolved/<raw_name> with flash "אליאס נוסף בהצלחה"
```

In `unresolved_detail.html`, add a form **below the alias suggestions section**:

```html
<form method="POST" action="/unresolved/.../add_alias">
  <select name="product_code">{% for p in all_products %}...{% endfor %}</select>
  <button type="submit">➕ הוסף אליאס</button>
</form>
```

Route must pass `all_products` list (code + canonical_name_he) to the template.

### 2b — Product detail alias management

In `organic_market_agent/admin/routes/products.py`, add:

**`POST /products/<code>/disable_alias/<alias_id>`**

Logic:
```python
# Set product_aliases.is_active = False WHERE id = alias_id AND product_id = product.id
# Write audit_log: action='disable_alias', entity_type='product_alias'
# Redirect to /products/<code> with flash
```

In `product_detail.html`, add a "השבת" (disable) button next to each active alias.

### 2c — Standalone alias list page

**`GET /aliases`** — list all active aliases (product, alias_text, scope/source, created_at).  
Each row: "השבת" button → `POST /aliases/<id>/disable`.  
**`GET /aliases/new`** — form to create alias: select product + enter alias text + optional source scope.  
**`POST /aliases/new`** — create + audit_log + redirect.

Template: `admin/aliases.html`, `admin/alias_new.html`.  
Add "אליאסים" to the navbar in `base.html`.

---

## Task 3 — Normalizer Rules CRUD

### 3a — Rules list

**`GET /rules`** — list all `normalizer_rules` rows grouped by `normalizer_profile_id`.

Columns: profile | kind | pattern | match_type | replacement | priority | active | notes | actions.

### 3b — Create rule

**`GET /rules/new`** — form: profile_id (dropdown), rule_kind (unit_map / organic_flag / price_multiplier / exclusion), match_pattern, match_type (exact/regex/contains), replacement_value, priority, notes.  
**`POST /rules/new`** → INSERT + audit_log + redirect to `/rules`.

### 3c — Disable rule

**`POST /rules/<id>/disable`** → set `is_active = False` + audit_log.

Templates: `admin/rules.html`, `admin/rule_new.html`.  
Add "כללים" to the navbar.

---

## Task 4 — Manual Run Trigger

### 4a — Run trigger route

In a new `organic_market_agent/admin/routes/runs.py`, add:

**`GET /runs`** — list last 20 `ingestion_runs` with status, started_at, finished_at, and per-run summary stats.

**`POST /runs/trigger`** (`@login_required`) — start a full pipeline cycle in a background thread:

```python
import threading
from organic_market_agent.scheduler.run_ingestion import run_pipeline

def trigger_run():
    # 1. Insert ingestion_runs row, get id
    # 2. In a daemon thread: run_pipeline(ingestion_run_id)
    # 3. audit_log: action='trigger_run'

threading.Thread(target=trigger_run, daemon=True).start()
# flash "הרצה הופעלה ברקע" and redirect to /runs
```

> **Important:** The trigger must not block the HTTP response. Use `threading.Thread(daemon=True)`. The run status is visible on `/runs` refresh.

### 4b — Run detail

**`GET /runs/<run_id>`** — show per-source stats for that run: source code, items extracted, resolved, unresolvable, errors.

Templates: `admin/runs.html`, `admin/run_detail.html`.  
Add "הרצות" to navbar.

---

## Task 5 — QA Flags View (read-only)

**`GET /qa_flags`** — list all `observation_flags` rows, most recent first (limit 200).

Columns: תאריך | מוצר | מקור | סוג דגל | סיבה | מחיר | סטטוס.

Link each row's product name to `/products/<code>` detail page.

Template: `admin/qa_flags.html`.  
Add "דגלי QA" to navbar.

---

## Task 6 — Audit Log View (read-only)

**`GET /audit`** — list last 200 `audit_log` rows.

Columns: תאריך | משתמש | פעולה | ישות | מזהה | לפני | אחרי.

Show `before_state` / `after_state` as collapsed JSON (use `<details><summary>JSON</summary>...</details>`).

Template: `admin/audit.html`.  
Add "יומן פעולות" to navbar.

---

## Task 7 — Helper: `audit_write()` utility

Create `organic_market_agent/admin/audit.py`:

```python
from flask_login import current_user
from sqlalchemy.orm import Session
from organic_market_agent.models.runs import AuditLog  # or wherever audit_log model is

def audit_write(
    session: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    before: dict | None = None,
    after: dict | None = None,
    notes: str | None = None,
) -> None:
    """Insert one audit_log row. Call after every admin write action."""
    user_id = int(current_user.id) if current_user.is_authenticated else None
    actor = current_user.display_name if current_user.is_authenticated else "system"
    session.add(AuditLog(
        user_id=user_id,
        actor_name=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before,
        after_state=after,
        notes=notes,
    ))
```

Use `audit_write()` in every POST handler that modifies data.

---

## Task 8 — Tests: `tests/test_admin_routes.py`

Minimum 10 tests using Flask test client (`app.test_client()`). No browser automation. Use the existing `db_session` fixture from `tests/conftest.py`.

Required tests:

| Test ID | Description |
|---------|-------------|
| T01 | All read-only GET routes return HTTP 200 (dashboard, sources, products, unresolved, aliases, rules, runs, qa_flags, audit) |
| T02 | `POST /auth/login` with correct credentials → session cookie set, redirect to `/` |
| T03 | `POST /auth/login` with wrong password → HTTP 200, error message in response |
| T04 | `POST /aliases/new` without login → redirect to login (401 or 302) |
| T05 | `POST /aliases/new` with login → alias created in DB + audit_log row inserted |
| T06 | `POST /aliases/<id>/disable` with login → `is_active = False` in DB |
| T07 | `POST /rules/new` with login → rule inserted in DB |
| T08 | `POST /rules/<id>/disable` with login → `is_active = False` in DB |
| T09 | `POST /runs/trigger` with login → `ingestion_runs` row created (do NOT wait for run to finish — just verify row exists) |
| T10 | `POST /products/<code>/disable_alias/<id>` with login → alias disabled + audit_log row |
| T11 | `GET /audit` returns 200 and contains at least the audit entries created in T05–T10 |

---

## File Map

```
organic_market_agent/admin/
├── __init__.py                          EDIT  (register new blueprints, login_manager)
├── auth.py                              NEW   (LoginManager, AdminUser, user_loader)
├── audit.py                             NEW   (audit_write helper)
├── routes/
│   ├── auth.py                          NEW   (login/logout)
│   ├── aliases.py                       NEW   (list, new, disable, add_from_unresolved)
│   ├── rules.py                         NEW   (list, new, disable)
│   ├── runs.py                          NEW   (list, trigger, detail)
│   ├── qa_flags.py                      NEW   (list — read-only)
│   ├── audit.py                         NEW   (list — read-only)
│   ├── unresolved.py                    EDIT  (add POST add_alias + all_products to detail)
│   └── products.py                      EDIT  (add POST disable_alias)
└── templates/admin/
    ├── base.html                        EDIT  (add new nav items, login status)
    ├── login.html                       NEW
    ├── aliases.html                     NEW
    ├── alias_new.html                   NEW
    ├── rules.html                       NEW
    ├── rule_new.html                    NEW
    ├── runs.html                        NEW
    ├── run_detail.html                  NEW
    ├── qa_flags.html                    NEW
    └── audit.html                       NEW

tests/
└── test_admin_routes.py                 NEW   (10+ tests)

requirements.txt                         EDIT  (Flask-Login, bcrypt)
```

---

## Navigation bar — final state after M5

```
🌿 MyFarmAgents  |  דשבורד  |  מקורות  |  מוצרים  |  לא מזוהים  |  אליאסים  |  כללים  |  הרצות  |  דגלי QA  |  יומן פעולות  |  [שם משתמש ▸ יציאה]
```

---

## Out of scope for M5

- uPress FTPS publishing (M7)
- Email alerting (M6)
- Cron scheduling (M6)
- Product / source creation from UI
- Unit conversion calculator
- Any DB schema structural changes (Team 20 only)

---

## Implementation Order

```
Task 7 (audit_write helper)
  └─► Task 1 (auth)
        └─► Task 2 (alias CRUD)
        └─► Task 3 (rules CRUD)
        └─► Task 4 (run trigger)
        └─► Task 5 (qa_flags — no auth needed)
        └─► Task 6 (audit log — no auth needed)
              └─► Task 8 (tests — after all routes exist)
```

Tasks 2–6 are independent of each other once auth is in place.

---

**Signed:** Team 100 — Architecture  
**Date:** 2026-03-31
