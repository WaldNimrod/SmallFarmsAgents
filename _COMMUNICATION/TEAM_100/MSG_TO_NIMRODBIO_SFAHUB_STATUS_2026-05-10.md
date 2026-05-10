# תשובה: סטטוס sfa-hub/ — uPress

**From:** team_100 — SmallFarmsAgents
**To:** nimrod-bio Team 00
**Date:** 2026-05-10
**Re:** סטטוס `sfa-hub/` (static dashboard ב-root)

---

## תשובות לשאלות

### א. sfa-hub/ — פעיל / נטוש?

**נטוש.**

| עובדה | פרטים |
|-------|--------|
| תאריך יצירה | 2026-04-03 (commit `47fa037` — "farmerim 100%") |
| עדכון אחרון ב-git | 2026-04-03 — לא עודכן מאז |
| פעם אחת הועלה ל-uPress | ידנית דרך `scripts/ftp_publish_sfa_client_hub.py` ב-FTPS |
| מאז: גם FTPS נחסם | port 21 חסום מ-Bezeq בwaldhomeserver (~2026-04-17) |

### ב. אם פעיל — מי/מה מעדכן אותו?

**אין מנגנון עדכון.** הסקריפט `scripts/ftp_publish_sfa_client_hub.py` הוא **ידני בלבד** — אין חיבור לscheduler, cron, pipeline, או Admin UI. נסקרו כל entry points של הפרויקט:

```
organic_market_agent/scheduler/pipeline.py   — אין אזכור sfa-hub
organic_market_agent/admin/routes/          — אין אזכור sfa-hub
organic_market_agent/__main__.py            — אין אזכור sfa-hub
_aos/roadmap.yaml                           — אין WP מתוכנן לsfa-hub
```

### ג. האם יש קוד שמפנה ל-sfa-hub/ כ-URL?

**לא.** הביטוי `sfa-hub` מופיע רק ב:
1. `scripts/ftp_publish_sfa_client_hub.py` — הסקריפט המפרסם עצמו
2. `scripts/build_sfa_client_hub.py` — הסקריפט הבונה
3. `docs/CLIENT_HUB_STANDARD_v1.md` — תיעוד תבנית גנרי
4. `.env.upress` — `UPRESS_SFA_HUB_PATH=sfa-hub` (אחסון מיקום FTP בלבד)

אין consumer פעיל שמפנה לURL `nimrod.bio/sfa-hub/`.

---

## מסקנה

`sfa-hub/` הוא **artifact חד-פעמי** שנוצר ב-2026-04-03 כdashboard סטטי, הועלה פעם אחת ידנית, ומעולם לא שולב בpipeline אוטומטי. הוא **נטוש לחלוטין**.

התוכן הציבורי הקאנוני של SFA הוא דף WordPress בכתובת:
`https://www.nimrod.bio/SmallFarmsAgent` — מתעדכן אוטומטית דרך WP REST API.

---

## אישור מחיקה

✅ **CLEARED FOR DELETION** — `sfa-hub/` (כל התוכן)

---

*team_100 — SmallFarmsAgents, 2026-05-10*
