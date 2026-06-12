<?php
/**
 * market_product.php — Route /market/{slug} — redesign DS (WP-CB-MARKET-DETAIL)
 *
 * Re-skinned from the Class-B v2 design (.pbig/.pgraph/.pstats + inline styles +
 * raw OS emoji) to the redesign design system, matching the market-list drill-down
 * (.pcard/.pc__* + .fresh.f/.a/.s + .bigspark + redesign tokens). Render-layer only;
 * the MarketViewController::detail data contract is unchanged.
 *
 * Data contract (MarketViewController::detail):
 *   $product — merged row with name_he, price_current, price_min, price_max,
 *              price_median, source_count, observation_count, freshness_days,
 *              history (array), book_slug, book_label_he, updated_he, unit_he, wc_art
 *   $history — array<{price_date, price, source}> — 28-day window (also $product['history'])
 *
 * AC-5: 7י/28י active · 90י/שנה honestly disabled "בקרוב" (no 90-day/yearly data).
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$product = is_array($product ?? null) ? $product : [];
$history = is_array($history ?? null) ? $history : [];

$slug          = (string)($product['slug']          ?? '');
$name_he       = (string)($product['name_he']       ?? $product['hebrew_name'] ?? '');
$en_name       = (string)($product['en_name']       ?? '');
$icon_slug     = (string)($product['icon_slug']     ?? 'leaf');
$wc_art        = (string)($product['wc_art']        ?? '');
$unit          = (string)($product['unit_he']       ?? $product['unit'] ?? '');
$currency      = '₪';
$price_current = isset($product['price_current']) && $product['price_current'] !== null
    ? (float)$product['price_current'] : (isset($product['last_price']) ? (float)$product['last_price'] : null);
$price_median  = (float)($product['price_median']  ?? 0);
$price_min     = (float)($product['price_min']     ?? 0);
$price_max     = (float)($product['price_max']     ?? 0);
$source_count  = (int)($product['source_count']    ?? 0);
$obs_count     = (int)($product['observation_count'] ?? 0);
$freshness     = isset($product['freshness_days']) ? (int)$product['freshness_days'] : null;
$updated_he    = (string)($product['updated_he']   ?? $product['last_price_date'] ?? '');
$book_slug     = (string)($product['book_slug']    ?? '');
$book_label_he = (string)($product['book_label_he']?? $name_he);

// History rows (prefer $product['history'] which is mapped; fallback to raw $history)
$hist_rows = !empty($product['history']) ? $product['history'] : $history;

// Unit label (§9a)
$_unit_norm = strtolower(trim($unit));
$unit_lbl = match($_unit_norm) {
    'kg', 'ק"ג', 'ק״ג'                         => 'לק״ג',
    'unit', 'יח׳', 'יח\''                       => 'ליחידה',
    'bunch', 'אגודה'                             => 'לאגודה',
    'basket_large', 'basket_medium', 'basket_small' => 'לסל',
    default => (preg_match('/^[a-z][a-z_]*$/', $_unit_norm) ? 'ליחידה' : ($unit !== '' ? 'ל' . $unit : '')),
};

// Freshness pill — AC-4: redesign .fresh.f/.a/.s (consistent with the market list).
if ($freshness === null) {
    $fcls = 's'; $flbl = 'אין דיווח';
} elseif ($freshness <= 3) {
    $fcls = 'f';
    $flbl = $freshness === 0 ? 'טרי · עודכן היום' : ($freshness === 1 ? 'טרי · עודכן אתמול' : 'טרי · לפני ' . $freshness . ' ימים');
} elseif ($freshness <= 7) {
    $fcls = 'a'; $flbl = 'מתעדכן · לפני ' . $freshness . ' ימים';
} else {
    $fcls = 's'; $flbl = 'ישן · לפני ' . $freshness . ' ימים';
}

$is_empty = ($price_current === null || $price_current <= 0);

// Big sparkline data from last-7 history rows (pure CSS, no chart lib)
$spark_prices = [];
foreach (array_slice($hist_rows, 0, 7) as $hr) {
    $spark_prices[] = (float)($hr['price'] ?? 0);
}
$spark_max = $spark_prices ? max($spark_prices) : 0;

// SVG path for the 28-day graph from history
$graph_rows = array_reverse($hist_rows); // oldest first for left-to-right
$svg_points = [];
$svg_w = 400; $svg_h = 100;
if (count($graph_rows) >= 2) {
    $prices = array_map(fn($r) => (float)($r['price'] ?? 0), $graph_rows);
    $pmin = min($prices); $pmax = max($prices);
    $prange = max($pmax - $pmin, 0.01);
    $n = count($graph_rows);
    foreach ($prices as $i => $p) {
        $x = round(($i / ($n - 1)) * $svg_w, 1);
        $y = round($svg_h - (($p - $pmin) / $prange) * ($svg_h - 16) - 8, 1);
        $svg_points[] = $x . ',' . $y;
    }
}
$has_graph = count($svg_points) >= 2;
$svg_path  = $has_graph ? 'M' . implode(' L', $svg_points) : '';
$svg_area  = $has_graph ? 'M' . implode(' L', $svg_points) . ' L' . $svg_w . ',' . $svg_h . ' L0,' . $svg_h . ' Z' : '';

// Delta (last vs previous)
$delta = null;
if (count($hist_rows) >= 2) {
    $last = (float)($hist_rows[0]['price'] ?? 0);
    $prev = (float)($hist_rows[1]['price'] ?? 0);
    if ($prev > 0) { $delta = (($last - $prev) / $prev) * 100; }
}

$page_title = $name_he !== '' ? $name_he : 'מוצר';
$page_sub   = 'מחירון · ' . ($name_he !== '' ? $name_he : '');
$active     = 'market';

ob_start();
?>
<div class="mdetail">

  <?php /* Compact disclaimer — mandatory on detail too (copy LOCKED by team_00) */ ?>
  <?php $compact = true; include __DIR__ . '/../macros/market_disclaimer.php'; ?>

  <div class="lead">
    <div>
      <h1><?= $h($name_he) ?></h1>
      <p>מחירון קהילתי<?php if ($en_name !== ''): ?> · <span dir="ltr"><?= $h($en_name) ?></span><?php endif; ?></p>
    </div>
    <span class="fresh <?= $h($fcls) ?>"><?= $h($flbl) ?></span>
  </div>

  <div class="mdgrid">
    <div class="mdgrid__main">

      <?php /* Price hero — redesign .pcard + watercolor art (AC-3) */ ?>
      <div class="pcard mdhero">
        <div class="pc__top">
          <div class="pc__art" aria-hidden="true">
            <?php if ($wc_art !== ''): ?>
              <img src="/public_assets/img/crops/<?= $h($wc_art) ?>" alt="" loading="lazy" decoding="async">
            <?php else: ?>
              <svg class="gi"><use href="#icon-<?= $h($icon_slug) ?>"/></svg>
            <?php endif; ?>
          </div>
          <div>
            <div class="pc__name"><?= $h($name_he) ?></div>
            <?php if ($unit_lbl !== ''): ?><div class="pc__unit">מחיר <?= $h($unit_lbl) ?></div><?php endif; ?>
          </div>
        </div>

        <?php if (!$is_empty): ?>
        <div class="pc__price">
          <span class="big"><span class="num"><?= number_format($price_current, 2) ?></span></span>
          <span class="cur"><?= $currency ?></span>
          <?php if ($unit_lbl !== ''): ?><span class="per"><?= $h($unit_lbl) ?></span><?php endif; ?>
          <?php if ($delta !== null): ?>
            <span class="trend <?= $delta >= 0 ? 'pc__trend--up' : 'pc__trend--dn' ?>"><?= $delta >= 0 ? '▲' : '▼' ?><span class="num"><?= number_format(abs($delta), 1) ?></span>%</span>
          <?php endif; ?>
        </div>
        <div class="mdmeta">
          <?php if ($price_min > 0 && $price_max > 0): ?>
            <span>טווח <b><span class="num"><?= number_format($price_min, 2) ?>–<?= number_format($price_max, 2) ?></span> ₪</b></span>
          <?php endif; ?>
          <?php if ($price_median > 0): ?>
            <span>חציון <b><span class="num"><?= number_format($price_median, 2) ?></span> ₪</b></span>
          <?php endif; ?>
          <?php if ($source_count > 0): ?>
            <span><span class="num"><?= (int)$source_count ?></span> מקורות</span>
          <?php endif; ?>
          <?php if ($updated_he !== ''): ?>
            <span>עודכן <?= $h($updated_he) ?></span>
          <?php endif; ?>
        </div>
        <?php else: ?>
        <div class="pc__price"><span class="big muted">—</span></div>
        <p class="muted" style="margin:8px 0 0">אין דיווחי מחיר עבור מוצר זה.</p>
        <?php endif; ?>
      </div>

      <?php /* Price graph — 28-day (AC-5 range selector) */ ?>
      <section class="pcard mdcard" data-slug="<?= $h($slug) ?>">
        <div class="mdcard__top">
          <h2 class="mdcard__title">מחיר — 28 ימים אחרונים</h2>
          <div class="rangesel" role="group" aria-label="טווח זמן">
            <button type="button" class="is-active" data-days="7">7י</button>
            <button type="button" class="is-active" data-days="28">28י</button>
            <button type="button" class="is-soon" disabled aria-disabled="true" title="בקרוב">90י</button>
            <button type="button" class="is-soon" disabled aria-disabled="true" title="בקרוב">שנה</button>
          </div>
        </div>
        <?php if ($has_graph): ?>
        <svg class="mdgraph" viewBox="0 0 <?= $svg_w ?> <?= $svg_h ?>" preserveAspectRatio="none" aria-label="גרף מחיר 28 ימים">
          <path class="mdgraph__area" d="<?= $svg_area ?>"/>
          <path class="mdgraph__line" d="<?= $svg_path ?>"/>
        </svg>
        <div class="mdgraph__x">
          <?php if (!empty($graph_rows)):
            $first = $graph_rows[0]; $last_r = end($graph_rows);
          ?>
            <span><?= $h((string)($first['date_he'] ?? $first['price_date'] ?? '')) ?></span>
            <span><?= $h((string)($last_r['date_he'] ?? $last_r['price_date'] ?? '')) ?></span>
          <?php endif; ?>
        </div>
        <div class="mdcard__legend"><span class="num">₪</span> <?= $h($currency) ?><?= $unit_lbl !== '' ? ' · ' . $h($unit_lbl) : '' ?></div>
        <?php elseif ($is_empty): ?>
        <div class="mdempty">
          <span class="mdempty__ic"><svg class="gi" aria-hidden="true"><use href="#i-box"/></svg></span>
          <div><b>אין נתוני גרף</b><p>לא נמצאו דיווחי מחיר. <a href="/community">תרמו מחיר</a> ועזרו לבנות את הנתונים.</p></div>
        </div>
        <?php else: ?>
        <div class="mdempty">
          <span class="mdempty__ic"><svg class="gi" aria-hidden="true"><use href="#i-chart"/></svg></span>
          <div><b>אין מספיק נתונים לגרף</b><p>נדרשות לפחות 2 תצפיות להצגת קו מגמה.</p></div>
        </div>
        <?php endif; ?>
      </section>

      <?php /* Price history table */ ?>
      <section class="pcard mdcard">
        <h2 class="mdcard__title">היסטוריית מחיר</h2>
        <?php if (!empty($hist_rows)): ?>
        <div class="mdtable-wrap">
        <table class="mdtable">
          <thead><tr><th>תאריך</th><th>מחיר</th><th>מקור</th><th>שינוי</th></tr></thead>
          <tbody>
            <?php
            $prev_price = null;
            foreach ($hist_rows as $hr):
              $date_he  = (string)($hr['date_he'] ?? $hr['price_date'] ?? '');
              $price_v  = (float)($hr['price'] ?? 0);
              $source_v = (string)($hr['source'] ?? '');
              $row_delta = null;
              if ($prev_price !== null && $prev_price > 0) {
                  $row_delta = (($price_v - $prev_price) / $prev_price) * 100;
              }
              $prev_price = $price_v;
            ?>
            <tr>
              <td><?= $h($date_he) ?></td>
              <td><span class="num"><?= number_format($price_v, 2) ?></span> ₪</td>
              <td><?= $h($source_v) ?></td>
              <td>
                <?php if ($row_delta !== null): ?>
                  <span class="<?= $row_delta >= 0 ? 'delta-up' : 'delta-dn' ?>"><?= $row_delta >= 0 ? '▲' : '▼' ?><span class="num"><?= number_format(abs($row_delta), 1) ?></span>%</span>
                <?php else: ?>—<?php endif; ?>
              </td>
            </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
        </div>
        <?php else: ?>
        <div class="mdempty">
          <span class="mdempty__ic"><svg class="gi" aria-hidden="true"><use href="#i-box"/></svg></span>
          <div><b>אין נתוני היסטוריה</b><p>לא נמצאו דיווחי מחיר ב-28 הימים האחרונים.</p></div>
        </div>
        <?php endif; ?>
      </section>

    </div><!-- /mdgrid__main -->

    <aside class="mdgrid__side">

      <?php /* Stat strip */ ?>
      <div class="pcard mdcard mdstats">
        <?php if (!$is_empty): ?>
          <div class="mdstat"><div class="mdstat__k">מחיר נוכחי</div><div class="mdstat__v"><span class="num"><?= number_format($price_current, 2) ?></span><small> ₪</small></div></div>
          <?php if ($price_median > 0): ?><div class="mdstat"><div class="mdstat__k">חציון</div><div class="mdstat__v"><span class="num"><?= number_format($price_median, 2) ?></span><small> ₪</small></div></div><?php endif; ?>
          <?php if ($price_min > 0): ?><div class="mdstat"><div class="mdstat__k">מינימום</div><div class="mdstat__v"><span class="num"><?= number_format($price_min, 2) ?></span><small> ₪</small></div></div><?php endif; ?>
          <?php if ($price_max > 0): ?><div class="mdstat"><div class="mdstat__k">מקסימום</div><div class="mdstat__v"><span class="num"><?= number_format($price_max, 2) ?></span><small> ₪</small></div></div><?php endif; ?>
          <?php if ($source_count > 0): ?><div class="mdstat"><div class="mdstat__k">מקורות</div><div class="mdstat__v"><span class="num"><?= (int)$source_count ?></span></div></div><?php endif; ?>
          <?php if ($obs_count > 0): ?><div class="mdstat"><div class="mdstat__k">תצפיות</div><div class="mdstat__v"><span class="num"><?= (int)$obs_count ?></span></div></div><?php endif; ?>
        <?php else: ?>
          <div class="mdempty" style="grid-column:1/-1">
            <span class="mdempty__ic"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg></span>
            <div><b>תרמו מחיר</b><p>עזרו לבנות את המחירון עבור מוצר זה.</p></div>
          </div>
        <?php endif; ?>
      </div>

      <?php /* Big sparkline (7 latest) */ ?>
      <?php if (!empty($spark_prices) && $spark_max > 0): ?>
      <div class="pcard mdcard mdspark">
        <div class="mdcard__sub">7 תצפיות אחרונות</div>
        <div class="bigspark" aria-hidden="true">
          <?php foreach (array_slice($spark_prices, 0, 7) as $i => $sp):
            $bar_h = $spark_max > 0 ? max(4, (int)(($sp / $spark_max) * 100)) : 4;
          ?>
          <i<?= $i === 0 ? ' class="hi"' : '' ?> style="height:<?= $bar_h ?>%;min-height:2px"></i>
          <?php endforeach; ?>
        </div>
      </div>
      <?php endif; ?>

      <?php /* Cross-link to crop book (AC-7) */ ?>
      <?php if ($book_slug !== ''): ?>
      <a class="pcard mdlink" href="/crop-book/<?= $h($book_slug) ?>">
        <span class="mdlink__ic"><svg class="gi" aria-hidden="true"><use href="#i-book"/></svg></span>
        <span class="mdlink__b">
          <span class="mdlink__t"><?= $h($book_label_he) ?></span>
          <span class="mdlink__s">ספר גידולים — זנים, DTM, יבול</span>
        </span>
        <span class="mdlink__arrow" aria-hidden="true">←</span>
      </a>
      <?php endif; ?>

      <?php /* Source breakdown */ ?>
      <?php
      $prov_sources = [];
      foreach ($hist_rows as $hr) {
          $src = (string)($hr['source'] ?? '');
          if ($src !== '') { $prov_sources[$src] = ($prov_sources[$src] ?? 0) + 1; }
      }
      if (!empty($prov_sources)):
      ?>
      <div class="pcard mdcard mdsrc">
        <div class="mdcard__sub">מקורות נתונים</div>
        <?php foreach ($prov_sources as $src => $cnt): ?>
        <div class="mdsrc__row"><span><?= $h($src) ?></span><span class="num"><?= (int)$cnt ?></span></div>
        <?php endforeach; ?>
      </div>
      <?php endif; ?>

    </aside><!-- /mdgrid__side -->
  </div><!-- /mdgrid -->

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
