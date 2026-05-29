<?php
/**
 * crop_identity.php — Species-level identity metadata block.
 *
 * Variables expected from include scope:
 *   $crop (array) — full crop array with keys:
 *     identity (array from payload):
 *       category, growth_cycle, harvest_unit_default, first_fruit_year,
 *       description, family (array: name_he, scientific_name)
 *     dtm_min, dtm_max (from crop columns)
 *     name_lat / scientific_name (fallback)
 *     family (array: slug, name_he) — from controller canonicalisation
 *
 * Renders: category pill, growth cycle, harvest unit, first_fruit_year,
 *          DTM range, description, family link.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$crop     = $crop ?? [];
$identity = is_array($crop['identity'] ?? null) ? $crop['identity'] : [];
$family   = is_array($crop['family']   ?? null) ? $crop['family']   : null;

// Merge identity fields into local vars, falling back to crop root keys.
$category        = (string)($identity['category']             ?? ($crop['category']             ?? ''));
$growth_cycle    = (string)($identity['growth_cycle']         ?? ($crop['growth_cycle']         ?? ''));
$harvest_unit    = (string)($identity['harvest_unit_default'] ?? ($crop['harvest_unit_default'] ?? ''));
$first_fruit_year= $identity['first_fruit_year']               ?? ($crop['first_fruit_year']    ?? null);
$description     = (string)($identity['description']          ?? ($crop['description_he']       ?? ($crop['description'] ?? '')));

// DTM range — prefer identity block, fall back to crop columns.
$dtm_min = $identity['dtm_min'] ?? ($crop['dtm_min'] ?? null);
$dtm_max = $identity['dtm_max'] ?? ($crop['dtm_max'] ?? null);
// Single representative DTM already in $crop['dtm_days'] from controller.
$dtm_days = $crop['dtm_days'] ?? null;

// Scientific name from identity.family, or root keys.
$sci_name = '';
if (!empty($identity['family']['scientific_name'])) {
    $sci_name = (string)$identity['family']['scientific_name'];
} elseif (!empty($crop['name_lat'])) {
    $sci_name = (string)$crop['name_lat'];
} elseif (!empty($crop['scientific_name'])) {
    $sci_name = (string)$crop['scientific_name'];
}

// Category Hebrew labels.
$CAT_LABELS = [
    'vegetables'  => 'ירקות',
    'herbs'       => 'עשבי תיבול',
    'fruits'      => 'פירות',
    'legumes'     => 'קטניות',
    'grains'      => 'דגנים',
    'flowers'     => 'פרחים',
    'roots'       => 'שורשים',
    'brassicas'   => 'כרוביים',
    'alliums'     => 'בצליים',
    'cucurbits'   => 'דלועיים',
    'solanums'    => 'סולניים',
];
$category_he = $CAT_LABELS[strtolower($category)] ?? $category;

// Growth cycle Hebrew labels.
$CYCLE_LABELS = [
    'annual'    => 'חד-שנתי',
    'biennial'  => 'דו-שנתי',
    'perennial' => 'רב-שנתי',
];
$growth_cycle_he = $CYCLE_LABELS[strtolower($growth_cycle)] ?? $growth_cycle;

// Collect identity meta-rows (label => value) to render as a small fact grid.
$meta = [];
if ($category_he !== '')    $meta['קטגוריה']     = $category_he;
if ($growth_cycle_he !== '') $meta['מחזור חיים']  = $growth_cycle_he;
if ($harvest_unit !== '')    $meta['יחידת קטיף']  = $harvest_unit;
if ($first_fruit_year !== null && $first_fruit_year !== '') {
    $meta['שנת פרי ראשון'] = (string)$first_fruit_year;
}

// DTM range string.
if ($dtm_min !== null && $dtm_max !== null && (int)$dtm_min !== -32768 && (int)$dtm_max !== -32768) {
    $meta['ימים להבשלה'] = (int)$dtm_min . '–' . (int)$dtm_max;
} elseif ($dtm_days !== null && (int)$dtm_days !== -32768) {
    $meta['ימים להבשלה'] = (string)(int)$dtm_days;
}

if ($sci_name !== '') $meta['שם לטיני'] = $sci_name;
?>
<div class="cb-identity">
  <?php if ($description !== ''): ?>
    <p class="cb-identity__desc"><?= $h($description) ?></p>
  <?php endif; ?>

  <?php if (!empty($meta)): ?>
  <dl class="cb-identity__grid">
    <?php foreach ($meta as $label => $value): ?>
      <dt><?= $h((string)$label) ?></dt>
      <dd><?= $h((string)$value) ?></dd>
    <?php endforeach; ?>
    <?php if ($family !== null): ?>
      <dt>משפחה בוטנית</dt>
      <dd><a href="/crop-book/family/<?= $h((string)($family['slug'] ?? '')) ?>" class="cb-identity__family-link"><?= $h((string)($family['name_he'] ?? '')) ?></a></dd>
    <?php endif; ?>
  </dl>
  <?php endif; ?>
</div>
