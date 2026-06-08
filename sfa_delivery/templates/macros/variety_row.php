<?php
/**
 * variety_row.php — COMPONENTS.md §7 (WP-UI-patch03 rewrite)
 *
 * .cb-var is a BLOCK element (not <tr>). Sentinel: dtm_days === -32768
 * means "no DTM data, presence only" (per WP-B1/B3 convention) — render "—".
 *
 * Required vars (passed in via include scope):
 *   $variety — array with keys:
 *     vslug, name_he, breeding_type (F1/heirloom/OP), is_default (bool),
 *     dtm_days  (aliased from agronomy.days_to_maturity by controller),
 *     agronomy  (associative array field_name => number|null — from ingest contract),
 *     agro_delta (associative array field_name => bool — true when value differs
 *                 from the default variety; all-false for the default itself)
 *   $crop_slug — parent crop slug (for the href)
 *
 * Agronomic fields rendered (only when present in $variety['agronomy']):
 *   days_to_maturity, germination_temp_c_opt, in_row_spacing_cm,
 *   rows_per_bed, soil_ph_target, storage_temp_c_max, storage_life_days,
 *   yield_per_m2_kg, nutrient_removal_n_kg_ha, nutrient_removal_p_kg_ha,
 *   nutrient_removal_k_kg_ha, harvest_window_max_days, seeds_per_gram
 *
 * BEM contract: .cb-var, .cb-var--default, .cb-var__head, .cb-var__star,
 *   .cb-var__grid, .cb-var__val--delta, .pill, .pill--code
 */
$variety   = $variety   ?? [];
$crop_slug = (string)($crop_slug ?? '');

$vslug         = (string)($variety['vslug']         ?? '');
$name_he       = (string)($variety['name_he']        ?? '');
$breeding_type = (string)($variety['breeding_type']  ?? '');
$is_default    = !empty($variety['is_default']);
$dtm_days      = $variety['dtm_days'] ?? null;
$agronomy      = is_array($variety['agronomy']   ?? null) ? $variety['agronomy']   : [];
$agro_delta    = is_array($variety['agro_delta'] ?? null) ? $variety['agro_delta'] : [];

// Hebrew label map — only agronomic fields (AC-U3-08: no color/taste/shape/resistance).
$AGRO_LABELS = [
    'days_to_maturity'           => 'ימים להבשלה',
    'germination_temp_c_opt'     => 'טמ׳ נביטה',
    'in_row_spacing_cm'          => 'מרווח שורה (ס״מ)',
    'rows_per_bed'               => 'שורות/ערוגה',
    'soil_ph_target'             => 'pH קרקע',
    'storage_temp_c_max'         => 'טמ׳ אחסון',
    'storage_life_days'          => 'חיי מדף (ימים)',
    'yield_per_m2_kg'            => 'יבול (ק״ג/מ״ר)',
    'nutrient_removal_n_kg_ha'   => 'N/P/K (ק״ג/דונם)',
    'harvest_window_max_days'    => 'חלון קטיף (ימים)',
    'seeds_per_gram'             => 'זרעים/גרם',
];

// Format a numeric value sensibly: integers for days/spacing/rows/seeds;
// 1 decimal for pH, yield, nutrient, temperature.
$fmt = static function ($field, $value): string {
    if ($value === null || $value === '') {
        return '—';
    }
    $intFields = ['days_to_maturity', 'in_row_spacing_cm', 'rows_per_bed',
                  'storage_life_days', 'harvest_window_max_days', 'seeds_per_gram'];
    if (in_array($field, $intFields, true)) {
        return (string)(int)$value;
    }
    return number_format((float)$value, 1);
};

// Collect only fields that are present in agronomy.
// days_to_maturity is read from the top-level dtm_days (already aliased).
$cells = [];
foreach ($AGRO_LABELS as $field => $label) {
    if ($field === 'days_to_maturity') {
        // Use the controller-aliased dtm_days value.
        $raw = $dtm_days;
        if ($raw === null || $raw === '' || (int)$raw === -32768) {
            continue; // skip if absent / sentinel
        }
        $cells[] = [
            'label' => $label,
            'value' => (string)(int)$raw,
            'delta' => (bool)($agro_delta[$field] ?? false),
        ];
    } else {
        if (!array_key_exists($field, $agronomy)) {
            continue; // skip absent fields — no perpetual "—"
        }
        $cells[] = [
            'label' => $label,
            'value' => $fmt($field, $agronomy[$field]),
            'delta' => (bool)($agro_delta[$field] ?? false),
        ];
    }
}

// nutrient_removal_n/p/k — merge into a single "N/P/K" cell if any are present.
// Remove individual n/p/k cells and inject a combined one.
$nFields = ['nutrient_removal_n_kg_ha', 'nutrient_removal_p_kg_ha', 'nutrient_removal_k_kg_ha'];
$hasnpk  = false;
foreach ($nFields as $nf) {
    if (array_key_exists($nf, $agronomy)) {
        $hasnpk = true;
        break;
    }
}
if ($hasnpk) {
    // Remove individual n/p/k entries added by the foreach above (label collision).
    $cells = array_filter($cells, fn ($c) => $c['label'] !== 'N/P/K (ק״ג/דונם)');
    $nVal  = isset($agronomy['nutrient_removal_n_kg_ha']) ? number_format((float)$agronomy['nutrient_removal_n_kg_ha'], 1) : '—';
    $pVal  = isset($agronomy['nutrient_removal_p_kg_ha']) ? number_format((float)$agronomy['nutrient_removal_p_kg_ha'], 1) : '—';
    $kVal  = isset($agronomy['nutrient_removal_k_kg_ha']) ? number_format((float)$agronomy['nutrient_removal_k_kg_ha'], 1) : '—';
    $npkDelta = (bool)($agro_delta['nutrient_removal_n_kg_ha'] ?? false)
             || (bool)($agro_delta['nutrient_removal_p_kg_ha'] ?? false)
             || (bool)($agro_delta['nutrient_removal_k_kg_ha'] ?? false);
    $cells[] = [
        'label' => 'N/P/K (ק״ג/דונם)',
        'value' => $nVal . ' / ' . $pVal . ' / ' . $kVal,
        'delta' => $npkDelta,
    ];
}
$cells = array_values($cells);
?>
<a class="cb-var<?= $is_default ? ' cb-var--default' : '' ?>" href="/crop-book/<?= htmlspecialchars($crop_slug, ENT_QUOTES, 'UTF-8') ?>/variety/<?= htmlspecialchars($vslug, ENT_QUOTES, 'UTF-8') ?>/">
  <div class="cb-var__head">
    <?php if ($is_default): ?><span class="cb-var__star" title="זן ברירת מחדל"><svg class="gi" aria-hidden="true"><use href="#i-star"/></svg></span><?php endif; ?>
    <h4><?= htmlspecialchars($name_he, ENT_QUOTES, 'UTF-8') ?></h4>
    <?php if (!empty($breeding_type)): ?>
      <span class="pill pill--code"><?= htmlspecialchars($breeding_type, ENT_QUOTES, 'UTF-8') ?></span>
    <?php endif; ?>
  </div>
  <?php if (!empty($cells)): ?>
  <div class="cb-var__grid">
    <?php foreach ($cells as $cell): ?>
      <span>
        <small><?= htmlspecialchars($cell['label'], ENT_QUOTES, 'UTF-8') ?></small>
        <span class="<?= $cell['delta'] ? 'cb-var__val--delta' : '' ?>"><?= htmlspecialchars($cell['value'], ENT_QUOTES, 'UTF-8') ?></span>
      </span>
    <?php endforeach; ?>
  </div>
  <?php endif; ?>
</a>
