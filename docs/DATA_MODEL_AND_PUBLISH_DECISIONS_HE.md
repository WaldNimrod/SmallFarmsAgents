# מודל מידע והחלטות Publish

גרסה: 1.1  
תאריך: 2026-03-29  
שינויים מגרסה 1.0: PostgreSQL, users/audit_log/log_entries, basket as product, min_sample, stale TTL, manifest atomicity, platform_family, observation_flags table

## 1. מטרת המסמך

לנעול שלוש החלטות יסוד:

1. מהו מודל הנתונים המקומי הדרוש למערכת
2. איך המידע נשמר מקומית לאורך זמן
3. איך ה-publish לאתר הציבורי מתבצע אוטומטית וללא תלות ב-DB של וורדפרס

## 2. החלטות שנסגרו ב-v1.1

- ה-system of record הוא מקומי
- וורדפרס אינו data store
- האונליין יציג versioned artifacts + manifest
- יש חובה ל-`local admin` מ-V1 — כולל ניהול normalizer
- publish יומי אוטומטי
- `last good artifact + manifest_last_good.json`
- staleness: 3 ימים warning, 8 ימים stale
- `updated_at` ו-`staleness_level` מוטמעים ב-manifest
- **PostgreSQL** (לא SQLite)
- **Python + Flask**
- baskets = מוצרים עצמאיים
- min 2 observations מ-2 מקורות לפרסום
- publish threshold: min 2 community sources

## 3. בסיס נתונים מקומי

**PostgreSQL ישירות על המכשיר, ללא Docker.**

| שאלה | תשובה |
|---|---|
| מנוע | PostgreSQL 15+ |
| חיבור | `postgresql://smallfarms_app@localhost/smallfarms_local` |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |

Schema מלא: ראו `DATABASE_SCHEMA_SPEC_HE.md`

## 4. עקרון שמירת המידע המקומי

**Hybrid model:**
- PostgreSQL לנתונים מובנים
- filesystem ל-raw files ול-artifacts

## 5. מודל המידע — סיכום ישויות

### 5.1 שכבת יחידות ומוצרים

| טבלה | תיאור |
|---|---|
| `measurement_units` | קילוגרם, גרם, יחידה, צרור, basket types, pack types |
| `unit_conversions` | המרות מוגדרות (exact/heuristic/product_specific) |
| `products` | קטלוג קנוני. כולל `is_basket_product` flag |
| `product_aliases` | שמות חלופיים — global + per-source + per-normalizer |
| `product_variants` | צורות מסחר שונות של אותו מוצר |
| `product_merges` | איחוד מוצרים כפולים — data-driven, ב-DB |

**basket policy:** `is_basket_product=true` — לא נכנסים לאגרגציית ק"ג. aggregate נפרד.

### 5.2 שכבת מקורות

| טבלה | תיאור |
|---|---|
| `sources` | מקורות לוגיים, כולל `status`, `legal_review_required` |
| `source_fetch_profiles` | כולל `platform_family` — 'easyfarm', 'standalone', 'govt', 'aggregator' |

### 5.3 שכבת normalizer (data-driven)

| טבלה | תיאור |
|---|---|
| `normalizer_profiles` | type ו-config per source |
| `normalizer_rules` | חוקים: product_alias, unit_map, quantity_parse, organic_flag, ignore_pattern, benchmark_tag, basket_parse, price_correction |

כל שינוי ב-rules גורם לתוצאה שונה בריצה הבאה — ללא deploy.

### 5.4 שכבת ריצות ו-raw

| טבלה | תיאור |
|---|---|
| `ingestion_runs` | ריצה מערכתית — כולל `community_sources_succeeded` |
| `source_fetch_runs` | ריצה per מקור |
| `raw_assets` | metadata על קבצי raw + checksum |

### 5.5 שכבת extraction ו-normalization

| טבלה | תיאור |
|---|---|
| `raw_extracted_items` | פריטים גולמיים — כולל `normalizer_profile_id`, `extraction_status`, `unresolvable_reason` |
| `normalized_observations` | תצפיות מנורמלות — `confidence_score`, `flag_status`, `is_basket_product` |
| `observation_flags` | flags data-driven: hide/review לפי scope (single/source_product/all_from_source) |

### 5.6 שכבת aggregation

| טבלה | תיאור |
|---|---|
| `daily_aggregates` | כולל `weighted_avg_price`, `unweighted_avg_price`, `meets_publish_threshold`, `distinct_sources` |
| `weekly_snapshots` | כולל `data_completeness_pct` |

**min publish threshold per product:**
```
meets_publish_threshold = (sample_size >= 2 AND distinct_sources >= 2)
```

### 5.7 שכבת publish

| טבלה | תיאור |
|---|---|
| `publish_runs` | כולל `community_products`, `benchmark_products` |
| `publish_artifacts` | כולל `manifest_last_good_json` type |

### 5.8 שכבת ניהול ואבטחה (חדש ב-v1.1)

| טבלה | תיאור |
|---|---|
| `users` | Phase A: ריק. Phase B: admin יחיד |
| `audit_log` | כל פעולת admin/agent — `actor_name`, `before_state`, `after_state` |
| `log_entries` | לוגים מובנים ב-DB — level, module, entity, extra_json |

## 6. מבנה publish מומלץ

### artifacts ציבוריים

בכל publish:

- `manifest.json`
- `public_report-{version}.json`
- `public_report-{version}.html`
- `manifest_last_good.json` (עותק של manifest הקודם הטוב)

### תפקיד כל קובץ

#### `manifest.json`

```json
{
    "schema_version": "1.0",
    "artifact_version": "20260329-060000",
    "published_at": "2026-03-29T06:15:00+02:00",
    "json_path": "market/public_report-20260329-060000.json",
    "html_path": "market/public_report-20260329-060000.html",
    "staleness_level": "ok",
    "staleness_days": 0,
    "community_products": 18,
    "benchmark_products": 8,
    "status": "published"
}
```

**staleness_level** — מחושב בעת build, מוטמע ב-manifest:
- `ok`: פחות מ-3 ימים מהפרסום הטוב האחרון
- `warning`: 3–8 ימים
- `stale`: מעל 8 ימים

#### `public_report-{version}.json`

ה-data contract הציבורי — ראו schema בסעיף 7.

#### `public_report-{version}.html`

HTML עם JavaScript מוטמע minimal שקורא את ה-JSON ומציג.  
WP page template מוטמע את ה-HTML.

#### `manifest_last_good.json`

עותק של ה-manifest מהפרסום המוצלח האחרון לפני הנוכחי.  
WP renderer: אם manifest.json → artifact לא נגיש → fallback ל-manifest_last_good.json.

## 7. public_report.json schema

```json
{
    "schema_version": "1.0",
    "artifact_version": "20260329-060000",
    "generated_at": "2026-03-29T06:15:00+02:00",
    "community": {
        "date": "2026-03-29",
        "products": [
            {
                "code": "PRD001",
                "name": "עגבנייה",
                "category": "fruiting_vegetables",
                "is_basket": false,
                "price_unit": "kg",
                "avg_price": 14.8,
                "median_price": 14.2,
                "stddev_price": 1.9,
                "min_price": 12.5,
                "max_price": 18.0,
                "sample_size": 9,
                "distinct_sources": 5
            }
        ]
    },
    "benchmark": {
        "date": "2026-03-29",
        "products": [...]
    },
    "baskets": {
        "date": "2026-03-29",
        "products": [...]
    },
    "history": {
        "weeks": [...]
    }
}
```

**מה לא נכנס ל-JSON ציבורי:**
- source_name / source_url
- raw_values
- parser diagnostics
- confidence scores
- observation-level data
- internal IDs

## 8. upload mechanism

### נתיב ראשי: FTPS

```python
import ftplib

with ftplib.FTP_TLS(FTP_HOST) as ftp:
    ftp.login(FTP_USER, FTP_PASSWORD)
    ftp.prot_p()
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
```

### upload order (atomicity)

```
1. upload public_report-{version}.json
2. upload public_report-{version}.html
3. verify checksums (HTTP GET + compare)
4. upload manifest.json
5. upload manifest_last_good.json
```

אם שלב 1–3 נכשל — abort. לא לעדכן manifest.

## 9. WordPress rendering

WP page template קורא JavaScript מוטמע ב-HTML artifact:

```javascript
// embedded בתוך public_report-{version}.html
fetch('/wp-content/uploads/market/manifest.json')
    .then(r => r.json())
    .then(manifest => {
        if (manifest.status !== 'published') {
            return fetch('/wp-content/uploads/market/manifest_last_good.json')
                .then(r => r.json());
        }
        return manifest;
    })
    .then(manifest => {
        renderStalenessBanner(manifest.staleness_level, manifest.staleness_days);
        return fetch('/wp-content/uploads/' + manifest.json_path);
    })
    .then(r => r.json())
    .then(data => renderMarketData(data));
```

## 10. staleness banners — הגדרה טכנית

| staleness_level | UI |
|---|---|
| `ok` | ללא banner |
| `warning` | background: #FFF3CD, text: "המידע לא עודכן ב-N ימים. אנחנו עובדים על עדכון." |
| `stale` | background: #F8D7DA, text: "⚠ המידע הזה אינו עדכני ועשוי שלא לשקף מחירים נוכחיים." |

## 11. CDN / cache — טיפול

uPress עלול להחזיק cache על `/wp-content/uploads/`.

**הפתרון:**
- versioned filenames: `public_report-20260329-060000.json` — ה-URL חדש בכל publish
- WordPress renderer קורא תמיד `manifest.json` ואז את הURL שמצביע → URL חדש ≠ cache hit

**אם cache עדיין בעיה:** להוסיף query param:
```
/wp-content/uploads/market/manifest.json?v=20260329060000
```

## 12. failure behavior

| מצב | פעולה |
|---|---|
| upload נכשל | publish_run.status='upload_failed', נשאר עם manifest ישן |
| manifest לא עודכן | WP ממשיך להציג גרסה קודמת |
| artifact חדש לא נגיש | WP fallback ל-manifest_last_good.json |
| כל run נכשל | email alert + admin banner |
| staleness >= 3 | manifest.staleness_level='warning', banner ציבורי |
| staleness >= 8 | manifest.staleness_level='stale', banner אדום |

## 13. observability

- `log_entries` ב-DB — level, module, entity, run_id
- קבצי log: app, fetch, publish — rotation 90 ימים
- email alert: run failure, staleness >= 2 ימים
- admin Dashboard: סטטוס ריצה אחרונה, publish_runs, log_entries

## 14. מגבלות cache ו-CDN שצריך לאמת

1. האם `/wp-content/uploads/market/manifest.json` כפוף ל-CDN cache?
2. מה ה-TTL של cache על הנתיב?
3. האם אפשר לבצע cache purge לנתיב ספציפי?
4. האם overwrite אוטומטי של קבצים מותר ב-uPress?

אלו שאלות לבדיקות U07–U08 ב-`UPRESS_VALIDATION_PLAN_HE.md`.

## 15. ה-recommendation set המעודכן

1. **PostgreSQL** מקומי ללא Docker.
2. raw ו-artifacts על filesystem.
3. `local web admin` חובה מ-V1, כולל **normalizer management**.
4. admin מקומי לניטור, logs, QA, publish, normalizer.
5. public publish: `manifest.json + versioned public_report.json + html`.
6. upload אוטומטי יומי ב-`FTPS` (לאחר proof test).
7. `manifest_last_good.json` חובה לצד `manifest.json`.
8. `staleness_level` ב-manifest, banners בציבורי.
9. benchmark + baskets מופרדים ויזואלית.
10. email alert על כשל / staleness.
11. `users` + `audit_log` + `log_entries` ב-schema מהיום הראשון.
12. `normalizer_rules` + `product_merges` + `observation_flags` — data-driven, ניהול ב-DB.
