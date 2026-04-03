# מנדט יישום — Client Hub Standard v1.1

**תאריך:** 2026-04-09  
**מוציא:** צוות 00 (נימרוד) + צוות 100 (אדריכלות) — פרויקט SmallFarmsAgents  
**יעד:** צוות 100 בפרויקט Eyal Amit 2026  
**סוג:** מנדט מחייב — לא המלצה

---

## 1. הוראה ראשית

נוהל **Client Hub Standard v1.1** אושר כסטנדרט ארגוני מחייב לכל פרויקטי Agents OS.

עליכם:

1. **להעתיק** את קובץ הנוהל למערכת שלכם (נתיב מלא להלן)
2. **לנעול** — הקובץ המועתק הוא **read-only**. אסור לערוך אותו. לעולם.
3. **ליישם** את כל הדרישות בהאב הלקוח של פרויקט אייל בהתאם מלא

**אם יש צורך בהתאמות ספציפיות לפרויקט** — מותר להוסיף **נספחים נפרדים** (קבצים נפרדים) שמפנים לנוהל. אסור לערוך, למחוק, או לשנות את קובץ הנוהל עצמו.

---

## 2. קובץ מקור — נתיב מלא

### נוהל קאנוני (להעתקה ונעילה):

```
/Users/nimrod/Documents/SmallFarmsAgents/docs/CLIENT_HUB_STANDARD_v1.md
```

### מימוש ייחוס — מבנה תיקיות SFA מלא:

```
/Users/nimrod/Documents/SmallFarmsAgents/hub/
├── data/
│   ├── decisions.json
│   ├── roadmap.json
│   ├── tasks.json
│   └── updates.json
├── src/
│   └── assets/
│       ├── hub-base.css          ← CSS בסיס משותף לכל ההאבים (§11.1)
│       ├── hub.css              ← CSS פרויקטי (שכבה מעל hub-base.css)
│       └── feedback.js          ← מודול ייצוא משוב גנרי
├── ssot/
│   ├── manifest.json
│   └── responses/               ← תיקייה ריקה — מתמלאת באינג'סט
└── dist/                        ← פלט הבנייה — לא ב-Git
```

### סקריפטים (מימוש ייחוס):

```
/Users/nimrod/Documents/SmallFarmsAgents/scripts/build_sfa_client_hub.py
/Users/nimrod/Documents/SmallFarmsAgents/scripts/ftp_publish_sfa_client_hub.py
/Users/nimrod/Documents/SmallFarmsAgents/scripts/ingest_sfa_feedback_json.py
```

### נכסים משותפים (CSS בסיס, JS משוב):

```
/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/hub-base.css
/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/hub.css
/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/feedback.js
```

---

## 3. שלבי יישום — רשימת פעולות מחייבת

### שלב א — העתקה ונעילה

| # | פעולה | פירוט |
|---|-------|-------|
| 1 | העתיקו את `CLIENT_HUB_STANDARD_v1.md` לתוך פרויקט אייל | יעד מומלץ: `docs/CLIENT_HUB_STANDARD_v1.md` |
| 2 | סמנו את הקובץ כ-**LOCKED / DO NOT EDIT** | הוסיפו הערה בראש הקובץ או הגנה ברמת Git — הקובץ הזה לא נערך לעולם |
| 3 | עדכנו את `project-context` של פרויקט אייל | הוסיפו רפרנס: `docs/CLIENT_HUB_STANDARD_v1.md (v1.1, canonical, locked)` |

### שלב ב — עדכון JSON לתאימות הנוהל

| # | פעולה | פירוט |
|---|-------|-------|
| 4 | שנו שמות שדות בכל קבצי ה-JSON | `title` → `titleHe`, `context` → `contextHe`, `optionsText` → `optionsHe`, `implications` → `implicationsHe`, `recommendation` → `recommendationHe` |
| 5 | צרו `data/tasks.json` | לפי סכימה §5.4 בנוהל — קטגוריות + עדיפויות. ראו מימוש ייחוס ב-SFA |
| 6 | ודאו `schemaVersion: 1` בכל קובצי JSON | `decisions.json`, `roadmap.json`, `updates.json`, `tasks.json` |

### שלב ג — הטמעת מיתוג ו-CSS

| # | פעולה | פירוט |
|---|-------|-------|
| 7 | אמצו `hub-base.css` כבסיס | פונט Heebo, RTL, badge classes, form fields — ראו §11 בנוהל |
| 8 | הפרידו CSS פרויקטי לקובץ נפרד | התאמות ספציפיות לאייל בקובץ נפרד, **לא** בתוך hub-base |
| 9 | הטמיעו מיתוג בכל עמוד | Footer חובה בכל עמוד: |

```html
<div class="hub-brand">
  <a href="https://wa.me/972547776770" target="_blank" rel="noopener">
    Agents OS @ nimrod.bio
  </a>
</div>
```

### שלב ד — משוב ו-SSOT

| # | פעולה | פירוט |
|---|-------|-------|
| 10 | החליפו את מודול המשוב ב-`HubFeedback` הגנרי | העתיקו `feedback.js` מ-SFA והתאימו פרמטרים: |

```javascript
HubFeedback.init({
  exportType: "eyal-feedback",
  defaultRespondent: "Eyal Amit",
  decisionIds: [/* מזהי ההחלטות שלכם */]
});
```

| # | פעולה | פירוט |
|---|-------|-------|
| 11 | צרו תיקיית SSOT | `hub/ssot/manifest.json` + `hub/ssot/responses/` (ריקה) |
| 12 | צרו / התאימו סקריפט אינג'סט | `ingest_eyal_feedback_json.py` — לפי מימוש ייחוס SFA |
| 13 | ודאו: כל ייצוא JSON מהדפדפן עובר ולידציה | `exportType`, `schemaVersion`, מזהי החלטות — הכול חייב להתאים |

### שלב ה — פריסה ואבטחה

| # | פעולה | פירוט |
|---|-------|-------|
| 14 | `<meta name="robots" content="noindex, nofollow">` בכל עמוד | + `robots.txt` עם `Disallow: /` בתיקיית ההאב |
| 15 | `metadata.json` ב-dist | `generatedAt`, `schemaVersion`, `project` |
| 16 | בנו ופרסו | `build → dist → deploy` לפי סביבת הפרויקט שלכם |
| 17 | ודאו: צפייה ציבורית, כתיבה עם אימות | אין Basic Auth על צפייה. אימות רק ל-server-side feedback (כש-F-15 ייושם) |

### שלב ו — ארכיון וסגירה

| # | פעולה | פירוט |
|---|-------|-------|
| 18 | סמנו את `CLIENT-HUB-PLATFORM-SPEC-DRAFT.md` כ-SUPERSEDED | הוסיפו בראש הקובץ: |

```markdown
> **SUPERSEDED:** This document has been superseded by the canonical standard:
> **CLIENT_HUB_STANDARD_v1.md** (v1.1, 2026-04-09) — copied from SmallFarmsAgents project.
> DO NOT EDIT the standard file. Add project-specific appendices as separate files.
```

| # | פעולה | פירוט |
|---|-------|-------|
| 19 | דווחו השלמה | ראו §5 להלן |

---

## 4. כללי ממשל — חובה

| כלל | הסבר |
|------|-------|
| **אסור לערוך את הנוהל** | הקובץ `CLIENT_HUB_STANDARD_v1.md` הוא read-only. שינוי = הפרת נוהל. |
| **מותר להוסיף נספחים** | קבצים נפרדים (למשל `CLIENT_HUB_APPENDIX_EYAL.md`) שמפנים לנוהל — מותרים ומעודדים |
| **בקשות שינוי → צוות 00** | אם יש צורך אמיתי בשינוי הנוהל עצמו — הגישו בקשה מנומקת לנימרוד (צוות 00) דרך WhatsApp או SSOT |
| **גרסה = מקור** | גרסת הנוהל ב-SmallFarmsAgents היא תמיד ה-master. אם יצאה גרסה חדשה — תקבלו מנדט עדכון |
| **Platform-agnostic** | הנוהל לא תלוי בוורדפרס או uPress. אם הפרויקט עובר לסביבה אחרת — ההאב ממשיך לעבוד |

---

## 5. דיווח השלמה

לאחר יישום מלא של כל 19 הפעולות, החזירו לצוות 00 דוח הכולל:

1. **אישור**: "כל 19 הפעולות בוצעו" — או פירוט מה טרם הושלם ולמה
2. **נתיב ההאב הפרוס**: URL ציבורי
3. **נתיב הנוהל הנעול בפרויקט**: נתיב מלא בריפו
4. **נספחים שנוספו** (אם נוספו): רשימת קבצים עם תיאור קצר
5. **הערות / בקשות שינוי לנוהל**: יטופלו ב-v1.2
6. **פיצ'רים ספציפיים לאייל** שלא מכוסים בנוהל הנוכחי

---

## 6. מידע מקור להתייחסות

| פריט | נתיב מלא |
|------|----------|
| נוהל קאנוני | `/Users/nimrod/Documents/SmallFarmsAgents/docs/CLIENT_HUB_STANDARD_v1.md` |
| CSS בסיס משותף (ייחוס) | `/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/hub-base.css` |
| CSS פרויקטי (ייחוס) | `/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/hub.css` |
| JS משוב (ייחוס) | `/Users/nimrod/Documents/SmallFarmsAgents/hub/src/assets/feedback.js` |
| JSON — decisions | `/Users/nimrod/Documents/SmallFarmsAgents/hub/data/decisions.json` |
| JSON — roadmap | `/Users/nimrod/Documents/SmallFarmsAgents/hub/data/roadmap.json` |
| JSON — tasks | `/Users/nimrod/Documents/SmallFarmsAgents/hub/data/tasks.json` |
| JSON — updates | `/Users/nimrod/Documents/SmallFarmsAgents/hub/data/updates.json` |
| SSOT manifest | `/Users/nimrod/Documents/SmallFarmsAgents/hub/ssot/manifest.json` |
| סקריפט בנייה | `/Users/nimrod/Documents/SmallFarmsAgents/scripts/build_sfa_client_hub.py` |
| סקריפט פריסה | `/Users/nimrod/Documents/SmallFarmsAgents/scripts/ftp_publish_sfa_client_hub.py` |
| סקריפט אינג'סט | `/Users/nimrod/Documents/SmallFarmsAgents/scripts/ingest_sfa_feedback_json.py` |
| פרומט זה | `/Users/nimrod/Documents/SmallFarmsAgents/docs/CLIENT_HUB_STANDARD_V1_HANDOFF_PROMPT.md` |

---

*מנדט זה אושר על ידי נימרוד (צוות 00). שאלות → WhatsApp 0547776770.*
