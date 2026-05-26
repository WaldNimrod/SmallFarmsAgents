<?php
use SFA\Lib\Template;
$page_title = 'מחירון';
ob_start();
?>
<section>
  <?php include __DIR__ . '/../macros/market_disclaimer.php'; ?>
  <h1>מחירון</h1>
  <table>
    <thead><tr><th scope="col">מוצר</th><th scope="col">מחיר</th><th scope="col">תאריך</th><th scope="col"><span class="visually-hidden">פעולות</span></th></tr></thead>
    <tbody>
      <?php foreach (($products ?? []) as $product): ?>
        <tr>
          <td><?= htmlspecialchars((string)$product['hebrew_name'], ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)($product['last_price'] ?? '—'), ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)($product['last_price_date'] ?? '—'), ENT_QUOTES, 'UTF-8') ?></td>
          <td><a href="/market/<?= htmlspecialchars((string)$product['slug'], ENT_QUOTES, 'UTF-8') ?>">פירוט</a></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
