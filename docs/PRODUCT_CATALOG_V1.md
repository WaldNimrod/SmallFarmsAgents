# קטלוג מוצרים V1 — ירקות אורגניים

גרסה: 1.0  
תאריך: 2026-03-29  
סטטוס: seed data רשמי לגרסה ראשונה

## מטרת המסמך

מסמך זה מגדיר את רשימת הירקות הרשמית ל-V1 של המערכת.  
הוא משמש כ:

- seed data לטבלאות `products`, `measurement_units`, `product_aliases`
- בסיס לבניית normalizer rules ראשוניים
- הגדרת scope ברורה — מה נאסף ומה לא

## עקרון מנחה

V1 מתמקד בירקות אורגניים בלבד, בערוצי מכירה קהילתיים.  
לא נכנסים לV1: פירות, עשבי תיבול (אלא אם בסל קבוע), ביצים, חלב, קטניות ארוזות, מוצרים מעובדים.

---

## יחידות מידה רשמיות

| code | name_he | unit_type | is_normalizable | base_for |
|---|---|---|---|---|
| kg | קילוגרם | weight | true | מחיר בסיס |
| g | גרם | weight | true | המרה ל-kg |
| unit | יחידה | count | false | ירקות לפי ראש/יחידה |
| bunch | צרור | bundle | false | ירקות עלים/גבעולים |
| basket_small | סל קטן | basket | false | מוצר סל |
| basket_medium | סל בינוני | basket | false | מוצר סל |
| basket_large | סל גדול | basket | false | מוצר סל |
| basket_family | סל משפחתי | basket | false | מוצר סל |
| pack_250g | מארז 250 גרם | pack | true | המרה ל-kg |
| pack_500g | מארז 500 גרם | pack | true | המרה ל-kg |
| pack_1kg | מארז ק"ג | pack | true | שווה ל-kg |

---

## קטגוריות

| code | name_he |
|---|---|
| root_vegetables | ירקות שורש |
| fruiting_vegetables | ירקות פרי |
| leafy_greens | ירקות עלים |
| brassicas | כרוביים |
| alliums | בצלים |
| cucurbits | דלועיים |
| legumes_fresh | קטניות טריות |
| baskets | סלים ו-CSA |

---

## רשימת המוצרים

### ירקות פרי (fruiting_vegetables)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD001 | עגבנייה | kg | fruiting_vegetables | true | כל השנה | מרכזי ביותר; מקורות רבים |
| PRD002 | עגבנייה שרי | kg | fruiting_vegetables | true | כל השנה | לעיתים לפי קופסה |
| PRD003 | פלפל אדום | kg | fruiting_vegetables | true | אביב-סתיו | |
| PRD004 | פלפל ירוק | kg | fruiting_vegetables | true | אביב-סתיו | |
| PRD005 | מלפפון | kg | fruiting_vegetables | true | אביב-קיץ | |
| PRD006 | חציל | kg | fruiting_vegetables | true | קיץ-סתיו | |
| PRD007 | קישוא | kg | fruiting_vegetables | true | אביב-קיץ | |
| PRD031 | פלפל סוויט בייט | kg | fruiting_vegetables | true | אביב-סתיו | לא PRD003; בייבי / sweet bite |
| PRD032 | פלפל חריף | kg | fruiting_vegetables | true | אביב-סתיו | נפרד מפלפל ירוק מתוק (PRD004) |

### ירקות עלים (leafy_greens)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD008 | חסה | unit | leafy_greens | true | חורף-אביב | לפי ראש; לעיתים לפי ק"ג; גנרי |
| PRD030 | חסה זן מובחר | unit | leafy_greens | true | חורף-אביב | זני אייסברג / חמאה / לאליק / סלאנובה |
| PRD009 | עלי תרד | bunch | leafy_greens | true | חורף | לפי צרור |
| PRD010 | רוקט | bunch | leafy_greens | true | חורף-אביב | |
| PRD011 | כוסברה | bunch | leafy_greens | true | כל השנה | |
| PRD012 | פטרוזיליה | bunch | leafy_greens | true | כל השנה | |

### ירקות שורש (root_vegetables)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD013 | גזר | kg | root_vegetables | true | כל השנה | |
| PRD014 | סלק | kg | root_vegetables | true | חורף-אביב | לעיתים לפי ראש |
| PRD015 | לפת | kg | root_vegetables | true | חורף | |
| PRD016 | צנון | bunch | root_vegetables | true | חורף-אביב | |

### בצלים (alliums)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD017 | בצל יבש | kg | alliums | true | כל השנה | |
| PRD018 | בצל ירוק | bunch | alliums | true | חורף-אביב | |
| PRD019 | שום | kg | alliums | true | אביב-קיץ | לעיתים לפי ראש |
| PRD020 | כרישה | unit | alliums | true | חורף | |

### כרוביים (brassicas)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD021 | כרוב לבן | unit | brassicas | true | חורף | |
| PRD022 | כרובית | unit | brassicas | true | חורף | |
| PRD023 | ברוקולי | unit | brassicas | true | חורף | |

### קטניות טריות (legumes_fresh)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD024 | שעועית ירוקה | kg | legumes_fresh | true | אביב-קיץ | |

### סלים ו-CSA (baskets)

| id | canonical_name_he | default_unit | category | is_organic_required | seasonality | notes |
|---|---|---|---|---|---|---|
| PRD025 | סל ירקות קטן | basket_small | baskets | true | כל השנה | ~2-3 ק"ג, אינו מפורק בV1 |
| PRD026 | סל ירקות בינוני | basket_medium | baskets | true | כל השנה | ~4-6 ק"ג; כולל לשעבר PRD029 (CSA שבועי) |
| PRD027 | סל ירקות גדול | basket_large | baskets | true | כל השנה | ~7-10 ק"ג; כולל לשעבר PRD028 (סל משפחתי) |
| PRD028 | סל ירקות משפחתי | basket_family | baskets | false | כל השנה | **Inactive** — ממוזג ל־PRD027 (DB migration 017) |
| PRD029 | ארגז CSA שבועי | basket_medium | baskets | false | כל השנה | **Inactive** — ממוזג ל־PRD026 (DB migration 017) |

---

## Alias Seeds — מיפויים ראשוניים

אלו alias ראשוניים המבוססים על שמות שנמצאו במקורות.  
כל אחד נשמר בטבלת `product_aliases`.

### עגבנייה (PRD001)

| alias_text | source_id | confidence | notes |
|---|---|---|---|
| עגבניה | null | 1.0 | איות נפוץ |
| עגבניות | null | 1.0 | רבים |
| עגבנייה לק"ג | null | 0.95 | עם יחידה |
| tomatoes | null | 0.9 | אנגלית |
| עגבניה בשלה | null | 0.85 | עם תיאור |

### עגבנייה שרי (PRD002)

| alias_text | source_id | confidence |
|---|---|---|
| עגבניות שרי | null | 1.0 |
| שרי | null | 0.85 |
| cherry tomatoes | null | 0.9 |

### מלפפון (PRD005)

| alias_text | source_id | confidence |
|---|---|---|
| מלפפונים | null | 1.0 |
| מלפפון חממה | null | 0.9 |
| מלפפון שדה | null | 0.9 |
| cucumber | null | 0.9 |

### חסה (PRD008)

| alias_text | source_id | confidence |
|---|---|---|
| חסה ראש | null | 1.0 |
| חסה לייחידה | null | 0.9 |
| lettuce | null | 0.9 |

### חסה זן מובחר (PRD030)

| alias_text | source_id | confidence |
|---|---|---|
| חסה אייסברג | null | 1.0 |
| חסה חמאה | null | 1.0 |
| חסה לאליק | null | 1.0 |
| חסה סלאנובה | null | 1.0 |

### פלפל סוויט בייט (PRD031)

| alias_text | source_id | confidence |
|---|---|---|
| פלפל אדום בייבי | null | 1.0 |
| פלפל סוויט בייט | null | 1.0 |
| sweet bite | null | 0.9 |
| sweetbite | null | 0.85 |

### פלפל חריף (PRD032)

| alias_text | source_id | confidence |
|---|---|---|
| פלפל חריף ירוק | null | 1.0 |
| פלפל חריף | null | 1.0 |
| פלפל חריף אדום | null | 0.95 |

### גזר (PRD013)

| alias_text | source_id | confidence |
|---|---|---|
| גזרים | null | 1.0 |
| גזר ק"ג | null | 0.95 |
| carrot | null | 0.9 |
| גזר שדה | null | 0.9 |

### בצל יבש (PRD017)

| alias_text | source_id | confidence |
|---|---|---|
| בצל | null | 0.9 |
| בצל לבן | null | 0.85 |
| בצל ק"ג | null | 0.95 |
| onion | null | 0.9 |

### כוסברה (PRD011)

| alias_text | source_id | confidence |
|---|---|---|
| כוסברה | null | 1.0 |
| כוסברה צרור | null | 1.0 |
| cilantro | null | 0.9 |

### סל ירקות קטן (PRD025)

| alias_text | source_id | confidence |
|---|---|---|
| סל קטן | null | 1.0 |
| סל אישי | null | 0.9 |
| ארגז קטן | null | 0.85 |

### סל ירקות בינוני (PRD026)

| alias_text | source_id | confidence |
|---|---|---|
| סל בינוני | null | 1.0 |
| סל זוגי | null | 0.9 |
| ארגז בינוני | null | 0.85 |
| ארגז שבועי | null | 1.0 | לשעבר PRD029 |
| מנוי שבועי | null | 0.9 | לשעבר PRD029 |
| סל מנוי | null | 0.85 | לשעבר PRD029 |
| קופסת ירקות | null | 0.8 | לשעבר PRD029 |

### סל ירקות גדול (PRD027)

| alias_text | source_id | confidence |
|---|---|---|
| סל גדול | null | 1.0 |
| סל ירקות גדול | null | 1.0 |
| ארגז גדול | null | 0.85 |
| סל משפחתי | null | 1.0 | לשעבר PRD028 |
| סל ירקות משפחתי | null | 1.0 | לשעבר PRD028 |
| ארגז משפחתי | null | 0.85 | לשעבר PRD028 |

---

## המרות יחידות ראשוניות

| from_unit | to_unit | factor | conversion_type | product_id | notes |
|---|---|---|---|---|---|
| g | kg | 0.001 | exact | null | גרם לקילוגרם |
| pack_250g | kg | 0.25 | exact | null | מארז 250g |
| pack_500g | kg | 0.5 | exact | null | מארז 500g |
| pack_1kg | kg | 1.0 | exact | null | מארז קילו |

---

## מה לא נכנס ל-V1

| פריט | סיבה |
|---|---|
| פירות | scope רחב מדי לV1; normalization מורכב |
| עשבי תיבול (בזיל, נענע) | נכנסים רק אם חלק קבוע מסל מפורט |
| ביצים | קטגוריה נפרדת לגמרי |
| חלב ומוצרי חלב | שוק שונה |
| דלועים שלמים (אבטיח, מלון) | עונתיות קיצונית; scope מוגבל |
| שורש סלרי / פסטרנק | נדיר מדי במקורות V1 |
| ארוגולה בשקית | לא עקבי בין מקורות; נדחה |

---

## הערות לפיתוח

1. כל product_id הוא canonical key — אסור לשנות אחרי יצירה
2. `canonical_name_he` הוא שם התצוגה הציבורי
3. aliases נוצרים מ-DB; ניתן להוסיף ידנית דרך admin/agent בלי deploy
4. מוצרי basket אינם נכנסים לאגרגציה ק"ג — הם aggregate נפרד
5. עמודת `is_active` ב-`products` מאפשרת הסרה זמנית ללא מחיקה
