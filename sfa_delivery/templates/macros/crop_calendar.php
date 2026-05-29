<?php
/**
 * crop_calendar.php — 12-month planting calendar strip.
 *
 * Variables expected from include scope:
 *   $calendar (array) — list of entries, each:
 *     activity_type (string): 'seed' | 'transplant'
 *     season        (string): e.g. 'spring'
 *     region        (string, optional)
 *     months        (array of 12 bools, index 0=Jan..11=Dec)
 *     notes         (string, optional)
 *
 * Renders one 12-month strip per activity_type found.
 * Months are displayed RTL — rendered right-to-left (Dec on left, Jan on right in HTML).
 * Active months are highlighted.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$calendar = is_array($calendar ?? null) ? $calendar : [];

// Month abbreviations in Hebrew (index 0 = January).
$MONTH_HE = ['ינו', 'פבר', 'מרץ', 'אפר', 'מאי', 'יונ', 'יול', 'אוג', 'ספט', 'אוק', 'נוב', 'דצמ'];

// Activity type labels.
$ACTIVITY_LABELS = [
    'seed'       => 'זריעה ישירה',
    'transplant' => 'שתילה',
];

// Group entries by activity_type.
$grouped = [];
foreach ($calendar as $entry) {
    $type = (string)($entry['activity_type'] ?? 'seed');
    $grouped[$type][] = $entry;
}

if (empty($grouped)): ?>
  <p class="cb-calendar__empty muted">אין נתוני לוח שנה זמינים.</p>
<?php else: ?>
  <div class="cb-calendar">
    <?php foreach ($grouped as $type => $entries): ?>
      <div class="cb-calendar__row">
        <div class="cb-calendar__label">
          <?= $h($ACTIVITY_LABELS[$type] ?? $type) ?>
        </div>
        <?php foreach ($entries as $entry):
            $months = is_array($entry['months'] ?? null) ? $entry['months'] : array_fill(0, 12, false);
            $region  = (string)($entry['region'] ?? '');
            $notes   = (string)($entry['notes']  ?? '');
            ?>
          <div class="cb-calendar__strip-wrap">
            <?php if ($region !== ''): ?>
              <span class="cb-calendar__region"><?= $h($region) ?></span>
            <?php endif; ?>
            <div class="cb-calendar__strip" dir="rtl" role="list" aria-label="לוח שנה <?= $h($ACTIVITY_LABELS[$type] ?? $type) ?>">
              <?php foreach ($MONTH_HE as $i => $mon):
                  $active = !empty($months[$i]);
                  ?>
                <span class="cb-calendar__month<?= $active ? ' cb-calendar__month--active' : '' ?>"
                      role="listitem"
                      aria-label="<?= $h($mon) ?><?= $active ? ' — פעיל' : '' ?>"><?= $h($mon) ?></span>
              <?php endforeach; ?>
            </div>
            <?php if ($notes !== ''): ?>
              <p class="cb-calendar__notes"><?= $h($notes) ?></p>
            <?php endif; ?>
          </div>
        <?php endforeach; ?>
      </div>
    <?php endforeach; ?>
  </div>
<?php endif; ?>
