# RESPONSE: nimrod-bio Finding — `Agents/` Path — FINAL (Supersedes v1)

**From:** team_100 (Chief Architect) — SmallFarmsAgents  
**To:** nimrod-bio team (originator of finding)  
**Date:** 2026-05-11  
**Ref:** `FINDING_AGENTS_PATH_UPRESS_2026-05-10_v1.md`  
**Status:** CLOSED — finding resolved, prior document superseded  

---

## תיקון לדוקומנט הקודם

מסמך `FINDING_AGENTS_PATH_UPRESS_2026-05-10_v1.md` הסיק שיש להוסיף `/Agents` ל-`UPRESS_PUBLIC_BASE`. **מסקנה זו שגויה** — נסתרה ע"י smoke-test שבוצע ב-2026-05-11 במסגרת פריסת WP009.

---

## 1. הממצא המקורי (nimrod-bio)

קבצים נמצאו בגיבוי ב:
```
https://nimrod.bio/Agents/wp-content/uploads/market/
```
שאלה: האם `/Agents/` (capital A) מכוון? מה הURL הקאנוני?

---

## 2. התשובה הסופית — מבוססת smoke-test

### מבנה השרת האמיתי

| שכבה | ערך |
|------|-----|
| FTP root עבור `mezoohost@nimrod.bio` | תיקיית root של WordPress |
| Document root של `nimrod.bio` | **אותה תיקייה** — FTP root = domain root |
| `/Agents/` בpath | שם תיקייה פנימי על filesystem של uPress — **לא מופיע ב-URL** |

### אימות (smoke-test, 2026-05-11)

```
POST /wp-json/sfagent/v1/upload  →  201 Created
קובץ נכתב ל: ABSPATH/smallfarmsagents/market/sfagent-smoke-test.json

בדיקת גישה ציבורית:
  404  https://nimrod.bio/Agents/smallfarmsagents/market/sfagent-smoke-test.json
  200  https://nimrod.bio/smallfarmsagents/market/sfagent-smoke-test.json  ✓
```

### מסקנה

`/Agents/` **אינו** חלק מה-URL הציבורי. הוא שם תיקייה על ה-filesystem של uPress בלבד.

---

## 3. מה היו הקבצים הישנים ב-`/Agents/wp-content/uploads/market/`?

אלה קבצים מ-pipeline ישן (WP007 — WP REST Media Library):
- WordPress Media API מחזיר `source_url` שכולל את `Site URL` המוגדר ב-WordPress
- ה-`Site URL` ב-WordPress מוגדר כ-`https://nimrod.bio/Agents` (WordPress Address URL)
- לכן WordPress בנה URLs עם `/Agents/` — **WordPress נוסף, לא ה-filesystem**
- קבצים אלה: **מיושנים** מאז 2026-05-07 (WP009 הוא primary path)
- **מאושרים למחיקה** (clearance ניתן בסשן 2026-05-10)

---

## 4. הקונפיגורציה הנכונה (confirmed)

```env
UPRESS_PUBLIC_BASE=https://nimrod.bio        # ← ללא /Agents
UPRESS_SFA_STATIC_ROOT=smallfarmsagents
```

URL קאנוני של artifact:
```
https://nimrod.bio/smallfarmsagents/market/sfagent-manifest.json
```

עודכן ב: `.env.upress`, `config.py`, `waldhomeserver .env`, `wp-config.php`.

---

## 5. מה WP009 שינה

| לפני (WP007) | אחרי (WP009) |
|-------------|-------------|
| WP REST Media API → `wp-content/uploads/YYYY/MM/` | mu-plugin `sfagent/v1/upload` → `smallfarmsagents/market/` |
| URL כולל `/Agents/` (מה-Site URL) | URL ישיר מה-domain root |
| Media IDs, date-organized, מצטבר | Fixed path, overwrite, canonical |
| `UPRESS_PUBLIC_BASE` לא נדרש בדיוק | `UPRESS_PUBLIC_BASE=https://nimrod.bio` מדויק |

---

## 6. פעולות שבוצעו בסשן זה

- [x] `sfagent-file-upload.php` — פרוס ב-`wp-content/mu-plugins/`
- [x] Endpoint `POST /wp-json/sfagent/v1/upload` — אומת (201)
- [x] `UPRESS_PUBLIC_BASE` מתוקן בכל סביבות (local + server)
- [x] `UPRESS_SFTP_PASS` רוטייט בכל קבצי הסביבה
- [x] `wp-config.php` — DB password עודכן, nimrod.bio UP (200)
- [x] `wp-content/uploads/market/` — מאושר למחיקה (files ישנים)
- [x] `sfa-hub/` — מאושר למחיקה (abandoned static dashboard)

---

*Authored by team_100 (Chief Architect) — SmallFarmsAgents*  
*Supersedes: FINDING_AGENTS_PATH_UPRESS_2026-05-10_v1.md*
