# דוח בחינה אדריכלית וקונספטואלית — SmallFarms Market Data System

גרסה: 1.0  
תאריך: 2026-03-29  
מסמכים שנבחנו: כלל שמונת מסמכי האפיון כולל INITIAL_PROJECT_PLAN_HE.md  
ביצע: צוות בחינה חיצוני (AI Review Agent)

---

## חלק א: Executive Assessment

### האם הכיוון הכללי נכון

**כן.** ארכיטקטורת `Local Data Hub + Static Public Artifacts + WordPress Presentation Layer` נכונה ומדויקת לפרויקט מהסוג הזה. שמירת מורכבות מקומית, חשיפה ציבורית פשוטה, ללא תלות ב-runtime ציבורי חי — אלו עקרונות שעומדים במבחן הזמן. זו אינה ארכיטקטורה שיש לאתגר, יש לדייק בתוכה.

### מה חזק במיוחד

- **הפרדת community/benchmark** — עקבית לאורך כל המסמכים, מוגדרת היטב הן ברמת מודל הנתונים והן ברמת ה-UX.
- **מודל הנתונים** — `DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` הוא המסמך החזק ביותר. מפרט ישויות מלאות, קשרים, שדות וסיבות. רמת הפירוט חריגה לטובה לשלב אפיון.
- **תכנית הולידציה ל-uPress** — הכנת מטריצת בדיקות מסודרת לפני הנחת הצלחה מעידה על בשלות הגישה.
- **מפת מקורות** — מסמך מקצועי שמבדיל בין תפקיד מקור, סיכון תחזוקה ועדיפות MVP.
- **גישת "simple first"** — המסמכים מתנגדים בעקביות להצעות מורכבות ומנמקים. נדיר ובריא.

### מה חלש במיוחד

- **אי-עקביות קריטית בבחירת DB** — שני מסמכים ממליצים SQLite, אחד ממליץ PostgreSQL, ללא הכרעה.
- **שכבת normalization לסלים ו-CSA תת-מוגדרת** — המודל מכיר ב-composite baskets אבל לא מגדיר אלגוריתם.
- **הממשק הציבורי מוקאפ מניח פילוח גיאוגרפי** שמודל הנתונים לא תומך בו.
- **pipeline הפרסום לא אומת** — כל ה-publish architecture מבוסס על הנחה שלא נבדקה.

### סתירה מהותית בארכיטקטורה

יש סתירה פונקציונלית אחת: הממשק הציבורי (מוקאפ) מציג אינטראקציה (סינון לפי אזור, ערוץ, תקופה), אך ה-artifact הציבורי המתוכנן הוא קובץ סטטי. קובץ סטטי לא יכול לתמוך בסינון אינטראקטיבי בלי JavaScript מוטמע.

**פתרון שהוחלט:** הסרת פילטר "אזור" מ-V1. סינון ערוץ ותקופה יתמכו ב-JavaScript מוטמע ב-HTML artifact.

---

## חלק ב: Architectural Findings

### Critical

#### [C1] אי-עקביות בבחירת DB מקומי — SQLite מול PostgreSQL

**הבעיה:** `INITIAL_PROJECT_PLAN_HE.md` ממליץ SQLite. `ARCHITECTURE_DECISIONS_HE.md` מאשר SQLite ("הפתרון הפשוט והנכון ביותר ל-V1"). `DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` ממליץ PostgreSQL. שלושה מסמכים ללא הכרעה.

**למה חשוב:** schema spec לא ניתן לכתוב בלי לדעת מהי מערכת הנתונים. ההבדל מהותי: Docker dependency, setup overhead, query capabilities, concurrent access.

**מקור:** `ARCHITECTURE_DECISIONS_HE.md` §3 לעומת `DATA_MODEL_AND_PUBLISH_DECISIONS_HE.md` §3.

**החלטה (v1.1):** PostgreSQL ישירות על המחשב המקומי, ללא Docker.

---

#### [C2] מנגנון הפרסום המרכזי לא אומת

**הבעיה:** כל ארכיטקטורת ה-publish (FTPS → `/wp-content/uploads/market/`) מבוססת על הנחה שלא נבדקה. `UPRESS_VALIDATION_PLAN_HE.md` מאשר שהבדיקות לא בוצעו.

**למה חשוב:** אם FTPS לא זמין, או יש CDN שמעכב עדכונים, כל מסלול ה-publish צריך שינוי.

**החלטה (v1.1):** bדיקת FTP/FTPS היא **שלב מקדים חובה** לפני כתיבת קוד כלשהו. אם הניסוי נכשל — פנייה לתמיכת uPress.

---

#### [C3] אין הגדרת קטלוג מוצרים ראשוני

**הבעיה:** כל המסמכים מניחים "רשימת מוצרים", אך אין מסמך שמגדיר אותה. אין ירקות, אין קטגוריות, אין יחידות ברירת מחדל.

**החלטה (v1.1):** נוצר `PRODUCT_CATALOG_V1.md` עם ~25 ירקות ליבה.

---

### High

#### [H1] נרמול מחיר סל/CSA — ללא הגדרת אלגוריתם

**הבעיה:** המודל מכיר ב-composite baskets אבל לא מגדיר כיצד ממירים מחיר-סל למחיר-פריט.

**החלטה (v1.1):** סלים הם **מוצרים עצמאיים** (סל קטן, סל גדול, סל משפחתי). הם נשמרים ב-DB ומוצגים בממשק הציבורי בשכבת "סלים ו-CSA" נפרדת. לא ממוזגים לאגרגציה של מחיר לק"ג. פירוק לפריטים בגרסה עתידית.

---

#### [H2] easyFarm — נקודת כשל יחידה לכמה מקורות

**הבעיה:** SRC002, SRC003, SRC004, SRC005, SRC006 — חמישה ממקורות הליבה — הם תת-דומיינים של `easyfarm.co.il`.

**החלטה (v1.1):** להוסיף `platform_family` ל-`source_fetch_profiles`. לבנות collector גנרי אחד ל-easyFarm שמקבל site כפרמטר. לנטר easyFarm כ-dependency קריטית.

---

#### [H3] פילטר "אזור" במוקאפ ציבורי — לא נתמך במודל

**הבעיה:** מוקאפ מציג `[אזור ▼]` אבל אין שדה גיאוגרפי בשום טבלה.

**החלטה (v1.1):** הסרת פילטר אזור מהממשק הציבורי ב-V1. אין הוספת `region` למודל כרגע.

---

#### [H4] אין threshold לפרסום ציבורי לפי כמות תצפיות

**הבעיה:** `daily_aggregates` כולל `sample_size` אבל לא מוגדר מינימום לפרסום.

**החלטה (v1.1):** מוצר מופיע בדוח ציבורי רק אם `sample_size >= 2` ומקורות מובחנים >= 2.

---

#### [H5] שני ממשקי publish — אין spec ל-WordPress renderer

**הבעיה:** שלוש אפשרויות מוזכרות (shortcode, HTML block, page template) ולא נבחרה אחת.

**החלטה (v1.1):** `public_report.html` מכיל JavaScript מוטמע minimal שקורא `manifest.json` ואז את ה-JSON המצוין בו. WordPress מציג את ה-HTML הזה דרך page template פשוט. אין plugin כבד.

---

### Medium

#### [M1] `last known good` — ללא הגדרת TTL

**החלטה (v1.1):** אחרי 3 ימים ללא עדכון — banner צהוב ציבורי. אחרי 8 ימים — banner אדום "מידע לא רלוונטי". הסטטוס מוטמע ב-`manifest.json` (`staleness_level`: `ok` / `warning` / `stale`).

---

#### [M2] `audit_log` ו-`users` נעלמו מהמודל המפורט

**החלטה (v1.1):** שתי הטבלאות חוזרות למודל. Phase A — `users` ריק (local-only ללא auth). Phase B — `users` עם admin יחיד ו-`Basic Auth`.

---

#### [M3] `confidence_score` לא משוקלל ב-`daily_aggregates`

**החלטה (v1.1):** `daily_aggregates` יכלול גם `weighted_avg_price` (שקלול לפי confidence) וגם `unweighted_avg_price`. הציבור יראה רק את `weighted_avg_price`.

---

#### [M4] אין error recovery thresholds — מתי partial run נחשב "fail"

**החלטה (v1.1):** publish מתבצע רק אם לפחות 2 מקורות קהילתיים (non-benchmark) הצליחו. benchmark אינו חובה ל-publish. run שנכשל לחלוטין שולח email alert.

---

#### [M5] Pricez ו-CHP — סיכון משפטי לא מסומן

**החלטה (v1.1):** SRC017, SRC018 מסומנים ב-`legal_review_required = true` ב-source map. לא בונים collector עבורם עד לבדיקת T&C.

---

#### [M6] אין spec ל-manifest.json update atomicity

**החלטה (v1.1):** סדר upload מוגדר: (1) העלה artifacts חדשים, (2) אמת checksum, (3) עדכן manifest — אחרת abort. manifest_last_good.json נשמר במקביל כ-fallback.

---

### Low

#### [L1] Discovery sources אינם מייצגים "מקורות ממתינים" במודל

**החלטה (v1.1):** הוספת `status` ל-`sources`: `active`, `candidate`, `deprecated`, `discovery_only`.

#### [L2] Normalizer rules הם code-only — שינוי alias דורש deploy

**החלטה (v1.1):** מנגנון normalizer הוא **data-driven לחלוטין** מ-DB. Admin/agent משנה rules בלי deploy. ראו `NORMALIZER_SPEC_HE.md`.

#### [L3] לא מוגדר אחסון לוגים

**החלטה (v1.1):** טבלת `log_entries` מובנית ב-DB לצד קבצי log טקסטואליים.

---

## חלק ג: Conceptual Review

### התאמה בין מטרה עסקית למבנה המערכת

**חזקה.** המטרה — מחירון קהילתי חינמי לחקלאים אורגניים — מתורגמת נכון לארכיטקטורה. publish יומי אחת מספיק. המבנה תואם את הצורך.

### האם מודל המקורות תואם את הנישה

**כמעט.** מקורות easyFarm family, Farmerim, האורגני, שדה ירוק, זינגר מכסים היטב. **פער:** שווקי איכרים פיזיים לרוב מפרסמים ב-Facebook/Instagram ולא באתר מובנה — V1 לא מתמודד עם זה. מקובל לדחות לגרסה עתידית.

### האם ההבחנה community/benchmark מוגדרת טוב

**כן, ברמת העיקרון.** `market_scope` ו-`is_benchmark` נוכחים בכל שכבה. **אתגר:** Farmerim ו-האורגני הם אגרגטורים — ייתכן שמוצרים שלהם מגיעים ממשקים לא-אורגניים. ה-flag `is_organic_claimed` קיים אבל הקשר לשכבת verification (Secal/IQC) לא מוגדר. מקובל לדחות לגרסה עתידית.

### האם מודל האגרגציה מוגדר נכון

**חלקית.** הנוסחה עצמה (avg, median, stddev, min/max, sample_size) פשוטה ונכונה. **נדרש** policy מפורש: daily_aggregate מחושב רק על observations עם `is_benchmark=false` ו-`flag_status='ok'` ו-`normalized_unit_id IN (kg, unit)` ו-`is_basket_product=false`.

---

## חלק ד: Data Model Review

### שלמות הישויות

**טובה מאוד.** 16 ישויות מוגדרות. **חסרים:**
- `users`
- `audit_log`
- `log_entries`

### קשרים חסרים

- `sources` אינו קשור ל-`region` — לא נדרש ב-V1, הוחלט להסיר
- `product_aliases` צריך להיות קשיר גם ל-`normalizer_profile_id` (לא רק ל-`source_id`)
- `raw_extracted_items` צריך `normalizer_profile_id` — לדעת איזה normalizer ייצר

### unit conversions

הכי מאתגר בפרויקט. מגבלות שנשארות בV1:
- ירק שנמכר ב-"חבילה" ללא משקל מצוין → `unresolvable_unit` flag
- מחיר "לפי מינימום הזמנה שבועית" (CSA) → מוצג כ-basket product
- `heuristic` conversions חייבים להיות מסומנים גם ב-`normalization_method`

### publish artifacts

מוגדרים היטב. `is_last_good` ב-`publish_runs` מאפשר recovery. **נדרש הוספה:** שדה `staleness_level` ב-`manifest.json` (`ok` / `warning` / `stale`).

---

## חלק ה: Operational Review

### Local admin from day one

מוגדר נכון. binding ל-`127.0.0.1`, ללא auth ב-Phase A. **פער:** ממשק ה-admin חייב לאפשר ניהול flexible של normalizer rules — merge products, hide observations, עריכת aliases — כדי לצמצם עבודה ידנית לאורך זמן. זה לא CRUD מלא, אבל admin/agent חייב להיות מסוגל לשנות rules ב-DB בלי deploy.

### Unattended daily publish

**פרצה:** לא מוגדרת שום התראה. **החלטה:** email alert אם run נכשל לחלוטין, ואם לא בוצע publish ב-24 שעות.

### uPress feasibility

**הכי פתוח.** אם uPress משתמש ב-Cloudflare/Varnish על `/wp-content/uploads/` — overwrite של קובץ עלול לא להיראות לגולשים שעות. **פתרון:** versioned filenames + manifest + בדיקה מקדימה של cache TTL כחלק מ-proof tests.

### Fallback strategy

WP renderer קורא `manifest.json` → אם version החדש לא עובד → fallback לקריאה של `manifest_last_good.json`. שני manifest files נשמרים בשרת.

### Observability

לפחות: email על כשל, log_entries ב-DB, בדיקת עדכניות manifest_published_at מהציבור.

---

## חלק ו: Clarification Questions — שהוכרעו

| שאלה | החלטה |
|---|---|
| SQLite vs PostgreSQL? | PostgreSQL ישירות, ללא Docker |
| Stack? | Python + Flask |
| Region filter בציבורי? | לא בV1 — הוסר |
| Basket normalization policy? | Baskets הם מוצרים עצמאיים; לא מפורקים בV1 |
| Min sample לפרסום? | 2 תצפיות מ-2 מקורות שונים |
| Publish threshold? | לפחות 2 מקורות קהילתיים הצליחו |
| Last good TTL ציבורי? | אזהרה אחרי 3 ימים, "לא רלוונטי" אחרי 8 |
| uPress validation? | שלב מקדים חובה לפני כל פיתוח |
| Admin framework? | Flask |

---

## חלק ז: Recommended Changes — יושמו ב-v1.1

| # | שינוי | מסמך יעד |
|---|---|---|
| R1 | צור PRODUCT_CATALOG_V1.md | מסמך חדש |
| R2 | קבע PostgreSQL ועדכן כל המסמכים | כל המסמכים |
| R3 | הסר region מהמוקאפ ומהמודל | INTERFACE_MOCKUPS, DATA_MODEL |
| R4 | הוסף users + audit_log + log_entries | DATA_MODEL |
| R5 | הגדר basket as product policy | DATA_MODEL, DETAILED_SPEC |
| R6 | הגדר minimum_sample_size לפרסום | DATA_MODEL |
| R7 | הוסף alerting_on_failure לדרישות | DETAILED_SPEC |
| R8 | הגדר manifest fallback strategy + manifest_last_good.json | DATA_MODEL |
| R9 | סמן SRC017, SRC018 עם legal_review_required | SOURCE_MAP |
| R10 | הוסף platform_family ל-source_fetch_profiles | DATA_MODEL, SOURCE_MAP |
| R11 | צור NORMALIZER_SPEC.md — מנגנון data-driven מלא | מסמך חדש |
| R12 | צור DATABASE_SCHEMA_SPEC.md — schema מלא | מסמך חדש |
| R13 | צור PIPELINE_ALGORITHMS.md — אלגוריתמי ליבה | מסמך חדש |
| R14 | הוסף stale data banners לממשק ציבורי | INTERFACE_MOCKUPS |
| R15 | קדם uPress validation לשלב מקדים | UPRESS_VALIDATION_PLAN |

---

## חלק ח: Readiness Verdict

```
Needs clarification before schema spec  →  (הוכרע)  →  Ready for schema spec
```

לאחר סגירת כל ההחלטות בתהליך הבחינה, האפיון **מוכן למעבר ל-schema spec ולשלב implementation**.

### תנאי מקדים אחד שנותר לפני קוד

**בדיקת uPress (U01–U03)** חייבת להתבצע לפני כתיבת publish pipeline. כל שאר הפיתוח יכול להתחיל במקביל.

---

### Findings Summary

| # | Finding | חומרה | סטטוס |
|---|---|---|---|
| C1 | אי-עקביות SQLite/PostgreSQL | Critical | הוכרע — PostgreSQL |
| C2 | uPress pipeline לא אומת | Critical | שלב מקדים חובה |
| C3 | קטלוג מוצרים חסר | Critical | נוצר PRODUCT_CATALOG_V1 |
| H1 | basket/CSA normalization לא מוגדר | High | baskets = מוצרים עצמאיים |
| H2 | easyFarm כנקודת כשל יחידה | High | platform_family + generic collector |
| H3 | region filter ללא תמיכה במודל | High | הוסר מ-V1 |
| H4 | אין threshold ל-sample_size | High | min 2 obs מ-2 מקורות |
| H5 | WordPress renderer לא מוגדר | High | HTML + embedded JS |
| M1 | last known good TTL לא מוגדר | Medium | 3 ימים warning, 8 ימים stale |
| M2 | users + audit_log חסרים | Medium | חזרו למודל |
| M3 | confidence לא משוקלל ב-aggregates | Medium | weighted_avg_price |
| M4 | אין error recovery thresholds | Medium | min 2 community sources |
| M5 | legal risk ב-Pricez/CHP | Medium | legal_review_required flag |
| M6 | manifest atomicity לא מוגדר | Medium | upload order + manifest_last_good |
