<?php
/**
 * hub_tiers.php — Route /about — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frame `about-tiers`.
 * Components: .tier-hero (§41), .tier-list, .tier-row (+--leaf/sun/paper/soil/tomato).
 *
 * Data contract (HubController::tiers):
 *   $tiers — MODULES_REGISTRY.yaml.tiers (keyed by tier id)
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

// Display order — open → beta → coming → paid → custom
$tier_order = ['open', 'beta', 'coming', 'paid', 'custom'];

// Color modifiers per tier
$tier_colors = [
    'open'   => 'leaf',
    'beta'   => 'sun',
    'coming' => 'paper',
    'paid'   => 'soil',
    'custom' => 'tomato',
];

// Tier examples
$tier_examples = [
    'open'   => ['title' => 'ספר גידולים', 'sub' => 'מחירון שוק'],
    'beta'   => ['title' => 'מחשבון שדה', 'sub' => 'ניסיוני'],
    'coming' => ['title' => 'יומן שדה', 'sub' => 'בפיתוח'],
    'paid'   => ['title' => 'מנהל לקוחות', 'sub' => 'מנוי'],
    'custom' => ['title' => 'נתוני שדה', 'sub' => 'בדיוק לחווה'],
];

$fallback_copy = [
    'open'   => 'הכלים הפתוחים — לכולם, ללא הרשמה. ספר גידולים, מחירון, מחשבון.',
    'beta'   => 'בטא — בפיתוח פעיל. משוב במייל / וואטסאפ.',
    'coming' => 'בקרוב — מתוכנן, לא זמין עדיין.',
    'paid'   => 'כלים מתקדמים — מנהל לקוחות, מעקב יבול. למודל מנוי.',
    'custom' => 'בדיוק לחווה שלך — נתוני שדה, יומן שדה, אינטגרציות ייעודיות. דברו איתנו.',
];

$tiers_in = is_array($tiers ?? null) ? $tiers : [];

$page_title = 'מה זה SFA';
$page_sub   = 'איך הכלים מסודרים';
$active     = 'home';

$wa_custom = 'https://wa.me/972547776770?text=' . rawurlencode('בדיוק לחווה שלי — דברו איתי');
ob_start();
?>
<div style="max-width:800px;margin:0 auto;padding:20px clamp(16px,3vw,28px)">

  <?php /* FIX 4: content-first — lead with what SFA is + the four value points. */ ?>
  <div class="about-intro">
    <h1>כלים פתוחים לחקלאות קטנה</h1>
    <p class="about-lead">SFA מרכז ידע חקלאי, מחירי שוק וכלי תכנון — חינמיים ופתוחים לכל גנן וחקלאי. נבנה בשיתוף הקהילה, על בסיס ניסיון מהשטח ומחקר.</p>
    <div class="about-points">
      <div class="about-point"><span class="ic"><svg class="gi" aria-hidden="true"><use href="#i-book"/></svg></span><div><h4>ידע פתוח</h4><p>מאגר גידולים — זנים, מרווחים, מחזורי גידול ומקורות מתועדים.</p></div></div>
      <div class="about-point"><span class="ic">₪</span><div><h4>מחירי שוק שקופים</h4><p>ממוצעים מתגלגלים מתוצרת טרייה, מתעדכנים יומית.</p></div></div>
      <div class="about-point"><span class="ic"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg></span><div><h4>כלי תכנון</h4><p>מחשבונים מנומקים — מהזרע ועד היבול וההכנסה.</p></div></div>
      <div class="about-point"><span class="ic"><svg class="gi" aria-hidden="true"><use href="#i-companions"/></svg></span><div><h4>נבנה בשיתוף</h4><p>הליבה תמיד פתוחה; הקהילה משלימה נתונים ומשפרת.</p></div></div>
    </div>
  </div>

  <?php /* Tier ladder — secondary expansion below the content (2 live / 3 soon). */ ?>
  <div class="about-tiers-h"><h2>השכבות</h2><span class="rule"></span><span class="sub">מה פתוח · מה בקרוב</span></div>

  <div class="tier-group tier-group--live">
    <div class="tier-group__head"><h2 style="font-size:15px">פעיל עכשיו</h2><span class="count">2</span><span class="rule"></span></div>
    <div class="tier-list">
      <div class="tier-row tier-row--leaf">
        <div class="tier-row__badge">
          <?php $tier = 'open'; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
          <span class="en dir-ltr">OPEN CORE</span>
        </div>
        <div class="tier-row__txt"><h3>ספר + מחירון</h3><p>כל הידע, החיפוש, לוחות הזריעה והמחשבונים — חינם, ללא חשבון.</p></div>
        <span class="tier-row__status tier-row__status--live"><span class="dot"></span>זמין</span>
      </div>
      <div class="tier-row tier-row--sun">
        <div class="tier-row__badge">
          <?php $tier = 'beta'; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
          <span class="en dir-ltr">BETA</span>
        </div>
        <div class="tier-row__txt"><h3>מחשבון מלא</h3><p>דשבורד מודולים עם סיכום וייצוא — פתוח לניסיון.</p></div>
        <span class="tier-row__status tier-row__status--live"><span class="dot"></span>זמין</span>
      </div>
    </div>
  </div>

  <div class="tier-group tier-group--soon">
    <div class="tier-group__head"><h2 style="font-size:15px">בקרוב</h2><span class="count">3</span><span class="rule"></span></div>
    <div class="tier-list">
      <div class="tier-row tier-row--paper">
        <div class="tier-row__badge">
          <?php $tier = 'coming'; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
          <span class="en dir-ltr">COMING</span>
        </div>
        <div class="tier-row__txt"><h3>מתכנן עונה ומשימות</h3><p>תכנון ערוגות ולוח משימות שבועי.</p></div>
        <span class="tier-row__status tier-row__status--soon"><span class="dot"></span>בפיתוח</span>
      </div>
      <div class="tier-row tier-row--soil">
        <div class="tier-row__badge">
          <?php $tier = 'paid'; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
          <span class="en dir-ltr">PAID</span>
        </div>
        <div class="tier-row__txt"><h3>ניהול לקוחות ומלאי</h3><p>מודולים מסחריים לחווה — מנוי.</p></div>
        <span class="tier-row__status tier-row__status--soon"><span class="dot"></span>בקרוב</span>
      </div>
      <div class="tier-row tier-row--tomato">
        <div class="tier-row__badge">
          <?php $tier = 'custom'; $size = 'lg'; include __DIR__ . '/../macros/tier_badge.php'; ?>
          <span class="en dir-ltr">CUSTOM</span>
        </div>
        <div class="tier-row__txt"><h3>פתרונות מותאמים</h3><p>אינטגרציות ופיתוח ייעודי לחוות וארגונים.</p></div>
        <span class="tier-row__status tier-row__status--soon"><span class="dot"></span>בתיאום</span>
      </div>
    </div>
  </div>

  <?php /* CTA system (FIX 4 + CTA SYSTEM): data (primary) · suggest (inline FORM) · WhatsApp (custom only). */ ?>
  <div class="cta">
    <div class="cta__card cta--data">
      <h3>הצטרפו לבנייה — השלימו מידע</h3>
      <p>הספר גדל מתרומות. שדה חסר שאתם מכירים? ספרו לנו.</p>
      <a class="cta__btn" href="/community">◐ השלמת מידע ›</a>
    </div>
    <div class="cta__card cta--suggest">
      <h3>הצעה או בקשה?</h3>
      <p>אין צ׳אט — טופס קצר.</p>
      <form class="cta__field" method="post" action="/community#suggest">
        <input type="text" name="suggestion" placeholder="מה תרצו לראות?" aria-label="הצעה"/>
        <button class="cta__send" type="submit">שליחה</button>
      </form>
    </div>
    <div class="cta__card cta--wa">
      <span class="ic" aria-hidden="true"><svg class="gi"><use href="#i-chat"/></svg></span>
      <div><h3>פתרון מותאם לחווה?</h3><p>פנייה ישירה בוואטסאפ</p></div>
      <a class="cta__btn" href="<?= $h($wa_custom) ?>" target="_blank" rel="noopener">וואטסאפ</a>
    </div>
  </div>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
