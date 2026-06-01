<?php
/**
 * assumption_field.php — AssumptionField component (WP-CB-1, component #18).
 *
 * 4 mandatory parts, 2 states (collapsed / .is-open).
 * NEVER disables a calculator. Always carries a default.
 * Launch-blocking: germination_rate + bed_width MUST have post_url.
 *
 * Variables:
 *   $key         string — assumption key (e.g. 'germination_rate')
 *   $assumption  array  — {key, default, unit, explainer_he, post_url}
 *                         (from GET /api/v1/assumptions or inline registry)
 *   $display_value  mixed  — formatted display (e.g. "90" for 0.90 fraction)
 *   $display_unit   string — display unit (e.g. "%")
 *   $input_min      numeric — (optional) min attribute
 *   $input_max      numeric — (optional) max attribute
 *   $data_scale     float  — (optional) scale factor (e.g. 0.01 for percent→fraction)
 *
 * @see COMPONENTS-delta.md §18
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$key           = $key          ?? '';
$assumption    = $assumption   ?? [];
$explainer_he  = (string)($assumption['explainer_he'] ?? '');
$post_url      = (string)($assumption['post_url']     ?? '');
$display_value = $display_value ?? (string)($assumption['default'] ?? '');
$display_unit  = $display_unit  ?? (string)($assumption['unit']    ?? '');
$input_min     = $input_min     ?? null;
$input_max     = $input_max     ?? null;
$data_scale    = $data_scale    ?? 1;

// Normalise fraction units to percent for display
if ($display_unit === 'fraction') {
    $display_unit   = '%';
    $display_value  = (string)round((float)$display_value * 100);
    $data_scale     = 0.01;
}
?>
<div class="af" data-assume-key="<?= $h($key) ?>">
  <div class="af__bar">
    <span class="af__tag">◇ הנחה</span>
    <div class="af__lbl"><?php
      // Label from FIELD_INFO dictionary — JS will inject the Hebrew label via data-field
      // We output a fallback key label as well for no-JS.
      $labels = [
        'germination_rate'     => 'נביטה',
        'bed_width'            => 'רוחב ערוגה',
        'oversow'              => 'גיבוי זריעה',
        'std_bed_length_m'     => 'אורך ערוגה',
        'compost_N_pct'        => '% חנקן בקומפוסט',
        'application_efficiency' => 'יעילות פיזור',
        'rotation_gap_seasons' => 'פער סבב',
        'tray_cells'           => 'תאי מגש',
      ];
      echo $h($labels[$key] ?? $key);
    ?><small><?= $h($key) ?></small></div>
    <div class="af__value">
      <div class="af__default"><?= $h($display_value) ?><small><?= $h($display_unit) ?></small></div>
      <button class="af__edit" type="button" aria-label="ערוך הנחה">✎</button>
    </div>
  </div>
  <div class="af__body">
    <div class="af__panel">
      <div class="af__override">
        <label>ערך מותאם</label>
        <span class="af__input">
          <input
            type="number"
            data-assume="<?= $h($key) ?>"
            data-scale="<?= $h((string)$data_scale) ?>"
            data-suffix="<?= $h($display_unit) ?>"
            value="<?= $h($display_value) ?>"
            <?= $input_min !== null ? 'min="' . $h((string)$input_min) . '"' : '' ?>
            <?= $input_max !== null ? 'max="' . $h((string)$input_max) . '"' : '' ?>
          /><span><?= $h($display_unit) ?></span>
        </span>
        <button class="af__reset" type="button"
                data-reset data-default="<?= $h($display_value) ?>"
        >↺ ברירת מחדל <?= $h($display_value) . $h($display_unit) ?></button>
      </div>
      <?php if ($explainer_he !== ''): ?>
      <div class="af__explain">
        <span class="when">מתי ולמה לשנות?</span>
        <p><?= $h($explainer_he) ?></p>
        <?php if ($post_url !== ''): ?>
          <a class="af__more" href="<?= $h($post_url) ?>" target="_blank" rel="noopener">קראו עוד ←</a>
        <?php else: ?>
          <a class="af__more is-soon" href="#" aria-disabled="true">בקרוב ←</a>
        <?php endif; ?>
      </div>
      <?php endif; ?>
    </div>
  </div>
</div>
