<?php
/**
 * prov_table.php — Drill-down provenance hierarchy (WP-CB-1, component #20 prov).
 *
 * Shows the per-source value hierarchy for one field in the Drill-down depth:
 *   winning value + class, then contributing sources ranked, each with a confidence bar.
 *
 * FIM §4: NO threshold math in the UI. The confidence-bar WIDTH is a raw display of the
 * backend confidence number (not a judgment). Any "low" emphasis is driven by a
 * backend-stamped flag ($s['is_low']) — the UI does not apply τ. (F-190-CB1-V-02)
 *
 * Variables:
 *   $field_name  string — canonical field key (machine hook only; never shown as a label)
 *   $label_he    string — Hebrew label (resolved by caller via FieldRegistry)
 *   $sources     array  — [{source_class, value, unit, confidence_score, is_winner, is_low}]
 *   $winning     array  — {source_class, value, unit}
 *
 * @see COMPONENTS-delta.md §2.2 (.prov)
 */
use SFA\Lib\Template;
use SFA\Lib\FieldRegistry;
$h = [Template::class, 'h'];
$field_name = (string)($field_name ?? '');
$label_he   = (string)($label_he   ?? $field_name);
$sources    = is_array($sources ?? null) ? $sources : [];
$winning    = is_array($winning ?? null) ? $winning : [];
// WP-CB-UI-FIDELITY §4.1 finding: format provenance values too (no raw 6-decimal floats /
// English unit tokens in the audit/source-value column). numeric → fmtNumber(unit-aware); unit → Hebrew.
$provVal = static function ($v, $u): string {
    $v = (string)($v ?? '');
    return is_numeric($v) ? FieldRegistry::fmtNumber($v, (string)$u) : $v;
};
?>
<div class="prov" data-field="<?= $h($field_name) ?>">
  <div class="prov__head">
    <span class="prov__label"><?= $h($label_he) ?></span>
    <?php if (!empty($winning)): ?>
    <span class="prov__win">
      <b><?= $h($provVal($winning['value'] ?? '', $winning['unit'] ?? '')) ?></b>
      <?php $wu = FieldRegistry::unitLabel((string)($winning['unit'] ?? '')); if ($wu !== ''): ?><small><?= $h($wu) ?></small><?php endif; ?>
      <span class="prov__cls"><?= $h((string)($winning['source_class'] ?? '')) ?></span>
    </span>
    <?php endif; ?>
  </div>
  <?php if (!empty($sources)): ?>
  <ul class="prov__list">
    <?php foreach ($sources as $s):
      $conf = isset($s['confidence_score']) ? (float)$s['confidence_score'] : 0.0;
      $cls  = (string)($s['source_class'] ?? '');
      // is_low is a backend-stamped flag (mirrors the reconciler's state); the UI does NOT compute τ.
      $low  = !empty($s['is_low']) ? ' is-low' : '';
    ?>
    <li class="prov__src<?= !empty($s['is_winner']) ? ' is-winner' : '' ?>">
      <span class="prov__srccls"><?= $h($cls) ?></span>
      <span class="confbar<?= $low ?>"><i style="width:<?= $h((string)min(100, round($conf * 100))) ?>%"></i></span>
      <span class="prov__srcval"><?= $h($provVal($s['value'] ?? '', $s['unit'] ?? '')) ?><?php $su = FieldRegistry::unitLabel((string)($s['unit'] ?? '')); if ($su !== ''): ?> <?= $h($su) ?><?php endif; ?></span>
    </li>
    <?php endforeach; ?>
  </ul>
  <?php endif; ?>
</div>
