# Handoff Prompt — uPress + WordPress Standard v2.0 for Eyal Amit Project

> **Purpose:** Ready-to-paste prompt for the agent/team operating in the Eyal Amit 2026 project.
> Copy the text below the divider line and paste it into the Eyal Amit Cursor workspace.

---

## PROMPT START

---

צוות 100 — הנחיה מפרויקט SmallFarmsAgents (Bentiv) בעקבות התייעצות בין-פרויקטית.

### רקע

ביום 2026-04-08 בוצע תהליך סינטזה מלא בין:
1. **Playbook SmallFarmsAgents** (v1.0, 2026-04-02) — נוהל מבוסס-ניסיון מול uPress production (nimrod.bio)
2. **נוהל Eyal Amit v1.0** (2026-04-08) — נוהל ארגוני שנוצר בפרויקט זה
3. **מסמך סינטזה** — השוואה טבלאית ב-12 נושאים, 40+ סעיפים
4. **דלטה + משוב** — תיעוד החלטות ארגוניות

התוצר: **UPRESS_WORDPRESS_STANDARD_v2.md** — נוהל סופי, מאוחד, באנגלית, לכלל הפרויקטים בסביבת uPress + WordPress.

### מסמך הנוהל הסופי

הנוהל נמצא כאן:

```
/Users/nimrod/Documents/SmallFarmsAgents/docs/UPRESS_WORDPRESS_STANDARD_v2.md
```

יש להעתיק אותו לפרויקט Eyal Amit בנתיב:

```
docs/project/UPRESS_WORDPRESS_STANDARD_v2.md
```

### החלטות ארגוניות עיקריות (שאושרו על ידי נימרוד)

1. **שפה:** אנגלית — שפת עבודה טבעית לסוכנים בכל הפרויקטים.
2. **Docker מקומי:** מומלץ מאוד (strongly recommended) — חובה לפרויקטים עם פיתוח PHP מותאם אישית, אופציונלי לאתרים פשוטים. הפרויקט שלכם כבר מיישם זאת — ממשיכים כמו שאתם.
3. **FTP/TLS:** FTPS+TLS הוא ברירת המחדל ל-production. בסטייג'ינג ב-uPress ייתכן שאין תעודת SSL — במקרה כזה FTP רגיל מותר בפיתוח בלבד, יש לתעד. כאשר TLS פעיל, חובה להשתמש במחלקת `ReusedSessionFTP_TLS` (מפורט בנוהל §2.2).
4. **סודות:** `.env.upress` (פורמט dotenv) הוא הסטנדרט הארגוני. **קבצי markdown לסודות (כמו staging.credentials.md) יש להימנע מהם** — סיכון להיכלל ב-git. יש לבצע מעבר ל-`.env.upress` עם `.env.upress.example` ב-repo.
5. **REST API + Application Password:** נוהל מפורט בנוהל §7 — יש ליישם בפרויקט.
6. **תוספים:** רשימת תוספים היא המלצה, לא חובה אחידה בין אתרים. כל פרויקט מתעד רשימת תוספים מאושרת משלו.
7. **Hub ללקוח:** מודל ה-Hub שפותח אצלכם אומץ כתבנית מומלצת ארגונית (§9 בנוהל).

### פעולות נדרשות

1. **העתקת הנוהל:** להעתיק `UPRESS_WORDPRESS_STANDARD_v2.md` לנתיב `docs/project/` בפרויקט.
2. **עדכון סודות:** להעביר את `local/staging.credentials` לפורמט `.env.upress` בהתאם לתבנית ב-§12 בנוהל. להוסיף `.env.upress` ל-`.gitignore`. ליצור `.env.upress.example` ב-repo.
3. **בחינת FTPS:** לבדוק האם שרת הסטייג'ינג תומך ב-TLS. אם כן — לעדכן את סקריפטי ה-FTP (`scripts/ftp_*.py`) להשתמש ב-`ReusedSessionFTP_TLS`. אם לא — לתעד את החריגה.
4. **Application Password:** ליישם את נוהל יצירת Application Password (§7.2) לטובת אוטומציה מול REST API.
5. **עדכון project-context:** להוסיף הפניה לנוהל v2 ב-`.cursor/rules/eyalamit-2026-project-context.mdc`.
6. **ביטול נוהל v1:** להוסיף header של `SUPERSEDED` ל-`UPRESS-WORDPRESS-HOSTING-STANDARD-v1-2026-04-08.md` ולמסמך הדלטה, עם הפניה לנוהל v2.
7. **עדכון מסמך סינטזה:** להוסיף שורה בסוף `CONSULTATION-UPRESS-WORDPRESS-PLAYBOOK-SYNTHESIS-TEAM100-2026-04-08.md` שמציינת שהסינטזה הובילה לנוהל v2.0.

### מבנה הנוהל v2 (14 פרקים)

1. Platform Lock — uPress כברירת מחדל + קישורי תיעוד
2. FTP Standard — פורט 21, מדיניות TLS, מחלקת Python, סקריפטי פריסה
3. FTP Accounts — סטנדרט + דריסה מתועדת
4. Database Access — phpMyAdmin, $wpdb, REST API, כללי בטיחות
5. Environments — staging vs production
6. Local Docker — מומלץ מאוד, מימוש לדוגמה
7. REST API + Application Passwords — נוהל מלא + דוגמאות קוד
8. Plugins — סטנדרטיזציה כהמלצה
9. Client Hub — תבנית מומלצת (מבוססת על הפרויקט שלכם)
10. functions.php Patterns — hooks, שורטקודים, בטיחות
11. Decision Matrix — איזה ערוץ לאיזו משימה
12. Credentials Template — סכמת .env.upress
13. Lessons Learned — לקחים משני הפרויקטים
14. Quick Reference — REST endpoints, שאילתות SQL, מבנה קבצים

### הערות

- הנוהל **לא כולל** נושאי צוותים, שערים, ומבנה `_communication` — אלה בנהלים נפרדים.
- הנוהל **כן כולל** את מודל ה-Hub שלכם כתבנית מומלצת (§9).
- כל שינוי בנוהל v2 ייעשה בתיאום בין-פרויקטי — לא לערוך חד-צדדית.

---

## PROMPT END
