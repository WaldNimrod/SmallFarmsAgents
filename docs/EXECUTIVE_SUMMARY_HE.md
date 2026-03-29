# תקציר מנהלים

תאריך: 2026-03-29

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

## החלטות אדריכליות מרכזיות

### architecture

- המערכת תיבנה כ-`Local Data Hub + Public WordPress Surface`
- וורדפרס הוא `presentation layer`, לא `system of record`

### local storage

- בסיס הנתונים המקומי המומלץ הוא `PostgreSQL`
- raw files ו-artifacts יישמרו על filesystem

### local admin

- ממשק admin מקומי הוא חובה מיום ראשון
- admin V1 מיועד לניטור, לוגים, QA והרצת תהליכים ידנית
- admin V1 אינו מיועד לניהול מלא של מקורות, normalizers או תוכן

### online publish

- האונליין ישתמש ב:
  - `manifest.json`
  - `public_report.json`
  - `public_report.html`
- אין שימוש ב-DB של WordPress לאחסון נתוני המערכת

### publish transport

- המסלול המועדף הוא upload אוטומטי ב-FTP/FTPS
- נדרש proof test מול `uPress` לפני אישור סופי

## מבנה המידע ברמה גבוהה

המערכת צריכה לשמור לפחות את היישויות הבאות:

- מקורות
- פרופילי fetch
- normalizer profiles
- normalizer rules
- מוצרים
- aliases
- variants
- יחידות מידה
- המרות
- raw assets
- extraction items
- normalized observations
- daily aggregates
- weekly snapshots
- publish runs
- publish artifacts

## ממשקים

### ממשק ציבורי

- פתוח לכולם
- מציג מחירון מאוגד
- מציג benchmark בנפרד
- מציג תאריך עדכון אחרון

### ממשק מקומי

- נגיש מקומית בלבד
- כולל:
  - Dashboard
  - Sources
  - Runs
  - Observations
  - QA
  - Publish

## סיכונים מרכזיים

- מקורות משתנים או נשברים
- קושי בנרמול יחידות וכמויות
- cache/CDN של `uPress` עלול לעכב עדכון קבצים
- מסלול publish עשוי להיות מוגבל לפי חבילת האחסון

## נושאים שעדיין דורשים ולידציה

- האם FTPS זמין ויציב עבור האתר הנוכחי
- האם נתיב publish ייעודי זמין וקבוע
- האם cache/CDN משפיע על refresh של artifacts
- האם WordPress עדיף שיקרא JSON או HTML כ-path ציבורי ראשי

## מסמכי הרפרנס המלאים

### מסמכי יסוד

- [אפיון ראשוני ותוכנית עבודה](/Users/nimrod/Documents/SmallFarmsAgents/docs/INITIAL_PROJECT_PLAN_HE.md)
- [אפיון מערכת מפורט](/Users/nimrod/Documents/SmallFarmsAgents/docs/DETAILED_SYSTEM_SPEC_HE.md)
- [החלטות אדריכליות מרוכזות](/Users/nimrod/Documents/SmallFarmsAgents/docs/ARCHITECTURE_DECISIONS_HE.md)
- [מודל מידע והחלטות Publish](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md)

### מקורות נתונים ומיפוי

- [מפת מקורות מאסטר](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER_HE.md)
- [קובץ מפת מקורות CSV](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER.csv)

### UX וממשקים

- [מוקאפ ממשקים](/Users/nimrod/Documents/SmallFarmsAgents/docs/INTERFACE_MOCKUPS_HE.md)

### ולידציה תפעולית

- [תכנית ולידציה ל-uPress](/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_VALIDATION_PLAN_HE.md)

## המלצה לסדר קריאה

1. מסמך זה
2. [אפיון מערכת מפורט](/Users/nimrod/Documents/SmallFarmsAgents/docs/DETAILED_SYSTEM_SPEC_HE.md)
3. [מודל מידע והחלטות Publish](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md)
4. [מפת מקורות מאסטר](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER_HE.md)
5. [מוקאפ ממשקים](/Users/nimrod/Documents/SmallFarmsAgents/docs/INTERFACE_MOCKUPS_HE.md)
6. [תכנית ולידציה ל-uPress](/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_VALIDATION_PLAN_HE.md)

## סטטוס נוכחי

הפרויקט נמצא בשלב אפיון מפורט לפני כתיבת קוד.

הצעדים הבאים לאישור:

1. אישור עקרונות הארכיטקטורה
2. אישור מודל המידע
3. ביצוע proof tests מול `uPress`
4. אישור הממשקים והמוקאפים
5. מעבר ל-Schema Spec ו-Execution Plan
