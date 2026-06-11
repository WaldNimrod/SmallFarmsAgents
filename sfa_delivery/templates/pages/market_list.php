<?php
/**
 * market_list.php — Route /market/ — WP-CB-UI-REDESIGN (WI-5)
 *
 * Rebuilt from team_35 market mockup: the community price index is a grid of
 * universal-drill-down <details class="pcard"> cards — CLOSED shows price +
 * trend + freshness + mini sparkline; OPEN reveals range / median / sources ·
 * observations / updated + the 28-day graph + cross-links to the crop book and
 * the calculator. Honest freshness states (fresh/aging/stale → "אין מגמה" when
 * stale); prices LTR-isolated. Mandatory community-index disclaimer preserved.
 *
 * Data contract (MarketViewController::index): $products[] each name_he,
 * unit_he, price_current, price_min/max/median, source_count, observation_count,
 * freshness_days, updated_he, icon_slug, book_slug, spark[], trend_pct, trend_dir.
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
        $norm = strtolower(trim($unit));
        return match($norm) {
            'kg', 'ק"ג', 'ק״ג'                         => 'לק״ג',
            'unit', 'יח׳', 'יח\''                       => 'ליחידה',
            'bunch', 'אגודה'                             => 'לאגודה',
            'basket_large', 'basket_medium', 'basket_small' => 'לסל',
            default => (preg_match('/^[a-z][a-z_]*$/', $norm) ? 'ליחידה' : ($unit !== '' ? 'ל' . $unit : '')),
        };
    }
}

$fresh_n = 0;
foreach ($products as $p) { if (isset($p['freshness_days']) && (int)$p['freshness_days'] <= 7) { $fresh_n++; } }

$nf2 = static fn ($v) => number_format((float)$v, 2);

ob_start();
?>
<div class="market-index">

  <div class="lead">
    <div>
      <h1>מחירון השוק הקהילתי</h1>
      <p>מדד מחירים לירקות אורגניים — מסריקות ציבוריות ותרומות הקהילה, מתעדכן באופן שוטף.</p>
    </div>
    <span class="pill pill--tomato"><span class="num"><?= count($products) ?></span> מוצרים במחירון</span>
  </div>

  <?php /* Disclaimer — MANDATORY, never suppressed (LOCKED copy). Collapsible, closed default. */ ?>
  <?php $collapsible = true; include __DIR__ . '/../macros/market_disclaimer.php'; $collapsible = false; ?>

  <div class="tb">
    <div class="chips" role="group" aria-label="סינון לפי קטגוריה">
      <a class="chip<?= $current_category === '' ? ' on' : '' ?>" href="/market/">הכל</a>
      <?php foreach ($categories as $cat):
        $cat_slug = (string)($cat['slug'] ?? '');
        $cat_name = (string)($cat['name_he'] ?? $cat_slug);
      ?>
      <a class="chip<?= $current_category === $cat_slug ? ' on' : '' ?>" href="/market/?category=<?= urlencode($cat_slug) ?>"><?= $h($cat_name) ?></a>
      <?php endforeach; ?>
    </div>
  </div>

  <div class="legend" aria-label="מקרא טריות">
    <span><i style="background:var(--gj-leaf)"></i>טרי (0–3 ימים)</span>
    <span><i style="background:var(--gj-sun)"></i>מתעדכן (4–7)</span>
    <span><i style="background:var(--gj-tomato)"></i>ישן (7+)</span>
    <span style="margin-inline-start:auto">לחצו על מוצר להרחבה: טווח, חציון, מקורות וגרף 28 יום</span>
  </div>

  <div class="cnt">מציג <b class="num"><?= count($products) ?></b> מוצרים<?php if ($fresh_n > 0): ?> · <b class="num"><?= $fresh_n ?></b> עודכנו השבוע<?php endif; ?></div>

  <div class="pgrid" id="mkt-scope">
    <?php if (empty($products)): ?>
      <div class="note" style="grid-column:1/-1">המחירון עדיין ריק — חזרו בקרוב או <a href="/community">תרמו מחיר</a>.</div>
    <?php else: ?>
      <?php foreach ($products as $row):
        $name_he   = (string)($row['name_he'] ?? $row['hebrew_name'] ?? '');
        $slug      = (string)($row['slug'] ?? '');
        $unit_lbl  = sfa_unit_label((string)($row['unit_he'] ?? $row['unit'] ?? ''));
        $price     = isset($row['price_current']) && $row['price_current'] !== null ? (float)$row['price_current'] : (isset($row['last_price']) ? (float)$row['last_price'] : null);
        $pmin      = (float)($row['price_min'] ?? 0);
        $pmax      = (float)($row['price_max'] ?? 0);
        $pmed      = (float)($row['price_median'] ?? 0);
        $src       = (int)($row['source_count'] ?? 0);
        $obs       = (int)($row['observation_count'] ?? 0);
        $fresh     = isset($row['freshness_days']) ? (int)$row['freshness_days'] : null;
        $icon_slug = (string)($row['icon_slug'] ?? 'leaf');
        $wc_art    = (string)($row['wc_art'] ?? '');
        $book_slug = (string)($row['book_slug'] ?? '');
        $updated   = (string)($row['updated_he'] ?? '');
        $spark     = is_array($row['spark'] ?? null) ? $row['spark'] : [];
        $trend_dir = (string)($row['trend_dir'] ?? 'flat');
        $trend_pct = (float)($row['trend_pct'] ?? 0);

        $is_empty = ($price === null || $price <= 0);
        $is_stale = !$is_empty && ($fresh !== null && $fresh > 7);

        if ($fresh === null)      { $fcls = 's'; $flbl = 'אין דיווח'; }
        elseif ($fresh <= 3)      { $fcls = 'f'; $flbl = $fresh === 0 ? 'טרי · עודכן היום' : 'טרי · לפני ' . $fresh . ' ימים'; }
        elseif ($fresh <= 7)      { $fcls = 'a'; $flbl = 'מתעדכן · לפני ' . $fresh . ' ימים'; }
        else                      { $fcls = 's'; $flbl = 'ישן · לפני ' . $fresh . ' ימים'; }
      ?>
      <details class="pcard<?= $is_stale ? ' stale' : '' ?>">
        <summary>
          <div class="pc__top">
            <div class="pc__art" aria-hidden="true"><?php if ($wc_art !== ''): ?><img src="/public_assets/img/crops/<?= $h($wc_art) ?>" alt="" loading="lazy" decoding="async"><?php else: ?><svg class="gi"><use href="#icon-<?= $h($icon_slug) ?>"/></svg><?php endif; ?></div>
            <div><div class="pc__name"><?= $h($name_he) ?></div><?php if ($unit_lbl !== ''): ?><div class="pc__unit"><?= $h($unit_lbl) ?></div><?php endif; ?></div>
            <span class="pc__chev">▾</span>
          </div>
          <?php if (!$is_empty): ?>
          <div class="pc__price">
            <span class="big num"><?= $nf2($price) ?></span><span class="cur">₪</span><?php if ($unit_lbl !== ''): ?><span class="per"><?= $h($unit_lbl) ?></span><?php endif; ?>
            <?php if ($is_stale || $trend_dir === 'flat'): ?>
              <span class="trend pc__trend--none"></span>
            <?php elseif ($trend_dir === 'up'): ?>
              <span class="trend up">▲ <span class="num"><?= (int)abs($trend_pct) ?>%</span></span>
            <?php else: ?>
              <span class="trend down">▼ <span class="num"><?= (int)abs($trend_pct) ?>%</span></span>
            <?php endif; ?>
          </div>
          <div class="pc__foot">
            <span class="fresh <?= $fcls ?>"><?= $h($flbl) ?></span>
            <?php if ($src > 0): ?><span class="pc__src"><span class="num"><?= $src ?></span> מקורות</span><?php endif; ?>
            <?php if (!empty($spark)): ?><span class="spark" aria-hidden="true"><?php foreach (array_slice($spark, -7) as $bh): ?><i style="height:<?= (int)$bh ?>%<?= $is_stale ? ';background:var(--gj-paper-3)' : '' ?>"></i><?php endforeach; ?></span><?php endif; ?>
          </div>
          <?php else: ?>
          <div class="pc__price"><span class="big">—</span></div>
          <div class="pc__foot"><span class="fresh s">אין דיווח</span></div>
          <?php endif; ?>
        </summary>
        <div class="pc__body">
          <div class="drill">▾ עומק נוסף</div>
          <dl style="margin:0">
            <?php if ($pmin > 0 && $pmax > 0 && $pmin !== $pmax): ?><div class="prow"><dt>טווח מחירים</dt><dd><span class="num">₪<?= $nf2($pmin) ?>–₪<?= $nf2($pmax) ?></span></dd></div><?php endif; ?>
            <?php if ($pmed > 0): ?><div class="prow"><dt>חציון</dt><dd><span class="num">₪<?= $nf2($pmed) ?></span></dd></div><?php endif; ?>
            <?php if ($src > 0): ?><div class="prow"><dt>מקורות · תצפיות</dt><dd><span class="num"><?= $src ?> · <?= $obs ?></span></dd></div><?php endif; ?>
            <?php if ($updated !== ''): ?><div class="prow"><dt>עודכן</dt><dd><?= $h($updated) ?></dd></div><?php endif; ?>
          </dl>
          <?php if (!$is_stale && count($spark) >= 2): ?>
            <div class="bigspark" aria-hidden="true"><?php $last = count($spark) - 1; foreach ($spark as $i => $bh): ?><i class="<?= $i === $last ? 'hi' : '' ?>" style="height:<?= (int)$bh ?>%"></i><?php endforeach; ?></div>
            <div style="font-size:12px;color:var(--gj-ink-soft);text-align:center">מגמת 28 יום</div>
          <?php endif; ?>
          <?php if ($is_stale): ?>
            <div class="note" style="margin-top:10px">מחיר ישן — <a href="/community" style="color:inherit;text-decoration:underline;font-weight:700">דווחו מחיר עדכני ←</a></div>
          <?php endif; ?>
          <div class="pc__links">
            <?php if ($book_slug !== ''): ?><a class="btn btn--ghost" href="/crop-book/<?= $h($book_slug) ?>/"><svg class="gi" aria-hidden="true"><use href="#i-book"/></svg> בספר הגידולים</a><?php endif; ?>
            <a class="btn btn--ghost" href="/calc/?crop=<?= $h(rawurlencode($name_he)) ?>"><svg class="gi" aria-hidden="true"><use href="#i-scale"/></svg> חשב הכנסה</a>
          </div>
        </div>
      </details>
      <?php endforeach; ?>
    <?php endif; ?>
  </div>

  <section class="contrib" style="margin-top:28px">
    <span class="contrib__ic" aria-hidden="true"><svg class="gi"><use href="#i-shekel"/></svg></span>
    <div class="t"><b>יודעים מחיר מהשוק?</b><p>דווחו מחיר — וזה יידלק לכל הקהילה. ככל שיותר מקורות, המדד מדויק יותר.</p></div>
    <span class="sp"></span>
    <a class="btn btn--primary" href="/community">✎ דווחו מחיר ←</a>
  </section>

</div>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
