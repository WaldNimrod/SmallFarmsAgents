# SmallFarms — Roadmap ותוכנית פיתוח
**גרסה:** 1.0  
**תאריך:** 2026-03-29  
**מאת:** צוות 100 (ארכיטקטורה)  
**שלב פעיל:** M1 — Local Foundation  
**Reference ראשי לתהליך הפיתוח — קרא לפני כל סשן**

---

## מפת צוותות

| צוות | שם | תפקיד | מנדט נוכחי |
|------|-----|--------|------------|
| **Team 100** | ארכיטקטורה | אדריכל, בעלים על ספק, בחינת פלטים | review מתמשך |
| **Team 50** | QA | ולידציה מול spec, פתיחת gates | בדיקת G1 עם סיום M1 |
| **Team 20** | Infrastructure | סביבה, DB, skeleton | **M1 — פעיל** |
| **Team 10** | Feature Dev | Collectors, parsers, normalizer, aggregator, admin | ממתין לG1 |

---

## ציר הזמן — 7 אבני דרך

```
M1 ──► M2 ──► M3 ──► M4 ──► M5 ──► M6 ──► M7
 DB   Collect  Norm   Agg   Admin  Automate  Go-Live
Team20 Team10 Team10 Team10 Team10  Team10   Team10+20
```

---

## M1 — Local Foundation (תשתית מקומית)
**צוות מבצע:** Team 20 (Infrastructure)  
**מנדט:** `_COMMUNICATION/TEAM_20/MANDATE_M1_INFRASTRUCTURE.md`  
**שלב נוכחי:** פעיל

### תוצרים
- Python project skeleton (`smallfarms/` package, כל submodules)
- `requirements.txt` מלא
- PostgreSQL מותקן ומוגדר מקומית
- Alembic migrations (5 revisions: schema + 4 seed revisions)
- כל 23 טבלאות + 2 views
- SQLAlchemy 2.x models לכל הטבלאות
- Seed data: 11 יחידות מידה, 4 המרות, 29 מוצרים, 20 מקורות, aliases ראשוניים
- `smallfarms/utils/`: logging, config, checksum, db_check
- `smallfarms/db/`: session factory, engine factory
- CLI: `python -m smallfarms.db.check`

### Gate G1 — קריטריוני קבלה
- [ ] `python -m smallfarms.db.check` — מדווח PASS לכל 23 טבלאות
- [ ] `alembic upgrade head` — רץ ללא שגיאות על DB ריק
- [ ] `alembic downgrade base` + `alembic upgrade head` — הלוך ושוב ללא שגיאות
- [ ] כל 29 מוצרים בDB, כל 20 מקורות, כל 11 יחידות
- [ ] `from smallfarms.models import *` — ייבוא ללא שגיאות
- [ ] `pytest tests/test_db_health.py` — PASS
- [ ] Team 50 sign-off על G1

---

## M2 — Collection Layer (שכבת איסוף)
**צוות מבצע:** Team 10 (Feature Dev)  
**תלויות:** G1 חייב להיות פתוח  
**מנדט:** יוכן לאחר פתיחת G1

### תוצרים
- `CollectorEngine` framework: retry, timeout, checksum dedup
- 3 collectors ראשוניים:
  - `EasyFarmCollector` (generic, לSRC002–SRC006)
  - `StandaloneHTMLCollector` (לSRC008, SRC009)
  - `GovtBenchmarkCollector` (לSRC015)
- `ParserEngine` dispatcher
- 3 parsers: `EasyFarmCatalogParser`, `SimpleProductGridParser`, `OfficialWholesaleParser`
- raw_assets שמורים לfilesystem + metadata בDB
- raw_extracted_items מאוכלסת

### Gate G2 — קריטריוני קבלה
- [ ] 3+ מקורות נאספים בהצלחה
- [ ] raw_extracted_items מאוכלסת עם ≥50 פריטים
- [ ] checksum dedup עובד (הרצה כפולה = אפס רשומות חדשות)
- [ ] retry logic עובד (מקור לא זמין → retry → log)
- [ ] `pytest tests/test_collectors.py tests/test_parsers.py` — PASS
- [ ] Team 50 sign-off על G2

---

## M3 — Normalizer Engine (מנוע נרמול)
**צוות מבצע:** Team 10  
**תלויות:** G2 חייב להיות פתוח  
**מנדט:** יוכן לאחר פתיחת G2

### תוצרים
- `NormalizerEngine` עם 7 שלבים (ראה `NORMALIZER_SPEC_HE.md`)
- `alias_resolver.py` — DB-driven alias lookup
- `unit_resolver.py` — המרות יחידות מDB
- `price_resolver.py` — נרמול מחיר לk"g
- `confidence.py` — חישוב confidence score
- normalized_observations מאוכלסת
- Admin endpoint בסיסי לניהול aliases (CRUD)

### Gate G3 — קריטריוני קבלה
- [ ] normalized_observations מאוכלסת עם ≥40 תצפיות תקינות
- [ ] alias resolution עובד מDB (שינוי alias ב-DB = שינוי ב-normalization)
- [ ] confidence scores בטווח 0–1 עבור כל תצפית
- [ ] מוצרי basket מסומנים `is_basket_product=true` ואינם מקבלים `normalized_price_value`
- [ ] `pytest tests/test_normalizer.py` — PASS
- [ ] Team 50 sign-off על G3

---

## M4 — Aggregation + Local Viewer (דוח מקומי)
**צוות מבצע:** Team 10  
**תלויות:** G3 חייב להיות פתוח  
**מנדט:** יוכן לאחר פתיחת G3

### תוצרים
- `AggregatorEngine`: daily_aggregates, weekly_snapshots
- `QAEngine`: outlier detection, missing source alerts, duplicate detection
- `PublishEngine` (local only — ללא FTPS):
  - בונה `public_report.json` לתיקיה מקומית
  - בונה `public_report.html` עם Jinja2 template
  - בונה `manifest.json`
- Local viewer: Python `http.server` על `localhost:8080`
- staleness_level מחושב ב-manifest

### Gate G4 — קריטריוני קבלה
- [ ] `daily_aggregates` מאוכלסת לאחר ריצה
- [ ] `meets_publish_threshold=true` לפחות ל-5 מוצרים
- [ ] `public_report.json` תקין (schema validation)
- [ ] `public_report.html` נטען ב-`localhost:8080` ומציג נתונים
- [ ] `manifest.json` כולל `staleness_level` נכון
- [ ] QA flags מסומנים על תצפיות חריגות
- [ ] `pytest tests/test_aggregator.py tests/test_publisher_local.py` — PASS
- [ ] Team 50 sign-off על G4

---

## M5 — Admin UI (ממשק ניהול)
**צוות מבצע:** Team 10  
**תלויות:** G4 חייב להיות פתוח  
**מנדט:** יוכן לאחר פתיחת G4

### תוצרים
- Flask app factory + auth (phase A: ללא auth; phase B: local password)
- Blueprints: dashboard, sources, runs, observations, qa, publish, normalizer
- מסכים: ראה `INTERFACE_MOCKUPS_HE.md` (admin sections)
- Normalizer management panel: CRUD מלא לaliases, rules, merges, flags
- Trigger manual ingestion run מה-UI

### Gate G5 — קריטריוני קבלה
- [ ] כל 7 blueprints עובדים
- [ ] Normalizer management: CRUD מלא ל-aliases/rules/merges/flags
- [ ] שינוי alias ב-UI → validation שהנרמול השתנה
- [ ] Manual run trigger → run רץ ועדכון בUI
- [ ] Team 100 architectural review → approval
- [ ] Team 50 sign-off על G5

---

## M6 — Automation + Resilience (אוטומציה)
**צוות מבצע:** Team 10 + Team 20 (cron setup)  
**תלויות:** G5 חייב להיות פתוח  
**מנדט:** יוכן לאחר פתיחת G5

### תוצרים
- cron job: `0 6 * * * python -m smallfarms.scheduler.runner`
- Email alerting (SMTP): ingestion failure, partial run, stale data (3d + 8d)
- Retry logic מלא + error recovery
- log_entries auto-cleanup (90 ימים)

### Gate G6 — קריטריוני קבלה
- [ ] cron מוגדר ורץ 7 ימים ללא מגע יד אדם
- [ ] email alert נשלח בכשל ingestion (בדיקת failover מלאכותי)
- [ ] staleness warning נשלח אחרי 3 ימים ללא עדכון
- [ ] retry logic עובד לפחות 2 ניסיונות לפני כשל
- [ ] Team 50 full integration sign-off על G6

---

## M7 — Public Publishing / Go-Live (עלייה לאוויר)
**צוות מבצע:** Team 10 + Team 20  
**תלויות:** G6 חייב להיות פתוח + אישור משתמש (נמרוד)  
**מנדט:** `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md` (נדחה לשלב זה)

### תוצרים
- uPress FTP validation (Tests U01–U12 מהמנדט הנדחה)
- PublishEngine: FTPS upload + manifest atomicity
- manifest_last_good.json fallback
- WordPress rendering integration (template/block)
- Stale data banners (3 ימים / 8 ימים)

### Gate G7 — קריטריוני קבלה
- [ ] U01–U07 עוברים (FTP/FTPS + write + public access)
- [ ] publish pipeline אוטומטי מריץ end-to-end
- [ ] WordPress מציג נתונים חיים
- [ ] stale banners מוצגים נכון
- [ ] אישור ידני מנמרוד → LIVE

---

## מדיניות מעבר gates

1. **צוות 10/20 מגיש** דוח לתיקיית reports שלו עם בקשת gate
2. **צוות 50 בודק** ומאשר/חוסם ב-reports שלו
3. **גייט לא נפתח** ללא אישור כתוב של צוות 50
4. **G5 וG7** דורשים גם אישור ידני של צוות 100 או נמרוד

---

## reference לקריאה נוספת

- `docs/DATABASE_SCHEMA_SPEC_HE.md` — 23 טבלאות + views
- `docs/PIPELINE_ALGORITHMS_HE.md` — אלגוריתמי כל שלב
- `docs/NORMALIZER_SPEC_HE.md` — 7 שלבי normalizer
- `docs/ARCHITECTURE_DECISIONS_HE.md` — החלטות נעולות
- `docs/PRODUCT_CATALOG_V1.md` — 29 מוצרים + aliases
- `docs/SOURCE_MAP_MASTER_HE.md` — 20 מקורות
