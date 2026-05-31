<?php
/**
 * prov_value.php — Single cue authority for field provenance (WP-CB-1).
 *
 * Reads per-field state and emits exactly one of:
 *   VALIDATED   → plain value + unit (--cb-validated color via CSS)
 *   UNVALIDATED → value + .ast asterisk + tooltip
 *   MISSING     → "—" + .reqinfo request-info CTA
 *
 * Complies with FIM §4: no threshold math here — render the stamped field_state.
 * If field_state is absent, derive defensively from confidence_score (τ=0.40).
 *
 * Variables (pass as an array or as extract()ed vars):
 *   $field        array — enrichment row: value_best, unit, field_state,
 *                         winning_source_class, confidence_score, field_name, label_he
 *   $field_name   string — canonical field key (for data-field + reqinfo)
 *   $crop_slug    string — (optional) crop slug for reqinfo POST payload
 *   $show_tooltip bool   — (default true) show unvalidated tooltip
 *
 * Usage: Template::partial('macros/prov_value', ['field' => $row, 'field_name' => 'yield_per_bed_m'])
 * Or include inline with $field and $field_name in scope.
 *
 * @see FIELD_INTERFACE_MAP_v1.0.0.md §4
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$field       = $field       ?? [];
$field_name  = $field_name  ?? (string)($field['field_name'] ?? '');
$crop_slug   = $crop_slug   ?? '';
$show_tooltip = $show_tooltip ?? true;

// Resolve state — backend stamps field_state when available; derive otherwise.
$state = (string)($field['field_state'] ?? '');
if ($state === '') {
    // Defensive derivation: EX/NI → VALIDATED; confidence_score ≥ 0.40 → VALIDATED; else UNVALIDATED/MISSING
    $src   = strtoupper((string)($field['winning_source_class'] ?? ''));
    $conf  = isset($field['confidence_score']) ? (float)$field['confidence_score'] : null;
    $val   = $field['value_best'] ?? null;
    if ($val === null || $val === '') {
        $state = 'MISSING';
    } elseif (in_array($src, ['EX', 'NI'], true) || ($conf !== null && $conf >= 0.40)) {
        $state = 'VALIDATED';
    } else {
        $state = 'UNVALIDATED';
    }
}

$value = $field['value_best'] ?? null;
$unit  = (string)($field['unit'] ?? '');
$src   = strtoupper((string)($field['winning_source_class'] ?? ''));
$conf  = isset($field['confidence_score']) ? (float)$field['confidence_score'] : null;

if ($state === 'MISSING' || ($value === null || $value === '')) {
?>
<span class="val--missing" data-field="<?= $h($field_name) ?>"
>—<?php if ($field_name !== ''): ?> <a class="reqinfo"
    href="#"
    data-field="<?= $h($field_name) ?>"
    data-crop="<?= $h($crop_slug) ?>"
    >◐ בקשו נתון</a><?php endif; ?>
</span>
<?php
} elseif ($state === 'UNVALIDATED') {
    $tip_he = 'מקור: ' . $h($src) . ($conf !== null ? ' · ביטחון ' . round($conf * 100) . '%' : '') . ' — מאומת חלקית';
?>
<span class="tip" data-field="<?= $h($field_name) ?>">
  <?= $h((string)$value) ?><?php if ($unit !== ''): ?><small> <?= $h($unit) ?></small><?php endif; ?>
  <span class="ast" title="<?= $h($tip_he) ?>">*</span>
  <?php if ($show_tooltip): ?>
  <span class="tip__pop">
    <b>ערך לא מאומת</b>
    <?= $h($tip_he) ?>
  </span>
  <?php endif; ?>
</span>
<?php
} else { // VALIDATED
?>
<span class="pv-validated" data-field="<?= $h($field_name) ?>"><?= $h((string)$value) ?><?php if ($unit !== ''): ?><small> <?= $h($unit) ?></small><?php endif; ?></span>
<?php
}
