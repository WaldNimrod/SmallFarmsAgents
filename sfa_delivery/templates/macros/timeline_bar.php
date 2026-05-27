<?php
/**
 * timeline_bar.php — COMPONENTS.md §12
 *
 * Required vars (passed in via include scope):
 *   $prep_pct    — float, % width of "הכנה" segment
 *   $grow_pct    — float, % width of "גידול" segment
 *   $harv_pct    — float, % width of "קציר" segment (sum of three = 100)
 *   $harv_days   — int, harvest duration in days
 *   $week_labels — (optional) array<string> ruler labels
 *
 * BEM contract: .gj-timeline, .gj-timeline__bar, .gj-timeline__seg,
 *   .gj-timeline__seg--prep, .gj-timeline__seg--grow, .gj-timeline__seg--harv,
 *   .gj-timeline__ruler
 */
$prep_pct    = (float)($prep_pct    ?? 0.0);
$grow_pct    = (float)($grow_pct    ?? 0.0);
$harv_pct    = (float)($harv_pct    ?? 0.0);
$harv_days   = (int)  ($harv_days   ?? 0);
$week_labels = isset($week_labels) && is_array($week_labels) ? $week_labels : [];
?>
<section class="gj-timeline">
  <h4>חיי הגידול</h4>
  <div class="gj-timeline__bar">
    <div class="gj-timeline__seg gj-timeline__seg--prep" style="width: <?= number_format($prep_pct, 2, '.', '') ?>%">הכנה</div>
    <div class="gj-timeline__seg gj-timeline__seg--grow" style="width: <?= number_format($grow_pct, 2, '.', '') ?>%">גידול</div>
    <div class="gj-timeline__seg gj-timeline__seg--harv" style="width: <?= number_format($harv_pct, 2, '.', '') ?>%">קציר · <?= (int)$harv_days ?> ימים</div>
  </div>
  <?php if (!empty($week_labels)): ?>
    <div class="gj-timeline__ruler">
      <?php foreach ($week_labels as $lbl): ?>
        <span><?= htmlspecialchars((string)$lbl, ENT_QUOTES, 'UTF-8') ?></span>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>
</section>
