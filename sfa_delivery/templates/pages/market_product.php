<?php
use SFA\Lib\Template;
$page_title = (string)($product['hebrew_name'] ?? 'מוצר');
ob_start();
?>
<section>
  <?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>
  <h1><?= htmlspecialchars((string)($product['hebrew_name'] ?? ''), ENT_QUOTES, 'UTF-8') ?></h1>
  <p>מחיר אחרון: <?= htmlspecialchars((string)($product['last_price'] ?? '—'), ENT_QUOTES, 'UTF-8') ?> ₪</p>
  <h2>היסטוריה (28 ימים)</h2>
  <table>
    <thead><tr><th>תאריך</th><th>מחיר</th><th>מקור</th></tr></thead>
    <tbody>
      <?php foreach (($history ?? []) as $row): ?>
        <tr>
          <td><?= htmlspecialchars((string)$row['price_date'], ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)$row['price'], ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)($row['source'] ?? '—'), ENT_QUOTES, 'UTF-8') ?></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
