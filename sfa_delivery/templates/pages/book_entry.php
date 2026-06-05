<?php
/**
 * book_entry.php — Route /crop-book/ (CB0)
 *
 * Mandate §3 (route 5): `.gj-shell` + 4 `mod-card`s (entry-path cards).
 * Per LOD400 v1.0.3 §0.5: COMPONENTS.md class names verbatim.
 * Uses `.cb-paths` wrapper (crop-book-deep.css L13) for layout per spec.
 *
 * WP-UI-patch03 (AC-U3-07): when controller passes $crops, renders a crop-card
 * grid using the existing crop_card.php macro below the nav cards.
 *
 * Variables expected from controller (all optional, defaults render):
 *   $crop_total      int   — total crop count (defaults to 66)
 *   $family_total    int   — total family count (defaults to 8)
 *   $variety_total   int   — total variety count (defaults to 242)
 *   $question_total  int   — total question count (defaults to 12)
 *   $crops           array — normalized crop list (each: slug, name_he, en_name,
 *                            icon_svg, icon_url, family_tag_he, dtm_days, category)
 */
use SFA\Lib\Template;

$page_title = 'ספר גידולים';
$page_sub   = 'מאגר ידע פתוח';
$active     = 'crop-book';

$crop_total     = (int)($crop_total     ?? 66);
$family_total   = (int)($family_total   ?? 8);
$variety_total  = (int)($variety_total  ?? 242);
$question_total = (int)($question_total ?? 3);

$paths = [
  [
    'slug'       => 'questions',
    'name_he'    => 'שאלות מובילות',
    'tier'       => 'open',
    'tier_color' => 'sun',
    'sub_he'     => 'מה מתחילים לזרוע השבוע?',
    'stat_he'    => $question_total . ' שאלות',
    'href'       => '/crop-book/questions',
    'icon_id'    => 'icon-leaf',
  ],
  [
    'slug'       => 'family',
    'name_he'    => 'משפחות בוטניות',
    'tier'       => 'open',
    'tier_color' => 'leaf',
    'sub_he'     => 'מה גדל ליד מה? איך מסובבים?',
    'stat_he'    => $family_total . ' משפחות',
    'href'       => '/crop-book/family',
    'icon_id'    => 'icon-seedling',
  ],
  [
    'slug'       => 'table',
    'name_he'    => 'טבלה מלאה',
    'tier'       => 'open',
    'tier_color' => 'soil',
    'sub_he'     => 'כל הגידולים — סינון, מיון, השוואה',
    'stat_he'    => $crop_total . ' גידולים',
    'href'       => '/crop-book/table',
    'icon_id'    => 'icon-tomato',
  ],
  [
    'slug'       => 'search',
    'name_he'    => 'חיפוש חופשי',
    'tier'       => 'open',
    'tier_color' => 'tomato',
    'sub_he'     => 'שם · משפחה · עברית · אנגלית',
    'stat_he'    => $variety_total . ' זנים',
    'href'       => '/crop-book/search',
    'icon_id'    => 'icon-cucumber',
  ],
];

$crops = is_array($crops ?? null) ? $crops : [];
$view  = (string)($view  ?? 'cards');
$total = (int)($total ?? count($crops));

// Watercolor art mapping
// Watercolor art mapping — original singular keys + C1 plural DB-slug aliases (patch01 recovery)
$wc_art_map = [
    // original singular keys (14 masters)
    'basil'      => 'wc-basil.png',
    'beet'       => 'wc-beet.png',
    'broccoli'   => 'wc-broccoli.png',
    'bush-bean'  => 'wc-bush-bean.png',
    'cabbage'    => 'wc-cabbage.png',
    'carrot'     => 'wc-carrot.png',
    'chard'      => 'wc-chard.png',
    'cucumber'   => 'wc-cucumber.png',
    'dill'       => 'wc-dill.png',
    'eggplant'   => 'wc-eggplant.png',
    'fennel'     => 'wc-fennel.png',
    'garlic'     => 'wc-garlic.png',
    'ginger'     => 'wc-ginger.png',
    'kale'       => 'wc-kale.png',
    'leek'       => 'wc-leek.png',
    'lettuce'    => 'wc-lettuce.png',
    'melon'      => 'wc-melon.png',
    'onion'      => 'wc-onion.png',
    'parsley'    => 'wc-parsley.png',
    'pea'        => 'wc-pea.png',
    'pepper'     => 'wc-pepper.png',
    'pole-bean'  => 'wc-pole-bean.png',
    'radish'     => 'wc-radish.png',
    'scallion'   => 'wc-scallion.png',
    'spinach'    => 'wc-spinach.png',
    'tomato'     => 'wc-tomato.png',
    'turmeric'   => 'wc-turmeric.png',
    'zucchini'   => 'wc-zucchini.png',
    // C1: plural DB-slug aliases (patch01 recovery)
    'carrots'                      => 'wc-carrot.png',
    'tomatoes'                     => 'wc-tomato.png',
    'cucumbers'                    => 'wc-cucumber.png',
    'onions'                       => 'wc-onion.png',
    'peppers'                      => 'wc-pepper.png',
    'peas'                         => 'wc-pea.png',
    'beets'                        => 'wc-beet.png',
    'radishes'                     => 'wc-radish.png',
    'melons'                       => 'wc-melon.png',
    'leeks'                        => 'wc-leek.png',
    'cherry-tomato'                => 'wc-tomato.png',
    'summer-squash'                => 'wc-zucchini.png',
    'onions-scallions'             => 'wc-scallion.png',
    'beans-default-pole-climbing-' => 'wc-pole-bean.png',
    // C2: 43 new watercolor identity slugs (WP-CB-UI-FIDELITY batch)
    'anise-hyssop'                 => 'wc-anise-hyssop.png',
    'artichokes'                   => 'wc-artichokes.png',
    'arugula'                      => 'wc-arugula.png',
    'bay'                          => 'wc-bay.png',
    'beans-default-pole-climbing'  => 'wc-beans-default-pole-climbing.png',
    'blackberry'                   => 'wc-blackberry.png',
    'cauliflower'                  => 'wc-cauliflower.png',
    'celery'                       => 'wc-celery.png',
    'chickpea'                     => 'wc-chickpea.png',
    'chicory'                      => 'wc-chicory.png',
    'chinese-lantern'              => 'wc-chinese-lantern.png',
    'chives'                       => 'wc-chives.png',
    'cilantro'                     => 'wc-cilantro.png',
    'cress'                        => 'wc-cress.png',
    'edamame'                      => 'wc-edamame.png',
    'fava-bean'                    => 'wc-fava-bean.png',
    'hibiscus'                     => 'wc-hibiscus.png',
    'jerusalem-artichokes'         => 'wc-jerusalem-artichokes.png',
    'jicama'                       => 'wc-jicama.png',
    'kohlrabi'                     => 'wc-kohlrabi.png',
    'lemon-balm'                   => 'wc-lemon-balm.png',
    'lemon-verbena'                => 'wc-lemon-verbena.png',
    'lettuce-salad-mix'            => 'wc-lettuce-salad-mix.png',
    'lovage'                       => 'wc-lovage.png',
    'mint'                         => 'wc-mint.png',
    'new-zealand-spinach'          => 'wc-new-zealand-spinach.png',
    'okra'                         => 'wc-okra.png',
    'oranges'                      => 'wc-oranges.png',
    'pac-choi-bok-choy'            => 'wc-pac-choi-bok-choy.png',
    'potato'                       => 'wc-potato.png',
    'sage'                         => 'wc-sage.png',
    'sesame'                       => 'wc-sesame.png',
    'soybean'                      => 'wc-soybean.png',
    'strawberry'                   => 'wc-strawberry.png',
    'sunflower'                    => 'wc-sunflower.png',
    'sweet-corn'                   => 'wc-sweet-corn.png',
    'sweet-potato'                 => 'wc-sweet-potato.png',
    'tarragon'                     => 'wc-tarragon.png',
    'thyme'                        => 'wc-thyme.png',
    'turnips'                      => 'wc-turnips.png',
    'watermelon'                   => 'wc-watermelon.png',
    'wheat'                        => 'wc-wheat.png',
    'winter-squash'                => 'wc-winter-squash.png',
];

ob_start();
?>
<section class="cb-hero cb-hero--compact" aria-label="ספר הגידולים">
  <img class="cb-hero__art" src="/public_assets/img/crops/wc-cropbook-hero.webp"
       alt="ספר גידולים" loading="eager" decoding="async">
  <div class="cb-hero__txt">
    <h1 class="cb-hero__title">ספר הגידולים</h1>
    <p class="cb-hero__sub">אינדקס פתוח של גידולים, זנים ומחזורי גידול — עם מחשבונים לתכנון.</p>
  </div>
</section>
<section class="cb-entry">
  <h2 class="cb-section-h">איך תרצו להיכנס?</h2>
  <div class="cb-paths">
    <?php foreach ($paths as $module): ?>
      <?php include __DIR__ . '/../macros/module_card.php'; ?>
    <?php endforeach; ?>
  </div>
</section>
<?php
  // WP-CB-1-patch01: render the crops section (incl. filter bar) whenever there are
  // results OR an active filter — so a 0-result filter still shows the bar to recover.
  $has_active_filter = is_array($filters ?? null) && implode('', array_map(fn($v) => (string)$v, $filters)) !== '';
?>
<?php if (!empty($crops) || $has_active_filter): ?>
<section class="cb-entry-crops">
  <!-- WP-CB-1: Audience switch + filter bar + results -->
  <div class="aud-head">
    <h2 class="cb-section-h">כל הגידולים</h2>
    <?php
    $active_view = $view;
    $scope_id    = 'crop-list-scope';
    include __DIR__ . '/../macros/audience_switch.php';
    ?>
    <span class="aud-head__sub"><?= $h((string)$total) ?> גידולים</span>
  </div>

  <!-- Top filter bar — WP-CB-1-patch01: real server-side GET form -->
  <?php
    $families = is_array($families ?? null) ? $families : [];
    $flt      = is_array($filters  ?? null) ? $filters  : [];
    $fq       = (string)($flt['q']      ?? '');
    $ffam     = (string)($flt['family'] ?? '');
    $fseason  = (string)($flt['season'] ?? '');
    $fdtm     = $flt['dtm_max'] ?? null;
    $fsow     = (string)($flt['sow']    ?? '');
    $ffrost   = (string)($flt['frost']  ?? '');
    $advOpen  = ($ffam !== '' || $fseason !== '' || $fdtm !== null || $fsow !== '' || $ffrost !== '');
    $sel      = fn($a, $b) => $a === $b ? ' selected' : '';
  ?>
  <form class="ftop" method="get" action="/crop-book/">
    <input type="hidden" name="view" value="<?= $h($view) ?>">
    <div class="ftop__top">
      <div class="filters__search">
        <span class="ic">🔍</span>
        <input type="text" name="q" value="<?= $h($fq) ?>" placeholder="חיפוש גידולים..." aria-label="חיפוש"/>
      </div>
      <button class="ftop__advbtn" type="button"
              data-filter-toggle="adv-filters"
              aria-expanded="<?= $advOpen ? 'true' : 'false' ?>">
        סינון מתקדם <span class="chev">▾</span>
      </button>
      <button class="filters__apply" type="submit">חיפוש</button>
      <span class="ftop__count"><b><?= $h((string)$total) ?></b> גידולים</span>
    </div>
    <div id="adv-filters" class="ftop__adv"<?= $advOpen ? ' style="display:block"' : '' ?>>
      <div class="ftop__row">
        <div class="fset">
          <label class="fset__lbl" for="f-family">משפחה בוטנית</label>
          <select id="f-family" name="family">
            <option value="">הכל</option>
            <?php foreach ($families as $fam): ?>
            <option value="<?= $h($fam) ?>"<?= $sel($ffam, (string)$fam) ?>><?= $h($fam) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="fset">
          <label class="fset__lbl" for="f-season">עונה</label>
          <?php
          // Decision A (2026-06-04): real planting-season filter, derived from
          // sowing_months ∪ transplant_months in payload_json['agronomy'] (PHP post-filter).
          // Coverage: ~39–44/70 crops have month data; unmatched crops are excluded honestly.
          $season_opts = [
              ''       => 'הכל',
              'summer' => 'קיץ',
              'winter' => 'חורף',
              'spring' => 'אביב',
              'autumn' => 'סתיו',
          ];
          ?>
          <select id="f-season" name="season">
            <?php foreach ($season_opts as $val => $lbl): ?>
            <option value="<?= $h($val) ?>"<?= $sel($fseason, $val) ?>><?= $h($lbl) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="fset">
          <label class="fset__lbl" for="f-dtm">ימים להבשלה (עד)</label>
          <input id="f-dtm" type="number" min="0" name="dtm_max" value="<?= $fdtm !== null ? $h((string)$fdtm) : '' ?>" placeholder="למשל 60">
        </div>
        <div class="fset">
          <label class="fset__lbl" for="f-sow">שיטת שתילה</label>
          <select id="f-sow" name="sow">
            <option value="">הכל</option>
            <option value="direct_seed"<?= $sel($fsow, 'direct_seed') ?>>זריעה ישירה</option>
            <option value="transplant"<?= $sel($fsow, 'transplant') ?>>שתיל</option>
          </select>
        </div>
        <div class="fset">
          <label class="fset__lbl" for="f-frost">עמידות לקרה</label>
          <select id="f-frost" name="frost">
            <option value="">הכל</option>
            <option value="hardy"<?= $sel($ffrost, 'hardy') ?>>עמיד</option>
            <option value="half_hardy"<?= $sel($ffrost, 'half_hardy') ?>>חצי-עמיד</option>
            <option value="tender"<?= $sel($ffrost, 'tender') ?>>רגיש</option>
            <option value="very_tender"<?= $sel($ffrost, 'very_tender') ?>>רגיש מאוד</option>
          </select>
        </div>
      </div>
      <div class="ftop__advfoot">
        <span class="ftop__count"><b><?= $h((string)$total) ?></b> גידולים</span>
        <a class="filters__clear" href="/crop-book/?view=<?= $h($view) ?>">↺ איפוס</a>
        <button class="filters__apply" type="submit">החל סינון</button>
      </div>
    </div>
  </form>

  <div id="crop-list-scope">
    <?php if (empty($crops)): ?>
    <div class="cb-empty">
      <p>לא נמצאו גידולים התואמים את הסינון.</p>
      <a class="filters__clear" href="/crop-book/?view=<?= $h($view) ?>">↺ נקו סינון</a>
    </div>
    <?php else: ?>
    <!-- Cards view — WP-CB-MOBILE FIX 1: compact 1-up ROW cards, no wash,
         in-season "now" badge (server-derived, current month), .cparam chips. -->
    <div data-aud-view="cards" style="<?= $view !== 'cards' ? 'display:none' : '' ?>">
      <?php
        // In-season count for the current month (server-derived in_season flag).
        $in_season_n = 0;
        foreach ($crops as $c) { if (!empty($c['in_season'])) { $in_season_n++; } }
        // Hebrew month name for the count line.
        $MONTH_HE_FULL = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
        $now_he = $MONTH_HE_FULL[(int)date('n') - 1];
        // Activity → in-season badge label + glyph (NEVER leak the raw key).
        $now_badge = [
          'seed'       => ['g' => '🌱', 'label' => 'עכשיו לזריעה'],
          'transplant' => ['g' => '🪴', 'label' => 'עכשיו לשתילה'],
        ];
      ?>
      <div class="seasonchips" role="group" aria-label="סינון לפי עונה">
        <button class="fchip is-on" type="button">🌱 עכשיו בעונה</button>
        <button class="fchip" type="button">הכל</button>
      </div>
      <?php if ($in_season_n > 0): ?>
      <p class="mcount"><b><?= (int)$in_season_n ?></b> גידולים מתאימים לשתילה/זריעה ב<?= $h($now_he) ?></p>
      <?php endif; ?>

      <div class="cards-grid">
        <?php
          $first = true;
          foreach ($crops as $c):
            $cslug = (string)($c['slug'] ?? '');
            $wc    = $wc_art_map[$cslug] ?? null;
            $act   = (string)($c['in_season_activity'] ?? '');
            $badge = $now_badge[$act] ?? null;
            $feat  = $first; // featured first card
            $first = false;
        ?>
        <a class="ccard<?= $feat ? ' ccard--feat' : '' ?>" href="/crop-book/<?= $h($cslug) ?>/">
          <div class="ccard__art">
            <?php if ($wc !== null): ?>
              <img src="/public_assets/img/crops/<?= $h($wc) ?>" alt="<?= $h((string)($c['name_he'] ?? '')) ?>" loading="lazy"/>
            <?php else: ?>
              <span class="veg" aria-hidden="true">🌱</span>
            <?php endif; ?>
            <!-- state dot: no completeness signal at index level → omitted (honest) -->
          </div>
          <div class="ccard__body">
            <?php if ($feat): ?>
              <span class="ccard__feattag">מומלץ</span>
            <?php endif; ?>
            <?php if ($badge !== null): ?>
              <span class="ccard__now"><span class="g"><?= $badge['g'] ?></span><?= $h($badge['label']) ?></span>
            <?php endif; ?>
            <div class="ccard__name"><?= $h((string)($c['name_he'] ?? '')) ?></div>
            <?php if (!empty($c['en_name'])): ?>
              <div class="ccard__en" dir="ltr"><?= $h((string)$c['en_name']) ?></div>
            <?php endif; ?>
            <div class="cparams">
              <?php if (!empty($c['dtm_days'])): ?>
              <span class="cparam cparam--dtm"><span class="g">⏳</span><span dir="ltr"><?= (int)$c['dtm_days'] ?></span><small>ימים</small></span>
              <?php endif; ?>
              <?php if ($act === 'seed'): ?>
              <span class="cparam cparam--method"><span class="g">🌱</span>זריעה</span>
              <?php elseif ($act === 'transplant'): ?>
              <span class="cparam cparam--method"><span class="g">🪴</span>שתיל</span>
              <?php endif; ?>
              <?php if (!empty($c['family_tag_he'])): ?>
              <span class="cparam"><span class="g">🌿</span><?= $h((string)$c['family_tag_he']) ?></span>
              <?php endif; ?>
            </div>
          </div>
        </a>
        <?php endforeach; ?>
      </div>

      <!-- CTA foot — complete missing data (primary). -->
      <div class="cta">
        <div class="cta__card cta--data">
          <h3>חסר מידע על גידול?</h3>
          <p>הספר נבנה בשיתוף הקהילה. אם גידלתם — תרמו נתון, וזה יידלק לכולם.</p>
          <a class="cta__btn" href="/community">◐ תרמו נתון ›</a>
        </div>
      </div>
    </div>

    <!-- Table view -->
    <div data-aud-view="table" style="<?= $view !== 'table' ? 'display:none' : '' ?>">
      <div style="overflow-x:auto">
        <table class="ptable">
          <thead>
            <tr>
              <th class="sortable">גידול</th>
              <th class="sortable">משפחה</th>
              <th class="sortable">DTM ימ׳</th>
              <th class="sortable calc-col">זרעים/מ׳ <small>#1</small></th>
              <th class="sortable calc-col">הכנסה/מ׳ <small>#9</small></th>
            </tr>
          </thead>
          <tbody>
            <?php foreach ($crops as $c): ?>
            <tr>
              <td>
                <div class="t-name">
                  <a href="/crop-book/<?= $h((string)($c['slug'] ?? '')) ?>/"><?= $h((string)($c['name_he'] ?? '')) ?></a>
                  <?php if (!empty($c['en_name'])): ?><em><?= $h((string)$c['en_name']) ?></em><?php endif; ?>
                </div>
              </td>
              <td class="t-fam"><?= $h((string)($c['family_tag_he'] ?? '')) ?></td>
              <td><?= !empty($c['dtm_days']) ? (int)$c['dtm_days'] : '—' ?></td>
              <td class="calc-cell">—<small>ח/מ׳</small></td>
              <td class="calc-cell">—<small>₪/מ׳</small></td>
            </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
      </div>
    </div>
    <?php endif; /* crops empty/non-empty */ ?>
  </div>

  <?php if (!empty($crops)): ?>
  <!-- Pagination -->
  <div class="pager" data-pager>
    <div class="pager__info">עמוד <b>1</b> מתוך <?= (int)ceil($total / 25) ?></div>
    <div class="pager__nav">
      <button class="pager__arrow" type="button">→</button>
      <button class="pager__pg is-active" type="button">1</button>
      <?php if ($total > 25): ?><button class="pager__pg" type="button">2</button><?php endif; ?>
      <button class="pager__arrow" type="button">←</button>
    </div>
    <div class="pager__size">
      שורות בעמוד:
      <select aria-label="שורות לעמוד"><option>25</option><option>50</option><option>100</option></select>
    </div>
  </div>
  <?php endif; /* pager only when crops present */ ?>
</section>
<?php endif; ?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
