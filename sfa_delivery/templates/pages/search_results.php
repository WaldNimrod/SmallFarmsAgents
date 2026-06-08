<?php
/**
 * search_results.php — Route /search — Class B v2
 *
 * WP-CB-UI-CLASSB — Board-B frames `search-results` / `search-nomatch`.
 * Components: .srch-bar, .srch-echo, .srch-suggest, .srch-group, .srch-rows,
 *             .srow (book + market), .srch-nomatch + .reqinfo, .srch-recent.
 *
 * Data contract (HubController::search):
 *   $query           string — search query
 *   $crop_results    array  — crops (slug, name_he, en_name, family_tag_he)
 *   $product_results array  — products (slug, name_he, unit_he, price_current,
 *                             last_price) — NOTE: source_count=0 from controller
 *
 * MINOR F-04 (honesty §4): controller sets price_median=price_min=price_max=current
 *   and source_count=0. We ONLY show single price (no range/source count on srow).
 *   Where absent, show — / empty state. Never fabricate numbers.
 */
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$query           = (string)($query ?? ($q ?? ''));
$crop_results    = is_array($crop_results ?? null) ? $crop_results : [];
$product_results = is_array($product_results ?? null) ? $product_results : [];

$total = count($crop_results) + count($product_results);

$page_title = 'חיפוש';
$active     = 'home';

/**
 * Wrap matched portion with <mark>.
 * Finds first occurrence of query in text (case-insensitive) and wraps it.
 * Guard with function_exists — template may be included multiple times in tests.
 */
if (!function_exists('sfa_mark')) {
    function sfa_mark(string $text, string $query): string {
        if ($query === '' || $text === '') return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
        $pos = mb_stripos($text, $query, 0, 'UTF-8');
        if ($pos === false) return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
        $before = mb_substr($text, 0, $pos, 'UTF-8');
        $match  = mb_substr($text, $pos, mb_strlen($query, 'UTF-8'), 'UTF-8');
        $after  = mb_substr($text, $pos + mb_strlen($query, 'UTF-8'), null, 'UTF-8');
        return htmlspecialchars($before, ENT_QUOTES, 'UTF-8')
             . '<mark>' . htmlspecialchars($match, ENT_QUOTES, 'UTF-8') . '</mark>'
             . htmlspecialchars($after, ENT_QUOTES, 'UTF-8');
    }
}

ob_start();
?>
<div style="max-width:740px;margin:0 auto;padding:20px clamp(16px,3vw,28px)">

  <?php /* Search bar */ ?>
  <form class="srch-bar" action="/search" method="get" role="search" aria-label="חיפוש">
    <span class="ic">⌕</span>
    <input type="search" name="q" value="<?= $h($query) ?>" placeholder="חיפוש גידולים ומחירים…"
           autofocus aria-label="שדה חיפוש">
    <?php if ($query !== ''): ?>
      <button type="button" class="clear" onclick="this.form.reset();this.form.q.focus()" aria-label="נקה">×</button>
    <?php endif; ?>
  </form>

  <?php if ($query === ''): ?>
    <?php /* Empty state — no query yet */ ?>
    <div class="srch-suggest">
      <span class="srch-suggest__lbl"><svg class="gi" aria-hidden="true"><use href="#i-bulb"/></svg> נסו:</span>
      <a class="schip" href="/search?q=עגבנייה">עגבנייה</a>
      <a class="schip" href="/search?q=מלפפון">מלפפון</a>
      <a class="schip" href="/search?q=פלפל">פלפל</a>
      <a class="schip" href="/search?q=בצל">בצל</a>
      <a class="schip" href="/search?q=גזר">גזר</a>
    </div>

  <?php elseif (empty($crop_results) && empty($product_results)): ?>
    <?php /* No-match state */ ?>
    <p class="srch-echo">חיפוש: <b class="q"><?= $h($query) ?></b> — לא נמצאו תוצאות</p>
    <div class="srch-nomatch">
      <div class="srch-nomatch__ic" aria-hidden="true">⌕</div>
      <h3>לא נמצאה תוצאה עבור "<?= $h($query) ?>"</h3>
      <p>נסו מילת חיפוש אחרת, או בקשו הוספת גידול/מוצר חדש.</p>
      <a class="reqinfo" href="/community">◐ בקשו הוספה</a>
    </div>

  <?php else: ?>
    <?php /* Results echo */ ?>
    <p class="srch-echo">תוצאות עבור: <b class="q"><?= $h($query) ?></b> — <?= (int)$total ?> נמצאו</p>

    <?php /* Book results group */ ?>
    <?php if (!empty($crop_results)): ?>
    <div class="srch-group">
      <div class="srch-group__head">
        <span class="ic ic--book" aria-hidden="true">▤</span>
        <h3>ספר הגידולים</h3>
        <span class="count"><?= count($crop_results) ?> תוצאות</span>
        <a class="seeall" href="/crop-book/?q=<?= urlencode($query) ?>">כל הגידולים ←</a>
      </div>
      <div class="srch-rows">
        <?php foreach ($crop_results as $crop):
          $c_slug   = (string)($crop['slug'] ?? '');
          $c_name   = (string)($crop['name_he'] ?? '');
          $c_en     = (string)($crop['en_name'] ?? '');
          $c_family = (string)($crop['family_tag_he'] ?? '');
          $c_dtm    = $crop['dtm_days'] ?? null;
          $c_glyph  = $c_name !== '' ? mb_substr($c_name, 0, 1, 'UTF-8') : '<svg class="gi" aria-hidden="true"><use href="#i-seedling"/></svg>';
        ?>
        <a class="srow" href="/crop-book/<?= $h($c_slug) ?>">
          <div class="srow__art">
            <span class="veg"><?= $c_glyph ?></span>
          </div>
          <div>
            <div class="srow__name"><?= sfa_mark($c_name, $query) ?>
              <?php if ($c_en !== ''): ?><em><?= $h($c_en) ?></em><?php endif; ?>
            </div>
            <div class="srow__meta">
              <?php if ($c_family !== ''): ?><span><?= $h($c_family) ?></span><?php endif; ?>
              <?php if ($c_dtm !== null): ?><span><span class="num"><?= (int)$c_dtm ?></span> ימים</span><?php endif; ?>
            </div>
          </div>
          <div class="srow__end">
            <span style="color:var(--gj-leaf-deep);font-size:15px">←</span>
          </div>
        </a>
        <?php endforeach; ?>
      </div>
    </div>
    <?php endif; ?>

    <?php /* Market results group */ ?>
    <?php if (!empty($product_results)): ?>
    <div class="srch-group">
      <div class="srch-group__head">
        <span class="ic ic--market" aria-hidden="true">₪</span>
        <h3>מחירון</h3>
        <span class="count"><?= count($product_results) ?> תוצאות</span>
        <a class="seeall" href="/market/">כל המחירון ←</a>
      </div>
      <div class="srch-rows">
        <?php foreach ($product_results as $prod):
          $p_slug  = (string)($prod['slug'] ?? '');
          $p_name  = (string)($prod['name_he'] ?? '');
          $p_unit  = (string)($prod['unit_he'] ?? '');
          // MINOR F-04: only show real price (price_current / last_price).
          // Do NOT show price_min/max/median/source_count — these are shims (= current, 0).
          $p_price = null;
          if (isset($prod['price_current']) && (float)$prod['price_current'] > 0) {
              $p_price = (float)$prod['price_current'];
          } elseif (isset($prod['last_price']) && (float)$prod['last_price'] > 0) {
              $p_price = (float)$prod['last_price'];
          }
          $p_glyph = $p_name !== '' ? mb_substr($p_name, 0, 1, 'UTF-8') : '<svg class="gi" aria-hidden="true"><use href="#i-basket"/></svg>';
          $unit_lbl = match(strtolower(trim($p_unit))) {
              'kg', 'ק"ג', 'ק״ג' => 'לק״ג',
              'unit', 'יח׳', 'יח\'' => 'ליחידה',
              'bunch', 'אגודה' => 'לאגודה',
              default => $p_unit !== '' ? 'ל' . $p_unit : '',
          };
        ?>
        <a class="srow" href="/market/<?= $h($p_slug) ?>">
          <div class="srow__art">
            <span class="veg"><?= $p_glyph ?></span>
          </div>
          <div>
            <div class="srow__name"><?= sfa_mark($p_name, $query) ?></div>
            <div class="srow__meta">
              <?php if ($unit_lbl !== ''): ?><span><?= $h($unit_lbl) ?></span><?php endif; ?>
            </div>
          </div>
          <div class="srow__end">
            <?php if ($p_price !== null): ?>
              <span class="srow__price"><?= number_format($p_price, 2) ?><small> ₪</small></span>
            <?php else: ?>
              <span class="srow__price" style="color:var(--gj-ink-soft)">—</span>
            <?php endif; ?>
            <?php if ($unit_lbl !== ''): ?><small style="font-size:10px;color:var(--gj-ink-soft)"><?= $h($unit_lbl) ?></small><?php endif; ?>
          </div>
        </a>
        <?php endforeach; ?>
      </div>
    </div>
    <?php endif; ?>

  <?php endif; ?>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
