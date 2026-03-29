# תקציר מנהלים

גרסה: 1.1  
תאריך: 2026-03-29  
שינויים מגרסה 1.0: stack Python/Flask/PostgreSQL, basket policy, stale data policy, uPress כשלב מקדים, normalizer data-driven

## מטרת המסמך

מסמך זה הוא נקודת הכניסה הרשמית ללימוד האפיון של הפרויקט עבור:

- לקוח
- צוות בחינה חיצוני
- שותפים טכניים
- גורמי אישור

המטרה שלו היא לתת תמונה מהירה, מדויקת וברורה של:

- מהו הפרויקט
- מה הבעיה שהוא פותר
- איך המערכת תעבוד
- אילו החלטות אדריכליות כבר התקבלו
- אילו מסמכי עומק מלווים את האפיון

## הרעיון והקונספט

הפרויקט נועד להקים שירות קהילתי חינמי עבור קהילת החקלאים האורגניים והאקולוגיים בישראל.

הפיצ'ר הראשון של המערכת הוא מחירון שוק לירקות אורגניים, עם מיקוד ברור בשוק מאוד מסוים:

- חוות קטנות
- שיווק ישיר
- סלים
- CSA
- שווקי איכרים
- חנויות בחווה

המערכת לא מנסה לייצר "מחיר אמת" ממקור אחד, אלא מבצעת אגרגציה של מקורות רבים וחלקיים.

בנוסף, מוצגים גם מחירי benchmark מרשתות גדולות וממקורות כלליים, אך בנפרד ובאופן שלא מתערבב עם מדד השוק הקהילתי.

## תיאור כללי של המערכת

המערכת בנויה משני חלקים:

### 1. מערכת מקומית

מערכת מקומית מריצה:

- איסוף נתונים
- שמירת raw
- parsing
- normalization
- אגרגציה
- ניטור
- publish

במערכת המקומית נשמר כל המידע המלא, והיא ה-`system of record`.

### 2. ממשק ציבורי באתר `nimrod.bio`

האתר הציבורי יציג רק נתונים מאוגדים.

הוא לא יציג:

- מקורות ספציפיים
- raw data
- diagnostics
- מידע פנימי תפעולי

האתר הציבורי יחיה בתוך סביבת הוורדפרס הקיימת, אך לא יישען על בסיס הנתונים של וורדפרס כמערכת הרשומה.

## עקרונות יסוד

- פשטות קודם
- שכבת ניהול מקומית בלבד
- שמירה מלאה של raw והיסטוריה
- הפרדה בין שוק קהילתי לבין benchmark
- הפרדה בין data internals לבין public presentation
- publish אוטומטי יומי ללא התערבות אנושית
- fallback ל-`last known good`
- normalizer גמיש data-driven — שינוי rules ללא deploy

## החלטות אדריכליות מרכזיות

### stack טכנולוגי

- שפת פיתוח: **Python 3.11+**
- ממשק admin מקומי: **Flask** (Python)
- ORM: **SQLAlchemy 2.x**
- Migrations: **Alembic**
- HTTP scraping: **httpx + BeautifulSoup4**
- Scheduler: **cron** (מערכת הפעלה)

### architecture

- המערכת תיבנה כ-`Local Data Hub + Public WordPress Surface`
- וורדפרס הוא `presentation layer`, לא `system of record`
- agents מפתחים — מבנה קוד מודולרי שמאפשר עבודה מקבילה

### local storage

- בסיס הנתונים המקומי: **PostgreSQL** (ישירות על המכשיר, ללא Docker)
- raw files ו-artifacts נשמרים על filesystem

### normalizer

- מנגנון normalizer הוא **data-driven לחלוטין** — כל rules, aliases, merges ו-flags נשמרים ב-DB
- admin/agent משנה rules בלי deploy
- תוצאה: פחות עבודה ידנית לאורך זמן, שיפור עקבי של הנרמול

### basket policy

- סלים ו-CSA הם **מוצרים עצמאיים** (סל קטן, סל בינוני, סל גדול, סל משפחתי)
- הם מוצגים בממשק הציבורי בשכבה נפרדת "סלים ו-CSA"
- הם אינם מחושבים ב-aggregation לפי מחיר ק"ג
- פירוק לפריטים בגרסה עתידית

### local admin

- ממשק admin מקומי הוא חובה מיום ראשון
- admin V1 מיועד לניטור, לוגים, QA, הרצת תהליכים ידנית, **וניהול normalizer rules**
- ממשק admin הוא מרכז הניטור הבלעדי — לא הציבורי

### online publish

- האונליין ישתמש ב:
  - `manifest.json`
  - `public_report-{version}.json`
  - `public_report-{version}.html`
- אין שימוש ב-DB של WordPress לאחסון נתוני המערכת
- WordPress מציג HTML artifact עם JavaScript מוטמע minimal

### publish transport

- המסלול המועדף הוא upload אוטומטי ב-FTPS
- **בדיקת uPress (U01–U12) היא שלב מקדים חובה לפני כל פיתוח**
- אם ניסוי FTP נכשל — פנייה לתמיכת uPress

### stale data policy

```
published_at < 3 ימים    →  תצוגה רגילה
published_at 3-8 ימים    →  banner צהוב: "המידע לא עודכן ב-N ימים"
published_at > 8 ימים    →  banner אדום: "המידע לא רלוונטי"
```

הסטטוס מוטמע ב-`manifest.json` (שדה `staleness_level`) — WordPress renderer לא מחשב בעצמו.

## מבנה המידע ברמה גבוהה

המערכת שומרת את הישויות הבאות:

- מקורות + fetch profiles
- normalizer profiles ו-rules (data-driven)
- מוצרים + aliases + variants + merges
- יחידות מידה + המרות
- raw assets
- extraction items
- normalized observations + observation flags
- daily aggregates
- weekly snapshots
- publish runs + artifacts
- users + audit_log + log_entries

## ממשקים

### ממשק ציבורי

- פתוח לכולם
- מציג מחירון מאוגד (community)
- מציג benchmark בנפרד
- מציג תאריך עדכון אחרון
- מציג אזהרת staleness לפי מדיניות
- **לא** מציג מקורות, raw data, סטטוס טכני, diagnostics

### ממשק מקומי (admin)

- נגיש מקומית בלבד (127.0.0.1)
- כולל:
  - Dashboard
  - Sources
  - Runs
  - Observations
  - QA
  - Publish
  - Normalizer (aliases, rules, merges, flags)

## סיכונים מרכזיים

- מקורות משתנים או נשברים
- קושי בנרמול יחידות וכמויות
- cache/CDN של `uPress` עלול לעכב עדכון קבצים
- easyFarm כנקודת כשל יחידה לחמישה מקורות
- מסלול publish עשוי להיות מוגבל לפי חבילת האחסון

## נושאים שאומתו ב-v1.1

- הוחלט: **PostgreSQL** (לא SQLite)
- הוחלט: **Python + Flask** (לא PHP)
- הוחלט: baskets = מוצרים עצמאיים (לא ממירים לק"ג)
- הוחלט: normalizer data-driven מ-DB
- הוחלט: min 2 observations מ-2 מקורות לפרסום ציבורי
- הוחלט: uPress validation הוא **שלב מקדים** (לא שלב מאוחר)
- הוחלט: stale data — 3 ימים warning, 8 ימים not relevant
- הוחלט: פילטר region הוסר מ-V1

## מסמכי הרפרנס המלאים

### מסמכי יסוד

- [אפיון ראשוני ותוכנית עבודה](/Users/nimrod/Documents/SmallFarmsAgents/docs/INITIAL_PROJECT_PLAN_HE.md)
- [אפיון מערכת מפורט](/Users/nimrod/Documents/SmallFarmsAgents/docs/DETAILED_SYSTEM_SPEC_HE.md) — v1.1
- [החלטות אדריכליות מרוכזות](/Users/nimrod/Documents/SmallFarmsAgents/docs/ARCHITECTURE_DECISIONS_HE.md) — v1.1
- [מודל מידע והחלטות Publish](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md) — v1.1

### מסמכים חדשים ב-v1.1

- [דוח בחינה אדריכלית](/Users/nimrod/Documents/SmallFarmsAgents/docs/REVIEW_REPORT_V1.md)
- [קטלוג מוצרים V1](/Users/nimrod/Documents/SmallFarmsAgents/docs/PRODUCT_CATALOG_V1.md)
- [מפרט schema בסיס נתונים](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATABASE_SCHEMA_SPEC_HE.md)
- [מפרט מנגנון Normalizer](/Users/nimrod/Documents/SmallFarmsAgents/docs/NORMALIZER_SPEC_HE.md)
- [אלגוריתמי Pipeline](/Users/nimrod/Documents/SmallFarmsAgents/docs/PIPELINE_ALGORITHMS_HE.md)

### מקורות נתונים ומיפוי

- [מפת מקורות מאסטר](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER_HE.md) — v1.1

### UX וממשקים

- [מוקאפ ממשקים](/Users/nimrod/Documents/SmallFarmsAgents/docs/INTERFACE_MOCKUPS_HE.md) — v1.1

### ולידציה תפעולית

- [תכנית ולידציה ל-uPress](/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_VALIDATION_PLAN_HE.md) — v1.1 (שלב מקדים)

## המלצה לסדר קריאה

1. מסמך זה
2. [דוח בחינה אדריכלית](/Users/nimrod/Documents/SmallFarmsAgents/docs/REVIEW_REPORT_V1.md)
3. [אפיון מערכת מפורט](/Users/nimrod/Documents/SmallFarmsAgents/docs/DETAILED_SYSTEM_SPEC_HE.md)
4. [מפרט schema בסיס נתונים](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATABASE_SCHEMA_SPEC_HE.md)
5. [מפרט מנגנון Normalizer](/Users/nimrod/Documents/SmallFarmsAgents/docs/NORMALIZER_SPEC_HE.md)
6. [אלגוריתמי Pipeline](/Users/nimrod/Documents/SmallFarmsAgents/docs/PIPELINE_ALGORITHMS_HE.md)
7. [מפת מקורות מאסטר](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER_HE.md)
8. [מוקאפ ממשקים](/Users/nimrod/Documents/SmallFarmsAgents/docs/INTERFACE_MOCKUPS_HE.md)
9. [תכנית ולידציה ל-uPress](/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_VALIDATION_PLAN_HE.md)

## סטטוס נוכחי

הפרויקט נמצא בסיום שלב אפיון מפורט v1.1.

**שלב מקדים חובה לפני כתיבת קוד:**
- ביצוע בדיקות U01–U06 מול uPress (FTP access + file visibility)

**לאחר מכן, צעדים לביצוע:**

1. הרצת Alembic migrations ליצירת schema בפועל
2. seed data: measurement_units, products, sources
3. collectors ל-SRC002, SRC003, SRC004 (easyFarm family)
4. normalizer rules ראשוניים מ-PRODUCT_CATALOG_V1
5. admin UI: Dashboard + Runs + Observations
6. publish pipeline end-to-end test
