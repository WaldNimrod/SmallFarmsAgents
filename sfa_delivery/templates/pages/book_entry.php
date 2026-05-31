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
$question_total = (int)($question_total ?? 12);

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
$wc_art_map = ['lettuce'=>'wc-lettuce.png', 'radish'=>'wc-radish.png', 'parsley'=>'wc-parsley.png', 'dill'=>'wc-dill.png', 'tomato'=>'wc-tomato.png', 'cucumber'=>'wc-cucumber.png', 'beet'=>'wc-beet.png', 'pepper'=>'wc-pepper.png', 'broccoli'=>'wc-broccoli.png', 'cabbage'=>'wc-cabbage.png', 'chard'=>'wc-chard.png', 'eggplant'=>'wc-eggplant.png', 'fennel'=>'wc-fennel.png', 'garlic'=>'wc-garlic.png', 'kale'=>'wc-kale.png', 'scallion'=>'wc-scallion.png', 'leek'=>'wc-leek.png', 'melon'=>'wc-melon.png', 'onion'=>'wc-onion.png', 'basil'=>'wc-basil.png', 'carrot'=>'wc-carrot.png'];

ob_start();
?>
<section class="cb-entry">
  <h2 class="cb-section-h">איך תרצו להיכנס?</h2>
  <div class="cb-paths">
    <?php foreach ($paths as $module): ?>
      <?php include __DIR__ . '/../macros/module_card.php'; ?>
    <?php endforeach; ?>
  </div>
</section>
<?php if (!empty($crops)): ?>
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

  <!-- Top filter bar -->
  <div class="ftop">
    <div class="ftop__top">
      <div class="filters__search">
        <span class="ic">🔍</span>
        <input type="text" placeholder="חיפוש גידולים..." aria-label="חיפוש"/>
      </div>
      <button class="ftop__advbtn" type="button"
              data-filter-toggle="adv-filters"
              aria-expanded="false">
        סינון מתקדם <span class="chev">▾</span>
      </button>
      <span class="ftop__count"><b><?= $h((string)$total) ?></b> גידולים</span>
    </div>
    <div id="adv-filters" class="ftop__adv">
      <div class="ftop__row">
        <div class="fset">
          <span class="fset__lbl" data-field="planting_method">שיטת שתילה</span>
          <div class="fchips">
            <button class="fchip" data-single data-default-on type="button">הכל</button>
            <button class="fchip" data-single type="button">זריעה ישירה</button>
            <button class="fchip" data-single type="button">שתיל</button>
          </div>
        </div>
        <div class="fset">
          <span class="fset__lbl" data-field="frost_tolerance_class">עמידות לקרה</span>
          <div class="fchips">
            <button class="fchip" data-single data-default-on type="button">הכל</button>
            <button class="fchip" data-single type="button">עמיד</button>
            <button class="fchip" data-single type="button">חצי-עמיד</button>
            <button class="fchip" data-single type="button">רגיש</button>
          </div>
        </div>
      </div>
      <div class="ftop__advfoot">
        <span class="ftop__count"><b><?= $h((string)$total) ?></b> גידולים</span>
        <button class="filters__clear" data-filter-reset type="button">↺ איפוס</button>
        <button class="filters__apply" type="button">החל סינון</button>
      </div>
    </div>
  </div>

  <div id="crop-list-scope">
    <!-- Cards view -->
    <div data-aud-view="cards" style="<?= $view !== 'cards' ? 'display:none' : '' ?>">
      <div class="cards-grid">
        <?php foreach ($crops as $c):
          $cslug = (string)($c['slug'] ?? '');
          $wc = $wc_art_map[$cslug] ?? null;
        ?>
        <a class="ccard" href="/crop-book/<?= $h($cslug) ?>/">
          <div class="ccard__art">
            <?php if ($wc !== null): ?>
              <img src="/public_assets/img/crops/<?= $h($wc) ?>" alt="<?= $h((string)($c['name_he'] ?? '')) ?>" loading="lazy"/>
            <?php else: ?>
              <span class="veg" aria-hidden="true">🌱</span>
            <?php endif; ?>
            <!-- state dot: no enrichment data at list level — show neutral -->
          </div>
          <div class="ccard__body">
            <div class="ccard__name"><?= $h((string)($c['name_he'] ?? '')) ?></div>
            <?php if (!empty($c['en_name'])): ?>
              <div class="ccard__en"><?= $h((string)$c['en_name']) ?></div>
            <?php endif; ?>
            <div class="ccard__meta">
              <div class="ccard__calcs">
                <!-- calc pips: dim by default (no live enrichment at index level) -->
                <?php for ($pi = 0; $pi < 6; $pi++): ?><i class="off"></i><?php endfor; ?>
              </div>
              <?php if (!empty($c['dtm_days'])): ?>
              <div class="ccard__dtm"><?= (int)$c['dtm_days'] ?><small>ימ׳</small></div>
              <?php endif; ?>
            </div>
          </div>
        </a>
        <?php endforeach; ?>
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
  </div>

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
</section>
<?php endif; ?>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
