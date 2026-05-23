<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = 'ספר גידולים';
$active = 'crop_book';
ob_start();
?>

<header class="page-head">
  <h1>ספר גידולים</h1>
  <p class="muted"><?= (int)$total ?> גידולים</p>
</header>

<?php if (!empty($categories)): ?>
<nav class="facets">
  <a href="/crop-book/" class="chip <?= empty($current_category) ? 'is-active' : '' ?>">הכל</a>
  <?php foreach ($categories as $cat): ?>
    <a href="/crop-book/?category=<?= $h(urlencode($cat['category'])) ?>"
       class="chip <?= ($current_category === $cat['category']) ? 'is-active' : '' ?>">
      <?= $h($cat['category']) ?> <span class="count"><?= (int)$cat['c'] ?></span>
    </a>
  <?php endforeach ?>
</nav>
<?php endif ?>

<?php if (empty($crops)): ?>
  <p class="empty">אין גידולים בקטגוריה הזו עדיין.</p>
<?php else: ?>
<ul class="card-grid">
  <?php foreach ($crops as $c): ?>
    <li class="card">
      <a href="/crop-book/<?= $h($c['slug']) ?>" class="card-link">
        <h2 class="card-title"><?= $h($c['hebrew_name']) ?></h2>
        <?php if (!empty($c['scientific_name'])): ?>
          <p class="card-subtitle"><em><?= $h($c['scientific_name']) ?></em></p>
        <?php endif ?>
        <dl class="card-meta">
          <?php if (!empty($c['family_name_he'])): ?>
            <dt>משפחה</dt><dd><?= $h($c['family_name_he']) ?></dd>
          <?php endif ?>
          <?php if (!empty($c['category'])): ?>
            <dt>קטגוריה</dt><dd><?= $h($c['category']) ?></dd>
          <?php endif ?>
          <?php if (!empty($c['dtm_min']) || !empty($c['dtm_max'])): ?>
            <dt>זמן לבשלות</dt>
            <dd><?= (int)$c['dtm_min'] ?>–<?= (int)$c['dtm_max'] ?> ימים</dd>
          <?php endif ?>
        </dl>
      </a>
    </li>
  <?php endforeach ?>
</ul>
<?php endif ?>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
