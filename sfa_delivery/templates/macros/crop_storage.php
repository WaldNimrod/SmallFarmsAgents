<?php
/**
 * crop_storage.php — Post-harvest storage conditions.
 *
 * Variables expected from include scope:
 *   $storage (array) — keys:
 *     temp     (array: min, max — Celsius)
 *     rh       (array: min, max — percent)
 *     ethylene_production   (string|null)
 *     ethylene_sensitivity  (string|null)
 *     life_days (array: min, max)
 *     notes    (string, optional)
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$storage = is_array($storage ?? null) ? $storage : [];

if (empty($storage)): ?>
  <p class="muted">אין נתוני אחסון זמינים.</p>
<?php else:
    $temp  = is_array($storage['temp']      ?? null) ? $storage['temp']      : [];
    $rh    = is_array($storage['rh']        ?? null) ? $storage['rh']        : [];
    $life  = is_array($storage['life_days'] ?? null) ? $storage['life_days'] : [];
    $eth_prod = (string)($storage['ethylene_production']  ?? '');
    $eth_sens = (string)($storage['ethylene_sensitivity'] ?? '');
    $notes    = (string)($storage['notes']                ?? '');

    // Ethylene Hebrew labels.
    $ETH_LABELS = [
        'low'    => 'נמוך',
        'medium' => 'בינוני',
        'high'   => 'גבוה',
        'none'   => 'ללא',
    ];
    $eth_prod_he = $ETH_LABELS[strtolower($eth_prod)] ?? $eth_prod;
    $eth_sens_he = $ETH_LABELS[strtolower($eth_sens)] ?? $eth_sens;

    $rows = [];
    if (!empty($temp['min']) || !empty($temp['max'])) {
        $parts = [];
        if (isset($temp['min'])) $parts[] = number_format((float)$temp['min'], 1);
        if (isset($temp['max'])) $parts[] = number_format((float)$temp['max'], 1);
        $rows['טמפרטורת אחסון'] = implode('–', $parts) . ' °C';
    }
    if (!empty($rh['min']) || !empty($rh['max'])) {
        $parts = [];
        if (isset($rh['min'])) $parts[] = (int)$rh['min'];
        if (isset($rh['max'])) $parts[] = (int)$rh['max'];
        $rows['לחות יחסית'] = implode('–', $parts) . '%';
    }
    if (!empty($life['min']) || !empty($life['max'])) {
        $parts = [];
        if (isset($life['min'])) $parts[] = (int)$life['min'];
        if (isset($life['max'])) $parts[] = (int)$life['max'];
        $rows['חיי מדף'] = implode('–', $parts) . ' ימים';
    }
    if ($eth_prod_he !== '') $rows['ייצור אתילן'] = $eth_prod_he;
    if ($eth_sens_he !== '') $rows['רגישות לאתילן'] = $eth_sens_he;
?>
  <div class="cb-storage">
    <dl class="cb-storage__grid">
      <?php foreach ($rows as $label => $value): ?>
        <dt><?= $h((string)$label) ?></dt>
        <dd><?= $h((string)$value) ?></dd>
      <?php endforeach; ?>
    </dl>
    <?php if ($notes !== ''): ?>
      <p class="cb-storage__notes"><?= $h($notes) ?></p>
    <?php endif; ?>
  </div>
<?php endif; ?>
