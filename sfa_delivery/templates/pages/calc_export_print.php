<?php
/**
 * calc_export_print.php — WP-CB-1-patch01.
 * Print-friendly plan sheet for /calc/export.pdf — the browser's print-to-PDF
 * produces the PDF (no server-side PDF engine on the shared LAMP host).
 * Self-contained HTML (no _layout shell) + auto-print.
 *
 * Vars: $context (label=>value), $rows (label=>value)
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];
$context = is_array($context ?? null) ? $context : [];
$rows    = is_array($rows ?? null) ? $rows : [];
?><!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>תכנון מחשבון — SFA</title>
<style>
  body { font-family: "Assistant","Heebo",system-ui,sans-serif; color:#1f2a22; margin:32px; }
  h1 { font-family:"Frank Ruhl Libre",serif; color:#4d6a2c; font-size:26px; margin:0 0 4px; }
  .sub { color:#5d6b5e; margin:0 0 24px; font-size:14px; }
  table { border-collapse:collapse; width:100%; max-width:560px; margin-bottom:24px; }
  th,td { text-align:right; padding:8px 12px; border-bottom:1px solid #dce6dc; font-size:14px; }
  th { color:#5d6b5e; font-weight:700; width:40%; }
  .empty { color:#8e3018; }
  .foot { color:#5d6b5e; font-size:12px; margin-top:32px; }
  @media print { .noprint { display:none; } body { margin:12mm; } }
</style>
</head>
<body onload="if (!window.location.hash.includes('nopr')) window.print()">
  <h1>תכנון מחשבון · ספר גידולים SFA</h1>
  <p class="sub">sfa.nimrod.bio · הופק לתכנון אישי</p>

  <?php if (!empty($context)): ?>
  <table>
    <tbody>
    <?php foreach ($context as $k => $v): ?>
      <tr><th><?= $h($k) ?></th><td><?= $h($v) ?></td></tr>
    <?php endforeach; ?>
    </tbody>
  </table>
  <?php endif; ?>

  <?php if (!empty($rows)): ?>
  <table>
    <thead><tr><th>פריט</th><td>ערך</td></tr></thead>
    <tbody>
    <?php foreach ($rows as $k => $v): ?>
      <tr><th><?= $h($k) ?></th><td><?= $h($v) ?></td></tr>
    <?php endforeach; ?>
    </tbody>
  </table>
  <?php else: ?>
  <p class="empty">לא נבחרו ערכי תכנון — חזרו למחשבון, מלאו נתונים ונסו שוב.</p>
  <?php endif; ?>

  <p class="foot">הערכים הם בסיס תכנוני; אמתו מול הספר ומול תנאי השדה שלכם.</p>
  <button class="noprint" onclick="window.print()">הדפסה / שמירה כ-PDF</button>
</body>
</html>
