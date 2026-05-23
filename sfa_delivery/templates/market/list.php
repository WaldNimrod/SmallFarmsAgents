<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = 'מחירון';
$active = 'market';
ob_start();
?>

<header class="page-head">
  <h1>מחירון תוצרת</h1>
  <p class="muted"><?= (int)$total ?> מוצרים פעילים</p>
</header>

<?php if (!empty($categories)): ?>
<nav class="facets">
  <a href="/market/" class="chip <?= empty($current_category) ? 'is-active' : '' ?>">הכל</a>
  <?php foreach ($categories as $cat): ?>
    <a href="/market/?category=<?= $h(urlencode($cat['category'])) ?>"
       class="chip <?= ($current_category === $cat['category']) ? 'is-active' : '' ?>">
      <?= $h($cat['category']) ?> <span class="count"><?= (int)$cat['c'] ?></span>
    </a>
  <?php endforeach ?>
</nav>
<?php endif ?>

<?php if (empty($products)): ?>
  <p class="empty">אין מוצרים בקטגוריה הזו עדיין.</p>
<?php else: ?>
<table class="data-table">
  <thead>
    <tr>
      <th>שם</th>
      <th>קטגוריה</th>
      <th>יחידה</th>
      <th>מחיר אחרון</th>
      <th>טריות</th>
    </tr>
  </thead>
  <tbody>
    <?php foreach ($products as $p): ?>
      <tr>
        <td><a href="/market/<?= $h($p['slug']) ?>"><?= $h($p['hebrew_name']) ?></a></td>
        <td><?= $h($p['category']) ?></td>
        <td><?= $h($p['unit']) ?></td>
        <td>
          <?php if (!empty($p['last_price'])): ?>
            <strong><?= number_format((float)$p['last_price'], 2) ?> ₪</strong>
            <?php if (!empty($p['last_price_date'])): ?>
              <small class="muted">· <?= $h($p['last_price_date']) ?></small>
            <?php endif ?>
          <?php else: ?>
            <span class="muted">—</span>
          <?php endif ?>
        </td>
        <td>
          <?php
          $fd = $p['freshness_days'];
          if ($fd === null) { echo '<span class="muted">—</span>'; }
          elseif ($fd <= 1) { echo '<span class="fresh-good">היום</span>'; }
          elseif ($fd <= 7) { echo '<span class="fresh-ok">' . (int)$fd . ' ימים</span>'; }
          else              { echo '<span class="fresh-old">' . (int)$fd . ' ימים</span>'; }
          ?>
        </td>
      </tr>
    <?php endforeach ?>
  </tbody>
</table>
<?php endif ?>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
