<?php
/**
 * hub_home.php — Hub home page (route: /) — Class B v2
 *
 * WP-CB-UI-CLASSB — team_10 build on Board-B frame `hub-home` / `hub-home-mobile`.
 * Components: .hub-intro, .hub-groupbar, .hub-grid, .modtile (§31),
 *             .hub-manifest (§32), .hub-aud / .audcard (§32).
 *
 * Data contract (HubController::home):
 *   $modules  array — MODULES_REGISTRY.yaml.modules
 *   $tiers    array — MODULES_REGISTRY.yaml.tiers
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$modules_in = is_array($modules ?? null) ? $modules : [];
$tiers_in   = is_array($tiers ?? null) ? $tiers : [];

// Hero image map (per WP-CB-1-patch01 art)
$module_hero_map = [
    'crop-book' => '/public_assets/img/modules/module-crop-book.png',
    'market'    => '/public_assets/img/modules/module-market.png',
    'calc'      => '/public_assets/img/modules/module-calc.png',
];

// Tier-color → modtile modifier
$tier_color_map = [
    'leaf'   => 'leaf',
    'sun'    => 'sun',
    'soil'   => 'soil',
    'tomato' => 'tomato',
    'paper'  => '',
];

// Icon sprite map — DSX-1: line glyphs from icons.svg (crops) / ui-icons.svg,
// never OS emoji (locked principle #6). Module icon name → sprite id.
$icon_sprite_map = [
    'tomato' => 'icon-tomato', 'lettuce' => 'icon-lettuce', 'cucumber' => 'icon-cucumber',
    'carrot' => 'icon-carrot', 'pepper'  => 'icon-pepper',  'onion'    => 'icon-onion',
    'eggplant' => 'icon-eggplant', 'zucchini' => 'icon-zucchini',
    'seedling' => 'i-seedling', 'leaf' => 'icon-leaf', 'basil' => 'icon-leaf',
    'journal' => 'i-journal', 'box' => 'i-box', 'receipt' => 'i-receipt',
    'calc' => 'i-scale', 'market' => 'i-basket', 'book' => 'i-book',
];

// Partition modules: live/beta = open grid; planned/coming = soon
$open_mods = [];
$soon_mods = [];
foreach ($modules_in as $m) {
    $status = (string)($m['status'] ?? 'planned');
    if (in_array($status, ['live', 'beta'], true)) {
        $open_mods[] = $m;
    } else {
        $soon_mods[] = $m;
    }
}

// Stats from module registry
$crop_count    = 0;
$product_count = 0;
foreach ($modules_in as $m) {
    if (($m['id'] ?? '') === 'crop-book')  { $crop_count    = (int)($m['stat_count'] ?? 0); }
    if (($m['id'] ?? '') === 'market')     { $product_count = (int)($m['stat_count'] ?? 0); }
}

$page_title = 'SFA';
$page_sub   = 'חקלאות מקומית';
$active     = 'home';

ob_start();
?>
<div class="sh__body--wide">
<div class="hub-home__inner">

  <?php /* ── Hub intro ── */ ?>
  <div class="hub-intro">
    <div class="hub-intro__txt">
      <h1>כלים פתוחים לחקלאות <em>מקומית</em></h1>
      <p>ספר גידולים קהילתי, מחירון שוק בזמן-אמת, ומחשבון שדה — בנויים על ניסיון שדה ומחקר AI.</p>
    </div>
    <div class="hub-intro__stats">
      <?php if ($crop_count > 0): ?>
        <span class="pill pill--leaf"><?= (int)$crop_count ?> גידולים</span>
      <?php endif; ?>
      <?php if ($product_count > 0): ?>
        <span class="pill pill--tomato"><?= (int)$product_count ?> מוצרים</span>
      <?php endif; ?>
    </div>
  </div>

  <?php /* ── Open tools ── */ ?>
  <?php if (!empty($open_mods)): ?>
  <div class="hub-groupbar">
    <h2>כלים פתוחים</h2>
    <span class="gj-eyebrow">זמינים עכשיו</span>
  </div>
  <div class="hub-grid">
    <?php foreach ($open_mods as $m):
      $m_id      = (string)($m['id']      ?? '');
      $m_name    = (string)($m['name_he'] ?? '');
      $m_sub     = (string)($m['sub']     ?? '');
      $m_stat    = (string)($m['stat']    ?? '');
      $m_tier    = (string)($m['tier']    ?? 'open');
      $m_color   = (string)($m['color']   ?? 'leaf');
      $m_icon    = (string)($m['icon']    ?? 'leaf');
      $m_route   = str_replace('/book/', '/crop-book/', preg_replace('#^/sfa/#', '/', (string)($m['route'] ?? '#')));
      $hero_url  = $module_hero_map[$m_id] ?? '';
      $tile_mod  = $tier_color_map[$m_color] ?? '';
      $glyph     = $icon_sprite_map[$m_icon] ?? 'i-grid';
    ?>
    <a class="modtile modtile--row<?= $tile_mod !== '' ? ' modtile--' . $h($tile_mod) : '' ?>" href="<?= $h($m_route) ?>">
      <div class="modtile__art">
        <?php if ($hero_url !== ''): ?>
          <img src="<?= $h($hero_url) ?>" alt="" loading="lazy" decoding="async">
        <?php endif; ?>
        <span class="modtile__tier">
          <?php $tier = $m_tier; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        </span>
        <span class="modtile__glyph" aria-hidden="true"><svg class="gi"><use href="#<?= $h($glyph) ?>"/></svg></span>
      </div>
      <div class="modtile__body">
        <div class="modtile__title"><?= $h($m_name) ?></div>
        <p class="modtile__desc"><?= $h($m_sub) ?></p>
        <div class="modtile__foot">
          <?php if ($m_stat !== ''): ?>
            <span class="modtile__stat"><?= $h($m_stat) ?></span>
          <?php endif; ?>
          <span class="modtile__go">כניסה ←</span>
        </div>
      </div>
    </a>
    <?php endforeach; ?>
    <?php /* ── WP-CB-UI-patch01: Field Log in-development teaser tile ── */ ?>
    <div class="modtile modtile--row modtile--soil is-dev" aria-disabled="true">
      <div class="modtile__art">
        <span class="modtile__glyph" aria-hidden="true"><svg class="gi"><use href="#i-journal"/></svg></span>
      </div>
      <div class="modtile__body">
        <div class="modtile__title">יומן השדה</div>
        <p class="modtile__desc">תיעוד פעולות שדה — זריעה, השקיה, יבול ומשימות</p>
        <div class="modtile__foot">
          <span class="modtile__go">בפיתוח</span>
        </div>
      </div>
    </div>
  </div>
  <?php endif; ?>

  <?php /* ── Hub manifest band ── */ ?>
  <div class="hub-manifest">
    <svg class="hub-manifest__mark" aria-hidden="true"><use href="#sfa-logo"/></svg>
    <div class="hub-manifest__txt">
      <h2>ידע פתוח לחקלאות <em>מקומית</em></h2>
      <p>SFA נבנה על ניסיון שדה קהילתי ומחקר AI מתקדם. כל נתון — מחיר, מינון, מועד — פתוח לעיון ולתרומה.</p>
    </div>
    <div class="hub-manifest__stats">
      <?php if ($crop_count > 0): ?>
        <div class="hub-manifest__stat">
          <b><?= (int)$crop_count ?></b>
          <span>גידולים בספר</span>
        </div>
      <?php endif; ?>
      <?php if ($product_count > 0): ?>
        <div class="hub-manifest__stat">
          <b><?= (int)$product_count ?></b>
          <span>מוצרים במחירון</span>
        </div>
      <?php endif; ?>
    </div>
  </div>

  <?php /* ── Audience entry cards ── */ ?>
  <div class="hub-groupbar">
    <h2>למי זה מתאים?</h2>
  </div>
  <div class="hub-aud">
    <a class="audcard audcard--leaf" href="/crop-book/">
      <div class="audcard__ic"><svg class="gi" aria-hidden="true"><use href="#i-sprout"/></svg></div>
      <div class="audcard__t">גנן<small>GARDENER</small></div>
      <p class="audcard__d">ספר גידולים עם מועדי זריעה, ריווח וצרכי דישון — לגינה הקטנה.</p>
      <span class="audcard__go">לספר הגידולים ←</span>
    </a>
    <a class="audcard audcard--soil" href="/market/">
      <div class="audcard__ic"><svg class="gi" aria-hidden="true"><use href="#i-tractor"/></svg></div>
      <div class="audcard__t">חקלאי מקומי<small>FARMER</small></div>
      <p class="audcard__d">מחירון שוק בזמן-אמת ומחשבון שדה — לקבלת החלטות חכמה.</p>
      <span class="audcard__go">למחירון ←</span>
    </a>
    <a class="audcard audcard--code" href="/about">
      <div class="audcard__ic"><svg class="gi" aria-hidden="true"><use href="#i-bulb"/></svg></div>
      <div class="audcard__t">מתכנן / יועץ<small>PLANNER</small></div>
      <p class="audcard__d">כלים מתקדמים לניהול לקוחות, מעקב יבול ואינטגרציות שדה.</p>
      <span class="audcard__go">על הכלים ←</span>
    </a>
  </div>

  <?php /* ── Coming-soon modules ── */ ?>
  <?php if (!empty($soon_mods)): ?>
  <div class="hub-groupbar">
    <h2>כלים מתקדמים</h2>
    <span class="gj-eyebrow">בקרוב</span>
  </div>
  <div class="hub-grid">
    <?php foreach ($soon_mods as $m):
      $m_name    = (string)($m['name_he'] ?? '');
      $m_sub     = (string)($m['sub']     ?? '');
      $m_tier    = (string)($m['tier']    ?? 'coming');
      $m_color   = (string)($m['color']   ?? 'leaf');
      $m_icon    = (string)($m['icon']    ?? 'leaf');
      $m_id      = (string)($m['id']      ?? '');
      $hero_url  = $module_hero_map[$m_id] ?? '';
      $tile_mod  = $tier_color_map[$m_color] ?? '';
      $glyph     = $icon_sprite_map[$m_icon] ?? 'i-grid';
    ?>
    <div class="modtile modtile--row<?= $tile_mod !== '' ? ' modtile--' . $h($tile_mod) : '' ?> is-soon" aria-disabled="true">
      <div class="modtile__art">
        <?php if ($hero_url !== ''): ?>
          <img src="<?= $h($hero_url) ?>" alt="" loading="lazy" decoding="async">
        <?php endif; ?>
        <span class="modtile__tier">
          <?php $tier = $m_tier; $size = 'sm'; include __DIR__ . '/../macros/tier_badge.php'; ?>
        </span>
        <span class="modtile__glyph" aria-hidden="true"><svg class="gi"><use href="#<?= $h($glyph) ?>"/></svg></span>
      </div>
      <div class="modtile__body">
        <div class="modtile__title"><?= $h($m_name) ?></div>
        <p class="modtile__desc"><?= $h($m_sub) ?></p>
        <div class="modtile__foot">
          <span class="modtile__go">בקרוב</span>
        </div>
      </div>
    </div>
    <?php endforeach; ?>
  </div>
  <?php endif; ?>


  <?php /* ── Hub CTA system (FIX 5 + CTA SYSTEM) ──
           data (primary, complete missing data) · suggest (inline FORM, never
           WhatsApp) · WhatsApp (custom/paid only). */ ?>
  <?php
  $cta_wa_num  = '972547776770';
  if (!empty($contact) && is_array($contact)) {
      $cta_wa_num = preg_replace('/\D/', '', (string)($contact['whatsapp'] ?? '972547776770'));
  }
  $cta_wa_link = 'https://wa.me/' . $cta_wa_num . '?text=' . rawurlencode('פתרון מותאם לחווה שלי — דברו איתי');
  ?>
  <div class="cta">
    <div class="cta__card cta--data">
      <h3>עזרו להשלים את המידע</h3>
      <p>הספר והמחירון גדלים מתרומות הקהילה. מצאתם נתון חסר או שגוי? ספרו לנו.</p>
      <a class="cta__btn" href="/community">◐ השלמת מידע ›</a>
    </div>
    <div class="cta__card cta--suggest">
      <h3>הצעה או בקשה?</h3>
      <p>אין צ׳אט — טופס קצר.</p>
      <form class="cta__field" method="post" action="/community#suggest">
        <input type="text" name="suggestion" placeholder="מה תרצו שנפתח?" aria-label="הצעה"/>
        <button class="cta__send" type="submit">שליחה</button>
      </form>
    </div>
    <div class="cta__card cta--wa">
      <span class="ic" aria-hidden="true">✆</span>
      <div><h3>פתרון מותאם לחווה?</h3><p>פנייה ישירה בוואטסאפ</p></div>
      <a class="cta__btn" href="<?= $h($cta_wa_link) ?>" target="_blank" rel="noopener">וואטסאפ</a>
    </div>
  </div>

</div><!-- /hub-home__inner -->

</div><!-- /sh__body--wide -->
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
