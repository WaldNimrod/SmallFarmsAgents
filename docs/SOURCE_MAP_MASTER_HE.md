# מפת מקורות מאסטר

תאריך בדיקה: 2026-03-29

## מטרת המסמך

לרכז בטבלה אחת את מקורות המידע הרלוונטיים לפרויקט, גם אם כל מקור מספק רק חלק מהנתונים.

הגישה המנחה:

- לא מחפשים מקור מושלם אחד
- כן מחפשים הרבה מקורות חלקיים
- האגרגציה תתבצע ברמת `observation`
- לכל מקור יש תפקיד שונה: מחיר ישיר, סל/CSA, discovery, benchmark, או אימות אורגני

## מקרא ציונים

- `איכות נתון`: עד כמה הנתון גלוי, מפורט ושימושי לאגרגציה
- `כיסוי`: כמה המוצר/הקטגוריה/הנישה מיוצגים במקור
- `יציבות טכנית`: עד כמה המקור נראה יציב לאיסוף לאורך זמן
- `סיכון תחזוקה`: כמה מאמץ צפוי להחזיק parser/collector למקור
- `עדיפות MVP`: כמה נכון להתחבר למקור מוקדם

הסקאלה היא 1-5.

## טבלת מקורות

| ID | מקור | קבוצה | סוג שוק | URL | מה זמין בפועל | איכות נתון | כיסוי | יציבות | סיכון תחזוקה | עדיפות MVP | תפקיד מומלץ |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| SRC001 | easyFarm platform | תשתית discovery | niche/community | [easyfarm.co.il](https://www.easyfarm.co.il/) | זיהוי משפחת חנויות חקלאיות עם מחירון, סלים, אזורי חלוקה ותדירות הזמנה | 4 | 5 | 4 | 2 | 5 | משפחת מקור ליבה + ערוץ discovery של חנויות חדשות |
| SRC002 | סבתא יהודית | מחיר ישיר + סלים | niche/community | [sapta.easyfarm.co.il/manage/product/price_list/](https://sapta.easyfarm.co.il/manage/product/price_list/) | מחירון ציבורי מלא, יחידות, ק"ג, סלים, ספקים נוספים; מופיע גם "פיקוח אורגני ע\"י סקאל" | 5 | 4 | 4 | 2 | 5 | אחד ממקורות הליבה הראשונים |
| SRC003 | ח'ביזה | CSA / subscription | niche/community | [chubeza.easyfarm.co.il/manage/customer/ano_custom_reg/HE/](https://chubeza.easyfarm.co.il/manage/customer/ano_custom_reg/HE/) | מחירי ארגזים, תדירות, הרכב סל עונתי, נקודות חלוקה | 4 | 3 | 4 | 2 | 5 | מקור ליבה לשכבת סלים ו-CSA |
| SRC004 | קיימא בית זית | מחיר ישיר + סלים | niche/community | [kaima.easyfarm.co.il/shop/home/](https://kaima.easyfarm.co.il/shop/home/) | מחירי ירקות לפי ק"ג/יחידה, ארגזים, חלונות הזמנה, משלוח והרכבה עצמית | 5 | 4 | 4 | 2 | 5 | מקור ליבה לנישה |
| SRC005 | קיימא חוקוק | מחיר ישיר + חנות חווה | niche/community | [kaima-hukuk.easyfarm.co.il/shop/](https://kaima-hukuk.easyfarm.co.il/shop/) | מחירים לצרכן, איסוף מקומי, שעות פתיחה, ציון מפורש של פיקוח `IQC` ומספר עוסק אורגני | 5 | 3 | 4 | 2 | 5 | מקור ליבה עם מטא-דאטה אורגני טוב |
| SRC006 | עץ השדה | חנות חווה / הזמנות | niche/community | [etzhasade.easyfarm.co.il/shop/](https://etzhasade.easyfarm.co.il/shop/) | קטלוג הזמנות, מחירי מוצרים, הערת סטיות משקל, מידע על משלוחים שבועיים | 4 | 3 | 4 | 2 | 4 | מקור משלים ממשפחת easyFarm |
| SRC007 | סלסילה | סלים | niche/community | [salsila.co.il](https://www.salsila.co.il/) | הרכב סל משתנה, חלון עדכון קבוע לפני משלוח | 3 | 2 | 3 | 3 | 4 | מקור ייעודי לשכבת baskets |
| SRC008 | שדה ירוק | חנות אונליין אורגנית | niche/community | [sadeyarok.co.il](https://www.sadeyarok.co.il/) | מחירי מארזים, מחירי ק"ג, מבצעים, תוצרת משק | 5 | 4 | 4 | 3 | 5 | מקור חזק לנישה המורחבת |
| SRC009 | משק זינגר | חנות אונליין אורגנית | niche/community | [zinger-organic.com/cat/ירקות](https://www.zinger-organic.com/cat/%D7%99%D7%A8%D7%A7%D7%95%D7%AA) | קטגוריית ירקות עם כ-60 מוצרים, מחירים, יחידות, יצרנים, חנות משק | 5 | 4 | 4 | 3 | 5 | מקור ליבה לנישה |
| SRC010 | Farmerim | אגרגטור אורגני | niche/community | [farmerim.com/organic](https://farmerim.com/organic) | מחירים, מארזים/ק"ג, סימון אורגני, לעיתים שם משק/מגדל | 4 | 5 | 4 | 3 | 5 | מקור רוחב חזק לאגרגציה |
| SRC011 | האורגני | אגרגטור חקלאים אורגניים | niche/community | [haorgani.co.il](https://haorgani.co.il/) | חנות עם מחירים, רשת של 80+ חקלאים ויצרנים, שיח ישיר של קהילה-חקלאים | 4 | 5 | 4 | 3 | 5 | מקור רוחב חזק + discovery של חקלאים |
| SRC012 | בידיים - מעגל העסקים | discovery | niche/community | [bayadaim.org.il](https://www.bayadaim.org.il/%D7%94%D7%91%D7%9C%D7%95%D7%92/%D7%9E%D7%A2%D7%92%D7%9C-%D7%94%D7%A2%D7%A1%D7%A7%D7%99%D7%9D-%D7%A2%D7%9C-%D7%9E%D7%94-%D7%95%D7%9C%D7%9E%D7%94/) | אינדקס עסקים ויוזמות קיימות עם קישורים לאתרים חיצוניים | 2 | 4 | 4 | 1 | 4 | discovery לחוות חדשות ומקורות עתידיים |
| SRC013 | פרמקלצ'ר ישראל | discovery | niche/community | [permaculture.org.il](https://www.permaculture.org.il/) | "מפת רשת החיים", פרויקטים, קהילות, חקלאים ומורים | 2 | 4 | 4 | 1 | 4 | discovery ואימות קהילתי |
| SRC014 | תנועת החוות הירוקות | discovery/meta | niche/community | [next.obudget.org/.../580652170](https://next.obudget.org/i/org/association/580652170) | רישום ארגון בלבד, כרגע ללא אינדקס חוות ציבורי שנמצא | 1 | 1 | 3 | 1 | 2 | מעקב בלבד עד שיימצא נכס ציבורי שימושי |
| SRC015 | מחירי תוצרת הארץ - משרד החקלאות | benchmark רשמי | benchmark | [prices.moag.gov.il](https://prices.moag.gov.il) | מחירי שוק סיטוני רשמיים לפירות וירקות | 5 | 5 | 4 | 2 | 5 | benchmark כללי נפרד |
| SRC016 | דוחות שבועיים - משרד החקלאות | benchmark/validation | benchmark | [gov.il weekly-prices](https://www.gov.il/he/departments/dynamiccollectors/weekly-prices?skip=0&year=9) | דוחות שבועיים מסכמים, כולל חיבור בין סיטונאי לצרכן | 4 | 4 | 5 | 1 | 4 | validation ובקרה עסקית |
| SRC017 | Pricez | benchmark קמעונאי | benchmark | [pricez.co.il](https://www.pricez.co.il/) | השוואת מחירי רשתות; האתר מציג שהמחירים מסופקים על ידי הרשתות עצמן | 4 | 5 | 4 | 3 | 5 | שכבת benchmark לרשתות |
| SRC018 | CHP | benchmark קמעונאי | benchmark | [chp.co.il](https://chp.co.il/) | השוואת מחירים לפי אזור וחנויות, כולל מוצרי ירקות/פירות | 4 | 5 | 4 | 3 | 5 | שכבת benchmark לרשתות |
| SRC019 | סקאל ישראל | אימות אורגני | verification | [secal.co.il](https://www.secal.co.il/) | מידע על תקנים אורגניים וחקלאיים; שימושי לאימות claim אורגני | 3 | 3 | 4 | 1 | 4 | שכבת verification |
| SRC020 | IQC | אימות אורגני | verification | [iqc.co.il](https://www.iqc.co.il/) | גוף פיקוח ואישור לחקלאות אורגנית ותקנים חקלאיים | 3 | 3 | 4 | 1 | 4 | שכבת verification |

## חלוקה תפעולית מומלצת

### קבוצת ליבה לחיבור מוקדם

- `SRC002` סבתא יהודית
- `SRC003` ח'ביזה
- `SRC004` קיימא בית זית
- `SRC005` קיימא חוקוק
- `SRC008` שדה ירוק
- `SRC009` משק זינגר
- `SRC010` Farmerim
- `SRC011` האורגני

### קבוצת benchmark

- `SRC015` מחירי תוצרת הארץ
- `SRC016` דוחות שבועיים
- `SRC017` Pricez
- `SRC018` CHP

### קבוצת discovery

- `SRC001` easyFarm platform
- `SRC012` בידיים
- `SRC013` פרמקלצ'ר ישראל
- `SRC014` תנועת החוות הירוקות

### קבוצת verification

- `SRC019` סקאל
- `SRC020` IQC

## מסקנות עבודה

1. משפחת `easyFarm` היא כיום ערוץ האיסוף הטוב ביותר לחיבור מהיר למספר חוות ו-CSA.
2. מקורות כמו `Farmerim` ו-`האורגני` חשובים כי הם מספקים כיסוי רחב גם אם אינם "חווה בודדת".
3. מקורות discovery לא נותנים מחירים, אבל הם קריטיים להרחבת הרשת.
4. מקורות benchmark חייבים להיות נפרדים מהאגרגציה הקהילתית הראשית.
5. verification של אורגני צריך להישמר כשכבת מטא-דאטה, לא כמקור מחיר.

## צעד המשך מומלץ

לשלב הפיתוח הבא נכון לקחת את `SRC002-005` ו-`SRC008-011`, ולבנות עבורם:

- טבלת `sources`
- טבלת `source_fetch_profiles`
- טבלת `source_product_aliases`
- טסט גישה ראשוני לכל מקור
