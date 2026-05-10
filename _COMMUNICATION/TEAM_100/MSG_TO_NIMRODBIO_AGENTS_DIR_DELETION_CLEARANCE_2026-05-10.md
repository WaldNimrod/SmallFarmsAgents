# אישור מחיקת Agents/wp-content/uploads/market/

**From:** team_100 — SmallFarmsAgents
**To:** nimrod-bio Team 00
**Date:** 2026-05-10
**Re:** בקשת אישור מחיקת תיקיית `Agents/wp-content/uploads/market/`

---

## תשובה ישירה

**כן — SFA הפסיק לכתוב ל-`Agents/wp-content/uploads/market/` החל מ-2026-05-07.**
התיקייה בטוחה למחיקה.

---

## ציר הזמן

| תאריך | אירוע |
|-------|-------|
| 2026-04-17 | הכתיבה האוטומטית (cron FTPS) נתקעת — באג TLS 425 על FTPS port 21 |
| 2026-04-18 | redeploy ידני אחרון ל-`uploads/market/` (waldhomeserver `.env` נכתב מחדש) |
| ~2026-04-25 | כנראה הכתיבה האחרונה לתיקייה (manual run) — עקבי עם ממצא הגיבוי |
| 2026-05-07 | **WP007 deployed** — FTPS הוחלף ב-WP REST API (HTTPS port 443) כ-primary upload path. `UPRESS_FALLBACK_FTPS` ברירת מחדל = 0. מרגע זה אין כתיבה ל-`uploads/market/` |
| 2026-05-07 | **WP008 deployed** — גם scheduler (cron) וגם Admin UI עברו ל-WP REST API. ביטול מוחלט של FTPS מכל נתיבי ה-upload |

---

## מנגנון Upload נוכחי

**WP REST API** — `POST https://www.nimrod.bio/wp-json/wp/v2/media`

WordPress מאחסן את הקבצים ב-**media library date-organized**:
```
Agents/wp-content/uploads/2026/MM/sfagent-manifest.json
Agents/wp-content/uploads/2026/MM/sfagent-public-report.json
Agents/wp-content/uploads/2026/MM/sfagent-public-report.html
Agents/wp-content/uploads/2026/MM/sfagent-public-report-body.html
Agents/wp-content/uploads/2026/MM/sfagent-manifest-of-urls.json
```

הנתיב `uploads/market/` **אינו נכתב יותר** — ה-pipeline לא מעביר `UPRESS_UPLOAD_PATH` ל-`wp_upload.py`. ה-env var הזה קיים רק לשרידות FTPS fallback (מושבת).

---

## בדיקת בטיחות לפני מחיקה

קוד שעשוי לקרוא מ-`uploads/market/`:

| קובץ | שימוש | סטטוס |
|------|-------|--------|
| `ftps_upload.py` — `UPRESS_VERIFY_PUBLIC_MANIFEST` | GET לבדיקת גרסת manifest | **מושבת** כברירת מחדל (env var לא מוגדר) |
| `manifest.json` שדה `upload_base` | informational only — לא נצרך לפתרון URL | לא מוחזק ב-WordPress options |
| WordPress shortcode `[sfagent_market_report]` | קורא מ-`sfagent_manifest_of_urls_url` WP option | ה-option מצביע ל-media library URL (לא `market/`) |

**מסקנה:** אין קוד פעיל שקורא מ-`Agents/wp-content/uploads/market/`.

---

## אישור מחיקה

✅ **CLEARED FOR DELETION** — `Agents/wp-content/uploads/market/`

אין צורך בשימור. nimrod-bio Team 00 רשאי למחוק את התיקייה ותכולתה.

---

*team_100 — SmallFarmsAgents, 2026-05-10*
