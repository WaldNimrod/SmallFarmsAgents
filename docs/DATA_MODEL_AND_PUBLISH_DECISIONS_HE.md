# מודל מידע והחלטות Publish

תאריך: 2026-03-29

## 1. מטרת המסמך

לנעול שלוש החלטות יסוד:

1. מהו מודל הנתונים המקומי הדרוש למערכת
2. איך המידע נשמר מקומית לאורך זמן
3. איך ה-publish לאתר הציבורי מתבצע אוטומטית וללא תלות ב-DB של וורדפרס

## 2. החלטות שכבר נסגרו

- ה-system of record הוא מקומי
- וורדפרס אינו data store
- האונליין יציג `HTML + JSON`
- יש חובה ל-`local admin` מ-V1
- אין תהליך ידני קבוע; היעד הוא publish יומי אוטומטי
- חייב להיות `last good artifact`
- בממשק הציבורי יוצג `updated_at`

## 3. החלטת בסיס נתונים מקומי

### חלופות

| חלופה | יתרונות | חסרונות | המלצה |
|---|---|---|---|
| SQLite | פשוט, מהיר להתחלה | נוטה להפוך זמני כשהמערכת גדלה, פחות טוב לעבודה מובנית עם הרבה טבלאות וקשרים | לא מומלץ במקרה שלכם |
| MySQL/MariaDB | מוכר, נוח ל-PHP, בשל | פחות נוח ל-JSON מורכב, constraints ו-analytics פנימי לעומת Postgres | אפשרי |
| PostgreSQL | חזק, schema עשיר, constraints טובים, JSONB, views/materialized patterns, נוח למודל נתונים מורכב | מעט יותר setup | מומלץ |

### החלטה

לבנות מראש על `PostgreSQL` מקומי בתוך Docker.

### למה

- יש לכם כבר Docker
- יש הרבה ישויות וקשרים
- יש raw metadata, normalizers, aliases, conversions, runs, snapshots ו-publish history
- חשוב לשמור דיוק, auditability ויכולת query טובה לאורך זמן
- זה חוסך migration מיותרת מ-SQLite בשלב מאוחר

## 4. עקרון שמירת המידע המקומי

### לא כל המידע צריך להישמר באותה צורה

המודל הנכון הוא hybrid:

- `PostgreSQL` לנתונים מובנים
- filesystem ל-raw files ול-artifacts

### למה לא לשים הכל ב-DB

- raw HTML/PDF/JSON יכולים לגדול מהר
- DB blobs מסרבלים גיבוי, בדיקה ותחזוקה
- קל יותר לשמור checksum + path ב-DB ואת הקובץ עצמו על הדיסק

### החלטה

- metadata ב-DB
- payload files על הדיסק
- publish artifacts גם ב-DB metadata וגם כקבצים

## 5. מודל המידע הדרוש

להלן מודל הנתונים המינימלי-מלא המומלץ ל-V1.

### 5.1 שכבת מקורות

#### `sources`

מייצגת מקור לוגי.

שדות מומלצים:

- `id`
- `code`
- `name`
- `base_url`
- `source_group`
  - direct_price
  - basket_csa
  - discovery
  - benchmark
  - verification
- `market_scope`
  - community
  - benchmark
  - verification
- `sales_channel`
  - community_direct
  - csa_basket
  - farm_shop
  - farmers_market
  - retail_chain_benchmark
- `is_active`
- `priority`
- `notes`
- `created_at`
- `updated_at`

#### `source_fetch_profiles`

מייצגת איך ניגשים למקור בפועל.

שדות:

- `id`
- `source_id`
- `fetch_mode`
  - html_page
  - json_endpoint
  - pdf_download
  - rss
  - directory_page
- `entry_url`
- `http_method`
- `request_headers_json`
- `schedule_kind`
  - daily
  - weekly
  - manual_check
- `timeout_seconds`
- `retry_policy_json`
- `is_public_access`
- `charset_hint`
- `selector_profile`
- `is_active`

### 5.2 שכבת normalizers

#### `normalizer_profiles`

מגדירה איזה normalizer חל על מקור.

שדות:

- `id`
- `source_id`
- `normalizer_type`
  - easyfarm_catalog
  - simple_product_grid
  - basket_only
  - retail_benchmark
  - official_wholesale
- `version`
- `is_active`
- `notes`

#### `normalizer_rules`

חוקי normalizer ברמת מקור.

שדות:

- `id`
- `normalizer_profile_id`
- `rule_kind`
  - product_alias
  - unit_map
  - quantity_parse
  - organic_flag
  - ignore_pattern
  - benchmark_tag
  - basket_parse
- `match_pattern`
- `replacement_value`
- `priority`
- `is_active`

### 5.3 שכבת מוצרים

#### `products`

- `id`
- `canonical_name_he`
- `category`
- `is_organic_required`
- `default_measurement_unit_id`
- `is_active`

#### `product_aliases`

- `id`
- `product_id`
- `alias_text`
- `source_id` nullable
- `confidence`

#### `product_variants`

מייצג צורות מסחר שונות של אותו מוצר.

דוגמאות:

- חסה לראש
- בצל יבש לק"ג
- סל עגבניות 500 גרם
- צרור כוסברה

שדות:

- `id`
- `product_id`
- `variant_name`
- `quantity_value`
- `quantity_unit_id`
- `normalized_base_unit_id`
- `normalized_factor`
- `is_composite`
- `notes`

### 5.4 שכבת יחידות ומידות

#### `measurement_units`

- `id`
- `code`
  - kg
  - g
  - unit
  - bunch
  - basket
  - pack
- `name_he`
- `unit_type`
  - weight
  - count
  - bundle
  - basket
- `is_normalizable`

#### `unit_conversions`

משמש להמרות חוקיות ומבוקרות.

- `id`
- `from_unit_id`
- `to_unit_id`
- `factor`
- `conversion_type`
  - exact
  - heuristic
  - product_specific
- `product_id` nullable
- `notes`

#### `quantity_profiles`

מגדיר אריזות/כמויות נפוצות.

דוגמאות:

- מארז 250 גרם
- סל קטן
- סל משפחתי
- צרור

שדות:

- `id`
- `label_he`
- `quantity_value`
- `unit_id`
- `product_id` nullable
- `is_estimated`
- `notes`

### 5.5 שכבת ריצות ו-raw

#### `ingestion_runs`

מייצגת ריצה מערכתית אחת.

- `id`
- `run_type`
  - daily
  - manual
  - retry
- `started_at`
- `finished_at`
- `status`
- `sources_total`
- `sources_succeeded`
- `sources_failed`
- `triggered_by`

#### `source_fetch_runs`

ריצה אחת למקור אחד.

- `id`
- `ingestion_run_id`
- `source_id`
- `started_at`
- `finished_at`
- `status`
- `http_status`
- `error_message`
- `raw_asset_id`

#### `raw_assets`

מטא-דאטה על קבצי raw.

- `id`
- `source_id`
- `source_fetch_run_id`
- `storage_path`
- `file_type`
- `checksum_sha256`
- `bytes_size`
- `captured_at`

### 5.6 שכבת extraction ו-normalization

#### `raw_extracted_items`

רשומות ביניים ישירות אחרי parser.

- `id`
- `source_fetch_run_id`
- `raw_asset_id`
- `raw_product_name`
- `raw_price_text`
- `raw_unit_text`
- `raw_quantity_text`
- `raw_payload_json`
- `extracted_at`

#### `normalized_observations`

רשומת אמת מנורמלת לאגרגציה.

- `id`
- `source_id`
- `source_fetch_run_id`
- `product_id`
- `product_variant_id` nullable
- `market_scope`
- `sales_channel`
- `is_benchmark`
- `is_organic_claimed`
- `price_amount`
- `currency_code`
- `display_unit_id`
- `normalized_price_value`
- `normalized_unit_id`
- `normalization_method`
- `confidence_score`
- `flag_status`
  - ok
  - review
  - ignored
- `observed_at`

### 5.7 שכבת snapshots ואגרגציה

#### `daily_aggregates`

- `id`
- `aggregate_date`
- `product_id`
- `market_scope`
- `sales_channel`
- `sample_size`
- `min_price`
- `max_price`
- `avg_price`
- `median_price`
- `stddev_price`
- `last_observed_at`

#### `weekly_snapshots`

המלצה חשובה:

לא לשמור "עוד copy של כל raw" כסנפשוט שבועי. raw נשמר כבר יומית.

במקום זה:

`weekly_snapshots` יהיה freeze של מצב השוק לשבוע, כלומר snapshot אגרגטיבי.

שדות:

- `id`
- `week_start_date`
- `week_end_date`
- `product_id`
- `market_scope`
- `sales_channel`
- `sample_size`
- `week_avg_price`
- `week_median_price`
- `week_stddev_price`
- `week_min_price`
- `week_max_price`
- `snapshot_created_at`

### 5.8 שכבת publish

#### `publish_runs`

- `id`
- `ingestion_run_id` nullable
- `build_started_at`
- `build_finished_at`
- `status`
- `published_at`
- `artifact_version`
- `is_last_good`
- `error_message`

#### `publish_artifacts`

- `id`
- `publish_run_id`
- `artifact_type`
  - public_json
  - public_html
  - manifest_json
- `local_path`
- `checksum_sha256`
- `bytes_size`
- `remote_path`
- `uploaded_at`

## 6. מה שהוספת נכון ומה עוד צריך להשלים

### הדברים שהגדרת נכון

- מקורות
- הגדרות normalizer לכל מקור
- מוצרים
- כמויות/אריזות שונות
- המרות מידה
- raw calls
- weekly snapshot

### מה שחייבים להוסיף

- `source_fetch_profiles`
- `product_aliases`
- `product_variants`
- `measurement_units`
- `raw_extracted_items`
- `normalized_observations`
- `ingestion_runs`
- `publish_runs`
- `publish_artifacts`

בלי הישויות האלה יהיה קשה מאוד לדבג, לשחזר ולנהל QA.

## 7. מבנה publish מומלץ

### artifacts ציבוריים

מומלץ לייצר בכל publish:

- `manifest.json`
- `public_report.json`
- `public_report.html`

### תפקיד כל קובץ

#### `manifest.json`

קובץ קטן עם:

- `published_at`
- `artifact_version`
- `json_path`
- `html_path`
- `status`

#### `public_report.json`

ה-data contract הציבורי.

#### `public_report.html`

fallback view-ready לתצוגה או הטמעה.

## 8. חלופות להעלאה אוטומטית לאתר

המטרה: publish יומי אוטומטי ללא מגע יד אדם.

### חלופה A: push מקומי ב-FTPS

#### איך זה עובד

- אחרי build, השרת המקומי/המחשב המקומי מעלה קבצים ב-FTPS לנתיב ייעודי בשרת

#### יתרונות

- פשוט
- לא תלוי ב-DB של וורדפרס
- מתאים לסביבת shared managed hosting
- נשען על יכולת מתועדת של `uPress`

#### חסרונות

- נדרש לשמור credentials
- צריך retry + checksum + לוגים

#### התאמה ל-uPress

נמצאו מקורות רשמיים של `uPress` המעידים על:

- יצירת חשבונות FTP דרך הפאנל
- תמיכה ב-FTPS

#### מסקנה

זה הנתיב המומלץ ביותר כרגע.

### חלופה B: pull מהשרת דרך cron של uPress

#### איך זה עובד

- uPress מריץ cron שמושך artifact ממיקום חיצוני

#### יתרונות

- השרת יוזם

#### חסרונות

- צריך מקום חיצוני זמין למשיכה
- עוד חוליה בשרשרת
- פחות טבעי כשה-system of record מקומי

#### מסקנה

לא מומלץ כפתרון הראשי.

### חלופה C: endpoint push אל וורדפרס

#### איך זה עובד

- המערכת המקומית שולחת HTTP POST ל-endpoint

#### יתרונות

- יכול להיות אלגנטי

#### חסרונות

- דורש plugin/endpoint
- דורש auth
- יותר מורכב

#### מסקנה

לא ל-V1.

## 9. תכנית בדיקות היתכנות ל-uPress

החלטה:

האפיון יכלול מראש `proof tests` למסלול ה-publish, ולא יסתפק בהנחה תיאורטית.

הסיבה:

- `uPress` הוא שרת WordPress מנוהל ושיתופי
- חלק מהיכולות עשויות להשתנות לפי חבילה
- נדרש לאמת את המסלול הפשוט ביותר שבאמת עובד

### Test Group A: גישת קבצים

#### A1. FTP/FTPS access

מטרה:

- לאשר שניתן להתחבר אוטומטית מהסביבה המקומית

בדיקה:

- יצירת חשבון FTP ייעודי
- התחברות סקריפטית
- העלאת קובץ טסט קטן
- overwrite של אותו קובץ

קריטריון הצלחה:

- upload ו-overwrite עובדים ללא התערבות ידנית

#### A2. כתיבה לנתיב ייעודי

מטרה:

- לאשר שניתן לכתוב לנתיב קבוע תחת:
  - `wp-content/uploads/market/`

קריטריון הצלחה:

- ניתן ליצור, לעדכן ולמחוק קובצי טסט בנתיב

### Test Group B: נראות ציבורית ו-cache

#### B1. file visibility

מטרה:

- לוודא שקובץ שהועלה נגיש ב-HTTP

בדיקה:

- העלאת `test.json`
- קריאה ציבורית ב-browser/`curl`

#### B2. cache invalidation behavior

מטרה:

- לבדוק כמה זמן לוקח לעדכון קובץ להיראות לציבור

בדיקה:

- מעלים גרסה 1
- מוודאים קריאה
- מחליפים לגרסה 2
- בודקים after N seconds/minutes

קריטריון הצלחה:

- ניתן להבטיח עדכון יומי אמין, גם אם יש cache

#### B3. manifest switching

מטרה:

- לבדוק שהמודל של `manifest.json` + versioned files עובד היטב

בדיקה:

- מעלים:
  - `public_report-1.json`
  - `public_report-1.html`
  - `manifest.json`
- מעדכנים ל-גרסה 2
- בודקים שהעמוד או הקריאה החדשה מושכים את הגרסה החדשה

### Test Group C: WordPress rendering

#### C1. static HTML embed

מטרה:

- לבדוק האם קל להציג HTML ציבורי מוכן בעמוד

בדיקה:

- יצירת עמוד ניסוי
- הטמעת partial/fetch/render בסיסי

#### C2. JSON rendering

מטרה:

- לבדוק האם Page Template או block קטן יכול לקרוא JSON בצורה יציבה

בדיקה:

- טעינת JSON
- רינדור כמה שורות טבלה
- הצגת `updated_at`

### Test Group D: failure behavior

#### D1. broken upload tolerance

מטרה:

- לבדוק שהציבור לא נחשף לקובץ שבור

בדיקה:

- ניסיון upload חלקי/שבור
- וידוא שה-manifest לא מתחלף עד סוף upload

#### D2. last good fallback

מטרה:

- לוודא שהעמוד הציבורי ממשיך לעבוד גם כש-publish חדש נכשל

קריטריון הצלחה:

- הציבור ממשיך לראות גרסה קודמת תקינה עם `updated_at` תואם

### Test Group E: automation

#### E1. unattended publish

מטרה:

- לוודא שתהליך build+upload רץ ללא התערבות אנושית

בדיקה:

- הרצה מתוזמנת מקומית
- בדיקת לוגים
- בדיקת checksum
- בדיקת HTTP public output

### תוצרי הבדיקה הנדרשים

- `uPress capability matrix`
- log של test runs
- החלטה מאושרת על upload mechanism
- נתיב publish מאושר

### סטטוס נוכחי

התכנון קיים.
הבדיקות עצמן עדיין לא בוצעו, כי אין כרגע credentials וגישה לפאנל.

## 10. מה אפשר לאשר כרגע על uPress

נכון ל-2026-03-29, מהמקורות הציבוריים של uPress:

- קיימת אפשרות ליצור חשבונות FTP דרך הפאנל
- קיימת תמיכה ב-FTPS
- קיימת אפשרות ל-cronjobs דרך הפאנל
- קיימת אפשרות להגדיר הגבלת גישה לנתיב לפי IP

מה שלא הצלחתי לאשר מהמקורות הציבוריים:

- האם יש SSH בחבילה הנוכחית שלכם
- האם `rsync` זמין או מאושר
- האם יש policy מיוחד לגבי overwrite אוטומטי של קבצים תחת `uploads`
- האם יש מגבלות cache/CDN על קבצים סטטיים במסלול שתבחרו

### מסקנה

`FTPS` הוא הנתיב הבטוח ביותר להניח כקיים.
`rsync` ו-SSH דורשים בדיקה מול uPress.

## 11. מגבלות cache ו-CDN שצריך לקחת בחשבון

מאחר ו-uPress מציעים caching ו-CDN, צריך להניח שהעלאת קובץ חדש לא תמיד תיראה מיידית לציבור.

לכן מומלץ:

1. להעלות `manifest.json`
2. להעלות artifacts עם `artifact_version`
3. לעדכן את ה-manifest אחרון
4. להציג בממשק הציבורי `published_at`
5. לשמור `last good`

### דוגמת naming

- `market/manifest.json`
- `market/public_report-20260329-060000.json`
- `market/public_report-20260329-060000.html`

העמוד הציבורי יקרא קודם את `manifest.json`, ואז יטען את הנתיב הרלוונטי.

כך גם אם cache שומר עותק קודם, המעבר לגרסה חדשה נקי יותר.

## 12. benchmark מופרד ויזואלית - הבהרה

הכוונה אינה לשאלה טכנית אלא UX:

- לא לערבב שוק קהילתי עם benchmark באותה טבלה רציפה
- כן להציג benchmark באזור נפרד:
  - tab
  - accordion
  - section נפרד

### המלצה

באותו עמוד ציבורי, עם section נפרד וברור.

## 13. recommendation set מעודכן

1. `PostgreSQL` מקומי בתוך Docker.
2. raw ו-artifacts על filesystem.
3. `local web admin` חובה מ-V1.
4. admin מקומי לניטור, לוגים, QA ו-publish, לא ל-CRUD מלא.
5. public publish בפורמט `manifest.json + public_report.json + public_report.html`.
6. upload אוטומטי יומי ב-`FTPS`.
7. `last good artifact` חובה.
8. תאריך עדכון אחרון מוצג תמיד לציבור.
9. benchmark מופרד ויזואלית אך באותו עמוד.
10. `rsync/SSH` רק אם uPress יאשרו במפורש.

## 14. שאלות שצריך לסגור מול uPress

1. האם בחבילה שלכם יש SSH?
2. האם `rsync` מותר/זמין?
3. האם אפשר לכתוב אוטומטית לנתיב קבוע תחת `wp-content/uploads/market/`?
4. האם CDN/cache עלול לעכב קבצים שמתעדכנים יומית?
5. האם יש דרך לבצע purge לקבצים או לנתיב ספציפי?

## 15. ההמלצה הסופית

המערכת צריכה להיבנות כך:

- `PostgreSQL` מקומי כ-system of record
- filesystem ל-raw
- local admin חובה
- build אוטומטי יומי
- publish artifacts כקבצים סטטיים
- העלאה אוטומטית ב-FTPS
- וורדפרס כ-layer תצוגה בלבד

זה הפתרון הפשוט ביותר שמחזיק גם scale תפעולי וגם auditability.
