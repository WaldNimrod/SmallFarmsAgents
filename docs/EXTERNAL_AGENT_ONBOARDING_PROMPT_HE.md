# Onboarding Prompt לצוות בחינה חיצוני

תאריך: 2026-03-29

## מטרת הפרומפט

מסמך זה מיועד להעברה לצוות חדש או אייג'נט חיצוני בסביבה אחרת, לצורך לימוד מהיר של הפרויקט וביצוע בחינה אדריכלית וקונספטואלית עמוקה של האפיון הקיים.

ניתן להדביק את הטקסט כמות שהוא כפרומפט פתיחה.

---

## נוסח מומלץ להעברה

אתם מצטרפים כצוות בחינה חיצוני לפרויקט חדש בשלבי אפיון, שמטרתו להקים שירות קהילתי חינמי עבור קהילת החקלאים האורגניים והאקולוגיים בישראל.

### הקשר כללי

הפיצ'ר הראשון של המערכת הוא מחירון שוק לירקות אורגניים, עם מיקוד בשוק מאוד מסוים:

- חוות קטנות
- שיווק ישיר
- סלים
- CSA
- שווקי איכרים
- חנויות בחווה

המערכת אינה מבוססת על מקור יחיד, אלא על אגרגציה של מקורות מידע רבים וחלקיים.

בנוסף, יוצגו גם מחירי benchmark ממקורות כלליים ומרשתות גדולות, אך בנפרד מהשוק הקהילתי-אורגני.

### עקרונות שכבר הוגדרו

- המערכת צריכה להישאר פשוטה ככל האפשר
- ה-system of record הוא מקומי
- הממשק הציבורי חי בתוך אתר WordPress קיים: `nimrod.bio`
- וורדפרס הוא שכבת תצוגה בלבד, לא data store
- בצד הציבורי יוצגו רק נתונים מאוגדים
- לא יוצגו לציבור מקורות ספציפיים או raw data
- ממשק admin מקומי הוא חובה מיום ראשון
- ה-online publish מתוכנן להתבסס על artifacts סטטיים:
  - `manifest.json`
  - `public_report.json`
  - `public_report.html`
- בסיס הנתונים המקומי המועדף הוא `PostgreSQL`
- raw files וה-artifacts נשמרים על filesystem
- benchmark חייב להיות מופרד ויזואלית מהשוק הקהילתי
- חייב להיות `last known good` fallback
- בכל ממשק ציבורי חייב להיות `updated_at`

### מצב הפרויקט

אנחנו עדיין לפני כתיבת קוד.  
המשימה שלכם היא לא לכתוב מערכת, אלא לבצע בחינה עמוקה של האפיון הקיים ולהחזיר חוות דעת אדריכלית, קונספטואלית ומערכתית.

---

## המשימה שלכם

בצעו בחינה מעמיקה של כלל האפיון הקיים והפיקו review רחב, חד ומעמיק, שיכלול:

1. הערכה אדריכלית של המבנה המוצע
2. הערכה קונספטואלית של ההיגיון העסקי והתפעולי
3. זיהוי פערים, סיכונים, הנחות חלשות או מוקדים לא סגורים
4. הצעת שיפורים, דיוקים, simplifications או חלופות
5. שאלות הבהרה שנדרש לפתור לפני מעבר לפיתוח
6. המלצה אם הארכיטקטורה הנוכחית מוכנה ל-schema spec ולשלב implementation

---

## אופן העבודה המבוקש

### 1. קודם להבין, אחר כך לבקר

לפני ביקורת, קראו והבינו את המסמכים, את המיקוד, ואת אילוצי הפשטות והתחזוקה.

### 2. לשאול שאלות תוך כדי הדרך

אם במהלך הבחינה עולות נקודות מהותיות שאינן ניתנות להכרעה מתוך המסמכים, העלו שאלות הבהרה מסודרות.

לא לבנות הנחות מרחיקות לכת בלי לציין שהן הנחות.

### 3. לא להציע מורכבות מיותרת

הפרויקט בכוונה מכוון לפתרון פשוט, maintainable, ו-low-ops.

אם אתם מציעים חלופה מורכבת יותר:

- הסבירו מה מרוויחים
- הסבירו מה המחיר
- ציינו האם זה מתאים ל-V1 או רק לשלב מאוחר יותר

### 4. לשמור על הבחנה בין שלוש שכבות

- local system of record
- local admin / dev console
- public WordPress presentation layer

### 5. להתייחס גם ל-operational reality

בפרט:

- מנגנון publish
- מגבלות `uPress`
- cache / CDN
- last-good fallback
- ניטור ותפעול
- auditability

---

## תוצרים נדרשים

נא להחזיר תשובה מסודרת הכוללת לפחות את החלקים הבאים:

### חלק א: Executive Assessment

- האם הכיוון הכללי נכון
- מה חזק במיוחד
- מה חלש במיוחד
- האם יש סתירה מהותית בארכיטקטורה

### חלק ב: Architectural Findings

רשימת findings לפי עדיפות/חומרה, למשל:

- Critical
- High
- Medium
- Low

בכל finding יש לציין:

- הבעיה
- למה היא חשובה
- באיזה מסמך/החלטה היא נובעת
- מה ההמלצה

### חלק ג: Conceptual Review

בחינה של:

- התאמה בין המטרה העסקית למבנה המערכת
- האם מודל המקורות תואם את הנישה
- האם ההבחנה בין community לבין benchmark מוגדרת טוב
- האם מודל האגרגציה מוגדר נכון

### חלק ד: Data Model Review

בחינה של:

- שלמות הישויות
- קשרים חסרים
- סיכוני normalization
- unit conversions
- snapshots
- publish artifacts

### חלק ה: Operational Review

בחינה של:

- local admin from day one
- unattended daily publish
- `uPress` feasibility
- fallback strategy
- observability

### חלק ו: Clarification Questions

שאלות הבהרה שחייבות תשובה לפני פיתוח.

### חלק ז: Recommended Changes

רשימה פרקטית של שינויים מומלצים למסמכי האפיון.

### חלק ח: Readiness Verdict

סיכום חד:

- `Ready for schema spec`
- `Needs clarification before schema spec`
- `Needs architectural revision before proceeding`

---

## מוקדי בחינה מומלצים

נא לשים דגש מיוחד על:

1. האם ההחלטה על `PostgreSQL + filesystem + static public artifacts` היא ההחלטה הנכונה
2. האם מודל ה-admin המקומי מוגדר נכון ל-V1
3. האם מסלול `local -> build -> upload -> WordPress render` מספיק אמין ופשוט
4. האם מודל הנתונים מכסה היטב:
   - מקורות
   - fetch profiles
   - normalizers
   - aliases
   - variants
   - unit conversions
   - raw
   - observations
   - aggregates
   - weekly snapshots
   - publish runs
5. האם ה-separation בין public view לבין internal data חזק מספיק
6. האם יש סיכונים שלא קיבלו מענה מספק
7. האם יש פער בין האפיון לבין reality של WordPress managed hosting

---

## מסמכי רפרנס לקריאה

אנא קראו לפחות את המסמכים הבאים:

- [תקציר מנהלים](/Users/nimrod/Documents/SmallFarmsAgents/docs/EXECUTIVE_SUMMARY_HE.md)
- [אפיון מערכת מפורט](/Users/nimrod/Documents/SmallFarmsAgents/docs/DETAILED_SYSTEM_SPEC_HE.md)
- [החלטות אדריכליות מרוכזות](/Users/nimrod/Documents/SmallFarmsAgents/docs/ARCHITECTURE_DECISIONS_HE.md)
- [מודל מידע והחלטות Publish](/Users/nimrod/Documents/SmallFarmsAgents/docs/DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md)
- [תכנית ולידציה ל-uPress](/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_VALIDATION_PLAN_HE.md)
- [מפת מקורות מאסטר](/Users/nimrod/Documents/SmallFarmsAgents/docs/SOURCE_MAP_MASTER_HE.md)
- [מוקאפ ממשקים](/Users/nimrod/Documents/SmallFarmsAgents/docs/INTERFACE_MOCKUPS_HE.md)

לרקע רחב יותר:

- [אפיון ראשוני ותוכנית עבודה](/Users/nimrod/Documents/SmallFarmsAgents/docs/INITIAL_PROJECT_PLAN_HE.md)

---

## מגבלות והנחיות

- אל תניחו שוורדפרס ישמש כ-database layer
- אל תניחו שהמערכת הציבורית יכולה לראות את המידע המקומי בזמן אמת
- אל תניחו שהאינטרנט/השרת המנוהל מאפשרים endpoint מותאם אישית בלי עלות תחזוקה
- אל תניחו שהפתרון צריך להיות enterprise-grade
- כן לחפש פשטות, אמינות, והיגיון ארוך טווח

---

## ניסוח הסיום המבוקש

בסיום הבחינה, נא לתת:

1. verdict חד
2. 5-10 findings עיקריים
3. שאלות הבהרה הכרחיות
4. רשימת שינויים מומלצים למסמכי האפיון

---

## הערה למי שמעביר את הפרומפט

אם יש אפשרות, מומלץ לצרף יחד עם הפרומפט גם את מסמך [תקציר המנהלים](/Users/nimrod/Documents/SmallFarmsAgents/docs/EXECUTIVE_SUMMARY_HE.md) כנקודת כניסה ראשונה.
