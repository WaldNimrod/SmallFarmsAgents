# GREEN-INVOICE-CAPABILITIES-FINDINGS-2026-03-30

תאריך: 2026-03-30  
נושא: מחקר יכולות ופיצ'רים של חשבונית ירוקה / Morning, לצורך בחירת מסלול יישום ישים באתר WordPress רזה.

## 1. מסקנה קצרה

לפי התיעוד הרשמי שנסקר, חשבונית ירוקה של Morning מציעה היום שלוש רמות רלוונטיות לפרויקט:

1. **קישורי תשלום פשוטים**  
   לינק לתשלום בסכום קבוע, לינק לתשלום בסכום פתוח, ולינק להוראת קבע.

2. **דפי מכירה / דפי נחיתה**  
   Hosted pages עם קטלוג מוצרים, אפשרויות תשלום, קופונים, מלאי, delivery options, ניהול הזמנות ו־webhooks ללידים/תשלום.

3. **API + Webhooks + WooCommerce integration**  
   אפשריים, אבל זמינים למנויי `Best ומעלה` ודורשים יותר תחזוקה. רלוונטיים בעיקר לשלב 2, לא כנקודת הפתיחה של אתר WordPress רזה.

המסקנה האופרטיבית:  
ל־WordPress רזה, המסלולים הישימים ביותר כרגע הם **A. קישורי תשלום**, או **B. דפי מכירה חיצוניים**.  
`API` הוא יכולת אמיתית ומתועדת, אבל נראה כמו שלב עומק, לא כ-default הראשון.

## 2. ממצאים לפי שאלות המחקר

### 2.1 אילו סוגי קישורי תשלום קיימים

מהתיעוד הרשמי עלה שקיימים לפחות הסוגים הבאים:

#### א. לינק לתשלום בסכום קבוע

- זמין למנויי `Best ומעלה`
- מיועד ל"מוצר או שירות" בסכום מוגדר
- מפיק אוטומטית מסמך לאחר תשלום
- ניתן להפצה ללא הגבלה
- ניתן לשתף במייל, WhatsApp, כ־QR, לשלב בקמפיין ולהטמיע כקישור באתר

מקור:  
- [יצירת לינק לתשלום](https://www.greeninvoice.co.il/help-center/create-payment-link/)

#### ב. לינק לתשלום בסכום פתוח

- זמין למנויי `Best ומעלה`
- מיועד לתרומה / שירות / מוצר שבו הלקוח ממלא את הסכום
- מפיק אוטומטית קבלה / קבלה על תרומה / חשבונית מס-קבלה

מקור:  
- [יצירת לינק לתשלום בסכום פתוח](https://www.greeninvoice.co.il/help-center/open-payment-link/)

#### ג. לינק להוראת קבע

- זמין למנויי `Best ומעלה`
- מאפשר חיוב מחזורי קבוע באשראי
- מפיק אוטומטית קבלה או חשבונית מס/קבלה בכל חיוב

מקור:  
- [יצירת לינק להוראת קבע](https://www.greeninvoice.co.il/help-center/recurring-charges-link/)

#### ד. מסמך עם כפתור תשלום

- ניתן לשלוח מסמך דרישת תשלום / חשבונית עם כפתור תשלום
- התשלום יכול להיות באשראי, bit, Apple Pay, Google Pay
- לאחר תשלום מופקת קבלה / חשבונית מס-קבלה

מקור:  
- [אפליקציה – שליחת חשבונית עם כפתור תשלום](https://www.greeninvoice.co.il/help-center/payment-request-app/)
- [תשלומים דיגיטליים](https://www.greeninvoice.co.il/help-center/digital-payments/)

#### ה. דף מכירה / דף נחיתה

- Morning מאפשרת להקים Hosted `דף מכירה` או `דף נחיתה`
- אפשר להשתמש בדף כעמוד מכירה עם קטלוג ומוצרים
- אפשר גם להשתמש בו כדף נחיתה ללא מכירה
- אפשר להפיץ URL ו־QR

מקורות:  
- [הכל על יצירת דף מכירה לעסק](https://www.greeninvoice.co.il/help-center/all-about-sale-page/)
- [דפי המכירה שלנו](https://www.greeninvoice.co.il/help-center/sales-pages/)

#### ו. עגלה חיצונית / checkout חיצוני נפרד

לא מצאתי בתיעוד הרשמי שנסקר מוצר נפרד ומתועד של "עגלה חיצונית" כישות עצמאית, מעבר ל:

- `payment links`
- `sale pages`
- `WooCommerce` / אינטגרציות חנות

לכן כרגע:

`לא מתועד / לא זמין במקורות שנסקרו`

### 2.2 האם יש API / Webhooks רלוונטיים לפרויקט קטן

#### API

כן. קיים API רשמי ומתועד.

מה מתועד רשמית:

- `API` זמין למנויי `Best ומעלה`
- נדרש מפתח API
- קיימת סביבת `Sandbox`
- Morning מציגה את ה־API ככלי להתחברות ממערכות חיצוניות, חנויות, CRM ועוד

מקורות:  
- [ממשק ה-API שלנו](https://www.greeninvoice.co.il/help-center/api/)
- [יצירת מפתח API](https://www.greeninvoice.co.il/help-center/generating-api-key/)

#### Webhooks

כן. קיימים webhooks רלוונטיים.

מה מתועד רשמית:

- Webhooks זמינים למנויי `Best ומעלה`
- URL חייב להיות `https`
- יש לוג ייעודי ל-webhooks
- אם אין תגובה בתוך 6 שניות, המערכת מסמנת timeout ומבצעת ניסיונות חוזרים עד 24 שעות

האירועים המתועדים והרלוונטיים במיוחד:

- `document/created`
- `payment/received`
- `sale-pages/page-contacted`
- `sale-pages/order-paid`

הערה:

מצאתי דף דוגמה מפורש ל-`sale-pages/page-contacted`, אך לא מצאתי במקורות שנסקרו דף דוגמה נפרד ל-`sale-pages/order-paid`.  
האירוע עצמו כן מתועד רשמית ברשימת האירועים של מסך ה-Webhooks.

מקורות:  
- [הגדרת Webhooks](https://www.greeninvoice.co.il/help-center/creating-webhook/)
- [Webhook – document/created](https://www.greeninvoice.co.il/help-center/webhook-document-created/)
- [Webhook – payment/receive](https://www.greeninvoice.co.il/help-center/webhook-payment-receive/)
- [Webhook – sale-pages/page-contacted](https://www.greeninvoice.co.il/help-center/webhook-sales-page-contacted/)

#### מסקנה לפרויקט קטן

לפרויקט קטן:

- **Webhooks** נראים רלוונטיים יותר מ־API מלא
- **API** מתאים אם רוצים later stage sync או אוטומציה עמוקה
- לשלב ראשון של WordPress רזה, אין חובה להתחיל עם API

### 2.3 מגבלות ידועות

#### Plan gating

מגבלות plan מתועדות היטב:

- `API` – Best ומעלה
- `Webhooks` – Best ומעלה
- `Payment links` – Best ומעלה
- `Recurring payment link` – Best ומעלה
- `Sale Pages` – זמינים בכל המסלולים, אבל בתשלום חודשי לכל דף שפורסם

מקורות:  
- [ממשק ה-API שלנו](https://www.greeninvoice.co.il/help-center/api/)
- [יצירת מפתח API](https://www.greeninvoice.co.il/help-center/generating-api-key/)
- [הגדרת Webhooks](https://www.greeninvoice.co.il/help-center/creating-webhook/)
- [יצירת לינק לתשלום](https://www.greeninvoice.co.il/help-center/create-payment-link/)
- [דפי המכירה שלנו](https://www.greeninvoice.co.il/help-center/sales-pages/)

#### עלות Sale Pages

- לפי התיעוד הרשמי: `24 ₪ + מע״מ לחודש עבור כל דף מכירה מפורסם באוויר`

מקור:  
- [דפי המכירה שלנו](https://www.greeninvoice.co.il/help-center/sales-pages/)

#### מטבע

- בתיעוד הסליקה הרשמי נאמר כי `תשלומים דיגיטליים` הם **בשקלים בלבד**
- בתיעוד WooCommerce מצוין:
  - תשלומים דיגיטליים – `ש״ח בלבד`
  - ישראכרט – `ש״ח`, ובתיאום גם `דולר` ו־`יורו`

מקורות:  
- [חיבור לתשלומים דיגיטליים](https://www.greeninvoice.co.il/help-center/digital-payments-connect/)
- [WooCommerce – הגדרות מטבע](https://www.greeninvoice.co.il/help-center/woocommerce-currency/)

#### שפה

מצאתי תיעוד לגבי שפת מסמך ב־WooCommerce, אך **לא מצאתי במקורות שנסקרו matrix רשמי ומלא של שפות לדפי מכירה או לקישורי תשלום**.

לכן כרגע:  
`לא מתועד במפורש / לא זמין במקורות שנסקרו`

מקור רלוונטי:  
- [WooCommerce – הגדרות שפת מסמך](https://www.greeninvoice.co.il/help-center/woocommerce-language/)

#### קטגוריות / מספר מוצרים / hierarchy

בתיעוד דפי המכירה מופיעים:

- שם פריט / מק״ט
- תיאור
- מחיר
- תמונה
- מלאי
- הגבלת רכישה
- הנחה

אבל **לא מצאתי תיעוד רשמי במקורות שנסקרו על קטגוריות מוצרים, collections, או limit מספרי רשמי של מוצרים לדף**.

לכן כרגע:  
`לא מתועד / לא זמין במקורות שנסקרו`

מקורות:  
- [הכל על יצירת דף מכירה לעסק](https://www.greeninvoice.co.il/help-center/all-about-sale-page/)
- [עדכון מלאי בדף המכירה](https://www.greeninvoice.co.il/help-center/sale-page-inventory/)

### 2.4 תהליך עדכון כשמוסיפים מוצר חדש

#### מסלול 1: קישור תשלום פשוט

המינימום הנדרש:

1. ליצור לינק חדש ב־Morning
2. להעתיק את ה־URL
3. לעדכן את כפתור/קישור ה־WordPress

אם עורכים לינק קיים:

- לפי התיעוד, העריכה מתעדכנת על אותו לינק קיים
- לכן ייתכן שלא צריך להחליף את הקישור באתר, רק לעדכן את הלינק עצמו ב־Morning

מקורות:  
- [יצירת לינק לתשלום](https://www.greeninvoice.co.il/help-center/create-payment-link/)
- [עריכת לינק לתשלום](https://www.greeninvoice.co.il/help-center/edit-payment-link/)

#### מסלול 2: דף מכירה / קטלוג Morning

המינימום הנדרש:

1. להיכנס לעריכת דף המכירה
2. `הגדרות -> המוצרים שלי`
3. להוסיף שם/מק״ט/תיאור/מחיר/תמונה
4. לשמור
5. אם הדף כבר באוויר – ללחוץ `עדכון הדף`

מסקנה:

- אם עמוד WordPress מפנה לדף המכירה, לא חייבים לעדכן את WordPress בכל מוצר חדש
- צריך לעדכן רק את דף המכירה ב־Morning

מקור:  
- [הכל על יצירת דף מכירה לעסק](https://www.greeninvoice.co.il/help-center/all-about-sale-page/)

#### מסלול 3: WooCommerce / אינטגרציה עמוקה

המינימום הנדרש גבוה יותר:

- תחזוקת מוצר ב־WordPress/WooCommerce
- תחזוקת plugin / חיבור Morning
- תחזוקת הגדרות מסמך / מטבע / שפה / סליקה

מסקנה:

זה כבר לא "אתר רזה", אלא stack יותר חנותי.

מקורות:  
- [חיבור ל-WooCommerce להפקת חשבוניות אוטומטיות (ללא שירותי סליקה)](https://www.greeninvoice.co.il/help-center/woocommerce-invoices-only/)
- [תוסף WooCommerce הרשמי](https://www.greeninvoice.co.il/woocommerce/)

### 2.5 דוגמאות שימוש נפוץ באתרי תוכן

לא מצאתי case studies רשמיים מפורטים של "אתרי תוכן" דווקא.

אבל כן מצאתי שימושים מתועדים רשמיים שמתאימים לאתרי תוכן:

#### א. לינק לתשלום שמוטמע כקישור באתר

מתועד מפורשות שאפשר:

- לשלבו כקישור באתר
- להפיצו בקמפיינים
- לשתף ב־WhatsApp

מקור:  
- [יצירת לינק לתשלום](https://www.greeninvoice.co.il/help-center/create-payment-link/)

#### ב. דף נחיתה / דף מכירה חיצוני שמקודם מתוך ערוצי תוכן

מתועד מפורשות שדפי המכירה נועדו להפצה ב:

- רשתות חברתיות
- WhatsApp
- קמפיינים
- URL ישיר

ואף שניתן לפרסם דף כ־landing page לפני שמפעילים בכלל תשלומים.

מקורות:  
- [הכל על יצירת דף מכירה לעסק](https://www.greeninvoice.co.il/help-center/all-about-sale-page/)
- [הגדרת אפשרויות תשלום](https://www.greeninvoice.co.il/help-center/set-payment-methods/)

#### ג. איסוף לידים מדפי מכירה

מתועד מפורשות שדף מכירה יכול לשמש גם ללידים:

- בלוק יצירת קשר
- בלוק רשימת תפוצה
- webhook לליד

מקורות:  
- [הגדרת שליחת וובהוק עבור לידים מדף מכירה](https://www.greeninvoice.co.il/help-center/sale-page-webhook/)
- [Webhook – sale-pages/page-contacted](https://www.greeninvoice.co.il/help-center/webhook-sales-page-contacted/)

## 3. אופציות A / B / C ליישום באתר WordPress רזה

### Option A — WordPress content + כפתור ללינק תשלום

#### מה זה

- כל עמוד מוצר ב־WordPress נשאר עמוד תוכן
- כפתור ה־CTA מוביל ל־`payment link` של Morning
- אין קטלוג Morning, רק לינקים נפרדים

#### יתרונות

- הפתרון הכי רזה
- מהיר להקמה
- לא דורש WooCommerce
- לא דורש API
- מתאים במיוחד למספר מוצרים קטן/בינוני

#### חסרונות

- תחזוקה ידנית של לינק לכל מוצר
- אין "ניהול הזמנות" בתוך WordPress
- אין קטלוג מאוחד בצד Morning

#### מתי לבחור

- אם רוצים לעלות מהר
- אם מספר המוצרים לא גדול
- אם האתר הוא בעיקר תוכן עם כפתור קנייה

### Option B — WordPress content + דף מכירה חיצוני של Morning

#### מה זה

- WordPress מציג את המוצר והתוכן
- כפתור ה־CTA מוביל ל־sale page של Morning
- ב־Morning מנהלים את המוצר/ים, אמצעי התשלום, מלאי, הנחות, קופונים והזמנות

#### יתרונות

- עדיין לא דורש API
- נותן יותר יכולות ecommerce מאופציה A
- מאפשר:
  - מוצרים
  - הנחות
  - קופונים
  - ניהול הזמנות
  - מלאי
  - delivery settings
  - lead capture
- אם שומרים URL קבוע לדף, רוב עדכוני המוצרים לא מחייבים שינוי ב־WordPress

#### חסרונות

- כל דף מכירה שפורסם עולה חודשי
- החוויה עוברת לאתר/דף חיצוני של Morning
- פחות "owned checkout experience"

#### מתי לבחור

- אם רוצים WordPress רזה אבל עם מעטפת מכירה משמעותית
- אם רוצים להימנע מ־WooCommerce
- אם רוצים hosted checkout/landing מהיר

### Option C — אינטגרציה עמוקה יותר: API / Webhooks / WooCommerce

#### מה זה

- WordPress מפעיל שכבת מכירה עמוקה יותר
- אפשרות אחת: WooCommerce + plugin רשמי של Morning
- אפשרות שנייה: אתר custom עם API + webhooks

#### יתרונות

- שליטה גבוהה יותר
- אוטומציה עמוקה יותר
- תרחישים מתקדמים יותר
- אפשרות לסנכרון הזמנות / מסמכים / אירועים

#### חסרונות

- יותר מורכב
- דורש `Best ומעלה`
- דורש תחזוקת אינטגרציה
- פחות מתאים ל־"אתר WordPress רזה"

#### מתי לבחור

- רק אם מתברר ש־A/B לא מספיקים
- מתאים יותר לשלב 2 מאשר לשלב הראשוני

## 4. תשובות קצרות לשאלות החובה

| שאלה | תשובה קצרה |
|---|---|
| סוגי קישורי תשלום | לינק קבוע, לינק פתוח, הוראת קבע, מסמך עם כפתור תשלום, sale page / landing page |
| API / Webhooks | כן, קיימים; `Best+`; Webhooks נראים רלוונטיים יותר מ־API בשלב ראשון |
| מגבלות | plan gating ברור; סליקה דיגיטלית בש״ח בלבד; Sale Pages בתשלום חודשי; מספר מוצרים/קטגוריות/שפות לדפי מכירה לא תועדו במפורש במקורות שנסקרו |
| תהליך עדכון מוצר חדש | בקישורים: ליצור/לעדכן לינק ולהדביק ב־WP; בדפי מכירה: לעדכן ב־Morning וללחוץ "עדכון הדף" |
| שימוש באתרי תוכן | כן, מתועד שאפשר לשלב לינק באתר, להשתמש בדף כ־landing page, ולאסוף לידים |

## 5. המלצה עבודה לצוות

### מה לא לעשות כרגע

- לא להתחיל מ־API אם אין בכך צורך
- לא לקפוץ ל־WooCommerce אם האתר מיועד להישאר רזה

### מה כן לבדוק מול אייל בהמשך

- האם רוצים **קישור לכל מוצר** או **דף מכירה לכל קבוצת מוצרים**
- האם יש צורך ב:
  - מלאי
  - קופונים
  - ניהול הזמנות
  - לידים
  - recurring payments

אם לא צריך את אלה, `Option A` כנראה יספיק.  
אם כן צריך חלק מהם, `Option B` נראה נקודת ביניים חזקה מאוד.

## 6. פערים / מה לא הצלחתי לאשר מהתיעוד הרשמי

- limit רשמי למספר מוצרים בדף מכירה
- תמיכה רשמית בקטגוריות מוצרים בתוך Sale Pages
- matrix שפות רשמי לדפי מכירה / payment links
- direct permalink מתועד למוצר בודד מחוץ ל-sale page

לכן יש לסמן את אלה כ:

`לא מתועד / לא זמין במקורות שנסקרו`

## 7. מקורות עיקריים

- [ממשק ה-API שלנו](https://www.greeninvoice.co.il/help-center/api/)
- [יצירת מפתח API](https://www.greeninvoice.co.il/help-center/generating-api-key/)
- [הגדרת Webhooks](https://www.greeninvoice.co.il/help-center/creating-webhook/)
- [יצירת לינק לתשלום](https://www.greeninvoice.co.il/help-center/create-payment-link/)
- [יצירת לינק לתשלום בסכום פתוח](https://www.greeninvoice.co.il/help-center/open-payment-link/)
- [יצירת לינק להוראת קבע](https://www.greeninvoice.co.il/help-center/recurring-charges-link/)
- [דפי המכירה שלנו](https://www.greeninvoice.co.il/help-center/sales-pages/)
- [הכל על יצירת דף מכירה לעסק](https://www.greeninvoice.co.il/help-center/all-about-sale-page/)
- [הגדרת אפשרויות תשלום](https://www.greeninvoice.co.il/help-center/set-payment-methods/)
- [קבלת תשלום בדפי מכירה](https://www.greeninvoice.co.il/help-center/sales-page-payment)
- [ניהול הזמנות](https://www.greeninvoice.co.il/help-center/order-management-pages/)
- [חיבור לתשלומים דיגיטליים](https://www.greeninvoice.co.il/help-center/digital-payments-connect/)
- [WooCommerce – הפקת חשבוניות בלבד](https://www.greeninvoice.co.il/help-center/woocommerce-invoices-only/)
- [תוסף WooCommerce הרשמי](https://www.greeninvoice.co.il/woocommerce/)

## 8. הערת מסירה

לא נמצא בקודקס כרגע קובץ `GREEN-INVOICE-LINK-MAP.md`, ולכן הדוח הזה לא קושר אליו בשלב זה.

## 9. התאמה להעדפות שהוגדרו לאחר המחקר

לאחר השלמת המחקר הוגדרו ההעדפות הבאות:

- תשלום בשקלים בלבד
- תשלום לקהל בישראל בלבד
- WordPress בסיסי
- ללא תוספים מורכבים באתר
- ללא פיתוח מורכב
- העדפה לפתרון פשוט ויציב גם אם הממשק פחות אופטימלי

### משמעות ההעדפות על בחירת המסלול

ההעדפות הללו מצמצמות בפועל את מרחב האפשרויות למסלול אחד מועדף ברור.

### המסלול המומלץ כעת

#### Recommendation A1 — WordPress תוכני + כפתור ללינק תשלום

זהו מסלול היישום המומלץ ביותר כעת.

מה זה אומר:

- כל עמוד מוצר נשאר עמוד תוכן רגיל ב-WordPress
- כפתור ה-CTA בעמוד מוביל ללינק תשלום של Morning
- אין סל באתר
- אין checkout באתר
- אין WooCommerce
- אין API
- אין Webhooks
- אין plugin מסחרי ייעודי

### למה זו ההמלצה המעודכנת

#### 1. התאמה לשקלים בלבד

Morning תומכת באופן מתועד בתשלומים דיגיטליים בשקלים בלבד, כך שהמגבלה הזו אינה בעיה אלא התאמה טבעית.

מקור:  
- [חיבור לתשלומים דיגיטליים](https://www.greeninvoice.co.il/help-center/digital-payments-connect/)

#### 2. התאמה לישראל בלבד

מאחר שהפרויקט אינו דורש כרגע תמיכה בינלאומית, אין הצדקה לבחור מסלול מורכב יותר שנועד לפתור תרחישים של מטבעות, מדינות או checkout רב-שכבתי.

#### 3. התאמה ל-WordPress בסיסי

המסלול של לינק תשלום חיצוני מאפשר להשאיר את WordPress כשכבת תוכן בלבד:

- ללא WooCommerce
- ללא ניהול הזמנות באתר
- ללא סנכרון מוצרים
- ללא תחזוקת תוספי מסחר

#### 4. התאמה לרצון להימנע מפיתוח מורכב

כל מסלול מבוסס API / Webhooks / WooCommerce מוסיף מורכבות תפעולית ופיתוחית שלא נדרשת לצורך הנוכחי.

לכן, אף על פי שיכולות אלו קיימות במוצר, הן אינן המסלול הנכון כרגע.

### מסלולים שכדאי לדחות

#### Option B — Sale Pages

עדיין ישים, אך אינו ברירת המחדל לאחר ההעדפות החדשות.

למה לא כברירת מחדל:

- מייצר חוויה חיצונית יותר
- דורש ניהול נוסף בתוך Morning
- בתשלום חודשי לכל דף מכירה מפורסם
- מתאים רק אם באמת צריך יכולות שאין בלינק פשוט

מתי כן לשקול:

- אם יש צורך במלאי
- אם יש צורך בקופונים
- אם יש צורך בניהול הזמנות
- אם רוצים למכור כמה פריטים דרך אותו דף ייעודי

#### Option C — API / Webhooks / WooCommerce

לא מומלץ בשלב זה.

למה:

- מורכב מדי
- לא תואם WordPress בסיסי
- מיותר ביחס לצורך
- מוסיף coupling ותחזוקה

### המלצה תפעולית מעודכנת

#### מודל עבודה מומלץ

לכל מוצר:

1. יוצרים או מעדכנים עמוד תוכן ב-WordPress
2. יוצרים או מעדכנים לינק תשלום ב-Morning
3. מדביקים את הקישור בכפתור בעמוד

#### יתרונות המודל

- פשוט מאוד
- יציב
- מובן לכל עורך אתר
- לא יוצר תלות במפתחים לכל שינוי קטן
- נמנע מהפיכת האתר לחנות מורכבת

#### חסרונות שמתקבלים במודע

- חוויית קנייה פחות "חלקה" מחנות מלאה
- תחזוקה ידנית של קישור לכל מוצר
- אין עגלה באתר
- אין מרכז ניהול הזמנות בתוך וורדפרס

החסרונות הללו מתקבלים כאן במודע, כי הם תואמים את ההעדפה לפתרון פשוט ויציב.

### נוסח החלטה קצר

בהתאם להעדפות המעודכנות, המסלול המועדף הוא:

`WordPress בסיסי + לינק תשלום חיצוני של Morning לכל מוצר`

והמסלולים של `Sale Pages` או `API/WooCommerce` יישמרו רק כאופציות עתידיות או חריגות.
