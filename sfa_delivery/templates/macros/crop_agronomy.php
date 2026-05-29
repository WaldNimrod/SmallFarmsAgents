<?php
/**
 * crop_agronomy.php — Crop-level agronomy rollup (median across varieties).
 *
 * Variables expected from include scope:
 *   $agronomy (array) — keyed agronomic field => numeric|null value
 *     Keys: germination_temp_c_opt, in_row_spacing_cm, rows_per_bed,
 *           soil_ph_target, seeds_per_gram, yield_per_m2_kg, etc.
 *
 * Renders only populated fields — no perpetual "—" cells.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$agronomy = is_array($agronomy ?? null) ? $agronomy : [];

$AGRO_LABELS = [
    'germination_temp_c_opt'     => ['label' => 'טמפרטורת נביטה',   'unit' => '°C'],
    'in_row_spacing_cm'          => ['label' => 'מרווח בשורה',       'unit' => 'ס״מ'],
    'rows_per_bed'               => ['label' => 'שורות לערוגה',      'unit' => ''],
    'soil_ph_target'             => ['label' => 'pH קרקע מומלץ',     'unit' => ''],
    'seeds_per_gram'             => ['label' => 'זרעים לגרם',        'unit' => ''],
    'yield_per_m2_kg'            => ['label' => 'יבול משוער',        'unit' => 'ק״ג/מ״ר'],
    'days_to_maturity'           => ['label' => 'ימים להבשלה',       'unit' => 'ימים'],
    'harvest_window_max_days'    => ['label' => 'חלון קטיף',         'unit' => 'ימים'],
    'storage_life_days'          => ['label' => 'חיי מדף',           'unit' => 'ימים'],
    'storage_temp_c_max'         => ['label' => 'טמפרטורת אחסון',   'unit' => '°C'],
    'nutrient_removal_n_kg_ha'   => ['label' => 'צריכת חנקן (N)',    'unit' => 'ק״ג/דונם'],
    'nutrient_removal_p_kg_ha'   => ['label' => 'צריכת זרחן (P)',    'unit' => 'ק״ג/דונם'],
    'nutrient_removal_k_kg_ha'   => ['label' => 'צריכת אשלגן (K)',   'unit' => 'ק״ג/דונם'],
];

$intFields = ['in_row_spacing_cm', 'rows_per_bed', 'seeds_per_gram',
              'days_to_maturity', 'harvest_window_max_days', 'storage_life_days'];
$fmt = static function (string $field, $value) use ($intFields): string {
    if ($value === null || $value === '') return '';
    return in_array($field, $intFields, true)
        ? (string)(int)$value
        : number_format((float)$value, 1);
};

// Build rows — only present fields.
$rows = [];
foreach ($AGRO_LABELS as $field => $meta) {
    if (!array_key_exists($field, $agronomy)) continue;
    $val = $agronomy[$field];
    if ($val === null || $val === '') continue;
    $rows[] = [
        'label' => $meta['label'],
        'value' => $fmt($field, $val),
        'unit'  => $meta['unit'],
    ];
}

if (empty($rows)): ?>
  <p class="muted">אין נתוני אגרונומיה ברמת הגידול.</p>
<?php else: ?>
  <dl class="cb-agronomy__grid">
    <?php foreach ($rows as $row): ?>
      <dt><?= $h($row['label']) ?></dt>
      <dd>
        <?= $h($row['value']) ?>
        <?php if ($row['unit'] !== ''): ?>
          <span class="cb-agronomy__unit"><?= $h($row['unit']) ?></span>
        <?php endif; ?>
      </dd>
    <?php endforeach; ?>
  </dl>
  <p class="cb-agronomy__note muted">ממוצע חציוני על פני כל הזנים</p>
<?php endif; ?>
