<?php
/**
 * book_variety.php — Route /crop-book/{crop_slug}/variety/{vslug} (CB5 expanded)
 *
 * Mandate §3 (route 11): extends CB5 with `.crop-vars__row--expanded` + `.variety-fields` <dl><dt><dd>.
 * Per LOD400 v1.0.3 §0.5 + COMPONENTS.md / digest §7: actual classes are
 *   `.cb-var-detail` (page-level), `.cb-var__row--expanded` (DOM hook),
 *   `.variety-fields` + `.variety-fields__row` + `.variety-fields__extras` (AC-DB-1).
 *
 * AC-DB-1 (MANDATE §5.4): controllers may surface fields outside the known-label
 *   dictionary as the schema expands (parallel session). This template MUST render
 *   such fields gracefully via `<details class="variety-fields__extras">` rather than
 *   silently dropping or emitting PHP warnings. Implementation below.
 *
 * SECURITY: knowledge_notes filtered through is_internal_farm_use_only=TRUE
 *   (data inventory §E.5 licensing hard-gate).
 *
 * Variables expected from controller:
 *   $crop    array — ['slug','name_he','name_lat'?,'scientific_name'?]
 *   $variety array — variable shape; known keys:
 *     'vslug', 'name_he', 'name_lat'?, 'is_default'?, 'breeding_type'?,
 *     'dtm_days'?, 'yield_kg_per_m2'?, 'color_he'?, 'shape_he'?,
 *     'taste_stars'?, 'resistance_he'?, 'origin_country_he'?,
 *     'seed_supplier_he'?, 'planting_season_he'?, 'harvest_window_he'?,
 *     'enrichment'?, 'confidence_score'?, 'winning_source_class'?,
 *     'knowledge_notes'? — array of notes (filtered on render)
 *     (any other key → renders into the variety-fields__extras fallback)
 */
use SFA\Lib\Template;
$h = [Template::class, 'h'];

$crop    = $crop    ?? [];
$variety = $variety ?? [];

$crop_slug   = (string)($crop['slug']    ?? '');
$crop_name   = (string)($crop['name_he'] ?? '');
$crop_sci    = (string)($crop['name_lat'] ?? ($crop['scientific_name'] ?? ''));
$variety_slug = (string)($variety['vslug'] ?? '');
$variety_name = (string)($variety['name_he'] ?? 'זן');
$is_default   = !empty($variety['is_default']);

$page_title = $variety_name;
$page_sub   = 'זן · ' . $crop_name;
$active     = 'crop-book';
$back_url   = '/crop-book/' . $crop_slug;

// Known-label dictionary — Hebrew labels, ordered for display.
$known_labels = [
    'dtm_days'           => 'ימים לקציר',
    'yield_kg_per_m2'    => 'יבול (ק״ג/מ״ר)',
    'color_he'           => 'צבע',
    'shape_he'           => 'צורה',
    'taste_stars'        => 'טעם',
    'resistance_he'      => 'עמידות',
    'breeding_type'      => 'סוג רבייה',
    'origin_country_he'  => 'מקור',
    'seed_supplier_he'   => 'ספק זרעים',
    'planting_season_he' => 'עונת שתילה',
    'harvest_window_he'  => 'חלון קציר',
];

// Identifier / system fields excluded from the unknown-field fallback.
// These are presentation-handled elsewhere or are not user-facing data.
$reserved_keys = [
    'vslug', 'slug', 'name_he', 'name_lat', 'name_en', 'crop_slug', 'crop_id',
    'is_default', 'knowledge_notes', 'enrichment', 'confidence_score',
    'winning_source_class',
];

ob_start();
?>
<section class="cb-var-detail cb-var__row--expanded">
  <nav class="cb-crop-hero__breadcrumb">
    <a href="/crop-book/">ספר גידולים</a><span>›</span>
    <a href="/crop-book/<?= $h($crop_slug) ?>"><?= $h($crop_name) ?></a><span>›</span>
    <strong><?= $h($variety_name) ?></strong>
  </nav>

  <header class="cb-var-detail__head">
    <a href="/crop-book/<?= $h($crop_slug) ?>" class="cb-var-detail__back">← <?= $h($crop_name) ?></a>
    <h1 class="cb-var-detail__h">
      <?= $h($variety_name) ?>
      <?php if ($is_default): ?>
        <span class="cb-var__star" title="זן ברירת מחדל">★ ברירת מחדל</span>
      <?php endif; ?>
    </h1>
    <?php if (!empty($variety['breeding_type'])): ?>
      <span class="pill pill--code"><?= $h((string)$variety['breeding_type']) ?></span>
    <?php endif; ?>
    <?php if ($crop_sci !== ''): ?>
      <p class="muted">גידול: <a href="/crop-book/<?= $h($crop_slug) ?>"><?= $h($crop_name) ?></a> · <em><?= $h($crop_sci) ?></em></p>
    <?php endif; ?>
  </header>

  <dl class="variety-fields">
    <?php $rendered_known = 0; ?>
    <?php foreach ($known_labels as $key => $label):
        if (!array_key_exists($key, $variety)) continue;
        $value = $variety[$key];
        if ($value === null || $value === '') continue;
        $rendered_known++;
    ?>
      <div class="variety-fields__row">
        <dt><?= $h($label) ?></dt>
        <dd>
          <?php
          if ($key === 'dtm_days') {
              // -32768 sentinel (WP-B1/B3): "presence only — no DTM data".
              if ((int)$value === -32768) {
                  echo '<span class="muted">—</span>';
              } else {
                  echo (int)$value;
              }
          } elseif ($key === 'taste_stars') {
              $n = max(0, min(5, (int)$value));
              echo $n > 0 ? str_repeat('★', $n) : '—';
          } elseif ($key === 'yield_kg_per_m2') {
              echo $h(number_format((float)$value, 1) . ' ק״ג/מ״ר');
          } else {
              echo $h((string)$value);
          }
          ?>
        </dd>
      </div>
    <?php endforeach; ?>
    <?php if ($rendered_known === 0): ?>
      <div class="variety-fields__row">
        <dt>—</dt>
        <dd>אין עדיין מידע מפורט על זן זה.</dd>
      </div>
    <?php endif; ?>
  </dl>

  <?php
  // AC-DB-1 — unknown-field fallback.
  // Defensive rendering for parallel-session schema expansion: render any keys
  // not in $known_labels and not in $reserved_keys into a collapsed <details>.
  $payload_extras = [];
  foreach ($variety as $key => $value) {
      if (isset($known_labels[$key]))         continue;
      if (in_array($key, $reserved_keys, true)) continue;
      if ($value === null || $value === '')   continue;
      if (is_array($value)) {
          if (empty($value))                                   continue;
          // Skip arrays-of-objects — those need bespoke rendering.
          if (isset($value[0]) && is_array($value[0]))         continue;
      }
      $payload_extras[$key] = $value;
  }
  if (!empty($payload_extras)): ?>
    <details class="variety-fields__extras">
      <summary>פרטים נוספים מהמקור (<?= (int)count($payload_extras) ?>)</summary>
      <dl>
        <?php foreach ($payload_extras as $key => $value): ?>
          <div class="variety-fields__row">
            <dt><?= $h(str_replace('_', ' ', (string)$key)) ?></dt>
            <dd><?php
              if (is_scalar($value)) {
                  echo $h((string)$value);
              } elseif (is_array($value)) {
                  // Flat array of scalars → join; otherwise JSON-encode safely.
                  $flat = true;
                  foreach ($value as $iv) { if (!is_scalar($iv)) { $flat = false; break; } }
                  if ($flat) {
                      echo $h(implode(', ', array_map('strval', $value)));
                  } else {
                      echo '<code>' . $h(json_encode($value, JSON_UNESCAPED_UNICODE)) . '</code>';
                  }
              } else {
                  echo '—';
              }
            ?></dd>
          </div>
        <?php endforeach; ?>
      </dl>
    </details>
  <?php endif; ?>

  <?php
  // Enrichment confidence display — present only when controller supplies it.
  if (!empty($variety['enrichment']) && !empty($variety['confidence_score'])):
      $wsc = (string)($variety['winning_source_class'] ?? '');
      $wsc_lc = strtolower($wsc);
  ?>
    <div class="cb-var-conf">
      <span class="cb-var-conf__label">רמת ביטחון:</span>
      <span class="cb-var-conf__score"><?= $h(number_format((float)$variety['confidence_score'], 2)) ?></span>
      <?php if ($wsc !== '' && preg_match('/^[a-z0-9_-]+$/', $wsc_lc)): ?>
        <span class="cb-var-conf__tier pill pill--<?= $h($wsc_lc) ?>"><?= $h($wsc) ?></span>
      <?php endif; ?>
    </div>
  <?php endif; ?>

  <?php
  // Knowledge notes — MANDATORY filter on is_internal_farm_use_only.
  if (!empty($variety['knowledge_notes']) && is_array($variety['knowledge_notes'])):
      $public_notes = array_values(array_filter(
          $variety['knowledge_notes'],
          fn ($n) => is_array($n) && empty($n['is_internal_farm_use_only'])
      ));
      if (!empty($public_notes)): ?>
          <section class="cb-notes">
            <h2 class="cb-notes__h">הערות</h2>
            <?php foreach ($public_notes as $note): ?>
              <article class="cb-note">
                <h4 class="cb-note__h"><?= $h((string)($note['title_he'] ?? '')) ?></h4>
                <p class="cb-note__body"><?= $h((string)($note['text_he'] ?? '')) ?></p>
                <?php if (!empty($note['source_label_he'])): ?>
                  <small class="cb-note__src">— <?= $h((string)$note['source_label_he']) ?></small>
                <?php endif; ?>
              </article>
            <?php endforeach; ?>
          </section>
      <?php endif;
  endif; ?>

  <?php
  $context          = 'book.variety.' . $variety_slug;
  $context_label_he = 'זן · ' . $variety_name;
  include __DIR__ . '/../macros/contrib_strip.php';
  ?>
</section>
<?php
$content = ob_get_clean();
echo Template::render('_layout', compact('content', 'page_title', 'page_sub', 'active', 'back_url'));
