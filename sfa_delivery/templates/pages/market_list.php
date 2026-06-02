<?php
/**
 * market_list.php — Route /market/ — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frame `market-list`.
 * Components: .mkt-disc (§33, mandatory), .mkt-tools, .fchips/.fchip,
 *             .mkt-legend, .pcard-grid, .pcard (+.is-stale/.is-empty),
 *             .spark, .fresh (§34), .mkt-aud-head cards⇄table toggle.
 *
 * Data contract (MarketViewController::index):
 *   $products   — array of product rows (name_he, unit_he, last_price,
 *                  freshness_days, price_min, price_max, price_median,
 *                  source_count, observation_count, slug, ...)
 *   $categories — array<{slug,name_he}> — facet chips
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$page_title = 'מחירון';
$page_sub   = 'מחירי שוק קהילתיים';
$active     = 'market';

$products         = is_array($products ?? null) ? $products : [];
$categories       = is_array($categories ?? null) ? $categories : [];
$current_category = (string)($current_category ?? '');

// Unit display helper (LOD400 §9a) — guarded for multi-test-run environments
if (!function_exists('sfa_unit_label')) {
    function sfa_unit_label(string $unit): string {
        return match(strtolower(trim($unit))) {
            'kg', 'ק"ג', 'ק״ג' => 'לק״ג',
            'unit', 'יח׳', 'יח\''  => 'ליחידה',
            'bunch', 'אגודה'        => 'לאגודה',
            default => $unit !== '' ? 'ל' . $unit : '',
        };
    }
}

ob_start();
?>
<div class="sh__body--wide">

  <?php /* Disclaimer — MANDATORY, never suppressed (MINOR F-01: .mkt-disc class) */ ?>
  <?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>

  <?php /* Toolbar: category chips + freshness legend */ ?>
  <div class="mkt-tools">
    <div class="fchips" role="group" aria-label="סינון לפי קטגוריה">
      <a class="fchip<?= empty($current_category) ? ' is-on' : '' ?>" href="/market/">הכל</a>
      <?php foreach ($categories as $cat):
        $cat_slug = (string)($cat['slug'] ?? '');
        $cat_name = (string)($cat['name_he'] ?? $cat_slug);
      ?>
      <a class="fchip<?= $current_category === $cat_slug ? ' is-on' : '' ?>"
         href="/market/?category=<?= urlencode($cat_slug) ?>"><?= $h($cat_name) ?></a>
      <?php endforeach; ?>
    </div>
    <div class="mkt-legend" aria-label="מקרא טריות">
      <span><i style="background:var(--gj-leaf)"></i>טרי (0–3 ימים)</span>
      <span><i style="background:var(--gj-sun)"></i>מתעדכן (4–7)</span>
      <span><i style="background:var(--gj-tomato)"></i>ישן (7+)</span>
    </div>
  </div>

  <?php /* Cards ⇄ table toggle header */ ?>
  <div class="mkt-aud-head">
    <div class="mkt-aud-head__n"><b><?= count($products) ?></b> מוצרים</div>
    <div class="aud" role="group" aria-label="תצוגה">
      <button class="aud__btn is-on" data-aud="cards" type="button">כרטיסיות</button>
      <button class="aud__btn" data-aud="table" type="button">טבלה</button>
    </div>
  </div>

  <?php /* Card grid (default view) */ ?>
  <div id="mkt-scope" data-aud-view="cards">
    <div class="pcard-grid" data-view="cards">
      <?php if (empty($products)): ?>
        <div class="emptybox" style="grid-column:1/-1">
          <div class="emptybox__ic">📭</div>
          <div>
            <b>אין נתוני מחיר</b>
            <p>המחירון עדיין ריק — חזרו בקרוב או תרמו מחיר.</p>
          </div>
        </div>
      <?php else: ?>
        <?php foreach ($products as $row):
          $name_he       = (string)($row['name_he'] ?? $row['hebrew_name'] ?? '');
          $slug          = (string)($row['slug'] ?? '');
          $unit          = (string)($row['unit_he'] ?? $row['unit'] ?? '');
          $unit_lbl      = sfa_unit_label($unit);
          $last_price    = isset($row['last_price']) && $row['last_price'] !== null ? (float)$row['last_price'] : null;
          $price_current = isset($row['price_current']) && $row['price_current'] !== null ? (float)$row['price_current'] : $last_price;
          $price_min     = (float)($row['price_min'] ?? 0);
          $price_max     = (float)($row['price_max'] ?? 0);
          $price_median  = (float)($row['price_median'] ?? 0);
          $source_count  = (int)($row['source_count'] ?? 0);
          $freshness     = isset($row['freshness_days']) ? (int)$row['freshness_days'] : null;
          $glyph         = $name_he !== '' ? mb_substr($name_he, 0, 1, 'UTF-8') : '?';
          $icon_slug     = (string)($row['icon_slug'] ?? 'leaf');

          // Determine card state per §9a / §4 honest-data rule
          $is_empty = ($price_current === null || $price_current <= 0);
          $is_stale = !$is_empty && ($freshness !== null && $freshness > 7);

          // Freshness pill class (§9a — LOCKED thresholds)
          if ($freshness === null) {
              $fresh_cls = 'fresh--stale'; $fresh_lbl = 'אין דיווח';
          } elseif ($freshness <= 3) {
              $fresh_cls = 'fresh--fresh'; $fresh_lbl = $freshness === 0 ? 'טרי · עודכן היום' : 'טרי · לפני ' . $freshness . ' ימים';
          } elseif ($freshness <= 7) {
              $fresh_cls = 'fresh--aging'; $fresh_lbl = 'מתעדכן · לפני ' . $freshness . ' ימים';
          } else {
              $fresh_cls = 'fresh--stale'; $fresh_lbl = 'ישן · לפני ' . $freshness . ' ימים';
          }

          // Sparkline: last-7 bars (pure CSS; we fake a 7-bar struct since we only have list data)
          // No real per-day sparkline data here (would need history per product on list view).
          // Honest degrade: show empty sparkline on list page (history only available on detail).
          $spark_empty = true;
        ?>
        <a class="pcard<?= $is_empty ? ' is-empty' : ($is_stale ? ' is-stale' : '') ?>"
           href="/market/<?= $h($slug) ?>">
          <div class="pcard__top">
            <div class="pcard__sw pcard__sw--glyph" aria-hidden="true"><?= $h($glyph) ?></div>
            <div>
              <div class="pcard__name"><?= $h($name_he) ?></div>
              <?php if ($unit_lbl !== ''): ?>
                <div class="pcard__unit"><?= $h($unit_lbl) ?></div>
              <?php endif; ?>
            </div>
          </div>
          <?php if (!$is_empty): ?>
          <div class="pcard__price">
            <span class="big"><?= number_format($price_current, 2) ?></span>
            <span class="cur">₪</span>
            <?php if ($unit_lbl !== ''): ?><span class="per"><?= $h($unit_lbl) ?></span><?php endif; ?>
          </div>
          <?php if ($price_min > 0 && $price_max > 0 && $price_min !== $price_max): ?>
          <div class="pcard__range"><?= number_format($price_min, 2) ?>–<?= number_format($price_max, 2) ?> ₪ · <?= (int)$source_count ?> מקורות</div>
          <?php elseif ($source_count > 0): ?>
          <div class="pcard__range"><?= (int)$source_count ?> מקורות</div>
          <?php endif; ?>
          <div class="pcard__spark">
            <div class="spark spark--empty" aria-hidden="true">
              <?php for ($i = 0; $i < 7; $i++): ?><i></i><?php endfor; ?>
            </div>
          </div>
          <?php else: ?>
          <div class="pcard__price">
            <span class="big">—</span>
          </div>
          <div class="pcard__range">אין דיווח</div>
          <?php endif; ?>
          <div class="pcard__foot">
            <span class="pcard__src">
              <?php if ($source_count > 0): ?><b><?= (int)$source_count ?></b> מקורות<?php endif; ?>
            </span>
            <span class="fresh <?= $h($fresh_cls) ?>"><?= $h($fresh_lbl) ?></span>
          </div>
        </a>
        <?php endforeach; ?>
      <?php endif; ?>
    </div>

    <?php /* Table view (hidden by default via CSS / JS toggle) */ ?>
    <?php if (!empty($products)): ?>
    <div data-view="table" style="display:none">
      <table class="ptable" style="width:100%;border-collapse:collapse">
        <thead>
          <tr>
            <th class="ptable__th ptable__th--start">מוצר</th>
            <th class="ptable__th">מחיר</th>
            <th class="ptable__th">טריות</th>
          </tr>
        </thead>
        <tbody>
          <?php foreach ($products as $row):
            $name_he    = (string)($row['name_he'] ?? $row['hebrew_name'] ?? '');
            $slug       = (string)($row['slug'] ?? '');
            $unit       = (string)($row['unit_he'] ?? $row['unit'] ?? '');
            $unit_lbl   = sfa_unit_label($unit);
            $last_price = isset($row['last_price']) && $row['last_price'] !== null ? (float)$row['last_price'] : null;
            $price_current = isset($row['price_current']) && $row['price_current'] !== null ? (float)$row['price_current'] : $last_price;
            $freshness  = isset($row['freshness_days']) ? (int)$row['freshness_days'] : null;
            $is_empty   = ($price_current === null || $price_current <= 0);

            if ($freshness === null) {
                $fresh_cls = 'fresh--stale'; $fresh_lbl = 'אין דיווח';
            } elseif ($freshness <= 3) {
                $fresh_cls = 'fresh--fresh'; $fresh_lbl = 'טרי';
            } elseif ($freshness <= 7) {
                $fresh_cls = 'fresh--aging'; $fresh_lbl = 'מתעדכן';
            } else {
                $fresh_cls = 'fresh--stale'; $fresh_lbl = 'ישן';
            }
          ?>
          <tr>
            <td style="padding:9px 10px;border-bottom:1px solid var(--gj-line)">
              <a href="/market/<?= $h($slug) ?>"><?= $h($name_he) ?></a>
            </td>
            <td class="t-price<?= $is_empty ? ' t-stale' : '' ?>" style="padding:9px 10px;border-bottom:1px solid var(--gj-line)">
              <?php if (!$is_empty): ?>
                <?= number_format($price_current, 2) ?> ₪<?php if ($unit_lbl !== ''): ?><small> <?= $h($unit_lbl) ?></small><?php endif; ?>
              <?php else: ?>
                <span class="t-stale">—</span>
              <?php endif; ?>
            </td>
            <td style="padding:9px 10px;border-bottom:1px solid var(--gj-line)">
              <span class="fresh <?= $h($fresh_cls) ?>"><?= $h($fresh_lbl) ?></span>
            </td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
    <?php endif; ?>
  </div>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
