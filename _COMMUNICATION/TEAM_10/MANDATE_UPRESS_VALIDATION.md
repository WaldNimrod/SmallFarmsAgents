# Mandate — Team 10 / Team 20: uPress Validation (Gate G7)
**From:** Team 100 (Architecture)  
**Date:** 2026-03-29  
**Updated:** 2026-03-29  
**Priority:** ~~Critical pre-development gate~~ → **DEFERRED to M7 (Go-Live)**  
**Gate:** G7 (formerly G0)  
**Spec document:** `docs/UPRESS_VALIDATION_PLAN_HE.md`

> **ARCHITECTURE NOTE — 2026-03-29**
>
> This mandate is **deferred to M7** by Nimrod's decision.
> Reason: We start with the local system implementation and a temporary local
> viewer. uPress validation will be executed only as part of the Go-Live process (M7).
>
> **Do not execute the tests in this document before Gate G6 is open.**
> See `_COMMUNICATION/ROADMAP.md` for the correct execution order.

---

## מה זה המנדט הזה

זהו מנדט הביצוע הראשון של צוות 10. אין לכתוב קוד publish pipeline לפני שהמנדט הזה הושלם ושער G0 נפתח על ידי צוות 50.

**מה בסיכון:** אם FTPS לא זמין, או cache מונע עדכון יומי, או נתיב ה-upload חסום — ארכיטקטורת ה-publish כולה משתנה. לכן — בדיקה ראשונה.

---

## [USER ACTION REQUIRED] — לפני שצוות 10 יכול להתחיל

### נמרוד — נדרשים ממך הפרטים הבאים:

| מה | היכן למצוא | נדרש ל |
|----|-----------|--------|
| **FTP Host** | uPress cPanel → FTP Accounts | בדיקות U01-U06 |
| **FTP Username** | uPress cPanel → FTP Accounts | בדיקות U01-U06 |
| **FTP Password** | uPress cPanel → FTP Accounts (הגדר אם חסר) | בדיקות U01-U06 |
| **נתיב uploads** | uPress cPanel → File Manager → `public_html/wp-content/uploads/` | ולידציית write path |
| **URL ציבורי לאישור** | בדרך כלל `https://nimrod.bio/wp-content/uploads/` | בדיקת U07 |
| **גישה ל-WordPress admin** | `https://nimrod.bio/wp-admin` | בדיקות U09, U10 |

### כיצד להגדיר FTP ב-uPress (אם אין חשבון):

1. כנס ל-uPress cPanel
2. חפש "FTP Accounts" (או "חשבונות FTP")
3. צור חשבון FTP חדש:
   - שם משתמש: `smallfarms` (המלצה)
   - ספריית בית: `/public_html/wp-content/uploads/market` (הגבל לנתיב זה בלבד)
   - סיסמה: חזקה, שמור בסביבת משתנים מקומיים
4. שמור: `Host`, `Username (full)`, `Password`, `Port` (בדרך כלל 21)
5. העבר לצוות 10 דרך `.env` מקומי (אל תשלח בצ'אט)

### הגדרת `.env` מקומי לצוות 10:

```bash
# /Users/nimrod/Documents/SmallFarmsAgents/.env  (לא ב-git!)
UPRESS_FTP_HOST=ftp.nimrod.bio        # החלף בערך הנכון
UPRESS_FTP_USER=smallfarms@nimrod.bio # החלף בערך הנכון
UPRESS_FTP_PASS=your_password_here    # החלף בערך הנכון
UPRESS_FTP_PORT=21
UPRESS_PUBLIC_BASE=https://nimrod.bio
UPRESS_UPLOAD_PATH=wp-content/uploads/market
```

**לאחר שתעביר ל-`.env` — שלח לצוות 10 הודעה שהמנדט יכול להתחיל.**

---

## תוכנית עבודה לצוות 10 — שלב אחר שלב

### שלב 0: הכנה (לפני כל בדיקה)

```bash
# וודא Python dependencies
pip install httpx ftputil python-dotenv

# צור תיקיית הבדיקות
mkdir -p /Users/nimrod/Documents/SmallFarmsAgents/tests/upress_validation

# צור .gitignore כדי לא לדחוף .env
echo ".env" >> /Users/nimrod/Documents/SmallFarmsAgents/.gitignore
echo "*.log" >> /Users/nimrod/Documents/SmallFarmsAgents/.gitignore
```

### שלב 1: File Transport (U01–U04) — חובה ראשון

**מטרה:** ולידציה שניתן להעלות קבצים ל-uPress ב-FTPS.

#### קובץ בדיקה: `tests/upress_validation/test_ftp_transport.py`

```python
"""
uPress Validation — שלב 1: File Transport
Tests: U01 (FTP login), U02 (FTPS), U03 (write path), U04 (overwrite)
"""
import ftplib
import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('UPRESS_FTP_HOST')
USER = os.getenv('UPRESS_FTP_USER')
PASS = os.getenv('UPRESS_FTP_PASS')
PORT = int(os.getenv('UPRESS_FTP_PORT', 21))
UPLOAD_PATH = os.getenv('UPRESS_UPLOAD_PATH', 'wp-content/uploads/market')

RESULTS = {}


def _make_ftp():
    """מחזיר חיבור FTPS מאומת."""
    ftp = ftplib.FTP_TLS()
    ftp.connect(HOST, PORT, timeout=30)
    ftp.login(USER, PASS)
    ftp.prot_p()  # encrypted data channel
    return ftp


def test_u01_ftp_login():
    """U01: FTP login works."""
    try:
        ftp = ftplib.FTP()
        ftp.connect(HOST, PORT, timeout=30)
        ftp.login(USER, PASS)
        ftp.quit()
        RESULTS['U01'] = 'PASS'
        print("✅ U01: FTP login — PASS")
    except Exception as e:
        RESULTS['U01'] = f'FAIL: {e}'
        print(f"❌ U01: FTP login — FAIL: {e}")
        print("   ACTION: פנה לתמיכת uPress — ייתכן שחשבון FTP לא הוגדר")
        raise


def test_u02_ftps():
    """U02: FTPS encrypted channel works."""
    try:
        ftp = _make_ftp()
        ftp.quit()
        RESULTS['U02'] = 'PASS'
        print("✅ U02: FTPS encrypted channel — PASS")
    except ftplib.error_perm as e:
        RESULTS['U02'] = f'FAIL: {e}'
        print(f"⚠️  U02: FTPS not supported — FAIL: {e}")
        print("   FALLBACK: ניתן להמשיך עם FTP רגיל אם uPress לא תומכים ב-FTPS")
        print("   ACTION: תעד ב-report ובקש אישור ארכיטקטורה (צוות 100)")


def test_u03_write_path():
    """U03: Can write to uploads/market path."""
    test_file = Path('/tmp/sf_test_write.txt')
    test_file.write_text('smallfarms validation test', encoding='utf-8')
    try:
        ftp = _make_ftp()
        try:
            ftp.mkd(UPLOAD_PATH)
        except ftplib.error_perm:
            pass  # likely already exists
        with open(test_file, 'rb') as f:
            ftp.storbinary(f'STOR {UPLOAD_PATH}/sf_test_write.txt', f)
        ftp.quit()
        RESULTS['U03'] = 'PASS'
        print(f"✅ U03: write to {UPLOAD_PATH} — PASS")
    except Exception as e:
        RESULTS['U03'] = f'FAIL: {e}'
        print(f"❌ U03: write path — FAIL: {e}")
        print("   ACTION: בדוק נתיב חלופי או פנה לתמיכה")
        raise


def test_u04_overwrite():
    """U04: Overwriting an existing file works."""
    test_file = Path('/tmp/sf_test_overwrite.txt')
    test_file.write_text('version 1', encoding='utf-8')
    remote_name = f'{UPLOAD_PATH}/sf_test_overwrite.txt'
    try:
        ftp = _make_ftp()
        with open(test_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote_name}', f)
        test_file.write_text('version 2', encoding='utf-8')
        with open(test_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote_name}', f)
        ftp.quit()
        RESULTS['U04'] = 'PASS'
        print("✅ U04: overwrite — PASS")
    except Exception as e:
        RESULTS['U04'] = f'FAIL: {e}'
        print(f"⚠️  U04: overwrite — FAIL: {e}")
        print("   MITIGATION: נעבור ל-versioned files בלבד (כבר מתוכנן)")


if __name__ == '__main__':
    print("=" * 60)
    print("uPress Validation — שלב 1: File Transport")
    print("=" * 60)
    test_u01_ftp_login()
    test_u02_ftps()
    test_u03_write_path()
    test_u04_overwrite()
    print("\n--- תוצאות שלב 1 ---")
    for k, v in RESULTS.items():
        status = "✅" if v == "PASS" else "❌"
        print(f"  {status} {k}: {v}")
    if all(v == 'PASS' for v in RESULTS.values()):
        print("\n✅ שלב 1 הושלם — ממשיכים לשלב 2")
    else:
        print("\n❌ שלב 1 נכשל — STOP. פנה לתמיכת uPress לפני המשך")
```

---

### שלב 2: Publish Contract (U05–U06, U11)

**מטרה:** ולידציה שמודל versioned artifacts ו-manifest עובדים.

#### קובץ בדיקה: `tests/upress_validation/test_publish_contract.py`

```python
"""
uPress Validation — שלב 2: Publish Contract
Tests: U05 (versioned files), U06 (manifest update), U11 (last-good fallback)
"""
import ftplib, os, json, time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('UPRESS_FTP_HOST')
USER = os.getenv('UPRESS_FTP_USER')
PASS = os.getenv('UPRESS_FTP_PASS')
PORT = int(os.getenv('UPRESS_FTP_PORT', 21))
UPLOAD_PATH = os.getenv('UPRESS_UPLOAD_PATH', 'wp-content/uploads/market')
PUBLIC_BASE = os.getenv('UPRESS_PUBLIC_BASE', 'https://nimrod.bio')

RESULTS = {}

# Test data — artifacts ניסיון
VERSION_TS = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
ARTIFACT_VERSION = f'test-{VERSION_TS}'

TEST_REPORT = {
    "schema_version": "1.0",
    "artifact_version": ARTIFACT_VERSION,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "community": {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "products": [
            {
                "code": "PRD001", "name": "עגבנייה",
                "category": "fruiting_vegetables", "is_basket": False,
                "price_unit": "kg", "avg_price": 14.8, "median_price": 14.2,
                "stddev_price": 1.9, "min_price": 12.5, "max_price": 18.0,
                "sample_size": 9, "distinct_sources": 5
            }
        ]
    },
    "benchmark": {"date": datetime.now(timezone.utc).date().isoformat(), "products": []},
    "baskets": {"date": datetime.now(timezone.utc).date().isoformat(), "products": []}
}

TEST_MANIFEST = {
    "schema_version": "1.0",
    "artifact_version": ARTIFACT_VERSION,
    "published_at": datetime.now(timezone.utc).isoformat(),
    "json_path": f"market/public_report-{ARTIFACT_VERSION}.json",
    "html_path": f"market/public_report-{ARTIFACT_VERSION}.html",
    "staleness_level": "ok",
    "staleness_days": 0,
    "community_products": 1,
    "benchmark_products": 0,
    "status": "published"
}


def _make_ftp():
    ftp = ftplib.FTP_TLS()
    ftp.connect(HOST, PORT, timeout=30)
    ftp.login(USER, PASS)
    ftp.prot_p()
    return ftp


def _upload_json(ftp, data: dict, remote_name: str):
    import io
    content = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    ftp.storbinary(f'STOR {UPLOAD_PATH}/{remote_name}', io.BytesIO(content))


def test_u05_versioned_files():
    """U05: versioned artifact files are accessible."""
    try:
        ftp = _make_ftp()
        _upload_json(ftp, TEST_REPORT, f'public_report-{ARTIFACT_VERSION}.json')
        ftp.quit()
        RESULTS['U05'] = 'PASS'
        print(f"✅ U05: versioned file upload — PASS (version: {ARTIFACT_VERSION})")
    except Exception as e:
        RESULTS['U05'] = f'FAIL: {e}'
        print(f"❌ U05: versioned files — FAIL: {e}")


def test_u06_manifest_update():
    """U06: manifest.json updated last, points to correct version."""
    try:
        ftp = _make_ftp()
        _upload_json(ftp, TEST_MANIFEST, 'manifest.json')
        _upload_json(ftp, TEST_MANIFEST, 'manifest_last_good.json')
        ftp.quit()
        RESULTS['U06'] = 'PASS'
        print("✅ U06: manifest update — PASS")
    except Exception as e:
        RESULTS['U06'] = f'FAIL: {e}'
        print(f"❌ U06: manifest update — FAIL: {e}")


def test_u11_last_good_fallback():
    """U11: manifest_last_good.json survives a failed manifest write."""
    try:
        import io, httpx
        # שמור manifest_last_good לפני
        ftp = _make_ftp()
        good_manifest = {**TEST_MANIFEST, "status": "last_good"}
        _upload_json(ftp, good_manifest, 'manifest_last_good.json')
        # העמד פנים שכתיבת manifest.json נכשלה (כותבים JSON שגוי)
        ftp.storbinary('STOR ' + UPLOAD_PATH + '/manifest.json',
                       io.BytesIO(b'{"broken": true}'))
        ftp.quit()
        # בדוק שlast_good עדיין תקין
        url = f"{PUBLIC_BASE}/wp-content/uploads/market/manifest_last_good.json"
        resp = httpx.get(url, timeout=10)
        data = resp.json()
        assert data.get('status') == 'last_good', f"expected last_good, got {data}"
        RESULTS['U11'] = 'PASS'
        print("✅ U11: last-good fallback — PASS")
    except Exception as e:
        RESULTS['U11'] = f'FAIL: {e}'
        print(f"❌ U11: last-good fallback — FAIL: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("uPress Validation — שלב 2: Publish Contract")
    print("=" * 60)
    test_u05_versioned_files()
    test_u06_manifest_update()
    test_u11_last_good_fallback()
    print("\n--- תוצאות שלב 2 ---")
    for k, v in RESULTS.items():
        status = "✅" if v == "PASS" else "❌"
        print(f"  {status} {k}: {v}")
```

---

### שלב 3: Public Rendering (U07–U10)

**מטרה:** ולידציה שקבצים נגישים ציבורית וWordPress יכול לרנדר אותם.

#### קובץ בדיקה: `tests/upress_validation/test_public_rendering.py`

```python
"""
uPress Validation — שלב 3: Public Rendering
Tests: U07 (public access), U08 (cache TTL), U09 (HTML render), U10 (JSON render)
"""
import httpx, os, time
from dotenv import load_dotenv

load_dotenv()

PUBLIC_BASE = os.getenv('UPRESS_PUBLIC_BASE', 'https://nimrod.bio')
UPLOAD_PATH = os.getenv('UPRESS_UPLOAD_PATH', 'wp-content/uploads/market')

RESULTS = {}


def test_u07_public_access():
    """U07: uploaded file accessible via public HTTP."""
    url = f"{PUBLIC_BASE}/wp-content/uploads/market/sf_test_write.txt"
    try:
        resp = httpx.get(url, timeout=15)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        RESULTS['U07'] = 'PASS'
        print(f"✅ U07: public access — PASS ({resp.status_code})")
    except Exception as e:
        RESULTS['U07'] = f'FAIL: {e}'
        print(f"❌ U07: public access — FAIL: {e}")
        print("   בדוק: file permissions, WordPress file blocking, .htaccess rules")
        raise


def test_u08_cache_ttl():
    """U08: measure cache TTL — informational only."""
    import ftplib, io
    from dotenv import load_dotenv
    HOST = os.getenv('UPRESS_FTP_HOST')
    USER = os.getenv('UPRESS_FTP_USER')
    PASS = os.getenv('UPRESS_FTP_PASS')
    PORT = int(os.getenv('UPRESS_FTP_PORT', 21))
    url = f"{PUBLIC_BASE}/wp-content/{UPLOAD_PATH}/sf_cache_test.txt"

    # upload קובץ חדש
    ftp = ftplib.FTP_TLS()
    ftp.connect(HOST, PORT, timeout=30)
    ftp.login(USER, PASS)
    ftp.prot_p()
    ts = str(time.time()).encode()
    ftp.storbinary(f'STOR {UPLOAD_PATH}/sf_cache_test.txt', io.BytesIO(ts))
    upload_time = time.time()
    ftp.quit()

    # poll עד שמקבלים את הערך החדש
    max_wait = 120  # seconds
    interval = 10
    for _ in range(max_wait // interval):
        try:
            resp = httpx.get(url, timeout=10)
            if resp.text.strip() == ts.decode():
                ttl_observed = time.time() - upload_time
                RESULTS['U08'] = f'PASS — cache TTL ≈ {ttl_observed:.0f}s'
                print(f"✅ U08: cache TTL ≈ {ttl_observed:.0f}s")
                return
        except Exception:
            pass
        time.sleep(interval)

    RESULTS['U08'] = 'INFO — CDN cache TTL > 120s. Document and proceed.'
    print("⚠️  U08: cache delay > 2 min. Versioned filenames mitigate this.")


def test_u09_wordpress_html_render():
    """U09: WordPress page renders HTML artifact.
    
    ידני — צוות 10 יוצר עמוד ניסוי ב-WordPress admin ומוסיף Custom HTML block:
    <div id='sf-market'></div>
    <script>
      fetch('/wp-content/uploads/market/manifest.json')
        .then(r=>r.json())
        .then(m=>fetch('/wp-content/uploads/'+m.json_path))
        .then(r=>r.json())
        .then(data=>document.getElementById('sf-market').innerHTML=
          '<p>'+data.community.products.length+' products loaded</p>')
    </script>
    
    לאחר שהעמוד פורסם — בדוק ידנית בדפדפן.
    """
    url = f"{PUBLIC_BASE}/?p=sf-validation-test"
    try:
        resp = httpx.get(url, timeout=15)
        if resp.status_code == 404:
            RESULTS['U09'] = 'PENDING — WordPress test page not yet created'
            print("⚠️  U09: test page not found — צור עמוד ניסוי ב-WordPress")
            print("   ראה הוראות בתוך הפונקציה test_u09_wordpress_html_render")
            return
        assert resp.status_code == 200
        RESULTS['U09'] = 'PASS — page accessible, verify content manually'
        print("✅ U09: WordPress page accessible — verify rendering manually")
    except Exception as e:
        RESULTS['U09'] = f'FAIL: {e}'
        print(f"❌ U09: WordPress render — FAIL: {e}")


def test_u10_wordpress_json_render():
    """U10: manifest.json + report JSON accessible and valid."""
    manifest_url = f"{PUBLIC_BASE}/wp-content/uploads/market/manifest.json"
    try:
        resp = httpx.get(manifest_url, timeout=15)
        assert resp.status_code == 200, f"manifest not accessible: {resp.status_code}"
        data = resp.json()
        assert 'artifact_version' in data
        assert 'json_path' in data
        report_url = f"{PUBLIC_BASE}/wp-content/uploads/{data['json_path']}"
        resp2 = httpx.get(report_url, timeout=15)
        assert resp2.status_code == 200
        report = resp2.json()
        assert 'community' in report
        RESULTS['U10'] = 'PASS'
        print("✅ U10: JSON render — PASS")
    except Exception as e:
        RESULTS['U10'] = f'FAIL: {e}'
        print(f"❌ U10: JSON render — FAIL: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("uPress Validation — שלב 3: Public Rendering")
    print("=" * 60)
    test_u07_public_access()
    test_u08_cache_ttl()
    test_u09_wordpress_html_render()
    test_u10_wordpress_json_render()
    print("\n--- תוצאות שלב 3 ---")
    for k, v in RESULTS.items():
        status = "✅" if "PASS" in str(v) else ("⚠️" if "PENDING" in str(v) or "INFO" in str(v) else "❌")
        print(f"  {status} U{k[-2:]}: {v}")
```

---

### שלב 4: Unattended Run (U12)

**מטרה:** ולידציה שהתהליך כולו יכול לרוץ ב-cron ללא מגע יד אדם.

#### קובץ בדיקה: `tests/upress_validation/test_unattended_run.py`

```python
"""
uPress Validation — שלב 4: Unattended Daily Run
Test: U12
"""
import subprocess, os, time, httpx
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

PUBLIC_BASE = os.getenv('UPRESS_PUBLIC_BASE', 'https://nimrod.bio')
RESULTS = {}


def test_u12_unattended_run():
    """U12: Full upload cycle runs unattended via script."""
    print("U12: הרץ את test_ftp_transport.py + test_publish_contract.py כ-subprocess")
    print("     וודא שהם רצים ללא input ידני, ומחזירים exit code 0")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = ['test_ftp_transport.py', 'test_publish_contract.py']
    all_passed = True
    for script in scripts:
        path = os.path.join(script_dir, script)
        result = subprocess.run(['python', path], capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"❌ U12: {script} failed:\n{result.stderr}")
            all_passed = False
        else:
            print(f"✅ U12: {script} — exit 0")

    # ולידציה שהתוצאה ניגשת ציבורית
    url = f"{PUBLIC_BASE}/wp-content/uploads/market/manifest.json"
    resp = httpx.get(url, timeout=15)
    if resp.status_code == 200:
        print(f"✅ U12: manifest publicly accessible after unattended run")
    else:
        all_passed = False
        print(f"❌ U12: manifest not accessible after run: {resp.status_code}")

    RESULTS['U12'] = 'PASS' if all_passed else 'FAIL'
    print(f"\n{'✅' if all_passed else '❌'} U12: Unattended run — {'PASS' if all_passed else 'FAIL'}")


if __name__ == '__main__':
    print("=" * 60)
    print("uPress Validation — שלב 4: Unattended Daily Run")
    print("=" * 60)
    test_u12_unattended_run()
```

---

## כיצד לדווח תוצאות (חובה)

לאחר ביצוע כל שלב, כתוב דוח ב:
`_COMMUNICATION/TEAM_10/reports/2026-MM-DD_UPRESS_VALIDATION_TEAM10.md`

**תבנית דוח:**

```markdown
# Team 10 — uPress Validation Results
**תאריך:** YYYY-MM-DD  
**שלב:** G0 — uPress FTP Validation  
**סטטוס:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

## תוצאות לפי Test ID

| Test ID | נושא | תוצאה | פרטים |
|---------|------|--------|--------|
| U01 | FTP login | ✅/❌ | [פרטים] |
| U02 | FTPS | ✅/❌/⚠️ | [פרטים] |
| U03 | write path | ✅/❌ | [פרטים] |
| U04 | overwrite | ✅/❌ | [פרטים] |
| U05 | versioned files | ✅/❌ | [פרטים] |
| U06 | manifest update | ✅/❌ | [פרטים] |
| U07 | public access | ✅/❌ | [פרטים] |
| U08 | cache TTL | ⚠️ INFO | [TTL בפועל] |
| U09 | HTML render | ✅/❌/⚠️ | [פרטים] |
| U10 | JSON render | ✅/❌ | [פרטים] |
| U11 | last-good fallback | ✅/❌ | [פרטים] |
| U12 | unattended run | ✅/❌ | [פרטים] |

## ממצאים קריטיים
[מה נכשל ומה מחייב שינוי ארכיטקטורה]

## המלצה ל-Publish Architecture
[FTP / FTPS / SFTP / HTTP endpoint / fallback]

## [USER ACTION REQUIRED] (אם רלוונטי)
[מה נמרוד צריך לעשות]

## בקשה לפתיחת שער G0
[בקשה לצוות 50 לאמת ולאשר]
```

---

## קריטריוני Gate G0 — פתיחה

**שער G0 נפתח כאשר:**
- ✅ U01, U02, U03 עברו (FTP/FTPS + write path)
- ✅ U07 עבר (public access)
- ✅ U06 עבר (manifest update)
- ℹ️ U08 — מתועד (לא חוסם)
- ✅ U09 או U10 — לפחות אחד מהם עבר (WordPress rendering)
- ✅ U12 עבר (unattended run)

**אם U01 נכשל:**
→ STOP — עדכן דוח עם `[USER ACTION REQUIRED]` ובקש מנמרוד לפנות לתמיכת uPress

**אם U02 נכשל (לא תומך FTPS):**
→ המשך עם FTP רגיל + תעד ב-report + בקש אישור מצוות 100

**אם U07 נכשל (לא גישה ציבורית):**
→ בדוק WordPress file permissions + .htaccess + עדכן report עם `[USER ACTION REQUIRED]`

---

## מותר להתחיל במקביל (לא תלוי ב-G0)

בעוד uPress validation רץ, צוות 10 יכול להתחיל את השלבים הבאים **במקביל**:
- ✅ DB schema + Alembic migrations (G1)
- ✅ Product catalog seed data
- ✅ Collectors framework (ללא publish)
- ✅ NormalizerEngine skeleton
- ✅ Admin UI בסיסי (Flask)

**אסור לממש PublishEngine עד שG0 נפתח.**
