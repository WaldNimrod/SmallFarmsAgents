<?php
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$page_title = $product['hebrew_name'] ?? 'מוצר';
$active = 'market';
ob_start();
?>

<nav class="breadcrumb">
  <a href="/market/">← מחירון</a>
</nav>

<article class="product-detail">
  <header>
    <h1><?= $h($product['hebrew_name']) ?></h1>
  </header>

  <dl class="kv-list">
    <?php if (!empty($product['category'])): ?>
      <dt>קטגוריה</dt><dd><?= $h($product['category']) ?></dd>
    <?php endif ?>
    <?php if (!empty($product['unit'])): ?>
      <dt>יחידת מידה</dt><dd><?= $h($product['unit']) ?></dd>
    <?php endif ?>
    <?php if (!empty($product['code'])): ?>
      <dt>קוד</dt><dd><code><?= $h($product['code']) ?></code></dd>
    <?php endif ?>
    <?php if (!empty($product['last_price'])): ?>
      <dt>מחיר אחרון</dt>
      <dd>
        <strong><?= number_format((float)$product['last_price'], 2) ?> ₪</strong>
        <?php if (!empty($product['last_price_date'])): ?>
          <small class="muted">(<?= $h($product['last_price_date']) ?>)</small>
        <?php endif ?>
      </dd>
    <?php endif ?>
    <?php if (!empty($product['is_organic_required'])): ?>
      <dt>תוקף אורגני</dt><dd><span class="tag tag-organic">חובה</span></dd>
    <?php endif ?>
    <?php if (!empty($product['is_basket_product'])): ?>
      <dt>מוצר סלסל</dt><dd><span class="tag">כן</span></dd>
    <?php endif ?>
  </dl>

  <?php if (!empty($product['seasonality_notes'])): ?>
  <section class="prose">
    <h2>עונתיות</h2>
    <p><?= nl2br($h($product['seasonality_notes'])) ?></p>
  </section>
  <?php endif ?>

  <?php if (!empty($history)): ?>
  <section>
    <h2>היסטוריית מחירים (30 ימים אחרונים)</h2>
    <table class="data-table compact">
      <thead><tr><th>תאריך</th><th>מחיר</th><th>מקור</th></tr></thead>
      <tbody>
        <?php foreach ($history as $row): ?>
          <tr>
            <td><?= $h($row['price_date']) ?></td>
            <td><?= number_format((float)$row['price'], 2) ?> ₪</td>
            <td><?= $h($row['source']) ?></td>
          </tr>
        <?php endforeach ?>
      </tbody>
    </table>
  </section>
  <?php else: ?>
    <p class="empty">אין נתוני מחיר ב-30 הימים האחרונים.</p>
  <?php endif ?>

  <footer class="meta-footer">
    <small class="muted">עודכן: <?= $h($product['last_pushed_at']) ?></small>
  </footer>
</article>

<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'active'));
