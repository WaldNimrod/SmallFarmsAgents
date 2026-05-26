<?php
// DO NOT EDIT — regenerate from MODULES_REGISTRY.yaml
return array (
  'version' => '1.0.0',
  'updated' => '2026-05-24',
  'tiers' => 
  array (
    'open' => 
    array (
      'label_he' => 'כלים לקהילה',
      'short_he' => 'פתוח',
      'color' => 'leaf',
      'description_he' => 'שירות ציבורי פתוח — נתונים מצרפיים, השוואת גורפים, בלי הרשמה ובלי תשלום. תרומה לקהילה החקלאית.',
    ),
    'beta' => 
    array (
      'label_he' => 'בטא · ניסיוני',
      'short_he' => 'בטא',
      'color' => 'sun',
      'description_he' => 'בפיתוח פעיל. ייתכנו שינויים, מוזמנים לתת פידבק.',
    ),
    'coming' => 
    array (
      'label_he' => 'בקרוב',
      'short_he' => 'בקרוב',
      'color' => 'paper',
      'description_he' => 'אנחנו עובדים על זה. השאירו פרטים כדי לקבל הודעה כשנפתח.',
    ),
    'paid' => 
    array (
      'label_he' => 'כלים מתקדמים',
      'short_he' => 'בתשלום',
      'color' => 'soil',
      'description_he' => 'יכולות תפעוליות מורחבות לחוות פעילות — תמחור לפי גודל ושימוש.',
    ),
    'custom' => 
    array (
      'label_he' => 'בדיוק לחווה שלך',
      'short_he' => 'בהזמנה',
      'color' => 'tomato',
      'description_he' => 'אינטגרציות וכלים מותאמים אישית — דברו איתנו, נתפור עבורכם.',
    ),
  ),
  'modules' => 
  array (
    0 => 
    array (
      'id' => 'crop-book',
      'name_he' => 'ספר גידולים',
      'name_en' => 'Crop Book',
      'sub' => 'אינדקס פתוח של גידולים, זנים, מחזורי גידול',
      'tier' => 'open',
      'icon' => 'lettuce',
      'thumb_prompt' => 'module_thumb_book',
      'stat' => '66 גידולים · 242 זנים',
      'stat_count' => 66,
      'color' => 'leaf',
      'route' => '/sfa/book/',
      'shortcode' => '[sfagent_crop_book]',
      'status' => 'live',
      'route_runtime' => '/crop-book/',
    ),
    1 => 
    array (
      'id' => 'market',
      'name_he' => 'מחירון',
      'name_en' => 'Market Index',
      'sub' => 'מדד מחירי תוצרת מנורמל יומי',
      'tier' => 'open',
      'icon' => 'tomato',
      'thumb_prompt' => 'module_thumb_market',
      'stat' => '30 מוצרים · 14 מקורות',
      'stat_count' => 30,
      'color' => 'tomato',
      'route' => '/sfa/market/',
      'shortcode' => '[sfagent_market_report]',
      'status' => 'live',
      'route_runtime' => '/market/',
    ),
    2 => 
    array (
      'id' => 'calc',
      'name_he' => 'מחשבון לחקלאי',
      'name_en' => 'Farmer Calculator',
      'sub' => 'תכנון רווחיות, שטחים, יבולים',
      'tier' => 'beta',
      'icon' => 'carrot',
      'thumb_prompt' => 'module_thumb_calc',
      'stat' => 'גרסת בטא · בפיתוח',
      'stat_count' => NULL,
      'color' => 'sun',
      'route' => '/sfa/calc/',
      'shortcode' => '[sfagent_app view="calc"]',
      'status' => 'beta',
      'route_runtime' => '/calc/',
    ),
    3 => 
    array (
      'id' => 'planner',
      'name_he' => 'תכנון עונה',
      'name_en' => 'Season Planner',
      'sub' => 'ערוגות, רוטציה, לוח שתילה',
      'tier' => 'coming',
      'icon' => 'basil',
      'thumb_prompt' => 'module_thumb_plan',
      'stat' => 'בקרוב',
      'color' => 'leaf',
      'route' => '/sfa/planner/',
      'shortcode' => '',
      'status' => 'planned',
      'route_runtime' => '/planner/',
    ),
    4 => 
    array (
      'id' => 'clients',
      'name_he' => 'ניהול לקוחות',
      'name_en' => 'Customer Management',
      'sub' => 'מנויי סלי תוצרת, חיובים, תקשורת',
      'tier' => 'paid',
      'icon' => 'cucumber',
      'thumb_prompt' => 'module_thumb_clients',
      'stat' => 'כלים מתקדמים',
      'color' => 'soil',
      'route' => '/sfa/clients/',
      'shortcode' => '',
      'status' => 'planned',
      'route_runtime' => '/clients/',
    ),
    5 => 
    array (
      'id' => 'inventory',
      'name_he' => 'מעקב יבול ומלאי',
      'name_en' => 'Yield & Inventory',
      'sub' => 'קצירה, אובדנים, מלאי קר',
      'tier' => 'paid',
      'icon' => 'strawberry',
      'thumb_prompt' => 'module_thumb_inv',
      'stat' => 'כלים מתקדמים',
      'color' => 'tomato',
      'route' => '/sfa/inventory/',
      'shortcode' => '',
      'status' => 'planned',
      'route_runtime' => '/inventory/',
    ),
    6 => 
    array (
      'id' => 'tend-bridge',
      'name_he' => 'חיבור Tend / חשבונית-ירוקה',
      'name_en' => 'Tend Bridge',
      'sub' => 'סנכרון חשבוניות והכנסות',
      'tier' => 'custom',
      'icon' => 'pepper',
      'thumb_prompt' => 'module_thumb_tend',
      'stat' => 'לפי הזמנה',
      'color' => 'soil',
      'route' => '/sfa/integrations/tend/',
      'shortcode' => '',
      'status' => 'custom',
      'route_runtime' => '/integrations/tend/',
    ),
    7 => 
    array (
      'id' => 'field-log',
      'name_he' => 'יומן שדה',
      'name_en' => 'Field Log',
      'sub' => 'תיעוד מזג אוויר, מחלות, טיפולים',
      'tier' => 'custom',
      'icon' => 'onion',
      'thumb_prompt' => 'module_thumb_field',
      'stat' => 'לפי הזמנה',
      'color' => 'leaf',
      'route' => '/sfa/field-log/',
      'shortcode' => '',
      'status' => 'custom',
      'route_runtime' => '/field-log/',
    ),
  ),
  'pages' => 
  array (
    0 => 
    array (
      'id' => 'hub-home',
      'route' => '/sfa/',
      'component' => 'HubHome',
      'title_he' => 'כלים גדולים לחוות קטנות',
      'route_runtime' => '/',
    ),
    1 => 
    array (
      'id' => 'about',
      'route' => '/sfa/about/',
      'component' => 'HubTiers',
      'title_he' => 'איך זה עובד?',
      'route_runtime' => '/about/',
    ),
    2 => 
    array (
      'id' => 'search',
      'route' => '/sfa/search/',
      'component' => 'Desktop_Search',
      'title_he' => 'חיפוש',
      'route_runtime' => '/search/',
    ),
    3 => 
    array (
      'id' => 'community',
      'route' => '/sfa/community/',
      'component' => 'Desktop_Community',
      'title_he' => 'קהילה',
      'route_runtime' => '/community/',
    ),
  ),
  'contact' => 
  array (
    'whatsapp' => '972547776770',
    'whatsapp_label' => '054-7776770',
    'whatsapp_intro' => 'שיחה של 15 דקות → הצעה. ‎WhatsApp 054-7776770',
    'email' => NULL,
    'email_label' => NULL,
  ),
  'ai_prompts' => 
  array (
    'hero_market' => 'איור בסגנון אקוורל חם וסגנון nimrod.bio. מבט-על על שולחן עץ מחוספס פרושים עליו ירקות
שורש: גזרים, סלק, בצל, צלפים, צרורות פטרוזיליה. אור בוקר רך מהצד הימני, צללים
ארוכים וחמימים. פלטה: טראקוטה אדמדמה, ירוק זית, חרדל-זהב, קרם נייר. דחיסות
גבוהה במרכז, שוליים בהירים יותר. ללא טקסט. 16:9.
',
    'hero_book' => 'איור בסגנון אקוורל חם וסגנון nimrod.bio. שדה חקלאות אקולוגית קטנה בפרדס חנה — שורות
גידול ירוקות-עמוקות בעוקבות-עוקבות, ערפל בוקר עדין, מעט שמש מבצבצת בקצה
השמאל-עליון. שתי דמויות מטושטשות בעבודת שדה ברקע. פלטה: ירוק עמוק,
כחול-אפור ערפילי, צהוב חמאתי. תחושת "קטן זה יפה, לאט זה שפוי". ללא טקסט. 16:9.
',
    'hero_calc' => 'איור בסגנון אקוורל חם וסגנון nimrod.bio. שולחן עבודה כפרי — מחברת מקופלת עם רישומי
עיפרון של מספרים וערוגות, סרגל עץ ישן, ספל קפה, מגוון זרעים בכפיות כפולות
מעוצבים בצורת רכוז דאטה. פלטה: חום-קקאו, ירוק זית, קרם, מעט תכלת.
רגוע, מתמטי-יד. ללא טקסט. 16:9.
',
    'module_hub' => 'איור בסגנון אקוורל חם וסגנון nimrod.bio. מבט מלמעלה על שולחן עבודה של חקלאי-מתכנן
— מפת ערוגות צבועה ביד, סרגל, פרוסות תפוז, גזיר עיתון, צרור מרווה. אווירה של
"סדנת מחקר ביתית". פלטה: קרם דהוי, ירוק זית, חמרה-טראקוטה, צל-כחול. ללא
טקסט. 16:9.
',
    'contact' => 'איור אקוורל חם. שני אנשים יושבים על ספסל-עץ פשוט מול חממה קטנה, שיחה
ידידותית. פלטה אדמה-ירוק-חמאה. ללא טקסט. 16:9.
',
    'module_thumb_book' => 'איור אקוורל קטן וריבועי. צרור ירוקים — חסה, בזיליקום, פטרוזיליה — בצרור קצר. פלטה ירוקה רכה עם רקע קרם נייר. ללא טקסט. 1:1.',
    'module_thumb_market' => 'איור אקוורל קטן וריבועי. שלושה גזרים על קופסת עץ קטנה, מבט מהצד. פלטה כתום-טראקוטה עם רקע קרם נייר. ללא טקסט. 1:1.',
    'module_thumb_calc' => 'איור אקוורל קטן וריבועי. מחברת חוט-ספירלי פתוחה עם רישומי דמויות-ערוגות וחישובים בעט עפרון. פלטה חום-קקאו עם רקע קרם. ללא טקסט. 1:1.',
    'module_thumb_plan' => 'איור אקוורל קטן וריבועי. לוח שנה חקלאי עם איקונים של ירקות, סימוני סהר ושמש. פלטה ירוק-זית עם רקע קרם. ללא טקסט. 1:1.',
    'module_thumb_clients' => 'איור אקוורל קטן וריבועי. ספל קפה ומשקפיים על דפים — לקוחות-נאמנים. פלטה חום-קפה עם רקע קרם. ללא טקסט. 1:1.',
    'module_thumb_inv' => 'איור אקוורל קטן וריבועי. ארגז עץ עם תוצרת מגוונת — תות, עגבנייה, סלרי. פלטה אדומה-ירוקה עם רקע קרם. ללא טקסט. 1:1.',
    'module_thumb_tend' => 'איור אקוורל קטן וריבועי. דף קווי אקסל-מעוצב-יד עם מספרים, חיבור צינור-משאבה דקורטיבי. פלטה אפור-תכלת עם רקע קרם. ללא טקסט. 1:1.',
    'module_thumb_field' => 'איור אקוורל קטן וריבועי. כלי עבודה — מעדר ויד-חופרת — מונחים על אדמה. פלטה חום-אדמה עם רקע קרם. ללא טקסט. 1:1.',
  ),
);
