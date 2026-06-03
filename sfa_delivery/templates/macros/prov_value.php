<?php
/**
 * prov_value.php — Single cue authority for field provenance (WP-CB-1).
 *
 * Reads per-field state and emits exactly one of:
 *   VALIDATED   → plain value + unit (--cb-validated color via CSS)
 *   UNVALIDATED → value + .ast asterisk + tooltip
 *   MISSING     → "—" + .reqinfo request-info CTA
 *
 * Complies with FIM §4: NO threshold math here — render the backend-stamped field_state.
 * If field_state is absent, render a neutral UNKNOWN cue. The UI never recomputes
 * VALIDATED from a confidence threshold — τ lives in the backend reconciler only
 * (F-190-CB1-V-02). This keeps the UI correct if τ changes (e.g. the 0.50 fast-follow).
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
use SFA\Lib\FieldRegistry;
$h = [Template::class, 'h'];

$field       = $field       ?? [];
$field_name  = $field_name  ?? (string)($field['field_name'] ?? '');
$crop_slug   = $crop_slug   ?? '';
$show_tooltip = $show_tooltip ?? true;

// Render the backend-stamped field_state verbatim — NO threshold math in the UI (FIM §4).
// The backend reconciler owns τ; the UI only displays VALIDATED / UNVALIDATED / MISSING.
$state = strtoupper((string)($field['field_state'] ?? ''));
$value = $field['value_best'] ?? null;
$unit  = (string)($field['unit'] ?? '');
$src   = strtoupper((string)($field['winning_source_class'] ?? ''));
$conf  = isset($field['confidence_score']) ? (float)$field['confidence_score'] : null;

// No value at all → MISSING regardless of (absent) state.
if ($value === null || $value === '') {
    $state = 'MISSING';
} elseif (!in_array($state, ['VALIDATED', 'UNVALIDATED', 'MISSING'], true)) {
    // Value present but the backend stamped no state (e.g. mirror predates the
    // field_state ingest, F-UI-01) → neutral UNKNOWN cue. Never assume VALIDATED.
    $state = 'UNKNOWN';
}

if ($state === 'MISSING') {
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
    // WI-1/WI-2: format number + Hebrew unit
    $_disp    = is_numeric($value) ? FieldRegistry::fmtNumber($value, $unit) : FieldRegistry::enumLabel($field_name, (string)$value);
    $_unit_he = FieldRegistry::unitLabel($unit);
?>
<span class="tip" data-field="<?= $h($field_name) ?>">
  <?= $h($_disp) ?><?php if ($_unit_he !== ''): ?><small> <?= $h($_unit_he) ?></small><?php endif; ?>
  <span class="ast" title="<?= $h($tip_he) ?>">*</span>
  <?php if ($show_tooltip): ?>
  <span class="tip__pop">
    <b>ערך לא מאומת</b>
    <?= $h($tip_he) ?>
  </span>
  <?php endif; ?>
</span>
<?php
} elseif ($state === 'UNKNOWN') {
    // Value present, backend stamped no state — show it plainly with a neutral
    // "not yet checked" cue. NOT styled as validated (no τ assumption). FIM §4.
    $_disp    = is_numeric($value) ? FieldRegistry::fmtNumber($value, $unit) : FieldRegistry::enumLabel($field_name, (string)$value);
    $_unit_he = FieldRegistry::unitLabel($unit);
?>
<span class="pv-unknown" data-field="<?= $h($field_name) ?>" title="טרם אומת מול הספר"><?= $h($_disp) ?><?php if ($_unit_he !== ''): ?><small> <?= $h($_unit_he) ?></small><?php endif; ?></span>
<?php
} else { // VALIDATED
    $_disp    = is_numeric($value) ? FieldRegistry::fmtNumber($value, $unit) : FieldRegistry::enumLabel($field_name, (string)$value);
    $_unit_he = FieldRegistry::unitLabel($unit);
?>
<span class="pv-validated" data-field="<?= $h($field_name) ?>"><?= $h($_disp) ?><?php if ($_unit_he !== ''): ?><small> <?= $h($_unit_he) ?></small><?php endif; ?></span>
<?php
}
