<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = $crop['hebrew_name'] ?? 'גידול';
$active = 'crop_book';
ob_start();
?>

<nav class="breadcrumb">
  <a href="/crop-book/">← ספר גידולים</a>
</nav>

<article class="crop-detail">
  <header>
    <h1><?= $h($crop['hebrew_name']) ?></h1>
    <?php if (!empty($crop['scientific_name'])): ?>
      <p class="muted"><em><?= $h($crop['scientific_name']) ?></em></p>
    <?php endif ?>
  </header>

  <dl class="kv-list">
    <?php if (!empty($crop['family_name_he'])): ?>
      <dt>משפחה</dt><dd><?= $h($crop['family_name_he']) ?></dd>
    <?php endif ?>
    <?php if (!empty($crop['category'])): ?>
      <dt>קטגוריה</dt><dd><?= $h($crop['category']) ?></dd>
    <?php endif ?>
    <?php if (!empty($crop['season'])): ?>
      <dt>מחזור</dt><dd><?= $h($crop['season']) ?></dd>
    <?php endif ?>
    <?php if (!empty($crop['dtm_min']) || !empty($crop['dtm_max'])): ?>
      <dt>זמן לבשלות</dt><dd><?= (int)$crop['dtm_min'] ?>–<?= (int)$crop['dtm_max'] ?> ימים</dd>
    <?php endif ?>
    <?php if (!empty($crop['harvest_unit_default'])): ?>
      <dt>יחידת קציר</dt><dd><?= $h($crop['harvest_unit_default']) ?></dd>
    <?php endif ?>
    <?php if (!empty($crop['variety_count'])): ?>
      <dt>זנים מתועדים</dt><dd><?= (int)$crop['variety_count'] ?></dd>
    <?php endif ?>
  </dl>

  <?php if (!empty($crop['description_md'])): ?>
  <section class="prose">
    <h2>תיאור</h2>
    <p><?= nl2br($h($crop['description_md'])) ?></p>
  </section>
  <?php endif ?>

  <?php if (!empty($varieties)): ?>
  <section>
    <h2>זנים</h2>
    <ul class="variety-list">
      <?php foreach ($varieties as $v): ?>
        <li class="variety">
          <h3>
            <?= $h($v['name']) ?>
            <?php if (!empty($v['is_default'])): ?><span class="tag">ברירת מחדל</span><?php endif ?>
          </h3>
          <dl class="variety-meta">
            <?php if (!empty($v['days_to_maturity'])): ?>
              <dt>ימים לבשלות</dt><dd><?= (int)$v['days_to_maturity'] ?></dd>
            <?php endif ?>
            <?php if (!empty($v['planting_method'])): ?>
              <dt>שיטת שתילה</dt><dd><?= $h($v['planting_method']) ?></dd>
            <?php endif ?>
            <?php if (!empty($v['planting_season'])): ?>
              <dt>עונת שתילה</dt><dd><?= $h($v['planting_season']) ?></dd>
            <?php endif ?>
            <?php if (!empty($v['in_row_spacing_cm'])): ?>
              <dt>מרווח בשורה</dt><dd><?= (int)$v['in_row_spacing_cm'] ?> ס"מ</dd>
            <?php endif ?>
            <?php if (!empty($v['documented_price'])): ?>
              <dt>מחיר מתועד</dt>
              <dd>
                <?= $h($v['documented_price']) ?>
                <?= $h($v['documented_price_unit'] ?? '') ?>
                <?php if (!empty($v['documented_price_source'])): ?>
                  <small class="muted">· <?= $h($v['documented_price_source']) ?></small>
                <?php endif ?>
              </dd>
            <?php endif ?>
          </dl>
          <?php if (!empty($v['notes'])): ?>
            <p class="notes"><?= nl2br($h($v['notes'])) ?></p>
          <?php endif ?>
        </li>
      <?php endforeach ?>
    </ul>
  </section>
  <?php endif ?>

  <footer class="meta-footer">
    <small class="muted">עודכן: <?= $h($crop['last_pushed_at']) ?></small>
  </footer>
</article>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
