<?php
use SFA\Lib\Template;
$page_title = 'טבלת גידולים';
ob_start();
?>
<section>
  <h1>טבלת גידולים</h1>
  <?php if (!empty($category)): ?><p>פילטר: <?= htmlspecialchars((string)$category, ENT_QUOTES, 'UTF-8') ?></p><?php endif; ?>
  <table>
    <thead><tr><th scope="col">שם</th><th scope="col">קטגוריה</th><th scope="col">עונה</th><th scope="col"><span class="visually-hidden">פעולות</span></th></tr></thead>
    <tbody>
      <?php foreach (($crops ?? []) as $crop): ?>
        <tr>
          <td><?= htmlspecialchars((string)$crop['hebrew_name'], ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)($crop['category'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
          <td><?= htmlspecialchars((string)($crop['season'] ?? ''), ENT_QUOTES, 'UTF-8') ?></td>
          <td><a href="/crop-book/<?= htmlspecialchars((string)$crop['slug'], ENT_QUOTES, 'UTF-8') ?>">פרטים</a></td>
        </tr>
      <?php endforeach; ?>
    </tbody>
  </table>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title'));
