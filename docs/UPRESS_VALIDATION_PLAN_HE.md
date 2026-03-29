# תכנית ולידציה ל-uPress

גרסה: 1.1  
תאריך: 2026-03-29  
**שינוי מרכזי מ-v1.0: תכנית זו היא שלב מקדים חובה לפני כל פיתוח. לא שלב לקראת סוף.**

---

## 1. מעמד המסמך — שלב מקדים

בדיקות אלו **חייבות להתבצע ולהסתיים לפני כתיבת publish pipeline.**

הסיבה: אם FTPS לא זמין, או cache מונע עדכון יומי, או נתיב הkupload חסום — יש צורך בשינוי ארכיטקטורת publish לפני שקוד נכתב.

**קריטריון לסיום שלב מקדים:**
- בדיקות U01–U06 עברו בהצלחה
- ידוע מה CDN/cache TTL על נתיב uploads/market
- מנגנון rendering ב-WordPress נבחר ואומת

אם בדיקות U01–U03 נכשלות — **פנייה לתמיכת uPress לפני המשך.**

---

## 2. רקע

המערכת מתוכננת כך:

- מנוע הנתונים רץ מקומית (Python)
- ה-admin רץ מקומית (Flask)
- השרת הציבורי של `nimrod.bio` מציג artifacts סטטיים בלבד
- אין שימוש ב-DB של וורדפרס

הנתיב המרכזי לאימות:

`local build → FTPS upload → public file serving → WordPress rendering`

---

## 3. מה ידוע כיום ממקורות ציבוריים של uPress

נכון ל-2026-03-29:

- קיימת תמיכה בחשבונות FTP דרך הפאנל: [כיצד להעלות ולהוריד קבצים באמצעות FTP](https://support.upress.co.il/dev/how-to-use-ftp/)
- קיימת תיעוד ל-build מקומי ו-upload לשרת: [התקנת חבילות NPM](https://support.upress.co.il/advanced/npm-install/)
- קיימת תיעוד לאבטחה: [קטגוריית אבטחה](https://support.upress.co.il/category/security/)

**לא אושר ציבורית:**
- FTPS בפועל עבור החשבון הקיים
- cache/CDN TTL על uploads/market
- overwrite אוטומטי בנתיב publish ייעודי
- SSH

---

## 4. שאלת ההכרעה

האם אפשר לממש על uPress מסלול `daily unattended publish` פשוט, אמין ונטול עבודה ידנית, המבוסס על artifacts סטטיים?

---

## 5. Strategy

### נתיב בדיקה ראשי

1. FTPS automated upload
2. versioned artifacts + manifest
3. WordPress page template rendering

### נתיבי fallback אם ראשי נכשל

1. SFTP/SSH — אם uPress מאשרים
2. endpoint-based upload (HTTP POST) — דורש plugin פשוט בWP
3. אם הכל נכשל — פנייה לתמיכת uPress לתמיכה ב-webhook/cron pull

---

## 6. Test Matrix — עדכון v1.1

| Test ID | נושא | מטרה | שיטה | קריטריון הצלחה | אם נכשל |
|---|---|---|---|---|---|
| U01 | FTP login | אישור גישה אוטומטית | Python ftplib חיבור סקריפטי | חיבור יציב | פנה לתמיכת uPress |
| U02 | FTPS support | הצפנת תעבורה | חיבור FTP_TLS | upload ב-FTPS | fallback ל-FTP רגיל |
| U03 | write path | אישור נתיב publish | upload ל-`uploads/market/` | קובץ נוצר בנתיב | נסה נתיב חלופי |
| U04 | overwrite | אישור update יומי | upload חוזר לאותו שם | הקובץ מוחלף | מעבר ל-versioned files בלבד |
| U05 | versioned files | מודל versioned artifacts | upload `public_report-{ts}.json` | קבצים חדשים נגישים | בדוק naming constraints |
| U06 | manifest update | החלפת גרסה | upload artifacts → manifest אחרון | manifest מצביע לגרסה החדשה | חזק order/retry |
| U07 | public access | הגשה ב-HTTP | `curl` או browser | קובץ נגיש ציבורית | בדוק permissions |
| U08 | cache delay | cache TTL | overwrite + check after N minutes | ניתן לעמוד ב-SLA יומי | versioned names (כבר מוגן) |
| U09 | WordPress HTML render | embed HTML artifact | עמוד ניסוי + template | HTML נטען יציב | fallback ל-JSON-only |
| U10 | WordPress JSON render | JavaScript fetch JSON | template/block פשוט | JSON נקרא ומוצג | fallback ל-HTML-only |
| U11 | last-good fallback | הגן על הציבור | כשל יזום + check | הציבור רואה גרסה קודמת | חזק manifest policy |
| U12 | unattended daily run | אוטומציה מלאה | cron מקומי Python + upload + verify | ללא מגע יד אדם | תקן orchestration |

---

## 7. סדר ביצוע — שלב מקדים

### שלב 1: File transport (חובה ראשון)

- U01 — FTP login
- U02 — FTPS support
- U03 — write path
- U04 — overwrite

**אם U01–U03 נכשלים — STOP. פנה לתמיכת uPress לפני המשך.**

### שלב 2: Publish contract

- U05 — versioned files
- U06 — manifest update
- U11 — last-good fallback

### שלב 3: Public rendering

- U07 — public access
- U08 — cache delay (תיעוד בלבד; versioned names מטפלים)
- U09 — WordPress HTML render
- U10 — WordPress JSON render

### שלב 4: Ops validation

- U12 — unattended daily run

---

## 8. Test Data

```json
// manifest_test.json
{
    "schema_version": "1.0",
    "artifact_version": "test-v1",
    "published_at": "2026-03-29T10:00:00+02:00",
    "json_path": "market/public_report-test-v1.json",
    "html_path": "market/public_report-test-v1.html",
    "staleness_level": "ok",
    "staleness_days": 0,
    "community_products": 3,
    "benchmark_products": 2,
    "status": "published"
}
```

```json
// public_report-test-v1.json
{
    "schema_version": "1.0",
    "artifact_version": "test-v1",
    "generated_at": "2026-03-29T10:00:00+02:00",
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
    "benchmark": {"date": "2026-03-29", "products": []},
    "baskets": {"date": "2026-03-29", "products": []}
}
```

---

## 9. Python test script

```python
# tests/upress_validation/test_ftp.py
import ftplib
import os

FTP_HOST = os.getenv('UPRESS_FTP_HOST')
FTP_USER = os.getenv('UPRESS_FTP_USER')
FTP_PASS = os.getenv('UPRESS_FTP_PASS')
UPLOAD_PATH = 'wp-content/uploads/market'

def test_u01_ftp_login():
    with ftplib.FTP_TLS(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        print("✓ U01: FTP login success")

def test_u02_ftps():
    with ftplib.FTP_TLS(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()  # encrypted data channel
        print("✓ U02: FTPS encrypted channel OK")

def test_u03_write_path():
    with ftplib.FTP_TLS(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()
        with open('/tmp/test_upload.txt', 'wb') as f:
            f.write(b'smallfarms test')
        with open('/tmp/test_upload.txt', 'rb') as f:
            ftp.storbinary(f'STOR {UPLOAD_PATH}/test_upload.txt', f)
        print(f"✓ U03: write to {UPLOAD_PATH} success")

def test_u07_public_access():
    import httpx
    url = f"https://nimrod.bio/wp-content/uploads/market/test_upload.txt"
    resp = httpx.get(url, timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"✓ U07: public access OK, status={resp.status_code}")

if __name__ == '__main__':
    test_u01_ftp_login()
    test_u02_ftps()
    test_u03_write_path()
    test_u07_public_access()
    print("\nAll basic tests passed. Proceed to U04-U06.")
```

---

## 10. fallback plan — אם הנתיב הראשי נכשל

### fallback 1: FTP → SFTP/SSH

```python
import paramiko  # pip install paramiko

ssh = paramiko.SSHClient()
ssh.connect(FTP_HOST, username=FTP_USER, password=FTP_PASS)
sftp = ssh.open_sftp()
sftp.put(local_path, remote_path)
```

דורש: uPress מאשרים SSH בחבילה.

### fallback 2: HTTP endpoint push

```python
# WordPress plugin קטן שמקבל POST עם artifact
import httpx

response = httpx.post(
    'https://nimrod.bio/wp-json/smallfarms/v1/publish',
    headers={'Authorization': f'Bearer {WP_API_KEY}'},
    files={'artifact': open(local_path, 'rb')}
)
```

דורש: WordPress plugin קטן (30–50 שורות PHP).

### fallback 3: GitHub Actions / external storage

- upload ל-GitHub repository (public/private)
- WordPress קורא מ-raw.githubusercontent.com
- פחות אידיאלי אבל עובד ללא תלות ב-uPress

---

## 11. output נדרש מהבדיקות

בסיום תהליך הוולידציה — מסמך תוצאות:

- מה עבד
- מה לא עבד
- CDN/cache TTL בפועל
- מנגנון upload מאושר
- נתיב publish מאושר
- מודל cache busting מאושר
- אם נדרש fallback — איזה

---

## 12. Gate לפיתוח

**לא להתחיל פיתוח publish pipeline לפני:**

1. U01–U03 הצליחו
2. U07 הצליח (public access)
3. CDN TTL ידוע

**מותר להתחיל במקביל (לא תלוי ב-uPress):**
- collectors
- parsers
- normalizer engine
- aggregator
- admin UI (Flask)
- DB schema + migrations
