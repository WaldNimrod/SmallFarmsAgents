<?php
/**
 * book_entry.php — Route /crop-book/ (CB0) — WP-CB-UI-REDESIGN (WI-3)
 *
 * Rebuilt from team_35 LOD300 book_list mockup: /crop-book/ is now the open
 * filtered crop index — a .lead header, an ALWAYS-visible .filters bar
 * (search · family · season · method · sort · view toggle), and a .grid of
 * decision .cc cards (availability · days · family · ₪ market chip). The card
 * IS a link to the crop page (Q-A: no in-card drill-down).
 *
 * Honest data: yield/difficulty are omitted (no clean per-m² / difficulty
 * source yet); the ₪ chip renders only when a product price exists for the
 * slug (book↔market loop) — never fabricated.
 *
 * Controller contract (CropBookViewController::entry):
 *   $crops    array  each: slug,name_he,en_name,icon_svg,icon_slug,
 *                    family_tag_he,category,dtm_days,in_season,in_season_activity
 *   $prices   array  slug => ['price'=>float,'unit'=>string]
 *   $view     string 'cards'|'table'
 *   $sort     string 'name'|'dtm'|'now'
 *   $total    int
 *   $families string[]
 *   $filters  array  q,family,season,dtm_max,sow,frost
 */
use SFA\Lib\CropArt;
use SFA\Lib\Template;

$h = [Template::class, 'h'];

$page_title = 'ספר גידולים';
$page_sub   = 'מאגר ידע פתוח';
$active     = 'crop-book';

$crops     = is_array($crops     ?? null) ? $crops     : [];
$prices    = is_array($prices    ?? null) ? $prices    : [];
$estimates = is_array($estimates ?? null) ? $estimates : [];
$families  = is_array($families  ?? null) ? $families  : [];
$view     = (string)($view ?? 'cards');
$sort     = (string)($sort ?? 'name');
$total    = (int)($total ?? count($crops));

$flt     = is_array($filters ?? null) ? $filters : [];
$fq      = (string)($flt['q']      ?? '');
$ffam    = (string)($flt['family'] ?? '');
$fseason = (string)($flt['season'] ?? '');
$fdtm    = $flt['dtm_max'] ?? null;
$fsow    = (string)($flt['sow']   ?? '');
$ffrost  = (string)($flt['frost'] ?? '');
$sel     = fn($a, $b) => $a === $b ? ' selected' : '';

// Preserve active filters across the view-toggle links.
$keep = array_filter([
    'q' => $fq, 'family' => $ffam, 'season' => $fseason,
    'dtm_max' => $fdtm, 'sow' => $fsow, 'frost' => $ffrost, 'sort' => $sort,
], static fn($v) => $v !== null && $v !== '');
$mkurl = static fn(array $over) => '/crop-book/?' . http_build_query(array_merge($keep, $over));

// In-season count for the current month.
$in_season_n = 0;
foreach ($crops as $c) { if (!empty($c['in_season'])) { $in_season_n++; } }
$MONTH_HE_FULL = ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'];
$now_he = $MONTH_HE_FULL[(int)date('n') - 1];

// Watercolor art mapping: single source of truth in SFA\Lib\CropArt (shared
// with the crop page + market grid). Resolved per-card via CropArt::file().

$season_opts = ['' => 'כל העונות', 'summer' => 'קיץ', 'autumn' => 'סתיו', 'winter' => 'חורף', 'spring' => 'אביב'];
$sort_opts   = ['name' => 'מיון: שם א׳–ת׳', 'now' => 'מיון: זמין עכשיו', 'dtm' => 'מיון: ימים להבשלה'];

ob_start();
?>
<div class="cb-crop-detail book-index">

  <div class="lead">
    <div>
      <h1>ספר הגידולים</h1>
      <p>אינדקס פתוח של גידולי ירקות — מועדי שתילה, ריווח, יבול ומחירים.</p>
    </div>
    <span class="pill pill--leaf"><span class="num"><?= (int)$total ?></span> גידולים בספר</span>
  </div>

  <?php /* preserve discoverability of the other crop-book entries the mockup folds away */ ?>
  <nav class="book-subnav" aria-label="כניסות נוספות לספר">
    <a href="/crop-book/questions"><svg class="gi" aria-hidden="true"><use href="#i-bulb"/></svg> שאלות מובילות</a>
    <a href="/crop-book/family"><svg class="gi" aria-hidden="true"><use href="#i-companions"/></svg> משפחות בוטניות</a>
    <a href="/crop-book/cover-crops"><svg class="gi" aria-hidden="true"><use href="#i-sprout"/></svg> כיסוי קרקע</a>
    <a href="/crop-book/search"><svg class="gi" aria-hidden="true"><use href="#i-book"/></svg> חיפוש חופשי</a>
  </nav>

  <?php /* ALWAYS-visible filter bar — real server-side GET form (mockup .filters) */ ?>
  <form class="filters" method="get" action="/crop-book/">
    <input type="hidden" name="view" value="<?= $h($view) ?>">
    <?php if ($fdtm !== null): ?><input type="hidden" name="dtm_max" value="<?= $h((string)$fdtm) ?>"><?php endif; ?>
    <?php if ($ffrost !== ''): ?><input type="hidden" name="frost" value="<?= $h($ffrost) ?>"><?php endif; ?>
    <div class="fsearch">
      <span aria-hidden="true">⌕</span>
      <input type="search" name="q" value="<?= $h($fq) ?>" placeholder="חפש גידול…" aria-label="חיפוש גידול">
    </div>
    <div class="sel">
      <select name="family" aria-label="משפחה בוטנית" onchange="this.form.submit()">
        <option value="">כל המשפחות</option>
        <?php foreach ($families as $fam): ?>
          <option value="<?= $h($fam) ?>"<?= $sel($ffam, (string)$fam) ?>><?= $h($fam) ?></option>
        <?php endforeach; ?>
      </select>
    </div>
    <div class="sel">
      <select name="season" aria-label="עונת שתילה" onchange="this.form.submit()">
        <?php foreach ($season_opts as $val => $lbl): ?>
          <option value="<?= $h($val) ?>"<?= $sel($fseason, $val) ?>><?= $h($lbl) ?></option>
        <?php endforeach; ?>
      </select>
    </div>
    <div class="sel">
      <select name="sow" aria-label="שיטת שתילה" onchange="this.form.submit()">
        <option value="">כל השיטות</option>
        <option value="direct_seed"<?= $sel($fsow, 'direct_seed') ?>>זריעה ישירה</option>
        <option value="transplant"<?= $sel($fsow, 'transplant') ?>>שתילה</option>
      </select>
    </div>
    <span class="fspring"></span>
    <div class="sel">
      <select name="sort" aria-label="מיון" onchange="this.form.submit()">
        <?php foreach ($sort_opts as $val => $lbl): ?>
          <option value="<?= $h($val) ?>"<?= $sel($sort, $val) ?>><?= $h($lbl) ?></option>
        <?php endforeach; ?>
      </select>
    </div>
    <button class="filters__apply" type="submit">סינון</button>
    <div class="viewtog" role="group" aria-label="תצוגה">
      <a class="vt<?= $view === 'cards' ? ' on' : '' ?>" href="<?= $h($mkurl(['view' => 'cards'])) ?>"><svg class="gi" aria-hidden="true"><use href="#i-grid"/></svg> כרטיסים</a>
      <a class="vt<?= $view === 'table' ? ' on' : '' ?>" href="<?= $h($mkurl(['view' => 'table'])) ?>"><svg class="gi" aria-hidden="true"><use href="#i-rows"/></svg> טבלה</a>
    </div>
  </form>

  <div class="fcount">מציג <b class="num"><?= (int)$total ?></b> גידולים<?php if ($in_season_n > 0): ?> · <b class="num"><?= (int)$in_season_n ?></b> זמינים לשתילה/זריעה ב<?= $h($now_he) ?><?php endif; ?></div>

  <div id="crop-list-scope">
  <?php if (empty($crops)): ?>
    <div class="cb-empty">
      <p>לא נמצאו גידולים התואמים את הסינון.</p>
      <a class="filters__clear" href="/crop-book/?view=<?= $h($view) ?>">↺ נקו סינון</a>
    </div>
  <?php elseif ($view === 'table'): ?>
    <div class="dt-table-wrap" style="overflow-x:auto">
      <table class="ptable dt-table">
        <thead>
          <tr><th>גידול</th><th>משפחה</th><th>ימים להבשלה</th><th>בעונה</th><th>מחיר שוק</th></tr>
        </thead>
        <tbody>
          <?php foreach ($crops as $c):
            $cslug = (string)($c['slug'] ?? '');
            $pr    = $prices[$cslug] ?? null;
            $est   = $estimates[$cslug] ?? null; // AC-1.2 estimated range (only when no live price)
          ?>
          <tr>
            <td><div class="t-name"><a href="/crop-book/<?= $h($cslug) ?>/"><?= $h((string)($c['name_he'] ?? '')) ?></a>
              <?php if (!empty($c['en_name'])): ?><em dir="ltr"><?= $h((string)$c['en_name']) ?></em><?php endif; ?></div></td>
            <td class="t-fam"><?= $h((string)($c['family_tag_he'] ?: ($c['category_he'] ?? $c['category']))) ?></td>
            <td><?= !empty($c['dtm_days']) ? '<span class="num">' . (int)$c['dtm_days'] . '</span>' : '—' ?></td>
            <td><?= !empty($c['in_season']) ? 'כן' : '—' ?></td>
            <td><?php if ($pr): ?><span class="num">₪<?= $h(number_format($pr['price'], 1)) ?></span><?php elseif ($est): ?><span class="num est">₪<?= $h(number_format($est['price_min'], 1)) ?><?= $est['price_max'] > $est['price_min'] ? '–' . $h(number_format($est['price_max'], 1)) : '' ?></span> <small class="est">מוערך</small><?php else: ?>—<?php endif; ?></td>
          </tr>
          <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  <?php else: ?>
    <div class="grid">
      <?php foreach ($crops as $c):
        $cslug = (string)($c['slug'] ?? '');
        $wc    = CropArt::file($cslug);
        $act   = (string)($c['in_season_activity'] ?? '');
        $pr    = $prices[$cslug] ?? null;
        $est   = $estimates[$cslug] ?? null; // AC-1.2 estimated range (only when no live price)
        $fam   = (string)($c['family_tag_he'] ?: ($c['category_he'] ?? $c['category']));
      ?>
      <a class="cc" href="/crop-book/<?= $h($cslug) ?>/">
        <div class="cc__art">
          <?php if ($wc !== null): ?>
            <img src="/public_assets/img/crops/<?= $h($wc) ?>" alt="<?= $h((string)($c['name_he'] ?? '')) ?>" loading="lazy" decoding="async">
          <?php else: ?>
            <span class="cc__icon" aria-hidden="true"><svg class="gi"><use href="#icon-<?= $h((string)($c['icon_slug'] ?? 'leaf')) ?>"/></svg></span>
          <?php endif; ?>
          <?php if ($act !== ''): ?>
            <span class="cc__now pill pill--now"><svg class="gi" aria-hidden="true"><use href="#<?= $act === 'transplant' ? 'i-seedling' : 'i-sprout' ?>"/></svg> עכשיו</span>
          <?php endif; ?>
        </div>
        <div class="cc__b">
          <div>
            <div class="cc__name"><?= $h((string)($c['name_he'] ?? '')) ?></div>
            <?php if (!empty($c['en_name'])): ?><div class="cc__latin" dir="ltr"><?= $h((string)$c['en_name']) ?></div><?php endif; ?>
          </div>
          <?php if ($fam !== ''): ?><span class="tag"><?= $h($fam) ?></span><?php endif; ?>
          <?php if ($pr !== null): ?>
            <span class="cc__price"><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg>בשוק <span class="num">₪<?= $h(number_format($pr['price'], 1)) ?></span><?php if ($pr['unit'] !== ''): ?>/<?= $h($pr['unit']) ?><?php endif; ?></span>
          <?php elseif ($est !== null): ?>
            <span class="cc__price cc__price--est"><svg class="gi" aria-hidden="true"><use href="#i-shekel"/></svg>מחיר מוערך <span class="num">₪<?= $h(number_format($est['price_min'], 1)) ?><?php if ($est['price_max'] > $est['price_min']): ?>–<?= $h(number_format($est['price_max'], 1)) ?><?php endif; ?></span><?php if ($est['unit'] !== ''): ?>/<?= $h($est['unit']) ?><?php endif; ?></span>
          <?php endif; ?>
          <div class="cc__stats">
            <?php if (!empty($c['dtm_days'])): ?>
              <div><b class="num"><?= (int)$c['dtm_days'] ?></b><span>ימים להבשלה</span></div>
            <?php endif; ?>
            <?php if ($act === 'seed'): ?>
              <div><b>זריעה</b><span>שיטה החודש</span></div>
            <?php elseif ($act === 'transplant'): ?>
              <div><b>שתילה</b><span>שיטה החודש</span></div>
            <?php endif; ?>
          </div>
        </div>
      </a>
      <?php endforeach; ?>
    </div>

    <div class="cta">
      <div class="cta__card cta--data">
        <h3>חסר מידע על גידול?</h3>
        <p>הספר נבנה בשיתוף הקהילה. אם גידלתם — תרמו נתון, וזה יידלק לכולם.</p>
        <a class="cta__btn" href="/community">◐ תרמו נתון ›</a>
      </div>
    </div>
  <?php endif; ?>
  </div>

</div><!-- /book-index -->
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active'));
