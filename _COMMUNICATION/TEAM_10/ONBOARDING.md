# ONBOARDING — צוות 10 (אימפלמנטציה)
## פתיחת סשן — הנחיות לאיגנט

---

## זהות הצוות

**שם:** צוות 10 — אימפלמנטציה  
**תפקיד:** ממש את מערכת SmallFarms בדיוק לפי האפיון. קרא את הספק לפני שאתה כותב שורת קוד. שאל לפני שאתה סוטה מהאפיון.  
**כותב דוחות ל:** `_COMMUNICATION/TEAM_10/reports/`  
**מדווח ל:** נמרוד (משתמש).  
**שאלות ארכיטקטורה → קרא את האפיון ב-`docs/`, אם עדיין לא ברור — כתוב ב-`_COMMUNICATION/TEAM_100/reports/`**

---

## פעולות ראשונות בפתיחת כל סשן

1. קרא קובץ זה (`_COMMUNICATION/TEAM_10/ONBOARDING.md`) עד הסוף
2. קרא `_COMMUNICATION/README.md` — מבנה שערי האישור
3. בדוק מה השלב הנוכחי — בדוק אילו שערים G0–G6 נפתחו:
   - חפש אישורים בדוחות `_COMMUNICATION/TEAM_50/reports/`
4. קרא את מסמך האפיון הרלוונטי לשלב הנוכחי (ראה טבלה למטה)
5. **לא מתחילים לכתוב קוד לפני שקראת את האפיון**

**המשימה הראשונה שלך:** ראה `_COMMUNICATION/TEAM_10/MANDATE_UPRESS_VALIDATION.md`

---

## מסמכי האפיון לפי שלב — `docs/`

| שלב | שערים | מסמכים לקריאה |
|-----|--------|----------------|
| uPress validation | G0 | `UPRESS_VALIDATION_PLAN_HE.md` |
| DB setup | G1 | `DATABASE_SCHEMA_SPEC_HE.md`, `ARCHITECTURE_DECISIONS_HE.md` |
| Collectors | G2 | `SOURCE_MAP_MASTER_HE.md`, `PIPELINE_ALGORITHMS_HE.md` |
| Parsers | G2 | `PIPELINE_ALGORITHMS_HE.md`, `PRODUCT_CATALOG_V1.md` |
| Normalizer | G3 | `NORMALIZER_SPEC_HE.md`, `DATABASE_SCHEMA_SPEC_HE.md` |
| Aggregator | G4 | `PIPELINE_ALGORITHMS_HE.md`, `DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` |
| Publisher | G4 | `PIPELINE_ALGORITHMS_HE.md`, `UPRESS_VALIDATION_PLAN_HE.md` |
| Admin UI | G5 | `INTERFACE_MOCKUPS_HE.md`, `DETAILED_SYSTEM_SPEC_HE.md` |
| Integration | G6 | כל המסמכים |

---

## Stack הפרויקט (נעול)

```
Python 3.11+
Flask 3.x         — Admin UI בלבד (127.0.0.1:5000)
PostgreSQL 15+    — התקנה ישירה (ללא Docker)
SQLAlchemy 2.x    — ORM (לא legacy session.query())
Alembic           — migrations
httpx             — HTTP async
BeautifulSoup4    — HTML parsing
cron              — תזמון יומי (06:00)
ftplib / ftputil  — FTPS upload
```

---

## מבנה הפרויקט הנדרש

```
smallfarms/
  collectors/       # קובץ אחד לכל מקור
  parsers/          # parser class לכל normalizer_type
  normalizer/       # NormalizerEngine + DB rules
  aggregator/       # AggregatorEngine + QAEngine
  publisher/        # PublishEngine + FTPSClient
  admin/            # Flask blueprints
  models/           # SQLAlchemy ORM (קובץ לכל קבוצת טבלאות)
  db/               # session factory + Alembic env
  scheduler/        # cron wrapper + IngestionRunner
  utils/            # logging, email alert, checksum
  tests/            # mirrors src structure
```

---

## כללים קריטיים לכתיבת קוד

| כלל | פירוט |
|-----|-------|
| **אסור float לכספים** | השתמש ב-`Decimal` / `NUMERIC(12,4)` בלבד |
| **אסור hardcode שמות מוצרים** | כולם מ-DB |
| **אסור session.query()** | SQLAlchemy 2.x style בלבד |
| **חובה TIMESTAMPTZ** | כל timestamp חייב timezone |
| **חובה log_entries** | כל שגיאה מתועדת |
| **חובה audit_log** | כל פעולת admin מתועדת |
| **הנורמליזר מ-DB** | כללים/aliases נטענים מ-DB, לא hardcoded |
| **אין region בV1** | הוסר מהאפיון |

---

## סדר ביצוע (Gates)

```
G0: uPress FTP validation          ← FIRST — אל תתחיל עד שנמרוד מאשר הגישה
G1: PostgreSQL schema + Alembic    ← DB מוכן
G2: Collectors + parsers           ← 3+ מקורות עובדים
G3: Normalizer engine              ← data-driven, DB aliases
G4: Aggregator + publish           ← FTPS + manifest
G5: Admin UI                       ← Flask admin
G6: Integration test               ← end-to-end
```

**כל שלב טעון אישור צוות 50 (QA) לפני שממשיכים.**

---

## תבנית דוח אימפלמנטציה

```markdown
# Team 10 — [נושא הדוח / שם השלב]
**תאריך:** YYYY-MM-DD  
**שלב:** G[מספר]  
**סטטוס:** ✅ הושלם / 🔄 בביצוע / ❌ חסום

## מה בוצע
[תיאור קצר של מה שנעשה]

## פלט / תוצרים
[קבצים שנוצרו, פונקציות שנכתבו]

## בדיקות שרצו
[בדיקות ידניות/אוטומטיות שרצו וצלחו]

## חריגות מהאפיון (אם קיימות)
[תאר כל סטייה מהאפיון — חייב אישור צוות 100]

## בלוקרים
[מה חוסם התקדמות]

## [USER ACTION REQUIRED] (אם רלוונטי)
[מה נמרוד צריך לעשות — credentials, WordPress config, וכו']

## בקשה לפתיחת שער G[מספר]
[בקשה רשמית לצוות 50 לבדוק ולאשר]
```

---

## כללי זהב לצוות 10

1. **קרא את האפיון לפני שאתה מקודד** — כל פעם
2. **שאל לפני שאתה מחליט** — כל ספק → כתוב דוח, שאל צוות 100
3. **אל תעבור שער ללא אישור** — QA (צוות 50) חייב לאשר
4. **תעד blockers מיד** — במיוחד כשצריך action מנמרוד (credentials, וכו')
5. **כתוב tests** — לכל פונקציה קריטית יש unit test ב-`tests/`
6. **Atomic commits** — commit אחד לכל feature/fix
