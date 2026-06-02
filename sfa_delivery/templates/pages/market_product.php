<?php
/**
 * market_product.php — Route /market/{slug} — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frame `market-detail`.
 * Components: .pdetail, .pbig, .pgraph+.rangesel (7/28 live; 90/year disabled),
 *             .phist, .pstats/.pstat, .prov (reused), .xlink, .emptybox,
 *             compact .mkt-disc (MINOR F-01), freshness pill (§9a).
 *
 * Data contract (MarketViewController::detail):
 *   $product — merged row with name_he, price_current, price_min, price_max,
 *              price_median, source_count, observation_count, freshness_days,
 *              history (array), book_slug, book_label_he, updated_he, unit_he
 *   $history — array<{price_date, price, source}> — 28-day window (also in
 *              $product['history'])
 *
 * MINOR F-02: graph range label = 28י (not 30), live 7+28, disabled 90+year.
 * MINOR F-05: 90י/year .rangesel buttons marked .is-disabled server-side.
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$product = is_array($product ?? null) ? $product : [];
$history = is_array($history ?? null) ? $history : [];

$slug          = (string)($product['slug']          ?? '');
$name_he       = (string)($product['name_he']       ?? $product['hebrew_name'] ?? '');
$en_name       = (string)($product['en_name']       ?? '');
$icon_slug     = (string)($product['icon_slug']     ?? 'leaf');
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
$unit_lbl = match(strtolower(trim($unit))) {
    'kg', 'ק"ג', 'ק״ג' => 'לק״ג',
    'unit', 'יח׳', 'יח\'' => 'ליחידה',
    'bunch', 'אגודה' => 'לאגודה',
    default => $unit !== '' ? 'ל' . $unit : '',
};

// Freshness pill (§9a — LOCKED thresholds)
if ($freshness === null) {
    $fresh_cls = 'fresh--stale'; $fresh_lbl = 'אין דיווח';
} elseif ($freshness <= 3) {
    $fresh_cls = 'fresh--fresh';
    $fresh_lbl = $freshness === 0 ? 'טרי · עודכן היום' : ($freshness === 1 ? 'טרי · עודכן אתמול' : 'טרי · לפני ' . $freshness . ' ימים');
} elseif ($freshness <= 7) {
    $fresh_cls = 'fresh--aging'; $fresh_lbl = 'מתעדכן · לפני ' . $freshness . ' ימים';
} else {
    $fresh_cls = 'fresh--stale'; $fresh_lbl = 'ישן · לפני ' . $freshness . ' ימים';
}

$is_empty = ($price_current === null || $price_current <= 0);

// Build sparkline data from last-7 history rows (pure CSS, no chart lib)
$spark_prices = [];
foreach (array_slice($hist_rows, 0, 7) as $hr) {
    $spark_prices[] = (float)($hr['price'] ?? 0);
}
$spark_max = $spark_prices ? max($spark_prices) : 0;

// Build SVG path for pgraph from history (28-day)
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
<div class="sh__body--wide">

  <?php /* Compact disclaimer — mandatory on detail too (MINOR F-01) */ ?>
  <?php $compact = true; include __DIR__ . '/../macros/market_disclaimer.php'; ?>

  <div class="pdetail">
    <div class="pdetail__main">

      <?php /* Price hero */ ?>
      <div class="pbig">
        <div class="pbig__art">
          <?php if (!$is_empty): ?>
            <span class="veg"><?= mb_substr($name_he, 0, 1, 'UTF-8') ?></span>
          <?php else: ?>
            <span class="veg">📦</span>
          <?php endif; ?>
        </div>
        <div>
          <h1 style="font-family:var(--gj-font-head);font-weight:900;font-size:22px;margin:0 0 4px"><?= $h($name_he) ?></h1>
          <?php if ($en_name !== ''): ?>
            <div style="font-size:12px;color:var(--gj-ink-soft);margin-bottom:6px"><?= $h($en_name) ?></div>
          <?php endif; ?>
          <?php if (!$is_empty): ?>
          <div class="pbig__price">
            <span class="big"><?= number_format($price_current, 2) ?></span>
            <span class="cur"><?= $currency ?></span>
            <?php if ($unit_lbl !== ''): ?><span class="per"><?= $h($unit_lbl) ?></span><?php endif; ?>
          </div>
          <div class="pbig__meta">
            <?php if ($price_min > 0 && $price_max > 0): ?>
              <span>טווח: <b><?= number_format($price_min, 2) ?>–<?= number_format($price_max, 2) ?> ₪</b></span>
            <?php endif; ?>
            <?php if ($price_median > 0): ?>
              <span>חציון: <b><?= number_format($price_median, 2) ?> ₪</b></span>
            <?php endif; ?>
            <?php if ($source_count > 0): ?>
              <span><?= (int)$source_count ?> מקורות</span>
            <?php endif; ?>
            <?php if ($updated_he !== ''): ?>
              <span>עודכן <?= $h($updated_he) ?></span>
            <?php endif; ?>
          </div>
          <?php else: ?>
          <div class="pbig__price"><span class="big" style="color:var(--gj-ink-soft)">—</span></div>
          <div style="font-size:12.5px;color:var(--gj-ink-soft);margin-top:6px">אין דיווחי מחיר עבור מוצר זה.</div>
          <?php endif; ?>
          <div style="margin-top:10px">
            <span class="fresh <?= $h($fresh_cls) ?>"><?= $h($fresh_lbl) ?></span>
          </div>
        </div>
      </div>

      <?php /* Price graph — 28-day (MINOR F-02: range selector shows 28י not 30) */ ?>
      <div class="pgraph">
        <div class="pgraph__top">
          <h3>מחיר — 28 ימים אחרונים</h3>
          <?php if ($delta !== null): ?>
            <span class="pgraph__chg <?= $delta >= 0 ? 'up' : 'dn' ?>">
              <?= $delta >= 0 ? '▲' : '▼' ?><?= number_format(abs($delta), 1) ?>%
              <small>לעומת תצפית קודמת</small>
            </span>
          <?php endif; ?>
          <?php /* Range selector — MINOR F-02 (28י) + MINOR F-05 (90/year disabled server-side) */ ?>
          <div class="rangesel" role="group" aria-label="טווח זמן">
            <button type="button" class="is-active" data-days="7">7י</button>
            <button type="button" class="is-active" data-days="28">28י</button>
            <button type="button" class="is-disabled" disabled aria-disabled="true" title="בקרוב">90י</button>
            <button type="button" class="is-disabled" disabled aria-disabled="true" title="בקרוב">שנה</button>
          </div>
        </div>
        <?php if ($has_graph): ?>
        <svg class="pgraph__svg" viewBox="0 0 <?= $svg_w ?> <?= $svg_h ?>" preserveAspectRatio="none" aria-label="גרף מחיר">
          <path class="pgraph__area" d="<?= $svg_area ?>"/>
          <path class="pgraph__line" d="<?= $svg_path ?>"/>
        </svg>
        <div class="pgraph__x">
          <?php if (!empty($graph_rows)):
            $first = $graph_rows[0]; $last_r = end($graph_rows);
          ?>
            <span><?= $h((string)($first['date_he'] ?? $first['price_date'] ?? '')) ?></span>
            <span><?= $h((string)($last_r['date_he'] ?? $last_r['price_date'] ?? '')) ?></span>
          <?php endif; ?>
        </div>
        <?php elseif ($is_empty): ?>
        <div class="emptybox">
          <div class="emptybox__ic">📭</div>
          <div>
            <b>אין נתוני גרף</b>
            <p>לא נמצאו דיווחי מחיר עבור מוצר זה. תרמו מחיר ועזרו לנו לבנות את הנתונים.</p>
          </div>
        </div>
        <?php else: ?>
        <div class="emptybox">
          <div class="emptybox__ic">📊</div>
          <div>
            <b>אין מספיק נתונים לגרף</b>
            <p>נדרשות לפחות 2 תצפיות להצגת קו מגמה.</p>
          </div>
        </div>
        <?php endif; ?>
        <?php if (!$is_empty): ?>
        <div class="pgraph__legend" style="margin-top:8px;font-size:10px">
          <span>₪ <?= $h($currency) ?><?= $unit_lbl !== '' ? ' · ' . $h($unit_lbl) : '' ?></span>
        </div>
        <?php endif; ?>
      </div>

      <?php /* Price history table (.phist) */ ?>
      <div>
        <h2 class="gj-h3" style="margin:0 0 10px">היסטוריית מחיר</h2>
        <?php if (!empty($hist_rows)): ?>
        <table class="phist">
          <thead>
            <tr>
              <th>תאריך</th>
              <th>מחיר</th>
              <th>מקור</th>
              <th>שינוי</th>
            </tr>
          </thead>
          <tbody>
            <?php
            $prev_price = null;
            foreach ($hist_rows as $idx => $hr):
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
              <td class="num"><?= number_format($price_v, 2) ?> ₪</td>
              <td><?= $h($source_v) ?></td>
              <td>
                <?php if ($row_delta !== null): ?>
                  <span class="<?= $row_delta >= 0 ? 'delta-up' : 'delta-dn' ?>">
                    <?= $row_delta >= 0 ? '▲' : '▼' ?><?= number_format(abs($row_delta), 1) ?>%
                  </span>
                <?php else: ?>—<?php endif; ?>
              </td>
            </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
        <?php else: ?>
        <div class="emptybox">
          <div class="emptybox__ic">📭</div>
          <div>
            <b>אין נתוני היסטוריה</b>
            <p>לא נמצאו דיווחי מחיר ב-28 הימים האחרונים עבור מוצר זה.</p>
          </div>
        </div>
        <?php endif; ?>
      </div>

    </div><!-- /pdetail__main -->

    <div><!-- sidebar -->

      <?php /* Stat strip */ ?>
      <div class="pstats" style="margin-bottom:16px">
        <?php if (!$is_empty): ?>
        <div class="pstat">
          <div class="pstat__k">מחיר נוכחי</div>
          <div class="pstat__v"><?= number_format($price_current, 2) ?><small> ₪</small></div>
        </div>
        <?php if ($price_median > 0): ?>
        <div class="pstat">
          <div class="pstat__k">חציון</div>
          <div class="pstat__v"><?= number_format($price_median, 2) ?><small> ₪</small></div>
        </div>
        <?php endif; ?>
        <?php if ($price_min > 0): ?>
        <div class="pstat">
          <div class="pstat__k">מינימום</div>
          <div class="pstat__v"><?= number_format($price_min, 2) ?><small> ₪</small></div>
        </div>
        <?php endif; ?>
        <?php if ($price_max > 0): ?>
        <div class="pstat">
          <div class="pstat__k">מקסימום</div>
          <div class="pstat__v"><?= number_format($price_max, 2) ?><small> ₪</small></div>
        </div>
        <?php endif; ?>
        <?php if ($source_count > 0): ?>
        <div class="pstat">
          <div class="pstat__k">מקורות</div>
          <div class="pstat__v"><?= (int)$source_count ?></div>
        </div>
        <?php endif; ?>
        <?php if ($obs_count > 0): ?>
        <div class="pstat">
          <div class="pstat__k">תצפיות</div>
          <div class="pstat__v"><?= (int)$obs_count ?></div>
        </div>
        <?php endif; ?>
        <?php else: ?>
        <div class="emptybox" style="grid-column:1/-1">
          <div class="emptybox__ic">◐</div>
          <div>
            <b>תרמו מחיר</b>
            <p>עזרו לנו לבנות את המחירון עבור מוצר זה.</p>
          </div>
        </div>
        <?php endif; ?>
      </div>

      <?php /* Sparkline in sidebar */ ?>
      <?php if (!empty($spark_prices) && $spark_max > 0): ?>
      <div style="margin-bottom:16px;background:var(--gj-paper);border:1px solid var(--gj-line);border-radius:var(--gj-r-m);padding:12px">
        <div style="font-size:11px;color:var(--gj-ink-soft);margin-bottom:8px">7 תצפיות אחרונות</div>
        <div class="spark">
          <?php foreach (array_slice($spark_prices, 0, 7) as $i => $sp):
            $bar_h = $spark_max > 0 ? max(4, (int)(($sp / $spark_max) * 100)) : 4;
            $is_hi = ($i === 0); // most recent is highlighted
          ?>
          <i<?= $is_hi ? ' class="hi"' : '' ?> style="height:<?= $bar_h ?>%;min-height:2px"></i>
          <?php endforeach; ?>
        </div>
      </div>
      <?php endif; ?>

      <?php /* Cross-link to crop book */ ?>
      <?php if ($book_slug !== ''): ?>
      <a class="xlink" href="/crop-book/<?= $h($book_slug) ?>" style="display:flex;align-items:center;gap:10px;padding:12px 14px;background:var(--gj-paper);border:1px solid var(--gj-line);border-radius:var(--gj-r-m);text-decoration:none;color:inherit;margin-bottom:12px">
        <span style="font-size:24px">📖</span>
        <div>
          <div style="font-family:var(--gj-font-head);font-weight:700;font-size:14px"><?= $h($book_label_he) ?></div>
          <div style="font-size:12px;color:var(--gj-ink-soft)">ספר גידולים — זנים, DTM, יבול</div>
        </div>
        <span style="margin-inline-start:auto;color:var(--gj-leaf-deep);font-size:16px">←</span>
      </a>
      <?php endif; ?>

      <?php /* Source breakdown (.prov reused) */ ?>
      <?php
      $prov_sources = [];
      foreach ($hist_rows as $hr) {
          $src = (string)($hr['source'] ?? '');
          if ($src !== '') {
              $prov_sources[$src] = ($prov_sources[$src] ?? 0) + 1;
          }
      }
      if (!empty($prov_sources)):
      ?>
      <div style="background:var(--gj-paper);border:1px solid var(--gj-line);border-radius:var(--gj-r-m);padding:12px;margin-bottom:12px">
        <div style="font-size:11px;font-weight:700;color:var(--gj-ink-soft);margin-bottom:8px">מקורות נתונים</div>
        <?php foreach ($prov_sources as $src => $cnt): ?>
        <div style="display:flex;justify-content:space-between;font-size:12.5px;padding:4px 0;border-bottom:1px solid var(--gj-line)">
          <span><?= $h($src) ?></span>
          <span style="font-family:var(--gj-font-mono)"><?= (int)$cnt ?></span>
        </div>
        <?php endforeach; ?>
      </div>
      <?php endif; ?>

    </div><!-- /sidebar -->
  </div><!-- /pdetail -->

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
