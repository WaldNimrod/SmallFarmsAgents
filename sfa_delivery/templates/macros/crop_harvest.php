<?php
/**
 * crop_harvest.php — Harvest & yield stats per season/year.
 *
 * Variables expected from include scope:
 *   $harvest (array) — list of entries, each:
 *     season (string)
 *     year   (int|string, optional)
 *     weeks  (array: first, peak, last — week numbers, optional)
 *     yield_per_bed (array: min, median, max, optional)
 *     unit   (string, optional)
 *
 * Renders a card-row per entry.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$harvest = is_array($harvest ?? null) ? $harvest : [];

$SEASON_HE = [
    'spring' => 'אביב',
    'summer' => 'קיץ',
    'autumn' => 'סתיו',
    'fall'   => 'סתיו',
    'winter' => 'חורף',
    'annual' => 'שנתי',
];

if (empty($harvest)): ?>
  <p class="muted">אין נתוני יבול זמינים.</p>
<?php else: ?>
  <div class="cb-harvest">
    <?php foreach ($harvest as $entry):
        $season  = (string)($entry['season'] ?? '');
        $season_he = $SEASON_HE[strtolower($season)] ?? $season;
        $year    = $entry['year'] ?? null;
        $weeks   = is_array($entry['weeks'] ?? null) ? $entry['weeks'] : [];
        $yield   = is_array($entry['yield_per_bed'] ?? null) ? $entry['yield_per_bed'] : [];
        $unit    = (string)($entry['unit'] ?? 'ק״ג/ערוגה');
        ?>
      <div class="cb-harvest__card">
        <div class="cb-harvest__season">
          <?= $h($season_he) ?>
          <?php if ($year !== null && $year !== ''): ?>
            <span class="cb-harvest__year"><?= $h((string)$year) ?></span>
          <?php endif; ?>
        </div>
        <dl class="cb-harvest__stats">
          <?php if (!empty($weeks['first']) || !empty($weeks['peak']) || !empty($weeks['last'])): ?>
            <dt>שבועות קטיף</dt>
            <dd>
              <?php
              $wParts = [];
              if (!empty($weeks['first'])) $wParts[] = 'ראשון: שבוע ' . (int)$weeks['first'];
              if (!empty($weeks['peak']))  $wParts[] = 'שיא: שבוע '  . (int)$weeks['peak'];
              if (!empty($weeks['last']))  $wParts[] = 'אחרון: שבוע ' . (int)$weeks['last'];
              echo $h(implode(' · ', $wParts));
              ?>
            </dd>
          <?php endif; ?>
          <?php if (!empty($yield)): ?>
            <dt>יבול לערוגה</dt>
            <dd>
              <?php
              $yParts = [];
              if (isset($yield['min']))    $yParts[] = 'מינ׳ ' . number_format((float)$yield['min'], 1);
              if (isset($yield['median'])) $yParts[] = 'חציון ' . number_format((float)$yield['median'], 1);
              if (isset($yield['max']))    $yParts[] = 'מקס׳ ' . number_format((float)$yield['max'], 1);
              echo $h(implode(' / ', $yParts));
              if ($unit !== '') echo ' <span class="cb-harvest__unit">' . $h($unit) . '</span>';
              ?>
            </dd>
          <?php endif; ?>
        </dl>
      </div>
    <?php endforeach; ?>
  </div>
<?php endif; ?>
