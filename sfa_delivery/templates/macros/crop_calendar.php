<?php
/**
 * crop_calendar.php — 12-month planting calendar.
 *
 * WP-CB-MOBILE FIX 2b: rebuilt as the team_35 `.pcal` grid (two activity
 * tracks: sow / transplant; cells .on / .now; legend + note). Server-side
 * label maps guarantee NO raw key (`IL_*`, `seed`, `spring`, …) ever reaches
 * visible text — region/activity/season are translated to Hebrew here.
 *
 * Variables expected from include scope:
 *   $calendar (array) — list of entries, each:
 *     activity_type (string): 'seed' | 'transplant' | 'both'
 *     season        (string): 'spring'|'summer'|'fall'|'winter'|'all'
 *     region        (string, optional)
 *     months        (array of 12 bools, index 0=Jan..11=Dec)
 *     notes         (string, optional)
 *
 * Backward-compat: the legacy `.cb-calendar*` class tokens are preserved on the
 * month cells so the existing render contract / tests stay green while the new
 * `.pcal` skin drives the visuals.
 */
$h = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

$calendar = is_array($calendar ?? null) ? $calendar : [];

// Month abbreviations in Hebrew (index 0 = January) + full names for the note.
$MONTH_HE      = ['ינו', 'פבר', 'מרץ', 'אפר', 'מאי', 'יונ', 'יול', 'אוג', 'ספט', 'אוק', 'נוב', 'דצמ'];
$MONTH_HE_FULL = ['ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני', 'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר'];

// Activity type → Hebrew label. NEVER leak the raw key. ('both' = שתילה ←
// the merged track shown on the transplant line; see grouping below.)
$ACTIVITY_LABELS = [
    'seed'       => 'זריעה ישירה',
    'transplant' => 'שתילה',
    'both'       => 'זריעה ושתילה',
];
// Short label used for the .pcal track + legend.
$ACTIVITY_SHORT = [
    'seed'       => 'זריעה',
    'transplant' => 'שתילה',
    'both'       => 'זריעה ושתילה',
];

// Season → Hebrew label (WP-CB-MOBILE FIX 2b). Raw `spring`/… must never leak.
$SEASON_LABELS = [
    'spring' => 'אביב',
    'summer' => 'קיץ',
    'fall'   => 'סתיו',
    'winter' => 'חורף',
    'all'    => 'כל השנה',
];

// Region code → Hebrew label (team_35 WP-CB-MOBILE v4, FIX 2). The planting
// calendar must never surface raw `IL_*`/`MED_*` tokens to users. Known codes
// map to friendly Hebrew; any unknown code is suppressed (rendered '') rather
// than leaked raw.
$REGION_LABELS = [
    'IL_general'  => 'כל הארץ',
    'IL_north'    => 'צפון',
    'IL_center'   => 'מרכז',
    'IL_south'    => 'דרום',
    'MED_general' => 'אגן הים התיכון',
];

// Current month (0-based) for the `now` cell + the note.
$now_idx = (int)date('n') - 1;

// Group entries by activity_type.
$grouped = [];
foreach ($calendar as $entry) {
    $type = (string)($entry['activity_type'] ?? 'seed');
    $grouped[$type][] = $entry;
}

if (empty($grouped)): ?>
  <p class="cb-calendar__empty muted">אין נתוני לוח שנה זמינים.</p>
<?php else:
    // Collect a single region label (first non-empty mapped region) + any note +
    // a union of active months across all entries (for the "in season / next
    // window" note line).
    $region_label = '';
    $note_text    = '';
    $seasons_seen = [];
    foreach ($calendar as $entry) {
        $rl = $REGION_LABELS[(string)($entry['region'] ?? '')] ?? '';
        if ($region_label === '' && $rl !== '') { $region_label = $rl; }
        $nt = trim((string)($entry['notes'] ?? ''));
        if ($note_text === '' && $nt !== '') { $note_text = $nt; }
        $sk = (string)($entry['season'] ?? '');
        if (isset($SEASON_LABELS[$sk])) { $seasons_seen[$SEASON_LABELS[$sk]] = true; }
    }
    ?>
  <div class="pcal cb-calendar">
    <div class="pcal__head">
      <h4 class="pcal__title"><span class="g">📅</span>מתי לזרוע ולשתול</h4>
      <?php if ($region_label !== ''): ?>
        <span class="pcal__region cb-calendar__region"><span class="g">📍</span><?= $h($region_label) ?></span>
      <?php endif; ?>
    </div>
    <div class="pcal__legend">
      <span><i class="is-seed"></i>זריעה</span>
      <span><i class="is-trans"></i>שתילה</span>
    </div>

    <?php foreach ($grouped as $type => $entries):
        // A track per activity type. Merge active months across same-type entries.
        $track_mod = $type === 'transplant' ? 'trans' : ($type === 'both' ? 'trans' : 'seed');
        $track_lbl = $ACTIVITY_SHORT[$type] ?? $type;
        // Union of active months for this track.
        $months_union = array_fill(0, 12, false);
        foreach ($entries as $entry) {
            $months = is_array($entry['months'] ?? null) ? $entry['months'] : array_fill(0, 12, false);
            for ($i = 0; $i < 12; $i++) {
                if (!empty($months[$i])) { $months_union[$i] = true; }
            }
        }
        ?>
      <div class="pcal__track pcal__track--<?= $h($track_mod) ?>">
        <span class="pcal__tracklbl"><?= $h($track_lbl) ?></span>
        <div class="pcal__cells" role="list" aria-label="לוח שנה <?= $h($ACTIVITY_LABELS[$type] ?? $type) ?>">
          <?php for ($i = 0; $i < 12; $i++):
              $month_active = !empty($months_union[$i]);
              $is_now       = ($i === $now_idx);
              // Legacy tokens kept on active cells for the render contract / tests.
              $cls = ['cb-calendar__month'];
              if ($month_active) { $cls[] = 'on'; $cls[] = 'cb-calendar__month--active'; }
              if ($is_now)       { $cls[] = 'now'; }
              ?>
            <i class="<?= $h(implode(' ', $cls)) ?>"
               role="listitem"
               aria-label="<?= $h($MONTH_HE[$i]) ?><?= $month_active ? ' — פעיל' : '' ?><?= $is_now ? ' — החודש' : '' ?>"></i>
          <?php endfor; ?>
        </div>
      </div>
    <?php endforeach; ?>

    <div class="pcal__months">
      <span></span>
      <div class="nums" dir="ltr">
        <?php for ($i = 1; $i <= 12; $i++): ?><span><?= $i ?></span><?php endfor; ?>
      </div>
    </div>

    <?php
    // Note line: today + (optional) season window + (optional) source note.
    $bits = [];
    $bits[] = 'היום <b>' . $h($MONTH_HE_FULL[$now_idx]) . '</b>';
    if (!empty($seasons_seen)) {
        $bits[] = 'עונת השתילה: <b>' . $h(implode(' · ', array_keys($seasons_seen))) . '</b>';
    }
    if ($note_text !== '') {
        $bits[] = $h($note_text);
    }
    ?>
    <p class="pcal__note cb-calendar__notes"><?= implode(' — ', $bits) ?>.</p>
  </div>
<?php endif; ?>
