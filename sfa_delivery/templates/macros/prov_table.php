<?php
/**
 * prov_table.php — Drill-down provenance hierarchy (component #20).
 *
 * Shows every source (EX/NI/PR/WR) for a field, the winning source,
 * and a confidence bar. Surfaced only in Drill-down depth.
 *
 * Variables:
 *   $field_name  string — canonical field name
 *   $label_he    string — Hebrew label
 *   $sources     array  — array of {source_class, source_name, value, unit, confidence_score, is_winner}
 *
 * @see COMPONENTS-delta.md §20
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$field_name = (string)($field_name ?? '');
$label_he   = (string)($label_he   ?? $field_name);
$sources    = is_array($sources ?? null) ? $sources : [];

if (empty($sources)) {
    return;
}
?>
<div class="prov" data-field="<?= $h($field_name) ?>">
  <div style="font-family:var(--gj-font-body);font-size:12px;font-weight:700;color:var(--gj-ink-soft);margin-bottom:6px;">
    <?= $h($label_he) ?> — מקורות
  </div>
  <?php foreach ($sources as $src):
    $cls   = strtolower((string)($src['source_class'] ?? 'wr'));
    $conf  = isset($src['confidence_score']) ? (float)$src['confidence_score'] : 0.0;
    $winner = !empty($src['is_winner']);
  ?>
  <div class="prov__row<?= $winner ? ' is-winner' : '' ?>">
    <span class="prov__cls prov__cls--<?= $h($cls) ?>"><?= $h(strtoupper($cls)) ?></span>
    <span class="prov__src"><?= $h((string)($src['source_name'] ?? '')) ?></span>
    <span class="prov__num"><?= $h((string)($src['value'] ?? '—')) ?><?php if (!empty($src['unit'])): ?> <small><?= $h((string)$src['unit']) ?></small><?php endif; ?></span>
    <span class="prov__conf">
      <span class="confbar<?= $conf < 0.40 ? ' is-low' : '' ?>"><i style="width:<?= $h((string)min(100, round($conf * 100))) ?>%"></i></span>
      <?= $h((string)round($conf * 100)) ?>%
    </span>
    <?php if ($winner): ?><span class="prov__win">✓ מנצח</span><?php endif; ?>
  </div>
  <?php endforeach; ?>
</div>
