> **LANGUAGE NOTICE:** This document is a legacy Hebrew specification (MyFarmAgents v1.1).
> Platform: **MyFarmAgents** | Agent: **OrganicMarketAgent**
> All new documents are written in English. See `docs/GLOSSARY.md` for canonical terminology.
> This file is pending English rewrite — scheduled per milestone.

---

# מפת מקורות מאסטר

גרסה: 1.1  
תאריך בדיקה: 2026-03-29  
שינויים מגרסה 1.0: הוספת platform_family, legal_review_required, עמודת status

## מטרת המסמך

לרכז בטבלה אחת את מקורות המידע הרלוונטיים לפרויקט, גם אם כל מקור מספק רק חלק מהנתונים.

הגישה המנחה:

- לא מחפשים מקור מושלם אחד
- כן מחפשים הרבה מקורות חלקיים
- האגרגציה תתבצע ברמת `observation`
- לכל מקור יש תפקיד שונה

## מקרא ציונים

- `איכות נתון`: עד כמה הנתון גלוי, מפורט ושימושי לאגרגציה
- `כיסוי`: כמה המוצר/הקטגוריה/הנישה מיוצגים במקור
- `יציבות טכנית`: עד כמה המקור נראה יציב לאיסוף לאורך זמן
- `סיכון תחזוקה`: כמה מאמץ צפוי להחזיק parser/collector למקור
- `עדיפות MVP`: כמה נכון להתחבר למקור מוקדם

הסקאלה היא 1-5.

## טבלת מקורות — v1.1

| ID | מקור | קבוצה | סוג שוק | URL | platform_family | מה זמין בפועל | איכות נתון | כיסוי | יציבות | סיכון תחזוקה | עדיפות MVP | status | legal_review_required | תפקיד מומלץ |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| SRC001 | easyFarm platform | תשתית discovery | community | [easyfarm.co.il](https://www.easyfarm.co.il/) | easyfarm | זיהוי משפחת חנויות חקלאיות, מחירון, סלים, אזורי חלוקה | 4 | 5 | 4 | 2 | 5 | active | false | משפחת מקור ליבה + discovery |
| SRC002 | סבתא יהודית | מחיר ישיר + סלים | community | [sapta.easyfarm.co.il](https://sapta.easyfarm.co.il/manage/product/price_list/) | easyfarm | מחירון ציבורי מלא, יחידות, ק"ג, סלים, פיקוח IQC | 5 | 4 | 4 | 2 | 5 | active | false | מקור ליבה ראשון |
| SRC003 | ח'ביזה | CSA / subscription | community | [chubeza.easyfarm.co.il](https://chubeza.easyfarm.co.il/manage/customer/ano_custom_reg/HE/) | easyfarm | מחירי ארגזים, תדירות, הרכב סל עונתי | 4 | 3 | 4 | 2 | 5 | active | false | מקור ליבה לשכבת CSA |
| SRC004 | קיימא בית זית | מחיר ישיר + סלים | community | [kaima.easyfarm.co.il](https://kaima.easyfarm.co.il/shop/home/) | easyfarm | מחירי ירקות לק"ג/יחידה, ארגזים, חלונות הזמנה | 5 | 4 | 4 | 2 | 5 | active | false | מקור ליבה לנישה |
| SRC005 | קיימא חוקוק | מחיר ישיר + חנות חווה | community | [kaima-hukuk.easyfarm.co.il](https://kaima-hukuk.easyfarm.co.il/shop/) | easyfarm | מחירים לצרכן, ציון IQC ומספר עוסק אורגני | 5 | 3 | 4 | 2 | 5 | active | false | מקור ליבה עם מטא-דאטה אורגני |
| SRC006 | עץ השדה | חנות חווה / הזמנות | community | [etzhasade.easyfarm.co.il](https://etzhasade.easyfarm.co.il/shop/) | easyfarm | קטלוג הזמנות, הערת סטיות משקל | 4 | 3 | 4 | 2 | 4 | active | false | מקור משלים easyFarm |
| SRC007 | סלסילה | סלים | community | [salsila.co.il](https://www.salsila.co.il/) | standalone | הרכב סל משתנה, עדכון קבוע לפני משלוח | 3 | 2 | 3 | 3 | 4 | active | false | מקור לשכבת baskets |
| SRC008 | שדה ירוק | חנות אונליין אורגנית | community | [sadeyarok.co.il](https://www.sadeyarok.co.il/) | standalone | מחירי מארזים, מחירי ק"ג, מבצעים | 5 | 4 | 4 | 3 | 5 | active | false | מקור חזק לנישה |
| SRC009 | משק זינגר | חנות אונליין אורגנית | community | [zinger-organic.com](https://www.zinger-organic.com/cat/%D7%99%D7%A8%D7%A7%D7%95%D7%AA) | standalone | ~60 מוצרים, מחירים, יחידות, יצרנים | 5 | 4 | 4 | 3 | 5 | active | false | מקור ליבה לנישה |
| SRC010 | Farmerim | אגרגטור אורגני | community | [farmerim.com](https://farmerim.com/organic) | aggregator | מחירים, מארזים/ק"ג, סימון אורגני | 4 | 5 | 4 | 3 | 5 | active | false | מקור רוחב לאגרגציה |
| SRC011 | האורגני | אגרגטור חקלאים | community | [haorgani.co.il](https://haorgani.co.il/) | aggregator | 80+ חקלאים ויצרנים, שיח קהילה-חקלאים | 4 | 5 | 4 | 3 | 5 | active | false | מקור רוחב + discovery |
| SRC012 | בידיים | discovery | community | [bayadaim.org.il](https://www.bayadaim.org.il/) | standalone | אינדקס עסקים וקישורים חיצוניים | 2 | 4 | 4 | 1 | 4 | active | false | discovery לחוות חדשות |
| SRC013 | פרמקלצ'ר ישראל | discovery | community | [permaculture.org.il](https://www.permaculture.org.il/) | standalone | "מפת רשת החיים", פרויקטים, קהילות | 2 | 4 | 4 | 1 | 4 | active | false | discovery ואימות קהילתי |
| SRC014 | תנועת החוות הירוקות | discovery/meta | community | [next.obudget.org](https://next.obudget.org/i/org/association/580652170) | standalone | רישום ארגון בלבד | 1 | 1 | 3 | 1 | 2 | candidate | false | מעקב בלבד |
| SRC015 | מחירי תוצרת הארץ | benchmark רשמי | benchmark | [prices.moag.gov.il](https://prices.moag.gov.il) | govt | מחירי שוק סיטוני רשמיים | 5 | 5 | 4 | 2 | 5 | active | false | benchmark ראשי |
| SRC016 | דוחות שבועיים משרד החקלאות | benchmark/validation | benchmark | [gov.il weekly-prices](https://www.gov.il/he/departments/dynamiccollectors/weekly-prices?skip=0&year=9) | govt | דוחות שבועיים PDF | 4 | 4 | 5 | 1 | 4 | active | false | validation ובקרה |
| SRC017 | Pricez | benchmark קמעונאי | benchmark | [pricez.co.il](https://www.pricez.co.il/) | standalone | השוואת מחירי רשתות | 4 | 5 | 4 | 3 | 5 | candidate | **true** | benchmark רשתות — עצור לbdיקה משפטית |
| SRC018 | CHP | benchmark קמעונאי | benchmark | [chp.co.il](https://chp.co.il/) | standalone | השוואת מחירים לפי אזור וחנויות | 4 | 5 | 4 | 3 | 5 | candidate | **true** | benchmark רשתות — עצור לבדיקה משפטית |
| SRC019 | סקאל ישראל | אימות אורגני | verification | [secal.co.il](https://www.secal.co.il/) | standalone | מידע על תקנים אורגניים | 3 | 3 | 4 | 1 | 4 | active | false | verification layer |
| SRC020 | IQC | אימות אורגני | verification | [iqc.co.il](https://www.iqc.co.il/) | standalone | גוף פיקוח ואישור אורגני | 3 | 3 | 4 | 1 | 4 | active | false | verification layer |

---

## הערות legal_review_required

### SRC017 — Pricez

**legal_review_required = true**

`pricez.co.il` מצהיר שהמחירים מסופקים על ידי הרשתות עצמן. אין ודאות לגבי:
- האם scraping מותר על פי תנאי השימוש
- האם ישנה מגבלה על שימוש בנתונים לפרסום ציבורי

**פעולה נדרשת:** לקרוא T&C של Pricez לפני בניית collector.  
**עד אז:** status=candidate, אין לבנות collector.

### SRC018 — CHP

**legal_review_required = true**

אותן מגבלות כמו Pricez.  
**פעולה נדרשת:** לקרוא T&C של CHP.  
**עד אז:** status=candidate.

---

## easyFarm Platform Family — הערה חשובה

SRC001–SRC006 כולם שייכים ל-`platform_family = 'easyfarm'`.

**משמעות:** שינוי בפלטפורמת easyFarm עשוי לשבור את כל ששת המקורות בבת אחת.

**ניהול הסיכון:**
- collector גנרי אחד: `collectors/easyfarm.py` שמקבל `site_subdomain` כפרמטר
- monitoring: אם easyFarm-family source נכשל — לוג WARNING ל-admin
- ב-source_fetch_profiles: `platform_family = 'easyfarm'` לכל 6 המקורות

---

## חלוקה תפעולית מומלצת

### קבוצת ליבה לחיבור מוקדם (V1 phase 1)

| ID | מקור | platform_family |
|---|---|---|
| SRC002 | סבתא יהודית | easyfarm |
| SRC003 | ח'ביזה | easyfarm |
| SRC004 | קיימא בית זית | easyfarm |
| SRC005 | קיימא חוקוק | easyfarm |
| SRC008 | שדה ירוק | standalone |
| SRC009 | משק זינגר | standalone |
| SRC010 | Farmerim | aggregator |
| SRC011 | האורגני | aggregator |

### קבוצת benchmark

| ID | מקור | status |
|---|---|---|
| SRC015 | מחירי תוצרת הארץ | active |
| SRC016 | דוחות שבועיים | active |
| SRC017 | Pricez | candidate — legal review |
| SRC018 | CHP | candidate — legal review |

### קבוצת discovery

- SRC001 easyFarm platform
- SRC012 בידיים
- SRC013 פרמקלצ'ר ישראל
- SRC014 תנועת החוות הירוקות

### קבוצת verification

- SRC019 סקאל
- SRC020 IQC

---

## מסקנות עבודה

1. משפחת `easyFarm` היא ערוץ האיסוף הטוב ביותר לחיבור מהיר — generic collector אחד.
2. מקורות `Farmerim` ו-`האורגני` חשובים לכיסוי רחב גם אם אינם "חווה בודדת".
3. discovery sources לא נותנים מחירים — קריטיים להרחבת הרשת בהמשך.
4. benchmark חייב להיות נפרד מהאגרגציה הקהילתית.
5. SRC017/SRC018 — לא לבנות collector לפני legal review.

## צעד המשך מומלץ

לשלב הפיתוח הראשון לקחת SRC002–SRC006 ו-SRC008–SRC011 ולבנות עבורם:

- טבלת `sources` (seed data)
- טבלת `source_fetch_profiles` עם `platform_family`
- collector tests: HTTP GET לכל entry_url
- parser skeleton לכל normalizer_type
