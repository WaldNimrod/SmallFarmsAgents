<?php
/**
 * calc_seq.php — Grouped calculator sequence (component #19b).
 *
 * Stacks calculators whose outputs feed each other (#1→#3→#4).
 * Renders .cv-seq wrapper with .cv-seq__link connectors.
 *
 * Variables:
 *   $panels  array of rendered HTML strings — each a cv panel
 *   $links   array of {from, to, value_label} — connector descriptions
 *
 * @see COMPONENTS-delta.md §19b
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$panels = is_array($panels ?? null) ? $panels : [];
$links  = is_array($links  ?? null) ? $links  : [];
?>
<div class="cv-seq">
  <?php foreach ($panels as $i => $panel_html): ?>
    <?= $panel_html ?>
    <?php if (isset($links[$i])): $lnk = $links[$i]; ?>
    <div class="cv-seq__link">
      <span class="arr">↓</span>
      <span class="flow"><?= $h((string)($lnk['value_label'] ?? '')) ?></span>
      <span>→ מזין מחשבון <?= $h((string)($lnk['to'] ?? '')) ?></span>
    </div>
    <?php endif; ?>
  <?php endforeach; ?>
</div>
