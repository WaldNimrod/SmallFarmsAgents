<?php
/**
 * crop_topics.php — shared topic renderer for the crop page Full + Deep depths.
 *
 * WP-CB-MOBILE Stage 2: Full and Deep share ONE topic taxonomy so they form a
 * clear Simple ⊂ Full ⊂ Deep progression. Full renders every field as a
 * collapsible .topic/.fieldgrid/.fg dt-dd. Deep renders the SAME structure but
 * each .fg dd also carries a .rng (variety range) and each topic a .srcline of
 * EX/PR/WR .srcpill source tags — drawn ONLY from data the controller actually
 * exposes ($variety_ranges, $source_classes); never fabricated.
 *
 * Expected in include scope (inherited from book_crop.php):
 *   $topics          array  — [{key,icon,label,class,fields[]}]
 *   $is_deep         bool   — true → render ranges + source pills
 *   $cb1_fields      array  — field => {value_best,field_state,unit,...}
 *   $variety_ranges  array  — field => {min,max,count}
 *   $source_classes  string[] — ordered EX/PR/WR codes backing this crop
 *   $notes           array  — public notes (pest topic drill-down)
 *   $pv              callable(string):string — rich value renderer
 *   $monthChips      callable($months):string
 *   $h               callable(string):string — htmlspecialchars
 */
use SFA\Lib\FieldRegistry;

$topics         = is_array($topics ?? null) ? $topics : [];
$is_deep        = (bool)($is_deep ?? false);
$variety_ranges = is_array($variety_ranges ?? null) ? $variety_ranges : [];
$source_classes = is_array($source_classes ?? null) ? $source_classes : [];

// Source-class display labels (trust rank EX > PR > WR). Used only in Deep.
$SRC_LABELS = [
    'EX' => ['cls' => 'ex', 'lbl' => 'EX · מומחה'],
    'PR' => ['cls' => 'pr', 'lbl' => 'PR · מקצועי'],
    'WR' => ['cls' => 'wr', 'lbl' => 'WR · רשת'],
];

// Range line for a field: "טווח min–max · N זנים". Only emitted when the field
// has ≥2 distinct reporting varieties (otherwise there is no real range).
$rngLine = function (string $field) use ($variety_ranges, $h): string {
    $r = $variety_ranges[$field] ?? null;
    if ($r === null || (int)$r['count'] < 2) {
        return '';
    }
    $min = FieldRegistry::fmtNumber($r['min']);
    $max = FieldRegistry::fmtNumber($r['max']);
    if ($min === $max) {
        return '';
    }
    return '<small class="rng">טווח <span class="num" dir="ltr">' . $h($min . '–' . $max) . '</span> · '
        . $h((string)$r['count'] . ' זנים') . '</small>';
};

foreach ($topics as $topic):
    if (empty($topic['fields'])) { continue; }
?>
<div class="topic topic--<?= $h($topic['class']) ?>">
  <div class="topic__head">
    <span class="topic__ic" aria-hidden="true"><?= $topic['icon'] ?></span>
    <div class="topic__t"><?= $h($topic['label']) ?></div>
    <span class="topic__chev" aria-hidden="true">▾</span>
  </div>
  <div class="topic__body">
    <dl class="fieldgrid">
      <?php foreach ($topic['fields'] as $fn):
        [$lbl_he,] = FieldRegistry::label($fn);
        $isProposed = FieldRegistry::isProposed($fn);
      ?>
      <div class="fg">
        <dt data-field="<?= $h($fn) ?>"><?= $h($lbl_he) ?>
          <?php if ($isProposed): ?><span class="proposed-tag">מוצע</span><?php endif; ?>
        </dt>
        <dd>
          <?php if ($isProposed): ?>
            <span class="proposed-tag">טרם הוגדר</span>
          <?php elseif ($fn === 'sowing_months'):
            $months = $cb1_fields['sowing_months']['value_best'] ?? null;
            echo $monthChips($months);
          else:
            echo $pv($fn);
            if ($is_deep) { echo $rngLine($fn); }
          endif; ?>
        </dd>
      </div>
      <?php endforeach; ?>
    </dl>

    <?php
    // Deep: per-topic source provenance row (EX/PR/WR), trust-ranked. Only the
    // source classes that actually back this crop's data are shown; when the
    // mirror carries no provenance ($source_classes empty) the row is omitted.
    if ($is_deep && !empty($source_classes)): ?>
    <div class="srcline" aria-label="מקורות הנתונים">
      <?php foreach ($source_classes as $sc):
        if (!isset($SRC_LABELS[$sc])) { continue; } ?>
        <span class="srcpill srcpill--<?= $h($SRC_LABELS[$sc]['cls']) ?>"><?= $h($SRC_LABELS[$sc]['lbl']) ?></span>
      <?php endforeach; ?>
    </div>
    <?php endif; ?>

    <?php
    // WI-9 / AC-10: מזיקים topic renders public pest/irrigation notes (kept).
    if ($topic['key'] === 'pest'):
      $pest_note_types = ['pest_disease', 'irrigation'];
      $pest_notes = array_values(array_filter($notes, static function ($n) use ($pest_note_types) {
          return in_array((string)($n['note_type'] ?? ''), $pest_note_types, true);
      }));
      if (!empty($pest_notes)):
    ?>
    <div class="pest-notes">
      <h4 class="pest-notes__title">פירוט מזיקים ומחלות</h4>
      <?php foreach ($pest_notes as $pn): ?>
      <div class="pest-note">
        <?php if (!empty($pn['title_he'])): ?><strong><?= $h((string)$pn['title_he']) ?></strong><?php endif; ?>
        <p><?= $h((string)($pn['body_text'] ?? '')) ?></p>
      </div>
      <?php endforeach; ?>
    </div>
    <?php endif; endif; ?>
  </div>
</div>
<?php endforeach; ?>
