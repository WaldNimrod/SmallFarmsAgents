<?php
/**
 * calc_panel.php — Calculator panel component (WP-CB-1, component #19).
 *
 * Renders one calculator card. Server pre-renders the default result;
 * crop-book-v1.js CALC[kind] recomputes client-side on input change.
 *
 * Disabled state: only when a REQUIRED book field is MISSING (not unvalidated,
 * not assumption, not user input). FIM §4, COMPONENTS §19a.
 *
 * Variables:
 *   $calc_no       int    — calculator number (1–14)
 *   $calc_kind     string — JS key ('seed','yield','revenue','pop','fert')
 *   $title_he      string — Hebrew title
 *   $audience      string — 'B'=both/'G'=gardener/'F'=farmer
 *   $book_fields   array  — array of {key, label_he, value, unit, field_state, field_name}
 *                           each resolving through FIM §1 alias
 *   $assumptions   array  — assumption keys to inline (e.g. ['germination_rate'])
 *   $all_assumptions array — full assumptions registry
 *   $user_inputs   array  — array of {key, label_he, value, unit}
 *   $result_label  string — label for result row
 *   $result_value  string — pre-computed result (server-side)
 *   $result_unit   string — unit for result
 *   $formula       string — formula string
 *   $modal_id      string — (optional) id for modal wrapper (standalone crop-page mode)
 *   $crop_slug     string — crop slug (for reqinfo)
 *
 * @see COMPONENTS-delta.md §19
 */
use SFA\Lib\Template;
use SFA\Lib\FieldRegistry;
$h = [Template::class, 'h'];

$calc_no        = (int)($calc_no ?? 0);
$calc_kind      = (string)($calc_kind ?? '');
$title_he       = (string)($title_he ?? '');
$audience       = (string)($audience ?? 'B');
$book_fields    = is_array($book_fields ?? null) ? $book_fields : [];
$assumptions    = is_array($assumptions ?? null) ? $assumptions : [];
$all_assumptions = is_array($all_assumptions ?? null) ? $all_assumptions : [];
$user_inputs    = is_array($user_inputs ?? null) ? $user_inputs : [];
$result_label   = (string)($result_label ?? 'תוצאה');
$result_value   = (string)($result_value ?? '—');
$result_unit    = (string)($result_unit ?? '');
$formula        = (string)($formula ?? '');
$modal_id       = (string)($modal_id ?? '');
$crop_slug      = (string)($crop_slug ?? '');

// Determine if disabled: any REQUIRED book field is MISSING
$disabled_field = null;
foreach ($book_fields as $bf) {
    $fs = strtoupper((string)($bf['field_state'] ?? ''));
    if ($fs === 'MISSING' || ($bf['value'] === null || $bf['value'] === '')) {
        if (!empty($bf['required'])) {
            $disabled_field = $bf;
            break;
        }
    }
}
$is_disabled = ($disabled_field !== null);

// Audience badge
$aud_labels = ['B' => 'שני הקהלים', 'G' => 'גנן/לומד', 'F' => 'חקלאי'];
$aud_class  = ['B' => 'tier--leaf', 'G' => 'tier--leaf', 'F' => 'tier--sun'];
$aud_label  = $aud_labels[$audience] ?? 'שני הקהלים';
$aud_cls    = $aud_class[$audience]  ?? 'tier--leaf';
?>
<div class="cv<?= $is_disabled ? ' is-disabled' : '' ?>" data-calc="<?= $h($calc_kind) ?>">
  <div class="cv__head">
    <span class="cv__no"><?= $h((string)$calc_no) ?></span>
    <div class="cv__title"><?= $h($title_he) ?></div>
    <span class="tier <?= $h($aud_cls) ?> cv__aud">● <?= $h($aud_label) ?></span>
  </div>

  <?php if ($is_disabled): ?>
  <div class="cv__body">
    <div class="cv__disabled">
      <span class="ic">🔒</span>
      <div>
        <h5>חסר שדה נדרש</h5>
        <?php [$disabled_label_he] = FieldRegistry::label((string)($disabled_field['field_name'] ?? '')); ?>
        <p>המחשבון יידלק כש<b><?= $h($disabled_label_he) ?></b> יתמלא.</p>
        <a class="reqinfo" href="#"
           data-field="<?= $h((string)($disabled_field['field_name'] ?? '')) ?>"
           data-crop="<?= $h($crop_slug) ?>"
        >◐ בקשו השלמת נתון</a>
      </div>
    </div>
  </div>

  <?php else: ?>
  <div class="cv__body">

    <?php if (!empty($book_fields)): ?>
    <div class="cv__uses">ערכי ספר</div>
    <div class="bvrow">
      <?php foreach ($book_fields as $bf):
        $fs  = strtoupper((string)($bf['field_state'] ?? ''));
        $val = $bf['value'] ?? null;
        $bv_cls = '';
        if ($fs === 'UNVALIDATED') $bv_cls = ' bv--ast';
        if ($fs === 'MISSING' || $val === null || $val === '') $bv_cls = ' bv--missing';
        $editable = !empty($bf['editable']) ? ' is-editable' : '';
        $fname = (string)($bf['field_name'] ?? '');
        $disp_val = $val !== null ? $h((string)$val) : '—';
      ?>
      <span class="bv<?= $bv_cls . $editable ?>"
            data-book="<?= $h((string)($bf['key'] ?? $fname)) ?>"
            data-val="<?= $h((string)($val ?? '0')) ?>">
        <span data-field="<?= $h($fname) ?>"><?= $h((string)($bf['label_he'] ?? $fname)) ?></span>
        <?php if (!empty($bf['editable'])): ?>
          <input class="bv__in" type="number" value="<?= $disp_val ?>" data-orig="<?= $disp_val ?>"/>
          <span class="bv__flag">שונה מהספר</span>
        <?php else: ?>
          <b><?= $disp_val ?></b>
        <?php endif; ?>
        <?php if (!empty($bf['unit'])): ?><small><?= $h((string)$bf['unit']) ?></small><?php endif; ?>
        <a class="bv__link" href="/crop-book/<?= $h($crop_slug) ?>/?depth=full#<?= $h($fname) ?>">↗ ספר</a>
        <?php if (!empty($bf['editable'])): ?>
          <button class="bv__restore" type="button">↺ ספר</button>
        <?php endif; ?>
        <?php if ($fs === 'UNVALIDATED'): ?>
          <span class="ast" title="ערך לא מאומת">*</span>
        <?php endif; ?>
      </span>
      <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <?php foreach ($assumptions as $ak):
      $assump = $all_assumptions[$ak] ?? ['key'=>$ak,'default'=>'','unit'=>'','explainer_he'=>'','post_url'=>''];
      $dv  = (string)($assump['default'] ?? '');
      $du  = (string)($assump['unit']    ?? '');
      $sc  = 1;
      if ($du === 'fraction') { $dv = (string)round((float)$dv * 100); $du = '%'; $sc = 0.01; }
      include __DIR__ . '/assumption_field.php';
      // reset to avoid bleed
      $key = $ak; $assumption = $assump; $display_value = $dv; $display_unit = $du; $data_scale = $sc;
    endforeach; ?>

    <?php if (!empty($user_inputs)): ?>
    <div class="cv__uses">קלט שלך</div>
    <div class="cv__inputs">
      <?php foreach ($user_inputs as $ui): ?>
      <label class="ipt">
        <label><?= $h((string)($ui['label_he'] ?? '')) ?></label>
        <span class="ipt__box">
          <input type="number"
                 data-k="<?= $h((string)($ui['key'] ?? '')) ?>"
                 value="<?= $h((string)($ui['value'] ?? '')) ?>"
                 <?= !empty($ui['min']) ? 'min="' . $h((string)$ui['min']) . '"' : '' ?>
                 <?= !empty($ui['max']) ? 'max="' . $h((string)$ui['max']) . '"' : '' ?>
          />
          <?php if (!empty($ui['unit'])): ?><span class="u"><?= $h((string)$ui['unit']) ?></span><?php endif; ?>
        </span>
      </label>
      <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <div class="cv__result">
      <span class="lbl"><?= $h($result_label) ?></span>
      <span class="big" data-result><?= $h($result_value) ?><?php if ($result_unit !== ''): ?> <small><?= $h($result_unit) ?></small><?php endif; ?></span>
    </div>
    <?php if ($formula !== ''): ?>
    <div class="cv__formula" data-formula><?= $h($formula) ?></div>
    <?php else: ?>
    <div class="cv__formula" data-formula></div>
    <?php endif; ?>
    <div data-extra></div>

    <?php if ($calc_kind === 'pop'): ?>
    <div class="popgrid" data-popgrid style="grid-template-columns:repeat(4,1fr)"></div>
    <?php endif; ?>

  </div>
  <?php endif; ?>
</div>
