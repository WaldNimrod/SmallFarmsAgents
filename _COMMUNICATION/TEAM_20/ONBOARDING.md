# ONBOARDING — צוות 20 (Infrastructure)
## פתיחת סשן — הנחיות לאיגנט

---

## זהות הצוות

**שם:** צוות 20 — Infrastructure  
**תפקיד:** סביבת פיתוח מקומית, PostgreSQL, Python project skeleton, Alembic migrations, SQLAlchemy models, seed data, utils.  
**לא מממש** collectors, parsers, normalizer, aggregator, admin UI — אלה שייכים לצוות 10.  
**כותב דוחות ל:** `_COMMUNICATION/TEAM_20/reports/`  
**מדווח ל:** נמרוד (משתמש).

---

## פעולות ראשונות בפתיחת כל סשן

1. קרא קובץ זה (`_COMMUNICATION/TEAM_20/ONBOARDING.md`) עד הסוף
2. קרא `_COMMUNICATION/ROADMAP.md` — מפת כל אבני הדרך
3. קרא `_COMMUNICATION/README.md` — מבנה gates ודרישות תקשורת
4. בדוק שלב נוכחי — קרא הדוחות האחרונים ב-`_COMMUNICATION/TEAM_20/reports/`
5. קרא מסמך M1: `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md`

---

## אחריות צוות 20 לפי milestone

| Milestone | אחריות |
|-----------|--------|
| M1 | **ליבה** — Python skeleton, PostgreSQL, Alembic, models, seed data, utils |
| M2 | תמיכה ל-Team 10: עזרה ב-DB queries, migration updates |
| M3–M5 | Alembic migrations נוספות שנדרשות, DB optimization |
| M6 | **ליבה** — cron job setup, log cleanup |
| M7 | **ליבה** — uPress FTP setup, environment config לפרודקשן |

---

## מסמכי הבסיס — לקריאה חובה לפני M1

| מסמך | נדרש לחלק |
|------|-----------|
| `docs/DATABASE_SCHEMA_SPEC_HE.md` | כל 23 הטבלאות, types, indexes |
| `docs/PRODUCT_CATALOG_V1.md` | 29 מוצרים, 11 יחידות, aliases |
| `docs/SOURCE_MAP_MASTER_HE.md` | 20 מקורות — seed data |
| `docs/ARCHITECTURE_DECISIONS_HE.md` | Python stack, PostgreSQL setup |
| `docs/DETAILED_SYSTEM_SPEC_HE.md` | מבנה הפרויקט (`smallfarms/`) |

---

## כללים קריטיים לצוות 20

| כלל | פירוט |
|-----|-------|
| Python 3.11+ | השתמש ב-`match`, `tomllib`, f-strings |
| SQLAlchemy 2.x | `session.execute(select(...))` — לא `session.query()` |
| TIMESTAMPTZ | **כל** timestamp = timezone-aware |
| NUMERIC(12,4) | **כל** ערך מספרי/כסף — לא float |
| alembic autogenerate OFF | כתוב migrations ידנית — לשליטה מלאה |
| Soft deletes | `is_active` בלבד — לא מוחקים רשומות |
| `.env` בלבד | אין hardcode של credentials בקוד |
| `.gitignore` | `.env`, `*.log`, `raw_files/`, `__pycache__/` |

---

## סביבת Python הנדרשת

```bash
# Python version
python3 --version  # >= 3.11

# venv
python3 -m venv .venv
source .venv/bin/activate

# install
pip install -r requirements.txt
```

---

## Gate G1 — אחריות צוות 20

כאשר M1 מושלם, הגש דוח ב-`_COMMUNICATION/TEAM_20/reports/` עם:
- אישור כל קריטריוני G1 (ראה ROADMAP.md)
- פלט של `python -m smallfarms.db.check`
- פלט של `pytest tests/test_db_health.py -v`
- בקשה לצוות 50 לפתוח שער G1

---

## כללי זהב לצוות 20

1. **אל תכתוב קוד feature** — רק infrastructure ו-skeleton
2. **Migrations = קוד** — כל migration נבדק הלוך ושוב (`upgrade` + `downgrade`)
3. **Seed data = tests** — כל seed מאומת ב-test
4. **ת'ד לפני קוד** — קרא MANDATE_M1_INFRASTRUCTURE.md לפני שכותב שורה
5. **דווח blockers** — אם PostgreSQL לא מותקן, לא ניגשים, כתוב דוח עם `[USER ACTION REQUIRED]`
