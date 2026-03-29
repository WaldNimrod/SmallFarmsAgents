# תכנית ולידציה ל-uPress

תאריך: 2026-03-29

## 1. מטרת המסמך

לאשר בפועל, לפני תחילת פיתוח מלא, שמסלול ה-publish הפשוט והנוח ביותר למערכת אכן עובד על סביבת `uPress` הקיימת.

המסמך אינו מניח הצלחה מראש.
הוא מגדיר בדיקות שיש לבצע, קריטריוני הצלחה, והחלטות שייגזרו מהן.

## 2. רקע

המערכת מתוכננת כך:

- מנוע הנתונים רץ מקומית
- ה-admin רץ מקומית
- השרת הציבורי של `nimrod.bio` מציג artifacts סטטיים בלבד
- אין שימוש ב-DB של וורדפרס כמערכת הרשומה

לכן הנתיב המרכזי שצריך לאמת הוא:

`local build -> automated upload -> public file serving -> WordPress rendering`

## 3. מה ידוע כיום ממקורות ציבוריים של uPress

נכון ל-2026-03-29:

- קיימת תמיכה בחשבונות FTP דרך הפאנל:
  - [כיצד להעלות ולהוריד קבצים באמצעות FTP](https://support.upress.co.il/dev/how-to-use-ftp/)
- בשרת שיתופי פעולות build מבוצעות לוקאלית והקבצים מועלים לשרת:
  - [התקנת חבילות NPM](https://support.upress.co.il/advanced/npm-install/)
- קיימת תיעוד לאפשרויות אבטחה והגבלת גישה:
  - [קטגוריית אבטחה](https://support.upress.co.il/category/security/)

מה שלא אושר ציבורית:

- SSH
- `rsync`
- FTPS בפועל עבור החשבון הקיים
- התנהגות cache/CDN על artifacts מתעדכנים
- overwrite אוטומטי בנתיב publish ייעודי

## 4. שאלת ההכרעה

האם אפשר לממש על `uPress` מסלול `daily unattended publish` פשוט, אמין ונטול עבודה ידנית, המבוסס על artifacts סטטיים?

## 5. Strategy

### נתיב בדיקה ראשי

1. לנסות `FTPS/FTP automated upload`
2. להעלות artifacts versioned
3. לעדכן `manifest.json` אחרון
4. לטעון את ה-artifacts מתוך עמוד WordPress ניסיוני

### נתיבי fallback

אם הנתיב הראשי נכשל:

1. לבדוק האם `SFTP/SSH` זמין
2. לבדוק endpoint-based upload
3. אם גם זה נכשל, לשקול מחדש את שכבת הפרסום

## 6. Test Matrix

| Test ID | נושא | מטרה | שיטה | קריטריון הצלחה | אם נכשל |
|---|---|---|---|---|---|
| U01 | FTP login | לאשר גישה אוטומטית | חיבור סקריפטי עם credentials | חיבור יציב והצגת תיקיות | לפתוח מול uPress |
| U02 | FTPS support | לבדוק הצפנת תעבורה | חיבור ב-FTPS | upload מוצלח ב-FTPS | fallback ל-FTP רק אם נדרש |
| U03 | write path | לאשר נתיב publish | העלאת קובץ ל-`uploads/market/` | הקובץ נוצר בנתיב הקבוע | להחליף נתיב |
| U04 | overwrite | לאשר update יומי | העלאה חוזרת לאותו שם | הקובץ מוחלף תקין | לעבור ל-versioned files |
| U05 | versioned files | לאשר model של versioned artifacts | העלאת `public_report-<ts>` | קבצים חדשים נגישים | לשנות naming |
| U06 | manifest update | לאשר החלפת גרסה אטומית | העלאת קבצים ואז manifest | manifest מצביע לגרסה החדשה | לחזק order/retry |
| U07 | public access | לאשר הגשה ב-HTTP | `curl` / browser | הקובץ נגיש ציבורית | לשנות מיקום |
| U08 | cache delay | למדוד latency לעדכון | overwrite/version switch | ניתן לעמוד ב-SLA יומי | להסתמך יותר על versioned names |
| U09 | WordPress HTML render | לאשר embed ל-HTML | עמוד ניסוי | HTML נטען יציב | לעבור ל-JSON render |
| U10 | WordPress JSON render | לאשר rendering ל-JSON | template/block פשוט | JSON נקרא ומוצג | לבחור HTML-only |
| U11 | last-good fallback | להגן על הציבור | כשל יזום ב-publish | הציבור רואה גרסה קודמת | לחזק manifest policy |
| U12 | unattended daily run | לאשר אוטומציה מלאה | cron מקומי + upload + verify | ללא מגע יד אדם | לתקן orchestration |

## 7. סדר ביצוע מומלץ

### שלב 1: File transport

- `U01`
- `U02`
- `U03`
- `U04`

### שלב 2: Publish contract

- `U05`
- `U06`
- `U11`

### שלב 3: Public rendering

- `U07`
- `U09`
- `U10`

### שלב 4: Ops validation

- `U08`
- `U12`

## 8. Test Data מומלץ

לבדיקות הראשונות אין צורך ב-data אמיתי.

מספיק להעלות:

- `manifest.json`
- `public_report-test-v1.json`
- `public_report-test-v1.html`

עם מבנה מינימלי של:

- `published_at`
- `artifact_version`
- `products`
- `community section`
- `benchmark section`

## 9. Output נדרש מהבדיקות

בסוף תהליך הוולידציה צריך להיווצר מסמך תוצאות הכולל:

- מה עבד
- מה לא עבד
- באילו תנאים זה עבד
- האם נדרש fallback
- מהו מנגנון ההעלאה המאושר
- מהו נתיב ה-publish המאושר
- מהו מודל cache busting המאושר

## 10. Gate לאישור ארכיטקטורה

הארכיטקטורה תאושר סופית ליישום רק אם שלושת התנאים הבאים מתקיימים:

1. upload אוטומטי עובד אמין
2. artifacts נגישים ונטענים ציבורית
3. WordPress יכול להציג את ה-artifacts בפשטות וביציבות

## 11. מסקנה נוכחית

הכיוון המועדף נשאר:

- local system of record
- publish קבצים סטטיים
- WordPress presentation layer

אבל המסלול מול `uPress` עדיין טעון proof tests לפני אישור סופי.
